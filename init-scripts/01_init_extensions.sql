-- NeuralNote 数据库初始化脚本
-- 创建必要的扩展

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 启用 PgVector 扩展（用于向量搜索）
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证扩展安装
SELECT extname, extversion FROM pg_extension WHERE extname IN ('uuid-ossp', 'vector');

-- 输出提示信息
DO $$
BEGIN
    RAISE NOTICE '✅ PostgreSQL 扩展安装完成';
    RAISE NOTICE '   - uuid-ossp: UUID 生成';
    RAISE NOTICE '   - vector: 向量搜索（PgVector）';
END $$;

