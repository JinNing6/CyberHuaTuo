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
