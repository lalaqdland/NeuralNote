import React, { useEffect, useState } from 'react';
import {
  Modal,
  List,
  Button,
  Space,
  Tag,
  Empty,
  Spin,
  message,
  Form,
  Select,
  InputNumber,
  Typography,
  Divider,
  Card,
  Row,
  Col,
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  LinkOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons';
import { memoryNodeService, NodeRelation, MemoryNode } from '../services/memoryNode';
import { UUID } from '../services/knowledgeGraph';

const { Text, Title } = Typography;

interface NodeRelationsManagerProps {
  visible: boolean;
  nodeId: UUID;
  nodeName: string;
  graphId: UUID;
  onClose: () => void;
}

const NodeRelationsManager: React.FC<NodeRelationsManagerProps> = ({
  visible,
  nodeId,
  nodeName,
  graphId,
  onClose,
}) => {
  const [loading, setLoading] = useState(false);
  const [relations, setRelations] = useState<NodeRelation[]>([]);
  const [nodes, setNodes] = useState<MemoryNode[]>([]);
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible && nodeId) {
      loadRelations();
      loadNodes();
    }
  }, [visible, nodeId]);

  const loadRelations = async () => {
    setLoading(true);
    try {
      const data = await memoryNodeService.getRelations(nodeId);
      setRelations(data);
    } catch (error) {
      message.error('加载关联关系失败');
    } finally {
      setLoading(false);
    }
  };

  const loadNodes = async () => {
    try {
      const response = await memoryNodeService.getNodes(graphId, 1, 100);
      // 过滤掉当前节点
      setNodes(response.items.filter((n) => n.id !== nodeId));
    } catch (error) {
      message.error('加载节点列表失败');
    }
  };

  const handleAddRelation = () => {
    form.resetFields();
    form.setFieldsValue({ strength: 50 });
    setAddModalVisible(true);
  };

  const handleSubmitRelation = async (values: any) => {
    try {
      await memoryNodeService.createRelation({
        source_id: nodeId,
        target_id: values.target_id,
        relation_type: values.relation_type,
        strength: values.strength,
      });
      message.success('创建关联成功');
      setAddModalVisible(false);
      loadRelations();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建关联失败');
    }
  };

  const handleDeleteRelation = async (relationId: UUID) => {
    try {
      await memoryNodeService.deleteRelation(relationId);
      message.success('删除成功');
      loadRelations();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const getRelationTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      prerequisite: '前置知识',
      related: '相关知识',
      similar: '相似知识',
    };
    return labels[type] || type;
  };

  const getRelationTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      prerequisite: 'red',
      related: 'blue',
      similar: 'cyan',
    };
    return colors[type] || 'default';
  };

  const getNodeName = (nodeId: UUID) => {
    const node = nodes.find((n) => n.id === nodeId);
    return node?.title || `节点 #${nodeId}`;
  };

  return (
    <>
      <Modal
        title={
          <Space>
            <LinkOutlined />
            <span>节点关联管理 - {nodeName}</span>
          </Space>
        }
        open={visible}
        onCancel={onClose}
        footer={[
          <Button key="close" onClick={onClose}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* 统计信息 */}
          <Card size="small">
            <Row gutter={16}>
              <Col span={8}>
                <Text type="secondary">出度（指向其他节点）</Text>
                <Title level={3} style={{ margin: '8px 0 0 0' }}>
                  {relations.filter((r) => r.source_id === nodeId).length}
                </Title>
              </Col>
              <Col span={8}>
                <Text type="secondary">入度（被其他节点指向）</Text>
                <Title level={3} style={{ margin: '8px 0 0 0' }}>
                  {relations.filter((r) => r.target_id === nodeId).length}
                </Title>
              </Col>
              <Col span={8}>
                <Text type="secondary">总关联数</Text>
                <Title level={3} style={{ margin: '8px 0 0 0' }}>
                  {relations.length}
                </Title>
              </Col>
            </Row>
          </Card>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <Title level={5} style={{ margin: 0 }}>
                关联列表
              </Title>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleAddRelation}>
                添加关联
              </Button>
            </div>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <Spin />
              </div>
            ) : relations.length === 0 ? (
              <Empty
                description="还没有关联关系"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                style={{ padding: '40px 0' }}
              >
                <Button type="primary" icon={<PlusOutlined />} onClick={handleAddRelation}>
                  添加第一个关联
                </Button>
              </Empty>
            ) : (
              <List
                dataSource={relations}
                renderItem={(relation) => {
                  const isOutgoing = relation.source_id === nodeId;
                  const otherNodeId = isOutgoing ? relation.target_id : relation.source_id;
                  const otherNodeName = getNodeName(otherNodeId);

                  return (
                    <List.Item
                      actions={[
                        <Button
                          type="text"
                          danger
                          icon={<DeleteOutlined />}
                          onClick={() => {
                            Modal.confirm({
                              title: '确认删除',
                              content: '确定要删除这个关联关系吗？',
                              okText: '确认',
                              cancelText: '取消',
                              okType: 'danger',
                              onOk: () => handleDeleteRelation(relation.id),
                            });
                          }}
                        >
                          删除
                        </Button>,
                      ]}
                    >
                      <List.Item.Meta
                        avatar={
                          <div
                            style={{
                              width: 40,
                              height: 40,
                              borderRadius: '50%',
                              background: isOutgoing
                                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                                : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: 'white',
                              fontWeight: 'bold',
                            }}
                          >
                            {isOutgoing ? '出' : '入'}
                          </div>
                        }
                        title={
                          <Space>
                            {isOutgoing ? (
                              <>
                                <Text strong>{nodeName}</Text>
                                <ArrowRightOutlined style={{ color: '#999' }} />
                                <Text>{otherNodeName}</Text>
                              </>
                            ) : (
                              <>
                                <Text>{otherNodeName}</Text>
                                <ArrowRightOutlined style={{ color: '#999' }} />
                                <Text strong>{nodeName}</Text>
                              </>
                            )}
                          </Space>
                        }
                        description={
                          <Space>
                            <Tag color={getRelationTypeColor(relation.relation_type)}>
                              {getRelationTypeLabel(relation.relation_type)}
                            </Tag>
                            <Text type="secondary">强度: {relation.strength}</Text>
                          </Space>
                        }
                      />
                    </List.Item>
                  );
                }}
              />
            )}
          </div>
        </Space>
      </Modal>

      {/* 添加关联模态框 */}
      <Modal
        title="添加关联关系"
        open={addModalVisible}
        onCancel={() => setAddModalVisible(false)}
        onOk={() => form.submit()}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical" onFinish={handleSubmitRelation}>
          <Form.Item
            name="target_id"
            label="目标节点"
            rules={[{ required: true, message: '请选择目标节点' }]}
          >
            <Select
              showSearch
              placeholder="选择要关联的节点"
              optionFilterProp="children"
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={nodes.map((node) => ({
                value: node.id,
                label: `${node.title} (${node.node_type})`,
              }))}
            />
          </Form.Item>

          <Form.Item
            name="relation_type"
            label="关联类型"
            rules={[{ required: true, message: '请选择关联类型' }]}
          >
            <Select placeholder="选择关联类型">
              <Select.Option value="prerequisite">
                <Tag color="red">前置知识</Tag>
                <Text type="secondary">学习当前节点前需要掌握的知识</Text>
              </Select.Option>
              <Select.Option value="related">
                <Tag color="blue">相关知识</Tag>
                <Text type="secondary">与当前节点相关的知识点</Text>
              </Select.Option>
              <Select.Option value="similar">
                <Tag color="cyan">相似</Tag>
                <Text type="secondary">与当前节点相似的知识点</Text>
              </Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="strength"
            label="关联强度"
            rules={[{ required: true, message: '请输入关联强度' }]}
            extra="0 - 100，数值越大表示关联越强"
          >
            <InputNumber
              min={0}
              max={100}
              step={1}
              style={{ width: '100%' }}
              placeholder="例如：80"
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default NodeRelationsManager;

