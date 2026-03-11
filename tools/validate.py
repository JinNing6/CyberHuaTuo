#!/usr/bin/env python3
"""
CyberHuaTuo 病例格式校验工具
验证 cases/ 目录下所有 .md 文件的 YAML front matter 是否符合规范

用法:
    python tools/validate.py              # 校验所有病例
    python tools/validate.py --verbose    # 详细输出
    python tools/validate.py --fix-dates  # 自动修复日期格式
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ 请安装 pyyaml: pip install pyyaml")
    sys.exit(1)

try:
    import jsonschema
except ImportError:
    print("❌ 请安装 jsonschema: pip install jsonschema")
    sys.exit(1)


# 项目根目录
ROOT = Path(__file__).parent.parent.resolve()
CASES_DIR = ROOT / "cases"
SCHEMA_PATH = ROOT / "schema" / "case.schema.json"

# 必须包含的 Markdown 标题
REQUIRED_SECTIONS = [
    "症状描述",
    "错误信息",
    "根因分析",
    "药方",
]


def load_schema() -> dict:
    """加载 JSON Schema"""
    if not SCHEMA_PATH.exists():
        print(f"⚠️  Schema 文件未找到: {SCHEMA_PATH}")
        return {}
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def parse_front_matter(filepath: Path) -> tuple[dict | None, str, list[str]]:
    """
    解析 Markdown 文件的 YAML front matter

    Returns:
        (metadata_dict, body_text, errors)
    """
    errors = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return None, "", [f"无法读取文件: {e}"]

    # 检查 front matter 边界
    if not content.startswith("---"):
        return None, content, ["文件缺少 YAML front matter (应以 --- 开头)"]

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content, ["YAML front matter 格式不完整 (缺少结束 ---)"]

    yaml_text = parts[1].strip()
    body = parts[2].strip()

    try:
        metadata = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        return None, body, [f"YAML 解析错误: {e}"]

    if not isinstance(metadata, dict):
        return None, body, ["YAML front matter 不是有效的字典格式"]

    return metadata, body, errors


def validate_schema(metadata: dict, schema: dict) -> list[str]:
    """使用 JSON Schema 校验 metadata"""
    errors = []
    if not schema:
        return errors

    try:
        jsonschema.validate(instance=metadata, schema=schema)
    except jsonschema.ValidationError as e:
        # 提取更友好的错误消息
        path = " → ".join(str(p) for p in e.absolute_path) if e.absolute_path else "(root)"
        errors.append(f"Schema 校验失败 [{path}]: {e.message}")
    except jsonschema.SchemaError as e:
        errors.append(f"Schema 定义错误: {e.message}")

    return errors


def validate_body(body: str, is_nourishing: bool = False) -> list[str]:
    """校验 Markdown 正文是否包含必要章节"""
    errors = []
    if is_nourishing:
        # 滋补类型使用不同的章节结构，核心章节要求较宽松
        nourishing_sections = ["滋补概述", "滋补药方"]
        for section in nourishing_sections:
            if section not in body:
                errors.append(f"正文缺少章节: 「{section}」")
    else:
        for section in REQUIRED_SECTIONS:
            if section not in body:
                errors.append(f"正文缺少章节: 「{section}」")
    return errors


def validate_filepath(filepath: Path, metadata: dict) -> list[str]:
    """校验文件路径是否与 framework 字段一致"""
    errors = []
    framework = metadata.get("framework", "")

    # 获取 cases/ 下的第一级目录名
    try:
        relative = filepath.relative_to(CASES_DIR)
        top_dir = relative.parts[0] if relative.parts else ""
    except ValueError:
        return errors

    if framework and top_dir and top_dir != framework:
        errors.append(
            f"文件路径 ({top_dir}/) 与 framework 字段 ({framework}) 不一致"
        )

    return errors


def validate_all(verbose: bool = False) -> bool:
    """校验所有病例文件"""
    schema = load_schema()

    # 收集所有病例文件
    case_files = sorted(CASES_DIR.rglob("*.md"))
    case_files = [f for f in case_files if f.name != "_index.md"]

    if not case_files:
        print("⚠️  未找到任何病例文件")
        return True

    print(f"\n🔍 正在校验 {len(case_files)} 个病例文件...\n")

    total_errors = 0
    all_ids = Counter()
    results = []

    for filepath in case_files:
        file_errors = []
        relative = filepath.relative_to(ROOT)

        # 1. 解析 front matter
        metadata, body, parse_errors = parse_front_matter(filepath)
        file_errors.extend(parse_errors)

        if metadata:
            # 2. Schema 校验
            schema_errors = validate_schema(metadata, schema)
            file_errors.extend(schema_errors)

            # 3. 正文校验
            is_nourishing = metadata.get("framework", "") == "_nourishing"
            body_errors = validate_body(body, is_nourishing=is_nourishing)
            file_errors.extend(body_errors)

            # 4. 路径校验
            path_errors = validate_filepath(filepath, metadata)
            file_errors.extend(path_errors)

            # 5. 记录 ID（后续检查唯一性）
            case_id = metadata.get("id", "")
            if case_id:
                all_ids[case_id] += 1

        # 输出结果
        if file_errors:
            total_errors += len(file_errors)
            results.append((relative, file_errors))
            print(f"  ❌ {relative}")
            for err in file_errors:
                print(f"     └─ {err}")
        elif verbose:
            case_id = metadata.get("id", "?") if metadata else "?"
            print(f"  ✅ {relative} ({case_id})")

    # 检查 ID 唯一性
    for case_id, count in all_ids.items():
        if count > 1:
            total_errors += 1
            print(f"\n  ❌ ID 重复: \"{case_id}\" 出现了 {count} 次")

    # 统计
    print(f"\n{'═' * 50}")
    passed = len(case_files) - len(results)
    print(f"  📊 总计: {len(case_files)} 个病例")
    print(f"  ✅ 通过: {passed}")
    print(f"  ❌ 失败: {len(results)} ({total_errors} 个错误)")

    if total_errors == 0:
        print(f"\n  🎉 All {len(case_files)} cases validated successfully!\n")
        return True
    else:
        print(f"\n  ⚠️  请修复上述 {total_errors} 个错误后重试\n")
        return False


def main():
    parser = argparse.ArgumentParser(description="CyberHuaTuo 病例格式校验")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    success = validate_all(verbose=args.verbose)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
