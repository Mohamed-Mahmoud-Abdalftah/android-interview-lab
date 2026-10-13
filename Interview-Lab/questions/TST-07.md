---
id: "TST-07"
question: "What is the test pyramid, and where do contract tests fit?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 402
editorial_status: "reviewed"
---

# TST-07

## Original interview question

What is the test pyramid, and where do contract tests fit?

## What the interviewer evaluates

- Risk-based pyramid rather than fixed percentages.
- Provider/consumer contracts as middle-layer evidence.

## Explanation in Arabic

الـtest pyramid فكرة لتوزيع السرعة والثقة: اختبارات policy كثيرة وسريعة، عدد أقل عند boundaries الحقيقية، وعدد محدود لمسارات UI/end-to-end الحرجة. النسبة الدقيقة مش قانون. Contract test تقع عند حد بين consumer وprovider: Android client يثبت request/response/error schema يتوقعها، والbackend يتحقق من نفس العقد.

## Practical walkthrough

ده يمنع كسر API رغم نجاح unit tests للطرفين. لكنه لا يثبت auth routing أو network أو Play artifact كامل؛ اختبر مسارًا متكاملًا واحدًا على الأقل حسب المخاطر. في payments مهم التمييز بين Unknown وDeclined، وثبات ID عبر retries. لا تختبر كل شيء بـUI البطيئة، ولا تستخدم mocks لتدعي أن التكامل الحقيقي سليم.

## Why it matters and how it works

Unit tests localize logic failures; integration tests validate real adapters; contract tests exercise agreed requests/responses or interface behavior; E2E tests validate wiring and deployment. A provider contract can pass while a production configuration or auth token flow fails, hence a small E2E layer remains.

## Worked example

For a payments API, consumer contract asserts `POST /intents` returns stable ID and `GET /intents/{id}` distinguishes Unknown from Declined. Backend verifies the same contract in CI. An E2E sandbox test then checks auth and routing from Android through backend.

## Trade-offs and decision criteria

Contract tests are faster and more diagnostic than full E2E, but they only cover declared examples. A brittle pyramid with many mocked unit tests may still miss data races; add integration where semantics matter.

## Failure modes

Backend changes timeout status from `pending` to `failed` without coordinating Android. Unit tests with hand-coded stub pass; contract test fails. Keep contracts versioned and include error/nullable fields, not just happy response.

## Production perspective

PR checks run fast contracts; nightly/release tests run cross-service E2E. Measure escaped contract failures and update examples from incidents.

## Interview answer — short

“The pyramid favors many fast tests and fewer expensive journeys. Contract tests check assumptions at component boundaries, catching API drift before full E2E while still requiring integration and deployment checks.”

## Interview answer — structured

“I use the pyramid as an economic model, not a quota. Unit tests cover deterministic decisions, integrations cover real database/network adapters, contracts check provider-consumer agreement, and a few E2E tests catch wiring and environment issues. For a payment API, the contract includes unknown outcomes and idempotency behavior, not only success JSON. Each layer should have an owner, a clear failure signal and a proportionate CI cost.”

## Interview answer — deep senior

“The pyramid is a feedback design, not a mandated ratio. I put many deterministic domain cases at the base, fewer tests with real database or HTTP boundaries in the middle, and a small number of complete user journeys at the top. A consumer contract belongs at an interface between systems: the Android client describes the request shape and status/error meanings it relies on, and the provider verifies it in CI. For a payments API, a contract should preserve the operation ID and distinguish pending or unknown from a confirmed decline; otherwise a client may retry unsafely after a timeout. Contract tests catch schema drift earlier than a full sandbox run, but they cannot prove credentials, routing, device behavior or a provider’s financial ledger in production. I therefore pair them with an end-to-end path through a signed release-like build and sandbox for the highest-risk flow. I also watch test cost and diagnostic value. If an end-to-end test is flaky because of shared state, I fix that boundary instead of adding retries that hide genuine regressions.”

## How to answer in the interview

- **Why:** broad confidence must remain fast enough for every change.
- **How:** place domain, boundary, contract and full-flow tests at their proper scopes.
- **Trade-off:** many fast tests versus a few expensive cross-system tests.
- **Failure case:** passing consumer mocks while provider schema changes.
- **Production solution:** shared API contract plus a small signed-app sandbox path.

## Deep-dive talking points

Prompt for boundary examples, negative contract cases, limits of E2E and test economics.

## Follow-up questions

- [TST-01](../tst-01/): What does E2E add? **Answer:** deployed wiring and full journey evidence.
- [TST-12](../tst-12/): What can a local HTTP server test? **Answer:** Android parsing, retries and error mapping.

## Self-check rubric

Place many fast domain tests, fewer boundary tests and a small number of end-to-end flows according to risk. Show what a consumer contract checks for a payment API and why it does not replace one real integrated path.

## References and reviewed-on date

- [Android testing fundamentals](https://developer.android.com/training/testing/fundamentals) — test scope.
- [Android data-layer testing](https://developer.android.com/topic/architecture/data-layer) — interface/data boundaries.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
