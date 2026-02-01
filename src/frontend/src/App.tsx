import React, { useEffect, useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Typography, Space, Button, Badge } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  ApiOutlined,
  ReadOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  SearchOutlined,
  BellOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import { authService } from './services/auth';
import { useAppDispatch, useAppSelector } from './store/hooks';
import { setUser, clearUser } from './store/authSlice';
import VectorSearchModal from './components/VectorSearchModal';
import NotificationSettingsModal from './components/NotificationSettings';
import { notificationService } from './services/notification';
import type { MenuProps } from 'antd';

const { Header, Content, Footer } = Layout;
const { Text } = Typography;

const App: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.auth.user);
  const [searchModalVisible, setSearchModalVisible] = useState(false);
  const [notificationModalVisible, setNotificationModalVisible] = useState(false);
  const [unreadNotifications, setUnreadNotifications] = useState(0);

  useEffect(() => {
    // 初始化时从 localStorage 加载用户信息
    const currentUser = authService.getCurrentUser();
    if (currentUser) {
      dispatch(setUser(currentUser));
    }

    // 更新未读通知数量
    updateUnreadCount();

    // 每分钟更新一次未读通知数量
    const timer = setInterval(updateUnreadCount, 60000);
    return () => clearInterval(timer);
  }, [dispatch]);

  const updateUnreadCount = () => {
    const records = notificationService.getRecords();
    const unread = records.filter((r) => !r.clicked).length;
    setUnreadNotifications(unread);
  };

  const handleLogout = () => {
    authService.logout();
    dispatch(clearUser());
    navigate('/login');
  };

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
      icon: <ReadOutlined />,
      label: '复习',
    },
    {
      key: '/achievements',
      icon: <TrophyOutlined />,
      label: '成就',
    },
  ];

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'notifications',
      icon: <BellOutlined />,
      label: '通知设置',
      onClick: () => {
        setNotificationModalVisible(true);
        updateUnreadCount();
      },
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
          <div
            style={{
              fontSize: '24px',
              fontWeight: 700,
              color: 'white',
              cursor: 'pointer',
              letterSpacing: '-0.5px',
            }}
            onClick={() => navigate('/')}
          >
            NeuralNote
          </div>
          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
            style={{
              flex: 1,
              minWidth: 0,
              background: 'transparent',
              border: 'none',
            }}
          />
        </div>

        <Space size="middle">
          <Button
            type="text"
            icon={<SearchOutlined />}
            onClick={() => setSearchModalVisible(true)}
            style={{ color: 'white' }}
          >
            搜索
          </Button>
          <Badge count={unreadNotifications} offset={[-5, 5]}>
            <Button
              type="text"
              icon={<BellOutlined />}
              onClick={() => {
                setNotificationModalVisible(true);
                updateUnreadCount();
              }}
              style={{ color: 'white' }}
            />
          </Badge>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar
                style={{ backgroundColor: '#f56a00' }}
                icon={<UserOutlined />}
                src={user?.avatar_url}
              />
              <Text style={{ color: 'white', fontWeight: 500 }}>{user?.username || '用户'}</Text>
            </Space>
          </Dropdown>
        </Space>
      </Header>

      <Content style={{ padding: '24px', background: '#f5f7fa' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <Outlet />
        </div>
      </Content>

      <Footer style={{ textAlign: 'center', background: '#fff', borderTop: '1px solid #f0f0f0' }}>
        <Text type="secondary">NeuralNote ©2026 - 智能学习，知识图谱化管理</Text>
      </Footer>

      {/* 全局搜索模态框 */}
      <VectorSearchModal
        visible={searchModalVisible}
        onClose={() => setSearchModalVisible(false)}
      />

      {/* 通知设置模态框 */}
      <NotificationSettingsModal
        visible={notificationModalVisible}
        onClose={() => {
          setNotificationModalVisible(false);
          updateUnreadCount();
        }}
      />
    </Layout>
  );
};

export default App;
