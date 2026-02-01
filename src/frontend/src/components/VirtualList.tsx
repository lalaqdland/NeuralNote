import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Spin } from 'antd';

interface VirtualListProps<T> {
  data: T[];
  itemHeight: number;
  containerHeight: number;
  renderItem: (item: T, index: number) => React.ReactNode;
  overscan?: number; // 预渲染的额外项数
  loading?: boolean;
  emptyText?: string;
}

/**
 * 虚拟列表组件
 * 只渲染可见区域的列表项，提升大数据量列表的性能
 */
function VirtualList<T>({
  data,
  itemHeight,
  containerHeight,
  renderItem,
  overscan = 3,
  loading = false,
  emptyText = '暂无数据',
}: VirtualListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // 计算可见范围
  const visibleCount = Math.ceil(containerHeight / itemHeight);
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(data.length, startIndex + visibleCount + overscan * 2);
  const visibleData = data.slice(startIndex, endIndex);

  // 总高度
  const totalHeight = data.length * itemHeight;
  // 偏移量
  const offsetY = startIndex * itemHeight;

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const target = e.target as HTMLDivElement;
    setScrollTop(target.scrollTop);
  }, []);

  // 滚动到指定索引
  const scrollToIndex = useCallback((index: number) => {
    if (containerRef.current) {
      const scrollTop = index * itemHeight;
      containerRef.current.scrollTop = scrollTop;
      setScrollTop(scrollTop);
    }
  }, [itemHeight]);

  // 暴露滚动方法给父组件
  useEffect(() => {
    if (containerRef.current) {
      (containerRef.current as any).scrollToIndex = scrollToIndex;
    }
  }, [scrollToIndex]);

  if (loading) {
    return (
      <div
        style={{
          height: containerHeight,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Spin size="large" />
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div
        style={{
          height: containerHeight,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          color: '#999',
        }}
      >
        {emptyText}
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      style={{
        height: containerHeight,
        overflow: 'auto',
        position: 'relative',
      }}
    >
      {/* 占位容器，撑开滚动高度 */}
      <div style={{ height: totalHeight, position: 'relative' }}>
        {/* 可见项容器 */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            transform: `translateY(${offsetY}px)`,
          }}
        >
          {visibleData.map((item, index) => (
            <div
              key={startIndex + index}
              style={{
                height: itemHeight,
                overflow: 'hidden',
              }}
            >
              {renderItem(item, startIndex + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default VirtualList;

