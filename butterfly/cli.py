import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from butterfly.conversion_pipeline import ConversionPipeline

app = typer.Typer(help="Butterfly: USENET to Markdown Conversion Tool")
console = Console()


@app.command()
def convert(
        input_dir: Path = typer.Argument(Path("input"), help="Path to the directory containing source files (default: 'input')"),
        output_dir: Path = typer.Argument(Path("output"), help="Path to the directory for Markdown output (default: 'output')"),
        skip_dir: Path = typer.Argument(Path("skip"), help="Path to the directory for skipped non-story files (default: 'skip')"),
        use_llm: bool = typer.Option(False, "--use-llm", help="Enable optional LLM enhancement for ambiguous formatting"),
        model_path: Optional[Path] = typer.Option(None, "--model", help="Path to local GGUF model file"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Process files but do not write Markdown to disk"),
        discard_skips: bool = typer.Option(False, "--discard-skips", help="Do not save skipped non-story files to disk (overrides skip_dir)"),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed warnings and logs"),
):
    """Convert USENET source files to clean Markdown."""

    if not input_dir.exists() or not input_dir.is_dir():
        console.print(f"[bold red]Error:[/bold red] Input directory '{input_dir}' does not exist.")
        raise typer.Exit(code=1)

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Create skip directory only if we are actually going to use it
    if not discard_skips and not dry_run:
        skip_dir.mkdir(parents=True, exist_ok=True)

    # Gather all files (recursively, ignoring hidden files)
    files = [f for f in input_dir.rglob('*') if f.is_file() and not f.name.startswith('.')]

    if not files:
        console.print("[yellow]No files found in the input directory.[/yellow]")
        raise typer.Exit(code=0)

    console.print(f"[bold green]Found {len(files)} files to process.[/bold green]")

    # Initialize pipeline with CLI arguments
    pipeline = ConversionPipeline(
        use_llm=use_llm,
        model_path=str(model_path) if model_path else None
    )

    success_count = 0
    warning_count = 0
    skipped_count = 0

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
    ) as progress:
        task = progress.add_task("[cyan]Processing files...", total=len(files))

        for file_path in files:
            progress.update(task, description=f"Processing: {file_path.name}")

            # Determine output path (same relative structure, .md extension)
            try:
                relative_path = file_path.relative_to(input_dir)
                output_path = output_dir / relative_path.with_suffix('.md')
            except ValueError:
                output_path = output_dir / f"{file_path.stem}.md"

            result = pipeline.process_file(
                input_path=file_path,
                output_path=output_path,
                dry_run=dry_run
            )

            if result.is_non_story:
                skipped_count += 1

                # Copy skipped files to the positional skip_dir, unless --discard-skips is used
                if not discard_skips and not dry_run:
                    try:
                        rel_path = file_path.relative_to(input_dir)
                        dest_path = skip_dir / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, dest_path)
                    except Exception as e:
                        if verbose:
                            console.print(f"[red]Failed to copy skipped file {file_path.name}: {e}[/red]")

            elif result.success:
                success_count += 1
                if not dry_run:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(result.to_yaml_frontmatter() + result.markdown_content, encoding="utf-8")
            else:
                warning_count += 1
                if verbose:
                    console.print(f"[red]Failed: {file_path.name} - {', '.join(result.warnings)}[/red]")

            progress.advance(task)

    # Summary Table
    table = Table(title="Conversion Summary")
    table.add_column("Status", justify="right")
    table.add_column("Count", justify="left")
    table.add_row("[green]Successful[/green]", str(success_count))
    table.add_row("[yellow]Skipped (Non-story)[/yellow]", str(skipped_count))
    table.add_row("[red]Failed / Warnings[/red]", str(warning_count))
    console.print(table)

    if dry_run:
        console.print("[bold blue]Dry run complete. No files were written to disk.[/bold blue]")
    else:
        console.print(f"[bold green]Output saved to: {output_dir.resolve()}[/bold green]")

        if not discard_skips and skipped_count > 0:
            console.print(f"[bold yellow]{skipped_count} skipped files copied to: {skip_dir.resolve()}[/bold yellow]")
        elif discard_skips and skipped_count > 0:
            console.print("[bold yellow]Skipped files were discarded as requested.[/bold yellow]")


if __name__ == "__main__":
    app()
