"""
🧪 CyberHuaTuo 测试 — Bot 匹配器
测试 bot_matcher.py 的匹配逻辑和回复生成
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from cyberhuatuo.bot_matcher import (
    MatchResult,
    Prescription,
    _compute_text_similarity,
    _detect_error_types,
    _detect_frameworks,
    _extract_quick_fix,
    _tokenize,
    format_bot_reply,
    load_prescriptions,
    match_prescriptions,
)


# ============================================================
# 测试数据 Fixtures
# ============================================================

@pytest.fixture
def sample_prescriptions():
    """构建一组测试用药方"""
    return [
        Prescription(
            id="langchain-import-chatmodel-001",
            title="LangChain 0.3 升级后 ChatOpenAI 导入失败",
            title_en="ChatOpenAI import error after upgrading to LangChain 0.3",
            framework="langchain",
            severity="medium",
            complexity="simple",
            tags=["import-error", "breaking-change", "migration"],
            filepath="cases/langchain/import-error/chatmodel-import-001.md",
            content=(
                "## 症状描述\n"
                "从 LangChain 0.2.x 升级到 0.3.x 后\n"
                "```python\n"
                "ImportError: cannot import name 'ChatOpenAI' from 'langchain'\n"
                "```\n"
                "## 药方 1：更新导入路径 ✅ 推荐\n"
                "```bash\n"
                "pip install langchain-openai\n"
                "```\n"
                "```python\n"
                "from langchain_openai import ChatOpenAI\n"
                "```\n"
            ),
            error_patterns=[
                "ImportError: cannot import name 'ChatOpenAI' from 'langchain'",
            ],
            _search_text="",
        ),
        Prescription(
            id="crewai-agent-infinite-loop-001",
            title="CrewAI Agent 陷入无限循环",
            title_en="CrewAI agent stuck in infinite loop",
            framework="crewai",
            severity="high",
            complexity="moderate",
            tags=["infinite-loop", "agent-behavior", "timeout"],
            filepath="cases/crewai/agent-behavior/agent-infinite-loop-001.md",
            content=(
                "## 症状描述\n"
                "CrewAI Agent 执行任务时进入无限循环\n"
                "## 药方 1 ✅ 推荐\n"
                "```python\n"
                "agent = Agent(max_iter=10)\n"
                "```\n"
            ),
            error_patterns=[
                "Agent execution exceeded maximum iterations",
            ],
            _search_text="",
        ),
        Prescription(
            id="mcp-tool-timeout-001",
            title="MCP Tool 调用超时",
            title_en="MCP tool calling timeout",
            framework="mcp",
            severity="medium",
            complexity="moderate",
            tags=["tool-calling", "timeout", "connection"],
            filepath="cases/mcp/tool-calling/tool-timeout-001.md",
            content=(
                "## 症状描述\n"
                "MCP Tool 调用超时，连接被拒绝\n"
                "```\n"
                "TimeoutError: Tool call timed out after 30s\n"
                "```\n"
                "## 药方 1 ✅ 推荐\n"
                "```python\n"
                "client = MCPClient(timeout=60)\n"
                "```\n"
            ),
            error_patterns=[
                "TimeoutError: Tool call timed out after 30s",
            ],
            _search_text="",
        ),
    ]


@pytest.fixture
def sample_prescriptions_with_search_text(sample_prescriptions):
    """为测试药方填充搜索文本"""
    for rx in sample_prescriptions:
        rx._search_text = " ".join([
            rx.title, rx.title_en, rx.framework,
            " ".join(rx.tags), rx.content[:3000],
        ]).lower()
    return sample_prescriptions


# ============================================================
# 框架检测测试
# ============================================================

class TestFrameworkDetection:
    """测试框架名检测"""

    def test_detect_langchain(self):
        detected = _detect_frameworks("I'm using LangChain 0.3 and got an error")
        assert "langchain" in detected

    def test_detect_crewai(self):
        detected = _detect_frameworks("My CrewAI agent is stuck in a loop")
        assert "crewai" in detected

    def test_detect_mcp(self):
        detected = _detect_frameworks("MCP tool calling timeout")
        assert "mcp" in detected

    def test_detect_multiple_frameworks(self):
        detected = _detect_frameworks("LangChain and CrewAI both fail with OpenAI")
        assert "langchain" in detected
        assert "crewai" in detected

    def test_detect_no_framework(self):
        detected = _detect_frameworks("The weather today is nice")
        # 不应该包含具体的 agent 框架
        assert "langchain" not in detected
        assert "crewai" not in detected
        assert "mcp" not in detected


# ============================================================
# 错误类型检测测试
# ============================================================

class TestErrorDetection:
    """测试错误类型关键词检测"""

    def test_detect_import_error(self):
        detected = _detect_error_types("ImportError: cannot import name 'ChatOpenAI'")
        assert any("import" in e for e in detected)

    def test_detect_timeout(self):
        detected = _detect_error_types("Connection timed out after 30 seconds")
        assert any("timeout" in e or "timed out" in e for e in detected)

    def test_detect_oom(self):
        detected = _detect_error_types("MemoryError: Out of Memory when loading model")
        assert any("memory" in e or "oom" in e for e in detected)

    def test_detect_no_errors(self):
        detected = _detect_error_types("Everything works fine, just a question about best practices")
        # 不应检测到特定错误类型
        assert "importerror" not in detected


# ============================================================
# 文本相似度测试
# ============================================================

class TestTextSimilarity:
    """测试文本相似度计算"""

    def test_identical_text(self):
        sim = _compute_text_similarity("langchain import error", "langchain import error")
        assert sim > 0.9

    def test_similar_text(self):
        sim = _compute_text_similarity(
            "LangChain ImportError ChatOpenAI",
            "langchain import error chatmodel import",
        )
        assert sim > 0.1

    def test_unrelated_text(self):
        sim = _compute_text_similarity(
            "The weather is nice today",
            "langchain import error chatmodel",
        )
        assert sim < 0.3

    def test_empty_text(self):
        sim = _compute_text_similarity("", "some text")
        assert sim == 0.0


# ============================================================
# 药方匹配测试
# ============================================================

class TestPrescriptionMatching:
    """测试药方匹配逻辑"""

    def test_match_langchain_import_error(self, sample_prescriptions_with_search_text):
        """输入 LangChain ImportError 描述，应匹配到对应药方"""
        matches = match_prescriptions(
            issue_title="ImportError: cannot import name 'ChatOpenAI' from 'langchain'",
            issue_body="After upgrading langchain to 0.3, I got ImportError",
            prescriptions=sample_prescriptions_with_search_text,
        )
        assert len(matches) > 0
        assert matches[0].prescription.framework == "langchain"
        assert matches[0].score > 0

    def test_match_crewai_loop(self, sample_prescriptions_with_search_text):
        """输入 CrewAI 无限循环描述，应匹配到对应药方"""
        matches = match_prescriptions(
            issue_title="CrewAI agent infinite loop",
            issue_body="My CrewAI agent is stuck in an infinite loop, it keeps running forever",
            prescriptions=sample_prescriptions_with_search_text,
        )
        assert len(matches) > 0
        assert matches[0].prescription.framework == "crewai"

    def test_match_no_result(self, sample_prescriptions_with_search_text):
        """输入完全无关内容，应返回空列表"""
        matches = match_prescriptions(
            issue_title="今天天气不错",
            issue_body="阳光明媚，适合出去散步",
            prescriptions=sample_prescriptions_with_search_text,
            min_score=50.0,
        )
        assert len(matches) == 0

    def test_score_ranking(self, sample_prescriptions_with_search_text):
        """多个匹配结果应按相关度降序排列"""
        matches = match_prescriptions(
            issue_title="LangChain ImportError timeout",
            issue_body="langchain import error and also timeout issues",
            prescriptions=sample_prescriptions_with_search_text,
            min_score=5.0,
        )
        if len(matches) > 1:
            for i in range(len(matches) - 1):
                assert matches[i].score >= matches[i + 1].score

    def test_empty_prescriptions(self):
        """空药方库应返回空列表"""
        matches = match_prescriptions(
            issue_title="Some error",
            issue_body="Some description",
            prescriptions=[],
        )
        assert matches == []


# ============================================================
# 回复格式化测试
# ============================================================

class TestReplyFormatting:
    """测试回复 Markdown 格式化"""

    def test_format_reply_with_matches(self, sample_prescriptions):
        """有匹配时应生成包含药方信息的回复"""
        matches = [
            MatchResult(
                prescription=sample_prescriptions[0],
                score=85.0,
                match_reasons=["框架匹配: langchain", "错误匹配: import"],
                framework_matched=True,
                error_matched=True,
            ),
        ]
        reply = format_bot_reply(matches, trigger_type="auto")
        assert "赛博华佗" in reply
        assert "Auto Diagnosis" in reply
        assert "langchain" in reply
        assert "药方 1" in reply
        assert "相关度 85%" in reply

    def test_format_reply_no_matches_mention(self):
        """@提及但无匹配时应返回友好提示"""
        reply = format_bot_reply([], trigger_type="mention")
        assert "赛博华佗" in reply
        assert "暂未找到" in reply
        assert len(reply) > 50

    def test_format_reply_no_matches_auto(self):
        """自动匹配无结果时应返回空字符串（不发评论）"""
        reply = format_bot_reply([], trigger_type="auto")
        assert reply == ""

    def test_format_reply_contains_footer(self, sample_prescriptions):
        """回复应包含品牌 Footer"""
        matches = [
            MatchResult(
                prescription=sample_prescriptions[0],
                score=90.0,
                match_reasons=["框架匹配"],
            ),
        ]
        reply = format_bot_reply(matches, trigger_type="auto")
        assert "CyberHuaTuo" in reply
        assert "⭐" in reply


# ============================================================
# 速效药提取测试
# ============================================================

class TestQuickFixExtraction:
    """测试从药方内容中提取速效药"""

    def test_extract_recommended_fix(self):
        content = (
            "## 药方 1：更新导入路径 ✅ 推荐\n"
            "```python\n"
            "from langchain_openai import ChatOpenAI\n"
            "```\n"
        )
        fix = _extract_quick_fix(content)
        assert fix is not None
        assert "langchain_openai" in fix

    def test_extract_no_code_block(self):
        content = "这是一段没有代码块的描述文本"
        fix = _extract_quick_fix(content)
        assert fix is None


# ============================================================
# @CyberHuaTuo 提及检测测试
# ============================================================

class TestMentionDetection:
    """测试 @CyberHuaTuo 提及检测"""

    def test_exact_mention(self):
        from cyberhuatuo.github_bot import _detect_mention
        assert _detect_mention("@CyberHuaTuo help me with this error")

    def test_lowercase_mention(self):
        from cyberhuatuo.github_bot import _detect_mention
        assert _detect_mention("@cyberhuatuo what's wrong?")

    def test_no_mention(self):
        from cyberhuatuo.github_bot import _detect_mention
        assert not _detect_mention("This is a normal comment without any mention")

    def test_mention_in_middle(self):
        from cyberhuatuo.github_bot import _detect_mention
        assert _detect_mention("Hey @CyberHuaTuo, can you check this?")


# ============================================================
# 药方加载测试
# ============================================================

class TestPrescriptionLoading:
    """测试从文件系统加载药方"""

    def test_load_from_cases_dir(self):
        """应能从 cases/ 目录加载药方"""
        cases_dir = Path(__file__).parent.parent / "cases"
        prescriptions = load_prescriptions(cases_dir)
        assert isinstance(prescriptions, list)
        # 项目中应该至少有一些药方
        assert len(prescriptions) > 0

    def test_load_from_nonexistent_dir(self):
        """不存在的目录应返回空列表"""
        prescriptions = load_prescriptions(Path("/nonexistent/path"))
        assert prescriptions == []

    def test_loaded_prescription_structure(self):
        """加载的药方应有完整的结构"""
        cases_dir = Path(__file__).parent.parent / "cases"
        prescriptions = load_prescriptions(cases_dir)

        for rx in prescriptions:
            assert rx.id, "药方必须有 ID"
            assert rx.title, "药方必须有标题"
            assert rx.framework, "药方必须有框架信息"
            assert rx.severity in ("low", "medium", "high", "critical")
            assert rx.filepath, "药方必须有文件路径"


# ============================================================
# Tokenizer 测试
# ============================================================

class TestTokenizer:
    """测试分词器"""

    def test_english_tokenization(self):
        tokens = _tokenize("LangChain ImportError ChatOpenAI")
        assert "langchain" in tokens
        assert "importerror" in tokens

    def test_chinese_tokenization(self):
        tokens = _tokenize("导入错误")
        assert "导" in tokens
        assert "入" in tokens

    def test_mixed_tokenization(self):
        tokens = _tokenize("LangChain 导入失败")
        assert "langchain" in tokens
        assert "导" in tokens

    def test_url_removal(self):
        tokens = _tokenize("Check https://github.com/example for details")
        assert "https" not in " ".join(tokens)
