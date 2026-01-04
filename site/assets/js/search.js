(function ($) {
    var $window = $(window),
        $body = $('body'),
        $searchInput = $('#search-input');

    if (!$searchInput.length) return;

    $searchInput.on('keypress', function (e) {
        if (e.which == 13) { // Enter key
            var query = $(this).val().toLowerCase().trim();
            if (query.length >= 3) {
                performSearch(query);
            }
        }
    });

    function performSearch(query) {
        // Find the site root by looking at the script tags
        var script = document.querySelector('script[src*="jquery.min.js"]');
        var prefix = script ? script.getAttribute('src').replace('assets/js/jquery.min.js', '') : '';
        var jsonPath = prefix + 'content.json';

        fetch(jsonPath)
            .then(response => response.json())
            .then(data => {
                var results = data.filter(item => {
                    return item.title.toLowerCase().includes(query) ||
                        item.summary.toLowerCase().includes(query) ||
                        (item.subtitle && item.subtitle.toLowerCase().includes(query));
                });
                renderResults(results, query, prefix);
            })
            .catch(err => console.error('Search error:', err));
    }

    function renderResults(results, query, prefix) {
        // Replace the contents of the page
        // Specifically, everything inside .inner except the header and search box
        var $inner = $('#main .inner');
        $inner.children().not('#header, #search-bar').remove();

        var html = '<section><header class="major"><h2>Search Results for "' + query + '"</h2></header>';

        if (results.length === 0) {
            html += '<p>No results found.</p>';
        } else {
            html += '<div class="posts">';
            results.forEach(item => {
                var url = prefix + item.url.replace(/index\.html$/, '');
                var imgUrl = prefix + item.image;
                html += '<article>';
                html += '    <a href="' + url + '" class="image"><img src="' + imgUrl + '" alt="" /></a>';
                html += '    <h3><a href="' + url + '">' + item.title + '</a></h3>';
                html += '    <p>' + item.summary + '</p>';
                html += '    <ul class="actions"><li><a href="' + url + '" class="button">More</a></li></ul>';
                html += '</article>';
            });
            html += '</div>';
        }
        html += '</section>';

        $inner.append(html);

        // Update URL hash or title? Optional, but let's keep it simple as requested.
        document.title = 'Search: ' + query + ' - Insert Coin';

        // Scroll to top
        window.scrollTo(0, 0);
    }

})(jQuery);
