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

JUnit بتنظم test cases وassertions/runner؛ Mockito وMockK لtest doubles والتحقق من calls؛ Espresso بتتفاعل مع Android Views مع idling synchronization؛ Compose UI testing بتستخدم semantics tree وCompose test rules. دول مش بدائل لبعض: تقدر تستخدم JUnit مع mock framework، وUI framework حسب نوع الشاشة.

## Why it matters and how it works

JUnit is the execution/assertion foundation in JVM/Android test setups. Mockito/MockK replace collaborator behavior. Espresso targets View hierarchy and synchronization, while Compose testing queries semantics nodes and drives Compose interactions. Instrumentation/device environment is required for many UI behaviors.

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

“For pure Kotlin logic I use JUnit with minimal doubles. For Android Views I use Espresso and its synchronization model; for Compose I query semantics nodes through a Compose test rule and control its clock. MockK or Mockito are useful when a collaborator must be controlled, but they do not replace real integration coverage. I avoid fixed sleeps and brittle pixel selectors. Mockito/MockK replace collaborator behavior.”

## Interview answer — deep senior

“I select tools from the architecture, not from fashion. A ViewModel’s state machine is usually cheapest in a JVM test with a fake repository and TestDispatcher. A Compose screen uses semantics assertions for accessibility and navigation behavior; a legacy View uses Espresso. For database, permission or SDK behavior I run instrumentation on devices. Mock frameworks are deliberately narrow: verifying incidental calls makes tests fragile. CI separates fast feedback from slower device journeys and captures screenshots/logs only with redaction.”

## Deep-dive talking points

Prompt for tool roles, UI technology selection, synchronization and mocks versus real integrations.

## Follow-up questions

- [TST-14](../tst-14/): What does Compose testing query? **Answer:** semantics nodes and interactions.
- [TST-15](../tst-15/): Why avoid sleeps? **Answer:** scheduler/environment timing varies across CI.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android testing overview](https://developer.android.com/training/testing) — framework choices.
- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — semantics and test APIs.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
