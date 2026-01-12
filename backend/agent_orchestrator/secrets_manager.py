"""
Secrets Manager - 密钥管理

负责安全地管理和提供 Agent 运行时需要的密钥。
"""

import logging
import os
from typing import Any, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SecretsManager:
    """密钥管理器"""

    def __init__(self, supabase_client: Optional[Any] = None):
        """
        初始化密钥管理器

        Args:
            supabase_client: 可选的 Supabase 客户端（用于从数据库读取密钥）
        """
        self.supabase = supabase_client
        self._cache = {}  # 密钥缓存

    def get_secret(self, name: str, source: str = "env", key: Optional[str] = None) -> Optional[str]:
        """
        获取密钥

        Args:
            name: 密钥名称（环境变量名或缓存键）
            source: 密钥来源（env | supabase_secrets）
            key: supabase_secrets 时的 key 名称

        Returns:
            密钥值，如果不存在返回 None
        """
        # 检查缓存
        cache_key = f"{source}:{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 根据来源获取密钥
        secret_value = None

        if source == "env":
            secret_value = os.getenv(name)
        elif source == "supabase_secrets":
            secret_value = self._get_from_supabase(key or name)
        else:
            logger.warning(f"Unknown secret source: {source}")

        # 缓存密钥
        if secret_value:
            self._cache[cache_key] = secret_value

        return secret_value

    def _get_from_supabase(self, key: str) -> Optional[str]:
        """
        从 Supabase 密钥表读取密钥

        Args:
            key: 密钥 key

        Returns:
            密钥值，如果不存在返回 None
        """
        if not self.supabase:
            logger.warning("Supabase client not configured, cannot fetch secrets")
            return None

        try:
            result = (
                self.supabase.table("secrets")
                .select("value")
                .eq("key", key)
                .single()
                .execute()
            )

            if result.data:
                return result.data.get("value")

        except Exception as e:
            logger.error(f"Failed to fetch secret from Supabase: {key} - {e}")

        return None

    def load_agent_secrets(self, agent_config) -> Dict[str, str]:
        """
        加载 Agent 配置中声明的所有密钥

        Args:
            agent_config: AgentYamlConfig 实例

        Returns:
            密钥字典 {ENV_VAR_NAME: value}
        """
        secrets = {}

        for secret_config in agent_config.secrets:
            value = self.get_secret(
                name=secret_config.name,
                source=secret_config.source,
                key=secret_config.key
            )

            if value:
                secrets[secret_config.name] = value
            else:
                logger.warning(
                    f"Secret not found: {secret_config.name} "
                    f"(source: {secret_config.source})"
                )

        return secrets

    def inject_secrets_to_env(self, secrets: Dict[str, str]):
        """
        将密钥注入到环境变量

        Args:
            secrets: 密钥字典 {ENV_VAR_NAME: value}
        """
        for name, value in secrets.items():
            os.environ[name] = value
            logger.debug(f"Injected secret to env: {name}")

    def clear_cache(self):
        """清空密钥缓存"""
        self._cache.clear()
        logger.info("Secrets cache cleared")


# 全局单例
_global_secrets_manager: Optional[SecretsManager] = None


def get_global_secrets_manager() -> SecretsManager:
    """获取全局 Secrets Manager 单例"""
    global _global_secrets_manager
    if _global_secrets_manager is None:
        _global_secrets_manager = SecretsManager()
    return _global_secrets_manager


def init_global_secrets_manager(supabase_client: Optional[Any] = None):
    """
    初始化全局 Secrets Manager

    Args:
        supabase_client: Supabase 客户端实例
    """
    global _global_secrets_manager
    _global_secrets_manager = SecretsManager(supabase_client)
    return _global_secrets_manager


if __name__ == "__main__":
    # 测试代码
    import sys

    # 设置测试环境变量
    os.environ["TEST_SECRET"] = "test_value_123"

    manager = SecretsManager()

    print("=" * 60)
    print("Secrets Manager Test")
    print("=" * 60)

    # 测试从环境变量获取
    value = manager.get_secret("TEST_SECRET", source="env")
    print(f"\n✅ get_secret('TEST_SECRET') = {value}")

    # 测试缓存
    value2 = manager.get_secret("TEST_SECRET", source="env")
    print(f"✅ get_secret('TEST_SECRET') [cached] = {value2}")

    # 测试不存在的密钥
    value3 = manager.get_secret("NONEXISTENT_SECRET", source="env")
    print(f"✅ get_secret('NONEXISTENT_SECRET') = {value3}")

    print("\n✅ All tests passed!")
