from collections import Counter
import re

from langchain_core.documents import Document


PAGE_LABEL_PATTERN = re.compile(
    r"^\d+\s*\|\s*.*(?:page|p\s*a\s*g\s*e).*$",
    re.IGNORECASE
)


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

        # PyMuPDFLoader stores page index from 0
        pdf_page_number = str(
            doc.metadata["page"] + 1
        )

        # ==================================================
        # STAGE 1:
        # Remove blank lines + repeated boilerplate first
        # ==================================================

        filtered_lines = []

        for line in doc.page_content.splitlines():

            stripped = (
                line.strip()
                .replace("\u00a0", " ")
                .replace("\u200b", "")
                .replace("\ufeff", "")
            )

            # Ignore blank lines
            if not stripped:
                continue

            # Remove repeated headers / footers
            if stripped in repeated_lines:
                continue

            filtered_lines.append(line)

        # ==================================================
        # STAGE 2:
        # Remove page numbers / dynamic page labels
        # after boilerplate has already been removed
        # ==================================================

        cleaned_lines = []

        for index, line in enumerate(filtered_lines):

            stripped = (
                line.strip()
                .replace("\u00a0", " ")
                .replace("\u200b", "")
                .replace("\ufeff", "")
            )

            near_boundary = (
                index < 5
                or index >= len(filtered_lines) - 5
            )

            # Remove dynamic page labels such as:
            # 26 | पृʿ / P a g e
            if (
                near_boundary
                and PAGE_LABEL_PATTERN.match(stripped)
            ):
                continue

            # Remove simple printed page number such as:
            # 1
            # 2
            # 26
            #
            # Only when it matches the actual PDF page number.
            if (
                near_boundary
                and stripped == pdf_page_number
            ):
                continue

            cleaned_lines.append(line)

        cleaned_docs.append(
            Document(
                page_content="\n".join(cleaned_lines),
                metadata=doc.metadata.copy()
            )
        )

    return cleaned_docs