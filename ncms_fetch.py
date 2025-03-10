import json
import os
from notion_client import Client
from dotenv import load_dotenv
import subprocess
from datetime import datetime

# Load environment variables
load_dotenv()
notion = Client(auth=os.getenv('NOTION_API_KEY'))
database_id = os.getenv('NOTION_DATABASE_ID')
output_dir = os.getenv('OUTPUT_DIR')
project_dir = os.getenv('PROJECT_DIR')

# Fetch database content
def fetch_database_content(database_id):
    results = []
    has_more = True
    start_cursor = None
    while has_more:
        response = notion.databases.query(
            database_id=database_id,
            filter={"property": "Status", "select": {"equals": "publish"}},
            start_cursor=start_cursor
        )
        results.extend(response.get('results', []))
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor', None)
    return results

# Fetch page content blocks
def fetch_page_content(page_id):
    response = notion.blocks.children.list(block_id=page_id)
    content = ''
    for block in response['results']:
        block_type = block['type']
        rich_text = block[block_type].get('rich_text', [])
        # Join rich text with <br> for newlines within the block
        text = '<br>\n\t\t'.join([t['plain_text'] for t in rich_text if 'plain_text' in t])
        if block_type == 'callout' and 'icon' in block['callout'] and block['callout']['icon']['type'] == 'emoji' and block['callout']['icon']['emoji'] == '🖼️':
            content += f"<?php $alt='{text}'; require('../HTML/Fragment/Component_cover.php') ?>\n\t<h2 class='center'><?php echo $desc; ?></h2>\n"
        elif block_type == 'heading_1':
            content += f"\t<h3>{text}</h3>\n"
        elif block_type == 'paragraph' and text:
            content += f"\t<p class='first-letter-high'>\n\t\t{text}\n\t</p>\n"
        elif block_type == 'bulleted_list_item':
            content += f"\t<li><div>{text}</div></li>\n"
        elif block_type == 'numbered_list_item':
            content += f"\t<li><div>{text}</div></li>\n"
        elif block_type == 'table':
            content += "\t<table>\n"
            table_rows = notion.blocks.children.list(block_id=block['id'])['results']
            for row in table_rows:
                cells = ''.join([f"<td>{''.join([t['plain_text'] for t in cell if 'plain_text' in t])}</td>" for cell in row['table_row']['cells']])
                content += f"\t\t<tr>{cells}</tr>\n"
            content += "\t</table>\n"
    return content

# Extract fields with corrected slug handling
def extract_fields(database_content):
    articles = []
    for page in database_content:
        properties = page['properties']
        def get_rich_text(prop_name, default=""):
            prop = properties.get(prop_name, {})
            rich_text = prop.get('rich_text', [])
            return rich_text[0]['plain_text'] if rich_text else default

        slug = properties["Id"]["title"][0]["plain_text"] if properties["Id"].get("title") else ""
        article = {
            "id": page["id"],
            "status": properties["Status"]["select"]["name"] if properties["Status"].get("select") else "",
            "slug": slug,
            "label": get_rich_text("Label"),
            "title": get_rich_text("Title"),
            "js": properties["JS"]["select"]["name"] if properties["JS"].get("select") else "0",
            "description": get_rich_text("Description"),
            "content": fetch_page_content(page["id"])
        }
        if article["status"] == "publish":
            articles.append(article)
            print(f"Extracted article: Id={article['slug']}, Title={article['title']}")
    return articles

# Update ID.tsv with overwrite for existing entries
def update_id_tsv(articles, output_base):
    id_tsv_path = os.path.join(output_base, 'Config/ID.tsv')
    os.makedirs(os.path.dirname(id_tsv_path), exist_ok=True)
    
    # Read existing entries to detect updates
    existing_entries = {}
    if os.path.exists(id_tsv_path):
        with open(id_tsv_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    existing_entries[parts[1]] = line.strip()  # Key by Id

    # Update or add new entries
    with open(id_tsv_path, 'w', encoding='utf-8') as f:
        for article in articles:
            line = f"{article['status']}\t{article['slug']}\t{article['label']}\t{article['title']}\t{article['js']}\t{article['description']}"
            existing_entries[article['slug']] = line
        for entry in existing_entries.values():
            f.write(f"{entry}\n")
    print(f"Updated {id_tsv_path}")

# Update Url.tsv with overwrite for existing entries
def update_url_tsv(articles, output_base):
    url_tsv_path = os.path.join(output_base, 'Config/Url.tsv')
    os.makedirs(os.path.dirname(url_tsv_path), exist_ok=True)
    
    existing_entries = {}
    if os.path.exists(url_tsv_path):
        with open(url_tsv_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 1:
                    existing_entries[parts[0]] = line.strip()  # Key by path

    with open(url_tsv_path, 'w', encoding='utf-8') as f:
        for article in articles:
            path = article['slug'].replace('/', '\\')
            line = f"{path}\tindex\tjpg"
            existing_entries[path] = line
        for entry in existing_entries.values():
            f.write(f"{entry}\n")
    print(f"Updated {url_tsv_path}")

# Update firebase.json with dynamic rewrites and redirects
def update_firebase_json(articles, output_base):
    firebase_json_path = os.path.join(project_dir, 'build', 'firebase.json')  # Use FIREBASE_DIR
    if not os.path.exists(firebase_json_path):
        firebase_data = {
            "hosting": {
                "public": "public",
                "ignore": [".htaccess"],
                "redirects": [],
                "rewrites": []
            }
        }
    else:
        with open(firebase_json_path, 'r', encoding='utf-8') as f:
            firebase_data = json.load(f)

    if "hosting" not in firebase_data:
        firebase_data["hosting"] = {"redirects": [], "rewrites": []}
    
    # Overwrite redirects and rewrites
    redirects = []
    rewrites = []
    for article in articles:
        slug = article['slug']
        slug_parts = slug.split('/')
        if len(slug_parts) > 1:
            redirects.append({
                "source": f"/{slug_parts[-1]}",
                "destination": f"/{slug}",
                "type": 301
            })
        rewrites.extend([
            {"source": f"/{slug}.json", "destination": f"/{slug}/index.json"},
            {"source": f"/{slug}.jpg", "destination": f"/{slug}/index.jpg"}
        ])
    
    firebase_data["hosting"]["redirects"] = redirects
    firebase_data["hosting"]["rewrites"] = rewrites

    with open(firebase_json_path, 'w', encoding='utf-8') as f:
        json.dump(firebase_data, f, indent=4)
    print(f"Updated {firebase_json_path}")

# Update sitemap.xml with overwrite for existing URLs
def update_sitemap_xml(articles, output_base):
    sitemap_xml_path = os.path.join(output_base, 'Site/sitemap.xml')
    os.makedirs(os.path.dirname(sitemap_xml_path), exist_ok=True)
    base_url = "https://ujnotes.com"

    if not os.path.exists(sitemap_xml_path):
        with open(sitemap_xml_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>')

    # Read existing sitemap and overwrite with new URLs
    with open(sitemap_xml_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    urlset_start = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    urlset_end = '</urlset>'
    new_urls = [f"\t<url>\n\t\t<loc>{base_url}/{article['slug']}</loc>\n\t</url>\n" for article in articles]
    
    with open(sitemap_xml_path, 'w', encoding='utf-8') as f:
        f.write(urlset_start + ''.join(new_urls) + urlset_end)
    print(f"Updated {sitemap_xml_path} with {len(new_urls)} URLs")

# Call push_git.sh equivalent
def push_git(output_base):
    try:
        subprocess.run(["git", "add", "-A"], cwd=output_base, check=True)
        # subprocess.run(["git", "commit", "-m", f"Update articles from Notion - {subprocess.check_output(['date', '+%Y-%m-%d-%H-%M-%S']).decode().strip()}"], cwd=output_base, check=True)
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        commit_message = f"Update articles from Notion - {timestamp}"
        subprocess.run(["git", "commit", "-m", commit_message], cwd=output_base, check=True)
        subprocess.run(["git", "push", "origin", "publish"], cwd=output_base, check=True)
        print("Git push successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git push failed: {e}")
        return False

# Update Notion status to 'published'
def update_notion_status(articles):
    for article in articles:
        try:
            notion.pages.update(
                page_id=article['id'],
                properties={
                    "Status": {
                        "select": {"name": "published"}
                    }
                }
            )
            print(f"Updated status to 'published' for {article['slug']}")
        except Exception as e:
            print(f"Failed to update status for {article['slug']}: {e}")

# Transform to PHP with correct directory structure and auto-indent
def transform_to_php(articles):
    if not output_dir:
        print("Error: OUTPUT_DIR not set in .env, defaulting to 'test'")
        output_base = 'test'
    else:
        output_base = output_dir
    output_base_html = os.path.join(output_base, 'HTML/Component/')
    written_dirs = set()

    for article in articles:
        category_path = article['slug'].strip()
        if not category_path:
            category_path = article['title'].replace(' ', '_').lower()
            print(f"Warning: Empty Id for {article['title']}, using {category_path}")

        full_output_dir = os.path.join(output_base_html, category_path)
        print(f"Creating directory: {full_output_dir}")

        try:
            os.makedirs(full_output_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory {full_output_dir}: {e}")
            continue

        php_file = 'index.php'
        full_file_path = os.path.join(full_output_dir, php_file)

        if full_file_path in written_dirs:
            php_file = f"{article['title'].replace(' ', '_').lower()}.php"
            full_file_path = os.path.join(full_output_dir, php_file)
            print(f"Index.php exists, using {php_file} instead")

        written_dirs.add(full_file_path)

        js_include = "<?php require('../JS/Base/page.js'); ?>" if article['js'] == "1" else ""
        php_code_lines = [
            "<div id='message'>",
            f"\t{article['content']}",
            "</div>",
            js_include,
            "<?php require('../HTML/Fragment/Component_bottom.php') ?>"
        ]
        php_code = '\n'.join(php_code_lines)

        print(f"Writing to: {full_file_path}")
        try:
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(php_code)
        except Exception as e:
            print(f"Error writing to {full_file_path}: {e}")

    # Perform additional updates
    update_id_tsv(articles, output_dir or '.')
    update_url_tsv(articles, output_dir or '.')
    update_firebase_json(articles, output_dir or '.')
    update_sitemap_xml(articles, output_dir or '.')

    # Push to Git if all steps succeed
    if push_git(project_dir):
        update_notion_status(articles)

def write_ids_tsv(articles):
    """Write all fields (Status, Id, Label, Title, JS, Description) to a TSV file.
    Updates the row if an entry with the same Id exists; otherwise, appends a new row.
    The file is located at output/config/IDs.tsv."""
    file_path = "output/config/IDs.tsv"
    existing = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                header = lines[0].strip().split("\t")
                for line in lines[1:]:
                    fields = line.strip().split("\t")
                    if len(fields) >= 2:
                        # Assuming the second column (Id) is the path id
                        existing[fields[1]] = fields
    header_line = "Status\tId\tLabel\tTitle\tJS\tDescription\n"
    for article in articles:
        existing[article["id"]] = [article["status"], article["id"], article["label"], article["title"], article["js"], article["description"]]
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(header_line)
        for row in existing.values():
            f.write("\t".join(row) + "\n")

def main():
    if not database_id:
        print("Error: NOTION_DATABASE_ID not set in .env")
        return
    database_content = fetch_database_content(database_id)
    articles = extract_fields(database_content)
    write_ids_tsv(articles)
    transform_to_php(articles)
    print(f"Processed {len(articles)} articles")

if __name__ == "__main__":
    main()
