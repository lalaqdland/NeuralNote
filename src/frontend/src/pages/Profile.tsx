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
  Tabs,
  Modal,
  Progress,
  Tag,
  Spin,
} from 'antd';
import {
  UserOutlined,
  MailOutlined,
  EditOutlined,
  CameraOutlined,
  BookOutlined,
  FireOutlined,
  TrophyOutlined,
  LockOutlined,
  PhoneOutlined,
  LineChartOutlined,
} from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { setUser } from '../store/authSlice';
import { userService, UserStatistics } from '../services/user';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;

const Profile: React.FC = () => {
  const user = useAppSelector((state) => state.auth.user);
  const dispatch = useAppDispatch();
  const [editing, setEditing] = useState(false);
  const [passwordModalVisible, setPasswordModalVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statistics, setStatistics] = useState<UserStatistics | null>(null);
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        phone: user.phone,
      });
      loadStatistics();
    }
  }, [user, form]);

  const loadStatistics = async () => {
    setLoading(true);
    try {
      const data = await userService.getUserStatistics();
      setStatistics(data);
    } catch (error) {
      message.error('加载统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: any) => {
    try {
      await userService.updateUser({
        username: values.username,
        phone: values.phone,
      });
      
      // 更新 Redux 状态
      if (user) {
        dispatch(setUser({ ...user, username: values.username, phone: values.phone }));
      }
      
      message.success('保存成功');
      setEditing(false);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败');
    }
  };

  const handleChangePassword = async (values: any) => {
    try {
      await userService.changePassword({
        old_password: values.old_password,
        new_password: values.new_password,
      });
      message.success('密码修改成功，请重新登录');
      setPasswordModalVisible(false);
      passwordForm.resetFields();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '密码修改失败');
    }
  };

  const getMasteryData = () => {
    if (!statistics) return [];
    const dist = statistics.mastery_distribution;
    return [
      { name: '未学习', value: dist.level_0, color: '#f5222d' },
      { name: '初步了解', value: dist.level_1, color: '#fa8c16' },
      { name: '基本掌握', value: dist.level_2, color: '#faad14' },
      { name: '熟练掌握', value: dist.level_3, color: '#52c41a' },
      { name: '精通', value: dist.level_4, color: '#1890ff' },
      { name: '完全掌握', value: dist.level_5, color: '#722ed1' },
    ];
  };

  const getActivityData = () => {
    if (!statistics) return [];
    return statistics.recent_activity.map((item) => ({
      date: dayjs(item.date).format('MM-DD'),
      reviews: item.reviews,
      nodes: item.nodes_created,
    }));
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
                  onClick={() => message.info('头像上传功能开发中')}
                />
              </div>

              <div>
                <Title level={3} style={{ marginBottom: 4 }}>
                  {user?.username}
                </Title>
                <Text type="secondary">{user?.email}</Text>
                {user?.is_verified && (
                  <div style={{ marginTop: 8 }}>
                    <Tag color="green">已验证</Tag>
                  </div>
                )}
              </div>

              <Divider style={{ margin: '8px 0' }} />

              <Space direction="vertical" size="small" style={{ width: '100%', textAlign: 'left' }}>
                <Text type="secondary">
                  <UserOutlined /> 用户ID: {user?.id}
                </Text>
                <Text type="secondary">
                  <MailOutlined /> 注册时间: {dayjs(user?.created_at).format('YYYY-MM-DD')}
                </Text>
                {user?.last_login_at && (
                  <Text type="secondary">
                    <FireOutlined /> 最后登录: {dayjs(user?.last_login_at).format('YYYY-MM-DD HH:mm')}
                  </Text>
                )}
              </Space>
            </Space>
          </Card>

          {/* 成就卡片 */}
          <Card title="学习成就" style={{ marginTop: 16 }}>
            {loading ? (
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <Spin />
              </div>
            ) : statistics ? (
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div style={{ textAlign: 'center' }}>
                  <TrophyOutlined style={{ fontSize: 48, color: '#faad14' }} />
                  <Title level={4} style={{ marginTop: 8 }}>
                    学习达人
                  </Title>
                  <Text type="secondary">连续学习 {statistics.study_days} 天</Text>
                </div>
                <Divider style={{ margin: '8px 0' }} />
                <div>
                  <Paragraph>
                    <Text strong>学习进度</Text>
                  </Paragraph>
                  <Progress
                    percent={
                      statistics.total_nodes > 0
                        ? Math.round(
                            ((statistics.mastery_distribution.level_4 +
                              statistics.mastery_distribution.level_5) /
                              statistics.total_nodes) *
                              100
                          )
                        : 0
                    }
                    strokeColor={{
                      '0%': '#667eea',
                      '100%': '#764ba2',
                    }}
                  />
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    已掌握节点占比
                  </Text>
                </div>
              </Space>
            ) : (
              <Text type="secondary">暂无数据</Text>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Tabs
            defaultActiveKey="stats"
            items={[
              {
                key: 'stats',
                label: (
                  <span>
                    <LineChartOutlined />
                    学习统计
                  </span>
                ),
                children: loading ? (
                  <div style={{ textAlign: 'center', padding: '60px 0' }}>
                    <Spin size="large" />
                  </div>
                ) : statistics ? (
                  <Space direction="vertical" size="large" style={{ width: '100%' }}>
                    {/* 学习统计 */}
                    <Card>
                      <Row gutter={[16, 16]}>
                        <Col xs={12} sm={6}>
                          <Statistic
                            title="知识图谱"
                            value={statistics.total_graphs}
                            prefix={<BookOutlined />}
                            suffix="个"
                          />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic
                            title="知识节点"
                            value={statistics.total_nodes}
                            prefix={<BookOutlined />}
                            suffix="个"
                          />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic
                            title="学习天数"
                            value={statistics.study_days}
                            prefix={<FireOutlined />}
                            suffix="天"
                          />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic
                            title="复习次数"
                            value={statistics.total_reviews}
                            prefix={<TrophyOutlined />}
                            suffix="次"
                          />
                        </Col>
                      </Row>
                    </Card>

                    {/* 掌握度分布 */}
                    <Card title="掌握度分布">
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie
                            data={getMasteryData()}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) =>
                              percent > 0 ? `${name} ${(percent * 100).toFixed(0)}%` : ''
                            }
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {getMasteryData().map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </Card>

                    {/* 最近活动 */}
                    <Card title="最近7天活动">
                      <ResponsiveContainer width="100%" height={250}>
                        <LineChart data={getActivityData()}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="reviews"
                            name="复习次数"
                            stroke="#1890ff"
                            strokeWidth={2}
                          />
                          <Line
                            type="monotone"
                            dataKey="nodes"
                            name="创建节点"
                            stroke="#52c41a"
                            strokeWidth={2}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </Card>
                  </Space>
                ) : (
                  <Text type="secondary">暂无数据</Text>
                ),
              },
              {
                key: 'info',
                label: (
                  <span>
                    <UserOutlined />
                    个人信息
                  </span>
                ),
                children: (
                  <Card
                    extra={
                      !editing && (
                        <Button type="link" icon={<EditOutlined />} onClick={() => setEditing(true)}>
                          编辑
                        </Button>
                      )
                    }
                  >
                    <Form form={form} layout="vertical" onFinish={handleSave} disabled={!editing}>
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

                      <Form.Item name="phone" label="手机号">
                        <Input prefix={<PhoneOutlined />} placeholder="手机号（可选）" />
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

                    <Divider />

                    <Button
                      icon={<LockOutlined />}
                      onClick={() => setPasswordModalVisible(true)}
                    >
                      修改密码
                    </Button>
                  </Card>
                ),
              },
            ]}
          />
        </Col>
      </Row>

      {/* 修改密码模态框 */}
      <Modal
        title="修改密码"
        open={passwordModalVisible}
        onCancel={() => {
          setPasswordModalVisible(false);
          passwordForm.resetFields();
        }}
        onOk={() => passwordForm.submit()}
        okText="确定"
        cancelText="取消"
      >
        <Form form={passwordForm} layout="vertical" onFinish={handleChangePassword}>
          <Form.Item
            name="old_password"
            label="当前密码"
            rules={[{ required: true, message: '请输入当前密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="当前密码" />
          </Form.Item>

          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码至少6个字符' },
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="新密码" />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            label="确认新密码"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="确认新密码" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Profile;
