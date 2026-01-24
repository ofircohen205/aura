"""
RAG Tools

LangChain tools for RAG retrieval that agents can use in workflows.
Tools use the @tool decorator with docstring parsing so agents understand
when to use them based on the current state.
"""

from langchain.tools import tool

from agentic_py.rag.service import get_rag_service


@tool(parse_docstring=True)
async def retrieve_knowledge(
    query: str,
    error_patterns: list[str] | None = None,
    top_k: int | None = None,
) -> str:
    """Retrieve relevant documentation and code examples from the knowledge base.

    Use this tool when you need context about:
    - Error patterns or debugging help
    - Code examples and best practices
    - Documentation for specific concepts
    - Solutions to common problems

    The tool searches the vector database for semantically similar content
    based on the query and optional error patterns. Results are ranked by
    relevance and returned as formatted text.

    Args:
        query: The search query describing what information you need.
               Should be specific and descriptive (e.g., "How to handle
               async errors in Python" not just "errors").
        error_patterns: Optional list of error messages or patterns to
                        help narrow down relevant documentation. Useful
                        when user is experiencing specific errors.
        top_k: Number of results to return. If None, uses default from
               configuration (typically 3-5 results).

    Returns:
        A formatted string containing relevant documentation chunks,
        code examples, and explanations. Each result includes source
        information when available.

    Example:
        >>> result = await retrieve_knowledge(
        ...     query="Python async exception handling",
        ...     error_patterns=["RuntimeError", "asyncio.TimeoutError"]
        ... )
    """
    rag_service = get_rag_service()
    return await rag_service.query_knowledge(
        query=query,
        error_patterns=error_patterns,
        top_k=top_k,
    )


@tool(parse_docstring=True)
async def retrieve_contextual_lesson(
    error_type: str,
    code_context: str,
    _user_level: str = "intermediate",  # Reserved for future difficulty filtering
) -> str:
    """Retrieve a contextual lesson based on specific error and code context.

    This tool is optimized for generating educational content. It retrieves
    lessons that match the error type and code context, filtered by user
    experience level.

    Use this when generating personalized lesson recommendations for users
    who are struggling with specific errors in their code.

    Args:
        error_type: The type of error (e.g., "TypeError", "AttributeError").
        code_context: The relevant code snippet or context where the error
                      occurred. Helps find lessons with similar code patterns.
        _user_level: User experience level - "beginner", "intermediate", or
                   "advanced". Reserved for future difficulty filtering.

    Returns:
        A formatted lesson recommendation with explanations, examples, and
        next steps tailored to the user's level.
    """
    rag_service = get_rag_service()
    query = f"{error_type} in {code_context[:100]}"
    return await rag_service.query_knowledge(
        query=query,
        error_patterns=[error_type],
        top_k=5,  # More results for lessons
    )
