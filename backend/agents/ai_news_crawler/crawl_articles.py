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

# 重试配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 5  # 重试间隔（秒）
RETRY_BACKOFF = 2  # 退避因子（每次重试间隔翻倍）

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
    """获取页面 HTML（带重试机制）"""
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.text
        except httpx.TimeoutException as e:
            last_error = e
            delay = RETRY_DELAY * (RETRY_BACKOFF ** attempt)
            print(f"⏳ 请求超时 (尝试 {attempt + 1}/{MAX_RETRIES}): {url}", file=sys.stderr)
            print(f"   {delay}秒后重试...", file=sys.stderr)
            time.sleep(delay)
        except httpx.ConnectError as e:
            last_error = e
            delay = RETRY_DELAY * (RETRY_BACKOFF ** attempt)
            print(f"🔌 连接失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {url}", file=sys.stderr)
            print(f"   {delay}秒后重试...", file=sys.stderr)
            time.sleep(delay)
        except httpx.HTTPStatusError as e:
            # 4xx 错误不重试
            if 400 <= e.response.status_code < 500:
                print(f"❌ 请求失败 (HTTP {e.response.status_code}): {url}", file=sys.stderr)
                return None
            # 5xx 错误重试
            last_error = e
            delay = RETRY_DELAY * (RETRY_BACKOFF ** attempt)
            print(f"⚠️ 服务器错误 (尝试 {attempt + 1}/{MAX_RETRIES}): HTTP {e.response.status_code}", file=sys.stderr)
            print(f"   {delay}秒后重试...", file=sys.stderr)
            time.sleep(delay)
        except httpx.HTTPError as e:
            last_error = e
            delay = RETRY_DELAY * (RETRY_BACKOFF ** attempt)
            print(f"⚠️ 网络错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}", file=sys.stderr)
            print(f"   {delay}秒后重试...", file=sys.stderr)
            time.sleep(delay)

    print(f"❌ 请求失败，已达最大重试次数: {url}", file=sys.stderr)
    print(f"   最后错误: {last_error}", file=sys.stderr)
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
    seen_urls = set()  # 用于去重
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
        
        # 查找文章卡片 - 使用更精确的选择器避免重复
        # bestblogs.dev 的文章卡片通常有特定的结构
        cards = soup.select('article[class*="card"], div[class*="article-card"], div[class*="post-card"]')
        
        if not cards:
            # 尝试其他选择器，但排除嵌套元素
            cards = soup.select('a[href*="/article/"]')
            # 过滤掉嵌套的链接，只保留最外层
            cards = [c for c in cards if not c.find_parent('a')]
        
        if not cards:
            # 最后的备选方案
            cards = soup.select('[class*="article"], [class*="post-item"]')
        
        if not cards:
            print(f"⚠️ 第 {page} 页未找到文章卡片", file=sys.stderr)
            break
        
        found_old = False
        page_articles = 0
        
        for card in cards:
            article = parse_article_card(card)
            if article:
                # 去重检查
                if article["url"] in seen_urls:
                    continue
                seen_urls.add(article["url"])
                
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
                page_articles += 1
        
        print(f"  📄 第 {page} 页: 获取 {page_articles} 篇文章（去重后）")
        
        if found_old:
            print("  ⏰ 已到达时间范围边界")
            break
        
        # 检查是否有下一页
        next_link = soup.select_one('a[class*="next"], [aria-label="下一页"], .pagination a:last-child')
        if not next_link:
            break
        
        page += 1
        time.sleep(REQUEST_DELAY)
    
    print(f"✅ 共获取 {len(articles)} 篇文章（已去重）")
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


def generate_briefing_for_feed(articles: list[dict]) -> dict:
    """
    生成简报格式 - 用于信息流卡片展示
    
    生成的数据结构兼容 Flutter 应用的 Briefing 模型，
    可以直接插入 Supabase 数据库供前端展示。
    
    Returns:
        简报数据，兼容现有卡片系统
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not articles:
        return {
            "error": "No articles found",
            "should_push": False
        }
    
    now = datetime.now()
    report_date = now.strftime("%Y-%m-%d")
    
    # 按评分排序
    articles_sorted = sorted(articles, key=lambda x: x.get("score", 0), reverse=True)
    
    # 按分类分组
    by_category = {}
    for article in articles:
        cat = article.get("category", "AI") or "AI"
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(article)
    
    # 判断是否值得推送
    should_push = False
    priority = "P2"
    
    high_score_count = sum(1 for a in articles if a.get("score", 0) >= 90)
    
    if high_score_count >= 3:
        should_push = True
        priority = "P1"  # 重要
    elif len(articles) >= 5 or high_score_count >= 1:
        should_push = True
        priority = "P2"  # 普通
    
    # 生成标题
    if articles_sorted:
        top_article = articles_sorted[0]
        title_text = top_article["title"]
        
        if len(articles) > 1:
            title = f"📚 今日精选：{title_text[:25]}等{len(articles)}篇"
        else:
            title = f"📖 推荐阅读：{title_text[:30]}"
    else:
        title = "今日暂无新文章推荐"
        should_push = False
    
    # 生成摘要（Markdown 格式，用于卡片内容展示）
    summary_lines = []
    for i, article in enumerate(articles_sorted[:5], 1):
        score = article.get("score", 0)
        source = article.get("source", "")
        summary_lines.append(f"**{i}. [{article['title']}]({article['url']})**")
        if source:
            summary_lines.append(f"   📖 {source} | ⭐ {score}")
        if article.get("summary"):
            summary_lines.append(f"   > {article['summary'][:100]}...")
        summary_lines.append("")
    
    summary = "\n".join(summary_lines)
    
    # 影响说明
    impact = None
    if high_score_count >= 2:
        impact = f"今日有 {high_score_count} 篇高评分文章（≥90分），建议优先阅读"
    
    # 关键文章列表（用于 context_data）
    key_articles = []
    for article in articles_sorted[:10]:
        key_articles.append({
            "title": article["title"],
            "url": article["url"],
            "source": article.get("source", ""),
            "score": article.get("score", 0),
            "category": article.get("category", ""),
            "summary": article.get("summary", "")[:200],
            "date": article.get("date", "")
        })
    
    # 构建兼容 Briefing 模型的数据
    briefing = {
        # 简报元数据
        "briefing_type": "summary",  # 摘要类型
        "priority": priority,
        "title": title,
        "summary": summary,
        "impact": impact,
        
        # 操作按钮
        "actions": [
            {"label": "查看全部", "action": "view_report"},
            {"label": "详细分析", "action": "start_conversation", "prompt": "请帮我分析今天的AI资讯有什么值得关注的趋势"}
        ],
        
        # 上下文数据（完整文章列表）
        "context_data": {
            "source": "bestblogs.dev",
            "date": report_date,
            "total_articles": len(articles),
            "high_score_count": high_score_count,
            "categories": list(by_category.keys()),
            "articles": key_articles,
            "generated_at": now.isoformat()
        },
        
        # 推送判断
        "should_push": should_push,
        "importance_score": min(0.5 + high_score_count * 0.1, 0.95)
    }
    
    # 保存到本地文件
    filename = f"briefing_articles_{report_date}.json"
    filepath = REPORTS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(briefing, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 简报已生成: {filepath}")
    
    return briefing


def push_briefing_to_feed(briefing: dict, agent_name: str = "AI资讯追踪官") -> bool:
    """
    将简报推送到信息流（插入 Supabase 数据库）
    
    需要设置环境变量:
    - SUPABASE_URL
    - SUPABASE_SERVICE_KEY
    
    Args:
        briefing: 简报数据
        agent_name: Agent 名称，用于查找 agent_id
        
    Returns:
        是否推送成功
    """
    import uuid
    
    # 检查环境变量
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("⚠️ 未配置 Supabase 环境变量，跳过推送到信息流")
        print("   设置 SUPABASE_URL 和 SUPABASE_SERVICE_KEY 以启用推送")
        return False
    
    try:
        from supabase import create_client
        
        supabase = create_client(supabase_url, supabase_key)
        
        # 1. 查找 Agent ID
        agents = supabase.table('agents').select('id, name').eq('name', agent_name).limit(1).execute()
        if not agents.data:
            # 尝试模糊匹配
            agents = supabase.table('agents').select('id, name').ilike('name', f'%资讯%').limit(1).execute()
        
        if not agents.data:
            print(f"⚠️ 未找到 Agent: {agent_name}")
            return False
        
        agent_id = agents.data[0]['id']
        print(f"✅ 找到 Agent: {agents.data[0]['name']}")
        
        # 2. 获取所有活跃用户
        users = supabase.table('users').select('id').eq('is_active', True).execute()
        if not users.data:
            print("⚠️ 没有活跃用户，跳过推送")
            return False
        
        print(f"📤 准备推送给 {len(users.data)} 个用户...")
        
        # 3. 为每个用户创建简报
        briefings_to_insert = []
        for user in users.data:
            briefings_to_insert.append({
                'id': str(uuid.uuid4()),
                'agent_id': agent_id,
                'user_id': user['id'],
                'briefing_type': briefing.get('briefing_type', 'summary'),
                'priority': briefing.get('priority', 'P2'),
                'title': briefing['title'],
                'summary': briefing['summary'],
                'impact': briefing.get('impact'),
                'actions': briefing.get('actions', []),
                'context_data': briefing.get('context_data', {}),
                'importance_score': briefing.get('importance_score', 0.5),
                'status': 'new'
            })
        
        # 4. 批量插入
        result = supabase.table('briefings').insert(briefings_to_insert).execute()
        print(f"✅ 成功推送 {len(result.data)} 条简报到信息流！")
        return True
        
    except ImportError:
        print("⚠️ 未安装 supabase 库，运行: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ 推送失败: {e}")
        return False


def generate_html_cards_report(articles: list[dict], index: dict) -> str:
    """
    生成 HTML 卡片式报告
    - 外层以卡片形式呈现文章列表
    - 点击卡片全屏显示完整内容
    - 现代化的样式设计
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now()
    
    # 按评分排序
    articles_sorted = sorted(articles, key=lambda x: x.get("score", 0), reverse=True)
    
    # 分类颜色映射
    category_colors = {
        "AI": "#6366f1",
        "LLM": "#8b5cf6",
        "GPT": "#a855f7",
        "机器学习": "#ec4899",
        "深度学习": "#f43f5e",
        "产业": "#f97316",
        "技术": "#0ea5e9",
        "开源": "#14b8a6",
        "默认": "#64748b"
    }
    
    def get_category_color(category: str) -> str:
        for key, color in category_colors.items():
            if key in (category or ""):
                return color
        return category_colors["默认"]
    
    # 生成文章卡片 HTML
    cards_html = ""
    for i, article in enumerate(articles_sorted):
        url_hash = get_url_hash(article["url"])
        article_data = index.get("articles", {}).get(url_hash, {})
        file_path = article_data.get("file_path", "")
        
        # 读取文章内容（如果已爬取）
        content_html = ""
        if file_path:
            full_path = SCRIPT_DIR / file_path.replace("articles/", "data/articles/")
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                    # 移除 frontmatter
                    if md_content.startswith("---"):
                        parts = md_content.split("---", 2)
                        if len(parts) >= 3:
                            md_content = parts[2].strip()
                    content_html = md_content
        
        if not content_html:
            content_html = article.get("summary", "暂无内容预览")
        
        category = article.get("category", "AI资讯") or "AI资讯"
        category_color = get_category_color(category)
        score = article.get("score", 0)
        source = article.get("source", "未知来源") or "未知来源"
        
        # 处理内容，转义 HTML 和特殊字符用于 JavaScript
        content_escaped = content_html.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        
        cards_html += f'''
        <article class="card" onclick="openModal({i})" data-index="{i}">
            <div class="card-header">
                <span class="category" style="background: {category_color}20; color: {category_color}">{category}</span>
                <span class="score">⭐ {score}</span>
            </div>
            <h2 class="card-title">{article["title"]}</h2>
            <p class="card-summary">{article.get("summary", "")[:200]}...</p>
            <div class="card-footer">
                <span class="source">{source}</span>
                <span class="read-more">点击阅读 →</span>
            </div>
        </article>
        <script>
            articleContents[{i}] = {{
                title: `{article["title"].replace("`", "'")}`,
                category: `{category}`,
                categoryColor: `{category_color}`,
                source: `{source}`,
                url: `{article["url"]}`,
                score: {score},
                content: `{content_escaped}`
            }};
        </script>
        '''
    
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI资讯速递 - {now.strftime("%Y年%m月%d日")}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0f0f23;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --bg-card-hover: #1a2a4a;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --border-color: #334155;
            --shadow-color: rgba(0, 0, 0, 0.3);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        /* 背景渐变效果 */
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(ellipse at 20% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 40% 60%, rgba(6, 182, 212, 0.08) 0%, transparent 40%);
            pointer-events: none;
            z-index: -1;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        /* 头部样式 */
        .header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem 0;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}
        
        .header .subtitle {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}
        
        .header .meta {{
            margin-top: 1rem;
            display: flex;
            justify-content: center;
            gap: 2rem;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
        
        .header .meta span {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        /* 卡片网格 */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 1.5rem;
        }}
        
        /* 卡片样式 */
        .card {{
            background: var(--bg-card);
            border-radius: 16px;
            padding: 1.5rem;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }}
        
        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .card:hover {{
            transform: translateY(-4px);
            background: var(--bg-card-hover);
            box-shadow: 0 20px 40px var(--shadow-color);
            border-color: var(--accent-primary);
        }}
        
        .card:hover::before {{
            opacity: 1;
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        
        .category {{
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .score {{
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        
        .card-title {{
            font-size: 1.2rem;
            font-weight: 600;
            line-height: 1.4;
            margin-bottom: 0.75rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .card-summary {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-bottom: 1rem;
        }}
        
        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
        }}
        
        .source {{
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        
        .read-more {{
            color: var(--accent-primary);
            font-size: 0.9rem;
            font-weight: 500;
            opacity: 0;
            transform: translateX(-10px);
            transition: all 0.3s;
        }}
        
        .card:hover .read-more {{
            opacity: 1;
            transform: translateX(0);
        }}
        
        /* 模态框样式 */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s;
            backdrop-filter: blur(8px);
        }}
        
        .modal.active {{
            display: flex;
            opacity: 1;
        }}
        
        .modal-content {{
            background: var(--bg-secondary);
            width: 100%;
            max-width: 900px;
            max-height: 90vh;
            margin: auto;
            border-radius: 20px;
            overflow: hidden;
            transform: scale(0.9);
            transition: transform 0.3s;
            display: flex;
            flex-direction: column;
        }}
        
        .modal.active .modal-content {{
            transform: scale(1);
        }}
        
        .modal-header {{
            padding: 1.5rem 2rem;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
        }}
        
        .modal-header-info {{
            flex: 1;
        }}
        
        .modal-header .category {{
            margin-bottom: 0.75rem;
            display: inline-block;
        }}
        
        .modal-title {{
            font-size: 1.5rem;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 0.5rem;
        }}
        
        .modal-meta {{
            display: flex;
            gap: 1.5rem;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
        
        .close-btn {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            flex-shrink: 0;
        }}
        
        .close-btn:hover {{
            background: var(--accent-primary);
            color: white;
            border-color: var(--accent-primary);
        }}
        
        .modal-body {{
            padding: 2rem;
            overflow-y: auto;
            flex: 1;
        }}
        
        .modal-body .content {{
            color: var(--text-primary);
            font-size: 1.05rem;
            line-height: 1.8;
        }}
        
        .modal-body .content h1,
        .modal-body .content h2,
        .modal-body .content h3 {{
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        .modal-body .content h1 {{ font-size: 1.5rem; }}
        .modal-body .content h2 {{ font-size: 1.3rem; }}
        .modal-body .content h3 {{ font-size: 1.1rem; }}
        
        .modal-body .content p {{
            margin-bottom: 1rem;
        }}
        
        .modal-body .content pre {{
            background: var(--bg-primary);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            border: 1px solid var(--border-color);
        }}
        
        .modal-body .content code {{
            font-family: 'JetBrains Mono', monospace;
            background: var(--bg-primary);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        .modal-body .content ul,
        .modal-body .content ol {{
            margin-left: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .modal-body .content li {{
            margin-bottom: 0.5rem;
        }}
        
        .modal-body .content blockquote {{
            border-left: 4px solid var(--accent-primary);
            padding-left: 1rem;
            margin: 1rem 0;
            color: var(--text-secondary);
            font-style: italic;
        }}
        
        .modal-body .content img {{
            max-width: 100%;
            border-radius: 8px;
            margin: 1rem 0;
        }}
        
        .modal-body .content a {{
            color: var(--accent-primary);
            text-decoration: none;
        }}
        
        .modal-body .content a:hover {{
            text-decoration: underline;
        }}
        
        .modal-footer {{
            padding: 1rem 2rem;
            background: var(--bg-card);
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: flex-end;
            gap: 1rem;
        }}
        
        .btn {{
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            border: none;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        }}
        
        .btn-secondary {{
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }}
        
        .btn-secondary:hover {{
            background: var(--bg-card);
            color: var(--text-primary);
        }}
        
        /* 响应式 */
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .cards-grid {{
                grid-template-columns: 1fr;
            }}
            
            .modal-content {{
                margin: 0;
                border-radius: 0;
                max-height: 100vh;
            }}
            
            .modal-title {{
                font-size: 1.2rem;
            }}
        }}
        
        /* 动画 */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .card {{
            animation: fadeIn 0.5s ease-out forwards;
        }}
        
        .cards-grid .card:nth-child(1) {{ animation-delay: 0.05s; }}
        .cards-grid .card:nth-child(2) {{ animation-delay: 0.1s; }}
        .cards-grid .card:nth-child(3) {{ animation-delay: 0.15s; }}
        .cards-grid .card:nth-child(4) {{ animation-delay: 0.2s; }}
        .cards-grid .card:nth-child(5) {{ animation-delay: 0.25s; }}
        .cards-grid .card:nth-child(6) {{ animation-delay: 0.3s; }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🤖 AI资讯速递</h1>
            <p class="subtitle">精选前沿 AI 技术文章，每日更新</p>
            <div class="meta">
                <span>📅 {now.strftime("%Y年%m月%d日")}</span>
                <span>📰 共 {len(articles)} 篇文章</span>
                <span>🔗 来源: bestblogs.dev</span>
            </div>
        </header>
        
        <main class="cards-grid">
            <script>const articleContents = {{}};</script>
            {cards_html}
        </main>
    </div>
    
    <!-- 模态框 -->
    <div class="modal" id="articleModal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-header-info">
                    <span class="category" id="modalCategory"></span>
                    <h2 class="modal-title" id="modalTitle"></h2>
                    <div class="modal-meta">
                        <span id="modalSource"></span>
                        <span id="modalScore"></span>
                    </div>
                </div>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="content" id="modalContent"></div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal()">关闭</button>
                <a class="btn btn-primary" id="modalLink" href="#" target="_blank">
                    🔗 阅读原文
                </a>
            </div>
        </div>
    </div>
    
    <script>
        const modal = document.getElementById('articleModal');
        
        function openModal(index) {{
            const article = articleContents[index];
            if (!article) return;
            
            document.getElementById('modalCategory').textContent = article.category;
            document.getElementById('modalCategory').style.background = article.categoryColor + '20';
            document.getElementById('modalCategory').style.color = article.categoryColor;
            document.getElementById('modalTitle').textContent = article.title;
            document.getElementById('modalSource').textContent = '📖 ' + article.source;
            document.getElementById('modalScore').textContent = '⭐ ' + article.score;
            document.getElementById('modalContent').innerHTML = renderMarkdown(article.content);
            document.getElementById('modalLink').href = article.url;
            
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }}
        
        function closeModal() {{
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }}
        
        // 点击模态框外部关闭
        modal.addEventListener('click', (e) => {{
            if (e.target === modal) {{
                closeModal();
            }}
        }});
        
        // ESC 键关闭
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') {{
                closeModal();
            }}
        }});
        
        // 简单的 Markdown 渲染
        function renderMarkdown(text) {{
            if (!text) return '';
            
            return text
                // 代码块
                .replace(/```(\\w*)\\n([\\s\\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
                // 行内代码
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                // 标题
                .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                .replace(/^# (.*$)/gim, '<h1>$1</h1>')
                // 粗体
                .replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>')
                // 斜体
                .replace(/\\*([^*]+)\\*/g, '<em>$1</em>')
                // 链接
                .replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank">$1</a>')
                // 图片
                .replace(/!\\[([^\\]]*?)\\]\\(([^)]+)\\)/g, '<img src="$2" alt="$1" />')
                // 引用
                .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
                // 无序列表
                .replace(/^- (.*$)/gim, '<li>$1</li>')
                // 段落
                .replace(/\\n\\n/g, '</p><p>')
                // 换行
                .replace(/\\n/g, '<br>');
        }}
    </script>
</body>
</html>
'''
    
    # 保存 HTML 报告
    filename = f"articles_{now.strftime('%Y-%m-%d')}.html"
    filepath = REPORTS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ HTML卡片报告已生成: {filepath}")
    return str(filepath)


def main():
    parser = argparse.ArgumentParser(description='AI资讯追踪官 - 文章爬虫')
    parser.add_argument('--days', type=int, default=7, help='获取最近N天的文章（默认7天）')
    parser.add_argument('--category', type=str, help='按分类筛选')
    parser.add_argument('--force', action='store_true', help='强制全量更新，忽略缓存')
    parser.add_argument('--report', choices=['weekly', 'daily', 'html', 'cards', 'briefing', 'all'], 
                        help='生成报告类型')
    parser.add_argument('--push', action='store_true', help='推送简报到信息流（需配置 Supabase）')
    parser.add_argument('--list-only', action='store_true', help='只获取列表，不抓取详情')
    
    args = parser.parse_args()
    
    # 加载索引
    index = load_index()
    
    # 如果只是生成报告（从索引生成）
    if args.report == 'weekly':
        generate_weekly_report(index)
        return
    
    # 从缓存生成报告
    if args.report in ['html', 'cards', 'briefing', 'all']:
        cached_articles = list(index.get("articles", {}).values())
        if cached_articles:
            print(f"📊 使用缓存数据生成报告（{len(cached_articles)} 篇文章）")
            
            if args.report in ['html', 'cards']:
                generate_html_cards_report(cached_articles, index)
            elif args.report == 'briefing':
                briefing = generate_briefing_for_feed(cached_articles)
                if args.push and briefing.get('should_push'):
                    push_briefing_to_feed(briefing)
                elif args.push:
                    print("ℹ️ 简报价值不足，跳过推送")
            elif args.report == 'all':
                generate_briefing_for_feed(cached_articles)
                generate_html_cards_report(cached_articles, index)
            
            return
        else:
            print("⚠️ 缓存中没有文章，尝试在线获取...")
            # 继续执行在线获取逻辑
    
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
        
        # 生成报告
        if args.report in ['html', 'cards']:
            generate_html_cards_report(articles, index)
            return
        
        if args.report in ['briefing', 'all']:
            briefing = generate_briefing_for_feed(articles)
            
            # 如果指定了 --push 且简报值得推送
            if args.push and briefing.get('should_push'):
                push_briefing_to_feed(briefing)
            elif args.push and not briefing.get('should_push'):
                print("ℹ️ 简报价值不足，跳过推送（可手动推送）")
            
            if args.report == 'all':
                # 同时生成 HTML 报告
                generate_html_cards_report(articles, index)
            
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

