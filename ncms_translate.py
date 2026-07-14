"""
Auto-translate English articles to a target language via Google Cloud Translation.
Creates draft pages in Notion for human review.

Usage:
    python ncms_translate.py hi                          # Translate all English articles to Hindi
    python ncms_translate.py hi world/philosophy/life     # Translate a specific article
    python ncms_translate.py hi --dry-run                 # Preview without creating pages

Prerequisites:
    - Notion database must have Language and TranslationGroup properties
    - Google Cloud Translation API enabled with credentials
    - .env: NOTION_API_KEY, NOTION_DATABASE_ID, GOOGLE_CLOUD_PROJECT
"""
import sys
import os
from notion_client import Client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
notion = Client(auth=os.getenv('NOTION_API_KEY'))
database_id = os.getenv('NOTION_DATABASE_ID')

SUPPORTED_LANGUAGES = {'hi': 'Hindi', 'hi-in': 'Hindi (India)'}

# --- Google Cloud Translation ---

_translate_client = None

def get_translate_client():
    global _translate_client
    if _translate_client is None:
        from google.cloud import translate_v3 as translate
        _translate_client = translate.TranslationServiceClient()
    return _translate_client

def translate_text(text, target_lang):
    """Translate text using Google Cloud Translation API."""
    if not text or not text.strip():
        return text
    client = get_translate_client()
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    parent = f"projects/{project_id}/locations/global"
    # Use base language code (e.g., 'hi' from 'hi-in')
    lang_code = target_lang.split('-')[0]
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": "en",
            "target_language_code": lang_code,
        }
    )
    return response.translations[0].translated_text

# --- Notion helpers ---

def fetch_english_articles(slug_filter=None):
    """Fetch published English articles from Notion."""
    results = []
    has_more = True
    start_cursor = None
    while has_more:
        query_filter = {
            "and": [
                {"property": "Status", "select": {"equals": "published"}},
                {"or": [
                    {"property": "Language", "select": {"equals": "en"}},
                    {"property": "Language", "select": {"is_empty": True}}
                ]}
            ]
        }
        response = notion.databases.query(
            database_id=database_id,
            filter=query_filter,
            start_cursor=start_cursor
        )
        results.extend(response.get('results', []))
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor')

    if slug_filter:
        results = [p for p in results
                   if p['properties'].get('Id', {}).get('title', [{}])[0].get('plain_text') == slug_filter]
    return results

def translation_exists(slug, target_lang):
    """Check if a translation page already exists."""
    response = notion.databases.query(
        database_id=database_id,
        filter={
            "and": [
                {"property": "Id", "title": {"equals": slug}},
                {"property": "Language", "select": {"equals": target_lang}}
            ]
        }
    )
    return len(response.get('results', [])) > 0

def fetch_blocks(page_id):
    """Fetch all blocks from a page."""
    blocks = []
    has_more = True
    start_cursor = None
    while has_more:
        kwargs = {'block_id': page_id}
        if start_cursor:
            kwargs['start_cursor'] = start_cursor
        response = notion.blocks.children.list(**kwargs)
        blocks.extend(response['results'])
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor')
    return blocks

# --- Block translation ---

# Emoji callouts that should NOT be translated (paths, code, image refs)
SKIP_TRANSLATE_EMOJIS = {'🖼️', '🏞️', '🔗', '🔧'}

def translate_rich_text(rich_text_list, target_lang):
    """Translate rich_text segments, preserving formatting annotations."""
    translated = []
    for segment in rich_text_list:
        new_seg = {
            "type": "text",
            "text": {"content": translate_text(segment.get('plain_text', ''), target_lang)},
            "annotations": segment.get('annotations', {})
        }
        # Preserve links
        href = segment.get('href')
        if href:
            new_seg["text"]["link"] = {"url": href}
        translated.append(new_seg)
    return translated

def translate_block(block, target_lang):
    """Translate a single Notion block. Returns a block dict for the Notion API, or None to skip."""
    block_type = block['type']

    # Text blocks that need translation
    text_types = ['paragraph', 'heading_1', 'heading_2', 'heading_3',
                  'bulleted_list_item', 'numbered_list_item', 'quote']

    if block_type in text_types:
        rich_text = block[block_type].get('rich_text', [])
        if not rich_text:
            return {"object": "block", "type": block_type, block_type: {"rich_text": []}}
        return {
            "object": "block",
            "type": block_type,
            block_type: {"rich_text": translate_rich_text(rich_text, target_lang)}
        }

    # Callouts — skip translation for technical emojis
    if block_type == 'callout':
        icon = block['callout'].get('icon', {})
        emoji = icon.get('emoji', '') if icon.get('type') == 'emoji' else ''
        rich_text = block['callout'].get('rich_text', [])

        if emoji in SKIP_TRANSLATE_EMOJIS:
            # Keep original text (paths, code references)
            return {
                "object": "block",
                "type": "callout",
                "callout": {
                    "icon": {"type": "emoji", "emoji": emoji},
                    "rich_text": [{"type": "text", "text": {"content": t.get('plain_text', '')}} for t in rich_text]
                }
            }
        else:
            return {
                "object": "block",
                "type": "callout",
                "callout": {
                    "icon": icon,
                    "rich_text": translate_rich_text(rich_text, target_lang)
                }
            }

    # Code blocks — never translate
    if block_type == 'code':
        rich_text = block['code'].get('rich_text', [])
        return {
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": t.get('plain_text', '')}} for t in rich_text],
                "language": block['code'].get('language', 'plain text')
            }
        }

    # Divider — pass through
    if block_type == 'divider':
        return {"object": "block", "type": "divider", "divider": {}}

    # Table — translate cell content
    if block_type == 'table':
        # Tables require fetching children separately; skip for now
        print(f"    Skipping table block (manual translation needed)")
        return None

    # Unknown block type — skip
    print(f"    Skipping unsupported block type: {block_type}")
    return None

# --- Page creation ---

def create_translated_page(source_page, translated_blocks, target_lang):
    """Create a new Notion page with translated content."""
    props = source_page['properties']
    slug = props["Id"]["title"][0]["plain_text"]

    # Translate metadata
    label = props.get("Label", {}).get("rich_text", [])
    label_text = label[0]["plain_text"] if label else ""
    translated_label = translate_text(label_text, target_lang)

    title = props.get("Title", {}).get("rich_text", [])
    title_text = title[0]["plain_text"] if title else ""
    translated_title = translate_text(title_text, target_lang)

    desc = props.get("Description", {}).get("rich_text", [])
    desc_text = desc[0]["plain_text"] if desc else ""
    translated_desc = translate_text(desc_text, target_lang)

    js_val = props.get("JS", {}).get("select", {})
    js_name = js_val.get("name", "0") if js_val else "0"

    page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Id": {"title": [{"text": {"content": slug}}]},
            "Status": {"select": {"name": "draft"}},
            "Label": {"rich_text": [{"text": {"content": translated_label}}]},
            "Title": {"rich_text": [{"text": {"content": translated_title}}]},
            "JS": {"select": {"name": js_name}},
            "Description": {"rich_text": [{"text": {"content": translated_desc}}]},
            "Language": {"select": {"name": target_lang}},
            "TranslationGroup": {"rich_text": [{"text": {"content": slug}}]},
        },
        children=translated_blocks[:100]  # Notion API limit: 100 blocks per request
    )

    # Append remaining blocks in batches
    if len(translated_blocks) > 100:
        for i in range(100, len(translated_blocks), 100):
            batch = translated_blocks[i:i + 100]
            notion.blocks.children.append(block_id=page['id'], children=batch)

    return page

# --- Main ---

def main():
    if len(sys.argv) < 2:
        print("Usage: python ncms_translate.py <target_lang> [slug] [--dry-run]")
        print(f"  Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}")
        sys.exit(1)

    target_lang = sys.argv[1]
    if target_lang not in SUPPORTED_LANGUAGES and target_lang != '--dry-run':
        print(f"Unsupported language: {target_lang}")
        print(f"  Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}")
        sys.exit(1)

    slug_filter = None
    dry_run = '--dry-run' in sys.argv
    for arg in sys.argv[2:]:
        if arg != '--dry-run':
            slug_filter = arg

    if dry_run:
        print("DRY RUN -- no pages will be created\n")

    print(f"Target language: {target_lang} ({SUPPORTED_LANGUAGES[target_lang]})")
    if slug_filter:
        print(f"Filtering to slug: {slug_filter}")
    print()

    pages = fetch_english_articles(slug_filter)
    print(f"Found {len(pages)} English articles to translate\n")

    translated_count = 0
    skipped_count = 0

    for page in pages:
        slug = page['properties']['Id']['title'][0]['plain_text']
        print(f"Processing: {slug}")

        if translation_exists(slug, target_lang):
            print(f"  Already has {target_lang} translation, skipping")
            skipped_count += 1
            continue

        # Fetch and translate blocks
        blocks = fetch_blocks(page['id'])
        translated_blocks = []
        for block in blocks:
            tb = translate_block(block, target_lang)
            if tb:
                translated_blocks.append(tb)

        print(f"  Translated {len(translated_blocks)} blocks")

        if not dry_run:
            new_page = create_translated_page(page, translated_blocks, target_lang)
            print(f"  Created draft page: {new_page['id']}")
        else:
            print(f"  Would create draft page with {len(translated_blocks)} blocks")

        translated_count += 1

    print(f"\nDone: {translated_count} translated, {skipped_count} skipped")

if __name__ == "__main__":
    main()
