import React, { lazy, Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { Spin } from 'antd';
import App from '../App';
import Login from '../pages/Login';
import ProtectedRoute from '../components/ProtectedRoute';

// 懒加载页面组件
const Home = lazy(() => import('../pages/Home'));
const KnowledgeGraph = lazy(() => import('../pages/KnowledgeGraph'));
const Review = lazy(() => import('../pages/Review'));
const Profile = lazy(() => import('../pages/Profile'));

// 加载中组件
const LoadingFallback = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
    <Spin size="large" />
  </div>
);

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <App />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<LoadingFallback />}>
            <Home />
          </Suspense>
        ),
      },
      {
        path: 'graph',
        element: (
          <Suspense fallback={<LoadingFallback />}>
            <KnowledgeGraph />
          </Suspense>
        ),
      },
      {
        path: 'graph/:id',
        element: (
          <Suspense fallback={<LoadingFallback />}>
            <KnowledgeGraph />
          </Suspense>
        ),
      },
      {
        path: 'review',
        element: (
          <Suspense fallback={<LoadingFallback />}>
            <Review />
          </Suspense>
        ),
      },
      {
        path: 'profile',
        element: (
          <Suspense fallback={<LoadingFallback />}>
            <Profile />
          </Suspense>
        ),
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);

export default router;
