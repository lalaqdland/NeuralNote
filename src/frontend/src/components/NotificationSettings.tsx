import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Switch,
  InputNumber,
  TimePicker,
  Button,
  Space,
  Alert,
  Divider,
  List,
  Tag,
  Empty,
  Popconfirm,
  message,
} from 'antd';
import {
  BellOutlined,
  ClockCircleOutlined,
  SoundOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { notificationService, NotificationSettings, NotificationRecord } from '../services/notification';

interface NotificationSettingsModalProps {
  visible: boolean;
  onClose: () => void;
}

const NotificationSettingsModal: React.FC<NotificationSettingsModalProps> = ({ visible, onClose }) => {
  const [form] = Form.useForm();
  const [settings, setSettings] = useState<NotificationSettings>(notificationService.getSettings());
  const [records, setRecords] = useState<NotificationRecord[]>([]);
  const [permission, setPermission] = useState<NotificationPermission | 'unsupported'>(
    notificationService.checkPermission()
  );

  useEffect(() => {
    if (visible) {
      loadData();
    }
  }, [visible]);

  const loadData = () => {
    const currentSettings = notificationService.getSettings();
    setSettings(currentSettings);
    setRecords(notificationService.getRecords());
    setPermission(notificationService.checkPermission());

    // 设置表单值
    form.setFieldsValue({
      enabled: currentSettings.enabled,
      checkInterval: currentSettings.checkInterval,
      quietHoursStart: currentSettings.quietHoursStart
        ? dayjs(currentSettings.quietHoursStart, 'HH:mm')
        : null,
      quietHoursEnd: currentSettings.quietHoursEnd ? dayjs(currentSettings.quietHoursEnd, 'HH:mm') : null,
      minDueCount: currentSettings.minDueCount,
      soundEnabled: currentSettings.soundEnabled,
    });
  };

  const handleRequestPermission = async () => {
    const granted = await notificationService.requestPermission();
    if (granted) {
      message.success('通知权限已授予');
      setPermission('granted');
    } else {
      message.error('通知权限被拒绝');
      setPermission('denied');
    }
  };

  const handleTestNotification = async () => {
    if (permission !== 'granted') {
      message.warning('请先授予通知权限');
      return;
    }
    await notificationService.testNotification();
    message.success('测试通知已发送');
    // 刷新记录
    setTimeout(() => {
      setRecords(notificationService.getRecords());
    }, 500);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const newSettings: NotificationSettings = {
        enabled: values.enabled,
        checkInterval: values.checkInterval,
        quietHoursStart: values.quietHoursStart ? values.quietHoursStart.format('HH:mm') : undefined,
        quietHoursEnd: values.quietHoursEnd ? values.quietHoursEnd.format('HH:mm') : undefined,
        minDueCount: values.minDueCount,
        soundEnabled: values.soundEnabled,
      };
      notificationService.updateSettings(newSettings);
      message.success('设置已保存');
      onClose();
    } catch (error) {
      console.error('保存设置失败:', error);
    }
  };

  const handleClearRecords = () => {
    notificationService.clearRecords();
    setRecords([]);
    message.success('通知记录已清空');
  };

  const formatTimestamp = (timestamp: number) => {
    return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss');
  };

  return (
    <Modal
      title={
        <Space>
          <BellOutlined />
          通知设置
        </Space>
      }
      open={visible}
      onCancel={onClose}
      width={700}
      footer={[
        <Button key="cancel" onClick={onClose}>
          取消
        </Button>,
        <Button key="save" type="primary" onClick={handleSave}>
          保存设置
        </Button>,
      ]}
    >
      {/* 权限状态 */}
      {permission === 'unsupported' && (
        <Alert
          message="浏览器不支持通知功能"
          description="您的浏览器不支持桌面通知，请使用现代浏览器（Chrome、Firefox、Edge等）"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {permission === 'default' && (
        <Alert
          message="需要授予通知权限"
          description={
            <Space direction="vertical">
              <span>要使用复习提醒功能，需要授予浏览器通知权限</span>
              <Button type="primary" size="small" onClick={handleRequestPermission}>
                授予权限
              </Button>
            </Space>
          }
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {permission === 'denied' && (
        <Alert
          message="通知权限被拒绝"
          description="您已拒绝通知权限，请在浏览器设置中手动开启"
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {permission === 'granted' && (
        <Alert
          message="通知权限已授予"
          description={
            <Space>
              <span>您可以接收复习提醒通知</span>
              <Button type="link" size="small" onClick={handleTestNotification}>
                发送测试通知
              </Button>
            </Space>
          }
          type="success"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 设置表单 */}
      <Form form={form} layout="vertical">
        <Form.Item name="enabled" label="启用复习提醒" valuePropName="checked">
          <Switch
            checkedChildren="开启"
            unCheckedChildren="关闭"
            disabled={permission !== 'granted'}
          />
        </Form.Item>

        <Form.Item
          name="checkInterval"
          label="检查间隔（分钟）"
          tooltip="系统会按此间隔检查是否有需要复习的内容"
        >
          <InputNumber min={5} max={1440} style={{ width: '100%' }} disabled={!settings.enabled} />
        </Form.Item>

        <Form.Item
          name="minDueCount"
          label="最少待复习数量"
          tooltip="只有当待复习节点数量达到此值时才会发送通知"
        >
          <InputNumber min={1} max={100} style={{ width: '100%' }} disabled={!settings.enabled} />
        </Form.Item>

        <Form.Item label="免打扰时间段" tooltip="在此时间段内不会发送通知">
          <Space>
            <Form.Item name="quietHoursStart" noStyle>
              <TimePicker format="HH:mm" placeholder="开始时间" disabled={!settings.enabled} />
            </Form.Item>
            <span>至</span>
            <Form.Item name="quietHoursEnd" noStyle>
              <TimePicker format="HH:mm" placeholder="结束时间" disabled={!settings.enabled} />
            </Form.Item>
          </Space>
        </Form.Item>

        <Form.Item name="soundEnabled" label="提示音" valuePropName="checked">
          <Switch
            checkedChildren={<SoundOutlined />}
            unCheckedChildren={<SoundOutlined />}
            disabled={!settings.enabled}
          />
        </Form.Item>
      </Form>

      <Divider>通知历史</Divider>

      {/* 通知记录 */}
      <div style={{ maxHeight: 300, overflowY: 'auto' }}>
        {records.length === 0 ? (
          <Empty description="暂无通知记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        ) : (
          <>
            <div style={{ marginBottom: 8, textAlign: 'right' }}>
              <Popconfirm
                title="确定要清空所有通知记录吗？"
                onConfirm={handleClearRecords}
                okText="确定"
                cancelText="取消"
              >
                <Button size="small" danger icon={<DeleteOutlined />}>
                  清空记录
                </Button>
              </Popconfirm>
            </div>
            <List
              size="small"
              dataSource={records}
              renderItem={(record) => (
                <List.Item
                  extra={
                    record.clicked && (
                      <Tag icon={<CheckCircleOutlined />} color="success">
                        已查看
                      </Tag>
                    )
                  }
                >
                  <List.Item.Meta
                    avatar={<ClockCircleOutlined style={{ fontSize: 20, color: '#1890ff' }} />}
                    title={
                      <Space>
                        {record.title}
                        {record.dueCount && (
                          <Tag color="orange">{record.dueCount} 个待复习</Tag>
                        )}
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size={0}>
                        <span>{record.body}</span>
                        <span style={{ fontSize: 12, color: '#999' }}>
                          {formatTimestamp(record.timestamp)}
                        </span>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </>
        )}
      </div>
    </Modal>
  );
};

export default NotificationSettingsModal;

