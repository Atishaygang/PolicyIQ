from collections import Counter
from langchain_core.documents import Document


def find_repeated_lines(documents, threshold=0.6):
    line_counter = Counter()
    total_pages = len(documents)

    for doc in documents:
        unique_lines = set(
            line.strip()
            for line in doc.page_content.splitlines()
            if line.strip()
        )

        line_counter.update(unique_lines)

    return {
        line
        for line, count in line_counter.items()
        if count / total_pages >= threshold
    }


def clean_documents(documents, repeated_lines):
    cleaned_docs = []

    for doc in documents:
        # PyMuPDFLoader stores page as zero-indexed
        pdf_page_number = str(doc.metadata["page"] + 1)

        cleaned_lines = [
            line
            for line in doc.page_content.splitlines()
            if line.strip() not in repeated_lines
            and line.strip() != pdf_page_number
        ]

        cleaned_docs.append(
            Document(
                page_content="\n".join(cleaned_lines),
                metadata=doc.metadata.copy()
            )
        )

    return cleaned_docs