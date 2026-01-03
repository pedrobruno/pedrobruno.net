import os
import shutil
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Post:
    source_path: Path
    rel_path: str
    filename: str
    title: str
    subtitle: str
    body: str
    date: str
    first_image: str
    summary: str
    target_rel_url: str

class MarkdownConverter:
    @staticmethod
    def convert(md_content: str) -> Dict:
        # Extract frontmatter
        frontmatter = {}
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', md_content, flags=re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            for fm_line in fm_text.split('\n'):
                if ':' in fm_line:
                    key, val = fm_line.split(':', 1)
                    frontmatter[key.strip()] = val.strip()
        
        # Remove frontmatter for body processing
        body_md = re.sub(r'^---\s*\n.*?\n---\s*\n', '', md_content, flags=re.DOTALL)
        
        lines = body_md.split('\n')
        title = ""
        subtitle = ""
        body_lines = []
        first_image = ""
        found_h1 = found_h2 = False

        def process_inline(text):
            nonlocal first_image
            def image_replacer(match):
                nonlocal first_image
                alt, url = match.group(1), match.group(2)
                
                # YouTube support
                yt_match = re.search(r'https://i\.ytimg\.com/vi/([^/]+)', url)
                if yt_match:
                    if not first_image: first_image = url
                    video_id = yt_match.group(1)
                    return f'<iframe class="video" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
                
                # Video support
                if url.lower().endswith(('.mp4', '.webm', '.ogg')):
                    return f'<video src="{url}" controls class="image fit">Your browser does not support the video tag.</video>'
                    
                if not first_image: first_image = url
                return f'<span class="image fit"><img src="{url}" alt="{alt}"></span>'

            t = re.sub(r'!\[(.*?)\]\((.*?)\)', image_replacer, text)
            t = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', t)
            
            # Handle italics (simple version protecting HTML tags)
            parts = re.split(r'(<[^>]+>)', t)
            for i in range(len(parts)):
                if not parts[i].startswith('<'):
                    parts[i] = re.sub(r'\*(.*?)\*', r'<em>\1</em>', parts[i])
                    parts[i] = re.sub(r'_(.*?)_', r'<em>\1</em>', parts[i])
            return "".join(parts).strip()

        in_list = None
        for line in lines:
            stripped = line.strip()
            ol_match = re.match(r'^\d+\.\s+(.*)', stripped)
            ul_match = re.match(r'^[-*+]\s+(.*)', stripped)
            
            if ol_match or ul_match:
                l_type = 'ol' if ol_match else 'ul'
                l_content = ol_match.group(1) if ol_match else ul_match.group(1)
                if in_list != l_type:
                    if in_list: body_lines.append(f'</{in_list}>')
                    body_lines.append(f'<{l_type}>')
                    in_list = l_type
                body_lines.append(f'<li>{process_inline(l_content)}</li>')
                continue
            
            if in_list:
                body_lines.append(f'</{in_list}>')
                in_list = None

            if not stripped:
                if body_lines: body_lines.append('')
                continue
                
            header_match = re.match(r'^(#+)\s+(.*)', stripped)
            if header_match:
                level = len(header_match.group(1))
                text = header_match.group(2)
                if level == 1 and not found_h1:
                    title, found_h1 = text, True
                elif level == 2 and not found_h2:
                    subtitle, found_h2 = text, True
                else:
                    body_lines.append(f'<h{level}>{text}</h{level}>')
            else:
                processed = process_inline(line)
                special_starts = ('<span class="image', '<iframe', '<video')
                if any(processed.startswith(s) for s in special_starts):
                    body_lines.append(processed)
                else:
                    body_lines.append(f'<p>{processed}</p>')
        
        if in_list: body_lines.append(f'</{in_list}>')
        body_html = '\n'.join(body_lines)
        
        # Extract summary
        summary_text = re.sub(r'<[^>]+>', '', body_html)
        summary_text = re.sub(r'\s+', ' ', summary_text).strip()
        
        # Find first stop symbol that is not part of an ellipsis
        match = re.search(r'(?:(?<!\.)\.(?!\.)|[!?;])', summary_text)
        if match:
            stop_idx = match.start()
            summary = summary_text[:stop_idx + 1]
        else:
            summary = summary_text[:100]
            if len(summary_text) > 100: summary += "..."
            
        return {
            'title': title, 'subtitle': subtitle, 'body': body_html,
            'date': frontmatter.get('date', ''), 'first_image': first_image, 'summary': summary
        }

def fix_relative_paths(html: str, prefix: str) -> str:
    if not prefix: return html
    def replacer(match):
        attr, path = match.group(1), match.group(2)
        if path.startswith(('http', 'https', '/', '#')): return match.group(0)
        return f'{attr}="{prefix}{path}"'
    return re.sub(r'(href|src)="(.*?)"', replacer, html)

class SiteGenerator:
    def __init__(self, posts_dir: Path, site_dir: Path):
        self.posts_dir = posts_dir
        self.site_dir = site_dir
        self.site_content_dir = site_dir / 'content'
        self.layout_raw = ""
        self.item_template = ""
        self.main_template_raw = ""
        self.all_posts: List[Post] = []

    def load_templates(self, publish=False):
        with open('base.html', 'r', encoding='utf-8') as f:
            self.layout_raw = f.read()

        if publish:
            # Replace assets with minified versions in template
            js_replacement = '<script src="assets/js/site.min.js"></script>'
            css_replacement = '<link rel="stylesheet" href="assets/css/main.min.css" />'
            
            # Pattern for the three JS files
            js_pattern = r'<script src="assets/js/util\.js"></script>\s*<script src="assets/js/main\.js"></script>\s*<script src="assets/js/load-more\.js"></script>'
            self.layout_raw = re.sub(js_pattern, js_replacement, self.layout_raw)
            
            # Pattern for CSS
            css_pattern = r'<link rel="stylesheet" href="assets/css/main\.css" />'
            self.layout_raw = re.sub(css_pattern, css_replacement, self.layout_raw)
        
        with open('base_item.html', 'r', encoding='utf-8') as f:
            item_raw = f.read()
        
        # Cleanup item template
        item_raw = re.sub(r'<iframe.*?</iframe>', '', item_raw, flags=re.DOTALL)
        sections = list(re.finditer(r'<section>.*?</section>', item_raw, flags=re.DOTALL))
        if len(sections) >= 2:
            item_raw = item_raw.replace(sections[1].group(0), "")
        
        pattern = r'(<header class="main">.*?</header>).*?(</section>)'
        marker = r'\1\n{{BODY}}\n{{PAGINATION}}\n\2'
        item_processed = re.sub(pattern, marker, item_raw, count=1, flags=re.DOTALL)
        item_processed = item_processed.replace("Most Leaders Don't Even Know the Game They're In", "{{TITLE}}")
        item_processed = item_processed.replace("Simon Sinek", "{{SUBTITLE}}")
        
        self.item_template = self.layout_raw.replace('<content />', item_processed)

        with open('base_main.html', 'r', encoding='utf-8') as f:
            self.main_template_raw = f.read()

    def scan_posts(self):
        print(f"Scanning posts in {self.posts_dir}...")
        for root, _, files in os.walk(self.posts_dir):
            for file in files:
                if not file.lower().endswith('.md'): continue
                
                source_path = Path(root) / file
                rel_path = str(source_path.parent.relative_to(self.posts_dir))
                
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                parts = MarkdownConverter.convert(content)
                
                slug = 'index.html' if file.lower() == 'index.md' else f"{file[:-3]}.html"
                if slug == 'index.html':
                    target_rel_url = f"content/{rel_path}/" if rel_path != '.' else "content/"
                else:
                    target_rel_url = f"content/{rel_path}/{slug}"
                target_rel_url = target_rel_url.replace('\\', '/').replace('//', '/')
                
                self.all_posts.append(Post(
                    source_path=source_path, rel_path=rel_path, filename=file,
                    title=parts['title'] or "Untitled", subtitle=parts['subtitle'],
                    body=parts['body'], date=parts['date'],
                    first_image=parts['first_image'], summary=parts['summary'],
                    target_rel_url=target_rel_url
                ))
        
        self.all_posts.sort(key=lambda x: x.date, reverse=True)

    def resolve_img_url(self, post: Post) -> str:
        if not post.first_image or post.first_image.startswith(('http', 'https', '/')):
            return post.first_image
        return str(Path('content') / post.rel_path / post.first_image).replace('\\', '/')

    def build_post_grid(self, posts: List[Post], link_prefix: str = "") -> str:
        grid_html = ""
        for p in posts:
            img_url = self.resolve_img_url(p)
            url = f"{link_prefix}{p.target_rel_url}"
            grid_html += f'''
        <article>
            <a href="{url}" class="image"><img src="{link_prefix}{img_url}" alt="" /></a>
            <h3>{p.title}</h3>
            <p>{p.summary}</p>
            <ul class="actions">
                <li><a href="{url}" class="button">More</a></li>
            </ul>
        </article>'''
        return grid_html

    def generate_posts(self):
        print(f"Generating {len(self.all_posts)} posts...")
        if self.site_content_dir.exists():
            shutil.rmtree(self.site_content_dir)
        self.site_content_dir.mkdir(parents=True)

        for i, post in enumerate(self.all_posts):
            target_dir = self.site_content_dir / post.rel_path
            target_dir.mkdir(parents=True, exist_ok=True)
            
            slug = 'index.html' if post.filename.lower() == 'index.md' else f"{post.filename[:-3]}.html"
            target_file = target_dir / slug
            
            depth = Path(post.rel_path).parts
            prefix = "../" * (len(depth) + 1 if post.rel_path != '.' else 1)
            if post.rel_path == '.': prefix = "../" # Corner case for root posts

            # Pagination
            pagination_html = ""
            parts = []
            if i < len(self.all_posts) - 1:
                older = self.all_posts[i+1]
                parts.append(f'<div class="col-6 align-left"><a href="{prefix}{older.target_rel_url}">&larr; {older.title}</a><div class="pagination">Previous</div></div>')
            else:
                parts.append('<div class="col-6"></div>')
            
            if i > 0:
                newer = self.all_posts[i-1]
                parts.append(f'<div class="col-6 align-right"><a href="{prefix}{newer.target_rel_url}">{newer.title} &rarr;</a><div class="pagination">Next</div></div>')
            
            if any(p for p in parts if 'href' in p):
                pagination_html = f'<section><div class="row">{"".join(parts)}</div></section>'

            html = self.item_template.replace("{{TITLE}}", post.title)
            if post.subtitle:
                html = html.replace("{{SUBTITLE}}", post.subtitle)
            else:
                html = re.sub(r'<h2>\s*{{SUBTITLE}}\s*</h2>', '', html)
            
            html = fix_relative_paths(html, prefix)
            html = html.replace("{{BODY}}", post.body).replace("{{PAGINATION}}", pagination_html)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(html)

    def generate_homepage(self):
        print("Generating homepage...")
        featured = self.all_posts[0]
        html = self.main_template_raw
        
        # Featured section
        header_block = f'<h1>{featured.title}</h1>' + (f'\n\t\t\t<p>{featured.subtitle}</p>' if featured.subtitle else "")
        html = re.sub(r'<header>\s*<h1></h1>\s*<p></p>\s*</header>', 
                       lambda m: f'<header>\n\t\t\t{header_block}\n\t\t</header>', html, flags=re.DOTALL)
        html = html.replace('<p></p>', f'<p>{featured.summary}</p>', 1)
        html = html.replace('href="" class="button big"', f'href="{featured.target_rel_url}" class="button big"')
        html = html.replace('src=""', f'src="{self.resolve_img_url(featured)}"', 1)

        # Grid section
        grid_html = self.build_post_grid(self.all_posts[1:7])
        html = re.sub(r'<div class="posts">.*?</div>', lambda m: f'<div class="posts">{grid_html}\n\t</div>', html, flags=re.DOTALL)
        
        final_html = self.layout_raw.replace('<content />', html)
        final_html = fix_relative_paths(final_html, "")
        
        with open(self.site_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(final_html)

    def generate_json(self):
        print("Generating content.json...")
        items = [{
            'title': p.title, 'subtitle': p.subtitle, 'date': p.date,
            'summary': p.summary, 'url': p.target_rel_url, 'image': self.resolve_img_url(p)
        } for p in self.all_posts]
        with open(self.site_dir / 'content.json', 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=4, ensure_ascii=False)

    def generate_archive(self):
        print("Generating archive pages...")
        by_year = {}
        for p in self.all_posts:
            year = p.date[:4] if p.date else (p.rel_path.split('/')[0] if p.rel_path != '.' else "")
            if year and year.isdigit():
                by_year.setdefault(year, []).append(p)

        # Individual Year Pages
        for year, year_posts in by_year.items():
            grid = self.build_post_grid(year_posts, "")
            
            match = re.search(r'<!-- Section -->\s*<section>.*?</section>', self.main_template_raw, flags=re.DOTALL)
            if match:
                content = match.group(0)
                content = content.replace('<h2>Previous</h2>', f'<h2>{year}</h2>')
                content = re.sub(r'<div class="load-more-container">.*?</div>', '', content, flags=re.DOTALL)
                content = re.sub(r'<div class="posts">.*?</div>', lambda m: f'<div class="posts">{grid}\n\t</div>', content, flags=re.DOTALL)
            else:
                content = f'<section><header class="major"><h2>{year}</h2></header><div class="posts">{grid}</div></section>'

            final = fix_relative_paths(self.layout_raw.replace('<content />', content), "../../")
            (self.site_content_dir / year).mkdir(exist_ok=True)
            with open(self.site_content_dir / year / 'index.html', 'w', encoding='utf-8') as f:
                f.write(final)

        # Content Index Page
        sorted_years = sorted(by_year.keys(), reverse=True)
        links = '\n'.join([f'<li><a href="{y}/">{y}</a> <small>({len(by_year[y])} post{"s" if len(by_year[y])!=1 else ""})</small></li>' for y in sorted_years])
        archive_html = f'<section><header class="major"><h2>Archive by Year</h2></header><ul>{links}</ul></section>'
        
        final_idx = fix_relative_paths(self.layout_raw.replace('<content />', archive_html), "../")
        with open(self.site_content_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(final_idx)

    def copy_assets(self):
        print("Copying static assets...")
        for root, _, files in os.walk(self.posts_dir):
            rel = Path(root).relative_to(self.posts_dir)
            for file in files:
                if file.lower().endswith('.md'): continue
                target = self.site_content_dir / rel / file
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(Path(root) / file, target)

    def compress_js(self):
        try:
            from jsmin import jsmin
        except ImportError:
            print("Error: jsmin library not found. Please install it using 'pip install jsmin'.")
            return

        base_path = self.site_dir / 'assets' / 'js'
        files = ['util.js', 'main.js', 'load-more.js'] # Order matters for dependencies
        output_file = base_path / 'site.min.js'

        print("Concatenating and minifying JS files (publish mode)...")
        combined = ""
        for f_name in files:
            f_path = base_path / f_name
            if f_path.exists():
                with open(f_path, 'r', encoding='utf-8') as f:
                    combined += f.read() + "\n"
                print(f" - Added {f_name}")
            else:
                print(f" - Warning: {f_name} not found at {f_path}")

        if combined:
            minified = jsmin(combined)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(minified)
            print(f"Done! Created {output_file}")

    def compress_css(self):
        try:
            from cssmin import cssmin
        except ImportError:
            print("Error: cssmin library not found. Please install it using 'pip install cssmin'.")
            return

        base_path = self.site_dir / 'assets' / 'css'
        input_file = base_path / 'main.css'
        output_file = base_path / 'main.min.css'

        if input_file.exists():
            print("Minifying CSS file (publish mode)...")
            with open(input_file, 'r', encoding='utf-8') as f:
                minified = cssmin(f.read())
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(minified)
            print(f"Done! Created {output_file}")
        else:
            print(f" - Warning: main.css not found at {input_file}")

    def generate(self, publish=False):
        self.load_templates(publish=publish)
        self.scan_posts()
        self.generate_posts()
        self.generate_homepage()
        self.generate_json()
        self.generate_archive()
        self.copy_assets()
        
        if publish:
            self.compress_js()
            self.compress_css()
            
        print("Site generation completed successfully.")

def main():
    parser = argparse.ArgumentParser(description="Static Site Generator")
    parser.add_argument("-i", "--input", default="posts", help="Directory with markdown posts")
    parser.add_argument("-o", "--output", default="../site", help="Site output directory")
    parser.add_argument("-p", "--publish", action="store_true", help="Concatenate and minify JS assets")
    args = parser.parse_args()

    gen = SiteGenerator(Path(args.input), Path(args.output))
    gen.generate(publish=args.publish)

if __name__ == "__main__":
    main()
