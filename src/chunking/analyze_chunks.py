from statistics import mean, median
from collections import Counter

from src.ingestion.corpus import load_corpus
from src.chunking.splitter import split_documents


def analyze_chunks(chunks):

    lengths = [
        len(chunk.page_content)
        for chunk in chunks
    ]

    print("\n==============================")
    print("CHUNK ANALYSIS")
    print("==============================")

    print("Total chunks:", len(chunks))
    print("Average characters:", round(mean(lengths), 2))
    print("Median characters:", median(lengths))
    print("Minimum characters:", min(lengths))
    print("Maximum characters:", max(lengths))

    very_small_chunks = [
        chunk
        for chunk in chunks
        if len(chunk.page_content) < 200
    ]

    print(
        "Chunks under 200 characters:",
        len(very_small_chunks)
    )

    print("\n--- CHUNKS PER DOCUMENT ---")

    counts = Counter(
        chunk.metadata["document_id"]
        for chunk in chunks
    )

    for document_id, count in counts.items():
        print(
            f"{document_id}: {count}"
        )


if __name__ == "__main__":

    # 1. Build cleaned corpus
    corpus_docs = load_corpus(
        data_dir=r"D:\Policy_IQ\data\raw",
        manifest_path=r"D:\Policy_IQ\data\menifest.csv"
    )

    # 2. Experiment A
    chunks = split_documents(corpus_docs)

    # 3. Analyze
    analyze_chunks(chunks)

    # 4. Inspect sample chunks
    print("\n==============================")
    print("SAMPLE CHUNKS")
    print("==============================")

    for i, chunk in enumerate(chunks[:5]):

        print(f"\n--- CHUNK {i + 1} ---")

        print(chunk.page_content)

        print("\nMETADATA")

        print(
            "Document:",
            chunk.metadata.get("document_id")
        )

        print(
            "Filename:",
            chunk.metadata.get("filename")
        )

        print(
            "PDF page:",
            chunk.metadata.get("pdf_page")
        )

def inspect_document_chunks(chunks, document_id, limit=5):

    document_chunks = [
        chunk
        for chunk in chunks
        if chunk.metadata.get("document_id") == document_id
    ]

    print(
        f"\n===== {document_id} "
        f"| TOTAL CHUNKS: {len(document_chunks)} ====="
    )

    for i, chunk in enumerate(document_chunks[:limit]):

        print(f"\n--- CHUNK {i + 1} ---")
        print(
            f"Page: {chunk.metadata.get('pdf_page')} "
            f"| Characters: {len(chunk.page_content)}"
        )

        print(chunk.page_content)

inspect_document_chunks(chunks, "DOC001", 5)
inspect_document_chunks(chunks, "DOC004", 5)
inspect_document_chunks(chunks, "DOC006", 5)