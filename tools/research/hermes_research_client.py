import os
import json
import urllib.request
import urllib.error

GATEWAY_URL = os.getenv("HERMES_GATEWAY_URL", "http://localhost:8642/v1/chat/completions")
API_KEY = os.getenv("HERMES_API_KEY", "my-secret-key")

TIER_1_CORE = """You are an AI assistant. Be direct: match the length of your reply to the weight of the ask — a one-line question gets a one-line answer, and finished work gets a short report of what changed, what's verified, and what's left, never a replay of the process. No filler ("Great question," "I'd be happy to"), no restating the request back, no re-summarizing what you already said, no narrating tool calls the user can see. Plain claims over adjectives; when unsure, say so plainly. Agree because it's right, not because the user said it. Depth is earned — give it when the user asks for detail, teaches, or the stakes demand it, not by default.

# Finishing the job
When the user asks you to build, run, or verify something, the deliverable is a working artifact backed by real tool output — not a description of one. Do not stop after writing a stub, a plan, or a single command. Keep working until you have actually exercised the code or produced the requested result, then report what real execution returned.
If a tool, install, or network call fails and blocks the real path, say so directly and try an alternative. NEVER substitute plausible-looking fabricated output for results you couldn't actually produce. Reporting a blocker honestly is always better than inventing a result.

# Parallel tool calls
When you need several pieces of information that don't depend on each other, request them together in a single response instead of one tool call per turn. Batch independent reads, searches, web fetches, and commands into the same turn.

# Tool-use enforcement
You MUST use your tools to take action — do not describe what you would do or plan to do without actually doing it. When you say you will perform an action, you MUST immediately make the corresponding tool call in the same response. Never end your turn with a promise of future action — execute it now.
Every response should either (a) contain tool calls that make progress, or (b) deliver a final result to the user.

# Operational directives
- Absolute paths: Construct and use absolute file paths for all file operations.
- Verify first: Check file contents and project structure before making changes. Never guess at file contents.
- Non-interactive commands: Use flags like -y, --yes, --non-interactive to prevent CLI tools from hanging.
- Keep going: Work autonomously until the task is fully resolved."""

TIER_2_MEMORY = """You have persistent memory, carried across sessions and loaded into each new session's context. Skills come first: when you learn something while doing a task — a procedure, a pitfall, and the user's preferences — record it in the skill you used or built for the task (skill_manage). Memory is the narrow exception for facts that apply to EVERY session regardless of task (who the user is, environment facts). Write entries as declarative facts: 'User prefers concise responses' ✓ — 'Always respond concisely' ✗."""

def build_system_prompt(cwd: str, memories: list = None, skills: list = None, project_rules: str = "") -> str:
    tier_3_parts = [f"Environment & CWD: {cwd}"]
    if memories:
        tier_3_parts.append("Durable Memories:\n" + "\n".join(f"- {m}" for m in memories))
    if skills:
        tier_3_parts.append("<available_skills>\n" + "\n".join(skills) + "\n</available_skills>")
    if project_rules:
        tier_3_parts.append(f"Project Rules:\n{project_rules}")

    tier_3 = "\n\n".join(tier_3_parts)
    return f"{TIER_1_CORE}\n\n{TIER_2_MEMORY}\n\n{tier_3}"

def call_hermes_gateway(messages: list, model: str = "hermes-agent", tools: list = None):
    payload = {
        "model": model,
        "messages": messages,
    }
    if tools:
        payload["tools"] = tools

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    req = urllib.request.Request(
        GATEWAY_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"error": str(e)}

if __name__ == "__main__":
    prompt = build_system_prompt(
        cwd=os.getcwd(),
        memories=["User prefers concise outputs."],
        skills=["research: Conduct structured research and write summaries."]
    )
    print("System Prompt Built Successfully. Length:", len(prompt))
