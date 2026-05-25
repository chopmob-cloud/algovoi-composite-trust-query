import { describe, it, expect } from 'vitest';
import { existsSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

import { canonicalize, sha256Jcs } from '@algovoi/substrate';
import {
  TRUST_OUTCOMES,
  CtqResponseError,
  buildCtqResponse,
} from '../src/composite-trust-query.js';

describe('TRUST_OUTCOMES', () => {
  it('is exactly the 4-state enum', () => {
    expect([...TRUST_OUTCOMES]).toEqual([
      'TRUSTED',
      'PROVISIONAL',
      'INSUFFICIENT_EVIDENCE',
      'UNTRUSTED',
    ]);
  });
});

describe('buildCtqResponse', () => {
  const base = {
    trust_outcome: 'TRUSTED',
    chain_ref:
      'sha256:0dd5d0b76c9b9281fdeb2509ad38ab132b16a17385ca01d976ff9e6e12563a0f',
    query_ref:
      'sha256:8b7df143d91c716ecfa5fc1730022f6b421b05cedee8fd52b1fc65a96030ad52',
    ctq_timestamp_ms: 1716494400000,
    verifier_did: 'did:web:api.algovoi.co.uk',
    jurisdiction_flags: ['UK', 'EU'],
  };

  it('builds canonical response', () => {
    const r = buildCtqResponse(base);
    expect(r).toEqual({ ...base, canon_version: 'jcs-rfc8785-v1' });
  });

  it('four distinct outcomes produce four distinct hashes', () => {
    const hashes = new Set<string>();
    for (const outcome of TRUST_OUTCOMES) {
      const r = buildCtqResponse({ ...base, trust_outcome: outcome });
      hashes.add(sha256Jcs(r));
    }
    expect(hashes.size).toBe(4);
  });

  it('rejects invalid outcome', () => {
    expect(() =>
      buildCtqResponse({ ...base, trust_outcome: 'MAYBE' }),
    ).toThrow(/trust_outcome must be one of/);
  });

  it('rejects float timestamp', () => {
    expect(() =>
      buildCtqResponse({ ...base, ctq_timestamp_ms: 1716494400000.5 }),
    ).toThrow(/Substrate Rule 2/);
  });

  it('rejects string timestamp', () => {
    expect(() =>
      buildCtqResponse({
        ...base,
        ctq_timestamp_ms: '2024-05-23T12:00:00Z' as unknown as number,
      }),
    ).toThrow(/Substrate Rule 2/);
  });

  it('canon_version defaults to jcs-rfc8785-v1', () => {
    expect(buildCtqResponse(base).canon_version).toBe('jcs-rfc8785-v1');
  });

  it('jurisdiction order is byte-load-bearing', () => {
    const ukEu = buildCtqResponse({ ...base, jurisdiction_flags: ['UK', 'EU'] });
    const euUk = buildCtqResponse({ ...base, jurisdiction_flags: ['EU', 'UK'] });
    expect(sha256Jcs(ukEu)).not.toBe(sha256Jcs(euUk));
  });
});

describe('Conformance vector reproduction', () => {
  const VECTOR_PATH =
    'C:/algo/algovoi-jcs-conformance-vectors/vectors/composite_trust_query_v1/composite_trust_query_v1.json';

  it('reproduces vectors 001 to 005 byte-identical', () => {
    if (!existsSync(VECTOR_PATH)) return;
    const data = JSON.parse(readFileSync(VECTOR_PATH, 'utf-8'));
    for (const v of data.vectors) {
      if (!v.response) continue;
      const canon = canonicalize(v.response);
      const canonBytes = Buffer.from(canon, 'utf-8');
      expect(canonBytes.toString('base64')).toBe(v.expected_jcs_bytes_b64);
      expect(createHash('sha256').update(canonBytes).digest('hex')).toBe(
        v.expected_content_hash,
      );
    }
  });
});
