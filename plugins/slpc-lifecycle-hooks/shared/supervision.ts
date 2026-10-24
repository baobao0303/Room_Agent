import { defineRpc, defineSettings } from "@getpaseo/plugin";
import { z } from "zod";

export const SUPERVISOR_ROLES = ["Supervisor", "supervisor", "codex-supervisor"];

export const supervisionSettings = defineSettings({
  id: "slppc-supervision",
  scope: "host",
  version: 1,
  schema: z.object({
    enabled: z.boolean().default(true),
    supervisorAgentId: z.string().trim().min(1).nullable().default(null),
    supervisorTitle: z.string().trim().min(1).nullable().default(null),
    workspaceId: z.string().trim().min(1).nullable().default(null),
  }),
});

export type SupervisionSettings = z.output<typeof supervisionSettings.schema>;

export function isSelectableSupervisorRole(titleOrProvider: string | null | undefined): boolean {
  if (!titleOrProvider) return false;
  const lower = titleOrProvider.toLowerCase();
  return lower.includes("supervisor");
}

export const syncSupervisorRpc = defineRpc({
  name: "slppc.supervisor.sync",
  input: z.object({
    enabled: z.boolean(),
    supervisorAgentId: z.string().nullable(),
    supervisorTitle: z.string().nullable(),
    workspaceId: z.string().nullable(),
  }),
  output: z.object({
    status: z.enum(["active", "disabled", "updated"]),
    supervisorAgentId: z.string().nullable(),
  }),
});

export type SupervisorSyncInput = z.output<typeof syncSupervisorRpc.input>;
