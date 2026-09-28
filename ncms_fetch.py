import argparse
import json
import os
import re
import sys
from html import escape
from notion_client import Client
from dotenv import load_dotenv
import subprocess
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

# Load environment variables
load_dotenv()
notion = Client(auth=os.getenv('NOTION_API_KEY'))
database_id = os.getenv('NOTION_DATABASE_ID')
output_dir = os.getenv('OUTPUT_DIR')
project_dir = os.getenv('PROJECT_DIR')
git_push_enabled = os.getenv('GIT_PUSH', 'false').lower() == 'true'
notion_update_enabled = os.getenv('NOTION_UPDATE', 'false').lower() == 'true'

SAFE_SLUG_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_./-]*$')
NAV_SLUG_PATTERN = re.compile(r'^[a-z0-9_]+(?:/[a-z0-9_]+)*$')
LANGUAGE_PREFIX_PATTERN = re.compile(r'^[a-z]{2,3}(?:-[a-z]{2})?$')
NESTED_TRANSLATION_TITLE_PATTERN = re.compile(
    r'^.+\(([A-Za-z]{2,3}(?:-[A-Za-z]{2})?)\)\s*$'
)

# Fetch database content
def fetch_database_content(database_id, status='publish'):
    results = []
    has_more = True
    start_cursor = None
    while has_more:
        response = notion.databases.query(
            database_id=database_id,
            filter={"property": "Status", "select": {"equals": status}},
            start_cursor=start_cursor
        )
        results.extend(response.get('results', []))
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor', None)
    return results


def fetch_page_by_id_title(database_id, slug, status='publish'):
    """Fetch Status-matched rows whose Id title equals slug.

    Notion's Status-only listing can omit rows that a compound Id filter still
    returns, so slug-targeted publishes must query the page directly.
    """
    response = notion.databases.query(
        database_id=database_id,
        filter={
            "and": [
                {"property": "Status", "select": {"equals": status}},
                {"property": "Id", "title": {"equals": slug}},
            ]
        },
    )
    return response.get("results", [])


def resolve_publish_pages(database_id, status='publish', requested_slug=None):
    pages = fetch_database_content(database_id, status=status)
    if not requested_slug:
        return pages
    try:
        select_publish_page(pages, requested_slug)
        return pages
    except RuntimeError:
        pass

    requested_slug = validate_slug(requested_slug)
    lookups = [requested_slug]
    parts = requested_slug.split("/", 1)
    if len(parts) == 2 and LANGUAGE_PREFIX_PATTERN.fullmatch(parts[0].lower()):
        lookups.append(parts[1])

    seen_ids = {page.get("id") for page in pages}
    extra = []
    for lookup in lookups:
        for page in fetch_page_by_id_title(database_id, lookup, status=status):
            if page.get("id") not in seen_ids:
                extra.append(page)
                seen_ids.add(page.get("id"))
        if extra:
            break
    return pages + extra

# --- Rich text rendering ---

def escape_php_single_quoted(value):
    """Escape untrusted text for a PHP single-quoted string literal."""
    return value.replace('\\', '\\\\').replace("'", "\\'")


def internal_link_path(href):
    """Return an internal site path, or None when href is external."""
    if href.startswith('/') and not href.startswith('//'):
        return href

    parsed = urlsplit(href)
    if parsed.hostname not in {'ujnotes.com', 'www.ujnotes.com'}:
        return None

    return urlunsplit(('', '', parsed.path or '/', parsed.query, parsed.fragment))

def render_rich_text(rich_text_list):
    """Convert Notion rich_text array to formatted HTML with annotations and links."""
    html_parts = []
    for segment in rich_text_list:
        plain_text = segment.get('plain_text', '')
        if not plain_text:
            continue
        text = escape(plain_text, quote=False)
        # Preserve line breaks within text segments
        text = text.replace('\n', '<br>\n\t\t')

        annotations = segment.get('annotations', {})
        href = segment.get('href')

        # Apply inline formatting (innermost first)
        if annotations.get('code'):
            text = f"<code class='inline'>{text}</code>"
        if annotations.get('bold'):
            text = f"<strong>{text}</strong>"
        if annotations.get('italic'):
            text = f"<em>{text}</em>"
        if annotations.get('strikethrough'):
            text = f"<s>{text}</s>"
        if annotations.get('underline'):
            text = f"<u>{text}</u>"

        # Apply links (outermost wrapper)
        if href:
            path = internal_link_path(href)
            if path is not None:
                # Internal XURL link
                clean_path = path.lstrip('/')
                href_path = path if path.startswith('/') else '/' + path
                if not clean_path:
                    clean_path = 'root'
                    href_path = '/'
                safe_path = escape(href_path, quote=True)
                safe_target = escape(clean_path, quote=True)
                safe_display = escape(plain_text, quote=True)
                text = f'<a class="content-link XURL" href="{safe_path}" data-target="{safe_target}" data-title="{safe_display}">{text}</a>'
            else:
                safe_href = escape(href, quote=True)
                text = f'<a class="content-link" href="{safe_href}" target="_blank" rel="noopener noreferrer">{text}</a>'

        html_parts.append(text)

    return ''.join(html_parts)


LEADING_DATE_SEPARATOR = re.compile(
    r'^(?:&nbsp;|\xa0|\s)*'
    r'(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})'
    r'\s*(?:—|&mdash;|–|&ndash;|-)\s*'
)


def wrap_leading_date(html):
    """Keep timeline dates in a fixed-width span so the following dash lines up."""
    return LEADING_DATE_SEPARATOR.sub(
        r"<span class='date'>\1</span> — ",
        html,
        count=1,
    )


# --- Block handlers ---
# Each returns a tuple of (block_type, html_string) for list wrapping post-processing

def handle_paragraph(block, notion_client):
    rich_text = block['paragraph'].get('rich_text', [])
    text = render_rich_text(rich_text)
    if text:
        return ('paragraph', f"\t<p>\n\t\t{text}\n\t</p>\n")
    return ('paragraph', '')

def handle_heading_1(block, notion_client):
    rich_text = block['heading_1'].get('rich_text', [])
    text = render_rich_text(rich_text)
    return ('heading_1', f"\t<h3>{text}</h3>\n")

def handle_heading_2(block, notion_client):
    rich_text = block['heading_2'].get('rich_text', [])
    text = render_rich_text(rich_text)
    return ('heading_2', f"\t<h2>{text}</h2>\n")

def handle_heading_3(block, notion_client):
    rich_text = block['heading_3'].get('rich_text', [])
    text = render_rich_text(rich_text)
    return ('heading_3', f"\t<h4>{text}</h4>\n")

def handle_bulleted_list_item(block, notion_client):
    rich_text = block['bulleted_list_item'].get('rich_text', [])
    text = wrap_leading_date(render_rich_text(rich_text))
    return ('bulleted_list_item', f"\t\t<li><div>{text}</div></li>\n")

def handle_numbered_list_item(block, notion_client):
    rich_text = block['numbered_list_item'].get('rich_text', [])
    text = wrap_leading_date(render_rich_text(rich_text))
    return ('numbered_list_item', f"\t\t<li><div>{text}</div></li>\n")

def handle_table(block, notion_client):
    content = "\t<table>\n"
    table_rows = notion_client.blocks.children.list(block_id=block['id'])['results']
    for row in table_rows:
        cells = ''.join([
            f"<td>{render_rich_text(cell)}</td>"
            for cell in row['table_row']['cells']
        ])
        content += f"\t\t<tr>{cells}</tr>\n"
    content += "\t</table>\n"
    return ('table', content)

def handle_quote(block, notion_client):
    rich_text = block['quote'].get('rich_text', [])
    text = render_rich_text(rich_text)
    return ('quote', f"\t<blockquote>\n\t\t{text}\n\t</blockquote>\n")

def handle_code(block, notion_client):
    rich_text = block['code'].get('rich_text', [])
    # Use plain_text for code blocks — no HTML formatting inside code
    text = escape(''.join([t.get('plain_text', '') for t in rich_text]), quote=False)
    return ('code', f"\t<pre class='indent-c'><code class='block'>{text}</code></pre>\n")

def handle_divider(block, notion_client):
    return ('divider', "\t<div id='content-body-separator' class='center'></div>\n")


# --- Callout handlers (dispatched by emoji icon) ---

def handle_cover_image(block, rich_text):
    text = ''.join([t.get('plain_text', '') for t in rich_text])
    safe_text = escape_php_single_quoted(text)
    return ('callout', f"\t<?php $alt='{safe_text}'; require('../HTML/Fragment/Component_cover.php') ?>\n\t<h2 class='center'><?php echo $desc; ?></h2>\n")

def handle_content_image(block, rich_text):
    """🏞️ callout — text format: img_title|ext|alt|center"""
    text = ''.join([t.get('plain_text', '') for t in rich_text])
    parts = text.split('|')
    img_title = parts[0].strip() if len(parts) > 0 else ''
    ext = parts[1].strip() if len(parts) > 1 else 'svg'
    alt = parts[2].strip() if len(parts) > 2 else ''
    center = parts[3].strip() if len(parts) > 3 else ''
    php_vars = (
        f"$img_title='{escape_php_single_quoted(img_title)}'; "
        f"$ext='{escape_php_single_quoted(ext)}'; "
        f"$alt='{escape_php_single_quoted(alt)}'"
    )
    if center:
        php_vars += f"; $center='{escape_php_single_quoted(center)}'"
    return ('callout', f"\t<?php {php_vars}; require('Fragment/Component_image.php') ?>\n")

def handle_link_xurl(block, rich_text):
    """🔗 callout — one link per line, format: path|label"""
    text = ''.join([t.get('plain_text', '') for t in rich_text])
    content = ''
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        parts = line.split('|')
        if len(parts) >= 2:
            path = parts[0].strip()
            label = parts[1].strip()
            safe_path = escape_php_single_quoted(path)
            safe_label = escape_php_single_quoted(label)
            content += f"\t<?php link_xurl('{safe_path}', '{safe_label}') ?>\n"
    return ('callout', content)

def handle_raw_php(block, rich_text):
    """🔧 callout — output text verbatim as raw PHP/HTML"""
    text = ''.join([t.get('plain_text', '') for t in rich_text])
    return ('callout', f"\t{text}\n")

def handle_first_letter_high(block, rich_text):
    """🔠 callout — render an author-selected paragraph with a drop cap."""
    text = render_rich_text(rich_text)
    if text:
        return ('callout', f"\t<p class='first-letter-high'>\n\t\t{text}\n\t</p>\n")
    return ('callout', '')

def normalize_emoji(emoji):
    return (emoji or '').replace('\ufe0f', '')


def callout_emoji(block):
    icon = (block.get('callout') or {}).get('icon') or {}
    if icon.get('type') != 'emoji':
        return ''
    return icon.get('emoji', '') or ''


def handle_layout(block, rich_text):
    """📐 callout — page layout metadata; not rendered as body HTML."""
    return ('layout', '')


def handle_navigation_policy(block, rich_text):
    """🏠/🧭 callouts are rendered into config files, never page content."""
    return ('navigation', '')


def handle_callout(block, notion_client):
    emoji = callout_emoji(block)
    rich_text = block['callout'].get('rich_text', [])
    handler = CALLOUT_HANDLERS.get(emoji) or CALLOUT_HANDLERS.get(normalize_emoji(emoji))
    if handler:
        return handler(block, rich_text)
    # Default: render an unrecognized callout as a normal paragraph.
    text = render_rich_text(rich_text)
    if text:
        return ('callout', f"\t<p>\n\t\t{text}\n\t</p>\n")
    return ('callout', '')


CALLOUT_HANDLERS = {
    '🖼️': handle_cover_image,
    '🏞️': handle_content_image,
    '🔗': handle_link_xurl,
    '🔧': handle_raw_php,
    '🔠': handle_first_letter_high,
    '📐': handle_layout,
    '🏠': handle_navigation_policy,
    '🧭': handle_navigation_policy,
}

BLOCK_HANDLERS = {
    'paragraph': handle_paragraph,
    'heading_1': handle_heading_1,
    'heading_2': handle_heading_2,
    'heading_3': handle_heading_3,
    'bulleted_list_item': handle_bulleted_list_item,
    'numbered_list_item': handle_numbered_list_item,
    'table': handle_table,
    'callout': handle_callout,
    'quote': handle_quote,
    'code': handle_code,
    'divider': handle_divider,
}


# --- List wrapping ---

def wrap_lists(block_tuples):
    """Wrap consecutive list items in <ul>/<ol> tags."""
    result = []
    current_list_type = None

    for block_type, html in block_tuples:
        is_bulleted = block_type == 'bulleted_list_item'
        is_numbered = block_type == 'numbered_list_item'

        if is_bulleted and current_list_type != 'bulleted':
            if current_list_type:
                tag = 'ul' if current_list_type == 'bulleted' else 'ol'
                result.append(f"\t</{tag}>\n")
            result.append("\t<ul class=\"list-bullet content-list\">\n")
            current_list_type = 'bulleted'
        elif is_numbered and current_list_type != 'numbered':
            if current_list_type:
                tag = 'ul' if current_list_type == 'bulleted' else 'ol'
                result.append(f"\t</{tag}>\n")
            result.append("\t<ol class=\"list-bullet content-list\">\n")
            current_list_type = 'numbered'
        elif not is_bulleted and not is_numbered and current_list_type:
            tag = 'ul' if current_list_type == 'bulleted' else 'ol'
            result.append(f"\t</{tag}>\n")
            current_list_type = None

        if html:
            result.append(html)

    # Close any remaining open list
    if current_list_type:
        tag = 'ul' if current_list_type == 'bulleted' else 'ol'
        result.append(f"\t</{tag}>\n")

    return ''.join(result)


# Fetch page content blocks with pagination
def fetch_page_blocks(page_id):
    blocks = []
    has_more = True
    start_cursor = None
    while has_more:
        kwargs = {'block_id': page_id}
        if start_cursor:
            kwargs['start_cursor'] = start_cursor
        response = notion.blocks.children.list(**kwargs)
        blocks.extend(response.get('results', []))
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor')
    return blocks


def translation_language_from_title(title):
    match = NESTED_TRANSLATION_TITLE_PATTERN.fullmatch((title or '').strip())
    return match.group(1).lower() if match else None


def plain_rich_text(rich_text):
    return ''.join(item.get('plain_text', '') for item in rich_text)


LAYOUT_EMOJI = '📐'
HOME_POLICY_EMOJI = '🏠'
SIDE_POLICY_EMOJI = '🧭'
ME_TABLE_HEADINGS = {'heading_1', 'heading_2', 'heading_3'}
PROFILE_LINK_IDS = (
    ('linkedin.com', 'linkedin-badge'),
    ('stackoverflow.com/users', 'stackoverflow-badge'),
    ('facebook.com', 'facebook-badge'),
)


def parse_page_layout(blocks):
    """Read a 📐 callout: layout name plus optional bottom: nav|default."""
    for block in blocks:
        if block.get('type') != 'callout':
            continue
        if normalize_emoji(callout_emoji(block)) != LAYOUT_EMOJI:
            continue
        text = plain_rich_text((block.get('callout') or {}).get('rich_text', []))
        fields = {}
        tokens = []
        for line in text.replace('<br>', '\n').splitlines():
            line = line.strip()
            if not line:
                continue
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                fields[key] = value
                if key in ('layout', 'name') and value:
                    tokens.append(value)
            else:
                tokens.append(line)
        name = (
            fields.get('layout')
            or fields.get('name')
            or (tokens[0] if tokens else '')
        ).strip().lower()
        if not name:
            continue
        bottom = (fields.get('bottom') or '').strip().lower()
        if bottom not in ('nav', 'default'):
            bottom = 'nav' if name == 'me-table' else 'default'
        return {
            'block_id': block.get('id'),
            'name': name,
            'bottom': bottom,
        }
    return None


def _nav_slug(value, field):
    if not isinstance(value, str) or not NAV_SLUG_PATTERN.fullmatch(value):
        raise ValueError(f'{field} must be a lowercase component slug: {value!r}')
    return value


def _nav_slug_list(value, field):
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f'{field} must be a list of slugs')
    slugs = [_nav_slug(item, field) for item in value]
    if len(slugs) != len(set(slugs)):
        raise ValueError(f'{field} contains duplicate slugs')
    return slugs


def validate_home_policy(policy):
    if not isinstance(policy, dict):
        raise ValueError('Home menu policy must be a JSON object')
    allowed = {'branch', 'syntheticChildren', 'leafSlugs', 'capChildrenOf',
               'largeGroupSlugs', 'selectedChildren', 'childLimits'}
    if set(policy) - allowed:
        raise ValueError(f'Unknown home menu policy keys: {set(policy) - allowed}')
    _nav_slug(policy.get('branch'), 'branch')
    for key in ('leafSlugs', 'capChildrenOf', 'largeGroupSlugs'):
        _nav_slug_list(policy.get(key, []), key)
    for key in ('syntheticChildren', 'selectedChildren'):
        rules = policy.get(key, {})
        if not isinstance(rules, dict):
            raise ValueError(f'{key} must be an object')
        for parent, children in rules.items():
            _nav_slug(parent, key)
            slugs = _nav_slug_list(children, f'{key}.{parent}')
            if key == 'selectedChildren' and any(
                child.rpartition('/')[0] != parent for child in slugs
            ):
                raise ValueError(f'{key}.{parent} must contain direct children')
    limits = policy.get('childLimits', {})
    if not isinstance(limits, dict):
        raise ValueError('childLimits must be an object')
    for parent, limit in limits.items():
        _nav_slug(parent, 'childLimits')
        if type(limit) is not int or limit < 1:
            raise ValueError(f'childLimits.{parent} must be a positive integer')
    return policy


def validate_side_policy(policy):
    if not isinstance(policy, dict) or set(policy) - {'groups', 'labels'} or 'groups' not in policy:
        raise ValueError('Side menu policy needs groups and optional labels')
    groups = policy['groups']
    if not isinstance(groups, list) or not groups:
        raise ValueError('Side menu groups must be a nonempty list')
    seen = set()
    for group in groups:
        if (not isinstance(group, dict) or 'kind' not in group or 'items' not in group
                or set(group) - {'kind', 'items', 'includeHomeHubs'}):
            raise ValueError('Each side menu group needs kind and items')
        if group['kind'] not in ('image', 'text'):
            raise ValueError('Side menu kind must be image or text')
        items = _nav_slug_list(group['items'], 'side menu items')
        if 'includeHomeHubs' in group and type(group['includeHomeHubs']) is not bool:
            raise ValueError('includeHomeHubs must be a boolean')
        if not items or seen.intersection(items):
            raise ValueError('Side menu groups need unique, nonempty items')
        seen.update(items)
    labels = policy.get('labels', {})
    if not isinstance(labels, dict):
        raise ValueError('Side menu labels must be an object')
    for slug, translations in labels.items():
        _nav_slug(slug, 'labels')
        if not isinstance(translations, dict):
            raise ValueError(f'Side menu labels.{slug} must be an object')
        for language, label in translations.items():
            if not LANGUAGE_PREFIX_PATTERN.fullmatch(language) and language != 'en':
                raise ValueError(f'Invalid side menu language: {language!r}')
            if not isinstance(label, str) or not label.strip():
                raise ValueError(f'Side menu labels.{slug}.{language} must be text')
    return policy


def parse_navigation_policy(block, name, validator):
    """Read one JSON code child of a named Notion navigation callout."""
    if not block.get('has_children'):
        raise ValueError(f'{name} callout needs one JSON code child')
    children = fetch_page_blocks(block['id'])
    if len(children) != 1 or children[0].get('type') != 'code':
        raise ValueError(f'{name} callout needs exactly one JSON code child')
    source = plain_rich_text(children[0]['code'].get('rich_text', []))
    try:
        return validator(json.loads(source))
    except json.JSONDecodeError as error:
        raise ValueError(f'{name} contains invalid JSON: {error}') from error


def extract_home_navigation(blocks):
    found = {}
    for block in blocks:
        if block.get('type') != 'callout':
            continue
        emoji = normalize_emoji(callout_emoji(block))
        if emoji not in (HOME_POLICY_EMOJI, SIDE_POLICY_EMOJI):
            continue
        name, validator = (
            ('home', validate_home_policy) if emoji == HOME_POLICY_EMOJI
            else ('side', validate_side_policy)
        )
        if name in found:
            raise ValueError(f'Duplicate {name} navigation callout')
        found[name] = parse_navigation_policy(block, name, validator)
    if set(found) != {'home', 'side'}:
        raise ValueError('The root page needs 🏠 and 🧭 navigation callouts')
    return found


def heading_plain(block):
    block_type = block.get('type')
    rich_text = (block.get(block_type) or {}).get('rich_text', [])
    return render_rich_text(rich_text)


def apply_profile_link_ids(html):
    """Keep About-me badge CSS hooks on well-known profile links."""
    for needle, element_id in PROFILE_LINK_IDS:
        pattern = re.compile(
            r'<a (?![^>]*\bid=)([^>]*href="[^"]*'
            + re.escape(needle)
            + r'[^"]*")',
            re.IGNORECASE,
        )
        html = pattern.sub(rf"<a id='{element_id}' \1", html, count=1)
    return html


def me_table_html(rows):
    parts = ["\t<div id='me-table'>\n"]
    for row in rows:
        value = '<br>\n\t\t\t\t'.join(part for part in row['parts'] if part)
        value = apply_profile_link_ids(value)
        parts.append("\t\t<div>\n")
        parts.append(f"\t\t\t<div class='R1'>{row['label']}</div>\n")
        parts.append("\t\t\t<div class='R2'>\n")
        parts.append(f"\t\t\t\t{value}\n")
        parts.append("\t\t\t</div>\n")
        parts.append("\t\t</div>\n")
    parts.append("\t</div>\n")
    return ''.join(parts)


def render_labeled_profile(blocks, skip_block_ids):
    """Heading + following paragraphs become #me-table rows; keep the CSS contract."""
    skip_block_ids = set(skip_block_ids)
    prefix_tuples = []
    tail_tuples = []
    rows = []
    current = None
    phase = 'prefix'

    def flush_row():
        nonlocal current
        if current and current.get('label'):
            rows.append(current)
        current = None

    def handle_standard(block):
        handler = BLOCK_HANDLERS.get(block.get('type'))
        if not handler:
            return None
        result = handler(block, notion)
        return result if result and result[1] else None

    for block in blocks:
        if block.get('id') in skip_block_ids or block.get('type') == 'child_page':
            continue
        block_type = block.get('type')
        if phase == 'prefix':
            if block_type in ME_TABLE_HEADINGS:
                phase = 'rows'
                current = {'label': heading_plain(block), 'parts': []}
            else:
                result = handle_standard(block)
                if result:
                    prefix_tuples.append(result)
            continue
        if phase == 'rows':
            if block_type in ME_TABLE_HEADINGS:
                flush_row()
                current = {'label': heading_plain(block), 'parts': []}
                continue
            if block_type == 'divider':
                flush_row()
                phase = 'tail'
                result = handle_standard(block)
                if result:
                    tail_tuples.append(result)
                continue
            if current is None:
                result = handle_standard(block)
                if result:
                    tail_tuples.append(result)
                phase = 'tail'
                continue
            if block_type == 'paragraph':
                text = render_rich_text((block.get('paragraph') or {}).get('rich_text', []))
                if text:
                    current['parts'].append(text)
                continue
            if block_type in ('bulleted_list_item', 'numbered_list_item'):
                rich_text = (block.get(block_type) or {}).get('rich_text', [])
                text = wrap_leading_date(render_rich_text(rich_text))
                if text:
                    current['parts'].append(text)
                continue
            flush_row()
            phase = 'tail'
            result = handle_standard(block)
            if result:
                tail_tuples.append(result)
            continue
        result = handle_standard(block)
        if result:
            tail_tuples.append(result)
    flush_row()

    html_parts = []
    prefix_html = wrap_lists(prefix_tuples)
    if prefix_html:
        html_parts.append(prefix_html)
    if rows:
        html_parts.append(me_table_html(rows))
    html_parts.append(wrap_lists(tail_tuples))
    return ''.join(html_parts)


def parse_translation_metadata(blocks, expected_language):
    for block in blocks:
        if block.get('type') != 'callout':
            continue
        callout = block.get('callout', {})
        icon = callout.get('icon', {})
        if icon.get('type') != 'emoji' or icon.get('emoji') != '🌐':
            continue
        text = plain_rich_text(callout.get('rich_text', []))
        fields = {}
        for line in text.replace('<br>', '\n').splitlines():
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            fields[key.strip().lower()] = value.strip()
        language = fields.get('language', '').lower()
        if language != expected_language:
            raise RuntimeError(
                f"Nested translation language mismatch: title={expected_language!r}, "
                f"metadata={language!r}"
            )
        required = ('label', 'title', 'description')
        missing = [key for key in required if not fields.get(key)]
        if missing:
            raise RuntimeError(
                f"Nested translation {language!r} is missing metadata: {missing}"
            )
        return {
            'language': language,
            'label': fields['label'],
            'title': fields['title'],
            'description': fields['description'],
            'metadata_block_id': block.get('id'),
        }
    raise RuntimeError(
        f"Nested translation {expected_language!r} is missing its 🌐 metadata callout"
    )


def render_page_blocks(blocks, skip_block_ids=(), layout=None):
    layout = layout if layout is not None else parse_page_layout(blocks)
    skip_block_ids = set(skip_block_ids)
    if layout and layout.get('block_id'):
        skip_block_ids.add(layout['block_id'])
    if layout and layout.get('name') == 'me-table':
        return render_labeled_profile(blocks, skip_block_ids)
    block_tuples = []
    for block in blocks:
        if block.get('id') in skip_block_ids:
            continue
        block_type = block['type']
        handler = BLOCK_HANDLERS.get(block_type)
        if handler:
            result = handler(block, notion)
            if result[1]:
                block_tuples.append(result)
    return wrap_lists(block_tuples)


def render_article_body(blocks, extra_skip=()):
    layout = parse_page_layout(blocks)
    html = render_page_blocks(blocks, skip_block_ids=extra_skip, layout=layout)
    return html, layout


def localize_xurl_links(html, language):
    """Keep canonical data-target values while routing translated links by language."""
    if language == 'en':
        return html
    pattern = re.compile(r'(<a class="content-link XURL" href=")(/[^"]*)(")')

    def replace(match):
        path = match.group(2)
        if path == f'/{language}' or path.startswith(f'/{language}/'):
            return match.group(0)
        return f'{match.group(1)}/{language}{path}{match.group(3)}'

    return pattern.sub(replace, html)


def fetch_page_content(page_id):
    html, _layout = render_article_body(fetch_page_blocks(page_id))
    return html


def extract_nested_translations(page_blocks, base_article):
    translations = []
    seen_languages = set()
    for block in page_blocks:
        if block.get('type') != 'child_page':
            continue
        title = block.get('child_page', {}).get('title', '')
        language = translation_language_from_title(title)
        if not language:
            continue
        if language == 'en':
            raise RuntimeError('English must remain on the base database page')
        if language in seen_languages:
            raise RuntimeError(
                f"Duplicate nested translation {language!r} for {base_article['slug']}"
            )
        child_blocks = fetch_page_blocks(block['id'])
        metadata = parse_translation_metadata(child_blocks, language)
        content, child_layout = render_article_body(
            child_blocks,
            extra_skip=(metadata['metadata_block_id'],),
        )
        content = localize_xurl_links(content, language)
        translations.append({
            'id': block['id'],
            'status': base_article['status'],
            'slug': base_article['slug'],
            'language': language,
            'translation_group': base_article['slug'],
            'label': metadata['label'],
            'title': metadata['title'],
            'js': base_article['js'],
            'description': metadata['description'],
            'type': base_article['type'],
            'content': content,
            'layout': child_layout or base_article.get('layout'),
        })
        seen_languages.add(language)
    return translations
# Extract fields with corrected slug handling
def extract_fields(database_content, included_statuses=('publish',)):
    """Extract articles whose status is explicitly allowed by the caller."""
    articles = []
    included_statuses = set(included_statuses)
    for page in database_content:
        properties = page['properties']
        def get_rich_text(prop_name, default=""):
            prop = properties.get(prop_name, {})
            rich_text = prop.get('rich_text', [])
            return rich_text[0]['plain_text'] if rich_text else default

        def get_flags():
            prop = properties.get("Flags", {})
            if prop.get("rich_text"):
                return " ".join(
                    item.get("plain_text", "") for item in prop["rich_text"]
                    if item.get("plain_text")
                )
            if prop.get("select"):
                return prop["select"].get("name", "")
            if prop.get("multi_select"):
                return " ".join(
                    item.get("name", "") for item in prop["multi_select"]
                    if item.get("name")
                )
            return ""

        slug = properties["Id"]["title"][0]["plain_text"] if properties["Id"].get("title") else ""
        language = "en"
        if properties.get("Language") and properties["Language"].get("select") and properties["Language"]["select"]:
            language = properties["Language"]["select"]["name"]
        translation_group = slug
        if properties.get("TranslationGroup") and properties["TranslationGroup"].get("rich_text"):
            tg = properties["TranslationGroup"]["rich_text"]
            if tg:
                translation_group = tg[0]["plain_text"]
        status = properties["Status"]["select"]["name"] if properties["Status"].get("select") else ""
        if status not in included_statuses:
            if status in ("draft", "published", "test", "publish"):
                print(f"Skipping ({status}): Id={slug}")
            else:
                print(f"Unknown status '{status}' for Id={slug}")
            continue

        page_blocks = fetch_page_blocks(page["id"])
        content, layout = render_article_body(page_blocks)
        navigation = None
        if slug == 'root':
            if not layout or layout.get('name') != 'home':
                raise ValueError('The root page requires a 📐 home layout callout')
            navigation = extract_home_navigation(page_blocks)
        article = {
            "id": page["id"],
            "status": status,
            "slug": slug,
            "language": language,
            "translation_group": translation_group,
            "label": get_rich_text("Label"),
            "title": get_rich_text("Title"),
            "js": properties["JS"]["select"]["name"] if properties["JS"].get("select") else "0",
            "description": get_rich_text("Description"),
            "type": properties["Type"]["select"]["name"] if properties.get("Type", {}).get("select") else "",
            "content": content,
        }
        if layout:
            article["layout"] = layout
        if navigation:
            article['navigation'] = navigation
        if "Flags" in properties:
            article["flags"] = get_flags()
        articles.append(article)
        translations = extract_nested_translations(page_blocks, article)
        articles.extend(translations)
        print(f"Extracted article: Id={article['slug']}, Title={article['title']}")
        for translation in translations:
            print(
                f"Extracted nested translation: Id={translation['slug']}, "
                f"Language={translation['language']}, Title={translation['title']}"
            )
    return articles

# Update ID.tsv with overwrite for existing entries (per-language files)
def update_id_tsv(articles, output_base):
    # Group articles by language
    by_lang = {}
    for article in articles:
        lang = article.get('language', 'en')
        by_lang.setdefault(lang, []).append(article)

    for lang, lang_articles in by_lang.items():
        suffix = '' if lang == 'en' else f'_{lang}'
        id_tsv_path = os.path.join(output_base, f'Config/ID{suffix}.tsv')
        os.makedirs(os.path.dirname(id_tsv_path), exist_ok=True)

        default_header = ['Status', 'Id', 'Label', 'Title', 'JS', 'Description', 'Type']
        include_flags = any('flags' in article for article in lang_articles)

        # Read existing entries to detect updates
        header = default_header
        existing_entries = {}
        if os.path.exists(id_tsv_path):
            with open(id_tsv_path, 'r', encoding='utf-8') as f:
                rows = [line.rstrip('\r\n').split('\t') for line in f if line.strip()]
            if rows and 'id' in [column.lower() for column in rows[0]]:
                header = rows.pop(0)
            id_index = next(
                (i for i, column in enumerate(header) if column.lower() == 'id'),
                1
            )
            include_flags = include_flags or any(
                column.lower() == 'flags' for column in header
            )
            for row in rows:
                if len(row) > id_index:
                    existing_entries[row[id_index]] = row

        if not any(column.lower() == 'type' for column in header):
            header.append('Type')

        if include_flags and not any(column.lower() == 'flags' for column in header):
            header.append('Flags')

        column_keys = [column.lower() for column in header]
        article_keys = {
            'status': 'status',
            'id': 'slug',
            'label': 'label',
            'title': 'title',
            'js': 'js',
            'description': 'description',
            'type': 'type',
            'flags': 'flags',
        }

        # Update or add new entries
        for article in lang_articles:
            row = []
            for column in column_keys:
                key = article_keys.get(column)
                row.append(str(article.get(key, '')) if key else '')
            existing_entries[article['slug']] = row

        with open(id_tsv_path, 'w', encoding='utf-8') as f:
            f.write('\t'.join(header) + '\n')
            for row in existing_entries.values():
                row = row + [''] * (len(header) - len(row))
                f.write('\t'.join(row[:len(header)]) + '\n')
        print(f"Updated {id_tsv_path}")

    # Generate Translations.tsv cross-index
    update_translations_tsv(articles, output_base)

def update_translations_tsv(articles, output_base):
    """Generate Config/Translations.tsv — maps translation groups to per-language status."""
    trans_path = os.path.join(output_base, 'Config/Translations.tsv')
    os.makedirs(os.path.dirname(trans_path), exist_ok=True)

    # Collect all languages present
    all_langs = sorted(set(a.get('language', 'en') for a in articles))
    # Ensure 'en' is first
    if 'en' in all_langs:
        all_langs.remove('en')
        all_langs.insert(0, 'en')

    # Read existing entries
    existing = {}
    if os.path.exists(trans_path):
        with open(trans_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                header = lines[0].strip().split('\t')
                old_langs = header[1:]
                for line in lines[1:]:
                    parts = line.strip().split('\t')
                    if parts:
                        group = parts[0]
                        existing[group] = {}
                        for i, lang in enumerate(old_langs):
                            if i + 1 < len(parts):
                                existing[group][lang] = parts[i + 1]

    # Merge new articles into existing data
    for article in articles:
        group = article.get('translation_group', article['slug'])
        lang = article.get('language', 'en')
        if lang not in all_langs:
            all_langs.append(lang)
        if group not in existing:
            existing[group] = {}
        existing[group][lang] = article['status']

    # Write
    with open(trans_path, 'w', encoding='utf-8') as f:
        f.write('TranslationGroup\t' + '\t'.join(all_langs) + '\n')
        for group in sorted(existing.keys()):
            row = [group]
            for lang in all_langs:
                row.append(existing[group].get(lang, ''))
            f.write('\t'.join(row) + '\n')
    print(f"Updated {trans_path}")

# Update Url.tsv with overwrite for existing entries (per-language)
def update_url_tsv(articles, output_base):
    by_lang = {}
    for article in articles:
        lang = article.get('language', 'en')
        by_lang.setdefault(lang, []).append(article)

    for lang, lang_articles in by_lang.items():
        # Shared covers belong in Url.tsv. Language files are hand-maintained
        # for language-specific assets only (for example hi/computer/*.svg).
        if lang != 'en':
            continue
        url_tsv_path = os.path.join(output_base, 'Config/Url.tsv')
        os.makedirs(os.path.dirname(url_tsv_path), exist_ok=True)

        existing_entries = {}
        if os.path.exists(url_tsv_path):
            with open(url_tsv_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 1:
                        existing_entries[parts[0]] = line.strip()

        with open(url_tsv_path, 'w', encoding='utf-8') as f:
            for article in lang_articles:
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
    translated_languages = {
        article.get('language', 'en')
        for article in articles
        if article.get('language', 'en') != 'en'
    }

    config_dir = os.path.join(output_base, 'Config')
    if os.path.isdir(config_dir):
        for filename in os.listdir(config_dir):
            match = re.fullmatch(r'ID_([A-Za-z]{2,3}(?:-[A-Za-z]{2})?)\.tsv', filename)
            if match:
                translated_languages.add(match.group(1).lower())

    for lang in sorted(translated_languages):
        rewrites.append({
            "source": f"/{lang}/menu",
            "destination": f"/{lang}/root/index.html"
        })

    for article in articles:
        slug = article['slug']
        lang = article.get('language', 'en')
        slug_parts = slug.split('/')

        if lang == 'en':
            prefix = ''
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
        else:
            prefix = f'/{lang}'
            rewrites.extend([
                {"source": f"{prefix}/{slug}.json", "destination": f"{prefix}/{slug}/index.json"},
                {"source": f"{prefix}/{slug}.jpg", "destination": f"{prefix}/{slug}/index.jpg"}
            ])

    firebase_data["hosting"]["redirects"] = redirects
    firebase_data["hosting"]["rewrites"] = rewrites

    # if directory does not exist, create it
    os.makedirs(os.path.dirname(firebase_json_path), exist_ok=True)
    with open(firebase_json_path, 'w', encoding='utf-8') as f:
        json.dump(firebase_data, f, indent=4)
    print(f"Updated {firebase_json_path}")

# Update sitemap.xml with overwrite for existing URLs and hreflang
def update_sitemap_xml(articles, output_base):
    sitemap_xml_path = os.path.join(output_base, 'Site/sitemap.xml')
    os.makedirs(os.path.dirname(sitemap_xml_path), exist_ok=True)
    base_url = "https://ujnotes.com"

    # Group by translation_group for hreflang cross-references
    groups = {}
    for article in articles:
        group = article.get('translation_group', article['slug'])
        groups.setdefault(group, []).append(article)

    urlset_start = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    urlset_end = '</urlset>'
    new_urls = []

    for _, group_articles in groups.items():
        for article in group_articles:
            lang = article.get('language', 'en')
            prefix = '' if lang == 'en' else f'/{lang}'
            loc = f"{base_url}{prefix}/{article['slug']}"

            url_entry = f"\t<url>\n\t\t<loc>{loc}</loc>\n"

            # Add hreflang alternates if multiple languages exist
            if len(group_articles) > 1:
                for alt in group_articles:
                    alt_lang = alt.get('language', 'en')
                    alt_prefix = '' if alt_lang == 'en' else f'/{alt_lang}'
                    alt_href = f"{base_url}{alt_prefix}/{alt['slug']}"
                    url_entry += f"\t\t<xhtml:link rel=\"alternate\" hreflang=\"{alt_lang}\" href=\"{alt_href}\" />\n"
                # x-default points to English
                url_entry += f"\t\t<xhtml:link rel=\"alternate\" hreflang=\"x-default\" href=\"{base_url}/{article['slug']}\" />\n"

            url_entry += "\t</url>\n"
            new_urls.append(url_entry)

    with open(sitemap_xml_path, 'w', encoding='utf-8') as f:
        f.write(urlset_start + ''.join(new_urls) + urlset_end)
    print(f"Updated {sitemap_xml_path} with {len(new_urls)} URLs")

# Helper function for running git commands with error capture
def _run_cmd(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)

# Call push_git.sh equivalent
def push_git(output_base):
    try:
        # Stage all changes
        result = _run_cmd(["git", "add", "-A"], cwd=output_base)
        if result.returncode != 0:
            print(f"Git add failed: {result.stderr}")
            return False

        # Check if there are staged changes
        result = _run_cmd(["git", "diff", "--cached", "--quiet"], cwd=output_base)
        if result.returncode == 0:
            # No staged changes - nothing to commit
            print("No changes to commit")
            return True

        # Commit staged changes
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        commit_message = f"Update articles from Notion - {timestamp}"
        result = _run_cmd(["git", "commit", "-m", commit_message], cwd=output_base)
        if result.returncode != 0:
            print(f"Git commit failed: {result.stderr}")
            return False

        # Push to remote
        result = _run_cmd(["git", "push", "-u", "origin", "main"], cwd=output_base)
        if result.returncode != 0:
            print(f"Git push failed: {result.stderr}")
            return False

        print("Git push successful")
        return True
    except Exception as e:
        print(f"Unexpected error during git operations: {e}")
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

def compose_php_page(article):
    """Wrap rendered Notion HTML in the Cutie component shell for this layout."""
    layout = article.get('layout') or {}
    name = (layout.get('name') or '').strip().lower()
    bottom = (layout.get('bottom') or '').strip().lower()
    content = article.get('content') or ''
    if article.get('slug') == 'root':
        if name != 'home':
            raise ValueError('The root page requires the home layout')
        return '\n'.join([
            "<div id='message'>",
            "\t<div>",
            "\t\t<div id='home-message'>",
            content,
            "\t\t</div>",
            "\t\t<div id='profile-image-container' class='message_leave'>",
            "\t\t\t<a id='profile-image' href='#'><img src='/photo.jpg' alt=\"Author's picture\"></a>",
            "\t\t</div>",
            "\t</div>",
            "</div>",
            "<div class='center' id='content-body-separator'></div>",
            "<div class='message_center_div' id='home-menu'>",
            "\t<section class='home-menu-branch' aria-label=\"<?php echo htmlspecialchars(getComponentLabel(home_menu_branch_slug()), ENT_QUOTES, 'UTF-8') ?>\">",
            "\t\t<?php home_menu_render_branch(home_menu_branch_slug()); ?>",
            "\t</section>",
            "</div>",
            "<div id='fb_components'>",
            "\t<?php require('../HTML/Fragment/Component_FB_buttons.php') ?>",
            "</div>",
        ])
    if name == 'me-table':
        if bottom not in ('nav', 'default'):
            bottom = 'nav'
        message_open = "<div id='message' class='center'>"
        js_include = ""
    else:
        if bottom not in ('nav', 'default'):
            bottom = 'default'
        message_open = "<div id='message'>"
        js_include = "<?php require('../JS/Base/page.js'); ?>" if article.get('js') == "1" else ""
    bottom_file = (
        'Component_bottom_nav.php' if bottom == 'nav' else 'Component_bottom.php'
    )
    lines = [
        message_open,
        f"\t{content}",
        "</div>",
    ]
    if js_include:
        lines.append(js_include)
    lines.append(f"<?php require('../HTML/Fragment/{bottom_file}') ?>")
    return '\n'.join(lines)


# Transform to PHP with correct directory structure and auto-indent
def transform_to_php(articles):
    if not output_dir:
        print("Error: OUTPUT_DIR not set in .env, defaulting to 'test'")
        output_base = 'test'
    else:
        output_base = output_dir
    written_dirs = set()

    for article in articles:
        lang = article.get('language', 'en')
        if lang == 'en':
            output_base_html = os.path.join(output_base, 'HTML/Component/')
        else:
            output_base_html = os.path.join(output_base, f'HTML/Component/{lang}/')

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

        php_code = compose_php_page(article)

        print(f"Writing to: {full_file_path}")
        try:
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(php_code)
        except Exception as e:
            print(f"Error writing to {full_file_path}: {e}")

        if article['slug'] == 'root' and article.get('language', 'en') == 'en':
            config_dir = os.path.join(output_base, 'Config')
            os.makedirs(config_dir, exist_ok=True)
            for key, filename in (('home', 'Home.json'), ('side', 'Menu.json')):
                target = os.path.join(config_dir, filename)
                with open(target, 'w', encoding='utf-8', newline='\n') as stream:
                    json.dump(article['navigation'][key], stream, ensure_ascii=False, indent=2)
                    stream.write('\n')

    # Perform additional updates
    update_id_tsv(articles, output_dir or '.')
    update_url_tsv(articles, output_dir or '.')
    update_firebase_json(articles, output_dir or '.')
    update_sitemap_xml(articles, output_dir or '.')

    # Push to Git if enabled
    if git_push_enabled:
        push_git(project_dir)
    else:
        print("Git push disabled (set GIT_PUSH=true to enable)")

    # Update Notion status if enabled
    if notion_update_enabled:
        update_notion_status(articles)
    else:
        print("Notion status update disabled (set NOTION_UPDATE=true to enable)")

def write_ids_tsv(articles):
    """Write article metadata to a TSV file, including Flags when available.
    Updates the row if an entry with the same Id exists; otherwise, appends a new row.
    The file is located at output/config/ID.tsv."""
    file_path = "output/config/ID.tsv"
    # if directory does not exist, create it
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
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
    include_flags = any("flags" in article for article in articles)
    header = ["Status", "Id", "Label", "Title", "JS", "Description", "Type"]
    if include_flags:
        header.append("Flags")
    for article in articles:
        row = [
            article["status"], article["slug"], article["label"],
            article["title"], article["js"], article["description"],
            article.get("type", "")
        ]
        if include_flags:
            row.append(article.get("flags", ""))
        existing[article["slug"]] = row
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\t".join(header) + "\n")
        for row in existing.values():
            row = row + [""] * (len(header) - len(row))
            f.write("\t".join(row[:len(header)]) + "\n")

def page_slug(page):
    title = page.get("properties", {}).get("Id", {}).get("title", [])
    return title[0].get("plain_text", "") if title else ""


def validate_slug(slug):
    if (
        not slug
        or slug.startswith("/")
        or slug.endswith("/")
        or "\\" in slug
        or any(part in {".", ".."} for part in slug.split("/"))
        or not SAFE_SLUG_PATTERN.fullmatch(slug)
    ):
        raise ValueError(f"Unsafe article slug: {slug!r}")
    return slug


def parse_publish_target(requested_slug, candidate_slugs=()):
    """Resolve a publish request into (base_slug, language_or_None).

    Public translation URLs use a language prefix (for example
    ``hi/world/philosophy/hindu``). Notion page Ids stay unprefixed. Prefer an
    exact Id match when the request equals a queued slug so article Ids that
    look like ``faq/...`` are not treated as language prefixes.
    """
    requested_slug = validate_slug(requested_slug)
    candidate_slugs = set(candidate_slugs)
    if requested_slug in candidate_slugs:
        return requested_slug, None
    parts = requested_slug.split("/", 1)
    if len(parts) == 2:
        language, remainder = parts[0].lower(), parts[1]
        if LANGUAGE_PREFIX_PATTERN.fullmatch(language):
            validate_slug(remainder)
            if not candidate_slugs or remainder in candidate_slugs:
                return remainder, language
    return requested_slug, None


def select_publish_page(pages, requested_slug=None):
    candidates = [{"slug": page_slug(page), "page_id": page["id"]} for page in pages]
    if requested_slug:
        base_slug, language = parse_publish_target(
            requested_slug,
            [item["slug"] for item in candidates],
        )
        selected = [page for page in pages if page_slug(page) == base_slug]
        if len(selected) != 1:
            raise RuntimeError(
                f"Expected one publish page for {requested_slug!r}; found {len(selected)}. "
                f"Queued: {[item['slug'] for item in candidates]}"
            )
        return selected[0], candidates, language

    if len(pages) != 1:
        raise RuntimeError(
            "Expected exactly one page with Status=publish. "
            f"Found {len(pages)}: {[item['slug'] for item in candidates]}. "
            "Pass --slug to select one explicitly."
        )
    validate_slug(page_slug(pages[0]))
    return pages[0], candidates, None


def publish_to_bundle(status, slug, bundle_dir, metadata_file, allow_empty=False):
    global output_dir, project_dir, git_push_enabled, notion_update_enabled

    if not database_id:
        raise RuntimeError("NOTION_DATABASE_ID is not set")

    bundle_dir = os.path.abspath(bundle_dir)
    metadata_file = os.path.abspath(metadata_file)
    os.makedirs(bundle_dir, exist_ok=True)
    os.makedirs(os.path.dirname(metadata_file), exist_ok=True)

    pages = resolve_publish_pages(database_id, status=status, requested_slug=slug)
    if not pages and allow_empty:
        metadata = {"no_work": True, "queued_slugs": []}
        with open(metadata_file, "w", encoding="utf-8", newline="\n") as target:
            json.dump(metadata, target, ensure_ascii=False, indent=2)
            target.write("\n")
        print("No queued Notion pages found")
        return metadata

    selected, candidates, requested_language = select_publish_page(pages, slug)

    output_dir = bundle_dir
    project_dir = bundle_dir
    git_push_enabled = False
    notion_update_enabled = False

    articles = extract_fields([selected], included_statuses=(status,))
    if not articles:
        raise RuntimeError("Expected at least one extracted article")
    base_articles = [
        article for article in articles if article.get("language", "en") == "en"
    ]
    if len(base_articles) != 1:
        raise RuntimeError(
            f"Expected one English base article; got {len(base_articles)}"
        )
    base_article = base_articles[0]

    if requested_language:
        articles = [
            article
            for article in articles
            if article.get("language", "en") == requested_language
        ]
        if not articles:
            raise RuntimeError(
                f"No {requested_language!r} translation for {base_article['slug']!r}"
            )

    transform_to_php(articles)
    variants = []
    for article in articles:
        language = article.get("language", "en")
        component_parts = ["HTML", "Component"]
        if language != "en":
            component_parts.append(language)
        component_parts.extend(article["slug"].split("/"))
        component_parts.append("index.php")
        component_path = os.path.join(bundle_dir, *component_parts)
        if not os.path.isfile(component_path) or os.path.getsize(component_path) == 0:
            raise RuntimeError(
                f"Generated component is missing or empty: {component_path}"
            )
        variants.append({
            "slug": article["slug"],
            "title": article["title"],
            "description": article["description"],
            "language": language,
            "component": os.path.relpath(component_path, bundle_dir).replace("\\", "/"),
        })

    primary_variant = variants[0]
    metadata = {
        "page_id": base_article["id"],
        "slug": base_article["slug"],
        "title": primary_variant["title"],
        "description": primary_variant["description"],
        "language": primary_variant["language"],
        "component": primary_variant["component"],
        "variants": variants,
        "queued_slugs": [item["slug"] for item in candidates],
    }
    if requested_language:
        metadata["requested_language"] = requested_language
        metadata["translation_merge"] = True
    with open(metadata_file, "w", encoding="utf-8", newline="\n") as target:
        json.dump(metadata, target, ensure_ascii=False, indent=2)
        target.write("\n")

    print("NCMS_RESULT=" + json.dumps(metadata, ensure_ascii=True))
    return metadata


def sync_home(status, site_project):
    """Refresh the local homepage source and menu policies from the root row."""
    global output_dir, project_dir, git_push_enabled, notion_update_enabled
    if not database_id:
        raise RuntimeError('NOTION_DATABASE_ID is not set')
    pages = fetch_page_by_id_title(database_id, 'root', status=status)
    if len(pages) != 1:
        raise RuntimeError(f'Expected one root page with Status={status}; found {len(pages)}')
    articles = extract_fields(pages, included_statuses=(status,))
    if not articles or articles[0]['slug'] != 'root':
        raise RuntimeError('NCMS did not extract the root page')

    site_project = Path(site_project).resolve()
    if not (site_project / 'config' / 'ID.tsv').is_file():
        raise RuntimeError(f'Not a site project: {site_project}')
    with tempfile.TemporaryDirectory(prefix='ncms-home-') as temporary:
        output_dir = temporary
        project_dir = temporary
        git_push_enabled = False
        notion_update_enabled = False
        transform_to_php(articles)
        copies = [
            (Path(temporary) / 'Config' / name, site_project / 'config' / name)
            for name in ('Home.json', 'Menu.json')
        ]
        for article in articles:
            if article['slug'] != 'root':
                continue
            language = article.get('language', 'en')
            source = Path(temporary) / 'HTML' / 'Component'
            if language != 'en':
                source /= language
            source = source / 'root' / 'index.php'
            destination = site_project / 'root' / 'HTML' / 'Component'
            destination = (destination / 'Root.php' if language == 'en'
                           else destination / language / 'Root' / 'index.php')
            copies.append((source, destination))
        for source, destination in copies:
            if not source.is_file() or source.stat().st_size == 0:
                raise RuntimeError(f'Missing generated homepage artifact: {source}')
            destination.parent.mkdir(parents=True, exist_ok=True)
            staged = destination.with_name(destination.name + '.ncms-tmp')
            try:
                shutil.copyfile(source, staged)
                os.replace(staged, destination)
            finally:
                staged.unlink(missing_ok=True)
            print(f'Synced {destination}')
    return articles


def mark_published(page_id, expected_slug):
    validate_slug(expected_slug)
    page = notion.pages.retrieve(page_id=page_id)
    actual_slug = page_slug(page)
    if actual_slug != expected_slug:
        raise RuntimeError(
            f"Notion page slug changed: expected {expected_slug!r}, got {actual_slug!r}"
        )

    status_property = page.get("properties", {}).get("Status", {}).get("select")
    status_name = status_property.get("name") if status_property else ""
    if status_name not in {"publish", "published"}:
        raise RuntimeError(f"Refusing to update unexpected status {status_name!r}")

    if status_name != "published":
        notion.pages.update(
            page_id=page_id,
            properties={"Status": {"select": {"name": "published"}}},
        )

    check = notion.pages.retrieve(page_id=page_id)
    final_status = (
        check.get("properties", {})
        .get("Status", {})
        .get("select", {})
        .get("name", "")
    )
    if final_status != "published":
        raise RuntimeError(f"Unexpected final status: {final_status!r}")
    print(f"{expected_slug} status={final_status}")


def legacy_main():
    if not database_id:
        print("Error: NOTION_DATABASE_ID not set in .env")
        return 1
    database_content = fetch_database_content(database_id)
    articles = extract_fields(database_content)
    write_ids_tsv(articles)
    transform_to_php(articles)
    print(f"Processed {len(articles)} articles")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Publish Notion content through NCMS")
    subparsers = parser.add_subparsers(dest="command")

    publish_parser = subparsers.add_parser(
        "publish",
        help="Render exactly one queued Notion page into an isolated bundle",
    )
    publish_parser.add_argument("--status", default="publish")
    publish_parser.add_argument("--slug")
    publish_parser.add_argument("--allow-empty", action="store_true")
    publish_parser.add_argument("--bundle-dir", required=True)
    publish_parser.add_argument("--metadata-file", required=True)

    mark_parser = subparsers.add_parser(
        "mark-published",
        help="Mark a verified Notion page as published",
    )
    mark_parser.add_argument("--page-id", required=True)
    mark_parser.add_argument("--expected-slug", required=True)
    home_parser = subparsers.add_parser(
        'sync-home', help='Refresh local homepage components and menu JSON from Notion'
    )
    home_parser.add_argument('--status', default='published')
    home_parser.add_argument('--site-project', required=True)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == 'sync-home':
        sync_home(args.status, args.site_project)
        return 0
    if args.command == "publish":
        publish_to_bundle(
            status=args.status,
            slug=args.slug,
            bundle_dir=args.bundle_dir,
            metadata_file=args.metadata_file,
            allow_empty=args.allow_empty,
        )
        return 0
    if args.command == "mark-published":
        mark_published(args.page_id, args.expected_slug)
        return 0
    return legacy_main()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"NCMS error: {error}", file=sys.stderr)
        sys.exit(1)
