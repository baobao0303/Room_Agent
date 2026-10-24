import { spawn } from "node:child_process";
import path from "node:path";

const PROJECT_ROOT = process.env.PASEO_PROJECT_ROOT || path.resolve(__dirname, "../../..");
const PYTHON_HOOK_SCRIPT =
  process.env.PASEO_HOOK_TOOL || path.join(__dirname, "../paseo_hooks.py");

export function redactEnvPayload(data: unknown): string {
  const entry = {
    timestamp: new Date().toISOString(),
    data,
  };
  return JSON.stringify(entry, (key, value: unknown) => {
    if (key === "env" && value !== null && typeof value === "object") {
      const redacted: Record<string, string> = {};
      for (const name of Object.keys(value as Record<string, unknown>)) {
        redacted[name] = "[redacted]";
      }
      return redacted;
    }
    return value;
  });
}

export function logAndDispatchHook(hook: string, data: unknown): void {
  const serialized = redactEnvPayload(data);
  console.log(JSON.stringify({ hook, timestamp: new Date().toISOString(), payload: JSON.parse(serialized).data }));

  try {
    const child = spawn(
      "python3",
      [PYTHON_HOOK_SCRIPT, "plugin-event", "--hook", hook],
      {
        cwd: PROJECT_ROOT,
        stdio: ["pipe", "ignore", "ignore"],
        detached: false,
      },
    );
    child.stdin.write(serialized);
    child.stdin.end();
    child.on("error", (err) => {
      console.error(`[slpc-lifecycle-hooks] Python hook dispatch error (${hook}):`, err.message);
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`[slpc-lifecycle-hooks] Failed to spawn paseo_hooks.py (${hook}):`, message);
  }
}

export function extractShellCommand(request: unknown): string | null {
  if (!request || typeof request !== "object") {
    return null;
  }
  const req = request as { input?: Record<string, unknown> };
  if (!req.input || typeof req.input !== "object") {
    return null;
  }
  if (typeof req.input.command === "string") {
    return req.input.command;
  }
  if (typeof req.input.cmd === "string") {
    return req.input.cmd;
  }
  return null;
}
