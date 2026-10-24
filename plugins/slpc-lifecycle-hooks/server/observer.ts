import type { PluginHookContext, PluginServerContext } from "@getpaseo/plugin/server";
import { supervisionSettings, syncSupervisorRpc, type SupervisorSyncInput } from "../shared/supervision";

export interface ObserverConfig {
  endpoint: string;
  model: string;
  alertConfidenceThreshold: number;
  supervisorAgentId: string | null;
}

export function bounded<T>(work: Promise<T>, timeoutMs = 15_000): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("SDK operation timed out")), timeoutMs);
    work
      .then((val) => {
        clearTimeout(timer);
        resolve(val);
      })
      .catch((err) => {
        clearTimeout(timer);
        reject(err);
      });
  });
}

export class SlppcObserver {
  private activeSupervisorId: string | null = null;
  private readonly leads = new Set<string>();
  private readonly peers = new Map<string, string>(); // peerId -> leadId

  constructor(private readonly server: PluginServerContext) {}

  public register(): () => void {
    // 1. Đăng ký settings schema cho Paseo UI
    this.server.registerSettings(supervisionSettings);

    // 2. Xử lý RPC đồng bộ Supervisor Thread
    this.server.handle(syncSupervisorRpc, async (input: SupervisorSyncInput) => {
      if (input.enabled && input.supervisorAgentId) {
        this.activeSupervisorId = input.supervisorAgentId;
        return {
          status: "active",
          supervisorAgentId: this.activeSupervisorId,
        };
      }
      this.activeSupervisorId = null;
      return {
        status: "disabled",
        supervisorAgentId: null,
      };
    });

    return () => {
      this.activeSupervisorId = null;
      this.leads.clear();
      this.peers.clear();
    };
  }

  public getActiveSupervisorId(): string | null {
    return this.activeSupervisorId;
  }
}
