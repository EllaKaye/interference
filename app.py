from shiny import App, reactive, render, ui
import random
from typing import Optional, Tuple
from pathlib import Path

# Card constants
CARD_VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "Blank"]
CARD_SUITS = ["S", "H", "D", "C"]
SUIT_ICONS = {"S": "♠️", "H": "♥️", "D": "♦️", "C": "♣️"}  # for nicer print method
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
            return "blank.png"
        value = "0" if self.value == "10" else self.value  # for deckofcardsapi
        return f"https://deckofcardsapi.com/static/img/{value}{self.suit}.png"


class Row(list):
    def is_stuck(self):
        """A Row is stuck if all Blanks are after Kings"""

        last_card_was_K = False

        for card in self:
            if card.value == "K":
                last_card_was_K = True
            elif card.value == "Blank":
                if not last_card_was_K:
                    return False  # Found a Blank not after a King
                # if we see a Blank after a K, or another Blank, do nothing
            else:
                last_card_was_K = False  # reset flag for any other card

        # We have looped over row and found all Blanks after Kings
        return True

    def split_index(self):
        if self[0].value != "2":  # no cards in order
            return 0

        suit = self[0].suit
        for i in range(1, len(self)):
            if self[i].suit != suit or self[i].value_int != i:
                return i
        return (
            len(self) - 1  # if row is fully ordered, allow Blank at end
        ) 

    def split(self, index):
        return self[:index], self[index:]

    def fill_row(self, deck):
        while len(self) < 13:
            self.append(deck.pop())
        return self

    def is_ordered(self):
        return self.split_index() == 12


class Rows(list):
    def get_card_indices(self, card: Card) -> Tuple[int, int]:
        for i, row in enumerate(self):
            for j, c in enumerate(row):
                if c.suit == card.suit and c.value == card.value:
                    return i, j
        return -1, -1  # Return invalid indices if card not found

    def get_test_card(self, card: Card) -> Optional[Card]:
        card_row, card_index = self.get_card_indices(card)
        if card_row == -1 or card_index == -1:
            return None
        if card_index == 0:
            return None  # If the card is at the start of a row, there's no card to test against
        else:
            return self[card_row][card_index - 1]  # the card to the left of `card`

    def is_valid_move(self, card1: Card, card2: Card) -> bool:
        test_card = self.get_test_card(card2)

        if not test_card and card1.value == "2":
            return True
        elif not test_card:
            return False
        elif card1.suit == test_card.suit and card1.value_int == (
            test_card.value_int + 1
        ):
            return True
        else:
            return False

    def swap_cards(self, card1: Card, card2: Card):
        # Only allow swaps on if valid
        if not self.is_valid_move(card1, card2):
            print(
                f"Invalid move: {card1.value}{card1.suit} with {card2.value}{card2.suit}"
            )
            return False

        row1, index1 = self.get_card_indices(card1)
        row2, index2 = self.get_card_indices(card2)
        self[row1][index1], self[row2][index2] = self[row2][index2], self[row1][index1]
        return True

    def all_stuck(self):
        return all(row.is_stuck() for row in self)

    def ordered_unordered(self):
        indices = [row.split_index() for row in self]
        split_rows = [row.split(i) for row, i in zip(self, indices)]
        ordered = [item[0] for item in split_rows]
        unordered = [element for item in split_rows for element in item[1]]
        return ordered, unordered

    def all_ordered(self):
        return all(row.is_ordered() for row in self)


class Deck:
    def __init__(self):
        self.cards = [
            Card(suit, value)
            for suit in CARD_SUITS
            for value in CARD_VALUES
        ]

    def shuffle(self):
        random.shuffle(self.cards)

    def __str__(self):
        return " ".join(str(card) for card in self.cards)

    def to_rows(self):
        rows = Rows()
        for i in range(4):
            rows.append(Row(self.cards[i * 13 : (i + 1) * 13]))
        return rows


class Game:
    def __init__(self):
        self.new_game()

    def new_game(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.rows = self.deck.to_rows()

        # Game state
        self.round = 1
        self.round_over = self.rows.all_stuck()
        self.game_info_message = f"Round {self.round} of 3"
        self.won = None

    def handle_swap(self, card1_id: str, card2_id: str) -> str:
        # Don't allow swaps if round is over (no valid swaps anyway)
        if self.round_over:
            return "Can't move card when the round/game is over"

        card1_value, card1_suit = card1_id.split(":")
        card2_value, card2_suit = card2_id.split(":")

        card1 = Card(card1_suit, card1_value)
        card2 = Card(card2_suit, card2_value)

        if self.rows.swap_cards(card1, card2):
            # after swap, check new game state
            self.round_over = self.rows.all_stuck()
            if self.round_over:
                self.won = self.rows.all_ordered()
                if self.won:
                    self.game_info_message = "You won!"
                elif self.round == 3 and not self.won:
                    self.game_info_message = "Game over. Click 'New Game' to try again."
                else:
                    self.game_info_message = (
                        "Round over. Click 'New Round' to continue."
                    )

            return f"Swapped {card1} with {card2}"
        else:
            return f"Invalid move: Cannot swap {card1} with {card2}"

    def new_round(self):
        if self.round == 3:
            self.game_info_message = "Out of rounds. Click 'New Game' to start again."
            return "Out of rounds"

        self.round_over = False
        self.round += 1
        self.game_info_message = f"Round {self.round} of 3"

        ordered, unordered = self.rows.ordered_unordered()
        self.rows = Rows([Row(row) for row in ordered])

        # separate out blanks from the rest
        blanks = [card for card in unordered if card.value == "Blank"]
        value_cards = [card for card in unordered if card.value != "Blank"]

        # create and shuffle a deck of the unordered cards
        unordered_deck = Deck()
        unordered_deck.cards = value_cards
        unordered_deck.shuffle()

        # deal the blanks
        for row in self.rows:
            row.append(blanks.pop())

        # deal the rest of the cards
        for row in self.rows:
            row.fill_row(unordered_deck.cards)

        return f"Starting Round {self.round}"


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
        ui.tags.script(src="drag-drop.js"),
        ui.tags.script(src="md-navigation.js")
    ),
    ui.nav_panel(
        "Instructions", 
        ui.row(
            ui.column(
                10, 
                ui.markdown(instructions), 
                offset=1
            )
        )
    ),
    ui.nav_panel(
        "About", 
        ui.row(
            ui.column(
                10, 
                ui.markdown(about), 
                offset=1
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
