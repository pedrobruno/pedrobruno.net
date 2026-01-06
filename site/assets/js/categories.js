(function ($) {
    const COOKIE_NAME = 'selected_categories';

    function setCookie(name, value, days) {
        let expires = "";
        if (days) {
            let date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/";
    }

    function getCookie(name) {
        let nameEQ = name + "=";
        let ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    function getSelectedCategories() {
        let cookie = getCookie(COOKIE_NAME);
        return cookie ? cookie.split(',') : [];
    }

    function toggleCategory(cat) {
        let selected = getSelectedCategories();
        let index = selected.indexOf(cat);
        if (index > -1) {
            selected.splice(index, 1);
        } else {
            selected.push(cat);
        }
        // Remove empty strings if any
        selected = selected.filter(s => s !== "");
        setCookie(COOKIE_NAME, selected.join(','), 365);
        return selected;
    }

    function updateUI() {
        let selected = getSelectedCategories();
        $('#menu a[data-category]').each(function () {
            let cat = $(this).data('category');
            if (selected.indexOf(cat) > -1) {
                $(this).addClass('selected-category');
            } else {
                $(this).removeClass('selected-category');
            }
        });
    }

    function performCategorySearch() {
        let selectedSlugs = getSelectedCategories();
        if (selectedSlugs.length === 0) {
            alert("Please select at least one category.");
            return;
        }

        if (!window.SiteSearch) {
            console.error("SiteSearch not found.");
            return;
        }

        let prefix = window.SiteSearch.getPrefix();
        let jsonPath = prefix + 'content.json';

        fetch(jsonPath)
            .then(response => response.json())
            .then(data => {
                // Map slugs to indices
                let selectedIndices = selectedSlugs.map(slug => data.categories.indexOf(slug))
                    .filter(idx => idx !== -1);

                if (selectedIndices.length === 0) {
                    window.SiteSearch.renderResults([], 'Filtered Results', prefix, 'Filtered');
                    return;
                }

                // Filter posts that match ALL selected categories
                let results = data.posts.filter(post => {
                    return selectedIndices.every(idx => post.cats.includes(idx));
                });

                let title = "Posts in: " + selectedSlugs.join(" + ");
                window.SiteSearch.renderResults(results, title, prefix, 'Category: ' + selectedSlugs.join(", "));
            })
            .catch(err => console.error('Category search error:', err));
    }

    $(function () {
        updateUI();

        $('#menu').on('click', 'a[data-category]', function (e) {
            e.preventDefault();
            let cat = $(this).data('category');
            toggleCategory(cat);
            updateUI();
        });

        $('#show-categories-btn').on('click', function (e) {
            e.preventDefault();
            performCategorySearch();
        });
    });

})(jQuery);
