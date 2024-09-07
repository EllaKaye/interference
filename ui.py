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
        #class_="card",
        class_=f"card {'card-playable' if card.value != 'Blank' else ''}",
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


with open("about.md", "r") as file:
    about = file.read()

with open("instructions.md", "r") as file:
    instructions = file.read()

# some styles, which need to override the bootstrap defaults,
# need to be in a style tag, rather than linking to a css stylesheet in a link tag
# so read in the file here
with open("styles.css", "r") as file:
    styles = file.read()

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
        ui.tags.link(rel="stylesheet", href="https://fonts.googleapis.com/css?family=Figtree"),
        ui.tags.style(styles),  # some styles need to override bootstrap defaults so have to be in style tag
        ui.tags.script(src="js/card-selection.js"),
        ui.tags.script(src="js/drag-drop.js"),
        ui.tags.script(src="js/md-navigation.js")
    )
)





