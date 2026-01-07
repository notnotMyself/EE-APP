"""
Agent Manager - 支持真正工具执行的版本
实现Bash, Read, Write, WebFetch等工具，让AI真正能执行任务
"""

import os
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Optional, AsyncIterator, List, Any
from dataclasses import dataclass
import json
import httpx

try:
    from anthropic import AsyncAnthropic
except ImportError:
    print("⚠️  Warning: anthropic package not found")
    AsyncAnthropic = None


@dataclass
class AgentConfig:
    """AI员工配置"""
    name: str
    role: str
    workdir: Path
    description: str


class AgentManager:
    """AI员工管理器 - 支持真正的工具执行"""

    def __init__(self, agents_base_dir: str = None):
        if agents_base_dir is None:
            current_file = Path(__file__).resolve()
            self.agents_base_dir = current_file.parent.parent / "agents"
        else:
            self.agents_base_dir = Path(agents_base_dir)

        self.agents: Dict[str, AgentConfig] = self._register_agents()
        self._init_claude_client()

        # HTTP客户端用于WebFetch
        self.http_client = httpx.AsyncClient(timeout=30.0)

    def _init_claude_client(self):
        """初始化Claude API客户端"""
        auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
        base_url = os.getenv("ANTHROPIC_BASE_URL")

        if not auth_token or AsyncAnthropic is None:
            self.claude_client = None
            return

        if base_url:
            self.claude_client = AsyncAnthropic(
                auth_token=auth_token,
                base_url=base_url
            )
        else:
            self.claude_client = AsyncAnthropic(auth_token=auth_token)

        self.model = os.getenv("ANTHROPIC_MODEL", "saas/claude-sonnet-4.5")
        print(f"✅ Claude client initialized with model: {self.model}")

    def _register_agents(self) -> Dict[str, AgentConfig]:
        """注册所有AI员工"""
        return {
            "dev_efficiency_analyst": AgentConfig(
                name="研发效能分析官",
                role="dev_efficiency_analyst",
                workdir=self.agents_base_dir / "dev_efficiency_analyst",
                description="持续监控团队研发效率，分析代码审查数据，检测异常趋势"
            ),
            "nps_insight_analyst": AgentConfig(
                name="NPS洞察官",
                role="nps_insight_analyst",
                workdir=self.agents_base_dir / "nps_insight_analyst",
                description="分析用户满意度数据，提取用户痛点，识别改进机会"
            ),
            "product_requirement_analyst": AgentConfig(
                name="产品需求提炼官",
                role="product_requirement_analyst",
                workdir=self.agents_base_dir / "product_requirement_analyst",
                description="帮助提炼和分析产品需求，确保需求清晰可执行"
            ),
            "competitor_tracking_analyst": AgentConfig(
                name="竞品追踪分析官",
                role="competitor_tracking_analyst",
                workdir=self.agents_base_dir / "competitor_tracking_analyst",
                description="追踪竞品动态，分析市场趋势，提供竞争洞察"
            ),
            "knowledge_management_assistant": AgentConfig(
                name="企业知识管理官",
                role="knowledge_management_assistant",
                workdir=self.agents_base_dir / "knowledge_management_assistant",
                description="组织和管理企业知识，帮助团队高效获取信息"
            ),
        }

    def get_agent_config(self, role: str) -> Optional[AgentConfig]:
        """获取AI员工配置"""
        return self.agents.get(role)

    def _load_agent_instructions(self, agent_config: AgentConfig) -> str:
        """加载Agent的CLAUDE.md作为系统指令"""
        claude_md_path = agent_config.workdir / "CLAUDE.md"

        if not claude_md_path.exists():
            return f"""你是{agent_config.name}。

职责：{agent_config.description}

请根据用户的问题提供专业的回答和建议。"""

        try:
            with open(claude_md_path, 'r', encoding='utf-8') as f:
                instructions = f.read()
            return instructions
        except Exception as e:
            print(f"Error loading CLAUDE.md for {agent_config.role}: {e}")
            return f"你是{agent_config.name}。"

    def _get_tools(self) -> List[Dict[str, Any]]:
        """
        定义AI可用的工具
        这是真正的Agent能力！
        """
        return [
            {
                "name": "bash",
                "description": """Execute bash commands in the agent's working directory.
                Use this to:
                - Run Python scripts (e.g., python3 .claude/skills/gerrit_analysis.py)
                - Execute data analysis tasks
                - Generate reports
                - Process files

                The command will be executed in the agent's isolated working directory.""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute"
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "read_file",
                "description": """Read the contents of a file in the agent's working directory.
                Use this to:
                - Read data files
                - Check analysis results
                - Load cached data

                File path is relative to the agent's working directory.""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file relative to working directory"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "write_file",
                "description": """Write content to a file in the agent's working directory.
                Use this to:
                - Save analysis results
                - Create reports
                - Store processed data

                File path is relative to the agent's working directory.""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file relative to working directory"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            },
            {
                "name": "web_fetch",
                "description": """Fetch content from a URL (e.g., API endpoints, web pages).
                Use this to:
                - Get data from Gerrit/Jira APIs
                - Fetch external data sources
                - Access web resources""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to fetch"
                        }
                    },
                    "required": ["url"]
                }
            }
        ]

    async def _execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        agent_workdir: Path
    ) -> str:
        """
        执行工具调用
        这是Agent能力的核心实现！
        """
        try:
            if tool_name == "bash":
                return await self._tool_bash(tool_input["command"], agent_workdir)

            elif tool_name == "read_file":
                return await self._tool_read_file(tool_input["file_path"], agent_workdir)

            elif tool_name == "write_file":
                return await self._tool_write_file(
                    tool_input["file_path"],
                    tool_input["content"],
                    agent_workdir
                )

            elif tool_name == "web_fetch":
                return await self._tool_web_fetch(tool_input["url"])

            else:
                return f"Error: Unknown tool '{tool_name}'"

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return f"Error executing {tool_name}: {str(e)}\n\n{error_detail}"

    async def _tool_bash(self, command: str, workdir: Path) -> str:
        """执行bash命令"""
        print(f"🔧 Executing bash: {command} in {workdir}")

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(workdir)
            )

            stdout, stderr = await process.communicate()

            result = stdout.decode('utf-8')
            if stderr:
                result += f"\n[stderr]: {stderr.decode('utf-8')}"

            if process.returncode != 0:
                result += f"\n[exit code]: {process.returncode}"

            print(f"✅ Bash result: {result[:200]}...")
            return result

        except Exception as e:
            return f"Failed to execute command: {str(e)}"

    async def _tool_read_file(self, file_path: str, workdir: Path) -> str:
        """读取文件"""
        full_path = workdir / file_path
        print(f"📖 Reading file: {full_path}")

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Read {len(content)} bytes")
            return content
        except Exception as e:
            return f"Failed to read file: {str(e)}"

    async def _tool_write_file(self, file_path: str, content: str, workdir: Path) -> str:
        """写入文件"""
        full_path = workdir / file_path
        print(f"✍️  Writing file: {full_path}")

        try:
            # 确保目录存在
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Wrote {len(content)} bytes")
            return f"Successfully wrote {len(content)} bytes to {file_path}"
        except Exception as e:
            return f"Failed to write file: {str(e)}"

    async def _tool_web_fetch(self, url: str) -> str:
        """获取Web内容"""
        print(f"🌐 Fetching: {url}")

        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            content = response.text
            print(f"✅ Fetched {len(content)} bytes")
            return content[:10000]  # 限制返回大小
        except Exception as e:
            return f"Failed to fetch URL: {str(e)}"

    async def chat_with_agent(
        self,
        role: str,
        message: str,
        conversation_history: list = None
    ) -> AsyncIterator[str]:
        """
        与AI员工对话（支持真正的工具执行）
        """
        agent_config = self.get_agent_config(role)
        if not agent_config:
            yield f"Error: Unknown agent role: {role}"
            return

        if not agent_config.workdir.exists():
            yield f"Error: Agent workdir not found: {agent_config.workdir}"
            return

        if self.claude_client is None:
            yield "Error: Claude client not initialized."
            return

        try:
            # 加载系统指令
            system_prompt = self._load_agent_instructions(agent_config)

            # 构建消息历史
            messages = []
            if conversation_history:
                for msg in conversation_history[-10:]:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })

            messages.append({
                "role": "user",
                "content": message
            })

            # 获取可用工具
            tools = self._get_tools()

            # 开始对话循环（支持多轮工具调用）
            while True:
                # 调用Claude API
                response = await self.claude_client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system_prompt,
                    messages=messages,
                    tools=tools
                )

                # 处理响应
                tool_uses = []
                text_content = []

                for block in response.content:
                    if block.type == "text":
                        text_content.append(block.text)
                        yield block.text
                    elif block.type == "tool_use":
                        tool_uses.append(block)

                # 如果没有工具调用，结束
                if not tool_uses:
                    break

                # 执行工具调用
                print(f"\n🔧 AI requested {len(tool_uses)} tool calls")

                # 将AI的响应添加到历史
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # 执行所有工具调用
                tool_results = []
                for tool_use in tool_uses:
                    print(f"  → {tool_use.name}({tool_use.input})")

                    result = await self._execute_tool(
                        tool_use.name,
                        tool_use.input,
                        agent_config.workdir
                    )

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result
                    })

                # 将工具结果添加到历史
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # 继续下一轮对话（AI会根据工具结果继续回复）

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Error in chat_with_agent: {error_detail}")
            yield f"\n\nError: {str(e)}"

    async def execute_scheduled_task(
        self,
        role: str,
        task_description: str
    ) -> Dict[str, any]:
        """执行定时任务"""
        agent_config = self.get_agent_config(role)
        if not agent_config:
            return {"error": f"Unknown agent role: {role}"}

        try:
            result_chunks = []
            async for chunk in self.chat_with_agent(role, task_description):
                result_chunks.append(chunk)

            return {
                "status": "success",
                "agent": agent_config.name,
                "result": "".join(result_chunks)
            }
        except Exception as e:
            return {
                "status": "error",
                "agent": agent_config.name,
                "error": str(e)
            }

    def list_agents(self) -> list:
        """列出所有可用的AI员工"""
        return [
            {
                "role": config.role,
                "name": config.name,
                "description": config.description,
                "workdir": str(config.workdir)
            }
            for config in self.agents.values()
        ]


# 全局agent管理器实例
agent_manager = AgentManager()
