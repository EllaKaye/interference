// enables dragging and dropping of cards

// written by Claude 3.5 Sonnet


let dragFeedback = null;
let dragOffset = { x: 0, y: 0 };
let isDragging = false;
let originalCardSrc = null;
let draggedCardId = null;


function dragStart(event) {
    // Find and deselect any currently selected card
    const selectedCard = document.querySelector('.card.selected');
    if (selectedCard) {
        selectedCard.classList.remove('selected');
        Shiny.setInputValue('card_clicked', null, {priority: 'event'});
    }

    const card = event.target.closest('.card');
    draggedCardId = card.id;
    const cardImg = card.querySelector('img');
    originalCardSrc = cardImg.src;
    const cardData = cardImg.getAttribute('data-card');

    // Calculate offset
    const rect = cardImg.getBoundingClientRect();
    dragOffset.x = event.clientX - rect.left;
    dragOffset.y = event.clientY - rect.top;

    // Create drag feedback
    dragFeedback = new Image();
    dragFeedback.src = originalCardSrc;
    dragFeedback.style.position = 'fixed';
    dragFeedback.style.zIndex = '1000';
    dragFeedback.style.pointerEvents = 'none';
    dragFeedback.style.opacity = '1';
    dragFeedback.style.width = cardImg.offsetWidth + 'px';
    dragFeedback.style.height = cardImg.offsetHeight + 'px';
    // Position the feedback image considering the offset
    dragFeedback.style.left = (event.clientX - dragOffset.x) + 'px';
    dragFeedback.style.top = (event.clientY - dragOffset.y) + 'px';
    //dragFeedback.style.transform = 'translate(-50%, -50%)';
    document.body.appendChild(dragFeedback);

    // Set a completely transparent 1x1 pixel image as the drag image
    let emptyImage = new Image();
    emptyImage.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
    event.dataTransfer.setDragImage(emptyImage, 0, 0);

    // Notify server of drag start
    Shiny.setInputValue('drag_started', {
        cardId: cardData,
        position: [Math.floor(parseInt(draggedCardId.split('_')[1]) / 13), parseInt(draggedCardId.split('_')[1]) % 13]
    }, {priority: 'event'});

    event.dataTransfer.setData("text/plain", card.id);
    console.log("Drag started:", card.id);
    Shiny.setInputValue('dragged_card', cardData, {priority: 'event'});

    document.addEventListener('dragover', updateDragFeedback);

    Shiny.setInputValue('dragged_card', cardData, {priority: 'event'});
}


function updateDragFeedback(event) {
    if (dragFeedback) {
        // Update position considering the initial offset
        dragFeedback.style.left = (event.clientX - dragOffset.x) + 'px';
        dragFeedback.style.top = (event.clientY - dragOffset.y) + 'px';
    }
    event.preventDefault(); // Necessary to allow dropping
}


function dragEnd(event) {
    console.log("Drag ended:", draggedCardId);
    
    // Check if the card was dropped on a valid target
    const cardImg = document.getElementById(draggedCardId).querySelector('img');
    if (cardImg.src.endsWith("blank.webp")) {
        // The card is still blank, meaning it wasn't dropped on a valid target
        // We need to revert it and notify the server
        cardImg.src = originalCardSrc;
        
        Shiny.setInputValue('drag_cancelled', {
            cardId: draggedCardId,
            position: [Math.floor(parseInt(draggedCardId.split('_')[1]) / 13), parseInt(draggedCardId.split('_')[1]) % 13]
        }, {priority: 'event'});
    }
    
    // Reset drag-related variables
    Shiny.setInputValue('dragged_card', null, {priority: 'event'});
    
    draggedCardId = null;
    originalCardSrc = null;
    
    // Remove drag feedback
    if (dragFeedback && dragFeedback.parentNode) {
        document.body.removeChild(dragFeedback);
    }
    dragFeedback = null;

    document.removeEventListener('drag', updateDragFeedback);
    document.removeEventListener('dragover', updateDragFeedback);
}

/*
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
            let targetCard = targetElement.querySelector('img').getAttribute('data-card');
            console.log("Sending swap_cards event with data:", {card2: targetCard, method: 'drag'});
            Shiny.setInputValue('swap_cards', {
                card2: targetCard,
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