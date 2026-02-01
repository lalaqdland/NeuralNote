import React, { useState } from 'react';
import { Card, Button, Space, Typography, Rate, Progress, Tag, Divider } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  QuestionCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { ReviewNode } from '../services/review';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;

interface ReviewCardProps {
  node: ReviewNode;
  onFeedback: (quality: number) => void;
  showAnswer: boolean;
  onToggleAnswer: () => void;
  currentIndex: number;
  totalCount: number;
}

const ReviewCard: React.FC<ReviewCardProps> = ({
  node,
  onFeedback,
  showAnswer,
  onToggleAnswer,
  currentIndex,
  totalCount,
}) => {
  const [selectedQuality, setSelectedQuality] = useState<number | null>(null);

  const getMasteryColor = (level: number) => {
    if (level >= 4) return '#52c41a';
    if (level >= 3) return '#1890ff';
    if (level >= 2) return '#faad14';
    return '#f5222d';
  };

  const getMasteryLabel = (level: number) => {
    const labels = ['未学习', '初步了解', '基本掌握', '熟练掌握', '精通', '完全掌握'];
    return labels[level] || '未知';
  };

  const handleQualitySelect = (quality: number) => {
    setSelectedQuality(quality);
    onFeedback(quality);
  };

  const qualityOptions = [
    { value: 0, label: '完全不会', color: '#f5222d', icon: <CloseCircleOutlined /> },
    { value: 1, label: '有印象', color: '#ff7875', icon: <QuestionCircleOutlined /> },
    { value: 2, label: '想起来了', color: '#faad14', icon: <QuestionCircleOutlined /> },
    { value: 3, label: '比较熟练', color: '#52c41a', icon: <CheckCircleOutlined /> },
    { value: 4, label: '很熟练', color: '#1890ff', icon: <CheckCircleOutlined /> },
    { value: 5, label: '完全掌握', color: '#722ed1', icon: <CheckCircleOutlined /> },
  ];

  return (
    <Card
      style={{
        maxWidth: 800,
        margin: '0 auto',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      }}
    >
      {/* 进度条 */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
          <Text type="secondary">
            第 {currentIndex + 1} / {totalCount} 题
          </Text>
          <Text type="secondary">{Math.round(((currentIndex + 1) / totalCount) * 100)}%</Text>
        </div>
        <Progress
          percent={((currentIndex + 1) / totalCount) * 100}
          showInfo={false}
          strokeColor="#667eea"
        />
      </div>

      {/* 节点信息 */}
      <Space direction="vertical" style={{ width: '100%', marginBottom: 24 }} size="middle">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ margin: 0 }}>
            {node.title}
          </Title>
          <Tag color={getMasteryColor(node.mastery_level)}>
            {getMasteryLabel(node.mastery_level)}
          </Tag>
        </div>

        {/* 复习信息 */}
        <Space split="|" style={{ fontSize: 12 }}>
          <Text type="secondary">
            <ClockCircleOutlined /> 已复习 {node.review_count} 次
          </Text>
          {node.last_reviewed_at && (
            <Text type="secondary">
              上次复习: {dayjs(node.last_reviewed_at).format('YYYY-MM-DD')}
            </Text>
          )}
        </Space>
      </Space>

      <Divider />

      {/* 题目内容 */}
      <div style={{ marginBottom: 24 }}>
        {node.content_data?.question && (
          <div style={{ marginBottom: 16 }}>
            <Text strong style={{ fontSize: 16 }}>
              📝 题目:
            </Text>
            <Paragraph
              style={{
                marginTop: 8,
                padding: 16,
                background: '#f5f5f5',
                borderRadius: 8,
                fontSize: 15,
                lineHeight: 1.8,
              }}
            >
              {node.content_data.question}
            </Paragraph>
          </div>
        )}

        {node.content_data?.description && !node.content_data?.question && (
          <div style={{ marginBottom: 16 }}>
            <Text strong style={{ fontSize: 16 }}>
              📖 内容:
            </Text>
            <Paragraph
              style={{
                marginTop: 8,
                padding: 16,
                background: '#f5f5f5',
                borderRadius: 8,
                fontSize: 15,
                lineHeight: 1.8,
              }}
            >
              {node.content_data.description}
            </Paragraph>
          </div>
        )}

        {/* 显示答案按钮 */}
        {!showAnswer && (
          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <Button type="primary" size="large" onClick={onToggleAnswer}>
              显示答案
            </Button>
          </div>
        )}

        {/* 答案和解析 */}
        {showAnswer && (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            {node.content_data?.answer && (
              <div>
                <Text strong style={{ fontSize: 16, color: '#52c41a' }}>
                  ✅ 答案:
                </Text>
                <Paragraph
                  style={{
                    marginTop: 8,
                    padding: 16,
                    background: '#e6f7ff',
                    borderRadius: 8,
                    fontSize: 15,
                    lineHeight: 1.8,
                  }}
                >
                  {node.content_data.answer}
                </Paragraph>
              </div>
            )}

            {node.content_data?.explanation && (
              <div>
                <Text strong style={{ fontSize: 16, color: '#faad14' }}>
                  💡 解析:
                </Text>
                <Paragraph
                  style={{
                    marginTop: 8,
                    padding: 16,
                    background: '#fff7e6',
                    borderRadius: 8,
                    fontSize: 15,
                    lineHeight: 1.8,
                  }}
                >
                  {node.content_data.explanation}
                </Paragraph>
              </div>
            )}

            {node.content_data?.knowledge_points && node.content_data.knowledge_points.length > 0 && (
              <div>
                <Text strong style={{ fontSize: 16 }}>
                  🎯 知识点:
                </Text>
                <div style={{ marginTop: 8 }}>
                  <Space wrap>
                    {node.content_data.knowledge_points.map((kp: any, index: number) => (
                      <Tag key={index} color="purple" style={{ padding: '4px 12px', fontSize: 14 }}>
                        {typeof kp === 'string' ? kp : kp.name}
                      </Tag>
                    ))}
                  </Space>
                </div>
              </div>
            )}
          </Space>
        )}
      </div>

      {/* 反馈按钮 */}
      {showAnswer && (
        <div>
          <Divider />
          <div style={{ marginBottom: 12 }}>
            <Text strong style={{ fontSize: 16 }}>
              掌握程度评价:
            </Text>
          </div>
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            {qualityOptions.map((option) => (
              <Button
                key={option.value}
                size="large"
                block
                type={selectedQuality === option.value ? 'primary' : 'default'}
                icon={option.icon}
                onClick={() => handleQualitySelect(option.value)}
                style={{
                  height: 48,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderColor: option.color,
                  color: selectedQuality === option.value ? '#fff' : option.color,
                  background: selectedQuality === option.value ? option.color : 'transparent',
                }}
              >
                {option.label}
              </Button>
            ))}
          </Space>
        </div>
      )}
    </Card>
  );
};

export default ReviewCard;

