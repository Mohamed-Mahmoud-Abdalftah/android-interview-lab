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

`test double` هو الاسم العام لأي بديل بنستخدمه بدل dependency حقيقية. Stub يرد بقيم جاهزة؛ fake عنده سلوك بسيط لكنه متماسك، زي repository in-memory؛ mock بنضبط عليه توقعات عن التفاعل؛ spy يسجل ما حدث، وقد يمرر التنفيذ لمكوّن حقيقي. مش لازم نعمل mock لكل object.

## Practical walkthrough

لو المطلوب إثبات إن ViewModel عرض Error بعد فشل، fake repository متحكم في نتيجته مع assertion على `UiState` أوضح من التحقق من سلسلة calls داخلية. لكن لو إرسال audit event نفسه requirement، يبقى فحص تفاعل الـport مناسب. احذر إن fake تختلف عن Room أو الشبكة في transaction/cancellation؛ نحتاج integration test عند الـboundary الحقيقي. اختَر الـdouble حسب السلوك المطلوب إثباته، وليس حسب سهولة الـframework.

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

“I choose the double according to the risk. A fake repository is useful for stateful ViewModel tests, a stub for a one-off response, and a mock for an important interaction such as dispatching an audit event. A spy can observe a real implementation but may retain real side effects. I avoid tests that assert incidental call order and add integration tests so a fake cannot hide database or network behavior.”

## Interview answer — deep senior

“I use ‘test double’ as the umbrella term, then choose the least complicated kind that proves the contract. A stub returns scripted data; a fake has a small working implementation, such as an in-memory repository; a mock verifies interactions; and a spy records calls, sometimes around a real object. For a ViewModel loading account data, I prefer a controllable fake that emits Loading and then Error, and I assert the visible state and retry behavior. If I mock every repository method call and its exact order, a harmless refactor can break tests without changing the user outcome. Interaction verification is valid when the interaction is the product requirement, for example one audit command or one idempotent submission to a gateway port. I also document the fake’s limits. An in-memory map does not reproduce Room transactions, migrations or process death, and a fake HTTP client cannot certify Retrofit cancellation. Those claims need integration tests against the real boundary. Good tests make a failure diagnostic: they say which observable contract broke, rather than which implementation detail moved.”

## How to answer in the interview

- **Why:** doubles keep tests deterministic without coupling them to every implementation call.
- **How:** name stub, fake, mock and spy, then choose a fake repository for state behavior.
- **Trade-off:** interaction checks are precise but can be brittle.
- **Failure case:** a fake map hides transaction semantics.
- **Production solution:** pair behavior tests with a real-boundary integration test.

## Deep-dive talking points

Prompt for five roles, outcome versus interaction, fake drift and real-adapter verification.

## Follow-up questions

- [TST-08](../tst-08/): What double fits ViewModel state? **Answer:** a controllable fake repository.
- [TST-07](../tst-07/): How catch fake drift? **Answer:** run shared contract expectations on real and fake adapters.

## Self-check rubric

Distinguish the umbrella term test double from stubbed answers, behavior-verifying mocks, stateful fakes and observation spies. Choose a fake repository for a ViewModel state test and explain when verifying a collaborator call is actually the requirement.

## References and reviewed-on date

- [Android test doubles](https://developer.android.com/training/testing/fundamentals/test-doubles) — official definitions and guidance.
- [Mockito documentation](https://site.mockito.org/) — mock interaction behavior.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
