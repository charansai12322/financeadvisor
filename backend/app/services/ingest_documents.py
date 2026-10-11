"""
Document Ingestion Script and Service.
Downloads reference PDFs (if not already cached locally), extracts text,
splits into chunks, and idempotently indexes into Chroma DB with deterministic IDs.
"""
import os
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure backend root directory is on sys.path for direct script execution
_backend_dir = str(Path(__file__).resolve().parent.parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from app.core.config import get_settings
from app.core.logging import logger
from app.repositories.vector_store import (
    VectorStoreRepository,
    vector_store_repository,
)


PDF_SOURCES = [
    {
        "id": "sebi_financial_education_booklet",
        "filename": "Financial_Education_Booklet_English.pdf",
        "url": "https://investor.sebi.gov.in/pdf/downloadable-documents/Financial%20Education%20Booklet%20-%20English.pdf",
        "title": "SEBI Financial Education Booklet (English)",
    },
    {
        "id": "cbic_gst_ready_reckoner",
        "filename": "CBIC_GST_Ready_Reckoner.pdf",
        "url": "https://a2ztaxcorp.net/wp-content/uploads/2025/09/CBIC-GST-Ready-Reckoner-indicating-updated-Central-Goods-and-Services-Tax-CGST-rates-on-goods.pdf",
        "title": "CBIC GST Ready Reckoner — Updated CGST Rates",
    },
]


def download_pdf_if_missing(url: str, destination_path: str) -> bool:
    """
    Downloads a PDF from url if destination_path does not exist.
    Handles Indian government CA intermediate certificates safely.
    """
    if os.path.exists(destination_path) and os.path.getsize(destination_path) > 10000:
        logger.info(f"Using locally cached PDF: {destination_path}")
        return True

    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    logger.info(f"Downloading reference PDF from {url} to {destination_path}...")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FinanceAdvisorIngestion/1.0"}
    req = urllib.request.Request(url, headers=headers)

    try:
        # First attempt with standard SSL validation
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            if not content.startswith(b"%PDF-"):
                raise ValueError("Downloaded payload is not a valid PDF header")
            with open(destination_path, "wb") as f:
                f.write(content)
            logger.info(f"Successfully downloaded {os.path.basename(destination_path)} ({len(content)} bytes)")
            return True
    except urllib.error.URLError as e:
        logger.warning(f"Standard SSL check failed for {url}: {e}. Retrying with unverified context...")
        try:
            # Fallback for Indian gov root CA chain
            ctx = ssl._create_unverified_context()
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                content = resp.read()
                if not content.startswith(b"%PDF-"):
                    raise ValueError("Downloaded payload is not a valid PDF header")
                with open(destination_path, "wb") as f:
                    f.write(content)
                logger.info(f"Downloaded via fallback SSL context: {destination_path} ({len(content)} bytes)")
                return True
        except Exception as retry_err:
            logger.error(f"Failed to download PDF from {url}: {retry_err}")
            return False


def load_pdf_pages(file_path: str) -> List[Dict[str, Any]]:
    """Loads and extracts text page by page from a local PDF using PyPDF."""
    pages = []
    reader = PdfReader(file_path)
    filename = os.path.basename(file_path)

    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append({
                "page": idx,
                "text": text.strip(),
                "source": filename,
            })
    return pages


def chunk_pages(pages: List[Dict[str, Any]], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
    """Splits extracted page texts into overlapping chunks with metadata."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = []
    chunk_counter = 0

    for p in pages:
        sub_chunks = splitter.split_text(p["text"])
        for sc in sub_chunks:
            if not sc.strip():
                continue
            chunk_id = VectorStoreRepository.generate_chunk_id(
                source_name=p["source"],
                page=p["page"],
                chunk_index=chunk_counter,
                content=sc,
            )
            chunks.append({
                "id": chunk_id,
                "content": sc.strip(),
                "metadata": {
                    "source": p["source"],
                    "page": p["page"],
                    "chunk_index": chunk_counter,
                },
            })
            chunk_counter += 1

    return chunks


def run_ingestion(repo: Optional[VectorStoreRepository] = None) -> Dict[str, Any]:
    """
    Executes complete ingestion pipeline:
    1. Downloads missing PDFs to PDF_STORAGE_DIR.
    2. Extracts and chunks text.
    3. Idempotently upserts into Chroma collection.
    """
    settings = get_settings()
    v_repo = repo or vector_store_repository
    storage_dir = os.path.abspath(settings.pdf_storage_dir)
    os.makedirs(storage_dir, exist_ok=True)

    total_pages = 0
    all_chunks = []

    for src in PDF_SOURCES:
        dest = os.path.join(storage_dir, src["filename"])
        success = download_pdf_if_missing(src["url"], dest)
        if not success:
            logger.warning(f"Skipping source {src['id']} due to download failure")
            continue

        pages = load_pdf_pages(dest)
        total_pages += len(pages)
        chunks = chunk_pages(pages)
        all_chunks.extend(chunks)
        logger.info(f"Loaded {src['title']}: {len(pages)} pages, {len(chunks)} chunks")

    logger.info(f"Total chunks prepared across all sources: {len(all_chunks)}")
    processed, total_in_db = v_repo.upsert_chunks_idempotent(all_chunks)

    return {
        "sources_processed": len(PDF_SOURCES),
        "total_pages": total_pages,
        "total_chunks_processed": processed,
        "total_chunks_in_collection": total_in_db,
    }


if __name__ == "__main__":
    result = run_ingestion()
    print("Ingestion Complete:", result)
