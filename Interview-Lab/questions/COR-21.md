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

A Semaphore limits concurrency by maintaining a pool of permits. Coroutines acquire a permit before entering a critical block and release it when done; if no permits are available, incoming coroutines suspend without blocking their threads until a permit is freed.

## Interview answer — structured

A `Semaphore` controls concurrent access to a resource by maintaining a set of available permits. It is the primary tool for concurrency throttling in Kotlin Coroutines.

When a coroutine invokes `semaphore.withPermit { ... }`, it attempts to acquire a permit. If permits are available, the permit count decrements and the coroutine proceeds immediately. If all permits are exhausted, subsequent coroutines suspend non-blockingly until an active coroutine finishes and releases its permit.

I use Semaphores in Android whenever I need to bound parallel resource consumption—such as limiting concurrent media uploads to 3 at a time, restricting simultaneous image decodes to avoid memory spikes, or capping database write connections. It prevents thread starvation, network congestion, and out-of-memory crashes.

## Interview answer — deep senior

Internally, Kotlin's `Semaphore` is implemented as a lock-free segment-based queue of continuations. When permits reach zero, callers are suspended and their continuations are enqueued onto a lock-free linked list. When a permit is released, the head continuation is resumed and dispatched to its coroutine dispatcher.

In modern Kotlin (1.6+), you can also limit parallelism at the dispatcher level using `dispatcher.limitedParallelism(N)`. How do they compare? `limitedParallelism(N)` creates a new Dispatcher view that constrains execution to N threads, which limits CPU/thread allocation. `Semaphore(N)` controls logical permit access regardless of which dispatcher is running the work. For example, if you want tasks to run on the broad `Dispatchers.IO` pool (scaling up to 64 threads) but want strictly 4 concurrent network uploads to an API, `Semaphore(4)` is the right abstraction.

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
