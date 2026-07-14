"""
Create a test article in Notion with all supported block types,
then fetch it via ncms to verify the output.
"""
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.getenv('NOTION_API_KEY'))
database_id = os.getenv('NOTION_DATABASE_ID')

TEST_SLUG = "test/ncms-blocks"

def cleanup_existing():
    """Delete any existing test page with the same slug."""
    response = notion.databases.query(
        database_id=database_id,
        filter={"property": "Id", "title": {"equals": TEST_SLUG}}
    )
    for page in response.get('results', []):
        notion.pages.update(page_id=page['id'], archived=True)
        print(f"Archived existing test page: {page['id']}")

def create_test_page():
    """Create a Notion page with all supported block types."""
    page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Id": {"title": [{"text": {"content": TEST_SLUG}}]},
            "Status": {"select": {"name": "publish"}},
            "Label": {"rich_text": [{"text": {"content": "NCMS Test"}}]},
            "Title": {"rich_text": [{"text": {"content": "NCMS Block Test"}}]},
            "JS": {"select": {"name": "0"}},
            "Description": {"rich_text": [{"text": {"content": "Testing all block types"}}]},
        },
        children=[
            # 1. Cover image callout (🖼️)
            {
                "type": "callout",
                "callout": {
                    "icon": {"type": "emoji", "emoji": "\U0001f5bc\ufe0f"},
                    "rich_text": [{"type": "text", "text": {"content": "A test cover image"}}]
                }
            },
            # 2. Heading 1 → <h3>
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "Heading 1 Test"}}]
                }
            },
            # 3. Paragraph with rich text
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "This is "}},
                        {"type": "text", "text": {"content": "bold"}, "annotations": {"bold": True}},
                        {"type": "text", "text": {"content": " and "}},
                        {"type": "text", "text": {"content": "italic"}, "annotations": {"italic": True}},
                        {"type": "text", "text": {"content": " and "}},
                        {"type": "text", "text": {"content": "code"}, "annotations": {"code": True}},
                        {"type": "text", "text": {"content": " formatting."}},
                    ]
                }
            },
            # 4. Paragraph with links
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Visit "}},
                        {"type": "text", "text": {"content": "Life", "link": {"url": "https://ujnotes.com/world/philosophy/life"}}},
                        {"type": "text", "text": {"content": " or "}},
                        {"type": "text", "text": {"content": "YouTube", "link": {"url": "https://www.youtube.com/watch?v=test"}}},
                        {"type": "text", "text": {"content": " for more."}},
                    ]
                }
            },
            # 5. Heading 2 → <h2>
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Heading 2 Test"}}]
                }
            },
            # 6. Heading 3 → <h4>
            {
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "Heading 3 Test"}}]
                }
            },
            # 7. Bulleted list items
            {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Bullet item one"}}]
                }
            },
            {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Bullet item two with "}},
                                  {"type": "text", "text": {"content": "bold"}, "annotations": {"bold": True}}]
                }
            },
            # 8. Numbered list items
            {
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Numbered item one"}}]
                }
            },
            {
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Numbered item two"}}]
                }
            },
            # 9. Quote block
            {
                "type": "quote",
                "quote": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "You have a right to perform your prescribed duty. "}},
                        {"type": "text", "text": {"content": "Gita 2.47", "link": {"url": "http://gitabase.com/the/gita/eng/BG/2/47"}}},
                    ]
                }
            },
            # 10. Code block
            {
                "type": "code",
                "code": {
                    "language": "php",
                    "rich_text": [{"type": "text", "text": {"content": "<?php echo 'Hello World'; ?>"}}]
                }
            },
            # 11. Divider
            {
                "type": "divider",
                "divider": {}
            },
            # 12. Content image callout (🏞️)
            {
                "type": "callout",
                "callout": {
                    "icon": {"type": "emoji", "emoji": "\U0001f3de\ufe0f"},
                    "rich_text": [{"type": "text", "text": {"content": "paths|svg||true"}}]
                }
            },
            # 13. Link xurl callout (🔗)
            {
                "type": "callout",
                "callout": {
                    "icon": {"type": "emoji", "emoji": "\U0001f517"},
                    "rich_text": [{"type": "text", "text": {"content": "world/philosophy/life|Life\nworld/philosophy/death|Death"}}]
                }
            },
            # 14. Raw PHP callout (🔧)
            {
                "type": "callout",
                "callout": {
                    "icon": {"type": "emoji", "emoji": "\U0001f527"},
                    "rich_text": [{"type": "text", "text": {"content": "<?php group_image('paths', 3, 'svg') ?>"}}]
                }
            },
            # 15. Table
            {
                "type": "table",
                "table": {
                    "table_width": 2,
                    "has_column_header": False,
                    "has_row_header": False,
                    "children": [
                        {
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Cell A1"}}],
                                    [{"type": "text", "text": {"content": "Cell B1"}}]
                                ]
                            }
                        },
                        {
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Cell A2"}}],
                                    [{"type": "text", "text": {"content": "Cell B2"}}]
                                ]
                            }
                        }
                    ]
                }
            },
            # 16. Final paragraph
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "End of test article."}}]
                }
            },
        ]
    )
    print(f"Created test page: {page['id']}")
    return page['id']

if __name__ == "__main__":
    print("=== NCMS Test Article Creator ===")
    cleanup_existing()
    page_id = create_test_page()
    print(f"\nTest page created with slug: {TEST_SLUG}")
    print(f"Page ID: {page_id}")
    print("\nNow run: python ncms_fetch.py")
    print(f"Then check: test/HTML/Component/{TEST_SLUG}/index.php")
