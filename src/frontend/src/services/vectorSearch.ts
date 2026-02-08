import apiClient from './api';
import { MemoryNode } from './memoryNode';
import { UUID } from './knowledgeGraph';

// 类型定义
export interface VectorSearchRequest {
  query: string;
  graph_id?: UUID;
  top_k?: number;
  threshold?: number;
}

interface BackendSimilarNode {
  node_id: UUID;
  title: string;
  node_type: string;
  summary?: string;
  similarity_score: number;
  graph_id: UUID;
}

interface BackendVectorSearchResponse {
  query_text: string;
  total: number;
  results: BackendSimilarNode[];
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
  node_ids: UUID[];
  size: number;
}

function mapSimilarNode(item: BackendSimilarNode): SimilarNode {
  return {
    node: {
      id: item.node_id,
      graph_id: item.graph_id,
      node_type: item.node_type as any,
      title: item.title,
      summary: item.summary,
      content_data: { description: item.summary ?? '' },
      mastery_level: 0,
      created_at: '',
      updated_at: '',
      review_count: 0,
    },
    similarity: item.similarity_score,
  };
}

// 向量搜索服务
export const vectorSearchService = {
  // 文本查询搜索相似节点
  async searchByText(data: VectorSearchRequest): Promise<SimilarNode[]> {
    const response = await apiClient.post<BackendVectorSearchResponse>('/api/v1/vector-search/search', {
      query_text: data.query,
      graph_id: data.graph_id,
      limit: data.top_k ?? 10,
      similarity_threshold: data.threshold ?? 0.7,
    });
    return response.data.results.map(mapSimilarNode);
  },

  // 查找与指定节点相似的节点
  async findSimilarNodes(
    nodeId: UUID,
    topK: number = 10,
    threshold: number = 0.7
  ): Promise<SimilarNode[]> {
    const response = await apiClient.get<BackendSimilarNode[]>(
      `/api/v1/vector-search/similar/${nodeId}`,
      {
        params: { limit: topK, similarity_threshold: threshold },
      }
    );
    return response.data.map(mapSimilarNode);
  },

  // 获取节点推荐（学习路径）
  async getRecommendations(
    nodeId: UUID,
    topK: number = 5
  ): Promise<NodeRecommendation[]> {
    const response = await apiClient.get<BackendSimilarNode[]>(
      `/api/v1/vector-search/recommend/${nodeId}`,
      {
        params: { limit: topK },
      }
    );
    return response.data.map((item) => ({
      ...mapSimilarNode(item),
      reason: '语义相似',
    }));
  },

  // 节点聚类（相似度分组）
  async clusterNodes(
    graphId: UUID,
    threshold: number = 0.8
  ): Promise<NodeCluster[]> {
    const response = await apiClient.get<{
      clusters: NodeCluster[];
    }>(`/api/v1/vector-search/cluster/${graphId}`, {
      params: { similarity_threshold: threshold },
    });
    return response.data.clusters;
  },
};

