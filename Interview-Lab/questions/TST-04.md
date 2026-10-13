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

الكلاس القابل للاختبار له inputs وoutputs وحدود dependencies واضحة. لو constructor يبدأ network request، يقرأ `System.currentTimeMillis()`، أو يجيب singleton global، الاختبار يصبح معتمدًا على توقيت وبيئة لا نتحكم فيهما. افصل الـclock، repository، dispatcher عند الحاجة، وخلي operation صريحة؛ بعدها fake clock وfake repository يثبتوا policy في وقت ثابت.

## Practical walkthrough

ده مش معناه إضافة interface لكل كلاس: اعزل فقط الحدود اللي تتغير أو لها side effects. الـtest الجيد يثبت result أو state بدل تفاصيل تنفيذ داخلية. ولو المشكلة في serialization أو Room transaction، ما يكفيش fake؛ اكتب integration test للـboundary الحقيقي. قابلية الاختبار عادة علامة على ownership أوضح، لكنها ليست هدفًا يبرر abstraction بلا فائدة.

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

“I look for hidden inputs: clocks, dispatchers, random IDs, global services and Android framework calls. I introduce interfaces or simple injected functions at those boundaries, then test deterministic inputs and outputs. I do not fragment a class solely to satisfy a mock framework. Pure logic is cheap to test; real database or network behavior still needs integration coverage.”

## Interview answer — deep senior

“Testability is the ability to control relevant inputs and observe the contract without relying on accidental global state or real time. Consider a session-expiry use case. If it reaches into `System.currentTimeMillis()`, a global Retrofit client and a singleton cache during construction, edge cases are difficult to reproduce. I would pass a `Clock` and repository boundary, make the operation explicit, and test just-before, at and after expiry with fixed instants. I would not create an interface for every data class merely to satisfy a mocking framework; the useful seams are time, I/O and externally owned behavior. I keep concurrency ownership visible as well: a suspend function can inherit its caller’s Job, while a newly created scope in each method makes cancellation and failures hard to assert. The unit test proves policy, not the real database or network adapter. I add integration tests where serialization, transactions or platform lifecycle are the risk. I judge a class testable when a failure points to a business invariant and the test survives reasonable refactoring of internals.”

## How to answer in the interview

- **Why:** hidden time and I/O make behavior hard to reproduce.
- **How:** inject Clock and repository, then test fixed expiry boundaries.
- **Trade-off:** useful seams versus needless interfaces.
- **Failure case:** constructor network work and global state cause flaky tests.
- **Production solution:** isolate policy and separately test real adapters.

## Deep-dive talking points

Prompt for hidden inputs, clock/dispatcher injection, observable contract and integration limits.

## Follow-up questions

- [TST-02](../tst-02/): What double is useful here? **Answer:** a fake at a real I/O boundary.
- [TST-08](../tst-08/): How test a ViewModel? **Answer:** inject repository and dispatcher, then assert StateFlow.

## Self-check rubric

Identify hidden clock, network and dispatcher dependencies in an untestable class; inject them through a small contract; run a deterministic fixed-time case; and explain why constructor side effects make isolation difficult.

## References and reviewed-on date

- [Android app architecture](https://developer.android.com/topic/architecture) — separation of concerns and testability.
- [Android test doubles](https://developer.android.com/training/testing/fundamentals/test-doubles) — dependency substitutions.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
