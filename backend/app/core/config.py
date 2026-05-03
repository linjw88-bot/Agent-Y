"""
配置管理
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Agent YJ V2"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api/v1"

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./yj_decision.db"

    # MiniMax API (可选)
    MINIMAX_API_KEY: str = ""
    MINIMAX_BASE_URL: str = "https://api.minimax.chat"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()