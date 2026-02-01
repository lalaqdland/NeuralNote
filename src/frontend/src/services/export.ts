/**
 * 数据导出服务
 * 支持导出知识图谱和节点数据为 JSON、CSV、Markdown 格式
 */

import { KnowledgeGraph } from './knowledgeGraph';
import { MemoryNode } from './memoryNode';

export type ExportFormat = 'json' | 'csv' | 'markdown';

export interface ExportOptions {
  format: ExportFormat;
  includeRelations?: boolean; // 是否包含关联关系
  includeStats?: boolean; // 是否包含统计信息
  includeReviewHistory?: boolean; // 是否包含复习历史
}

export interface ExportData {
  graph: KnowledgeGraph;
  nodes: MemoryNode[];
  relations?: any[];
  stats?: any;
  exportTime: string;
}

class ExportService {
  /**
   * 导出为 JSON 格式
   */
  exportToJSON(data: ExportData): string {
    return JSON.stringify(data, null, 2);
  }

  /**
   * 导出为 CSV 格式
   */
  exportToCSV(data: ExportData): string {
    const { nodes } = data;
    
    // CSV 表头
    const headers = [
      'ID',
      '标题',
      '类型',
      '掌握度',
      '复习次数',
      '上次复习时间',
      '下次复习时间',
      '创建时间',
      '标签',
    ];

    // CSV 数据行
    const rows = nodes.map((node) => [
      node.id,
      this.escapeCSV(node.title),
      node.node_type,
      node.mastery_level,
      node.review_count,
      node.last_reviewed_at || '',
      node.next_review_at || '',
      node.created_at,
      node.tags?.join(';') || '',
    ]);

    // 组合 CSV
    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n');

    return csvContent;
  }

  /**
   * 导出为 Markdown 格式
   */
  exportToMarkdown(data: ExportData): string {
    const { graph, nodes, relations, stats, exportTime } = data;

    let markdown = '';

    // 标题
    markdown += `# ${graph.name}\n\n`;
    markdown += `> ${graph.description || '暂无描述'}\n\n`;

    // 元信息
    markdown += `## 📊 图谱信息\n\n`;
    markdown += `- **创建时间**: ${new Date(graph.created_at).toLocaleString('zh-CN')}\n`;
    markdown += `- **更新时间**: ${new Date(graph.updated_at).toLocaleString('zh-CN')}\n`;
    markdown += `- **节点数量**: ${nodes.length}\n`;
    markdown += `- **导出时间**: ${new Date(exportTime).toLocaleString('zh-CN')}\n\n`;

    // 统计信息
    if (stats) {
      markdown += `## 📈 学习统计\n\n`;
      markdown += `- **总节点数**: ${stats.total_nodes}\n`;
      markdown += `- **已掌握**: ${stats.mastered_nodes}\n`;
      markdown += `- **平均掌握度**: ${(stats.average_mastery * 100).toFixed(1)}%\n`;
      markdown += `- **今日复习**: ${stats.reviewed_today}\n`;
      markdown += `- **待复习**: ${stats.due_today}\n`;
      markdown += `- **连续打卡**: ${stats.streak_days} 天\n\n`;
    }

    // 节点列表（按类型分组）
    markdown += `## 📚 知识节点\n\n`;

    const nodesByType = this.groupNodesByType(nodes);
    
    for (const [type, typeNodes] of Object.entries(nodesByType)) {
      markdown += `### ${this.getTypeLabel(type)}\n\n`;
      
      for (const node of typeNodes) {
        markdown += `#### ${node.title}\n\n`;
        
        // 节点元信息
        markdown += `- **掌握度**: ${this.getMasteryLabel(node.mastery_level)} (${(node.mastery_level * 100).toFixed(0)}%)\n`;
        markdown += `- **复习次数**: ${node.review_count}\n`;
        if (node.last_reviewed_at) {
          markdown += `- **上次复习**: ${new Date(node.last_reviewed_at).toLocaleString('zh-CN')}\n`;
        }
        if (node.next_review_at) {
          markdown += `- **下次复习**: ${new Date(node.next_review_at).toLocaleString('zh-CN')}\n`;
        }
        if (node.tags && node.tags.length > 0) {
          markdown += `- **标签**: ${node.tags.map(t => `\`${t}\``).join(', ')}\n`;
        }
        markdown += '\n';

        // 节点内容
        if (node.content_data) {
          if (node.node_type === 'QUESTION') {
            // 题目类型
            if (node.content_data.question) {
              markdown += `**题目**:\n\n${node.content_data.question}\n\n`;
            }
            if (node.content_data.answer) {
              markdown += `**答案**:\n\n${node.content_data.answer}\n\n`;
            }
            if (node.content_data.explanation) {
              markdown += `**解析**:\n\n${node.content_data.explanation}\n\n`;
            }
            if (node.content_data.knowledge_points && node.content_data.knowledge_points.length > 0) {
              markdown += `**知识点**:\n\n`;
              node.content_data.knowledge_points.forEach((kp: string) => {
                markdown += `- ${kp}\n`;
              });
              markdown += '\n';
            }
          } else if (node.node_type === 'CONCEPT') {
            // 概念类型
            if (node.content_data.definition) {
              markdown += `**定义**:\n\n${node.content_data.definition}\n\n`;
            }
            if (node.content_data.examples) {
              markdown += `**示例**:\n\n${node.content_data.examples}\n\n`;
            }
          } else if (node.node_type === 'NOTE') {
            // 笔记类型
            if (node.content_data.content) {
              markdown += `${node.content_data.content}\n\n`;
            }
          }
        }

        markdown += '---\n\n';
      }
    }

    // 关联关系
    if (relations && relations.length > 0) {
      markdown += `## 🔗 关联关系\n\n`;
      markdown += `| 源节点 | 关系类型 | 目标节点 | 强度 |\n`;
      markdown += `|--------|----------|----------|------|\n`;
      
      for (const rel of relations) {
        const sourceNode = nodes.find(n => n.id === rel.source_id);
        const targetNode = nodes.find(n => n.id === rel.target_id);
        markdown += `| ${sourceNode?.title || rel.source_id} | ${this.getRelationTypeLabel(rel.relation_type)} | ${targetNode?.title || rel.target_id} | ${rel.strength || 1.0} |\n`;
      }
      markdown += '\n';
    }

    return markdown;
  }

  /**
   * 下载文件
   */
  downloadFile(content: string, filename: string, mimeType: string): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * 导出数据
   */
  async exportData(data: ExportData, options: ExportOptions): Promise<void> {
    const { format } = options;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const graphName = data.graph.name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_');

    let content: string;
    let filename: string;
    let mimeType: string;

    switch (format) {
      case 'json':
        content = this.exportToJSON(data);
        filename = `${graphName}_${timestamp}.json`;
        mimeType = 'application/json';
        break;

      case 'csv':
        content = this.exportToCSV(data);
        filename = `${graphName}_${timestamp}.csv`;
        mimeType = 'text/csv;charset=utf-8;';
        break;

      case 'markdown':
        content = this.exportToMarkdown(data);
        filename = `${graphName}_${timestamp}.md`;
        mimeType = 'text/markdown;charset=utf-8;';
        break;

      default:
        throw new Error(`不支持的导出格式: ${format}`);
    }

    this.downloadFile(content, filename, mimeType);
  }

  /**
   * 转义 CSV 字段
   */
  private escapeCSV(value: any): string {
    if (value == null) return '';
    const str = String(value);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  }

  /**
   * 按类型分组节点
   */
  private groupNodesByType(nodes: MemoryNode[]): Record<string, MemoryNode[]> {
    const groups: Record<string, MemoryNode[]> = {};
    
    for (const node of nodes) {
      const type = node.node_type;
      if (!groups[type]) {
        groups[type] = [];
      }
      groups[type].push(node);
    }

    return groups;
  }

  /**
   * 获取类型标签
   */
  private getTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      CONCEPT: '💡 概念',
      QUESTION: '❓ 题目',
      NOTE: '📝 笔记',
      RESOURCE: '📚 资源',
    };
    return labels[type] || type;
  }

  /**
   * 获取掌握度标签
   */
  private getMasteryLabel(level: number): string {
    if (level >= 0.8) return '✅ 已掌握';
    if (level >= 0.6) return '🟢 熟练';
    if (level >= 0.4) return '🟡 一般';
    if (level >= 0.2) return '🟠 薄弱';
    return '🔴 未掌握';
  }

  /**
   * 获取关系类型标签
   */
  private getRelationTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      prerequisite: '前置知识',
      related: '相关',
      derived: '派生',
      example: '示例',
      application: '应用',
      contrast: '对比',
    };
    return labels[type] || type;
  }
}

export const exportService = new ExportService();

