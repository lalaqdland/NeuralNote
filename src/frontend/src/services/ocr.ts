import apiClient from './api';
import { UUID } from './knowledgeGraph';

// OCR 相关类型定义
export interface OCRRequest {
  file_id: UUID;
}

export interface OCRResponse {
  file_id: UUID;
  text: string;
  confidence: number;
  words_result: Array<{
    words: string;
    location: {
      left: number;
      top: number;
      width: number;
      height: number;
    };
  }>;
  processing_time: number;
}

export interface MathOCRResponse {
  file_id: UUID;
  latex: string;
  confidence: number;
  processing_time: number;
}

// OCR 服务
class OCRService {
  /**
   * 通用 OCR 识别
   */
  async recognizeText(fileId: UUID): Promise<OCRResponse> {
    const response = await apiClient.post<OCRResponse>('/api/v1/ocr/ocr', {
      file_id: fileId,
    });
    return response.data;
  }

  /**
   * 数学公式 OCR 识别
   */
  async recognizeMath(fileId: UUID): Promise<MathOCRResponse> {
    const response = await apiClient.post<MathOCRResponse>('/api/v1/ocr/ocr/math', {
      file_id: fileId,
    });
    return response.data;
  }
}

export const ocrService = new OCRService();

