---
id: "LEAD-07"
question: "How do you align mobile, backend, QA, and security teams on an API contract?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "B"
phase: 5
priority: "P2"
order: 462
editorial_status: "reviewed"
---

# LEAD-07

## Original interview question

How do you align mobile, backend, QA, and security teams on an API contract?

## What the interviewer evaluates

- Shared API contract across mobile/backend/QA/security.
- Error, retry, versioning and trust semantics before implementation.

## Explanation in Arabic

اتفاق API مش JSON happy path فقط. mobile وbackend يتفقوا على ownership، auth، states، timeout=unknown، idempotency key، error codes، pagination/versioning وbackward compatibility. QA تبني contract tests وsecurity تراجع trust boundary/data classification. نحط examples للnormal والفشل، ونحدد مين يملك التغيير وموعد deprecation.

### Practical walkthrough in Egyptian Arabic

عقد API للدفع مثلًا لازم يشمل أكثر من JSON success: operation ID، idempotency key، معنى timeout/unknown، status endpoint، error codes، retries، auth، وschema evolution. اجمع mobile/backend/QA/security على مثال lost response وبعده process death. اكتب sequence وما الذي يملكه كل طرف، ثم contract tests وsandbox evidence. لو backend يقول “كرر request” بدون dedup واضح، توقف وتصحح العقد قبل UI؛ Android وحدها لا تضمن أثر مالي واحد.

## Why it matters and how it works

A written schema can validate shape but not all semantics. Consumer-driven examples or OpenAPI plus contract tests make breaking changes visible. Mixed mobile versions remain installed, so server should support old contracts through a defined sunset period.

## Worked example

Payment endpoint contract says POST with stable operationId and immutable amount, returns pending/approved/declined; timeout is unknown; GET by ID resolves status; duplicate same-key request returns prior status, changed payload is rejected. QA injects lost response and security checks that client amount is not trusted.

## Trade-offs and decision criteria

Detailed contracts take cross-team time but prevent expensive integration defects. Server flexibility helps old apps but increases maintenance; negotiate explicit version support and deprecation.

## Failure modes

Backend changes `pending` to `failed` and client treats it as decline, causing repeat payment. Contract tests catch enum change; a rollout plan supports both versions or uses additive fields.

## Production perspective

Hold joint review before implementation, publish schema and examples, run both consumer/provider contracts in CI, and monitor unknown/unrecognized response metrics after rollout.

## Interview answer — short

“I align teams on semantics, not just fields: auth, state, retries, errors and compatibility. We write examples and contract tests, then stage changes for old installed clients.”

## Interview answer — structured

“I bring mobile, backend, QA and security into one contract review. We define request/response schema, ownership and authorization, idempotency identity, timeout semantics, error mapping, versioning and telemetry. QA turns examples into contract tests; security checks that client-provided amounts or flags are not authority. Because Android versions persist in the field, backend changes are additive or explicitly versioned with a sunset plan. We monitor parsing and unknown-state rates during rollout. ”

## Interview answer — deep senior

“I align teams around one concrete failure trace. For a payment attempt, the client persists an operation ID, sends it, the backend commits, and the response is lost. We jointly define whether a retry with the same identity returns the original outcome, how status is queried, how long identity is retained, and what each error code means. Mobile owns durable local state and user-visible unknown status; backend owns authorization, deduplication and the ledger; QA tests the trace across process death and network loss; security reviews authentication and data minimization. I write the request/response and state transitions as a versioned contract, then use consumer and provider tests plus sandbox evidence. I also define backward compatibility during a staggered mobile rollout, because old clients remain active. The trade-off is extra coordination before coding versus far less ambiguity in production. If a requirement cannot be represented safely in the backend contract, I escalate it before promising an Android-only workaround.”

## How to answer in the interview

- **Why:** distributed failures cross team boundaries.
- **How:** agree on lost-response trace and ownership.
- **Trade-off:** upfront coordination versus incident ambiguity.
- **Failure case:** each team assumes another handles dedup.
- **Production solution:** versioned contract and joint failure tests.

## Deep-dive talking points

Prompt for semantic contract, mixed versions, lost response, ownership and contract tests.

## Follow-up questions

- [PAY-02](../pay-02/): What must API say about idempotency? **Answer:** key scope, parameter matching, retention and lookup.
- [TST-07](../tst-07/): What tests catch drift? **Answer:** producer/consumer contract tests.

## Self-check rubric

Define request/response schema, errors, auth, idempotency and versioning with backend, QA and security; assign owners and prove agreement with a contract test.

## References and reviewed-on date

- [Android data-layer guide](https://developer.android.com/topic/architecture/data-layer) — repository/API boundaries.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — example retry semantics.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
