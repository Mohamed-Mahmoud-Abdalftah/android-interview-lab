---
id: "TST-14"
question: "How do you test Compose UI semantics, navigation, and accessibility?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 409
editorial_status: "reviewed"
---

# TST-14

## Original interview question

How do you test Compose UI semantics, navigation, and accessibility?

## What the interviewer evaluates

- Semantics-based Compose assertions and accessible interactions.
- Navigation contract versus implementation-specific route strings.

## Explanation in Arabic

Compose UI tests بتتعامل مع semantics tree: `onNodeWithText` أو content description/test tag عند الضرورة، وتعمل click/typing/assertions. نختبر إن المستخدم يقدر يوصل للشاشة، error واضح، focus وaccessibility labels صحيحة. Navigation نختبره من فعل المستخدم وvisible destination، مش بس إن `navController.navigate()` اتنادت.

## Why it matters and how it works

Compose test rules synchronize with recomposition and expose semantics nodes. Merged semantics can hide child nodes, so understand `useUnmergedTree` only when needed. Accessibility checks require meaningful labels, roles and state descriptions, not arbitrary test tags.

## Worked example

On a checkout form, enter an invalid amount, tap Pay, assert a readable error and that confirmation does not appear. Then provide valid input, tap Pay and assert a pending state and accessible confirmation destination. Use a fake payment source to avoid real charges.

## Trade-offs and decision criteria

Test tags are stable when text is localized, but overusing them can bypass user-visible semantics. Screenshot tests catch visual regressions but cannot replace semantic/a11y assertions.

## Failure modes

A button appears visually but has no content description when icon-only, so screen readers cannot identify it. A test selecting by internal tag passes; add semantics assertion or accessibility audit.

## Production perspective

Run Compose tests on supported screen sizes, RTL locales and font scaling; include keyboard/focus flow and TalkBack review for critical paths. Financial outcome remains backed by domain state, not a UI click assertion.

## Interview answer — short

“I test Compose through semantics and user actions, assert visible navigation outcomes, and include accessibility labels, focus and state. Tags help when needed but should not replace user-facing assertions.”

## Interview answer — structured

“Compose UI testing queries semantics nodes, performs clicks and text input, then asserts resulting UI state. I verify navigation by the destination the user sees rather than mocking a `navigate` call. For accessibility I check labels, roles and error announcements, and I test RTL/font scaling for important screens. A fake backend keeps tests deterministic; separate integration tests verify real payment state. ”

## Interview answer — deep senior

“I write UI tests around user intent and semantic output. I account for merged semantics, avoid brittle hierarchy selectors and use tags only when localization makes text unsuitable. A checkout test covers invalid input, loading, unknown outcome and retry affordance, and checks that an icon-only control has an accessible name. I test navigation across rotation where relevant and use device-level accessibility review beyond automated assertions. The UI test proves presentation and interaction, not issuer approval.”

## Deep-dive talking points

Prompt for semantics tree, merged nodes, accessible name, navigation outcome and RTL/font scaling.

## Follow-up questions

- [TST-17](../tst-17/): What catches pixel regressions? **Answer:** screenshot tests alongside semantic tests.
- [TST-18](../tst-18/): What after rotation? **Answer:** visible state should restore from proper owner.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — semantics and test rules.
- [Compose accessibility](https://developer.android.com/develop/ui/compose/accessibility) — semantics and accessible UI.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
