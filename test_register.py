import requests
import json

# 测试注册接口
url = "http://localhost:8000/api/v1/auth/register"
data = {
    "email": "296386091@qq.com",
    "username": "lalaqdland",
    "password": "test123456"
}

print("=" * 50)
print("测试注册接口")
print("=" * 50)
print(f"URL: {url}")
print(f"数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
print()

try:
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print()
    print("响应内容:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"错误: {e}")
    print(f"响应文本: {response.text if 'response' in locals() else 'N/A'}")

