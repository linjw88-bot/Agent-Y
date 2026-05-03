"""
知识库 API 路由
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.models import KnowledgeEntry
from app.schemas.schemas import KnowledgeEntryResponse

router = APIRouter()


@router.get("/knowledge", response_model=List[KnowledgeEntryResponse])
async def list_knowledge(
    industry_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    if industry_id:
        result = await db.execute(
            select(KnowledgeEntry).where(KnowledgeEntry.industry_id == industry_id)
        )
    else:
        result = await db.execute(select(KnowledgeEntry))
    entries = result.scalars().all()
    return entries


@router.get("/knowledge/{knowledge_id}", response_model=KnowledgeEntryResponse)
async def get_knowledge(knowledge_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(KnowledgeEntry).where(KnowledgeEntry.id == knowledge_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="知识条目不存在")
    return entry