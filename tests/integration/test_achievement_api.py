"""
测试成就系统 API

运行前确保：
1. 后端服务已启动（http://localhost:8000）
2. 已有测试用户并登录获取 token
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"
# 替换为你的实际 token
TOKEN = "your_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def test_get_stats():
    """测试获取用户统计数据"""
    print("\n=== 测试获取用户统计数据 ===")
    response = requests.get(f"{BASE_URL}/achievements/stats", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"错误: {response.text}")


def test_get_level():
    """测试获取用户等级信息"""
    print("\n=== 测试获取用户等级信息 ===")
    response = requests.get(f"{BASE_URL}/achievements/level", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"错误: {response.text}")


def test_get_achievements():
    """测试获取成就列表"""
    print("\n=== 测试获取成就列表 ===")
    response = requests.get(f"{BASE_URL}/achievements/achievements", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"总成就数: {data['data']['total']}")
        print(f"已解锁: {data['data']['unlocked_count']}")
        print(f"完成度: {data['data']['progress']}%")
        print(f"\n已解锁成就:")
        for achievement in data['data']['unlocked']:
            print(f"  {achievement['icon']} {achievement['name']} - {achievement['description']}")
    else:
        print(f"错误: {response.text}")


def test_get_profile():
    """测试获取完整档案"""
    print("\n=== 测试获取完整档案 ===")
    response = requests.get(f"{BASE_URL}/achievements/profile", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        profile = data['data']
        
        print("\n【统计数据】")
        print(f"  总节点数: {profile['stats']['total_nodes']}")
        print(f"  已掌握: {profile['stats']['mastered_nodes']}")
        print(f"  总复习: {profile['stats']['total_reviews']}")
        print(f"  知识图谱: {profile['stats']['total_graphs']}")
        print(f"  连续学习: {profile['stats']['current_streak']} 天")
        
        print("\n【等级信息】")
        print(f"  当前等级: {profile['level']['level']}")
        print(f"  总经验值: {profile['level']['total_exp']}")
        print(f"  等级进度: {profile['level']['progress']}%")
        
        print("\n【成就信息】")
        print(f"  已解锁: {profile['achievements']['unlocked_count']}/{profile['achievements']['total']}")
        print(f"  完成度: {profile['achievements']['progress']}%")
    else:
        print(f"错误: {response.text}")


if __name__ == "__main__":
    print("=" * 60)
    print("成就系统 API 测试")
    print("=" * 60)
    
    if TOKEN == "your_token_here":
        print("\n⚠️  请先设置有效的 TOKEN")
        print("1. 登录获取 token")
        print("2. 将 token 替换到脚本中的 TOKEN 变量")
    else:
        test_get_stats()
        test_get_level()
        test_get_achievements()
        test_get_profile()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)

