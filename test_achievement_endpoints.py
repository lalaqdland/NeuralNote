import requests

# 登录获取 token
r = requests.post('http://localhost:8000/api/v1/auth/login', json={'email': 'test@neuralnote.com', 'password': 'test123456'})
token = r.json()['access_token']
print(f'Token: {token[:50]}...')

# 测试所有成就系统端点
endpoints = [
    '/api/v1/achievements/stats',
    '/api/v1/achievements/level',
    '/api/v1/achievements/achievements',
    '/api/v1/achievements/profile'
]

for ep in endpoints:
    r = requests.get(f'http://localhost:8000{ep}', headers={'Authorization': f'Bearer {token}'})
    print(f'{ep}: {r.status_code}')
    if r.status_code != 200:
        print(f'  Error: {r.text[:200]}')

