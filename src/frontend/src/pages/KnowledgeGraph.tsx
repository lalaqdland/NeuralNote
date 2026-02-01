import React, { useEffect, useState } from 'react';
import {
  Card,
  Button,
  Modal,
  Form,
  Input,
  Switch,
  message,
  Row,
  Col,
  Empty,
  Spin,
  Tag,
  Space,
  Typography,
  Dropdown,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  MoreOutlined,
  BookOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import {
  knowledgeGraphService,
  KnowledgeGraph,
  CreateGraphRequest,
  UpdateGraphRequest,
} from '../services/knowledgeGraph';
import { useAppDispatch } from '../store/hooks';
import { setGraphs, addGraph, updateGraph as updateGraphAction, removeGraph } from '../store/graphSlice';
import ExportDataModal from '../components/ExportDataModal';
import dayjs from 'dayjs';
import type { MenuProps } from 'antd';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const KnowledgeGraphPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const dispatch = useAppDispatch();
  
  const [loading, setLoading] = useState(false);
  const [graphs, setGraphsList] = useState<KnowledgeGraph[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingGraph, setEditingGraph] = useState<KnowledgeGraph | null>(null);
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const [exportingGraph, setExportingGraph] = useState<KnowledgeGraph | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadGraphs();
  }, []);

  const loadGraphs = async () => {
    setLoading(true);
    try {
      const response = await knowledgeGraphService.getGraphs(1, 50);
      setGraphsList(response.items);
      dispatch(setGraphs(response.items));
    } catch (error) {
      message.error('加载知识图谱失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingGraph(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (graph: KnowledgeGraph) => {
    setEditingGraph(graph);
    form.setFieldsValue(graph);
    setModalVisible(true);
  };

  const handleDelete = async (graphId: number) => {
    try {
      await knowledgeGraphService.deleteGraph(graphId);
      message.success('删除成功');
      dispatch(removeGraph(graphId));
      loadGraphs();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async (values: CreateGraphRequest | UpdateGraphRequest) => {
    try {
      if (editingGraph) {
        // 更新
        const updated = await knowledgeGraphService.updateGraph(editingGraph.id, values);
        message.success('更新成功');
        dispatch(updateGraphAction(updated));
      } else {
        // 创建
        const created = await knowledgeGraphService.createGraph(values as CreateGraphRequest);
        message.success('创建成功');
        dispatch(addGraph(created));
      }
      setModalVisible(false);
      loadGraphs();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  const getMenuItems = (graph: KnowledgeGraph): MenuProps['items'] => [
    {
      key: 'view',
      icon: <EyeOutlined />,
      label: '查看详情',
      onClick: () => navigate(`/graph/${graph.id}`),
    },
    {
      key: 'edit',
      icon: <EditOutlined />,
      label: '编辑',
      onClick: () => handleEdit(graph),
    },
    {
      key: 'export',
      icon: <DownloadOutlined />,
      label: '导出数据',
      onClick: () => {
        setExportingGraph(graph);
        setExportModalVisible(true);
      },
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
          content: `确定要删除知识图谱"${graph.name}"吗？此操作不可恢复。`,
          okText: '确认',
          cancelText: '取消',
          okType: 'danger',
          onOk: () => handleDelete(graph.id),
        });
      },
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ marginBottom: 8 }}>
            知识图谱
          </Title>
          <Text type="secondary">管理你的知识图谱，构建知识体系</Text>
        </div>
        <Button type="primary" size="large" icon={<PlusOutlined />} onClick={handleCreate}>
          创建图谱
        </Button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '80px 0' }}>
          <Spin size="large" />
        </div>
      ) : graphs.length === 0 ? (
        <Card>
          <Empty
            description="还没有知识图谱"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            style={{ padding: '60px 0' }}
          >
            <Button type="primary" size="large" icon={<PlusOutlined />} onClick={handleCreate}>
              创建第一个图谱
            </Button>
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {graphs.map((graph) => (
            <Col xs={24} sm={12} lg={8} xl={6} key={graph.id}>
              <Card
                hoverable
                style={{ height: '100%' }}
                cover={
                  <div
                    style={{
                      height: 160,
                      background: graph.cover_image_url
                        ? `url(${graph.cover_image_url}) center/cover`
                        : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: 48,
                      fontWeight: 700,
                      cursor: 'pointer',
                    }}
                    onClick={() => navigate(`/graph/${graph.id}`)}
                  >
                    {!graph.cover_image_url && graph.name.charAt(0)}
                  </div>
                }
                actions={[
                  <Button
                    type="text"
                    icon={<EyeOutlined />}
                    onClick={() => navigate(`/graph/${graph.id}`)}
                  >
                    查看
                  </Button>,
                  <Button type="text" icon={<EditOutlined />} onClick={() => handleEdit(graph)}>
                    编辑
                  </Button>,
                  <Dropdown menu={{ items: getMenuItems(graph) }} trigger={['click']}>
                    <Button type="text" icon={<MoreOutlined />} />
                  </Dropdown>,
                ]}
              >
                <Card.Meta
                  title={
                    <Space>
                      <Text strong ellipsis style={{ maxWidth: 150 }}>
                        {graph.name}
                      </Text>
                      {graph.is_public && <Tag color="green">公开</Tag>}
                    </Space>
                  }
                  description={
                    <Space direction="vertical" style={{ width: '100%' }}>
                      {graph.subject && <Tag color="blue">{graph.subject}</Tag>}
                      <Paragraph
                        ellipsis={{ rows: 2 }}
                        style={{ marginBottom: 8, minHeight: 40 }}
                      >
                        {graph.description || '暂无描述'}
                      </Paragraph>
                      <Space split="|" style={{ fontSize: 12 }}>
                        <Text type="secondary">
                          <BookOutlined /> {graph.node_count} 节点
                        </Text>
                        <Text type="secondary">{dayjs(graph.updated_at).format('MM-DD')}</Text>
                      </Space>
                    </Space>
                  }
                />
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {/* 创建/编辑模态框 */}
      <Modal
        title={editingGraph ? '编辑知识图谱' : '创建知识图谱'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
        okText="确定"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{ is_public: false }}
        >
          <Form.Item
            name="name"
            label="图谱名称"
            rules={[
              { required: true, message: '请输入图谱名称' },
              { max: 100, message: '名称不能超过100个字符' },
            ]}
          >
            <Input placeholder="例如：高等数学、Python编程" />
          </Form.Item>

          <Form.Item name="subject" label="学科分类">
            <Input placeholder="例如：数学、编程、英语" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea
              rows={4}
              placeholder="简要描述这个知识图谱的内容和用途"
              maxLength={500}
              showCount
            />
          </Form.Item>

          <Form.Item name="cover_image_url" label="封面图片URL">
            <Input placeholder="https://example.com/image.jpg" />
          </Form.Item>

          <Form.Item name="is_public" label="公开图谱" valuePropName="checked">
            <Switch checkedChildren="公开" unCheckedChildren="私密" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 数据导出模态框 */}
      {exportingGraph && (
        <ExportDataModal
          visible={exportModalVisible}
          graphId={exportingGraph.id}
          graphName={exportingGraph.name}
          onClose={() => {
            setExportModalVisible(false);
            setExportingGraph(null);
          }}
        />
      )}
    </div>
  );
};

export default KnowledgeGraphPage;
