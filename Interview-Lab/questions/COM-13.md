---
id: "COM-13"
question: "How do you correctly implement Snackbar, navigation, and callbacks?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 242
editorial_status: "reviewed"
---

# COM-13

## Original interview question

How do you correctly implement Snackbar, navigation, and callbacks?

## What the interviewer evaluates

- Separate user actions, UI effects, and destination state.
- Explain Snackbar coroutine ownership and navigation idempotence.
- Handle lifecycle gaps and current callbacks.

## Explanation in Arabic

الـcomposable ترسل event للمالك مثل `onSave` بدل أن تغير NavController أو repository في جسم الرسم. Snackbar هي UI operation: `SnackbarHostState.showSnackbar()` suspend، فتطلقها من callback عبر `rememberCoroutineScope` أو effect مملوكة للشاشة. Navigation ينفذ عند نتيجة صالحة، وليس كل recomposition لــ`success=true`. صمّم one-shot delivery أو state مع acknowledgment كي لا يتكرر بعد rotation، وانتبه أن event stream قد يفوت عندما lifecycle متوقفة. callback داخل effect طويلة قد تصبح قديمة؛ استخدم key مناسب أو `rememberUpdatedState`.

### Practical walkthrough in Egyptian Arabic

في Save، الـbutton يعمل `onSave()` بس. نتيجة الـViewModel لازم تكون event/transition لها ID أو acknowledgment؛ route تنفذ navigation مرة وتعلم إنها اتعالجت. لو فشل، الـroute تعرض snackbar من coroutine مرتبطة بالشاشة؛ لا تكتب `navController.navigate()` في body لما `success` تبقى true. لو event stream غير replayable والشاشة متوقفة، ممكن رسالة النجاح تضيع؛ ولو success Boolean دائمة، navigation ممكن تتكرر. اختار delivery/acknowledgment واضح واختبر rotation والتطبيق في background.

## Why it matters and how it works

Recomposition can re-enter render code, so an imperative UI command must have a clear event trigger and owner. `SnackbarHostState` serializes visual messages through a suspending call. Navigation changes back stack state and should occur once for a particular transition, with `launchSingleTop` or state consumption as appropriate but not as a substitute for a correct event contract. Callback capture depends on effect keys and composition updates.

## Worked example

The user taps Save. The screen invokes `onSave`, the ViewModel submits once, and exposes `Saved(receiptId)` or a consumed navigation action. The route navigates to a receipt ID after observing the transition and marks it handled; if the save fails, it shows a Snackbar using the screen-owned host state. A repeated tap while saving is rejected in both UI and domain layers.

### Compose/Kotlin walkthrough

```kotlin
// Route-level example; ViewModel emits a unique, consumable UiEffect.
LaunchedEffect(viewModel, navController) {
    viewModel.effects.collect { effect ->
        when (effect) {
            is UiEffect.Saved -> navController.navigate("receipt/${Uri.encode(effect.id)}")
            is UiEffect.Error -> snackbarHostState.showSnackbar(effect.message)
        }
    }
}
// Screen: Button(onClick = onSave) { Text("Save") }
// UiEffect/effects are app contracts; import android.net.Uri.
// Define event delivery/acknowledgment for stopped lifecycle and restoration.
```

## Trade-offs and decision criteria

Keeping NavController at route level makes a reusable screen easier to preview and test. A one-off event stream is concise but needs buffering/lifecycle policy; destination state can survive recreation but needs consumption semantics. Snackbars are transient feedback, while durable errors should remain visible in UI state.

## Failure modes

`if (state.saved) nav.navigate(...)` in a composable body navigates repeatedly. A Channel event emitted while stopped is lost. A Snackbar callback uses a scope after the screen leaves. A lambda captured by a Unit-keyed effect points to an old owner.

## Production perspective

Test duplicate taps, rotation during saving, STOP/START delivery, and back navigation. Keep navigation routes typed or validated, and do not pass large sensitive payloads through route arguments.

## Interview answer — short

“User callbacks send intent upward; Snackbar is a screen-owned suspending UI action; navigation follows a consumed result or explicit event contract, never a bare render-body condition. A click emits intent; the route performs one navigation or Snackbar action after a result.”

## Interview answer — structured

“I keep a reusable screen unaware of NavController and pass `onSave` or similar callbacks from its route. The owner handles the request and exposes result state. The route shows transient feedback through `SnackbarHostState` in an owned coroutine, and navigates once when a valid result is consumed. I decide how events behave while stopped and after rotation, and I use current callback handling in long-running effects. Duplicate-tap control is in the use case as well as the button. For Save, I separate the request, its authoritative outcome, and the route’s consumed action.”

## Interview answer — deep senior

“I separate three things that often get conflated: the user's intent, the state resulting from work, and an imperative UI action. The screen emits a callback for Save; a ViewModel or use case owns submission and exposes loading, error or saved data. The route owns navigation because that is a destination concern, and a `SnackbarHostState` owned by the visible Scaffold can show feedback from an event-triggered coroutine. I do not navigate from a composable's plain `if (saved)` body, because recomposition or recreation could replay it. Instead I define a one-time transition with acknowledgment, or encode destination state so the route can consume it deterministically. I test what happens if the Activity is stopped when a result arrives; a Channel with no collector can lose it, while a replaying state can duplicate it unless consumed. For callback observers tied to composition I key the actual owner and use `rememberUpdatedState` when the callback changes without changing registration identity. Finally, a disabled button is UX, not the payment or save idempotency guarantee; the domain/backend boundary must reject duplicate operations. I choose an event-delivery contract that accounts for a stopped lifecycle and process restoration.”

## How to answer in the interview

- **Why:** imperative UI commands need a single trigger.
- **How:** separate button intent, authoritative result, and route action.
- **Trade-off:** a transient stream may miss events while stopped.
- **Failure case:** success state causes repeat navigation after recreation.
- **Production solution:** define consumption and restore-safe destination state.

## Deep-dive talking points

Discuss route/screen split, Snackbar suspension, event delivery, navigation replay, callback capture, and idempotency.

## Follow-up questions

- Why avoid navigation in a composable body? **Answer:** rendering may repeat and trigger duplicate back-stack changes.
- Where should `showSnackbar` launch? **Answer:** from a screen-owned coroutine triggered by an event or controlled effect.
- Can a disabled button guarantee one save? **Answer:** no; domain and backend operations must handle duplicates too.

## Self-check rubric

Trace Save through callback, state, Snackbar or navigation; cover rotation and duplicate delivery.

## References and reviewed-on date

- [Compose Snackbar](https://developer.android.com/develop/ui/compose/components/snackbar) — host and suspending API.
- [Navigation in Compose](https://developer.android.com/develop/ui/compose/navigation) — route navigation practices.
- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — callbacks and effects.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Event-delivery choice is application-specific.
