from shiny import App, reactive, render, ui
import random
from typing import Optional, Tuple

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
            return "https://raw.githubusercontent.com/EllaKaye/interference-shiny/main/www/blank.png"
        value = "0" if self.value == "10" else self.value
        return f"https://deckofcardsapi.com/static/img/{value}{self.suit[0]}.png"

class Row(list):
    pass

class Rows(list):
    def get_card_indices(self, card: Card) -> Tuple[int, int]:
        #print(f"calling get_card_indices for card: {card}")
        for i, row in enumerate(self):
            #print(f"Checking row {i}:")
            for j, c in enumerate(row):
                #print(f"  Comparing with card at index {j}: {c}")
                if c.suit == card.suit and c.value == card.value:
                    #print(f"Debug: card found in row {i} at index {j}")
                    return i, j
        #print("Debug: card not found in any row")
        return -1, -1  # Return invalid indices if card not found

    def get_test_card(self, card: Card) -> Optional[Card]:
        card_row, card_index = self.get_card_indices(card)
        if card_row == -1 or card_index == -1:
            return None
        if card_index == 0:
            return None  # If the card is at the start of a row, test_card should be None
        else:
            return self[card_row][card_index - 1]

    def is_valid_move(self, card1: Card, card2: Card) -> bool:
        test_card = self.get_test_card(card2)
        #print(f"Debug - is_valid_move: card1={card1}, card2={card2}, test_card={test_card}")  # Debug print
        #print(f"Debug - self.rows:")
        #for i, row in enumerate(self):
        #    print(f"Row {i}: {' '.join(str(card) for card in row)}")

        if not test_card and card1.value_int == 2:
            return True
        elif not test_card:
            return False
        elif card1.suit == test_card.suit and card1.value_int == (test_card.value_int + 1):
            return True
        else:
            return False

    def swap_cards(self, card1: Card, card2: Card):
        row1, index1 = self.get_card_indices(card1)
        row2, index2 = self.get_card_indices(card2)
        self[row1][index1], self[row2][index2] = self[row2][index2], self[row1][index1]

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

        # Game state
        self.round = 1
        #self.round_over = self.rows.all_stuck()
        #self.round_message = f"Round {self.round} of 3"
        self.game_info_message = f"Round {self.round} of 3"
        self.won = None

    def handle_click(self, clicked_card: Card) -> str:
        if clicked_card.value != "Blank" and not self.card_1 and not self.blank:
            self.card_1 = clicked_card
            return "Selected first card"
        
        elif clicked_card.value != "Blank" and self.card_1 and not self.blank:
            self.card_1 = clicked_card
            return "Changed selection"

        elif clicked_card.value == "Blank" and self.card_1 and not self.blank:
            self.blank = clicked_card

            if self.rows.is_valid_move(self.card_1, self.blank):
                self.rows.swap_cards(self.card_1, self.blank)
                self.card_1 = self.blank = None


                return "Valid move, cards swapped"
            else:
                self.card_1 = self.blank = None
                return "Invalid move"

        return "No action"

app_ui = ui.page_navbar(
    ui.nav_panel("Interference",
        ui.div(
            ui.row(
                ui.column(10,
                    ui.div(
                        ui.input_action_button("new_game", "New Game"),
                    ),
                    ui.div(
                        ui.output_text("game_info_output"),
                        style="margin-bottom: 10px; font-size: 120%"
                    ),                    
                    ui.output_ui("cards"),
                    ui.output_text("clicked_card_text"),
                    ui.output_text("debug_output"),
                    ui.output_text("card_1_and_blank"),
                    offset=1
                )
            ),
            ui.tags.script("""
            function dragStart(event) {
                event.dataTransfer.setData("text/plain", event.target.id);
                console.log("Drag started:", event.target.id);  // Debug log
            }

            function allowDrop(event) {
                event.preventDefault();
            }

            function drop(event) {
                event.preventDefault();
                var sourceId = event.dataTransfer.getData("text");
                var targetId = event.target.closest('img').id;  // Get the ID of the closest img element
                console.log("Drop - Source:", sourceId, "Target:", targetId);  // Debug log
                if (sourceId !== targetId) {
                    Shiny.setInputValue('swap_cards', sourceId + ',' + targetId, {priority: 'event'});
                }
            }
            """)            
        )
    )
)



def server(input, output, session):
    game = reactive.Value(Game())
    clicked_card: reactive.Value[Optional[Card]] = reactive.Value(None)
    debug_message = reactive.Value("")
    game_info_message = reactive.Value("")
    game_state = reactive.Value(0)
    #game_info_message.set("New game started")

    @reactive.Effect
    @reactive.event(input.new_game)
    def _():
        game_instance = game()
        game_instance.new_game()
        game.set(game_instance)
        clicked_card.set(None)
        game_info_message.set("New game started")
        debug_message.set("New game started")
        game_state.set(game_state() + 1)

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
                                    "draggable": "true",
                                    "ondragstart": "dragStart(event)",
                                    "ondrop": "drop(event)",
                                    "ondragover": "allowDrop(event)",
                                    "id": f"{card.value}:{card.suit}",
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

    @reactive.Effect
    @reactive.event(input.clicked_card)
    def _():
        if input.clicked_card():
            suit, value = input.clicked_card().split(":")
            new_card = Card(suit, value)
            clicked_card.set(new_card)
            
            game_instance = game()
            result = game_instance.handle_click(new_card)
            game.set(game_instance)
            
            debug_message.set(f"Card clicked: {suit} {value} (value_int: {new_card.value_int}). Result: {result}")
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
    @reactive.event(game_state)
    def game_info_output():
        return game().game_info_message

    @render.text
    @reactive.event(game_state)
    def card_1_and_blank():
        game_instance = game()
        card_1_str = str(game_instance.card_1) if game_instance.card_1 else "None"
        blank_str = str(game_instance.blank) if game_instance.blank else "None"
        return f"card_1: {card_1_str}, blank: {blank_str}"

app = App(app_ui, server)