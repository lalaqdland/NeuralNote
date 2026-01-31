# NeuralNote 前端

基于 React 18 + TypeScript + Vite + Ant Design 的现代化前端应用。

## 技术栈

- **框架**: React 18.3
- **构建工具**: Vite 7.2
- **语言**: TypeScript 5.9
- **UI 库**: Ant Design 5.13
- **状态管理**: Redux Toolkit 2.0
- **路由**: React Router v6
- **HTTP 客户端**: Axios 1.6
- **图表**: Recharts 2.10
- **图谱可视化**: D3.js 7.8 / Cytoscape.js 3.28
- **日期处理**: Day.js 1.11

## 项目结构

```
src/
├── components/          # 公共组件
│   └── ProtectedRoute.tsx  # 路由守卫
├── pages/              # 页面组件
│   ├── Login.tsx       # 登录/注册页面
│   ├── Home.tsx        # 首页
│   ├── KnowledgeGraph.tsx  # 知识图谱管理
│   ├── Review.tsx      # 复习中心
│   └── Profile.tsx     # 个人中心
├── services/           # API 服务
│   ├── api.ts          # Axios 配置和拦截器
│   ├── auth.ts         # 认证服务
│   ├── knowledgeGraph.ts  # 知识图谱服务
│   └── memoryNode.ts   # 记忆节点服务
├── store/              # Redux 状态管理
│   ├── index.ts        # Store 配置
│   ├── authSlice.ts    # 认证状态
│   ├── graphSlice.ts   # 图谱状态
│   └── hooks.ts        # 类型化的 Hooks
├── router/             # 路由配置
│   └── index.tsx       # 路由定义
├── styles/             # 样式文件
├── utils/              # 工具函数
├── App.tsx             # 主应用组件
├── main.tsx            # 应用入口
└── style.css           # 全局样式
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 功能特性

### ✅ 已完成

1. **用户认证**
   - 登录/注册页面
   - JWT Token 管理
   - 路由守卫
   - 自动登录状态恢复

2. **主布局**
   - 响应式导航栏
   - 用户信息下拉菜单
   - 统一的页面布局

3. **首页**
   - 学习统计展示
   - 最近图谱列表
   - 快速操作入口

4. **知识图谱管理**
   - 图谱列表展示
   - 创建/编辑/删除图谱
   - 图谱卡片视图

5. **复习中心**
   - 复习统计
   - 4种复习模式选择
   - 学习进度展示

6. **个人中心**
   - 用户信息展示
   - 学习统计
   - 个人信息编辑

### 🚧 待开发

1. **文件上传功能**
   - 拖拽上传组件
   - 图片预览
   - OCR 识别界面

2. **AI 分析展示**
   - 题目解答展示
   - 知识点提取结果
   - 手动校正功能

3. **知识图谱可视化**
   - 2D 图谱渲染（D3.js/Cytoscape.js）
   - 节点交互（点击、拖拽、缩放）
   - 关联关系展示
   - 颜色标注系统

4. **复习系统**
   - 复习卡片界面
   - 复习反馈
   - 复习历史记录

5. **统计图表**
   - 学习进度图表
   - 复习统计图表
   - 知识掌握度分析

## API 配置

在项目根目录创建 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 设计规范

### 颜色主题

- **主色**: `#667eea` (紫色渐变)
- **辅助色**: `#764ba2` (深紫色)
- **成功**: `#52c41a`
- **警告**: `#faad14`
- **错误**: `#f5222d`
- **信息**: `#1890ff`

### 字体

- **主字体**: Inter
- **备用字体**: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif

### 圆角

- **卡片**: 12px
- **按钮**: 8px
- **输入框**: 10px

## 代码规范

### 组件规范

```typescript
import React from 'react';
import { Button } from 'antd';

interface MyComponentProps {
  title: string;
  onAction?: () => void;
}

const MyComponent: React.FC<MyComponentProps> = ({ title, onAction }) => {
  return (
    <div>
      <h1>{title}</h1>
      <Button onClick={onAction}>Action</Button>
    </div>
  );
};

export default MyComponent;
```

### API 调用规范

```typescript
import { useState, useEffect } from 'react';
import { knowledgeGraphService } from '../services/knowledgeGraph';
import { message } from 'antd';

const MyComponent = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await knowledgeGraphService.getGraphs();
      setData(response.items);
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  return <div>{/* ... */}</div>;
};
```

### Redux 使用规范

```typescript
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { setUser } from '../store/authSlice';

const MyComponent = () => {
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.auth.user);

  const handleLogin = (userData) => {
    dispatch(setUser(userData));
  };

  return <div>{/* ... */}</div>;
};
```

## 性能优化

1. **路由懒加载**: 使用 `React.lazy()` 和 `Suspense`
2. **组件懒加载**: 按需加载大型组件
3. **图片优化**: 使用 WebP 格式，添加懒加载
4. **代码分割**: Vite 自动进行代码分割
5. **缓存策略**: API 响应缓存，减少重复请求

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 开发注意事项

1. **API 调用**: 所有 API 调用都应该有错误处理
2. **加载状态**: 异步操作要显示加载状态
3. **用户反馈**: 操作成功/失败要有明确的提示
4. **响应式设计**: 所有页面都要支持移动端
5. **类型安全**: 充分利用 TypeScript 的类型检查

## 常见问题

### Q: 如何添加新的 API 服务？

A: 在 `src/services/` 目录下创建新的服务文件，参考现有服务的结构。

### Q: 如何添加新的页面？

A: 
1. 在 `src/pages/` 创建页面组件
2. 在 `src/router/index.tsx` 添加路由配置
3. 如果需要认证，使用 `ProtectedRoute` 包裹

### Q: 如何管理全局状态？

A: 
1. 在 `src/store/` 创建新的 slice
2. 在 `src/store/index.ts` 注册 reducer
3. 使用 `useAppDispatch` 和 `useAppSelector` hooks

## 相关文档

- [React 文档](https://react.dev/)
- [Vite 文档](https://vitejs.dev/)
- [Ant Design 文档](https://ant.design/)
- [Redux Toolkit 文档](https://redux-toolkit.js.org/)
- [React Router 文档](https://reactrouter.com/)

## License

MIT

