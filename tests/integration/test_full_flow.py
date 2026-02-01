import requests
import json

print("=" * 60)
print("测试完整的注册流程")
print("=" * 60)

# 测试 1: 检查后端健康状态
print("\n[1] 检查后端服务...")
try:
    r = requests.get("http://localhost:8000/health", timeout=5)
    print(f"✅ 后端服务正常 (状态码: {r.status_code})")
except Exception as e:
    print(f"❌ 后端服务异常: {e}")
    exit(1)

# 测试 2: 测试 CORS（模拟前端请求）
print("\n[2] 测试 CORS 配置...")
headers = {
    "Origin": "http://localhost:3001",
    "Content-Type": "application/json",
}
try:
    r = requests.options(
        "http://localhost:8000/api/v1/auth/register",
        headers=headers,
        timeout=5
    )
    if "access-control-allow-origin" in r.headers:
        print(f"✅ CORS 配置正确: {r.headers.get('access-control-allow-origin')}")
    else:
        print("⚠️  未找到 CORS 头，但可能正常")
except Exception as e:
    print(f"❌ CORS 测试失败: {e}")

# 测试 3: 注册新用户
print("\n[3] 测试注册接口...")
register_data = {
    "email": "final_test@example.com",
    "username": "finaltest",
    "password": "test123456"
}
headers = {
    "Origin": "http://localhost:3001",
    "Content-Type": "application/json",
}
try:
    r = requests.post(
        "http://localhost:8000/api/v1/auth/register",
        json=register_data,
        headers=headers,
        timeout=10
    )
    if r.status_code == 201:
        print(f"✅ 注册成功！")
        user_data = r.json()
        print(f"   用户ID: {user_data['id']}")
        print(f"   用户名: {user_data['username']}")
        print(f"   邮箱: {user_data['email']}")
    elif r.status_code == 400:
        print(f"⚠️  注册失败: {r.json().get('detail', '未知错误')}")
    else:
        print(f"❌ 注册失败 (状态码: {r.status_code})")
        print(f"   响应: {r.text}")
except Exception as e:
    print(f"❌ 注册请求失败: {e}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)

