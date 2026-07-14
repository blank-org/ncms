"""
ncms_upload.py — Upload existing PHP/HTML article content to Notion pages.

Reverse of ncms_fetch.py: reads PHP/HTML files from Component directory,
parses them into Notion blocks, and appends them to the corresponding
Notion pages (matched by slug from ID.tsv).

Usage:
    python ncms_upload.py                  # Upload all articles
    python ncms_upload.py about            # Upload a single article by slug
    python ncms_upload.py --dry-run        # Parse and show blocks without uploading
    python ncms_upload.py --dry-run about  # Dry-run a single article
"""

import os
import re
import sys
import json
import time
import base64
import html as html_module
from bs4 import BeautifulSoup, NavigableString, Tag
from notion_client import Client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

# --- Config ---

COMPONENT_DIR = r'H:\Website\site\project\root\HTML\Component'
TSV_PATH = r'H:\Website\site\project\config\ID.tsv'

load_dotenv()
notion = Client(auth=os.getenv('NOTION_API_KEY'))
database_id = os.getenv('NOTION_DATABASE_ID')

# Boilerplate PHP patterns to skip entirely
SKIP_PHP_PATTERNS = [
    r"require\s*\(\s*['\"]\.\.\/HTML\/Fragment\/Component_bottom\.php['\"]\s*\)",
    r"require\s*\(\s*['\"]\.\.\/HTML\/Fragment\/Component_FB_comments\.php['\"]\s*\)",
    r"require\s*\(\s*['\"]\.\.\/HTML\/Fragment\/Component_FB_buttons\.php['\"]\s*\)",
    r"require\s*\(\s*['\"]\.\.\/HTML\/Fragment\/NavList\.php['\"]\s*\)",
    r"require\s*\(\s*['\"]\.\.\/JS\/Base\/page\.js['\"]\s*\)",
    r"require_once\s+['\"]Fragment\/Item_text\.php['\"]",
    r"require_once\s+['\"]Fragment\/Item_image\.php['\"]",
]


# ============================================================
# Step 1: Build slug → file path mapping from filesystem
# ============================================================

def build_file_map():
    """Scan Component directory and build a map from lowercase slug to file path."""
    file_map = {}
    for root, dirs, files in os.walk(COMPONENT_DIR):
        for f in files:
            if not f.endswith(('.php', '.html')):
                continue
            full_path = os.path.join(root, f)
            rel = os.path.relpath(full_path, COMPONENT_DIR).replace('\\', '/')
            name, _ext = os.path.splitext(rel)
            # If filename is 'Index', use directory path only
            if name.lower().endswith('/index'):
                slug = name[:name.rfind('/')]
            else:
                slug = name
            slug = slug.lower()
            file_map[slug] = full_path
    return file_map


def read_tsv_slugs():
    """Read the TSV and return list of slug strings (skip header)."""
    slugs = []
    with open(TSV_PATH, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue  # skip header
            parts = line.strip().split('\t')
            if len(parts) >= 2 and parts[1]:
                slugs.append(parts[1])
    return slugs


# ============================================================
# Step 2: Query Notion for all pages → slug:page_id mapping
# ============================================================

def fetch_all_notion_pages():
    """Query the entire database (no filter) to get slug → page_id."""
    results = []
    has_more = True
    start_cursor = None
    while has_more:
        kwargs = {'database_id': database_id}
        if start_cursor:
            kwargs['start_cursor'] = start_cursor
        response = notion.databases.query(**kwargs)
        results.extend(response.get('results', []))
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor')
    page_map = {}
    for page in results:
        props = page['properties']
        title_prop = props.get('Id', {}).get('title', [])
        if title_prop:
            slug = title_prop[0]['plain_text']
            page_map[slug] = page['id']
    return page_map


# ============================================================
# Step 3: HTML/PHP → Notion blocks parser
# ============================================================

SITE_BASE = "https://ujnotes.com"


def normalize_url(url):
    """Convert relative URLs to absolute for Notion API compatibility."""
    if not url:
        return url
    if url.startswith('/') and not url.startswith('//'):
        return SITE_BASE + url
    if url.startswith('//'):
        return 'https:' + url
    return url


def make_text(content, annotations=None, link=None):
    """Create a single Notion rich_text element."""
    if not content:
        return None
    rt = {"type": "text", "text": {"content": content}}
    if link:
        rt["text"]["link"] = {"url": normalize_url(link)}
    if annotations:
        ann = {}
        for key in ['bold', 'italic', 'code', 'strikethrough', 'underline']:
            if annotations.get(key):
                ann[key] = True
        if ann:
            rt["annotations"] = ann
    return rt


def element_to_rich_text(element):
    """Recursively convert a BS4 element's children into Notion rich_text array."""
    rich_text = []

    def walk(node, annotations=None, link=None):
        if annotations is None:
            annotations = {}

        if isinstance(node, NavigableString):
            text = str(node)
            # Check if this is a PHP marker
            if text.strip().startswith('%%PHP_'):
                # This shouldn't happen in well-structured content
                rt = make_text(text.strip(), annotations, link)
                if rt:
                    rich_text.append(rt)
                return
            if text:
                rt = make_text(text, annotations, link)
                if rt:
                    rich_text.append(rt)
            return

        if not isinstance(node, Tag):
            return

        tag = node.name

        if tag == 'br':
            rt = make_text('\n')
            if rt:
                rich_text.append(rt)
            return

        if tag == 'php-marker':
            # Inline PHP — extract and handle
            php_code = node.get('data-code', '')
            if php_code:
                php_code = base64.b64decode(php_code).decode('utf-8')
            # Check if it's link_xurl
            m = re.match(r"<\?php\s+link_xurl\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)\s*\?>", php_code)
            if m:
                path, label = m.group(1), m.group(2)
                url = '/' + path if not path.startswith('/') else path
                rt = make_text(label, annotations, url)
                if rt:
                    rich_text.append(rt)
                return
            # Check for echo $desc
            if 'echo $desc' in php_code:
                return  # skip, part of cover pattern
            # Other inline PHP — render as code
            rt = make_text(php_code.strip(), {**annotations, 'code': True}, link)
            if rt:
                rich_text.append(rt)
            return

        # Inline formatting tags
        if tag in ('strong', 'b'):
            for child in node.children:
                walk(child, {**annotations, 'bold': True}, link)
        elif tag in ('em', 'i'):
            for child in node.children:
                walk(child, {**annotations, 'italic': True}, link)
        elif tag == 'code':
            for child in node.children:
                walk(child, {**annotations, 'code': True}, link)
        elif tag == 's':
            for child in node.children:
                walk(child, {**annotations, 'strikethrough': True}, link)
        elif tag == 'u':
            for child in node.children:
                walk(child, {**annotations, 'underline': True}, link)
        elif tag == 'a':
            href = node.get('href', '')
            for child in node.children:
                walk(child, annotations, href)
        elif tag == 'span':
            classes = node.get('class', [])
            new_ann = {**annotations}
            if 'bold' in classes:
                new_ann['bold'] = True
            for child in node.children:
                walk(child, new_ann, link)
        elif tag == 'img':
            alt = node.get('alt', '')
            rt = make_text(f"[image: {alt}]", annotations, link)
            if rt:
                rich_text.append(rt)
        else:
            # For other inline tags (div inside li, etc.), process children
            for child in node.children:
                walk(child, annotations, link)

    if isinstance(element, Tag):
        for child in element.children:
            walk(child)
    elif isinstance(element, NavigableString):
        walk(element)

    # Clean up: merge adjacent text segments with same annotations, trim
    return clean_rich_text(rich_text)


def clean_rich_text(rich_text):
    """Clean up rich_text: remove leading/trailing whitespace-only segments."""
    if not rich_text:
        return rich_text

    # Remove entirely empty segments
    rich_text = [rt for rt in rich_text if rt and rt['text']['content']]

    # Strip leading whitespace from first segment
    if rich_text:
        first = rich_text[0]['text']['content']
        stripped = first.lstrip('\n\t')
        if stripped:
            rich_text[0] = {**rich_text[0], 'text': {**rich_text[0]['text'], 'content': stripped}}
        elif len(rich_text) > 1:
            rich_text = rich_text[1:]

    # Strip trailing whitespace from last segment
    if rich_text:
        last = rich_text[-1]['text']['content']
        stripped = last.rstrip('\n\t ')
        if stripped:
            rich_text[-1] = {**rich_text[-1], 'text': {**rich_text[-1]['text'], 'content': stripped}}
        elif len(rich_text) > 1:
            rich_text = rich_text[:-1]

    # Merge adjacent segments with same annotations and link
    merged = []
    for rt in rich_text:
        if merged:
            prev = merged[-1]
            same_ann = (prev.get('annotations', {}) == rt.get('annotations', {}))
            same_link = (prev['text'].get('link') == rt['text'].get('link'))
            if same_ann and same_link:
                merged[-1] = {**prev, 'text': {**prev['text'],
                    'content': prev['text']['content'] + rt['text']['content']}}
                continue
        merged.append(rt)
    rich_text = merged

    # Notion limit: each rich_text content max 2000 chars
    final = []
    for rt in rich_text:
        content = rt['text']['content']
        while len(content) > 2000:
            chunk = {**rt, 'text': {**rt['text'], 'content': content[:2000]}}
            final.append(chunk)
            content = content[2000:]
        if content:
            rt_copy = {**rt, 'text': {**rt['text'], 'content': content}}
            final.append(rt_copy)

    return final


# --- Block constructors ---

def is_rich_text_empty(rich_text):
    """Check if rich_text contains only whitespace."""
    if not rich_text:
        return True
    text = ''.join(rt['text']['content'] for rt in rich_text)
    return not text.strip()


def make_paragraph(rich_text):
    if not rich_text or is_rich_text_empty(rich_text):
        return None
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rich_text}
    }


def make_heading(level, rich_text):
    """level: 1, 2, or 3 → heading_1, heading_2, heading_3"""
    if not rich_text:
        return None
    key = f"heading_{level}"
    return {
        "object": "block",
        "type": key,
        key: {"rich_text": rich_text}
    }


def make_bulleted_list_item(rich_text):
    if not rich_text:
        return None
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": rich_text}
    }


def make_numbered_list_item(rich_text):
    if not rich_text:
        return None
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": rich_text}
    }


def make_quote(rich_text):
    if not rich_text:
        return None
    return {
        "object": "block",
        "type": "quote",
        "quote": {"rich_text": rich_text}
    }


def make_code(text, language="plain text"):
    if not text:
        return None
    return {
        "object": "block",
        "type": "code",
        "code": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "language": language
        }
    }


def make_divider():
    return {
        "object": "block",
        "type": "divider",
        "divider": {}
    }


def make_callout(emoji, text):
    """Create a callout block with emoji icon and plain text."""
    if not text:
        return None
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "icon": {"type": "emoji", "emoji": emoji}
        }
    }


def make_table(rows):
    """Create a table block. rows is a list of lists of strings."""
    if not rows:
        return None
    width = max(len(row) for row in rows) if rows else 0
    children = []
    for row in rows:
        cells = []
        for i in range(width):
            cell_text = row[i].strip() if i < len(row) else ''
            cells.append([{"type": "text", "text": {"content": cell_text}}])
        children.append({
            "type": "table_row",
            "table_row": {"cells": cells}
        })
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": width,
            "has_column_header": False,
            "has_row_header": False,
            "children": children
        }
    }


# --- PHP tag preprocessing ---

def preprocess_php(content):
    """Replace <?php ... ?> with <php-marker> tags for BS4 parsing.
    Returns (processed_html, php_tags_list)."""
    php_tags = []

    def replacer(match):
        idx = len(php_tags)
        php_code = match.group(0)
        php_tags.append(php_code)
        encoded = base64.b64encode(php_code.encode('utf-8')).decode('ascii')
        return f'<php-marker data-idx="{idx}" data-code="{encoded}"></php-marker>'

    processed = re.sub(r'<\?php\s.*?\?>', replacer, content, flags=re.DOTALL)
    return processed, php_tags


def is_skip_php(php_code):
    """Check if a PHP tag is boilerplate that should be skipped."""
    for pattern in SKIP_PHP_PATTERNS:
        if re.search(pattern, php_code):
            return True
    return False


def classify_php_block(php_code):
    """Classify a standalone PHP tag and return a Notion block or None."""
    if is_skip_php(php_code):
        return None

    # Cover image: <?php $alt='...'; require('...Component_cover.php') ?>
    m = re.search(r"\$alt\s*=\s*'([^']*)'\s*;\s*require\s*\(\s*['\"].*Component_cover\.php['\"]\s*\)", php_code)
    if m:
        alt_text = m.group(1)
        return make_callout('🖼️', alt_text)

    # Content image: <?php $img_title='...'; ... require('Fragment/Component_image.php') ?>
    m = re.search(r"require\s*\(\s*['\"]Fragment\/Component_image\.php['\"]\s*\)", php_code)
    if m:
        # Extract variables
        img_title = re.search(r"\$img_title\s*=\s*'([^']*)'", php_code)
        ext = re.search(r"\$ext\s*=\s*'([^']*)'", php_code)
        alt = re.search(r"\$alt\s*=\s*'([^']*)'", php_code)
        center = re.search(r"\$center\s*=\s*'([^']*)'", php_code)
        parts = []
        parts.append(img_title.group(1) if img_title else '')
        parts.append(ext.group(1) if ext else 'svg')
        parts.append(alt.group(1) if alt else '')
        if center:
            parts.append(center.group(1))
        return make_callout('🏞️', '|'.join(parts))

    # link_xurl standalone: <?php link_xurl('path', 'label') ?>
    links = re.findall(r"link_xurl\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)", php_code)
    if links:
        lines = [f"{path}|{label}" for path, label in links]
        return make_callout('🔗', '\n'.join(lines))

    # group_image / group_image_id — raw PHP
    if 'group_image' in php_code:
        # Strip the <?php and ?> wrappers
        inner = php_code.strip()
        if inner.startswith('<?php'):
            inner = inner[5:]
        if inner.endswith('?>'):
            inner = inner[:-2]
        return make_callout('🔧', inner.strip())

    # include/require for content files (not boilerplate)
    if re.search(r'(include|require)', php_code):
        inner = php_code.strip()
        if inner.startswith('<?php'):
            inner = inner[5:]
        if inner.endswith('?>'):
            inner = inner[:-2]
        return make_callout('🔧', inner.strip())

    # Default: raw PHP callout
    inner = php_code.strip()
    if inner.startswith('<?php'):
        inner = inner[5:]
    if inner.endswith('?>'):
        inner = inner[:-2]
    return make_callout('🔧', inner.strip())


# --- Main parser ---

def parse_file_to_blocks(file_path):
    """Parse a PHP/HTML file and return a list of Notion block objects."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Preprocess PHP tags
    processed, php_tags = preprocess_php(content)

    soup = BeautifulSoup(processed, 'html.parser')

    # Find the message div
    message_div = soup.find('div', id='message')
    if not message_div:
        # No message div — try parsing the whole content
        message_div = soup

    blocks = []
    skip_next_h2_desc = False  # Flag to skip <h2><?php echo $desc; ?></h2>

    for element in message_div.children:
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if not text:
                continue
            # Standalone text outside tags — skip whitespace
            continue

        if not isinstance(element, Tag):
            continue

        tag = element.name

        # PHP marker (standalone)
        if tag == 'php-marker':
            idx = int(element.get('data-idx', 0))
            php_code = php_tags[idx]
            # Check if it's the cover image
            if re.search(r'Component_cover\.php', php_code):
                skip_next_h2_desc = True
            block = classify_php_block(php_code)
            if block:
                blocks.append(block)
            continue

        # Headings
        if tag == 'h2':
            # Always check if this h2 contains echo $desc (metadata heading)
            h2_html = str(element)
            has_desc = 'echo $desc' in h2_html
            if not has_desc:
                for marker in element.find_all('php-marker'):
                    code = marker.get('data-code', '')
                    if code:
                        decoded = base64.b64decode(code).decode('utf-8')
                        if 'echo $desc' in decoded:
                            has_desc = True
                            break
            if has_desc:
                skip_next_h2_desc = False
                continue  # Skip — generated from metadata
            skip_next_h2_desc = False
            # Regular h2 → heading_2 in Notion
            rt = element_to_rich_text(element)
            block = make_heading(2, rt)
            if block:
                blocks.append(block)
            continue

        if tag == 'h3':
            skip_next_h2_desc = False
            rt = element_to_rich_text(element)
            block = make_heading(1, rt)
            if block:
                blocks.append(block)
            continue

        if tag == 'h4':
            rt = element_to_rich_text(element)
            block = make_heading(3, rt)
            if block:
                blocks.append(block)
            continue

        # Paragraph
        if tag == 'p':
            rt = element_to_rich_text(element)
            block = make_paragraph(rt)
            if block:
                blocks.append(block)
            continue

        # Lists
        if tag == 'ul':
            for li in element.find_all('li', recursive=False):
                # Content is often in a <div> inside <li>
                div = li.find('div', recursive=False)
                target = div if div else li
                rt = element_to_rich_text(target)
                block = make_bulleted_list_item(rt)
                if block:
                    blocks.append(block)
            continue

        if tag == 'ol':
            for li in element.find_all('li', recursive=False):
                div = li.find('div', recursive=False)
                target = div if div else li
                rt = element_to_rich_text(target)
                block = make_numbered_list_item(rt)
                if block:
                    blocks.append(block)
            continue

        # Table
        if tag == 'table':
            rows = []
            for tr in element.find_all('tr'):
                cells = []
                for td in tr.find_all(['td', 'th']):
                    cells.append(td.get_text().strip())
                if cells:
                    rows.append(cells)
            block = make_table(rows)
            if block:
                blocks.append(block)
            continue

        # Code block
        if tag == 'pre':
            code_elem = element.find('code')
            if code_elem:
                text = code_elem.get_text()
            else:
                text = element.get_text()
            block = make_code(text)
            if block:
                blocks.append(block)
            continue

        # Blockquote
        if tag == 'blockquote':
            rt = element_to_rich_text(element)
            block = make_quote(rt)
            if block:
                blocks.append(block)
            continue

        # Divs — check for special types
        if tag == 'div':
            div_id = element.get('id', '')
            div_class = ' '.join(element.get('class', []))

            # Divider
            if 'content-body-separator' in div_id or 'content-body-separator' in div_class:
                blocks.append(make_divider())
                continue

            # Skip FB components, home-menu, profile-image, etc.
            if div_id in ('fb_components', 'profile-image-container'):
                continue
            if 'message_leave' in div_class:
                continue

            # For other divs, recurse into children and process them
            # (e.g. <div class="indent-c"> wrapping a table)
            child_blocks = parse_children_to_blocks(element, php_tags)
            blocks.extend(child_blocks)
            continue

    # Also look for content AFTER the message div (dividers, PHP, etc.)
    # but only at the top level of the document
    if message_div != soup:
        after_message = False
        for element in soup.children:
            if element == message_div:
                after_message = True
                continue
            if not after_message:
                continue
            if not isinstance(element, Tag):
                continue

            tag = element.name

            if tag == 'php-marker':
                idx = int(element.get('data-idx', 0))
                php_code = php_tags[idx]
                block = classify_php_block(php_code)
                if block:
                    blocks.append(block)
                continue

            if tag == 'div':
                div_id = element.get('id', '')
                div_class = ' '.join(element.get('class', []))
                if 'content-body-separator' in div_id or 'content-body-separator' in div_class:
                    blocks.append(make_divider())
                    continue
                if div_id in ('fb_components',):
                    continue
                # Process child blocks for other divs (like home-menu)
                child_blocks = parse_children_to_blocks(element, php_tags)
                if child_blocks:
                    blocks.extend(child_blocks)
                continue

    return blocks


def parse_children_to_blocks(parent_element, php_tags):
    """Parse children of a div into blocks (for nested content)."""
    blocks = []
    for element in parent_element.children:
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if not text:
                continue
            continue  # skip standalone text

        if not isinstance(element, Tag):
            continue

        tag = element.name

        if tag == 'php-marker':
            idx = int(element.get('data-idx', 0))
            php_code = php_tags[idx]
            block = classify_php_block(php_code)
            if block:
                blocks.append(block)
            continue

        if tag == 'p':
            rt = element_to_rich_text(element)
            block = make_paragraph(rt)
            if block:
                blocks.append(block)
            continue

        if tag in ('h2', 'h3', 'h4'):
            level_map = {'h2': 2, 'h3': 1, 'h4': 3}
            rt = element_to_rich_text(element)
            block = make_heading(level_map[tag], rt)
            if block:
                blocks.append(block)
            continue

        if tag == 'table':
            rows = []
            for tr in element.find_all('tr'):
                cells = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
                if cells:
                    rows.append(cells)
            block = make_table(rows)
            if block:
                blocks.append(block)
            continue

        if tag == 'ul':
            for li in element.find_all('li', recursive=False):
                div = li.find('div', recursive=False)
                target = div if div else li
                rt = element_to_rich_text(target)
                block = make_bulleted_list_item(rt)
                if block:
                    blocks.append(block)
            continue

        if tag == 'ol':
            for li in element.find_all('li', recursive=False):
                div = li.find('div', recursive=False)
                target = div if div else li
                rt = element_to_rich_text(target)
                block = make_numbered_list_item(rt)
                if block:
                    blocks.append(block)
            continue

        if tag == 'div':
            div_id = element.get('id', '')
            div_class = ' '.join(element.get('class', []))
            if 'content-body-separator' in div_id or 'content-body-separator' in div_class:
                blocks.append(make_divider())
                continue
            if div_id in ('fb_components', 'profile-image-container'):
                continue
            # Recurse
            child_blocks = parse_children_to_blocks(element, php_tags)
            blocks.extend(child_blocks)
            continue

        if tag == 'br':
            continue  # skip standalone br

    return blocks


# ============================================================
# Step 4: Upload blocks to Notion
# ============================================================

def clear_page_content(page_id):
    """Remove all existing blocks from a Notion page."""
    has_more = True
    start_cursor = None
    while has_more:
        kwargs = {'block_id': page_id}
        if start_cursor:
            kwargs['start_cursor'] = start_cursor
        response = notion.blocks.children.list(**kwargs)
        for block in response['results']:
            try:
                notion.blocks.delete(block_id=block['id'])
            except Exception as e:
                print(f"  Warning: Failed to delete block {block['id']}: {e}")
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor')
        # If we deleted blocks, the cursor is invalidated — restart
        if has_more:
            has_more = True
            start_cursor = None


def upload_blocks(page_id, blocks):
    """Append blocks to a Notion page, respecting the 100-block limit."""
    # Notion API allows max 100 blocks per append call
    for i in range(0, len(blocks), 100):
        batch = blocks[i:i + 100]
        try:
            notion.blocks.children.append(block_id=page_id, children=batch)
        except Exception as e:
            print(f"  Error appending blocks (batch {i//100 + 1}): {e}")
            # Try one by one for this batch to identify the problematic block
            for j, block in enumerate(batch):
                try:
                    notion.blocks.children.append(block_id=page_id, children=[block])
                except Exception as e2:
                    print(f"  Block {i+j} failed: {e2}")
                    print(f"  Block content: {json.dumps(block, indent=2, ensure_ascii=False)[:500]}")


# ============================================================
# Main
# ============================================================

def main():
    dry_run = '--dry-run' in sys.argv
    target_slug = None
    for arg in sys.argv[1:]:
        if arg != '--dry-run':
            target_slug = arg

    print("Building file map from Component directory...")
    file_map = build_file_map()
    print(f"  Found {len(file_map)} files")

    print("Reading TSV slugs...")
    tsv_slugs = read_tsv_slugs()
    print(f"  Found {len(tsv_slugs)} entries")

    if not dry_run:
        print("Fetching Notion pages...")
        page_map = fetch_all_notion_pages()
        print(f"  Found {len(page_map)} pages")
    else:
        page_map = {}

    # Filter to target slug if specified
    if target_slug:
        tsv_slugs = [s for s in tsv_slugs if s == target_slug]
        if not tsv_slugs:
            print(f"Error: slug '{target_slug}' not found in TSV")
            return

    success = 0
    skipped = 0
    failed = 0

    for slug in tsv_slugs:
        # Find file
        file_path = file_map.get(slug)
        if not file_path:
            print(f"SKIP {slug}: no matching file found")
            skipped += 1
            continue

        if not dry_run:
            page_id = page_map.get(slug)
            if not page_id:
                print(f"SKIP {slug}: no Notion page found")
                skipped += 1
                continue

        print(f"\nProcessing: {slug}")
        print(f"  File: {file_path}")

        try:
            blocks = parse_file_to_blocks(file_path)
            print(f"  Parsed {len(blocks)} blocks")

            if dry_run:
                for i, block in enumerate(blocks):
                    btype = block['type']
                    if btype == 'callout':
                        emoji = block['callout']['icon']['emoji']
                        text = block['callout']['rich_text'][0]['text']['content'][:60]
                        print(f"    [{i}] {btype} {emoji} : {text}")
                    elif btype == 'table':
                        nrows = len(block['table']['children'])
                        print(f"    [{i}] {btype} ({nrows} rows)")
                    elif btype == 'divider':
                        print(f"    [{i}] {btype}")
                    else:
                        rt = block[btype].get('rich_text', [])
                        text = ''.join(r['text']['content'] for r in rt)[:80]
                        print(f"    [{i}] {btype}: {text}")
                success += 1
            else:
                print(f"  Clearing existing content...")
                clear_page_content(page_id)
                print(f"  Uploading {len(blocks)} blocks...")
                upload_blocks(page_id, blocks)
                print(f"  Done!")
                success += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {success} uploaded, {skipped} skipped, {failed} failed")


if __name__ == '__main__':
    main()
