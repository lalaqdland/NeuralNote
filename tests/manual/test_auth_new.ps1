# 测试注册新用户
Write-Host "=== 测试注册新用户 ===" -ForegroundColor Green
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$registerBody = @{
    email = "newuser_$timestamp@example.com"
    username = "newuser_$timestamp"
    password = "password123"
} | ConvertTo-Json

Write-Host "注册信息: $registerBody" -ForegroundColor Cyan

try {
    $registerResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
    Write-Host "✓ 注册成功！状态码: $($registerResponse.StatusCode)" -ForegroundColor Green
    Write-Host "响应内容: $($registerResponse.Content)" -ForegroundColor Cyan
    
    # 解析注册响应
    $userData = $registerResponse.Content | ConvertFrom-Json
    $email = $userData.email
    
    Write-Host ""
    Write-Host "=== 测试登录 ===" -ForegroundColor Green
    $loginBody = @{
        email = $email
        password = "password123"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json" -UseBasicParsing
    Write-Host "✓ 登录成功！状态码: $($loginResponse.StatusCode)" -ForegroundColor Green
    Write-Host "响应内容: $($loginResponse.Content)" -ForegroundColor Cyan
    
    # 解析token
    $tokenData = $loginResponse.Content | ConvertFrom-Json
    $accessToken = $tokenData.access_token
    
    Write-Host ""
    Write-Host "=== 测试获取用户信息 ===" -ForegroundColor Green
    $headers = @{
        "Authorization" = "Bearer $accessToken"
    }
    $meResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/me" -Method GET -Headers $headers -UseBasicParsing
    Write-Host "✓ 获取用户信息成功！" -ForegroundColor Green
    Write-Host "用户信息: $($meResponse.Content)" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "=== 测试总结 ===" -ForegroundColor Magenta
    Write-Host "✓ 注册功能正常" -ForegroundColor Green
    Write-Host "✓ 登录功能正常" -ForegroundColor Green
    Write-Host "✓ 获取用户信息功能正常" -ForegroundColor Green
    Write-Host "✓ 所有认证功能测试通过！" -ForegroundColor Green
    
} catch {
    Write-Host "✗ 测试失败" -ForegroundColor Red
    Write-Host "错误信息: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "响应内容: $responseBody" -ForegroundColor Yellow
    }
}

