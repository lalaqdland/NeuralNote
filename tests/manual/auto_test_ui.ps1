# 自动化UI测试脚本
Write-Host "=== NeuralNote 登录功能自动化测试 ===" -ForegroundColor Cyan
Write-Host ""

# 1. 检查服务状态
Write-Host "1. 检查服务状态..." -ForegroundColor Yellow
try {
    $frontendCheck = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "   ✓ 前端服务运行正常 (状态码: $($frontendCheck.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ✗ 前端服务未运行" -ForegroundColor Red
    exit 1
}

try {
    $backendCheck = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "   ✓ 后端服务运行正常" -ForegroundColor Green
} catch {
    Write-Host "   ✗ 后端服务未运行" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. 打开浏览器访问登录页面..." -ForegroundColor Yellow
Start-Process "http://localhost:3000/login"
Write-Host "   ✓ 浏览器已打开" -ForegroundColor Green

Write-Host ""
Write-Host "3. 执行API注册测试..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$testEmail = "uitest_$timestamp@example.com"
$testUsername = "uitest_$timestamp"
$testPassword = "Test123456"

$registerBody = @{
    email = $testEmail
    username = $testUsername
    password = $testPassword
} | ConvertTo-Json

try {
    $registerResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
    $userData = $registerResponse.Content | ConvertFrom-Json
    Write-Host "   ✓ 注册成功！" -ForegroundColor Green
    Write-Host "     邮箱: $($userData.email)" -ForegroundColor Cyan
    Write-Host "     用户名: $($userData.username)" -ForegroundColor Cyan
    Write-Host "     用户ID: $($userData.id)" -ForegroundColor Cyan
} catch {
    Write-Host "   ✗ 注册失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "4. 执行API登录测试..." -ForegroundColor Yellow
$loginBody = @{
    email = $testEmail
    password = $testPassword
} | ConvertTo-Json

try {
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json" -UseBasicParsing
    $tokenData = $loginResponse.Content | ConvertFrom-Json
    Write-Host "   ✓ 登录成功！" -ForegroundColor Green
    Write-Host "     Token类型: $($tokenData.token_type)" -ForegroundColor Cyan
    Write-Host "     过期时间: $($tokenData.expires_in)秒" -ForegroundColor Cyan
    
    # 获取用户信息
    $headers = @{
        "Authorization" = "Bearer $($tokenData.access_token)"
    }
    $meResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/me" -Method GET -Headers $headers -UseBasicParsing
    $userInfo = $meResponse.Content | ConvertFrom-Json
    Write-Host "   ✓ 获取用户信息成功！" -ForegroundColor Green
    Write-Host "     最后登录: $($userInfo.last_login_at)" -ForegroundColor Cyan
} catch {
    Write-Host "   ✗ 登录失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== 测试总结 ===" -ForegroundColor Magenta
Write-Host "✓ 前端服务正常" -ForegroundColor Green
Write-Host "✓ 后端服务正常" -ForegroundColor Green
Write-Host "✓ 注册功能正常" -ForegroundColor Green
Write-Host "✓ 登录功能正常" -ForegroundColor Green
Write-Host "✓ Token认证正常" -ForegroundColor Green
Write-Host ""
Write-Host "测试账户信息（可用于UI测试）：" -ForegroundColor Yellow
Write-Host "  邮箱: $testEmail" -ForegroundColor White
Write-Host "  密码: $testPassword" -ForegroundColor White
Write-Host ""
Write-Host "浏览器已打开登录页面，您可以使用上述账户进行登录测试！" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意键关闭..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

