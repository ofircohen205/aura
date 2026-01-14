import typer
from rich.console import Console

from aura_cli.commands import audit, hook
from aura_cli.config import config_manager

app = typer.Typer(
    name="aura",
    help="Aura CLI: Guardian of the Codebase",
    add_completion=True,
)
console = Console()

app.add_typer(audit.app, name="audit")
app.add_typer(hook.app, name="hook")


@app.command()
def config():
    """
    Show current configuration.
    """
    cfg = config_manager.load()
    console.print("[bold blue]Aura Configuration[/bold blue]")
    console.print(f"Path: {config_manager.config_file}")
    console.print(f"Data: {cfg.model_dump()}")


if __name__ == "__main__":
    app()
