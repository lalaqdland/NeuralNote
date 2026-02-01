import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Empty, Spin, Typography, Space, Tag } from 'antd';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { MemoryNode } from '../services/memoryNode';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

interface StatisticsChartsProps {
  nodes: MemoryNode[];
  loading?: boolean;
}

const StatisticsCharts: React.FC<StatisticsChartsProps> = ({ nodes, loading = false }) => {
  const [masteryData, setMasteryData] = useState<any[]>([]);
  const [typeData, setTypeData] = useState<any[]>([]);
  const [timelineData, setTimelineData] = useState<any[]>([]);
  const [tagData, setTagData] = useState<any[]>([]);

  useEffect(() => {
    if (nodes.length > 0) {
      calculateStatistics();
    }
  }, [nodes]);

  const calculateStatistics = () => {
    // 1. 掌握度分布
    const masteryDistribution = [
      { level: '未学习', value: 0, color: '#f5222d' },
      { level: '初步了解', value: 1, color: '#fa8c16' },
      { level: '基本掌握', value: 2, color: '#faad14' },
      { level: '熟练掌握', value: 3, color: '#52c41a' },
      { level: '精通', value: 4, color: '#1890ff' },
      { level: '完全掌握', value: 5, color: '#722ed1' },
    ];

    const masteryCount = masteryDistribution.map((item) => ({
      ...item,
      count: nodes.filter((n) => n.mastery_level === item.value).length,
    }));

    setMasteryData(masteryCount);

    // 2. 节点类型分布
    const typeDistribution = [
      { type: 'CONCEPT', name: '概念', color: '#1890ff' },
      { type: 'QUESTION', name: '题目', color: '#52c41a' },
      { type: 'NOTE', name: '笔记', color: '#faad14' },
      { type: 'RESOURCE', name: '资源', color: '#722ed1' },
    ];

    const typeCount = typeDistribution.map((item) => ({
      ...item,
      count: nodes.filter((n) => n.node_type === item.type).length,
    }));

    setTypeData(typeCount.filter((item) => item.count > 0));

    // 3. 时间线数据（最近7天的节点创建数）
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = dayjs().subtract(6 - i, 'day');
      return {
        date: date.format('MM-DD'),
        count: nodes.filter((n) =>
          dayjs(n.created_at).isSame(date, 'day')
        ).length,
      };
    });

    setTimelineData(last7Days);

    // 4. 标签统计（Top 10）
    const tagCount: Record<string, number> = {};
    nodes.forEach((node) => {
      if (node.tags && Array.isArray(node.tags)) {
        node.tags.forEach((tag) => {
          tagCount[tag] = (tagCount[tag] || 0) + 1;
        });
      }
    });

    const tagArray = Object.entries(tagCount)
      .map(([tag, count]) => ({ tag, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    setTagData(tagArray);
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (nodes.length === 0) {
    return (
      <Empty
        description="还没有节点数据"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        style={{ padding: '60px 0' }}
      />
    );
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {/* 第一行：掌握度分布 + 节点类型分布 */}
      <Row gutter={16}>
        <Col xs={24} lg={12}>
          <Card title="掌握度分布" bordered={false}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={masteryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="level" angle={-15} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" name="节点数">
                  {masteryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <Space>
                <Text type="secondary">平均掌握度:</Text>
                <Text strong style={{ fontSize: 18, color: '#1890ff' }}>
                  {(
                    nodes.reduce((sum, n) => sum + n.mastery_level, 0) / nodes.length
                  ).toFixed(2)}
                </Text>
                <Text type="secondary">/ 5.00</Text>
              </Space>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="节点类型分布" bordered={false}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={typeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {typeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <Space size="large">
                {typeData.map((item) => (
                  <Space key={item.type}>
                    <div
                      style={{
                        width: 12,
                        height: 12,
                        borderRadius: '50%',
                        background: item.color,
                      }}
                    />
                    <Text>{item.name}</Text>
                    <Text strong>{item.count}</Text>
                  </Space>
                ))}
              </Space>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 第二行：时间线趋势 */}
      <Row gutter={16}>
        <Col span={24}>
          <Card title="最近7天节点创建趋势" bordered={false}>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="count"
                  name="创建节点数"
                  stroke="#1890ff"
                  strokeWidth={2}
                  dot={{ fill: '#1890ff', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 第三行：标签统计 + 掌握度雷达图 */}
      <Row gutter={16}>
        <Col xs={24} lg={12}>
          <Card title="热门标签 Top 10" bordered={false}>
            {tagData.length === 0 ? (
              <Empty description="还没有标签" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={tagData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="tag" type="category" width={100} />
                  <Tooltip />
                  <Bar dataKey="count" name="使用次数" fill="#722ed1" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="节点类型掌握度分析" bordered={false}>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart
                data={typeData.map((item) => {
                  const typeNodes = nodes.filter((n) => n.node_type === item.type);
                  const avgMastery =
                    typeNodes.length > 0
                      ? typeNodes.reduce((sum, n) => sum + n.mastery_level, 0) /
                        typeNodes.length
                      : 0;
                  return {
                    type: item.name,
                    mastery: avgMastery,
                    fullMark: 5,
                  };
                })}
              >
                <PolarGrid />
                <PolarAngleAxis dataKey="type" />
                <PolarRadiusAxis angle={90} domain={[0, 5]} />
                <Radar
                  name="平均掌握度"
                  dataKey="mastery"
                  stroke="#1890ff"
                  fill="#1890ff"
                  fillOpacity={0.6}
                />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <Text type="secondary">各类型节点的平均掌握程度（满分5分）</Text>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 统计摘要 */}
      <Card title="统计摘要" bordered={false}>
        <Row gutter={[16, 16]}>
          <Col xs={12} sm={6}>
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">总节点数</Text>
              <Title level={2} style={{ margin: '8px 0', color: '#1890ff' }}>
                {nodes.length}
              </Title>
            </div>
          </Col>
          <Col xs={12} sm={6}>
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">已掌握节点</Text>
              <Title level={2} style={{ margin: '8px 0', color: '#52c41a' }}>
                {nodes.filter((n) => n.mastery_level >= 4).length}
              </Title>
            </div>
          </Col>
          <Col xs={12} sm={6}>
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">学习中节点</Text>
              <Title level={2} style={{ margin: '8px 0', color: '#faad14' }}>
                {nodes.filter((n) => n.mastery_level >= 1 && n.mastery_level < 4).length}
              </Title>
            </div>
          </Col>
          <Col xs={12} sm={6}>
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">未学习节点</Text>
              <Title level={2} style={{ margin: '8px 0', color: '#f5222d' }}>
                {nodes.filter((n) => n.mastery_level === 0).length}
              </Title>
            </div>
          </Col>
        </Row>
      </Card>
    </Space>
  );
};

export default StatisticsCharts;

