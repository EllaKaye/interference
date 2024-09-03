// enables clicking on a link in a page rendered from markdown
// and having it switch to the corresponding page of the app

// written by Shiny Assistant

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're in a Shiny app
    if (window.Shiny) {
        document.querySelectorAll('a[href$=".md"]').forEach(function(link) {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                let target = this.getAttribute('href').replace('.md', '');
                // Attempt to find and click the corresponding nav link
                let navLink = document.querySelector('a[data-value="' + target + '"]');
                if (navLink) {
                    navLink.click();
                } else {
                    console.log('No matching tab found for:', target);
                }
            });
        });
    }
});

/*
$(document).on('click', 'a[href^="#"]', function(event) {
    event.preventDefault();
    let target = $(this).attr('href').substring(1);
    $('a[data-value="' + target + '"]').tab('show');
});
*/