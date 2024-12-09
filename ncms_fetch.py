import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv('NOTION_API_KEY'))

# Replace with your page ID
page_id = os.getenv('NOTION_PAGE_ID')

# Function to fetch a page content
def fetch_page_content(page_id):
    blocks = notion.blocks.children.list(block_id=page_id)
    return blocks


# Function to fetch database content
def fetch_database_content(database_id):
    results = []
    has_more = True
    start_cursor = None

    while has_more:
        response = notion.databases.query(
            **{
                "database_id": database_id,
                "start_cursor": start_cursor
            }
        )
        results.extend(response.get('results', []))
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor', None)

    return results


# Extract necessary fields from the database
def extract_fields(database_content):
    articles = []
    for page in database_content:
        article = {
            "id": page["id"],
            "title": page["properties"]["Name"]["title"][0]["plain_text"],
            "author": page["properties"].get("Author", {}).get("rich_text", [{}])[0].get("plain_text", ""),
            "date": page["properties"].get("Date", {}).get("date", {}).get("start", ""),
            "tags": [tag["name"] for tag in page["properties"].get("Tags", {}).get("multi_select", [])],
            "content": get_page_content(page["id"])
        }
        articles.append(article)
    return articles


def get_page_content(page_id):
    response = notion.blocks.children.list(block_id=page_id)
    content = ''
    for block in response['results']:
        if block['type'] == 'paragraph':
            text = ''.join([t['plain_text'] for t in block['paragraph']['rich_text']])
            content += text + '<br>\n'
    return content


# Function to transform Notion content to PHP
def transform_to_php(articles):
    for article in articles:
        php_code = "<?php\n\n"
        php_code += "<div id='message'>\n"
        php_code += f"\t<?php $alt='{article['title']}'; require('../HTML/Fragment/Component_cover.php') ?>\n"
        php_code += "\t<h2 class='center'>\n"
        php_code += f"\t\t<?php echo $desc; ?>\n"
        php_code += "\t</h2>\n"
        php_code += "\t<p class='first-letter-high'>\n"
        php_code += f"\t\t{article['content']}\n"
        php_code += "\t</p>\n"
        php_code += "</div>\n"
        php_code += "<?php require('../HTML/Fragment/Component_bottom.php') ?>\n"

        # Write to PHP file
        file_name = f"{article['title'].replace(' ', '_')}.php"
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(php_code)

def main():
    # database_content = fetch_database_content(page_id)
    database_content = fetch_page_content(page_id)
    articles = extract_fields(database_content)
    transform_to_php(articles)

if __name__ == "__main__":
    main()
