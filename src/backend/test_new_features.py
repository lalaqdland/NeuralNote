"""
测试文件上传、OCR 和 AI 分析功能
"""

import asyncio
import httpx
from pathlib import Path


# API 基础 URL
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# 测试用户凭证
TEST_USER = {
    "email": "test@neuralnote.com",
    "password": "test123456"
}


async def login() -> str:
    """登录并获取 Token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_V1}/auth/login",
            json=TEST_USER
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 登录成功: {data['username']}")
            return data["access_token"]
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(response.text)
            return None


async def test_file_upload(token: str):
    """测试文件上传"""
    print("\n" + "="*60)
    print("测试 1: 文件上传")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建一个测试图片（如果不存在）
    test_image_path = Path("test_image.jpg")
    if not test_image_path.exists():
        print("⚠️  测试图片不存在，跳过文件上传测试")
        print("提示：请在项目根目录放置一个名为 test_image.jpg 的图片文件")
        return None
    
    # 上传文件
    async with httpx.AsyncClient() as client:
        with open(test_image_path, "rb") as f:
            files = {"file": ("test_image.jpg", f, "image/jpeg")}
            response = await client.post(
                f"{API_V1}/files/upload",
                headers=headers,
                files=files
            )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 文件上传成功")
            print(f"   文件ID: {data['file_id']}")
            print(f"   文件URL: {data['file_url']}")
            print(f"   文件大小: {data['file_size']} bytes")
            return data['file_id']
        else:
            print(f"❌ 文件上传失败: {response.status_code}")
            print(response.text)
            return None


async def test_file_list(token: str):
    """测试文件列表"""
    print("\n" + "="*60)
    print("测试 2: 获取文件列表")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_V1}/files/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取文件列表成功")
            print(f"   总数: {data['total']}")
            print(f"   当前页: {data['page']}/{data['total_pages']}")
            print(f"   文件数: {len(data['items'])}")
            
            for item in data['items'][:3]:  # 只显示前3个
                print(f"   - {item['original_filename']} ({item['status']})")
        else:
            print(f"❌ 获取文件列表失败: {response.status_code}")
            print(response.text)


async def test_ocr(token: str, file_id: str):
    """测试 OCR 识别"""
    print("\n" + "="*60)
    print("测试 3: OCR 识别")
    print("="*60)
    
    if not file_id:
        print("⚠️  没有文件ID，跳过 OCR 测试")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{API_V1}/ocr/ocr",
            headers=headers,
            json={
                "file_id": file_id,
                "ocr_engine": "baidu"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OCR 识别成功")
            print(f"   引擎: {data['engine']}")
            print(f"   置信度: {data['confidence']:.2%}")
            print(f"   处理时间: {data['processing_time']:.2f}秒")
            print(f"   识别文本: {data['text'][:100]}...")
        else:
            print(f"❌ OCR 识别失败: {response.status_code}")
            print(response.text)


async def test_ai_analysis(token: str):
    """测试 AI 分析"""
    print("\n" + "="*60)
    print("测试 4: AI 文本分析")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    test_text = """
    求函数 f(x) = x^2 + 2x + 1 的导数。
    """
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{API_V1}/ai/analyze",
            headers=headers,
            json={
                "text": test_text,
                "engine": "auto",
                "include_embedding": False
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI 分析成功")
            print(f"   学科: {data['subject']}")
            print(f"   难度: {data['difficulty']}")
            print(f"   题型: {data['question_type']}")
            print(f"   引擎: {data['engine']}")
            print(f"   知识点: {', '.join(data['key_points'])}")
            print(f"   总结: {data['summary']}")
            print(f"   解答: {data['answer'][:200]}...")
        else:
            print(f"❌ AI 分析失败: {response.status_code}")
            print(response.text)


async def test_knowledge_extraction(token: str):
    """测试知识点提取"""
    print("\n" + "="*60)
    print("测试 5: 知识点提取")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    test_content = """
    导数是微积分中的核心概念，表示函数在某一点的变化率。
    对于函数 f(x)，其导数定义为：f'(x) = lim(h->0) [f(x+h) - f(x)] / h
    常见的导数公式包括：幂函数、指数函数、对数函数、三角函数的导数。
    """
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{API_V1}/ai/extract-knowledge",
            headers=headers,
            json={
                "content": test_content,
                "engine": "auto"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 知识点提取成功")
            print(f"   引擎: {data['engine']}")
            print(f"   知识点数量: {len(data['knowledge_points'])}")
            for i, kp in enumerate(data['knowledge_points'], 1):
                print(f"   {i}. {kp}")
        else:
            print(f"❌ 知识点提取失败: {response.status_code}")
            print(response.text)


async def main():
    """主测试函数"""
    print("🚀 开始测试 NeuralNote 新功能")
    print("="*60)
    
    # 1. 登录
    token = await login()
    if not token:
        print("❌ 登录失败，终止测试")
        return
    
    # 2. 测试文件上传
    file_id = await test_file_upload(token)
    
    # 3. 测试文件列表
    await test_file_list(token)
    
    # 4. 测试 OCR（需要配置百度 OCR）
    if file_id:
        print("\n⚠️  OCR 测试需要配置百度 OCR API")
        print("请在 .env 文件中配置：")
        print("  BAIDU_OCR_API_KEY=your_api_key")
        print("  BAIDU_OCR_SECRET_KEY=your_secret_key")
        # await test_ocr(token, file_id)
    
    # 5. 测试 AI 分析（需要配置 AI API）
    print("\n⚠️  AI 分析测试需要配置 AI API")
    print("请在 .env 文件中配置：")
    print("  DEEPSEEK_API_KEY=your_api_key  或")
    print("  OPENAI_API_KEY=your_api_key")
    # await test_ai_analysis(token)
    # await test_knowledge_extraction(token)
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

