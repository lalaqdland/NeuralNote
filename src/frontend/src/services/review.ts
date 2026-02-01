import apiClient from './api';

// 复习相关类型定义
export type ReviewMode = 'spaced' | 'focused' | 'random' | 'graph_traversal';

export interface ReviewNode {
  node_id: number;
  title: string;
  content_data: any;
  mastery_level: number;
  last_reviewed_at?: string;
  next_review_at?: string;
  review_count: number;
}

export interface ReviewQueueResponse {
  mode: ReviewMode;
  nodes: ReviewNode[];
  total_count: number;
  estimated_time: number;
}

export interface ReviewFeedbackRequest {
  node_id: number;
  quality: number; // 0-5
  time_spent?: number;
}

export interface ReviewFeedbackResponse {
  node_id: number;
  new_mastery_level: number;
  next_review_at: string;
  interval_days: number;
}

export interface ReviewStats {
  total_nodes: number;
  reviewed_today: number;
  due_today: number;
  mastered_nodes: number;
  average_mastery: number;
  total_review_time: number;
  streak_days: number;
}

// 复习服务
class ReviewService {
  /**
   * 获取复习队列
   */
  async getReviewQueue(
    graphId: number,
    mode: ReviewMode = 'spaced',
    limit: number = 20
  ): Promise<ReviewQueueResponse> {
    const response = await apiClient.get<ReviewQueueResponse>('/api/v1/review/queue', {
      params: { graph_id: graphId, mode, limit },
    });
    return response.data;
  }

  /**
   * 提交复习反馈
   */
  async submitFeedback(feedback: ReviewFeedbackRequest): Promise<ReviewFeedbackResponse> {
    const response = await apiClient.post<ReviewFeedbackResponse>('/api/v1/review/feedback', feedback);
    return response.data;
  }

  /**
   * 获取复习统计
   */
  async getReviewStats(graphId: number): Promise<ReviewStats> {
    const response = await apiClient.get<ReviewStats>('/api/v1/review/statistics', {
      params: { graph_id: graphId },
    });
    return response.data;
  }

  /**
   * 获取今日待复习节点数
   */
  async getDueTodayCount(graphId: number): Promise<number> {
    const stats = await this.getReviewStats(graphId);
    return stats.due_today;
  }
}

export const reviewService = new ReviewService();

