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

## Concept and technical explanation

An Application Not Responding (ANR) error occurring from a coroutine launched on the Main thread illustrates the fundamental divergence between cooperative suspension and thread blocking. When viewModelScope.launch executes without an explicit dispatcher argument, it defaults to Dispatchers.Main.immediate, running directly on the Android UI Main Thread (the Looper message queue). A fatal misconception is assuming that coroutines prevent ANRs automatically. Suspending operations (such as delay, withContext, or asynchronous Room calls) cooperatively yield the main thread back to the Android Choreographer to render frames. However, if that coroutine executes synchronous, blocking code—such as Thread.sleep(), synchronous disk file reading (FileInputStream.read), or legacy synchronous networking (OkHttpClient.newCall().execute())—the physical Main Thread is held captive. The Choreographer cannot draw 120Hz/60Hz display frames, and user touch events accumulate unprocessed in the InputDispatcher queue. If touch input remains unacknowledged for 5 seconds, the OS ActivityManagerService declares an ANR and presents a crash dialog. The definitive fix is enforcing Main-Safety by offloading blocking calls via withContext(Dispatchers.IO).

## Practical walkthrough (English)

Consider an Android application reading an encrypted configuration file directly on the Main thread:
```kotlin
// Erroneous implementation: blocks the Main thread Looper, triggering an ANR
class SettingsViewModel(private val repository: SettingsRepository) : ViewModel() {
    fun loadConfig() {
        viewModelScope.launch {
            // BUG: Runs on Dispatchers.Main by default!
            // readConfigBlocking blocks the Main Thread for 6 seconds -> TRIGGERS ANR!
            val config = repository.readConfigBlocking() 
            updateUi(config)
        }
    }
}

// Production-grade solution: enforcing Main-Safety in the repository
class SettingsRepository(private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO) {
    // Suspend function is Main-Safe; caller never needs to worry about dispatchers:
    suspend fun readConfig(): Config = withContext(ioDispatcher) {
        // Blocks a background worker thread in Dispatchers.IO, NOT the Main UI thread!
        readConfigBlocking() 
    }
}

// ViewModel consumes cleanly on Main without ANR:
class SafeSettingsViewModel(private val repository: SettingsRepository) : ViewModel() {
    fun loadConfig() {
        viewModelScope.launch {
            val config = repository.readConfig() // Suspends main thread without blocking!
            updateUi(config) // Runs immediately on Main upon resumption
        }
    }
}
```

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

viewModelScope.launch runs on Dispatchers.Main by default. Calling blocking code (Thread.sleep, synchronous I/O, or blocking networking) blocks the Android Main UI Thread Looper. If touch events are blocked for 5 seconds, the OS triggers an ANR. Suspending yields the thread, but blocking halts it. The fix is enforcing Main-Safety: offloading blocking calls inside withContext(Dispatchers.IO).

## Interview answer — structured

Experiencing an Application Not Responding (ANR) crash from a coroutine on the Main thread stems from confusing coroutine suspension with thread blocking. By default, viewModelScope.launch executes on Dispatchers.Main, which maps directly to the Android Main Thread and its Looper message queue.

While suspending functions like delay release the main thread to render frames and handle touch events, calling blocking code—such as Thread.sleep, synchronous file I/O, or blocking network clients—physically locks the thread. When the main thread is blocked, the Android Choreographer cannot process vsync pulses, and touch inputs queue up in the InputDispatcher. If the main thread fails to process an input event within 5 seconds, the ActivityManagerService displays an ANR dialog.

In production, the architectural resolution is enforcing the Main-Safety principle. The repository or data source must take responsibility for wrapping blocking legacy calls inside withContext(Dispatchers.IO).

This shifts the blocking operation to a background worker thread while suspending the main thread coroutine non-blockingly, allowing UI rendering and touch handling to proceed flawlessly.


## Interview answer — deep senior

Under the hood, the Android UI framework is driven by a single-threaded event loop managed by Looper, Handler, and MessageQueue inside ActivityThread. The Android Choreographer schedules frame callbacks on every VSYNC signal (every 8.3ms on 120Hz screens or 16.6ms on 60Hz displays). When a coroutine suspends on Dispatchers.Main, it posts a Continuation runnable to the Handler and returns control immediately to Looper.loop(), keeping frame rendering completely smooth. However, when a coroutine invokes a synchronous blocking call like Thread.sleep(6000) or a blocking socket read, execution never returns to Looper.loop(). The thread program counter is trapped inside the blocking stack frame. Meanwhile, the Linux kernel InputReader receives touch events from the hardware digitizer and forwards them to the system server's InputDispatcher. The InputDispatcher writes events into the app's InputChannel socket pair. Because the app's Main Thread is blocked and cannot drain its MessageQueue, the socket buffer fills up. When the InputDispatcher detects that a key or touch event has been waiting for more than 5 seconds without acknowledgment, it triggers the ANR mechanism: the system server dumps the app's stack traces to /data/anr/traces.txt and displays the ANR dialog to the user. In staff-level architecture, we eliminate ANRs through three layers of defense. First, we enforce the Main-Safety rule: every suspend function exposed by Domain or Data layers must be safe to invoke directly from Dispatchers.Main without the caller managing dispatchers. The repository wraps blocking calls in withContext(ioDispatcher), where ioDispatcher is injected via Hilt. Second, in debug builds, we enable Android StrictMode with penaltyDeath() for disk reads, disk writes, and network operations executed on the Main thread. Third, in CI pipelines, we monitor automated UI tests using Android Vitals and LeakCanary to detect slow main thread frames before code reaches production.

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
