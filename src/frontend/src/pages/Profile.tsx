import React, { useEffect, useState } from 'react';
import {
  Card,
  Avatar,
  Typography,
  Space,
  Button,
  Form,
  Input,
  Upload,
  message,
  Divider,
  Row,
  Col,
  Statistic,
} from 'antd';
import {
  UserOutlined,
  MailOutlined,
  EditOutlined,
  CameraOutlined,
  BookOutlined,
  FireOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import { useAppSelector } from '../store/hooks';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

const Profile: React.FC = () => {
  const user = useAppSelector((state) => state.auth.user);
  const [editing, setEditing] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        username: user.username,
        email: user.email,
      });
    }
  }, [user, form]);

  const handleSave = async (values: any) => {
    try {
      // TODO: 调用更新用户信息的 API
      message.success('保存成功');
      setEditing(false);
    } catch (error) {
      message.error('保存失败');
    }
  };

  const stats = {
    totalGraphs: 12,
    totalNodes: 256,
    studyDays: 45,
    totalReviews: 1234,
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ marginBottom: 8 }}>
          个人中心
        </Title>
        <Text type="secondary">管理你的个人信息和学习数据</Text>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          {/* 用户信息卡片 */}
          <Card>
            <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center' }}>
              <div style={{ position: 'relative', display: 'inline-block' }}>
                <Avatar
                  size={120}
                  icon={<UserOutlined />}
                  src={user?.avatar_url}
                  style={{ backgroundColor: '#667eea' }}
                />
                <Button
                  type="primary"
                  shape="circle"
                  icon={<CameraOutlined />}
                  size="small"
                  style={{
                    position: 'absolute',
                    bottom: 0,
                    right: 0,
                  }}
                />
              </div>

              <div>
                <Title level={3} style={{ marginBottom: 4 }}>
                  {user?.username}
                </Title>
                <Text type="secondary">{user?.email}</Text>
              </div>

              <Divider style={{ margin: '8px 0' }} />

              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <Text type="secondary">
                  <UserOutlined /> 用户ID: {user?.id}
                </Text>
                <Text type="secondary">
                  <MailOutlined /> 注册时间: {dayjs(user?.created_at).format('YYYY-MM-DD')}
                </Text>
              </Space>
            </Space>
          </Card>

          {/* 成就卡片 */}
          <Card title="学习成就" style={{ marginTop: 16 }}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div style={{ textAlign: 'center' }}>
                <TrophyOutlined style={{ fontSize: 48, color: '#faad14' }} />
                <Title level={4} style={{ marginTop: 8 }}>
                  学习达人
                </Title>
                <Text type="secondary">连续学习 {stats.studyDays} 天</Text>
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          {/* 学习统计 */}
          <Card title="学习统计" style={{ marginBottom: 16 }}>
            <Row gutter={[16, 16]}>
              <Col xs={12} sm={6}>
                <Statistic
                  title="知识图谱"
                  value={stats.totalGraphs}
                  prefix={<BookOutlined />}
                  suffix="个"
                />
              </Col>
              <Col xs={12} sm={6}>
                <Statistic
                  title="知识节点"
                  value={stats.totalNodes}
                  prefix={<BookOutlined />}
                  suffix="个"
                />
              </Col>
              <Col xs={12} sm={6}>
                <Statistic
                  title="学习天数"
                  value={stats.studyDays}
                  prefix={<FireOutlined />}
                  suffix="天"
                />
              </Col>
              <Col xs={12} sm={6}>
                <Statistic
                  title="复习次数"
                  value={stats.totalReviews}
                  prefix={<TrophyOutlined />}
                  suffix="次"
                />
              </Col>
            </Row>
          </Card>

          {/* 个人信息编辑 */}
          <Card
            title="个人信息"
            extra={
              !editing && (
                <Button type="link" icon={<EditOutlined />} onClick={() => setEditing(true)}>
                  编辑
                </Button>
              )
            }
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSave}
              disabled={!editing}
            >
              <Form.Item
                name="username"
                label="用户名"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, message: '用户名至少3个字符' },
                ]}
              >
                <Input prefix={<UserOutlined />} placeholder="用户名" />
              </Form.Item>

              <Form.Item
                name="email"
                label="邮箱"
                rules={[
                  { required: true, message: '请输入邮箱' },
                  { type: 'email', message: '请输入有效的邮箱地址' },
                ]}
              >
                <Input prefix={<MailOutlined />} placeholder="邮箱" disabled />
              </Form.Item>

              {editing && (
                <Form.Item>
                  <Space>
                    <Button type="primary" htmlType="submit">
                      保存
                    </Button>
                    <Button onClick={() => setEditing(false)}>取消</Button>
                  </Space>
                </Form.Item>
              )}
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Profile;
