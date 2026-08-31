from pathlib import Path
from collections import Counter

import pandas as pd

from src.ingestion.loader import load_and_clean_pdf


REQUIRED_MANIFEST_COLUMNS = {
    "document_id",
    "filename",
    "document_type",
    "category",
}


RESERVED_METADATA_KEYS = {
    "page",
    "pdf_page",
    "source",
    "file_path",
    "total_pages",
}


def load_manifest(manifest_path):

    manifest = pd.read_csv(manifest_path).fillna("")

    # -----------------------------
    # Required columns check
    # -----------------------------
    missing_columns = (
        REQUIRED_MANIFEST_COLUMNS - set(manifest.columns)
    )

    if missing_columns:
        raise ValueError(
            "Manifest missing required columns: "
            f"{sorted(missing_columns)}"
        )

    # Clean accidental spaces
    manifest["filename"] = (
        manifest["filename"]
        .astype(str)
        .str.strip()
    )

    manifest["document_id"] = (
        manifest["document_id"]
        .astype(str)
        .str.strip()
    )

    # -----------------------------
    # Duplicate filename check
    # -----------------------------
    if manifest["filename"].duplicated().any():

        duplicates = manifest[
            manifest["filename"].duplicated(keep=False)
        ]["filename"].tolist()

        raise ValueError(
            f"Duplicate filenames found in manifest: {duplicates}"
        )

    # -----------------------------
    # Duplicate document ID check
    # -----------------------------
    if manifest["document_id"].duplicated().any():

        duplicates = manifest[
            manifest["document_id"].duplicated(keep=False)
        ]["document_id"].tolist()

        raise ValueError(
            f"Duplicate document IDs found: {duplicates}"
        )

    # -----------------------------
    # Reserved metadata protection
    # -----------------------------
    conflicting_columns = (
        set(manifest.columns) & RESERVED_METADATA_KEYS
    )

    if conflicting_columns:
        raise ValueError(
            "Manifest contains reserved metadata columns: "
            f"{sorted(conflicting_columns)}"
        )

    return {
        row["filename"]: row.to_dict()
        for _, row in manifest.iterrows()
    }


def load_corpus(data_dir, manifest_path):

    manifest_lookup = load_manifest(manifest_path)

    corpus_docs = []

    # -----------------------------
    # Discover PDFs recursively
    # -----------------------------
    pdf_files = sorted(
        Path(data_dir).rglob("*.pdf")
    )

    discovered_filenames = {
        pdf_path.name
        for pdf_path in pdf_files
    }

    manifest_filenames = set(
        manifest_lookup.keys()
    )

    # -----------------------------
    # PDF exists but manifest missing
    # -----------------------------
    missing_manifest_entries = (
        discovered_filenames - manifest_filenames
    )

    if missing_manifest_entries:
        raise ValueError(
            "PDFs without manifest entries: "
            f"{sorted(missing_manifest_entries)}"
        )

    # -----------------------------
    # Manifest exists but PDF missing
    # -----------------------------
    missing_pdf_files = (
        manifest_filenames - discovered_filenames
    )

    if missing_pdf_files:
        raise ValueError(
            "Manifest entries without PDFs: "
            f"{sorted(missing_pdf_files)}"
        )

    # -----------------------------
    # Process each PDF independently
    # -----------------------------
    for pdf_path in pdf_files:

        _, clean_docs, repeated_lines = (
            load_and_clean_pdf(pdf_path)
        )

        manifest_metadata = (
            manifest_lookup[pdf_path.name]
        )

        # -----------------------------
        # Metadata enrichment
        # -----------------------------
        for doc in clean_docs:

            doc.metadata.update(
                manifest_metadata
            )

            doc.metadata["filename"] = (
                pdf_path.name
            )

            doc.metadata["pdf_page"] = (
                doc.metadata["page"] + 1
            )

        corpus_docs.extend(clean_docs)

        print(
            f"Loaded {pdf_path.name} "
            f"| Pages: {len(clean_docs)} "
            f"| Boilerplate patterns detected: "
            f"{len(repeated_lines)}"
        )

    return corpus_docs


if __name__ == "__main__":

    corpus_docs = load_corpus(
        data_dir=r"D:\Policy_IQ\data\raw",
        manifest_path=r"D:\Policy_IQ\data\menifest.csv"
    )

    # =====================================================
    # CORPUS VALIDATION
    # =====================================================

    print("\n==============================")
    print("CORPUS SUMMARY")
    print("==============================")

    print(
        "PDF files loaded:",
        len(
            set(
                doc.metadata["filename"]
                for doc in corpus_docs
            )
        )
    )

    print(
        "Total page documents:",
        len(corpus_docs)
    )

    empty_pages = [
        doc
        for doc in corpus_docs
        if not doc.page_content.strip()
    ]

    print(
        "Empty pages:",
        len(empty_pages)
    )

    # -----------------------------
    # Document page counts
    # -----------------------------
    print("\n--- DOCUMENT PAGE COUNTS ---")

    counts = Counter(
        doc.metadata["document_id"]
        for doc in corpus_docs
    )

    for document_id, page_count in counts.items():
        print(
            f"{document_id}: {page_count}"
        )

    # -----------------------------
    # Sample combined document
    # -----------------------------
    if corpus_docs:

        sample_index = min(
            25,
            len(corpus_docs) - 1
        )

        doc = corpus_docs[sample_index]

        print("\n--- SAMPLE PAGE CONTENT ---")

        print(
            doc.page_content[:500]
        )

        print("\n--- SAMPLE METADATA ---")

        for key, value in doc.metadata.items():
            print(
                f"{key}: {value}"
            )

    # -----------------------------
    # Empty page inspection
    # -----------------------------
    if empty_pages:

        print("\n--- EMPTY PAGES ---")

        for doc in empty_pages:
            print(
                doc.metadata["filename"],
                "| PDF page:",
                doc.metadata["pdf_page"]
            )