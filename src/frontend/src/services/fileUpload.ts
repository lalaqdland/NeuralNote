import apiClient from './api';

// 文件上传相关类型定义
export interface FileUploadResponse {
  id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_url: string;
  file_type: string;
  file_size: number;
  upload_time: string;
  user_id: number;
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

// 文件上传服务
class FileUploadService {
  /**
   * 上传文件
   */
  async uploadFile(file: File, onProgress?: (progress: number) => void): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<FileUploadResponse>('/api/v1/files/upload', formData, {
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

    return response.data;
  }

  /**
   * 获取文件列表
   */
  async getFiles(page: number = 1, pageSize: number = 20): Promise<FileListResponse> {
    const response = await apiClient.get<FileListResponse>('/api/v1/files/', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  /**
   * 获取文件详情
   */
  async getFileDetail(fileId: number): Promise<FileUploadResponse> {
    const response = await apiClient.get<FileUploadResponse>(`/api/v1/files/${fileId}`);
    return response.data;
  }

  /**
   * 删除文件
   */
  async deleteFile(fileId: number): Promise<void> {
    await apiClient.delete(`/api/v1/files/${fileId}`);
  }
}

export const fileUploadService = new FileUploadService();

