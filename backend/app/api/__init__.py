"""
API module initialization
"""
from app.api.industries import router as industries_router
from app.api.knowledge import router as knowledge_router
from app.api.feedback import router as feedback_router
from app.api.conversations import router as conversations_router

__all__ = [
    "consultation_router",
    "industries_router",
    "knowledge_router",
    "feedback_router",
    "conversations_router",
]