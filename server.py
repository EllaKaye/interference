from shiny import reactive, render, ui
from game import Game, Card
from helpers import game_over_modal, round_over_modal
from ui import card_ui
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def server(input, output, session):
    game = reactive.Value(None)
    card_positions = reactive.Value(None)
    selected_card = reactive.Value(None)
    
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

    ### swap cards
    @reactive.effect
    @reactive.event(input.swap_cards)  # updated in the drag-drop.js files
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


    @reactive.effect
    @reactive.event(input.card_clicked)  # set in card-selection.js
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


    # Add a debug output
    @render.text
    def debug_output():
        return f"Selected card: {selected_card()}"

