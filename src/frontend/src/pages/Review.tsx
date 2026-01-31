import React, { useState } from 'react';
import {
  Card,
  Button,
  Typography,
  Space,
  Row,
  Col,
  Statistic,
  Empty,
  Radio,
  Progress,
  Tag,
} from 'antd';
import {
  FireOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ThunderboltOutlined,
  BookOutlined,
  BulbOutlined,
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

const Review: React.FC = () => {
  const [reviewMode, setReviewMode] = useState<string>('spaced');

  const reviewModes = [
    {
      key: 'spaced',
      title: '间隔复习',
      icon: <ClockCircleOutlined />,
      description: '基于遗忘曲线的智能复习',
      color: '#1890ff',
    },
    {
      key: 'focused',
      title: '专注复习',
      icon: <FireOutlined />,
      description: '针对薄弱知识点强化训练',
      color: '#f5222d',
    },
    {
      key: 'random',
      title: '随机复习',
      icon: <ThunderboltOutlined />,
      description: '随机抽取节点进行复习',
      color: '#faad14',
    },
    {
      key: 'graph_traversal',
      title: '图谱遍历',
      icon: <BulbOutlined />,
      description: '按照知识图谱结构系统复习',
      color: '#52c41a',
    },
  ];

  const stats = {
    todayReview: 15,
    todayTarget: 20,
    weekStreak: 7,
    totalMastered: 156,
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ marginBottom: 8 }}>
          复习中心
        </Title>
        <Text type="secondary">坚持复习，巩固知识</Text>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日复习"
              value={stats.todayReview}
              suffix={`/ ${stats.todayTarget}`}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            />
            <Progress
              percent={(stats.todayReview / stats.todayTarget) * 100}
              strokeColor="#52c41a"
              showInfo={false}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="连续打卡"
              value={stats.weekStreak}
              suffix="天"
              prefix={<FireOutlined style={{ color: '#f5222d' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已掌握"
              value={stats.totalMastered}
              suffix="个"
              prefix={<BookOutlined style={{ color: '#1890ff' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="待复习"
              value={45}
              suffix="个"
              prefix={<ClockCircleOutlined style={{ color: '#faad14' }} />}
            />
          </Card>
        </Col>
      </Row>

      {/* 复习模式选择 */}
      <Card title="选择复习模式" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          {reviewModes.map((mode) => (
            <Col xs={24} sm={12} lg={6} key={mode.key}>
              <Card
                hoverable
                style={{
                  borderColor: reviewMode === mode.key ? mode.color : undefined,
                  borderWidth: reviewMode === mode.key ? 2 : 1,
                }}
                onClick={() => setReviewMode(mode.key)}
              >
                <Space direction="vertical" style={{ width: '100%', textAlign: 'center' }}>
                  <div style={{ fontSize: 48, color: mode.color }}>{mode.icon}</div>
                  <Title level={4} style={{ marginBottom: 8 }}>
                    {mode.title}
                  </Title>
                  <Text type="secondary">{mode.description}</Text>
                  {reviewMode === mode.key && (
                    <Tag color={mode.color} style={{ marginTop: 8 }}>
                      已选择
                    </Tag>
                  )}
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 开始复习 */}
      <Card>
        <Empty
          description={
            <Space direction="vertical" size="large">
              <div>
                <Title level={4}>准备好开始复习了吗？</Title>
                <Paragraph type="secondary">
                  选择一个复习模式，开始今天的学习之旅
                </Paragraph>
              </div>
              <Button
                type="primary"
                size="large"
                icon={<FireOutlined />}
                style={{ height: 48, fontSize: 16, fontWeight: 600 }}
              >
                开始复习
              </Button>
            </Space>
          }
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    </div>
  );
};

export default Review;
