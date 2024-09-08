from shiny import reactive, render, ui
from game import Game, Card
from helpers import game_over_modal, round_over_modal
from ui import card_ui
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def server(input, output, session):
    game = reactive.value(None)
    card_positions = reactive.value(None)
    selected_card = reactive.value(None)
    dragged_card = reactive.value(None)
    swap_method = reactive.value(None)
    
    ### set up the game
    def initialize_game():
        game_instance = Game()
        game_instance.new_game()
        game.set(game_instance)
        card_pos = [[reactive.Value(card) for card in row] for row in game_instance.rows]
        card_positions.set(card_pos)

    @reactive.effect
    def _():
        initialize_game()

    ### respond to new_game and new_round buttons
    @reactive.effect
    @reactive.event(input.new_game)
    def _():
        ui.modal_remove()
        initialize_game()
        selected_card.set(None)

    @reactive.effect
    @reactive.event(input.new_game_modal)
    def _():
        ui.modal_remove()
        initialize_game()
        selected_card.set(None)

    @reactive.effect
    @reactive.event(input.new_round)
    def _():
        ui.modal_remove()
        game_instance = game()
        result = game_instance.new_round()
        game.set(game_instance)
        card_pos = [[reactive.Value(card) for card in row] for row in game_instance.rows]
        card_positions.set(card_pos)
        selected_card.set(None)

    @reactive.effect
    @reactive.event(input.new_round_modal)
    def _():
        ui.modal_remove()
        game_instance = game()
        result = game_instance.new_round()
        game.set(game_instance)
        card_pos = [[reactive.Value(card) for card in row] for row in game_instance.rows]
        card_positions.set(card_pos)
        selected_card.set(None)

    ### display modal at end of game or round
    @reactive.effect
    def _():
        game_over_title = game().game_over_title()
        if game_over_title:
            ui.modal_show(
                game_over_modal(game_over_title)
            )

    @reactive.effect
    def _():
        round_over_title = game().round_over_title()
        if round_over_title:
            ui.modal_show(
                round_over_modal(round_over_title)
            )

    ### update round number text at the beginning of new round or game
    @render.text
    @reactive.event(lambda: game().round())  # React to changes in the round value
    def game_info_output():
        return game().game_info_message


    ### render the card as 52 individual UI elements,
    ### so that individual cards can be updated without need to re-render the whole grid
    def create_card_render(i, j):
        @output(id=f"card_{i*13+j}")
        @render.ui
        def _():
            return card_ui(f"card_{i*13+j}", card_positions()[i][j]())

    for i in range(4):
        for j in range(13):
            create_card_render(i, j)

    ## Respond to clicks and drags
    @reactive.effect
    @reactive.event(input.card_clicked)  # set in card-selection.js
    def handle_card_click():
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


    @reactive.effect
    @reactive.event(input.drag_started)
    async def handle_drag_start():
        drag_start_data = input.drag_started()
        if drag_start_data:
            if selected_card():
                selected_card.set(None)
            dragged_card.set(drag_start_data['cardId'])
            # Update the UI to show a blank card in the original position
            row, col = drag_start_data['position']
            card_positions()[row][col].set(Card('S', 'Blank'))

    @reactive.effect
    @reactive.event(input.drag_started)
    def handle_drag_start():
        drag_start_data = input.drag_started()
        if drag_start_data:
            dragged_card.set(drag_start_data['cardId'])
            # Update the UI to show a blank card in the original position
            row, col = drag_start_data['position']
            card_positions()[row][col].set(Card('S', 'Blank'))

    @reactive.effect
    @reactive.event(input.drag_ended)
    def handle_drag_end():
        drag_end_data = input.drag_ended()
        if drag_end_data and isinstance(drag_end_data, dict):
            card_id = drag_end_data['id']
            original_src = drag_end_data['originalSrc']
            # If no swap occurred, ensure the card is reverted to its original state
            parts = card_id.split('_')
            if len(parts) >= 3:
                i, j = int(parts[1]), int(parts[2])
                current_card = card_positions()[i][j]()
                if current_card.image_path() == "img/webp/blank.webp":
                    # Recreate the original card based on the original_src
                    suit = original_src.split('/')[-1].split('.')[0][-1]
                    value = original_src.split('/')[-1].split('.')[0][:-1]
                    original_card = Card(suit, value)
                    card_positions()[i][j].set(original_card)

    @reactive.effect
    @reactive.event(input.swap_cards)
    def handle_swap():
        swap_data = input.swap_cards()
        if swap_data is None:
            return

        #card1_str = swap_data['card1']
        card1_str = dragged_card()
        card2_str = swap_data['card2']
        swap_method = swap_data.get('method', 'click')

        game_instance = game()
        result = game_instance.handle_swap(card1_str, card2_str)
        game.set(game_instance)

        if result:
            # Update card positions after successful swap
            for i, row in enumerate(game_instance.rows):
                for j, card in enumerate(row):
                    card_positions()[i][j].set(card)
        elif swap_method == 'drag':
            # If drag swap was unsuccessful, revert the source card
            source_id = swap_data.get('sourceId', '')
            parts = source_id.split('_')
            if len(parts) >= 3:
                i, j = int(parts[1]), int(parts[2])
                suit, value = card1_str.split(':')
                original_card = Card(suit, value)
                card_positions()[i][j].set(original_card)
            else:
                print(f"Warning: Invalid source_id format: {source_id}")



    # Add a debug output
    @render.text
    def debug_output():
        return f"Selected card: {selected_card()}"

