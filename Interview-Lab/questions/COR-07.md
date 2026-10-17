---
id: "COR-07"
question: "What do Dispatchers.Main, IO, Default, and Unconfined do?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "A"
phase: 1
priority: "P1"
order: 88
editorial_status: "reviewed"
---

# COR-07

## Original interview question

What do Dispatchers.Main, IO, Default, and Unconfined do?

## What the interviewer evaluates

Whether the candidate maps dispatchers to execution resources while rejecting `suspend` as automatic backgrounding.

## Concept and technical explanation

A dispatcher is a context element that determines where a coroutine executes its code and resumes after suspension. On Android, `Dispatchers.Main` targets the UI thread. `Dispatchers.Default` is intended for CPU-heavy work. `Dispatchers.IO` is intended for blocking I/O and uses shared elastic worker resources; its default parallelism setting is not a global maximum thread count because IO views created with `limitedParallelism` can add capacity. `Dispatchers.Unconfined` does not confine execution to one thread and may resume wherever the suspending operation resumes it. A dispatcher is not a substitute for cancellation, backpressure, or understanding whether an API is already non-blocking.

## Practical walkthrough (English)

Consider an analytical report generation feature that aggregates thousands of transactions, calculates tax metrics, writes a PDF document to disk, and updates the screen progress.

Proper separation of concerns across dispatchers:
```kotlin
fun exportFinancialReport() {
    // 1. Dispatchers.Main: Update UI loading state on the main thread
    viewModelScope.launch(Dispatchers.Main) {
        _uiState.value = ExportUiState.Loading

        // 2. Dispatchers.Default: Heavy CPU calculations and summaries
        val summary = withContext(Dispatchers.Default) {
            calculateFinancialMetrics(rawTransactions)
        }

        // 3. Dispatchers.IO: Blocking disk write operation
        val pdfFile = withContext(Dispatchers.IO) {
            writePdfToDisk(summary)
        }

        // 4. Return to Dispatchers.Main automatically to display the success dialog
        _uiState.value = ExportUiState.Success(pdfFile)
    }
}
```
By segmenting the pipeline, heavy mathematical computations do not block UI frame rendering, and blocking disk operations do not saturate the CPU-bound thread pool.

## Explanation in Arabic

الـ Dispatcher بتحدد فين كود الـ Coroutine يتنفذ ويرجع يكمل بعد التعليق. على Android، `Dispatchers.Main` للـ UI thread؛ ما أحطش عليها شغل حظري أو حسابات طويلة. `Dispatchers.Default` مناسبة لشغل CPU التقيل زي معالجة بيانات كبيرة. `Dispatchers.IO` مناسبة لعمليات I/O الحظرية، وبتستخدم موارد Workers مشتركة ومرنة. إعداد parallelism الافتراضي للـ IO مش حد أقصى لكل Threads التطبيق؛ Views من `limitedParallelism` ممكن تضيف سعة، فلازم أحدد عدد الطلبات والاتصالات بشكل مستقل.

`Dispatchers.Unconfined` مش بتربط التنفيذ بـ Thread واحد، وممكن تكمل على Thread اللي استأنفها. عادة ما أستخدمهاش في كود UI عادي لأن الكود محتاج سياق تنفيذ واضح. ووجود `suspend` أو Dispatcher معينة ما يغنيش عن فهم عقد المكتبة أو التعامل مع الإلغاء.

## Practical walkthrough

في شاشة معالجة وتصدير تقرير مالي (PDF Export & Sync):
- **توزيع العمل على الـ Dispatchers باحترافية:**
  viewModelScope.launch(Dispatchers.Main) { // 1. نبدأ على Main لعرض شريط التحميل
      _uiState.value = UiState.Exporting
      
      // 2. عمليات حسابية ثقيلة لمعالجة الأرقام ننقلها لـ Default (CPU):
      val processedData = withContext(Dispatchers.Default) {
          calculateFinancialSummaries(rawTransactions)
      }
      
      // 3. كتابة ملف الـ PDF على القرص نرسلها لـ IO (Disk Blocking):
      val pdfFile = withContext(Dispatchers.IO) {
          writePdfToStorage(processedData)
      }
      
      // 4. نعود تلقائياً لـ Main لإخفاء شريط التحميل وعرض إشعار النجاح:
      _uiState.value = UiState.Success(pdfFile)
  }

## Why it matters and how it works

Dispatcher is a context element that decides where continuation executes. Main targets the Android UI dispatcher, Default uses a shared CPU-oriented pool, and IO is elastic for blocking calls. `Unconfined` does not confine execution to one thread. Suspending operations may free a thread; synchronous calls still occupy their selected thread.

## Worked example

Android repository illustration; `blockingDecoder` is a synchronous CPU operation and `readFile` is synchronous disk I/O.

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

suspend fun readAndDecode(
    readFile: () -> ByteArray,
    blockingDecoder: (ByteArray) -> String,
): String {
    val bytes = withContext(Dispatchers.IO) { readFile() }
    return withContext(Dispatchers.Default) { blockingDecoder(bytes) }
}
```

## Trade-offs and decision criteria

Keep UI mutations on Main; put true blocking disk/network calls behind an IO boundary; use Default for CPU work. Some suspending clients are already main-safe, so an extra IO hop is unnecessary. Avoid hard-coded dispatchers in hard-to-test code; inject when tests need control.

## Failure modes

Using Default for hundreds of long blocking calls can starve CPU tasks; using Main for synchronous decoding causes jank or ANR. Assuming `Unconfined` always resumes on Main can produce a thread-confinement bug. `withContext(IO)` does not make a blocking driver promptly cancellable.

## Production perspective

A photo repository reads bytes from a legacy file API on IO, decodes thumbnail data on Default and exposes a main-safe suspend function. The ViewModel launches from Main and observes a result. Benchmark decode cost, bound parallel operations, and test UI responsiveness.

## Interview answer — short

On Android, `Main` is for UI work, `Default` for CPU-heavy work, and `IO` for blocking I/O. `Unconfined` does not promise a particular thread, so I rarely use it in app code. I choose the dispatcher at the operation that knows whether it blocks, and I still limit how much work I start.

## Interview answer — structured

I use a dispatcher to place execution, not to make an operation magically asynchronous. `Main` is Android's UI thread, so it is where I publish UI state and handle view work. `Default` is the choice for sustained CPU work, such as sorting a large in-memory data set. `IO` is intended for a synchronous file read or a blocking SDK call. `Unconfined` does not keep work on one thread, so it is rarely appropriate for ordinary Android UI logic.

For example, if a ViewModel exports a report, I can start on Main, calculate a large summary on `Default`, write the file through a blocking API on `IO`, then return to Main with the result. If the file library already offers a main-safe suspending API, I would check its contract before adding an IO switch.

The trade-off is resource use. `Dispatchers.IO` has a default parallelism setting, but it is not a universal cap on all worker threads or network requests. Launching hundreds of blocking calls can still exhaust connections or overload a service. I would bound requests at the operation level and test cancellation and responsiveness under realistic load.

## Interview answer — deep senior

The dispatcher is part of `CoroutineContext`; child coroutines inherit it unless they override it. A coroutine still runs on a real thread while executing, and suspension can release that thread. `withContext` changes context for one block and resumes the caller in its prior context afterward. That makes a repository a useful place to hide a known blocking dependency behind a main-safe suspend API.

`Default` and `IO` share worker infrastructure on the JVM, but they are tuned for different types of work. CPU work should not be spread over an unbounded number of workers; blocking I/O can need more waiting threads. The default `IO` parallelism is configurable and is commonly 64 or the core count, whichever is larger. It is a limit for the default IO view's active blocking tasks, not a total cap for every `Dispatchers.IO.limitedParallelism` view. I would not make an interview answer depend on one library-internal scheduler class, because that implementation can change.

`Unconfined` starts in the caller's call frame and may resume on the thread chosen by a suspending function. That makes thread-sensitive UI code unsafe there. `Main.immediate` may avoid an extra dispatch when already on Main, but it does not grant extra frame time. If a coroutine calls a synchronous method on Main, it can cause jank or an ANR; `suspend` syntax and a dispatcher choice do not turn the method non-blocking.

Finally, dispatcher placement and concurrency limits are separate choices. `limitedParallelism` limits simultaneously executing segments on a dispatcher view, not the total number of coroutines in flight across suspensions. If I need to cap concurrent requests, I use a semaphore or a bounded queue and verify it with a load test.

## How to answer in the interview

- **Why:** the dispatcher must fit the work, not the function name.
- **How:** Main renders, IO accommodates blocking I/O, Default runs CPU work, Unconfined has no stable thread guarantee.
- **Trade-off:** switches cost complexity and IO is not backpressure.
- **Failure case:** CPU decoding on Main or blocking on Default at scale.
- **Production solution:** place switches at repository boundaries and limit fan-out separately.

## Deep-dive talking points

Trace a coroutine across dispatcher switches and suspension; distinguish thread capacity, concurrency limits and cancellation of a blocking driver.

## Follow-up questions

- **Interviewer:** "Would you put every suspend network call on `Dispatchers.IO`?"
  **Answer:** "No. I would check whether the client already exposes a main-safe suspending call. I use IO for a dependency that actually blocks its caller thread."

- **Interviewer:** "Does `Dispatchers.IO.limitedParallelism(4)` cap requests at four?"
  **Answer:** "It limits simultaneously executing code segments in that dispatcher view, not every coroutine that is suspended on a request. For a request-level cap I would use a semaphore or bounded queue."

- **Interviewer:** "What would go wrong with `Unconfined` in a ViewModel?"
  **Answer:** "It gives no stable thread confinement after suspension. I might resume on a callback thread and touch UI state from the wrong context. I would use an explicit dispatcher or inherit the ViewModel's Main context."

## Self-check rubric

Can I map each dispatcher, reject `Unconfined` for UI confinement, identify a blocking boundary, and explain that cancellation remains cooperative?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — dispatcher and context.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — main safety and repository boundaries.

- [Kotlin IO dispatcher](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/-i-o.html) — default parallelism and elastic views.
- [Limited parallelism](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-main-coroutine-dispatcher/limited-parallelism.html) — execution segments versus concurrent requests.
Technically reviewed against primary documentation on 2026-10-17.
