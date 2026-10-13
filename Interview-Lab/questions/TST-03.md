---
id: "TST-03"
question: "What are JUnit, MockK/Mockito, Espresso, and Compose UI Testing?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 398
editorial_status: "reviewed"
---

# TST-03

## Original interview question

What are JUnit, MockK/Mockito, Espresso, and Compose UI Testing?

## What the interviewer evaluates

- Roles of JUnit, Mockito/MockK, Espresso and Compose testing.
- Framework choice based on test target rather than popularity.

## Explanation in Arabic

`JUnit` يوفّر test runner وassertions/lifecycle للـtests؛ `MockK` و`Mockito` يعملوا doubles لما نحتاج نعزل dependency أو نراقب تفاعل. `Espresso` تختبر View hierarchy في Android، وCompose UI Testing تستعلم من semantics tree وتنفّذ actions. الأدوات دي مش بدائل متساوية: pure validation function تتختبر بـJUnit في JVM، لكن permission dialog أو lifecycle محتاجان Android test، وزر Compose يحتاج semantics assertion.

## Practical walkthrough

مثال login: اختبر validation كدالة، ViewModel state بـfake repository، ثم UI test يكتب input ويضغط ويتأكد من رسالة الخطأ والـfocus. تجنّب assertion على implementation tags لو label/role كفاية؛ اختبر ما يراه المستخدم. ولا تخلط نجاح UI test مع نجاح backend auth الحقيقي.

## Why it matters and how it works

JUnit is the execution/assertion foundation in JVM/Android test setups. The tool choice follows the boundary under test: logic, Android interaction, or collaboration. Espresso targets View hierarchy and synchronization, while Compose testing queries semantics nodes and drives Compose interactions. Instrumentation/device environment is required for many UI behaviors.

## Worked example

For a Compose login screen, use `createAndroidComposeRule`, find a semantics node by text or tag, enter input and assert an error message. For an old View screen, Espresso `onView(withId(...)).perform(click())` is appropriate. Pure password-validation logic remains a JVM JUnit test.

## Trade-offs and decision criteria

Compose semantics tests are more stable than pixel coordinates but may miss visual regressions; screenshot tests complement them. Mocking UI dependencies can make tests deterministic but hides integration failures; add a few real-path tests.

## Failure modes

An Espresso test sleeps for two seconds to await a network response and flakes on CI. Use a controllable fake or idling resource; Compose tests should use its test clock and wait APIs rather than arbitrary sleeps.

## Production perspective

Choose libraries per UI technology and run release-critical flows on an emulator/device matrix. Keep test selectors accessible and behavior-oriented rather than tied to internal implementation details.

## Interview answer — short

“JUnit runs tests; MockK/Mockito create doubles; Espresso tests Views; Compose UI testing exercises semantics and interactions in Compose. I combine them based on the layer under test.”

## Interview answer — structured

“For pure Kotlin logic I use JUnit with minimal doubles. For Android Views I use Espresso and its synchronization model; for Compose I query semantics nodes through a Compose test rule and control its clock. MockK or Mockito are useful when a collaborator must be controlled, but they do not replace real integration coverage. I avoid fixed sleeps and brittle pixel selectors, then add a device test for the interaction that matters to users.”

## Interview answer — deep senior

“I start with what must be observed, then pick the tool. JUnit supplies execution and assertions for JVM or Android tests. MockK and Mockito create doubles when replacing an external dependency is useful, but they do not define a test layer. Espresso targets traditional Android Views; Compose UI testing queries the semantics tree of composables and performs user actions. For a login feature I would put password policy in fast JVM tests, drive ViewModel states with a controlled repository fake and test the visible validation and submit action in the relevant UI framework. I keep a smaller Android integration test for lifecycle, Activity Result permissions or navigation because a JVM test cannot claim those platform behaviors. A Compose test should prefer accessible text, role or content description over brittle layout structure; tags are useful when localization or duplicated semantics make them necessary. I also separate presentation proof from system proof: tapping Sign In and seeing a spinner does not prove the backend accepted credentials. Finally, I run the release-like build variant where shrinker, manifest or dependency differences could alter behavior.”

## How to answer in the interview

- **Why:** each framework observes a different part of the app.
- **How:** map JUnit, doubles, Espresso and Compose semantics to one login flow.
- **Trade-off:** JVM speed versus Android/platform fidelity.
- **Failure case:** a JVM test claims permission or navigation behavior.
- **Production solution:** keep a small instrumented suite for user-critical integration.

## Deep-dive talking points

Prompt for tool roles, UI technology selection, synchronization and mocks versus real integrations.

## Follow-up questions

- [TST-14](../tst-14/): What does Compose testing query? **Answer:** semantics nodes and interactions.
- [TST-15](../tst-15/): Why avoid sleeps? **Answer:** scheduler/environment timing varies across CI.

## Self-check rubric

Map JUnit to test execution/assertions, MockK or Mockito to test doubles, Espresso to View UI, and Compose testing to semantics. Name one assertion each tool can make and one platform behavior a JVM-only test cannot verify.

## References and reviewed-on date

- [Android testing overview](https://developer.android.com/training/testing) — framework choices.
- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — semantics and test APIs.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
