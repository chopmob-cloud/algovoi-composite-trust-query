/**
 * @algovoi/composite-trust-query
 *
 * AlgoVoi composite trust query response reference implementation.
 * Verifier-side categorical conclusion over audit chains under JCS RFC 8785.
 * Closed four-element outcome enum:
 * {TRUSTED, PROVISIONAL, INSUFFICIENT_EVIDENCE, UNTRUSTED}.
 *
 * Specified in IETF Internet-Draft draft-hopley-x402-composite-trust-query-00.
 * Apache 2.0.
 */

export {
  TRUST_OUTCOMES,
  type TrustOutcome,
  CtqResponseError,
  type CtqResponse,
  type BuildCtqResponseInput,
  buildCtqResponse,
} from './composite-trust-query.js';
