import apiClient from './api';

// 类型定义
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserInfo {
  id: string;
  email: string;
  username: string;
  avatar_url?: string;
  phone?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login_at?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

// 认证服务
export const authService = {
  // 用户登录
  async login(data: LoginRequest): Promise<LoginResponse> {
    // 发送登录请求
    const tokenResponse = await apiClient.post<TokenResponse>('/api/v1/auth/login', data);
    
    // 保存 Token
    if (tokenResponse.data.access_token) {
      localStorage.setItem('access_token', tokenResponse.data.access_token);
      localStorage.setItem('refresh_token', tokenResponse.data.refresh_token);
      
      // 获取用户信息
      const userResponse = await apiClient.get<UserInfo>('/api/v1/auth/me');
      localStorage.setItem('user_info', JSON.stringify(userResponse.data));
      
      return {
        access_token: tokenResponse.data.access_token,
        token_type: tokenResponse.data.token_type,
        user: userResponse.data,
      };
    }
    
    throw new Error('登录失败');
  },

  // 用户注册
  async register(data: RegisterRequest): Promise<UserInfo> {
    const response = await apiClient.post<UserInfo>('/api/v1/auth/register', data);
    return response.data;
  },

  // 退出登录
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
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

