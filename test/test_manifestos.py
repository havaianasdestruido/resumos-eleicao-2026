"""Testes leves; não executam nem apagam outputs dos notebooks."""

import base64
import json
import unittest
from pathlib import Path

from manifestos import is_sha512_base64, load_manifests


ROOT = Path(__file__).resolve().parent.parent


class ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifests = load_manifests(ROOT)

    def test_inventory_skips_macos_metadata_but_keeps_both_media_dates(self):
        self.assertEqual(len(self.manifests), 32)
        self.assertFalse(any("__MACOSX" in str(m.source) for m in self.manifests))
        media = [m for m in self.manifests if m.family == "midias"]
        self.assertEqual(len(media), 8)
        self.assertEqual({m.subtitle.rsplit(" - ", 1)[1] for m in media}, {"01/09/2026", "02/09/2026"})

    def test_urna_sections_are_not_counted_as_files(self):
        urna = next(m for m in self.manifests if m.source.parent.name == "path1u13")
        self.assertEqual(sum(e.kind == "file" for e in urna.entries), 611)
        self.assertEqual(sum(e.kind == "aggregate" for e in urna.entries), 28)
        self.assertEqual(sum(e.section == "UF = SP" and e.kind == "file" for e in urna.entries), 17)
        self.assertEqual(sum(e.path == "HASH GERAL UF = SP" for e in urna.entries), 1)
        self.assertFalse(any(e.path == "ARQUIVOS BASE" for e in urna.entries))

    def test_all_digest_strings_have_sha512_base64_shape(self):
        entries = [e for m in self.manifests for e in m.entries]
        self.assertGreater(len(entries), 3000)
        self.assertTrue(all(is_sha512_base64(e.digest) for e in entries))
        self.assertFalse(is_sha512_base64("not a hash"))
        # Formato correto não prova autenticidade nem permite verificar arquivos ausentes.

    def test_png_figures_are_embedded_in_every_notebook(self):
        paths = sorted((ROOT / "test").glob("*.ipynb"))
        self.assertGreaterEqual(len(paths), 3)
        for path in paths:
            with self.subTest(notebook=path.name):
                notebook = json.loads(path.read_text(encoding="utf-8"))
                images = [
                    output["data"]["image/png"]
                    for cell in notebook["cells"]
                    for output in cell.get("outputs", [])
                    if "image/png" in output.get("data", {})
                ]
                self.assertTrue(images, "Execute test/run_notebooks.py e salve os outputs")
                for image in images:
                    if isinstance(image, list):
                        image = "".join(image)
                    self.assertTrue(base64.b64decode(image).startswith(b"\x89PNG\r\n\x1a\n"))


if __name__ == "__main__":
    unittest.main()
