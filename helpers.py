from shiny import ui

round_over = ui.modal(
    "Click 'New Round' to continue",
    title = "Round over",
    footer = ui.input_action_button("new_round_modal", "New Round")
)

def round_over_modal(title):
    m = ui.modal(  
        "Click 'New Round' to continue",  
        title = title,
        footer = ui.input_action_button("new_round_modal", "New Round"),
        size = "s")
    return m

def game_over_modal(title):
    m = ui.modal(  
        "Click 'New Game' to play again",  
        title = title,
        footer = ui.input_action_button("new_game_modal", "New Game"),
        size = "s")
    return m