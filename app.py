from shiny import App, reactive, render, ui
#import random
from typing import Optional, Tuple
from classes import Card, Game
from pathlib import Path

with open("about.md", "r") as file:
    about = file.read()

with open("instructions.md", "r") as file:
    instructions = file.read()

# Written with help from Shiny Assistant
app_ui = ui.page_navbar(
    ui.nav_panel(
        "Interference",
        ui.div(
            ui.row(
                ui.column(
                    10,
                    ui.div(
                        ui.input_action_button("new_game", "New Game"),
                        ui.input_action_button("new_round", "New Round"),
                    ),
                    ui.div(
                        ui.output_text("game_info_output"),
                        style="margin-bottom: 10px; font-size: 120%",
                    ),
                    ui.output_ui("cards"),
                    # ui.output_text("debug_output"),
                    offset=1
                )
            ),
        ),
        ui.tags.link(rel="stylesheet", href="styles.css"),
        ui.tags.link(rel="stylesheet", href="https://fonts.googleapis.com/css?family=Figtree"),
        ui.tags.script(src="drag-drop.js"),
        ui.tags.script(src="md-navigation.js")
    ),
    ui.nav_panel(
        "Instructions", 
        ui.row(
            ui.column(
                8, 
                ui.markdown(instructions), 
                offset=2
            )
        )
    ),
    ui.nav_panel(
        "About", 
        ui.row(
            ui.column(
                8, 
                ui.markdown(about), 
                offset=2
            )
        )
    )
)


# Written with help from Shiny Assistant
def server(input, output, session):
    game = reactive.Value(Game())
    clicked_card: reactive.Value[Optional[Card]] = reactive.Value(None)
    debug_message = reactive.Value("")
    game_info_message = reactive.Value("")
    game_state = reactive.Value(0)

    @reactive.effect
    @reactive.event(input.new_game)
    def _():
        game_instance = game()
        game_instance.new_game()
        game.set(game_instance)
        clicked_card.set(None)
        game_info_message.set("New game started")
        debug_message.set("New game started")
        game_state.set(game_state() + 1)

    @reactive.effect
    @reactive.event(input.new_round)
    def _():
        game_instance = game()
        result = game_instance.new_round()
        game.set(game_instance)
        game_info_message.set("New round started")
        debug_message.set(result)
        game_state.set(game_state() + 1)

    @render.ui
    @reactive.event(game_state)
    def cards():
        rows = game().rows
        return ui.div(
            ui.tags.style(
                """
                .card-container { display: flex; flex-direction: column; }
                .card-row { display: flex; justify-content: flex-start; margin-bottom: 20px; }
                .card { margin-right: 4px; cursor: pointer; width: 90px; height: 126px; }
            """
            ),
            ui.div(
                {"class": "card-container"},
                [
                    ui.div(
                        {"class": "card-row"},
                        [
                            ui.div(
                                ui.img(
                                    {
                                        "src": card.image_url(),
                                        "draggable": "true",
                                        "ondragstart": "dragStart(event)",
                                        "ondrop": "drop(event)",
                                        "ondragover": "allowDrop(event)",
                                        "id": f"{card.value}:{card.suit}",
                                        "style": "width: 90px; height: 126px;",
                                    }
                                ),
                                class_="card",
                            )
                            for card in row
                        ],
                    )
                    for row in rows
                ],
            ),
        )

    @reactive.effect
    @reactive.event(input.swap_cards)
    def _():
        if input.swap_cards():
            game_instance = game()
            result = game_instance.handle_swap(
                input.swap_cards()["source"], input.swap_cards()["target"]
            )
            game.set(game_instance)
            debug_message.set(result)
            game_state.set(game_state() + 1)  # Trigger UI update

    @render.text
    def debug_output():
        return debug_message()

    @render.text
    @reactive.event(game_state)
    def game_info_output():
        return game().game_info_message


app_dir = Path(__file__).parent

app = App(app_ui, server, static_assets=app_dir / "www")
