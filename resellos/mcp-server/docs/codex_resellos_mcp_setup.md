# Codex + ResellOS MCP Setup

## Register the server

Point your MCP client at:

### Codex Desktop config snippet

Add this block to your Codex config file, usually `~/.codex/config.toml`:

```toml
[mcp_servers.resellos-mcp]
command = "node"
args = ["/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/index.js"]
cwd = "/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server"
```

Then restart Codex Desktop so the tool endpoint appears.

### Manual run

```bash
cd /Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server
npm install
npm run build
npm run start
```

## Backend requirement

ResellOS FastAPI should be running locally, usually at:

```text
http://localhost:8000
```

## Safety notes

- Do not enable raw SQL access.
- Do not expose destructive tools.
- Do not allow any MCP tool to set `READY_FOR_SAMPLE`.
- Treat DataForSEO as active market presence only.
- Treat verified sold demand as `USER_VERIFIED` only.

## Example operating flow

1. Read discovery board.
2. Read current watchlist product cockpit.
3. Get next research action.
4. Run one controlled Google Shopping query.
5. Poll the job.
6. Review candidates.
7. Approve only proof-backed candidates.
8. Run product research.
9. Read the resulting next action.
