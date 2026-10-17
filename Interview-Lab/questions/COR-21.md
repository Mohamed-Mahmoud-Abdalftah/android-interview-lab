---
id: "COR-21"
question: "What is a semaphore? How do you limit parallelism?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 102
editorial_status: "reviewed"
---

# COR-21

## Original interview question

What is a semaphore? How do you limit parallelism?

## What the interviewer evaluates

Explain permit accounting and how to limit active operations separately from dispatcher choice.

## Concept and technical explanation

A Semaphore in Kotlin coroutines (kotlinx.coroutines.sync.Semaphore) is a non-blocking synchronization primitive designed to throttle concurrency by managing a bounded pool of execution permits. Unlike a Mutex, which enforces binary mutual exclusion with strict single-owner semantics, a Semaphore is initialized with a capacity of N permits. Coroutines acquire permits asynchronously via the acquire() suspending function or the idiomatic withPermit block. When all N permits are actively checked out, subsequent coroutines suspend their execution without blocking their underlying OS worker threads, queueing their continuations until an active permit is released via release(). This permit accounting mechanism decouples concurrency limits from physical thread allocation. Engineers frequently confuse Semaphore with CoroutineDispatcher.limitedParallelism(N): limitedParallelism restricts how many physical OS threads a dispatcher may dispatch work onto concurrently, whereas a Semaphore restricts how many concurrent instances of a specific domain operation (such as parallel image downloads, network socket connections, or disk read operations) may be in flight simultaneously, irrespective of which dispatcher executes them.

## Practical walkthrough (English)

Consider an Android application downloading 100 user photo thumbnails in parallel. Launching 100 concurrent network requests overwhelms device bandwidth and triggers HTTP 429 Too Many Requests:
```kotlin
// Erroneous implementation: launches 100 unconstrained concurrent downloads
suspend fun downloadAllThumbnails(urls: List<String>) = coroutineScope {
    urls.map { url ->
        async(Dispatchers.IO) {
            imageClient.download(url) // 100 requests in flight simultaneously!
        }
    }.awaitAll()
}

// Production-grade solution: throttling concurrency using a Semaphore
suspend fun downloadAllThumbnailsThrottled(urls: List<String>) = coroutineScope {
    val semaphore = Semaphore(permits = 4) // Allow at most 4 concurrent downloads
    urls.map { url ->
        async(Dispatchers.IO) {
            semaphore.withPermit {
                imageClient.download(url) // Only 4 downloads active at any time
            }
        }
    }.awaitAll()
}
```
If an active download operation is cancelled while holding a permit inside withPermit, the builder guarantees that the acquired permit is automatically released in its finally block, preventing permit leaks.

## Explanation in Arabic

الـ `Semaphore` في Kotlin Coroutines هو أداة للتحكم في عدد العمليات المتزامنة وتحديد سقف التوازي (Concurrency Throttling):

1. ما هو الـ Semaphore؟
   - هو عداد تصاريح (Permit Counter) معلق.
   - يسمح لعدد محدد فقط من الـ Coroutines بالدخول في نفس الوقت (مثلاً: 3 coroutines فقط بالتوازي).
   - أي Coroutine إضافية تحاول الدخول **تُعلّق (Suspends)** بدون حظر الـ Thread، حتى تفرغ إحدى العمليات الحالية وتطلق التصريح (`release()`).

2. ما الفرق بين الـ Mutex والـ Semaphore؟
   - الـ `Mutex` هو حالة خاصة من الـ Semaphore بتصريح واحد فقط (`permits = 1`)، ويضمن الاستبعاد المتبادل الحصري (Mutual Exclusion).
   - الـ `Semaphore` يسمح بـ N تصاريح (`permits = N`) لتحديد سقف التوازي.

3. متى نستخدمه في Android الإنتاجي؟
   - **رفع ملفات وصور متعددة بالتوازي:** لو المستخدم بيختار 50 صورة لرفعها، لا نريد إطلاق 50 طلب شبكة في نفس اللحظة لإرهاق الـ Socket والـ Bandwidth؛ نستخدم Semaphore بـ 3 تصاريح.
   - **تحديد استهلاك الـ Memory والـ CPU** في معالجة الـ Bitmaps.

## Practical walkthrough

في شاشة رفع ألبوم صور (Batch Image Uploader):
```kotlin
class ImageUploadRepository(private val api: MediaApi) {
    // نحدد الحد الأقصى للرفع المتزامن بـ 3 صور فقط:
    private val uploadSemaphore = Semaphore(permits = 3)

    suspend fun uploadAllImages(images: List<File>): List<UploadResult> = coroutineScope {
        images.map { imageFile ->
            async(Dispatchers.IO) {
                // acquire تصريح، وتنفيذ الرفع، ثم تحرير التصريح تلقائياً عبر withPermit:
                uploadSemaphore.withPermit {
                    api.uploadImage(imageFile)
                }
            }
        }.awaitAll()
    }
}
```
النتيجة: يتم رفع الـ 50 صورة بالكامل، ولكن بحد أقصى 3 صور في نفس اللحظة بسلاسة تامة وبدون خنق لشبكة الجهاز.

## Why it matters and how it works

`withPermit` acquires cancellably and releases when the block exits, including failure. Scope the semaphore to the shared resource, not per request, or every call gets a fresh full quota. Use bounded queues and timeouts when callers can accumulate indefinitely.

## Worked example

JVM/Android-compatible snippet; all calls share one limiter instance and `fetch` is cancellable.

```kotlin
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

class LimitedApi(private val fetch: suspend (String) -> String) {
    private val permits = Semaphore(3)
    suspend fun get(id: String): String = permits.withPermit { fetch(id) }
}
```

## Trade-offs and decision criteria

Use semaphore for a bounded number of in-flight operations; `limitedParallelism` can limit dispatcher execution but is not identical to an end-to-end API permit. Too few permits raise latency; too many overload dependencies. Observe queue wait and server responses.

## Failure modes

Constructing `Semaphore(3)` inside each `get` call limits nothing globally. Manually acquiring without `finally` can leak a permit after exception and stall all later requests. Permit limits alone do not prevent a huge waiting queue.

## Production perspective

A media repository limits concurrent thumbnail downloads to three per host while allowing UI cancellation. Metrics separate wait time, network time and server throttling. A bounded producer prevents thousands of queued offscreen requests.

## Interview answer — short

A Semaphore throttles concurrency by managing N permits. Coroutines acquire permits via withPermit and suspend without blocking threads when none are available. Unlike limitedParallelism, which restricts the number of active OS threads, a Semaphore throttles access to specific shared operations or resources (like network requests or database connections) regardless of the underlying dispatcher.

## Interview answer — structured

A Semaphore manages a defined quota of permits to throttle concurrent access to shared resources in Kotlin coroutines. When initialized with N permits, up to N coroutines can enter the protected block concurrently using withPermit.

The essential characteristic of kotlinx.coroutines Semaphore is that it is completely non-blocking. When all permits are exhausted, additional coroutines suspend in user space rather than parking physical operating system threads, ensuring that shared dispatchers remain responsive.

In production, a Semaphore is ideal for throttling high-volume background tasks such as bulk media uploads, database queries, or rate-limited API integrations where overwhelming remote services must be prevented.

Engineers must distinguish between a Semaphore and dispatcher throttling. While CoroutineDispatcher.limitedParallelism restricts thread allocation within a pool, a Semaphore restricts logical operation concurrency. Using withPermit guarantees automatic permit release even if the enclosed suspending operation is cancelled or throws an exception, eliminating permit leak vulnerabilities.


## Interview answer — deep senior

Under the hood, kotlinx.coroutines.sync.Semaphore is implemented using a lock-free queue of continuations and an atomic state counter representing available permits. When acquire is invoked, the semaphore attempts to decrement the permit counter via a compare-and-swap loop. If the counter is greater than zero, the permit is granted immediately with zero suspension overhead. If no permits remain, the coroutine creates a CancellableContinuation, enqueues it into a linked segment queue (SegmentQueue), and suspends. When an active coroutine completes and calls release, the semaphore checks the waiting queue: if queued continuations exist, it dequeues the next continuation and resumes it directly on its dispatcher; otherwise, it atomically increments the permit counter. Crucially, withPermit wraps this sequence in a try-finally block. If a waiting coroutine is cancelled while queued in the semaphore, its continuation cancellation listener cleanly unlinks the node from the segment queue without leaking permits. Conversely, if cancellation strikes while the permit is actively held, the finally block ensures release is invoked, returning the permit to the available pool. The architectural distinction between Semaphore(N) and Dispatchers.IO.limitedParallelism(N) is vital in staff-level design. limitedParallelism(N) limits execution to N threads within that dispatcher view, but does not prevent coroutines running on Dispatchers.Default or Dispatchers.Main from accessing the same underlying API. A Semaphore acts as an application-level token bucket that governs access across any dispatcher, ensuring that external constraints—such as an HTTP client's connection pool or a third-party SDK concurrency limit—are strictly respected across the entire application.

## How to answer in the interview

- **Why:** a backend and device have finite concurrent capacity.
- **How:** share one Semaphore across calls and release permits in finally through withPermit.
- **Trade-off:** lower concurrency protects service but increases queue latency.
- **Failure case:** per-request semaphores do not constrain global fan-out.
- **Production solution:** tune the limit from metrics and combine it with server rate-limit handling.

## Deep-dive talking points

Compare permit bound, thread bound, rate limit and queued backlog.

## Follow-up questions

- **Interviewer:** "What happens if a coroutine holding a Semaphore permit is cancelled?"
  **Answer:** "When using `semaphore.withPermit`, the release is wrapped in a `try-finally` block. If the coroutine is cancelled while holding the permit, the `finally` block executes and releases the permit automatically, preventing permit leaks."

- **Interviewer:** "Can a Semaphore be initialized with 1 permit?"
  **Answer:** "Yes. A Semaphore with 1 permit behaves conceptually like a Mutex, but `Mutex` is preferred for single-permit mutual exclusion because it provides clearer ownership semantics and dedicated locking helpers."

- **Interviewer:** "How does Semaphore compare to Java's `java.util.concurrent.Semaphore`?"
  **Answer:** "Java's Semaphore blocks the OS thread when `acquire()` is called without permits. Kotlin's `kotlinx.coroutines.sync.Semaphore` is non-blocking: its `acquire()` is a suspending function that frees the underlying thread."

## Self-check rubric

Can I scope a shared semaphore, release permits safely, and distinguish active versus waiting work?

## References and reviewed-on date

- [Kotlin Semaphore API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-semaphore/) — permit semantics.

Technically reviewed against primary documentation on 2026-10-13.
