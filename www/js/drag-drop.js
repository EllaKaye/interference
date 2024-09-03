// enables draging and droping of cards

// written by Shiny Assistant

function dragStart(event) {
    event.dataTransfer.setData("text/plain", event.target.id);
    console.log("Drag started:", event.target.id);  // Debug log
    Shiny.setInputValue('dragged_card', event.target.id, {priority: 'event'});
}

function dragEnd(event) {
    console.log("Drag ended:", event.target.id);  // Debug log
    Shiny.setInputValue('dragged_card', null, {priority: 'event'});
    Shiny.setInputValue('drag_ended', Math.random(), {priority: 'event'});
}

function dragEnter(event, cardId) {
    event.preventDefault();
    const targetElement = event.target.closest('img');
    if (targetElement) {
        const isValidTarget = targetElement.dataset.isValidTarget === "true";
        if (isValidTarget && targetElement.src.endsWith("blank.png")) {
            targetElement.src = "img/blank_valid.png";
        }
    }
}

function dragLeave(event) {
    const targetElement = event.target.closest('img');
    if (targetElement && targetElement.src.endsWith("blank_valid.png")) {
        targetElement.src = "img/blank.png";
    }
}

function allowDrop(event) {
    event.preventDefault();
}

function drop(event) {
    event.preventDefault();
    var sourceId = event.dataTransfer.getData("text");
    var targetElement = event.target.closest('img');
    if (targetElement) {
        var targetId = targetElement.id;
        console.log("Drop - Source:", sourceId, "Target:", targetId);  // Debug log
        if (sourceId !== targetId) {
            Shiny.setInputValue('swap_cards', sourceId + ',' + targetId, {priority: 'event'});
        }
        if (targetElement.src.endsWith("blank_valid.png")) {
            targetElement.src = "img/blank.png";
        }
    } else {
        console.log("Drop outside valid target");  // Debug log
    }
    Shiny.setInputValue('dragged_card', null, {priority: 'event'});
}

document.addEventListener('dragover', function(event) {
    event.preventDefault();
});

document.addEventListener('drop', function(event) {
    event.preventDefault();
    var sourceId = event.dataTransfer.getData("text");
    console.log("Drop outside grid - Source:", sourceId);  // Debug log
    Shiny.setInputValue('dragged_card', null, {priority: 'event'});
    Shiny.setInputValue('drag_ended', Math.random(), {priority: 'event'});
});

/*
function drop(event) {
    event.preventDefault();
    var sourceId = event.dataTransfer.getData("text");
    var targetId = event.target.closest('img').id;  // Get the ID of the closest img element
    console.log("Drop - Source:", sourceId, "Target:", targetId);  // Debug log
    if (sourceId !== targetId) {
        Shiny.setInputValue('swap_cards', sourceId + ',' + targetId, {priority: 'event'}); // Reset the dragged card state after a drop, regardless of whether the swap was valid or not
    }
    Shiny.setInputValue('dragged_card', null, {priority: 'event'});
}
*/


