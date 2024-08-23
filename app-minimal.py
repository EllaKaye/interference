from shiny import App, ui, render, reactive
from typing import List, Optional

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def image_url(self):
        if self.value == "Blank":
            return "blank.png"
        value = "0" if self.value == "10" else self.value
        return f"https://deckofcardsapi.com/static/img/{value}{self.suit[0]}.png"

class Rows(list):
    def __init__(self, deck: List[Card]):
        super().__init__()
        for i in range(4):
            self.append(deck[i*13:(i+1)*13])

    def is_valid_move(self, card1, card2):
        if card1.suit == card2.suit or card1.value == card2.value:
            return True
        return False

def get_deck() -> List[Card]:
    values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    return [Card(value, suit) for suit in suits for value in values]

app_ui = ui.page_fluid(
    ui.h1("Deck of Cards"),
    ui.output_ui("card_grid")
)

def server(input, output, session):
    clicked_card: reactive.Value[Optional[Card]] = reactive.Value(None)

    @output
    @render.ui
    def card_grid():
        deck = get_deck()
        rows = Rows(deck)
        ui_rows = []
        for row in rows:
            ui_row = ui.div(
                {"class": "d-flex justify-content-between mb-2"},
                [ui.img(src=card.image_url(), style="width: 7%; height: auto;") for card in row]
            )
            ui_rows.append(ui_row)
        return ui.div(ui_rows)

app = App(app_ui, server)
