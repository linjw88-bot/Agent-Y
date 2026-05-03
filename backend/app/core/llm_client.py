"""
MiniMax LLM 客户端
"""
from typing import Optional, List, Dict


class MiniMaxClient:
    """MiniMax API 客户端"""

    def __init__(self):
        from app.core.config import settings
        self.api_key = settings.MINIMAX_API_KEY
        self.base_url = settings.MINIMAX_BASE_URL

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        发送聊天请求到 MiniMax API
        """
        import aiohttp

        if not self.api_key:
            return ""

        url = f"{self.base_url}/v1/text/chatcompletion_v2"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        payload = {
            "model": "MiniMax-Text-01",
            "messages": all_messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    else:
                        return ""
        except Exception:
            return ""