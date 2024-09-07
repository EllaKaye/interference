let selectedCard = null;

$(document).on('click', function(event) {
    if (!$(event.target).closest('.card').length) {
        // If the click is outside any card, deselect the current card
        if (selectedCard) {
            $(selectedCard).removeClass('selected');
            selectedCard = null;
            Shiny.setInputValue('card_clicked', null, {priority: 'event'});
        }
    }
});

$(document).on('click', '.card', function() {
    let cardData = $(this).find('img').attr('data-card');
    console.log("Card clicked:", cardData);

    if (selectedCard === null) {
        // If no card is selected, select this card
        selectedCard = this;
        $(this).addClass('selected');
    } else if (this !== selectedCard) {
        // If a different card is clicked
        let card1 = $(selectedCard).find('img').attr('data-card');
        let card2 = cardData;
        
        if (card2.split(':')[0] !== 'Blank') {
            // If the clicked card is not a "Blank", make it the new selected card
            $(selectedCard).removeClass('selected');
            selectedCard = this;
            $(this).addClass('selected');
        } else {
            // If the clicked card is a "Blank", attempt to swap
            Shiny.setInputValue('swap_cards', {card1: card1, card2: card2}, {priority: 'event'});
            $(selectedCard).removeClass('selected');
            selectedCard = null;
        }
    } else {
        // If the same card is clicked again, deselect it
        $(this).removeClass('selected');
        selectedCard = null;
    }

    Shiny.setInputValue('card_clicked', cardData, {priority: 'event'});
});