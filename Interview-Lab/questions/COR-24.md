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

GlobalScope and ad-hoc repository scopes destroy structured concurrency. They produce un-cancellable background tasks that leak memory, waste network bandwidth, bypass exception handling, and make deterministic unit testing impossible. Repositories should expose suspend functions or Flows, leaving lifecycle scoping to ViewModels.

## Interview answer — structured

Using `GlobalScope` or creating ad-hoc `CoroutineScope` instances inside repository methods completely breaks structured concurrency.

When a repository creates its own scope (e.g., `CoroutineScope(Dispatchers.IO).launch`), that coroutine is detached from the calling ViewModel's lifecycle. If the user navigates away and the screen is destroyed, the ViewModel's `viewModelScope` cancels, but the repository coroutine keeps running in the background. This wastes CPU, leaks network bandwidth, and can trigger database race conditions.

Furthermore, detached scopes swallow or misdirect exceptions, making centralized error handling impossible, and they break unit testing because test runners cannot wait for or control un-tracked scopes.

In clean architecture, repositories should never launch coroutines. Repositories should expose **suspend functions** for one-shot operations (using `withContext` for main-safety) or **Flow** for streams. The ViewModel remains the sole owner of the lifecycle scope via `viewModelScope`.


## Interview answer — deep senior

From an architectural governance perspective, there is only one legitimate use case for a non-ViewModel scope in the data layer: operations that **must survive UI teardown** (like saving an offline transaction or uploading an analytics batch). However, even in that scenario, creating ad-hoc scopes inside methods is forbidden. Instead, we use an explicitly injected **ApplicationScope**:

```kotlin
class OrderRepository @Inject constructor(
    @ApplicationScope private val externalScope: CoroutineScope,
    private val api: OrderApi
) {
    suspend fun submitOrder(order: Order) {
        externalScope.launch { api.submit(order) }.join()
    }
}
```

By injecting a singleton `ApplicationScope` bound to a `SupervisorJob`, the lifecycle is formally tracked by the DI container, exceptions are captured by a centralized handler, and unit tests can easily inject a `TestScope` to verify background completion.


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
