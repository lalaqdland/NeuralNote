import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Typography,
  Space,
  Row,
  Col,
  Statistic,
  Empty,
  Progress,
  Tag,
  message,
  Spin,
  Select,
  Result,
} from 'antd';
import {
  FireOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ThunderboltOutlined,
  BookOutlined,
  BulbOutlined,
  TrophyOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { knowledgeGraphService, KnowledgeGraph } from '../services/knowledgeGraph';
import { reviewService, ReviewMode, ReviewNode, ReviewStats } from '../services/review';
import { notificationService } from '../services/notification';
import ReviewCard from '../components/ReviewCard';

const { Title, Text, Paragraph } = Typography;

const Review: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [reviewMode, setReviewMode] = useState<ReviewMode>('spaced');
  const [selectedGraph, setSelectedGraph] = useState<number | null>(null);
  const [graphs, setGraphs] = useState<KnowledgeGraph[]>([]);
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [reviewQueue, setReviewQueue] = useState<ReviewNode[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [isReviewing, setIsReviewing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [reviewCompleted, setReviewCompleted] = useState(false);

  useEffect(() => {
    loadGraphs();
  }, []);

  useEffect(() => {
    if (selectedGraph) {
      loadStats();
      // 启动定时检查通知
      const settings = notificationService.getSettings();
      if (settings.enabled) {
        notificationService.startPeriodicCheck(selectedGraph);
      }
    }

    // 组件卸载时停止定时检查
    return () => {
      notificationService.stopPeriodicCheck();
    };
  }, [selectedGraph]);

  useEffect(() => {
    // 从 URL 参数中获取图谱 ID（从通知点击进入）
    const graphIdFromUrl = searchParams.get('graph');
    if (graphIdFromUrl && graphs.length > 0) {
      const graphId = parseInt(graphIdFromUrl, 10);
      if (!isNaN(graphId)) {
        setSelectedGraph(graphId);
      }
    }
  }, [searchParams, graphs]);

  const loadGraphs = async () => {
    try {
      const response = await knowledgeGraphService.getGraphs(1, 50);
      setGraphs(response.items);
      if (response.items.length > 0) {
        setSelectedGraph(response.items[0].id);
      }
    } catch (error) {
      message.error('加载知识图谱失败');
    }
  };

  const loadStats = async () => {
    if (!selectedGraph) return;
    try {
      const data = await reviewService.getReviewStats(selectedGraph);
      setStats(data);
    } catch (error) {
      message.error('加载统计数据失败');
    }
  };

  const handleStartReview = async () => {
    if (!selectedGraph) {
      message.warning('请先选择知识图谱');
      return;
    }

    setLoading(true);
    try {
      const response = await reviewService.getReviewQueue(selectedGraph, reviewMode, 20);
      if (response.nodes.length === 0) {
        message.info('暂无需要复习的节点');
        return;
      }
      setReviewQueue(response.nodes);
      setCurrentIndex(0);
      setShowAnswer(false);
      setIsReviewing(true);
      setReviewCompleted(false);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取复习队列失败');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (quality: number) => {
    const currentNode = reviewQueue[currentIndex];
    try {
      await reviewService.submitFeedback({
        node_id: currentNode.node_id,
        quality,
      });

      // 延迟后进入下一题
      setTimeout(() => {
        if (currentIndex < reviewQueue.length - 1) {
          setCurrentIndex(currentIndex + 1);
          setShowAnswer(false);
        } else {
          // 复习完成
          setReviewCompleted(true);
          loadStats(); // 刷新统计数据
        }
      }, 500);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '提交反馈失败');
    }
  };

  const handleToggleAnswer = () => {
    setShowAnswer(!showAnswer);
  };

  const handleBackToHome = () => {
    setIsReviewing(false);
    setReviewCompleted(false);
    setCurrentIndex(0);
    setReviewQueue([]);
  };

  const reviewModes = [
    {
      key: 'spaced' as ReviewMode,
      title: '间隔复习',
      icon: <ClockCircleOutlined />,
      description: '基于遗忘曲线的智能复习',
      color: '#1890ff',
    },
    {
      key: 'focused' as ReviewMode,
      title: '专注复习',
      icon: <FireOutlined />,
      description: '针对薄弱知识点强化训练',
      color: '#f5222d',
    },
    {
      key: 'random' as ReviewMode,
      title: '随机复习',
      icon: <ThunderboltOutlined />,
      description: '随机抽取节点进行复习',
      color: '#faad14',
    },
    {
      key: 'graph_traversal' as ReviewMode,
      title: '图谱遍历',
      icon: <BulbOutlined />,
      description: '按照知识图谱结构系统复习',
      color: '#52c41a',
    },
  ];

  // 复习完成页面
  if (reviewCompleted) {
    return (
      <div style={{ maxWidth: 600, margin: '60px auto' }}>
        <Result
          status="success"
          icon={<TrophyOutlined style={{ color: '#faad14' }} />}
          title="恭喜！复习完成"
          subTitle={`本次复习了 ${reviewQueue.length} 个节点，继续保持！`}
          extra={[
            <Button type="primary" size="large" icon={<FireOutlined />} onClick={handleStartReview} key="continue">
              继续复习
            </Button>,
            <Button size="large" icon={<HomeOutlined />} onClick={handleBackToHome} key="back">
              返回首页
            </Button>,
          ]}
        />
      </div>
    );
  }

  // 复习中页面
  if (isReviewing && reviewQueue.length > 0) {
    return (
      <div style={{ padding: '24px 0' }}>
        <div style={{ marginBottom: 24, textAlign: 'center' }}>
          <Button onClick={handleBackToHome}>退出复习</Button>
        </div>
        <ReviewCard
          node={reviewQueue[currentIndex]}
          onFeedback={handleFeedback}
          showAnswer={showAnswer}
          onToggleAnswer={handleToggleAnswer}
          currentIndex={currentIndex}
          totalCount={reviewQueue.length}
        />
      </div>
    );
  }

  // 主页面
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ marginBottom: 8 }}>
          复习中心
        </Title>
        <Text type="secondary">坚持复习，巩固知识</Text>
      </div>

      {/* 知识图谱选择 */}
      {graphs.length > 0 && (
        <Card style={{ marginBottom: 16 }}>
          <Space>
            <Text strong>选择知识图谱:</Text>
            <Select
              value={selectedGraph}
              onChange={setSelectedGraph}
              style={{ width: 300 }}
              options={graphs.map((g) => ({ label: g.name, value: g.id }))}
            />
          </Space>
        </Card>
      )}

      {/* 统计卡片 */}
      {stats && (
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="今日复习"
                value={stats.reviewed_today}
                prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="连续打卡"
                value={stats.streak_days}
                suffix="天"
                prefix={<FireOutlined style={{ color: '#f5222d' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="已掌握"
                value={stats.mastered_nodes}
                suffix="个"
                prefix={<BookOutlined style={{ color: '#1890ff' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="待复习"
                value={stats.due_today}
                suffix="个"
                prefix={<ClockCircleOutlined style={{ color: '#faad14' }} />}
              />
            </Card>
          </Col>
        </Row>
      )}

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
        {loading ? (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <Spin size="large" />
            <Title level={4} style={{ marginTop: 24 }}>
              正在准备复习内容...
            </Title>
          </div>
        ) : graphs.length === 0 ? (
          <Empty
            description="还没有知识图谱"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" onClick={() => navigate('/graph')}>
              创建知识图谱
            </Button>
          </Empty>
        ) : (
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
                  onClick={handleStartReview}
                  style={{ height: 48, fontSize: 16, fontWeight: 600 }}
                >
                  开始复习
                </Button>
              </Space>
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </Card>
    </div>
  );
};

export default Review;
