import json
import tempfile
import unittest
from pathlib import Path

import ncms_fetch


class FirebaseRouteTests(unittest.TestCase):
    def test_generates_menu_rewrite_for_persisted_translation_language(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "Config"
            config_dir.mkdir()
            (config_dir / "ID_hi.tsv").write_text(
                "Status\tId\tLabel\tTitle\tJS\tDescription\tType\n",
                encoding="utf-8",
            )

            previous_project_dir = ncms_fetch.project_dir
            ncms_fetch.project_dir = str(root)
            try:
                ncms_fetch.update_firebase_json(
                    [{"slug": "about", "language": "en"}], str(root)
                )
            finally:
                ncms_fetch.project_dir = previous_project_dir

            firebase = json.loads(
                (root / "build" / "firebase.json").read_text(encoding="utf-8")
            )
            self.assertIn(
                {
                    "source": "/hi/menu",
                    "destination": "/hi/root/index.html",
                },
                firebase["hosting"]["rewrites"],
            )


if __name__ == "__main__":
    unittest.main()
