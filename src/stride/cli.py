import typer
from stride.strava.connection import update_strava_config

app = typer.Typer()

@app.command("strava-setup")
def strava_setup() -> None:
    """
    Run Strava setup and update the config.
    """
    update_strava_config()

if __name__ == "__main__":
    app()
