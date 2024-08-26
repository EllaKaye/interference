// enables draging and droping of cards

// written by Shiny Assistant

function dragStart(event) {
    event.dataTransfer.setData("text/plain", event.target.id);
    console.log("Drag started:", event.target.id);
}

function allowDrop(event) {
    event.preventDefault();
}

function drop(event) {
    event.preventDefault();
    var sourceId = event.dataTransfer.getData("text");
    var targetId = event.target.closest('img').id;
    console.log("Drop - Source:", sourceId, "Target:", targetId);
    if (sourceId !== targetId) {
        Shiny.setInputValue('swap_cards', {source: sourceId, target: targetId}, {priority: 'event'});
    }
}