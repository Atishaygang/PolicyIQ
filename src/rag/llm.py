from langchain_huggingface import HuggingFaceEndpoint , ChatHuggingFace
from dotenv import load_dotenv
load_dotenv()
import os

def get_llm():
    llm = HuggingFaceEndpoint(
    repo_id='openai/gpt-oss-120b',
    task='text-generation',
    huggingfacehub_api_token= os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN"),
    temperature= 0,
    max_new_tokens= 5000
    )
    chat_model = ChatHuggingFace(
    llm = llm
    )
    return chat_model
    

 