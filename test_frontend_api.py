import requests
import json

# 模拟前端发送的注册请求
url = "http://localhost:8000/api/v1/auth/register"
headers = {
    "Content-Type": "application/json",
}
data = {
    "email": "frontend_test@example.com",
    "username": "frontendtest",
    "password": "test123456"
}

print("=" * 50)
print("模拟前端注册请求")
print("=" * 50)
print(f"URL: {url}")
print(f"Headers: {json.dumps(headers, indent=2)}")
print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
print()

try:
    response = requests.post(url, json=data, headers=headers, timeout=10)
    print(f"✅ 状态码: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ 注册成功！")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ 注册失败")
        print(f"响应: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ 连接错误：无法连接到后端服务")
    print("请确认后端服务是否在 http://localhost:8000 运行")
except requests.exceptions.Timeout:
    print("❌ 请求超时")
except Exception as e:
    print(f"❌ 错误: {type(e).__name__}: {e}")
    if 'response' in locals():
        print(f"响应文本: {response.text}")

