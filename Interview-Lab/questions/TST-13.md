---
id: "TST-13"
question: "How do you test DI substitutions and scoped dependencies?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 408
editorial_status: "reviewed"
---

# TST-13

## Original interview question

How do you test DI substitutions and scoped dependencies?

## What the interviewer evaluates

- DI replacement scope and leak between tests.
- Production graph parity, Hilt test bindings and lifecycle.

## Explanation in Arabic

DI test لازم يستبدل dependency في scope الصح: fake repository واحد للـtest، مش singleton يتسرب لاختبار تاني، وViewModel/Activity تشوف نفس instance المتوقع. في Hilt نستخدم test bindings أو `@UninstallModules` حسب الحاجة، وننشئ component بعد تجهيز replacement. اختبار graph مهم عشان qualifier أو scope غلط ممكن يشتغل unit test ويقع في التطبيق.

## Why it matters and how it works

Hilt generates a component graph with scopes and qualifiers; test replacement alters bindings, not the consumer contract. A local JVM use-case test can construct dependencies directly, while Android instrumentation can test graph construction and injected UI.

## Worked example

For a login screen test, replace `AuthRepository` with a controllable fake in a Hilt test component. Configure its response before launching Activity, then assert UI state. Separately instantiate the production graph in a smoke test to catch missing qualifiers.

## Trade-offs and decision criteria

Full Hilt tests are slower than constructor-injected JVM tests but validate wiring. Use direct construction for behavior and a few graph tests for scopes and qualifiers.

## Failure modes

A singleton fake retains a logged-in session from a previous test, causing order dependence. Reset state per test and avoid shared mutable test objects. A test binding that replaces only one flavor may leave another release graph broken.

## Production perspective

CI verifies unit behavior, instrumentation graph injection and each shipped flavor’s production graph. Test rules clean up components and Main dispatcher after each case.

## Interview answer — short

“I replace dependencies at the intended DI scope, configure them before launching the consumer, and test production graph wiring separately. Shared fake state and wrong qualifiers are common failures.”

## Interview answer — structured

“For a use case, constructor injection makes a fast JVM test enough. For an Android screen, I use Hilt test bindings to replace the repository, then launch the Activity after configuring the fake. I verify scopes and qualifiers so the screen and worker receive the intended instance. I also keep a production graph smoke test because test-only bindings can conceal missing real bindings. The mechanics matter. Hilt generates a component graph with scopes and qualifiers; test replacement alters bindings, not the consumer contract. A local JVM use-case test can construct dependencies directly, while Android instrumentation can test graph construction and injected UI. The choice has a trade-off. Full Hilt tests are slower than constructor-injected JVM tests but validate wiring. Use direct construction for behavior and a few graph tests for scopes and qualifiers.”

## Interview answer — deep senior

“I distinguish behavior testing from graph testing. Most domain behavior uses direct construction and short-lived fakes; a smaller instrumentation layer checks Hilt replacement and the real component hierarchy. I verify singleton versus activity/viewmodel scope, qualifiers and cleanup so tests do not leak session state. A worker that runs after process death may use a different component instance, so its contract gets separate coverage. CI builds every release flavor’s graph, not just the test flavor. Consider a concrete case. For a login screen test, replace `AuthRepository` with a controllable fake in a Hilt test component. Configure its response before launching Activity, then assert UI state. Separately instantiate the production graph in a smoke test to catch missing qualifiers. A failure case illustrates the risk. A singleton fake retains a logged-in session from a previous test, causing order dependence. Reset state per test and avoid shared mutable test objects. A test binding that replaces only one flavor may leave another release graph broken. In production, the response is concrete. CI verifies unit behavior, instrumentation graph injection and each shipped flavor’s production graph. Test rules clean up components and Main dispatcher after each case. The decision has a trade-off. Full Hilt tests are slower than constructor-injected JVM tests but validate wiring. Use direct construction for behavior and a few graph tests for scopes and qualifiers.”

## Deep-dive talking points

Prompt for binding override, scope, setup-before-launch, flavor parity and fake cleanup.

## Follow-up questions

- [TST-08](../tst-08/): Which tests need Hilt? **Answer:** graph/UI wiring; pure use cases can construct directly.
- [TST-15](../tst-15/): How avoid order-dependent tests? **Answer:** isolate and reset shared fake state.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Hilt testing](https://developer.android.com/training/dependency-injection/hilt-testing) — test bindings and components.
- [Android test doubles](https://developer.android.com/training/testing/fundamentals/test-doubles) — dependency replacement.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
