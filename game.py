from shiny import reactive
import random
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

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

    def image_path(self):
        if self.value == "Blank":
            return "img/blank.png"
        return f"img/{self.value}{self.suit}.png"


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
        self._round = 1  # Non-reactive round counter
        self.round = reactive.value(self._round)  # Reactive wrapper for round
        self.new_game()

    def new_game(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.rows = self.deck.to_rows()

        # Game state
        self._round = 1
        self.round.set(self._round)
        self.round_over = self.rows.all_stuck()
        self.game_info_message = f"Round {self._round} of 3"
        self.success = None
        
        # Reset reactive values
        if hasattr(self, 'game_over_title'):
            self.game_over_title.set("")
        else:
            self.game_over_title = reactive.value("")
        
        if hasattr(self, 'round_over_title'):
            self.round_over_title.set("")
        else:
            self.round_over_title = reactive.value("")


    def handle_swap(self, card1_id: str, card2_id: str) -> bool:
        logger.info(f"Handling swap for cards: {card1_id} and {card2_id}")
        
        def parse_card_id(card_id):
            parts = card_id.split(":")
            if len(parts) != 2:
                logger.error(f"Invalid card ID format: {card_id}")
                return None, None
            value, suit = parts
            return value, suit

        card1_value, card1_suit = parse_card_id(card1_id)
        card2_value, card2_suit = parse_card_id(card2_id)

        if None in (card1_value, card1_suit, card2_value, card2_suit):
            return False

        try:
            card1 = Card(card1_suit, card1_value)
            card2 = Card(card2_suit, card2_value)
        except Exception as e:
            logger.error(f"Error creating Card objects: {e}")
            return False

        if self.rows.swap_cards(card1, card2):
            logger.info("Swap successful")
            self.round_over = self.rows.all_stuck()
            if self.round_over:
                self.success = self.rows.all_ordered()
                if self.success:
                    logger.info("Game won!")
                    self.game_over_title = "Success!"
                elif self._round == 3 and not self.success:
                    logger.info("Game over")
                    self.game_over_title = "Game over"
                else:               
                    logger.info("Round over")
                    self.round_over_title = "Round over"
            return True
        else:
            logger.info("Swap unsuccessful")
            return False

    
    def new_round(self):
        if self._round == 3:
            self.game_over_title.set("Out of rounds")
            return "Out of rounds"

        self.round_over = False
        self.round_over_title.set("")
        self._round += 1
        self.round.set(self._round)
        self.game_info_message = f"Round {self.round()} of 3"

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

        return f"Starting Round {self._round}"


