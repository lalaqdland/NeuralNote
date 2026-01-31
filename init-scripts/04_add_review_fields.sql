-- 添加复习相关字段到 memory_nodes 表
-- 执行时间：2026-01-31

-- 添加 user_id 字段
ALTER TABLE memory_nodes 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- 为现有数据设置 user_id（从 created_by 复制）
UPDATE memory_nodes 
SET user_id = created_by 
WHERE user_id IS NULL AND created_by IS NOT NULL;

-- 为没有 created_by 的记录，从 knowledge_graphs 获取 user_id
UPDATE memory_nodes mn
SET user_id = kg.user_id
FROM knowledge_graphs kg
WHERE mn.graph_id = kg.id AND mn.user_id IS NULL;

-- 设置 user_id 为 NOT NULL
ALTER TABLE memory_nodes 
ALTER COLUMN user_id SET NOT NULL;

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_memory_nodes_user_id ON memory_nodes(user_id);

-- 添加掌握程度字段
ALTER TABLE memory_nodes 
ADD COLUMN IF NOT EXISTS mastery_level VARCHAR(20) DEFAULT 'not_started';

-- 添加复习时间字段
ALTER TABLE memory_nodes 
ADD COLUMN IF NOT EXISTS last_review_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE memory_nodes 
ADD COLUMN IF NOT EXISTS next_review_at TIMESTAMP WITH TIME ZONE;

-- 添加索引以优化复习查询
CREATE INDEX IF NOT EXISTS idx_memory_nodes_mastery_level ON memory_nodes(mastery_level);
CREATE INDEX IF NOT EXISTS idx_memory_nodes_next_review_at ON memory_nodes(next_review_at);

-- 更新现有数据的 review_stats 字段（如果为旧格式）
UPDATE memory_nodes 
SET review_stats = '{}'::jsonb 
WHERE review_stats IS NULL 
   OR review_stats = '{
       "last_reviewed_at": null,
       "next_review_due": null,
       "review_count": 0,
       "forgetting_curve_index": 100,
       "mastery_status": "FRESH"
   }'::jsonb;

-- 添加注释
COMMENT ON COLUMN memory_nodes.user_id IS '用户ID';
COMMENT ON COLUMN memory_nodes.mastery_level IS '掌握程度：not_started, learning, familiar, proficient, mastered';
COMMENT ON COLUMN memory_nodes.last_review_at IS '上次复习时间';
COMMENT ON COLUMN memory_nodes.next_review_at IS '下次复习时间';

