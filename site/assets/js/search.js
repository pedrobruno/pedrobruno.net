(function ($) {
    var $window = $(window),
        $body = $('body'),
        $searchInput = $('#search-input');

    if (!$searchInput.length) return;

    window.SiteSearch = {
        getPrefix: function () {
            var script = document.querySelector('script[src*="jquery.min.js"]');
            return script ? script.getAttribute('src').replace('assets/js/jquery.min.js', '') : '';
        },

        performSearch: function (query) {
            var prefix = this.getPrefix();
            var jsonPath = prefix + 'content.json';

            fetch(jsonPath)
                .then(response => response.json())
                .then(data => {
                    var results = data.posts.filter(item => {
                        return item.title.toLowerCase().includes(query) ||
                            item.summary.toLowerCase().includes(query) ||
                            (item.subtitle && item.subtitle.toLowerCase().includes(query));
                    });
                    this.renderResults(results, 'Search Results for "' + query + '"', prefix, 'Search: ' + query);
                })
                .catch(err => console.error('Search error:', err));
        },

        renderResults: function (results, title, prefix, pageTitle) {
            // Replace the contents of the page
            // Specifically, everything inside .inner except the header and search box
            var $inner = $('#main .inner');
            $inner.children().not('#header, #search-bar').remove();

            var html = '<section><header class="major"><h2>' + title + '</h2></header>';

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

            if (pageTitle) {
                document.title = pageTitle + ' - Insert Coin';
            }

            window.scrollTo(0, 0);
        }
    };

    $searchInput.on('keypress', function (e) {
        if (e.which == 13) { // Enter key
            var query = $(this).val().toLowerCase().trim();
            if (query.length >= 3) {
                window.SiteSearch.performSearch(query);
            }
        }
    });

})(jQuery);
