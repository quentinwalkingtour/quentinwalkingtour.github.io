import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import markdown
import yaml


def generate_blog_posts(config_file='blog-posts.yaml', template_file='template-blog.html', output_dir='blog', index_file='index.html'):
    Path(output_dir).mkdir(exist_ok=True)

    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()

    with open(config_file, 'r', encoding='utf-8') as f:
        posts = yaml.safe_load(f)

    post_list = []

    for post in posts:
        content_html = markdown.markdown(post['content'], extensions=['extra'])
        post_date = post.get('date', datetime.now().strftime('%Y-%m-%d'))
        modified_date = post.get('modified_date', post_date)
        slug = post.get('slug', post['title'].lower().replace(' ', '-').replace("'", '').replace('"', ''))

        post_html = template.replace('{{title}}', post['title'])
        post_html = post_html.replace('{{image}}', post['image'])
        post_html = post_html.replace('{{content}}', content_html)
        post_html = post_html.replace('{{slug}}', slug)
        post_html = post_html.replace('{{description}}', post.get('description', f"Useful Paris tips about {post['title']} from Quentin"))
        post_html = post_html.replace('{{keywords}}', post.get('keywords', f"Paris, Paris walking tour, {post['title']}, local Paris guide"))
        post_html = post_html.replace('{{author}}', post.get('author', 'Quentin'))
        post_html = post_html.replace('{{date}}', post_date)
        post_html = post_html.replace('{{modified_date}}', modified_date)
        post_html = post_html.replace('{{category}}', post.get('category', 'Paris Guides'))

        filename = f"{slug}.html"
        output_path = Path(output_dir) / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(post_html)

        image_path = Path(post['image'])
        if image_path.exists():
            destination = Path(output_dir) / image_path.name
            if image_path.resolve() != destination.resolve():
                shutil.copy2(image_path, destination)

        post_list.append({
            'title': post['title'],
            'url': f"{output_dir}/{filename}",
            'description': post.get('description', ''),
            'date': post_date,
            'category': post.get('category', 'Paris Guides')
        })

    if Path(index_file).exists():
        update_index_with_posts(index_file, post_list)


def update_index_with_posts(index_file, post_list):
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()

    blog_posts_js = json.dumps(post_list, indent=2)

    if 'const blogPosts = [' in content:
        pattern = r'const blogPosts = \[.*?\];'
        replacement = f'const blogPosts = {blog_posts_js};'
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        print('Blog posts section not found in index.html')
        return

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)


def main():
    parser = argparse.ArgumentParser(description='Generate static blog posts')
    parser.add_argument('--config_file', default='blog-posts.yaml', help='YAML file containing blog post data')
    parser.add_argument('--template_file', default='template-blog.html', help='HTML template file')
    parser.add_argument('--output_dir', default='blog', help='Output directory for generated files')
    parser.add_argument('--index_file', default='index.html', help='Index file to update with blog posts')
    args = parser.parse_args()

    generate_blog_posts(
        config_file=args.config_file,
        template_file=args.template_file,
        output_dir=args.output_dir,
        index_file=args.index_file
    )


if __name__ == '__main__':
    main()
