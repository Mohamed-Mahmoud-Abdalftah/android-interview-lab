---
id: "ARC-20"
question: "How do you test Presentation, Domain, and Data independently?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 165
editorial_status: "reviewed"
---

# ARC-20

## Original interview question

How do you test Presentation, Domain, and Data independently?

## What the interviewer evaluates

Define independent tests for UI transitions, business rules and data consistency, plus boundary integration checks.

## Explanation in Arabic

Presentation test تحقن fake repository/use case وتتحقق من `UiState` بعد events، loading، error، cancellation، من غير network. Domain use case test تحقن fake contracts وتتحقق من rules وedge cases. Data test تستخدم fake service وin-memory Room أو test DB لتتأكد من mapping، transactions، cache/server ordering؛ وinstrumented test لما Android behavior مهم. ما تكتفيش mocks بتأكد إن method اتنادت؛ اختبر observable behavior. ولا تسمّي JVM tests إثبات lifecycle/device behavior؛ Compose UI أو Room على الجهاز تحتاج suite مناسبة.

### Practical walkthrough in Egyptian Arabic

Presentation test يرسل event ويتحقق من UiState، Domain test يثبت rule/edge case، Data integration test يختبر Room migration/HTTP mapping. Fakes مفيدة لحدود، لكنها لا تثبت SQL أو wire contract. مثال timeout payment: VM يعرض Unknown، use case لا يكرر key جديد، backend contract يضمن one effect. اربط كل test بما يستطيع إثباته.

## Why it matters and how it works

Layered tests isolate logic and localize failures. Fakes at boundaries make state transitions deterministic; integration tests catch mapper and storage interactions that isolated tests miss. Android-specific behavior needs Android-capable tests.

## Worked example

Test plan for checkout: ViewModel fake use case emits `Pending` then `Accepted`, assert state and duplicate-tap behavior; domain fake repository checks amount limits and cancellation; data fake API plus Room validates request mapping, transaction and retry reconciliation. Device/UI test checks visible states and accessibility.

## Trade-offs and decision criteria

Unit tests are fast and precise but may miss wiring, database migrations and lifecycle. Integration/device tests cost more but cover real behavior. Use a small number of meaningful end-to-end flows instead of mirroring every implementation line.

## Failure modes

A test only verifies `repository.get()` was called, while ViewModel emits `Success` after a failure. Assert output state. Another failure is mocking Room DAO and claiming transaction behavior passed; use a real test database for that guarantee.

## Production perspective

CI runs JVM ViewModel/domain suites on each change, data integration tests for Room/network mapping, and selected instrumented Compose flows for loading/error/success and recreation. Reports distinguish simulated tests from device evidence.

## Interview answer — short

I test each layer through its public behavior: ViewModel state transitions with fakes, domain rules with fake repositories, and data mapping/transactions with test data sources or Room. Then I add integration and device tests for wiring and lifecycle.

## Interview answer — structured

For Presentation, I drive user events and assert the emitted UI state with a fake use case or repository and controlled coroutines. For Domain, I test business rules and error categories without Android UI. For Data, I verify DTO/entity mapping, database transactions, and sync ordering with realistic test sources. Isolated tests are fast but cannot prove the whole graph or device lifecycle, so I include targeted integration and instrumented UI cases. I focus on behavior, not just mock interactions. For a checkout flow, I assert ViewModel state after each event, use case policy outcomes for different amounts, and repository behavior when network and Room disagree. One integration test checks that the real graph maps a response all the way to displayed state.

## Interview answer — deep senior

Independent tests should match ownership. The ViewModel contract is state over time after events; the domain contract is policy outcomes over boundary inputs; the data contract is consistency across sources. I use fakes that expose meaningful scenarios, not mocks that merely record method calls. A Room transaction needs a real test database; a server contract needs representative payloads, including malformed and versioned cases. I separately test DI wiring and Compose rendering, accessibility and recreation where Android runtime behavior matters. Coroutine tests control scheduling and verify cancellation. CI labels JVM simulations versus instrumented/device evidence honestly. This mix finds logic defects quickly while still catching integration mistakes and process/lifecycle edge cases. I also choose the environment honestly. JVM unit tests can validate pure logic and coroutine transitions, but they do not prove Android lifecycle, Room migration or Compose accessibility. Room needs an appropriate database test, and selected device tests should cover recreation and visible UI states. I prefer fakes that produce meaningful outcomes over mocks that simply verify calls, because a method can be invoked while the wrong state is emitted. CI should report each suite and its limits separately.

## How to answer in the interview

- **Why:** different layers fail in different ways.
- **How:** test state, policy and real adapters separately.
- **Trade-off:** fast feedback versus integration cost.
- **Failure case:** fake passes while Room migration fails.
- **Production solution:** risk-based suite across boundaries.

## Deep-dive talking points

Specify one behavior assertion per layer, a real Room test boundary and an instrumented lifecycle/UI scenario.

## Follow-up questions

- [ARC-18](../arc-18/): What makes ViewModel tests deterministic? **Answer:** fake dependencies and controlled coroutine scheduling.
- [ARC-19](../arc-19/): What data behavior needs integration tests? **Answer:** transaction, mapping and refresh ordering.

## Self-check rubric

Design a three-layer test matrix for checkout and explain what each suite cannot prove.

## References and reviewed-on date

- [Android testing guide](https://developer.android.com/training/testing) — local and instrumented test roles.
- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — testability.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
