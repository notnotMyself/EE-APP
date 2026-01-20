"""
封面图片生成服务 - 为简报生成AI封面图片
"""

import logging
import os
import httpx
import base64
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CoverImageService:
    """封面图片生成服务（使用Gemini Imagen API）"""

    # 提示词模板（根据简报类型）
    PROMPT_TEMPLATES = {
        "alert": "urgent red gradient background with warning icons, modern minimalist style, professional corporate design, 16:9 aspect ratio",
        "insight": "analytical blue gradient background with data visualization elements, modern minimalist style, professional corporate design, 16:9 aspect ratio",
        "summary": "calm green gradient background with summary icons, modern minimalist style, professional corporate design, 16:9 aspect ratio",
        "action": "energetic orange gradient background with action icons, modern minimalist style, professional corporate design, 16:9 aspect ratio",
    }

    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        初始化封面图片生成服务

        Args:
            gemini_api_key: Gemini API密钥（如未提供则从环境变量读取）
        """
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured, cover image generation disabled")

    async def generate_cover_image(
        self,
        briefing_type: str,
        title: str,
        summary: str,
        priority: str = "P2",
    ) -> Optional[Dict[str, Any]]:
        """
        生成简报封面图片

        Args:
            briefing_type: 简报类型 (alert, insight, summary, action)
            title: 简报标题
            summary: 简报摘要
            priority: 优先级 (P0, P1, P2)

        Returns:
            包含图片数据的字典 {"image_data": bytes, "metadata": dict}
            如果生成失败返回None
        """
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured, skipping cover image generation")
            return None

        # 根据类型获取基础提示词
        base_prompt = self.PROMPT_TEMPLATES.get(briefing_type, self.PROMPT_TEMPLATES["summary"])

        # 增强提示词（融入标题关键词）
        enhanced_prompt = self._enhance_prompt(base_prompt, title, summary)

        logger.info(f"Generating cover image with prompt: {enhanced_prompt[:100]}...")

        try:
            # 调用Gemini Imagen API
            image_data = await self._call_gemini_imagen(enhanced_prompt)

            if image_data:
                metadata = {
                    "model": "gemini-imagen",
                    "prompt": enhanced_prompt,
                    "briefing_type": briefing_type,
                    "priority": priority,
                    "generated_at": datetime.utcnow().isoformat(),
                }
                return {"image_data": image_data, "metadata": metadata}
            else:
                logger.warning("Gemini Imagen returned no image data")
                return None

        except Exception as e:
            logger.error(f"Failed to generate cover image: {e}", exc_info=True)
            return None

    def _enhance_prompt(self, base_prompt: str, title: str, summary: str) -> str:
        """
        增强提示词（融入标题关键词）

        Args:
            base_prompt: 基础提示词
            title: 标题
            summary: 摘要

        Returns:
            增强后的提示词
        """
        # 提取关键词（简单实现：取标题中的关键名词）
        keywords = []

        # 常见关键词
        tech_keywords = ["Review", "构建", "测试", "部署", "代码", "效率", "性能", "AI", "资讯"]
        for keyword in tech_keywords:
            if keyword in title or keyword in summary:
                keywords.append(keyword)

        # 如果找到关键词，添加到提示词中
        if keywords:
            keyword_hint = f"with subtle text '{' '.join(keywords[:2])}' integrated into design, "
            # 在base_prompt的第一个逗号后插入
            parts = base_prompt.split(",", 1)
            if len(parts) == 2:
                enhanced = f"{parts[0]}, {keyword_hint}{parts[1]}"
            else:
                enhanced = f"{base_prompt}, {keyword_hint}"
        else:
            enhanced = base_prompt

        return enhanced

    async def _call_gemini_imagen(self, prompt: str) -> Optional[bytes]:
        """
        调用Gemini图片生成API

        使用 Gemini 3 Pro Image Preview 模型生成图片
        API文档: https://ai.google.dev/gemini-api/docs/image-generation

        Args:
            prompt: 图片生成提示词

        Returns:
            图片字节数据（PNG格式），失败返回None
        """
        # Gemini 3 Pro Image Preview API endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent"

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key,
        }

        data = {
            "contents": [
                {
                    "parts": [
                        {"text": f"Generate an image: {prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                result = response.json()

                # 解析返回的图片数据
                # 响应格式：candidates[0].content.parts[].inlineData.data (base64)
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    for part in parts:
                        if "inlineData" in part:
                            inline_data = part["inlineData"]
                            image_base64 = inline_data.get("data")
                            mime_type = inline_data.get("mimeType", "image/png")
                            if image_base64:
                                logger.info(f"Successfully generated image with mime type: {mime_type}")
                                return base64.b64decode(image_base64)

                logger.warning("No image data in Gemini response")
                return None

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Gemini API: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Gemini API: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}", exc_info=True)
            return None

    async def upload_to_storage(
        self,
        image_data: bytes,
        briefing_id: str,
        supabase_client: Any,
    ) -> Optional[str]:
        """
        上传图片到Supabase Storage

        Args:
            image_data: 图片字节数据
            briefing_id: 简报ID
            supabase_client: Supabase客户端

        Returns:
            图片的公开URL，失败返回None
        """
        if not supabase_client:
            logger.warning("Supabase client not provided, cannot upload image")
            return None

        bucket_name = "briefing-covers"
        file_path = f"{briefing_id}.png"

        try:
            # 上传到Supabase Storage
            result = supabase_client.storage.from_(bucket_name).upload(
                path=file_path,
                file=image_data,
                file_options={"content-type": "image/png"},
            )

            if result:
                # 获取公开URL
                public_url = supabase_client.storage.from_(bucket_name).get_public_url(file_path)
                logger.info(f"Uploaded cover image for briefing {briefing_id}: {public_url}")
                return public_url
            else:
                logger.error(f"Failed to upload cover image for briefing {briefing_id}")
                return None

        except Exception as e:
            logger.error(f"Error uploading cover image to storage: {e}", exc_info=True)
            return None
