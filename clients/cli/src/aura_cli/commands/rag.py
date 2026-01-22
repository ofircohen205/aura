"""
RAG Pipeline CLI Commands

Commands for ingesting documents into the RAG vector store.
"""

import asyncio
from pathlib import Path

import typer
from agentic_py.rag.service import RagService
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from aura_cli.commands.rag_constants import CLI_ERROR_DISPLAY_LIMIT, CLI_PREVIEW_FILE_LIMIT

app = typer.Typer(help="RAG pipeline commands for document ingestion")
console = Console()


@app.command()
def ingest(
    path: str = typer.Argument(..., help="File or directory path to ingest"),
    recursive: bool = typer.Option(
        True, "--recursive/--no-recursive", help="Search recursively in directories"
    ),
    file_patterns: str = typer.Option(
        None,
        "--file-patterns",
        help="Comma-separated file patterns (e.g., '*.md,*.py')",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be ingested without actually ingesting"
    ),
):
    """
    Ingest documents into the RAG vector store.

    Examples:
        # Ingest a single file
        aura rag ingest docs/guide.md

        # Ingest a directory recursively
        aura rag ingest docs/

        # Ingest only markdown files
        aura rag ingest docs/ --file-patterns "*.md"

        # Dry run to see what would be ingested
        aura rag ingest docs/ --dry-run
    """
    path_obj = Path(path)

    if not path_obj.exists():
        console.print(f"[red]Error:[/red] Path not found: {path}")
        raise typer.Exit(code=1)

    # Parse file patterns
    patterns = None
    if file_patterns:
        patterns = [p.strip() for p in file_patterns.split(",")]

    # Initialize RAG service
    service = RagService(enabled=True)

    async def _ingest():
        if path_obj.is_file():
            # Ingest single file
            if dry_run:
                console.print(f"[yellow]Dry run:[/yellow] Would ingest file: {path}")
                console.print(f"  Path: {path}")
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Ingesting file: {path}", total=None)
                try:
                    await service.ingest_document(path_obj)
                    progress.update(task, description=f"[green]✓[/green] Ingested: {path}")
                    console.print(f"[green]Successfully ingested file:[/green] {path}")
                except Exception as e:
                    progress.update(task, description=f"[red]✗[/red] Failed: {path}")
                    console.print(f"[red]Error ingesting file:[/red] {e}")
                    raise typer.Exit(code=1) from e

        else:
            # Ingest directory
            if dry_run:
                from agentic_py.rag.ingestion import discover_files

                files = discover_files(path_obj, file_patterns=patterns, recursive=recursive)
                console.print(
                    f"[yellow]Dry run:[/yellow] Would ingest {len(files)} files from: {path}"
                )
                for file in files[:CLI_PREVIEW_FILE_LIMIT]:
                    console.print(f"  - {file}")
                if len(files) > CLI_PREVIEW_FILE_LIMIT:
                    console.print(f"  ... and {len(files) - CLI_PREVIEW_FILE_LIMIT} more files")
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Ingesting directory: {path}", total=None)
                try:
                    result = await service.ingest_directory(
                        path_obj, file_patterns=patterns, recursive=recursive
                    )
                    progress.update(task, description="[green]✓[/green] Ingested directory")

                    console.print("\n[green]Ingestion completed![/green]")
                    console.print(f"  Files processed: {result['files_processed']}")
                    console.print(f"  Total chunks: {result['total_chunks']}")

                    if result["errors"]:
                        console.print(
                            f"\n[yellow]Warnings:[/yellow] {len(result['errors'])} errors occurred"
                        )
                        for error in result["errors"][:CLI_ERROR_DISPLAY_LIMIT]:
                            console.print(f"  - {error}")
                        if len(result["errors"]) > CLI_ERROR_DISPLAY_LIMIT:
                            console.print(
                                f"  ... and {len(result['errors']) - CLI_ERROR_DISPLAY_LIMIT} more errors"
                            )
                except Exception as e:
                    progress.update(task, description="[red]✗[/red] Failed")
                    console.print(f"[red]Error ingesting directory:[/red] {e}")
                    raise typer.Exit(code=1) from e

    # Run async function
    try:
        asyncio.run(_ingest())
    except KeyboardInterrupt:
        console.print("\n[yellow]Ingestion cancelled by user[/yellow]")
        raise typer.Exit(code=1) from None
