---
id: "PAT-17"
question: "A global Singleton makes tests order-dependent. How do you redesign ownership?"
topic: "Design Patterns"
code: "PAT"
group: "C"
phase: 2
priority: "P1"
order: 208
editorial_status: "reviewed"
---

# PAT-17

## Original interview question

A global Singleton makes tests order-dependent. How do you redesign ownership?

## What the interviewer evaluates

Redesign global mutable singleton ownership to eliminate test order dependence and lifecycle leaks.

## Explanation in Arabic

Global singleton mutable زي `object SessionCache { var user = ... }` تفضل بين tests في نفس process، فتستطيع test A تغيّر نتيجة B. كمان process death يمسحها وActivity references تسرّب memory. حدّد owner: repository أو session state holder بlifetime واضح، constructor injection للكود اللي يحتاجه، وfactory/test setup تنشئ instance جديدة لكل test. لو في shared app instance، اجعل state immutable snapshots أو تحكم في writes، وخزّن durable facts في data layer. `object` stateless formatter ممكن يفضل okay؛ المشكلة mutable global ownership.

## Why it matters and how it works

Global mutable state creates hidden dependencies and inter-test coupling. DI with explicit scopes makes ownership and replacement visible; repository persistence handles process death. Stateless singletons are different from shared mutable caches.

## Worked example

JVM illustration:
```kotlin
class SessionStore(initialUser: String? = null) {
    private var user = initialUser
    fun currentUser() = user
    fun update(value: String?) { user = value }
}
```
Each unit test constructs its own store. Production may wrap persistent storage and synchronization; this small class alone is not thread-safe or durable.

## Practical walkthrough

global `object SessionStore` بيعيش طول process، فtest A تكتب user وtest B تشوفه لو مفيش reset؛ production account switch ممكن يورث data من user قديم، وprocess death يمسحها. بدّلها بـ`SessionStore` instance تتخلق في auth/session scope وتتحقن في consumers، مع `close/reset` واضح وقت logout. test ينشئ store جديدة لكل case أو fake store. لو process restart، token/session recovery من persistent credential policy/server، مش من singleton memory. ما تعملش App-wide `@Singleton` لكل حاجة عشان DI موجودة؛ scope لازم تتطابق مع ownership.

## Trade-offs and decision criteria

An injected instance adds wiring but improves isolation and ownership. A stateless `object` may be simplest. If multiple threads access mutable session data, use a proper state holder and synchronization; merely replacing singleton with class does not solve races.

## Failure modes

A test sets `SessionCache.user = "admin"` and forgets reset; a later authorization test passes or fails depending on order. Clear setup per test is a temporary patch; explicit injected owner prevents cross-test state. Server still authorizes.

## Production perspective

A fintech app moves session facts to repository backed by protected storage and server refresh. Features observe typed state; tests inject fresh fake stores; logout/refresh races are tested.

## Interview answer — short

A mutable global Singleton makes tests share hidden state and can leak lifecycle objects. I replace it with an explicitly owned, injected state holder and fresh test instances, while keeping durable session truth in repository/server paths.

## Interview answer — structured

I first separate stateless singleton helpers from mutable global state. The latter creates order-dependent tests because values survive between cases in one process, and it does not survive Android process death reliably. I move the state into a repository or scoped holder with constructor injection, so each test gets a fresh fake. If production needs a shared instance, DI can scope it deliberately and I define synchronization and persistence. A singleton should not retain an Activity or act as client-side authorization authority.

## Interview answer — deep senior

The root problem is hidden ownership. A global `object` with mutable fields can be read and changed by any caller, so tests influence one another and production behavior depends on call order. I identify who owns updates and what must survive process death. A session repository can expose immutable snapshots, persist only appropriate token material, refresh with the backend, and invalidate on logout. Features depend on its contract rather than global access. Unit tests construct a new in-memory fake per test, and integration tests cover refresh/logout races. A DI singleton may still be used for the repository instance, but its scope and state protocol are explicit; it must not capture Activity context. Stateless `object` helpers remain fine.

I would first identify who owns the mutable state. A global `object SessionStore` couples every test to the previous process state and can retain one account after a switch. I replace it with an instance passed through constructors, scoped to the authenticated session, and dispose or reset it on logout. Each test constructs its own store, so order no longer changes the result; integration tests verify account-switch teardown. The object still disappears on process death, so durable credentials and server session recovery need a separate design. A DI container helps wire the scope, but marking the store application-wide singleton would recreate the problem under a different annotation. Ownership, not the keyword, is the fix.

## How to answer in the interview

- **Why:** Global mutable state creates order dependence and stale accounts.
- **How:** Inject a session-scoped store and tear it down on logout.
- **Trade-off:** Keep stateless singletons; scope mutable session objects narrowly.
- **Failure case:** Test pollution, Activity leak or process-death assumption.
- **Production solution:** Per-test instances, account-switch test and durable recovery path.

## Deep-dive talking points

Diagnose test order dependence, separate stateless singleton, specify owner, persistence and concurrency.

## Follow-up questions

- [PAT-03](../pat-03/): Is a Kotlin object durable? **Answer:** no; it is an in-process instance.
- [DI-14](../di-14/): Why not singleton-scope everything? **Answer:** long lifetimes cause leaks and shared mutable state.

## Self-check rubric

Explain a failing test order, propose injection, and state what must survive process death.

## References and reviewed-on date

- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — object lifetime.
- [Android architecture guide](https://developer.android.com/topic/architecture) — persistent data ownership.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
