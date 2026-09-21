from typing import TYPE_CHECKING, Any, Dict, List, Optional

from packages.shared.config import settings
from services.orchestrator.eligibility.rule_engine import rank_schemes_for_user
from .retriever import search_schemes, format_context_for_llm
from .prompts import get_system_prompt

if TYPE_CHECKING:
    from langchain_groq import ChatGroq


def get_llm() -> "ChatGroq":
    """
    Returns an instance of ChatGroq using configured API key and model name.
    """
    from langchain_groq import ChatGroq

    # ASSUMPTION: Using Groq LLM through ChatGroq integration from langchain_groq.
    # Model used is llama-3.3-70b-specdec as specified or via env.
    return ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL_NAME,
        temperature=0.2
    )


def _serialize_scheme(scheme: Any) -> Dict[str, Any]:
    return {
        "id": str(scheme.id),
        "scheme_name": scheme.scheme_name,
        "slug": scheme.slug,
        "details": scheme.details,
        "benefits": scheme.benefits,
        "eligibility": scheme.eligibility,
        "application_process": scheme.application_process,
        "documents_required": scheme.documents_required,
        "level": scheme.level,
        "scheme_category": scheme.scheme_category,
        "tags": scheme.tags,
    }


def _truncate(text: Optional[str], limit: int = 220) -> str:
    if not text:
        return "Details are not available in the local dataset."
    clean_text = " ".join(text.split())
    if len(clean_text) <= limit:
        return clean_text
    return f"{clean_text[: limit - 3].rstrip()}..."


def _fallback_intro(language: str) -> str:
    prompts = {
        "en": "Here are the closest scheme matches from the current local dataset.",
        "hi": "Maujooda local dataset ke aadhar par yeh sabse kareeb yojana milan hain.",
        "bn": "বর্তমান লোকাল ডেটাসেট অনুযায়ী এগুলো সবচেয়ে কাছের স্কিম মিল।",
    }
    return prompts.get(language, prompts["en"])


def _fallback_footer(language: str) -> str:
    prompts = {
        "en": "ASSUMPTION: This answer is based on the current local dataset in the repository and still needs source verification before production use.",
        "hi": "ASSUMPTION: Yeh jawab repository ke local dataset par aadharit hai aur production se pehle source verification zaroori hai.",
        "bn": "ASSUMPTION: এই উত্তরটি রিপোজিটরির লোকাল ডেটাসেটের উপর ভিত্তি করে তৈরি, প্রোডাকশনের আগে উৎস যাচাই দরকার।",
    }
    return prompts.get(language, prompts["en"])


def build_fallback_response(
    query: str,
    schemes_with_scores: List[Dict[str, Any]],
    language: str,
    user_profile: Optional[Dict[str, Any]] = None,
) -> str:
    if not schemes_with_scores:
        empty_messages = {
            "en": "I could not find a matching scheme in the current local dataset. Please try a more specific query or provide a verified scheme source.",
            "hi": "Mujhe current local dataset mein matching yojana nahi mili. Kripya zyada specific query dein ya verified scheme source share karein.",
            "bn": "বর্তমান লোকাল ডেটাসেটে মেলানো কোনো স্কিম পাইনি। অনুগ্রহ করে আরও নির্দিষ্ট প্রশ্ন করুন বা যাচাইকৃত স্কিম উৎস দিন।",
        }
        return empty_messages.get(language, empty_messages["en"])

    ranked_results = {}
    if user_profile:
        ranked = rank_schemes_for_user(
            user_profile,
            [_serialize_scheme(item["scheme"]) for item in schemes_with_scores],
        )
        ranked_results = {result.scheme_id: result for result in ranked}

    lines = [_fallback_intro(language)]
    for index, item in enumerate(schemes_with_scores, start=1):
        scheme = item["scheme"]
        lines.append(
            f"{index}. {scheme.scheme_name} [{scheme.level or 'Unknown level'} | relevance {item['relevance_score']:.2f}]"
        )
        lines.append(f"   Benefits: {_truncate(scheme.benefits)}")
        lines.append(f"   Eligibility: {_truncate(scheme.eligibility)}")
        lines.append(f"   Application: {_truncate(scheme.application_process)}")

        result = ranked_results.get(str(scheme.id))
        if result:
            lines.append(
                f"   Eligibility check: {result.explanation} Match score {result.match_score:.2f}."
            )

    lines.append(_fallback_footer(language))
    return "\n".join(lines)

def generate_response(
    query: str,
    language: str = "en",
    user_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate multilingual eligibility responses using RAG from local database schemes.
    """
    try:
        schemes_with_scores = search_schemes(query, top_k=3)
    except ModuleNotFoundError:
        return {
            "response": (
                "The retrieval stack is not installed yet. "
                "Run `python -m pip install -r requirements.txt` and bootstrap the dataset before using chat search."
            ),
            "language": language,
            "schemes_referenced": [],
        }
    
    # 2. Format context
    context = format_context_for_llm(schemes_with_scores)
    
    # 3. Formulate user profile context if available
    profile_str = "None"
    if user_profile:
        profile_str = (
            f"Age: {user_profile.get('age', 'N/A')}, "
            f"Income: {user_profile.get('income_bracket', 'N/A')}, "
            f"Category: {user_profile.get('category', 'N/A')}, "
            f"Occupation: {user_profile.get('occupation', 'N/A')}, "
            f"State: {user_profile.get('location_state', 'N/A')}, "
            f"District: {user_profile.get('location_district', 'N/A')}, "
            f"Education: {user_profile.get('education_level', 'N/A')}"
        )
        
    # 4. Get Prompt Template
    system_prompt = get_system_prompt(language)
    
    ai_text = build_fallback_response(
        query=query,
        schemes_with_scores=schemes_with_scores,
        language=language,
        user_profile=user_profile,
    )

    if settings.GROQ_API_KEY:
        try:
            from langchain_core.prompts import ChatPromptTemplate

            llm = get_llm()
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{query}")
            ])

            chain = prompt | llm
            response = chain.invoke({
                "context": context,
                "user_profile": profile_str,
                "query": query
            })
            ai_text = response.content
        except (ImportError, RuntimeError):
            pass
        
    # Format schemes referenced for output
    schemes_referenced = []
    for item in schemes_with_scores:
        scheme = item["scheme"]
        schemes_referenced.append(scheme)
        
    return {
        "response": ai_text,
        "language": language,
        "schemes_referenced": schemes_referenced
    }
