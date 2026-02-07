import apiClient from './api';
import { UUID } from './knowledgeGraph';

interface UploadResponse {
  file_id: UUID;
  file_url: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  message: string;
}

interface BackendFileUploadResponse {
  id: UUID;
  original_filename: string;
  stored_filename: string;
  file_url: string;
  file_size: number;
  mime_type: string;
  status: string;
  user_id: UUID;
  created_at: string;
  processing_result?: Record<string, any>;
}

// 文件上传相关类型定义
export interface FileUploadResponse {
  id: UUID;
  filename: string;
  original_filename: string;
  file_path: string;
  file_url: string;
  file_type: string;
  file_size: number;
  upload_time: string;
  user_id: UUID;
  status: string;
  ocr_result?: any;
  ai_analysis?: any;
}

export interface FileListResponse {
  items: FileUploadResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

function mapUploadResponse(data: UploadResponse): FileUploadResponse {
  return {
    id: data.file_id,
    filename: data.original_filename,
    original_filename: data.original_filename,
    file_path: data.file_url,
    file_url: data.file_url,
    file_type: data.mime_type,
    file_size: data.file_size,
    upload_time: new Date().toISOString(),
    user_id: '' as UUID,
    status: 'pending',
  };
}

function mapFileResponse(data: BackendFileUploadResponse): FileUploadResponse {
  return {
    id: data.id,
    filename: data.stored_filename,
    original_filename: data.original_filename,
    file_path: data.file_url,
    file_url: data.file_url,
    file_type: data.mime_type,
    file_size: data.file_size,
    upload_time: data.created_at,
    user_id: data.user_id,
    status: data.status,
    ocr_result: data.processing_result?.ocr_text ? data.processing_result : undefined,
    ai_analysis: data.processing_result?.ai_analysis,
  };
}

// 文件上传服务
class FileUploadService {
  /**
   * 上传文件
   */
  async uploadFile(file: File, onProgress?: (progress: number) => void): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<UploadResponse>('/api/v1/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return mapUploadResponse(response.data);
  }

  /**
   * 获取文件列表
   */
  async getFiles(page: number = 1, pageSize: number = 20): Promise<FileListResponse> {
    const response = await apiClient.get<{
      items: BackendFileUploadResponse[];
      total: number;
      page: number;
      page_size: number;
      total_pages: number;
    }>('/api/v1/files/', {
      params: { page, page_size: pageSize },
    });
    return {
      ...response.data,
      items: response.data.items.map(mapFileResponse),
    };
  }

  /**
   * 获取文件详情
   */
  async getFileDetail(fileId: UUID): Promise<FileUploadResponse> {
    const response = await apiClient.get<BackendFileUploadResponse>(`/api/v1/files/${fileId}`);
    return mapFileResponse(response.data);
  }

  /**
   * 删除文件
   */
  async deleteFile(fileId: UUID): Promise<void> {
    await apiClient.delete(`/api/v1/files/${fileId}`);
  }
}

export const fileUploadService = new FileUploadService();

