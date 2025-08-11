import typer

app = typer.Typer(help="Stride CLI - Strava activity tracking tool")


@app.command("strava-setup")
def strava_setup() -> None:
    """Run Strava setup and update the config."""
    from stride.provider.strava.connection import update_strava_config

    update_strava_config()


@app.command("test")
def test_command() -> None:
    """Test command to verify CLI is working."""
    print("CLI is working!")


if __name__ == "__main__":
    app()
