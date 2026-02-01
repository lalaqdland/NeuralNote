import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { cacheService } from './cache';

// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加 Token 和缓存检查
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 对于 GET 请求，检查缓存
    if (config.method === 'get' && config.url) {
      const useCache = (config as any).useCache !== false; // 默认使用缓存
      if (useCache) {
        const cachedData = cacheService.get(config.url, config.params);
        if (cachedData) {
          // 返回缓存数据（通过特殊标记）
          (config as any).cachedData = cachedData;
        }
      }
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误和缓存
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 对于 GET 请求，保存到缓存
    if (response.config.method === 'get' && response.config.url) {
      const useCache = (response.config as any).useCache !== false;
      const cacheTime = (response.config as any).cacheTime; // 自定义缓存时间
      if (useCache) {
        cacheService.set(
          response.config.url,
          response.data,
          response.config.params,
          cacheTime
        );
      }
    }
    return response;
  },
  (error: AxiosError) => {
    // 如果有缓存数据，在网络错误时返回缓存
    if (error.config && (error.config as any).cachedData) {
      console.warn('网络请求失败，使用缓存数据');
      return Promise.resolve({
        data: (error.config as any).cachedData,
        status: 200,
        statusText: 'OK (from cache)',
        headers: {},
        config: error.config,
      } as AxiosResponse);
    }

    if (error.response) {
      // 处理不同的错误状态码
      switch (error.response.status) {
        case 401:
          // Token 过期或无效，清除本地存储并跳转到登录页
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_info');
          cacheService.clear(); // 清空缓存
          window.location.href = '/login';
          break;
        case 403:
          console.error('没有权限访问该资源');
          break;
        case 404:
          console.error('请求的资源不存在');
          break;
        case 500:
          console.error('服务器内部错误');
          break;
        default:
          console.error('请求失败:', error.response.data);
      }
    } else if (error.request) {
      console.error('网络错误，请检查网络连接');
    } else {
      console.error('请求配置错误:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// 导出带缓存配置的请求方法
export const apiClientWithCache = {
  get: <T = any>(url: string, params?: any, cacheTime?: number) => {
    return apiClient.get<T>(url, {
      params,
      useCache: true,
      cacheTime,
    } as any);
  },
  getWithoutCache: <T = any>(url: string, params?: any) => {
    return apiClient.get<T>(url, {
      params,
      useCache: false,
    } as any);
  },
};

