from shiny import App, reactive, render, ui
import random
from typing import Optional

# Card constants
CARD_VALUES = ["Blank", "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]
SUIT_ICONS = {"Spades": "♠️", "Clubs": "♣️", "Hearts": "♥️", "Diamonds": "♦️"}
VALUES_INT = {value: index for index, value in enumerate(CARD_VALUES)}

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.value_int = VALUES_INT[value]

    def __str__(self):
        return f"{self.value}{SUIT_ICONS[self.suit]}"

    def image_url(self):
        if self.value == "Blank":
            return ""
        value = "0" if self.value == "10" else self.value
        return f"https://deckofcardsapi.com/static/img/{value}{self.suit[0]}.png"

class Row(list):
    pass

class Rows(list):
    pass

class Deck:
    def __init__(self):
        self.cards = [Card(suit, value) for suit in CARD_SUITS for value in CARD_VALUES if value != "A"]

    def shuffle(self):
        random.shuffle(self.cards)

    def __str__(self):
        return " ".join(str(card) for card in self.cards)

    def to_rows(self):
        rows = Rows()
        for i in range(4):
            rows.append(Row(self.cards[i*13:(i+1)*13]))
        return rows

app_ui = ui.page_fluid(
    ui.h1("Solitaire Game"),
    ui.input_action_button("shuffle", "Shuffle Deck"),
    ui.output_ui("cards"),
    ui.output_text("clicked_card_text"),
    ui.output_text("debug_output"),
    ui.output_text("card_1_and_blank"),
)

def server(input, output, session):
    deck = reactive.Value(Deck())
    clicked_card: reactive.Value[Optional[Card]] = reactive.Value(None)
    debug_message = reactive.Value("")
    card_1: reactive.Value[Optional[Card]] = reactive.Value(None)
    blank: reactive.Value[Optional[Card]] = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.shuffle)
    def _():
        new_deck = Deck()
        new_deck.shuffle()
        deck.set(new_deck)
        card_1.set(None)
        blank.set(None)

    @render.ui
    def cards():
        rows = deck().to_rows()
        return ui.div(
            ui.tags.style("""
                .card-container { display: flex; flex-direction: column; }
                .card-row { display: flex; justify-content: flex-start; margin-bottom: 10px; }
                .card, .card-placeholder { margin: 2px; cursor: pointer; width: 70px; height: 100px; }
                .card-placeholder { background-color: #f0f0f0; border: 1px dashed #ccc; }
            """),
            ui.div(
                {"class": "card-container"},
                [
                    ui.div(
                        {"class": "card-row"},
                        [
                            ui.div(
                                ui.img(src=card.image_url(), style="width: 70px; height: 100px;") if card.value != "Blank" else "",
                                class_="card" if card.value != "Blank" else "card-placeholder",
                                onclick=f"Shiny.setInputValue('clicked_card', '{card.suit}:{card.value}')"
                            )
                            for card in row
                        ]
                    ) for row in rows
                ]
            )
        )

    @reactive.Effect
    @reactive.event(input.clicked_card)
    def _():
        if input.clicked_card():
            suit, value = input.clicked_card().split(":")
            new_card = Card(suit, value)
            clicked_card.set(new_card)
            debug_message.set(f"Card clicked: {suit} {value} (value_int: {new_card.value_int})")
            print(f"Card clicked: {suit} {value} (value_int: {new_card.value_int})")  # Debug print

            if card_1() is None and blank() is None and value != "Blank":
                card_1.set(new_card)
            elif card_1() is not None and blank() is None:
                if value != "Blank":
                    card_1.set(new_card)
                else:
                    blank.set(new_card)

    @render.text
    def clicked_card_text():
        card = clicked_card()
        if card:
            return f"You clicked on {card} (value_int: {card.value_int})"
        return "No card clicked yet"

    @render.text
    def debug_output():
        return debug_message()

    @render.text
    def card_1_and_blank():
        card_1_str = str(card_1()) if card_1() else "None"
        blank_str = str(blank()) if blank() else "None"
        return f"card_1: {card_1_str}, blank: {blank_str}"

app = App(app_ui, server)
