---
id: "MEM-12"
question: "How can callbacks, Handler, observers, listeners, or static references cause leaks?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "B"
phase: 1
priority: "P1"
order: 67
editorial_status: "reviewed"
---

# MEM-12

## Original interview question

How can callbacks, Handler, observers, listeners, or static references cause leaks?

## What the interviewer evaluates

- Trace a concrete retaining chain from a long-lived owner to a short-lived screen.
- Choose symmetry, lifecycle-aware observation, or cancellation for each API.
- Separate leak prevention from mere exception suppression.

## Concept and technical explanation

Callbacks, Handlers, observers, listeners, and static variables cause memory leaks through the creation of unintentional, persistent reference chains from long-lived GC Roots to short-lived UI components. In the Java and Kotlin object model, non-static inner classes, anonymous interfaces, and lambdas implicitly capture a strong reference to their enclosing outer class instance (this$0). When an Activity or Fragment registers such a callback with a long-lived component—such as an active Handler message queue, a singleton event bus, a system sensor manager, or a static list—the short-lived UI component becomes transitively anchored to an enduring GC Root. Even after the Activity finishes or is recreated on rotation, the garbage collector cannot reclaim it because the live root path preserves reachability, causing steady memory accumulation.

## Practical walkthrough (English)

Analyzing Handler message leak mechanics and lifecycle-safe remediation:
```kotlin
// Leaky Handler: Anonymous Runnable holds implicit reference to Activity:
class LeakyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Delayed message holds Runnable, which holds LeakyActivity via this$0:
        handler.postDelayed({
            updateTitle() // Implicitly references LeakyActivity.this
        }, 60_000) // 1-minute delay leaks Activity across rotation!
    }
}

// Correct: Removing callbacks symmetrically or using lifecycle coroutines:
class SafeActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Coroutine automatically cancelled when Activity finishes:
        lifecycleScope.launch {
            delay(60_000)
            updateTitle()
        }
    }
}
```
Using lifecycleScope ensures that when the Activity is destroyed, the coroutine is cancelled and the continuation is released from the main looper, preventing memory retention.

## Explanation in Arabic

كيف تسبب الكولباكس (Callbacks)، الـ Handlers، الـ Observers، الـ Listeners، والمراجع الاستاتيكية (Static References) تسريبات ذاكرة؟

1. المراجع الاستاتيكية (Static References):
   - أي متغير ثابت (`companion object` أو `static field` في Java) يعيش في الذاكرة طوال حياة التطبيق.
   - إذا احتفظ المتغير الاستاتيكي بمرجع لنشاط (Activity) أو View أو كائن واجهة، فلن يستطيع مجمع النفايات تحريره إطلاقاً، مما يجعله GC Root دائم.

2. الـ Handlers والـ MessageQueue:
   - الـ `Handler` غير الثابت (Non-static inner class) في Java/Kotlin يحتفظ ضمنياً بمرجع للكائن الخارجي (`this@Activity`).
   - عندما ترسل رسالة مؤجلة (`handler.postDelayed(runnable, 60000)`):
   - الرسالة توضع في الـ `MessageQueue` الخاص بالـ Looper الرئيسي.
   - الكائن `Message` يحتفظ بمرجع للـ `Handler` (target)، والـ `Handler` يحتفظ بمرجع للـ `Activity`.
   - إذا خرج المستخدم من الشاشة، يظل النشاط مسرباً في الذاكرة طوال الـ 60 ثانية حتى يتم استهلاك الرسالة!

3. الـ Listeners والـ Observers غير الملغاة:
   - تسجيل Listener في خدمة طويلة الأجل (مثل `LocationManager` أو `SensorManager` أو Event Bus أحادي) يضيف مرجعاً للـ Activity إلى قائمة الملاحظين.
   - إذا نسيت إلغاء التسجيل في `onStop()` أو `onDestroy()` (`unregisterListener()`)، تظل الخدمة ممسكة بالـ Activity إلى الأبد.

## Practical walkthrough

أمثلة شائعة للتسريبات وكيفية معالجتها بدقة:
```kotlin
// ❌ أمثلة شائعة للتسريب:
class LeakyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper()) // كائن داخلي يمسك النشاط

    override fun onStart() {
        super.onStart()
        // 1. تسريب Handler: مهمة مؤجلة تبقى في MessageQueue:
        handler.postDelayed({ showPromotionDialog() }, 120_000)

        // 2. تسريب Listener: تسجيل في Singleton بدون إلغاء التسجيل:
        AuthManager.registerListener { onAuthStatusChanged(it) }
    }
}

// ✅ الكود النظيف المحمي من التسريب:
class SafeActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())
    private val authListener: (Boolean) -> Unit = { onAuthStatusChanged(it) }

    override fun onStart() {
        super.onStart()
        AuthManager.registerListener(authListener)
    }

    override fun onStop() {
        super.onStop()
        // إلغاء المهام المؤجلة وإلغاء تسجيل الملاحظين فوراً:
        handler.removeCallbacksAndMessages(null) // مسح الـ MessageQueue
        AuthManager.unregisterListener(authListener) // تحرير مرجع النشاط
    }
}
```

## Why it matters and how it works

GC reclaims only unreachable graphs. A system or application event source can remain reachable after an Activity closes; its callback then retains the Activity through an implicit `this`, binding, or View reference. Handler queues retain scheduled Runnable objects until execution/removal. Lifecycle-aware observers can remove themselves with an owner, but choosing Fragment instead of Fragment view lifecycle can still retain an obsolete view. A static field is process-lived and should hold only appropriately scoped data.

## Worked example

A screen registers a network-status listener in `onStart()` and removes it in `onStop()`. It also posts a delayed UI hint and removes that Runnable with `handler.removeCallbacks(hintRunnable)` in `onStop()` or view teardown. On re-entry, fresh callbacks are registered for the new view. The pattern assumes a known Handler and listener; the exact API cleanup must match the registration source.

This Android sketch assumes a `HintScheduler` owned by a Fragment view and disposed in `onDestroyView()`. It is illustrative, not compiled here.

```kotlin
import android.os.Handler
import android.os.Looper
import android.view.View

class HintScheduler(private val hintView: View) {
    private val handler = Handler(Looper.getMainLooper())
    private val hint = Runnable { hintView.visibility = View.VISIBLE }

    fun schedule() {
        handler.postDelayed(hint, 2_000L)
    }

    fun dispose() {
        handler.removeCallbacks(hint)
    }
}
```

Call `dispose()` during view teardown and release the `HintScheduler` field; remove any SDK listener separately with its matching API.

## Trade-offs and decision criteria

Lifecycle-aware Flow/LiveData collection reduces manual cleanup for UI rendering, but external SDK callbacks still require explicit unregister or adapter design. A weak reference can avoid retention but may yield missed callbacks and does not resolve stale operation ownership. A durable event should be stored in a repository rather than relying on a screen callback surviving backgrounding.

## Failure modes

A Handler Runnable references a destroyed binding and crashes later. A singleton callback list grows on each rotation, causing both leaks and duplicate events. A static Context is an Activity rather than application Context. Removing a callback with a different instance does nothing. Test repeated open/close cycles, count registrations, and inspect shortest heap paths from leaked views to roots.

## Production perspective

Wrap third-party listeners in a lifecycle-bound adapter that registers and unregisters the same object. Define whether the source is active while visible or resumed. Record active subscription counts in debug builds and add a leak regression test for the screen. Production telemetry can track OOM and memory trend but avoid logging event payloads.

## Interview answer — short

Callbacks, Handlers, listeners, and static fields cause leaks when they hold implicit or explicit references to short-lived Activities or Fragments from long-lived GC roots. An unexecuted Handler message or unreleased static listener keeps the entire Activity reachable after it is destroyed. Leaks are avoided through symmetrical unregistration, static classes with WeakReferences, or lifecycle-aware coroutines.

## Interview answer — structured

Reference leaks involving callbacks, Handlers, and static variables represent the classic failure mechanism of object retention in Android. In Kotlin and Java, any non-static inner class, anonymous listener, or lambda that touches an outer member implicitly captures a reference to that outer class instance. When an Activity registers an anonymous callback with a long-lived publisher—such as a location manager, an event bus, or a background worker—a direct reference edge is established.

If the publisher outlives the screen and the developer fails to unregister the listener symmetrically in onStop() or onDestroy(), the publisher acts as a GC Root that keeps the destroyed Activity reachable. Similarly, posting a delayed Message to a Handler enqueues an object in the main thread's MessageQueue; the message references the Handler, which captures the Activity, retaining it until the message executes.

Developers must maintain strict lifecycle symmetry, clear pending Handler messages via removeCallbacksAndMessages(null), or replace legacy callbacks with lifecycle-aware coroutines.


## Interview answer — deep senior

Under the hood, analyzing how the Android MessageQueue operates clarifies why Handler leaks occur so frequently. When handler.postDelayed(runnable, delay) is called, the runtime constructs a Message object where msg.target is assigned to the Handler, and msg.callback is assigned to the Runnable. This Message is inserted into the native MessageQueue ordered by execution timestamp. The native Looper associated with the active main thread continues polling this queue. Because the thread is an active GC Root, any pending message in the queue is strongly reachable. If the Runnable was declared as an anonymous class or a lambda capturing a view or Activity method, its implicit this$0 field keeps the entire Activity in the retained heap. If the user rotates the screen or navigates back while a 30-second delay is pending, the destroyed Activity remains leaked for the duration of that timer.

When dealing with static references, the issue is even more severe: a static collection like companion object holding listeners is rooted directly to the java.lang.Class object loaded by the application class loader, creating an immortal leak that persists until process death. To diagnose these retention chains in production, staff engineers use Android Studio Profiler's Paths to GC Roots tree. In modern architectures, legacy Handlers and callbacks should be refactored to kotlinx.coroutines. If a legacy API must be supported, engineers encapsulate the reference inside a WeakReference or utilize static nested classes to sever the implicit outer pointer, combined with defensive unregistration inside lifecycle teardown hooks.

## How to answer in the interview

- **Why:** Describe source-to-callback-to-view retention.
- **How:** Pair registration and removal using the same instance.
- **Trade-off:** Unsubscribing while stopped may miss transient events.
- **Failure case:** A stale Handler message retains a binding until it runs.
- **Production solution:** Requery durable state on resume and verify callback counts.

## Deep-dive talking points

Discuss callback capture, Handler queue retention, static root, exact removal token, Fragment view owner, and durable event state.

## Follow-up questions

- **Interviewer:** "What happens if a static Handler has no delayed messages but is active?"
  **Answer:** "If it has no messages in the queue, it does not retain memory. But if a message is posted, each queued `Message` references the Handler as `msg.target`. If that Handler holds an outer reference, the entire outer scope is retained until queue execution."

- **Interviewer:** "How do modern Android Jetpack components eliminate manual listener cleanup?"
  **Answer:** "Components like `LiveData` and `Flow` combined with `lifecycleScope` or `repeatOnLifecycle` automatically attach and detach observers in synchrony with lifecycle events, eliminating human error in unregistering."

## Self-check rubric

Trace one root path, pair register/unregister, cancel a Handler callback, identify wrong Fragment owner, and prove release.

## References and reviewed-on date

- [Manage your app's memory](https://developer.android.com/topic/performance/memory) — reference and resource ownership.
- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — view lifetime.
- [Handler reference](https://developer.android.com/reference/android/os/Handler) — callback queue and removal APIs.

Technically reviewed against primary documentation on 2026-10-13.
