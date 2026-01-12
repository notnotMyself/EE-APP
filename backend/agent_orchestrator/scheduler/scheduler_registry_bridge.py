"""
Scheduler Registry Bridge - 桥接 AgentRegistry 和 Scheduler

负责从 agent.yaml 加载定时任务配置，并注册到 APScheduler。
"""

import logging
from typing import Any, Dict, List
import hashlib

from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class SchedulerRegistryBridge:
    """AgentRegistry 和 Scheduler 之间的桥接器"""

    def __init__(self, agent_registry, scheduler_service):
        """
        初始化桥接器

        Args:
            agent_registry: AgentRegistry 实例
            scheduler_service: SchedulerService 实例
        """
        self.agent_registry = agent_registry
        self.scheduler_service = scheduler_service
        self.registered_jobs = {}  # {job_id: {agent_id, schedule_config}}

    async def load_jobs_from_yaml(self):
        """
        从所有 agent.yaml 加载定时任务配置

        遍历所有注册的 Agent，读取其 agent.yaml 中的 schedule 配置，
        并将其注册到 APScheduler。
        """
        if not self.scheduler_service.scheduler:
            raise RuntimeError("Scheduler not initialized")

        total_jobs = 0
        total_agents = 0

        for agent in self.agent_registry.list_agents():
            agent_id = agent.id
            schedules = agent.config.schedule

            if not schedules:
                logger.debug(f"Agent {agent_id} has no scheduled tasks")
                continue

            total_agents += 1

            for schedule_config in schedules:
                if not schedule_config.enabled:
                    logger.debug(
                        f"Skipping disabled schedule for agent {agent_id}: {schedule_config.task}"
                    )
                    continue

                try:
                    await self._register_schedule(agent, schedule_config)
                    total_jobs += 1
                except Exception as e:
                    logger.error(
                        f"Failed to register schedule for agent {agent_id}: {e}"
                    )

        logger.info(
            f"Loaded {total_jobs} scheduled jobs from {total_agents} agents (agent.yaml)"
        )

    async def _register_schedule(self, agent, schedule_config):
        """
        注册单个 Agent 的定时任务

        Args:
            agent: RegisteredAgent 实例
            schedule_config: AgentSchedule 实例
        """
        # 生成唯一的 job_id（基于 agent_id 和任务描述）
        job_id = self._generate_job_id(agent.id, schedule_config.task)

        # 解析 cron 表达式
        trigger = CronTrigger.from_crontab(
            schedule_config.cron,
            timezone="Asia/Shanghai"
        )

        # 从 AgentRegistry 获取 Agent UUID
        agent_uuid = agent.uuid

        # 构建任务参数
        job_kwargs = {
            "job_id": job_id,
            "agent_id": agent_uuid,  # JobExecutor 期望的是 UUID
            "task_prompt": schedule_config.task,
            "briefing_config": {},
            "target_user_ids": None,
            "source": "agent_yaml"  # 标记来源
        }

        # 添加到调度器
        self.scheduler_service.scheduler.add_job(
            func=self.scheduler_service._job_executor.execute,
            trigger=trigger,
            id=job_id,
            name=f"{agent.name} - {schedule_config.task}",
            kwargs=job_kwargs,
            replace_existing=True
        )

        # 记录已注册的任务
        self.registered_jobs[job_id] = {
            "agent_id": agent.id,
            "agent_uuid": agent_uuid,
            "agent_name": agent.name,
            "task": schedule_config.task,
            "cron": schedule_config.cron,
            "enabled": schedule_config.enabled,
            "source": "agent_yaml"
        }

        logger.info(
            f"Registered scheduled job from YAML: {agent.name} - {schedule_config.task} "
            f"({job_id})"
        )

    def _generate_job_id(self, agent_id: str, task: str) -> str:
        """
        生成唯一的 job_id

        使用 agent_id 和 task 的哈希值生成，确保同一 Agent 的同一任务总是得到相同的 ID。

        Args:
            agent_id: Agent ID
            task: 任务描述

        Returns:
            job_id string
        """
        # 使用哈希确保唯一性和一致性
        content = f"{agent_id}:{task}"
        hash_digest = hashlib.md5(content.encode()).hexdigest()[:16]
        return f"yaml_{agent_id}_{hash_digest}"

    def get_yaml_jobs(self) -> List[Dict[str, Any]]:
        """
        获取所有来自 agent.yaml 的定时任务

        Returns:
            任务列表
        """
        return [
            {
                "job_id": job_id,
                **job_info
            }
            for job_id, job_info in self.registered_jobs.items()
        ]

    async def reload_jobs(self):
        """
        重新加载所有 agent.yaml 中的定时任务

        先移除现有的 YAML 任务，然后重新加载。
        """
        # 移除所有来自 YAML 的任务
        for job_id in list(self.registered_jobs.keys()):
            try:
                self.scheduler_service.scheduler.remove_job(job_id)
                logger.info(f"Removed job for reload: {job_id}")
            except Exception as e:
                logger.warning(f"Failed to remove job {job_id}: {e}")

        self.registered_jobs.clear()

        # 重新加载 AgentRegistry
        self.agent_registry.reload()

        # 重新加载任务
        await self.load_jobs_from_yaml()

    def get_job_info(self, job_id: str) -> Dict[str, Any]:
        """
        获取指定 job 的信息

        Args:
            job_id: Job ID

        Returns:
            Job 信息字典，如果不存在返回 None
        """
        return self.registered_jobs.get(job_id)


async def integrate_yaml_schedules(scheduler_service, agent_registry):
    """
    集成 agent.yaml 中的定时任务到 Scheduler

    这是一个便捷函数，用于在 Scheduler 启动时自动加载 agent.yaml 中的定时任务。

    Args:
        scheduler_service: SchedulerService 实例
        agent_registry: AgentRegistry 实例

    Returns:
        SchedulerRegistryBridge 实例
    """
    bridge = SchedulerRegistryBridge(agent_registry, scheduler_service)
    await bridge.load_jobs_from_yaml()
    return bridge


if __name__ == "__main__":
    # 测试代码
    import asyncio
    from pathlib import Path
    import sys

    # 添加父目录到 path
    sys.path.insert(0, str(Path(__file__).parent))

    from agent_registry import AgentRegistry

    async def test():
        # 初始化 AgentRegistry
        agents_dir = Path(__file__).parent.parent / "agents"
        registry = AgentRegistry(agents_dir)

        print("=" * 60)
        print("Scheduler Registry Bridge Test")
        print("=" * 60)

        # 打印所有 Agent 的 schedule 配置
        print("\n📋 Agent Schedules:")
        for agent in registry.list_agents():
            print(f"\n  • {agent.name} ({agent.id})")
            if agent.config.schedule:
                for sched in agent.config.schedule:
                    status = "✅" if sched.enabled else "❌"
                    print(f"    {status} Cron: {sched.cron}")
                    print(f"       Task: {sched.task}")
            else:
                print("    (No scheduled tasks)")

    asyncio.run(test())
