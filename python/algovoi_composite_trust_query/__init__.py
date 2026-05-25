"""
algovoi-composite-trust-query -- AlgoVoi composite trust query response reference implementation.

Verifier-side categorical conclusion over audit chains composed of
compliance, settlement, cancellation, and refund receipts. The
verifier walks the chain, applies a structured query, and emits a
single composite-trust-claim response anchoring the chain by its
content-addressed root.

Closed four-element enumeration {TRUSTED, PROVISIONAL,
INSUFFICIENT_EVIDENCE, UNTRUSTED} captures the genuinely four-state
decision space: proceed, proceed-with-caution, hold-pending-more-data,
halt.

Specified in IETF Internet-Draft draft-hopley-x402-composite-trust-query-00
(Independent Submission, Informational; AlgoVoi-authored).

Top-of-stack format above the four AlgoVoi receipt formats, under the
shared urn:x402:canonicalisation:jcs-rfc8785-v1 pin.

Licensed under Apache 2.0.
"""

from algovoi_composite_trust_query.composite_trust_query import (
    TRUST_OUTCOMES,
    CtqResponse,
    CtqResponseError,
    build_ctq_response,
)

__all__ = [
    "TRUST_OUTCOMES",
    "CtqResponse",
    "CtqResponseError",
    "build_ctq_response",
]

__version__ = "0.1.0"
