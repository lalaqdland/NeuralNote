import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Paragraph } = Typography;

const Review: React.FC = () => {
  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Card>
        <Title level={2}>智能复习</Title>
        <Paragraph>
          基于遗忘曲线算法，智能提醒最佳复习时机。
        </Paragraph>
        <Paragraph>
          显示需要复习的知识点，支持掌握程度反馈。
        </Paragraph>
      </Card>
    </div>
  );
};

export default Review;
