"""
知识图谱接口测试
测试知识图谱的 CRUD 操作
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, KnowledgeGraph
from tests.conftest import TEST_GRAPH_DATA


class TestGraphCreation:
    """知识图谱创建测试"""

    @pytest.mark.asyncio
    async def test_create_graph_success(self, client: AsyncClient, auth_headers: dict):
        """测试成功创建知识图谱"""
        response = await client.post(
            "/api/v1/graphs/",
            headers=auth_headers,
            json=TEST_GRAPH_DATA
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == TEST_GRAPH_DATA["name"]
        assert data["description"] == TEST_GRAPH_DATA["description"]
        assert data["subject"] == TEST_GRAPH_DATA["subject"]
        assert "id" in data
        assert data["node_count"] == 0

    @pytest.mark.asyncio
    async def test_create_graph_no_auth(self, client: AsyncClient):
        """测试未认证创建图谱"""
        response = await client.post(
            "/api/v1/graphs/",
            json=TEST_GRAPH_DATA
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_graph_missing_fields(self, client: AsyncClient, auth_headers: dict):
        """测试缺少必填字段"""
        # 只有 name 是必填的，其他字段都是可选的
        # 所以只提供 name 应该成功创建
        response = await client.post(
            "/api/v1/graphs/",
            headers=auth_headers,
            json={"name": "测试图谱"}
        )
        
        # 应该成功创建（201）而不是验证失败（422）
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "测试图谱"
        
        # 测试真正缺少必填字段的情况（不提供 name）
        response2 = await client.post(
            "/api/v1/graphs/",
            headers=auth_headers,
            json={"description": "只有描述"}
        )
        
        assert response2.status_code == 422


class TestGraphRetrieval:
    """知识图谱查询测试"""

    @pytest.mark.asyncio
    async def test_list_graphs(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试获取图谱列表"""
        response = await client.get(
            "/api/v1/graphs/",
            headers=auth_headers,
            params={"page": 1, "page_size": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert len(data["items"]) > 0

    @pytest.mark.asyncio
    async def test_list_graphs_pagination(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试分页功能"""
        response = await client.get(
            "/api/v1/graphs/",
            headers=auth_headers,
            params={"page": 1, "page_size": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5

    @pytest.mark.asyncio
    async def test_get_graph_detail(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试获取图谱详情"""
        response = await client.get(
            f"/api/v1/graphs/{test_graph.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_graph.id)
        assert data["name"] == test_graph.name

    @pytest.mark.asyncio
    async def test_get_graph_not_found(self, client: AsyncClient, auth_headers: dict):
        """测试获取不存在的图谱"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.get(
            f"/api/v1/graphs/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_graph_stats(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试获取图谱统计信息"""
        response = await client.get(
            f"/api/v1/graphs/{test_graph.id}/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_nodes" in data
        assert "total_relations" in data
        assert "total_tags" in data


class TestGraphUpdate:
    """知识图谱更新测试"""

    @pytest.mark.asyncio
    async def test_update_graph_success(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试成功更新图谱"""
        update_data = {
            "name": "更新后的图谱名称",
            "description": "更新后的描述"
        }
        
        response = await client.put(
            f"/api/v1/graphs/{test_graph.id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_update_graph_not_found(self, client: AsyncClient, auth_headers: dict):
        """测试更新不存在的图谱"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.put(
            f"/api/v1/graphs/{fake_id}",
            headers=auth_headers,
            json={"name": "新名称"}
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_graph_partial(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试部分更新图谱"""
        response = await client.put(
            f"/api/v1/graphs/{test_graph.id}",
            headers=auth_headers,
            json={"name": "仅更新名称"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "仅更新名称"
        assert data["description"] == test_graph.description  # 保持不变


class TestGraphDeletion:
    """知识图谱删除测试"""

    @pytest.mark.asyncio
    async def test_delete_graph_success(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试成功删除图谱"""
        response = await client.delete(
            f"/api/v1/graphs/{test_graph.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # 验证图谱已被删除
        get_response = await client.get(
            f"/api/v1/graphs/{test_graph.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_graph_not_found(self, client: AsyncClient, auth_headers: dict):
        """测试删除不存在的图谱"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.delete(
            f"/api/v1/graphs/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestGraphFiltering:
    """知识图谱筛选测试"""

    @pytest.mark.asyncio
    async def test_filter_by_subject(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试按学科筛选"""
        response = await client.get(
            "/api/v1/graphs/",
            headers=auth_headers,
            params={"subject": test_graph.subject}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(item["subject"] == test_graph.subject for item in data["items"])

    @pytest.mark.asyncio
    async def test_search_by_name(self, client: AsyncClient, auth_headers: dict, test_graph: KnowledgeGraph):
        """测试按名称搜索"""
        response = await client.get(
            "/api/v1/graphs/",
            headers=auth_headers,
            params={"search": test_graph.name[:3]}  # 搜索名称的前几个字符
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0

