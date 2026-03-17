"""
测试 CyberHuaTuo Checkup Action — 静态规则引擎 & 入口脚本
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 将 action/ 目录加入 sys.path
ACTION_DIR = Path(__file__).parent.parent / "action"
sys.path.insert(0, str(ACTION_DIR))

from static_rules import static_scan  # noqa: E402
from entrypoint import collect_files, merge_reports, generate_markdown_report  # noqa: E402


# ═══════════════════════════════════════════════════════════
# 测试 static_scan 静态规则扫描
# ═══════════════════════════════════════════════════════════

class TestStaticScan:
    """测试六经脉静态规则扫描"""

    def test_clean_code(self):
        """安全代码应得高分"""
        code = '''
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": sanitized_input}],
    )
except Exception as e:
    logger.error(f"API call failed: {e}")
'''
        result = static_scan(code)
        assert result["health_score"] >= 70
        assert "强壮如虎" in result["level"] or "气血充沛" in result["level"]

    def test_hardcoded_openai_key(self):
        """检测硬编码 OpenAI API Key"""
        code = '''
api_key = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"
client = OpenAI(api_key=api_key)
'''
        result = static_scan(code)
        # 密钥安全维度应发现问题
        secret_dim = next(
            d for d in result["dimensions"] if d["name"] == "密钥安全"
        )
        assert secret_dim["score"] < 100
        assert len(secret_dim["findings"]) > 0
        # 总分应有所下降（但因为只有一个维度受影响，不会降太多）
        assert result["health_score"] < 100

    def test_hardcoded_aws_key(self):
        """检测硬编码 AWS Key"""
        code = '''
aws_key = "AKIAIOSFODNN7EXAMPLE"
'''
        result = static_scan(code)
        secret_dim = next(
            d for d in result["dimensions"] if d["name"] == "密钥安全"
        )
        assert secret_dim["score"] < 100

    def test_eval_exec_detection(self):
        """检测 eval/exec 危险函数"""
        code = '''
user_input = request.get("code")
result = eval(user_input)
exec(compile(user_input, "<string>", "exec"))
'''
        result = static_scan(code)
        sandbox_dim = next(
            d for d in result["dimensions"] if d["name"] == "沙箱隔离"
        )
        assert sandbox_dim["score"] < 80
        assert len(sandbox_dim["findings"]) >= 2

    def test_subprocess_shell_true(self):
        """检测 subprocess shell=True"""
        code = '''
import subprocess
subprocess.run(f"echo {user_input}", shell=True)
'''
        result = static_scan(code)
        sandbox_dim = next(
            d for d in result["dimensions"] if d["name"] == "沙箱隔离"
        )
        assert sandbox_dim["score"] < 100

    def test_prompt_injection_risk(self):
        """检测 Prompt 注入风险"""
        code = '''
prompt = f"Analyze this: {user_input}"
response = client.chat.completions.create(
    messages=[{"role": "user", "content": prompt}]
)
'''
        result = static_scan(code)
        prompt_dim = next(
            d for d in result["dimensions"] if d["name"] == "Prompt 安全"
        )
        assert prompt_dim["score"] < 100

    def test_missing_timeout(self):
        """检测 HTTP 请求缺少 timeout"""
        code = '''
import requests
response = requests.get("https://api.example.com/data")
'''
        result = static_scan(code)
        resilience_dim = next(
            d for d in result["dimensions"] if d["name"] == "韧性设计"
        )
        assert resilience_dim["score"] < 100

    def test_log_leaking_secrets(self):
        """检测日志中泄露密钥"""
        code = '''
import logging
logging.info(f"Using api_key: {api_key}")
'''
        result = static_scan(code)
        obs_dim = next(
            d for d in result["dimensions"] if d["name"] == "可观测性"
        )
        assert obs_dim["score"] < 100

    def test_output_format(self):
        """验证输出格式完整性"""
        code = "print('hello world')"
        result = static_scan(code)

        assert "health_score" in result
        assert "level" in result
        assert "dimensions" in result
        assert "top_issues" in result
        assert "summary" in result
        assert "scan_mode" in result
        assert result["scan_mode"] == "static_rules"
        assert len(result["dimensions"]) == 6
        assert 0 <= result["health_score"] <= 100

    def test_comment_lines_skipped(self):
        """注释行不应触发检测"""
        code = '''
# api_key = "sk-abcdefghijklmnopqrstuvwxyz1234"
# eval(user_input)
'''
        result = static_scan(code)
        assert result["health_score"] >= 90


# ═══════════════════════════════════════════════════════════
# 测试 collect_files 文件收集
# ═══════════════════════════════════════════════════════════

class TestCollectFiles:
    """测试文件收集逻辑"""

    def test_collect_python_files(self, tmp_path):
        """收集 Python 文件"""
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "utils.py").write_text("def foo(): pass")
        (tmp_path / "README.md").write_text("# readme")

        files = collect_files(str(tmp_path), "**/*.py", 10)
        assert len(files) == 2
        assert all(f.suffix == ".py" for f in files)

    def test_max_files_limit(self, tmp_path):
        """最大文件数限制"""
        for i in range(20):
            (tmp_path / f"file_{i}.py").write_text(f"# file {i}")

        files = collect_files(str(tmp_path), "**/*.py", 5)
        assert len(files) == 5

    def test_skip_venv_directory(self, tmp_path):
        """跳过 .venv 目录"""
        venv_dir = tmp_path / ".venv" / "lib"
        venv_dir.mkdir(parents=True)
        (venv_dir / "module.py").write_text("# venv file")
        (tmp_path / "main.py").write_text("# main file")

        files = collect_files(str(tmp_path), "**/*.py", 10)
        assert len(files) == 1
        assert files[0].name == "main.py"

    def test_skip_git_directory(self, tmp_path):
        """跳过 .git 目录"""
        git_dir = tmp_path / ".git" / "hooks"
        git_dir.mkdir(parents=True)
        (git_dir / "pre-commit.py").write_text("# hook")
        (tmp_path / "app.py").write_text("# app")

        files = collect_files(str(tmp_path), "**/*.py", 10)
        assert len(files) == 1

    def test_multiple_patterns(self, tmp_path):
        """多模式匹配"""
        (tmp_path / "main.py").write_text("print(1)")
        (tmp_path / "app.js").write_text("console.log(1)")
        (tmp_path / "style.css").write_text("body {}")

        files = collect_files(str(tmp_path), "**/*.py,**/*.js", 10)
        assert len(files) == 2


# ═══════════════════════════════════════════════════════════
# 测试 merge_reports 报告合并
# ═══════════════════════════════════════════════════════════

class TestMergeReports:
    """测试报告合并逻辑"""

    def test_empty_reports(self):
        """空报告列表"""
        report = merge_reports([])
        assert report["health_score"] == 100
        assert report["files_scanned"] == 0

    def test_single_report(self):
        """单文件报告"""
        single = {
            "health_score": 75,
            "level": "🔵 气血充沛",
            "scan_mode": "static_rules",
            "dimensions": [
                {"name": "沙箱隔离", "score": 80, "findings": []},
                {"name": "密钥安全", "score": 70, "findings": ["硬编码密钥"]},
                {"name": "Prompt 安全", "score": 85, "findings": []},
                {"name": "输出安全", "score": 90, "findings": []},
                {"name": "韧性设计", "score": 60, "findings": ["缺少超时"]},
                {"name": "可观测性", "score": 95, "findings": []},
            ],
            "top_issues": ["硬编码密钥"],
            "summary": "test",
        }
        report = merge_reports([single])
        assert report["health_score"] == 75
        assert report["files_scanned"] == 1

    def test_multiple_reports_worst_score(self):
        """多文件合并取最低分"""
        report_a = {
            "health_score": 90,
            "scan_mode": "static_rules",
            "dimensions": [
                {"name": "沙箱隔离", "score": 100, "findings": []},
                {"name": "密钥安全", "score": 100, "findings": []},
                {"name": "Prompt 安全", "score": 100, "findings": []},
                {"name": "输出安全", "score": 100, "findings": []},
                {"name": "韧性设计", "score": 100, "findings": []},
                {"name": "可观测性", "score": 100, "findings": []},
            ],
        }
        report_b = {
            "health_score": 30,
            "scan_mode": "static_rules",
            "dimensions": [
                {"name": "沙箱隔离", "score": 20, "findings": ["eval found"]},
                {"name": "密钥安全", "score": 10, "findings": ["hardcoded key"]},
                {"name": "Prompt 安全", "score": 50, "findings": []},
                {"name": "输出安全", "score": 40, "findings": []},
                {"name": "韧性设计", "score": 30, "findings": []},
                {"name": "可观测性", "score": 60, "findings": []},
            ],
        }
        report = merge_reports([report_a, report_b])
        # 合并应取各维度最低分
        sandbox_dim = next(d for d in report["dimensions"] if d["name"] == "沙箱隔离")
        assert sandbox_dim["score"] == 20
        assert report["files_scanned"] == 2


# ═══════════════════════════════════════════════════════════
# 测试 generate_markdown_report 报告生成
# ═══════════════════════════════════════════════════════════

class TestMarkdownReport:
    """测试 Markdown 报告生成"""

    def test_report_contains_key_sections(self):
        """报告应包含关键部分"""
        report = {
            "health_score": 65,
            "level": "🟡 需要调理",
            "scan_mode": "static_rules",
            "files_scanned": 2,
            "dimensions": [
                {"name": "沙箱隔离", "emoji": "🛡️", "score": 80, "status": "✅ 通过", "findings": [], "advice": ""},
                {"name": "密钥安全", "emoji": "🔑", "score": 30, "status": "❌ 危险", "findings": ["硬编码 Key"], "advice": "移到环境变量"},
                {"name": "Prompt 安全", "emoji": "🧠", "score": 70, "status": "⚠️ 警告", "findings": [], "advice": ""},
                {"name": "输出安全", "emoji": "🔒", "score": 85, "status": "✅ 通过", "findings": [], "advice": ""},
                {"name": "韧性设计", "emoji": "⏱️", "score": 55, "status": "⚠️ 警告", "findings": [], "advice": ""},
                {"name": "可观测性", "emoji": "📊", "score": 90, "status": "✅ 通过", "findings": [], "advice": ""},
            ],
            "top_issues": ["硬编码 Key"],
            "summary": "测试",
        }
        file_details = [
            {"filename": "main.py", "health_score": 65, "scan_mode": "static_rules"},
        ]

        md = generate_markdown_report(report, file_details)

        assert "CyberHuaTuo Security Checkup Report" in md
        assert "65/100" in md
        assert "沙箱隔离" in md
        assert "密钥安全" in md
        assert "硬编码 Key" in md
        assert "main.py" in md
        assert "赛博华佗" in md
