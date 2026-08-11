import unittest

import ncms_upload


class FakeChildren:
    def list(self, **kwargs):
        return {
            'results': [
                {'id': 'translation', 'type': 'child_page'},
                {'id': 'nested-db', 'type': 'child_database'},
                {'id': 'paragraph', 'type': 'paragraph'},
            ],
            'has_more': False,
            'next_cursor': None,
        }

    def append(self, **kwargs):
        raise AssertionError('append is not expected in this test')


class FakeBlocks:
    def __init__(self):
        self.children = FakeChildren()
        self.deleted = []

    def delete(self, block_id):
        self.deleted.append(block_id)


class FakeNotion:
    def __init__(self):
        self.blocks = FakeBlocks()


class UploadImageSafetyTests(unittest.TestCase):
    def test_clear_preserves_nested_pages_and_databases(self):
        original = ncms_upload.notion
        fake = FakeNotion()
        ncms_upload.notion = fake
        try:
            ncms_upload.clear_page_content('canonical-page')
        finally:
            ncms_upload.notion = original

        self.assertEqual(['paragraph'], fake.blocks.deleted)


if __name__ == '__main__':
    unittest.main()
