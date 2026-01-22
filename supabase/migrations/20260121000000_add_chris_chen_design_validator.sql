-- Migration: 添加 Chris Chen 设计评审员
-- 基于 Figma 设计稿定义
-- Date: 2026-01-21

-- 先删除旧的 design_validator (如果存在)
DELETE FROM agents WHERE role = 'design_validator';

-- 插入新的 Chris Chen 设计评审员
INSERT INTO agents (
  name,
  role,
  description,
  avatar_url,
  is_builtin,
  is_active,
  capabilities,
  trigger_conditions,
  data_sources,
  metadata
) VALUES (
  'Chris Chen',
  'design_validator',
  '身经百战，眼光如炬的设计老法师',
  NULL,
  true,
  true,
  '{
    "can_analyze_designs": true,
    "can_validate_interactions": true,
    "can_check_visual_consistency": true,
    "can_compare_designs": true,
    "can_search_cases": true,
    "multimodal": true
  }'::jsonb,
  '{
    "supported_file_types": ["image/png", "image/jpeg", "image/webp"]
  }'::jsonb,
  '{
    "knowledge_base": {"enabled": true}
  }'::jsonb,
  '{
    "version": "1.0",
    "category": "design",
    "figma_name": "Chris Chen",
    "figma_description": "身经百战，眼光如炬的设计老法师"
  }'::jsonb
);

-- 验证插入结果
DO $$
DECLARE
  agent_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO agent_count FROM agents WHERE role = 'design_validator';
  IF agent_count = 1 THEN
    RAISE NOTICE '✅ Chris Chen 设计评审员已添加成功';
  ELSE
    RAISE WARNING '❌ Chris Chen 设计评审员添加异常，当前数量: %', agent_count;
  END IF;
END $$;
