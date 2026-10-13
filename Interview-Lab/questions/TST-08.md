---
id: "TST-08"
question: "How do you unit-test ViewModels, UseCases, and Repositories?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 403
editorial_status: "reviewed"
---

# TST-08

## Original interview question

How do you unit-test ViewModels, UseCases, and Repositories?

## What the interviewer evaluates

- Layer-specific assertions, not one giant mocked ViewModel test.
- Coroutine scheduling, state emissions and real adapter checks.

## Explanation in Arabic

قسّم claims حسب owner. ViewModel test تستخدم `runTest` وfake repository متحكم فيها: تبدأ Loading، تطلع Success/Error، وتأكد Retry لا يطلق شغلًا مكررًا. UseCase test تركز على policy نقية مثل overdraft أو validation بمدخلات وحدود واضحة. Repository test توصل للـdata source الحقيقي عندما المطلوب إثبات cache، Room transaction، mapping أو stream بعد recreation؛ fake وحدها لا تثبت التخزين.

## Practical walkthrough

حقن dispatchers والوقت يمنع sleeps. لا تجعل الاختبار يطابق تسلسل كل method call الداخلي؛ اقرأ UI state والبيانات المحفوظة. أضف Android instrumented test لما تعتمد على Lifecycle أو Room/SQLite في بيئة Android. كل طبقة تثبت contract مختلف، فلا نكتفي بعدد الاختبارات.

## Why it matters and how it works

Inject dependencies and dispatchers. Collect StateFlow under TestScope, trigger actions and advance scheduler deliberately. For repository tests, fake network/DAO for coordination logic and add integration tests for SQL, serialization and transaction behavior.

## Worked example

A ViewModel loads account summary. Fake repository emits Loading then an error; test asserts UI state and retry action. A use case test checks overdraft policy pure JVM. A Room repository integration test verifies that cache write and observation survive recreation.

## Trade-offs and decision criteria

Fast fakes improve diagnosis but may not model DB/HTTP contracts. Over-mocking every method call makes tests fragile; assert externally visible state and add real-adapter tests for persistence.

## Failure modes

A ViewModel launches on real Main and the test hangs; install a MainDispatcherRule and share testScheduler. A repository fake returns immediate success, hiding intermediate Loading; control emission timing.

## Production perspective

CI runs JVM layer tests on each PR, targeted DB/network integration tests, and a few UI flows. Production defects feed new tests at the responsible layer.

## Interview answer — short

“I test ViewModels through observable UI state, use cases through business outputs, and repositories through data coordination plus real-adapter integrations. Inject dispatchers and use runTest for deterministic coroutine timing.”

## Interview answer — structured

“For ViewModels, I substitute a controllable repository and Main dispatcher, trigger a UI action, and assert StateFlow emissions including loading and failure. For use cases, I test pure business rules and edge cases. For repositories, I verify cache/network decisions with fakes and run focused Room/HTTP integration tests for actual storage and parsing. I avoid asserting incidental internal call order. For each layer I state which behavior a fake can prove and where a real adapter test is needed.”

## Interview answer — deep senior

“I split the problem by ownership. A ViewModel test runs under a controlled test scheduler with a fake repository: it asserts Loading before the fake completes, then Success or Error, and checks that Retry and cancellation do not publish stale state. A UseCase test focuses on a domain invariant, such as rejecting an overdraft or normalizing an amount, with ordinary JVM inputs and edge cases. A Repository test needs to exercise the real persistence or HTTP adapter when the claim is about transactions, cache consistency, mapping or observation after recreation. Replacing Room with an in-memory map can verify orchestration, but it cannot prove a migration or atomic write. I inject dispatchers and clocks at meaningful boundaries, and avoid fixed sleeps or assertions on every private call. For an offline account screen, I would test a local write becoming observable, a sync failure leaving pending state, and recovery after repository recreation. The final test layer follows the claim: a JVM policy test is fast, while platform lifecycle and database behavior may need Android instrumentation.”

## How to answer in the interview

- **Why:** ViewModel, UseCase and Repository own different invariants.
- **How:** test UI state with a fake, policy on JVM and storage with a real data source.
- **Trade-off:** isolation speeds feedback but cannot prove persistence.
- **Failure case:** asserting only collaborator calls misses a wrong displayed state.
- **Production solution:** layer-specific tests for one offline account journey.

## Deep-dive talking points

Prompt for layer contracts, test scheduler, fake drift, StateFlow sequence and process-death boundary.

## Follow-up questions

- [TST-05](../tst-05/): How control delay? **Answer:** runTest plus injected TestDispatcher.
- [TST-11](../tst-11/): What needs real Room? **Answer:** SQL, migration and transaction semantics.

## Self-check rubric

Test a ViewModel state transition with a controlled fake and dispatcher, a UseCase invariant on the JVM, and a Repository persistence/observation contract against its real data source. Identify which mock-only assertion would be too weak.

## References and reviewed-on date

- [Android ViewModel testing](https://developer.android.com/topic/libraries/architecture/viewmodel) — ViewModel lifecycle and state.
- [Android coroutine testing](https://developer.android.com/kotlin/coroutines/test) — dispatcher/test-scope guidance.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
