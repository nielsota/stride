import typer
from stride.connections.strava import update_strava_config

app = typer.Typer()


@app.command("strava-setup")
def strava_setup() -> None:
    """
    Run Strava setup and update the config.
    """
    update_strava_config()
