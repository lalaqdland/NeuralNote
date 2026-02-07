import apiClient from './api';
import { UUID } from './knowledgeGraph';
import { memoryNodeService } from './memoryNode';

// 复习相关类型定义
export type ReviewMode = 'spaced' | 'focused' | 'random' | 'graph_traversal';

export interface ReviewNode {
  node_id: UUID;
  title: string;
  content_data: Record<string, any>;
  mastery_level: number;
  last_reviewed_at?: string;
  next_review_at?: string;
  review_count: number;
}

interface BackendReviewQueueNode {
  node_id: UUID;
  title: string;
  node_type: string;
  mastery_level: string;
  last_review_at?: string;
  next_review_at?: string;
  review_stats?: Record<string, any>;
}

interface BackendReviewQueueResponse {
  total: number;
  nodes: BackendReviewQueueNode[];
}

interface BackendReviewStats {
  total_nodes: number;
  mastery_distribution: Record<string, number>;
  mastery_rate: number;
  due_today: number;
  overdue: number;
  total_reviews: number;
}

export interface ReviewQueueResponse {
  mode: ReviewMode;
  nodes: ReviewNode[];
  total_count: number;
  estimated_time: number;
}

export interface ReviewFeedbackRequest {
  node_id: UUID;
  quality: number; // 0-5
  review_duration?: number;
}

export interface ReviewFeedbackResponse {
  node_id: UUID;
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

const MASTERY_TO_NUM: Record<string, number> = {
  not_started: 0,
  learning: 1,
  familiar: 3,
  proficient: 4,
  mastered: 5,
};

function masteryToNum(level: string): number {
  return MASTERY_TO_NUM[level] ?? 0;
}

function calcAverageMastery(distribution: Record<string, number>): number {
  const weights: Record<string, number> = {
    not_started: 0,
    learning: 1,
    familiar: 3,
    proficient: 4,
    mastered: 5,
  };
  let total = 0;
  let weighted = 0;
  Object.entries(distribution).forEach(([key, value]) => {
    const count = Number(value ?? 0);
    total += count;
    weighted += count * (weights[key] ?? 0);
  });
  if (total === 0) return 0;
  return weighted / total;
}

// 复习服务
class ReviewService {
  /**
   * 获取复习队列
   */
  async getReviewQueue(
    graphId: UUID,
    mode: ReviewMode = 'spaced',
    limit: number = 20
  ): Promise<ReviewQueueResponse> {
    const response = await apiClient.get<BackendReviewQueueResponse>('/api/v1/reviews/queue', {
      params: { graph_id: graphId, mode, limit },
    });

    const nodes = await Promise.all(
      response.data.nodes.map(async (node) => {
        try {
          const detail = await memoryNodeService.getNode(node.node_id);
          return {
            node_id: node.node_id,
            title: node.title,
            content_data: detail.content_data ?? {},
            mastery_level: detail.mastery_level ?? masteryToNum(node.mastery_level),
            last_reviewed_at: node.last_review_at,
            next_review_at: node.next_review_at,
            review_count: Number(node.review_stats?.total_reviews ?? detail.review_count ?? 0),
          } as ReviewNode;
        } catch {
          return {
            node_id: node.node_id,
            title: node.title,
            content_data: {},
            mastery_level: masteryToNum(node.mastery_level),
            last_reviewed_at: node.last_review_at,
            next_review_at: node.next_review_at,
            review_count: Number(node.review_stats?.total_reviews ?? 0),
          } as ReviewNode;
        }
      })
    );

    return {
      mode,
      nodes,
      total_count: response.data.total,
      estimated_time: nodes.length * 2,
    };
  }

  /**
   * 提交复习反馈
   */
  async submitFeedback(feedback: ReviewFeedbackRequest): Promise<ReviewFeedbackResponse> {
    const response = await apiClient.post<any>(`/api/v1/reviews/${feedback.node_id}`, {
      quality: feedback.quality,
      review_duration: feedback.review_duration ?? 60,
    });
    return {
      node_id: response.data.node_id,
      new_mastery_level: masteryToNum(response.data.mastery_level),
      next_review_at: response.data.next_review_at,
      interval_days: response.data.interval_days,
    };
  }

  /**
   * 获取复习统计
   */
  async getReviewStats(graphId: UUID): Promise<ReviewStats> {
    const response = await apiClient.get<BackendReviewStats>('/api/v1/reviews/statistics', {
      params: { graph_id: graphId },
    });
    const dist = response.data.mastery_distribution ?? {};
    const masteredNodes = Number(dist.proficient ?? 0) + Number(dist.mastered ?? 0);
    return {
      total_nodes: response.data.total_nodes ?? 0,
      reviewed_today: 0,
      due_today: response.data.due_today ?? 0,
      mastered_nodes: masteredNodes,
      average_mastery: calcAverageMastery(dist),
      total_review_time: 0,
      streak_days: 0,
    };
  }

  /**
   * 获取今日待复习节点数
   */
  async getDueTodayCount(graphId: UUID): Promise<number> {
    const stats = await this.getReviewStats(graphId);
    return stats.due_today;
  }
}

export const reviewService = new ReviewService();

