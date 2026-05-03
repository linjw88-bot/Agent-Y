"""
会话历史 API 路由
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.models import Conversation

router = APIRouter()


@router.get("/conversations")
async def list_conversations(
    session_id: str = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    if session_id:
        result = await db.execute(
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .order_by(desc(Conversation.created_at))
            .limit(limit)
        )
    else:
        result = await db.execute(
            select(Conversation)
            .order_by(desc(Conversation.created_at))
            .limit(limit)
        )
    conversations = result.scalars().all()
    return [
        {
            "id": c.id,
            "session_id": c.session_id,
            "user_query": c.user_query,
            "identified_industry_id": c.identified_industry_id,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="对话不存在")
    return {
        "id": conversation.id,
        "session_id": conversation.session_id,
        "user_query": conversation.user_query,
        "identified_industry_id": conversation.identified_industry_id,
        "required_info": conversation.required_info,
        "user_answers": conversation.user_answers,
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
    }