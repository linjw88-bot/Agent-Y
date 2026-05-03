"""
反馈 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.models import Feedback, AnalysisResult
from app.schemas.schemas import FeedbackCreate, FeedbackResponse

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def create_feedback(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.id == feedback.analysis_result_id)
    )
    analysis_result = result.scalar_one_or_none()
    if not analysis_result:
        raise HTTPException(status_code=404, detail="分析结果不存在")

    db_feedback = Feedback(
        analysis_result_id=feedback.analysis_result_id,
        is_helpful=1 if feedback.is_helpful else (0 if feedback.is_helpful is False else None),
        actual_outcome=feedback.actual_outcome,
        notes=feedback.notes,
    )
    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)
    return db_feedback


@router.get("/feedback/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(feedback_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
    feedback = result.scalar_one_or_none()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    return feedback