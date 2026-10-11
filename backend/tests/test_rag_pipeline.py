"""
Unit tests for GST Document and RAG pipeline.
Audits document metadata formatting, TypeError bug reproduction, and vector deduplication logic.
"""
import unittest


class MockDocument:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata


# Notebook Cell 8 original formatting logic
def original_format_search_results(results):
    if not results:
        return "No relevant information found in the knowledge base."
    context = ""
    for doc in results:
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "N/A")
        # In Cell 8: context += f"Source: {source} (Page {page + 1})\n"
        context += f"Source: {source} (Page {page + 1})\n"
        context += f"Content: {doc.page_content}\n\n"
    return context


# Hardened safe formatting logic
def hardened_format_search_results(results):
    if not results:
        return "No relevant information found in the knowledge base."
    context_blocks = []
    for doc in results:
        source = doc.metadata.get("source", "Official Document")
        # Extract clean filename if source is a file path
        clean_source = source.replace("\\", "/").split("/")[-1] if isinstance(source, str) else str(source)
        page_val = doc.metadata.get("page")
        if isinstance(page_val, int):
            page_str = f"Page {page_val + 1}"
        elif page_val is not None and str(page_val).isdigit():
            page_str = f"Page {int(page_val) + 1}"
        else:
            page_str = "Page Unknown"

        block = f"Source: {clean_source} ({page_str})\nContent: {doc.page_content.strip()}"
        context_blocks.append(block)
    return "\n\n".join(context_blocks)


class TestRAGPipeline(unittest.TestCase):

    def test_original_formatting_success_with_integer_page(self):
        """When doc metadata contains integer page (0-indexed), original formatting produces 1-indexed page."""
        docs = [MockDocument("GST rate on gold is 3%.", {"source": "gst_reckoner.pdf", "page": 5})]
        formatted = original_format_search_results(docs)
        self.assertIn("Source: gst_reckoner.pdf (Page 6)", formatted)
        self.assertIn("Content: GST rate on gold is 3%.", formatted)

    def test_original_formatting_crashes_on_missing_page(self):
        """When metadata has no 'page' key, default 'N/A' causes TypeError: can only concatenate str to str."""
        docs = [MockDocument("General financial advisory.", {"source": "sebi_booklet.pdf"})]
        with self.assertRaises(TypeError):
            original_format_search_results(docs)

    def test_original_formatting_crashes_on_string_page(self):
        """When metadata has 'page': 'cover', TypeError is raised."""
        docs = [MockDocument("Title page", {"source": "sebi.pdf", "page": "cover"})]
        with self.assertRaises(TypeError):
            original_format_search_results(docs)

    def test_hardened_formatting_handles_missing_page_safely(self):
        """Hardened formatter handles missing, string, or non-integer page metadata safely."""
        docs = [
            MockDocument("Section 1 content", {"source": "/content/pdfs/document_1.pdf"}),
            MockDocument("Section 2 content", {"source": "C:\\docs\\gst.pdf", "page": "N/A"}),
            MockDocument("Section 3 content", {"source": "doc.pdf", "page": 10}),
        ]
        result = hardened_format_search_results(docs)
        self.assertIn("document_1.pdf (Page Unknown)", result)
        self.assertIn("gst.pdf (Page Unknown)", result)
        self.assertIn("doc.pdf (Page 11)", result)
        self.assertIn("Section 1 content", result)

    def test_vector_store_deduplication_necessity(self):
        """
        Simulate Chroma vector store behavior:
        Adding identical chunks without IDs increments collection count, causing duplicate retrieval results.
        """
        simulated_collection = []

        def naive_add_documents(chunks):
            # This is what Cell 6 did: vector_store.add_documents(documents=batch)
            simulated_collection.extend(chunks)

        chunks = [{"text": "GST on silver is 3%"}, {"text": "Gold import duty is 6%"}]
        naive_add_documents(chunks)
        self.assertEqual(len(simulated_collection), 2)

        # Rerunning cell 6 duplicates all documents!
        naive_add_documents(chunks)
        self.assertEqual(len(simulated_collection), 4, "Naive addition duplicated chunks")

        # Deterministic ID approach prevents duplicates
        id_indexed_collection = {}
        def deduplicated_add_documents(chunks):
            for i, c in enumerate(chunks):
                doc_id = f"chunk_{i}_{hash(c['text'])}"
                id_indexed_collection[doc_id] = c

        deduplicated_add_documents(chunks)
        self.assertEqual(len(id_indexed_collection), 2)
        # Rerunning does not duplicate
        deduplicated_add_documents(chunks)
        self.assertEqual(len(id_indexed_collection), 2, "Deduplication successfully prevented duplicates")


if __name__ == "__main__":
    unittest.main()
