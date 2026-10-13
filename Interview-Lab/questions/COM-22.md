---
id: "COM-22"
question: "How do you support accessibility, screen readers, and adaptive layouts?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 251
editorial_status: "reviewed"
---

# COM-22

## Original interview question

How do you support accessibility, screen readers, and adaptive layouts?

## What the interviewer evaluates

- Address semantics, roles, labels, focus and touch targets.
- Adapt to window size and text scaling rather than device labels alone.
- Include RTL, screen-reader and real-device verification.

## Explanation in Arabic

في Compose، semantics تقدم معنى العنصر لخدمات accessibility والاختبارات: label، role، state، action. أي icon-only button يحتاج وصف مفهوم؛ decorative icon يمكن إخفاؤه من القراءة إذا parent يشرح الوظيفة. رتّب focus منطقيًا، لا تدمج semantics بشكل يمحو actions، ووفّر touch targets مناسبة. التصميم المتكيف يعتمد على مساحة النافذة الفعلية (window size classes) وليس “tablet” من model name؛ اختبر split-screen، foldable، font scaling وRTL عربي. UI تنقل المعلومات النصية بوضوح حتى لو اللون لا يُرى.

### Practical walkthrough in Egyptian Arabic

زرار أيقونة بس لازم يبقى له وصف مفهوم للـTalkBack، والـdecorative icon ما تتقرأش مرتين. في layout كبيرة استخدم المساحة المتاحة، مش اسم الجهاز؛ split-screen ممكن يخلي tablet ضيق. اختبر Arabic RTL و200% font وتاب keyboard وترتيب القراءة، لأن screenshot سليمة مش كفاية. لو icon بتعمل action مختلفة عن الصف، دمج semantics كله ممكن يخفيها من TalkBack. جرّب swipe order وkeyboard focus على نافذة ضيقة مع font كبير قبل اعتماد التصميم.

## Why it matters and how it works

Accessibility services consume a semantics tree that can differ from the visual composable tree. Material components provide some built-in semantics, but custom controls need explicit meaning and actions. Window size can change at runtime through resizing or folding; adaptive layout should respond to current constraints. Large text and RTL can change line breaks, order and available target space.

## Worked example

A transaction row displays amount, merchant and a small receipt icon. Give the row a clear combined spoken description and an accessible “Open receipt” action, or keep icon action separately focusable if it does something distinct. On compact width use a single column; on expanded width show list/detail panes. Test TalkBack swipe order, keyboard focus, 200% font and Arabic layout with a resizable emulator.

### Compose/Kotlin walkthrough

```kotlin
@Composable
fun ReceiptAction(onOpen: () -> Unit) {
    IconButton(onClick = onOpen) {
        Icon(Icons.Default.Info, contentDescription = "Open receipt")
    }
}
@Composable
fun AdaptiveOrders(width: Dp, orders: List<OrderUi>) {
    if (width < 600.dp) OrdersList(orders)
    else Row { OrdersList(orders); OrderDetails() }
}
// Imports: material3.IconButton/Icon, material.icons.Icons,
// material.icons.filled.Info, ui.unit.Dp/dp.
// In production derive width from current window constraints/window size class.
```

## Trade-offs and decision criteria

Merged semantics reduce verbosity for a row but can hide independent actions, so choose based on interaction. Two-pane layouts use available width well but need state continuity when crossing breakpoints. Custom drawing affords control but requires more accessibility work than standard Material controls.

## Failure modes

A clickable Box has no role or label. Two actions are merged into one inaccessible node. A fixed-height card clips text at large font scale. Layout chooses tablet mode from device type and fails in split-screen. RTL reverses visual order without a sensible reading order.

## Production perspective

Add semantics assertions, automated accessibility checks where available, and hands-on TalkBack/keyboard tests. Maintain a matrix for compact/expanded windows, font scaling, dark mode and Arabic RTL; inspect focus after navigation or dialog changes.

## Interview answer — short

“I give controls meaningful semantics and touch targets, verify TalkBack/focus, and adapt layout to current window size, text scale and RTL. Give controls meaningful semantics and adapt to current window space.”

## Interview answer — structured

“I use standard components when possible because they carry baseline semantics, then add clear labels, roles, states and actions for custom UI. I test screen-reader order and keyboard focus, not just visual screenshots. For adaptive layouts I branch on current window constraints or size classes, so split-screen and fold changes work. I also test large fonts and Arabic RTL for clipping and logical order. I would make an icon-only receipt action speak its purpose and switch layout at a width constraint.”

## Interview answer — deep senior

“I treat accessibility as part of the UI contract. The semantics tree needs to tell a screen reader what each control is, its state, and what action it performs; a visual icon alone is not enough. For a transaction row, I decide whether to merge merchant and amount into one concise spoken unit or expose the receipt action separately. I verify focus order, actionable target size and state changes with TalkBack and keyboard, because a passing screenshot cannot reveal those failures. For adaptive design I respond to the app window's actual width and posture rather than assuming every tablet is wide or every phone is narrow; multi-window and folding change constraints while the app runs. A list/detail layout may collapse to one pane, so selected-item state must survive that transition. Large font scaling, Arabic RTL, dark mode and color contrast are part of the same test matrix. I prefer standard Material components for built-in behavior but inspect custom semantics and avoid merging nodes that hide independent actions. Device and assistive-technology checks complete the evidence beyond automated assertions. I verify TalkBack order, keyboard focus, 200% text, and Arabic RTL on resizable windows.”

## How to answer in the interview

- **Why:** semantics and current window space determine usability.
- **How:** show a spoken action and a responsive branch.
- **Trade-off:** merged semantics can hide distinct actions.
- **Failure case:** color-only status or clipped large text.
- **Production solution:** test TalkBack, keyboard, RTL, resizing, and font scaling.

## Deep-dive talking points

Discuss semantics tree, roles/actions, merge policy, focus, current window size, fold changes, font scaling and RTL.

## Follow-up questions

- Is a content description enough for every custom control? **Answer:** no; role, state, action and focus behavior may also be needed.
- Why use window size rather than device category? **Answer:** a window can resize or enter split-screen regardless of device model.
- What can semantics merging break? **Answer:** independent child actions may become hidden from assistive navigation.

## Self-check rubric

Design one accessible row, choose an adaptive breakpoint response, and describe TalkBack/RTL verification.

## References and reviewed-on date

- [Compose semantics](https://developer.android.com/develop/ui/compose/accessibility/semantics) — accessibility meaning and actions.
- [Window size classes](https://developer.android.com/develop/adaptive-apps/guides/use-window-size-classes) — adaptive layout decisions.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Device validation remains necessary.
