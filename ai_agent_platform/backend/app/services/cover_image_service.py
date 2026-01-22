"""
封面图生成服务 - 使用 Gemini Imagen 生成简报封面

支持：
1. Gemini Imagen 3 生成 AI 封面图
2. 上传到 Supabase Storage
3. 降级到渐变占位符（如果生成失败）
"""

import logging
import os
import uuid
import base64
import httpx
from typing import Optional, Dict, Any

from app.core.config import settings
from app.db.supabase import get_supabase_admin_client

logger = logging.getLogger(__name__)


class CoverImageService:
    """封面图生成服务"""
    
    # Gemini API 配置
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict"
    
    # 简报类型对应的风格描述
    TYPE_STYLES = {
        "alert": {
            "color": "warm red and orange tones",
            "mood": "urgent, attention-grabbing",
            "elements": "warning symbols, alert indicators, data anomaly visualization"
        },
        "insight": {
            "color": "purple and violet gradients",
            "mood": "thoughtful, analytical, discovery",
            "elements": "lightbulb, data patterns, trend lines, magnifying glass"
        },
        "summary": {
            "color": "blue and cyan tones",
            "mood": "professional, comprehensive, organized",
            "elements": "charts, dashboards, data panels, summary icons"
        },
        "action": {
            "color": "green and teal tones",
            "mood": "actionable, productive, task-oriented",
            "elements": "checkboxes, task lists, progress indicators"
        }
    }
    
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning("Gemini API key not configured. Cover image generation will be disabled.")
    
    async def generate_cover_image(
        self,
        briefing_type: str,
        title: str,
        summary: str,
        priority: str = "P2"
    ) -> Optional[str]:
        """
        生成简报封面图
        
        Args:
            briefing_type: 简报类型 (alert, insight, summary, action)
            title: 简报标题
            summary: 简报摘要
            priority: 优先级 (P0, P1, P2)
            
        Returns:
            封面图 URL（存储在 Supabase Storage），失败返回 None
        """
        if not self.enabled:
            logger.debug("Cover image generation disabled (no API key)")
            return None
        
        try:
            # 1. 构建生成 prompt
            prompt = self._build_prompt(briefing_type, title, summary, priority)
            logger.info(f"Generating cover image for {briefing_type} briefing")
            
            # 2. 调用 Gemini Imagen API
            image_data = await self._call_gemini_api(prompt)
            
            if not image_data:
                logger.warning("Gemini API returned no image data")
                return None
            
            # 3. 上传到 Supabase Storage
            image_url = await self._upload_to_storage(image_data, briefing_type)
            
            logger.info(f"Cover image generated and uploaded: {image_url[:50]}...")
            return image_url
            
        except Exception as e:
            logger.error(f"Failed to generate cover image: {e}", exc_info=True)
            return None
    
    def _build_prompt(
        self,
        briefing_type: str,
        title: str,
        summary: str,
        priority: str
    ) -> str:
        """构建图片生成 prompt"""
        style = self.TYPE_STYLES.get(briefing_type, self.TYPE_STYLES["insight"])
        
        # 根据优先级调整紧急感
        urgency = {
            "P0": "extremely urgent, critical attention needed",
            "P1": "important, needs attention",
            "P2": "informational, for awareness"
        }.get(priority, "informational")
        
        # 提取标题中的关键数字和概念
        key_concepts = self._extract_key_concepts(title, summary)
        
        prompt = f"""Create a modern, minimalist cover image for a business intelligence briefing:

THEME: {title[:50]}
KEY CONCEPTS: {key_concepts}

STYLE REQUIREMENTS:
- Color palette: {style['color']}
- Mood: {style['mood']}, {urgency}
- Visual elements: {style['elements']}

DESIGN RULES:
- Flat design, minimalist aesthetic
- NO text or words in the image
- Abstract data visualization style
- Suitable for mobile app card cover
- 16:9 aspect ratio (landscape)
- Clean, professional look
- Subtle gradients and geometric shapes
- Modern tech/business aesthetic

The image should convey the feeling of data analysis and business insights without being too literal."""

        return prompt
    
    def _extract_key_concepts(self, title: str, summary: str) -> str:
        """从标题和摘要中提取关键概念"""
        concepts = []
        
        # 检测数字相关
        if any(char.isdigit() for char in title):
            concepts.append("metrics and numbers")
        
        # 检测趋势相关
        trend_words = ["上升", "下降", "增长", "减少", "提升", "恶化", "改善"]
        if any(word in title + summary for word in trend_words):
            concepts.append("trend analysis")
        
        # 检测效率相关
        efficiency_words = ["效率", "耗时", "返工", "通过率", "分支"]
        if any(word in title + summary for word in efficiency_words):
            concepts.append("efficiency metrics")
        
        # 检测团队相关
        team_words = ["团队", "人员", "部门", "协作"]
        if any(word in title + summary for word in team_words):
            concepts.append("team collaboration")
        
        return ", ".join(concepts) if concepts else "business analytics"
    
    async def _call_gemini_api(self, prompt: str) -> Optional[bytes]:
        """调用 Gemini Imagen API"""
        url = f"{self.GEMINI_API_URL}?key={self.api_key}"
        
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "16:9",
                "personGeneration": "DONT_ALLOW",
                "safetyFilterLevel": "BLOCK_MEDIUM_AND_ABOVE"
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code} - {response.text[:500]}")
                return None
            
            result = response.json()
            
            # 提取图片数据
            predictions = result.get("predictions", [])
            if not predictions:
                return None
            
            # Gemini 返回 base64 编码的图片
            image_base64 = predictions[0].get("bytesBase64Encoded")
            if not image_base64:
                return None
            
            return base64.b64decode(image_base64)
    
    async def _upload_to_storage(self, image_data: bytes, briefing_type: str) -> str:
        """上传图片到 Supabase Storage"""
        supabase = get_supabase_admin_client()
        
        # 生成唯一文件名
        file_name = f"covers/{briefing_type}/{uuid.uuid4()}.png"
        
        # 上传到 Storage
        result = supabase.storage.from_("briefing-assets").upload(
            file_name,
            image_data,
            file_options={"content-type": "image/png"}
        )
        
        # 获取公开 URL
        public_url = supabase.storage.from_("briefing-assets").get_public_url(file_name)
        
        return public_url


# 单例实例
cover_image_service = CoverImageService()

