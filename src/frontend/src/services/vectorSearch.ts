import apiClient from './api';
import { MemoryNode } from './memoryNode';

// 类型定义
export interface VectorSearchRequest {
  query: string;
  graph_id?: number;
  top_k?: number;
  threshold?: number;
}

export interface SimilarNode {
  node: MemoryNode;
  similarity: number;
}

export interface NodeRecommendation {
  node: MemoryNode;
  reason: string;
  similarity: number;
}

export interface NodeCluster {
  cluster_id: number;
  nodes: MemoryNode[];
  avg_similarity: number;
}

// 向量搜索服务
export const vectorSearchService = {
  // 文本查询搜索相似节点
  async searchByText(data: VectorSearchRequest): Promise<SimilarNode[]> {
    const response = await apiClient.post<SimilarNode[]>('/api/v1/vector-search/search', data);
    return response.data;
  },

  // 查找与指定节点相似的节点
  async findSimilarNodes(
    nodeId: number,
    topK: number = 10,
    threshold: number = 0.7
  ): Promise<SimilarNode[]> {
    const response = await apiClient.get<SimilarNode[]>(
      `/api/v1/vector-search/similar/${nodeId}`,
      {
        params: { top_k: topK, threshold },
      }
    );
    return response.data;
  },

  // 获取节点推荐（学习路径）
  async getRecommendations(
    nodeId: number,
    topK: number = 5
  ): Promise<NodeRecommendation[]> {
    const response = await apiClient.get<NodeRecommendation[]>(
      `/api/v1/vector-search/recommend/${nodeId}`,
      {
        params: { top_k: topK },
      }
    );
    return response.data;
  },

  // 节点聚类（相似度分组）
  async clusterNodes(
    graphId: number,
    threshold: number = 0.8
  ): Promise<NodeCluster[]> {
    const response = await apiClient.get<NodeCluster[]>(
      `/api/v1/vector-search/cluster/${graphId}`,
      {
        params: { threshold },
      }
    );
    return response.data;
  },
};

