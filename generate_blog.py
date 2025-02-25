import yaml
import markdown
from pathlib import Path
import shutil
import argparse

def generate_blog_posts(config_file='blog-posts.yaml', template_file='template-blog.html', output_dir='blog'):
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Read template
    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Read posts configuration
    with open(config_file, 'r', encoding='utf-8') as f:
        posts = yaml.safe_load(f)
    
    # Generate each post
    for post in posts:
        # Convert markdown content to HTML
        content_html = markdown.markdown(post['content'])
        
        # Fill template
        post_html = template.replace('{{title}}', post['title'])
        post_html = post_html.replace('{{image}}', post['image'])
        post_html = post_html.replace('{{content}}', content_html)
        
        # Generate filename from title
        filename = post['title'].lower().replace(' ', '-') + '.html'
        output_path = Path(output_dir) / filename
        
        # Write the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(post_html)
        
        # Check if image is a relative path
        image_path = Path(post['image'])
        if image_path.exists():
            # Copy image to output directory
            shutil.copy2(image_path, Path(output_dir) / image_path.name)

def main():
    parser = argparse.ArgumentParser(description='Generate static blog posts')
    parser.add_argument('--config_file', default='blog-posts.yaml', help='YAML file containing blog post data')
    parser.add_argument('--template_file', default='template-blog.html', help='HTML template file')
    parser.add_argument('--output_dir', default='blog', help='Output directory for generated files')
    args = parser.parse_args()
    
    generate_blog_posts(
        config_file=args.config_file,
        template_file=args.template_file,
        output_dir=args.output_dir
    )

if __name__ == '__main__':
    main()


