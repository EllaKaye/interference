from shiny import ui

def card_ui(card_id, card):
    return ui.div(
        ui.img(
            src=card.image_path(),
            class_="card-image",
            draggable="true",
            **{
                "data-card": f"{card.value}:{card.suit}",
                "ondragstart": "dragStart(event)",
                "ondragend": "dragEnd(event)",
                "ondrop": "drop(event)",
                "ondragover": "allowDrop(event)",
                "ondragenter": f"dragEnter(event, '{card.value}:{card.suit}')",
                "ondragleave": "dragLeave(event)",
            }
        ),
        class_="card",
        id=card_id,
    )

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
                ui.div(
                    *[ui.div(
                        *[ui.output_ui(f"card_{i*13+j}") for j in range(13)],
                        class_="row",
                    ) for i in range(4)],
                    class_="cards-container"
                ),
                offset=1
            )
        )
    )
)

# ... (keep the rest of your UI code, including md_panel definitions)

with open("about.md", "r") as file:
    about = file.read()

with open("instructions.md", "r") as file:
    instructions = file.read()

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
        ui.tags.script(src="js/card-selection.js"),
        ui.tags.script(src="js/drag-drop.js"),
        ui.tags.script(src="js/md-navigation.js"),
        ui.tags.style(
            """
            .modal-content {
                background-color: #156645 !important;
            }
            .cards-container {
                display: grid;
                grid-template-columns: repeat(13, 1fr);
                gap: calc(2vw + 2px) 1px;
                justify-items: center;
            }
            .row {
                display: contents;
            }
            .card {
                box-shadow: none;
                border: none;
                margin: 0;
                cursor: pointer;
            }
            .card-image {
                width: 120%;
                height: auto;
                max-width: calc(100vw / 15);
            }
            .card.selected {
                box-shadow: 0 0 10px 5px rgba(0,0,255,0.5);
            }
            @media (max-width: 1200px) {
                .cards-container {
                    gap: calc(1.5vw + 5px) 1px;
                }
                .card-image {
                    max-width: calc(100vw / 14);
                }
            }
            @media (max-width: 900px) {
                .cards-container {
                    gap: calc(1vw + 5px) 1px;
                }
                .card-image {
                    max-width: calc(100vw / 13);
                }
            }
            @media (max-width: 600px) {
                .cards-container {
                    gap: calc(0.5vw + 5px) 1px;
                }
                .card-image {
                    max-width: calc(100vw / 12);
                }
            }
            """
        )
    )
)





