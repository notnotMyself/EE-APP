"""
Agent Orchestrator - FastAPI服务
提供HTTP API让Flutter前端与AI员工交互

v3.1 - 添加定时任务调度和简报系统
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from pathlib import Path

# 添加 backend 目录到 path，以便导入 agent_sdk
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    # 尝试多个可能的 .env 路径
    env_paths = [
        Path(__file__).parent / ".env",  # 当前目录
        Path(__file__).parent.parent.parent / "ai_agent_platform/backend/.env",  # 原有后端
        Path(__file__).parent.parent.parent / "ai_agent_app/backend/.env",  # app后端
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            logging.info(f"Loaded .env from {env_path}")
            break
except ImportError:
    logging.warning("python-dotenv not installed, using system environment variables")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json

# 新的 Agent SDK
from agent_sdk import AgentSDKService, AgentSDKConfig
from agent_sdk.mcp_tools import create_dev_efficiency_server
from agent_sdk.exceptions import AgentNotFoundError, AgentSDKError

# Agent Registry（新增）
from agent_registry import AgentRegistry, init_global_registry

# 调度器和服务模块
from scheduler import SchedulerService, JobExecutor
from services import BriefingService, ImportanceEvaluator, ConversationService
from services.task_execution_service import TaskExecutionService
from api import (
    briefings_router,
    scheduled_jobs_router,
    conversations_router,
    profile_router,
    notifications_router
)
from api.briefings import set_briefing_service
from api.scheduled_jobs import set_scheduler_service, set_supabase_client
from api.conversations import set_conversation_service
from api.profile import set_services as set_profile_services

# Supabase 客户端
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 Agent Registry（新增）
agents_base_dir = Path(__file__).parent.parent / "agents"
agent_registry = init_global_registry(agents_base_dir)
logger.info(f"Agent Registry initialized with {len(agent_registry.get_all_ids())} agents: {agent_registry.get_all_ids()}")

# 初始化 Agent SDK 服务
agent_config = AgentSDKConfig()
agent_service = AgentSDKService(config=agent_config)

# Supabase 客户端
supabase_client: Client = None
supabase_url = os.getenv("SUPABASE_URL")
# 支持两种环境变量名
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

if SUPABASE_AVAILABLE and supabase_url and supabase_key:
    try:
        supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize Supabase client: {e}")
else:
    logger.warning("Supabase not configured (missing URL or key)")

# 初始化服务
importance_evaluator = ImportanceEvaluator()

# 注意：ConversationService、BriefingService、TaskExecutionService有复杂的循环依赖
# 需要多步初始化来解决

# Step 1: 创建BriefingService（不传conversation_service）
briefing_service = BriefingService(
    supabase_client=supabase_client,
    importance_evaluator=importance_evaluator,
    conversation_service=None,  # 暂时为None
)

# Step 2: 创建TaskExecutionService（不传conversation_service）
task_execution_service = TaskExecutionService(
    agent_service=agent_service,
    briefing_service=briefing_service,
    importance_evaluator=importance_evaluator,
    supabase_client=supabase_client,
)

# Step 3: 创建ConversationService（传入briefing_service）
conversation_service = ConversationService(
    supabase_client=supabase_client,
    agent_service=agent_service,  # 使用Agent SDK service
    briefing_service=briefing_service,
)

# Step 4: 设置循环依赖引用
briefing_service.conversation_service = conversation_service
task_execution_service.set_conversation_service(conversation_service)
conversation_service.set_task_executor(task_execution_service)

logger.info("Service dependencies configured successfully")

# 初始化JobExecutor
job_executor = JobExecutor(
    agent_service=agent_service,
    briefing_service=briefing_service,
    supabase_client=supabase_client
)
# 初始化 SchedulerService，传递 AgentRegistry
scheduler_service = SchedulerService(
    supabase_client=supabase_client,
    agent_registry=agent_registry  # 传递 AgentRegistry
)

# 注入服务到API模块
set_briefing_service(briefing_service)
set_conversation_service(conversation_service)
set_scheduler_service(scheduler_service)
set_supabase_client(supabase_client)
set_profile_services(conversation_service, briefing_service)

# 调试：输出配置信息
logger.info(f"Agent SDK Config loaded:")
logger.info(f"  - anthropic_base_url: {agent_config.anthropic_base_url}")
logger.info(f"  - anthropic_auth_token: {agent_config.anthropic_auth_token[:15] if agent_config.anthropic_auth_token else None}...")
logger.info(f"  - default_model: {agent_config.default_model}")
logger.info(f"  - env dict keys: {list(agent_config.get_env_dict().keys())}")

# 创建 MCP 工具服务器（研发效能分析）
# 注意：暂时禁用 MCP 服务器，因为存在与 Claude Agent SDK 的兼容性问题
# TODO: 调试 MCP 服务器集成问题
# mcp_dev_efficiency = create_dev_efficiency_server()
mcp_dev_efficiency = None  # 临时禁用


# ============================================
# 应用生命周期管理
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting application...")

    # 初始化并启动调度器
    try:
        scheduler_service.initialize(job_executor)
        await scheduler_service.start()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

    yield

    # 关闭时
    logger.info("Shutting down application...")
    await scheduler_service.shutdown()


app = FastAPI(
    title="AI Agent Orchestrator",
    description="""
# AI数字员工平台 - Agent协调层

基于 **Claude Agent SDK** 架构的AI员工管理平台。

## 核心功能

- **AI员工管理**: 管理多个专业AI员工（研发效能分析官、NPS洞察官等）
- **实时对话**: SSE/WebSocket 流式对话，支持工具调用
- **定时任务**: APScheduler 驱动的定时分析任务
- **简报系统**: AI主动推送简报（信息流铁律：一天≤3条）

## Agent能力（Claude Agent SDK）

每个AI员工拥有：
- 独立的工作目录（workspace）
- 基于 CLAUDE.md 的行为定义
- SDK 内置工具（Read/Write/Bash/Grep/Glob）
- MCP 自定义工具（gerrit_query/efficiency_trend/generate_report）

## 技术栈

- FastAPI + Python 3.11
- **Claude Agent SDK** (替代直接 Anthropic API)
- **APScheduler** (定时任务调度)
- SSE / WebSocket 流式响应
- Supabase (PostgreSQL)
""",
    version="3.1.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "health",
            "description": "健康检查和服务状态"
        },
        {
            "name": "agents",
            "description": "AI员工管理 - 查询、配置AI员工"
        },
        {
            "name": "chat",
            "description": "对话接口 - WebSocket和HTTP SSE流式对话"
        },
        {
            "name": "briefings",
            "description": "简报系统 - AI主动推送的分析简报"
        },
        {
            "name": "scheduled_jobs",
            "description": "定时任务 - 管理和执行定时分析任务"
        },
        {
            "name": "tasks",
            "description": "即时任务 - 手动触发任务执行"
        }
    ]
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册新的API路由
app.include_router(briefings_router)
app.include_router(scheduled_jobs_router)
app.include_router(conversations_router)
app.include_router(profile_router)
app.include_router(notifications_router)

# Agent Management API
from api.agent_management import router as agent_management_router
app.include_router(agent_management_router)


# ============================================
# 数据模型
# ============================================

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    agent_role: str
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


class ScheduledTaskRequest(BaseModel):
    agent_role: str
    task_description: str
    interval_seconds: Optional[int] = 86400  # 默认每天执行


# ============================================
# 健康检查
# ============================================

@app.get(
    "/",
    tags=["health"],
    summary="服务信息",
    description="获取服务基本信息和运行状态"
)
async def root():
    """获取服务元信息"""
    return {
        "service": "AI Agent Orchestrator",
        "version": "3.1.0",
        "status": "running",
        "backend": "Claude Agent SDK",
        "features": ["chat", "briefings", "scheduled_jobs"]
    }


@app.get(
    "/health",
    tags=["health"],
    summary="健康检查",
    description="用于负载均衡器和监控系统的健康检查端点"
)
async def health_check():
    """健康检查接口"""
    scheduler_jobs = scheduler_service.get_jobs() if scheduler_service.scheduler else []
    return {
        "status": "healthy",
        "supabase": "connected" if supabase_client else "not_configured",
        "scheduler": {
            "status": "running" if scheduler_service.scheduler else "not_initialized",
            "jobs_count": len(scheduler_jobs)
        }
    }


# ============================================
# AI员工管理
# ============================================

@app.get(
    "/api/v1/agents",
    tags=["agents"],
    summary="列出所有AI员工",
    description="""
获取所有可用的AI员工列表。

每个AI员工包含：
- **role**: 员工角色标识（用于API调用）
- **name**: 员工名称（中文）
- **description**: 职责描述
- **workdir**: 工作目录路径
- **model**: 使用的模型
- **available**: 是否可用（工作目录存在）

当前支持的AI员工：
- dev_efficiency_analyst: 研发效能分析官
- nps_insight_analyst: NPS洞察官
- product_requirement_analyst: 产品需求提炼官
- competitor_tracking_analyst: 竞品追踪分析官
- knowledge_management_assistant: 企业知识管理官
""",
    response_description="AI员工列表和总数"
)
async def list_agents():
    """列出所有可用的AI员工"""
    # 使用 AgentRegistry 获取最新的agent列表
    agents = []
    for agent_id in agent_registry.get_all_ids():
        agent_info = agent_registry.get_agent(agent_id)
        if agent_info:
            agents.append({
                "role": agent_info.id,
                "name": agent_info.name,
                "description": agent_info.config.metadata.description,
                "model": agent_info.config.metadata.model,
                "workdir": str(agent_info.agent_dir),
                "available": agent_info.agent_dir.exists()
            })
    return {
        "agents": agents,
        "total": len(agents)
    }


@app.get(
    "/api/v1/agents/{role}",
    tags=["agents"],
    summary="获取AI员工详情",
    description="根据role获取特定AI员工的详细信息",
    response_description="AI员工的详细配置"
)
async def get_agent_info(role: str):
    """
    获取特定AI员工的信息

    Args:
        role: 员工角色标识，例如 'dev_efficiency_analyst'
    """
    agent_info = agent_registry.get_agent(role)
    if not agent_info:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 获取allowed_tools
    allowed_tools = agent_info.config.allowed_tools if hasattr(agent_info.config, 'allowed_tools') else []

    return {
        "role": role,
        "name": agent_info.name,
        "description": agent_info.config.metadata.description,
        "model": agent_info.config.metadata.model,
        "workdir": str(agent_info.agent_dir),
        "allowed_tools": allowed_tools,
        "available": agent_info.agent_dir.exists()
    }


# ============================================
# 对话接口（WebSocket - 流式响应）
# ============================================

@app.websocket("/api/v1/chat/{agent_role}")
async def chat_websocket(websocket: WebSocket, agent_role: str):
    """
    与AI员工进行流式对话（WebSocket）

    客户端发送格式：
    {
        "message": "用户消息",
        "conversation_history": [...]  // 可选
    }

    服务端返回格式（流式）：
    {
        "type": "chunk",
        "content": "AI回复的文本块"
    }
    或
    {
        "type": "tool_use",
        "tool_name": "工具名称",
        "input": {...}
    }
    或
    {
        "type": "done"
    }
    或
    {
        "type": "error",
        "error": "错误信息"
    }
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for agent: {agent_role}")

    # 获取 MCP 服务器（如果是研发效能分析官）
    # 注意：暂时禁用 MCP 服务器
    mcp_servers = None
    # if agent_role == "dev_efficiency_analyst" and mcp_dev_efficiency:
    #     mcp_servers = {"dev_efficiency": mcp_dev_efficiency}

    try:
        while True:
            # 接收用户消息
            data = await websocket.receive_text()
            request_data = json.loads(data)

            message = request_data.get("message")
            if not message:
                await websocket.send_json({
                    "type": "error",
                    "error": "Message is required"
                })
                continue

            # 使用新的 Agent SDK 流式调用
            try:
                async for event in agent_service.execute_query(
                    prompt=message,
                    agent_role=agent_role,
                    mcp_servers=mcp_servers,
                ):
                    if event["type"] == "text_chunk":
                        await websocket.send_json({
                            "type": "chunk",
                            "content": event["content"]
                        })
                    elif event["type"] == "tool_use":
                        await websocket.send_json({
                            "type": "tool_use",
                            "tool_name": event["tool_name"],
                            "input": event.get("input", {})
                        })
                    elif event["type"] == "error":
                        await websocket.send_json({
                            "type": "error",
                            "error": event["error"]
                        })

                # 完成标记
                await websocket.send_json({
                    "type": "done"
                })

            except AgentSDKError as e:
                logger.error(f"Agent SDK error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })
            except Exception as e:
                logger.error(f"Unexpected error in chat: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from chat with {agent_role}")
    except Exception as e:
        logger.error(f"Error in chat websocket: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass


# ============================================
# 对话接口（HTTP SSE - 流式响应）
# ============================================

@app.post("/api/v1/chat/stream")
async def chat_stream_http(request: ChatRequest):
    """
    HTTP SSE流式对话

    使用 Claude Agent SDK 进行流式对话，支持 MCP 工具调用。
    """
    import asyncio
    
    # 获取 MCP 服务器
    # 注意：暂时禁用 MCP 服务器
    mcp_servers = None
    # if request.agent_role == "dev_efficiency_analyst" and mcp_dev_efficiency:
    #     mcp_servers = {"dev_efficiency": mcp_dev_efficiency}

    # 使用队列来传递事件
    queue: asyncio.Queue = asyncio.Queue()
    
    async def producer():
        """后台任务：执行 Agent 查询并将事件放入队列"""
        try:
            async for event in agent_service.execute_query(
                prompt=request.message,
                agent_role=request.agent_role,
                mcp_servers=mcp_servers,
            ):
                await queue.put(event)
            await queue.put({"type": "done"})
        except AgentNotFoundError as e:
            logger.error(f"Agent not found: {e}")
            await queue.put({"type": "error", "error": f"Agent not found: {request.agent_role}"})
        except AgentSDKError as e:
            logger.error(f"Agent SDK error: {e}")
            await queue.put({"type": "error", "error": str(e)})
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await queue.put({"type": "error", "error": str(e)})
        finally:
            await queue.put(None)  # 终止信号
    
    # 启动后台任务
    task = asyncio.create_task(producer())

    async def generate():
        """SSE 生成器"""
        try:
            while True:
                event = await queue.get()
                if event is None:
                    break
                
                if event["type"] == "text_chunk":
                    yield f"event: message\n"
                    yield f"data: {json.dumps({'content': event['content']})}\n\n"
                elif event["type"] == "tool_use":
                    yield f"event: tool_use\n"
                    yield f"data: {json.dumps({'tool': event['tool_name'], 'input': event.get('input', {})})}\n\n"
                elif event["type"] == "error":
                    yield f"event: error\n"
                    yield f"data: {json.dumps({'error': event['error']})}\n\n"
                elif event["type"] == "done":
                    yield f"event: done\n"
                    yield f"data: {json.dumps({})}\n\n"
                elif event["type"] == "result":
                    # 可以添加统计信息
                    pass
        except Exception as e:
            logger.error(f"SSE generate error: {e}")
            yield f"event: error\n"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


# ============================================
# 定时任务管理
# ============================================

@app.post("/api/v1/tasks/schedule")
async def schedule_task(request: ScheduledTaskRequest):
    """
    创建定时任务
    TODO: 实现定时调度逻辑（后续阶段）
    """
    return {
        "status": "scheduled",
        "agent_role": request.agent_role,
        "task": request.task_description,
        "interval": request.interval_seconds,
        "message": "Scheduled task feature will be implemented in next phase"
    }


@app.post("/api/v1/tasks/execute")
async def execute_task(request: ScheduledTaskRequest):
    """
    立即执行一次任务（用于测试）
    使用 Claude Agent SDK 执行任务。
    """
    # 获取 MCP 服务器
    # 注意：暂时禁用 MCP 服务器
    mcp_servers = None
    # if request.agent_role == "dev_efficiency_analyst" and mcp_dev_efficiency:
    #     mcp_servers = {"dev_efficiency": mcp_dev_efficiency}

    try:
        result_content = []
        async for event in agent_service.execute_query(
            prompt=request.task_description,
            agent_role=request.agent_role,
            mcp_servers=mcp_servers,
        ):
            if event["type"] == "text_chunk":
                result_content.append(event["content"])

        return {
            "status": "success",
            "agent_role": request.agent_role,
            "result": "".join(result_content)
        }
    except AgentSDKError as e:
        return {
            "status": "error",
            "agent_role": request.agent_role,
            "error": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "agent_role": request.agent_role,
            "error": str(e)
        }


# ============================================
# 启动配置
# ============================================

if __name__ == "__main__":
    import uvicorn

    # 检查环境变量
    auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
    if not auth_token:
        print("Warning: ANTHROPIC_AUTH_TOKEN not set!")
        print("   Please set it before running:")
        print('   export ANTHROPIC_AUTH_TOKEN="your-token"')

    base_url = os.getenv("ANTHROPIC_BASE_URL", "")
    if base_url:
        print(f"Using custom Anthropic base URL: {base_url}")

    print("\nStarting AI Agent Orchestrator v3.1...")
    print("Backend: Claude Agent SDK + APScheduler")
    print("Agent workspaces: backend/agents/")
    print("API docs: http://localhost:8000/docs")

    # Supabase状态
    if supabase_client:
        print("Supabase: connected")
    else:
        print("Supabase: not configured (briefings will not persist)")

    # 列出可用的 Agents
    agents = agent_service.list_agents()
    print(f"\nAvailable Agents ({len(agents)}):")
    for agent in agents:
        status = "[OK]" if agent["available"] else "[--]"
        print(f"   {status} {agent['name']} ({agent['role']})")
    print()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
