"""
测试运行脚本
快速运行所有测试或特定测试
"""

import sys
import subprocess


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("运行所有测试")
    print("=" * 60)
    subprocess.run(["pytest", "-v"])


def run_coverage():
    """运行测试并生成覆盖率报告"""
    print("=" * 60)
    print("运行测试并生成覆盖率报告")
    print("=" * 60)
    subprocess.run([
        "pytest",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term",
        "-v"
    ])


def run_specific_test(test_file):
    """运行特定测试文件"""
    print("=" * 60)
    print(f"运行测试: {test_file}")
    print("=" * 60)
    subprocess.run(["pytest", f"tests/{test_file}", "-v"])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "all":
            run_all_tests()
        elif command == "coverage":
            run_coverage()
        elif command == "auth":
            run_specific_test("test_auth.py")
        elif command == "graphs":
            run_specific_test("test_knowledge_graphs.py")
        elif command == "nodes":
            run_specific_test("test_memory_nodes.py")
        elif command == "users":
            run_specific_test("test_users.py")
        else:
            print(f"未知命令: {command}")
            print("可用命令: all, coverage, auth, graphs, nodes, users")
    else:
        run_all_tests()

