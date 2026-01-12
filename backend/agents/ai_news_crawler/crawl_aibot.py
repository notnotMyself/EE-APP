#!/usr/bin/env python3
"""
AI资讯追踪官 - AI工具集(ai-bot.cn)爬虫脚本

爬取 ai-bot.cn/daily-ai-news/ 的每日 AI 资讯
生成精美日报（参考 SACC-AI Native 实验室风格）
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup

# 配置
BASE_URL = "https://ai-bot.cn"
NEWS_URL = f"{BASE_URL}/daily-ai-news/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 路径配置
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
REPORTS_DIR = SCRIPT_DIR / "reports"
AIBOT_INDEX = DATA_DIR / "aibot_index.json"

# 分类映射（根据关键词自动分类）
CATEGORY_KEYWORDS = {
    "产业重磅": ["融资", "投资", "收购", "上市", "估值", "亿元", "亿美元", "合作"],
    "前沿技术": ["开源", "模型", "框架", "算法", "论文", "研究", "发布", "推出"],
    "工具发布": ["工具", "平台", "应用", "功能", "上线", "更新", "版本"],
    "安全合规": ["安全", "隐私", "合规", "监管", "护栏"],
}


def categorize_news(title: str, summary: str) -> tuple[str, str]:
    """根据标题和摘要自动分类，返回 (类别, 标签)"""
    text = title + summary
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                # 确定标签
                if "融资" in text or "投资" in text:
                    tag = "重磅"
                elif "开源" in text:
                    tag = "开源"
                elif "论文" in text or "研究" in text:
                    tag = "学术"
                elif "工具" in text or "平台" in text:
                    tag = "工具"
                elif "安全" in text:
                    tag = "安全"
                else:
                    tag = ""
                return category, tag
    
    return "前沿技术", ""


def load_index() -> dict:
    """加载索引"""
    if AIBOT_INDEX.exists():
        with open(AIBOT_INDEX, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_updated": None,
        "source": "ai-bot.cn",
        "news_by_date": {}
    }


def save_index(index: dict):
    """保存索引"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    index["last_updated"] = datetime.now().isoformat()
    with open(AIBOT_INDEX, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def fetch_news(days: int = 3) -> dict[str, list[dict]]:
    """
    获取最近 N 天的新闻
    返回格式: {"1月6·周二": [news1, news2, ...], ...}
    """
    print(f"📡 正在获取 ai-bot.cn 最近 {days} 天的 AI 资讯...")
    
    try:
        with httpx.Client(
            headers={"User-Agent": USER_AGENT},
            timeout=30.0,
            follow_redirects=True
        ) as client:
            response = client.get(NEWS_URL)
            response.raise_for_status()
            html = response.text
    except httpx.HTTPError as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        return {}
    
    soup = BeautifulSoup(html, 'html.parser')
    
    news_by_date = {}
    current_date = None
    collected_dates = 0
    
    # 查找所有日期和新闻项
    for elem in soup.select('.news-date, .news-item'):
        if 'news-date' in elem.get('class', []):
            # 新的日期
            current_date = elem.get_text(strip=True)
            if current_date not in news_by_date:
                news_by_date[current_date] = []
                collected_dates += 1
                if collected_dates > days:
                    break
        
        elif 'news-item' in elem.get('class', []) and current_date:
            # 新闻条目
            content = elem.select_one('.news-content')
            if not content:
                continue
            
            # 提取标题和链接
            title_elem = content.select_one('h2 a')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            url = title_elem.get('href', '')
            
            # 提取摘要
            summary_elem = content.select_one('p')
            summary = ""
            source = ""
            if summary_elem:
                # 移除来源标签后的文本作为摘要
                summary_text = summary_elem.get_text(strip=True)
                # 提取来源
                source_elem = summary_elem.select_one('.news-time')
                if source_elem:
                    source = source_elem.get_text(strip=True).replace('来源：', '')
                    summary = summary_text.replace(source_elem.get_text(), '').strip()
                else:
                    summary = summary_text
            
            # 自动分类
            category, tag = categorize_news(title, summary)
            
            news_item = {
                "title": title,
                "url": url,
                "summary": summary,
                "source": source,
                "category": category,
                "tag": tag
            }
            
            news_by_date[current_date].append(news_item)
    
    # 统计
    total_news = sum(len(items) for items in news_by_date.values())
    print(f"✅ 获取 {len(news_by_date)} 天共 {total_news} 条资讯")
    
    return news_by_date


def generate_daily_report(news_by_date: dict, date_key: str = None) -> str:
    """
    生成日报（参考 SACC-AI Native 实验室风格）
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 如果没有指定日期，使用最新的一天
    if date_key is None:
        date_key = list(news_by_date.keys())[0] if news_by_date else None
    
    if not date_key or date_key not in news_by_date:
        print("❌ 没有找到指定日期的新闻", file=sys.stderr)
        return ""
    
    news_items = news_by_date[date_key]
    
    # 解析日期
    now = datetime.now()
    # 从 "1月6·周二" 格式解析
    date_match = re.match(r'(\d+)月(\d+)', date_key)
    if date_match:
        month, day = int(date_match.group(1)), int(date_match.group(2))
        report_date = f"{now.year}.{month:02d}.{day:02d}"
    else:
        report_date = now.strftime("%Y.%m.%d")
    
    # 按分类分组
    by_category = {}
    for item in news_items:
        cat = item.get("category", "前沿技术")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    # 生成日报头部摘要
    highlights = []
    for item in news_items[:3]:  # 取前3条作为头条
        title_short = item["title"][:15] + "..." if len(item["title"]) > 15 else item["title"]
        highlights.append(title_short)
    headline = "，".join(highlights) + "。"
    
    # 生成报告
    report = f"""# AI Daily Report

**DAILY NEWS** {report_date}

*AI资讯追踪官*

{headline}

---

"""
    
    # 按分类输出
    category_icons = {
        "产业重磅": "📈",
        "前沿技术": "🔬",
        "工具发布": "🛠️",
        "安全合规": "🔒",
    }
    
    for category in ["产业重磅", "前沿技术", "工具发布", "安全合规"]:
        if category not in by_category:
            continue
        
        icon = category_icons.get(category, "📌")
        report += f"## {icon} {category}\n\n"
        
        for item in by_category[category]:
            tag = f"**{item['tag']}** " if item.get('tag') else ""
            source = f" ({item['source']})" if item.get('source') else ""
            
            report += f"### {tag}[{item['title']}]({item['url']}){source}\n\n"
            report += f"{item['summary']}\n\n"
        
        report += "---\n\n"
    
    report += f"""
> ⚡ 每日更新 · 洞察未来
> 
> *由 AI资讯追踪官 自动生成 - {datetime.now().strftime("%Y-%m-%d %H:%M")}*
> 
> 数据来源: [AI工具集](https://ai-bot.cn/daily-ai-news/)
"""
    
    # 保存报告
    filename = f"daily_{report_date.replace('.', '-')}.md"
    filepath = REPORTS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 日报已生成: {filepath}")
    return str(filepath)


def generate_json_report(news_by_date: dict, date_key: str = None) -> str:
    """生成 JSON 格式的结构化数据（便于前端渲染）"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if date_key is None:
        date_key = list(news_by_date.keys())[0] if news_by_date else None
    
    if not date_key or date_key not in news_by_date:
        return ""
    
    news_items = news_by_date[date_key]
    
    # 解析日期
    now = datetime.now()
    date_match = re.match(r'(\d+)月(\d+)', date_key)
    if date_match:
        month, day = int(date_match.group(1)), int(date_match.group(2))
        report_date = f"{now.year}-{month:02d}-{day:02d}"
    else:
        report_date = now.strftime("%Y-%m-%d")
    
    # 按分类分组
    by_category = {}
    for item in news_items:
        cat = item.get("category", "前沿技术")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    report_data = {
        "date": report_date,
        "date_display": date_key,
        "generated_at": datetime.now().isoformat(),
        "total_news": len(news_items),
        "source": "ai-bot.cn",
        "categories": by_category,
        "highlights": [item["title"] for item in news_items[:3]]
    }
    
    filename = f"daily_{report_date}.json"
    filepath = REPORTS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ JSON 报告已生成: {filepath}")
    return str(filepath)


def generate_briefing(news_by_date: dict, date_key: str = None) -> dict:
    """
    生成简报格式 - 用于信息流推送
    
    简报设计原则：
    1. 标题动词开头，说清核心发现
    2. 摘要简洁有力
    3. 只在有价值时推送
    
    Returns:
        简报数据，包含 should_push 判断
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if date_key is None:
        date_key = list(news_by_date.keys())[0] if news_by_date else None
    
    if not date_key or date_key not in news_by_date:
        return {
            "error": "No news found",
            "should_push": False
        }
    
    news_items = news_by_date[date_key]
    
    # 解析日期
    now = datetime.now()
    date_match = re.match(r'(\d+)月(\d+)', date_key)
    if date_match:
        month, day = int(date_match.group(1)), int(date_match.group(2))
        report_date = f"{now.year}-{month:02d}-{day:02d}"
    else:
        report_date = now.strftime("%Y-%m-%d")
    
    # 按分类分组
    by_category = {}
    for item in news_items:
        cat = item.get("category", "前沿技术")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    # 判断是否值得推送
    should_push = False
    priority = "P2"
    
    # 产业重磅新闻数量
    major_news_count = len(by_category.get("产业重磅", []))
    # 重磅标签数量
    hot_news_count = sum(1 for item in news_items if item.get("tag") == "重磅")
    
    # 推送判断逻辑
    if major_news_count >= 2 or hot_news_count >= 2:
        should_push = True
        priority = "P1"  # 重要
    elif len(news_items) >= 3:
        should_push = True
        priority = "P2"  # 普通
    elif major_news_count >= 1:
        should_push = True
        priority = "P2"
    
    # 生成标题（动词开头，说清核心发现）
    if news_items:
        top_news = news_items[0]
        # 提取关键信息
        title_text = top_news["title"]
        
        # 判断是否是重大新闻
        if "上市" in title_text:
            title = f"今日AI头条：{title_text[:20]}..."
        elif "融资" in title_text or "投资" in title_text:
            title = f"AI产业动态：{title_text[:20]}..."
        elif "发布" in title_text or "推出" in title_text:
            title = f"新品速递：{title_text[:20]}..."
        elif "开源" in title_text:
            title = f"开源动态：{title_text[:20]}..."
        else:
            title = f"今日AI资讯：{len(news_items)}条重要动态"
    else:
        title = "今日暂无重要AI资讯"
        should_push = False
    
    # 生成摘要（简洁有力）
    summary_parts = []
    for item in news_items[:3]:
        # 提取核心内容
        item_summary = item.get("summary", "")[:50]
        source = item.get("source", "")
        if source:
            summary_parts.append(f"{item['title'][:15]}...({source})")
        else:
            summary_parts.append(f"{item['title'][:20]}...")
    
    summary = "；".join(summary_parts) + "。"
    
    # 按重要性排序的关键新闻
    key_news = []
    # 先添加产业重磅
    for item in by_category.get("产业重磅", [])[:2]:
        key_news.append({
            "title": item["title"],
            "source": item.get("source", ""),
            "category": "产业重磅",
            "url": item.get("url", "")
        })
    # 再添加其他分类
    for cat in ["前沿技术", "工具发布", "安全合规"]:
        for item in by_category.get(cat, [])[:1]:
            if len(key_news) < 5:
                key_news.append({
                    "title": item["title"],
                    "source": item.get("source", ""),
                    "category": cat,
                    "url": item.get("url", "")
                })
    
    # 生成结构化新闻列表（用于前端卡片展示）
    summary_structured = []
    for idx, item in enumerate(news_items[:5], 1):
        summary_structured.append({
            "index": idx,
            "title": item["title"][:40] + ("..." if len(item["title"]) > 40 else ""),
            "full_title": item["title"],
            "source": item.get("source", ""),
            "category": item.get("category", "前沿技术"),
            "tag": item.get("tag", ""),
            "url": item.get("url", "")
        })

    briefing = {
        "briefing_type": "ai_news",
        "generated_at": datetime.now().isoformat(),
        "date": report_date,
        "date_display": date_key,
        "should_push": should_push,
        "priority": priority,
        "title": title,
        "summary": summary,
        "summary_structured": summary_structured,  # 结构化新闻列表
        "cover_style": "news_list",  # 提示UI使用紧凑样式
        "metrics": {
            "total_news": len(news_items),
            "major_news": major_news_count,
            "hot_news": hot_news_count,
            "categories": list(by_category.keys())
        },
        "key_news": key_news,
        "source": "ai-bot.cn"
    }
    
    # 保存简报
    filename = f"briefing_{report_date}.json"
    filepath = REPORTS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(briefing, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 简报已生成: {filepath}")
    
    return briefing


def print_news_summary(news_by_date: dict):
    """在终端打印新闻摘要"""
    for date_key, items in news_by_date.items():
        print(f"\n📅 {date_key} ({len(items)} 条)")
        print("-" * 50)
        for i, item in enumerate(items, 1):
            tag = f"[{item['tag']}] " if item.get('tag') else ""
            print(f"  {i}. {tag}{item['title']}")
            if item.get('source'):
                print(f"     └─ 来源: {item['source']}")


def main():
    parser = argparse.ArgumentParser(description='AI资讯追踪官 - AI工具集爬虫')
    parser.add_argument('--days', type=int, default=3, help='获取最近N天的资讯（默认3天）')
    parser.add_argument('--report', choices=['daily', 'json', 'briefing', 'both', 'all'], 
                        help='生成报告类型: daily(日报), json(结构化数据), briefing(简报), both(日报+JSON), all(全部)')
    parser.add_argument('--date', type=str, help='指定日期生成报告（如 "1月6·周二"）')
    parser.add_argument('--list', action='store_true', help='只列出资讯，不生成报告')
    parser.add_argument('--output-json', action='store_true', help='输出JSON到stdout（用于管道）')
    
    args = parser.parse_args()
    
    # 获取新闻
    news_by_date = fetch_news(args.days)
    
    if not news_by_date:
        print("❌ 未获取到任何资讯", file=sys.stderr)
        sys.exit(1)
    
    # 保存索引
    index = load_index()
    index["news_by_date"].update(news_by_date)
    save_index(index)
    
    # 列出新闻
    if args.list:
        print_news_summary(news_by_date)
        return
    
    # 生成报告
    if args.report:
        date_key = args.date or list(news_by_date.keys())[0]
        
        if args.report in ['daily', 'both', 'all']:
            generate_daily_report(news_by_date, date_key)
        
        if args.report in ['json', 'both', 'all']:
            generate_json_report(news_by_date, date_key)
        
        if args.report in ['briefing', 'all']:
            briefing = generate_briefing(news_by_date, date_key)
            if args.output_json:
                # 输出到stdout（用于管道）
                print(json.dumps(briefing, ensure_ascii=False, indent=2))
    else:
        # 默认打印摘要
        print_news_summary(news_by_date)
        print(f"\n💡 提示: 使用 --report daily 生成日报, --report briefing 生成简报")


if __name__ == "__main__":
    main()

