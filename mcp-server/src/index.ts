#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

import { loadConfig, loadLocalConfig } from './config.js';
import { MexApiClient } from './api-client.js';
import { saveDocumentTool, handleSaveDocument } from './tools/record-activity.js';
import { listProjectsTool, handleListProjects } from './tools/list-projects.js';
import { getProjectContextTool, handleGetProjectContext } from './tools/get-context.js';

async function main() {
  const config = loadConfig();
  const localConfig = loadLocalConfig();
  const client = new MexApiClient(config);

  const server = new Server(
    {
      name: 'mex-mcp-server',
      version: '0.2.0',
    },
    {
      capabilities: {
        tools: {},
      },
    },
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [saveDocumentTool, listProjectsTool, getProjectContextTool],
    };
  });

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case 'save_document': {
          const result = await handleSaveDocument(client, config, args as any, localConfig);
          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }
        case 'list_projects': {
          const result = await handleListProjects(client);
          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify({ projects: result }, null, 2),
              },
            ],
          };
        }
        case 'get_project_context': {
          const projectId = (args as { project_id?: string }).project_id;
          const result = await handleGetProjectContext(client, projectId, localConfig);
          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }
        default:
          return {
            content: [
              {
                type: 'text',
                text: `Unknown tool: ${name}`,
              },
            ],
            isError: true,
          };
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      return {
        content: [
          {
            type: 'text',
            text: message,
          },
        ],
        isError: true,
      };
    }
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error('MCP server failed to start', error);
  process.exit(1);
});
