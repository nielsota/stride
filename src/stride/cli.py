import typer
from stride.connections.cli import app as connections_app

app = typer.Typer()

# Add the connections CLI as a sub-app
app.add_typer(connections_app, name="connections")

if __name__ == "__main__":
    app()
