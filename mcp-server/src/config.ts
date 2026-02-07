import fs from 'fs';
import os from 'os';
import path from 'path';

export interface MexConfig {
  api_url: string;
  api_key: string;
  ai_tool?: string;
}

export function loadConfig(): MexConfig {
  const configPath = path.join(os.homedir(), '.mex', 'config.json');

  if (!fs.existsSync(configPath)) {
    throw new Error(`Config not found: ${configPath}`);
  }

  const raw = fs.readFileSync(configPath, 'utf-8');
  const parsed = JSON.parse(raw) as MexConfig;

  if (!parsed.api_url || !parsed.api_key) {
    throw new Error('api_url と api_key が必要です');
  }

  return {
    api_url: parsed.api_url.replace(/\/$/, ''),
    api_key: parsed.api_key,
    ai_tool: parsed.ai_tool || 'claude_code',
  };
}
