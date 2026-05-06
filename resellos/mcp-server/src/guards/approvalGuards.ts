import type { AppConfig } from '../types.js';

export function guardWriteEnabled(config: AppConfig): void {
  if (!config.allowWrites) {
    throw new Error('Writes are disabled in ResellOS MCP configuration.');
  }
}

export function guardPaidToolEnabled(config: AppConfig, confirm?: boolean | null): void {
  if (!config.allowPaidTools && !confirm) {
    throw new Error('Paid tools are disabled. Set RESELLOS_MCP_ALLOW_PAID_TOOLS=true or confirm the call explicitly.');
  }
}
