"""
Vector Store Repository.
Manages persistent Chroma DB collection access with lazy-loaded embeddings
and deterministic chunk IDs for idempotent ingestion.
"""
import hashlib
import os
from typing import Any, Dict, List, Optional, Tuple
import chromadb
from app.core.config import get_settings
from app.core.logging import logger
from app.schemas.documents import DocumentChunk


class VectorStoreRepository:
    """Repository encapsulating persistent Chroma collection operations."""

    def __init__(self):
        self._settings = get_settings()
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection = None

    def _get_client(self) -> chromadb.PersistentClient:
        if self._client is None:
            persist_dir = os.path.abspath(self._settings.chroma_persist_directory)
            os.makedirs(persist_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(path=persist_dir)
            logger.info(f"Connected to persistent Chroma DB at {persist_dir}")
        return self._client

    def get_collection(self):
        """Lazily retrieves or creates the Chroma collection."""
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=self._settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def get_status(self) -> Dict[str, Any]:
        """Returns collection count, persistence path, and document sources."""
        try:
            collection = self.get_collection()
            count = collection.count()
            # Sample documents in collection to extract unique sources
            sources = set()
            if count > 0:
                sample = collection.get(limit=min(count, 100), include=["metadatas"])
                for meta in sample.get("metadatas", []):
                    if meta and "source" in meta:
                        sources.add(os.path.basename(str(meta["source"])))

            return {
                "indexed": count > 0,
                "collection_name": self._settings.chroma_collection_name,
                "total_chunks": count,
                "available_documents": sorted(list(sources)),
                "storage_directory": os.path.abspath(self._settings.chroma_persist_directory),
            }
        except Exception as e:
            logger.error(f"Error checking vector store status: {e}")
            return {
                "indexed": False,
                "collection_name": self._settings.chroma_collection_name,
                "total_chunks": 0,
                "available_documents": [],
                "storage_directory": os.path.abspath(self._settings.chroma_persist_directory),
            }

    @staticmethod
    def generate_chunk_id(source_name: str, page: Optional[int], chunk_index: int, content: str) -> str:
        """
        Generates a deterministic unique chunk ID based on source, page, index, and content hash.
        Guarantees that re-ingesting the exact same documents produces identical IDs.
        """
        content_hash = hashlib.sha256(content.strip().encode("utf-8")).hexdigest()[:16]
        clean_source = os.path.basename(source_name).replace(" ", "_")
        return f"{clean_source}_p{page or 0}_c{chunk_index}_{content_hash}"

    def upsert_chunks_idempotent(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100,
    ) -> Tuple[int, int]:
        """
        Idempotently inserts or updates chunks into the collection using deterministic IDs.
        Returns (total_processed, new_or_updated_count).
        """
        collection = self.get_collection()
        total = len(chunks)
        if total == 0:
            return 0, 0

        for i in range(0, total, batch_size):
            batch = chunks[i : i + batch_size]
            ids = [c["id"] for c in batch]
            documents = [c["content"] for c in batch]
            metadatas = [c["metadata"] for c in batch]

            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
            logger.info(f"Upserted chunks {min(i + len(batch), total)}/{total}")

        final_count = collection.count()
        return total, final_count

    def search_similarity(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[DocumentChunk]:
        """
        Performs query search against Chroma collection.
        Formats results into DocumentChunk with safe metadata.
        """
        collection = self.get_collection()
        count = collection.count()
        if count == 0:
            return []

        actual_k = min(top_k, count)
        results = collection.query(
            query_texts=[query],
            n_results=actual_k,
            include=["documents", "metadatas", "distances"],
        )

        formatted_chunks = []
        doc_lists = results.get("documents", [[]])[0]
        meta_lists = results.get("metadatas", [[]])[0]
        dist_lists = results.get("distances", [[]])[0] if "distances" in results else []

        for idx, text in enumerate(doc_lists):
            meta = meta_lists[idx] if idx < len(meta_lists) else {}
            dist = dist_lists[idx] if idx < len(dist_lists) else None

            raw_source = meta.get("source", "Official Document")
            clean_source = os.path.basename(str(raw_source))

            raw_page = meta.get("page")
            int_page: Optional[int] = None
            if isinstance(raw_page, int):
                int_page = raw_page
                page_label = f"Page {raw_page + 1}"
            elif raw_page is not None and str(raw_page).isdigit():
                int_page = int(raw_page)
                page_label = f"Page {int_page + 1}"
            else:
                page_label = "Page Unknown"

            formatted_chunks.append(
                DocumentChunk(
                    content=text.strip(),
                    source=clean_source,
                    page=int_page,
                    page_label=page_label,
                    score=round(float(dist), 4) if dist is not None else None,
                )
            )

        return formatted_chunks


vector_store_repository = VectorStoreRepository()
