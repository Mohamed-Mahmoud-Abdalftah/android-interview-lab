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

Non-static Handlers retain outer Activity references; delayed messages in the MessageQueue keep the Activity pinned in memory until processed. Similarly, static fields act as permanent GC roots, and unregistered listeners or observers in long-lived singletons or system services keep transient UI components alive indefinitely.

## Interview answer — structured

Memory leaks from callbacks, Handlers, observers, and static references stem from breaking object lifecycle symmetry.

First, a Handlers & MessageQueue is a non-static Handler holds an implicit reference to its enclosing Activity. When a message is scheduled with `postDelayed()`, the `Message` in the main thread's `MessageQueue` holds a reference to the Handler target, which holds the Activity. Until the message executes or is cleared with `removeCallbacksAndMessages(null)`, the entire Activity graph is retained as a GC Root. Next, with Static References, any `companion object` property or static variable persists across the entire application process. Assigning an Activity or View to a static field directly prevents GC reclamation.
Finally, with Unregistered Observers, when an Activity registers as a listener with a long-lived publisher—such as `LocationManager`, `SensorManager`, or a singleton EventBus—the publisher stores a strong reference. Failing to unregister symmetry (`unregisterListener()` in `onStop()` or `onDestroy()`) creates a permanent leak.

In modern Android development, we prevent these by replacing raw Handlers with lifecycle-aware coroutines (`lifecycleScope`), binding observers with `LifecycleOwner`, and utilizing `AutoCloseable` or structured cleanup patterns.


## Interview answer — deep senior

Under the hood, Java and Kotlin inner classes differ in reference semantics: a standard inner class holds an implicit `$this$0` synthetic pointer to the outer instance. In Kotlin, declaring an anonymous lambda or `object : Runnable` inside an Activity implicitly captures the outer instance unless it references no instance properties or is explicitly declared in a `companion object` or static file-level context.

When dealing with Handlers specifically, the classic Java remedy was declaring a static class paired with a `WeakReference<Activity>`. However, in modern Kotlin, Handlers are largely legacy; suspending coroutines with `delay()` within `lifecycleScope` are automatically cancelled via cooperative cancellation when the `LifecycleOwner` reaches `DESTROYED`, dropping the continuation and preventing the leak entirely.

In enterprise monitoring, LeakCanary excels at pinpointing these leaks by identifying the `target` field in queued `android.os.Message` instances or scanning registered observer arrays in system managers.


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
