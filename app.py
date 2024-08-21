from shiny import App, reactive, render, ui
import random

# Card constants
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]
SUIT_ICONS = {"Spades": "♠️", "Clubs": "♣️", "Hearts": "♥️", "Diamonds": "♦️"}

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __str__(self):
        return f"{self.value}{SUIT_ICONS[self.suit]}"

    def image_url(self):
        value = "0" if self.value == "10" else self.value
        return f"https://deckofcardsapi.com/static/img/{value}{self.suit[0]}.png"

class Deck:
    def __init__(self):
        self.cards = [Card(suit, value) for suit in CARD_SUITS for value in CARD_VALUES]

    def shuffle(self):
        random.shuffle(self.cards)

    def __str__(self):
        return " ".join(str(card) for card in self.cards)

    def group_by_suit(self):
        return {suit: [card for card in self.cards if card.suit == suit] for suit in CARD_SUITS}

app_ui = ui.page_fluid(
    ui.h1("Solitaire Game"),
    ui.input_action_button("shuffle", "Shuffle Deck"),
    ui.output_ui("cards"),
)

def server(input, output, session):
    deck = reactive.Value(Deck())

    @reactive.Effect
    @reactive.event(input.shuffle)
    def _():
        new_deck = Deck()
        new_deck.shuffle()
        deck.set(new_deck)

    @render.ui
    def cards():
        grouped_cards = deck().group_by_suit()
        return ui.div(
            ui.tags.style("""
                .card-container { display: flex; flex-direction: column; }
                .card-row { display: flex; justify-content: flex-start; margin-bottom: 10px; }
                .card { margin: 2px; }
            """),
            ui.div(
                {"class": "card-container"},
                [
                    ui.div(
                        {"class": "card-row"},
                        [ui.img(src=card.image_url(), style="width: 70px; height: 100px;", class_="card") for card in grouped_cards[suit]]
                    ) for suit in CARD_SUITS
                ]
            )
        )

app = App(app_ui, server)