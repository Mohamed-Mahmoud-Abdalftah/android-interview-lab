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

Test pyramid معناها أغلب الاختبارات السريعة والدقيقة عند logic، وعدد أقل من UI/E2E المكلفة. مش قاعدة نسب ثابتة. Contract tests بتتحقق إن provider وconsumer متفقين على schema/status/error semantics من غير تشغيل كل النظام. في Android، repository API وbackend HTTP contract يحتاجوا tests تمنع drift، لكن مش بديل عن رحلة E2E.

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

“I use the pyramid as an economic model, not a quota. Unit tests cover deterministic decisions, integrations cover real database/network adapters, contracts check provider-consumer agreement, and a few E2E tests catch wiring and environment issues. For a payment API, the contract includes unknown outcomes and idempotency behavior, not only success JSON. Each layer has a distinct failure signal. ”

## Interview answer — deep senior

“I place a test at the lowest layer that can detect the actual risk. A server/client contract can catch an enum or field change in PRs without waiting for an emulator and live backend, but it cannot prove auth configuration, migrations or a hardware callback. I test both sides against versioned examples and include negative cases, then retain a thin E2E path for deployment wiring. I track flakiness, runtime and production escapes to rebalance the portfolio rather than target a magic unit-test percentage.”

## Deep-dive talking points

Prompt for boundary examples, negative contract cases, limits of E2E and test economics.

## Follow-up questions

- [TST-01](../tst-01/): What does E2E add? **Answer:** deployed wiring and full journey evidence.
- [TST-12](../tst-12/): What can a local HTTP server test? **Answer:** Android parsing, retries and error mapping.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android testing fundamentals](https://developer.android.com/training/testing/fundamentals) — test scope.
- [Android data-layer testing](https://developer.android.com/topic/architecture/data-layer) — interface/data boundaries.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
