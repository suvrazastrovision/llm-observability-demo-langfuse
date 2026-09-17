from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel


console = Console()


def print_recommendation(
    customer_request: str,
    available_flavours: list[str],
    recommendation: str,
) -> None:
    """Render the request, available flavours, and recommendation."""
    console.print(
        Panel(
            f"[italic]{customer_request}[/italic]",
            title="🍦  Customer request",
            border_style="cyan",
            title_align="left",
        )
    )
    console.print(
        Panel(
            f"[dim]{', '.join(available_flavours)}[/dim]",
            title="📋  Today's flavours",
            border_style="yellow",
            title_align="left",
        )
    )
    console.print(
        Panel(
            Markdown(recommendation),
            title="✨  Ice-cream recommendation",
            border_style="green",
            title_align="left",
        )
    )
