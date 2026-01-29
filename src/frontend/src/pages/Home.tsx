import React from 'react';
import { Card, Typography, Space, Button } from 'antd';
import { UploadOutlined, ApiOutlined, BarChartOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const Home: React.FC = () => {
  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Hero Section */}
        <Card style={{ textAlign: 'center', padding: '48px 0' }}>
          <Title level={1}>NeuralNote (纽伦笔记)</Title>
          <Paragraph style={{ fontSize: '18px', color: '#666' }}>
            Be Your Own Memory Architect. 做你自己的记忆架构师
          </Paragraph>
          <Space size="large" style={{ marginTop: '24px' }}>
            <Button type="primary" size="large" icon={<UploadOutlined />}>
              上传题目
            </Button>
            <Button size="large" icon={<ApiOutlined />}>
              AI 解答
            </Button>
            <Button size="large" icon={<BarChartOutlined />}>
              查看图谱
            </Button>
          </Space>
        </Card>

        {/* 功能介绍 */}
        <Title level={2}>核心功能</Title>
        <Card title="智能采集">
          <Paragraph>
            支持拍照、截图、文件上传，AI自动识别题目内容，提取关键信息。
          </Paragraph>
        </Card>

        <Card title="AI 解答">
          <Paragraph>
            基于深度学习的AI模型，自动生成详细解答，提炼关键记忆点。
          </Paragraph>
        </Card>

        <Card title="知识图谱">
          <Paragraph>
            可视化展示知识点分布与关联，支持2D/3D视图切换。
          </Paragraph>
        </Card>

        <Card title="智能复习">
          <Paragraph>
            基于遗忘曲线算法，智能提醒最佳复习时机，提升记忆效率。
          </Paragraph>
        </Card>
      </Space>
    </div>
  );
};

export default Home;
