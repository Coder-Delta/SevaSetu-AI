from packages.shared.config import settings
import os

def get_chroma_client():
    import chromadb

    os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
    return chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)

def get_embedding_function():
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    return SentenceTransformerEmbeddingFunction(model_name=settings.EMBEDDING_MODEL)

def get_or_create_collection():
    client = get_chroma_client()
    embedding_function = get_embedding_function()
    collection = client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=embedding_function
    )
    return collection
