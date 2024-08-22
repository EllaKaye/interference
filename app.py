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

class Game:
    def __init__(self):
        self.new_game()

    def new_game(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.rows = self.deck.to_rows()
        self.card_1: Optional[Card] = None
        self.blank: Optional[Card] = None

    def handle_click(self, clicked_card: Card):
        if self.card_1 is None and self.blank is None and clicked_card.value != "Blank":
            self.card_1 = clicked_card
        elif self.card_1 is not None and self.blank is None:
            if clicked_card.value != "Blank":
                self.card_1 = clicked_card
            else:
                self.blank = clicked_card

app_ui = ui.page_fluid(
    ui.h1("Solitaire Game"),
    ui.div(
        ui.input_action_button("new_game", "New Game"),
        style="margin-bottom: 10px;"
    ),
    ui.output_ui("cards"),
    ui.output_text("clicked_card_text"),
    ui.output_text("debug_output"),
    ui.output_text("card_1_and_blank"),
)

def server(input, output, session):
    game = reactive.Value(Game())
    clicked_card: reactive.Value[Optional[Card]] = reactive.Value(None)
    debug_message = reactive.Value("")
    game_state = reactive.Value(0)

    @reactive.Effect
    @reactive.event(input.new_game)
    def _():
        game_instance = game()
        game_instance.new_game()
        game.set(game_instance)
        clicked_card.set(None)
        debug_message.set("New game started")
        game_state.set(game_state() + 1)

    @render.ui
    @reactive.event(game_state)
    def cards():
        rows = game().rows
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

            game_instance = game()
            game_instance.handle_click(new_card)
            game.set(game_instance)
            game_state.set(game_state() + 1)  # Trigger UI update

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
    @reactive.event(game_state)  # Add this decorator to make it react to game state changes
    def card_1_and_blank():
        game_instance = game()
        card_1_str = str(game_instance.card_1) if game_instance.card_1 else "None"
        blank_str = str(game_instance.blank) if game_instance.blank else "None"
        return f"card_1: {card_1_str}, blank: {blank_str}"

app = App(app_ui, server)
