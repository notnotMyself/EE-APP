#!/usr/bin/env python3
"""
Chris 设计资讯爬虫 - Best Designs on X

爬取 bestdesignsonx.com 上精选的 X (Twitter) 设计帖子
通过点击卡片获取完整帖子内容（作者、文字、媒体）

依赖安装：
    pip install playwright
    playwright install chromium
"""

import argparse
import asyncio
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# 路径配置
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data" / "bestdesignsonx"
REPORTS_DIR = SCRIPT_DIR / "reports"
INDEX_FILE = DATA_DIR / "index.json"

# 配置
BASE_URL = "https://bestdesignsonx.com/"


def get_post_hash(text: str) -> str:
    """生成内容的短哈希值"""
    return hashlib.md5(text.encode()).hexdigest()[:12]


def load_index() -> dict:
    """加载帖子索引"""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_updated": None,
        "source": "bestdesignsonx.com",
        "posts": {}
    }


def save_index(index: dict):
    """保存帖子索引"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    index["last_updated"] = datetime.now().isoformat()
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


async def fetch_posts_playwright(max_posts: int = 20) -> list[dict]:
    """
    使用 Playwright 爬取 bestdesignsonx.com 的设计帖子
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ 未安装 Playwright，请运行: pip install playwright && playwright install chromium", file=sys.stderr)
        return []
    
    print(f"📡 正在获取 bestdesignsonx.com 的设计帖子...")
    
    posts = []
    seen_urls = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        try:
            await page.goto(BASE_URL, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(6000)
            
            # 滚动加载更多
            for _ in range(2):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(1500)
            await page.evaluate('window.scrollTo(0, 0)')
            await page.wait_for_timeout(1000)
            
            # 查找媒体图片卡片
            imgs = await page.query_selector_all('img[src*="cdn.bestdesignsonx.com/media"]')
            print(f"   找到 {len(imgs)} 个设计卡片")
            
            # 遍历卡片
            for i, img in enumerate(imgs):
                if len(posts) >= max_posts:
                    break
                
                try:
                    # 滚动到图片位置
                    await img.scroll_into_view_if_needed()
                    await page.wait_for_timeout(300)
                    
                    # 点击打开弹窗
                    await img.click()
                    await page.wait_for_timeout(1500)
                    
                    # 提取弹窗内容
                    post_data = await page.evaluate('''() => {
                        // 查找弹窗容器
                        const modals = document.querySelectorAll('[class*="bg-background"]');
                        for (const modal of modals) {
                            if (!modal.innerText.includes('View on X')) continue;
                            
                            // 提取作者（font-semibold）
                            const authorEl = modal.querySelector('.font-semibold');
                            const author = authorEl ? authorEl.innerText.trim() : '';
                            
                            // 提取用户名（text-gray-500 包含@）
                            const usernameEls = modal.querySelectorAll('.text-gray-500, [class*="gray"]');
                            let username = '';
                            for (const el of usernameEls) {
                                const text = el.innerText.trim();
                                if (text.startsWith('@')) {
                                    username = text.substring(1);
                                    break;
                                }
                            }
                            
                            // 提取内容（第二个 text-gray-500，不包含@）
                            let content = '';
                            for (const el of usernameEls) {
                                const text = el.innerText.trim();
                                if (!text.startsWith('@') && text.length > 1) {
                                    content = text;
                                    break;
                                }
                            }
                            
                            // 提取 X 链接
                            const linkEl = modal.querySelector('a[href*="x.com/"][href*="/status/"]');
                            const x_url = linkEl ? linkEl.href : '';
                            
                            // 提取媒体图片
                            const mediaImgs = modal.querySelectorAll('img[src*="cdn.bestdesignsonx.com/media"]');
                            const media_urls = Array.from(mediaImgs).map(img => img.src);
                            
                            // 提取视频
                            const videos = modal.querySelectorAll('video');
                            const video_urls = [];
                            videos.forEach(v => {
                                const src = v.src || v.querySelector('source')?.src;
                                if (src && src.includes('cdn.bestdesignsonx.com')) {
                                    video_urls.push({
                                        src: src,
                                        poster: v.poster || ''
                                    });
                                }
                            });
                            
                            // 提取头像
                            const avatarEl = modal.querySelector('img[src*="twimg.com/profile_images"]');
                            const avatar_url = avatarEl ? avatarEl.src : '';
                            
                            if (x_url) {
                                return {
                                    author: author,
                                    username: username,
                                    content: content,
                                    x_url: x_url,
                                    media_urls: media_urls,
                                    video_urls: video_urls,
                                    avatar_url: avatar_url,
                                    has_video: video_urls.length > 0
                                };
                            }
                        }
                        return null;
                    }''')
                    
                    if post_data and post_data.get('x_url') and post_data['x_url'] not in seen_urls:
                        seen_urls.add(post_data['x_url'])
                        
                        post = {
                            "id": get_post_hash(post_data['x_url']),
                            "author": post_data.get('author', ''),
                            "username": post_data.get('username', ''),
                            "content": post_data.get('content', ''),
                            "x_url": post_data['x_url'],
                            "media_urls": post_data.get('media_urls', []),
                            "video_urls": post_data.get('video_urls', []),
                            "has_video": post_data.get('has_video', False),
                            "avatar_url": post_data.get('avatar_url', ''),
                            "source": "bestdesignsonx",
                            "source_name": "Best Designs on X",
                            "category": "设计灵感",
                            "tags": ["X/Twitter", "设计"],
                            "fetched_at": datetime.now().isoformat()
                        }
                        
                        posts.append(post)
                        media_type = "🎬 视频" if post['has_video'] else f"📷 {len(post['media_urls'])}图"
                        print(f"   [{len(posts)}/{max_posts}] @{post['username']}: {post['content'][:35]}... [{media_type}]")
                    
                    # 关闭弹窗
                    await page.keyboard.press('Escape')
                    await page.wait_for_timeout(500)
                    
                except Exception as e:
                    await page.keyboard.press('Escape')
                    await page.wait_for_timeout(300)
                    continue
            
            print(f"✅ 从 Best Designs on X 获取 {len(posts)} 个设计帖子")
            
        except Exception as e:
            print(f"❌ 爬取失败: {e}", file=sys.stderr)
        
        finally:
            await browser.close()
    
    return posts


def fetch_posts_sync(max_posts: int = 20) -> list[dict]:
    """同步版本"""
    return asyncio.run(fetch_posts_playwright(max_posts))


def generate_briefing(posts: list[dict]) -> dict:
    """生成简报"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not posts:
        return {"error": "No posts found", "should_push": False}
    
    report_date = datetime.now().strftime("%Y-%m-%d")
    
    should_push = len(posts) >= 5
    priority = "P1" if len(posts) >= 10 else "P2"
    
    # 生成标题
    if posts:
        author = posts[0].get("author") or posts[0].get("username", "")
        title = f"X 设计灵感：@{author} 等 {len(posts)} 个精选帖子"
    else:
        title = "本周暂无精选设计帖子"
        should_push = False
    
    # 生成摘要
    summary_parts = []
    for post in posts[:3]:
        content = post.get("content", "")[:30]
        username = post.get("username", "")
        if content:
            summary_parts.append(f"@{username}: {content}")
    summary = " | ".join(summary_parts) if summary_parts else "精选 X 上的设计灵感。"
    
    # 结构化列表
    summary_structured = []
    for idx, post in enumerate(posts[:10], 1):
        summary_structured.append({
            "index": idx,
            "author": post.get("author", ""),
            "username": post.get("username", ""),
            "content": post.get("content", ""),
            "x_url": post.get("x_url", ""),
            "media_urls": post.get("media_urls", [])[:3],
            "avatar_url": post.get("avatar_url", "")
        })
    
    briefing = {
        "briefing_type": "x_design_inspiration",
        "generated_at": datetime.now().isoformat(),
        "date": report_date,
        "should_push": should_push,
        "priority": priority,
        "title": title,
        "summary": summary,
        "summary_structured": summary_structured,
        "cover_style": "social_cards",
        "metrics": {
            "total_posts": len(posts),
            "unique_authors": len(set(p.get("username", "") for p in posts)),
            "with_media": len([p for p in posts if p.get("media_urls")])
        },
        "posts": posts,
        "source": "bestdesignsonx.com"
    }
    
    # 保存
    filename = f"x_design_briefing_{report_date}.json"
    filepath = REPORTS_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(briefing, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 简报已生成: {filepath}")
    return briefing


def print_posts_summary(posts: list[dict]):
    """打印摘要"""
    video_count = len([p for p in posts if p.get('has_video')])
    image_count = len(posts) - video_count
    
    print(f"\n🐦 Best Designs on X ({len(posts)} 个帖子: {image_count} 图片, {video_count} 视频)")
    print("-" * 70)
    
    for i, post in enumerate(posts, 1):
        author = post.get("author", "")
        username = post.get("username", "unknown")
        content = post.get("content", "")[:50]
        media_count = len(post.get("media_urls", []))
        has_video = post.get("has_video", False)
        
        display_name = f"{author} @{username}" if author else f"@{username}"
        print(f"  {i}. {display_name}")
        if content:
            print(f"     └─ {content}...")
        if has_video:
            video_urls = post.get("video_urls", [])
            print(f"     └─ 🎬 视频 ({len(video_urls)} 个)")
        elif media_count:
            print(f"     └─ 📷 {media_count} 张图片")
        print(f"     └─ {post.get('x_url', '')}")
        print()


def main():
    parser = argparse.ArgumentParser(description='Chris 设计资讯爬虫 - Best Designs on X')
    parser.add_argument('--max', type=int, default=20, help='最大帖子数（默认20）')
    parser.add_argument('--briefing', action='store_true', help='生成简报')
    parser.add_argument('--list', action='store_true', help='列出帖子')
    parser.add_argument('--output-json', action='store_true', help='输出JSON')
    
    args = parser.parse_args()
    
    posts = fetch_posts_sync(args.max)
    
    if not posts:
        print("❌ 未获取到帖子", file=sys.stderr)
        sys.exit(1)
    
    # 保存索引
    index = load_index()
    for post in posts:
        index["posts"][post["id"]] = post
    save_index(index)
    
    if args.list:
        print_posts_summary(posts)
        return
    
    if args.briefing:
        briefing = generate_briefing(posts)
        if args.output_json:
            print(json.dumps(briefing, ensure_ascii=False, indent=2))
    else:
        print_posts_summary(posts)
        print(f"\n💡 使用 --briefing 生成简报")


if __name__ == "__main__":
    main()
