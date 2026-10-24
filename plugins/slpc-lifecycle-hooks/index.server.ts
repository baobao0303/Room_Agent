import type { PluginServerContext } from "@getpaseo/plugin/server";
import path from "node:path";
import { extractShellCommand, logAndDispatchHook } from "./server/hook-bridge";
import { SlppcObserver } from "./server/observer";

const PROJECT_ROOT = process.env.PASEO_PROJECT_ROOT || path.resolve(__dirname, "../..");
const PLUGIN_DIR = path.resolve(__dirname);

const SLPC_DEFAULT_ENV: Record<string, string> = {
  PASEO_SLPC_HOOK_ACTIVE: "1",
  PASEO_PROJECT_ROOT: PROJECT_ROOT,
  PASEO_HOOK_TOOL: path.join(PLUGIN_DIR, "paseo_hooks.py"),
  PASEO_RESEARCH_GEN_TOOL: path.join(PROJECT_ROOT, "tools/profile_research_gen.py"),
};

const SAFE_AUTO_APPROVE_PATTERN =
  /^(git\s+(status|diff|log|branch)|python3\s+.*(tools\/|scripts\/|plugins\/slpc-lifecycle-hooks\/)[\w_]+\.py\b|python3\s+-m\s+unittest\b|orca\s+terminal\s+(list|read|show|status|wait)\b)/;

function enforceSupervisorArgonModel<T extends Record<string, unknown>>(req: T): T {
  const title = String(req.title ?? (req.config as Record<string, unknown> | undefined)?.title ?? "");
  const isSupervisor = /^supervisor\b/i.test(title.trim());
  if (!isSupervisor) {
    return req;
  }
  const currentModel = String(req.model ?? (req.config as Record<string, unknown> | undefined)?.model ?? "");
  const targetModel = currentModel.startsWith("gemini-3.8-flash") ? currentModel : "gemini-3.8-flash-high";
  const next: Record<string, unknown> = {
    ...req,
    provider: "antigravity",
    model: targetModel,
  };
  if (req.config && typeof req.config === "object") {
    next.config = {
      ...(req.config as Record<string, unknown>),
      provider: "antigravity",
      model: targetModel,
      modeId: "full-access",
    };
  }
  return next as T;
}

export default function contribute(server: PluginServerContext) {
  const observer = new SlppcObserver(server);
  const unregisterObserver = observer.register();

  // 1. Agent Creation & Session Open Hooks (Bootstrap Gate)
  server.before("agent.create", ({ request }) => {
    const nextRequest = enforceSupervisorArgonModel({
      ...request,
      env: {
        ...SLPC_DEFAULT_ENV,
        ...request.env,
      },
    });
    logAndDispatchHook("before:agent.create", { request: nextRequest });
    return nextRequest;
  });

  server.before("agent.session_open", ({ request }) => {
    const nextRequest = enforceSupervisorArgonModel({
      ...request,
      env: {
        ...SLPC_DEFAULT_ENV,
        ...request.env,
      },
    });
    logAndDispatchHook("before:agent.session_open", { request: nextRequest });
    return nextRequest;
  });

  // 2. Permission & Security Guard (Friction Gate: Auto-Allow Safe / Hard-Deny Destructive)
  server.on("agent.permission_requested", async (event, context) => {
    logAndDispatchHook("agent.permission_requested", event);

    const command = extractShellCommand(event.request);
    if (command === null) {
      return;
    }

    const agent = context.paseo.agents.ref(event.agent.id);
    if (/\brm\s+-rf\s+\/(\s|$)/.test(command)) {
      await agent.respondToPermission({
        requestId: event.request.id,
        response: {
          behavior: "deny",
          message: "Blocked destructive root deletion via slpc-lifecycle-hooks.",
        },
      });
      return;
    }

    if (SAFE_AUTO_APPROVE_PATTERN.test(command.trim())) {
      await agent.respondToPermission({
        requestId: event.request.id,
        response: { behavior: "allow" },
      });
    }
  });

  // 3. Turn Ended (Handoff & Progress Synchronization Gate)
  server.on("agent.turn_ended", (event) => {
    logAndDispatchHook("agent.turn_ended", event);
  });

  // 4. Agent Archived (Ephemeral Cleanup & Resource Reclamation Gate)
  server.on("agent.archived", (event) => {
    logAndDispatchHook("agent.archived", event);
  });

  return () => {
    unregisterObserver();
  };
}
