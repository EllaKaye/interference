// enables clicking on a link in a page rendered from markdown
// and having it switch to the corresponding page of the app

// written by Shiny Assistant

$(document).on('click', 'a[href^="#"]', function(event) {
    event.preventDefault();
    let target = $(this).attr('href').substring(1);
    $('a[data-value="' + target + '"]').tab('show');
});