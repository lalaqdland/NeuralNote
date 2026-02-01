import apiClient from './api';

// 类型定义
export interface UpdateUserRequest {
  username?: string;
  avatar_url?: string;
  phone?: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

export interface UserStatistics {
  total_graphs: number;
  total_nodes: number;
  total_reviews: number;
  study_days: number;
  mastery_distribution: {
    level_0: number;
    level_1: number;
    level_2: number;
    level_3: number;
    level_4: number;
    level_5: number;
  };
  recent_activity: Array<{
    date: string;
    reviews: number;
    nodes_created: number;
  }>;
}

// 用户服务
export const userService = {
  // 获取用户统计数据
  async getUserStatistics(): Promise<UserStatistics> {
    const response = await apiClient.get<UserStatistics>('/api/v1/users/statistics');
    return response.data;
  },

  // 更新用户信息
  async updateUser(data: UpdateUserRequest): Promise<any> {
    const response = await apiClient.put('/api/v1/users/me', data);
    // 更新本地存储的用户信息
    const userInfo = localStorage.getItem('user_info');
    if (userInfo) {
      const user = JSON.parse(userInfo);
      const updatedUser = { ...user, ...data };
      localStorage.setItem('user_info', JSON.stringify(updatedUser));
    }
    return response.data;
  },

  // 修改密码
  async changePassword(data: ChangePasswordRequest): Promise<void> {
    await apiClient.post('/api/v1/users/change-password', data);
  },
};

