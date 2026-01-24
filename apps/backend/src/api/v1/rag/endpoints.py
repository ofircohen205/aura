"""RAG API endpoints for querying the vector store."""

from typing import Annotated

from agentic_py.config.rag import PGVECTOR_COLLECTION, RAG_ENABLED
from agentic_py.rag.service import RagService
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from loguru import logger
from sqlalchemy import text

from api.dependencies import get_current_active_user
from api.logging import get_log_context, log_operation
from api.v1.rag.exceptions import (
    RAGQueryError,
    RAGServiceUnavailableError,
    RAGStatsError,
    register_exception_handlers,
)
from api.v1.rag.schemas import RAGQueryRequest, RAGQueryResponse, RAGStatsResponse
from db.database import AsyncSession, SessionDep
from db.models.user import User

router = APIRouter(tags=["rag"])


@router.post(
    "/query",
    response_model=RAGQueryResponse,
    summary="Query RAG vector store",
    description="Search the vector database for documents similar to the query. "
    "Returns relevant context that can be used for lesson generation or other purposes.",
    responses={
        200: {"description": "Query successful"},
        422: {"description": "Validation error"},
        500: {"description": "RAG query failed"},
        503: {"description": "RAG service not enabled"},
    },
)
async def query_rag(
    request: RAGQueryRequest,
    http_request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> RAGQueryResponse:
    """
    Query the RAG vector store for relevant context.

    This endpoint searches the vector database for documents similar to the query
    and returns relevant context that can be used for lesson generation or other purposes.
    """
    if not RAG_ENABLED:
        log_context = get_log_context(http_request)
        logger.warning(
            "RAG query attempted but service is disabled",
            extra={**log_context, "endpoint": "/rag/query"},
        )
        raise RAGServiceUnavailableError(
            "RAG service is not enabled. Set RAG_ENABLED=true to enable."
        )

    with log_operation(
        "rag_query",
        http_request,
        query_length=len(request.query),
        top_k=request.top_k,
        error_patterns_count=len(request.error_patterns or []),
    ) as op_ctx:
        try:
            service = RagService(enabled=True)
            context = await service.query_knowledge(
                query=request.query,
                error_patterns=request.error_patterns,
                top_k=request.top_k,
            )

            op_ctx["context_length"] = len(context)
            op_ctx["context_preview"] = context[:100] + "..." if len(context) > 100 else context

            logger.debug(
                "RAG query successful",
                extra={
                    **op_ctx,
                    "query_preview": request.query[:100] + "..."
                    if len(request.query) > 100
                    else request.query,
                },
            )

            return RAGQueryResponse(
                context=context,
                query=request.query,
                top_k=request.top_k,
            )
        except (HTTPException, RAGServiceUnavailableError, RAGQueryError):
            raise
        except Exception as e:
            op_ctx["error"] = str(e)
            op_ctx["error_type"] = type(e).__name__
            logger.error(
                "RAG query failed",
                extra=op_ctx,
                exc_info=True,
            )
            raise RAGQueryError(f"RAG query failed: {str(e)}") from e


@router.get(
    "/stats",
    response_model=RAGStatsResponse,
    summary="Get RAG vector store statistics",
    description="Get statistics about the RAG vector store including total documents, "
    "chunks, and breakdowns by language and difficulty level.",
    responses={
        200: {"description": "Statistics retrieved successfully"},
        500: {"description": "Failed to get RAG stats"},
        503: {"description": "RAG service not enabled"},
    },
)
async def get_rag_stats(
    db: Annotated[AsyncSession, SessionDep],
    http_request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> RAGStatsResponse:
    """
    Get statistics about the RAG vector store.

    Returns counts of documents, chunks, and breakdowns by language and difficulty.
    """
    if not RAG_ENABLED:
        log_context = get_log_context(http_request)
        logger.warning(
            "RAG stats requested but service is disabled",
            extra={**log_context, "endpoint": "/rag/stats"},
        )
        raise RAGServiceUnavailableError(
            "RAG service is not enabled. Set RAG_ENABLED=true to enable."
        )

    with log_operation(
        "rag_stats",
        http_request,
        collection_name=PGVECTOR_COLLECTION,
    ) as op_ctx:
        try:
            logger.debug("Querying RAG collection", extra=op_ctx)
            collection_query = text(
                """
                SELECT uuid, name FROM langchain_pg_collection
                WHERE name = :collection_name
                LIMIT 1
                """
            )
            result = await db.execute(collection_query, {"collection_name": PGVECTOR_COLLECTION})
            collection_row = result.fetchone()

            if not collection_row:
                logger.info(
                    "RAG collection not found",
                    extra={**op_ctx, "collection_name": PGVECTOR_COLLECTION},
                )
                return RAGStatsResponse(
                    total_documents=0,
                    total_chunks=0,
                    documents_by_language={},
                    documents_by_difficulty={},
                    collection_name=PGVECTOR_COLLECTION,
                )

            collection_uuid = collection_row[0]
            op_ctx["collection_uuid"] = str(collection_uuid)

            logger.debug("Querying total chunks", extra=op_ctx)
            count_query = text(
                """
                SELECT COUNT(*) FROM langchain_pg_embedding
                WHERE collection_id = :collection_id
                """
            )
            result = await db.execute(count_query, {"collection_id": collection_uuid})
            total_chunks = result.scalar() or 0
            op_ctx["total_chunks"] = total_chunks

            logger.debug("Querying unique documents", extra=op_ctx)
            docs_query = text(
                """
                SELECT COUNT(DISTINCT cmetadata->>'source')
                FROM langchain_pg_embedding
                WHERE collection_id = :collection_id
                """
            )
            result = await db.execute(docs_query, {"collection_id": collection_uuid})
            total_documents = result.scalar() or 0
            op_ctx["total_documents"] = total_documents

            logger.debug("Querying documents by language", extra=op_ctx)
            lang_query = text(
                """
                SELECT
                    cmetadata->>'language' as language,
                    COUNT(*) as count
                FROM langchain_pg_embedding
                WHERE collection_id = :collection_id
                AND cmetadata->>'language' IS NOT NULL
                GROUP BY cmetadata->>'language'
                """
            )
            result = await db.execute(lang_query, {"collection_id": collection_uuid})
            documents_by_language = {
                row[0]: row[1]
                for row in result.fetchall()
                if row[0] is not None and row[1] is not None
            }
            op_ctx["languages_count"] = len(documents_by_language)

            logger.debug("Querying documents by difficulty", extra=op_ctx)
            diff_query = text(
                """
                SELECT
                    cmetadata->>'difficulty' as difficulty,
                    COUNT(*) as count
                FROM langchain_pg_embedding
                WHERE collection_id = :collection_id
                AND cmetadata->>'difficulty' IS NOT NULL
                GROUP BY cmetadata->>'difficulty'
                """
            )
            result = await db.execute(diff_query, {"collection_id": collection_uuid})
            documents_by_difficulty = {
                row[0]: row[1]
                for row in result.fetchall()
                if row[0] is not None and row[1] is not None
            }
            op_ctx["difficulties_count"] = len(documents_by_difficulty)

            logger.info(
                "RAG stats retrieved successfully",
                extra=op_ctx,
            )

            return RAGStatsResponse(
                total_documents=total_documents,
                total_chunks=total_chunks,
                documents_by_language=documents_by_language,
                documents_by_difficulty=documents_by_difficulty,
                collection_name=PGVECTOR_COLLECTION,
            )

        except (HTTPException, RAGServiceUnavailableError, RAGStatsError):
            raise
        except Exception as e:
            op_ctx["error"] = str(e)
            op_ctx["error_type"] = type(e).__name__
            logger.error(
                "Failed to get RAG stats",
                extra=op_ctx,
                exc_info=True,
            )
            raise RAGStatsError(f"Failed to get RAG stats: {str(e)}") from e


def create_rag_app() -> FastAPI:
    """Create and configure the RAG service FastAPI sub-application."""
    app = FastAPI(title="RAG API")
    register_exception_handlers(app)
    app.include_router(router)
    return app
