import apiClient from './api';

// 类型定义
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export interface UserInfo {
  id: number;
  email: string;
  username: string;
  avatar_url?: string;
  created_at: string;
}

// 认证服务
export const authService = {
  // 用户登录
  async login(data: LoginRequest): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);

    const response = await apiClient.post<LoginResponse>('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    // 保存 Token 和用户信息
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user_info', JSON.stringify(response.data.user));
    }
    
    return response.data;
  },

  // 用户注册
  async register(data: RegisterRequest): Promise<UserInfo> {
    const response = await apiClient.post<UserInfo>('/api/v1/auth/register', data);
    return response.data;
  },

  // 退出登录
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
  },

  // 获取当前用户信息
  getCurrentUser(): UserInfo | null {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
  },

  // 检查是否已登录
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};

