---
id: "COM-24"
question: "A listener keeps working after a composable leaves composition. Which effect is wrong?"
topic: "Jetpack Compose"
code: "COM"
group: "C"
phase: 3
priority: "P1"
order: 253
editorial_status: "reviewed"
---

# COM-24

## Original interview question

A listener keeps working after a composable leaves composition. Which effect is wrong?

## What the interviewer evaluates

- Identify missing cleanup or wrong ownership rather than naming one API blindly.
- Use DisposableEffect keys and onDispose appropriately.
- Verify actual lifecycle and late callbacks.

## Explanation in Arabic

أول احتمال: listener اتسجل في body أو `LaunchedEffect` بدون unregister، أو اتسجل عبر scope عمرها أطول من composable. لو listener يجب يعيش فقط مع composable، `DisposableEffect(ownerOrSource)` تسجله و`onDispose` تلغيه عند خروج composable أو تغير key. لو callback يتغير لكن المصدر لا، `rememberUpdatedState` يضمن أحدث callback دون إعادة التسجيل. إذا السلوك مطلوب حتى بعد اختفاء UI، فالمالك ربما ViewModel أو service ويحتاج سياسة lifetime واضحة؛ وجود listener مستمر ليس خطأ تلقائيًا قبل تحديد owner.

## Why it matters and how it works

Composition entry and exit are not identical to Activity START/STOP. `DisposableEffect` pairs setup with cleanup at composition exit or key replacement. A listener registered externally retains references until removed; a coroutine's cancellation may not unregister an SDK callback unless bridged correctly. Lifecycle-aware start/stop utilities may be better when visibility, rather than composition presence, is the requirement.

## Worked example

`LocationBadge` registers a sensor listener in a composable body. Navigating away leaves the sensor active and its callback captures an old state holder. Move registration to `DisposableEffect(sensorManager)` and call `unregisterListener` in `onDispose`; if location should run only while the Activity is STARTED, coordinate with lifecycle as well. A test removes the badge and asserts unregister count and no later UI update.

## Trade-offs and decision criteria

Composition ownership is suitable for UI-only listeners; lifecycle START/STOP ownership better reflects foreground-only resources. ViewModel ownership can survive temporary composition changes but must release at `onCleared`. A global owner may be justified for deliberate background monitoring with permissions and energy budget.

## Failure modes

`LaunchedEffect(Unit)` starts an SDK listener but cancellation does not remove it. `DisposableEffect(Unit)` keeps a listener bound to an old source when source changes. A new callback closes over stale props. Cleanup happens only in Activity `onDestroy` even when composable left much earlier.

## Production perspective

Document source, owner, register/unregister pair and visibility requirement. Test key swap, navigation removal, rotation and late SDK callbacks; inspect battery and heap retention for long-lived listeners.

## Interview answer — short

“If a composition-owned listener survives exit, registration and cleanup are mismatched. I use `DisposableEffect` with the real source key and unregister in `onDispose`.”

## Interview answer — structured

“I first identify the intended owner. If the listener exists only for the composable, registering in its body or a long-lived scope is wrong; `DisposableEffect(source)` pairs registration with `onDispose`. Its key must change when the source changes. I use `rememberUpdatedState` if only the callback implementation changes and should stay current without re-registering. If foreground lifecycle rather than composition presence is the contract, I use the corresponding lifecycle mechanism. I verify removal and late callbacks in a test.”

## Interview answer — deep senior

“I would not diagnose this from the word ‘listener’ alone; I ask whether it should be active while the composable is present, while its Activity is STARTED, or for an app-level background task. If it is a UI listener, the common error is registering during rendering or launching a coroutine that registers with an SDK without pairing removal. Compose may recompose, and cancellation of a coroutine does not automatically tell a callback-based SDK to unregister. `DisposableEffect` around the actual source or owner creates the registration once for that identity and runs `onDispose` on key change or exit. If the callback lambda changes while the source stays the same, `rememberUpdatedState` avoids stale capture without churning registration. If the requirement is visible lifecycle, I also coordinate START/STOP; leaving composition and stopping Activity are different events. I test navigation away, source replacement, rotation and a callback delivered after cleanup. The acceptance evidence is no registration retained, no old screen referenced in a heap path, and no unexpected background resource use. If the product truly needs ongoing monitoring, I move ownership to an explicit longer-lived component and document permission and battery cost.”

## Deep-dive talking points

Discuss composition versus Lifecycle, callback SDK cancellation, correct keys, stale captures, and leak proof.

## Follow-up questions

- Does canceling a coroutine always unregister an SDK listener? **Answer:** no; callback registration needs an explicit cleanup bridge.
- When should `DisposableEffect` restart? **Answer:** when a key representing the listener source or owner changes.
- Is every continued listener a bug? **Answer:** only if its intended owner ended; app-owned monitoring may be deliberate.

## Self-check rubric

Choose the owner, show register/unregister, handle key changes, and verify late callbacks.

## References and reviewed-on date

- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — DisposableEffect and keys.
- [Lifecycle in Compose](https://developer.android.com/topic/libraries/architecture/lifecycle) — visibility-bound effects.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Sensor scenario is illustrative.
A listener keeps working after a composable leaves composition. Which effect is wrong?
