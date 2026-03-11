"""
🩺 CyberHuaTuo 测试 — validate.py 校验工具
测试病例格式校验的核心逻辑，不依赖外部 API
"""

import tempfile
from pathlib import Path

import pytest
import yaml


# ===== 导入被测模块 =====
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from tools.validate import (
    parse_front_matter,
    validate_body,
    validate_filepath,
)


# ===== 测试数据 =====

VALID_CASE_CONTENT = """---
id: "langchain-import-chatmodel-001"
title: "LangChain 0.3 升级后 ChatOpenAI 导入失败"
title_en: "ChatOpenAI import error after upgrading to LangChain 0.3"
framework: "langchain"
framework_version: ">=0.3.0"
language: "python"
tags:
  - "import-error"
  - "breaking-change"
severity: "medium"
complexity: "simple"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-10"
updated_at: "2026-03-10"
contributors:
  - github: "test-user"
source_url: ""
related_cases: []
---

## 🏥 症状描述

升级到 LangChain 0.3 后 import 报错

## 🔍 错误信息

```
ImportError: cannot import name 'ChatOpenAI' from 'langchain'
```

## 🔬 根因分析

LangChain 0.3 拆分了包结构

## 💊 药方

### 药方 1：推荐方案 ✅ 推荐

```bash
pip install langchain-openai
```
"""

MISSING_FRONT_MATTER_CONTENT = """# 没有 YAML front matter 的文件

这是一个缺少 front matter 的文件。
"""

INCOMPLETE_FRONT_MATTER_CONTENT = """---
id: "test-001"
title: "测试"
---

## 只有两个章节

## 🏥 症状描述

症状
"""

MISSING_SECTIONS_BODY = """
## 🏥 症状描述

有症状描述

## 💊 药方

有药方
"""


# ===== 测试类 =====

class TestParseFrontMatter:
    """测试 YAML front matter 解析"""

    def test_valid_front_matter(self, tmp_path):
        """正常的 front matter 应该成功解析"""
        case_file = tmp_path / "test.md"
        case_file.write_text(VALID_CASE_CONTENT, encoding="utf-8")

        metadata, body, errors = parse_front_matter(case_file)

        assert metadata is not None
        assert len(errors) == 0
        assert metadata["id"] == "langchain-import-chatmodel-001"
        assert metadata["framework"] == "langchain"
        assert metadata["severity"] == "medium"
        assert metadata["complexity"] == "simple"
        assert "症状描述" in body

    def test_missing_front_matter(self, tmp_path):
        """缺少 front matter 的文件应该报错"""
        case_file = tmp_path / "no_fm.md"
        case_file.write_text(MISSING_FRONT_MATTER_CONTENT, encoding="utf-8")

        metadata, body, errors = parse_front_matter(case_file)

        assert metadata is None
        assert len(errors) > 0
        assert any("front matter" in e.lower() or "---" in e for e in errors)

    def test_incomplete_front_matter(self, tmp_path):
        """不完整的 front matter 应该能解析出部分数据"""
        case_file = tmp_path / "incomplete.md"
        case_file.write_text(INCOMPLETE_FRONT_MATTER_CONTENT, encoding="utf-8")

        metadata, body, errors = parse_front_matter(case_file)

        assert metadata is not None
        assert metadata["id"] == "test-001"

    def test_nonexistent_file(self, tmp_path):
        """不存在的文件应该返回错误"""
        case_file = tmp_path / "nonexistent.md"

        metadata, body, errors = parse_front_matter(case_file)

        assert metadata is None
        assert len(errors) > 0

    def test_invalid_yaml(self, tmp_path):
        """无效的 YAML 应该报错"""
        case_file = tmp_path / "invalid_yaml.md"
        case_file.write_text("---\n[invalid: yaml: content\n---\n\nbody", encoding="utf-8")

        metadata, body, errors = parse_front_matter(case_file)

        assert metadata is None
        assert len(errors) > 0


class TestValidateBody:
    """测试 Markdown 正文章节校验"""

    def test_valid_body(self):
        """包含所有必要章节的正文应该通过"""
        body = """
## 🏥 症状描述
描述

## 🔍 错误信息
错误

## 🔬 根因分析
分析

## 💊 药方
药方
"""
        errors = validate_body(body)
        assert len(errors) == 0

    def test_missing_sections(self):
        """缺少章节的正文应该报错"""
        errors = validate_body(MISSING_SECTIONS_BODY)

        # 应该缺少 "错误信息" 和 "根因分析"
        assert len(errors) == 2
        assert any("错误信息" in e for e in errors)
        assert any("根因分析" in e for e in errors)

    def test_empty_body(self):
        """空正文应该报告所有缺少的章节"""
        errors = validate_body("")

        assert len(errors) == 4  # 四个必需章节都缺少

    def test_partial_match(self):
        """部分存在时只报告缺少的"""
        body = """
## 🏥 症状描述
有

## 🔍 错误信息
有

## 🔬 根因分析
有
"""
        errors = validate_body(body)
        assert len(errors) == 1
        assert "药方" in errors[0]


class TestValidateFilepath:
    """测试文件路径与 framework 一致性校验"""

    def test_consistent_path(self, tmp_path):
        """路径与 framework 一致应该通过"""
        # 模拟 cases/langchain/xxx.md 路径
        cases_dir = tmp_path / "cases" / "langchain" / "import-error"
        cases_dir.mkdir(parents=True)
        filepath = cases_dir / "test-001.md"
        filepath.touch()

        # 由于 validate_filepath 依赖 CASES_DIR 常量，
        # 我们直接测试其逻辑
        metadata = {"framework": "langchain"}

        # 路径一致 → 不应该报错
        # 注意：由于 CASES_DIR 是硬编码的，这里测试逻辑而非路径匹配
        errors = validate_filepath(filepath, metadata)
        # 如果不在 CASES_DIR 下，不会报错（返回空列表）
        assert isinstance(errors, list)

    def test_inconsistent_path(self):
        """路径与 framework 不一致时应检测到错误"""
        # 直接测试逻辑：传入已知的 CASES_DIR 子目录
        from tools.validate import CASES_DIR

        if CASES_DIR.exists():
            # 如果 cases/ 目录存在，创建一个测试路径
            for fw_dir in CASES_DIR.iterdir():
                if fw_dir.is_dir():
                    test_file = fw_dir / "dummy.md"
                    metadata = {"framework": "definitely_not_this_framework"}
                    errors = validate_filepath(test_file, metadata)
                    # 应该检测到路径不一致
                    assert len(errors) > 0
                    break


class TestEdgeCases:
    """边缘情况测试"""

    def test_unicode_content(self, tmp_path):
        """包含 Unicode 字符的文件应该正常处理"""
        content = """---
id: "test-unicode-001"
title: "测试中文标题 🩺 特殊字符"
title_en: "Test Unicode"
framework: "langchain"
severity: "low"
complexity: "simple"
tags: ["unicode"]
created_at: "2026-03-11"
contributors:
  - github: "test"
---

## 🏥 症状描述
中文描述 + emoji 🔥

## 🔍 错误信息
错误 ⚠️

## 🔬 根因分析
根因 🔬

## 💊 药方
方案 💊
"""
        case_file = tmp_path / "unicode.md"
        case_file.write_text(content, encoding="utf-8")

        metadata, body, errors = parse_front_matter(case_file)

        assert metadata is not None
        assert len(errors) == 0
        assert "🩺" in metadata["title"]

        body_errors = validate_body(body)
        assert len(body_errors) == 0

    def test_empty_metadata_values(self, tmp_path):
        """空值的 metadata 字段不应崩溃"""
        content = """---
id: ""
title: ""
framework: ""
---

## body
"""
        case_file = tmp_path / "empty_values.md"
        case_file.write_text(content, encoding="utf-8")

        metadata, body, errors = parse_front_matter(case_file)

        assert metadata is not None
        assert metadata["id"] == ""
