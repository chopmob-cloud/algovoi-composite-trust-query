"""
Composite trust query response shape -- verifier-side categorical
conclusion over an audit chain, under the JCS RFC 8785
canonicalisation discipline.

Specified in IETF Internet-Draft
`draft-hopley-x402-composite-trust-query-00` (Independent Submission,
Informational; AlgoVoi-authored).

The categorical outcome (TRUSTED / PROVISIONAL / INSUFFICIENT_EVIDENCE
/ UNTRUSTED) captures the verifier's conclusion over a stated query
applied to a content-addressed audit chain:

- TRUSTED: chain answers the query affirmatively; all anchored
  receipts present and consistent. Operator proceeds.
- PROVISIONAL: partial chain or pending finality; operator proceeds
  cautiously, re-queries after pending events finalise.
- INSUFFICIENT_EVIDENCE: chain doesn't contain enough evidence;
  operator gathers more data, does not proceed under TRUSTED.
- UNTRUSTED: chain contains evidence negating the query
  (compliance-forced termination, settled-then-reversed,
  REJECTED refund, expired mandate). Operator halts.

Composes with compliance_receipt_v1, settlement_attestation_v1,
cancellation_receipt_v1, and refund_receipt_v1 (chain_ref references
the audit chain root composed of these formats).

Shape (7 fields, sorted lexicographically by JCS during
canonicalisation):
- canon_version: "jcs-rfc8785-v1"
- chain_ref: "sha256:<hex>" reference to the audit chain root
- ctq_timestamp_ms: integer (Substrate Rule 2)
- jurisdiction_flags: ordered list of jurisdiction codes
- query_ref: "sha256:<hex>" reference to the canonical bytes of the query
- trust_outcome: TRUSTED | PROVISIONAL | INSUFFICIENT_EVIDENCE | UNTRUSTED
- verifier_did: DID URI of the verifier
"""

from __future__ import annotations

from typing import TypedDict

from algovoi_substrate.canonicalize import CANON_VERSION

TRUST_OUTCOMES = frozenset(
    {"TRUSTED", "PROVISIONAL", "INSUFFICIENT_EVIDENCE", "UNTRUSTED"}
)


class CtqResponseError(ValueError):
    """Raised when CTQ response inputs violate the substrate discipline."""


class CtqResponse(TypedDict):
    canon_version: str
    chain_ref: str
    ctq_timestamp_ms: int
    jurisdiction_flags: list[str]
    query_ref: str
    trust_outcome: str
    verifier_did: str


def _require_str(field: str, value: object) -> str:
    if not isinstance(value, str) or not value:
        raise CtqResponseError(f"{field} must be a non-empty string")
    return value


def _require_int_timestamp_ms(value: object) -> int:
    if isinstance(value, bool):
        raise CtqResponseError("ctq_timestamp_ms must be int, got bool")
    if not isinstance(value, int):
        raise CtqResponseError(
            f"ctq_timestamp_ms must be epoch-millisecond integer "
            f"(Substrate Rule 2), got {type(value).__name__}"
        )
    if value < 0:
        raise CtqResponseError(
            f"ctq_timestamp_ms must be non-negative, got {value}"
        )
    return value


def _require_jurisdiction_flags(value: object) -> list[str]:
    if not isinstance(value, list):
        raise CtqResponseError(
            f"jurisdiction_flags must be list, got {type(value).__name__}"
        )
    for i, code in enumerate(value):
        if not isinstance(code, str) or not code:
            raise CtqResponseError(
                f"jurisdiction_flags[{i}] must be a non-empty string"
            )
    return list(value)


def build_ctq_response(
    *,
    trust_outcome: str,
    chain_ref: str,
    query_ref: str,
    ctq_timestamp_ms: int,
    verifier_did: str,
    jurisdiction_flags: list[str],
    canon_version: str = CANON_VERSION,
) -> CtqResponse:
    """Build a validated composite trust query response.

    trust_outcome MUST be one of TRUSTED, PROVISIONAL,
    INSUFFICIENT_EVIDENCE, UNTRUSTED.

    chain_ref is a content-addressed reference (`sha256:<hex>`) to the
    root of the audit chain the verifier walked. The chain itself is
    composed of compliance, settlement, cancellation, and refund
    receipts under the shared canonicalisation pin.

    query_ref is a content-addressed reference (`sha256:<hex>`) to the
    canonical bytes of the query that was answered. The query format
    is opaque to this response shape; callers MAY use any structured
    question encoding.

    verifier_did identifies the verifier that emitted the response.

    jurisdiction_flags is treated as ordered; ["UK","EU"] and
    ["EU","UK"] produce distinct canonical bytes per RFC 8785 Section
    3.2.3.

    ctq_timestamp_ms MUST be an integer (Substrate Rule 2).
    RFC 3339 string forms are rejected.
    """
    if trust_outcome not in TRUST_OUTCOMES:
        raise CtqResponseError(
            f"trust_outcome must be one of {sorted(TRUST_OUTCOMES)}, "
            f"got {trust_outcome!r}"
        )

    return CtqResponse(
        canon_version=_require_str("canon_version", canon_version),
        chain_ref=_require_str("chain_ref", chain_ref),
        ctq_timestamp_ms=_require_int_timestamp_ms(ctq_timestamp_ms),
        jurisdiction_flags=_require_jurisdiction_flags(jurisdiction_flags),
        query_ref=_require_str("query_ref", query_ref),
        trust_outcome=trust_outcome,
        verifier_did=_require_str("verifier_did", verifier_did),
    )
