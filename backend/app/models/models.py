from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Industry(Base):
    """行业分类"""
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    keywords = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

    knowledge_entries = relationship("KnowledgeEntry", back_populates="industry")
    analysis_methods = relationship("AnalysisMethod", back_populates="industry")


class KnowledgeEntry(Base):
    """知识条目"""
    __tablename__ = "knowledge_entries"

    id = Column(Integer, primary_key=True, index=True)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))
    tags = Column(JSON)
    source = Column(String(255))
    source_url = Column(String(512), nullable=True)
    source_type = Column(String(50), nullable=True)
    relevance_score = Column(Float, default=0.5)
    summary = Column(Text, nullable=True)
    detail_content = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    industry = relationship("Industry", back_populates="knowledge_entries")


class AnalysisMethod(Base):
    """分析方法"""
    __tablename__ = "analysis_methods"

    id = Column(Integer, primary_key=True, index=True)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    steps = Column(JSON)
    when_to_use = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    industry = relationship("Industry", back_populates="analysis_methods")


class Conversation(Base):
    """对话历史"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_query = Column(Text, nullable=False)
    identified_industry_id = Column(Integer, ForeignKey("industries.id"))
    required_info = Column(JSON)
    user_answers = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

    identified_industry = relationship("Industry")
    analysis_results = relationship("AnalysisResult", back_populates="conversation")


class AnalysisResult(Base):
    """分析结果"""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    industry_name = Column(String(100))
    confidence = Column(Float)
    present_situation = Column(Text)
    transformation = Column(Text)
    future_possibility = Column(Text)
    probability_distribution = Column(JSON)
    recommended_action = Column(Text)
    leading_indicators = Column(JSON)
    contingency_triggers = Column(JSON)
    llm_analysis = Column(Text, nullable=True)
    knowledge_context = Column(JSON, nullable=True)
    depth_analysis = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    conversation = relationship("Conversation", back_populates="analysis_results")
    feedback = relationship("Feedback", back_populates="analysis_result")


class Feedback(Base):
    """用户反馈"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    analysis_result_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False)
    is_helpful = Column(Integer)
    actual_outcome = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    analysis_result = relationship("AnalysisResult", back_populates="feedback")