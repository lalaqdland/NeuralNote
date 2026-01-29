import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Paragraph } = Typography;

const Profile: React.FC = () => {
  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Card>
        <Title level={2}>个人中心</Title>
        <Paragraph>
          用户信息管理、订阅设置、复习统计等功能。
        </Paragraph>
      </Card>
    </div>
  );
};

export default Profile;
