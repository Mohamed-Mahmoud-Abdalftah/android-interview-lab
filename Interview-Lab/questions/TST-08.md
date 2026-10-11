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

ViewModel test يركز على UI state/actions مع fake repository وtest dispatcher؛ UseCase test يركز business rule بمداخل محددة؛ Repository test يتأكد من تنسيق sources/cache/errors وربما Room/HTTP adapters حقيقية حسب risk. لازم نتحكم في coroutine scheduler ونفحص loading، success، error وcancellation بدل انتظار sleep.

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

“For ViewModels, I substitute a controllable repository and Main dispatcher, trigger a UI action, and assert StateFlow emissions including loading and failure. For use cases, I test pure business rules and edge cases. For repositories, I verify cache/network decisions with fakes and run focused Room/HTTP integration tests for actual storage and parsing. I avoid asserting incidental internal call order. Inject dependencies and dispatchers. ”

## Interview answer — deep senior

“I start with the contract each layer owns. A ViewModel translates domain outcomes into UI state and cancels work with its lifecycle; a use case enforces a rule; a repository coordinates sources and durable state. I inject a shared TestCoroutineScheduler, advance through intermediate emissions and test stale-response/cancellation races. Then I prove the adapters separately: Room transactions, migrations and HTTP error mapping. Process death is not solved by a ViewModel unit test, so I restore from persistence in a device/integration test. A ViewModel loads account summary.”

## Deep-dive talking points

Prompt for layer contracts, test scheduler, fake drift, StateFlow sequence and process-death boundary.

## Follow-up questions

- [TST-05](../tst-05/): How control delay? **Answer:** runTest plus injected TestDispatcher.
- [TST-11](../tst-11/): What needs real Room? **Answer:** SQL, migration and transaction semantics.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android ViewModel testing](https://developer.android.com/topic/libraries/architecture/viewmodel) — ViewModel lifecycle and state.
- [Android coroutine testing](https://developer.android.com/kotlin/coroutines/test) — dispatcher/test-scope guidance.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
