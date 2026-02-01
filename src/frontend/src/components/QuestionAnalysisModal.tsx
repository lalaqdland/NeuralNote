import React, { useState } from 'react';
import {
  Modal,
  Steps,
  Button,
  Space,
  Typography,
  Card,
  Spin,
  Alert,
  Divider,
  Tag,
  message,
  Input,
} from 'antd';
import {
  CloudUploadOutlined,
  ScanOutlined,
  RobotOutlined,
  CheckCircleOutlined,
  EditOutlined,
} from '@ant-design/icons';
import ImageUpload from './ImageUpload';
import { FileUploadResponse } from '../services/fileUpload';
import { ocrService, OCRResponse } from '../services/ocr';
import { aiAnalysisService, AnalyzeQuestionResponse } from '../services/aiAnalysis';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

interface QuestionAnalysisModalProps {
  visible: boolean;
  graphId: number;
  onClose: () => void;
  onSuccess?: (result: AnalyzeQuestionResponse) => void;
}

type StepStatus = 'wait' | 'process' | 'finish' | 'error';

const QuestionAnalysisModal: React.FC<QuestionAnalysisModalProps> = ({
  visible,
  graphId,
  onClose,
  onSuccess,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [uploadedFile, setUploadedFile] = useState<FileUploadResponse | null>(null);
  const [ocrResult, setOcrResult] = useState<OCRResponse | null>(null);
  const [ocrText, setOcrText] = useState('');
  const [analysisResult, setAnalysisResult] = useState<AnalyzeQuestionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 重置状态
  const resetState = () => {
    setCurrentStep(0);
    setUploadedFile(null);
    setOcrResult(null);
    setOcrText('');
    setAnalysisResult(null);
    setLoading(false);
    setError(null);
  };

  // 处理上传成功
  const handleUploadSuccess = (file: FileUploadResponse) => {
    setUploadedFile(file);
    setError(null);
  };

  // 执行 OCR 识别
  const handleOCR = async () => {
    if (!uploadedFile) {
      message.error('请先上传图片');
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentStep(1);

    try {
      const result = await ocrService.recognizeText(uploadedFile.id);
      setOcrResult(result);
      setOcrText(result.text);
      setCurrentStep(2);
      message.success('OCR 识别成功');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'OCR 识别失败');
      message.error('OCR 识别失败');
    } finally {
      setLoading(false);
    }
  };

  // 执行 AI 分析
  const handleAnalysis = async () => {
    if (!uploadedFile) {
      message.error('请先上传图片');
      return;
    }

    if (!ocrText.trim()) {
      message.error('OCR 识别文本为空');
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentStep(2);

    try {
      const result = await aiAnalysisService.analyzeQuestion({
        file_id: uploadedFile.id,
        graph_id: graphId,
        ocr_text: ocrText,
      });
      setAnalysisResult(result);
      setCurrentStep(3);
      message.success('AI 分析完成');
      
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'AI 分析失败');
      message.error('AI 分析失败');
    } finally {
      setLoading(false);
    }
  };

  // 关闭模态框
  const handleClose = () => {
    resetState();
    onClose();
  };

  const steps = [
    {
      title: '上传图片',
      icon: <CloudUploadOutlined />,
      description: '上传题目图片',
    },
    {
      title: 'OCR 识别',
      icon: <ScanOutlined />,
      description: '识别图片中的文字',
    },
    {
      title: 'AI 分析',
      icon: <RobotOutlined />,
      description: '分析题目并提取知识点',
    },
    {
      title: '完成',
      icon: <CheckCircleOutlined />,
      description: '创建记忆节点',
    },
  ];

  return (
    <Modal
      title="题目分析"
      open={visible}
      onCancel={handleClose}
      width={800}
      footer={null}
      destroyOnClose
    >
      <Steps current={currentStep} items={steps} style={{ marginBottom: 32 }} />

      {error && (
        <Alert
          message="错误"
          description={error}
          type="error"
          closable
          onClose={() => setError(null)}
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 步骤 0: 上传图片 */}
      {currentStep === 0 && (
        <div>
          <ImageUpload onUploadSuccess={handleUploadSuccess} />
          {uploadedFile && (
            <div style={{ marginTop: 16, textAlign: 'right' }}>
              <Button type="primary" size="large" onClick={handleOCR}>
                下一步：OCR 识别
              </Button>
            </div>
          )}
        </div>
      )}

      {/* 步骤 1: OCR 识别中 */}
      {currentStep === 1 && loading && (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <Spin size="large" />
          <Title level={4} style={{ marginTop: 24, color: '#667eea' }}>
            正在识别图片中的文字...
          </Title>
          <Text type="secondary">这可能需要几秒钟</Text>
        </div>
      )}

      {/* 步骤 2: OCR 结果展示和编辑 */}
      {currentStep === 2 && !loading && ocrResult && (
        <div>
          <Card
            title={
              <Space>
                <ScanOutlined style={{ color: '#667eea' }} />
                <span>OCR 识别结果</span>
                <Tag color="green">置信度: {(ocrResult.confidence * 100).toFixed(1)}%</Tag>
              </Space>
            }
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                耗时: {ocrResult.processing_time.toFixed(2)}s
              </Text>
            }
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Text strong>
                  <EditOutlined /> 识别文本（可编辑）:
                </Text>
                <TextArea
                  value={ocrText}
                  onChange={(e) => setOcrText(e.target.value)}
                  rows={8}
                  style={{ marginTop: 8 }}
                  placeholder="请输入或修正题目文本"
                />
                <Text type="secondary" style={{ fontSize: 12, marginTop: 4, display: 'block' }}>
                  提示: 如果识别有误，可以手动修正
                </Text>
              </div>
            </Space>
          </Card>

          <div style={{ marginTop: 16, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setCurrentStep(0)}>返回上一步</Button>
              <Button type="primary" size="large" onClick={handleAnalysis}>
                下一步：AI 分析
              </Button>
            </Space>
          </div>
        </div>
      )}

      {/* 步骤 2: AI 分析中 */}
      {currentStep === 2 && loading && (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <Spin size="large" />
          <Title level={4} style={{ marginTop: 24, color: '#667eea' }}>
            AI 正在分析题目...
          </Title>
          <Text type="secondary">正在生成解答和提取知识点</Text>
        </div>
      )}

      {/* 步骤 3: AI 分析结果展示 */}
      {currentStep === 3 && analysisResult && (
        <div>
          <Card
            title={
              <Space>
                <RobotOutlined style={{ color: '#667eea' }} />
                <span>AI 分析结果</span>
                <Tag color="blue">难度: {analysisResult.difficulty}/5</Tag>
              </Space>
            }
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                耗时: {analysisResult.processing_time.toFixed(2)}s
              </Text>
            }
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* 题目 */}
              <div>
                <Text strong>📝 题目:</Text>
                <Paragraph style={{ marginTop: 8, padding: 12, background: '#f5f5f5', borderRadius: 8 }}>
                  {analysisResult.question_text}
                </Paragraph>
              </div>

              <Divider />

              {/* 答案 */}
              <div>
                <Text strong>✅ 答案:</Text>
                <Paragraph style={{ marginTop: 8, padding: 12, background: '#e6f7ff', borderRadius: 8 }}>
                  {analysisResult.answer}
                </Paragraph>
              </div>

              <Divider />

              {/* 解析 */}
              <div>
                <Text strong>💡 解析:</Text>
                <Paragraph style={{ marginTop: 8, padding: 12, background: '#fff7e6', borderRadius: 8 }}>
                  {analysisResult.explanation}
                </Paragraph>
              </div>

              <Divider />

              {/* 知识点 */}
              <div>
                <Text strong>🎯 知识点:</Text>
                <Space wrap style={{ marginTop: 8 }}>
                  {analysisResult.knowledge_points.map((kp, index) => (
                    <Tag key={index} color="purple" style={{ padding: '4px 12px', fontSize: 14 }}>
                      {kp.name}
                    </Tag>
                  ))}
                </Space>
              </div>

              {/* 标签 */}
              {analysisResult.tags.length > 0 && (
                <div>
                  <Text strong>🏷️ 标签:</Text>
                  <Space wrap style={{ marginTop: 8 }}>
                    {analysisResult.tags.map((tag, index) => (
                      <Tag key={index} color="cyan">
                        {tag}
                      </Tag>
                    ))}
                  </Space>
                </div>
              )}
            </Space>
          </Card>

          <div style={{ marginTop: 16, textAlign: 'right' }}>
            <Space>
              <Button onClick={handleClose}>关闭</Button>
              <Button type="primary" size="large" onClick={handleClose}>
                完成
              </Button>
            </Space>
          </div>
        </div>
      )}
    </Modal>
  );
};

export default QuestionAnalysisModal;

