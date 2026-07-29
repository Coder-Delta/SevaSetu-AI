from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from data.relational_db.database import get_db
from data.relational_db.models.conversation import Conversation
from data.relational_db.models.user import User
from packages.shared.auth import get_current_user
from packages.shared.schemas import ChatRequest, ChatResponse
from services.api_gateway.routes.common import build_user_profile_dict

router = APIRouter(prefix="/chat", tags=["chat"])


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    session_language: str
    messages: list[dict]

    model_config = ConfigDict(from_attributes=True)


@router.post("/", response_model=ChatResponse)
def chat_with_assistant(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    from services.orchestrator.rag.chain import generate_response

    conversation = None
    if payload.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == payload.conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found.",
            )
    else:
        conversation = Conversation(
            user_id=current_user.id,
            session_language=payload.language,
            messages=[],
        )
        db.add(conversation)
        db.flush()

    user_message = {
        "role": "user",
        "content": payload.message,
        "language": payload.language,
        "timestamp": datetime.utcnow().isoformat(),
    }
    conversation.messages = [*conversation.messages, user_message]

    generated = generate_response(
        query=payload.message,
        language=payload.language,
        user_profile=build_user_profile_dict(current_user),
    )
    assistant_message = {
        "role": "assistant",
        "content": generated["response"],
        "language": generated["language"],
        "timestamp": datetime.utcnow().isoformat(),
    }
    conversation.messages = [*conversation.messages, assistant_message]

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return ChatResponse(
        response=generated["response"],
        language=generated["language"],
        conversation_id=conversation.id,
        schemes_referenced=generated["schemes_referenced"],
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Conversation:
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )
    return conversation
