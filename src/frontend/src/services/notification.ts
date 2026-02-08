/**
 * 通知服务
 * 负责浏览器通知、复习提醒等功能
 */

import { reviewService } from './review';
import { UUID } from './knowledgeGraph';

export interface NotificationSettings {
  enabled: boolean;
  checkInterval: number; // 检查间隔（分钟）
  quietHoursStart?: string; // 免打扰开始时间 (HH:mm)
  quietHoursEnd?: string; // 免打扰结束时间 (HH:mm)
  minDueCount: number; // 最少待复习数量才提醒
  soundEnabled: boolean; // 是否播放提示音
}

export interface NotificationRecord {
  id: string;
  title: string;
  body: string;
  timestamp: number;
  graphId?: UUID;
  dueCount?: number;
  clicked: boolean;
}

const STORAGE_KEY_SETTINGS = 'neuralnote_notification_settings';
const STORAGE_KEY_RECORDS = 'neuralnote_notification_records';
const DEFAULT_SETTINGS: NotificationSettings = {
  enabled: false,
  checkInterval: 60, // 每小时检查一次
  quietHoursStart: '22:00',
  quietHoursEnd: '08:00',
  minDueCount: 5,
  soundEnabled: true,
};

class NotificationService {
  private checkTimer: number | null = null;
  private settings: NotificationSettings;
  private records: NotificationRecord[] = [];

  constructor() {
    this.settings = this.loadSettings();
    this.records = this.loadRecords();
  }

  /**
   * 请求通知权限
   */
  async requestPermission(): Promise<boolean> {
    if (!('Notification' in window)) {
      console.warn('浏览器不支持通知功能');
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }

    return false;
  }

  /**
   * 检查通知权限状态
   */
  checkPermission(): NotificationPermission | 'unsupported' {
    if (!('Notification' in window)) {
      return 'unsupported';
    }
    return Notification.permission;
  }

  /**
   * 发送桌面通知
   */
  async sendNotification(
    title: string,
    options?: NotificationOptions & { graphId?: UUID; dueCount?: number }
  ): Promise<void> {
    const permission = await this.requestPermission();
    if (!permission) {
      console.warn('没有通知权限');
      return;
    }

    const notification = new Notification(title, {
      icon: '/logo.png',
      badge: '/logo.png',
      ...options,
    });

    // 记录通知
    const record: NotificationRecord = {
      id: Date.now().toString(),
      title,
      body: options?.body || '',
      timestamp: Date.now(),
      graphId: options?.graphId,
      dueCount: options?.dueCount,
      clicked: false,
    };
    this.addRecord(record);

    // 点击通知时的处理
    notification.onclick = () => {
      window.focus();
      this.markRecordAsClicked(record.id);
      // 跳转到复习页面
      if (options?.graphId) {
        window.location.href = `/review?graph=${options.graphId}`;
      } else {
        window.location.href = '/review';
      }
      notification.close();
    };

    // 播放提示音
    if (this.settings.soundEnabled) {
      this.playNotificationSound();
    }
  }

  /**
   * 播放通知提示音
   */
  private playNotificationSound(): void {
    try {
      const audio = new Audio('/notification.mp3');
      audio.volume = 0.5;
      audio.play().catch((err) => console.warn('播放提示音失败:', err));
    } catch (error) {
      console.warn('播放提示音失败:', error);
    }
  }

  /**
   * 检查是否在免打扰时间段
   */
  private isInQuietHours(): boolean {
    if (!this.settings.quietHoursStart || !this.settings.quietHoursEnd) {
      return false;
    }

    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();

    const [startHour, startMin] = this.settings.quietHoursStart.split(':').map(Number);
    const [endHour, endMin] = this.settings.quietHoursEnd.split(':').map(Number);
    const startTime = startHour * 60 + startMin;
    const endTime = endHour * 60 + endMin;

    // 处理跨天的情况（如 22:00 - 08:00）
    if (startTime > endTime) {
      return currentTime >= startTime || currentTime < endTime;
    } else {
      return currentTime >= startTime && currentTime < endTime;
    }
  }

  /**
   * 检查待复习节点并发送通知
   */
  async checkAndNotify(graphId: UUID): Promise<void> {
    if (!this.settings.enabled) {
      return;
    }

    if (this.isInQuietHours()) {
      console.log('当前处于免打扰时间段');
      return;
    }

    try {
      const stats = await reviewService.getReviewStats(graphId);
      const dueCount = stats.due_today;

      if (dueCount >= this.settings.minDueCount) {
        await this.sendNotification('复习提醒', {
          body: `您有 ${dueCount} 个知识点需要复习，点击开始复习`,
          tag: 'review-reminder',
          requireInteraction: false,
          graphId,
          dueCount,
        });
      }
    } catch (error) {
      console.error('检查复习提醒失败:', error);
    }
  }

  /**
   * 启动定时检查
   */
  startPeriodicCheck(graphId: UUID): void {
    this.stopPeriodicCheck();

    if (!this.settings.enabled) {
      return;
    }

    // 立即检查一次
    this.checkAndNotify(graphId);

    // 设置定时检查
    const intervalMs = this.settings.checkInterval * 60 * 1000;
    this.checkTimer = setInterval(() => {
      this.checkAndNotify(graphId);
    }, intervalMs);

    console.log(`已启动定时检查，间隔 ${this.settings.checkInterval} 分钟`);
  }

  /**
   * 停止定时检查
   */
  stopPeriodicCheck(): void {
    if (this.checkTimer) {
      clearInterval(this.checkTimer);
      this.checkTimer = null;
      console.log('已停止定时检查');
    }
  }

  /**
   * 获取通知设置
   */
  getSettings(): NotificationSettings {
    return { ...this.settings };
  }

  /**
   * 更新通知设置
   */
  updateSettings(settings: Partial<NotificationSettings>): void {
    this.settings = { ...this.settings, ...settings };
    this.saveSettings();
  }

  /**
   * 加载设置
   */
  private loadSettings(): NotificationSettings {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_SETTINGS);
      if (saved) {
        return { ...DEFAULT_SETTINGS, ...JSON.parse(saved) };
      }
    } catch (error) {
      console.error('加载通知设置失败:', error);
    }
    return DEFAULT_SETTINGS;
  }

  /**
   * 保存设置
   */
  private saveSettings(): void {
    try {
      localStorage.setItem(STORAGE_KEY_SETTINGS, JSON.stringify(this.settings));
    } catch (error) {
      console.error('保存通知设置失败:', error);
    }
  }

  /**
   * 获取通知记录
   */
  getRecords(): NotificationRecord[] {
    return [...this.records];
  }

  /**
   * 添加通知记录
   */
  private addRecord(record: NotificationRecord): void {
    this.records.unshift(record);
    // 只保留最近100条
    if (this.records.length > 100) {
      this.records = this.records.slice(0, 100);
    }
    this.saveRecords();
  }

  /**
   * 标记通知为已点击
   */
  private markRecordAsClicked(id: string): void {
    const record = this.records.find((r) => r.id === id);
    if (record) {
      record.clicked = true;
      this.saveRecords();
    }
  }

  /**
   * 清空通知记录
   */
  clearRecords(): void {
    this.records = [];
    this.saveRecords();
  }

  /**
   * 加载通知记录
   */
  private loadRecords(): NotificationRecord[] {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_RECORDS);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (error) {
      console.error('加载通知记录失败:', error);
    }
    return [];
  }

  /**
   * 保存通知记录
   */
  private saveRecords(): void {
    try {
      localStorage.setItem(STORAGE_KEY_RECORDS, JSON.stringify(this.records));
    } catch (error) {
      console.error('保存通知记录失败:', error);
    }
  }

  /**
   * 测试通知
   */
  async testNotification(): Promise<void> {
    await this.sendNotification('测试通知', {
      body: '这是一条测试通知，如果您看到了这条消息，说明通知功能正常工作',
      tag: 'test-notification',
    });
  }
}

export const notificationService = new NotificationService();

