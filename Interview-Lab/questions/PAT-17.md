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

Can the candidate find shared mutable state, identify its real owner and lifetime, isolate tests, and separate instance scope from persistence and thread safety?

## Concept and technical explanation

A Kotlin `object` is a convenient single instance within its runtime context. Mutable fields on a globally reachable object can become hidden input to tests that share a JVM process: one test changes a token, another observes it. The same symptom can come from any shared mutable cache or test fixture, so diagnose the state path before blaming the pattern name. Stateless objects and constants are not inherently problematic.

Choose who owns the state. An account session may need one in-memory instance per signed-in account, a durable source for facts that must survive process death, and an explicit logout or account-switch transition. Consumers receive the owner through constructors. Unit tests construct a fresh owner or fake per test and avoid sharing it across parallel cases. Hilt can provide one instance within a chosen component, but `@Singleton` means one per application component instance, not durable storage, automatic account isolation, or thread safety. An ordinary class can be wired manually as well.

## Practical walkthrough (English)

First reproduce the order dependency: a test logs in by setting `GlobalSession.user`, and a later logged-out test unexpectedly sees that value in the same test process. Trace every write and read. Replace implicit global access with a `SessionStore` passed into the use case. Each test creates a fresh store. Production owns the shared store at a deliberate lifetime, clears it on logout, and loads persisted state through a separate repository if restart recovery is needed.

## Explanation in Arabic

المشكلة مش كلمة Singleton لوحدها؛ المشكلة Shared Mutable State مالهاش Owner واضح. `object` فيها `var user` ممكن تختبر Log in فتسيب قيمة، واختبار تاني في نفس الـ JVM يشوفها. حدد مين يملك Session ولمدة قد إيه، ومرّر Store صريحة للـ consumers. في كل Test أنشئ Store جديدة. في Production حدّد Logout وAccount Switch وProcess Restart، وما تعتبرش `@Singleton` تخزين دائم أو حماية تلقائية من Race Conditions.

## Why it matters and how it works

Implicit global state hides dependencies and makes test outcomes sensitive to earlier writes. Explicit construction makes the state owner visible and lets tests choose a fresh instance. A DI scope can share an instance where needed, but tests must still isolate all other shared resources. If multiple threads update a session, add synchronization or a serialized state owner. If state must survive process death, store and restore it explicitly; an in-memory singleton cannot provide that.

## Worked example

Runnable Kotlin/JVM example. This small store is intentionally in-memory and not thread-safe:

```kotlin
class SessionStore(initialUser: String? = null) {
    private var user = initialUser
    fun currentUser(): String? = user
    fun update(value: String?) { user = value }
}

class IsSignedIn(private val session: SessionStore) {
    fun check(): Boolean = session.currentUser() != null
}
```

Each test creates its own `SessionStore` and `IsSignedIn`. In production, the owner would define synchronization, persistence, and account-switch behavior according to the app's needs.

## Trade-offs and decision criteria

Constructor injection adds wiring but makes state ownership and test setup explicit. A stateless `object` can remain simple. An application-scoped store may be appropriate for one active session, but it can still hold stale account data unless logout and switching are designed. A narrower owner is preferable when state belongs to a screen or flow. Neither replacing `object` with `class` nor adding an interface removes races by itself.

## Failure modes

A test resets a global only in `@AfterEach`; an exception or parallel test still exposes shared state. A fresh store per test helps with that store, but shared database files, static clocks, or external services can still cause order dependence. A Hilt `@Singleton` that captures an `Activity` can outlive that Activity. Storing a token only in memory loses it on process death; retaining sensitive data requires an explicit security and persistence decision.

## Production perspective

For a signed-in account, define one session owner and a clear logout/account-switch action. Let a repository load any durable facts after restart. Test two fresh instances independently, then test account switching and concurrent updates using the chosen synchronization contract. Server authorization remains authoritative; an in-memory session flag is only local UI state.

## Interview answer — short

I trace the mutable state that one test leaves for another, then give it an explicit owner and lifetime. Consumers receive a session store through constructors, and each test gets a fresh instance. Production may share one scoped instance, but `@Singleton` does not make it durable or thread-safe. I also define logout and account switching; a stateless Kotlin `object` can stay.

## Interview answer — structured

An order-dependent test tells me some input is leaking between cases. A global `object` with a mutable user or token is one possible source; shared files, caches, and fixtures can do the same. I reproduce the order, trace reads and writes, and move session state behind an owner whose lifetime matches the product: account, flow, or application instance. Consumers take it in the constructor instead of reaching for global state.

Each unit test creates a fresh store or fake, so its setup does not inherit that particular state from another case. Production can use Hilt to share the owner at an appropriate component scope, or wire it manually. I still need an explicit logout/account-switch path, synchronization if threads write concurrently, and persistent storage if facts must survive process death. I would test those separately rather than promise that DI alone fixes every flaky test.

## Interview answer — deep senior

I start by proving the coupling. I run the failing tests in opposite orders and trace every read and write to the shared `object` or static holder. Kotlin initializes an object declaration on first access, but the mutable fields remain reachable for its runtime lifetime. Tests sharing a process may observe earlier writes. It is a hidden dependency, so the same failure can appear with a static cache, reused fixture, database file, or fake server. I do not call every singleton bad: stateless objects and immutable constants are often fine.

Next I choose the owner from the domain lifetime. For a signed-in account, a session store might be shared across features until logout or account switch. I make those transitions explicit and inject the store into consumers. Each unit test constructs a fresh owner; this removes that one shared-state path, though parallel tests still need isolation of any other shared resources. An interface is useful if it protects a meaningful boundary, but an ordinary concrete class is enough for a small in-memory store.

In production, Hilt `@Singleton` scopes an instance to its application component; it is not durable storage, a mutex, or a per-account scope. If state survives restart, a repository loads it from a chosen durable source. If multiple threads mutate it, I use a synchronization or serialized update contract. I test logout, account switching, process restoration, and concurrent writes according to those contracts. A temporary reset hook can aid diagnosis, but I would remove dependence on global mutation instead of treating reset order as the architecture.

## How to answer in the interview

- Reproduce the order dependency and name the shared mutable input.
- Specify the owner and lifetime before choosing DI scope.
- Explain fresh per-test instances and separate persistence and concurrency concerns.
- State when a stateless `object` remains reasonable.

## Deep-dive talking points

Test-process sharing; hidden inputs; application component scope versus account lifetime; logout and process death; concurrent mutation; test fixtures beyond the session store.

## Follow-up questions

- **Interviewer:** “Is every Kotlin `object` bad?” **Answer:** “No. The issue here is globally reachable mutable state; a stateless object can be appropriate.”
- **Interviewer:** “Does Hilt `@Singleton` solve test order dependence?” **Answer:** “It scopes one instance to a component. Tests still need fresh graphs or stores, and other shared resources can still leak.”
- **Interviewer:** “What survives process death?” **Answer:** “Only data explicitly persisted and restored; an in-memory session instance does not.”

## Self-check rubric

Can I trace an order-dependent write, pick the right state owner, isolate tests, and distinguish DI scope from durability and thread safety?

## References and reviewed-on date

- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — singleton object semantics.
- [Android Hilt guide](https://developer.android.com/training/dependency-injection/hilt-android) — generated components and scopes.
- [Android architecture](https://developer.android.com/topic/architecture) — state and data ownership.

Technically reviewed against primary documentation on 2026-10-19.
