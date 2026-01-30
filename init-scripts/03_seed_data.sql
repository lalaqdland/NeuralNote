-- NeuralNote 数据库种子数据
-- 用于开发环境测试

-- ==================== 创建测试用户 ====================
INSERT INTO users (
    email, 
    username, 
    password_hash, 
    timezone, 
    language, 
    subscription_plan,
    is_active,
    is_verified
) VALUES (
    'test@neuralnote.com',
    'testuser',
    -- 密码: test123456 (实际使用时应该用bcrypt加密)
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/VXlTW',
    'Asia/Shanghai',
    'zh-CN',
    'free',
    true,
    true
) ON CONFLICT (email) DO NOTHING;

-- ==================== 创建测试知识图谱 ====================
INSERT INTO knowledge_graphs (
    user_id,
    name,
    description,
    subject,
    is_public,
    is_preset
) VALUES (
    (SELECT id FROM users WHERE email = 'test@neuralnote.com'),
    '考研数学知识图谱',
    '2026考研数学复习知识图谱',
    'math',
    false,
    false
) ON CONFLICT DO NOTHING;

-- ==================== 输出完成信息 ====================
DO $$
BEGIN
    RAISE NOTICE '✅ 种子数据插入完成';
    RAISE NOTICE '   - 测试用户: test@neuralnote.com';
    RAISE NOTICE '   - 密码: test123456';
    RAISE NOTICE '   - 测试图谱: 考研数学知识图谱';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  注意: 这些是测试数据，生产环境请删除！';
END $$;

