import type { AppConfig } from './types.js';
import type { ResellOSClient } from './resellosClient.js';

export interface ToolContext {
  client: ResellOSClient;
  config: AppConfig;
}
