from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="""
## Agent Y - 顶级案例决策系统

核心理念：借鉴同领域顶级案例的经验，通过情景推演和概率分析，输出胜率最高的一步。

### 功能
- 领域识别：自动识别问询所属领域
- 知识库检索：从多个领域知识库中获取权威知识
- 情景分析：多情景概率加权分析
- 决策推荐：输出当前胜率最高的行动方案
    """,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.consultation import router as consultation_router
from app.api.industries import router as industries_router
from app.api.knowledge import router as knowledge_router
from app.api.feedback import router as feedback_router
from app.api.conversations import router as conversations_router

app.include_router(consultation_router, prefix=settings.API_PREFIX, tags=["咨询"])
app.include_router(industries_router, prefix=settings.API_PREFIX, tags=["行业"])
app.include_router(knowledge_router, prefix=settings.API_PREFIX, tags=["知识库"])
app.include_router(feedback_router, prefix=settings.API_PREFIX, tags=["反馈"])
app.include_router(conversations_router, prefix=settings.API_PREFIX, tags=["会话历史"])


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api": settings.API_PREFIX
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}