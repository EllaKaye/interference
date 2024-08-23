from shiny import App, ui, render, reactive
from typing import Optional

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
    def __init__(self, deck):
        super().__init__()
        for i in range(4):
            self.append(deck[i*13:(i+1)*13])

    def is_valid_move(self, card1, card2):
        if card1.suit == card2.suit or card1.value == card2.value:
            return True
        return False

def get_deck():
    values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    return [Card(value, suit) for suit in suits for value in values]

app_ui = ui.page_fluid(
    ui.h1("Deck of Cards"),
    ui.output_ui("card_grid"),
    ui.input_text("clicked_card", "Clicked Card", value=""),
    ui.output_text("clicked_card_info")
)

def server(input, output, session):
    deck = reactive.Value(get_deck())
    clicked_card = reactive.Value(None)

    @output
    @render.ui
    def card_grid():
        rows = Rows(deck.get())
        ui_rows = []
        for row_index, row in enumerate(rows):
            ui_row = ui.div(
                {"class": "d-flex justify-content-between mb-2"},
                [ui.input_action_button(
                    f"card_{row_index}_{col_index}",
                    "",
                    style=f"background-image: url({card.image_url()}); background-size: cover; width: 7%; height: 100px; border: none;",
                    onclick=f"Shiny.setInputValue('clicked_card', '{card.value}:{card.suit}');"
                ) for col_index, card in enumerate(row)]
            )
            ui_rows.append(ui_row)
        return ui.div(
            ui_rows,
            ui.tags.style("#clicked_card { display: none; }")
        )

    @reactive.Effect
    @reactive.event(input.clicked_card)
    def update_clicked_card():
        if input.clicked_card():
            value, suit = input.clicked_card().split(":")
            new_card = Card(value, suit)
            clicked_card.set(new_card)

    @output
    @render.text
    def clicked_card_info():
        card = clicked_card.get()
        if card:
            return f"Clicked card: {card.value} of {card.suit}"
        return "No card clicked yet"

app = App(app_ui, server)
