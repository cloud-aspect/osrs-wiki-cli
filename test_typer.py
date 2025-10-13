#!/usr/bin/env python3
"""
Minimal test to debug Typer issue
"""

import typer

app = typer.Typer()

@app.command()
def test(name: str):
    """Test command"""
    typer.echo(f"Hello {name}")

if __name__ == "__main__":
    app()