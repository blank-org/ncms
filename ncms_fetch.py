import json
import os
from html import escape
from notion_client import Client
from dotenv import load_dotenv
import subprocess
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

# Load environment variables
load_dotenv()
notion = Client(auth=os.getenv('NOTION_API_KEY'))
database_id = os.getenv('NOTION_DATABASE_ID')
output_dir = os.getenv('OUTPUT_DIR')
project_dir = os.getenv('PROJECT_DIR')
git_push_enabled = os.getenv('GIT_PUSH', 'false').lower() == 'true'
notion_update_enabled = os.getenv('NOTION_UPDATE', 'false').lower() == 'true'

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
                safe_path = escape(path, quote=True)
                safe_target = escape(clean_path, quote=True)
                safe_display = escape(plain_text, quote=True)
                text = f'<a class="content-link XURL" href="{safe_path}" data-target="{safe_target}" data-title="{safe_display}">{text}</a>'
            else:
                safe_href = escape(href, quote=True)
                text = f'<a class="content-link" href="{safe_href}" target="_blank" rel="noopener noreferrer">{text}</a>'

        html_parts.append(text)

    return ''.join(html_parts)


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
    text = render_rich_text(rich_text)
    return ('bulleted_list_item', f"\t\t<li><div>{text}</div></li>\n")

def handle_numbered_list_item(block, notion_client):
    rich_text = block['numbered_list_item'].get('rich_text', [])
    text = render_rich_text(rich_text)
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

def handle_callout(block, notion_client):
    icon = block['callout'].get('icon', {})
    emoji = icon.get('emoji', '') if icon.get('type') == 'emoji' else ''
    rich_text = block['callout'].get('rich_text', [])
    handler = CALLOUT_HANDLERS.get(emoji)
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
def fetch_page_content(page_id):
    block_tuples = []
    has_more = True
    start_cursor = None
    while has_more:
        kwargs = {'block_id': page_id}
        if start_cursor:
            kwargs['start_cursor'] = start_cursor
        response = notion.blocks.children.list(**kwargs)
        for block in response['results']:
            block_type = block['type']
            handler = BLOCK_HANDLERS.get(block_type)
            if handler:
                result = handler(block, notion)
                if result[1]:
                    block_tuples.append(result)
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor')
    return wrap_lists(block_tuples)

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
            "content": fetch_page_content(page["id"])
        }
        if "Flags" in properties:
            article["flags"] = get_flags()
        articles.append(article)
        print(f"Extracted article: Id={article['slug']}, Title={article['title']}")
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
        suffix = '' if lang == 'en' else f'_{lang}'
        url_tsv_path = os.path.join(output_base, f'Config/Url{suffix}.tsv')
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

        js_include = "<?php require('../JS/Base/page.js'); ?>" if article['js'] == "1" else ""
        php_code_lines = [
            "<div id='message'>",
            f"\t{article['content']}",
            "</div>",
            js_include,
            "<?php require('../HTML/Fragment/Component_bottom.php') ?>"
        ]
        php_code = '\n'.join(php_code_lines)

        print(f"Writing to: {full_file_path}")
        try:
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(php_code)
        except Exception as e:
            print(f"Error writing to {full_file_path}: {e}")

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

def main():
    if not database_id:
        print("Error: NOTION_DATABASE_ID not set in .env")
        return
    database_content = fetch_database_content(database_id)
    articles = extract_fields(database_content)
    write_ids_tsv(articles)
    transform_to_php(articles)
    print(f"Processed {len(articles)} articles")

if __name__ == "__main__":
    main()
