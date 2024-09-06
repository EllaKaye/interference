from shiny import reactive, render
from game import Game, Card
from ui import card_ui
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def server(input, output, session):
    game = reactive.Value(None)
    card_positions = reactive.Value(None)
    selected_card = reactive.Value(None)

    def initialize_game():
        game_instance = Game()
        game_instance.new_game()
        game.set(game_instance)
        card_pos = [[reactive.Value(card) for card in row] for row in game_instance.rows]
        card_positions.set(card_pos)

    @reactive.Effect
    def _():
        initialize_game()

    @reactive.Effect
    @reactive.event(input.new_game)
    def _():
        initialize_game()
        selected_card.set(None)

    @reactive.Effect
    @reactive.event(input.new_round)
    def _():
        game_instance = game()
        result = game_instance.new_round()
        game.set(game_instance)
        card_pos = [[reactive.Value(card) for card in row] for row in game_instance.rows]
        card_positions.set(card_pos)
        selected_card.set(None)

    def create_card_render(i, j):
        @output(id=f"card_{i*13+j}")
        @render.ui
        def _():
            return card_ui(f"card_{i*13+j}", card_positions()[i][j]())

    for i in range(4):
        for j in range(13):
            create_card_render(i, j)

    @reactive.Effect
    @reactive.event(input.swap_cards)
    def _():
        swap_data = input.swap_cards()
        logger.info(f"Received swap_cards event with data: {swap_data}")
        
        if swap_data is None:
            logger.warning("swap_cards event received with None data")
            return

        try:
            card1_str = swap_data['card1']
            card2_str = swap_data['card2']
        except KeyError as e:
            logger.error(f"KeyError when accessing swap_cards data: {e}")
            return

        logger.info(f"Attempting to swap cards: {card1_str} and {card2_str}")

        game_instance = game()
        try:
            result = game_instance.handle_swap(card1_str, card2_str)
            logger.info(f"Swap result: {result}")
        except ValueError as e:
            logger.error(f"ValueError in handle_swap: {e}")
            return
        except Exception as e:
            logger.error(f"Unexpected error in handle_swap: {e}")
            return

        game.set(game_instance)

        if result:
            logger.info("Updating card positions after successful swap")
            for i, row in enumerate(game_instance.rows):
                for j, card in enumerate(row):
                    card_positions()[i][j].set(card)
        else:
            logger.info("Swap was unsuccessful, not updating card positions")

    @reactive.Effect
    @reactive.event(input.card_clicked)
    def _():
        clicked_card = input.card_clicked()
        logger.info(f"Card clicked: {clicked_card}")
        
        if selected_card() is None:
            logger.info(f"Setting selected card to: {clicked_card}")
            selected_card.set(clicked_card)
        else:
            logger.info(f"Attempting to swap {selected_card()} with {clicked_card}")
            game_instance = game()
            try:
                result = game_instance.handle_swap(selected_card(), clicked_card)
                logger.info(f"Swap result: {result}")
            except ValueError as e:
                logger.error(f"ValueError in handle_swap: {e}")
                selected_card.set(None)
                return
            except Exception as e:
                logger.error(f"Unexpected error in handle_swap: {e}")
                selected_card.set(None)
                return

            game.set(game_instance)

            if result:
                logger.info("Updating card positions after successful swap")
                for i, row in enumerate(game_instance.rows):
                    for j, card in enumerate(row):
                        card_positions()[i][j].set(card)
            else:
                logger.info("Swap was unsuccessful, not updating card positions")

            selected_card.set(None)

    @render.text
    @reactive.event(game)
    def game_info_output():
        if game() is None:
            return ""
        return game().game_info_message

    # Add a debug output
    @render.text
    def debug_output():
        return f"Selected card: {selected_card()}"

    # ... (keep other reactive effects and renderers from your original server function)

# ... (keep other reactive effects and renderers from your original server function)
# def server(input, output, session):
#     game = reactive.value(Game())
#     dragged_card: reactive.value[Optional[Card]] = reactive.value(None)
#     debug_message = reactive.value("")
#     game_state = reactive.value(0)

#     @reactive.effect
#     @reactive.event(input.new_game)
#     def _():
#         ui.modal_remove()
#         game_instance = game()
#         game_instance.new_game()
#         game.set(game_instance)
#         dragged_card.set(None)
#         debug_message.set("New game started")
#         game_state.set(game_state() + 1)

#     @reactive.effect
#     @reactive.event(input.new_game_modal)
#     def _():
#         ui.modal_remove()
#         game_instance = game()
#         game_instance.new_game()
#         game.set(game_instance)
#         dragged_card.set(None)
#         debug_message.set("New game started")
#         game_state.set(game_state() + 1)

#     @reactive.effect
#     @reactive.event(input.new_round)
#     def _():
#         ui.modal_remove()
#         game_instance = game()
#         result = game_instance.new_round()
#         game.set(game_instance)
#         dragged_card.set(None)
#         debug_message.set(result)
#         game_state.set(game_state() + 1)

#     @reactive.effect
#     @reactive.event(input.new_round_modal)
#     def _():
#         ui.modal_remove()
#         game_instance = game()
#         result = game_instance.new_round()
#         game.set(game_instance)
#         dragged_card.set(None)
#         debug_message.set(result)
#         game_state.set(game_state() + 1)
    
#     @reactive.effect
#     def _():
#         game_over_title = game().game_over_title()
#         if game_over_title:
#             ui.modal_show(
#                 game_over_modal(game_over_title)
#             )

#     @reactive.effect
#     def _():
#         round_over_title = game().round_over_title()
#         if round_over_title:
#             ui.modal_show(
#                 round_over_modal(round_over_title)
#             )

#     @render.ui
#     @reactive.event(game_state, dragged_card)
#     def cards():
#         rows = game().rows
#         currently_dragged = dragged_card.get()
#         #print(f"Rendering cards. Currently dragged: {currently_dragged}")  # Debug print
#         return ui.div(
#             ui.div(
#                 {"class": "card-container"},
#                 [
#                     ui.div(
#                         {"class": "card-row"},
#                         [
#                             ui.div(
#                                 ui.img(
#                                     {
#                                         "src": "img/blank.png" if f"{card.value}:{card.suit}" == currently_dragged else card.image_path(),
#                                         "draggable": "true",
#                                         "ondragstart": "dragStart(event)",
#                                         "ondragend": "dragEnd(event)",
#                                         "ondrop": "drop(event)",
#                                         "ondragover": "allowDrop(event)",
#                                         "ondragenter": f"dragEnter(event, '{card.value}:{card.suit}')",
#                                         "ondragleave": "dragLeave(event)",              
#                                         "id": f"{card.value}:{card.suit}",
#                                         "style": "width: 90px; height: 126px;",
#                                         "data-is-valid-target": "true" if is_valid_target(currently_dragged, card) else "false",
#                                     }
#                                 ),
#                                 class_=f"card {'card-playable' if card.value != 'Blank' else ''}"
#                             )
#                             for card in row
#                         ]
#                     )
#                     for row in rows
#                 ]
#             )
#         )

#     def is_valid_target(dragged_card_id: str, target_card: Card) -> bool:
#         if not dragged_card_id or target_card.value != "Blank":
#             return False
        
#         dragged_value, dragged_suit = dragged_card_id.split(":")
#         dragged_card = Card(dragged_suit, dragged_value)
        
#         return game().rows.is_valid_move(dragged_card, target_card)

#     @reactive.effect
#     @reactive.event(input.dragged_card)
#     def update_dragged_card():
#         #print(f"Dragged card updated: {input.dragged_card()}")  # Debug print
#         dragged_card.set(input.dragged_card())
#         #print(f"Dragged card updated and set: {input.dragged_card()}")  # Debug print
#         #if input.dragged_card() is None:
#         #game_state.set(game_state() + 1) 
#         game_state.set(game_state() + 1)

#     @reactive.effect
#     @reactive.event(input.drag_ended)
#     def handle_drag_end():
#         #print("Drag ended event received")  # Debug print
#         dragged_card.set(None)
#         game_state.set(game_state() + 1)  # Trigger UI update

#     @reactive.effect
#     @reactive.event(input.swap_cards)
#     def _():
#         if input.swap_cards():
#             game_instance = game()
#             card1_id, card2_id = input.swap_cards().split(',')
#             result = game_instance.handle_swap(card1_id, card2_id)
#             game.set(game_instance)
#             debug_message.set(result)
#         dragged_card.set(None)
#         game_state.set(game_state() + 1)  # Trigger UI update


#     @render.text
#     def debug_output():
#         return debug_message()

#     @render.text
#     @reactive.event(lambda: game().round())  # React to changes in the round value
#     def game_info_output():
#         return game().game_info_message

