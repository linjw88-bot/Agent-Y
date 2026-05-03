"""
知识库管理器
负责知识检索和相关性排序
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class KnowledgeBase:
    """知识库管理器"""

    def __init__(self):
        pass

    async def retrieve(
        self,
        query: str,
        industry_id: int,
        db: AsyncSession,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        从知识库中检索相关内容
        """
        from app.models.models import KnowledgeEntry

        search_terms = self._extract_keywords(query)

        stmt = select(KnowledgeEntry).where(KnowledgeEntry.industry_id == industry_id)
        result = await db.execute(stmt)
        all_entries = result.scalars().all()

        scored_entries = []
        for entry in all_entries:
            score = self._calculate_relevance(query, entry, search_terms)
            scored_entries.append({
                "id": entry.id,
                "title": entry.title,
                "summary": getattr(entry, 'summary', None) or (entry.content[:120] + "…" if entry.content and len(entry.content) > 120 else entry.content or ""),
                "content": getattr(entry, 'detail_content', None) or entry.content or "",
                "category": entry.category,
                "tags": entry.tags or [],
                "source": entry.source,
                "relevance_score": score
            })

        scored_entries.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_entries[:limit]

    def _extract_keywords(self, query: str) -> List[str]:
        import re as _re

        stopwords = {
            '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都',
            '一', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着',
            '看', '好', '这', '吗', '什', '怎', '哪', '个', '能', '以', '吧',
            '什么', '怎么', '一个', '没有'
        }

        words = []

        segments = _re.split(r'[,，、；。？！\n]+', query)
        all_chinese = ''.join(
            _re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', seg)
            for seg in segments
        )
        english_parts = _re.findall(r'[a-zA-Z]+', query)
        words.extend([w.lower() for w in english_parts if len(w) >= 2])

        if not all_chinese:
            return list(dict.fromkeys(words))[:25]

        seen_2 = set()
        for i in range(len(all_chinese) - 1):
            word = all_chinese[i:i+2]
            if word[0].isascii() and word[1].isascii():
                continue
            if word not in stopwords and word not in seen_2:
                words.append(word)
                seen_2.add(word)

        seen_3plus = set()
        for n in [3, 4]:
            for i in range(len(all_chinese) - n + 1):
                word = all_chinese[i:i+n]
                if word not in stopwords and word not in seen_3plus and word not in seen_2:
                    words.append(word)
                    seen_3plus.add(word)

        return list(dict.fromkeys(words))[:25]

    def _calculate_relevance(
        self,
        query: str,
        entry,
        search_terms: List[str]
    ) -> float:
        score = 0.0

        query_lower = query.lower()
        title_lower = entry.title.lower() if entry.title else ""
        content_lower = entry.content.lower() if entry.content else ""
        summary_lower = (getattr(entry, 'summary', None) or '').lower()
        detail_lower = (getattr(entry, 'detail_content', None) or '').lower()

        title_matches = sum(1 for term in search_terms if len(term) >= 2 and term.lower() in title_lower)
        score += title_matches * 0.35

        tag_match_count = 0
        total_tags = len(entry.tags) if entry.tags else 0
        if entry.tags:
            for tag in entry.tags:
                for term in search_terms:
                    if len(term) >= 2 and term.lower() in tag.lower():
                        tag_match_count += 1
        if total_tags > 0:
            tag_precision = tag_match_count / total_tags
            score += tag_precision * 0.30

        summary_matches = sum(1 for term in search_terms if len(term) >= 2 and term.lower() in summary_lower)
        detail_matches = sum(1 for term in search_terms if len(term) >= 2 and term.lower() in detail_lower)
        score += summary_matches * 0.12
        score += detail_matches * 0.08

        if any(word in query_lower for word in ['应该', '如何', '怎么', '能否', '是否', '适合', '可以']):
            if entry.category == 'methodology':
                score += 0.08
        if any(word in query_lower for word in ['案例', '例子', '曾经']):
            if entry.category == 'case':
                score += 0.08

        if title_matches == 0 and tag_match_count == 0:
            score = 0.05

        if score == 0 and ((summary_matches + detail_matches) > 0 or len(search_terms) >= 2):
            score = 0.10

        return min(score, 1.0)