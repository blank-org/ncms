"""
Test the new parser by temporarily setting a content-rich page to 'publish',
running the fetch, then examining the output.
Does NOT push to git or update Notion status — just generates locally.
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.getenv('NOTION_API_KEY'))
database_id = os.getenv('NOTION_DATABASE_ID')

# Import the parser functions directly
from ncms_fetch import fetch_page_content, render_rich_text

# Pick a content-rich page to test with
TEST_SLUG = "world/philosophy/consciousness/free_will"

def find_page_by_slug(slug):
    response = notion.databases.query(
        database_id=database_id,
        filter={"property": "Id", "title": {"equals": slug}}
    )
    results = response.get('results', [])
    return results[0] if results else None

def test_fetch_page(slug):
    """Fetch and display the parsed content of a page without modifying anything."""
    page = find_page_by_slug(slug)
    if not page:
        print(f"Page not found: {slug}")
        return

    page_id = page['id']
    print(f"=== Fetching content for: {slug} (ID: {page_id}) ===\n")

    content = fetch_page_content(page_id)
    print("--- Generated PHP/HTML ---")
    print(content)
    print("--- End ---")

    # Write to test output file
    output_path = f"test/HTML/Component/{slug.replace('/', os.sep)}/index.php"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    php_code = f"<div id='message'>\n\t{content}\n</div>\n\n<?php require('../HTML/Fragment/Component_bottom.php') ?>"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(php_code)
    print(f"\nWritten to: {output_path}")

if __name__ == "__main__":
    slugs = [TEST_SLUG]
    if len(sys.argv) > 1:
        slugs = sys.argv[1:]

    for slug in slugs:
        test_fetch_page(slug)
        print()
