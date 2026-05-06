import type { ResellosErrorPayload } from '../types.js';

export class ResellosApiError extends Error {
  status: number;
  details: unknown;

  constructor(status: number, message: string, details?: unknown) {
    super(message);
    this.name = 'ResellosApiError';
    this.status = status;
    this.details = details;
  }
}

export function toErrorPayload(error: unknown): ResellosErrorPayload {
  if (error instanceof ResellosApiError) {
    return {
      ok: false,
      status: error.status,
      message: error.message,
      details: error.details,
    };
  }

  if (error instanceof Error) {
    return {
      ok: false,
      status: 500,
      message: error.message,
      details: { name: error.name },
    };
  }

  return {
    ok: false,
    status: 500,
    message: 'Unknown error',
    details: error,
  };
}
