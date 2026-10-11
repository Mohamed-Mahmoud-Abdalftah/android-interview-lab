---
id: "TST-04"
question: "What makes a class testable?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 399
editorial_status: "reviewed"
---

# TST-04

## Original interview question

What makes a class testable?

## What the interviewer evaluates

- Dependency boundaries, deterministic time and observable outputs.
- Why testability should follow clear ownership, not public-method proliferation.

## Explanation in Arabic

Class قابلة للاختبار لما dependencies تدخل من برّه بدل hard-coded singletons، والوقت/dispatcher/IO ممكن التحكم فيهم، والنتيجة تظهر كstate أو return value. مش لازم نخلي كل private method public؛ نفصل pure decision logic عن Android side effects، ونختبر contract. Testability غالبًا نتيجة design واضح.

## Why it matters and how it works

Constructor-injected interfaces let tests substitute deterministic collaborators. Clock and coroutine dispatcher injection remove wall-time scheduling; immutable inputs and explicit outputs make behavior reproducible. The class should own one coherent responsibility with errors represented clearly.

## Worked example

A `SessionExpiryUseCase(clock: Clock, repository: SessionRepository)` can be tested at a fixed instant with a fake repository. A class that calls `System.currentTimeMillis()` and a global Retrofit singleton during its constructor forces slow, brittle integration tests.

## Trade-offs and decision criteria

Injecting every trivial value can overcomplicate code. Prefer seams at nondeterministic boundaries—time, network, disk, randomness—and keep pure functions simple. A real-adapter test remains necessary for integration semantics.

## Failure modes

A test fake passes because the class never checks database transaction behavior. Testability does not mean replacing every dependency in all tests; use focused integration tests. Static/global state leaking between tests causes order dependence.

## Production perspective

Code review checks constructor side effects, hidden globals and lifecycle ownership. Tests cover normal, error and cancellation paths through public behavior; performance-sensitive adapter details get separate integration checks.

## Interview answer — short

“A testable class has explicit dependencies, controllable nondeterminism and observable behavior. I inject time and I/O boundaries, keep decisions cohesive, and test public contracts rather than exposing private methods.”

## Interview answer — structured

“I look for hidden inputs: clocks, dispatchers, random IDs, global services and Android framework calls. I introduce interfaces or simple injected functions at those boundaries, then test deterministic inputs and outputs. I do not fragment a class solely to satisfy a mock framework. Pure logic is cheap to test; real database or network behavior still needs integration coverage. The mechanics matter. Constructor-injected interfaces let tests substitute deterministic collaborators. Clock and coroutine dispatcher injection remove wall-time scheduling; immutable inputs and explicit outputs make behavior reproducible. The class should own one coherent responsibility with errors represented clearly. The choice has a trade-off. Injecting every trivial value can overcomplicate code. Prefer seams at nondeterministic boundaries—time, network, disk, randomness—and keep pure functions simple. A real-adapter test remains necessary for integration semantics.”

## Interview answer — deep senior

“A good test seam reflects an architectural boundary. For a payment retry use case I inject a clock, stable ID source and repository; I can simulate timeout, process restart and duplicate triggers without sleeps. The repository contract says what is durable and idempotent, while separate integration tests prove Room and HTTP adapters honor it. I avoid publicizing implementation helpers or mocking every line. If tests require deep knowledge of call order, I revisit responsibility and state ownership rather than add more mocks. Consider a concrete case. A `SessionExpiryUseCase(clock: Clock, repository: SessionRepository)` can be tested at a fixed instant with a fake repository. A class that calls `System.currentTimeMillis()` and a global Retrofit singleton during its constructor forces slow, brittle integration tests. A failure case illustrates the risk. A test fake passes because the class never checks database transaction behavior. Testability does not mean replacing every dependency in all tests; use focused integration tests. Static/global state leaking between tests causes order dependence. In production, the response is concrete. Code review checks constructor side effects, hidden globals and lifecycle ownership. Tests cover normal, error and cancellation paths through public behavior; performance-sensitive adapter details get separate integration checks.”

## Deep-dive talking points

Prompt for hidden inputs, clock/dispatcher injection, observable contract and integration limits.

## Follow-up questions

- [TST-02](../tst-02/): What double is useful here? **Answer:** a fake at a real I/O boundary.
- [TST-08](../tst-08/): How test a ViewModel? **Answer:** inject repository and dispatcher, then assert StateFlow.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android app architecture](https://developer.android.com/topic/architecture) — separation of concerns and testability.
- [Android test doubles](https://developer.android.com/training/testing/fundamentals/test-doubles) — dependency substitutions.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
