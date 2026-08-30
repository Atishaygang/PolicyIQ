from langchain_community.document_loaders import PyMuPDFLoader
from cleaner import find_repeated_lines, clean_documents


def load_and_clean_pdf(file_path):
    loader = PyMuPDFLoader(str(file_path))

    raw_docs = loader.load()

    repeated_lines = find_repeated_lines(raw_docs)

    clean_docs = clean_documents(
        raw_docs,
        repeated_lines
    )

    return raw_docs, clean_docs, repeated_lines

