"""
行业 API 路由
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.models import Industry
from app.schemas.schemas import IndustryResponse

router = APIRouter()


@router.get("/industries", response_model=List[IndustryResponse])
async def list_industries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Industry))
    industries = result.scalars().all()
    return industries


@router.get("/industries/{industry_id}", response_model=IndustryResponse)
async def get_industry(industry_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Industry).where(Industry.id == industry_id))
    industry = result.scalar_one_or_none()
    if not industry:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="行业不存在")
    return industry