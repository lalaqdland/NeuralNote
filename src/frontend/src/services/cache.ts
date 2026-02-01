/**
 * API 缓存服务
 * 使用内存缓存和 localStorage 实现两级缓存
 */

interface CacheItem<T> {
  data: T;
  timestamp: number;
  expiresIn: number; // 过期时间（毫秒）
}

class CacheService {
  private memoryCache: Map<string, CacheItem<any>> = new Map();
  private readonly MAX_MEMORY_CACHE_SIZE = 50; // 内存缓存最大条目数
  private readonly DEFAULT_EXPIRE_TIME = 5 * 60 * 1000; // 默认5分钟过期

  /**
   * 生成缓存键
   */
  private generateKey(url: string, params?: any): string {
    const paramStr = params ? JSON.stringify(params) : '';
    return `${url}:${paramStr}`;
  }

  /**
   * 检查缓存是否过期
   */
  private isExpired(item: CacheItem<any>): boolean {
    return Date.now() - item.timestamp > item.expiresIn;
  }

  /**
   * 从内存缓存获取
   */
  private getFromMemory<T>(key: string): T | null {
    const item = this.memoryCache.get(key);
    if (!item) return null;

    if (this.isExpired(item)) {
      this.memoryCache.delete(key);
      return null;
    }

    return item.data as T;
  }

  /**
   * 从 localStorage 获取
   */
  private getFromStorage<T>(key: string): T | null {
    try {
      const itemStr = localStorage.getItem(`cache:${key}`);
      if (!itemStr) return null;

      const item: CacheItem<T> = JSON.parse(itemStr);
      if (this.isExpired(item)) {
        localStorage.removeItem(`cache:${key}`);
        return null;
      }

      // 同步到内存缓存
      this.memoryCache.set(key, item);
      return item.data;
    } catch (error) {
      console.error('从 localStorage 读取缓存失败:', error);
      return null;
    }
  }

  /**
   * 保存到内存缓存
   */
  private saveToMemory<T>(key: string, data: T, expiresIn: number): void {
    // 如果超过最大缓存数，删除最旧的
    if (this.memoryCache.size >= this.MAX_MEMORY_CACHE_SIZE) {
      const firstKey = this.memoryCache.keys().next().value;
      this.memoryCache.delete(firstKey);
    }

    this.memoryCache.set(key, {
      data,
      timestamp: Date.now(),
      expiresIn,
    });
  }

  /**
   * 保存到 localStorage
   */
  private saveToStorage<T>(key: string, data: T, expiresIn: number): void {
    try {
      const item: CacheItem<T> = {
        data,
        timestamp: Date.now(),
        expiresIn,
      };
      localStorage.setItem(`cache:${key}`, JSON.stringify(item));
    } catch (error) {
      console.error('保存到 localStorage 失败:', error);
      // localStorage 可能已满，尝试清理旧缓存
      this.clearExpiredStorage();
    }
  }

  /**
   * 获取缓存
   */
  get<T>(url: string, params?: any): T | null {
    const key = this.generateKey(url, params);

    // 先从内存缓存获取
    const memoryData = this.getFromMemory<T>(key);
    if (memoryData !== null) {
      return memoryData;
    }

    // 再从 localStorage 获取
    return this.getFromStorage<T>(key);
  }

  /**
   * 设置缓存
   */
  set<T>(url: string, data: T, params?: any, expiresIn: number = this.DEFAULT_EXPIRE_TIME): void {
    const key = this.generateKey(url, params);

    // 保存到内存缓存
    this.saveToMemory(key, data, expiresIn);

    // 保存到 localStorage（持久化）
    this.saveToStorage(key, data, expiresIn);
  }

  /**
   * 删除指定缓存
   */
  remove(url: string, params?: any): void {
    const key = this.generateKey(url, params);
    this.memoryCache.delete(key);
    localStorage.removeItem(`cache:${key}`);
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.memoryCache.clear();
    
    // 清空 localStorage 中的所有缓存
    const keys = Object.keys(localStorage);
    keys.forEach((key) => {
      if (key.startsWith('cache:')) {
        localStorage.removeItem(key);
      }
    });
  }

  /**
   * 清理过期的 localStorage 缓存
   */
  clearExpiredStorage(): void {
    const keys = Object.keys(localStorage);
    keys.forEach((key) => {
      if (key.startsWith('cache:')) {
        try {
          const itemStr = localStorage.getItem(key);
          if (itemStr) {
            const item: CacheItem<any> = JSON.parse(itemStr);
            if (this.isExpired(item)) {
              localStorage.removeItem(key);
            }
          }
        } catch (error) {
          // 解析失败，删除该缓存
          localStorage.removeItem(key);
        }
      }
    });
  }

  /**
   * 获取缓存统计信息
   */
  getStats() {
    const memorySize = this.memoryCache.size;
    const storageKeys = Object.keys(localStorage).filter((key) => key.startsWith('cache:'));
    const storageSize = storageKeys.length;

    return {
      memorySize,
      storageSize,
      totalSize: memorySize + storageSize,
    };
  }
}

// 导出单例
export const cacheService = new CacheService();

// 定期清理过期缓存（每小时）
setInterval(() => {
  cacheService.clearExpiredStorage();
}, 60 * 60 * 1000);

