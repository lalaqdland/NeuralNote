import React, { useEffect, useRef, useState, useMemo } from 'react';
import { Empty, Spin, Select, Space, Button, message, Slider } from 'antd';
import {
  ZoomInOutlined,
  ZoomOutOutlined,
  FullscreenOutlined,
  ReloadOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text, Line, Sphere, Box, Cone, Octahedron } from '@react-three/drei';
import * as THREE from 'three';
import { MemoryNode } from '../services/memoryNode';
import { UUID } from '../services/knowledgeGraph';

interface GraphVisualization3DProps {
  graphId: UUID;
  nodes: MemoryNode[];
  relations?: Array<{
    source_id: UUID;
    target_id: UUID;
    relation_type: string;
    strength: number;
  }>;
  onNodeClick?: (node: MemoryNode) => void;
}

interface Node3D {
  id: UUID;
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  node: MemoryNode;
}

type LayoutType = 'force' | 'sphere' | 'helix' | 'grid';

// 获取节点颜色
const getNodeColor = (mastery: number): string => {
  if (mastery >= 4) return '#52c41a'; // 绿色 - 精通
  if (mastery >= 3) return '#1890ff'; // 蓝色 - 熟练
  if (mastery >= 2) return '#faad14'; // 橙色 - 基本掌握
  if (mastery >= 1) return '#ff7875'; // 红色 - 初步了解
  return '#d9d9d9'; // 灰色 - 未学习
};

// 获取节点大小
const getNodeSize = (mastery: number): number => {
  return 0.3 + mastery * 0.1; // 0.3 - 0.8
};

// 3D 节点组件
const Node3D: React.FC<{
  node: MemoryNode;
  position: THREE.Vector3;
  onClick: () => void;
  isSelected: boolean;
}> = ({ node, position, onClick, isSelected }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame(() => {
    if (meshRef.current) {
      // 选中或悬停时的动画效果
      const targetScale = isSelected || hovered ? 1.3 : 1;
      meshRef.current.scale.lerp(
        new THREE.Vector3(targetScale, targetScale, targetScale),
        0.1
      );
    }
  });

  const color = getNodeColor(node.mastery_level);
  const size = getNodeSize(node.mastery_level);

  // 根据节点类型选择不同的几何体
  const renderGeometry = () => {
    switch (node.node_type) {
      case 'CONCEPT':
        return <Sphere args={[size, 32, 32]} />;
      case 'QUESTION':
        return <Box args={[size * 1.5, size * 1.5, size * 1.5]} />;
      case 'NOTE':
        return <Cone args={[size, size * 2, 32]} />;
      case 'RESOURCE':
        return <Octahedron args={[size * 1.2]} />;
      default:
        return <Sphere args={[size, 32, 32]} />;
    }
  };

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation();
          onClick();
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={() => {
          setHovered(false);
          document.body.style.cursor = 'auto';
        }}
      >
        {renderGeometry()}
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isSelected || hovered ? 0.5 : 0.2}
          metalness={0.3}
          roughness={0.4}
        />
      </mesh>

      {/* 节点标签 */}
      <Text
        position={[0, size + 0.5, 0]}
        fontSize={0.3}
        color="#333"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.02}
        outlineColor="#fff"
      >
        {node.title}
      </Text>

      {/* 选中时的光环效果 */}
      {(isSelected || hovered) && (
        <mesh>
          <ringGeometry args={[size * 1.5, size * 1.8, 32]} />
          <meshBasicMaterial color="#667eea" transparent opacity={0.5} side={THREE.DoubleSide} />
        </mesh>
      )}
    </group>
  );
};

// 3D 边组件
const Edge3D: React.FC<{
  start: THREE.Vector3;
  end: THREE.Vector3;
  color?: string;
}> = ({ start, end, color = '#cccccc' }) => {
  const points = useMemo(() => [start, end], [start, end]);

  return (
    <Line
      points={points}
      color={color}
      lineWidth={2}
      transparent
      opacity={0.6}
    />
  );
};

// 力导向布局算法
const useForceLayout = (nodes: MemoryNode[], relations: any[]) => {
  const [nodes3D, setNodes3D] = useState<Node3D[]>([]);

  useEffect(() => {
    // 初始化节点位置
    const initialNodes: Node3D[] = nodes.map((node, index) => ({
      id: node.id,
      position: new THREE.Vector3(
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 20
      ),
      velocity: new THREE.Vector3(0, 0, 0),
      node,
    }));

    setNodes3D(initialNodes);

    // 力导向布局迭代
    const iterations = 100;
    const repulsionStrength = 50;
    const attractionStrength = 0.01;
    const damping = 0.9;

    for (let iter = 0; iter < iterations; iter++) {
      // 计算斥力（所有节点之间）
      for (let i = 0; i < initialNodes.length; i++) {
        for (let j = i + 1; j < initialNodes.length; j++) {
          const nodeA = initialNodes[i];
          const nodeB = initialNodes[j];
          const delta = new THREE.Vector3().subVectors(nodeA.position, nodeB.position);
          const distance = delta.length();

          if (distance > 0) {
            const force = repulsionStrength / (distance * distance);
            delta.normalize().multiplyScalar(force);
            nodeA.velocity.add(delta);
            nodeB.velocity.sub(delta);
          }
        }
      }

      // 计算引力（有关联的节点之间）
      relations.forEach((rel) => {
        const sourceNode = initialNodes.find((n) => n.id === rel.source_id);
        const targetNode = initialNodes.find((n) => n.id === rel.target_id);

        if (sourceNode && targetNode) {
          const delta = new THREE.Vector3().subVectors(
            targetNode.position,
            sourceNode.position
          );
          const distance = delta.length();
          const force = distance * attractionStrength * rel.strength;
          delta.normalize().multiplyScalar(force);

          sourceNode.velocity.add(delta);
          targetNode.velocity.sub(delta);
        }
      });

      // 更新位置
      initialNodes.forEach((node) => {
        node.position.add(node.velocity);
        node.velocity.multiplyScalar(damping);
      });
    }

    setNodes3D(initialNodes);
  }, [nodes, relations]);

  return nodes3D;
};

// 球形布局
const useSphereLayout = (nodes: MemoryNode[]) => {
  return useMemo(() => {
    const radius = 10;
    return nodes.map((node, index) => {
      const phi = Math.acos(-1 + (2 * index) / nodes.length);
      const theta = Math.sqrt(nodes.length * Math.PI) * phi;

      return {
        id: node.id,
        position: new THREE.Vector3(
          radius * Math.cos(theta) * Math.sin(phi),
          radius * Math.sin(theta) * Math.sin(phi),
          radius * Math.cos(phi)
        ),
        velocity: new THREE.Vector3(0, 0, 0),
        node,
      };
    });
  }, [nodes]);
};

// 螺旋布局
const useHelixLayout = (nodes: MemoryNode[]) => {
  return useMemo(() => {
    const radius = 8;
    const height = 20;
    return nodes.map((node, index) => {
      const t = index / nodes.length;
      const angle = t * Math.PI * 4; // 2圈螺旋

      return {
        id: node.id,
        position: new THREE.Vector3(
          radius * Math.cos(angle),
          height * (t - 0.5),
          radius * Math.sin(angle)
        ),
        velocity: new THREE.Vector3(0, 0, 0),
        node,
      };
    });
  }, [nodes]);
};

// 网格布局
const useGridLayout = (nodes: MemoryNode[]) => {
  return useMemo(() => {
    const gridSize = Math.ceil(Math.cbrt(nodes.length));
    const spacing = 3;

    return nodes.map((node, index) => {
      const x = (index % gridSize) - gridSize / 2;
      const y = Math.floor((index / gridSize) % gridSize) - gridSize / 2;
      const z = Math.floor(index / (gridSize * gridSize)) - gridSize / 2;

      return {
        id: node.id,
        position: new THREE.Vector3(x * spacing, y * spacing, z * spacing),
        velocity: new THREE.Vector3(0, 0, 0),
        node,
      };
    });
  }, [nodes]);
};

// 场景组件
const Scene: React.FC<{
  nodes3D: Node3D[];
  relations: any[];
  onNodeClick: (node: MemoryNode) => void;
  selectedNodeId: UUID | null;
  autoRotate: boolean;
}> = ({ nodes3D, relations, onNodeClick, selectedNodeId, autoRotate }) => {
  const { camera } = useThree();

  useEffect(() => {
    camera.position.set(20, 20, 20);
    camera.lookAt(0, 0, 0);
  }, [camera]);

  return (
    <>
      {/* 环境光 */}
      <ambientLight intensity={0.5} />

      {/* 方向光 */}
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <directionalLight position={[-10, -10, -5]} intensity={0.5} />

      {/* 点光源 */}
      <pointLight position={[0, 0, 0]} intensity={0.5} color="#667eea" />

      {/* 渲染节点 */}
      {nodes3D.map((node3D) => (
        <Node3D
          key={node3D.id}
          node={node3D.node}
          position={node3D.position}
          onClick={() => onNodeClick(node3D.node)}
          isSelected={selectedNodeId === node3D.id}
        />
      ))}

      {/* 渲染边 */}
      {relations.map((rel, index) => {
        const sourceNode = nodes3D.find((n) => n.id === rel.source_id);
        const targetNode = nodes3D.find((n) => n.id === rel.target_id);

        if (sourceNode && targetNode) {
          return (
            <Edge3D
              key={index}
              start={sourceNode.position}
              end={targetNode.position}
              color="#667eea"
            />
          );
        }
        return null;
      })}

      {/* 轨道控制器 */}
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        autoRotate={autoRotate}
        autoRotateSpeed={0.5}
        minDistance={5}
        maxDistance={50}
      />
    </>
  );
};

const GraphVisualization3D: React.FC<GraphVisualization3DProps> = ({
  graphId,
  nodes,
  relations = [],
  onNodeClick,
}) => {
  const [loading, setLoading] = useState(true);
  const [layout, setLayout] = useState<LayoutType>('force');
  const [selectedNodeId, setSelectedNodeId] = useState<UUID | null>(null);
  const [autoRotate, setAutoRotate] = useState(false);

  // 根据布局类型获取节点位置
  const forceNodes = useForceLayout(nodes, relations);
  const sphereNodes = useSphereLayout(nodes);
  const helixNodes = useHelixLayout(nodes);
  const gridNodes = useGridLayout(nodes);

  const nodes3D = useMemo(() => {
    switch (layout) {
      case 'force':
        return forceNodes;
      case 'sphere':
        return sphereNodes;
      case 'helix':
        return helixNodes;
      case 'grid':
        return gridNodes;
      default:
        return forceNodes;
    }
  }, [layout, forceNodes, sphereNodes, helixNodes, gridNodes]);

  useEffect(() => {
    if (nodes.length > 0) {
      setLoading(false);
    }
  }, [nodes]);

  const handleNodeClick = (node: MemoryNode) => {
    setSelectedNodeId(node.id);
    if (onNodeClick) {
      onNodeClick(node);
    }
    message.info(`点击了节点: ${node.title}`);
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
              { label: '力导向布局', value: 'force' },
              { label: '球形布局', value: 'sphere' },
              { label: '螺旋布局', value: 'helix' },
              { label: '网格布局', value: 'grid' },
            ]}
          />
          <Button
            icon={<EyeOutlined />}
            onClick={() => setAutoRotate(!autoRotate)}
            size="small"
            type={autoRotate ? 'primary' : 'default'}
            block
          >
            {autoRotate ? '停止旋转' : '自动旋转'}
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => setSelectedNodeId(null)}
            size="small"
            block
          >
            取消选择
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
        <div style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 8 }}>节点类型</div>
        <Space direction="vertical" size={4}>
          {[
            { label: '概念 (球体)', type: 'CONCEPT' },
            { label: '题目 (立方体)', type: 'QUESTION' },
            { label: '笔记 (圆锥)', type: 'NOTE' },
            { label: '资源 (八面体)', type: 'RESOURCE' },
          ].map((item) => (
            <div key={item.type} style={{ fontSize: 12 }}>
              {item.label}
            </div>
          ))}
        </Space>

        <div style={{ fontSize: 12, fontWeight: 'bold', marginTop: 12, marginBottom: 8 }}>
          掌握程度
        </div>
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

      {/* 操作提示 */}
      <div
        style={{
          position: 'absolute',
          top: 16,
          left: 16,
          zIndex: 100,
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '12px',
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          fontSize: 12,
        }}
      >
        <div style={{ fontWeight: 'bold', marginBottom: 4 }}>操作提示</div>
        <div>🖱️ 左键拖拽：旋转视角</div>
        <div>🖱️ 右键拖拽：平移视角</div>
        <div>🖱️ 滚轮：缩放视角</div>
        <div>🖱️ 点击节点：查看详情</div>
      </div>

      {/* 3D 画布 */}
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
        style={{
          width: '100%',
          height: '600px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: 8,
          overflow: 'hidden',
        }}
      >
        <Canvas>
          <Scene
            nodes3D={nodes3D}
            relations={relations}
            onNodeClick={handleNodeClick}
            selectedNodeId={selectedNodeId}
            autoRotate={autoRotate}
          />
        </Canvas>
      </div>
    </div>
  );
};

export default GraphVisualization3D;

