from src.retrieval.retriever import retrieve_documents
from src.rag.llm import get_llm
from src.rag.prompt import SYSTEM_PROMPT, USER_PROMPT


def build_context(documents):

    context_parts = []

    for index, doc in enumerate(
        documents,
        start=1
    ):

        source = (
            f"[SOURCE {index}]\n"
            f"Document ID: {doc.metadata['document_id']}\n"
            f"Filename: {doc.metadata['filename']}\n"
            f"PDF Page: {doc.metadata['pdf_page']}\n"
            f"Content:\n"
            f"{doc.page_content}"
        )

        context_parts.append(source)

    return "\n\n".join(context_parts)


def build_sources(documents):

    sources = []

    for doc in documents:

        source = {
            "document_id": doc.metadata["document_id"],
            "filename": doc.metadata["filename"],
            "page": doc.metadata["pdf_page"]
        }

        sources.append(source)

    return sources


def ask_policyiq(question):

    documents = retrieve_documents(
        query=question,
        k=5
    )

    context = build_context(documents)

    formatted_user_prompt = USER_PROMPT.format(
        context=context,
        question=question
    )

    llm = get_llm()

    response = llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", formatted_user_prompt)
        ]
    )

    sources = build_sources(documents)

    result = {
        "question": question,
        "answer": response.content,
        "sources": sources
    }

    return result


if __name__ == "__main__":

    question = (
        """What is the insurance policy if the driver was
          drunk at the time of driving"""
    )

    result = ask_policyiq(question)

    print("\n==============================")
    print("POLICYIQ ANSWER")
    print("==============================")

    print(result["answer"])

    print("\n==============================")
    print("RETRIEVED SOURCES")
    print("==============================")

    for index, source in enumerate(
        result["sources"],
        start=1
    ):

        print(
            f"{index}. "
            f"{source['document_id']} "
            f"| {source['filename']} "
            f"| Page {source['page']}"
        )