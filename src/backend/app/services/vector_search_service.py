"""
向量相似度搜索服务
基于 PgVector 实现语义搜索
"""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.memory_node import MemoryNode
from app.services.ai_service import ai_service


class VectorSearchService:
    """向量搜索服务"""
    
    async def search_similar_nodes(
        self,
        db: AsyncSession,
        query_text: str,
        graph_id: Optional[UUID] = None,
        node_type: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[MemoryNode, float]]:
        """
        基于文本查询搜索相似节点
        
        Args:
            db: 数据库会话
            query_text: 查询文本
            graph_id: 限制在特定知识图谱（可选）
            node_type: 限制节点类型（可选）
            limit: 返回结果数量
            similarity_threshold: 相似度阈值（0-1）
            
        Returns:
            (节点, 相似度分数) 元组列表，按相似度降序排列
        """
        # 生成查询文本的向量嵌入
        try:
            query_embedding = await ai_service.generate_embedding(query_text)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"生成查询向量失败: {str(e)}"
            )
        
        # 构建查询
        query = select(
            MemoryNode,
            # 使用余弦相似度（1 - 余弦距离）
            (1 - MemoryNode.content_embedding.cosine_distance(query_embedding)).label("similarity")
        ).where(
            MemoryNode.deleted_at.is_(None),
            MemoryNode.content_embedding.isnot(None)
        )
        
        # 添加过滤条件
        if graph_id:
            query = query.where(MemoryNode.graph_id == graph_id)
        
        if node_type:
            query = query.where(MemoryNode.node_type == node_type)
        
        # 添加相似度阈值过滤
        query = query.having(
            text(f"similarity >= {similarity_threshold}")
        )
        
        # 按相似度降序排列
        query = query.order_by(text("similarity DESC"))
        
        # 限制结果数量
        query = query.limit(limit)
        
        # 执行查询
        result = await db.execute(query)
        rows = result.all()
        
        return [(row[0], row[1]) for row in rows]
    
    async def find_similar_nodes_by_id(
        self,
        db: AsyncSession,
        node_id: UUID,
        graph_id: Optional[UUID] = None,
        node_type: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[MemoryNode, float]]:
        """
        查找与指定节点相似的其他节点
        
        Args:
            db: 数据库会话
            node_id: 参考节点ID
            graph_id: 限制在特定知识图谱（可选）
            node_type: 限制节点类型（可选）
            limit: 返回结果数量
            similarity_threshold: 相似度阈值（0-1）
            
        Returns:
            (节点, 相似度分数) 元组列表，按相似度降序排列
        """
        # 获取参考节点
        result = await db.execute(
            select(MemoryNode).where(
                MemoryNode.id == node_id,
                MemoryNode.deleted_at.is_(None)
            )
        )
        reference_node = result.scalar_one_or_none()
        
        if not reference_node:
            raise HTTPException(status_code=404, detail="参考节点不存在")
        
        if not reference_node.content_embedding:
            raise HTTPException(status_code=400, detail="参考节点没有向量嵌入")
        
        # 构建查询
        query = select(
            MemoryNode,
            (1 - MemoryNode.content_embedding.cosine_distance(
                reference_node.content_embedding
            )).label("similarity")
        ).where(
            MemoryNode.deleted_at.is_(None),
            MemoryNode.content_embedding.isnot(None),
            MemoryNode.id != node_id  # 排除自己
        )
        
        # 添加过滤条件
        if graph_id:
            query = query.where(MemoryNode.graph_id == graph_id)
        
        if node_type:
            query = query.where(MemoryNode.node_type == node_type)
        
        # 添加相似度阈值过滤
        query = query.having(
            text(f"similarity >= {similarity_threshold}")
        )
        
        # 按相似度降序排列
        query = query.order_by(text("similarity DESC"))
        
        # 限制结果数量
        query = query.limit(limit)
        
        # 执行查询
        result = await db.execute(query)
        rows = result.all()
        
        return [(row[0], row[1]) for row in rows]
    
    async def recommend_related_nodes(
        self,
        db: AsyncSession,
        node_id: UUID,
        limit: int = 5
    ) -> List[Tuple[MemoryNode, float]]:
        """
        为指定节点推荐相关节点（用于学习路径推荐）
        
        Args:
            db: 数据库会话
            node_id: 节点ID
            limit: 推荐数量
            
        Returns:
            (节点, 相似度分数) 元组列表
        """
        # 获取节点
        result = await db.execute(
            select(MemoryNode).where(
                MemoryNode.id == node_id,
                MemoryNode.deleted_at.is_(None)
            )
        )
        node = result.scalar_one_or_none()
        
        if not node:
            raise HTTPException(status_code=404, detail="节点不存在")
        
        # 在同一知识图谱中查找相似节点
        similar_nodes = await self.find_similar_nodes_by_id(
            db=db,
            node_id=node_id,
            graph_id=node.graph_id,
            limit=limit,
            similarity_threshold=0.6  # 降低阈值以获得更多推荐
        )
        
        return similar_nodes
    
    async def cluster_nodes_by_similarity(
        self,
        db: AsyncSession,
        graph_id: UUID,
        similarity_threshold: float = 0.8
    ) -> List[List[UUID]]:
        """
        基于相似度对节点进行聚类
        
        Args:
            db: 数据库会话
            graph_id: 知识图谱ID
            similarity_threshold: 相似度阈值
            
        Returns:
            节点ID聚类列表
        """
        # 获取图谱中所有有向量嵌入的节点
        result = await db.execute(
            select(MemoryNode).where(
                MemoryNode.graph_id == graph_id,
                MemoryNode.deleted_at.is_(None),
                MemoryNode.content_embedding.isnot(None)
            )
        )
        nodes = result.scalars().all()
        
        if not nodes:
            return []
        
        # 简单的聚类算法：贪心聚类
        clusters = []
        visited = set()
        
        for node in nodes:
            if node.id in visited:
                continue
            
            # 创建新簇
            cluster = [node.id]
            visited.add(node.id)
            
            # 查找相似节点
            similar_nodes = await self.find_similar_nodes_by_id(
                db=db,
                node_id=node.id,
                graph_id=graph_id,
                limit=100,  # 查找所有相似节点
                similarity_threshold=similarity_threshold
            )
            
            for similar_node, _ in similar_nodes:
                if similar_node.id not in visited:
                    cluster.append(similar_node.id)
                    visited.add(similar_node.id)
            
            if len(cluster) > 1:  # 只保留包含多个节点的簇
                clusters.append(cluster)
        
        return clusters
    
    async def update_node_embedding(
        self,
        db: AsyncSession,
        node_id: UUID
    ) -> MemoryNode:
        """
        更新节点的向量嵌入
        
        Args:
            db: 数据库会话
            node_id: 节点ID
            
        Returns:
            更新后的节点
        """
        # 获取节点
        result = await db.execute(
            select(MemoryNode).where(
                MemoryNode.id == node_id,
                MemoryNode.deleted_at.is_(None)
            )
        )
        node = result.scalar_one_or_none()
        
        if not node:
            raise HTTPException(status_code=404, detail="节点不存在")
        
        # 构建嵌入文本（标题 + 摘要 + 内容）
        embedding_text_parts = [node.title]
        
        if node.summary:
            embedding_text_parts.append(node.summary)
        
        # 从 content_data 中提取文本内容
        if isinstance(node.content_data, dict):
            if "question" in node.content_data:
                embedding_text_parts.append(node.content_data["question"])
            if "answer" in node.content_data:
                embedding_text_parts.append(node.content_data["answer"])
            if "content" in node.content_data:
                embedding_text_parts.append(str(node.content_data["content"]))
        
        embedding_text = " ".join(embedding_text_parts)
        
        # 生成向量嵌入
        try:
            embedding = await ai_service.generate_embedding(embedding_text)
            node.content_embedding = embedding
            await db.commit()
            await db.refresh(node)
            return node
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"更新向量嵌入失败: {str(e)}"
            )
    
    async def batch_update_embeddings(
        self,
        db: AsyncSession,
        graph_id: Optional[UUID] = None
    ) -> int:
        """
        批量更新节点的向量嵌入
        
        Args:
            db: 数据库会话
            graph_id: 限制在特定知识图谱（可选）
            
        Returns:
            更新的节点数量
        """
        # 查询需要更新的节点（没有向量嵌入的节点）
        query = select(MemoryNode).where(
            MemoryNode.deleted_at.is_(None),
            MemoryNode.content_embedding.is_(None)
        )
        
        if graph_id:
            query = query.where(MemoryNode.graph_id == graph_id)
        
        result = await db.execute(query)
        nodes = result.scalars().all()
        
        updated_count = 0
        for node in nodes:
            try:
                await self.update_node_embedding(db, node.id)
                updated_count += 1
            except Exception as e:
                print(f"更新节点 {node.id} 的向量嵌入失败: {str(e)}")
                continue
        
        return updated_count


# 创建全局向量搜索服务实例
vector_search_service = VectorSearchService()

