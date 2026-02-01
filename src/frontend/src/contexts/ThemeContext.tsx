import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ConfigProvider, theme as antdTheme } from 'antd';
import zhCN from 'antd/locale/zh_CN';

// 主题类型
export type ThemeMode = 'light' | 'dark';

// 主题配置接口
interface ThemeConfig {
  mode: ThemeMode;
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    hover: string;
    gradient: string;
    shadow: string;
  };
}

// 亮色主题配置
const lightTheme: ThemeConfig = {
  mode: 'light',
  colors: {
    primary: '#667eea',
    secondary: '#764ba2',
    background: '#f5f7fa',
    surface: '#ffffff',
    text: '#1a1a1a',
    textSecondary: '#666666',
    border: '#e8e8e8',
    hover: '#f0f0f0',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    shadow: 'rgba(0, 0, 0, 0.1)',
  },
};

// 暗色主题配置
const darkTheme: ThemeConfig = {
  mode: 'dark',
  colors: {
    primary: '#7c3aed',
    secondary: '#a855f7',
    background: '#0f0f0f',
    surface: '#1a1a1a',
    text: '#e5e5e5',
    textSecondary: '#a3a3a3',
    border: '#2a2a2a',
    hover: '#262626',
    gradient: 'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)',
    shadow: 'rgba(0, 0, 0, 0.5)',
  },
};

// Context 接口
interface ThemeContextType {
  theme: ThemeConfig;
  themeMode: ThemeMode;
  toggleTheme: () => void;
  setThemeMode: (mode: ThemeMode) => void;
}

// 创建 Context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Provider Props
interface ThemeProviderProps {
  children: ReactNode;
}

// 本地存储键名
const THEME_STORAGE_KEY = 'neuralnote-theme-mode';

// Theme Provider 组件
export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // 从 localStorage 读取主题设置，默认为亮色
  const [themeMode, setThemeModeState] = useState<ThemeMode>(() => {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    return (savedTheme as ThemeMode) || 'light';
  });

  // 获取当前主题配置
  const theme = themeMode === 'dark' ? darkTheme : lightTheme;

  // 切换主题
  const toggleTheme = () => {
    setThemeModeState((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  // 设置主题
  const setThemeMode = (mode: ThemeMode) => {
    setThemeModeState(mode);
  };

  // 持久化主题设置
  useEffect(() => {
    localStorage.setItem(THEME_STORAGE_KEY, themeMode);
    
    // 更新 document 的 data-theme 属性，方便 CSS 使用
    document.documentElement.setAttribute('data-theme', themeMode);
    
    // 更新 meta theme-color（移动端浏览器地址栏颜色）
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', theme.colors.primary);
    }
  }, [themeMode, theme.colors.primary]);

  // Ant Design 主题配置
  const antdThemeConfig = {
    algorithm: themeMode === 'dark' ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
    token: {
      colorPrimary: theme.colors.primary,
      colorBgBase: theme.colors.surface,
      colorTextBase: theme.colors.text,
      borderRadius: 8,
      fontSize: 14,
    },
    components: {
      Layout: {
        headerBg: themeMode === 'dark' ? '#1a1a1a' : theme.colors.primary,
        bodyBg: theme.colors.background,
        footerBg: theme.colors.surface,
      },
      Menu: {
        darkItemBg: 'transparent',
        darkItemSelectedBg: 'rgba(255, 255, 255, 0.1)',
      },
      Card: {
        colorBgContainer: theme.colors.surface,
      },
      Modal: {
        contentBg: theme.colors.surface,
        headerBg: theme.colors.surface,
      },
      Drawer: {
        colorBgElevated: theme.colors.surface,
      },
    },
  };

  return (
    <ThemeContext.Provider value={{ theme, themeMode, toggleTheme, setThemeMode }}>
      <ConfigProvider theme={antdThemeConfig} locale={zhCN}>
        {children}
      </ConfigProvider>
    </ThemeContext.Provider>
  );
};

// 自定义 Hook
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// 导出主题配置供外部使用
export { lightTheme, darkTheme };
export type { ThemeConfig };

