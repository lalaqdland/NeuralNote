import apiClient from './api';

// AI 分析相关类型定义
export interface AnalyzeQuestionRequest {
  file_id: number;
  graph_id: number;
  ocr_text?: string;
}

export interface KnowledgePoint {
  name: string;
  description: string;
  difficulty: number;
  tags: string[];
}

export interface AnalyzeQuestionResponse {
  file_id: number;
  graph_id: number;
  question_text: string;
  answer: string;
  explanation: string;
  knowledge_points: KnowledgePoint[];
  difficulty: number;
  tags: string[];
  node_id: number;
  processing_time: number;
}

export interface ExtractKnowledgeRequest {
  text: string;
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

// AI 分析服务
class AIAnalysisService {
  /**
   * 完整的题目分析流程（上传 → OCR → AI 分析 → 创建节点）
   */
  async analyzeQuestion(request: AnalyzeQuestionRequest): Promise<AnalyzeQuestionResponse> {
    const response = await apiClient.post<AnalyzeQuestionResponse>(
      '/api/v1/ai/analyze-question',
      request
    );
    return response.data;
  }

  /**
   * 提取知识点
   */
  async extractKnowledge(text: string): Promise<ExtractKnowledgeResponse> {
    const response = await apiClient.post<ExtractKnowledgeResponse>(
      '/api/v1/ai/extract-knowledge',
      { text }
    );
    return response.data;
  }

  /**
   * 文本分析
   */
  async analyzeText(request: TextAnalysisRequest): Promise<TextAnalysisResponse> {
    const response = await apiClient.post<TextAnalysisResponse>('/api/v1/ai/analyze', request);
    return response.data;
  }
}

export const aiAnalysisService = new AIAnalysisService();

