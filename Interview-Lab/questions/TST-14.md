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

Compose UI test تتعامل مع semantics، مش ترتيب الـcomposables في source. ابحث عن node بالنص أو role أو content description، واستخدم test tag فقط عند الحاجة، ثم أدخل input واضغط وتأكد من state/destination. في checkout جرّب amount غير صالح: رسالة Error واضحة، Pay لا يعمل charge، ولا تظهر شاشة التأكيد؛ وبعد قيمة صحيحة تأكد من Pending ثم النتيجة المناسبة.

## Practical walkthrough

Navigation يُختبر بمحتوى الشاشة التي وصل لها المستخدم، مش mock لـ`navigate()`. accessibility تحتاج labels وroles وfocus وfont scaling وRTL؛ automated semantics assertions تساعد لكن لا تستبدل TalkBack/manual device pass. Fake payment source يجعل test حتمية، لكن لا يثبت approval حقيقي أو Android permission dialog. اختبر Route/platform integration منفصلًا.

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

“I write Compose tests from the user’s point of view. I query the semantics tree by visible text, role or content description, perform typing and clicks, and assert the resulting UI state. For a checkout form I enter an invalid amount, tap Pay and verify a readable error appears while confirmation remains absent. With valid input I release a controlled fake response and assert the pending state and final accessible destination. I avoid matching an exact composable hierarchy; semantics merging can change without changing the user contract. A navigation test should observe the destination, not merely verify a mocked `NavController.navigate` call. Accessibility assertions cover names for icon buttons, error text, action availability and focus where feasible, with RTL and large-font layouts checked on representative devices. Automated tests cannot certify TalkBack behavior or payment authorization, so I keep targeted manual/device accessibility checks and backend integration tests. I also control animation time and lifecycle recreation rather than adding arbitrary sleeps.”

## How to answer in the interview

- **Why:** users interact with semantics and destinations, not composable internals.
- **How:** type invalid/valid input, click and assert error, pending and destination.
- **Trade-off:** stable semantic selectors versus tags tied to implementation.
- **Failure case:** test only verifies navigate() call or ignores inaccessible icon labels.
- **Production solution:** UI assertions plus device accessibility review.

## Deep-dive talking points

Prompt for semantics tree, merged nodes, accessible name, navigation outcome and RTL/font scaling.

## Follow-up questions

- [TST-17](../tst-17/): What catches pixel regressions? **Answer:** screenshot tests alongside semantic tests.
- [TST-18](../tst-18/): What after rotation? **Answer:** visible state should restore from proper owner.

## Self-check rubric

Use semantics to enter invalid input, assert an accessible error and absent destination, then submit valid input and assert pending/navigation state. Identify one screen-reader or platform behavior requiring device review.

## References and reviewed-on date

- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — semantics and test rules.
- [Compose accessibility](https://developer.android.com/develop/ui/compose/accessibility) — semantics and accessible UI.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
