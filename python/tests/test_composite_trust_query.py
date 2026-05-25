"""Tests for algovoi-composite-trust-query."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

import pytest

from algovoi_substrate.canonicalize import CANON_VERSION, canonicalize, sha256_jcs
from algovoi_composite_trust_query import (
    TRUST_OUTCOMES,
    CtqResponseError,
    build_ctq_response,
)


class TestTrustOutcomes:
    def test_four_state_enum(self) -> None:
        assert TRUST_OUTCOMES == frozenset(
            {"TRUSTED", "PROVISIONAL", "INSUFFICIENT_EVIDENCE", "UNTRUSTED"}
        )


class TestBuildCtqResponse:
    def test_builds_canonical_response(self) -> None:
        r = build_ctq_response(
            trust_outcome="TRUSTED",
            chain_ref="sha256:0dd5d0b76c9b9281fdeb2509ad38ab132b16a17385ca01d976ff9e6e12563a0f",
            query_ref="sha256:8b7df143d91c716ecfa5fc1730022f6b421b05cedee8fd52b1fc65a96030ad52",
            ctq_timestamp_ms=1716494400000,
            verifier_did="did:web:api.algovoi.co.uk",
            jurisdiction_flags=["UK", "EU"],
        )
        assert r["trust_outcome"] == "TRUSTED"
        assert r["ctq_timestamp_ms"] == 1716494400000
        assert r["canon_version"] == CANON_VERSION

    def test_four_distinct_outcomes_four_distinct_hashes(self) -> None:
        common = dict(
            chain_ref="sha256:abc",
            query_ref="sha256:def",
            ctq_timestamp_ms=1716494400000,
            verifier_did="did:web:x",
            jurisdiction_flags=["UK"],
        )
        hashes = set()
        for outcome in TRUST_OUTCOMES:
            r = build_ctq_response(trust_outcome=outcome, **common)
            hashes.add(sha256_jcs(dict(r)))
        assert len(hashes) == 4

    def test_rejects_invalid_outcome(self) -> None:
        with pytest.raises(CtqResponseError, match="trust_outcome must be one of"):
            build_ctq_response(
                trust_outcome="MAYBE",
                chain_ref="sha256:abc",
                query_ref="sha256:def",
                ctq_timestamp_ms=0,
                verifier_did="did:web:x",
                jurisdiction_flags=["UK"],
            )

    def test_rejects_float_timestamp(self) -> None:
        with pytest.raises(CtqResponseError, match="Substrate Rule 2"):
            build_ctq_response(
                trust_outcome="TRUSTED",
                chain_ref="sha256:abc",
                query_ref="sha256:def",
                ctq_timestamp_ms=1716494400000.5,  # type: ignore[arg-type]
                verifier_did="did:web:x",
                jurisdiction_flags=["UK"],
            )

    def test_rejects_string_timestamp(self) -> None:
        with pytest.raises(CtqResponseError, match="Substrate Rule 2"):
            build_ctq_response(
                trust_outcome="TRUSTED",
                chain_ref="sha256:abc",
                query_ref="sha256:def",
                ctq_timestamp_ms="2024-05-23T12:00:00Z",  # type: ignore[arg-type]
                verifier_did="did:web:x",
                jurisdiction_flags=["UK"],
            )

    def test_canon_version_default(self) -> None:
        r = build_ctq_response(
            trust_outcome="UNTRUSTED",
            chain_ref="sha256:abc",
            query_ref="sha256:def",
            ctq_timestamp_ms=0,
            verifier_did="did:web:x",
            jurisdiction_flags=["UK"],
        )
        assert r["canon_version"] == "jcs-rfc8785-v1"

    def test_jurisdiction_order_matters(self) -> None:
        common = dict(
            trust_outcome="TRUSTED",
            chain_ref="sha256:abc",
            query_ref="sha256:def",
            ctq_timestamp_ms=1716494400000,
            verifier_did="did:web:x",
        )
        uk_eu = build_ctq_response(jurisdiction_flags=["UK", "EU"], **common)
        eu_uk = build_ctq_response(jurisdiction_flags=["EU", "UK"], **common)
        assert sha256_jcs(dict(uk_eu)) != sha256_jcs(dict(eu_uk))


class TestConformanceVectorReproduction:
    VECTOR_PATH = Path(
        "C:/algo/algovoi-jcs-conformance-vectors/vectors/composite_trust_query_v1/composite_trust_query_v1.json"
    )

    def test_vectors_001_to_005_reproduce(self) -> None:
        if not self.VECTOR_PATH.exists():
            pytest.skip("conformance vectors not co-located")
        data = json.loads(self.VECTOR_PATH.read_text(encoding="utf-8"))
        for v in data["vectors"]:
            if "response" not in v:
                continue
            canon = canonicalize(v["response"])
            canon_bytes = canon.encode("utf-8") if isinstance(canon, str) else canon
            assert (
                base64.b64encode(canon_bytes).decode("ascii")
                == v["expected_jcs_bytes_b64"]
            ), f"{v['vector_id']}: JCS bytes mismatch"
            assert (
                hashlib.sha256(canon_bytes).hexdigest() == v["expected_content_hash"]
            ), f"{v['vector_id']}: content_hash mismatch"
