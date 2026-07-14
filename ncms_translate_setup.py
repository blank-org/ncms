"""
One-time setup: Add Language=en and TranslationGroup=slug to all existing Notion pages.

Usage:
    python ncms_translate_setup.py              # Dry run (preview)
    python ncms_translate_setup.py --apply      # Apply changes

Prerequisites:
    - Add a "Language" Select property to the Notion database (values: en, hi)
    - Add a "TranslationGroup" Rich Text property to the Notion database
"""
import sys
import os
from notion_client import Client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
notion = Client(auth=os.getenv('NOTION_API_KEY'))
database_id = os.getenv('NOTION_DATABASE_ID')

def fetch_all_pages():
    results = []
    has_more = True
    start_cursor = None
    while has_more:
        response = notion.databases.query(
            database_id=database_id,
            start_cursor=start_cursor
        )
        results.extend(response.get('results', []))
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor', None)
    return results

def get_slug(page):
    props = page['properties']
    if props.get("Id") and props["Id"].get("title"):
        return props["Id"]["title"][0]["plain_text"]
    return ""

def get_language(page):
    props = page['properties']
    if props.get("Language") and props["Language"].get("select") and props["Language"]["select"]:
        return props["Language"]["select"]["name"]
    return None

def get_translation_group(page):
    props = page['properties']
    if props.get("TranslationGroup") and props["TranslationGroup"].get("rich_text"):
        rt = props["TranslationGroup"]["rich_text"]
        return rt[0]["plain_text"] if rt else None
    return None

def main():
    dry_run = "--apply" not in sys.argv

    if dry_run:
        print("DRY RUN — pass --apply to make changes\n")

    pages = fetch_all_pages()
    print(f"Found {len(pages)} pages\n")

    updated = 0
    skipped = 0

    for page in pages:
        slug = get_slug(page)
        current_lang = get_language(page)
        current_group = get_translation_group(page)
        status = page['properties'].get("Status", {}).get("select", {})
        status_name = status.get("name", "?") if status else "?"

        needs_lang = current_lang is None
        needs_group = current_group is None or current_group == ""

        if not needs_lang and not needs_group:
            skipped += 1
            continue

        updates = {}
        if needs_lang:
            updates["Language"] = {"select": {"name": "en"}}
        if needs_group:
            updates["TranslationGroup"] = {
                "rich_text": [{"text": {"content": slug}}]
            }

        changes = []
        if needs_lang:
            changes.append("Language=en")
        if needs_group:
            changes.append(f"TranslationGroup={slug}")

        print(f"  [{status_name}] {slug} → {', '.join(changes)}")

        if not dry_run:
            try:
                notion.pages.update(page_id=page['id'], properties=updates)
                updated += 1
            except Exception as e:
                print(f"    ERROR: {e}")
        else:
            updated += 1

    print(f"\n{'Would update' if dry_run else 'Updated'}: {updated}, Already set: {skipped}")

if __name__ == "__main__":
    main()
