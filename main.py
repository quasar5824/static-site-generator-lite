import os
import re
from datetime import datetime

# Simple Markdown-to-HTML converter (subset of Markdown)
def md_to_html(text):
    # Code blocks
    def replace_code_block(match):
        code = match.group(1).strip()
        return f'<pre style="background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; font-family: monospace;"><code>{code}</code></pre>'
    
    text = re.sub(r'```(.*?)```', replace_code_block, text, flags=re.DOTALL)

    # Headers
    text = re.sub(r'^# (.*)$', r'<h1 style="margin-bottom: 0.5em">\1</h1>', text, flags=re.M)
    text = re.sub(r'^## (.*)$', r'<h2 style="margin-bottom: 0.5em">\1</h2>', text, flags=re.M)
    text = re.sub(r'^### (.*)$', r'<h3 style="margin-bottom: 0.5em">\1</h3>', text, flags=re.M)
    
    # Unordered Lists
    def replace_ul(match):
        lines = match.group(0).split('\n')
        items = [f'<li>{line.strip("-* ") }</li>' for line in lines if line.strip()]
        return f'<ul>\n  ' + '\n  '.join(items) + '\n</ul>'

    text = re.sub(r'((^[-*] .*(?:\n[-*] .*)*$))', replace_ul, text, flags=re.M)

    # Ordered Lists
    def replace_ol(match):
        lines = match.group(0).split('\n')
        items = [f'<li>{re.sub(r'^\d+\.\s*', '', line)}</li>' for line in lines if line.strip()]
        return f'<ol>\n  ' + '\n  '.join(items) + '\n</ol>'

    text = re.sub(r'((^\d+\.\s+.*(?:\n\d+\.\s+.*)*$))', replace_ol, text, flags=re.M)

    # Inline Code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # Bold and Italic
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Paragraphs: split by double newline, wrap non-html blocks
    blocks = text.split('\n\n')
    processed_blocks = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if not (block.startswith('<h') or block.startswith('<ul') or block.startswith('<ol') or block.startswith('<pre')):
            block = f'<p>{block.replace("\n", " ")}</p>'
        processed_blocks.append(block)
    
    return "\n".join(processed_blocks)

def parse_frontmatter(content):
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        meta_raw, body = match.groups()
        meta = {}
        for line in meta_raw.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
        return meta, body
    return {}, content

LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }}
        nav {{ margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
        nav a {{ color: #007bff; text-decoration: none; font-weight: bold; }}
        nav a:hover {{ text-decoration: underline; }}
        h1 {{ color: #222; }}
        ul {{ margin-bottom: 1em; }}
        ol {{ margin-bottom: 1em; }}
        li {{ margin-bottom: 0.25em; }}
        p {{ margin-bottom: 1em; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-family: monospace; }}
    </style>
</head>
<body>
    <nav>
        <a href="index.html">🏠 Home</a>
    </nav>
    {content}
</body>
</html>
"""

def build():
    content_dir = 'content'
    output_dir = 'public'
    
    if not os.path.exists(content_dir):
        os.makedirs(content_dir)
        with open(f"{content_dir}/hello.md", "w") as f:
            f.write("---\ntitle: Hello World\ndate: 2023-10-27\n---\n# Welcome to my site!\nThis is a *simple* static site generated from **Markdown**.\n\n## What this supports:\n* Simple headers\n* Unordered lists\n* Bold and italic text\n\n### Try this too:\n1. Ordered lists\n2. Inline `code` snippets\n\n```python\nprint("Hello World")\n```\n\nEnjoy your minimalist blog!")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    posts = []
    for filename in os.listdir(content_dir):
        if filename.endswith('.md'):
            with open(os.path.join(content_dir, filename), 'r', encoding='utf-8') as f:
                raw = f.read()
                meta, body = parse_frontmatter(raw)
                html_body = md_to_html(body)
                
                title = meta.get('title', filename)
                slug = filename.replace('.md', '.html')
                
                with open(os.path.join(output_dir, slug), 'w', encoding='utf-8') as out:
                    out.write(LAYOUT.format(title=title, content=html_body))
                
                posts.append({'title': title, 'slug': slug, 'date': meta.get('date', 'Unknown')})

    # Generate Index
    posts.sort(key=lambda x: x['date'], reverse=True)
    index_content = "<h1 style=\"margin-bottom: 1em\">Blog Posts</h1><ul style=\"list-style: none; padding: 0;\">";
    for p in posts:
        index_content += f'<li style="margin-bottom: 10px;"><strong style="color: #666;">{p["date"]}</strong> - <a href="{p["slug"]}">{p["title"]}</a></li>'
    index_content += "</ul>"
    
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as out:
        out.write(LAYOUT.format(title="My Minimal Blog", content=index_content))

    print(f"Successfully built {len(posts)} pages to {output_dir}/")

if __name__ == "__main__":
    build()