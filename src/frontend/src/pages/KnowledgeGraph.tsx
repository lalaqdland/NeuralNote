import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Paragraph } = Typography;

const KnowledgeGraph: React.FC = () => {
  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Card>
        <Title level={2}>知识图谱</Title>
        <Paragraph>
          知识图谱可视化模块，展示知识点分布与关联。
        </Paragraph>
        <Paragraph>
          支持 2D/3D 视图切换，拖拽、缩放等交互功能。
        </Paragraph>
      </Card>
    </div>
  );
};

export default KnowledgeGraph;
