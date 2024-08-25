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
        self.cards = [
            Card(suit, value)
            for suit in CARD_SUITS
            for value in CARD_VALUES
        ]

def server(input, output, session):
    game = reactive.Value(Game())
    game_state = reactive.Value(0)

    @render.ui
    @reactive.event(game_state)
    def cards():
        cards = game().cards
        return ui.div(
            ui.tags.style("""
                .card-container {
                    width: 100%;
                    overflow-x: auto;
                }
                .card-grid {
                    display: grid;
                    grid-template-columns: repeat(13, 70px);
                    grid-auto-rows: 98px;
                    gap: 5px;
                    width: max-content;
                }
                .card {
                    width: 70px;
                    height: 98px;
                    object-fit: contain;
                    cursor: pointer;
                }
                @media (max-height: 500px) {
                    .card-grid {
                        grid-auto-rows: minmax(0, 1fr);
                    }
                    .card {
                        height: auto;
                        max-height: 100%;
                    }
                }
            """),
            ui.div(
                {"class": "card-container"},
                ui.div(
                    {"class": "card-grid"},
                    *[
                        ui.img(
                            {
                                "src": card.image_url(),
                                "class": "card",
                                "onclick": f"Shiny.setInputValue('clicked_card', '{card.suit}:{card.value}')"
                            }
                        )
                        for card in cards
                    ]
                )
            )
        )

app_ui = ui.page_fluid(
    ui.h1("Responsive Card Grid"),
    ui.output_ui("cards")
)

app = App(app_ui, server)
