from shiny import ui

with open("about.md", "r") as file:
    about = file.read()

with open("instructions.md", "r") as file:
    instructions = file.read()

interference_panel = ui.nav_panel(
        "interference",
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
            )
        )
    )
    

def md_panel(id, md):
    return ui.nav_panel(
    id, 
    ui.row(
        ui.column(
            8, 
            ui.markdown(md), 
            offset=2
        )
    )
)

app_ui = ui.page_navbar(
    interference_panel,
    md_panel("instructions", instructions),
    md_panel("about", about),
    header = ui.tags.head(
        ui.tags.link(rel="stylesheet", href="styles.css"),
        ui.tags.link(rel="stylesheet", href="https://fonts.googleapis.com/css?family=Figtree"),
        ui.tags.script(src="js/drag-drop.js"),
        ui.tags.script(src="js/md-navigation.js"),
        ui.tags.style(
            """
            .modal-content { background-color: #156645 !important; }
            .card-container { display: flex; flex-direction: column; }
            .card-row { display: flex; justify-content: flex-start; margin-bottom: 20px; }
            .card { margin-right: 4px; cursor: pointer; width: 90px; height: 126px; }
            .card-playable:hover { transform: translateY(-1px); z-index: 10; }
            img { opacity: 1 !important; }
            """)
    )
)
