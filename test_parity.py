"""Verify a Notion test clone against its website article source."""
import re
import sys

from bs4 import BeautifulSoup

import ncms_fetch
from ncms_upload import build_file_map, database_id, notion, parse_file_to_blocks


DEFAULT_SOURCE_SLUG = 'world/philosophy/life'
DEFAULT_TEST_SLUG = 'test/parity-life'
RICH_TEXT_BLOCKS = {
    'paragraph', 'heading_1', 'heading_2', 'heading_3', 'bulleted_list_item',
    'numbered_list_item', 'quote', 'code', 'callout',
}


def find_page(slug):
    response = notion.databases.query(
        database_id=database_id,
        filter={'property': 'Id', 'title': {'equals': slug}},
    )
    results = response.get('results', [])
    return results[0] if results else None


def expected_rich_text(items):
    return [
        {
            'text': item['text']['content'],
            'annotations': item.get('annotations', {}),
            'href': (item['text'].get('link') or {}).get('url'),
        }
        for item in items
    ]


def actual_rich_text(items):
    return [
        {
            'text': item.get('plain_text', ''),
            'annotations': {
                key: True for key in ('bold', 'italic', 'code', 'strikethrough', 'underline')
                if item.get('annotations', {}).get(key)
            },
            'href': item.get('href'),
        }
        for item in items
    ]


def canonical_expected(block):
    block_type = block['type']
    result = {'type': block_type}
    if block_type in RICH_TEXT_BLOCKS:
        result['rich_text'] = expected_rich_text(block[block_type].get('rich_text', []))
    if block_type == 'callout':
        result['emoji'] = block['callout'].get('icon', {}).get('emoji')
    if block_type == 'code':
        result['language'] = block['code'].get('language')
    return result


def canonical_actual(block):
    block_type = block['type']
    result = {'type': block_type}
    if block_type in RICH_TEXT_BLOCKS:
        result['rich_text'] = actual_rich_text(block[block_type].get('rich_text', []))
    if block_type == 'callout':
        result['emoji'] = block['callout'].get('icon', {}).get('emoji')
    if block_type == 'code':
        result['language'] = block['code'].get('language')
    return result


def visible_text(content):
    without_php = re.sub(r'<\?php.*?\?>', ' ', content, flags=re.DOTALL)
    soup = BeautifulSoup(without_php, 'html.parser')
    return ' '.join(soup.get_text(' ', strip=True).split())


def main():
    source_slug = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SOURCE_SLUG
    test_slug = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TEST_SLUG

    file_path = build_file_map().get(source_slug)
    if not file_path:
        raise RuntimeError(f'Website source file not found: {source_slug}')

    test_page = find_page(test_slug)
    if not test_page:
        raise RuntimeError(f'Notion parity page not found: {test_slug}')
    status = test_page['properties'].get('Status', {}).get('select', {}).get('name')
    if status != 'test':
        raise RuntimeError(f'Parity page must remain in test status, got: {status}')

    expected_blocks = parse_file_to_blocks(file_path)
    actual_blocks = notion.blocks.children.list(block_id=test_page['id'])['results']
    expected = [canonical_expected(block) for block in expected_blocks]
    actual = [canonical_actual(block) for block in actual_blocks]
    if actual != expected:
        raise AssertionError(f'Notion block mismatch\nExpected: {expected}\nActual: {actual}')

    with open(file_path, encoding='utf-8') as source_file:
        source_soup = BeautifulSoup(source_file.read(), 'html.parser')
    source_message = source_soup.select_one('#message')
    generated = ncms_fetch.fetch_page_content(test_page['id'])
    if visible_text(str(source_message)) != visible_text(generated):
        raise AssertionError(
            'Visible text mismatch\n'
            f'Source: {visible_text(str(source_message))}\n'
            f'Generated: {visible_text(generated)}'
        )

    print(f'Parity verified: {source_slug} -> {test_slug}')
    print(f'Blocks: {len(actual)}')
    print('Status: test')


if __name__ == '__main__':
    main()
