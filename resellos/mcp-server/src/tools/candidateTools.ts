import type { AppConfig, CandidateApproveInput, ManualCaptureInput, ToolResult } from '../types.js';
import { buildAudit } from '../utils/audit.js';
import type { ResellOSClient } from '../resellosClient.js';
import { guardWriteEnabled } from '../guards/approvalGuards.js';

export async function listEvidenceCandidates(client: ResellOSClient, input: { idea_id?: string; product_id?: string; job_id?: string; review_status?: string }, config: AppConfig): Promise<ToolResult> {
  const params = new URLSearchParams();
  if (input.idea_id) params.set('idea_id', input.idea_id);
  if (input.product_id) params.set('product_id', input.product_id);
  if (input.job_id) params.set('job_id', input.job_id);
  if (input.review_status) params.set('review_status', input.review_status);
  const path = `/api/evidence-candidates${params.toString() ? `?${params.toString()}` : ''}`;
  const candidates = await client.get<any[]>(path);
  return {
    ok: true,
    data: { candidates },
    summary: `Loaded ${candidates.length} evidence candidate(s).`,
    warnings: [],
    next_recommended_tool: candidates.length ? 'resellos_approve_candidate' : 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_list_evidence_candidates', config.actor, input as Record<string, unknown>),
  };
}

export async function approveCandidate(client: ResellOSClient, input: CandidateApproveInput, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  if (config.requireApprovalForPaidTools && !input.confirm) {
    throw new Error('Approval requires confirmation in this MCP configuration.');
  }
  const response = await client.post<any>(`/api/evidence-candidates/${input.candidate_id}/approve`, {
    approve_as: input.approve_as,
    task_id: input.task_id ?? undefined,
    product_id: input.product_id ?? undefined,
    notes: input.notes ?? undefined,
  });
  return {
    ok: true,
    data: response,
    summary: `Approved candidate ${input.candidate_id} as ${input.approve_as}.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_approve_candidate', config.actor, input as unknown as Record<string, unknown>),
  };
}

export async function rejectCandidate(client: ResellOSClient, input: { candidate_id: string; reason?: string }, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  const response = await client.post<any>(`/api/evidence-candidates/${input.candidate_id}/reject`, {
    notes: input.reason ?? undefined,
  });
  return {
    ok: true,
    data: response,
    summary: `Rejected candidate ${input.candidate_id}.`,
    warnings: [],
    next_recommended_tool: 'resellos_list_evidence_candidates',
    audit: buildAudit('resellos_reject_candidate', config.actor, input as unknown as Record<string, unknown>),
  };
}

export async function captureManualEvidence(client: ResellOSClient, input: ManualCaptureInput, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  const formData = new FormData();
  if (input.idea_id) formData.set('idea_id', input.idea_id);
  if (input.product_id) formData.set('product_id', input.product_id);
  formData.set('capture_type', input.capture_type);
  if (input.url) formData.set('url', input.url);
  if (input.pasted_text) formData.set('pasted_text', input.pasted_text);
  if (input.notes) formData.set('notes', input.notes);
  const response = await fetch(`${config.apiBaseUrl}/api/capture/manual`, { method: 'POST', body: formData });
  if (!response.ok) {
    throw new Error(`Manual capture failed with HTTP ${response.status}`);
  }
  const json = await response.json();
  return {
    ok: true,
    data: json,
    summary: `Captured manual evidence candidate for ${input.capture_type}.`,
    warnings: [],
    next_recommended_tool: 'resellos_list_evidence_candidates',
    audit: buildAudit('resellos_capture_manual_evidence', config.actor, input as unknown as Record<string, unknown>),
  };
}
