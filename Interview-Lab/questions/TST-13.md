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

اختبار DI لازم يثبت حاجتين مختلفتين: test graph تقدر تستبدل dependency وتتوقع UI behavior، وproduction graph فيها كل bindings/qualifiers/scopes المطلوبة. في Hilt test استبدل `AuthRepository` بfake قبل Activity launch، وخلّي fake ترد بحالة معلومة؛ بعدين assertion على الشاشة أو ViewModel. لو عملت replacement لكل شيء، الاختبار لن يكشف binding ناقصة في build الحقيقي، لذلك ضيف smoke compile/launch للـproduction graph.

## Practical walkthrough

جرّب scope: object اللي المفروض Activity-scoped لا يعيش بعد Activity، وSingleton لا يمسك Activity Context. assisted/runtime parameters لها owner واضح. reset fake state بين tests حتى لا تظهر flakes. الـDI framework أداة لتوصيل graph؛ الاختبار يثبت contract السلوك وعمر dependency.

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

“For a use case, constructor injection makes a fast JVM test enough. For an Android screen, I use Hilt test bindings to replace the repository, then launch the Activity after configuring the fake. I verify scopes and qualifiers so the screen and worker receive the intended instance. I also keep a production graph smoke test because test-only bindings can conceal missing real bindings.”

## Interview answer — deep senior

“I test substitution and graph integrity separately. In a Hilt instrumented test I replace an `AuthRepository` binding with a controllable fake before launching the Activity, then assert Loading, success, denial or retry through the screen. This proves the feature can consume the substituted contract. It does not prove production has the correct qualifier, constructor binding or scope, because the test graph may replace the missing piece. I add a production-graph smoke build or launch in the release-like variant. Scope tests should check lifetime rather than only object identity: an Activity-scoped collaborator must not retain an old Activity after recreation, and a Singleton should not capture Activity Context. I also test runtime parameters where assisted creation is used and clear fake state between tests. I avoid replacing internal details that would make a test pass while the real boundary is broken. DI tests are most useful when they reveal a wrong graph or a user-visible state, not when they merely assert that injection syntax compiled.”

## How to answer in the interview

- **Why:** a replaceable test graph can hide a broken production graph.
- **How:** substitute AuthRepository before Activity launch and separately smoke-test real bindings.
- **Trade-off:** deterministic feature test versus realistic DI wiring.
- **Failure case:** missing qualifier or wrong scope survives fake-only tests.
- **Production solution:** test both user-visible state and release graph construction.

## Deep-dive talking points

Prompt for binding override, scope, setup-before-launch, flavor parity and fake cleanup.

## Follow-up questions

- [TST-08](../tst-08/): Which tests need Hilt? **Answer:** graph/UI wiring; pure use cases can construct directly.
- [TST-15](../tst-15/): How avoid order-dependent tests? **Answer:** isolate and reset shared fake state.

## Self-check rubric

Replace an AuthRepository in a test graph before Activity launch, assert the screen consumes the fake, and separately smoke-test production bindings. Explain scope and qualifier mistakes that a replaced graph can hide.

## References and reviewed-on date

- [Hilt testing](https://developer.android.com/training/dependency-injection/hilt-testing) — test bindings and components.
- [Android test doubles](https://developer.android.com/training/testing/fundamentals/test-doubles) — dependency replacement.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
