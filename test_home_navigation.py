"""Homepage contract: Notion policy blocks produce config, not executable body."""

import json
import unittest
from unittest.mock import patch

from ncms_fetch import (
    compose_php_page,
    extract_home_navigation,
    localize_xurl_links,
    render_page_blocks,
)


class HomeNavigationTests(unittest.TestCase):
    def setUp(self):
        self.home = {
            'branch': 'world',
            'syntheticChildren': {'world': ['philosophy', 'science']},
            'leafSlugs': [],
        }
        self.side = {
            'groups': [{'kind': 'image', 'items': ['root', 'world'],
                        'includeHomeHubs': True}],
            'labels': {'root': {'en': 'home', 'hi': 'मुखपृष्ठ'}},
        }
        self.blocks = [
            self.callout('home', '🏠'), self.callout('side', '🧭'),
        ]

    @staticmethod
    def callout(block_id, emoji):
        return {'id': block_id, 'type': 'callout', 'has_children': True,
                'callout': {'icon': {'type': 'emoji', 'emoji': emoji},
                            'rich_text': [{'plain_text': block_id}]}}

    def children(self, block_id):
        policy = self.home if block_id == 'home' else self.side
        return [{'type': 'code', 'code': {'rich_text': [
            {'plain_text': json.dumps(policy)}
        ]}}]

    def test_policies_are_parsed_and_not_rendered_as_body(self):
        with patch('ncms_fetch.fetch_page_blocks', side_effect=self.children):
            result = extract_home_navigation(self.blocks)
        self.assertEqual(result['home']['syntheticChildren']['world'],
                         ['philosophy', 'science'])
        self.assertTrue(result['side']['groups'][0]['includeHomeHubs'])
        self.assertEqual(render_page_blocks(self.blocks), '')

    def test_invalid_policy_fails_before_generation(self):
        self.home['selectedChildren'] = {'science': ['unrelated/article']}
        with patch('ncms_fetch.fetch_page_blocks', side_effect=self.children):
            with self.assertRaisesRegex(ValueError, 'direct children'):
                extract_home_navigation(self.blocks)

    def test_home_shell_keeps_notion_body(self):
        php = compose_php_page({
            'slug': 'root', 'layout': {'name': 'home'},
            'content': '<p>From Notion</p>',
        })
        self.assertIn('<p>From Notion</p>', php)
        self.assertIn('home_menu_render_branch(home_menu_branch_slug())', php)
        self.assertNotIn('Homepage tree policy', php)

    def test_translated_xurl_keeps_canonical_target(self):
        source = '<a class="content-link XURL" href="/about_me" data-target="about_me">Name</a>'
        result = localize_xurl_links(source, 'hi')
        self.assertIn('href="/hi/about_me"', result)
        self.assertIn('data-target="about_me"', result)


if __name__ == '__main__':
    unittest.main()
