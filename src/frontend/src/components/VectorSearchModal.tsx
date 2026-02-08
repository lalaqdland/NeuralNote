import React, { useState } from 'react';
import {
  Modal,
  Input,
  Button,
  List,
  Tag,
  Empty,
  Spin,
  Space,
  Typography,
  Card,
  Progress,
  Divider,
  Select,
  Slider,
} from 'antd';
import {
  SearchOutlined,
  BulbOutlined,
  NodeIndexOutlined,
  FireOutlined,
} from '@ant-design/icons';
import { vectorSearchService, SimilarNode } from '../services/vectorSearch';
import { useNavigate } from 'react-router-dom';
import { UUID } from '../services/knowledgeGraph';

const { Text, Title, Paragraph } = Typography;
const { TextArea } = Input;

interface VectorSearchModalProps {
  visible: boolean;
  graphId?: UUID;
  onClose: () => void;
}

const VectorSearchModal: React.FC<VectorSearchModalProps> = ({
  visible,
  graphId,
  onClose,
}) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SimilarNode[]>([]);
  const [topK, setTopK] = useState(10);
  const [threshold, setThreshold] = useState(0.7);

  const handleSearch = async () => {
    if (!query.trim()) {
      return;
    }

    setLoading(true);
    try {
      const data = await vectorSearchService.searchByText({
        query: query.trim(),
        graph_id: graphId,
        top_k: topK,
        threshold,
      });
      setResults(data);
    } catch (error) {
      console.error('搜索失败:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const getNodeTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      CONCEPT: 'blue',
      QUESTION: 'green',
      NOTE: 'orange',
      RESOURCE: 'purple',
    };
    return colors[type] || 'default';
  };

  const getNodeTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      CONCEPT: '概念',
      QUESTION: '题目',
      NOTE: '笔记',
      RESOURCE: '资源',
    };
    return labels[type] || type;
  };

  const getMasteryColor = (level: number) => {
    if (level >= 4) return '#52c41a';
    if (level >= 3) return '#1890ff';
    if (level >= 2) return '#faad14';
    return '#f5222d';
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.9) return '#52c41a';
    if (similarity >= 0.8) return '#1890ff';
    if (similarity >= 0.7) return '#faad14';
    return '#f5222d';
  };

  return (
    <Modal
      title={
        <Space>
          <SearchOutlined />
          <span>智能搜索</span>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
      style={{ top: 20 }}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 搜索框 */}
        <Card size="small">
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <div>
              <Text strong>搜索内容</Text>
              <TextArea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="输入问题、概念或关键词，AI 将为你找到相关的知识节点..."
                rows={3}
                onPressEnter={(e) => {
                  if (e.ctrlKey || e.metaKey) {
                    handleSearch();
                  }
                }}
              />
              <Text type="secondary" style={{ fontSize: 12 }}>
                提示：按 Ctrl+Enter 快速搜索
              </Text>
            </div>

            <div>
              <Space style={{ width: '100%' }} size="large">
                <div style={{ flex: 1 }}>
                  <Text strong>返回结果数</Text>
                  <Select
                    value={topK}
                    onChange={setTopK}
                    style={{ width: '100%', marginTop: 8 }}
                    options={[
                      { label: '5 个', value: 5 },
                      { label: '10 个', value: 10 },
                      { label: '20 个', value: 20 },
                      { label: '50 个', value: 50 },
                    ]}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <Text strong>相似度阈值: {threshold.toFixed(2)}</Text>
                  <Slider
                    min={0.5}
                    max={1.0}
                    step={0.05}
                    value={threshold}
                    onChange={setThreshold}
                    marks={{
                      0.5: '0.5',
                      0.7: '0.7',
                      0.9: '0.9',
                      1.0: '1.0',
                    }}
                    style={{ marginTop: 8 }}
                  />
                </div>
              </Space>
            </div>

            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleSearch}
              loading={loading}
              size="large"
              block
            >
              搜索
            </Button>
          </Space>
        </Card>

        {/* 搜索结果 */}
        <div style={{ maxHeight: 500, overflowY: 'auto' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <Spin size="large" tip="正在搜索相关知识..." />
            </div>
          ) : results.length === 0 ? (
            query ? (
              <Empty
                description="没有找到相关节点"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                style={{ padding: '40px 0' }}
              >
                <Text type="secondary">尝试调整搜索关键词或降低相似度阈值</Text>
              </Empty>
            ) : (
              <Empty
                description="输入搜索内容开始查找"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                style={{ padding: '40px 0' }}
              >
                <Space direction="vertical">
                  <BulbOutlined style={{ fontSize: 32, color: '#faad14' }} />
                  <Text type="secondary">AI 将基于语义理解为你找到最相关的知识节点</Text>
                </Space>
              </Empty>
            )
          ) : (
            <>
              <div style={{ marginBottom: 16 }}>
                <Text type="secondary">
                  找到 <Text strong>{results.length}</Text> 个相关节点
                </Text>
              </div>
              <List
                dataSource={results}
                renderItem={(item, index) => (
                  <List.Item
                    key={item.node.id}
                    style={{
                      background: '#fafafa',
                      marginBottom: 8,
                      padding: 16,
                      borderRadius: 8,
                      cursor: 'pointer',
                    }}
                    onClick={() => {
                      navigate(`/graph/${item.node.graph_id}`);
                      onClose();
                    }}
                  >
                    <List.Item.Meta
                      avatar={
                        <div
                          style={{
                            width: 48,
                            height: 48,
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            fontWeight: 'bold',
                            fontSize: 18,
                          }}
                        >
                          {index + 1}
                        </div>
                      }
                      title={
                        <Space>
                          <Text strong style={{ fontSize: 16 }}>
                            {item.node.title}
                          </Text>
                          <Tag color={getNodeTypeColor(item.node.node_type)}>
                            {getNodeTypeLabel(item.node.node_type)}
                          </Tag>
                          <Tag
                            color={getMasteryColor(item.node.mastery_level)}
                            style={{ minWidth: 60, textAlign: 'center' }}
                          >
                            掌握度 {item.node.mastery_level}/5
                          </Tag>
                        </Space>
                      }
                      description={
                        <Space direction="vertical" style={{ width: '100%' }}>
                          {item.node.content_data?.description && (
                            <Paragraph
                              ellipsis={{ rows: 2 }}
                              style={{ marginBottom: 8, color: '#666' }}
                            >
                              {item.node.content_data.description}
                            </Paragraph>
                          )}
                          <Space>
                            <Text
                              strong
                              style={{
                                color: getSimilarityColor(item.similarity),
                                fontSize: 14,
                              }}
                            >
                              <FireOutlined /> 相似度: {(item.similarity * 100).toFixed(1)}%
                            </Text>
                            <Progress
                              percent={item.similarity * 100}
                              strokeColor={getSimilarityColor(item.similarity)}
                              showInfo={false}
                              style={{ width: 100 }}
                            />
                          </Space>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </>
          )}
        </div>
      </Space>
    </Modal>
  );
};

export default VectorSearchModal;

