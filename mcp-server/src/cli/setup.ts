#!/usr/bin/env node
/**
 * MEX MCP Server セットアップCLI
 *
 * 1コマンドでMCPサーバーの設定を完了させるCLI。
 * - メール/パスワードでログイン
 * - APIトークンを取得
 * - ~/.mex/config.json を自動生成
 *
 * 3つのAIレビューすべてが「MCP設定の複雑さ」をCritical Issueとして指摘。
 * 手動でconfig.json作成 + JWTコピーは学生ユーザーの90%が離脱するため実装。
 */
import fs from 'fs';
import os from 'os';
import path from 'path';
import readline from 'readline';
import { fileURLToPath } from 'url';

const DEFAULT_API_URL = 'http://localhost:8000/api';

interface SetupConfig {
  api_url: string;
  email: string;
  password: string;
  ai_tool: string;
}

function createReadlineInterface(): readline.Interface {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
}

function question(rl: readline.Interface, prompt: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      resolve(answer.trim());
    });
  });
}

/**
 * パスワード入力（エコーバック抑制は端末依存のため、
 * Node.js標準のreadlineではプレーンテキスト表示となる）
 */
function questionPassword(rl: readline.Interface, prompt: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      resolve(answer.trim());
    });
  });
}

async function login(apiUrl: string, email: string, password: string): Promise<string> {
  const response = await fetch(`${apiUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`ログイン失敗 (${response.status}): ${text}`);
  }

  const data = (await response.json()) as { access_token: string };
  return data.access_token;
}

async function getApiToken(apiUrl: string, accessToken: string): Promise<string> {
  const response = await fetch(`${apiUrl}/auth/api-token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`APIトークン取得失敗 (${response.status}): ${text}`);
  }

  const data = (await response.json()) as { api_token: string; expires_in_days: number };
  return data.api_token;
}

function writeConfig(apiUrl: string, apiKey: string, aiTool: string): string {
  const mexDir = path.join(os.homedir(), '.mex');
  const configPath = path.join(mexDir, 'config.json');

  if (!fs.existsSync(mexDir)) {
    fs.mkdirSync(mexDir, { recursive: true });
  }

  const config = {
    api_url: apiUrl,
    api_key: apiKey,
    ai_tool: aiTool,
  };

  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  return configPath;
}

async function main() {
  console.log('');
  console.log('=== MEX MCP Server セットアップ ===');
  console.log('');
  console.log('MCPサーバーの設定を自動で行います。');
  console.log('MEXアカウントのメールアドレスとパスワードが必要です。');
  console.log('');

  const rl = createReadlineInterface();

  try {
    // API URL
    const apiUrlInput = await question(
      rl,
      `API URL [${DEFAULT_API_URL}]: `,
    );
    const apiUrl = apiUrlInput || DEFAULT_API_URL;

    // Email
    const email = await question(rl, 'メールアドレス: ');
    if (!email) {
      console.error('エラー: メールアドレスを入力してください');
      process.exit(1);
    }

    // Password
    const password = await questionPassword(rl, 'パスワード: ');
    if (!password) {
      console.error('エラー: パスワードを入力してください');
      process.exit(1);
    }

    // AI Tool
    const aiToolInput = await question(
      rl,
      'AI Tool名 [claude_code]: ',
    );
    const aiTool = aiToolInput || 'claude_code';

    console.log('');
    console.log('ログイン中...');

    // Step 1: Login
    const accessToken = await login(apiUrl, email, password);
    console.log('✓ ログイン成功');

    // Step 2: Get API Token (30-day)
    const apiToken = await getApiToken(apiUrl, accessToken);
    console.log('✓ APIトークン取得成功（30日間有効）');

    // Step 3: Write config
    const configPath = writeConfig(apiUrl, apiToken, aiTool);
    console.log(`✓ 設定ファイル作成: ${configPath}`);

    // Step 4: Show MCP config snippet
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = path.dirname(__filename);
    const serverPath = path.resolve(__dirname, '..', 'index.js');
    console.log('');
    console.log('=== セットアップ完了 ===');
    console.log('');
    console.log('Claude Desktop / Claude Code の MCP 設定に以下を追加してください:');
    console.log('');
    console.log(JSON.stringify(
      {
        mex: {
          command: 'node',
          args: [serverPath],
        },
      },
      null,
      2,
    ));
    console.log('');
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error(`\nエラー: ${message}`);
    process.exit(1);
  } finally {
    rl.close();
  }
}

main();
