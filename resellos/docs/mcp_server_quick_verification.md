# ResellOS MCP Server Quick Verification

This packet captures the current local state of the ResellOS MCP server and its safety guardrails.

## 1. Git Identity

Command:

```bash
git -C /Users/admin/CascadeProjects/is44ks-shop rev-parse HEAD
git -C /Users/admin/CascadeProjects/is44ks-shop status --short
git -C /Users/admin/CascadeProjects/is44ks-shop log --oneline -3
```

Output:

```text
e4107a5d9c1e11d124ed56f6090dd437c3cbd57d


e4107a5 Changes
09d3943 Changes
0661451 Changes
```

## 2. MCP Tree

Command:

```bash
find /Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server -maxdepth 3 -type f | sort
```

The raw output is long because it includes `dist/` and `node_modules/`. The MCP-relevant portion of the exact tree output is:

```text
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/.env
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/.env.example
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/.gitignore
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/README.md
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/config.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/guards/approvalGuards.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/guards/costGuards.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/guards/costGuards.test.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/guards/verificationGuards.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/guards/verificationGuards.test.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/index.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/resellosClient.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/toolRegistry.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/toolTypes.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/tools/candidateTools.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/tools/discoveryTools.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/tools/externalResearchTools.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/tools/productTools.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/tools/verificationTools.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/types.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/utils/audit.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/utils/errors.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/utils/validation.js
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/docs/codex_resellos_mcp_setup.md
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/docs/resellos_mcp_tool_reference.md
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/package-lock.json
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/package.json
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/config.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/guards/approvalGuards.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/guards/costGuards.test.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/guards/costGuards.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/guards/verificationGuards.test.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/guards/verificationGuards.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/index.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/resellosClient.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/toolRegistry.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/toolTypes.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/tools/candidateTools.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/tools/discoveryTools.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/tools/externalResearchTools.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/tools/productTools.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/tools/verificationTools.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/types.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/utils/audit.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/utils/errors.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/utils/validation.ts
/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/tsconfig.json
```

## 3. Tool Registry

Source: [resellos/mcp-server/src/toolRegistry.ts](/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/toolRegistry.ts)

Exported tool names:

```text
resellos_get_discovery_board
resellos_create_discovery_idea
resellos_run_quick_scan
resellos_generate_research_tasks
resellos_run_dataforseo_google_shopping
resellos_poll_external_research_job
resellos_list_evidence_candidates
resellos_approve_candidate
resellos_reject_candidate
resellos_capture_manual_evidence
resellos_get_product_cockpit
resellos_run_product_research
resellos_get_next_research_action
resellos_verify_marketplace_evidence
resellos_verify_supplier_source
resellos_verify_competitor_listing
resellos_generate_product_research_report
```

## 4. Backend-Only Client Proof

Source: [resellos/mcp-server/src/resellosClient.ts](/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/resellosClient.ts)

```ts
import type { ResellosErrorPayload } from './types.js';
import { ResellosApiError } from './utils/errors.js';

export class ResellOSClient {
  constructor(private readonly baseUrl: string) {}

  async get<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'GET' });
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'POST',
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  }

  async patch<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'PATCH',
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' });
  }

  private async request<T>(path: string, init: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(init.headers || {}),
      },
    });

    if (!response.ok) {
      let payload: ResellosErrorPayload | undefined;
      try {
        payload = await response.json();
      } catch {
        // ignore
      }
      const text = payload?.message || (await response.text().catch(() => '')) || response.statusText;
      throw new ResellosApiError(response.status, text, payload?.details);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  }
}
```

Proof notes:

- No Postgres client is imported.
- No database connection string exists in this client.
- No raw SQL is present.
- All server access goes through HTTP `fetch(...)` calls to the FastAPI backend.

## 5. Guardrails

### Cost guards

Source: [resellos/mcp-server/src/guards/costGuards.ts](/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/guards/costGuards.ts)

```ts
import type { AppConfig } from '../types.js';
import { ensureOneQuery, ensureWithin } from '../utils/validation.js';

export function guardDataForSeoRequest(config: AppConfig, query: string, maxResults: number): { query: string; maxResults: number } {
  const normalizedQuery = query.trim();
  ensureWithin(maxResults, config.maxDataForSeoResults, 'max_results');
  return {
    query: normalizedQuery,
    maxResults,
  };
}

export function guardQueries(config: AppConfig, queries: string[]): string {
  if (queries.length > config.maxDataForSeoQueries) {
    throw new Error(`Only ${config.maxDataForSeoQueries} query(ies) allowed per run.`);
  }
  return ensureOneQuery(queries);
}
```

### Verification guards

Source: [resellos/mcp-server/src/guards/verificationGuards.ts](/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/guards/verificationGuards.ts)

```ts
import type { AppConfig } from '../types.js';

function hasProof(input: { source_url?: string | null; screenshot_url?: string | null; verification_notes?: string | null }): boolean {
  return Boolean(input.source_url || input.screenshot_url || input.verification_notes);
}

export function guardVerificationApproval(config: AppConfig, input: { confirm?: boolean | null; source_url?: string | null; screenshot_url?: string | null; verification_notes?: string | null }): void {
  if (config.requireApprovalForVerification && !input.confirm) {
    throw new Error('Verification requires explicit confirmation.');
  }
  if (!hasProof(input)) {
    throw new Error('Verification requires source_url, screenshot_url, or verification_notes.');
  }
}

export function guardSupplierVerification(config: AppConfig, input: { confirm?: boolean | null; source_url?: string | null; screenshot_url?: string | null; verification_notes?: string | null; unit_cost?: number | null; estimated_landed_cost?: number | null }): void {
  guardVerificationApproval(config, input);
  if (input.unit_cost == null) {
    throw new Error('Supplier verification requires unit_cost.');
  }
  if (input.estimated_landed_cost == null && !input.verification_notes) {
    throw new Error('Supplier verification requires estimated_landed_cost or explicit shipping note.');
  }
}

export function guardSoldEvidenceVerification(config: AppConfig, input: { confirm?: boolean | null; source_url?: string | null; screenshot_url?: string | null; verification_notes?: string | null; price?: number | null }): void {
  guardVerificationApproval(config, input);
  if (input.price == null) {
    throw new Error('Evidence verification requires a price.');
  }
}
```

### Approval guards

Source: [resellos/mcp-server/src/guards/approvalGuards.ts](/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src/guards/approvalGuards.ts)

```ts
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
```

## 6. Forbidden Tool Search

Command:

```bash
grep -R -n "raw_sql\\|delete_product\\|delete_all\\|bulk_verify\\|READY_FOR_SAMPLE\\|set_final_decision\\|reset_database\\|postgres\\|psql" /Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/src || true
```

Output:

```text
(no matches)
```

## 7. Build / Test / Startup

### Build

Command:

```bash
cd /Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server
npm run build
```

Output:

```text
> resellos-mcp-server@0.1.0 build
> tsc -p tsconfig.json
```

### Test

Command:

```bash
cd /Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server
npm test
```

Output:

```text
> resellos-mcp-server@0.1.0 test
> npm run build && node --test dist/**/*.test.js

> resellos-mcp-server@0.1.0 build
> tsc -p tsconfig.json

TAP version 13
# Subtest: guardQueries allows a single non-empty query
ok 1 - guardQueries allows a single non-empty query
# Subtest: guardQueries rejects multiple queries
ok 2 - guardQueries rejects multiple queries
# Subtest: guardDataForSeoRequest rejects max results above config
ok 3 - guardDataForSeoRequest rejects max results above config
# Subtest: guardVerificationApproval requires proof and confirmation
ok 4 - guardVerificationApproval requires proof and confirmation
# Subtest: guardSoldEvidenceVerification requires price and proof
ok 5 - guardSoldEvidenceVerification requires price and proof
# Subtest: guardSupplierVerification requires unit cost and proof
ok 6 - guardSupplierVerification requires unit cost and proof
1..6
# tests 6
# suites 0
# pass 6
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 31.910709
```

### Startup

Command:

```bash
cd /Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server
npm start
```

Output:

```text
EXIT 0
```

## 8. Codex Config

Source: [~/.codex/config.toml](/Users/admin/.codex/config.toml)

```toml
[mcp_servers.resellos-mcp]
command = "node"
args = ["/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server/dist/index.js"]
cwd = "/Users/admin/CascadeProjects/is44ks-shop/resellos/mcp-server"

[features]
```

## 9. Final Assessment

- Does MCP expose raw DB access? **No**
- Does MCP expose destructive tools? **No**
- Does MCP expose readiness override? **No**
- Are paid tools guarded? **Yes**
- Are verification tools proof-gated? **Yes**
- Is it ready for local Codex testing? **Yes**

## 10. Notes

- The MCP server is a thin HTTP wrapper over the existing ResellOS FastAPI backend.
- Verification and readiness remain owned by the backend app; the MCP server does not write directly to Postgres.
- The backend repository currently has one unrelated modified file outside the MCP work: `resellos/backend/app/schemas/product_schema.py`.
