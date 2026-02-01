import React, { useState } from 'react';
import { Upload, message, Progress, Card, Image, Space, Typography, Button } from 'antd';
import {
  InboxOutlined,
  FileImageOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { fileUploadService, FileUploadResponse } from '../services/fileUpload';

const { Dragger } = Upload;
const { Text, Title } = Typography;

interface ImageUploadProps {
  onUploadSuccess?: (file: FileUploadResponse) => void;
  onUploadError?: (error: any) => void;
  maxSize?: number; // MB
  accept?: string;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  onUploadSuccess,
  onUploadError,
  maxSize = 10,
  accept = 'image/*',
}) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState<FileUploadResponse | null>(null);
  const [previewVisible, setPreviewVisible] = useState(false);

  const handleUpload = async (file: File) => {
    // 文件大小验证
    const isLtMaxSize = file.size / 1024 / 1024 < maxSize;
    if (!isLtMaxSize) {
      message.error(`图片大小不能超过 ${maxSize}MB`);
      return false;
    }

    // 文件类型验证
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件');
      return false;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const response = await fileUploadService.uploadFile(file, (progress) => {
        setUploadProgress(progress);
      });

      setUploadedFile(response);
      message.success('上传成功');
      
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传失败');
      if (onUploadError) {
        onUploadError(error);
      }
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }

    return false; // 阻止默认上传行为
  };

  const handleRemove = () => {
    setUploadedFile(null);
    setUploadProgress(0);
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept,
    beforeUpload: handleUpload,
    showUploadList: false,
    disabled: uploading,
  };

  return (
    <div>
      {!uploadedFile ? (
        <Dragger {...uploadProps} style={{ padding: '20px' }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined style={{ fontSize: 48, color: '#667eea' }} />
          </p>
          <p className="ant-upload-text" style={{ fontSize: 16, fontWeight: 500 }}>
            点击或拖拽图片到此区域上传
          </p>
          <p className="ant-upload-hint" style={{ color: '#999' }}>
            支持 JPG、PNG、GIF 等格式，单个文件不超过 {maxSize}MB
          </p>
        </Dragger>
      ) : (
        <Card
          hoverable
          cover={
            <div style={{ position: 'relative', paddingTop: '75%', overflow: 'hidden' }}>
              <Image
                src={uploadedFile.file_url}
                alt={uploadedFile.original_filename}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  objectFit: 'contain',
                }}
                preview={{
                  visible: previewVisible,
                  onVisibleChange: setPreviewVisible,
                }}
              />
            </div>
          }
          actions={[
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => setPreviewVisible(true)}
            >
              预览
            </Button>,
            <Button type="text" icon={<DeleteOutlined />} danger onClick={handleRemove}>
              删除
            </Button>,
          ]}
        >
          <Card.Meta
            avatar={<FileImageOutlined style={{ fontSize: 24, color: '#667eea' }} />}
            title={
              <Text ellipsis style={{ maxWidth: 200 }}>
                {uploadedFile.original_filename}
              </Text>
            }
            description={
              <Space direction="vertical" size={4}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  大小: {(uploadedFile.file_size / 1024).toFixed(2)} KB
                </Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  类型: {uploadedFile.file_type}
                </Text>
              </Space>
            }
          />
        </Card>
      )}

      {uploading && (
        <div style={{ marginTop: 16 }}>
          <Progress percent={uploadProgress} status="active" strokeColor="#667eea" />
          <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>
            正在上传...
          </Text>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;

