import React from 'react';
import { Layout, Menu, Typography } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { HomeOutlined, ApiOutlined, BarChartOutlined, UserOutlined } from '@ant-design/icons';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/graph',
      icon: <ApiOutlined />,
      label: '知识图谱',
    },
    {
      key: '/review',
      icon: <BarChartOutlined />,
      label: '复习',
    },
    {
      key: '/profile',
      icon: <UserOutlined />,
      label: '个人中心',
    },
  ];

  return (
    <Layout className="layout" style={{ minHeight: '100vh' }}>
      <Header>
        <div style={{ float: 'left', marginRight: '24px' }}>
          <Title level={3} style={{ color: 'white', margin: '16px 0' }}>
            NeuralNote
          </Title>
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>
      <Content style={{ padding: '24px' }}>
        <div className="site-layout-content">
          <Outlet />
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        NeuralNote ©2026 Created with Ant Design
      </Footer>
    </Layout>
  );
};

export default App;
