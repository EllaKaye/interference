// enables dragging and dropping of cards

// written by Claude 3.5 Sonnet


let dragFeedback = null;
let isDragging = false;
let originalCardSrc = null;
let draggedCardId = null;

function dragStart(event) {
    const card = event.target.closest('.card');
    draggedCardId = card.id;
    const cardImg = card.querySelector('img');
    originalCardSrc = cardImg.src;
    
    // Change the image in the grid to blank.webp
    cardImg.src = "img/webp/blank.webp";

    event.dataTransfer.setData("text/plain", card.id);
    console.log("Drag started:", card.id);
    Shiny.setInputValue('dragged_card', cardImg.getAttribute('data-card'), {priority: 'event'});

    // Create drag feedback
    requestAnimationFrame(() => {
        if (isDragging) return;
        isDragging = true;

        // Create a new image element for drag feedback
        dragFeedback = new Image();
        dragFeedback.src = originalCardSrc;
        dragFeedback.style.position = 'fixed';
        dragFeedback.style.zIndex = '1000';
        dragFeedback.style.pointerEvents = 'none';
        dragFeedback.style.opacity = '1'; // Fully opaque
        dragFeedback.style.width = cardImg.width + 'px'; // Set width to match original card
        dragFeedback.style.height = cardImg.height + 'px'; // Set height to match original card
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

    // Prevent the default drag image
    var img = new Image();
    img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs=';
    event.dataTransfer.setDragImage(img, 0, 0);
}

function dragEnd(event) {
    console.log("Drag ended:", draggedCardId);
    
    // Revert the image if no swap occurred
    const cardImg = document.getElementById(draggedCardId).querySelector('img');
    if (cardImg.src.endsWith("blank.webp")) {
        cardImg.src = originalCardSrc;
    }
    
    Shiny.setInputValue('dragged_card', null, {priority: 'event'});
    Shiny.setInputValue('drag_ended', {
        id: draggedCardId,
        originalSrc: originalCardSrc
    }, {priority: 'event'});
    
    isDragging = false;
    draggedCardId = null;
    originalCardSrc = null;
}

/*
function dragStart(event) {
    const card = event.target.closest('.card');
    draggedCardId = card.id;
    const cardImg = card.querySelector('img');
    originalCardSrc = cardImg.src;
    
    // Change the image in the grid to blank.webp
    cardImg.src = "img/webp/blank.webp";

    event.dataTransfer.setData("text/plain", card.id);
    console.log("Drag started:", card.id);
    Shiny.setInputValue('dragged_card', cardImg.getAttribute('data-card'), {priority: 'event'});

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
    console.log("Drag ended:", draggedCardId);
    
    // Revert the image if no swap occurred
    const cardImg = document.getElementById(draggedCardId).querySelector('img');
    if (cardImg.src.endsWith("blank.webp")) {
        cardImg.src = originalCardSrc;
    }
    
    Shiny.setInputValue('dragged_card', null, {priority: 'event'});
    Shiny.setInputValue('drag_ended', {
        id: draggedCardId,
        originalSrc: originalCardSrc
    }, {priority: 'event'});
    
    isDragging = false;
    draggedCardId = null;
    originalCardSrc = null;
}
    */

function dragEnter(event, cardId) {
    event.preventDefault();
    const targetElement = event.target.closest('.card-image');
    if (targetElement) {
        const isValidTarget = targetElement.getAttribute('data-card').split(':')[0] === "Blank";
        if (isValidTarget) {
            targetElement.src = "img/webp/blank_valid.webp";
        }
    }
}

function dragLeave(event) {
    const targetElement = event.target.closest('.card-image');
    if (targetElement && targetElement.src.endsWith("blank_valid.webp")) {
        targetElement.src = "img/webp/blank.webp";
    }
}

function allowDrop(event) {
    event.preventDefault();
}

function drop(event) {
    event.preventDefault();
    var sourceId = event.dataTransfer.getData("text");
    var targetElement = event.target.closest('.card');
    if (targetElement) {
        var targetId = targetElement.id;
        console.log("Drop - Source:", sourceId, "Target:", targetId);
        if (sourceId !== targetId) {
            let sourceCard = document.getElementById(sourceId).querySelector('img').getAttribute('data-card');
            let targetCard = targetElement.querySelector('img').getAttribute('data-card');
            console.log("Sending swap_cards event with data:", {card1: sourceCard, card2: targetCard, sourceId: sourceId, targetId: targetId});
            Shiny.setInputValue('swap_cards', {
                card1: sourceCard, 
                card2: targetCard,
                sourceId: sourceId,
                targetId: targetId,
                method: 'drag'  // Indicate this was a drag-and-drop swap
            }, {priority: 'event'});
        } else {
            // If dropped on itself, revert the image
            document.getElementById(sourceId).querySelector('img').src = originalCardSrc;
        }
        let blankImage = targetElement.querySelector('img[src$="blank_valid.webp"]');
        if (blankImage) {
            blankImage.src = "img/webp/blank.webp";
        }
    } else {
        console.log("Drop outside valid target");
        // Revert the image if dropped outside a valid target
        document.getElementById(sourceId).querySelector('img').src = originalCardSrc;
    }
    Shiny.setInputValue('dragged_card', null, {priority: 'event'});

    // Remove drag feedback
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