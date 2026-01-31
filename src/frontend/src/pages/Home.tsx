import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Button,
  Typography,
  Space,
  Empty,
  Spin,
  List,
  Tag,
  Progress,
} from 'antd';
import {
  PlusOutlined,
  BookOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  FireOutlined,
  RightOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { knowledgeGraphService, KnowledgeGraph } from '../services/knowledgeGraph';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

const { Title, Text, Paragraph } = Typography;

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [graphs, setGraphs] = useState<KnowledgeGraph[]>([]);
  const [stats, setStats] = useState({
    totalGraphs: 0,
    totalNodes: 0,
    reviewToday: 0,
    masteredNodes: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await knowledgeGraphService.getGraphs(1, 5);
      setGraphs(response.items);
      
      // 计算统计数据
      const totalNodes = response.items.reduce((sum, g) => sum + g.node_count, 0);
      setStats({
        totalGraphs: response.total,
        totalNodes,
        reviewToday: Math.floor(totalNodes * 0.2), // 模拟数据
        masteredNodes: Math.floor(totalNodes * 0.6), // 模拟数据
      });
    } catch (error) {
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMasteryProgress = (nodeCount: number) => {
    // 模拟掌握进度
    return Math.floor(Math.random() * 40) + 40;
  };

  return (
    <div>
      {/* 欢迎区域 */}
      <Card
        style={{
          marginBottom: 24,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          border: 'none',
        }}
        bodyStyle={{ padding: '40px' }}
      >
        <Row align="middle" justify="space-between">
          <Col>
            <Title level={2} style={{ color: 'white', marginBottom: 8 }}>
              欢迎回来！👋
            </Title>
            <Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: 16 }}>
              继续你的学习之旅，构建你的知识图谱
            </Text>
          </Col>
          <Col>
            <Space size="middle">
              <Button
                type="primary"
                size="large"
                icon={<PlusOutlined />}
                onClick={() => navigate('/graph')}
                style={{
                  background: 'white',
                  color: '#667eea',
                  border: 'none',
                  height: 48,
                  fontSize: 16,
                  fontWeight: 600,
                }}
              >
                创建图谱
              </Button>
              <Button
                size="large"
                icon={<FireOutlined />}
                onClick={() => navigate('/review')}
                style={{
                  background: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.3)',
                  height: 48,
                  fontSize: 16,
                }}
              >
                开始复习
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="知识图谱"
              value={stats.totalGraphs}
              prefix={<BookOutlined style={{ color: '#667eea' }} />}
              suffix="个"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="知识节点"
              value={stats.totalNodes}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              suffix="个"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日复习"
              value={stats.reviewToday}
              prefix={<ClockCircleOutlined style={{ color: '#faad14' }} />}
              suffix="个"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已掌握"
              value={stats.masteredNodes}
              prefix={<FireOutlined style={{ color: '#f5222d' }} />}
              suffix="个"
            />
          </Card>
        </Col>
      </Row>

      {/* 最近的图谱 */}
      <Card
        title={
          <Space>
            <BookOutlined />
            <span>最近的知识图谱</span>
          </Space>
        }
        extra={
          <Button type="link" onClick={() => navigate('/graph')}>
            查看全部 <RightOutlined />
          </Button>
        }
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" />
          </div>
        ) : graphs.length === 0 ? (
          <Empty
            description="还没有知识图谱"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/graph')}>
              创建第一个图谱
            </Button>
          </Empty>
        ) : (
          <List
            dataSource={graphs}
            renderItem={(graph) => (
              <List.Item
                key={graph.id}
                style={{ cursor: 'pointer', padding: '16px 0' }}
                onClick={() => navigate(`/graph/${graph.id}`)}
                extra={
                  <Button type="primary" ghost>
                    查看详情
                  </Button>
                }
              >
                <List.Item.Meta
                  avatar={
                    <div
                      style={{
                        width: 60,
                        height: 60,
                        borderRadius: 12,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: 24,
                        fontWeight: 700,
                      }}
                    >
                      {graph.name.charAt(0)}
                    </div>
                  }
                  title={
                    <Space>
                      <Text strong style={{ fontSize: 16 }}>
                        {graph.name}
                      </Text>
                      {graph.subject && <Tag color="blue">{graph.subject}</Tag>}
                      {graph.is_public && <Tag color="green">公开</Tag>}
                    </Space>
                  }
                  description={
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Paragraph
                        ellipsis={{ rows: 2 }}
                        style={{ marginBottom: 8, color: '#666' }}
                      >
                        {graph.description || '暂无描述'}
                      </Paragraph>
                      <Space split="|">
                        <Text type="secondary">
                          <BookOutlined /> {graph.node_count} 个节点
                        </Text>
                        <Text type="secondary">
                          更新于 {dayjs(graph.updated_at).fromNow()}
                        </Text>
                      </Space>
                      <div style={{ marginTop: 8 }}>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          掌握进度
                        </Text>
                        <Progress
                          percent={getMasteryProgress(graph.node_count)}
                          strokeColor={{
                            '0%': '#667eea',
                            '100%': '#764ba2',
                          }}
                          size="small"
                        />
                      </div>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
};

export default Home;
