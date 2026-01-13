
import typer
from rich.console import Console

app = typer.Typer(help="Run code audits")
console = Console()

@app.command()
def run(staged: bool = typer.Option(False, "--staged", help="Audit only staged files")):
    """
    Run the guardian audit.
    """
    console.print(f"[bold blue]Aura Audit[/bold blue] (staged={staged})")
    
    # Placeholder for actual audit logic (linting, secrets, etc.)
    # In Phase 1, we just verify the command runs.
    
    # Simulating a check
    all_clear = True
    
    if all_clear:
        console.print("[green]All checks passed![/green]")
        raise typer.Exit(code=0)
    else:
        console.print("[red]Issues found![/red]")
        raise typer.Exit(code=1)
