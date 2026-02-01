/**
 * 性能监控工具
 * 监控页面加载、组件渲染、API 请求等性能指标
 */

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private readonly MAX_METRICS = 100;

  /**
   * 记录性能指标
   */
  record(name: string, value: number): void {
    this.metrics.push({
      name,
      value,
      timestamp: Date.now(),
    });

    // 限制存储数量
    if (this.metrics.length > this.MAX_METRICS) {
      this.metrics.shift();
    }
  }

  /**
   * 测量函数执行时间
   */
  measure<T>(name: string, fn: () => T): T {
    const start = performance.now();
    const result = fn();
    const duration = performance.now() - start;
    this.record(name, duration);
    return result;
  }

  /**
   * 测量异步函数执行时间
   */
  async measureAsync<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const start = performance.now();
    const result = await fn();
    const duration = performance.now() - start;
    this.record(name, duration);
    return result;
  }

  /**
   * 获取页面加载性能指标
   */
  getPageLoadMetrics() {
    if (!window.performance || !window.performance.timing) {
      return null;
    }

    const timing = window.performance.timing;
    const navigationStart = timing.navigationStart;

    return {
      // DNS 查询时间
      dns: timing.domainLookupEnd - timing.domainLookupStart,
      // TCP 连接时间
      tcp: timing.connectEnd - timing.connectStart,
      // 请求时间
      request: timing.responseStart - timing.requestStart,
      // 响应时间
      response: timing.responseEnd - timing.responseStart,
      // DOM 解析时间
      domParse: timing.domInteractive - timing.domLoading,
      // DOM 内容加载完成时间
      domContentLoaded: timing.domContentLoadedEventEnd - navigationStart,
      // 页面完全加载时间
      pageLoad: timing.loadEventEnd - navigationStart,
      // 首次渲染时间
      firstPaint: this.getFirstPaint(),
      // 首次内容渲染时间
      firstContentfulPaint: this.getFirstContentfulPaint(),
    };
  }

  /**
   * 获取首次渲染时间 (FP)
   */
  private getFirstPaint(): number | null {
    if (!window.performance || !window.performance.getEntriesByType) {
      return null;
    }

    const paintEntries = window.performance.getEntriesByType('paint');
    const firstPaint = paintEntries.find((entry) => entry.name === 'first-paint');
    return firstPaint ? firstPaint.startTime : null;
  }

  /**
   * 获取首次内容渲染时间 (FCP)
   */
  private getFirstContentfulPaint(): number | null {
    if (!window.performance || !window.performance.getEntriesByType) {
      return null;
    }

    const paintEntries = window.performance.getEntriesByType('paint');
    const fcp = paintEntries.find((entry) => entry.name === 'first-contentful-paint');
    return fcp ? fcp.startTime : null;
  }

  /**
   * 获取资源加载性能
   */
  getResourceMetrics() {
    if (!window.performance || !window.performance.getEntriesByType) {
      return [];
    }

    const resources = window.performance.getEntriesByType('resource') as PerformanceResourceTiming[];
    return resources.map((resource) => ({
      name: resource.name,
      type: resource.initiatorType,
      duration: resource.duration,
      size: resource.transferSize || 0,
      startTime: resource.startTime,
    }));
  }

  /**
   * 获取所有记录的指标
   */
  getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  /**
   * 获取指定名称的指标统计
   */
  getMetricStats(name: string) {
    const filtered = this.metrics.filter((m) => m.name === name);
    if (filtered.length === 0) {
      return null;
    }

    const values = filtered.map((m) => m.value);
    const sum = values.reduce((a, b) => a + b, 0);
    const avg = sum / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);

    return {
      count: filtered.length,
      avg,
      min,
      max,
      sum,
    };
  }

  /**
   * 清空所有指标
   */
  clear(): void {
    this.metrics = [];
  }

  /**
   * 打印性能报告
   */
  printReport(): void {
    console.group('📊 性能监控报告');

    // 页面加载性能
    const pageMetrics = this.getPageLoadMetrics();
    if (pageMetrics) {
      console.group('📄 页面加载性能');
      console.table(pageMetrics);
      console.groupEnd();
    }

    // 自定义指标统计
    const metricNames = [...new Set(this.metrics.map((m) => m.name))];
    if (metricNames.length > 0) {
      console.group('⏱️ 自定义指标统计');
      const stats = metricNames.map((name) => ({
        name,
        ...this.getMetricStats(name),
      }));
      console.table(stats);
      console.groupEnd();
    }

    // 资源加载性能（前10个最慢的）
    const resources = this.getResourceMetrics()
      .sort((a, b) => b.duration - a.duration)
      .slice(0, 10);
    if (resources.length > 0) {
      console.group('📦 资源加载性能（前10慢）');
      console.table(resources);
      console.groupEnd();
    }

    console.groupEnd();
  }

  /**
   * 监控长任务（超过50ms的任务）
   */
  observeLongTasks(callback?: (entries: PerformanceEntry[]) => void): void {
    if (!('PerformanceObserver' in window)) {
      console.warn('浏览器不支持 PerformanceObserver');
      return;
    }

    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          console.warn(`⚠️ 检测到长任务: ${entry.name}, 耗时: ${entry.duration.toFixed(2)}ms`);
          this.record(`long-task:${entry.name}`, entry.duration);
        });
        if (callback) {
          callback(entries);
        }
      });

      observer.observe({ entryTypes: ['longtask'] });
    } catch (error) {
      console.warn('长任务监控启动失败:', error);
    }
  }
}

// 导出单例
export const performanceMonitor = new PerformanceMonitor();

// 开发环境下自动打印性能报告
if (import.meta.env.DEV) {
  window.addEventListener('load', () => {
    setTimeout(() => {
      performanceMonitor.printReport();
    }, 2000);
  });

  // 监控长任务
  performanceMonitor.observeLongTasks();

  // 暴露到全局，方便调试
  (window as any).performanceMonitor = performanceMonitor;
}

