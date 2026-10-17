---
id: "MEM-10"
question: "What is an ANR, and what are common causes?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 65
editorial_status: "reviewed"
---

# MEM-10

## Original interview question

What is an ANR, and what are common causes?

## What the interviewer evaluates

- Define ANR as a responsiveness failure with component-specific timeouts, not simply a crash.
- Identify Main-thread blockage, lock/Binder waits, broadcast/service work, and system contention.
- Diagnose with ANR traces and timing evidence before choosing a fix.

## Concept and technical explanation

An Application Not Responding (ANR) error is an Android system-level watchdog failure triggered when an application's main thread is blocked for too long and cannot process incoming user input or system callbacks. The operating system monitors main thread responsiveness via ActivityManagerService and AnrHelper. If the app fails to dispatch an input event (touch, key press) within 5 seconds, finish executing a foreground BroadcastReceiver within 10 to 20 seconds (60 seconds in background), or complete a foreground Service lifecycle callback within 20 seconds (200 seconds in background), the OS halts the process, logs an ANR trace, and displays the system ANR dialog. Common causes include running synchronous disk I/O or database queries on the main thread, performing network requests, executing CPU-intensive algorithms, deadlocks and lock contention waiting on background threads, and IPC Binder call starvation.

## Practical walkthrough (English)

Identifying main-thread blockage and moving work to background dispatchers:
```kotlin
// ANR Trigger: Synchronous disk I/O and heavy parsing on the Main Thread:
class BadSettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Blocking main thread with disk read and JSON parsing in onCreate:
        val rawConfig = File(filesDir, "config.json").readText() // Disk I/O on Main Thread!
        val parsed = JSONObject(rawConfig) // CPU-heavy parsing blocking Looper!
        applyConfig(parsed)
    }
}

// Clean Architecture: Asynchronous execution on Dispatchers.IO:
class GoodSettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            val parsed = withContext(Dispatchers.IO) {
                val rawConfig = File(filesDir, "config.json").readText()
                JSONObject(rawConfig)
            }
            applyConfig(parsed)
        }
    }
}
```
Offloading file operations and JSON parsing to Dispatchers.IO keeps the Main Thread Looper free to process frame rendering and touch events without triggering watchdog timeouts.

## Explanation in Arabic

تعريف ظاهرة ANR (Application Not Responding) وأسبابها الجذرية وكيفية معالجتها:

1. ما هو الـ ANR؟
   - الـ ANR هو تنبيه يعرضه نظام تشغيل Android للمستخدم (مع خيار إغلاق التطبيق بالقوة Force Close أو الانتظار Wait) عندما يفشل التطبيق في الاستجابة لمدخلات المستخدم خلال مهلة زمنية محددة.
   - المهل الزمنية الشائعة:
     * **Input dispatching timeout**: عدم الاستجابة للمس الشاشة أو ضغط الأزرار خلال **5 ثوانٍ**.
     * **BroadcastReceiver**: عدم إنهاء دالة `onReceive()` خلال **10 إلى 60 ثانية** (حسب Foreground/Background).
     * **Service execution**: استغراق الـ Service أكثر من **20 ثانية** (Foreground) أو **200 ثانية** (Background) في معالجة أمر.

2. الأسباب الشائعة للـ ANR:
   - **I/O blocking on Main Thread**: قراءة أو كتابة ملفات، استدعاء قاعدة بيانات Room، أو قراءة SharedPreferences المتزامنة على الـ Main Thread.
   - **Network calls on Main Thread**: محاولة الاتصال بالإنترنت مباشرة (يسبب `NetworkOnMainThreadException` غالباً، ولكن أحياناً عبر مكتبات C++).
   - **Lock Contention (Deadlock/LiveLock)**: الـ Main Thread ينتظر قفل (Mutex/synchronized) ممسوكاً بواسطة Background Thread يقوم بعملية طويلة.
   - **Heavy CPU Calculations**: تشفير، ضغط صور، أو معالجة JSON ضخمة على الـ Main Thread.

3. كيف نحقق في الـ ANR؟
   - فحص ملف **traces.txt** المأخوذ من مسار `/data/anr/traces.txt` عبر adb أو فحص تقارير Android Vitals و Firebase Crashlytics.
   - الملف يسجل Stack Trace لكل الـ Threads في اللحظة التي حدث فيها الـ ANR بدقة.

## Practical walkthrough

سيناريو عملي لتجنب حظر الـ Main Thread ومنع الـ ANR:
```kotlin
// ❌ كود كارثي: تنفيذ عمليات ديسك وتشفير على الـ Main Thread يسبب ANR فوراً:
class BadSettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // قراءة متزامنة لملف كبير أو SharedPreferences على الـ Main Thread:
        val heavyConfig = File(filesDir, "config.json").readText() // IO Blocking!
        applyConfig(heavyConfig)
    }
}

// ✅ كود احترافي: نقل العمليات الثقيلة إلى Dispatchers.IO عبر Coroutines:
class SafeSettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            val heavyConfig = withContext(Dispatchers.IO) {
                File(filesDir, "config.json").readText() // يتم في Background Thread بأمان
            }
            applyConfig(heavyConfig) // العودة للـ Main Thread لتحديث الـ UI
        }
    }
}
```

## Why it matters and how it works

Android dispatches UI input and lifecycle/component callbacks through constrained threads and deadlines. When an event cannot be handled in time, it records an ANR and may show a dialog. Input-dispatch timeouts often point to Main being blocked, but thread dumps captured late can show an idle frame rather than the earlier cause. Slow Binder replies, lock contention, expensive startup, synchronous I/O, and long calculations can all delay responsiveness. Perfetto scheduling and ANR clusters help separate runnable-but-starved Main from a thread waiting on another dependency.

## Worked example

Suppose an order screen sometimes freezes after tapping “Pay”. The ANR cluster shows Main waiting for a synchronized token refresh while a worker thread holds the lock during a network request. Moving only the button handler to a coroutine still leaves Main waiting if UI state reads the same lock. Shorten the critical section, avoid network under the lock, make the repository API main-safe, and measure traces before and after. A timeout in payment submission remains an unknown business outcome even after the UI becomes responsive.

## Trade-offs and decision criteria

Moving blocking work off Main is necessary, but unbounded offloading can exhaust worker threads or overload a service. Reducing lock scope may be better than adding threads. Asynchronous APIs can improve resource use but require cancellation and error handling. StrictMode in development catches some accidental Main-thread operations; production ANR/vitals data reveals real-device timing and OEM effects. Set a measurable responsiveness budget rather than relying only on a single reproduction.

## Failure modes

Calling `Thread.sleep` inside `viewModelScope.launch` still blocks Main. A receiver doing network work inside `onReceive` can exceed its deadline. A delayed trace with `nativePollOnce` may not identify the original blocker; correlate with earlier slices and other threads. Catching every exception and retrying repeatedly in a callback can prolong a freeze. Fix the root cause and verify rate changes across a rollout, not just one local trace.

## Production perspective

Cluster ANRs by trigger, Android version, device, and stack; gather representative traces and app custom trace spans. Identify whether Main is running, waiting on a lock/Binder, or not scheduled. Reproduce with slow network and load, write a targeted regression test where possible, and monitor Play vitals ANR rate after rollout. Keep the fix separate from payment transaction safety so reducing a UI stall does not introduce duplicate charges.

## Interview answer — short

An ANR occurs when the main thread looper is blocked and cannot respond to user input within 5 seconds, a broadcast receiver within 10 to 20 seconds, or a service within 20 seconds. Common causes include synchronous disk or database I/O on the main thread, lock contention with background threads, network calls, and long garbage collection pauses. Profiling traces.txt helps identify root causes.

## Interview answer — structured

An Application Not Responding condition is not a runtime crash or an out-of-memory error, but an operating system responsiveness failure. The Android OS monitors main thread execution through watchdog timers managed by ActivityManagerService. When an app fails to respond to touch or key input within five seconds, finish a foreground BroadcastReceiver within ten to twenty seconds, or execute a foreground Service callback within twenty seconds, the system displays the ANR dialog and allows the user to kill the process.

An ANR occurs whenever the Main Thread Looper message queue is prevented from processing pending messages. The most frequent triggers are synchronous disk reads or writes, database operations, network calls, and complex JSON deserialization executed directly on the UI thread.

In production, subtle ANRs are caused by thread lock contention, where the main thread attempts to acquire a synchronized mutex held by a low-priority background thread.

Senior engineers enforce strict threading boundaries, offloading all non-UI computation to background coroutine dispatchers and instrumenting debug builds with StrictMode.


## Interview answer — deep senior

At a staff engineering level, triaging production ANRs centers on analyzing thread execution states and kernel wait-channels inside the system ANR trace file (data anr traces.txt) or Google Play Console Android Vitals. When an ANR occurs, the Android kernel dumps stack traces for all active threads in the process. When inspecting the main thread in the trace, we examine its execution state: RUNNABLE, BLOCKED, or WAITING. If the main thread is in the BLOCKED state, the trace reveals the specific monitor lock it is waiting to acquire, along with the thread ID holding that lock. This signature immediately points to multi-threading lock contention or priority inversion, where a background thread was preempted while holding a critical shared resource.

If the main thread is marked as WAITING or NATIVE in a Binder call (such as BinderProxy.transact), the application is stalled waiting on a synchronous IPC response from a system service or another application process. Furthermore, we evaluate total CPU utilization reported in the ANR header: if CPU usage is near 100% with high kswapd0 or ART GC daemon activity, the ANR is an indirect casualty of extreme memory pressure or allocation churn, where continuous stop-the-world GC cycles starved the main thread of CPU execution slices. To prevent ANRs proactively, we configure StrictMode in debug environments and monitor our Google Play Console ANR rate to remain comfortably below the bad behavior threshold of 0.47%.

## How to answer in the interview

- **Why:** Define responsiveness deadline and trace evidence.
- **How:** Follow Main's wait chain to the lock or service holder.
- **Trade-off:** Moving work off Main may add concurrency pressure.
- **Failure case:** A worker-held lock can still freeze Main.
- **Production solution:** Shorten lock scope and verify ANR cohort after rollout.

## Deep-dive talking points

Explain input and component deadlines, Main-thread state, late stack traces, Binder and lock chains, StrictMode, Perfetto scheduling, and production cluster verification.

## Follow-up questions

- **Interviewer:** "What is lock contention, and how does it cause an ANR?"
  **Answer:** "Lock contention happens when the main thread tries to enter a synchronized block or acquire a mutex that is currently locked by a background thread doing heavy I/O or computation. The main thread is forced into a BLOCKED state until the background worker releases the lock."

- **Interviewer:** "How does `goAsync()` in a BroadcastReceiver help avoid ANRs?"
  **Answer:** "`goAsync()` flags to the system that the receiver will finish its work asynchronously on a background dispatcher, returning immediately from `onReceive()` while retaining a `PendingResult` to call `finish()` later, avoiding the main thread timeout."

## Self-check rubric

Define ANR precisely; name four causes; follow a lock or Binder wait from Main; explain why a late trace can mislead; and propose a rate-based validation after fixing it.

## References and reviewed-on date

- [Diagnose and fix ANRs](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs) — types, traces, and contention diagnosis.
- [Android coroutines best practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — main-safe blocking boundaries.

Technically reviewed against primary documentation on 2026-10-13.
