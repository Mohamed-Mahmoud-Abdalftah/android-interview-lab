---
id: "COR-31"
question: "A coroutine starts on Main, calls blocking library code, and causes ANR. Explain the exact failure and fix."
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 112
editorial_status: "reviewed"
---

# COR-31

## Original interview question

A coroutine starts on Main, calls blocking library code, and causes ANR. Explain the exact failure and fix.

## What the interviewer evaluates

Diagnose why a coroutine on Main can still produce jank/ANR and provide a verifiable fix.

## Explanation in Arabic

بدء Coroutine على `Dispatchers.Main` واستدعاء مكتبة تعمل بنظام Blocking وحدوث ANR هو السيناريو الكلاسيكي لأخطاء الـ Main Thread في Android:

1. تحليل العطل الدقيق (The Exact Failure Mechanism):
   - `Dispatchers.Main` مربوط بالـ `Looper.getMainLooper()` والـ `Handler` الخاص بالـ UI Thread.
   - عندما تبدأ Coroutine على Main وتستدعي دالة Blocking من مكتبة خارجية (مثل `legacyCrypto.hash()` أو `file.readBytes()` أو `Thread.sleep()`):
   - الـ Coroutine **لا تُعلّق (Does NOT suspend)**؛ بل تحظر خيط الـ Main Thread بالكامل (Blocks OS Main Thread)!
   - الـ Main Thread يتوقف عن معالجة رسائل الـ `Choreographer` المسؤولة عن رسم الشاشة (Rendering frames)، ويتوقف عن معالجة أحداث اللمس (Input events).
   - بعد 5 ثوانٍ من عدم الاستجابة، يتدخل نظام أندرويد ويعرض للمستخدم نافذة: **'Application Not Responding (ANR)'** ويطلب إغلاق التطبيق بالقوة.

2. الإصلاح الدقيق (The Fix):
   - نقل الاستدعاء الـ Blocking فوراً من الـ Main Thread إلى `Dispatchers.IO` (لو كان I/O) أو `Dispatchers.Default` (لو كان CPU math) عبر دالة **`withContext`**.
   - بذلك تصبح الدالة **Main-Safe**، ويظل الـ Main Thread حراً لرسم الشاشة بسلاسة تامة.

## Practical walkthrough

الكود الفاشل وإصلاحه المعماري:
```kotlin
// ❌ الكود المسبب للـ ANR:
fun onProcessClicked() {
    viewModelScope.launch(Dispatchers.Main) {
        _uiState.value = UiState.Loading
        // كارثة: مكتبة تحظر الـ Thread لمدة 6 ثوانٍ على الـ Main Thread:
        val key = LegacyCryptoLib.generateRsaKeySync(4096) // ANR CRASH!
        _uiState.value = UiState.Success(key)
    }
}

// ✅ الإصلاح السليم بتحقيق Main-Safety:
fun onProcessClicked() {
    viewModelScope.launch(Dispatchers.Main) {
        _uiState.value = UiState.Loading
        // ننقل الحسابات الثقيلة لـ Dispatchers.Default باستخدام withContext:
        val key = withContext(Dispatchers.Default) {
            LegacyCryptoLib.generateRsaKeySync(4096) // يعمل في الخلفية بدون أي تأثير على UI
        }
        // نعود لـ Main Thread تلقائياً لتحديث الـ UI:
        _uiState.value = UiState.Success(key)
    }
}
```

## Why it matters and how it works

A coroutine only releases Main at genuine suspension. `Thread.sleep`, synchronous disk/network or a blocking Binder/SDK call inside Main continues to occupy it. `withContext(IO)` protects Main for known blocking I/O, while heavy CPU belongs on Default. The chosen library may not respond promptly to cancellation; set native timeouts and bound concurrent calls.

## Worked example

Android/JVM repository example assumes `LegacyClient.fetchBlocking` is synchronous. ViewModel calls the main-safe suspending repository method.

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

interface LegacyClient { fun fetchBlocking(id: String): String }
class LegacyRepository(private val client: LegacyClient) {
    suspend fun fetch(id: String): String =
        withContext(Dispatchers.IO) { client.fetchBlocking(id) }
}
```

## Trade-offs and decision criteria

Prefer a true async client if maintained and cancellable; IO dispatch is a pragmatic wrapper for legacy blocking I/O. More IO threads do not fix a saturated server or unbounded work. Avoid using `runBlocking` from UI callbacks, which intentionally blocks Main.

## Failure modes

Calling `client.fetchBlocking()` directly inside `viewModelScope.launch` can freeze frames and trigger ANR. A superficial fix of declaring it `suspend` changes no execution behavior. If the SDK ignores cancellation, late results must be discarded and requests bounded.

## Production perspective

An ANR report shows Main parked in a third-party synchronous SDK. The team reproduces it with a slow fake and UI frame monitoring, moves the boundary to an injected IO dispatcher, configures SDK timeout and checks release traces. It also limits concurrent calls and replaces the SDK when feasible.

## Interview answer — short

The failure occurs because calling synchronous blocking code on Dispatchers.Main halts the Android UI Looper message queue, preventing Choreographer frame rendering and touch dispatch, triggering an ANR after 5 seconds. Fix it by offloading the blocking call to withContext(Dispatchers.Default) or withContext(Dispatchers.IO) to restore Main-Safety.

## Interview answer — structured

The exact failure mechanism is thread starvation on the Android UI Looper.

`Dispatchers.Main` executes directly on Android's Main Looper thread. Marking a function as a coroutine does not change how synchronous code runs. When the coroutine executes a synchronous blocking call from a third-party library (like heavy cryptography or disk reading), it monopolizes the operating system main thread.

Because the main thread is blocked, Android's `Choreographer` cannot process VSYNC pulses to draw 60/120Hz frames, and the `InputDispatcher` cannot dispatch user touch events. If an input event goes unhandled for 5 seconds, the OS flags an Application Not Responding (ANR) error and prompts the user to force-close the app.

The definitive fix is enforcing **Main-Safety**: wrap the blocking library invocation inside `withContext(Dispatchers.Default)` for CPU-bound computations or `withContext(Dispatchers.IO)` for blocking I/O. The coroutine suspends, yields the main thread to the Android message queue so the UI remains fluid, executes the blocking code on a background worker thread, and seamlessly resumes on Main with the result.


## Interview answer — deep senior

From a performance monitoring and diagnostic perspective, identifying these bottlenecks in production requires strict tooling. In debug builds, we enable **StrictMode**:

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectDiskReads()
        .detectDiskWrites()
        .detectCustomSlowCalls()
        .penaltyLog()
        .penaltyDeathOnNetwork()
        .build()
)
```

StrictMode immediately logs a red flash or crashes the app in debug builds if disk or network I/O touches the main thread.

In production APM monitoring, we track **ANR Watchdog traces** and Google Play Console vitals. When inspecting an ANR trace file (`traces.txt`), a blocked coroutine on Main will show the main thread in the `BLOCKED` or `RUNNABLE` state stuck in the third-party library method frame rather than in `MessageQueue.nativePollOnce()`. Offloading that exact stack frame via `withContext` completely resolves the ANR.


## How to answer in the interview

- **Why:** the UI Looper cannot render or handle input while a synchronous call occupies Main.
- **How:** trace dispatcher inheritance and the blocking stack frame.
- **Trade-off:** IO offload restores responsiveness but costs a worker; an async client is preferable when available.
- **Failure case:** merely adding suspend or unbounded IO fan-out.
- **Production solution:** main-safe repository boundary, limits, and trace-based verification.

## Deep-dive talking points

Trace Looper starvation, identify blocking stack evidence and verify the fix under slow-library conditions.

## Follow-up questions

- **Interviewer:** "Why doesn't `suspend` automatically prevent this ANR?"
  **Answer:** "Because `suspend` is only a compiler marker for non-blocking suspension points. If the code inside the suspend function invokes a blocking Java or native call without switching dispatchers via withContext, it executes synchronously on the caller's thread."

- **Interviewer:** "How do you detect slow frame drops (Jank) before they become full ANRs?"
  **Answer:** "Using Android's `JankStats` library or Firebase Performance Monitoring to monitor dropped frames (jank occurs when a frame takes longer than 16.6ms at 60Hz or 8.3ms at 120Hz to render)."

- **Interviewer:** "Should repository methods be responsible for `withContext` or should the ViewModel handle it?"
  **Answer:** "The repository must be responsible. Following the Main-Safety design guideline, all public suspend functions exposed by repositories must internally guarantee that they can be safely called from Dispatchers.Main."

## Self-check rubric

Can I explain the exact UI-thread blockage, collect trace evidence, choose IO versus Default, and test a slow driver?

## References and reviewed-on date

- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — main safety.
- [Android ANR guidance](https://developer.android.com/topic/performance/vitals/anr) — diagnosis and traces.

Technically reviewed against primary documentation on 2026-10-13.
