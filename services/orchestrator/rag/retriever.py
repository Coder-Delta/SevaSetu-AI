from typing import List, Dict, Any, Optional
from data.vector_db.config import get_or_create_collection
from data.relational_db.database import SessionLocal
from data.relational_db.models.scheme import Scheme
from uuid import UUID

def search_schemes(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search schemes in ChromaDB vector store and hydrate them using PostgreSQL details.
    Returns:
        List of Dict containing scheme model details and the relevance score.
    """
    collection = get_or_create_collection()
    
    # Query vector store
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    hydrated_results = []
    
    if not results or not results['ids'] or len(results['ids'][0]) == 0:
        return hydrated_results

    db = SessionLocal()
    try:
        # results['ids'][0] contains the scheme IDs (as string)
        # results['distances'][0] contains the distance (lower = more relevant)
        ids = results['ids'][0]
        distances = results['distances'][0]
        
        for scheme_id_str, distance in zip(ids, distances):
            try:
                scheme_id = UUID(scheme_id_str)
            except ValueError:
                continue
                
            scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
            if scheme:
                # Calculate simple similarity score from distance
                # ChromaDB cosine distance range is 0 to 2 (0 is identical)
                score = max(0.0, 1.0 - (distance / 2.0))
                hydrated_results.append({
                    "scheme": scheme,
                    "relevance_score": score
                })
    finally:
        db.close()
        
    return hydrated_results

def format_context_for_llm(schemes_with_scores: List[Dict[str, Any]]) -> str:
    """
    Format scheme list into markdown context block for LLM prompts.
    """
    context_blocks = []
    for idx, item in enumerate(schemes_with_scores, 1):
        scheme = item["scheme"]
        block = (
            f"Scheme {idx}: {scheme.scheme_name}\n"
            f"Slug: {scheme.slug}\n"
            f"Details: {scheme.details}\n"
            f"Benefits: {scheme.benefits}\n"
            f"Eligibility: {scheme.eligibility}\n"
            f"Required Documents: {scheme.documents_required}\n"
            f"How to Apply: {scheme.application_process}\n"
            f"Level: {scheme.level}\n"
            f"Category: {scheme.scheme_category}\n"
            f"Tags: {scheme.tags}\n"
            f"----------------------------------------"
        )
        context_blocks.append(block)
        
    return "\n\n".join(context_blocks)
