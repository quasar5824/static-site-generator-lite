import os
import re
from datetime import datetime

# Simple Markdown-to-HTML converter (subset of Markdown)
def md_to_html(text):
    # Headers
    text = re.sub(r'^# (.*)$', r'<h1>\1</h1>', text, flags=re.M)
    text = re.sub(r'^## (.*)$', r'<h2>\1</h2>', text, flags=re.M)
    text = re.sub(r'^### (.*)$', r'<h3>\1</h3>', text, flags=re.M)
    # Bold and Italic
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Paragraphs
    text = re.sub(r'\n\n', r'</p><p>', text)
    return f'<p>{text}</p>'

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
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }}
        nav {{ margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        h1 {{ color: #222; }}
    </style>
</head>
<body>
    <nav><a href="index.html">Home</a></nav>
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
            f.write("---\ntitle: Hello World\ndate: 2023-10-27\n---\n# Welcome to my site!\nThis is a *simple* static site generated from **Markdown**.")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    posts = []
    for filename in os.listdir(content_dir):
        if filename.endswith('.md'):
            with open(os.path.join(content_dir, filename), 'r') as f:
                raw = f.read()
                meta, body = parse_frontmatter(raw)
                html_body = md_to_html(body)
                
                title = meta.get('title', filename)
                slug = filename.replace('.md', '.html')
                
                with open(os.path.join(output_dir, slug), 'w') as out:
                    out.write(LAYOUT.format(title=title, content=html_body))
                
                posts.append({'title': title, 'slug': slug, 'date': meta.get('date', 'Unknown')})

    # Generate Index
    posts.sort(key=lambda x: x['date'], reverse=True)
    index_content = "<h1>Blog Posts</h1><ul>"
    for p in posts:
        index_content += f'<li>{p["date"]} - <a href="{p["slug"]}">{p["title"]}</a></li>'
    index_content += "</ul>"
    
    with open(os.path.join(output_dir, 'index.html'), 'w') as out:
        out.write(LAYOUT.format(title="My Minimal Blog", content=index_content))

    print(f"Successfully built {len(posts)} pages to {output_dir}/")

if __name__ == "__main__":
    build()