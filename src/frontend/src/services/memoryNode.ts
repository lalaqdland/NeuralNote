import apiClient from './api';
import { PaginatedResponse, UUID } from './knowledgeGraph';

// 类型定义
export type NodeType = 'CONCEPT' | 'QUESTION' | 'NOTE' | 'RESOURCE';

export interface MemoryNode {
  id: UUID;
  graph_id: UUID;
  node_type: NodeType;
  title: string;
  summary?: string;
  content_data: Record<string, any>;
  mastery_level: number; // 0-5
  tags?: string[];
  position_x?: number;
  position_y?: number;
  position_z?: number;
  created_at: string;
  updated_at: string;
  last_reviewed_at?: string;
  next_review_at?: string;
  review_count?: number;
  vector_embedding?: number[];
}

export interface CreateNodeRequest {
  graph_id: UUID;
  node_type: NodeType;
  title: string;
  summary?: string;
  content_data: Record<string, any>;
  mastery_level?: number;
  tags?: string[];
  position_x?: number;
  position_y?: number;
  position_z?: number;
}

export interface UpdateNodeRequest {
  title?: string;
  summary?: string;
  content_data?: Record<string, any>;
  node_type?: NodeType;
  mastery_level?: number;
  tags?: string[];
  position_x?: number;
  position_y?: number;
  position_z?: number;
}

export interface NodeRelation {
  id: UUID;
  source_id: UUID;
  target_id: UUID;
  relation_type: string;
  strength: number;
  created_at: string;
}

export interface CreateRelationRequest {
  source_id: UUID;
  target_id: UUID;
  relation_type: string;
  strength?: number;
}

type BackendNodeType = 'CONCEPT' | 'QUESTION' | 'SNIPPET' | 'INSIGHT';
type BackendMasteryLevel = 'not_started' | 'learning' | 'familiar' | 'proficient' | 'mastered';

interface BackendMemoryNode {
  id: UUID;
  graph_id: UUID;
  node_type: BackendNodeType;
  title: string;
  summary?: string;
  content_data?: Record<string, any>;
  position_x?: number;
  position_y?: number;
  position_z?: number;
  created_at: string;
  updated_at: string;
  mastery_level?: BackendMasteryLevel;
  last_review_at?: string;
  next_review_at?: string;
  review_stats?: Record<string, any>;
}

interface BackendRelation {
  id: UUID;
  source_id: UUID;
  target_id: UUID;
  relation_type: string;
  strength: number;
  created_at: string;
}

const MASTERY_TO_NUM: Record<BackendMasteryLevel, number> = {
  not_started: 0,
  learning: 1,
  familiar: 3,
  proficient: 4,
  mastered: 5,
};

const UI_TO_BACKEND_NODE: Record<NodeType, BackendNodeType> = {
  CONCEPT: 'CONCEPT',
  QUESTION: 'QUESTION',
  NOTE: 'SNIPPET',
  RESOURCE: 'INSIGHT',
};

const BACKEND_TO_UI_NODE: Record<BackendNodeType, NodeType> = {
  CONCEPT: 'CONCEPT',
  QUESTION: 'QUESTION',
  SNIPPET: 'NOTE',
  INSIGHT: 'RESOURCE',
};

const UI_RELATION_TO_BACKEND: Record<string, string> = {
  prerequisite: 'PREREQUISITE',
  related: 'RELATED',
  similar: 'VARIANT',
  extends: 'RELATED',
  application: 'RELATED',
  example: 'RELATED',
};

const BACKEND_RELATION_TO_UI: Record<string, string> = {
  PREREQUISITE: 'prerequisite',
  RELATED: 'related',
  VARIANT: 'similar',
};

function toBackendNodeType(nodeType: NodeType): BackendNodeType {
  return UI_TO_BACKEND_NODE[nodeType] ?? 'CONCEPT';
}

function toUiNodeType(nodeType?: string): NodeType {
  if (!nodeType) return 'CONCEPT';
  return BACKEND_TO_UI_NODE[nodeType as BackendNodeType] ?? (nodeType as NodeType);
}

function toUiMastery(level?: BackendMasteryLevel | number): number {
  if (typeof level === 'number') return Math.max(0, Math.min(5, level));
  if (!level) return 0;
  return MASTERY_TO_NUM[level] ?? 0;
}

function normalizeStrength(strength?: number): number {
  if (strength === undefined || Number.isNaN(strength)) return 50;
  if (strength <= 1) return Math.round(strength * 100);
  return Math.max(0, Math.min(100, Math.round(strength)));
}

function toBackendRelationType(relationType: string): string {
  const upper = relationType.toUpperCase();
  if (upper === 'PREREQUISITE' || upper === 'RELATED' || upper === 'VARIANT') {
    return upper;
  }
  return UI_RELATION_TO_BACKEND[relationType] ?? 'RELATED';
}

function toUiRelationType(relationType: string): string {
  return BACKEND_RELATION_TO_UI[relationType] ?? relationType.toLowerCase();
}

function mapNode(node: BackendMemoryNode): MemoryNode {
  return {
    id: node.id,
    graph_id: node.graph_id,
    node_type: toUiNodeType(node.node_type),
    title: node.title,
    summary: node.summary,
    content_data: node.content_data ?? {},
    mastery_level: toUiMastery(node.mastery_level),
    position_x: node.position_x,
    position_y: node.position_y,
    position_z: node.position_z,
    created_at: node.created_at,
    updated_at: node.updated_at,
    last_reviewed_at: node.last_review_at,
    next_review_at: node.next_review_at,
    review_count: Number(node.review_stats?.total_reviews ?? 0),
  };
}

function mapRelation(relation: BackendRelation): NodeRelation {
  return {
    id: relation.id,
    source_id: relation.source_id,
    target_id: relation.target_id,
    relation_type: toUiRelationType(relation.relation_type),
    strength: relation.strength,
    created_at: relation.created_at,
  };
}

// 记忆节点服务
export const memoryNodeService = {
  // 创建记忆节点
  async createNode(data: CreateNodeRequest): Promise<MemoryNode> {
    const payload = {
      graph_id: data.graph_id,
      node_type: toBackendNodeType(data.node_type),
      title: data.title,
      summary: data.summary,
      content_data: data.content_data,
      position_x: data.position_x ?? 0,
      position_y: data.position_y ?? 0,
      position_z: data.position_z ?? 0,
    };
    const response = await apiClient.post<BackendMemoryNode>('/api/v1/nodes/', payload);
    return mapNode(response.data);
  },

  // 获取节点列表
  async getNodes(
    graphId: UUID,
    page: number = 1,
    pageSize: number = 20,
    nodeType?: NodeType
  ): Promise<PaginatedResponse<MemoryNode>> {
    const params: Record<string, any> = { graph_id: graphId, page, page_size: pageSize };
    if (nodeType) {
      params.node_type = toBackendNodeType(nodeType);
    }
    const response = await apiClient.get<PaginatedResponse<BackendMemoryNode>>('/api/v1/nodes/', {
      params,
    });

    // 列表接口返回字段较少，补充拉取详情以满足前端现有展示逻辑
    const detailItems = await Promise.all(
      response.data.items.map(async (item) => {
        try {
          const detail = await memoryNodeService.getNode(item.id);
          return detail;
        } catch {
          return mapNode(item);
        }
      })
    );

    return {
      ...response.data,
      items: detailItems,
    };
  },

  // 获取节点详情
  async getNode(nodeId: UUID): Promise<MemoryNode> {
    const response = await apiClient.get<BackendMemoryNode>(`/api/v1/nodes/${nodeId}`);
    return mapNode(response.data);
  },

  // 更新节点
  async updateNode(nodeId: UUID, data: UpdateNodeRequest): Promise<MemoryNode> {
    const payload: Record<string, any> = { ...data };
    if (payload.node_type) {
      payload.node_type = toBackendNodeType(payload.node_type);
    }
    delete payload.mastery_level;
    delete payload.tags;
    const response = await apiClient.put<BackendMemoryNode>(`/api/v1/nodes/${nodeId}`, payload);
    return mapNode(response.data);
  },

  // 删除节点
  async deleteNode(nodeId: UUID): Promise<void> {
    await apiClient.delete(`/api/v1/nodes/${nodeId}`);
  },

  // 创建节点关联
  async createRelation(data: CreateRelationRequest): Promise<NodeRelation> {
    const payload = {
      source_node_id: data.source_id,
      target_node_id: data.target_id,
      relation_type: toBackendRelationType(data.relation_type),
      strength: normalizeStrength(data.strength),
      is_auto_generated: false,
    };
    const response = await apiClient.post<BackendRelation>(`/api/v1/nodes/${data.source_id}/relations`, payload);
    return mapRelation(response.data);
  },

  // 获取节点关联
  async getRelations(nodeId: UUID): Promise<NodeRelation[]> {
    const response = await apiClient.get<BackendRelation[]>(`/api/v1/nodes/${nodeId}/relations`);
    return response.data.map(mapRelation);
  },

  // 删除节点关联
  async deleteRelation(relationId: UUID): Promise<void> {
    await apiClient.delete(`/api/v1/nodes/relations/${relationId}`);
  },
};
