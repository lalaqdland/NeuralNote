-- NeuralNote 数据库表结构创建脚本
-- 基于 API_Design.md 中的数据库设计

-- ==================== 用户表 ====================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    language VARCHAR(10) DEFAULT 'zh-CN',
    subscription_plan VARCHAR(20) DEFAULT 'free',
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE
);

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_plan);

COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.subscription_plan IS '订阅计划: free, pro_monthly, pro_yearly, team';

-- ==================== 知识图谱表 ====================
CREATE TABLE IF NOT EXISTS knowledge_graphs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    subject VARCHAR(50),
    cover_image_url VARCHAR(500),
    is_public BOOLEAN DEFAULT FALSE,
    is_preset BOOLEAN DEFAULT FALSE,
    node_count INTEGER DEFAULT 0,
    edge_count INTEGER DEFAULT 0,
    total_review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE
);

-- 知识图谱表索引
CREATE INDEX IF NOT EXISTS idx_graphs_user ON knowledge_graphs(user_id);
CREATE INDEX IF NOT EXISTS idx_graphs_subject ON knowledge_graphs(subject);
CREATE INDEX IF NOT EXISTS idx_graphs_public ON knowledge_graphs(is_public);

COMMENT ON TABLE knowledge_graphs IS '知识图谱表';
COMMENT ON COLUMN knowledge_graphs.subject IS '学科分类: math, physics, cs, etc.';
COMMENT ON COLUMN knowledge_graphs.is_preset IS '是否为公有云预设图谱';

-- ==================== 记忆节点表 ====================
CREATE TABLE IF NOT EXISTS memory_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    graph_id UUID NOT NULL REFERENCES knowledge_graphs(id) ON DELETE CASCADE,
    node_type VARCHAR(20) NOT NULL DEFAULT 'QUESTION',
    title VARCHAR(200) NOT NULL,
    summary TEXT,
    
    -- 灵活的内容数据 (JSONB)
    content_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- 向量嵌入 (用于语义搜索)
    content_embedding vector(1536),
    
    -- 图谱位置信息
    position_x FLOAT DEFAULT 0,
    position_y FLOAT DEFAULT 0,
    position_z FLOAT DEFAULT 0,
    
    -- 复习状态
    review_stats JSONB NOT NULL DEFAULT '{
        "last_reviewed_at": null,
        "next_review_due": null,
        "review_count": 0,
        "forgetting_curve_index": 100,
        "mastery_status": "FRESH"
    }'::jsonb,
    
    -- 元数据
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 记忆节点表索引
CREATE INDEX IF NOT EXISTS idx_nodes_graph ON memory_nodes(graph_id);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON memory_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_content ON memory_nodes USING gin (content_data);
CREATE INDEX IF NOT EXISTS idx_nodes_review ON memory_nodes USING btree ((review_stats->>'next_review_due'));

COMMENT ON TABLE memory_nodes IS '记忆节点表（核心实体）';
COMMENT ON COLUMN memory_nodes.node_type IS '节点类型: QUESTION, CONCEPT, SNIPPET, INSIGHT';
COMMENT ON COLUMN memory_nodes.content_data IS '灵活的内容数据，不同类型节点存储不同结构';
COMMENT ON COLUMN memory_nodes.content_embedding IS '1536维向量，用于语义搜索';

-- ==================== 知识点标签表 ====================
CREATE TABLE IF NOT EXISTS knowledge_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    graph_id UUID NOT NULL REFERENCES knowledge_graphs(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES knowledge_tags(id),
    color VARCHAR(20) DEFAULT '#1890FF',
    icon VARCHAR(50),
    importance_score FLOAT DEFAULT 50.0,
    mastery_rate FLOAT DEFAULT 0.0,
    node_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_tag_name UNIQUE (graph_id, name, parent_id)
);

-- 知识点标签表索引
CREATE INDEX IF NOT EXISTS idx_tags_graph ON knowledge_tags(graph_id);
CREATE INDEX IF NOT EXISTS idx_tags_parent ON knowledge_tags(parent_id);

COMMENT ON TABLE knowledge_tags IS '知识点标签表';
COMMENT ON COLUMN knowledge_tags.mastery_rate IS '该知识点的整体掌握率';

-- ==================== 节点-标签关联表 ====================
CREATE TABLE IF NOT EXISTS node_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id UUID NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES knowledge_tags(id) ON DELETE CASCADE,
    confidence FLOAT DEFAULT 1.0,
    is_manual BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_node_tag UNIQUE (node_id, tag_id)
);

-- 节点-标签关联表索引
CREATE INDEX IF NOT EXISTS idx_node_tags_node ON node_tags(node_id);
CREATE INDEX IF NOT EXISTS idx_node_tags_tag ON node_tags(tag_id);

COMMENT ON TABLE node_tags IS '节点-标签关联表';
COMMENT ON COLUMN node_tags.confidence IS 'AI推荐的置信度';
COMMENT ON COLUMN node_tags.is_manual IS '是否用户手动添加';

-- ==================== 节点关联表 ====================
CREATE TABLE IF NOT EXISTS node_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    graph_id UUID NOT NULL REFERENCES knowledge_graphs(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
    relation_type VARCHAR(20) NOT NULL,
    strength INTEGER DEFAULT 50,
    is_auto_generated BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_relation UNIQUE (source_id, target_id, relation_type)
);

-- 节点关联表索引
CREATE INDEX IF NOT EXISTS idx_relations_graph ON node_relations(graph_id);
CREATE INDEX IF NOT EXISTS idx_relations_source ON node_relations(source_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON node_relations(target_id);
CREATE INDEX IF NOT EXISTS idx_relations_type ON node_relations(relation_type);

COMMENT ON TABLE node_relations IS '节点关联表';
COMMENT ON COLUMN node_relations.relation_type IS '关联类型: PREREQUISITE, VARIANT, RELATED';
COMMENT ON COLUMN node_relations.strength IS '关联强度 0-100';

-- ==================== 视图配置表 ====================
CREATE TABLE IF NOT EXISTS view_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    graph_id UUID NOT NULL REFERENCES knowledge_graphs(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    view_type VARCHAR(20) NOT NULL DEFAULT 'custom',
    
    -- 过滤配置
    filter_config JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- 布局配置
    layout_engine VARCHAR(50) DEFAULT 'force-directed',
    layout_params JSONB DEFAULT '{}'::jsonb,
    
    -- 视觉配置
    color_scheme VARCHAR(50) DEFAULT 'fresh-modern',
    node_size_mode VARCHAR(20) DEFAULT 'fixed',
    show_labels BOOLEAN DEFAULT TRUE,
    animation_enabled BOOLEAN DEFAULT TRUE,
    
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 视图配置表索引
CREATE INDEX IF NOT EXISTS idx_views_user ON view_configs(user_id);
CREATE INDEX IF NOT EXISTS idx_views_graph ON view_configs(graph_id);

COMMENT ON TABLE view_configs IS '视图配置表';
COMMENT ON COLUMN view_configs.view_type IS '视图类型: preset, custom';

-- ==================== 复习记录表 ====================
CREATE TABLE IF NOT EXISTS review_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id UUID NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    review_mode VARCHAR(20) NOT NULL,
    
    -- 复习结果
    mastery_feedback VARCHAR(20) NOT NULL,
    time_spent_seconds INTEGER,
    
    -- 复习时的状态快照
    node_state_snapshot JSONB,
    
    -- 上下文信息
    device_type VARCHAR(20),
    app_version VARCHAR(20),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 复习记录表索引
CREATE INDEX IF NOT EXISTS idx_review_logs_node ON review_logs(node_id);
CREATE INDEX IF NOT EXISTS idx_review_logs_user ON review_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_review_logs_time ON review_logs(created_at);

COMMENT ON TABLE review_logs IS '复习记录表';
COMMENT ON COLUMN review_logs.review_mode IS '复习模式: graph-traversal, random, focused, spaced';
COMMENT ON COLUMN review_logs.mastery_feedback IS '掌握反馈: remembered, forgot, partial';

-- ==================== 文件上传记录表 ====================
CREATE TABLE IF NOT EXISTS file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    graph_id UUID REFERENCES knowledge_graphs(id),
    
    -- 文件信息
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    
    -- 处理状态
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    processing_result JSONB,
    error_message TEXT,
    
    -- 元数据
    uploaded_ip VARCHAR(45),
    device_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- 文件上传记录表索引
CREATE INDEX IF NOT EXISTS idx_uploads_user ON file_uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_uploads_status ON file_uploads(status);
CREATE INDEX IF NOT EXISTS idx_uploads_created ON file_uploads(created_at);

COMMENT ON TABLE file_uploads IS '文件上传记录表';
COMMENT ON COLUMN file_uploads.status IS '处理状态: pending, processing, completed, failed';

-- ==================== 创建触发器函数 ====================
-- 自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加触发器
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_graphs_updated_at 
    BEFORE UPDATE ON knowledge_graphs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_nodes_updated_at 
    BEFORE UPDATE ON memory_nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_views_updated_at 
    BEFORE UPDATE ON view_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== 输出完成信息 ====================
DO $$
BEGIN
    RAISE NOTICE '✅ 数据库表结构创建完成';
    RAISE NOTICE '   - users: 用户表';
    RAISE NOTICE '   - knowledge_graphs: 知识图谱表';
    RAISE NOTICE '   - memory_nodes: 记忆节点表（核心）';
    RAISE NOTICE '   - knowledge_tags: 知识点标签表';
    RAISE NOTICE '   - node_tags: 节点-标签关联表';
    RAISE NOTICE '   - node_relations: 节点关联表';
    RAISE NOTICE '   - view_configs: 视图配置表';
    RAISE NOTICE '   - review_logs: 复习记录表';
    RAISE NOTICE '   - file_uploads: 文件上传记录表';
    RAISE NOTICE '';
    RAISE NOTICE '✅ 触发器创建完成';
    RAISE NOTICE '   - 自动更新 updated_at 字段';
END $$;

