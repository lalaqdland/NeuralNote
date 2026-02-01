/**
 * 成就页面
 */

import React from 'react';
import { Typography } from 'antd';
import AchievementSystem from '../components/AchievementSystem';

const { Title } = Typography;

const Achievements: React.FC = () => {
  return (
    <div>
      <div style={{ padding: '24px 24px 0' }}>
        <Title level={2}>🏆 学习成就</Title>
        <p style={{ color: '#8c8c8c', marginBottom: 0 }}>
          查看你的学习等级、成就徽章和统计数据
        </p>
      </div>
      <AchievementSystem />
    </div>
  );
};

export default Achievements;

