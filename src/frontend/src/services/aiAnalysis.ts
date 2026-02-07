import apiClient from './api';
import { UUID } from './knowledgeGraph';

// AI 分析相关类型定义
export interface AnalyzeQuestionRequest {
  file_id: UUID;
  graph_id: UUID;
  ocr_text?: string;
}

export interface KnowledgePoint {
  name: string;
  description: string;
  difficulty: number;
  tags: string[];
}

export interface AnalyzeQuestionResponse {
  file_id: UUID;
  graph_id: UUID;
  question_text: string;
  answer: string;
  explanation: string;
  knowledge_points: KnowledgePoint[];
  difficulty: number;
  tags: string[];
  node_id?: UUID;
  processing_time: number;
}

export interface ExtractKnowledgeResponse {
  knowledge_points: KnowledgePoint[];
  processing_time: number;
}

export interface TextAnalysisRequest {
  text: string;
  analysis_type: 'summary' | 'keywords' | 'sentiment' | 'classification';
}

export interface TextAnalysisResponse {
  result: any;
  processing_time: number;
}

interface BackendAIAnalysis {
  subject: string;
  difficulty: string;
  question_type: string;
  answer: string;
  key_points: string[];
  summary: string;
  tags: string[];
  engine: string;
  embedding?: number[];
}

interface BackendAnalyzeQuestionResponse {
  file_id: UUID;
  analysis: BackendAIAnalysis;
  node_id?: UUID;
}

function difficultyToNumber(difficulty: string): number {
  const raw = String(difficulty || '').toLowerCase();
  if (raw.includes('easy') || raw.includes('简单')) return 2;
  if (raw.includes('hard') || raw.includes('困难')) return 4;
  if (raw.includes('medium') || raw.includes('中等')) return 3;
  const numeric = Number(difficulty);
  if (Number.isFinite(numeric) && numeric > 0) return Math.max(1, Math.min(5, numeric));
  return 3;
}

function toKnowledgePoints(list: string[] = []): KnowledgePoint[] {
  return list.map((name) => ({
    name,
    description: '',
    difficulty: 3,
    tags: [],
  }));
}

// AI 分析服务
class AIAnalysisService {
  /**
   * 完整的题目分析流程（上传 -> OCR -> AI 分析 -> 创建节点）
   */
  async analyzeQuestion(request: AnalyzeQuestionRequest): Promise<AnalyzeQuestionResponse> {
    const response = await apiClient.post<BackendAnalyzeQuestionResponse>(
      '/api/v1/ai/analyze-question',
      {
        file_id: request.file_id,
        graph_id: request.graph_id,
        create_node: true,
        engine: 'auto',
        ocr_text: request.ocr_text,
      }
    );

    const analysis = response.data.analysis;
    return {
      file_id: response.data.file_id,
      graph_id: request.graph_id,
      question_text: request.ocr_text ?? '',
      answer: analysis.answer ?? '',
      explanation: analysis.summary ?? '',
      knowledge_points: toKnowledgePoints(analysis.key_points),
      difficulty: difficultyToNumber(analysis.difficulty),
      tags: analysis.tags ?? [],
      node_id: response.data.node_id,
      processing_time: 0,
    };
  }

  /**
   * 提取知识点
   */
  async extractKnowledge(text: string): Promise<ExtractKnowledgeResponse> {
    const response = await apiClient.post<{ knowledge_points: string[] }>('/api/v1/ai/extract-knowledge', {
      content: text,
      engine: 'auto',
    });
    return {
      knowledge_points: toKnowledgePoints(response.data.knowledge_points),
      processing_time: 0,
    };
  }

  /**
   * 文本分析
   */
  async analyzeText(request: TextAnalysisRequest): Promise<TextAnalysisResponse> {
    const response = await apiClient.post<BackendAIAnalysis>('/api/v1/ai/analyze', {
      text: request.text,
      engine: 'auto',
      include_embedding: false,
    });
    return {
      result: response.data,
      processing_time: 0,
    };
  }
}

export const aiAnalysisService = new AIAnalysisService();

