import React, { useState } from 'react';
import {
  Modal,
  Form,
  Radio,
  Checkbox,
  Button,
  Space,
  Alert,
  Typography,
  Divider,
  message,
  Spin,
} from 'antd';
import {
  DownloadOutlined,
  FileTextOutlined,
  FileExcelOutlined,
  FileMarkdownOutlined,
} from '@ant-design/icons';
import { knowledgeGraphService } from '../services/knowledgeGraph';
import { memoryNodeService } from '../services/memoryNode';
import { reviewService } from '../services/review';
import { exportService, ExportFormat, ExportData } from '../services/export';

const { Text, Paragraph } = Typography;

interface ExportDataModalProps {
  visible: boolean;
  graphId: number;
  graphName: string;
  onClose: () => void;
}

const ExportDataModal: React.FC<ExportDataModalProps> = ({ visible, graphId, graphName, onClose }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [format, setFormat] = useState<ExportFormat>('json');

  const handleExport = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      // 获取图谱信息
      const graph = await knowledgeGraphService.getGraph(graphId);

      // 获取所有节点
      const nodesResponse = await memoryNodeService.getNodes(graphId, 1, 10000);
      const nodes = nodesResponse.items;

      // 准备导出数据
      const exportData: ExportData = {
        graph,
        nodes,
        exportTime: new Date().toISOString(),
      };

      // 获取关联关系（如果需要）
      if (values.includeRelations) {
        const relations = [];
        for (const node of nodes) {
          try {
            const nodeRelations = await memoryNodeService.getNodeRelations(node.id);
            relations.push(...nodeRelations);
          } catch (error) {
            console.warn(`获取节点 ${node.id} 的关联关系失败:`, error);
          }
        }
        exportData.relations = relations;
      }

      // 获取统计信息（如果需要）
      if (values.includeStats) {
        try {
          const stats = await reviewService.getReviewStats(graphId);
          exportData.stats = stats;
        } catch (error) {
          console.warn('获取统计信息失败:', error);
        }
      }

      // 导出数据
      await exportService.exportData(exportData, {
        format: values.format,
        includeRelations: values.includeRelations,
        includeStats: values.includeStats,
      });

      message.success('导出成功');
      onClose();
    } catch (error: any) {
      console.error('导出失败:', error);
      message.error(error.message || '导出失败');
    } finally {
      setLoading(false);
    }
  };

  const formatOptions = [
    {
      value: 'json',
      label: 'JSON',
      icon: <FileTextOutlined />,
      description: '结构化数据格式，适合程序处理和数据迁移',
      color: '#1890ff',
    },
    {
      value: 'csv',
      label: 'CSV',
      icon: <FileExcelOutlined />,
      description: '表格格式，可用 Excel 打开，适合数据分析',
      color: '#52c41a',
    },
    {
      value: 'markdown',
      label: 'Markdown',
      icon: <FileMarkdownOutlined />,
      description: '文档格式，可读性强，适合分享和阅读',
      color: '#722ed1',
    },
  ];

  return (
    <Modal
      title={
        <Space>
          <DownloadOutlined />
          导出数据
        </Space>
      }
      open={visible}
      onCancel={onClose}
      width={600}
      footer={[
        <Button key="cancel" onClick={onClose}>
          取消
        </Button>,
        <Button
          key="export"
          type="primary"
          icon={<DownloadOutlined />}
          onClick={handleExport}
          loading={loading}
        >
          导出
        </Button>,
      ]}
    >
      <Alert
        message="导出知识图谱数据"
        description={`即将导出「${graphName}」的所有数据，包括节点、关联关系和统计信息`}
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Form
        form={form}
        layout="vertical"
        initialValues={{
          format: 'json',
          includeRelations: true,
          includeStats: true,
        }}
      >
        <Form.Item name="format" label="导出格式">
          <Radio.Group onChange={(e) => setFormat(e.target.value)} style={{ width: '100%' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {formatOptions.map((option) => (
                <Radio.Button
                  key={option.value}
                  value={option.value}
                  style={{
                    width: '100%',
                    height: 'auto',
                    padding: '12px 16px',
                    textAlign: 'left',
                    borderColor: format === option.value ? option.color : undefined,
                    borderWidth: format === option.value ? 2 : 1,
                  }}
                >
                  <Space direction="vertical" size={0} style={{ width: '100%' }}>
                    <Space>
                      <span style={{ fontSize: 20, color: option.color }}>{option.icon}</span>
                      <Text strong style={{ fontSize: 16 }}>
                        {option.label}
                      </Text>
                    </Space>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {option.description}
                    </Text>
                  </Space>
                </Radio.Button>
              ))}
            </Space>
          </Radio.Group>
        </Form.Item>

        <Divider />

        <Form.Item label="导出选项">
          <Space direction="vertical">
            <Form.Item name="includeRelations" valuePropName="checked" noStyle>
              <Checkbox>包含节点关联关系</Checkbox>
            </Form.Item>
            <Form.Item name="includeStats" valuePropName="checked" noStyle>
              <Checkbox>包含学习统计信息</Checkbox>
            </Form.Item>
          </Space>
        </Form.Item>
      </Form>

      {loading && (
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <Spin size="large" />
          <Paragraph style={{ marginTop: 16 }}>正在导出数据，请稍候...</Paragraph>
        </div>
      )}

      <Alert
        message="提示"
        description={
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li>导出的文件将自动下载到您的浏览器下载目录</li>
            <li>文件名格式：图谱名称_时间戳.扩展名</li>
            <li>导出的数据仅包含当前知识图谱的内容</li>
          </ul>
        }
        type="warning"
        showIcon
        style={{ marginTop: 16 }}
      />
    </Modal>
  );
};

export default ExportDataModal;

