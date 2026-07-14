"""Read the dedicated Notion test article and generate an isolated fixture."""
import argparse
import os
import tempfile

import ncms_fetch


TEST_SLUG = 'test/ncms-blocks'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', help='Directory for generated artifacts')
    args = parser.parse_args()

    output_dir = args.output or tempfile.mkdtemp(prefix='ncms-e2e-')
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # This verification must never publish, commit, or change Notion state.
    ncms_fetch.output_dir = output_dir
    ncms_fetch.project_dir = output_dir
    ncms_fetch.git_push_enabled = False
    ncms_fetch.notion_update_enabled = False

    pages = ncms_fetch.fetch_database_content(ncms_fetch.database_id, status='test')
    pages = [
        page for page in pages
        if page.get('properties', {}).get('Id', {}).get('title')
        and page['properties']['Id']['title'][0].get('plain_text') == TEST_SLUG
    ]
    articles = ncms_fetch.extract_fields(pages, included_statuses=('test',))
    if len(articles) != 1:
        raise RuntimeError(f'Expected one {TEST_SLUG!r} article, got {len(articles)}')

    ncms_fetch.transform_to_php(articles)

    php_path = os.path.join(
        output_dir, 'HTML', 'Component', 'test', 'ncms-blocks', 'index.php'
    )
    required_paths = [
        php_path,
        os.path.join(output_dir, 'Config', 'ID.tsv'),
        os.path.join(output_dir, 'Config', 'Url.tsv'),
        os.path.join(output_dir, 'Config', 'Translations.tsv'),
        os.path.join(output_dir, 'build', 'firebase.json'),
        os.path.join(output_dir, 'Site', 'sitemap.xml'),
    ]
    missing = [path for path in required_paths if not os.path.isfile(path)]
    if missing:
        raise RuntimeError(f'Missing generated artifacts: {missing}')

    with open(php_path, encoding='utf-8') as php_file:
        php = php_file.read()

    expected_fragments = [
        '<h3>Heading 1 Test</h3>',
        '<strong>bold</strong>',
        '<ul class="list-bullet content-list">',
        '<ol class="list-bullet content-list">',
        '<blockquote>',
        '&lt;?php echo \'Hello World\'; ?&gt;',
        '<table>',
    ]
    missing_fragments = [fragment for fragment in expected_fragments if fragment not in php]
    if missing_fragments:
        raise RuntimeError(f'Missing expected output fragments: {missing_fragments}')

    raw_php_fragments = [
        "<?php group_image('paths', 3, 'svg') ?>",
        "<?php require('../HTML/Fragment/Component_FB_comments.php') ?>",
    ]
    if not any(fragment in php for fragment in raw_php_fragments):
        raise RuntimeError('Missing the intentional raw-PHP callout fixture')

    print(f'E2E verification passed: {php_path}')
    print(f'E2E output directory: {output_dir}')


if __name__ == '__main__':
    main()
