"""Create or refresh a Notion test page from an existing Ujnotes article."""
import sys

from ncms_upload import (
    build_file_map,
    clear_page_content,
    database_id,
    notion,
    parse_file_to_blocks,
    upload_blocks,
)


DEFAULT_SOURCE_SLUG = 'world/philosophy/life'
DEFAULT_TEST_SLUG = 'test/parity-life'


def find_page(slug):
    response = notion.databases.query(
        database_id=database_id,
        filter={'property': 'Id', 'title': {'equals': slug}},
    )
    results = response.get('results', [])
    return results[0] if results else None


def plain_property(properties, name, kind, default=''):
    values = properties.get(name, {}).get(kind, [])
    return values[0].get('plain_text', default) if values else default


def rich_text(content):
    return [{'type': 'text', 'text': {'content': content}}]


def build_test_properties(source_page, source_slug, test_slug):
    source = source_page['properties']
    label = plain_property(source, 'Label', 'rich_text', source_slug.rsplit('/', 1)[-1].title())
    title = plain_property(source, 'Title', 'rich_text', label)
    description = plain_property(source, 'Description', 'rich_text', '')
    js = source.get('JS', {}).get('select') or {'name': '0'}

    properties = {
        'Id': {'title': rich_text(test_slug)},
        'Status': {'select': {'name': 'test'}},
        'Label': {'rich_text': rich_text(f'Parity: {label}')},
        'Title': {'rich_text': rich_text(f'{title} — Parity Test')},
        'JS': {'select': {'name': js.get('name', '0')}},
        'Description': {
            'rich_text': rich_text(f'Parity clone of {source_slug}. {description}'.strip())
        },
    }

    language = source.get('Language', {}).get('select')
    if language:
        properties['Language'] = {'select': {'name': language['name']}}
    if 'TranslationGroup' in source:
        properties['TranslationGroup'] = {'rich_text': rich_text(test_slug)}

    return properties


def main():
    source_slug = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SOURCE_SLUG
    test_slug = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TEST_SLUG

    source_page = find_page(source_slug)
    if not source_page:
        raise RuntimeError(f'Notion source page not found: {source_slug}')

    file_path = build_file_map().get(source_slug)
    if not file_path:
        raise RuntimeError(f'Website source file not found: {source_slug}')

    blocks = parse_file_to_blocks(file_path)
    properties = build_test_properties(source_page, source_slug, test_slug)
    test_page = find_page(test_slug)

    if test_page:
        notion.pages.update(page_id=test_page['id'], properties=properties)
        clear_page_content(test_page['id'])
        action = 'Refreshed'
    else:
        test_page = notion.pages.create(
            parent={'database_id': database_id},
            properties=properties,
        )
        action = 'Created'

    upload_blocks(test_page['id'], blocks)
    print(f'{action} parity page: {test_slug}')
    print(f'Source: {source_slug}')
    print(f'Blocks: {len(blocks)}')
    print(f'Page ID: {test_page["id"]}')


if __name__ == '__main__':
    main()
