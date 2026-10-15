import type { PluginServerContext } from "@getpaseo/plugin/server";
import { extractShellCommand, logAndDispatchHook } from "./server/hook-bridge";

const SLPC_DEFAULT_ENV: Record<string, string> = {
  PASEO_SLPC_HOOK_ACTIVE: "1",
  PASEO_PROJECT_ROOT: "/home/baoltb/Desktop/Paseo_Project",
  PASEO_HOOK_TOOL: "/home/baoltb/Desktop/Paseo_Project/tools/paseo_hooks.py",
  PASEO_RESEARCH_GEN_TOOL: "/home/baoltb/Desktop/Paseo_Project/tools/profile_research_gen.py",
};

const SAFE_AUTO_APPROVE_PATTERN =
  /^(git\s+(status|diff|log|branch)|python3\s+.*tools\/(harness_manager|agent_progress|profile_research_gen|qc_test_generator|query_reader|crm_doc_reader|paseo_hooks|test_harness|test_qc_generator)\.py\b)/;

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
    const nextRequest = {
      ...request,
      env: {
        ...SLPC_DEFAULT_ENV,
        ...request.env,
      },
    };
    logAndDispatchHook("before:agent.create", { request: nextRequest });
    return nextRequest;
  });

  server.before("agent.session_open", ({ request }) => {
    const nextRequest = {
      ...request,
      env: {
        ...SLPC_DEFAULT_ENV,
        ...request.env,
      },
    };
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
