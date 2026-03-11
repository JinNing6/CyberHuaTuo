import asyncio
import os
import sys

sys.path.append(r"e:\ideaProjects\agent\CyberHuaTuo")

from cyberhuatuo.contributor import smart_extract_contribution
import traceback

async def main():
    try:
        issue = "React context 更新时导致组件无限重渲染"
        prescription = "使用 useMemo 包裹 provider value"
        res = await smart_extract_contribution(issue, prescription)
        with open("test_output.json", "w", encoding="utf-8") as f:
            import json
            json.dump(res, f, ensure_ascii=False, indent=2)
    except Exception as e:
        with open("test_output.json", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
