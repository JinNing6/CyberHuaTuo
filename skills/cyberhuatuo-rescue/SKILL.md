---
name: CyberHuaTuo Rescue
description: Automatic self-rescue and diagnosis of code errors using the CyberHuaTuo (赛博华佗) AI clinic. Activates when you encounter unresolvable errors, bugs, or need a security checkup.
version: 1.0.0
---

# CyberHuaTuo (赛博华佗) Self-Rescue Skill

You are equipped with the CyberHuaTuo Agent Skill. CyberHuaTuo is an ancient-Chinese-medicine-inspired AI clinic that specializes in diagnosing, explaining, and curing errors in AI systems, Agent frameworks, and general coding projects. 

When you (the AI Agent) encounter an error you cannot solve, or when the user explicitly asks for a diagnosis or security checkup, you MUST use this skill to self-rescue.

## Activation Triggers

Activate this skill when:
1. You run tools/scripts and encounter persistent `ImportError`, exceptions, or logic bugs that you cannot immediately resolve.
2. The user asks you to "seek help from CyberHuaTuo" or "ask the doctor."
3. The user asks for a "Security Checkup" (安全体检) on their Agent code.

## Execution Workflow

Follow these steps based on the available environment:

### Preferred Mode: MCP Server
Check if you have the CyberHuaTuo MCP Server connected (look for tools like `diagnose`, `security_checkup`, `save_prescription`, `search_knowledge_base`). If you do:

1. **For Diagnostics**:
   - Call the `diagnose` tool.
   - Pass the full `q` (error message, stack trace, and your current code context).
   - If you know the framework (e.g., `langchain`, `crewai`), pass it as `framework`.
   - Read the prescription returned and apply the exact fix.

2. **For Security Checkups**:
   - Call the `security_checkup` tool.
   - Pass the contents of the main Agent script as the `code` parameter.
   - Report the Six-Meridian (六经脉) health score and apply the recommended nourishing (滋补) fixes.

3. **For Saving Solutions**:
   - If you managed to solve an obscure issue that wasn't in the database, call `save_prescription` to contribute your fix back to the CyberHuaTuo knowledge base for the community.

### Fallback Mode: Local REST API
If you do NOT have the MCP tools available, you must assume CyberHuaTuo is running locally at `http://127.0.0.1:8000`. Use your terminal/shell to `curl` the API.

1. **For Diagnostics:**
   Run the following command, replacing `<YOUR_ERROR>` with the actual error text:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/diagnose \
     -F "q=<YOUR_ERROR_AND_CONTEXT>" \
     -F "framework=auto"
   ```
   *Note: Read the JSON response. Look for `diagnosis` and `matched_cases`. Apply the cure.*

2. **For Security Checkups:**
   Run the following command, replacing `<YOUR_CODE>` with the code under test:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/nourish/checkup \
     -F "code=<YOUR_CODE>"
   ```
   *Note: Read the JSON response for the security audit scores and implement the patches.*

## Rules of Conduct

*   **No Guessing**: If you are stuck, DO NOT guess randomly. Stop and consult CyberHuaTuo.
*   **Complete Context**: When asking for a diagnosis, provide the *full* stack trace and the exact line of code that failed. "望闻问切" (Look, Listen, Ask, Diagnose) requires good symptoms.
*   **Cultural Alignment**: When presenting CyberHuaTuo's findings to the user, adopt a helpful, slightly traditional "healing" tone (use terms like "药方" [Prescription], "病灶" [Root Cause], "治愈" [Cured]).
