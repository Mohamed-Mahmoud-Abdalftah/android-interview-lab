---
id: "COR-24"
question: "What is the risk of GlobalScope or creating a scope inside each repository method?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 105
editorial_status: "reviewed"
---

# COR-24

## Original interview question

What is the risk of GlobalScope or creating a scope inside each repository method?

## What the interviewer evaluates

Explain detached lifetime and why a fresh repository scope per method loses caller ownership.

## Concept and technical explanation

Violating structured concurrency by relying on GlobalScope or instantiating unattached CoroutineScope instances inside repository methods is a critical architectural anti-pattern in Android engineering. GlobalScope is an unbounded, top-level scope that operates across the entire lifetime of the application process. Coroutines launched in GlobalScope completely bypass the caller's cancellation hierarchy; if a user navigates away and the hosting ViewModel is cleared, a GlobalScope coroutine continues running, leaking memory references, consuming network bandwidth and battery, and dropping unhandled exceptions into the global process handler. Similarly, creating a new ad-hoc scope inside a repository method (such as CoroutineScope(Dispatchers.IO).launch) severs caller ownership. The calling ViewModel or UseCase cannot cancel the underlying task, cannot await its completion, cannot observe exceptions directly, and unit testing becomes non-deterministic because test runners cannot control detached scopes. Repositories should exclusively expose main-safe suspending functions or cold Flows that execute within the caller's lifecycle scope, delegating long-running operations to an injected application-level supervisor scope or WorkManager.

## Practical walkthrough (English)

Consider a repository method updating user profile settings:
```kotlin
// Erroneous implementation: creates a detached scope inside repository
class BadUserRepository {
    // BUG: Severing caller ownership and structured concurrency!
    fun updateUser(user: User) {
        CoroutineScope(Dispatchers.IO).launch {
            api.update(user) // Uncancellable by caller, leaks if ViewModel clears!
        }
    }
}

// Production-grade implementation: main-safe suspending contract
class GoodUserRepository(
    private val api: UserApi,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    // Suspends within caller scope, fully cancellable, main-safe:
    suspend fun updateUser(user: User): Result<Unit> = withContext(ioDispatcher) {
        try {
            api.update(user)
            Result.success(Unit)
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```
If the caller's viewModelScope cancels while api.update is in flight, withContext ensures the network call is promptly cancelled, maintaining zero resource leaks.

## Explanation in Arabic

استخدام `GlobalScope` أو إنشاء CoroutineScope داخل دوال الـ Repository هو أحد أسوأ الـ Anti-Patterns التي تدمر الـ Architecture:

1. مخاطر `GlobalScope`:
   - هو نطاق غير مقيد (Unbound Scope) بدون أي أب شرعي، ويعيش طوال حياة التطبيق.
   - **تسريب الموارد والذاكرة (Resource Leaks):** العمليات المطلقة فيه لا يمكن إلغاؤها عند مغادرة الشاشة؛ تظل تستهلك البطارية و RAM والشبكة في الخلفية.
   - **فقدان الاستثناءات والـ Crashes:** الاستثناءات فيه لا تخضع للـ Structured Concurrency، وتؤدي إما لانهيار التطبيق أو ضياع الأخطاء بصمت.

2. مخاطر إنشاء `CoroutineScope` داخل دوال الـ Repository:
   - كتابة `fun fetch() { CoroutineScope(Dispatchers.IO).launch { ... } }`.
   - **كسر دورة الحياة:** في كل مرة تنادي الدالة، يتم إنشاء Scope جديد منفصل تماماً ملوش أي علاقة بالـ ViewModel أو الـ UI.
   - **مستحيل إلغاؤه (Uncancellable):** لو المستخدم خرج من الشاشة، الـ Repository هيفضل شغال ويجلب بيانات مفيش حد مستنيها!
   - **كسر الـ Testing:** اختبارات الـ Unit Tests تفشل لأن الـ Scope الجديد يعمل على threads خارج سيطرة الـ TestDispatcher.

3. النمط المعماري الصحيح (The Architecture Standard):
   - دوال الـ Repository يجب أن تكون **`suspend fun` عادية** (تستقبل الـ Scope من المتصل) أو ترجع `Flow<T>`.
   - الـ ViewModel هو المسؤول الوحيد عن إطلاق الـ Coroutines عبر `viewModelScope`.

## Practical walkthrough

مقارنة بين التصميم السيئ والتصميم المعماري النظيف:
```kotlin
// ❌ تصميم كارثي في الـ Repository:
class BadUserRepository {
    fun updateUser(user: User) {
        // كارثة: ينشئ scope مستقل غير مربوط بالـ lifecycle ولا يمكن إلغاؤه!
        CoroutineScope(Dispatchers.IO).launch {
            api.update(user)
        }
    }
}

// ✅ التصميم النظيف المتوافق مع Clean Architecture:
class GoodUserRepository(private val api: Api, private val ioDispatcher: CoroutineDispatcher) {
    // الدالة معلقة، Main-Safe، ومربوطة بنطاق المتصل:
    suspend fun updateUser(user: User) = withContext(ioDispatcher) {
        api.update(user)
    }
}
```

## Why it matters and how it works

Structured child jobs allow the caller to await completion and cancel obsolete work. Detached scopes return before work finishes and need separate exception handling/shutdown. A repository may legitimately own a shared application scope for a specific in-process operation, but ownership must be explicit and testable.

## Worked example

Illustrative repository contract; `remote.fetch` is a main-safe suspending API, and the caller chooses `viewModelScope` or another owner.

```kotlin
interface RemoteProfile { suspend fun fetch(id: String): String }

class ProfileRepository(private val remote: RemoteProfile) {
    suspend fun load(id: String): String = remote.fetch(id)
}
```

## Trade-offs and decision criteria

A suspend API gives the caller control over lifetime and failure. Injecting an application scope is reasonable for independent in-process work such as cache warming, with a supervisor, logger and shutdown. WorkManager plus persistence is required for restartable work under OS scheduling.

## Failure modes

Fresh scopes per invocation can leak network calls after navigation, race with logout and hide errors. A `GlobalScope.launch` payment update may be killed with the process and has no reliable completion channel. Returning from a method does not mean its detached child succeeded.

## Production perspective

A profile ViewModel calls `repository.load` in `viewModelScope`; navigation cancels it. A cache warmer uses an injected application-owned scope. Payment reconciliation persists an operation ID and schedules durable work, then exposes status from storage.

## Interview answer — short

Using GlobalScope or creating detached CoroutineScopes inside repository methods breaks structured concurrency. It severs the caller's cancellation hierarchy, causing zombie background tasks, memory leaks, and silent failures when screens close. Repositories should expose main-safe suspend functions or cold Flows that execute within the caller's lifecycle scope, using an injected application scope or WorkManager only for durable operations.

## Interview answer — structured

Structured concurrency establishes that every coroutine must be launched within a well-defined lifecycle boundary that guarantees parent-child ownership. Relying on GlobalScope or instantiating ad-hoc CoroutineScopes inside repository methods directly undermines this contract.

Launching work in GlobalScope creates orphaned coroutines tied to process lifetime. When a ViewModel is cleared during screen exit, the coroutine continues executing in the background, wasting network bandwidth, battery, and retaining references that cause memory leaks.

In production, creating an internal scope like CoroutineScope(Dispatchers.IO) inside a repository method severs the link with the caller. The caller cannot cancel the operation, cannot await its completion, and cannot catch thrown exceptions. Furthermore, automated unit testing with runTest becomes impossible to synchronize deterministically because the detached scope operates outside the test scheduler.

Repositories must expose suspending functions using withContext for main-safety, or emit cold Flows. If a task must outlive the screen, it must be delegated to an application-scoped supervisor scope injected via dependency injection or scheduled durably using WorkManager.


## Interview answer — deep senior

At the framework level, the power of Kotlin coroutines derives from parent-child Job hierarchy trees. When viewModelScope.launch executes, the child coroutine inherits the parent's Job, ensuring that viewModelScope.cancel cascades downwards, transitioning all active child jobs to the Cancelling state and terminating active delay or I/O suspension points. When an engineer writes CoroutineScope(Dispatchers.IO).launch inside a repository, a new root Job is created with zero parent link. If the ViewModel is destroyed, its cancellation signal never reaches this orphaned job. This introduces severe production bugs: an orphaned network request can complete seconds later and attempt to write stale data into local databases, overwriting newer user changes in a race condition. Moreover, any unhandled exception in that detached scope cannot be caught by the calling ViewModel; it bypasses standard UI error handling and crashes the entire application process through the default thread exception handler. In staff-level architecture, we enforce a strict separation of concerns regarding scope ownership. UI and presentation logic own transient, view-bound lifecycles via viewModelScope. Repositories and DataSources must remain stateless with regard to execution lifecycles; they expose suspend functions or cold Flows that execute on whichever CoroutineContext the caller provides, switching dispatchers internally via withContext(ioDispatcher) to guarantee Main-Safety. For the rare operations that must survive screen transitions—such as finishing an offline database sync or logging an analytics event—we inject an @ApplicationScope CoroutineScope(SupervisorJob() + Dispatchers.Default) managed by Hilt. For guaranteed durability across process termination or device reboots, we reject in-memory scopes entirely and delegate execution to Android Jetpack WorkManager.

## How to answer in the interview

- **Why:** hidden scopes hide completion, cancellation, and failures.
- **How:** keep suspend repository APIs under the caller's Job unless work has a deliberate longer-lived owner.
- **Trade-off:** an application scope survives navigation but not process death.
- **Failure case:** stale session writes or uncaught GlobalScope launch errors.
- **Production solution:** inject an owned scope or persist and schedule durable operations.

## Deep-dive talking points

Compare job inheritance, injected owner lifetime, logout and process death; distinguish `withContext(IO)` from creating a new Job.

## Follow-up questions

- **Interviewer:** "Why does `GlobalScope` prevent unit test determinism?"
  **Answer:** "Because `GlobalScope` runs on background JVM threads completely outside the `kotlinx-coroutines-test` test scheduler. Unit tests will finish and exit before the `GlobalScope` coroutine completes, causing false passes or intermittent race condition test failures."

- **Interviewer:** "When should work be offloaded to WorkManager instead of an ApplicationScope?"
  **Answer:** "Use ApplicationScope for short tasks that should survive screen navigation while the app process is alive (e.g., in-memory cache sync). Use WorkManager for persistent tasks that must survive app process death, low memory kills, or device reboots (e.g., large file uploads, sync jobs)."

- **Interviewer:** "What is the rule of thumb for repository API contracts?"
  **Answer:** "Repositories expose suspend functions for one-shot requests and Flow<T> for continuous observable streams. Repositories do not launch coroutines; they only execute inside the caller's coroutine."

## Self-check rubric

Can I name the owner, explain error/cancellation propagation and design a durable alternative for process death?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — structured ownership.
- [Android background work](https://developer.android.com/develop/background-work/background-tasks/persistent) — persistent scheduling.

Technically reviewed against primary documentation on 2026-10-13.
