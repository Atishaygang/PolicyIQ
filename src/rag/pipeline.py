from src.retrieval.retriever import retrieve_documents
from src.rag.llm import get_llm
from src.rag.prompt import SYSTEM_PROMPT , USER_PROMPT

def build_context(documents):

    context_parts = []

    for index, doc in enumerate(
        documents,
        start=1
    ):

        source = (
            f"[SOURCE {index}]\n"
            f"Document ID: "
            f"{doc.metadata['document_id']}\n"
            f"Filename: "
            f"{doc.metadata['filename']}\n"
            f"PDF Page: "
            f"{doc.metadata['pdf_page']}\n"
            f"Content:\n"
            f"{doc.page_content}"
        )

        context_parts.append(source)

    return "\n\n".join(context_parts)

def ask_policyiq(question):

    documents = retrieve_documents(
        query=question,
        k=5
    )

    context = build_context(documents)

    user_prompt = USER_PROMPT.format(
        context=context,
        question=question
    )

    llm = get_llm()

    response = llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", user_prompt)
        ]
    )

    return response.content, documents

if __name__ == "__main__":

    question = (
        "What will HDFC ERGO's share price be next month?"
    )

    answer, sources = ask_policyiq(question)

    print("\n==============================")
    print("POLICYIQ ANSWER")
    print("==============================")

    print(answer)

    print("\n==============================")
    print("RETRIEVED SOURCES")
    print("==============================")

    for index, doc in enumerate(
        sources,
        start=1
    ):
        print(
            f"{index}. "
            f"{doc.metadata['document_id']} "
            f"| Page {doc.metadata['pdf_page']}"
        )