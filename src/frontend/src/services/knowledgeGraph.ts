import apiClient from './api';

export type UUID = string;

// 类型定义
export interface KnowledgeGraph {
  id: UUID;
  user_id: UUID;
  name: string;
  description?: string;
  subject?: string;
  cover_image_url?: string;
  is_public: boolean;
  node_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateGraphRequest {
  name: string;
  description?: string;
  subject?: string;
  cover_image_url?: string;
  is_public?: boolean;
}

export interface UpdateGraphRequest {
  name?: string;
  description?: string;
  subject?: string;
  cover_image_url?: string;
  is_public?: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface GraphStatistics {
  graph_id: UUID;
  total_nodes: number;
  total_relations: number;
  total_tags: number;
  review_due_count: number;
  last_review_at?: string;
}

// 知识图谱服务
export const knowledgeGraphService = {
  // 创建知识图谱
  async createGraph(data: CreateGraphRequest): Promise<KnowledgeGraph> {
    const response = await apiClient.post<KnowledgeGraph>('/api/v1/graphs/', data);
    return response.data;
  },

  // 获取知识图谱列表
  async getGraphs(page: number = 1, pageSize: number = 10): Promise<PaginatedResponse<KnowledgeGraph>> {
    const response = await apiClient.get<PaginatedResponse<KnowledgeGraph>>('/api/v1/graphs/', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  // 获取知识图谱详情
  async getGraph(graphId: UUID): Promise<KnowledgeGraph> {
    const response = await apiClient.get<KnowledgeGraph>(`/api/v1/graphs/${graphId}`);
    return response.data;
  },

  // 更新知识图谱
  async updateGraph(graphId: UUID, data: UpdateGraphRequest): Promise<KnowledgeGraph> {
    const response = await apiClient.put<KnowledgeGraph>(`/api/v1/graphs/${graphId}`, data);
    return response.data;
  },

  // 删除知识图谱
  async deleteGraph(graphId: UUID): Promise<void> {
    await apiClient.delete(`/api/v1/graphs/${graphId}`);
  },

  // 获取图谱统计信息
  async getGraphStatistics(graphId: UUID): Promise<GraphStatistics> {
    const response = await apiClient.get<GraphStatistics>(`/api/v1/graphs/${graphId}/stats`);
    return response.data;
  },
};

