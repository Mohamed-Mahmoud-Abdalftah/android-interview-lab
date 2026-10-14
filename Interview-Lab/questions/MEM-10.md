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

An ANR (Application Not Responding) occurs when the main thread is blocked and cannot respond to user input within 5 seconds, finish a BroadcastReceiver within 10-60 seconds, or execute a Service within 20 seconds. Common causes include disk I/O, heavy computation, lock contention, and IPC on the UI thread.

## Interview answer — structured

An ANR happens when the application's main looper is frozen and the system Activity Manager detects that the app is unresponsive.

The primary triggers and system timeout thresholds are.

First, with Input Events, failing to process a touch, key, or motion event within **5 seconds**. Next, with BroadcastReceivers, failing to complete `onReceive()` within **10 seconds** for foreground broadcasts or 60 seconds for background.
Finally, with Services, failing to execute lifecycle callbacks within **20 seconds** (foreground) or 200 seconds (background).

The root cause is almost always offloading inappropriate work to the main thread: performing synchronous disk reads/writes (like Room database calls or raw file parsing), parsing large JSON payloads, running cryptographic hashing, or suffering from **lock contention** where the UI thread blocks on a `synchronized` monitor or mutex held by a busy background worker.

In production, we maintain strict ANR budgets by enforcing `StrictMode` in debug builds to catch disk/network violations on the main thread, routing I/O to `Dispatchers.IO`, and diagnosing production ANRs via Android Vitals and system traces (`/data/anr/traces.txt`).


## Interview answer — deep senior

Diagnosing an ANR requires dissecting the system trace report. When an ANR occurs, the Android framework sends `SIGQUIT` to the process, generating a dump in `/data/anr/traces.txt`. When analyzing this dump, we inspect the `"main"` thread state: is it `RUNNABLE` (indicating an infinite loop or heavy CPU computation), `BLOCKED` (waiting on a lock held by another thread), or `TIMED_WAIT` / `WAITING` (waiting for a condition variable or synchronous IPC)?

A frequent hidden cause of ANRs in enterprise apps is **Binder transaction saturation**. Calling synchronous system services or IPC methods (like `PackageManager`, `TelephonyManager`, or `AccountManager`) on the main thread can stall if the remote system server is under heavy load, blocking the main thread indefinitely.

To capture ANRs before users experience them in production, we integrate ANR-WatchDog or Bugsnag/Sentry ANR detectors, which post a heartbeat runnable to the main handler every 2 seconds; if the runnable doesn't execute within 5 seconds, they capture thread stacks and upload a detailed snapshot.


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
