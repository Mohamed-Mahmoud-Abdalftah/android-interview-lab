---
id: "TST-02"
question: "Compare fake, mock, stub, spy, and test double."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 397
editorial_status: "reviewed"
---

# TST-02

## Original interview question

Compare fake, mock, stub, spy, and test double.

## What the interviewer evaluates

- Distinguishing all test-double roles by behavior.
- When state-based assertions are more robust than interaction assertions.

## Explanation in Arabic

Test double اسم عام لأي بديل في الاختبار. Stub بيرجع قيم محددة، fake implementation خفيف لكنه شغال (زي in-memory repository)، mock بنحدد له توقعات calls، spy يسجل أو يمرر calls لimplementation حقيقي. الاسم أقل أهمية من contract: هل الاختبار بيفحص النتيجة ولا تفاصيل التنفيذ؟

## Why it matters and how it works

Fakes model behavior and often support multiple tests; stubs provide canned responses; mocks verify interaction; spies observe real or wrapped behavior. Framework names can differ, so describe what the double does rather than rely on terminology alone.

## Worked example

For a ViewModel, an in-memory `PaymentsRepository` fake emits pending then approved. Assert `StateFlow` UI state. Mock an analytics port only when the event itself is the behavior under test; do not assert every incidental repository call.

## Trade-offs and decision criteria

Fakes can drift from production semantics, especially transactions/concurrency. Mocks are quick for rare failures but overuse couples tests to call order. Contract tests can check fake and real adapter behavior against the same expectations.

## Failure modes

A mock verifies `save()` called but the real Room implementation loses the write on rollback. Add integration coverage for persistence. A spy invokes real network unexpectedly; isolate side effects deliberately.

## Production perspective

Keep doubles local to test modules, specify failure/cancellation behavior, and review whether they preserve important contract rules. Use real database/HTTP adapters in focused integration tests.

## Interview answer — short

“A test double replaces a dependency; stubs return canned data, fakes implement simplified behavior, mocks verify calls, and spies observe real or wrapped behavior. I prefer outcome assertions unless interaction is the contract.”

## Interview answer — structured

“I choose the double according to the risk. A fake repository is useful for stateful ViewModel tests, a stub for a one-off response, and a mock for an important interaction such as dispatching an audit event. A spy can observe a real implementation but may retain real side effects. I avoid tests that assert incidental call order and add integration tests so a fake cannot hide database or network behavior. The mechanics matter. Fakes model behavior and often support multiple tests; stubs provide canned responses; mocks verify interaction; spies observe real or wrapped behavior. Framework names can differ, so describe what the double does rather than rely on terminology alone. The choice has a trade-off. Fakes can drift from production semantics, especially transactions/concurrency. Mocks are quick for rare failures but overuse couples tests to call order. Contract tests can check fake and real adapter behavior against the same expectations.”

## Interview answer — deep senior

“I ask whether the dependency contract is state or interaction. If the requirement is ‘shows pending after a timeout,’ a fake driving state is clearer than verifying three method calls. If the requirement is ‘enqueue exactly one reversal intent,’ an interaction or persisted-row assertion may be appropriate, but a mock alone cannot prove durable atomicity. I make doubles model cancellation and errors, then use contract tests or targeted integrations to detect semantic drift. This keeps tests resilient to refactoring while preserving real risk coverage. Consider a concrete case. For a ViewModel, an in-memory `PaymentsRepository` fake emits pending then approved. Assert `StateFlow` UI state. Mock an analytics port only when the event itself is the behavior under test; do not assert every incidental repository call. A failure case illustrates the risk. A mock verifies `save()` called but the real Room implementation loses the write on rollback. Add integration coverage for persistence. A spy invokes real network unexpectedly; isolate side effects deliberately. In production, the response is concrete. Keep doubles local to test modules, specify failure/cancellation behavior, and review whether they preserve important contract rules. Use real database/HTTP adapters in focused integration tests. The decision has a trade-off. Fakes can drift from production semantics, especially transactions/concurrency. Mocks are quick for rare failures but overuse couples tests to call order. Contract tests can check fake and real adapter behavior against the same expectations.”

## Deep-dive talking points

Prompt for five roles, outcome versus interaction, fake drift and real-adapter verification.

## Follow-up questions

- [TST-08](../tst-08/): What double fits ViewModel state? **Answer:** a controllable fake repository.
- [TST-07](../tst-07/): How catch fake drift? **Answer:** run shared contract expectations on real and fake adapters.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android test doubles](https://developer.android.com/training/testing/fundamentals/test-doubles) — official definitions and guidance.
- [Mockito documentation](https://site.mockito.org/) — mock interaction behavior.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
