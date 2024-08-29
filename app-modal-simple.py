from shiny import App, reactive, ui, render
from pathlib import Path

def game_over_modal(title):
    m = ui.modal(  
        "Click 'New Game' to start again",  
        title = title,
        footer = ui.input_action_button("new_game_button_modal", "New Game"),
        size = "s",
        class_="custom-modal")
    return m

class Game:
    def __init__(self):
        self.state = reactive.Value("playing")
        self.score = reactive.Value(0)
        self.letter = "a"
        self.title = "Title a" if self.letter == "a" else "Different title"


    def update_score(self, points):
        self.score.set(self.score() + points)
        # Example of game logic triggering the modal based on score
        if self.score() >= 3:
            self.state.set("won")

    def new_game(self):
        self.score.set(0)
        self.state.set("playing")

game = Game()

app_ui = ui.page_fluid(
    ui.h3("Game UI"),
    ui.input_action_button("new_game_button", "New Game"),
    ui.output_text("game_state"),
    ui.input_action_button("score_button", "Increase Score"),
    ui.tags.link(rel="stylesheet", href="styles.css"),
    ui.tags.style("""
        .modal-content {
            background-color: #156645 !important;
        }
    """)
    )

def server(input, output, session):
    @reactive.Effect
    @reactive.event(game.state)
    def check_game_state():
        # Trigger the modal based on the game's state
        if game.state() == "won":
            ui.modal_show(
                game_over_modal(f"{game.title}")
            )

    @output
    @render.text
    def game_state():
        return f"Score: {game.score()}, State: {game.state()}"

    @reactive.effect
    @reactive.event(input.score_button)
    def update_game():
        game.update_score(1)

    @reactive.effect
    @reactive.event(input.new_game_button, input.new_game_button_modal)
    def _update_game():
        ui.modal_remove()
        game.new_game()


app_dir = Path(__file__).parent

app = App(app_ui, server, static_assets=app_dir / "www")