# The basic card UI layout in app.py
# With overlapping cards

from shiny import App, reactive, render, ui

CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "0", "J", "Q", "K"]
CARD_SUITS = ["C", "H", "S", "D"]

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def image_url(self):
        return f"https://deckofcardsapi.com/static/img/{self.value}{self.suit}.png"

class Game:
    def __init__(self):
        self.rows = [
            [Card(suit, value) for value in CARD_VALUES]
            for suit in CARD_SUITS
        ]

def server(input, output, session):
    game = reactive.Value(Game())
    game_state = reactive.Value(0)

    @render.ui
    @reactive.event(game_state)
    def cards():
        rows = game().rows
        return ui.div(
            ui.tags.style("""
                .card-container { display: flex; flex-direction: column; }
                .card-row { display: flex; justify-content: flex-start; margin-bottom: 20px; }
                .card { margin-right: 4px; cursor: pointer; width: 90px; height: 126px; }
            """),
            ui.div(
                {"class": "card-container"},
                [
                    ui.div(
                        {"class": "card-row"},
                        [
                            ui.div(
                                ui.img(
                                    {"src": card.image_url(), 
                                    "style": "width: 90px; height: 126px;"}
                                ), 
                                class_="card", 
                                onclick=f"Shiny.setInputValue('clicked_card', '{card.suit}:{card.value}')"
                            )
                            for card in row
                        ]
                    ) for row in rows
                ]
            )
        )


app_ui = ui.page_navbar(
    ui.nav_panel("Interference",
        ui.div(
            ui.row(
                ui.column(10,                   
                    ui.output_ui("cards"),
                    offset=1
                )
            )      
        )
    )
)

app = App(app_ui, server)
