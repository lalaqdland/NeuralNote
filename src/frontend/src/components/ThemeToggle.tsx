import React from 'react';
import { Button, Tooltip } from 'antd';
import { BulbOutlined, BulbFilled } from '@ant-design/icons';
import { useTheme } from '../contexts/ThemeContext';

interface ThemeToggleProps {
  style?: React.CSSProperties;
  size?: 'small' | 'middle' | 'large';
  showText?: boolean;
}

const ThemeToggle: React.FC<ThemeToggleProps> = ({ 
  style, 
  size = 'middle',
  showText = false 
}) => {
  const { themeMode, toggleTheme } = useTheme();
  const isDark = themeMode === 'dark';

  return (
    <Tooltip title={isDark ? '切换到亮色模式' : '切换到暗黑模式'}>
      <Button
        type="text"
        icon={isDark ? <BulbFilled /> : <BulbOutlined />}
        onClick={toggleTheme}
        size={size}
        style={{
          color: 'inherit',
          transition: 'all 0.3s ease',
          ...style,
        }}
      >
        {showText && (isDark ? '暗黑模式' : '亮色模式')}
      </Button>
    </Tooltip>
  );
};

export default ThemeToggle;

