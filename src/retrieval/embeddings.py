from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np 


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def cosine_similarity(a,b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )

def get_embed_model():
    embedding_model = HuggingFaceEmbeddings(
        model_name = MODEL_NAME,
        model_kwargs = {
            'device':"cpu"
        },
        encode_kwargs = {
            'normalize_embeddings': True
        }
    )
    return embedding_model

if __name__ == "__main__":

    model = get_embed_model()

    texts = [
        "Damage caused while driving under the influence of alcohol is excluded.",
        "Is damage covered if the driver was drunk?",
        "The insured vehicle is covered against damage caused by floods."
    ]

    embeddings = model.embed_documents(texts)

    print("Number of embeddings:", len(embeddings))
    print("Embedding dimension:", len(embeddings[0]))

    similar_1 = cosine_similarity(
    embeddings[0],
    embeddings[1]
)

    similar_2 = cosine_similarity(
    embeddings[0],
    embeddings[2]
)
    print(
    "Related similarity:",
    similar_1
)

    print(
    "Unrelated similarity:",
    similar_2
)
    query_embedding = model.embed_query(
    "Can I claim if the driver had consumed alcohol?"
)

    print(
    "Query embedding dimension:",
    len(query_embedding)
)
