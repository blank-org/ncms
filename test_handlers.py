"""
Unit tests for all block handlers and rich text rendering.
Simulates Notion API responses locally — no API calls needed.
"""
import sys
import unittest
sys.stdout.reconfigure(encoding='utf-8')

from ncms_fetch import render_rich_text, wrap_lists
from ncms_fetch import (
    handle_paragraph, handle_heading_1, handle_heading_2, handle_heading_3,
    handle_bulleted_list_item, handle_numbered_list_item,
    handle_quote, handle_code, handle_divider,
    handle_callout, handle_cover_image, handle_content_image,
    handle_link_xurl, handle_raw_php,
    extract_fields, update_id_tsv, update_translations_tsv, update_sitemap_xml,
)

passed = 0
failed = 0

def check(name, actual, expected_substr):
    global passed, failed
    if expected_substr in actual:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")
        print(f"    Expected substring: {expected_substr!r}")
        print(f"    Got: {actual!r}")

def rt(text, bold=False, italic=False, code=False, strikethrough=False, underline=False, link=None):
    """Helper to build a Notion rich_text segment."""
    seg = {
        "type": "text",
        "text": {"content": text},
        "plain_text": text,
        "annotations": {
            "bold": bold, "italic": italic, "code": code,
            "strikethrough": strikethrough, "underline": underline,
            "color": "default"
        },
        "href": link
    }
    if link:
        seg["text"]["link"] = {"url": link}
        seg["href"] = link
    return seg


print("=== Rich Text Rendering ===")

result = render_rich_text([rt("Hello world")])
check("Plain text", result, "Hello world")

result = render_rich_text([rt("<script>alert('x')</script> & safe")])
check("HTML text escaped", result, "&lt;script&gt;alert('x')&lt;/script&gt; &amp; safe")

result = render_rich_text([rt("bold text", bold=True)])
check("Bold", result, "<strong>bold text</strong>")

result = render_rich_text([rt("italic text", italic=True)])
check("Italic", result, "<em>italic text</em>")

result = render_rich_text([rt("code text", code=True)])
check("Code", result, "<code class='inline'>code text</code>")

result = render_rich_text([rt("struck", strikethrough=True)])
check("Strikethrough", result, "<s>struck</s>")

result = render_rich_text([rt("underlined", underline=True)])
check("Underline", result, "<u>underlined</u>")

result = render_rich_text([rt("bold italic", bold=True, italic=True)])
check("Bold+Italic", result, "<em><strong>bold italic</strong></em>")

result = render_rich_text([rt("Life", link="https://ujnotes.com/world/philosophy/life")])
check("Internal XURL link", result, 'class="content-link XURL"')
check("Internal link href", result, 'href="/world/philosophy/life"')
check("Internal link data-target", result, 'data-target="world/philosophy/life"')

result = render_rich_text([rt('Quoted "title"', link='https://ujnotes.com/search?q="test"&safe=1')])
check("Internal link attributes escaped", result, 'q=&quot;test&quot;&amp;safe=1')

result = render_rich_text([rt("Spoof", link="https://ujnotes.com.evil.example/path")])
check("Lookalike domain remains external", result, 'target="_blank"')

result = render_rich_text([rt("YouTube", link="https://www.youtube.com/watch?v=test")])
check("External link", result, 'class="content-link"')
check("External link target", result, 'target="_blank"')

result = render_rich_text([rt("about", link="/about")])
check("Relative internal link", result, 'class="content-link XURL"')

result = render_rich_text([
    rt("Normal "), rt("bold", bold=True), rt(" end")
])
check("Mixed segments", result, "Normal <strong>bold</strong> end")


print("\n=== Block Handlers ===")

# Paragraph
block = {"paragraph": {"rich_text": [rt("Test paragraph")]}}
btype, html = handle_paragraph(block, None)
check("Paragraph type", btype, "paragraph")
check("Paragraph html", html, "<p class='first-letter-high'>")
check("Paragraph content", html, "Test paragraph")

# Empty paragraph
block = {"paragraph": {"rich_text": []}}
btype, html = handle_paragraph(block, None)
check("Empty paragraph", html, "")

# Heading 1
block = {"heading_1": {"rich_text": [rt("H1 Title")]}}
btype, html = handle_heading_1(block, None)
check("Heading 1", html, "<h3>H1 Title</h3>")

# Heading 2
block = {"heading_2": {"rich_text": [rt("H2 Title")]}}
btype, html = handle_heading_2(block, None)
check("Heading 2", html, "<h2>H2 Title</h2>")

# Heading 3
block = {"heading_3": {"rich_text": [rt("H3 Title")]}}
btype, html = handle_heading_3(block, None)
check("Heading 3", html, "<h4>H3 Title</h4>")

# Bulleted list
block = {"bulleted_list_item": {"rich_text": [rt("Bullet item")]}}
btype, html = handle_bulleted_list_item(block, None)
check("Bulleted list type", btype, "bulleted_list_item")
check("Bulleted list html", html, "<li><div>Bullet item</div></li>")

# Numbered list
block = {"numbered_list_item": {"rich_text": [rt("Num item")]}}
btype, html = handle_numbered_list_item(block, None)
check("Numbered list type", btype, "numbered_list_item")
check("Numbered list html", html, "<li><div>Num item</div></li>")

# Quote
block = {"quote": {"rich_text": [rt("A wise quote"), rt(" - Author", italic=True)]}}
btype, html = handle_quote(block, None)
check("Quote type", btype, "quote")
check("Quote blockquote", html, "<blockquote>")
check("Quote content", html, "A wise quote")
check("Quote italic", html, "<em> - Author</em>")

# Code
block = {"code": {"rich_text": [rt("echo 'hello';")], "language": "php"}}
btype, html = handle_code(block, None)
check("Code type", btype, "code")
check("Code pre tag", html, "<pre class='indent-c'>")
check("Code content", html, "echo 'hello';")

block = {"code": {"rich_text": [rt("<?php echo '<b>unsafe</b>'; ?>")], "language": "php"}}
btype, html = handle_code(block, None)
check("Code PHP opening tag escaped", html, "&lt;?php")
check("Code HTML escaped", html, "&lt;b&gt;unsafe&lt;/b&gt;")
check("Code PHP opening tag absent", str("<?php" not in html), "True")

# Divider
block = {"divider": {}}
btype, html = handle_divider(block, None)
check("Divider", html, "content-body-separator")


print("\n=== Callout Handlers ===")

# Cover image 🖼️
block = {"callout": {
    "icon": {"type": "emoji", "emoji": "\U0001f5bc\ufe0f"},
    "rich_text": [rt("A mountain landscape")]
}}
btype, html = handle_callout(block, None)
check("Cover image alt", html, "$alt='A mountain landscape'")
check("Cover image require", html, "Component_cover.php")
check("Cover image desc", html, "$desc")

block = {"callout": {
    "icon": {"type": "emoji", "emoji": "\U0001f5bc\ufe0f"},
    "rich_text": [rt("Traveler's \\ path")]
}}
btype, html = handle_callout(block, None)
check("Cover image PHP quote escaped", html, "Traveler\\'s")
check("Cover image PHP slash escaped", html, "\\\\ path")

# Content image 🏞️
block = {"callout": {
    "icon": {"type": "emoji", "emoji": "\U0001f3de\ufe0f"},
    "rich_text": [rt("paths|svg||true")]
}}
btype, html = handle_callout(block, None)
check("Content image img_title", html, "$img_title='paths'")
check("Content image ext", html, "$ext='svg'")
check("Content image center", html, "$center='true'")
check("Content image require", html, "Component_image.php")

# Link xurl 🔗
block = {"callout": {
    "icon": {"type": "emoji", "emoji": "\U0001f517"},
    "rich_text": [rt("world/philosophy/life|Life\nworld/philosophy/death|Death")]
}}
btype, html = handle_callout(block, None)
check("Link xurl Life", html, "link_xurl('world/philosophy/life', 'Life')")
check("Link xurl Death", html, "link_xurl('world/philosophy/death', 'Death')")

block = {"callout": {
    "icon": {"type": "emoji", "emoji": "\U0001f517"},
    "rich_text": [rt("author's/path|Author's page")]
}}
btype, html = handle_callout(block, None)
check("Link xurl path escaped", html, "author\\'s/path")
check("Link xurl label escaped", html, "Author\\'s page")

# Raw PHP 🔧
block = {"callout": {
    "icon": {"type": "emoji", "emoji": "\U0001f527"},
    "rich_text": [rt("<?php group_image('paths', 3, 'svg') ?>")]
}}
btype, html = handle_callout(block, None)
check("Raw PHP", html, "<?php group_image('paths', 3, 'svg') ?>")

# Unknown callout (default to paragraph)
block = {"callout": {
    "icon": {"type": "emoji", "emoji": "\u2764\ufe0f"},
    "rich_text": [rt("Some callout text")]
}}
btype, html = handle_callout(block, None)
check("Unknown callout as paragraph", html, "<p class='first-letter-high'>")


print("\n=== List Wrapping ===")

tuples = [
    ('bulleted_list_item', '\t\t<li><div>A</div></li>\n'),
    ('bulleted_list_item', '\t\t<li><div>B</div></li>\n'),
    ('paragraph', '\t<p>Break</p>\n'),
    ('numbered_list_item', '\t\t<li><div>1</div></li>\n'),
    ('numbered_list_item', '\t\t<li><div>2</div></li>\n'),
]
result = wrap_lists(tuples)
check("UL opening", result, '<ul class="list-bullet content-list">')
check("UL closing", result, '</ul>')
check("OL opening", result, '<ol class="list-bullet content-list">')
check("OL closing", result, '</ol>')
check("Paragraph between lists", result, "<p>Break</p>")

# Single list type
tuples2 = [
    ('bulleted_list_item', '\t\t<li><div>X</div></li>\n'),
]
result2 = wrap_lists(tuples2)
check("Single bullet wrapped", result2, '<ul class="list-bullet content-list">')
check("Single bullet closed", result2, '</ul>')

# No lists
tuples3 = [
    ('paragraph', '\t<p>Hello</p>\n'),
]
result3 = wrap_lists(tuples3)
check("No lists, no wrapping", result3, '<p>Hello</p>')


print("\n=== Language-Aware Config Generation ===")

import os, tempfile, shutil

# Helper to build mock articles with language fields
def make_article(slug, language='en', status='published', label='', title='', js='0', desc=''):
    return {
        'id': 'fake-id',
        'status': status,
        'slug': slug,
        'language': language,
        'translation_group': slug,
        'label': label or slug.split('/')[-1].capitalize(),
        'title': title or slug.split('/')[-1].capitalize(),
        'js': js,
        'description': desc or f'About {slug}',
        'content': '<p>Test</p>',
    }

# Test per-language ID.tsv generation
tmpdir = tempfile.mkdtemp()
try:
    articles = [
        make_article('world/philosophy/life', 'en'),
        make_article('world/philosophy/life', 'hi', label='जीवन', title='जीवन'),
        make_article('about', 'en'),
    ]
    update_id_tsv(articles, tmpdir)

    # Check English ID.tsv
    en_path = os.path.join(tmpdir, 'Config/ID.tsv')
    check("EN ID.tsv exists", str(os.path.exists(en_path)), "True")
    with open(en_path, 'r', encoding='utf-8') as f:
        en_content = f.read()
    check("EN ID.tsv has life", en_content, "world/philosophy/life")
    check("EN ID.tsv has about", en_content, "about")
    # English file should NOT have Hindi entries
    check("EN ID.tsv no Hindi label", str('जीवन' not in en_content), "True")

    # Check Hindi ID.tsv
    hi_path = os.path.join(tmpdir, 'Config/ID_hi.tsv')
    check("HI ID.tsv exists", str(os.path.exists(hi_path)), "True")
    with open(hi_path, 'r', encoding='utf-8') as f:
        hi_content = f.read()
    check("HI ID.tsv has Hindi label", hi_content, "जीवन")
    check("HI ID.tsv has slug", hi_content, "world/philosophy/life")

    # Check Translations.tsv
    trans_path = os.path.join(tmpdir, 'Config/Translations.tsv')
    check("Translations.tsv exists", str(os.path.exists(trans_path)), "True")
    with open(trans_path, 'r', encoding='utf-8') as f:
        trans_content = f.read()
    check("Translations header has en", trans_content, "en")
    check("Translations header has hi", trans_content, "hi")
    check("Translations has life group", trans_content, "world/philosophy/life")
finally:
    shutil.rmtree(tmpdir)

# Test sitemap hreflang generation
tmpdir2 = tempfile.mkdtemp()
try:
    articles = [
        make_article('world/philosophy/life', 'en'),
        make_article('world/philosophy/life', 'hi'),
        make_article('about', 'en'),
    ]
    update_sitemap_xml(articles, tmpdir2)
    sitemap_path = os.path.join(tmpdir2, 'Site/sitemap.xml')
    check("Sitemap exists", str(os.path.exists(sitemap_path)), "True")
    with open(sitemap_path, 'r', encoding='utf-8') as f:
        sitemap = f.read()
    check("Sitemap has xhtml namespace", sitemap, "xmlns:xhtml")
    check("Sitemap has en hreflang", sitemap, 'hreflang="en"')
    check("Sitemap has hi hreflang", sitemap, 'hreflang="hi"')
    check("Sitemap has x-default", sitemap, 'hreflang="x-default"')
    check("Sitemap has hi prefix URL", sitemap, "ujnotes.com/hi/world/philosophy/life")
    check("Sitemap has en URL (no prefix)", sitemap, "ujnotes.com/world/philosophy/life")
    # about has no translation, should not have hreflang alternates
    check("Sitemap about no hreflang", str('hreflang' in sitemap.split('about')[1].split('</url>')[0] if 'about' in sitemap else "False"), "False")
finally:
    shutil.rmtree(tmpdir2)

# Test extract_fields with language property
print("\n=== extract_fields Language Support ===")

# Mock a Notion page response with Language property
mock_page_en = {
    'id': 'page-en-123',
    'properties': {
        'Id': {'title': [{'plain_text': 'test/article'}]},
        'Status': {'select': {'name': 'publish'}},
        'Label': {'rich_text': [{'plain_text': 'Article'}]},
        'Title': {'rich_text': [{'plain_text': 'Test Article'}]},
        'JS': {'select': {'name': '0'}},
        'Description': {'rich_text': [{'plain_text': 'A test'}]},
        'Language': {'select': {'name': 'en'}},
        'TranslationGroup': {'rich_text': [{'plain_text': 'test/article'}]},
    }
}
mock_page_hi = {
    'id': 'page-hi-456',
    'properties': {
        'Id': {'title': [{'plain_text': 'test/article'}]},
        'Status': {'select': {'name': 'publish'}},
        'Label': {'rich_text': [{'plain_text': 'लेख'}]},
        'Title': {'rich_text': [{'plain_text': 'परीक्षण लेख'}]},
        'JS': {'select': {'name': '0'}},
        'Description': {'rich_text': [{'plain_text': 'एक परीक्षण'}]},
        'Language': {'select': {'name': 'hi'}},
        'TranslationGroup': {'rich_text': [{'plain_text': 'test/article'}]},
    }
}
# No Language property (defaults to 'en')
mock_page_no_lang = {
    'id': 'page-nolang-789',
    'properties': {
        'Id': {'title': [{'plain_text': 'legacy/article'}]},
        'Status': {'select': {'name': 'publish'}},
        'Label': {'rich_text': [{'plain_text': 'Legacy'}]},
        'Title': {'rich_text': [{'plain_text': 'Legacy Article'}]},
        'JS': {'select': {'name': '0'}},
        'Description': {'rich_text': [{'plain_text': 'Old article'}]},
    }
}

# Monkey-patch fetch_page_content to avoid API calls
import ncms_fetch
original_fpc = ncms_fetch.fetch_page_content
ncms_fetch.fetch_page_content = lambda page_id: '<p>Mock content</p>'

try:
    articles = extract_fields([mock_page_en, mock_page_hi, mock_page_no_lang])
    check("Extract 3 articles", str(len(articles)), "3")

    en_article = [a for a in articles if a.get('language') == 'en' and a['slug'] == 'test/article']
    check("EN article found", str(len(en_article)), "1")
    check("EN article language", en_article[0]['language'], "en")
    check("EN article translation_group", en_article[0]['translation_group'], "test/article")

    hi_article = [a for a in articles if a.get('language') == 'hi']
    check("HI article found", str(len(hi_article)), "1")
    check("HI article language", hi_article[0]['language'], "hi")

    no_lang_article = [a for a in articles if a['slug'] == 'legacy/article']
    check("No-lang defaults to en", no_lang_article[0]['language'], "en")

    mock_page_test = dict(mock_page_en)
    mock_page_test['id'] = 'page-test-status'
    mock_page_test['properties'] = dict(mock_page_en['properties'])
    mock_page_test['properties']['Status'] = {'select': {'name': 'test'}}
    test_articles = extract_fields([mock_page_test], included_statuses=('test',))
    check("Explicit test status included", str(len(test_articles)), "1")
    check("Explicit test status retained", test_articles[0]['status'], "test")
finally:
    ncms_fetch.fetch_page_content = original_fpc


print(f"\n=== Results: {passed} passed, {failed} failed ===")


class TestLegacyHandlerChecks(unittest.TestCase):
    """Expose the existing detailed checks to unittest discovery."""

    def test_all_handler_checks_pass(self):
        self.assertEqual(failed, 0, f"{failed} of {passed + failed} handler checks failed")


if __name__ == '__main__':
    unittest.main()
