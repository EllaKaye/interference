let selectedCard = null;

$(document).on('click', '.card', function() {
    if (selectedCard === null) {
        selectedCard = this;
        $(this).addClass('selected');
    } else {
        let card1 = selectedCard.getAttribute('data-card');
        let card2 = this.getAttribute('data-card');
        
        if (card1 !== card2) {
            Shiny.setInputValue('swap_cards', {card1: card1, card2: card2});
        }
        
        $(selectedCard).removeClass('selected');
        selectedCard = null;
    }
});