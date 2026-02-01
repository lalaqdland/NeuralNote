import { useState, useEffect } from 'react';

/**
 * 屏幕尺寸断点
 */
export const breakpoints = {
  xs: 480,   // 手机
  sm: 576,   // 手机横屏
  md: 768,   // 平板
  lg: 992,   // 桌面
  xl: 1200,  // 大屏桌面
  xxl: 1600, // 超大屏
};

/**
 * 设备类型
 */
export type DeviceType = 'mobile' | 'tablet' | 'desktop';

/**
 * 屏幕尺寸类型
 */
export type ScreenSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl';

/**
 * 响应式信息
 */
export interface ResponsiveInfo {
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  deviceType: DeviceType;
  screenSize: ScreenSize;
  orientation: 'portrait' | 'landscape';
}

/**
 * 获取当前屏幕尺寸类型
 */
function getScreenSize(width: number): ScreenSize {
  if (width < breakpoints.xs) return 'xs';
  if (width < breakpoints.sm) return 'sm';
  if (width < breakpoints.md) return 'md';
  if (width < breakpoints.lg) return 'lg';
  if (width < breakpoints.xl) return 'xl';
  return 'xxl';
}

/**
 * 获取设备类型
 */
function getDeviceType(width: number): DeviceType {
  if (width < breakpoints.md) return 'mobile';
  if (width < breakpoints.lg) return 'tablet';
  return 'desktop';
}

/**
 * 获取屏幕方向
 */
function getOrientation(width: number, height: number): 'portrait' | 'landscape' {
  return width > height ? 'landscape' : 'portrait';
}

/**
 * 获取响应式信息
 */
function getResponsiveInfo(): ResponsiveInfo {
  const width = window.innerWidth;
  const height = window.innerHeight;
  const screenSize = getScreenSize(width);
  const deviceType = getDeviceType(width);
  const orientation = getOrientation(width, height);

  return {
    width,
    height,
    isMobile: deviceType === 'mobile',
    isTablet: deviceType === 'tablet',
    isDesktop: deviceType === 'desktop',
    deviceType,
    screenSize,
    orientation,
  };
}

/**
 * React Hook: 响应式布局
 * 监听窗口大小变化，返回响应式信息
 */
export function useResponsive(): ResponsiveInfo {
  const [responsiveInfo, setResponsiveInfo] = useState<ResponsiveInfo>(getResponsiveInfo);

  useEffect(() => {
    const handleResize = () => {
      setResponsiveInfo(getResponsiveInfo());
    };

    // 使用防抖优化性能
    let timeoutId: NodeJS.Timeout;
    const debouncedResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(handleResize, 150);
    };

    window.addEventListener('resize', debouncedResize);
    window.addEventListener('orientationchange', handleResize);

    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('resize', debouncedResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);

  return responsiveInfo;
}

/**
 * React Hook: 媒体查询
 * 监听指定的媒体查询条件
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia(query).matches;
    }
    return false;
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    
    const handleChange = (e: MediaQueryListEvent) => {
      setMatches(e.matches);
    };

    // 现代浏览器使用 addEventListener
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      // 旧版浏览器使用 addListener
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, [query]);

  return matches;
}

/**
 * React Hook: 检测是否为移动设备
 */
export function useIsMobile(): boolean {
  return useMediaQuery(`(max-width: ${breakpoints.md - 1}px)`);
}

/**
 * React Hook: 检测是否为平板设备
 */
export function useIsTablet(): boolean {
  return useMediaQuery(
    `(min-width: ${breakpoints.md}px) and (max-width: ${breakpoints.lg - 1}px)`
  );
}

/**
 * React Hook: 检测是否为桌面设备
 */
export function useIsDesktop(): boolean {
  return useMediaQuery(`(min-width: ${breakpoints.lg}px)`);
}

/**
 * React Hook: 检测屏幕方向
 */
export function useOrientation(): 'portrait' | 'landscape' {
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>(() => {
    return getOrientation(window.innerWidth, window.innerHeight);
  });

  useEffect(() => {
    const handleOrientationChange = () => {
      setOrientation(getOrientation(window.innerWidth, window.innerHeight));
    };

    window.addEventListener('resize', handleOrientationChange);
    window.addEventListener('orientationchange', handleOrientationChange);

    return () => {
      window.removeEventListener('resize', handleOrientationChange);
      window.removeEventListener('orientationchange', handleOrientationChange);
    };
  }, []);

  return orientation;
}

/**
 * 工具函数：根据设备类型返回不同的值
 */
export function responsive<T>(config: {
  mobile?: T;
  tablet?: T;
  desktop: T;
}): (deviceType: DeviceType) => T {
  return (deviceType: DeviceType) => {
    if (deviceType === 'mobile' && config.mobile !== undefined) {
      return config.mobile;
    }
    if (deviceType === 'tablet' && config.tablet !== undefined) {
      return config.tablet;
    }
    return config.desktop;
  };
}

/**
 * 工具函数：根据屏幕尺寸返回不同的值
 */
export function responsiveSize<T>(config: {
  xs?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
  xxl: T;
}): (screenSize: ScreenSize) => T {
  return (screenSize: ScreenSize) => {
    // 从当前尺寸向上查找最近的配置值
    const sizes: ScreenSize[] = ['xs', 'sm', 'md', 'lg', 'xl', 'xxl'];
    const currentIndex = sizes.indexOf(screenSize);
    
    for (let i = currentIndex; i >= 0; i--) {
      const size = sizes[i];
      if (config[size] !== undefined) {
        return config[size] as T;
      }
    }
    
    return config.xxl;
  };
}

