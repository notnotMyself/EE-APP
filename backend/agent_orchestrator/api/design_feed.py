"""
Design Feed API
提供设计内容展示功能
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, Response
from pathlib import Path
import json
import httpx
import hashlib
import io
from typing import List, Dict, Any

router = APIRouter(prefix="/api/v1/design-feed", tags=["design"])

# 图片缓存目录
MEDIA_CACHE_DIR = Path(__file__).parent.parent.parent / "agents/design_validator/data/bestdesignsonx/media_cache"
MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 尝试导入 Pillow 用于图片格式转换
try:
    from PIL import Image
    # 注册 AVIF/HEIF 支持
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
        pillow_heif.register_avif_opener()
    except ImportError:
        pass
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

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


## 图片代理的通用 CORS 响应头
_CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "*",
    "Cache-Control": "public, max-age=86400",
}


@router.get("/media", summary="图片代理")
async def proxy_media(url: str, convert: bool = True):
    """
    图片代理端点，解决 CORS 问题，并可转换 AVIF 为 JPEG

    Args:
        url: 原始图片 URL
        convert: 是否将 AVIF/WebP 转换为 JPEG（默认 True）

    Returns:
        图片内容流
    """
    if not url:
        raise HTTPException(status_code=400, detail="缺少 url 参数")

    # 验证 URL 是否来自允许的域名
    allowed_domains = [
        "cdn.bestdesignsonx.com",
        "pbs.twimg.com",
    ]

    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.netloc not in allowed_domains:
        raise HTTPException(status_code=403, detail=f"不允许的域名: {parsed.netloc}")

    # 生成缓存文件名
    url_hash = hashlib.md5(url.encode()).hexdigest()
    ext = Path(parsed.path).suffix or ".jpg"

    # 判断是否需要转换
    needs_conversion = convert and ext.lower() in [".avif", ".webp"] and PILLOW_AVAILABLE

    # 缓存文件（如果需要转换，保存为 .jpg）
    cache_ext = ".jpg" if needs_conversion else ext
    cache_file = MEDIA_CACHE_DIR / f"{url_hash}{cache_ext}"

    # 检查缓存
    if cache_file.exists():
        content_type = _get_content_type(cache_ext)
        return Response(
            content=cache_file.read_bytes(),
            media_type=content_type,
            headers=_CORS_HEADERS,
        )

    # 从远程获取
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0),
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

            image_bytes = response.content
            content_type = _get_content_type(cache_ext)

            # 如果需要转换 AVIF/WebP 为 JPEG
            if needs_conversion:
                try:
                    img = Image.open(io.BytesIO(image_bytes))
                    # 转换为 RGB（去除透明通道）
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=90)
                    image_bytes = output.getvalue()
                    content_type = "image/jpeg"
                except Exception as e:
                    # 转换失败，返回原始内容
                    print(f"图片转换失败: {e}")
                    content_type = response.headers.get("content-type", _get_content_type(ext))

            # 保存到缓存
            cache_file.write_bytes(image_bytes)

            return Response(
                content=image_bytes,
                media_type=content_type,
                headers=_CORS_HEADERS,
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="获取图片超时，请稍后重试")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"获取图片失败: {str(e)}")


def _get_content_type(ext: str) -> str:
    """根据扩展名获取 Content-Type"""
    content_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".avif": "image/avif",
        ".mp4": "video/mp4",
    }
    return content_types.get(ext.lower(), "application/octet-stream")
