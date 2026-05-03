"""
咨询 API 路由
"""
import asyncio
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.agent import AgentY
from app.models.models import Conversation, Industry, AnalysisResult
from app.schemas.schemas import (
    ConsultationRequest,
    ConsultationResponse,
    RequiredInfoRequest,
    AnalysisResultResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

agent = AgentY()

_task_store: Dict[int, Dict[str, Any]] = {}


async def _run_full_analysis(conversation_id: int, db: AsyncSession) -> None:
    try:
        conv_result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            _task_store[conversation_id] = {"status": "error", "error": "对话不存在"}
            return

        # Get industry name from conversation
        industry_name = "待确认"
        if conversation.identified_industry_id:
            ind_result = await db.execute(
                select(Industry).where(Industry.id == conversation.identified_industry_id)
            )
            industry = ind_result.scalar_one_or_none()
            if industry:
                industry_name = industry.name

        full_analysis = await agent.full_analysis(
            query=conversation.user_query,
            answers=conversation.user_answers or {},
            industry_id=conversation.identified_industry_id,
            industry_name=industry_name,
            db=db
        )

        new_result = AnalysisResult(
            conversation_id=conversation_id,
            industry_name=full_analysis.get("industry_name", ""),
            confidence=full_analysis.get("confidence", 0.5),
            present_situation=full_analysis.get("present_situation", ""),
            transformation=full_analysis.get("transformation", ""),
            future_possibility=full_analysis.get("future_possibility", ""),
            probability_distribution=full_analysis.get("probability_distribution", {}),
            recommended_action=full_analysis.get("recommended_action", ""),
            leading_indicators=full_analysis.get("leading_indicators", []),
            contingency_triggers=full_analysis.get("contingency_triggers", []),
            llm_analysis=full_analysis.get("llm_analysis", ""),
            knowledge_context=full_analysis.get("knowledge_context", []),
            depth_analysis=full_analysis.get("depth_analysis", {}),
        )
        db.add(new_result)
        await db.commit()
        await db.refresh(new_result)

        _task_store[conversation_id] = {
            "status": "done",
            "result": full_analysis,
            "result_id": new_result.id,
        }
        logger.info(f"[Job {conversation_id}] Analysis completed successfully.")

    except Exception as e:
        logger.error(f"[Job {conversation_id}] Analysis failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        _task_store[conversation_id] = {"status": "error", "error": str(e)}


@router.post("/consultation", response_model=ConsultationResponse)
async def submit_consultation(
    request: ConsultationRequest,
    db: AsyncSession = Depends(get_db)
):
    analysis = await agent.analyze_query(request.query, db)

    conversation = Conversation(
        session_id=request.session_id,
        user_query=request.query,
        identified_industry_id=analysis.get("industry_id"),
        required_info=analysis.get("required_info", []),
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    industry_response = None
    if analysis.get("industry_id"):
        result = await db.execute(
            select(Industry).where(Industry.id == analysis["industry_id"])
        )
        industry = result.scalar_one_or_none()
        if industry:
            industry_response = {
                "id": industry.id,
                "name": industry.name,
                "description": industry.description,
                "keywords": industry.keywords,
            }

    if analysis.get("can_proceed"):
        conversation.user_answers = {}
        await db.commit()
        _task_store[conversation.id] = {"status": "pending", "result": None, "error": None}
        asyncio.create_task(_run_full_analysis(conversation.id, db))
        logger.info(f"[Job {conversation.id}] Analysis task queued (can_proceed=True).")

    return ConsultationResponse(
        conversation_id=conversation.id,
        session_id=request.session_id,
        identified_industry=industry_response,
        required_info=analysis.get("required_info", []),
        confidence=analysis.get("confidence", 0.5),
        can_proceed=analysis.get("can_proceed", False),
    )


@router.post("/consultation/info")
async def submit_required_info(
    request: RequiredInfoRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Conversation).where(Conversation.id == request.conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    conversation.user_answers = request.answers
    await db.commit()

    _task_store[request.conversation_id] = {"status": "pending", "result": None, "error": None}
    asyncio.create_task(_run_full_analysis(request.conversation_id, db))
    logger.info(f"[Job {request.conversation_id}] Analysis task queued (after info submitted).")

    return {
        "message": "信息已提交，分析任务已启动",
        "conversation_id": request.conversation_id
    }


@router.get("/consultation/{conversation_id}/result")
async def get_analysis_result(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    job = _task_store.get(conversation_id)

    if job and job["status"] == "pending":
        return AnalysisResultResponse(
            conversation_id=conversation_id,
            status="pending"
        )

    if job and job["status"] == "error":
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {job.get('error', '未知错误')}"
        )

    if job and job["status"] == "done":
        full_analysis = job["result"]
        return AnalysisResultResponse(
            id=job.get("result_id"),
            conversation_id=conversation_id,
            status="done",
            industry_name=full_analysis.get("industry_name", ""),
            confidence=full_analysis.get("confidence", 0.5),
            present_situation=full_analysis.get("present_situation", ""),
            transformation=full_analysis.get("transformation", ""),
            future_possibility=full_analysis.get("future_possibility", ""),
            probability_distribution=full_analysis.get("probability_distribution", {}),
            recommended_action=full_analysis.get("recommended_action", ""),
            leading_indicators=full_analysis.get("leading_indicators", []),
            contingency_triggers=full_analysis.get("contingency_triggers", []),
            knowledge_context=full_analysis.get("knowledge_context", []),
            llm_analysis=full_analysis.get("llm_analysis", ""),
            llm_available=full_analysis.get("llm_available", False),
            depth_analysis=full_analysis.get("depth_analysis", {}),
        )

    db_result = await db.execute(
        select(AnalysisResult).where(
            AnalysisResult.conversation_id == conversation_id
        ).order_by(AnalysisResult.created_at.desc()).limit(1)
    )
    analysis_result = db_result.scalar_one_or_none()

    if analysis_result:
        return AnalysisResultResponse(
            id=analysis_result.id,
            conversation_id=conversation_id,
            status="done",
            industry_name=analysis_result.industry_name or "",
            confidence=analysis_result.confidence or 0.5,
            present_situation=analysis_result.present_situation or "",
            transformation=analysis_result.transformation or "",
            future_possibility=analysis_result.future_possibility or "",
            probability_distribution=analysis_result.probability_distribution or {},
            recommended_action=analysis_result.recommended_action or "",
            leading_indicators=analysis_result.leading_indicators or [],
            contingency_triggers=analysis_result.contingency_triggers or [],
            llm_analysis=analysis_result.llm_analysis or "",
            llm_available=bool(analysis_result.llm_analysis),
            knowledge_context=analysis_result.knowledge_context or [],
            depth_analysis=analysis_result.depth_analysis or {},
        )

    raise HTTPException(
        status_code=404,
        detail="分析任务不存在，请先提交咨询"
    )