"""
Agent Management API - 在EE App中创建和管理AI员工
"""

import logging
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, Field

from skill_templates import get_all_templates, generate_skill_script

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/agents", tags=["agent-management"])


# ============================================
# Request/Response Models
# ============================================

class SkillDefinition(BaseModel):
    """技能定义"""
    name: str = Field(..., description="技能名称")
    entry: str = Field(..., description="入口文件路径（相对于.claude/skills/）")
    script_content: str = Field(..., description="Python脚本内容")
    timeout: int = Field(default=300, description="超时时间（秒）")
    description: str = Field(default="", description="技能描述")


class ScheduleDefinition(BaseModel):
    """定时任务定义"""
    cron: str = Field(..., description="Cron表达式")
    skill: str = Field(..., description="要执行的技能名称")
    description: str = Field(default="", description="任务描述")
    enabled: bool = Field(default=True, description="是否启用")


class CreateAgentRequest(BaseModel):
    """创建Agent请求"""
    name: str = Field(..., description="Agent中文名称")
    agent_id: str = Field(..., description="Agent ID（英文，唯一）")
    description: str = Field(..., description="职责描述")
    visibility: str = Field(default="public", description="可见性（public/private）")
    claude_md_content: str = Field(..., description="CLAUDE.md文件内容（角色定义）")
    skills: List[SkillDefinition] = Field(default=[], description="技能列表")
    schedule: List[ScheduleDefinition] = Field(default=[], description="定时任务列表")
    allowed_tools: List[str] = Field(
        default=["Read", "Write", "Bash"],
        description="允许的工具列表"
    )
    secrets: List[Dict[str, str]] = Field(default=[], description="密钥列表")
    max_turns: int = Field(default=20, description="最大轮次限制")
    model: str = Field(default="saas/claude-sonnet-4.5", description="使用的模型")


class CreateAgentResponse(BaseModel):
    """创建Agent响应"""
    success: bool
    agent_id: str
    uuid: str
    message: str


class TestAgentRequest(BaseModel):
    """测试Agent请求"""
    test_prompt: str = Field(..., description="测试提示词")


class TestAgentResponse(BaseModel):
    """测试Agent响应"""
    success: bool
    response: str
    execution_time: float


# ============================================
# API Endpoints
# ============================================

@router.post("/create", response_model=CreateAgentResponse)
async def create_agent(request: CreateAgentRequest):
    """
    创建新的AI员工

    流程:
    1. 生成UUID
    2. 创建目录结构
    3. 生成 agent.yaml
    4. 写入 CLAUDE.md
    5. 写入 Skills 脚本
    6. 注册到数据库
    7. 重新加载 AgentRegistry
    """
    try:
        # 1. 生成UUID
        agent_uuid = str(uuid4())

        # 2. 创建目录结构
        agents_base_dir = Path(__file__).parent.parent.parent / "agents"
        agent_dir = agents_base_dir / request.agent_id

        if agent_dir.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Agent ID '{request.agent_id}' already exists"
            )

        agent_dir.mkdir(parents=True, exist_ok=True)
        (agent_dir / ".claude" / "skills").mkdir(parents=True, exist_ok=True)
        (agent_dir / "data").mkdir(exist_ok=True)
        (agent_dir / "reports").mkdir(exist_ok=True)

        logger.info(f"Created directory structure for agent {request.agent_id}")

        # 3. 生成 agent.yaml
        agent_yaml = {
            "metadata": {
                "id": request.agent_id,
                "uuid": agent_uuid,
                "name": request.name,
                "description": request.description,
                "model": request.model,
                "visibility": request.visibility,
                "created_via": "app",
                "created_at": datetime.now().isoformat(),
            },
            "skills": [
                {
                    "name": skill.name,
                    "entry": f".claude/skills/{skill.entry}",
                    "description": skill.description,
                    "timeout": skill.timeout,
                }
                for skill in request.skills
            ],
            "schedule": [
                {
                    "cron": schedule.cron,
                    "skill": schedule.skill,
                    "description": schedule.description,
                    "enabled": schedule.enabled,
                }
                for schedule in request.schedule
            ],
            "allowed_tools": request.allowed_tools,
            "secrets": request.secrets,
            "max_turns": request.max_turns,
        }

        with open(agent_dir / "agent.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(agent_yaml, f, allow_unicode=True, default_flow_style=False)

        logger.info(f"Generated agent.yaml for {request.agent_id}")

        # 4. 写入 CLAUDE.md
        with open(agent_dir / "CLAUDE.md", 'w', encoding='utf-8') as f:
            f.write(request.claude_md_content)

        logger.info(f"Wrote CLAUDE.md for {request.agent_id}")

        # 5. 写入 Skills 脚本
        for skill in request.skills:
            skill_path = agent_dir / ".claude" / "skills" / skill.entry
            skill_path.parent.mkdir(parents=True, exist_ok=True)

            with open(skill_path, 'w', encoding='utf-8') as f:
                f.write(skill.script_content)

            # 设置可执行权限
            os.chmod(skill_path, 0o755)

            logger.info(f"Wrote skill script: {skill.entry}")

        # 6. 注册到数据库
        # TODO: 集成Supabase客户端
        # await supabase.table("agents").insert({
        #     "id": agent_uuid,
        #     "name": request.name,
        #     "role": request.agent_id,
        #     "description": request.description,
        #     "is_builtin": True,
        #     "is_active": True,
        #     "visibility": request.visibility,
        #     "metadata": {
        #         "agent_yaml_path": str(agent_dir / "agent.yaml"),
        #         "created_via": "app",
        #         "created_at": datetime.now().isoformat()
        #     }
        # }).execute()

        logger.info(f"Agent {request.agent_id} created successfully")

        # 7. 重新加载 AgentRegistry
        # TODO: 触发 AgentRegistry reload
        # await agent_registry.reload()

        return CreateAgentResponse(
            success=True,
            agent_id=request.agent_id,
            uuid=agent_uuid,
            message=f"Agent '{request.name}' created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.post("/{agent_id}/skills/upload")
async def upload_skill(
    agent_id: str,
    skill_name: str,
    file: UploadFile = File(...)
):
    """
    上传技能脚本
    """
    try:
        agents_base_dir = Path(__file__).parent.parent.parent / "agents"
        agent_dir = agents_base_dir / agent_id

        if not agent_dir.exists():
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        # 保存文件
        skill_path = agent_dir / ".claude" / "skills" / file.filename
        skill_path.parent.mkdir(parents=True, exist_ok=True)

        content = await file.read()
        with open(skill_path, 'wb') as f:
            f.write(content)

        # 设置可执行权限
        os.chmod(skill_path, 0o755)

        logger.info(f"Uploaded skill {file.filename} for agent {agent_id}")

        return {
            "success": True,
            "message": f"Skill '{file.filename}' uploaded successfully",
            "path": str(skill_path.relative_to(agent_dir))
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload skill: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/deploy")
async def deploy_agent(agent_id: str):
    """
    部署Agent（重新加载AgentRegistry）
    """
    try:
        agents_base_dir = Path(__file__).parent.parent.parent / "agents"
        agent_dir = agents_base_dir / agent_id

        if not agent_dir.exists():
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        # TODO: 触发 AgentRegistry reload
        # await agent_registry.reload()

        logger.info(f"Agent {agent_id} deployed successfully")

        return {
            "success": True,
            "message": f"Agent '{agent_id}' deployed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deploy agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/test", response_model=TestAgentResponse)
async def test_agent(agent_id: str, request: TestAgentRequest):
    """
    测试Agent对话
    """
    try:
        import time
        start_time = time.time()

        # TODO: 实际调用Agent进行测试对话
        # response = await agent_manager.process_message(
        #     agent_id=agent_id,
        #     user_id="test_user",
        #     message=request.test_prompt
        # )

        # 临时返回模拟响应
        test_response = f"[Test Mode] Agent '{agent_id}' received prompt: {request.test_prompt}"

        execution_time = time.time() - start_time

        return TestAgentResponse(
            success=True,
            response=test_response,
            execution_time=execution_time
        )

    except Exception as e:
        logger.error(f"Failed to test agent: {e}", exc_info=True)
        return TestAgentResponse(
            success=False,
            response=f"Error: {str(e)}",
            execution_time=0
        )


@router.get("/{agent_id}/info")
async def get_agent_info(agent_id: str):
    """
    获取Agent信息
    """
    try:
        agents_base_dir = Path(__file__).parent.parent.parent / "agents"
        agent_dir = agents_base_dir / agent_id

        if not agent_dir.exists():
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        # 读取agent.yaml
        with open(agent_dir / "agent.yaml", 'r', encoding='utf-8') as f:
            agent_yaml = yaml.safe_load(f)

        # 读取CLAUDE.md
        with open(agent_dir / "CLAUDE.md", 'r', encoding='utf-8') as f:
            claude_md = f.read()

        return {
            "agent_id": agent_id,
            "config": agent_yaml,
            "claude_md": claude_md,
            "directory": str(agent_dir)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """
    删除Agent
    """
    try:
        agents_base_dir = Path(__file__).parent.parent.parent / "agents"
        agent_dir = agents_base_dir / agent_id

        if not agent_dir.exists():
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        # 删除目录
        import shutil
        shutil.rmtree(agent_dir)

        # TODO: 从数据库删除
        # await supabase.table("agents").delete().eq("role", agent_id).execute()

        # TODO: 重新加载 AgentRegistry
        # await agent_registry.reload()

        logger.info(f"Agent {agent_id} deleted successfully")

        return {
            "success": True,
            "message": f"Agent '{agent_id}' deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Skill Templates (技能市场)
# ============================================

@router.get("/skill-templates")
async def list_skill_templates():
    """
    获取所有技能模板（技能市场）
    """
    try:
        templates = get_all_templates()
        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }
    except Exception as e:
        logger.error(f"Failed to list skill templates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class GenerateSkillRequest(BaseModel):
    """生成技能脚本请求"""
    template_name: str = Field(..., description="模板名称")
    parameters: Dict[str, Any] = Field(default={}, description="模板参数")


@router.post("/skill-templates/generate")
async def generate_skill_from_template(request: GenerateSkillRequest):
    """
    根据模板生成技能脚本
    """
    try:
        script = generate_skill_script(request.template_name, request.parameters)
        return {
            "success": True,
            "script": script,
            "template_name": request.template_name
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate skill: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
