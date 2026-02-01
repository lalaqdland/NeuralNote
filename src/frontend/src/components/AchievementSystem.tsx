/**
 * 成就系统组件
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Progress,
  Tag,
  Tabs,
  Empty,
  Spin,
  Statistic,
  Badge,
  Tooltip,
  Space,
  Divider,
  message,
} from 'antd';
import {
  TrophyOutlined,
  FireOutlined,
  StarOutlined,
  RocketOutlined,
  CrownOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import {
  getUserProfile,
  UserProfile,
  Achievement,
  getLevelTitle,
  getLevelColor,
  getAchievementCategoryName,
  getAchievementCategoryColor,
} from '../services/achievement';

const { TabPane } = Tabs;

const AchievementSystem: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = await getUserProfile();
      setProfile(data);
    } catch (error) {
      message.error('加载成就数据失败');
      console.error('加载成就数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (!profile) {
    return <Empty description="暂无数据" />;
  }

  const { stats, level, achievements } = profile;

  // 按分类分组成就
  const achievementsByCategory: Record<string, Achievement[]> = {};
  [...achievements.unlocked, ...achievements.locked].forEach((achievement) => {
    if (!achievementsByCategory[achievement.category]) {
      achievementsByCategory[achievement.category] = [];
    }
    achievementsByCategory[achievement.category].push(achievement);
  });

  return (
    <div style={{ padding: '24px' }}>
      {/* 等级信息卡片 */}
      <Card
        style={{
          marginBottom: 24,
          background: `linear-gradient(135deg, ${getLevelColor(level.level)}15 0%, ${getLevelColor(level.level)}05 100%)`,
          border: `2px solid ${getLevelColor(level.level)}`,
        }}
      >
        <Row gutter={24} align="middle">
          <Col xs={24} md={8} style={{ textAlign: 'center' }}>
            <div
              style={{
                fontSize: 72,
                fontWeight: 'bold',
                color: getLevelColor(level.level),
                lineHeight: 1,
              }}
            >
              {level.level}
            </div>
            <div style={{ fontSize: 20, fontWeight: 500, marginTop: 8 }}>
              {getLevelTitle(level.level)}
            </div>
            <Tag
              color={getLevelColor(level.level)}
              style={{ marginTop: 8, fontSize: 14 }}
            >
              <ThunderboltOutlined /> {level.total_exp} EXP
            </Tag>
          </Col>

          <Col xs={24} md={16}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8, fontSize: 16 }}>
                <span style={{ fontWeight: 500 }}>等级进度</span>
                <span style={{ float: 'right', color: '#8c8c8c' }}>
                  {level.exp_in_level} / {level.exp_to_next} EXP
                </span>
              </div>
              <Progress
                percent={level.progress}
                strokeColor={getLevelColor(level.level)}
                strokeWidth={12}
                format={(percent) => `${percent?.toFixed(1)}%`}
              />
            </div>

            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="当前等级"
                  value={level.level}
                  prefix={<CrownOutlined />}
                  valueStyle={{ color: getLevelColor(level.level) }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="下一等级"
                  value={level.level < 20 ? level.level + 1 : 'MAX'}
                  prefix={<RocketOutlined />}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="还需经验"
                  value={level.level < 20 ? level.exp_to_next - level.exp_in_level : 0}
                  prefix={<ThunderboltOutlined />}
                  valueStyle={{ fontSize: 20 }}
                />
              </Col>
            </Row>
          </Col>
        </Row>
      </Card>

      {/* 统计数据卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="总节点数"
              value={stats.total_nodes}
              prefix={<StarOutlined style={{ color: '#1890ff' }} />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="已掌握"
              value={stats.mastered_nodes}
              prefix={<TrophyOutlined style={{ color: '#52c41a' }} />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="总复习"
              value={stats.total_reviews}
              prefix={<FireOutlined style={{ color: '#faad14' }} />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="连续学习"
              value={stats.current_streak}
              suffix="天"
              prefix={<FireOutlined style={{ color: '#ff4d4f' }} />}
            />
          </Card>
        </Col>
      </Row>

      {/* 成就列表 */}
      <Card
        title={
          <Space>
            <TrophyOutlined />
            <span>成就徽章</span>
            <Badge
              count={achievements.unlocked_count}
              style={{ backgroundColor: '#52c41a' }}
            />
          </Space>
        }
        extra={
          <Tag color="blue">
            完成度: {achievements.progress.toFixed(1)}%
          </Tag>
        }
      >
        <div style={{ marginBottom: 16 }}>
          <Progress
            percent={achievements.progress}
            strokeColor={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
            format={(percent) =>
              `${achievements.unlocked_count} / ${achievements.total}`
            }
          />
        </div>

        <Tabs defaultActiveKey="all">
          <TabPane tab="全部成就" key="all">
            <AchievementList achievements={[...achievements.unlocked, ...achievements.locked]} />
          </TabPane>
          <TabPane
            tab={
              <Badge count={achievements.unlocked_count} offset={[10, 0]}>
                已解锁
              </Badge>
            }
            key="unlocked"
          >
            {achievements.unlocked.length > 0 ? (
              <AchievementList achievements={achievements.unlocked} />
            ) : (
              <Empty description="还没有解锁任何成就" />
            )}
          </TabPane>
          {Object.keys(achievementsByCategory).map((category) => (
            <TabPane
              tab={getAchievementCategoryName(category)}
              key={category}
            >
              <AchievementList achievements={achievementsByCategory[category]} />
            </TabPane>
          ))}
        </Tabs>
      </Card>
    </div>
  );
};

// 成就列表组件
const AchievementList: React.FC<{ achievements: Achievement[] }> = ({
  achievements,
}) => {
  if (achievements.length === 0) {
    return <Empty description="暂无成就" />;
  }

  return (
    <Row gutter={[16, 16]}>
      {achievements.map((achievement) => (
        <Col xs={24} sm={12} md={8} lg={6} key={achievement.id}>
          <Tooltip title={achievement.description}>
            <Card
              hoverable
              style={{
                opacity: achievement.unlocked ? 1 : 0.5,
                border: achievement.unlocked
                  ? `2px solid ${getAchievementCategoryColor(achievement.category)}`
                  : '1px solid #d9d9d9',
                position: 'relative',
              }}
            >
              {achievement.unlocked && (
                <div
                  style={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    fontSize: 20,
                  }}
                >
                  ✓
                </div>
              )}
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 48, marginBottom: 8 }}>
                  {achievement.icon}
                </div>
                <div style={{ fontWeight: 500, fontSize: 16, marginBottom: 4 }}>
                  {achievement.name}
                </div>
                <div style={{ fontSize: 12, color: '#8c8c8c' }}>
                  {achievement.description}
                </div>
                <Tag
                  color={getAchievementCategoryColor(achievement.category)}
                  style={{ marginTop: 8 }}
                >
                  {getAchievementCategoryName(achievement.category)}
                </Tag>
              </div>
            </Card>
          </Tooltip>
        </Col>
      ))}
    </Row>
  );
};

export default AchievementSystem;

