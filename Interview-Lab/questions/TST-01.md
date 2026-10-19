---
id: "TST-01"
question: "Compare unit, integration, instrumentation, UI, and end-to-end tests."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 396
editorial_status: "reviewed"
---

# TST-01

## Original interview question

Compare unit, integration, instrumentation, UI, and end-to-end tests.

## What the interviewer evaluates

- Separate test scope, execution environment, and subject; the five names are not mutually exclusive tiers.
- Choose a test that observes the relevant failure with reasonable speed and determinism.
- State what a fake, device test, UI test, and full journey can and cannot prove.

## Concept and technical explanation

Unit, integration, and end-to-end describe roughly how much of the system a test includes. A unit test checks a small rule in isolation; an integration test checks cooperating components or a real boundary; an end-to-end test follows a broad user journey. Instrumentation says where an Android test runs: on a physical or emulated device with the Android framework. UI says what is under test: interaction and rendered or semantic behavior. These categories overlap. A Room DAO test can be both integration and instrumented; a Compose screen test can be UI and instrumented; a full checkout can be UI and end-to-end.

Local tests run on the host, commonly in `src/test/`. Device tests commonly live in `src/androidTest/`. A JVM fake repository test can prove a ViewModel maps a timeout to an error state, but cannot prove Room migration or device permission behavior. A device test can exercise a real Android boundary, but a fake backend does not prove a production payment processor contract.

## Practical walkthrough (English)

Take a checkout flow. Test a pure fee policy with a local unit test. Test repository mapping against a controlled HTTP server or a Room database with an integration test; use a device if the actual Android platform behavior matters. Test the confirmation screen's enabled state and accessibility semantics with a UI test. Keep a small end-to-end sandbox journey for the full request and response contract, including an unknown or timed-out result. State which backend is used and reset test data. Do not let a mocked success response stand in for a verified transaction.

## Explanation in Arabic

التصنيفات دي مش خمس درجات منفصلة. `Unit` و`Integration` و`End-to-End` بتتكلم عن حجم الجزء اللي الاختبار بيغطيه. `Instrumentation` بتقول الاختبار شغال على جهاز Android حقيقي أو Emulator. `UI Test` بتقول أنت بتختبر تفاعل الشاشة وسلوكها. ممكن اختبار `Room DAO` يبقى Integration وInstrumented في نفس الوقت، واختبار شاشة Compose يبقى UI وInstrumented.

الـ Local Test غالبًا في `src/test/` وبتشتغل على Host JVM؛ الـ Device Test غالبًا في `src/androidTest/`. لو اختبرت ViewModel بـ Fake Repository، أثبتّ Mapping حالات الـ UI حسب الـ Fake، مش Migration قاعدة البيانات ولا Permission على جهاز. الاختبار الصح يعتمد على الـ Risk اللي عايز تكشفه، مش اسم طبقة محفوظ.

## Practical walkthrough

في Checkout Flow أختبر حساب الرسوم كـ Unit Test محلي. أختبر Repository مع Mock HTTP Server أو Room فعلية كـ Integration؛ ولو سلوك Android نفسه مهم أستخدم Device Test. أختبر زر التأكيد وAccessibility Semantics كـ UI Test. وأخلي Journey صغيرة في Sandbox تغطي Request/Response الحقيقيين وحالة Timeout أو Unknown، مع Test Data معزولة. Mock Response ناجحة ما تثبتش إن Processor وافق أو إن الفلوس اتحركت.

## Why it matters and how it works

The useful axes are scope, environment, and subject. A narrow test gives fast diagnosis but cannot observe omitted boundaries. A broad test can catch contract mismatches but needs controlled data and failure handling. Device execution gives platform fidelity where needed, not automatic correctness. Test selection should follow the concrete risk: pure fee math, Room migration, Compose interaction, or a processor sandbox contract require different evidence.

## Worked example

For a fee rule, a local test asserts the result for zero, boundary, and invalid amounts. For a Room migration, a device integration test opens an old schema and verifies the new schema preserves rows. For a Compose screen, a UI test checks that an error state is visible and the retry control works. For checkout, a sandbox end-to-end run checks the app and backend agree on a transaction status. These are test designs, not executable snippets or claims of payment certification.

## Trade-offs and decision criteria

Use fast local tests for many deterministic rule cases. Add integration tests when data mapping, persistence, or network contracts are the risk. Use device tests for behavior that depends on the Android runtime or supported API levels. Use UI tests for visible interaction and semantics, and a limited number of end-to-end journeys for cross-system failures. A larger test is not inherently more reliable; uncontrolled clocks, state, networks, and animations can make it less diagnostic.

## Failure modes

A fake DAO lets a ViewModel test pass while a Room migration loses data. A device test using a fake HTTP response passes while the real backend contract changes. An end-to-end test with shared accounts becomes order-dependent. A flaky UI test that waits a fixed time hides missing synchronization. Counting tests or prescribing a fixed percentage per layer says little about the risks actually covered.

## Production perspective

Run deterministic local tests early in CI, then integration and device tests on the supported configuration matrix. Reserve expensive end-to-end runs for critical journeys, keep accounts and data isolated, and report which external systems are real or simulated. Diagnose flaky tests rather than retrying them indefinitely. For payment journeys, use a documented sandbox contract and never equate a successful UI assertion with financial settlement.

## Interview answer — short

I compare tests on three axes. Unit, integration, and end-to-end describe scope; instrumentation means the test runs on an Android device; UI means it checks user-visible behavior. So a Room test can be both integration and instrumented. I put fee rules in fast local tests, Android-specific persistence or permissions on a device, screen interaction in UI tests, and a few controlled full journeys for cross-system risks.

## Interview answer — structured

Those five labels overlap. Unit tests check a small rule, integration tests check collaborating components or a real boundary, and end-to-end tests cover a larger journey. Instrumented means the test runs on an emulator or device, while UI describes the behavior under test. A Compose UI test can also be instrumented; a Room migration test can be both integration and instrumented.

For checkout, I test fee calculation locally with many edge cases. I test repository mapping with a controlled HTTP server and Room migration against a real database when persistence matters. I use a UI test for button state and accessibility semantics. A small sandbox end-to-end test then checks the app and backend contract, including a timeout or unknown result.

Each gives different evidence. A fake repository ViewModel test does not prove the real database or backend works. A full journey is useful for integration risk but slower and harder to diagnose. I choose the narrowest test that can actually observe the failure, and keep high-risk cross-system paths covered without relying on a fixed test pyramid ratio.

## Interview answer — deep senior

I frame the choice by scope, environment, and subject. Scope runs from a small pure rule through multiple cooperating components to a complete user journey. Environment is host or Android device. Subject might be business logic, persistence, UI semantics, or a network contract. These are orthogonal enough that calling them five mutually exclusive tiers is misleading. Android's testing guide explicitly gives examples of both a broad local test and a narrow instrumented test.

I would map an incident to the first boundary where a test could have caught it. A wrong fee formula belongs in a deterministic unit test with boundary cases. A DTO mapper or Room migration needs the relevant real component, not just a fake. A permission result or framework lifecycle needs a device when host simulation would miss the behavior. A Compose UI test checks interaction and semantics; it does not by itself prove the backend processed a request. For checkout, a small sandbox end-to-end suite checks the documented contract and handles unknown outcomes without asserting settlement from a screen state.

The trade-off is diagnostic speed versus coverage of real boundaries. Local tests generally give faster feedback, but I do not invent a universal millisecond time or mandate an 80/20 test split. Device and end-to-end tests require isolated accounts, controlled clocks where possible, synchronization with asynchronous UI, and explicit reset paths. When one flakes, I find the uncontrolled dependency before adding retries. CI can stage fast checks early and run a supported device matrix and critical journeys later. I report exactly which integrations were real and which were faked.

## How to answer in the interview

Start by separating scope, environment, and subject. Give one example where labels overlap, then map a concrete feature risk to the cheapest test that can observe it. End with a limitation of the fake or sandbox.

## Deep-dive talking points

Local versus instrumented; small, medium, and big scope; Room migrations; Compose semantics; controlled HTTP servers; sandbox contracts; test data isolation; flake diagnosis.

## Follow-up questions

- **Interviewer:** "Is every instrumented test end-to-end?" **Answer:** "No. A small SQLite or framework test on a device is instrumented but can have narrow scope."
- **Interviewer:** "Does a ViewModel test with a fake DAO prove Room works?" **Answer:** "No. It proves behavior against the fake. I need a test of the real DAO or migration for persistence."
- **Interviewer:** "Why can a UI test be flaky?" **Answer:** "Uncontrolled animation, clocks, network, or shared state. I use proper synchronization and isolate data before retrying."

## Self-check rubric

Can I classify one test on all three axes, explain what a fake cannot prove, and choose a real-boundary test for a concrete failure risk?

## References and reviewed-on date

- [Android testing fundamentals](https://developer.android.com/training/testing/fundamentals) — scope and local versus instrumented environments.
- [Android testing guidance](https://developer.android.com/training/testing) — official test entry points.
- [Compose UI testing](https://developer.android.com/develop/ui/compose/testing) — interactions and semantics.

Technically reviewed against current primary Android documentation on 2026-10-19; agent editorial review, not human verification.
