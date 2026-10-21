import type { PluginServerContext } from "@getpaseo/plugin/server";
import { extractShellCommand, logAndDispatchHook } from "./server/hook-bridge";

const SLPC_DEFAULT_ENV: Record<string, string> = {
  PASEO_SLPC_HOOK_ACTIVE: "1",
  PASEO_PROJECT_ROOT: "/Users/bao312/Desktop/Room_Agent",
  PASEO_HOOK_TOOL: "/Users/bao312/Desktop/Room_Agent/tools/paseo_hooks.py",
  PASEO_RESEARCH_GEN_TOOL: "/Users/bao312/Desktop/Room_Agent/tools/profile_research_gen.py",
};

const SAFE_AUTO_APPROVE_PATTERN =
  /^(git\s+(status|diff|log|branch)|python3\s+.*tools\/(harness_manager|agent_progress|profile_research_gen|qc_test_generator|query_reader|crm_doc_reader|paseo_hooks|test_harness|test_qc_generator)\.py\b)/;

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
  // 1. Workspace Lifecycle Hooks
  server.before("workspace.create", ({ request }) => {
    logAndDispatchHook("before:workspace.create", { request });
    return request;
  });

  server.on("workspace.created", (event) => {
    logAndDispatchHook("workspace.created", event);
  });

  server.on("workspace.archived", (event) => {
    logAndDispatchHook("workspace.archived", event);
  });

  // 2. Agent Creation & Session Open Hooks (Before + After)
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

  server.on("agent.created", (event) => {
    logAndDispatchHook("agent.created", event);
  });

  // 3. Turn & Permission Lifecycle Hooks
  server.on("agent.turn_started", (event) => {
    logAndDispatchHook("agent.turn_started", event);
  });

  server.on("agent.turn_ended", (event) => {
    logAndDispatchHook("agent.turn_ended", event);
  });

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

  server.on("agent.permission_resolved", (event) => {
    logAndDispatchHook("agent.permission_resolved", event);
  });

  // 4. Archive Hook
  server.on("agent.archived", (event) => {
    logAndDispatchHook("agent.archived", event);
  });

  return () => {};
}
