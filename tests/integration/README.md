# 集成测试

本目录包含集成测试，用于测试多个模块之间的交互。

## 测试文件

- `test_frontend_api.py` - 前端API集成测试
- `test_full_flow.py` - 完整业务流程测试
- `test_register.py` - 注册流程集成测试

## 运行测试

```bash
# 运行所有集成测试
pytest tests/integration/

# 运行特定测试文件
pytest tests/integration/test_full_flow.py
```

## 与单元测试的区别

- **单元测试** (`src/backend/tests/`) - 测试单个函数/类，使用mock隔离依赖
- **集成测试** (`tests/integration/`) - 测试多个模块协作，使用真实依赖
- **手动测试** (`tests/manual/`) - 手动执行的测试脚本（PowerShell等）

## 测试原则

1. 集成测试应该测试真实的业务流程
2. 使用真实的数据库连接（测试数据库）
3. 测试API端点之间的协作
4. 验证完整的用户场景

