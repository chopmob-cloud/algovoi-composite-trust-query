# algovoi-composite-trust-query

[![PyPI](https://img.shields.io/pypi/v/algovoi-composite-trust-query?label=PyPI)](https://pypi.org/project/algovoi-composite-trust-query/)
[![npm](https://img.shields.io/npm/v/@algovoi/composite-trust-query?label=npm)](https://www.npmjs.com/package/@algovoi/composite-trust-query)
[![Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-green)](./LICENSE)
[![IETF I-D](https://img.shields.io/badge/companion%20IETF%20I--D-draft--hopley--x402--composite--trust--query--00-blue)](https://datatracker.ietf.org/doc/draft-hopley-x402-composite-trust-query/)

AlgoVoi-authored reference implementation for the composite trust
query response format specified in IETF Internet-Draft
[`draft-hopley-x402-composite-trust-query`](https://datatracker.ietf.org/doc/draft-hopley-x402-composite-trust-query/)
(Independent Submission, Informational).

Verifier-side categorical conclusion over an audit chain composed of
compliance, settlement, cancellation, and refund receipts. Closed
four-element enumeration `{TRUSTED, PROVISIONAL,
INSUFFICIENT_EVIDENCE, UNTRUSTED}` captures the operationally-distinct
four-state decision space: proceed, proceed-with-caution,
hold-pending-more-data, halt.

Top-of-stack format above the four AlgoVoi receipt formats under the
shared canonicalisation discipline
([`urn:x402:canonicalisation:jcs-rfc8785-v1`](https://datatracker.ietf.org/doc/draft-hopley-x402-canonicalisation-jcs-v1/)).

Python and TypeScript reference implementations, byte-for-byte
parity, Apache 2.0.

## Lifecycle position

```
admission     settlement     cancellation    refund (if owed)
compliance -> settlement  -> cancellation -> refund
receipt       attestation    receipt         receipt
                              |
                              v   (chain_ref)
                          CTQ response (TRUSTED | PROVISIONAL | INSUFFICIENT_EVIDENCE | UNTRUSTED)
```

A verifier walks the audit chain, applies a structured query, and
emits a single composite-trust-claim response anchoring the chain by
its content-addressed root. Regulators, dashboards, and downstream
agents consume one byte-deterministic statement rather than
re-walking the underlying chain. The chain remains independently
verifiable at the `chain_ref` content-address.

## Packages

| Language | Package | Install |
|---|---|---|
| Python | [`algovoi-composite-trust-query`](https://pypi.org/project/algovoi-composite-trust-query/) | `pip install algovoi-composite-trust-query` |
| TypeScript | [`@algovoi/composite-trust-query`](https://www.npmjs.com/package/@algovoi/composite-trust-query) | `npm install @algovoi/composite-trust-query` |

Both depend on `algovoi-substrate` / `@algovoi/substrate` for the JCS
canonicalisation primitive.

## Quick start

### Python

```python
from algovoi_composite_trust_query import build_ctq_response
from algovoi_substrate import sha256_jcs

r = build_ctq_response(
    trust_outcome="TRUSTED",
    chain_ref="sha256:0dd5d0b76c9b9281fdeb2509ad38ab132b16a17385ca01d976ff9e6e12563a0f",
    query_ref="sha256:8b7df143d91c716ecfa5fc1730022f6b421b05cedee8fd52b1fc65a96030ad52",
    ctq_timestamp_ms=1716494400000,
    verifier_did="did:web:api.algovoi.co.uk",
    jurisdiction_flags=["UK", "EU"],
)
print(sha256_jcs(dict(r)))
```

### TypeScript

```typescript
import { buildCtqResponse } from "@algovoi/composite-trust-query";
import { sha256Jcs } from "@algovoi/substrate";

const r = buildCtqResponse({
  trust_outcome: "TRUSTED",
  chain_ref:
    "sha256:0dd5d0b76c9b9281fdeb2509ad38ab132b16a17385ca01d976ff9e6e12563a0f",
  query_ref:
    "sha256:8b7df143d91c716ecfa5fc1730022f6b421b05cedee8fd52b1fc65a96030ad52",
  ctq_timestamp_ms: 1716494400000,
  verifier_did: "did:web:api.algovoi.co.uk",
  jurisdiction_flags: ["UK", "EU"],
});
console.log(sha256Jcs(r));
```

## Response format

Seven-field JSON object canonicalised under RFC 8785 (JCS):

| Field | Type | Description |
|---|---|---|
| `canon_version` | string | `jcs-rfc8785-v1` |
| `chain_ref` | string | `sha256:<hex>` reference to audit chain root |
| `ctq_timestamp_ms` | integer | Epoch ms (Substrate Rule 2) |
| `jurisdiction_flags` | ordered array | ISO-3166-1 codes; primary jurisdiction first |
| `query_ref` | string | `sha256:<hex>` reference to the canonical bytes of the query that was answered |
| `trust_outcome` | string (closed enum) | `TRUSTED` / `PROVISIONAL` / `INSUFFICIENT_EVIDENCE` / `UNTRUSTED` |
| `verifier_did` | string | DID URI of the verifier |

## Closed enumeration: `trust_outcome`

| Value | Semantic | Operator action |
|---|---|---|
| `TRUSTED` | Verified chain answers the query affirmatively. All anchored receipts valid, present, consistent. No revocation, reversal, or compliance-forced termination. | Proceed under asserted trust posture. |
| `PROVISIONAL` | Chain partially complete; some receipts in `PENDING_FINALITY` or analogous non-terminal state. | Proceed cautiously; re-query after pending events finalise. |
| `INSUFFICIENT_EVIDENCE` | Chain does not contain enough evidence to answer the query (missing segments, external-state references, undereferenceable pointers). | Gather more evidence; do not proceed under TRUSTED. |
| `UNTRUSTED` | Chain contains evidence that negates the query (compliance-forced termination, settled-then-reversed transaction, REJECTED refund, expired mandate). | Halt the action the query was framed to authorise. |

The four-value enum is byte-load-bearing under RFC 8785: each value
produces a byte-distinct `content_hash`. Collapsing to three values
loses the operationally-distinct INSUFFICIENT_EVIDENCE state
("we couldn't verify either way") from UNTRUSTED ("we verified and
the answer is no"), which matters for operator dashboards, regulator
reporting, and downstream automated decision-making.

## Conformance vectors

8 byte-level reference vectors + 7 pair invariants + 3 chain invariants at [`vectors/composite_trust_query_v1/`](https://github.com/chopmob-cloud/algovoi-jcs-conformance-vectors/tree/main/vectors/composite_trust_query_v1).

## Companion IETF Internet-Draft

[`draft-hopley-x402-composite-trust-query`](https://datatracker.ietf.org/doc/draft-hopley-x402-composite-trust-query/) (Independent Submission, Informational). AlgoVoi-authored. Normatively references [`draft-hopley-x402-canonicalisation-jcs-v1`](https://datatracker.ietf.org/doc/draft-hopley-x402-canonicalisation-jcs-v1/). Welcomes downstream-adopter contributions per the Appendix C "Known Adopters" pattern.

## What this is NOT

- **Not a receipt.** Receipts record events that happened; a CTQ response records a verifier's categorical conclusion over an event chain. Receipts are emitted by participants in the event; CTQ responses are emitted by verifiers reading the chain.
- **Not the query itself.** The query that was asked is identified by `query_ref` (content-addressed). The query format is opaque to the response format; callers MAY use any structured-question encoding.
- **Not a chain-finality model.** The verifier applies whatever finality semantics its risk model requires; the response records the verifier's categorical conclusion, not the underlying finality model.

## Related AlgoVoi packages

| Package | Purpose |
|---|---|
| [`algovoi-substrate`](https://pypi.org/project/algovoi-substrate/) / [`@algovoi/substrate`](https://www.npmjs.com/package/@algovoi/substrate) | JCS RFC 8785 canonicalisation, `action_ref`, compliance receipts |
| [`algovoi-settlement-attestation`](https://pypi.org/project/algovoi-settlement-attestation/) / [`@algovoi/settlement-attestation`](https://www.npmjs.com/package/@algovoi/settlement-attestation) | Settlement attestation |
| [`algovoi-refund-receipt`](https://pypi.org/project/algovoi-refund-receipt/) / [`@algovoi/refund-receipt`](https://www.npmjs.com/package/@algovoi/refund-receipt) | Refund receipt |
| [`@algovoi/cancellation-receipt`](https://www.npmjs.com/package/@algovoi/cancellation-receipt) | Mandate cancellation receipt |
| **`algovoi-composite-trust-query`** / `@algovoi/composite-trust-query` | **This package.** Top-of-stack verifier response format |

## Conformance to the canonicalisation discipline

This package emits composite-trust-query responses pinned to `canon_version: jcs-rfc8785-v1` on every emitted response. The pin is in-band; downstream consumers (including [`algovoi-audit-verifier`](https://pypi.org/project/algovoi-audit-verifier/) and any conformant third-party verifier) read the pin to select the canonicalisation rule applied at emission.

The pin is the load-bearing primitive for the [Substrate Adopters Registry](https://docs.algovoi.co.uk/adopters): adopters anchoring to this discipline pin the same `canon_version` value in their own publicly-citable artefacts. AlgoVoi maintains the registry as a neutral observer; this package itself is recorded there as the AlgoVoi reference implementation.

## Substrate adopters

AlgoVoi is recorded in the [Substrate Adopters Registry](https://docs.algovoi.co.uk/adopters) as the substrate author (v1 and v2). Parties anchoring their own services or specifications to `canon_version: jcs-rfc8785-v1` are recorded in the registry via the [submission process](https://docs.algovoi.co.uk/adopters#how-to-submit-an-adoption-entry). AlgoVoi validates submissions against the artefact's canonical bytes and adds qualifying entries.

## Licence

Apache 2.0.
