/**
 * 成就系统服务
 */

import api from './api';

export interface UserStats {
  total_nodes: number;
  mastered_nodes: number;
  total_reviews: number;
  total_graphs: number;
  current_streak: number;
  night_reviews: number;
  morning_reviews: number;
  perfect_week: boolean;
}

export interface LevelInfo {
  level: number;
  total_exp: number;
  current_level_exp: number;
  next_level_exp: number;
  exp_in_level: number;
  exp_to_next: number;
  progress: number;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  unlocked: boolean;
}

export interface AchievementsData {
  unlocked: Achievement[];
  locked: Achievement[];
  total: number;
  unlocked_count: number;
  progress: number;
}

export interface UserProfile {
  stats: UserStats;
  level: LevelInfo;
  achievements: AchievementsData;
}

/**
 * 获取用户统计数据
 */
export const getUserStats = async (): Promise<UserStats> => {
  const response = await api.get('/api/v1/achievements/stats');
  return response.data.data;
};

/**
 * 获取用户等级信息
 */
export const getUserLevel = async (): Promise<LevelInfo> => {
  const response = await api.get('/api/v1/achievements/level');
  return response.data.data;
};

/**
 * 获取用户成就列表
 */
export const getUserAchievements = async (): Promise<AchievementsData> => {
  const response = await api.get('/api/v1/achievements/achievements');
  return response.data.data;
};

/**
 * 获取用户完整档案
 */
export const getUserProfile = async (): Promise<UserProfile> => {
  const response = await api.get('/api/v1/achievements/profile');
  return response.data.data;
};

/**
 * 获取等级称号
 */
export const getLevelTitle = (level: number): string => {
  if (level >= 20) return '传奇大师';
  if (level >= 18) return '至尊学者';
  if (level >= 16) return '博学鸿儒';
  if (level >= 14) return '知识巨匠';
  if (level >= 12) return '学识渊博';
  if (level >= 10) return '知识大师';
  if (level >= 8) return '学有所成';
  if (level >= 6) return '勤奋学者';
  if (level >= 4) return '知识探索者';
  if (level >= 2) return '初窥门径';
  return '初学者';
};

/**
 * 获取等级颜色
 */
export const getLevelColor = (level: number): string => {
  if (level >= 18) return '#ff4d4f'; // 红色 - 传奇
  if (level >= 15) return '#fa8c16'; // 橙色 - 史诗
  if (level >= 12) return '#a0d911'; // 黄绿 - 稀有
  if (level >= 8) return '#52c41a';  // 绿色 - 优秀
  if (level >= 4) return '#1890ff';  // 蓝色 - 良好
  return '#8c8c8c';                   // 灰色 - 新手
};

/**
 * 获取成就分类名称
 */
export const getAchievementCategoryName = (category: string): string => {
  const categoryMap: Record<string, string> = {
    milestone: '学习里程碑',
    review: '复习成就',
    mastery: '掌握成就',
    streak: '连续学习',
    graph: '知识图谱',
    special: '特殊成就',
  };
  return categoryMap[category] || category;
};

/**
 * 获取成就分类颜色
 */
export const getAchievementCategoryColor = (category: string): string => {
  const colorMap: Record<string, string> = {
    milestone: '#1890ff',
    review: '#52c41a',
    mastery: '#faad14',
    streak: '#ff4d4f',
    graph: '#722ed1',
    special: '#eb2f96',
  };
  return colorMap[category] || '#8c8c8c';
};

