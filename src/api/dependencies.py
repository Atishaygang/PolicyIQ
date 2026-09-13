

# ==========================================
# Preload PolicyIQ components
# ==========================================

def preload_policyiq():

    from src.retrieval.hybrid_retriever import hybrid_search
    from src.retrieval.reranker import get_reranker
    from src.rag.llm import get_llm

    warmup_question = "What is No Claim Bonus?"

    print("\n======================================")
    print("PRELOADING POLICYIQ")
    print("======================================")

    print("Loading retrieval components...")

    hybrid_search(
        query=warmup_question,
        dense_k=10,
        bm25_k=10,
        final_k=10
    )

    print("Retrieval components loaded.")

    print("Loading Jina reranker...")

    get_reranker()

    print("Jina reranker loaded.")

    print("Loading LLM client...")

    get_llm()

    print("LLM client loaded.")

    print("======================================")
    print("POLICYIQ PRELOAD COMPLETE")
    print("======================================\n")