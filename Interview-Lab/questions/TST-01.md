---
id: "TST-01"
question: "Compare unit, integration, instrumentation, UI, and end-to-end tests."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 396
editorial_status: "reviewed"
---

# TST-01

## Original interview question

Compare unit, integration, instrumentation, UI, and end-to-end tests.

## What the interviewer evaluates

- Test boundary, speed and fidelity across five levels.
- Choosing the cheapest level that detects a specific risk.

## Explanation in Arabic

الفرق مش اسم الـtool، لكن الـboundary اللي الاختبار بيثبتها. Unit test تشغّل policy أو UseCase في JVM بعزل واضح وتدّي feedback سريع. Integration test توصل أجزاء حقيقية ببعض، زي Repository مع Room أو client مع test server. Instrumented test تحتاج Android runtime لما السلوك متعلق بـLifecycle أو permissions أو قاعدة بيانات Android.

## Practical walkthrough

UI test تتعامل مع الشاشة كما يراها المستخدم، وend-to-end تعدّي على المسار كله مع backend أو sandbox مناسب. لو عملت mock للـDAO ثم قلت migration سليمة، أنت اختبرت توقعات الـmock فقط. صمّم test matrix حسب خطر الفشل: حساب الرسوم يحتاج حالات حدودية كثيرة وسريعة؛ استرجاع payment بعد process death يحتاج persistence/platform؛ والتكامل المالي النهائي يحتاج authority خارج التطبيق. اختبارات كثيرة في طبقة واحدة لا تعوّض boundary غير مختبرة.

## Why it matters and how it works

The levels vary in environment, not just file location. A pure JVM test cannot prove platform permission behavior, while an end-to-end payment test may detect cross-system contract failures but runs slower and is less deterministic. Contract tests sit between isolated unit logic and full E2E.

## Worked example

Test fee calculation as JVM unit; Room migration on an Android test device or suitable test database; Compose semantics with UI testing; a checkout sandbox flow end-to-end. Do not use a mocked repository to claim database durability was tested.

## Trade-offs and decision criteria

Fast tests give tight feedback; high-fidelity tests cover platform and system integration. Put deterministic logic low in the pyramid, then add a small number of device and E2E tests for risks only they can observe.

## Failure modes

A ViewModel unit test passes while a manifest permission or Room migration breaks on device. Conversely, thousands of UI tests make every PR slow and flaky. Map each production incident to the lowest effective test layer.

## Production perspective

CI runs JVM tests and static checks early, device tests on supported API/device matrix, and a limited critical-journey suite before release. Track failure detection value and runtime per layer.

## Interview answer — short

“Unit tests cover isolated logic; integration tests cover collaborating components; instrumentation runs on Android; UI tests exercise interactions; E2E validates a user journey across systems. I choose by risk and environment fidelity.”

## Interview answer — structured

“I do not equate more E2E tests with better coverage. A pure use case belongs in fast JVM tests, repository plus database in integration tests, permission and lifecycle behavior on an emulator, and a few critical purchase journeys in E2E. UI tests may be instrumentation tests, so these labels overlap. The test plan states what each layer proves and what it cannot.”

## Interview answer — deep senior

“I define tests by the claim they prove. A JVM unit test is ideal for deterministic fee rules, mapping and state reducers: it runs quickly, covers boundary cases and avoids Android setup. An integration test keeps a real boundary in place, such as a Repository with Room or an HTTP client with a controlled server, so it can expose schema or serialization mistakes that mocks hide. Instrumented tests use Android when the platform contract matters: lifecycle recreation, permissions, actual Room behavior or Compose UI semantics. A small end-to-end suite checks that the signed app, backend and provider sandbox agree on a critical journey. I do not put every scenario at the slowest layer. For checkout, I would unit-test amount and state policy extensively, integration-test durable intent storage and lost HTTP replies, run targeted device tests for recreation, and keep a limited sandbox path for authorization and reconciliation. Each layer has a blind spot: a fake cannot prove persistence, a UI test cannot prove server idempotency, and a happy-path end-to-end test rarely isolates an edge case. I map each release risk to the lowest layer that can actually observe it, then retain a few cross-boundary checks.”

## How to answer in the interview

- **Why:** one test layer cannot see every boundary.
- **How:** map fee policy, Room, UI and sandbox checkout to the lowest layer that can observe each.
- **Trade-off:** fast isolated coverage versus slower integrated confidence.
- **Failure case:** a mocked DAO cannot prove migration or persistence.
- **Production solution:** risk-based matrix with a few complete release journeys.

## Deep-dive talking points

Prompt for overlap of labels, fidelity limits, payment invariants and CI runtime.

## Follow-up questions

- [TST-07](../tst-07/): Where do contract tests sit? **Answer:** they check interface assumptions between components without full E2E.
- [TST-16](../tst-16/): What requires a device? **Answer:** actual Android framework behavior such as permissions and migrations.

## Self-check rubric

Score one point each for choosing a JVM unit test for pure policy, an integration test for real boundaries, an Android instrumented test for platform behavior, a UI test for user interaction, and a small end-to-end test for the full checkout path. State what each test cannot prove.

## References and reviewed-on date

- [Android testing fundamentals](https://developer.android.com/training/testing/fundamentals) — test types and environment.
- [Android test strategy](https://developer.android.com/training/testing) — official test guidance.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
