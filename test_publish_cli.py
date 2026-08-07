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
        selected, candidates, language = ncms_fetch.select_publish_page(pages, "two")
        self.assertEqual("page-2", selected["id"])
        self.assertEqual(["one", "two"], [item["slug"] for item in candidates])
        self.assertIsNone(language)

    def test_selects_language_prefixed_public_slug(self):
        pages = [
            make_page("world/philosophy/hindu"),
            make_page("world/philosophy/life", page_id="page-2"),
        ]
        selected, _, language = ncms_fetch.select_publish_page(
            pages, "hi/world/philosophy/hindu"
        )
        self.assertEqual("page-1", selected["id"])
        self.assertEqual("hi", language)

    def test_prefers_exact_slug_over_language_prefix(self):
        pages = [make_page("hi/world/example", page_id="exact")]
        selected, _, language = ncms_fetch.select_publish_page(
            pages, "hi/world/example"
        )
        self.assertEqual("exact", selected["id"])
        self.assertIsNone(language)

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
            self.assertEqual(["en"], [item["language"] for item in metadata["variants"]])
            self.assertFalse(ncms_fetch.git_push_enabled)
            self.assertFalse(ncms_fetch.notion_update_enabled)

    def test_bundle_contains_base_and_nested_translation_variants(self):
        base = {
            "id": "page-1",
            "status": "publish",
            "slug": "world/example",
            "title": "Example",
            "description": "Description",
            "language": "en",
        }
        hindi = {
            "id": "child-hi",
            "status": "publish",
            "slug": "world/example",
            "title": "हिंदी उदाहरण",
            "description": "हिंदी विवरण",
            "language": "hi",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_path = os.path.join(temp_dir, "metadata.json")

            def fake_transform(articles):
                for article in articles:
                    parts = [temp_dir, "HTML", "Component"]
                    if article["language"] != "en":
                        parts.append(article["language"])
                    parts.extend(["world", "example", "index.php"])
                    component = os.path.join(*parts)
                    os.makedirs(os.path.dirname(component), exist_ok=True)
                    with open(component, "w", encoding="utf-8") as target:
                        target.write(f"<p>{article['title']}</p>")

            with (
                patch.object(ncms_fetch, "database_id", "database"),
                patch.object(
                    ncms_fetch,
                    "fetch_database_content",
                    return_value=[make_page("world/example")],
                ),
                patch.object(
                    ncms_fetch,
                    "extract_fields",
                    return_value=[base, hindi],
                ),
                patch.object(
                    ncms_fetch,
                    "transform_to_php",
                    side_effect=fake_transform,
                ),
            ):
                metadata = ncms_fetch.publish_to_bundle(
                    "publish", None, temp_dir, metadata_path
                )

            self.assertEqual(
                ["en", "hi"],
                [variant["language"] for variant in metadata["variants"]],
            )
            self.assertEqual(
                "HTML/Component/hi/world/example/index.php",
                metadata["variants"][1]["component"],
            )
            self.assertEqual("page-1", metadata["page_id"])
            self.assertNotIn("requested_language", metadata)

    def test_language_prefixed_slug_publishes_only_that_translation(self):
        base = {
            "id": "page-1",
            "status": "publish",
            "slug": "world/example",
            "title": "Example",
            "description": "Description",
            "language": "en",
        }
        hindi = {
            "id": "child-hi",
            "status": "publish",
            "slug": "world/example",
            "title": "हिंदी उदाहरण",
            "description": "हिंदी विवरण",
            "language": "hi",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_path = os.path.join(temp_dir, "metadata.json")
            transformed = []

            def fake_transform(articles):
                transformed.extend(article["language"] for article in articles)
                for article in articles:
                    parts = [temp_dir, "HTML", "Component"]
                    if article["language"] != "en":
                        parts.append(article["language"])
                    parts.extend(["world", "example", "index.php"])
                    component = os.path.join(*parts)
                    os.makedirs(os.path.dirname(component), exist_ok=True)
                    with open(component, "w", encoding="utf-8") as target:
                        target.write(f"<p>{article['title']}</p>")

            with (
                patch.object(ncms_fetch, "database_id", "database"),
                patch.object(
                    ncms_fetch,
                    "fetch_database_content",
                    return_value=[make_page("world/example")],
                ),
                patch.object(
                    ncms_fetch,
                    "extract_fields",
                    return_value=[base, hindi],
                ),
                patch.object(
                    ncms_fetch,
                    "transform_to_php",
                    side_effect=fake_transform,
                ),
            ):
                metadata = ncms_fetch.publish_to_bundle(
                    "publish",
                    "hi/world/example",
                    temp_dir,
                    metadata_path,
                )

            self.assertEqual(["hi"], transformed)
            self.assertEqual(["hi"], [v["language"] for v in metadata["variants"]])
            self.assertEqual("hi", metadata["language"])
            self.assertEqual("hi", metadata["requested_language"])
            self.assertTrue(metadata["translation_merge"])
            self.assertEqual("page-1", metadata["page_id"])
            self.assertEqual("world/example", metadata["slug"])


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
