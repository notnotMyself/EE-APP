#!/usr/bin/env python3
"""
预下载所有图片到 media_cache 目录。

在本地（能访问外网的机器）运行此脚本，
将图片缓存下载好后部署到服务器，
代理接口检测到缓存文件存在会直接返回，不再请求外网。

用法:
    python3 download_media_cache.py
"""
import json
import hashlib
import io
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx

# 尝试导入 Pillow 用于 AVIF → JPEG 转换
try:
    from PIL import Image
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
        pillow_heif.register_avif_opener()
    except ImportError:
        pass
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️  Pillow 未安装，AVIF 图片不会被转换为 JPEG")

DATA_FILE = Path(__file__).parent / "index.json"
CACHE_DIR = Path(__file__).parent / "media_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def collect_urls(data: dict) -> set:
    """从 index.json 中提取所有媒体和头像 URL"""
    urls = set()
    for post in data.get("posts", {}).values():
        for url in post.get("media_urls", []):
            if url:
                urls.add(url)
        for item in post.get("video_urls", []):
            if isinstance(item, str) and item:
                urls.add(item)
            elif isinstance(item, dict):
                src = item.get("src", "")
                if src:
                    urls.add(src)
        avatar = post.get("avatar_url", "")
        if avatar:
            urls.add(avatar)
    return urls


def cache_path_for(url: str) -> Path:
    """与 design_feed.py 中的缓存逻辑完全一致"""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    parsed = urlparse(url)
    ext = Path(parsed.path).suffix or ".jpg"

    needs_conversion = ext.lower() in [".avif", ".webp"] and PILLOW_AVAILABLE
    cache_ext = ".jpg" if needs_conversion else ext
    return CACHE_DIR / f"{url_hash}{cache_ext}", needs_conversion


def download_and_cache(url: str, client: httpx.Client) -> bool:
    """下载单个 URL 并缓存"""
    cache_file, needs_conversion = cache_path_for(url)

    if cache_file.exists():
        return True  # 已缓存

    try:
        resp = client.get(url)
        resp.raise_for_status()
        image_bytes = resp.content

        if needs_conversion:
            try:
                img = Image.open(io.BytesIO(image_bytes))
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")
                output = io.BytesIO()
                img.save(output, format="JPEG", quality=90)
                image_bytes = output.getvalue()
            except Exception as e:
                print(f"  ⚠️  转换失败 ({e})，保存原始格式")
                # 保存原始格式
                parsed = urlparse(url)
                ext = Path(parsed.path).suffix or ".jpg"
                cache_file = CACHE_DIR / f"{hashlib.md5(url.encode()).hexdigest()}{ext}"

        cache_file.write_bytes(image_bytes)
        return True

    except httpx.HTTPStatusError as e:
        print(f"  ❌ HTTP {e.response.status_code}")
        return False
    except Exception as e:
        print(f"  ❌ {e}")
        return False


def main():
    if not DATA_FILE.exists():
        print(f"❌ 数据文件不存在: {DATA_FILE}")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    urls = collect_urls(data)
    print(f"📊 共发现 {len(urls)} 个媒体 URL")

    success = 0
    failed = 0

    with httpx.Client(
        timeout=httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0),
        follow_redirects=True,
    ) as client:
        for i, url in enumerate(sorted(urls), 1):
            short = url.split("/")[-1][:40]
            print(f"[{i}/{len(urls)}] {short}...", end=" ", flush=True)

            if download_and_cache(url, client):
                success += 1
                print("✅")
            else:
                failed += 1

    print(f"\n📦 完成! 成功: {success}, 失败: {failed}")
    print(f"📁 缓存目录: {CACHE_DIR}")
    print(f"💡 将 media_cache/ 部署到服务器同路径即可")


if __name__ == "__main__":
    main()
