import apiClient from './api';
import { PaginatedResponse } from './knowledgeGraph';

// 类型定义
export enum NodeType {
  CONCEPT = 'CONCEPT',
  QUESTION = 'QUESTION',
}

export enum MasteryLevel {
  NOT_STARTED = 'NOT_STARTED',
  LEARNING = 'LEARNING',
  REVIEWING = 'REVIEWING',
  MASTERED = 'MASTERED',
}

export interface MemoryNode {
  id: number;
  graph_id: number;
  node_type: NodeType;
  title: string;
  content_data: any;
  mastery_level: MasteryLevel;
  tags?: string[];
  position_x?: number;
  position_y?: number;
  created_at: string;
  updated_at: string;
  last_reviewed_at?: string;
  next_review_at?: string;
}

export interface CreateNodeRequest {
  graph_id: number;
  node_type: NodeType;
  title: string;
  content_data: any;
  tags?: string[];
  position_x?: number;
  position_y?: number;
}

export interface UpdateNodeRequest {
  title?: string;
  content_data?: any;
  mastery_level?: MasteryLevel;
  tags?: string[];
  position_x?: number;
  position_y?: number;
}

export interface NodeRelation {
  id: number;
  source_id: number;
  target_id: number;
  relation_type: string;
  strength: number;
  created_at: string;
}

export interface CreateRelationRequest {
  source_id: number;
  target_id: number;
  relation_type: string;
  strength?: number;
}

// 记忆节点服务
export const memoryNodeService = {
  // 创建记忆节点
  async createNode(data: CreateNodeRequest): Promise<MemoryNode> {
    const response = await apiClient.post<MemoryNode>('/api/v1/memory-nodes/', data);
    return response.data;
  },

  // 获取节点列表
  async getNodes(
    graphId: number,
    page: number = 1,
    pageSize: number = 20,
    nodeType?: NodeType
  ): Promise<PaginatedResponse<MemoryNode>> {
    const params: any = { graph_id: graphId, page, page_size: pageSize };
    if (nodeType) {
      params.node_type = nodeType;
    }
    const response = await apiClient.get<PaginatedResponse<MemoryNode>>('/api/v1/memory-nodes/', {
      params,
    });
    return response.data;
  },

  // 获取节点详情
  async getNode(nodeId: number): Promise<MemoryNode> {
    const response = await apiClient.get<MemoryNode>(`/api/v1/memory-nodes/${nodeId}`);
    return response.data;
  },

  // 更新节点
  async updateNode(nodeId: number, data: UpdateNodeRequest): Promise<MemoryNode> {
    const response = await apiClient.put<MemoryNode>(`/api/v1/memory-nodes/${nodeId}`, data);
    return response.data;
  },

  // 删除节点
  async deleteNode(nodeId: number): Promise<void> {
    await apiClient.delete(`/api/v1/memory-nodes/${nodeId}`);
  },

  // 创建节点关联
  async createRelation(data: CreateRelationRequest): Promise<NodeRelation> {
    const response = await apiClient.post<NodeRelation>('/api/v1/node-relations/', data);
    return response.data;
  },

  // 获取节点关联
  async getRelations(nodeId: number): Promise<NodeRelation[]> {
    const response = await apiClient.get<NodeRelation[]>('/api/v1/node-relations/', {
      params: { node_id: nodeId },
    });
    return response.data;
  },

  // 删除节点关联
  async deleteRelation(relationId: number): Promise<void> {
    await apiClient.delete(`/api/v1/node-relations/${relationId}`);
  },
};

