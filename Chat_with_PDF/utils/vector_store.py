from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

def create_vector_store(chunks):
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    # Use HF embedding wrapper directly
    embedding_function = HuggingFaceEmbeddings(model_name=model_name)

    # chunks are strings, not Documents
    texts = chunks

    # Build FAISS vector store
    vector_store = FAISS.from_texts(texts=texts, embedding=embedding_function)
    return vector_store
