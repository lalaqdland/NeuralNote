"""
记忆节点接口测试
测试记忆节点的 CRUD 操作和关联管理
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import KnowledgeGraph, MemoryNode
from tests.conftest import TEST_NODE_DATA


class TestNodeCreation:
    """记忆节点创建测试"""

    @pytest.mark.asyncio
    async def test_create_node_success(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试成功创建节点"""
        node_data = {**TEST_NODE_DATA, "graph_id": str(test_graph.id)}
        
        response = await client.post(
            "/api/v1/nodes/",
            headers=auth_headers,
            json=node_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == TEST_NODE_DATA["title"]
        assert data["node_type"] == TEST_NODE_DATA["node_type"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_node_no_auth(self, client: AsyncClient, test_graph: KnowledgeGraph):
        """测试未认证创建节点"""
        node_data = {**TEST_NODE_DATA, "graph_id": str(test_graph.id)}
        
        response = await client.post(
            "/api/v1/nodes/",
            json=node_data
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_node_invalid_graph(self, client: AsyncClient, auth_headers: dict):
        """测试使用无效的图谱ID"""
        import uuid
        fake_graph_id = str(uuid.uuid4())
        node_data = {**TEST_NODE_DATA, "graph_id": fake_graph_id}
        
        response = await client.post(
            "/api/v1/nodes/",
            headers=auth_headers,
            json=node_data
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_node_different_types(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试创建不同类型的节点"""
        node_types = ["CONCEPT", "QUESTION", "FORMULA", "THEOREM"]
        
        for node_type in node_types:
            node_data = {
                "graph_id": str(test_graph.id),
                "node_type": node_type,
                "title": f"测试{node_type}节点",
                "summary": f"这是一个{node_type}类型的节点",
                "content_data": {"type": node_type}
            }
            
            response = await client.post(
                "/api/v1/nodes/",
                headers=auth_headers,
                json=node_data
            )
            
            assert response.status_code == 201
            assert response.json()["node_type"] == node_type


class TestNodeRetrieval:
    """记忆节点查询测试"""

    @pytest.mark.asyncio
    async def test_list_nodes(self, client: AsyncClient, auth_headers: dict, test_node: MemoryNode):
        """测试获取节点列表"""
        response = await client.get(
            "/api/v1/nodes/",
            headers=auth_headers,
            params={"graph_id": str(test_node.graph_id), "page": 1, "page_size": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) > 0

    @pytest.mark.asyncio
    async def test_get_node_detail(self, client: AsyncClient, auth_headers: dict, test_node: MemoryNode):
        """测试获取节点详情"""
        response = await client.get(
            f"/api/v1/nodes/{test_node.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_node.id)
        assert data["title"] == test_node.title

    @pytest.mark.asyncio
    async def test_get_node_not_found(self, client: AsyncClient, auth_headers: dict):
        """测试获取不存在的节点"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.get(
            f"/api/v1/nodes/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_filter_nodes_by_type(self, client: AsyncClient, auth_headers: dict, test_node: MemoryNode):
        """测试按类型筛选节点"""
        response = await client.get(
            "/api/v1/nodes/",
            headers=auth_headers,
            params={
                "graph_id": str(test_node.graph_id),
                "node_type": test_node.node_type
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(item["node_type"] == test_node.node_type for item in data["items"])


class TestNodeUpdate:
    """记忆节点更新测试"""

    @pytest.mark.asyncio
    async def test_update_node_success(self, client: AsyncClient, auth_headers: dict, test_node: MemoryNode):
        """测试成功更新节点"""
        update_data = {
            "title": "更新后的标题",
            "summary": "更新后的摘要",
            "content_data": {"updated": True}
        }
        
        response = await client.put(
            f"/api/v1/nodes/{test_node.id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["summary"] == update_data["summary"]

    @pytest.mark.asyncio
    async def test_update_node_not_found(self, client: AsyncClient, auth_headers: dict):
        """测试更新不存在的节点"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.put(
            f"/api/v1/nodes/{fake_id}",
            headers=auth_headers,
            json={"title": "新标题"}
        )
        
        assert response.status_code == 404


class TestNodeDeletion:
    """记忆节点删除测试"""

    @pytest.mark.asyncio
    async def test_delete_node_success(self, client: AsyncClient, auth_headers: dict, test_node: MemoryNode):
        """测试成功删除节点"""
        response = await client.delete(
            f"/api/v1/nodes/{test_node.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # 验证节点已被删除
        get_response = await client.get(
            f"/api/v1/nodes/{test_node.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_node_not_found(self, client: AsyncClient, auth_headers: dict):
        """测试删除不存在的节点"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.delete(
            f"/api/v1/nodes/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestNodeRelations:
    """节点关联测试"""

    @pytest.mark.asyncio
    async def test_create_relation(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试创建节点关联"""
        # 创建两个节点
        node1_data = {**TEST_NODE_DATA, "graph_id": str(test_graph.id), "title": "节点1"}
        node2_data = {**TEST_NODE_DATA, "graph_id": str(test_graph.id), "title": "节点2"}
        
        node1_response = await client.post("/api/v1/nodes/", headers=auth_headers, json=node1_data)
        node2_response = await client.post("/api/v1/nodes/", headers=auth_headers, json=node2_data)
        
        node1_id = node1_response.json()["id"]
        node2_id = node2_response.json()["id"]
        
        # 创建关联
        relation_data = {
            "source_node_id": node1_id,
            "target_node_id": node2_id,
            "relation_type": "RELATED",
            "strength": 80
        }
        
        response = await client.post(
            f"/api/v1/nodes/{node1_id}/relations",
            headers=auth_headers,
            json=relation_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["source_id"] == node1_id
        assert data["target_id"] == node2_id
        assert data["relation_type"] == "RELATED"

    @pytest.mark.asyncio
    async def test_get_node_relations(self, client: AsyncClient, auth_headers: dict, test_node: MemoryNode):
        """测试获取节点的所有关联"""
        response = await client.get(
            f"/api/v1/nodes/{test_node.id}/relations",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_delete_relation(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试删除节点关联"""
        # 创建两个节点和一个关联
        node1_data = {**TEST_NODE_DATA, "graph_id": str(test_graph.id), "title": "节点A"}
        node2_data = {**TEST_NODE_DATA, "graph_id": str(test_graph.id), "title": "节点B"}
        
        node1_response = await client.post("/api/v1/nodes/", headers=auth_headers, json=node1_data)
        node2_response = await client.post("/api/v1/nodes/", headers=auth_headers, json=node2_data)
        
        node1_id = node1_response.json()["id"]
        node2_id = node2_response.json()["id"]
        
        relation_data = {
            "source_node_id": node1_id,
            "target_node_id": node2_id,
            "relation_type": "RELATED",
            "strength": 80
        }
        
        relation_response = await client.post(
            f"/api/v1/nodes/{node1_id}/relations",
            headers=auth_headers,
            json=relation_data
        )
        relation_id = relation_response.json()["id"]
        
        # 删除关联（正确的路径是 /api/v1/nodes/relations/{relation_id}）
        delete_response = await client.delete(
            f"/api/v1/nodes/relations/{relation_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code == 204

