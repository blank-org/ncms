import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv('NOTION_API_KEY'))

# Function to fetch a page content
def fetch_page_content(page_id):
    blocks = notion.blocks.children.list(block_id=page_id)
    return blocks

# Function to transform Notion content to PHP
def transform_to_php(notion_content):
    php_code = "<?php\n\n"
    for block in notion_content['results']:
        if block['type'] == 'paragraph':
            text = ''.join([t['text']['content'] for t in block['paragraph']['rich_text']])
            php_code += f"// {text}\n"
        elif block['type'] == 'heading_1':
            text = ''.join([t['text']['content'] for t in block['heading_1']['rich_text']])
            php_code += f"// {text}\n"
        # Add more transformations based on block types
    php_code += "\n?>"
    return php_code

# Replace with your page ID
page_id = os.getenv('NOTION_PAGE_ID')

# Fetch the document content
notion_content = fetch_page_content(page_id)

# Transform the content to PHP
php_code = transform_to_php(notion_content)

# Save to a PHP file
with open('output.php', 'w') as file:
    file.write(php_code)

print("PHP code has been generated and saved to output.php")
