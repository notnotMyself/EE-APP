"""
AI News API
提供 AI 资讯内容，数据来自 AI Art Weekly 和 The Verge AI 等来源
"""
from fastapi import APIRouter
from pathlib import Path
import json
from typing import Dict, Any
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/ai-news", tags=["ai-news"])

# 数据文件路径
DATA_FILE = Path(__file__).parent.parent.parent / "agents/ai_news_crawler/data/ai_news.json"


def _relative_time(published_at: str) -> str:
    """将日期字符串转换为相对时间描述（如 '2h ago', '3d ago'）"""
    try:
        pub = datetime.strptime(published_at, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = now - pub
        hours = int(diff.total_seconds() / 3600)

        if hours < 1:
            return "just now"
        elif hours < 24:
            return f"{hours}h ago"
        elif hours < 48:
            return "yesterday"
        else:
            days = hours // 24
            if days < 7:
                return f"{days}d ago"
            elif days < 30:
                weeks = days // 7
                return f"{weeks}w ago"
            else:
                months = days // 30
                return f"{months}mo ago"
    except (ValueError, TypeError):
        return ""


@router.get("", summary="获取 AI 资讯文章列表")
async def get_ai_news(limit: int = 15, source: str = "") -> Dict[str, Any]:
    """
    获取 AI 资讯文章列表

    Args:
        limit: 返回的文章数量，默认 15
        source: 筛选来源（theverge / aiartweekly），留空返回全部

    Returns:
        文章列表
    """
    try:
        if not DATA_FILE.exists():
            return {"success": True, "articles": [], "total": 0, "returned": 0}

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        articles = data.get("articles", [])

        # 按来源筛选
        if source:
            source_map = {
                "theverge": "The Verge",
                "aiartweekly": "AI Art Weekly",
            }
            source_name = source_map.get(source, source)
            articles = [a for a in articles if a.get("source") == source_name]

        # 按发布日期排序（最新在前）
        articles.sort(key=lambda a: a.get("published_at", ""), reverse=True)

        total = len(articles)
        articles = articles[:limit]

        # 添加相对时间
        for article in articles:
            article["relative_time"] = _relative_time(article.get("published_at", ""))

        return {
            "success": True,
            "articles": articles,
            "total": total,
            "returned": len(articles),
            "sources": data.get("sources", {}),
        }
    except Exception as e:
        return {
            "success": False,
            "articles": [],
            "total": 0,
            "returned": 0,
            "error": str(e),
        }
