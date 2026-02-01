import React, { useState } from 'react';
import { Form, Input, Button, Tabs, message, Typography, Space } from 'antd';
import {
  UserOutlined,
  LockOutlined,
  MailOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  RocketOutlined,
  StarOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authService, LoginRequest, RegisterRequest } from '../services/auth';
import { useAppDispatch } from '../store/hooks';
import { setUser } from '../store/authSlice';
import './Login.css';

const { Title, Text, Paragraph } = Typography;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('login');
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  // 处理登录
  const handleLogin = async (values: LoginRequest) => {
    setLoading(true);
    try {
      const response = await authService.login(values);
      dispatch(setUser(response.user));
      message.success('登录成功！');
      navigate('/');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  // 处理注册
  const handleRegister = async (values: RegisterRequest) => {
    setLoading(true);
    try {
      await authService.register(values);
      message.success('注册成功！请登录');
      setActiveTab('login');
    } catch (error: any) {
      console.error('注册错误:', error);
      console.error('错误响应:', error.response);
      const errorMsg = error.response?.data?.detail || error.message || '注册失败，请稍后重试';
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const highlights = [
    {
      icon: '📸',
      text: '拍照即学',
    },
    {
      icon: '🕸️',
      text: '知识成网',
    },
    {
      icon: '📚',
      text: '科学复习',
    },
  ];

  return (
    <div className="login-container">
      {/* 左侧：产品展示区 */}
      <div className="login-showcase">
        <div className="showcase-background">
          <div className="gradient-orb orb-1"></div>
          <div className="gradient-orb orb-2"></div>
          <div className="gradient-orb orb-3"></div>
        </div>

        <div className="showcase-content">
          <div className="brand-section">
            <div className="brand-icon">🧠</div>
            <Title level={1} className="brand-title">
              NeuralNote
            </Title>
            <Paragraph className="brand-subtitle">
              纽伦笔记 · 让学习更智能
            </Paragraph>
          </div>

          {/* 概念可视化区域 */}
          <div className="concept-visualization">
            {/* 知识图谱概念图 */}
            <div className="knowledge-graph-demo">
              <svg className="graph-svg" viewBox="0 0 400 240" xmlns="http://www.w3.org/2000/svg">
                {/* 连接线 */}
                <g className="connections">
                  <line x1="200" y1="120" x2="120" y2="60" className="connection-line" strokeDasharray="5,5" />
                  <line x1="200" y1="120" x2="280" y2="60" className="connection-line" strokeDasharray="5,5" />
                  <line x1="200" y1="120" x2="120" y2="180" className="connection-line" strokeDasharray="5,5" />
                  <line x1="200" y1="120" x2="280" y2="180" className="connection-line" strokeDasharray="5,5" />
                  <line x1="120" y1="60" x2="280" y2="60" className="connection-line connection-weak" />
                  <line x1="120" y1="180" x2="280" y2="180" className="connection-line connection-weak" />
                </g>
                
                {/* 节点 */}
                <g className="nodes">
                  {/* 中心节点 */}
                  <circle cx="200" cy="120" r="30" className="node node-center" />
                  <text x="200" y="125" className="node-text node-text-center">核心</text>
                  
                  {/* 周围节点 */}
                  <circle cx="120" cy="60" r="24" className="node node-mastered" />
                  <text x="120" y="65" className="node-text">已掌握</text>
                  
                  <circle cx="280" cy="60" r="24" className="node node-learning" />
                  <text x="280" y="65" className="node-text">学习中</text>
                  
                  <circle cx="120" cy="180" r="24" className="node node-review" />
                  <text x="120" y="185" className="node-text">待复习</text>
                  
                  <circle cx="280" cy="180" r="24" className="node node-new" />
                  <text x="280" y="185" className="node-text">新知识</text>
                </g>
              </svg>
            </div>

            {/* 核心亮点 - 横向排列 */}
            <div className="highlights-compact">
              {highlights.map((highlight, index) => (
                <div
                  key={index}
                  className="highlight-compact-item"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="highlight-compact-icon">{highlight.icon}</div>
                  <Text className="highlight-compact-text">{highlight.text}</Text>
                </div>
              ))}
            </div>
          </div>

          <div className="showcase-footer">
            <Text className="footer-text">
              © 2026 NeuralNote · 智能学习管理系统
            </Text>
          </div>
        </div>
      </div>

      {/* 右侧：登录/注册表单 */}
      <div className="login-form-section">
        <div className="form-container">
          <div className="form-header">
            <Title level={2} className="form-title">
              {activeTab === 'login' ? '欢迎回来' : '开始使用'}
            </Title>
            <Text className="form-subtitle">
              {activeTab === 'login'
                ? '登录您的账户，继续学习之旅'
                : '创建账户，开启智能学习'}
            </Text>
          </div>

          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            centered
            className="login-tabs"
            items={[
              {
                key: 'login',
                label: '登录',
                children: (
                  <Form
                    name="login"
                    onFinish={handleLogin}
                    autoComplete="off"
                    size="large"
                    className="login-form"
                  >
                    <Form.Item
                      name="email"
                      rules={[
                        { required: true, message: '请输入邮箱' },
                        { type: 'email', message: '请输入有效的邮箱地址' },
                      ]}
                    >
                      <Input
                        prefix={<MailOutlined className="input-icon" />}
                        placeholder="邮箱"
                        className="form-input"
                      />
                    </Form.Item>

                    <Form.Item
                      name="password"
                      rules={[{ required: true, message: '请输入密码' }]}
                    >
                      <Input.Password
                        prefix={<LockOutlined className="input-icon" />}
                        placeholder="密码"
                        className="form-input"
                      />
                    </Form.Item>

                    <Form.Item>
                      <Button
                        type="primary"
                        htmlType="submit"
                        loading={loading}
                        block
                        className="submit-button"
                      >
                        登录
                      </Button>
                    </Form.Item>
                  </Form>
                ),
              },
              {
                key: 'register',
                label: '注册',
                children: (
                  <Form
                    name="register"
                    onFinish={handleRegister}
                    autoComplete="off"
                    size="large"
                    className="login-form"
                  >
                    <Form.Item
                      name="email"
                      rules={[
                        { required: true, message: '请输入邮箱' },
                        { type: 'email', message: '请输入有效的邮箱地址' },
                      ]}
                    >
                      <Input
                        prefix={<MailOutlined className="input-icon" />}
                        placeholder="邮箱"
                        className="form-input"
                      />
                    </Form.Item>

                    <Form.Item
                      name="username"
                      rules={[
                        { required: true, message: '请输入用户名' },
                        { min: 3, message: '用户名至少3个字符' },
                      ]}
                    >
                      <Input
                        prefix={<UserOutlined className="input-icon" />}
                        placeholder="用户名"
                        className="form-input"
                      />
                    </Form.Item>

                    <Form.Item
                      name="password"
                      rules={[
                        { required: true, message: '请输入密码' },
                        { min: 6, message: '密码至少6个字符' },
                      ]}
                    >
                      <Input.Password
                        prefix={<LockOutlined className="input-icon" />}
                        placeholder="密码"
                        className="form-input"
                      />
                    </Form.Item>

                    <Form.Item
                      name="confirm"
                      dependencies={['password']}
                      rules={[
                        { required: true, message: '请确认密码' },
                        ({ getFieldValue }) => ({
                          validator(_, value) {
                            if (!value || getFieldValue('password') === value) {
                              return Promise.resolve();
                            }
                            return Promise.reject(new Error('两次输入的密码不一致'));
                          },
                        }),
                      ]}
                    >
                      <Input.Password
                        prefix={<LockOutlined className="input-icon" />}
                        placeholder="确认密码"
                        className="form-input"
                      />
                    </Form.Item>

                    <Form.Item>
                      <Button
                        type="primary"
                        htmlType="submit"
                        loading={loading}
                        block
                        className="submit-button"
                      >
                        注册
                      </Button>
                    </Form.Item>
                  </Form>
                ),
              },
            ]}
          />
        </div>
      </div>
    </div>
  );
};

export default Login;

