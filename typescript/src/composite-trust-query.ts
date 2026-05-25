/**
 * Composite trust query response shape -- verifier-side categorical
 * conclusion over an audit chain, under the JCS RFC 8785
 * canonicalisation discipline.
 *
 * Specified in IETF Internet-Draft
 * draft-hopley-x402-composite-trust-query-00 (Independent Submission,
 * Informational; AlgoVoi-authored).
 *
 * Closed four-element enumeration {TRUSTED, PROVISIONAL,
 * INSUFFICIENT_EVIDENCE, UNTRUSTED} captures the genuinely four-state
 * decision space: proceed, proceed-with-caution, hold-pending-more-data,
 * halt.
 *
 * Composes above compliance, settlement, cancellation, and refund
 * receipt formats under the shared canonicalisation pin.
 */

import { CANON_VERSION } from '@algovoi/substrate';

export const TRUST_OUTCOMES = [
  'TRUSTED',
  'PROVISIONAL',
  'INSUFFICIENT_EVIDENCE',
  'UNTRUSTED',
] as const;
export type TrustOutcome = (typeof TRUST_OUTCOMES)[number];

export class CtqResponseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CtqResponseError';
  }
}

export interface CtqResponse {
  canon_version: string;
  chain_ref: string;
  ctq_timestamp_ms: number;
  jurisdiction_flags: string[];
  query_ref: string;
  trust_outcome: TrustOutcome;
  verifier_did: string;
}

export interface BuildCtqResponseInput {
  trust_outcome: string;
  chain_ref: string;
  query_ref: string;
  ctq_timestamp_ms: number;
  verifier_did: string;
  jurisdiction_flags: string[];
  canon_version?: string;
}

function requireNonEmptyString(field: string, value: unknown): string {
  if (typeof value !== 'string' || value.length === 0) {
    throw new CtqResponseError(`${field} must be a non-empty string`);
  }
  return value;
}

function requireIntTimestampMs(value: unknown): number {
  if (typeof value !== 'number') {
    throw new CtqResponseError(
      `ctq_timestamp_ms must be epoch-millisecond integer (Substrate Rule 2), got ${typeof value}`,
    );
  }
  if (!Number.isFinite(value) || !Number.isInteger(value)) {
    throw new CtqResponseError(
      `ctq_timestamp_ms must be epoch-millisecond integer (Substrate Rule 2), got ${value}`,
    );
  }
  if (value < 0) {
    throw new CtqResponseError(
      `ctq_timestamp_ms must be non-negative, got ${value}`,
    );
  }
  return value;
}

function requireJurisdictionFlags(value: unknown): string[] {
  if (!Array.isArray(value)) {
    throw new CtqResponseError(
      `jurisdiction_flags must be array, got ${typeof value}`,
    );
  }
  for (let i = 0; i < value.length; i++) {
    const code = value[i];
    if (typeof code !== 'string' || code.length === 0) {
      throw new CtqResponseError(
        `jurisdiction_flags[${i}] must be a non-empty string`,
      );
    }
  }
  return [...value] as string[];
}

/**
 * Build a validated composite trust query response.
 *
 * trust_outcome MUST be one of TRUSTED, PROVISIONAL,
 * INSUFFICIENT_EVIDENCE, UNTRUSTED.
 *
 * chain_ref is a content-addressed reference (sha256:<hex>) to the
 * root of the audit chain the verifier walked.
 *
 * query_ref is a content-addressed reference to the canonical bytes
 * of the query that was answered. Query format is opaque to this
 * response shape.
 *
 * jurisdiction_flags is treated as ordered.
 * ctq_timestamp_ms MUST be integer (Substrate Rule 2).
 */
export function buildCtqResponse(
  input: BuildCtqResponseInput,
): CtqResponse {
  if (!TRUST_OUTCOMES.includes(input.trust_outcome as TrustOutcome)) {
    throw new CtqResponseError(
      `trust_outcome must be one of ${JSON.stringify([...TRUST_OUTCOMES])}, got ${JSON.stringify(input.trust_outcome)}`,
    );
  }

  return {
    canon_version: requireNonEmptyString(
      'canon_version',
      input.canon_version ?? CANON_VERSION,
    ),
    chain_ref: requireNonEmptyString('chain_ref', input.chain_ref),
    ctq_timestamp_ms: requireIntTimestampMs(input.ctq_timestamp_ms),
    jurisdiction_flags: requireJurisdictionFlags(input.jurisdiction_flags),
    query_ref: requireNonEmptyString('query_ref', input.query_ref),
    trust_outcome: input.trust_outcome as TrustOutcome,
    verifier_did: requireNonEmptyString('verifier_did', input.verifier_did),
  };
}
