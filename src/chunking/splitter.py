from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(
        documents,
        chunk_size = 1200,
        chunk_overlap=200
):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ],
        length_function=len
    )

    chunks = splitter.split_documents(documents)

    return chunks
