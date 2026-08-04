import unittest
from unittest.mock import patch

import ncms_fetch


class NestedTranslationTests(unittest.TestCase):
    def make_base(self):
        return {
            "id": "base-page",
            "status": "publish",
            "slug": "world/example",
            "language": "en",
            "translation_group": "world/example",
            "label": "Example",
            "title": "Example",
            "js": "0",
            "description": "English description",
            "type": "article",
            "content": "<p>English</p>",
        }

    def test_extracts_nested_translation_and_hides_metadata_callout(self):
        parent_blocks = [
            {
                "id": "translation-hi",
                "type": "child_page",
                "child_page": {"title": "हिन्दी (hi)"},
            }
        ]
        child_blocks = [
            {
                "id": "metadata",
                "type": "callout",
                "callout": {
                    "icon": {"type": "emoji", "emoji": "🌐"},
                    "rich_text": [{
                        "plain_text": (
                            "Language: hi\nLabel: उदाहरण\nTitle: उदाहरण\n"
                            "Description: हिन्दी विवरण"
                        )
                    }],
                },
            },
            {
                "id": "heading",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"plain_text": "उदाहरण क्या है?", "annotations": {}}]},
            },
        ]
        with patch.object(ncms_fetch, "fetch_page_blocks", return_value=child_blocks):
            translations = ncms_fetch.extract_nested_translations(
                parent_blocks, self.make_base()
            )

        self.assertEqual(1, len(translations))
        translation = translations[0]
        self.assertEqual("hi", translation["language"])
        self.assertEqual("उदाहरण", translation["title"])
        self.assertEqual("world/example", translation["translation_group"])
        self.assertIn("उदाहरण क्या है?", translation["content"])
        self.assertNotIn("Language: hi", translation["content"])

    def test_ignores_non_language_child_pages(self):
        blocks = [{
            "id": "notes",
            "type": "child_page",
            "child_page": {"title": "Research notes"},
        }]
        self.assertEqual([], ncms_fetch.extract_nested_translations(blocks, self.make_base()))

    def test_rejects_language_mismatch(self):
        blocks = [{
            "id": "metadata",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "🌐"},
                "rich_text": [{"plain_text": "Language: en\nLabel: X\nTitle: X\nDescription: X"}],
            },
        }]
        with self.assertRaisesRegex(RuntimeError, "language mismatch"):
            ncms_fetch.parse_translation_metadata(blocks, "hi")


if __name__ == "__main__":
    unittest.main()