import yaml
import markdown
from pathlib import Path
import shutil
import argparse
import json
import re
from datetime import datetime

def generate_blog_posts(config_file='blog-posts.yaml', template_file='template-blog.html', output_dir='blog', index_file='index.html'):
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Read template
    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Read posts configuration
    with open(config_file, 'r', encoding='utf-8') as f:
        posts = yaml.safe_load(f)
    
    # Prepare post list for the index
    post_list = []
    
    # Generate each post
    for post in posts:
        # Convert markdown content to HTML
        content_html = markdown.markdown(post['content'], extensions=['extra'])
        
        # Get current date if not specified
        post_date = post.get('date', datetime.now().strftime('%Y-%m-%d'))
        modified_date = post.get('modified_date', post_date)
        
        # Create a slug if not provided
        slug = post.get('slug', post['title'].lower().replace(' ', '-').replace("'", '').replace('"', ''))
        
        # Fill template with basic content
        post_html = template.replace('{{title}}', post['title'])
        post_html = post_html.replace('{{image}}', post['image'])
        post_html = post_html.replace('{{content}}', content_html)
        
        # Add SEO meta tags
        post_html = post_html.replace('{{description}}', post.get('description', f"Learn about {post['title']} with Quentin Walking Tour in Lyon"))
        post_html = post_html.replace('{{keywords}}', post.get('keywords', f"Lyon, tour, {post['title']}, walking tour"))
        post_html = post_html.replace('{{author}}', post.get('author', 'Quentin'))
        post_html = post_html.replace('{{date}}', post_date)
        post_html = post_html.replace('{{modified_date}}', modified_date)
        post_html = post_html.replace('{{category}}', post.get('category', 'Lyon Tours'))
        
        # Generate filename from slug
        filename = f"{slug}.html"
        output_path = Path(output_dir) / filename
        
        # Write the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(post_html)
        
        # Check if image is a relative path
        image_path = Path(post['image'])
        if image_path.exists():
            # Copy image to output directory
            shutil.copy2(image_path, Path(output_dir) / image_path.name)
        
        # Add post to the list for index
        post_list.append({
            'title': post['title'],
            'url': f"{output_dir}/{filename}",
            'description': post.get('description', ''),
            'date': post_date,
            'category': post.get('category', 'Lyon Tours')
        })
    
    # Sort posts by date (newest first)
    # post_list.sort(key=lambda x: x['date'], reverse=True)
    
    # Update the index.html with the blog post list
    if Path(index_file).exists():
        update_index_with_posts(index_file, post_list)

def update_index_with_posts(index_file, post_list):
    # Read the index file
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encode the content to prevent issues with special characters (like emojis)
    content = content.encode('unicode_escape').decode('utf-8')

    # Create the JavaScript array of blog posts
    blog_posts_js = json.dumps(post_list, indent=2)
    
    # Replace the placeholder in the script section
    if 'const blogPosts = [' in content:
        # Use regex to replace the existing array with the updated one
        pattern = r'const blogPosts = \[.*?\];'
        replacement = f'const blogPosts = {blog_posts_js};'
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # If the blog section doesn't exist yet, don't modify the file
        print("Blog posts section not found in index.html")
        return
    
        # Decode back the Unicode escape sequences into actual characters
    updated_content = updated_content.encode('utf-8').decode('unicode_escape')
    
    # Write the updated content back to the index file
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