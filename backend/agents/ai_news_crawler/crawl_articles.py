#!/usr/bin/env python3
"""
AI资讯追踪官 - 文章爬虫脚本

爬取 bestblogs.dev 的 AI 前沿资讯文章
支持增量更新、格式保留、报告生成
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

# 代理配置（可通过环境变量设置）
HTTP_PROXY = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

# 配置
BASE_URL = "https://www.bestblogs.dev"
ARTICLES_URL = f"{BASE_URL}/articles"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQUEST_DELAY = 1.5  # 请求间隔（秒）

# 路径配置
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
ARTICLES_DIR = DATA_DIR / "articles"
REPORTS_DIR = SCRIPT_DIR / "reports"
INDEX_FILE = DATA_DIR / "index.json"


def get_url_hash(url: str) -> str:
    """生成 URL 的短哈希值"""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def slugify(text: str, max_length: int = 50) -> str:
    """将标题转换为文件名安全的 slug"""
    # 移除特殊字符，保留中文、字母、数字
    text = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', text)
    # 替换空格为连字符
    text = re.sub(r'\s+', '-', text)
    # 截断
    return text[:max_length].strip('-')


def load_index() -> dict:
    """加载文章索引"""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_updated": None,
        "source": "bestblogs.dev",
        "articles": {}
    }


def save_index(index: dict):
    """保存文章索引"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    index["last_updated"] = datetime.now().isoformat()
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def fetch_page(url: str, client: httpx.Client) -> Optional[str]:
    """获取页面 HTML"""
    try:
        response = client.get(url, follow_redirects=True)
        response.raise_for_status()
        return response.text
    except httpx.HTTPError as e:
        print(f"❌ 请求失败: {url} - {e}", file=sys.stderr)
        return None


def parse_article_card(card) -> Optional[dict]:
    """解析文章卡片，提取元数据"""
    try:
        # 查找标题和链接
        title_elem = card.select_one('h2, h3, [class*="title"]')
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        
        # 查找链接
        link_elem = card.select_one('a[href*="/article"]') or card.select_one('a')
        if not link_elem:
            return None
        
        url = link_elem.get('href', '')
        if not url.startswith('http'):
            url = urljoin(BASE_URL, url)
        
        # 提取其他元数据
        article = {
            "title": title,
            "url": url,
            "source": "",
            "date": "",
            "word_count": 0,
            "read_time": "",
            "score": 0,
            "category": "",
            "summary": ""
        }
        
        # 尝试提取来源
        source_elem = card.select_one('[class*="source"], [class*="author"]')
        if source_elem:
            article["source"] = source_elem.get_text(strip=True)
        
        # 尝试提取日期
        date_elem = card.select_one('time, [class*="date"]')
        if date_elem:
            date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
            article["date"] = date_text
        
        # 尝试提取评分
        score_elem = card.select_one('[class*="score"], [class*="rating"]')
        if score_elem:
            score_text = score_elem.get_text(strip=True)
            score_match = re.search(r'\d+', score_text)
            if score_match:
                article["score"] = int(score_match.group())
        
        # 尝试提取摘要
        summary_elem = card.select_one('[class*="summary"], [class*="desc"], p')
        if summary_elem:
            article["summary"] = summary_elem.get_text(strip=True)[:500]
        
        # 尝试提取分类
        category_elem = card.select_one('[class*="category"], [class*="tag"]')
        if category_elem:
            article["category"] = category_elem.get_text(strip=True)
        
        # 尝试提取字数和阅读时间
        text = card.get_text()
        word_match = re.search(r'(\d+)\s*字', text)
        if word_match:
            article["word_count"] = int(word_match.group(1))
        
        time_match = re.search(r'约?\s*(\d+)\s*分钟', text)
        if time_match:
            article["read_time"] = f"约 {time_match.group(1)} 分钟"
        
        return article
        
    except Exception as e:
        print(f"⚠️ 解析文章卡片失败: {e}", file=sys.stderr)
        return None


def fetch_article_list(client: httpx.Client, days: int = 7, category: Optional[str] = None) -> list[dict]:
    """获取文章列表"""
    print(f"📡 正在获取最近 {days} 天的文章列表...")
    
    articles = []
    page = 1
    max_pages = 10  # 限制最大页数
    cutoff_date = datetime.now() - timedelta(days=days)
    
    while page <= max_pages:
        # 构建 URL（根据网站实际 API 调整）
        url = f"{ARTICLES_URL}?page={page}"
        
        html = fetch_page(url, client)
        if not html:
            break
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找文章卡片（根据网站实际结构调整选择器）
        cards = soup.select('article, [class*="article-card"], [class*="post-item"], .card')
        
        if not cards:
            # 尝试其他选择器
            cards = soup.select('div[class*="article"], div[class*="post"], div[class*="item"]')
        
        if not cards:
            print(f"⚠️ 第 {page} 页未找到文章卡片", file=sys.stderr)
            break
        
        found_old = False
        for card in cards:
            article = parse_article_card(card)
            if article:
                # 检查日期是否在范围内
                if article["date"]:
                    try:
                        article_date = datetime.fromisoformat(article["date"].replace('Z', '+00:00'))
                        if article_date.replace(tzinfo=None) < cutoff_date:
                            found_old = True
                            continue
                    except ValueError:
                        pass  # 日期格式不标准，保留文章
                
                # 分类筛选
                if category and article["category"] and category not in article["category"]:
                    continue
                
                articles.append(article)
        
        print(f"  📄 第 {page} 页: 获取 {len(cards)} 篇文章")
        
        if found_old:
            print("  ⏰ 已到达时间范围边界")
            break
        
        # 检查是否有下一页
        next_link = soup.select_one('a[class*="next"], [aria-label="下一页"], .pagination a:last-child')
        if not next_link:
            break
        
        page += 1
        time.sleep(REQUEST_DELAY)
    
    print(f"✅ 共获取 {len(articles)} 篇文章")
    return articles


def html_to_markdown(html_content: str, base_url: str = "") -> str:
    """将 HTML 转换为 Markdown，保留格式"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 移除脚本和样式
    for tag in soup.select('script, style, nav, footer, header, aside'):
        tag.decompose()
    
    lines = []
    
    def process_element(elem, depth=0):
        if isinstance(elem, str):
            text = elem.strip()
            if text:
                lines.append(text)
            return
        
        tag_name = elem.name if hasattr(elem, 'name') else None
        
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            text = elem.get_text(strip=True)
            if text:
                lines.append(f"\n{'#' * level} {text}\n")
        
        elif tag_name == 'p':
            text = elem.get_text(strip=True)
            if text:
                lines.append(f"\n{text}\n")
        
        elif tag_name in ['pre', 'code']:
            code = elem.get_text()
            lang = ''
            if elem.get('class'):
                for cls in elem.get('class', []):
                    if cls.startswith('language-'):
                        lang = cls.replace('language-', '')
                        break
            if tag_name == 'pre' or '\n' in code:
                lines.append(f"\n```{lang}\n{code}\n```\n")
            else:
                lines.append(f"`{code}`")
        
        elif tag_name == 'img':
            src = elem.get('src', '')
            alt = elem.get('alt', '图片')
            if src:
                if not src.startswith('http'):
                    src = urljoin(base_url, src)
                lines.append(f"\n![{alt}]({src})\n")
        
        elif tag_name == 'a':
            href = elem.get('href', '')
            text = elem.get_text(strip=True)
            if href and text:
                if not href.startswith('http'):
                    href = urljoin(base_url, href)
                lines.append(f"[{text}]({href})")
        
        elif tag_name in ['ul', 'ol']:
            lines.append("")
            for i, li in enumerate(elem.find_all('li', recursive=False)):
                prefix = f"{i+1}. " if tag_name == 'ol' else "- "
                text = li.get_text(strip=True)
                if text:
                    lines.append(f"{prefix}{text}")
            lines.append("")
        
        elif tag_name == 'blockquote':
            text = elem.get_text(strip=True)
            if text:
                quoted = '\n'.join(f"> {line}" for line in text.split('\n'))
                lines.append(f"\n{quoted}\n")
        
        elif tag_name in ['strong', 'b']:
            text = elem.get_text(strip=True)
            if text:
                lines.append(f"**{text}**")
        
        elif tag_name in ['em', 'i']:
            text = elem.get_text(strip=True)
            if text:
                lines.append(f"*{text}*")
        
        elif tag_name in ['div', 'section', 'article', 'main']:
            for child in elem.children:
                process_element(child, depth + 1)
        
        elif hasattr(elem, 'children'):
            for child in elem.children:
                process_element(child, depth)
    
    # 查找文章主体
    main_content = soup.select_one('article, main, [class*="content"], [class*="post-body"]')
    if main_content:
        process_element(main_content)
    else:
        process_element(soup.body if soup.body else soup)
    
    # 清理输出
    result = '\n'.join(lines)
    result = re.sub(r'\n{3,}', '\n\n', result)  # 压缩多余空行
    return result.strip()


def fetch_article_detail(url: str, client: httpx.Client) -> Optional[str]:
    """获取文章详情并转换为 Markdown"""
    html = fetch_page(url, client)
    if not html:
        return None
    
    return html_to_markdown(html, url)


def save_article(article: dict, content: str) -> str:
    """保存文章为 Markdown 文件"""
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    date_str = article.get("date", datetime.now().strftime("%Y-%m-%d"))
    if isinstance(date_str, str) and len(date_str) >= 10:
        date_str = date_str[:10]
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    slug = slugify(article["title"])
    url_hash = get_url_hash(article["url"])
    filename = f"{date_str}-{slug}-{url_hash}.md"
    filepath = ARTICLES_DIR / filename
    
    # 构建 frontmatter
    frontmatter = f"""---
title: "{article['title']}"
source: "{article.get('source', '')}"
url: "{article['url']}"
date: "{article.get('date', '')}"
category: "{article.get('category', '')}"
score: {article.get('score', 0)}
word_count: {article.get('word_count', 0)}
crawled_at: "{datetime.now().isoformat()}"
---

"""
    
    full_content = frontmatter + content
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    return f"articles/{filename}"


def generate_weekly_report(index: dict) -> str:
    """生成周报"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    articles = list(index.get("articles", {}).values())
    
    # 按评分排序
    articles_by_score = sorted(articles, key=lambda x: x.get("score", 0), reverse=True)
    
    # 按分类分组
    by_category = {}
    for article in articles:
        cat = article.get("category", "其他") or "其他"
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(article)
    
    # 生成报告
    now = datetime.now()
    week_num = now.isocalendar()[1]
    
    report = f"""# AI资讯周报 - {now.year}年第{week_num}周

> 本周收录 **{len(articles)}** 篇 AI 前沿文章
> 数据来源: bestblogs.dev
> 生成时间: {now.strftime("%Y-%m-%d %H:%M")}

## 🔥 热门文章 TOP 5

"""
    
    for i, article in enumerate(articles_by_score[:5], 1):
        report += f"""{i}. **[{article['title']}]({article['url']})** - {article.get('source', '未知')} | ⭐ {article.get('score', 0)}
   > {article.get('summary', '')[:150]}...

"""
    
    report += "\n## 📂 按分类浏览\n\n"
    
    for cat, cat_articles in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
        report += f"### {cat} ({len(cat_articles)}篇)\n\n"
        for article in cat_articles[:10]:  # 每分类最多显示10篇
            report += f"- [{article['title']}]({article['url']}) - {article.get('source', '')}\n"
        if len(cat_articles) > 10:
            report += f"- *...还有 {len(cat_articles) - 10} 篇*\n"
        report += "\n"
    
    report += """---
*由 AI资讯追踪官 自动生成*
"""
    
    # 保存报告
    filename = f"weekly_{now.strftime('%Y-%m-%d')}.md"
    filepath = REPORTS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 周报已生成: {filepath}")
    return str(filepath)


def main():
    parser = argparse.ArgumentParser(description='AI资讯追踪官 - 文章爬虫')
    parser.add_argument('--days', type=int, default=7, help='获取最近N天的文章（默认7天）')
    parser.add_argument('--category', type=str, help='按分类筛选')
    parser.add_argument('--force', action='store_true', help='强制全量更新，忽略缓存')
    parser.add_argument('--report', choices=['weekly', 'daily'], help='生成报告')
    parser.add_argument('--list-only', action='store_true', help='只获取列表，不抓取详情')
    
    args = parser.parse_args()
    
    # 加载索引
    index = load_index()
    
    # 如果只是生成报告
    if args.report:
        if args.report == 'weekly':
            generate_weekly_report(index)
        return
    
    # 配置代理
    proxy_config = None
    if HTTPS_PROXY or HTTP_PROXY:
        proxy_url = HTTPS_PROXY or HTTP_PROXY
        proxy_config = proxy_url
        print(f"🌐 使用代理: {proxy_url}")
    
    # 创建 HTTP 客户端
    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
        follow_redirects=True,
        proxy=proxy_config
    ) as client:
        
        # 获取文章列表
        articles = fetch_article_list(client, args.days, args.category)
        
        if not articles:
            print("❌ 未获取到任何文章", file=sys.stderr)
            sys.exit(1)
        
        # 筛选新文章
        new_articles = []
        for article in articles:
            url_hash = get_url_hash(article["url"])
            if args.force or url_hash not in index["articles"]:
                new_articles.append(article)
        
        print(f"📊 新文章: {len(new_articles)} / 总计: {len(articles)}")
        
        if args.list_only:
            # 只输出列表
            print("\n📰 文章列表:")
            for article in articles:
                print(f"  - [{article['title']}] {article['url']}")
            return
        
        # 抓取新文章详情
        for i, article in enumerate(new_articles, 1):
            print(f"📥 [{i}/{len(new_articles)}] 正在抓取: {article['title'][:40]}...")
            
            content = fetch_article_detail(article["url"], client)
            if content:
                file_path = save_article(article, content)
                
                # 更新索引
                url_hash = get_url_hash(article["url"])
                index["articles"][url_hash] = {
                    **article,
                    "crawled_at": datetime.now().isoformat(),
                    "file_path": file_path
                }
            
            time.sleep(REQUEST_DELAY)
        
        # 保存索引
        save_index(index)
        
        print(f"\n✅ 完成! 已保存 {len(new_articles)} 篇新文章")
        print(f"📁 文章目录: {ARTICLES_DIR}")
        print(f"📋 索引文件: {INDEX_FILE}")


if __name__ == "__main__":
    main()

