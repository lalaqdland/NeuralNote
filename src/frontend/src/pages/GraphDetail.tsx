import React, { useEffect, useState, useRef } from 'react';
import {
  Card,
  Button,
  Space,
  Typography,
  Tabs,
  List,
  Tag,
  Empty,
  Spin,
  message,
  Statistic,
  Row,
  Col,
  Breadcrumb,
  Dropdown,
  Modal,
  Form,
  Input,
  Select,
} from 'antd';
import {
  PlusOutlined,
  ArrowLeftOutlined,
  NodeIndexOutlined,
  FileTextOutlined,
  BarChartOutlined,
  EditOutlined,
  DeleteOutlined,
  MoreOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { knowledgeGraphService, KnowledgeGraph } from '../services/knowledgeGraph';
import { memoryNodeService, MemoryNode } from '../services/memoryNode';
import QuestionAnalysisModal from '../components/QuestionAnalysisModal';
import GraphVisualization from '../components/GraphVisualization';
import GraphVisualization3D from '../components/GraphVisualization3D';
import NodeRelationsManager from '../components/NodeRelationsManager';
import StatisticsCharts from '../components/StatisticsCharts';
import dayjs from 'dayjs';
import type { MenuProps } from 'antd';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const GraphDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const graphId = parseInt(id || '0');

  const [loading, setLoading] = useState(false);
  const [graph, setGraph] = useState<KnowledgeGraph | null>(null);
  const [nodes, setNodes] = useState<MemoryNode[]>([]);
  const [relations, setRelations] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState('graph');
  const [analysisModalVisible, setAnalysisModalVisible] = useState(false);
  const [nodeModalVisible, setNodeModalVisible] = useState(false);
  const [relationsModalVisible, setRelationsModalVisible] = useState(false);
  const [editingNode, setEditingNode] = useState<MemoryNode | null>(null);
  const [selectedNode, setSelectedNode] = useState<MemoryNode | null>(null);
  const [viewMode, setViewMode] = useState<'2d' | '3d'>('2d');
  const [form] = Form.useForm();

  useEffect(() => {
    if (graphId) {
      loadGraphDetail();
      loadNodes();
    }
  }, [graphId]);

  useEffect(() => {
    if (nodes.length > 0) {
      loadRelations();
    }
  }, [nodes]);

  const loadGraphDetail = async () => {
    setLoading(true);
    try {
      const data = await knowledgeGraphService.getGraphDetail(graphId);
      setGraph(data);
    } catch (error) {
      message.error('加载图谱详情失败');
      navigate('/graph');
    } finally {
      setLoading(false);
    }
  };

  const loadNodes = async () => {
    try {
      const response = await memoryNodeService.getNodes(graphId, 1, 100);
      setNodes(response.items);
    } catch (error) {
      message.error('加载节点列表失败');
    }
  };

  const loadRelations = async () => {
    try {
      // 获取所有节点的关联关系
      const allRelations: any[] = [];
      for (const node of nodes) {
        const nodeRelations = await memoryNodeService.getRelations(node.id);
        allRelations.push(...nodeRelations);
      }
      // 去重（因为每条边会被两个节点都获取到）
      const uniqueRelations = allRelations.filter(
        (rel, index, self) =>
          index === self.findIndex((r) => r.id === rel.id)
      );
      setRelations(uniqueRelations);
    } catch (error) {
      console.error('加载关联关系失败:', error);
    }
  };

  const handleAnalysisSuccess = () => {
    setAnalysisModalVisible(false);
    loadNodes();
    loadGraphDetail();
    message.success('题目分析完成，已创建记忆节点');
  };

  const handleCreateNode = () => {
    setEditingNode(null);
    form.resetFields();
    form.setFieldsValue({ node_type: 'CONCEPT' });
    setNodeModalVisible(true);
  };

  const handleEditNode = (node: MemoryNode) => {
    setEditingNode(node);
    form.setFieldsValue(node);
    setNodeModalVisible(true);
  };

  const handleDeleteNode = async (nodeId: number) => {
    try {
      await memoryNodeService.deleteNode(nodeId);
      message.success('删除成功');
      loadNodes();
      loadGraphDetail();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmitNode = async (values: any) => {
    try {
      if (editingNode) {
        await memoryNodeService.updateNode(editingNode.id, values);
        message.success('更新成功');
      } else {
        await memoryNodeService.createNode({
          ...values,
          graph_id: graphId,
        });
        message.success('创建成功');
      }
      setNodeModalVisible(false);
      loadNodes();
      loadGraphDetail();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  const handleManageRelations = (node: MemoryNode) => {
    setSelectedNode(node);
    setRelationsModalVisible(true);
  };

  const getNodeMenuItems = (node: MemoryNode): MenuProps['items'] => [
    {
      key: 'relations',
      icon: <NodeIndexOutlined />,
      label: '管理关联',
      onClick: () => handleManageRelations(node),
    },
    {
      key: 'edit',
      icon: <EditOutlined />,
      label: '编辑',
      onClick: () => handleEditNode(node),
    },
    {
      type: 'divider',
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: '删除',
      danger: true,
      onClick: () => {
        Modal.confirm({
          title: '确认删除',
          content: `确定要删除节点"${node.title}"吗？此操作不可恢复。`,
          okText: '确认',
          cancelText: '取消',
          okType: 'danger',
          onOk: () => handleDeleteNode(node.id),
        });
      },
    },
  ];

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

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!graph) {
    return null;
  }

  return (
    <div>
      {/* 面包屑导航 */}
      <Breadcrumb style={{ marginBottom: 16 }}>
        <Breadcrumb.Item>
          <a onClick={() => navigate('/graph')}>知识图谱</a>
        </Breadcrumb.Item>
        <Breadcrumb.Item>{graph.name}</Breadcrumb.Item>
      </Breadcrumb>

      {/* 头部信息 */}
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Space direction="vertical" size="small">
              <Space>
                <Button
                  type="text"
                  icon={<ArrowLeftOutlined />}
                  onClick={() => navigate('/graph')}
                >
                  返回
                </Button>
                <Title level={2} style={{ margin: 0 }}>
                  {graph.name}
                </Title>
                {graph.subject && <Tag color="blue">{graph.subject}</Tag>}
                {graph.is_public && <Tag color="green">公开</Tag>}
              </Space>
              {graph.description && (
                <Paragraph type="secondary" style={{ marginBottom: 0 }}>
                  {graph.description}
                </Paragraph>
              )}
            </Space>

            <Space>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setAnalysisModalVisible(true)}
                size="large"
              >
                添加题目
              </Button>
              <Button icon={<PlusOutlined />} onClick={handleCreateNode} size="large">
                创建节点
              </Button>
            </Space>
          </div>

          {/* 统计信息 */}
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="节点总数"
                value={graph.node_count}
                prefix={<NodeIndexOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="概念节点"
                value={nodes.filter((n) => n.node_type === 'CONCEPT').length}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="题目节点"
                value={nodes.filter((n) => n.node_type === 'QUESTION').length}
                valueStyle={{ color: '#52c41a' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="平均掌握度"
                value={
                  nodes.length > 0
                    ? (nodes.reduce((sum, n) => sum + n.mastery_level, 0) / nodes.length).toFixed(1)
                    : 0
                }
                suffix="/ 5"
                valueStyle={{ color: '#faad14' }}
              />
            </Col>
          </Row>
        </Space>
      </Card>

      {/* 标签页 */}
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: 'graph',
            label: (
              <span>
                <NodeIndexOutlined />
                知识图谱
              </span>
            ),
            children: (
              <Card>
                {nodes.length === 0 ? (
                  <Empty
                    description="还没有节点"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                    style={{ padding: '60px 0' }}
                  >
                    <Space>
                      <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={() => setAnalysisModalVisible(true)}
                      >
                        添加题目
                      </Button>
                      <Button icon={<PlusOutlined />} onClick={handleCreateNode}>
                        创建节点
                      </Button>
                    </Space>
                  </Empty>
                ) : (
                  <div>
                    {/* 2D/3D 切换按钮 */}
                    <div style={{ marginBottom: 16, textAlign: 'right' }}>
                      <Space>
                        <Button
                          type={viewMode === '2d' ? 'primary' : 'default'}
                          onClick={() => setViewMode('2d')}
                        >
                          2D 视图
                        </Button>
                        <Button
                          type={viewMode === '3d' ? 'primary' : 'default'}
                          onClick={() => setViewMode('3d')}
                        >
                          3D 视图
                        </Button>
                      </Space>
                    </div>

                    {/* 渲染对应的图谱 */}
                    {viewMode === '2d' ? (
                      <GraphVisualization graphId={graphId} nodes={nodes} />
                    ) : (
                      <GraphVisualization3D graphId={graphId} nodes={nodes} relations={relations} />
                    )}
                  </div>
                )}
              </Card>
            ),
          },
          {
            key: 'nodes',
            label: (
              <span>
                <FileTextOutlined />
                节点列表 ({nodes.length})
              </span>
            ),
            children: (
              <Card>
                <List
                  dataSource={nodes}
                  renderItem={(node) => (
                    <List.Item
                      actions={[
                        <Dropdown menu={{ items: getNodeMenuItems(node) }} trigger={['click']}>
                          <Button type="text" icon={<MoreOutlined />} />
                        </Dropdown>,
                      ]}
                    >
                      <List.Item.Meta
                        title={
                          <Space>
                            <Text strong>{node.title}</Text>
                            <Tag color={getNodeTypeColor(node.node_type)}>
                              {getNodeTypeLabel(node.node_type)}
                            </Tag>
                            <Tag
                              color={getMasteryColor(node.mastery_level)}
                              style={{ minWidth: 60, textAlign: 'center' }}
                            >
                              掌握度 {node.mastery_level}/5
                            </Tag>
                          </Space>
                        }
                        description={
                          <Space direction="vertical" style={{ width: '100%' }}>
                            {node.content_data?.description && (
                              <Paragraph
                                ellipsis={{ rows: 2 }}
                                style={{ marginBottom: 0, color: '#666' }}
                              >
                                {node.content_data.description}
                              </Paragraph>
                            )}
                            <Space split="|" style={{ fontSize: 12 }}>
                              <Text type="secondary">
                                创建于 {dayjs(node.created_at).format('YYYY-MM-DD HH:mm')}
                              </Text>
                              <Text type="secondary">
                                更新于 {dayjs(node.updated_at).format('YYYY-MM-DD HH:mm')}
                              </Text>
                            </Space>
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              </Card>
            ),
          },
          {
            key: 'stats',
            label: (
              <span>
                <BarChartOutlined />
                统计分析
              </span>
            ),
            children: (
              <Card>
                <StatisticsCharts nodes={nodes} loading={loading} />
              </Card>
            ),
          },
        ]}
      />

      {/* 题目分析模态框 */}
      <QuestionAnalysisModal
        visible={analysisModalVisible}
        graphId={graphId}
        onClose={() => setAnalysisModalVisible(false)}
        onSuccess={handleAnalysisSuccess}
      />

      {/* 创建/编辑节点模态框 */}
      <Modal
        title={editingNode ? '编辑节点' : '创建节点'}
        open={nodeModalVisible}
        onCancel={() => setNodeModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical" onFinish={handleSubmitNode}>
          <Form.Item
            name="title"
            label="节点标题"
            rules={[{ required: true, message: '请输入节点标题' }]}
          >
            <Input placeholder="例如：二次函数、牛顿第一定律" />
          </Form.Item>

          <Form.Item
            name="node_type"
            label="节点类型"
            rules={[{ required: true, message: '请选择节点类型' }]}
          >
            <Select>
              <Select.Option value="CONCEPT">概念</Select.Option>
              <Select.Option value="QUESTION">题目</Select.Option>
              <Select.Option value="NOTE">笔记</Select.Option>
              <Select.Option value="RESOURCE">资源</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name={['content_data', 'description']} label="描述">
            <TextArea rows={4} placeholder="节点的详细描述" />
          </Form.Item>

          <Form.Item name="mastery_level" label="掌握程度" initialValue={0}>
            <Select>
              <Select.Option value={0}>未学习</Select.Option>
              <Select.Option value={1}>初步了解</Select.Option>
              <Select.Option value={2}>基本掌握</Select.Option>
              <Select.Option value={3}>熟练掌握</Select.Option>
              <Select.Option value={4}>精通</Select.Option>
              <Select.Option value={5}>完全掌握</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 节点关联管理模态框 */}
      {selectedNode && (
        <NodeRelationsManager
          visible={relationsModalVisible}
          nodeId={selectedNode.id}
          nodeName={selectedNode.title}
          graphId={graphId}
          onClose={() => {
            setRelationsModalVisible(false);
            setSelectedNode(null);
          }}
        />
      )}
    </div>
  );
};

export default GraphDetailPage;

