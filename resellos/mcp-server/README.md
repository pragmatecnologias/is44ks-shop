# ResellOS MCP Server

The ResellOS MCP Server is a thin, guarded MCP wrapper over the existing ResellOS FastAPI backend.

What it can do:
- Read discovery, opportunity, and cockpit state
- Create discovery ideas
- Run quick scans and task generation
- Run and poll controlled DataForSEO Google Shopping research
- Create and review evidence candidates
- Capture manual evidence as candidates
- Run product research
- Generate research reports
- Verify evidence, suppliers, and competitor listings when proof exists

What it cannot do:
- Bypass ResellOS readiness rules
- Write directly to the database
- Mark a product sample-ready
- Bulk verify evidence
- Run raw SQL
- Delete or reset product data
- Ignore paid-tool guardrails

## Setup

1. Install dependencies:

```bash
cd resellos/mcp-server
npm install
```

2. Build:

```bash
npm run build
```

3. Start:

```bash
npm run start
```

## Codex Desktop registration

Add this to `~/.codex/config.toml`:

```toml
[mcp_servers.resellos-mcp]
command = "node"
args = ["/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/index.js"]
cwd = "/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server"
```

Restart Codex Desktop afterward so the server appears as an available tool endpoint.

## Environment

Create `.env` from `.env.example` and set:

- `RESELLOS_API_BASE_URL`
- `RESELLOS_MCP_ACTOR`
- `RESELLOS_MCP_ALLOW_WRITES`
- `RESELLOS_MCP_ALLOW_PAID_TOOLS`
- `RESELLOS_MCP_MAX_DATAFORSEO_RESULTS`
- `RESELLOS_MCP_MAX_DATAFORSEO_QUERIES`

## Tool behavior

- Read-only tools are safe to run automatically.
- Write tools require the backend to accept the write.
- Paid tools are clamped to one query and ten results by default.
- Verification tools require proof fields and backend confirmation.

## Local backend

The MCP server expects ResellOS to be running locally at `http://localhost:8000` unless overridden.

## Troubleshooting

- If the backend is offline, tools return normalized API errors.
- If a paid tool is disabled, the tool call returns a guardrail error.
- If a verification proof is missing, the tool call is rejected before the backend write.
