const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3002;

const server = http.createServer((req, res) => {
  console.log(`请求: ${req.url}`);
  
  if (req.url === '/' || req.url === '/index.html') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(`
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cursor 内置浏览器测试</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 600px;
        }
        h1 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 2.5em;
        }
        p {
            color: #666;
            font-size: 1.2em;
            line-height: 1.6;
        }
        .success {
            color: #10b981;
            font-weight: bold;
            font-size: 1.5em;
            margin: 20px 0;
        }
        .info {
            background: #f0f9ff;
            border-left: 4px solid #0ea5e9;
            padding: 15px;
            margin: 20px 0;
            text-align: left;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            margin: 10px;
            transition: transform 0.2s;
        }
        button:hover {
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 成功！</h1>
        <p class="success">✅ Cursor 内置浏览器服务器运行中！</p>
        <div class="info">
            <strong>服务器信息：</strong><br>
            地址: http://localhost:${PORT}<br>
            时间: <span id="time"></span>
        </div>
        <p>这是一个本地测试服务器，用于验证 Cursor 的内置浏览器功能。</p>
        <button onclick="testClick()">测试点击</button>
        <button onclick="location.reload()">刷新页面</button>
        <p id="message"></p>
    </div>
    <script>
        document.getElementById('time').textContent = new Date().toLocaleString('zh-CN');
        function testClick() {
            document.getElementById('message').textContent = '✅ 按钮点击成功！浏览器交互正常！';
            document.getElementById('message').style.color = '#10b981';
            document.getElementById('message').style.fontWeight = 'bold';
        }
    </script>
</body>
</html>
    `);
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('404 Not Found');
  }
});

server.listen(PORT, 'localhost', () => {
  console.log(`\n🚀 服务器已启动！`);
  console.log(`📍 地址: http://localhost:${PORT}`);
  console.log(`\n请在 Cursor 中打开此地址来测试内置浏览器\n`);
});

