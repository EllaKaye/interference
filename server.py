from shiny import reactive, ui, render
from helpers import game_over_modal, round_over_modal
from typing import Optional
from game import Card, Game

def server(input, output, session):
    game = reactive.value(Game())
    dragged_card: reactive.value[Optional[Card]] = reactive.value(None)
    debug_message = reactive.value("")
    game_info_message = reactive.value("")
    game_state = reactive.value(0)

    @reactive.effect
    @reactive.event(input.new_game)
    def _():
        ui.modal_remove()
        game_instance = game()
        game_instance.new_game()
        game.set(game_instance)
        dragged_card.set(None)
        game_info_message.set("New game started")
        debug_message.set("New game started")
        game_state.set(game_state() + 1)

    @reactive.effect
    @reactive.event(input.swap_cards)
    def _():
        if input.swap_cards():
            game_instance = game()
            card1_id, card2_id = input.swap_cards().split(',')
            result = game_instance.handle_swap(card1_id, card2_id)
            game.set(game_instance)
            debug_message.set(result)
        
        dragged_card.set(None)
        game_state.set(game_state() + 1)

    def render_card(card, currently_dragged):
        card_id = f"{card.value}:{card.suit}"
        is_dragged = card_id == currently_dragged
        
        return ui.div(
            ui.img(
                {
                    "src": "img/blank.png" if is_dragged else card.image_path(),
                    "draggable": "true",
                    "ondragstart": "dragStart(event)",
                    "ondragend": "dragEnd(event)",
                    "ondrop": "drop(event)",
                    "ondragover": "allowDrop(event)",
                    "ondragenter": f"dragEnter(event, '{card_id}')",
                    "ondragleave": "dragLeave(event)",              
                    "id": card_id,
                    "style": "width: 90px; height: 126px;",
                    "data-is-valid-target": "true" if is_valid_target(currently_dragged, card) else "false",
                }
            ),
            class_=f"card {'card-playable' if card.value != 'Blank' else ''}"
        )

    @render.ui
    @reactive.event(game_state)
    def cards():
        rows = game().rows
        currently_dragged = dragged_card.get()

        return ui.div(
            ui.tags.style(
                """
                .card-container { display: flex; flex-direction: column; }
                .card-row { display: flex; justify-content: flex-start; margin-bottom: 20px; }
                .card { margin-right: 4px; cursor: pointer; width: 90px; height: 126px; }
                .card-playable:hover { transform: translateY(-1px); z-index: 10; }
                """
            ),
            ui.div(
                {"class": "card-container"},
                [
                    ui.div(
                        {"class": "card-row"},
                        [render_card(card, currently_dragged) for card in row]
                    )
                    for row in rows
                ]
            )
        )

    def is_valid_target(dragged_card_id: str, target_card: Card) -> bool:
        if not dragged_card_id or target_card.value != "Blank":
            return False
        
        dragged_value, dragged_suit = dragged_card_id.split(":")
        dragged_card = Card(dragged_suit, dragged_value)
        
        return game().rows.is_valid_move(dragged_card, target_card)

    @reactive.effect
    @reactive.event(input.dragged_card)
    def update_dragged_card():
        dragged_card.set(input.dragged_card())
        game_state.set(game_state() + 1)

    @reactive.effect
    @reactive.event(input.drag_ended)
    def handle_drag_end():
        dragged_card.set(None)
        game_state.set(game_state() + 1)

    # ... (rest of the server code remains the same)

    @render.text
    def debug_output():
        return debug_message()

    @render.text
    @reactive.event(game_state)
    def game_info_output():
        return game().game_info_message

