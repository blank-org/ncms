import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

import ncms_fetch


def make_page(slug, status="publish", page_id="page-1"):
    return {
        "id": page_id,
        "properties": {
            "Id": {"title": [{"plain_text": slug}]},
            "Status": {"select": {"name": status}},
        },
    }


class PublishSelectionTests(unittest.TestCase):
    def test_requires_exactly_one_page_without_slug(self):
        pages = [make_page("one"), make_page("two", page_id="page-2")]
        with self.assertRaisesRegex(RuntimeError, "Expected exactly one"):
            ncms_fetch.select_publish_page(pages)

    def test_selects_requested_slug(self):
        pages = [make_page("one"), make_page("two", page_id="page-2")]
        selected, candidates = ncms_fetch.select_publish_page(pages, "two")
        self.assertEqual("page-2", selected["id"])
        self.assertEqual(["one", "two"], [item["slug"] for item in candidates])

    def test_rejects_unsafe_slug(self):
        for slug in ("../secret", "/absolute", "trailing/", r"back\slash"):
            with self.subTest(slug=slug):
                with self.assertRaises(ValueError):
                    ncms_fetch.validate_slug(slug)


class PublishBundleTests(unittest.TestCase):
    def test_writes_metadata_and_disables_side_effects(self):
        article = {
            "id": "page-1",
            "slug": "world/example",
            "title": "Example",
            "description": "Description",
            "language": "en",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_path = os.path.join(temp_dir, "metadata.json")

            def fake_transform(articles):
                component = os.path.join(
                    temp_dir, "HTML", "Component", "world", "example", "index.php"
                )
                os.makedirs(os.path.dirname(component), exist_ok=True)
                with open(component, "w", encoding="utf-8") as target:
                    target.write("<p>Example</p>")

            with (
                patch.object(ncms_fetch, "database_id", "database"),
                patch.object(
                    ncms_fetch,
                    "fetch_database_content",
                    return_value=[make_page("world/example")],
                ),
                patch.object(ncms_fetch, "extract_fields", return_value=[article]),
                patch.object(ncms_fetch, "transform_to_php", side_effect=fake_transform),
            ):
                result = ncms_fetch.publish_to_bundle(
                    "publish", None, temp_dir, metadata_path
                )

            with open(metadata_path, encoding="utf-8") as source:
                metadata = json.load(source)
            self.assertEqual("world/example", result["slug"])
            self.assertEqual(result, metadata)
            self.assertFalse(ncms_fetch.git_push_enabled)
            self.assertFalse(ncms_fetch.notion_update_enabled)

    def test_empty_scheduled_queue_is_a_no_op(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_path = os.path.join(temp_dir, "metadata.json")
            with (
                patch.object(ncms_fetch, "database_id", "database"),
                patch.object(
                    ncms_fetch,
                    "fetch_database_content",
                    return_value=[],
                ),
            ):
                result = ncms_fetch.publish_to_bundle(
                    "publish", None, temp_dir, metadata_path, allow_empty=True
                )

            self.assertTrue(result["no_work"])
            with open(metadata_path, encoding="utf-8") as source:
                self.assertEqual(result, json.load(source))


class MarkPublishedTests(unittest.TestCase):
    def test_marks_only_expected_publish_page(self):
        publish_page = make_page("world/example")
        published_page = make_page("world/example", status="published")
        pages = Mock()
        pages.retrieve.side_effect = [publish_page, published_page]

        with patch.object(ncms_fetch.notion, "pages", pages):
            ncms_fetch.mark_published("page-1", "world/example")

        pages.update.assert_called_once_with(
            page_id="page-1",
            properties={"Status": {"select": {"name": "published"}}},
        )

    def test_refuses_unexpected_status(self):
        draft_page = make_page("world/example", status="draft")
        pages = Mock()
        pages.retrieve.return_value = draft_page

        with patch.object(ncms_fetch.notion, "pages", pages):
            with self.assertRaisesRegex(RuntimeError, "unexpected status"):
                ncms_fetch.mark_published("page-1", "world/example")
        pages.update.assert_not_called()


if __name__ == "__main__":
    unittest.main()
