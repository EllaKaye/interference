from shiny import App
from ui import app_ui
from server import server
from pathlib import Path

app_dir = Path(__file__).parent

app = App(app_ui, server, static_assets=app_dir / "www")
