import os
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
notion = Client(auth=os.getenv('NOTION_API_KEY'))
database_id = os.getenv('NOTION_DATABASE_ID')  # e.g., 1a2bbfdb472980c38995c450e4f0d65e
output_dir = os.getenv('OUTPUT_DIR')

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
        text = ''.join([t['plain_text'] for t in rich_text if 'plain_text' in t])
        if block_type == 'callout' and 'icon' in block['callout'] and block['callout']['icon']['type'] == 'emoji' and block['callout']['icon']['emoji'] == '🖼️':
            content += f"<?php $alt='{text}'; require('../HTML/Fragment/Component_cover.php') ?>\n<h2 class='center'><?php echo $desc; ?></h2>\n"
        elif block_type == 'heading_1':
            content += f"<h3>{text}</h3>\n"
        elif block_type == 'paragraph' and text:
            content += f"<p>{text}</p>\n"
        elif block_type == 'bulleted_list_item':
            content += f"<li><div>{text}</div></li>\n"
        elif block_type == 'numbered_list_item':
            content += f"<li><div>{text}</div></li>\n"
        elif block_type == 'table':
            content += "<table>\n"
            table_rows = notion.blocks.children.list(block_id=block['id'])['results']
            for row in table_rows:
                cells = ''.join([f"<td>{''.join([t['plain_text'] for t in cell if 'plain_text' in t])}</td>" for cell in row['table_row']['cells']])
                content += f"<tr>{cells}</tr>\n"
            content += "</table>\n"
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

        # Slug comes from 'Id' property, which is of type 'title'
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

# Transform to PHP with correct directory structure
def transform_to_php(articles):
    if not output_dir:
        print("Error: OUTPUT_DIR not set in .env, defaulting to 'HTML/Component/'")
        output_base = '.'
    else:
        output_base = output_dir
    output_base = os.path.join(output_base, 'HTML/Component/')
    written_dirs = set()  # Track written files to avoid overwriting

    for article in articles:
        # Use slug (Id) directly as the directory path
        category_path = article['slug'].strip()
        if not category_path:
            # Fallback if Id is empty
            category_path = article['title'].replace(' ', '_').lower()
            print(f"Warning: Empty Id for {article['title']}, using {category_path}")

        full_output_dir = os.path.join(output_base, category_path)
        print(f"Creating directory: {full_output_dir}")

        # Create directories
        try:
            os.makedirs(full_output_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory {full_output_dir}: {e}")
            continue

        # Use index.php as the default file name
        php_file = 'index.php'
        full_file_path = os.path.join(full_output_dir, php_file)

        # Avoid overwriting by using title if index.php exists
        if full_file_path in written_dirs:
            php_file = f"{article['title'].replace(' ', '_').lower()}.php"
            full_file_path = os.path.join(full_output_dir, php_file)
            print(f"Index.php exists, using {php_file} instead")

        written_dirs.add(full_file_path)

        # Generate PHP content
        js_include = "<?php require('../JS/Base/page.js'); ?>" if article['js'] == "1" else ""
        php_code = f"""
<div id='message'>
    {article['content']}
</div>
{js_include}
<?php require('../HTML/Fragment/Component_bottom.php') ?>

"""

        print(f"Writing to: {full_file_path}")
        try:
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(php_code.strip())
        except Exception as e:
            print(f"Error writing to {full_file_path}: {e}")

def main():
    if not database_id:
        print("Error: NOTION_DATABASE_ID not set in .env")
        return
    database_content = fetch_database_content(database_id)
    articles = extract_fields(database_content)
    transform_to_php(articles)
    print(f"Processed {len(articles)} articles")

if __name__ == "__main__":
    main()