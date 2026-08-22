# Pedro Bruno's Personal Blog

This repository contains the source code and content for [pedrobruno.net](https://pedrobruno.net). It features a custom-built Static Site Generator (SSG) in Python and the final generated static files.

## Project Structure

- **`generator/`**: The core of the site.
  - `posts/`: Source material in Markdown format, organized by year.
  - `generate.py`: The Python script that parses Markdown and generates the HTML site.
  - `*.html`: Templates used by the generator (base, item, main).
  - `generate.cmd`: Windows Batch script that sets up a virtual environment and runs the generator.
  - `publish.cmd`: Script that generates the site with minified assets and launches FileZilla for FTP transfer.
- **`site/`**: The generated output. This directory contains the complete static website ready for deployment.
  - `content/`: Generated HTML posts and their associated assets.
  - `assets/`: Global CSS, JS, and webfonts.
  - `.gitignore`: Configured to ignore the `content/` subdirectory to keep the repository size manageable.

## How to Use the Generator

To generate the site for local development or production:

1.  Make sure you have **Python 3** installed.
2.  Navigate to the `generator/` directory.
3.  Choose a script:
    -   **Local Generation**: Run `generate.cmd`. This generates the site without minifying assets.
    -   **Publish & Upload**: Run `publish.cmd`. This generates the site with minified assets and opens FileZilla with the correct server settings for transfer.

    Alternatively, if you have the dependencies installed:
    ```bash
    # Standard generation
    python generate.py -i posts -o ../site
    
    # Production generation with minification
    python generate.py -i posts -o ../site --publish
    ```

### Adding New Posts

1.  Create a new folder under `generator/posts/` (e.g., `2026`).
2.  Add a Markdown file with the following structure:
    ```markdown
    ---
    date: 2026-01-03
    ---
    # Your Post Title
    ## Optional Subtitle

    Your content goes here. You can use standard Markdown.
    ![Image Alt](image.jpg)
    ```
3.  Place any images or videos referenced in the post within the same folder.
4.  Re-run the generator script.

## Generator Features

- **Markdown Conversion**: Supports titles (`#`), subtitles (`##`), lists, bold/italic, and links.
- **Media Support**: Automatically handles images and videos. Also supports embedding YouTube videos if the image URL points to a YouTube thumbnail.
- **Homepage Generation**: Automatically features the most recent post and builds a grid of subsequent posts.
- **Automatic Archives**: Generates index pages for each year and a master archive page.
- **Post Pagination**: Automatically adds "Previous" and "Next" links to post pages.
- **Searchable Metadata**: Generates a `content.json` file for client-side functionality like the "Load More" feature.

## Development

When running with the `--publish` flag, the generator performs the following optimizations:

- **JavaScript**: Concatenates `util.js`, `main.js`, and `load-more.js` into a single `site.min.js` file and minifies it using `jsmin`.
- **CSS**: Minifies `main.css` into `main.min.css` using `cssmin`.
- **HTML Templates**: Automatically updates the site's head and footer to reference the minified assets instead of the source files.

This process is internal to `generate.py` and avoids the need for external build tools or manual concatenation.
