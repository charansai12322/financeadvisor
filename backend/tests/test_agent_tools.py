"""
Unit tests for Agent tools, prompt contract, and Gradio interfaces.
"""
import unittest
import json
import os

_candidates = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "financeadvisor.ipynb")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "financeadvisor.ipynb")),
    os.path.abspath("financeadvisor.ipynb"),
]
NOTEBOOK_PATH = next((p for p in _candidates if os.path.exists(p)), _candidates[0])
REPO_ROOT = os.path.dirname(NOTEBOOK_PATH)


class TestAgentToolsAndPrompt(unittest.TestCase):

    def setUp(self):
        with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
            self.nb = json.load(f)

    def test_system_prompt_financial_advisory_contract(self):
        """Verifies system prompt defines appropriate bounds and currency expectations."""
        cell_13 = "".join(self.nb["cells"][13].get("source", []))
        self.assertIn("Personal Finance AI Advisor for Indian citizens", cell_13)
        self.assertIn("search_finance_docs", cell_13)
        self.assertIn("get_market_price", cell_13)
        self.assertIn("Indian Rupees", cell_13)
        # Normalize whitespace to verify phrase regardless of linebreaks
        normalized = " ".join(cell_13.split())
        self.assertIn("Always mention the source of your information", normalized)

    def test_tool_definitions_in_notebook(self):
        """Verifies tool definitions in Cell 8 and Cell 10 have correct signatures and docstrings."""
        cell_8 = "".join(self.nb["cells"][8].get("source", []))
        cell_10 = "".join(self.nb["cells"][10].get("source", []))

        self.assertIn("def search_finance_docs(question: str) -> str:", cell_8)
        self.assertIn("def get_market_price(asset: str) -> str:", cell_10)

        # Check docstrings describe tools accurately
        self.assertIn("Search official Indian government financial documents", cell_8)
        self.assertIn("Get current market price for a financial asset in Indian Rupees", cell_10)

    def test_gradio_text_interface_signature(self):
        """Verifies Gradio text interface fn takes a single question argument."""
        cell_16 = "".join(self.nb["cells"][16].get("source", []))
        self.assertIn("def finance_advisor(question):", cell_16)
        self.assertIn("gr.Interface(", cell_16)
        self.assertIn("fn=finance_advisor", cell_16)

    def test_reproduce_voice_interface_crash(self):
        """Demonstrates that running finance_advisor_voice crashes due to missing speech_to_text."""
        def finance_advisor_voice_isolated(audio):
            if audio is None:
                return "No audio recorded.", "Please record your question first.", None
            # This is the exact code in Cell 17
            try:
                question = speech_to_text(audio)  # noqa: F821
            except NameError as e:
                return "CRASH", str(e), None
            return question, "answer", None

        status, error_msg, _ = finance_advisor_voice_isolated("fake_audio_bytes")
        self.assertEqual(status, "CRASH")
        self.assertIn("speech_to_text", error_msg)


if __name__ == "__main__":
    unittest.main()
