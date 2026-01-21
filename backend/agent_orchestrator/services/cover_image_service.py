"""
封面图片生成服务 - 为简报生成AI封面图片
"""

import logging
import os
import httpx
import base64
import random
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CoverImageService:
    """封面图片生成服务（使用 Gemini 3 Pro Image Preview）"""

    # 风格化提示词模板（多样化风格，随机选择）
    STYLE_TEMPLATES = [
        # 3D 等轴风格
        "isometric 3D illustration of a modern workspace with floating holographic data charts and AI assistant robot, soft pastel colors, clean geometric shapes, tech startup aesthetic, 16:9 aspect ratio",
        # 抽象科技风
        "abstract digital art with flowing data streams and neural network patterns, deep blue and cyan color scheme, futuristic tech aesthetic, soft glow effects, 16:9 aspect ratio",
        # 低多边形风格
        "low poly geometric landscape with mountains and sunrise, vibrant gradient colors from purple to orange, modern digital art style, clean and minimal, 16:9 aspect ratio",
        # 赛博朋克风
        "cyberpunk cityscape with neon lights and holographic billboards, rain reflections on streets, purple and pink color palette, atmospheric and moody, 16:9 aspect ratio",
        # 扁平插画风
        "flat illustration of a person working with floating screens and data visualizations, warm sunset color palette, modern vector art style, clean lines, 16:9 aspect ratio",
        # 玻璃拟态风
        "glassmorphism UI design with frosted glass cards floating in space, soft gradients and blur effects, modern minimal aesthetic, light and airy, 16:9 aspect ratio",
        # 渐变抽象风
        "abstract fluid art with smooth gradient blobs, vibrant colors mixing together, modern digital aesthetic, dreamy and ethereal, 16:9 aspect ratio",
        # 宇宙科幻风
        "cosmic space scene with nebula clouds and distant planets, starfield background, deep purple and blue tones, epic and inspiring, 16:9 aspect ratio",
    ]

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
        title: str,
        summary: str,
        **kwargs,  # 忽略其他参数（如 briefing_type, priority）
    ) -> Optional[Dict[str, Any]]:
        """
        生成简报封面图片

        Args:
            title: 简报标题
            summary: 简报摘要
            **kwargs: 其他参数（忽略）

        Returns:
            包含图片数据的字典 {"image_data": bytes, "metadata": dict}
            如果生成失败返回None
        """
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured, skipping cover image generation")
            return None

        # 随机选择一个风格模板
        style_prompt = random.choice(self.STYLE_TEMPLATES)

        # 基于标题内容微调提示词
        enhanced_prompt = self._enhance_prompt(style_prompt, title, summary)

        logger.info(f"Generating cover image with prompt: {enhanced_prompt[:100]}...")

        try:
            # 调用 Gemini 3 Pro Image Preview API
            image_data = await self._call_gemini_imagen(enhanced_prompt)

            if image_data:
                metadata = {
                    "model": "gemini-3-pro-image-preview",
                    "prompt": enhanced_prompt,
                    "generated_at": datetime.utcnow().isoformat(),
                }
                return {"image_data": image_data, "metadata": metadata}
            else:
                logger.warning("Gemini returned no image data")
                return None

        except Exception as e:
            logger.error(f"Failed to generate cover image: {e}", exc_info=True)
            return None

    def _enhance_prompt(self, style_prompt: str, title: str, summary: str) -> str:
        """
        基于标题内容微调提示词

        Args:
            style_prompt: 风格提示词
            title: 标题
            summary: 摘要

        Returns:
            增强后的提示词
        """
        # 检测内容主题，添加相关元素
        theme_hints = []

        # 检测技术相关
        if any(kw in title + summary for kw in ["代码", "Review", "Git", "构建", "部署", "测试"]):
            theme_hints.append("code editor elements")

        # 检测数据分析相关
        if any(kw in title + summary for kw in ["分析", "数据", "指标", "效率", "统计"]):
            theme_hints.append("data analytics dashboard")

        # 检测 AI 相关
        if any(kw in title + summary for kw in ["AI", "智能", "机器学习", "模型"]):
            theme_hints.append("AI brain neural network")

        # 检测资讯相关
        if any(kw in title + summary for kw in ["资讯", "新闻", "文章", "博客"]):
            theme_hints.append("news feed interface")

        # 如果有主题提示，融入到风格提示词中
        if theme_hints:
            hint_text = ", ".join(theme_hints[:2])
            enhanced = f"{style_prompt}, incorporating {hint_text}"
        else:
            enhanced = style_prompt

        return enhanced

    async def _call_gemini_imagen(self, prompt: str) -> Optional[bytes]:
        """
        调用 Gemini 3 Pro Image Preview API

        API文档: https://ai.google.dev/gemini-api/docs/image-generation

        Args:
            prompt: 图片生成提示词

        Returns:
            图片字节数据（PNG格式），失败返回None
        """
        # Gemini 3 Pro Image Preview API endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent"

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
