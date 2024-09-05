// enables dragging and dropping of cards

let dragFeedback = null;

function dragStart(event) {
    event.dataTransfer.setData("text/plain", event.target.id);
    console.log("Drag started:", event.target.id);  // Debug log
    Shiny.setInputValue('dragged_card', event.target.id, {priority: 'event'});

    // Force opacity to 1
    event.target.style.opacity = '1';
    
    // Disable the default ghost image
    var emptyImage = document.createElement('img');
    emptyImage.src = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==';
    event.dataTransfer.setDragImage(emptyImage, 0, 0);
    
    // Create a visual drag feedback
    dragFeedback = event.target.cloneNode(true);
    dragFeedback.style.position = 'fixed';
    dragFeedback.style.zIndex = '1000';
    dragFeedback.style.pointerEvents = 'none';
    dragFeedback.style.opacity = '1';
    document.body.appendChild(dragFeedback);
    
    // Update the position of the drag feedback
    function updateDragFeedback(e) {
        dragFeedback.style.left = (e.clientX - dragFeedback.offsetWidth / 2) + 'px';
        dragFeedback.style.top = (e.clientY - dragFeedback.offsetHeight / 2) + 'px';
    }
    
    document.addEventListener('dragover', updateDragFeedback);
    
    // Clean up
    function cleanUp() {
        if (dragFeedback && dragFeedback.parentNode) {
            document.body.removeChild(dragFeedback);
        }
        dragFeedback = null;
        document.removeEventListener('dragover', updateDragFeedback);
        document.removeEventListener('dragend', cleanUp);
    }
    
    document.addEventListener('dragend', cleanUp);
}

function dragEnd(event) {
    console.log("Drag ended:", event.target.id);  // Debug log
    Shiny.setInputValue('dragged_card', null, {priority: 'event'});
    Shiny.setInputValue('drag_ended', Math.random(), {priority: 'event'});
    
    // Reset opacity
    event.target.style.opacity = '';

    // Ensure dragFeedback is removed
    if (dragFeedback && dragFeedback.parentNode) {
        document.body.removeChild(dragFeedback);
    }
    dragFeedback = null;
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

    // Ensure dragFeedback is removed
    if (dragFeedback && dragFeedback.parentNode) {
        document.body.removeChild(dragFeedback);
    }
    dragFeedback = null;
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

    // Ensure dragFeedback is removed
    if (dragFeedback && dragFeedback.parentNode) {
        document.body.removeChild(dragFeedback);
    }
    dragFeedback = null;
});