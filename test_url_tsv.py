import tempfile
import unittest
from pathlib import Path

from ncms_fetch import update_url_tsv


class CoverUrlTests(unittest.TestCase):
    def test_only_explicit_covers_get_flat_canonical_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'Config'
            config.mkdir()
            url_file = config / 'Url.tsv'
            url_file.write_text(
                'Path\tName\tExtension\n'
                'science/physics/\tindex\tjpg\n'
                'science/physics/\tlegacy\tsvg\n'
                'policy/\tindex\tjpg\n',
                encoding='utf-8',
            )
            update_url_tsv([
                {'slug': 'science/physics', 'language': 'en',
                 'content': "require('../HTML/Fragment/Component_cover.php')"},
                {'slug': 'policy', 'language': 'en', 'content': '<p>No cover</p>'},
                {'slug': 'science/physics', 'language': 'hi', 'content': 'translated'},
            ], directory)
            self.assertEqual(url_file.read_text(encoding='utf-8').splitlines(), [
                'Path\tName\tExtension',
                'science/physics/\tlegacy\tsvg',
                'science/\tphysics\tjpg',
            ])


if __name__ == '__main__':
    unittest.main()
