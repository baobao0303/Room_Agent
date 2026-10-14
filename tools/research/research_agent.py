import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
from datetime import datetime, timezone

GATEWAY_URL = os.getenv("HERMES_GATEWAY_URL", "http://localhost:8642/v1/chat/completions")
API_KEY = os.getenv("HERMES_API_KEY", "hermes_secret_key_8642")
DEFAULT_MODEL = os.getenv("HERMES_MODEL", "gemini-3.7-medium")

TIER_1_CORE = """You are an AI research specialist. Be direct: match the length of your reply to the weight of the ask. No filler, no pleasantries. Plain claims backed by factual evidence. Never fabricate citations or findings. Depth is earned — provide thorough, structured technical research with clear sections, trade-offs, and actionable conclusions.

# Operational directives
- Structure outputs clearly: Problem Statement, Core Architecture, Findings/Evidence, Trade-offs, Recommendation.
- Absolute accuracy: Distinguish between verified facts and assumptions.
- Keep going: Provide complete analysis without truncation."""

TIER_2_RULES = """Persistent rules:
- Format findings as declarative facts.
- Explicitly state skipped elements and prerequisites."""

def build_system_prompt(cwd: str, topic: str) -> str:
    tier_3_context = f"""Environment & CWD: {cwd}
Active Workspace: Paseo_Project
Research Task: {topic}
Generated At: {datetime.now(timezone.utc).isoformat()}"""
    return f"{TIER_1_CORE}\n\n{TIER_2_RULES}\n\n{tier_3_context}"

def run_via_hermes_cli(system_prompt: str, topic: str) -> str:
    prompt = f"{system_prompt}\n\nPerform comprehensive research and analysis on the following topic:\n\n{topic}"
    res = subprocess.run(["hermes", "-z", prompt], capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip()
    # If -z empty, try hermes chat -q
    res2 = subprocess.run(["hermes", "chat", "-q", prompt, "-Q"], capture_output=True, text=True)
    if res2.returncode == 0 and res2.stdout.strip():
        # filter session_id footer if present
        lines = [l for l in res2.stdout.splitlines() if not l.startswith("session_id:")]
        return "\n".join(lines).strip()
    raise RuntimeError(f"Hermes CLI error: {res.stderr or res2.stderr}")

def run_research(topic: str, output_file: str = None) -> dict:
    cwd = os.path.abspath(os.path.dirname(__file__) + "/../..")
    system_prompt = build_system_prompt(cwd, topic)

    content = None
    # 1. Try HTTP Gateway first
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Perform comprehensive research and analysis on the following topic:\n\n{topic}"}
        ],
        "temperature": 0.2
    }

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
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        # 2. Fallback to direct Hermes CLI
        print(f"[Notice] Gateway HTTP {GATEWAY_URL} not reachable ({e}). Falling back to Hermes CLI directly...", file=sys.stderr)
        try:
            content = run_via_hermes_cli(system_prompt, topic)
        except Exception as cli_err:
            err_msg = f"Failed via both Gateway ({e}) and Hermes CLI ({cli_err})"
            print(err_msg, file=sys.stderr)
            return {"success": False, "error": err_msg}

    if output_file and content:
        target_path = os.path.abspath(os.path.join(cwd, output_file))
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(f"# Research Report: {topic}\n\n")
            f.write(f"> Generated via Hermes on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(content)
        print(f"Report saved to: {target_path}")

    return {"success": True, "content": content}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 research_agent.py '<topic>' [output_markdown_file]")
        sys.exit(1)

    topic_arg = sys.argv[1]
    out_arg = sys.argv[2] if len(sys.argv) > 2 else f"tools/research/{topic_arg.lower().replace(' ', '_')[:30]}.md"
    res = run_research(topic_arg, out_arg)
    if not res.get("success"):
        sys.exit(1)
