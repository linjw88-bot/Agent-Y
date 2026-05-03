from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class ConsultationRequest(BaseModel):
    query: str = Field(..., description="用户的决策问题或咨询内容")
    session_id: str = Field(..., description="会话ID，用于追踪对话历史")
    context: Optional[Dict[str, Any]] = Field(default=None, description="额外上下文信息")


class RequiredInfoRequest(BaseModel):
    conversation_id: int = Field(..., description="对话ID")
    answers: Dict[str, str] = Field(..., description="用户提供的补充信息")


class IndustryBase(BaseModel):
    name: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = None


class IndustryCreate(IndustryBase):
    pass


class IndustryResponse(IndustryBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class KnowledgeEntryBase(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    summary: Optional[str] = None
    detail_content: Optional[str] = None


class KnowledgeEntryCreate(KnowledgeEntryBase):
    industry_id: int


class KnowledgeEntryResponse(KnowledgeEntryBase):
    id: int
    industry_id: int
    relevance_score: float = 0.5
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisMethodBase(BaseModel):
    name: str
    description: Optional[str] = None
    steps: Optional[List[str]] = None
    when_to_use: Optional[str] = None


class AnalysisMethodCreate(AnalysisMethodBase):
    industry_id: int


class AnalysisMethodResponse(AnalysisMethodBase):
    id: int
    industry_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LeadingIndicator(BaseModel):
    name: str
    description: str
    threshold: Optional[str] = None


class ContingencyTrigger(BaseModel):
    condition: str
    action: str
    priority: str = "medium"


class AnalysisResultResponse(BaseModel):
    id: Optional[int] = Field(default=None)
    conversation_id: int
    status: str = Field(default="done")
    industry_name: str = Field(default="")
    confidence: float = Field(default=0.5)
    present_situation: str = Field(default="")
    transformation: str = Field(default="")
    future_possibility: str = Field(default="")
    probability_distribution: Dict[str, float] = Field(default_factory=dict)
    recommended_action: str = Field(default="")
    leading_indicators: List[LeadingIndicator] = Field(default_factory=list)
    contingency_triggers: List[ContingencyTrigger] = Field(default_factory=list)
    knowledge_context: List[Dict[str, Any]] = Field(default_factory=list)
    llm_analysis: str = Field(default="")
    llm_available: bool = Field(default=False)
    depth_analysis: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    conversation_id: int
    session_id: str
    identified_industry: Optional[IndustryResponse] = None
    required_info: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0, le=1)
    can_proceed: bool = Field(...)

    model_config = ConfigDict(from_attributes=True)


ConsultationResponse = ConversationResponse


class FeedbackCreate(BaseModel):
    analysis_result_id: int
    is_helpful: Optional[bool] = None
    actual_outcome: Optional[str] = None
    notes: Optional[str] = None


class FeedbackResponse(FeedbackCreate):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None