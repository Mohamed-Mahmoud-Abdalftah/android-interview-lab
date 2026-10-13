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

عندما يستمر مستمع (Listener) في العمل واستهلاك الموارد بعد مغادرة الـ Composable للشاشة: ما هو الـ Effect الخاطئ وكيف يُعالج؟

1. ما هو الـ Effect الخاطئ الشائع؟
   - الخطأ الكلاسيكي هو استخدام **`LaunchedEffect(Unit)`** أو `SideEffect` لتسجيل Listener خارجي متزامن (مثل `SensorManager`, `LocationListener`, `BroadcastReceiver`, أو SDK Listener).
   - `LaunchedEffect` مخصص للـ Suspending functions؛ عندما يغادر الـ Composable، يقوم بإلغاء الكوروتين الخاص به، ولكنه **لا يعرف كيف ينفذ دالة `unregisterListener()` العادية غير المعلقة!**
   - النتيجة: يظل الـ Listener مسجلاً داخل نظام التشغيل، ويستمر في إرسال الأحداث، مما يسبب تسريب ذاكرة كارثي واستنزاف بطارية الجهاز.

2. ما هو الـ Effect الصحيح الإلزامي؟
   - الـ Effect الصحيح هو **`DisposableEffect(key)`**.
   - يفرض `DisposableEffect` توفير كتلة تنظيف صريحة: **`onDispose { ... }`**.
   - عند مغادرة الـ Composable للشاشة أو عند تغير الـ key، يستدعي Compose دالة `onDispose` فوراً، مما يضمن إلغاء تسجيل الـ Listener بنسبة 100% وتحرير الموارد.

## Practical walkthrough

تصحيح تسريب مستمع المستشعر باستخدام DisposableEffect و onDispose:
```kotlin
// ❌ كود خاطئ: استخدام LaunchedEffect لتسجيل مستمع لا يتم تنظيفه عند المغادرة:
@Composable
fun BadSensorMonitor(sensorManager: SensorManager, sensor: Sensor) {
    LaunchedEffect(Unit) {
        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent?) { /* معالجة */ }
            override fun onAccuracyChanged(s: Sensor?, a: Int) {}
        }
        // 💥 المستمع يستمر في العمل في خلفية الهاتف حتى بعد مغادرة الشاشة!
        sensorManager.registerListener(listener, sensor, SensorManager.SENSOR_DELAY_UI)
    }
}

// ✅ كود سليم: استخدام DisposableEffect مع onDispose الإلزامي للتنظيف:
@Composable
fun GoodSensorMonitor(sensorManager: SensorManager, sensor: Sensor) {
    DisposableEffect(sensorManager, sensor) {
        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent?) { /* معالجة */ }
            override fun onAccuracyChanged(s: Sensor?, a: Int) {}
        }
        sensorManager.registerListener(listener, sensor, SensorManager.SENSOR_DELAY_UI)

        // يُستدعى تلقائياً فور مغادرة الـ Composable أو تغير الـ sensor:
        onDispose {
            sensorManager.unregisterListener(listener)
        }
    }
}
```

## Why it matters and how it works

Composition entry and exit are not identical to Activity START/STOP. `DisposableEffect` pairs setup with cleanup at composition exit or key replacement. A listener registered externally retains references until removed; a coroutine's cancellation may not unregister an SDK callback unless bridged correctly. Lifecycle-aware start/stop utilities may be better when visibility, rather than composition presence, is the requirement.

## Worked example

`LocationBadge` registers a sensor listener in a composable body. Navigating away leaves the sensor active and its callback captures an old state holder. Move registration to `DisposableEffect(sensorManager)` and call `unregisterListener` in `onDispose`; if location should run only while the Activity is STARTED, coordinate with lifecycle as well. A test removes the badge and asserts unregister count and no later UI update.

### Compose/Kotlin walkthrough

```kotlin
@Composable
fun SensorBadge(source: SensorSource, onReading: (Float) -> Unit) {
    val latestCallback by rememberUpdatedState(onReading)
    DisposableEffect(source) {
        val listener = SensorListener { value -> latestCallback(value) }
        source.register(listener)
        onDispose { source.unregister(listener) }
    }
}
// SensorSource/SensorListener are app wrappers around the platform callback API.
// Imports: androidx.compose.runtime.DisposableEffect/rememberUpdatedState/getValue.
```

## Trade-offs and decision criteria

Composition ownership is suitable for UI-only listeners; lifecycle START/STOP ownership better reflects foreground-only resources. ViewModel ownership can survive temporary composition changes but must release at `onCleared`. A global owner may be justified for deliberate background monitoring with permissions and energy budget.

## Failure modes

`LaunchedEffect(Unit)` starts an SDK listener but cancellation does not remove it. `DisposableEffect(Unit)` keeps a listener bound to an old source when source changes. A new callback closes over stale props. Cleanup happens only in Activity `onDestroy` even when composable left much earlier.

## Production perspective

Document source, owner, register/unregister pair and visibility requirement. Test key swap, navigation removal, rotation and late SDK callbacks; inspect battery and heap retention for long-lived listeners.

## Interview answer — short

The wrong effect is `LaunchedEffect(Unit)` or `SideEffect`. They lack cleanup callbacks for non-suspending listeners. When the composable leaves composition, the listener remains registered. The correct solution is `DisposableEffect`, which enforces an `onDispose { ... }` block to unregister listeners synchronously.

## Interview answer — structured

If a callback or listener continues operating after a composable leaves the composition, the developer mistakenly implemented the registration inside **`LaunchedEffect`** or raw composable code.

`LaunchedEffect` is tailored exclusively for cooperative Kotlin coroutines. When a composable leaves the Slot Table, Compose cancels the coroutine job. However, if a non-suspending, platform-level listener (such as `LocationListener`, `SensorEventListener`, or `BroadcastReceiver`) was registered inside the coroutine body, canceling the coroutine does not invoke `unregisterListener()`. The system service retains a strong reference, causing a persistent memory leak and background battery drain.

The mandatory solution is **`DisposableEffect`**:
1. It executes registration upon entering the composition.
2. It mandates a trailing **`onDispose { ... }`** clause.
3. The instant the composable leaves the composition tree (or if any key argument changes), Compose synchronously executes `onDispose`, unregistering the listener cleanly.

## Interview answer — deep senior

Under the hood, `DisposableEffectImpl` implements `RememberObserver`. When the Compose runtime determines during a layout pass that an existing node was pruned from the UI hierarchy, it invokes `onForgotten()` on registered `RememberObserver` instances, directly triggering the `onDispose` lambda.

Another frequent leak pattern is capturing changing parameters inside `onDispose`. If the keys passed to `DisposableEffect(key1)` mutate, Compose first executes `onDispose` for the old keys before executing the effect block for the new keys. If keys are omitted or set to `Unit` while external dependencies mutate, the unregistration might hold stale objects or unregister the wrong instance.

In modern Android architectures, we often hoist these listeners entirely out of the UI into cold Flows in repository/data layers using `callbackFlow { ... awaitClose { unregisterListener() } }`, consuming them in Compose via `collectAsStateWithLifecycle()`.

## How to answer in the interview

- **Why:** external callbacks outlive rendering unless removed.
- **How:** pair registration with disposal under the source key.
- **Trade-off:** composition presence differs from STARTED visibility.
- **Failure case:** stale callback or leak after navigation.
- **Production solution:** test key replacement, exit, and lifecycle stop.

## Deep-dive talking points

Discuss composition versus Lifecycle, callback SDK cancellation, correct keys, stale captures, and leak proof.

## Follow-up questions

- **Interviewer:** "What is `callbackFlow` and why is it preferred over `DisposableEffect` for listeners?"
  **Answer:** "`callbackFlow` encapsulates callback-based APIs into reactive Kotlin Flows with an `awaitClose { ... }` cleanup block, shifting lifecycle management away from UI components into domain/data layers."

- **Interviewer:** "What happens if you omit `onDispose` inside a `DisposableEffect`?"
  **Answer:** "The code will not compile. The Compose compiler enforces `onDispose` as the mandatory return type of a `DisposableEffect` block."

## Self-check rubric

Choose the owner, show register/unregister, handle key changes, and verify late callbacks.

## References and reviewed-on date

- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — DisposableEffect and keys.
- [Lifecycle in Compose](https://developer.android.com/topic/libraries/architecture/lifecycle) — visibility-bound effects.

Technically reviewed against primary documentation on 2026-10-13.
