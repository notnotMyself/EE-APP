# 简报封面生成 & LLM 配置说明

## 📸 封面图生成方案

### 当前实现（Phase 1）：纯前端渲染

**❌ 不使用任何图片生成 API**

封面是通过 Flutter 代码**实时渲染**的，不需要调用 Gemini、DALL-E 等图片生成服务。

#### 实现方式

```dart
// briefing_card.dart:190-259
Widget _buildCoverImage(BuildContext context) {
  return Container(
    width: double.infinity,
    height: 240,
    decoration: BoxDecoration(
      // ✅ 渐变背景（根据类型动态生成）
      gradient: LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: _getCoverGradientColors(briefing.briefingType),
      ),
    ),
    child: Center(
      // ✅ 半透明大图标
      child: Icon(
        _getTypeIcon(briefing.briefingType),
        size: 96,
        color: Colors.white.withOpacity(0.4),
      ),
    ),
  );
}
```

#### 渐变颜色映射

| 简报类型 | 渐变颜色（起始 → 结束） | 图标 |
|---------|----------------------|------|
| **Alert** | `#FEE2E2` → `#FECACA`（浅红→深红） | ⚠️ `warning_rounded` |
| **Insight** | `#EDE9FE` → `#DDD6FE`（浅紫→深紫） | 💡 `lightbulb_rounded` |
| **Summary** | `#DBEAFE` → `#BFDBFE`（浅蓝→深蓝） | 📊 `summarize_rounded` |
| **Action** | `#D1FAE5` → `#A7F3D0`（浅绿→深绿） | ✅ `task_alt_rounded` |

**优点**：
- ✅ 无需 API 调用，速度极快
- ✅ 零成本（不消耗 API 额度）
- ✅ 离线可用
- ✅ 风格统一、可控
- ✅ 性能优秀（纯 GPU 渲染）

**局限**：
- ❌ 缺少个性化（所有同类型简报封面相同）
- ❌ 不够吸引眼球

---

## 🚀 未来规划（Phase 2+）：AI 生成封面图

### 方案 1：使用 Gemini Imagen（推荐）

**API**: Google Gemini Imagen 3

**调用时机**：简报生成时，后端调用 Imagen API

**实现流程**：
```python
# backend/app/services/image_generation_service.py

from google.cloud import aiplatform
import os

class ImageGenerationService:
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = "us-central1"

    async def generate_briefing_cover(
        self,
        briefing_type: str,
        title: str,
        summary: str
    ) -> str:
        """生成简报封面图"""

        # 构建 prompt
        prompt = self._build_prompt(briefing_type, title, summary)

        # 调用 Imagen API
        client = aiplatform.gapic.PredictionServiceClient()
        endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/imagegeneration@006"

        response = client.predict(
            endpoint=endpoint,
            instances=[{"prompt": prompt}],
            parameters={
                "sampleCount": 1,
                "aspectRatio": "16:9",
                "personGeneration": "dont_allow"
            }
        )

        # 上传到 Supabase Storage
        image_url = await self._upload_to_storage(response.predictions[0])

        return image_url

    def _build_prompt(self, briefing_type, title, summary):
        """根据简报类型构建图片生成 prompt"""
        style_map = {
            "alert": "警报风格，红色调，紧急感，商务抽象图形",
            "insight": "洞察风格，紫色调，灯泡和数据可视化元素",
            "summary": "总结风格，蓝色调，图表和数据面板",
            "action": "行动风格，绿色调，复选框和任务列表元素"
        }

        base_style = style_map.get(briefing_type, "商务风格")

        return f"""
        创建一张简洁的商务风格配图：

        主题：{title}
        内容：{summary[:100]}

        风格要求：
        - {base_style}
        - 扁平化设计
        - 极简主义
        - 无文字
        - 适合作为信息流卡片封面
        - 16:9 横向构图
        """
```

**配置**：
```bash
# .env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

**成本估算**：
- Imagen 3：约 $0.02/张（标准质量）
- 假设每天生成 10 条简报 × 30 天 = 300 张/月
- 月成本：$6

---

### 方案 2：使用 Stability AI（备选）

**API**: Stable Diffusion 3

```python
import requests
import os

class ImageGenerationService:
    def __init__(self):
        self.api_key = os.getenv('STABILITY_API_KEY')
        self.api_url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

    async def generate_briefing_cover(self, prompt: str) -> str:
        response = requests.post(
            self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "image/*"
            },
            files={"none": ""},
            data={
                "prompt": prompt,
                "output_format": "png",
                "aspect_ratio": "16:9"
            }
        )

        # 保存并上传
        image_url = await self._upload_to_storage(response.content)
        return image_url
```

**成本**：约 $0.05/张

---

### 方案 3：DALL-E 3（最贵）

**API**: OpenAI DALL-E 3

```python
from openai import AsyncOpenAI

class ImageGenerationService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    async def generate_briefing_cover(self, prompt: str) -> str:
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",  # 16:9
            quality="standard",
            n=1
        )

        image_url = response.data[0].url
        return image_url
```

**成本**：$0.04/张（标准质量）

---

### 集成到简报生成流程

```python
# briefing_service.py

async def _create_briefing_for_user_supabase(
    self,
    agent_id: UUID,
    user_id: UUID,
    briefing_data: Dict[str, Any],
    context_data: Dict[str, Any]
) -> UUID:
    """为用户创建简报"""

    # ✨ 新增：生成封面图（如果启用）
    cover_image_url = None
    if settings.ENABLE_AI_COVER_GENERATION:
        try:
            cover_image_url = await image_generation_service.generate_briefing_cover(
                briefing_type=briefing_data.get('type'),
                title=briefing_data.get('title'),
                summary=briefing_data.get('summary')
            )
        except Exception as e:
            logger.warning(f"Failed to generate cover image: {e}")
            # 降级到渐变背景

    briefing_record = {
        'id': str(uuid.uuid4()),
        'agent_id': str(agent_id),
        'user_id': str(user_id),
        'briefing_type': briefing_data.get('type', 'insight'),
        'priority': briefing_data.get('priority', 'P2'),
        'title': briefing_data.get('title', '新简报'),
        'summary': briefing_data.get('summary', ''),
        'cover_image_url': cover_image_url,  # ✨ 新增字段
        'importance_score': importance_score,
        'status': 'new'
    }

    supabase = get_supabase_admin_client()
    result = supabase.table('briefings').insert(briefing_record).execute()

    return UUID(result.data[0]['id'])
```

**前端自动支持**（已有降级逻辑）：
```dart
// briefing_card.dart
Widget _buildCoverImage(BuildContext context) {
  // 如果有真实封面图
  if (briefing.coverImageUrl != null) {
    return Image.network(
      briefing.coverImageUrl!,
      height: 240,
      width: double.infinity,
      fit: BoxFit.cover,
    );
  }

  // 否则显示渐变背景（降级方案）
  return Container(
    // ... 现有的渐变代码
  );
}
```

---

## 🤖 LLM 配置详解

### 当前使用：Claude（Anthropic）

**不使用 Gemini！**

#### 配置信息

```bash
# .env
ANTHROPIC_AUTH_TOKEN=sk-QTakUxAFn8sR4t29yGlkWmJr5ne9JfsQKHtKKnmy8LEskgbX
ANTHROPIC_BASE_URL=https://llm-gateway.oppoer.me
ANTHROPIC_MODEL=saas/claude-sonnet-4.5
```

**说明**：
- ✅ 使用 **OPPO 内部 LLM Gateway**（`llm-gateway.oppoer.me`）
- ✅ 模型：**Claude Sonnet 4.5**（最新版本）
- ✅ 认证方式：Auth Token（不是标准 API Key）

#### 使用的 SDK

```python
# requirements.txt
anthropic>=0.40.0        # Anthropic Python SDK
claude-agent-sdk>=0.1.6  # Claude Agent SDK（用于工具调用）
```

#### 调用方式

**1. 简报判断（基础 API）**：
```python
# app/services/claude_service.py
from anthropic import Anthropic

client = Anthropic(
    base_url=settings.ANTHROPIC_BASE_URL,
    auth_token=settings.ANTHROPIC_AUTH_TOKEN
)

response = await client.messages.create(
    model=settings.ANTHROPIC_MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)
```

**2. Agent 任务执行（Agent SDK）**：
```python
# app/services/agent_sdk_client.py
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt=full_prompt,
    options=ClaudeAgentOptions(
        allowed_tools=["Bash", "Read", "Write", "Grep", "Glob"],
        cwd=agent_workspace,
        model=settings.ANTHROPIC_MODEL  # 使用相同的模型
    )
):
    result_chunks.append(str(message))
```

---

## 🔑 API Key 配置指南

### 方式 1：使用 OPPO LLM Gateway（当前）

**优势**：
- ✅ 统一管理（公司级）
- ✅ 成本可控（公司买单）
- ✅ 无需担心额度

**配置**：
```bash
ANTHROPIC_AUTH_TOKEN=sk-xxx  # 从 OPPO 内部系统获取
ANTHROPIC_BASE_URL=https://llm-gateway.oppoer.me
ANTHROPIC_MODEL=saas/claude-sonnet-4.5
```

---

### 方式 2：使用 Anthropic 官方 API（备选）

**场景**：开发测试、Demo 环境

**配置**：
```bash
# 注释掉 Auth Token 和 Base URL
# ANTHROPIC_AUTH_TOKEN=
# ANTHROPIC_BASE_URL=

# 使用标准 API Key
ANTHROPIC_API_KEY=sk-ant-api03-xxx  # 从 console.anthropic.com 获取
ANTHROPIC_MODEL=claude-sonnet-4-20250514  # 官方模型名称
```

**代码自动兼容**：
```python
# app/core/config.py
class Settings(BaseSettings):
    ANTHROPIC_AUTH_TOKEN: str = ""  # 优先使用 Auth Token
    ANTHROPIC_API_KEY: str = ""     # 备用 API Key
    ANTHROPIC_BASE_URL: str = ""    # 自定义 Base URL

    @property
    def anthropic_client_config(self):
        if self.ANTHROPIC_AUTH_TOKEN:
            return {
                "auth_token": self.ANTHROPIC_AUTH_TOKEN,
                "base_url": self.ANTHROPIC_BASE_URL
            }
        else:
            return {
                "api_key": self.ANTHROPIC_API_KEY
            }
```

---

## 📊 成本对比

### LLM 调用成本（Claude Sonnet 4.5）

| 场景 | Token 消耗 | 成本（官方价格） |
|------|-----------|----------------|
| 简报判断（_decide_briefing） | ~1,000 tokens | $0.003 |
| Agent 分析任务 | ~4,000 tokens | $0.012 |
| 单次完整流程 | ~5,000 tokens | $0.015 |

**月度估算**：
- 每天 10 个定时任务 × 30 天 = 300 次/月
- 月成本：300 × $0.015 = **$4.5**

### 图片生成成本（如果启用 Phase 2）

| 服务 | 每张成本 | 月成本（300张） |
|------|---------|---------------|
| Gemini Imagen 3 | $0.02 | $6 |
| Stability AI | $0.05 | $15 |
| DALL-E 3 | $0.04 | $12 |

---

## 🎯 推荐配置

### 开发环境
```bash
# 使用 OPPO Gateway（免费）
ANTHROPIC_AUTH_TOKEN=sk-xxx
ANTHROPIC_BASE_URL=https://llm-gateway.oppoer.me
ANTHROPIC_MODEL=saas/claude-sonnet-4.5

# 封面图：使用渐变背景（Phase 1）
ENABLE_AI_COVER_GENERATION=false
```

### 生产环境
```bash
# LLM：继续使用 OPPO Gateway
ANTHROPIC_AUTH_TOKEN=sk-xxx
ANTHROPIC_BASE_URL=https://llm-gateway.oppoer.me
ANTHROPIC_MODEL=saas/claude-sonnet-4.5

# 封面图：启用 Gemini Imagen（Phase 2）
ENABLE_AI_COVER_GENERATION=true
GOOGLE_CLOUD_PROJECT=ai-agent-platform
GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-credentials.json
```

---

## ❓ 常见问题

### Q1: 为什么不用 Gemini 做 LLM？
**A**: Claude 在**推理能力**和**工具调用**方面更强，特别适合需要执行复杂任务的 Agent 场景。Gemini 更适合多模态任务（图片、视频）。

### Q2: 封面图必须用 AI 生成吗？
**A**: 不必须。当前的渐变背景方案已经足够美观且统一。AI 生成封面可以在 Phase 2 作为增强功能。

### Q3: 能否混合使用多个 LLM？
**A**: 可以。例如：
- Claude：Agent 任务执行（推理能力强）
- Gemini Flash：简单的文本总结（成本低）
- GPT-4o-mini：图表数据解读（视觉能力强）

### Q4: API Key 泄露怎么办？
**A**:
1. 立即在控制台撤销 Key
2. 重新生成新 Key
3. 更新 `.env` 文件
4. 确保 `.env` 在 `.gitignore` 中

---

## 📚 参考文档

- [Claude API 文档](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk)
- [Gemini Imagen 文档](https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview)
- [Stability AI 文档](https://platform.stability.ai/docs/api-reference)

---

## 🔄 版本历史

- **v1.0** (2026-01-06): 初始版本，使用渐变背景 + Claude Sonnet 4.5
- **v2.0** (计划中): 集成 Gemini Imagen 生成封面图
- **v3.0** (规划中): 支持多 LLM 混合调用
