"""
🩺 CyberHuaTuo 测试 — searcher.py 搜索引擎
测试搜索结果的数据结构和基本逻辑，不依赖外部 API
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))


class TestSearcherModule:
    """测试搜索模块的可导入性和基本结构"""

    def test_import_searcher(self):
        """searcher 模块应该可以被导入"""
        from cyberhuatuo.searcher import search_cases
        assert callable(search_cases)

    def test_import_indexer(self):
        """indexer 模块应该可以被导入"""
        from cyberhuatuo.indexer import build_index, scan_cases
        assert callable(build_index)
        assert callable(scan_cases)

    def test_scan_cases_returns_list(self):
        """scan_cases 应该返回列表"""
        from cyberhuatuo.indexer import scan_cases
        cases = scan_cases()
        assert isinstance(cases, list)

    def test_scan_cases_structure(self):
        """扫描到的每个 case 应该包含必要的字段"""
        from cyberhuatuo.indexer import scan_cases
        cases = scan_cases()

        for case in cases:
            assert "id" in case or "metadata" in case
            # 如果有 metadata，检查其结构
            if "metadata" in case:
                meta = case["metadata"]
                assert isinstance(meta, dict)


class TestContributorModule:
    """测试贡献者模块的常量和数据结构"""

    def test_import_contributor(self):
        """contributor 模块应该可以被导入"""
        from cyberhuatuo.contributor import (
            FRAMEWORKS, SEVERITIES, COMPLEXITIES,
        )
        assert isinstance(FRAMEWORKS, (list, tuple, dict))
        assert isinstance(SEVERITIES, (list, tuple, dict))
        assert isinstance(COMPLEXITIES, (list, tuple, dict))

    def test_frameworks_not_empty(self):
        """框架列表不应为空"""
        from cyberhuatuo.contributor import FRAMEWORKS
        assert len(FRAMEWORKS) > 0

    def test_severities_values(self):
        """severity 应该包含标准的四个级别"""
        from cyberhuatuo.contributor import SEVERITIES
        expected = {"low", "medium", "high", "critical"}
        # SEVERITIES 可能是 list 或 dict，提取值
        if isinstance(SEVERITIES, dict):
            actual = set(SEVERITIES.keys())
        else:
            actual = set(SEVERITIES)
        assert expected.issubset(actual)


class TestConfigModule:
    """测试配置模块"""

    def test_import_config(self):
        """config 模块应该可以被导入"""
        from cyberhuatuo.config import config
        assert config is not None

    def test_config_has_port(self):
        """config 应该有 PORT 属性"""
        from cyberhuatuo.config import config
        assert hasattr(config, "PORT")
        assert isinstance(config.PORT, int)

    def test_config_has_host(self):
        """config 应该有 HOST 属性"""
        from cyberhuatuo.config import config
        assert hasattr(config, "HOST")

    def test_config_has_ephemeral_search(self):
        """config 应该有 EPHEMERAL_SEARCH_ENABLED 属性"""
        from cyberhuatuo.config import config
        assert hasattr(config, "EPHEMERAL_SEARCH_ENABLED")
        assert isinstance(config.EPHEMERAL_SEARCH_ENABLED, bool)


# ============================================================
# 🔍 搜索结果 source 字段测试
# ============================================================


class TestSearchResultSource:
    """测试 SearchResult 的 source 字段"""

    def test_search_result_has_source_field(self):
        """SearchResult 应该有 source 字段"""
        from cyberhuatuo.searcher import SearchResult
        result = SearchResult(
            case_id="test-001",
            title="测试",
            title_en="test",
            framework="langchain",
            severity="medium",
            complexity="moderate",
            tags="test",
            filepath="cases/test.md",
            distance=0.0,
            relevance=95.0,
            content=None,
        )
        # 默认值应该是 "常驻"
        assert result.source == "常驻"

    def test_search_result_ephemeral_source(self):
        """可以创建 source='瞬时' 的搜索结果"""
        from cyberhuatuo.searcher import SearchResult
        result = SearchResult(
            case_id="issue-42",
            title="瞬时药方",
            title_en="ephemeral",
            framework="pytorch",
            severity="high",
            complexity="simple",
            tags="",
            filepath="https://github.com/test/issues/42",
            distance=0.0,
            relevance=75.0,
            content="药方内容",
            source="瞬时",
        )
        assert result.source == "瞬时"


# ============================================================
# 📋 Issue 解析测试
# ============================================================


class TestIssueParser:
    """测试 GitHub Issue 解析为 SearchResult 的逻辑"""

    def test_extract_structured_data(self):
        """应正确提取 <details> 中的 JSON 数据"""
        from cyberhuatuo.searcher import _extract_structured_data

        body = '''## 药方摘要

<details><summary>Data</summary>

```json
{"framework": "langchain", "title": "测试标题", "severity": "high"}
```

</details>'''
        data = _extract_structured_data(body)
        assert data is not None
        assert data["framework"] == "langchain"
        assert data["title"] == "测试标题"

    def test_extract_structured_data_invalid_json(self):
        """无效 JSON 应返回 None"""
        from cyberhuatuo.searcher import _extract_structured_data

        body = '```json\n{invalid json}\n```'
        data = _extract_structured_data(body)
        assert data is None

    def test_extract_structured_data_no_json(self):
        """无 JSON 块应返回 None"""
        from cyberhuatuo.searcher import _extract_structured_data

        body = "这只是普通文本"
        data = _extract_structured_data(body)
        assert data is None

    def test_clean_issue_body(self):
        """应移除 <details> 块和自动签名"""
        from cyberhuatuo.searcher import _clean_issue_body

        body = '''## 药方摘要

<details><summary>Data</summary>

```json
{"test": "data"}
```

</details>

*此 Issue 由 CyberHuaTuo MCP Server 自动创建 / Auto-created*'''

        cleaned = _clean_issue_body(body)
        assert "<details>" not in cleaned
        assert "此 Issue 由" not in cleaned
        assert "药方摘要" in cleaned

    def test_parse_issue_to_result(self):
        """应正确解析完整的 Issue 为 SearchResult"""
        from cyberhuatuo.searcher import _parse_issue_to_result

        issue = {
            "number": 42,
            "title": "🩺 [langchain] RAG内存泄漏修复",
            "html_url": "https://github.com/test/issues/42",
            "labels": [
                {"name": "prescription"},
                {"name": "framework:langchain"},
                {"name": "severity:high"},
            ],
            "body": '''## 药方

```json
{"framework": "langchain", "title": "RAG内存泄漏修复", "title_en": "RAG memory leak fix", "prescription": "修复方案", "severity": "high", "complexity": "moderate", "tags": ["rag", "memory"]}
```''',
        }

        result = _parse_issue_to_result(issue)
        assert result is not None
        assert result.case_id == "issue-42"
        assert result.framework == "langchain"
        assert result.severity == "high"
        assert result.source == "瞬时"
        assert result.title == "RAG内存泄漏修复"


# ============================================================
# 📦 browse_prescriptions 工具测试
# ============================================================


class TestBrowsePrescriptions:
    """测试 browse_prescriptions 药方库浏览工具"""

    def test_browse_list_returns_string(self):
        """list action 应返回包含药方库标题的字符串"""
        from cyberhuatuo.mcp_server import browse_prescriptions
        result = browse_prescriptions(action="list")
        assert isinstance(result, str)
        assert "药方库" in result or "药方" in result

    def test_browse_list_with_framework_filter(self):
        """按框架筛选时，结果中应只包含对应框架的药方"""
        from cyberhuatuo.mcp_server import browse_prescriptions
        result = browse_prescriptions(action="list", framework="langchain")
        assert isinstance(result, str)
        # 如果 langchain 有药方，结果中应包含 langchain
        # 如果没有药方，结果中也应有合理提示
        if "未找到" not in result:
            assert "langchain" in result.lower()

    def test_browse_detail_with_valid_id(self):
        """detail action + 已知 case_id 应返回包含完整内容的字符串"""
        from cyberhuatuo.indexer import scan_cases
        from cyberhuatuo.mcp_server import browse_prescriptions
        cases = scan_cases()
        if cases:
            first_id = cases[0]["id"]
            result = browse_prescriptions(action="detail", case_id=first_id)
            assert isinstance(result, str)
            assert "药方详情" in result or first_id in result

    def test_browse_detail_missing_id(self):
        """detail action 不提供 case_id 应返回提示信息"""
        from cyberhuatuo.mcp_server import browse_prescriptions
        result = browse_prescriptions(action="detail")
        assert isinstance(result, str)
        assert "case_id" in result

    def test_browse_stats(self):
        """stats action 应返回包含统计数据的字符串"""
        from cyberhuatuo.mcp_server import browse_prescriptions
        result = browse_prescriptions(action="stats")
        assert isinstance(result, str)
        assert "总计" in result or "统计" in result or "为空" in result

    def test_browse_pagination(self):
        """分页参数应生效，page_size=1 时只展示 1 条"""
        from cyberhuatuo.indexer import scan_cases
        from cyberhuatuo.mcp_server import browse_prescriptions
        cases = scan_cases()
        if len(cases) > 1:
            result = browse_prescriptions(action="list", page_size=1)
            # 表格中应只有 1 条数据行（除了表头两行）
            # 第 2 页链接应存在
            assert "下一页" in result or "page=2" in result
