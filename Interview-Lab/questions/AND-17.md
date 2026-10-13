---
id: "AND-17"
question: "How should you register/unregister lifecycle-dependent listeners?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "B"
phase: 1
priority: "P1"
order: 47
editorial_status: "reviewed"
---

# AND-17

## Original interview question

How should you register/unregister lifecycle-dependent listeners?

## What the interviewer evaluates

- Pair registration with the lifecycle boundary matching the resource and visibility requirement.
- Remove callbacks from their exact owner; distinguish Activity, Fragment, and Fragment view lifecycles.
- Avoid double registration, leaked Context references, and missed events after recreation.

## Explanation in Arabic

تسجيل وإلغاء المستمعين المعتمدين على دورة الحياة (Registering/Unregistering Lifecycle-Dependent Listeners) هو الاختبار الحقيقي لمعرفة ما إذا كان المهندس يكتب كوداً نظيفاً يمنع تسريب الذاكرة:

1. النهج القديم السيئ (The Deprecated / Cluttered Approach):
   - كتابة كود التسجيل والفصل داخل دوال الـ Activity نفسها (`onStart` و `onStop`):
     * المشكلة: تضخم كود الـ Activity (God Activity)، وصعوبة إعادة استخدام المستمع، ونسيان فصل المستمع مما يسبب تسريب الذاكرة (Memory Leak).

2. النهج الحديث المعياري: `DefaultLifecycleObserver`:
   - إنشاء كلاس مستقل للمستمع ينفذ واجهة `DefaultLifecycleObserver`.
   - الكلاس يتولى تسجيل نفسه في `onStart()` وإلغاء تسجيله تلقائياً في `onStop()`.
   - الـ Activity تضيف سطراً واحداً فقط: `lifecycle.addObserver(myListener)`.

3. مطابقة أزواج دورة الحياة بدقة (Symmetric Pairs):
   - **لو سجلت في `onCreate()`:** يجب الإلغاء في **`onDestroy()`**.
   - **لو سجلت في `onStart()`:** يجب الإلغاء في **`onStop()`** (الأكثر شيوعاً للمستشعرات والـ Location).
   - **لو سجلت في `onResume()`:** يجب الإلغاء في **`onPause()`** (للكاميرا أو مستشعرات الحركة الحساسة جداً).

## Practical walkthrough

بناء مستمع موقع جغرافي ذاتي الإدارة (Self-contained Lifecycle Observer):
```kotlin
class LocationTracker(
    private val context: Context,
    private val onLocationChanged: (Location) -> Unit
) : DefaultLifecycleObserver {

    override fun onStart(owner: LifecycleOwner) {
        // 1. تسجيل المستمع عندما تصبح الشاشة مرئية:
        startGpsUpdates()
    }

    override fun onStop(owner: LifecycleOwner) {
        // 2. إلغاء المستمع تلقائياً عندما تختفي الشاشة:
        stopGpsUpdates()
    }
}

// في الـ Activity أو Fragment: سطر واحد فقط نظيف:
class MapActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val tracker = LocationTracker(this) { updatePin(it) }
        lifecycle.addObserver(tracker) // يربط نفسه بدورة الحياة تلقائياً بدون تكرار كود
    }
}
```

## Why it matters and how it works

An event source retains callbacks until removed or its own lifetime ends. A system sensor listener, broadcast receiver, or repository observer can therefore keep a destroyed Activity or view reachable. A lifecycle observer can own registration and disposal at the intended state. For a Fragment view, `viewLifecycleOwner` limits UI collection to the current view instance. Lifecycle-aware collection suspends or cancels the UI observer at a boundary; it does not automatically shut down upstream work with a longer scope.

## Worked example

For a visible-only sensor preview, register the sensor listener in `onStart()` and call `sensorManager.unregisterListener(listener)` in `onStop()`. For a Fragment's UI StateFlow, launch from `viewLifecycleOwner.lifecycleScope` and call `repeatOnLifecycle(Lifecycle.State.STARTED) { state.collect { render(it) } }`. This abbreviated Kotlin assumes the AndroidX lifecycle KTX extensions, an existing listener, and a main-safe `render`; it is not a standalone program.

## Trade-offs and decision criteria

`STARTED` is suitable for visible UI updates; a resource needed while resumed only may use `RESUMED`. A process-wide observer needs a process or application owner, not a transient screen. Automatic `repeatOnLifecycle` removes manual UI collection bookkeeping, but direct platform listeners still need explicit cleanup or a lifecycle wrapper. Missing interim events is acceptable for state streams but may be wrong for one-off operations that require persistence.

## Failure modes

Registration in `onCreate()` with no matching removal keeps receiving callbacks after the screen closes. Collecting against a Fragment lifecycle renders into a destroyed view. Calling register every `onResume()` without symmetric unregister duplicates callbacks. Stop/start races can drop transient events; represent durable state in a repository and reload it on return. Use a heap dump and registration counters to diagnose retention and duplication.

## Production perspective

In a barcode scanning screen, camera preview and sensor updates run only while visible. UI observation uses the view lifecycle; the scan result is persisted before navigation. Instrument active registrations and test rotation, back navigation, split-screen visibility, and app backgrounding. A stop path releases hardware promptly and a recreated screen reads the latest saved result.

## Interview answer — short

Encapsulate listeners inside standalone classes implementing DefaultLifecycleObserver, matching symmetric lifecycle pairs: onStart/onStop for sensors and visibility, onResume/onPause for camera, and onCreate/onDestroy for hardware resources, registered via lifecycle.addObserver().

## Interview answer — structured

The modern, professional way to manage lifecycle-dependent listeners is by implementing **`DefaultLifecycleObserver`** inside a dedicated, self-contained component rather than cluttering Activity callbacks.

To prevent memory leaks and battery drain, listeners must follow strict **symmetric lifecycle pairing**:

1. **`onStart()` and `onStop()` (Standard Default)**: Use for location updates, network monitoring, and UI data streams. The listener registers when the app is visible and unregisters the moment the app is backgrounded, conserving device battery.
2. **`onResume()` and `onPause()`**: Use for exclusive foreground hardware that cannot be shared in multi-window mode, such as the camera hardware or high-frequency accelerometer sensors.

The calling Activity or Fragment simply hooks the component using `lifecycle.addObserver(myListener)`. When the host is destroyed, the lifecycle observer is automatically torn down without manual Activity boilerplate.

## Interview answer — deep senior

Under the hood, `androidx.lifecycle.LifecycleRegistry` manages an internal state machine. When you call `lifecycle.addObserver()`, the registry automatically brings the newly added observer up to the current state of the owner (e.g., if added in `onResume`, it immediately executes `onCreate`, `onStart`, and `onResume` in sequence).

When working with Jetpack Compose, the equivalent paradigm is **`DisposableEffect`**:

```kotlin
DisposableEffect(lifecycleOwner) {
    val observer = LifecycleEventObserver { _, event ->
        if (event == Lifecycle.Event.ON_START) startListening()
        else if (event == Lifecycle.Event.ON_STOP) stopListening()
    }
    lifecycleOwner.lifecycle.addObserver(observer)
    onDispose {
        lifecycleOwner.lifecycle.removeObserver(observer)
    }
}
```

`onDispose` guarantees that the listener is detached when the Composable leaves composition, preventing dangling callbacks.

## How to answer in the interview

- **Why:** Listeners should exist only while their owner can use events.
- **How:** Pair registration and cleanup at matching lifecycle transitions.
- **Trade-offs:** Use view-scoped collection for rendering and a longer owner for genuinely ongoing work.
- **Failure cases:** Mention duplicate registration and callbacks into a destroyed view.
- **Production solution:** Test a sensor preview across rotation, navigation, and background transitions.

## Deep-dive talking points

Discuss callback ownership, STARTED versus RESUMED, Fragment view lifecycle, hot Flow producer scope, and repeat-transition testing.

## Follow-up questions

- **Interviewer:** "Why did `LifecycleObserver` with `@OnLifecycleEvent` annotations get deprecated?"
  **Answer:** "Because it relied on runtime reflection or compile-time annotation processing code generation. `DefaultLifecycleObserver` uses Java 8 default interface methods, providing direct, fast method invocation with zero reflection overhead."

- **Interviewer:** "What happens if a listener is registered in `onStart` but unregistered in `onDestroy`?"
  **Answer:** "Asymmetry bug! Every time the Activity is stopped and restarted (e.g., user presses Home and returns), `onStart` registers another duplicate listener without unregistering the old one, leaking callbacks and stacking duplicate events."

- **Interviewer:** "How does `repeatOnLifecycle` simplify this for Flows?"
  **Answer:** "`repeatOnLifecycle` encapsulates this exact onStart/onStop pairing declaratively for coroutines: it launches flow collection on `ON_START` and cancels the coroutine on `ON_STOP` automatically."

## Self-check rubric

Choose a lifecycle boundary, pair registration and removal, explain Fragment view ownership, distinguish UI collection from producer lifetime, and test rapid transitions.

## References and reviewed-on date

- [Lifecycle-aware components](https://developer.android.com/topic/libraries/architecture/lifecycle) — observer ownership.
- [StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — lifecycle-aware collection.

Technically reviewed against primary documentation on 2026-10-13.
