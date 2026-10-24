import type { PluginClientContext } from "@getpaseo/plugin/client";
import { isSelectableSupervisorRole, syncSupervisorRpc } from "./shared/supervision";

export default function contribute(client: PluginClientContext): () => void {
  let headerRemover: (() => void) | null = null;

  // 1. Command Center: Đặt thread hiện tại làm Supervisor
  const offSetSupervisor = client.addCommandCenterItem({
    id: "set-slppc-supervisor",
    title: "Set this thread as SLPPC Supervisor",
    icon: "ShieldAlert",
    keywords: ["supervisor", "slppc", "room", "spoc"],
    context: "agent",
    async onSelect({ agent, workspace, rpc }) {
      const title = agent.title || "";
      if (!isSelectableSupervisorRole(title) && !isSelectableSupervisorRole(agent.id)) {
        throw new Error("Chỉ thread có vai trò Supervisor mới được nhận thông báo điều phối SLPPC.");
      }

      await rpc(syncSupervisorRpc, {
        enabled: true,
        supervisorAgentId: agent.id,
        supervisorTitle: title || "Supervisor",
        workspaceId: workspace.id,
      });

      // Hiển thị nút Header Bell
      if (headerRemover) headerRemover();
      const btn = client.addHeaderButton({
        id: "slppc-supervisor-indicator",
        workspaceId: workspace.id,
        button: {
          title: "SLPPC Supervisor Active",
          icon: "Bell",
          behavior: {
            kind: "action",
            onPress() {
              client.openSettings("slppc-supervision");
            },
          },
        },
      });
      headerRemover = () => btn.remove();
    },
  });

  // 2. Command Center: Kích hoạt kiểm tra Audit Quy trình SLPPC
  const offAuditFlow = client.addCommandCenterItem({
    id: "run-slppc-audit",
    title: "Run SLPPC Governance & Flow Audit",
    icon: "ShieldCheck",
    keywords: ["audit", "slppc", "governance", "flow"],
    context: "workspace",
    async onSelect() {
      // Cho phép User kích hoạt kiểm tra nhanh từ Command Center
    },
  });

  return () => {
    offSetSupervisor();
    offAuditFlow();
    if (headerRemover) {
      headerRemover();
      headerRemover = null;
    }
  };
}
