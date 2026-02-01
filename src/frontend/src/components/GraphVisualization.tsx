import React, { useEffect, useRef, useState } from 'react';
import { Empty, Spin, Select, Space, Button, message } from 'antd';
import {
  ZoomInOutlined,
  ZoomOutOutlined,
  FullscreenOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import cytoscape, { Core, NodeSingular } from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { MemoryNode } from '../services/memoryNode';

// 注册 dagre 布局
cytoscape.use(dagre);

interface GraphVisualizationProps {
  graphId: number;
  nodes: MemoryNode[];
  onNodeClick?: (node: MemoryNode) => void;
}

type LayoutType = 'dagre' | 'circle' | 'grid' | 'concentric';

const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  graphId,
  nodes,
  onNodeClick,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [loading, setLoading] = useState(true);
  const [layout, setLayout] = useState<LayoutType>('dagre');

  useEffect(() => {
    if (containerRef.current && nodes.length > 0) {
      initGraph();
    }
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [nodes, layout]);

  const initGraph = () => {
    if (!containerRef.current) return;

    setLoading(true);

    // 准备节点数据
    const cyNodes = nodes.map((node) => ({
      data: {
        id: node.id.toString(),
        label: node.title,
        type: node.node_type,
        mastery: node.mastery_level,
        nodeData: node,
      },
    }));

    // 准备边数据（这里暂时为空，后续可以从 node_relations 获取）
    const cyEdges: any[] = [];

    // 获取节点颜色
    const getNodeColor = (mastery: number) => {
      if (mastery >= 4) return '#52c41a'; // 绿色 - 精通
      if (mastery >= 3) return '#1890ff'; // 蓝色 - 熟练
      if (mastery >= 2) return '#faad14'; // 橙色 - 基本掌握
      if (mastery >= 1) return '#ff7875'; // 红色 - 初步了解
      return '#d9d9d9'; // 灰色 - 未学习
    };

    // 获取节点形状
    const getNodeShape = (type: string) => {
      const shapes: Record<string, string> = {
        CONCEPT: 'ellipse',
        QUESTION: 'rectangle',
        NOTE: 'round-rectangle',
        RESOURCE: 'diamond',
      };
      return shapes[type] || 'ellipse';
    };

    // 初始化 Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements: [...cyNodes, ...cyEdges],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele: NodeSingular) => getNodeColor(ele.data('mastery')),
            label: 'data(label)',
            color: '#fff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '14px',
            'font-weight': 'bold',
            width: 80,
            height: 80,
            'text-wrap': 'wrap',
            'text-max-width': '70px',
            shape: 'ellipse',
            'border-width': 3,
            'border-color': '#fff',
            'overlay-padding': '6px',
            'z-index': 10,
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#667eea',
            'overlay-opacity': 0.2,
            'overlay-color': '#667eea',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 3,
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 1.5,
          },
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#667eea',
            'target-arrow-color': '#667eea',
            width: 4,
          },
        },
      ],
      layout: getLayoutConfig(layout),
      minZoom: 0.3,
      maxZoom: 3,
      wheelSensitivity: 0.2,
    });

    // 节点点击事件
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const nodeData = node.data('nodeData') as MemoryNode;
      if (onNodeClick) {
        onNodeClick(nodeData);
      }
      message.info(`点击了节点: ${nodeData.title}`);
    });

    // 节点悬停效果
    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target;
      node.style({
        'border-width': 5,
        'border-color': '#667eea',
      });
    });

    cy.on('mouseout', 'node', (evt) => {
      const node = evt.target;
      if (!node.selected()) {
        node.style({
          'border-width': 3,
          'border-color': '#fff',
        });
      }
    });

    cyRef.current = cy;
    setLoading(false);
  };

  const getLayoutConfig = (layoutType: LayoutType) => {
    const configs: Record<LayoutType, any> = {
      dagre: {
        name: 'dagre',
        rankDir: 'TB',
        nodeSep: 50,
        rankSep: 100,
        padding: 30,
        animate: true,
        animationDuration: 500,
      },
      circle: {
        name: 'circle',
        padding: 30,
        animate: true,
        animationDuration: 500,
      },
      grid: {
        name: 'grid',
        padding: 30,
        rows: Math.ceil(Math.sqrt(nodes.length)),
        animate: true,
        animationDuration: 500,
      },
      concentric: {
        name: 'concentric',
        padding: 30,
        animate: true,
        animationDuration: 500,
        concentric: (node: NodeSingular) => node.data('mastery'),
        levelWidth: () => 2,
      },
    };
    return configs[layoutType];
  };

  const handleZoomIn = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 1.2);
      cyRef.current.center();
    }
  };

  const handleZoomOut = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 0.8);
      cyRef.current.center();
    }
  };

  const handleFit = () => {
    if (cyRef.current) {
      cyRef.current.fit(undefined, 50);
    }
  };

  const handleReset = () => {
    if (cyRef.current) {
      cyRef.current.layout(getLayoutConfig(layout)).run();
      setTimeout(() => {
        cyRef.current?.fit(undefined, 50);
      }, 600);
    }
  };

  if (nodes.length === 0) {
    return (
      <Empty
        description="还没有节点"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        style={{ padding: '60px 0' }}
      />
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      {/* 控制面板 */}
      <div
        style={{
          position: 'absolute',
          top: 16,
          right: 16,
          zIndex: 100,
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '12px',
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        }}
      >
        <Space direction="vertical" size="small">
          <Select
            value={layout}
            onChange={setLayout}
            style={{ width: 150 }}
            options={[
              { label: '层次布局', value: 'dagre' },
              { label: '环形布局', value: 'circle' },
              { label: '网格布局', value: 'grid' },
              { label: '同心圆布局', value: 'concentric' },
            ]}
          />
          <Space>
            <Button icon={<ZoomInOutlined />} onClick={handleZoomIn} size="small" />
            <Button icon={<ZoomOutOutlined />} onClick={handleZoomOut} size="small" />
          </Space>
          <Button icon={<FullscreenOutlined />} onClick={handleFit} size="small" block>
            适应画布
          </Button>
          <Button icon={<ReloadOutlined />} onClick={handleReset} size="small" block>
            重置布局
          </Button>
        </Space>
      </div>

      {/* 图例 */}
      <div
        style={{
          position: 'absolute',
          bottom: 16,
          left: 16,
          zIndex: 100,
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '12px',
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        }}
      >
        <div style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 8 }}>掌握程度</div>
        <Space direction="vertical" size={4}>
          {[
            { label: '完全掌握', color: '#52c41a' },
            { label: '熟练掌握', color: '#1890ff' },
            { label: '基本掌握', color: '#faad14' },
            { label: '初步了解', color: '#ff7875' },
            { label: '未学习', color: '#d9d9d9' },
          ].map((item) => (
            <div key={item.label} style={{ display: 'flex', alignItems: 'center', fontSize: 12 }}>
              <div
                style={{
                  width: 16,
                  height: 16,
                  borderRadius: '50%',
                  background: item.color,
                  marginRight: 8,
                }}
              />
              <span>{item.label}</span>
            </div>
          ))}
        </Space>
      </div>

      {/* 图谱容器 */}
      {loading && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 200,
          }}
        >
          <Spin size="large" />
        </div>
      )}
      <div
        ref={containerRef}
        style={{
          width: '100%',
          height: '600px',
          background: '#fafafa',
          borderRadius: 8,
          border: '1px solid #e8e8e8',
        }}
      />
    </div>
  );
};

export default GraphVisualization;

