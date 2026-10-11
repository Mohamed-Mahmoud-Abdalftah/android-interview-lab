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

Unit test بتفحص logic صغير بمعزل عن Android؛ integration test بتفحص تعاون modules حقيقية مثل Repository مع Room؛ instrumentation بتشتغل على device/emulator؛ UI test تتفاعل مع الشاشة؛ end-to-end تتبع رحلة كاملة مع backend أو بيئة قريبة. المصطلحات بتتداخل: UI test غالبًا instrumentation، لكن الهدف مختلف. اختار مستوى الاختبار حسب failure المحتمل.

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

“I do not equate more E2E tests with better coverage. A pure use case belongs in fast JVM tests, repository plus database in integration tests, permission and lifecycle behavior on an emulator, and a few critical purchase journeys in E2E. UI tests may be instrumentation tests, so these labels overlap. The test plan states what each layer proves and what it cannot. The mechanics matter. The levels vary in environment, not just file location. A pure JVM test cannot prove platform permission behavior, while an end-to-end payment test may detect cross-system contract failures but runs slower and is less deterministic. Contract tests sit between isolated unit logic and full E2E. The choice has a trade-off. Fast tests give tight feedback; high-fidelity tests cover platform and system integration. Put deterministic logic low in the pyramid, then add a small number of device and E2E tests for risks only they can observe.”

## Interview answer — deep senior

“I build a risk matrix first. Business invariants like one charge per intent get deterministic unit and service contract tests; database migrations need real schemas and device execution; Compose semantics require UI tests; provider integration needs sandbox and hardware drills. I keep E2E sparse because timing, network and third-party state increase flakiness. Every failing test must have a clear ownership boundary, reproducible fixture and release impact. I also measure escapes and runtime, then move tests to lower layers when equivalent confidence is possible. Consider a concrete case. Test fee calculation as JVM unit; Room migration on an Android test device or suitable test database; Compose semantics with UI testing; a checkout sandbox flow end-to-end. Do not use a mocked repository to claim database durability was tested. A failure case illustrates the risk. A ViewModel unit test passes while a manifest permission or Room migration breaks on device. Conversely, thousands of UI tests make every PR slow and flaky. Map each production incident to the lowest effective test layer. In production, the response is concrete. CI runs JVM tests and static checks early, device tests on supported API/device matrix, and a limited critical-journey suite before release. Track failure detection value and runtime per layer.”

## Deep-dive talking points

Prompt for overlap of labels, fidelity limits, payment invariants and CI runtime.

## Follow-up questions

- [TST-07](../tst-07/): Where do contract tests sit? **Answer:** they check interface assumptions between components without full E2E.
- [TST-16](../tst-16/): What requires a device? **Answer:** actual Android framework behavior such as permissions and migrations.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android testing fundamentals](https://developer.android.com/training/testing/fundamentals) — test types and environment.
- [Android test strategy](https://developer.android.com/training/testing) — official test guidance.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
