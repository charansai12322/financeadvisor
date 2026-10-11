"""
Static analysis and security audit tests.
Validates notebook structure, absence of hardcoded secrets, undefined symbols,
and environment assumptions.
"""
import unittest
import json
import os
import re

# Search candidate locations for financeadvisor.ipynb (root vs backend)
_candidates = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "financeadvisor.ipynb")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "financeadvisor.ipynb")),
    os.path.abspath("financeadvisor.ipynb"),
]
NOTEBOOK_PATH = next((p for p in _candidates if os.path.exists(p)), _candidates[0])
REPO_ROOT = os.path.dirname(NOTEBOOK_PATH)


class TestStaticAndSecurity(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.exists(NOTEBOOK_PATH), f"Notebook not found at {NOTEBOOK_PATH}")
        with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
            self.nb = json.load(f)

    def test_notebook_structure_and_cell_count(self):
        """Verify notebook format and total cell count."""
        self.assertEqual(self.nb.get("nbformat"), 4)
        cells = self.nb.get("cells", [])
        self.assertEqual(len(cells), 19, "Expected 19 cells in financeadvisor.ipynb")
        self.assertEqual(cells[0].get("cell_type"), "markdown")
        for i in range(1, 19):
            self.assertEqual(cells[i].get("cell_type"), "code", f"Cell {i} expected to be code")

    def test_zero_hardcoded_secrets_in_notebook(self):
        """Ensure no API keys, tokens, or credentials are hardcoded in notebook source or outputs."""
        with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
            raw_content = f.read()

        secret_patterns = [
            (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
            (r"sk-[0-9A-Za-z]{32,}", "OpenAI API Key"),
            (r"hf_[0-9A-Za-z]{34,}", "Hugging Face Token"),
            (r"(?i)api[_-]?key[\"\'\s:=]+([a-zA-Z0-9_\-]{20,})", "Generic API Key"),
        ]

        for pattern, label in secret_patterns:
            matches = re.findall(pattern, raw_content)
            self.assertEqual(len(matches), 0, f"Potential {label} detected: {matches}")

    def test_detect_undefined_voice_functions(self):
        """Cell 17 references speech_to_text and text_to_speech without defining or importing them."""
        cell_17 = "".join(self.nb["cells"][17].get("source", []))
        self.assertIn("speech_to_text", cell_17)
        self.assertIn("text_to_speech", cell_17)

        # Check if defined anywhere in notebook preceding cell 17
        all_prior_code = ""
        for i in range(17):
            all_prior_code += "".join(self.nb["cells"][i].get("source", [])) + "\n"

        self.assertNotIn("def speech_to_text", all_prior_code, "speech_to_text should be missing prior to cell 17")
        self.assertNotIn("def text_to_speech", all_prior_code, "text_to_speech should be missing prior to cell 17")
        self.assertNotIn("import speech_to_text", all_prior_code)
        self.assertNotIn("import text_to_speech", all_prior_code)

    def test_detect_colab_specific_userdata_import(self):
        """Cell 12 imports google.colab.userdata which fails outside Google Colab."""
        cell_12 = "".join(self.nb["cells"][12].get("source", []))
        self.assertIn("from google.colab import userdata", cell_12)
        self.assertIn("userdata.get('sec1')", cell_12)

    def test_detect_hardcoded_colab_filesystem_paths(self):
        """Cell 2 uses hardcoded Linux /content/pdfs path."""
        cell_2 = "".join(self.nb["cells"][2].get("source", []))
        self.assertIn("/content/pdfs", cell_2)


if __name__ == "__main__":
    unittest.main()
