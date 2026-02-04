"""
Design Feed API
提供设计内容展示功能
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
from typing import List, Dict, Any

router = APIRouter(prefix="/api/v1/design-feed", tags=["design"])

# 数据文件路径
DATA_FILE = Path(__file__).parent.parent.parent / "agents/design_validator/data/bestdesignsonx/index.json"


@router.get("", summary="获取设计帖子列表")
async def get_design_posts(limit: int = 20) -> Dict[str, Any]:
    """
    获取设计帖子列表

    Args:
        limit: 返回的帖子数量，默认 20

    Returns:
        包含帖子列表和总数的字典
    """
    try:
        # 读取数据文件
        if not DATA_FILE.exists():
            raise HTTPException(
                status_code=500,
                detail=f"数据文件不存在: {DATA_FILE}"
            )

        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取所有帖子
        posts = list(data.get("posts", {}).values())

        # 只返回有图片的帖子
        posts_with_media = [p for p in posts if p.get('media_urls')]

        # 按时间倒序排列
        posts_with_media.sort(
            key=lambda x: x.get('fetched_at', ''),
            reverse=True
        )

        # 限制返回数量
        limited_posts = posts_with_media[:limit]

        return {
            "success": True,
            "posts": limited_posts,
            "total": len(posts_with_media),
            "returned": len(limited_posts)
        }

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"数据文件格式错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取设计帖子失败: {str(e)}"
        )


@router.get("/stats", summary="获取设计内容统计")
async def get_design_stats() -> Dict[str, Any]:
    """
    获取设计内容统计信息

    Returns:
        统计信息字典
    """
    try:
        if not DATA_FILE.exists():
            raise HTTPException(
                status_code=500,
                detail=f"数据文件不存在: {DATA_FILE}"
            )

        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        posts = list(data.get("posts", {}).values())

        # 统计信息
        total_posts = len(posts)
        posts_with_media = len([p for p in posts if p.get('media_urls')])
        posts_with_video = len([p for p in posts if p.get('video_urls')])

        # 作者统计
        authors = {}
        for post in posts:
            author = post.get('author', 'Unknown')
            authors[author] = authors.get(author, 0) + 1

        return {
            "success": True,
            "total_posts": total_posts,
            "posts_with_media": posts_with_media,
            "posts_with_video": posts_with_video,
            "total_authors": len(authors),
            "top_authors": sorted(
                authors.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "last_updated": data.get("crawl_time", "")
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
        )
