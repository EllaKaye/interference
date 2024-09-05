// enables dragging and dropping of cards

// written by Claude 3.5 Sonnet


let dragFeedback = null;
let isDragging = false;

function dragStart(event) {
    event.dataTransfer.setData("text/plain", event.target.id);
    console.log("Drag started:", event.target.id);  // Debug log
    Shiny.setInputValue('dragged_card', event.target.id, {priority: 'event'});

    // Step 1: Immediately set a 1x1 transparent image as the drag image
    let emptyImage = new Image();
    emptyImage.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
    event.dataTransfer.setDragImage(emptyImage, 0, 0);

    // Step 2: Set up the custom drag feedback after a short delay
    requestAnimationFrame(() => {
        if (isDragging) return; // Prevent duplicate creation
        isDragging = true;

        // Create the drag feedback element
        dragFeedback = event.target.cloneNode(true);
        dragFeedback.style.position = 'fixed';
        dragFeedback.style.zIndex = '1000';
        dragFeedback.style.pointerEvents = 'none';
        dragFeedback.style.opacity = '1';
        dragFeedback.style.transform = 'translate(-50%, -50%)';
        document.body.appendChild(dragFeedback);

        function updateDragFeedback(e) {
            if (!isDragging) return;
            dragFeedback.style.left = e.clientX + 'px';
            dragFeedback.style.top = e.clientY + 'px';
        }
        
        document.addEventListener('dragover', updateDragFeedback);
        
        // Trigger initial position update
        updateDragFeedback(event);
        
        // Clean up
        function cleanUp() {
            isDragging = false;
            if (dragFeedback && dragFeedback.parentNode) {
                document.body.removeChild(dragFeedback);
            }
            dragFeedback = null;
            document.removeEventListener('dragover', updateDragFeedback);
            document.removeEventListener('dragend', cleanUp);
        }
        
        document.addEventListener('dragend', cleanUp);
    });
}

function dragEnd(event) {
    console.log("Drag ended:", event.target.id);  // Debug log
    Shiny.setInputValue('dragged_card', null, {priority: 'event'});
    Shiny.setInputValue('drag_ended', Math.random(), {priority: 'event'});
    isDragging = false;
}

// ... rest of the file remains the same

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