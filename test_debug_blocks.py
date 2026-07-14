"""Debug: show raw Notion blocks for multiple pages."""
import os
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

# Check several pages for content
SLUGS = [
    "world/philosophy",
    "world/philosophy/intelligence",
    "root",
    "world",
    "computer",
    "about_me",
]

def main():
    notion = Client(auth=os.getenv('NOTION_API_KEY'))
    database_id = os.getenv('NOTION_DATABASE_ID')
    response = notion.databases.query(database_id=database_id)
    for page in response['results']:
        props = page['properties']
        slug = props["Id"]["title"][0]["plain_text"] if props["Id"].get("title") and props["Id"]["title"] else ""
        if slug in SLUGS:
            page_id = page['id']
            blocks = notion.blocks.children.list(block_id=page_id)
            block_count = len(blocks['results'])
            if block_count > 0:
                print(f"\n=== {slug} ({block_count} blocks) ===")
                for i, block in enumerate(blocks['results']):
                    bt = block['type']
                    if bt in ('paragraph', 'heading_1', 'heading_2', 'heading_3', 'callout', 'quote', 'code',
                              'bulleted_list_item', 'numbered_list_item'):
                        rich_text = block[bt].get('rich_text', [])
                        text_preview = ''.join([t.get('plain_text', '')[:80] for t in rich_text])
                        extra = ''
                        if bt == 'callout':
                            icon = block['callout'].get('icon', {})
                            emoji = icon.get('emoji', '?') if icon.get('type') == 'emoji' else '?'
                            extra = f" [emoji: {emoji}]"
                        print(f"  [{i}] {bt}{extra}: {text_preview!r}")
                    elif bt == 'table':
                        print(f"  [{i}] table")
                    elif bt == 'divider':
                        print(f"  [{i}] divider")
                    else:
                        print(f"  [{i}] {bt}")
            else:
                print(f"  {slug}: (empty)")


if __name__ == '__main__':
    main()
