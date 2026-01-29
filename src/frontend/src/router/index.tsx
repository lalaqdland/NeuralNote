import { createBrowserRouter } from 'react-router-dom';
import App from '../App';

// 懒加载页面组件
const Home = () => import('../pages/Home');
const KnowledgeGraph = () => import('../pages/KnowledgeGraph');
const Review = () => import('../pages/Review');
const Profile = () => import('../pages/Profile');

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: 'graph',
        element: <KnowledgeGraph />,
      },
      {
        path: 'review',
        element: <Review />,
      },
      {
        path: 'profile',
        element: <Profile />,
      },
    ],
  },
]);

export default router;
