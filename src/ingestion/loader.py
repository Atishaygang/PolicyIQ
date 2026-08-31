from langchain_community.document_loaders import PyMuPDFLoader
from src.ingestion.cleaner import (
    find_repeated_lines,
    clean_documents,
)


def load_and_clean_pdf(file_path):
    loader = PyMuPDFLoader(str(file_path))

    raw_docs = loader.load()

    repeated_lines = find_repeated_lines(raw_docs)

    clean_docs = clean_documents(
        raw_docs,
        repeated_lines
    )

    return raw_docs, clean_docs, repeated_lines

if __name__ == "__main__":

    raw_docs, clean_docs, repeated_lines = load_and_clean_pdf(
        r"D:\Policy_IQ\data\raw\motor\1_motor_policy.pdf"
    )

    print("\n--- RAW PAGE 1 ---")

    print([
        repr(line)
        for line in raw_docs[0].page_content.splitlines()[:10]
    ])

    print("\n--- CLEAN PAGE 1 ---")

    print([
        repr(line)
        for line in clean_docs[0].page_content.splitlines()[:10]
    ])

    print("\nMetadata page:", raw_docs[0].metadata["page"])

    print(
        "Expected page number:",
        raw_docs[0].metadata["page"] + 1
    )