from shiny import App, ui, render, reactive

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

    def swap_cards(self, card1, card2):
        if not self.is_valid_move(card1, card2):
            print(f"Invalid move: {card1.value}{card1.suit} with {card2.value}{card2.suit}")
            return False

        pos1 = pos2 = None
        for i, row in enumerate(self):
            for j, card in enumerate(row):
                if card.value == card1.value and card.suit == card1.suit:
                    pos1 = (i, j)
                elif card.value == card2.value and card.suit == card2.suit:
                    pos2 = (i, j)
                if pos1 and pos2:
                    break
            if pos1 and pos2:
                break
        
        if pos1 and pos2:
            self[pos1[0]][pos1[1]], self[pos2[0]][pos2[1]] = self[pos2[0]][pos2[1]], self[pos1[0]][pos1[1]]
            print(f"Swapped cards: {card1.value}{card1.suit} with {card2.value}{card2.suit}")  # Debug print
            return True
        print(f"Failed to swap cards: {card1.value}{card1.suit} with {card2.value}{card2.suit}")  # Debug print
        return False

def get_deck():
    values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    return [Card(value, suit) for suit in suits for value in values]

app_ui = ui.page_fluid(
    ui.h1("Deck of Cards"),
    ui.output_ui("card_grid"),
    ui.output_text("debug_output"),  # Debug output
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

def server(input, output, session):
    deck = reactive.Value(Rows(get_deck()))

    @output
    @render.ui
    def card_grid():
        rows = deck.get()
        ui_rows = []
        for row_index, row in enumerate(rows):
            ui_row = ui.div(
                {"class": "d-flex justify-content-between mb-2"},
                [ui.div(
                    ui.img(
                        {"src": card.image_url(), 
                         "draggable": "true",
                         "ondragstart": "dragStart(event)",
                         "ondrop": "drop(event)",
                         "ondragover": "allowDrop(event)",
                         "id": f"{card.value}:{card.suit}",
                         "style": "width: 100%; height: 100%;"}
                    ),
                    {"style": "width: 7%; height: 100px;"}
                ) for col_index, card in enumerate(row)]
            )
            ui_rows.append(ui_row)
        return ui.div(ui_rows)

    @reactive.Effect
    @reactive.event(input.swap_cards)
    def handle_swap():
        if input.swap_cards():
            print(f"Swap cards input received: {input.swap_cards()}")  # Debug print
            card1_id, card2_id = input.swap_cards().split(',')
            card1_value, card1_suit = card1_id.split(':')
            card2_value, card2_suit = card2_id.split(':')
            card1 = Card(card1_value, card1_suit)
            card2 = Card(card2_value, card2_suit)
            current_deck = deck.get()
            if current_deck.swap_cards(card1, card2):
                deck.set(Rows(sum(current_deck, [])))  # Create a new Rows object to trigger reactivity

    @output
    @render.text
    def debug_output():
        # Display the first few cards of each row for debugging
        rows = deck.get()
        debug_str = "Current Deck State:\n"
        for i, row in enumerate(rows):
            debug_str += f"Row {i+1}: " + ", ".join([f"{card.value}{card.suit[0]}" for card in row[:5]]) + "...\n"
        return debug_str

app = App(app_ui, server)
