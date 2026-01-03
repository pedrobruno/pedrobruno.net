(function () {
    let posts = [];
    let currentIndex = 7; // Indices 0-6 are already on the page (1 featured + 6 grid)
    const increment = 6;
    const container = document.querySelector('.posts');
    const button = document.getElementById('load-more-btn');
    const containerDiv = document.querySelector('.load-more-container');

    if (!button || !container) return;

    // Detect if we are on the homepage or a subpage
    // If url contains 'content/', we might need to adjust fetch path
    // But since it's injected in index.html, fetch('content.json') is fine.
    // Index.html is at the root of the site.

    fetch('content.json')
        .then(response => response.json())
        .then(data => {
            posts = data;
            // If we have fewer than 7 posts total, hide the button immediately
            if (posts.length <= currentIndex) {
                if (containerDiv) containerDiv.style.display = 'none';
            }
        })
        .catch(err => {
            console.error('Error loading content.json:', err);
            if (containerDiv) containerDiv.style.display = 'none';
        });

    button.addEventListener('click', function (e) {
        e.preventDefault();

        const nextSet = posts.slice(currentIndex, currentIndex + increment);

        nextSet.forEach(p => {
            const article = document.createElement('article');
            // Construct path based on current location
            // Since this script runs on index.html (root), relative paths in content.json work.
            article.innerHTML = `
                <a href="${p.url}" class="image"><img src="${p.image}" alt="" /></a>
                <h3>${p.title}</h3>
                <p>${p.summary}</p>
                <ul class="actions">
                    <li><a href="${p.url}" class="button">More</a></li>
                </ul>
            `;
            container.appendChild(article);
        });

        currentIndex += increment;
        if (currentIndex >= posts.length) {
            if (containerDiv) containerDiv.style.display = 'none';
        }
    });
})();
