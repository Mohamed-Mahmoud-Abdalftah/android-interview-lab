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

## Concept and technical explanation

In Android development, lifecycle-dependent listeners—including system location listeners, motion sensors, connectivity broadcast receivers, Bluetooth scanners, and reactive state flows—retain callbacks in memory. If a listener is registered without an unregistration mechanism tied to the host lifecycle, the callback retains a reference to the Activity, Fragment, or View hierarchy, preventing garbage collection and causing substantial memory leaks. Furthermore, continuous background polling of hardware sensors rapidly drains device battery and triggers thermal throttling.
To prevent these regressions, listener lifecycles must strictly mirror component lifecycles. Traditional implementations scattered manual registration calls across Activity callbacks. Modern architecture relies on DefaultLifecycleObserver from Jetpack Lifecycle, which encapsulates registration and unregistration logic within self-contained classes. For reactive streams, coroutine collections should be governed by repeatOnLifecycle, ensuring that subscriptions automatically cancel when the UI is hidden and restart when it becomes visible. In Fragment architectures, UI-bound listeners must observe viewLifecycleOwner to align with the destruction of the View hierarchy.

## Practical walkthrough (English)

A self-contained lifecycle observer decouples sensor registration from the Activity, handling subscription symmetry internally:

```kotlin
class LocationTracker(
    private val context: Context,
    private val onLocationChanged: (Location) -> Unit
) : DefaultLifecycleObserver {

    override fun onStart(owner: LifecycleOwner) {
        startTracking()
    }

    override fun onStop(owner: LifecycleOwner) {
        stopTracking()
    }

    private fun startTracking() {
        // Register location manager updates
    }

    private fun stopTracking() {
        // Remove location updates to conserve power
    }
}
```

In the host Activity or Fragment:

```kotlin
class MapActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val tracker = LocationTracker(this) { location -> updateMap(location) }
        lifecycle.addObserver(tracker)
    }
}
```

Failure scenario: A developer registers a sensor listener in onStart but removes it inside onDestroy. When the user repeatedly opens and closes other applications, the Activity cycles between onStart and onStop. Because onDestroy is never invoked during temporary backgrounding, new listeners accumulate on every restart, resulting in duplicated callback executions and severe battery drain.

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

Register and unregister lifecycle-dependent listeners with strict symmetry matching resource requirements: use onStart and onStop for visibility, onResume and onPause for exclusive hardware like cameras, and onCreate and onDestroy for process allocations. Encapsulate listeners using DefaultLifecycleObserver or repeatOnLifecycle rather than cluttering Activity callbacks. In Fragments, always bind UI listeners to viewLifecycleOwner.

## Interview answer — structured

Managing lifecycle-dependent listeners requires strict symmetry across lifecycle boundaries. Every registration must pair with an equivalent unregistration event: onStart pairs with onStop for visibility-dependent events, while onResume pairs with onPause for exclusive hardware access such as camera capture and high-frequency motion sensors.

Rather than cluttering Activities with boilerplate registration calls, we encapsulate listeners using DefaultLifecycleObserver. By attaching the observer directly to the host's LifecycleOwner, the component manages its own subscription lifecycle automatically, decoupling business logic from framework callbacks.

In production, involving asynchronous data streaming, we use repeatOnLifecycle or flowWithLifecycle for Coroutine collections. This suspends upstream data flow when the app is placed in the background, preventing unnecessary background processing and eliminating crashes caused by updating destroyed views.

In Fragment implementations, we bind all UI-related observers and ViewBinding references to viewLifecycleOwner. This prevents memory leaks when the Fragment's view hierarchy is destroyed in the back stack while the Fragment instance remains retained in memory.


## Interview answer — deep senior

Under the hood, registering a callback with a system service such as SensorManager or LocationManager passes an interface implementation across a Binder IPC interface or registers a local listener inside the system service's native client stub. If the host Activity fails to unregister the listener before destruction, the system service maintains a strong reference to the listener stub, which in turn holds an implicit reference to the enclosing Activity class. The ART garbage collector cannot reclaim the Activity, leaking its entire View hierarchy, Bitmaps, and ContextImpl structures in the Java heap.
From a threading and state machine perspective, DefaultLifecycleObserver methods are invoked sequentially on the main thread via the LifecycleRegistry. When using lifecycleScope.launch alone without repeatOnLifecycle, a coroutine continues collecting flow emissions even after onStop, consuming CPU cycles and potentially crashing if it interacts with detached UI components. Calling repeatOnLifecycle(Lifecycle.State.STARTED) launches a new child coroutine in onStart and cancels the underlying Job immediately when the state transitions to onStop. When the user navigates back to the screen, a new coroutine is spawned, collecting fresh emissions seamlessly.
In enterprise architectures, we audit listener lifecycles by integrating LeakCanary into debug builds to detect lingering observers. For hardware-intensive features like camera and audio processing, we enforce onResume and onPause bounds to release exclusive device hardware locks immediately when the window loses focus, ensuring reliable multi-window support and preventing system-level hardware lock contention across concurrent applications.

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
