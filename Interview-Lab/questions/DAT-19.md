---
id: "DAT-19"
question: "Two refresh-token requests both invalidate the session. How do you serialize refresh correctly?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "C"
phase: 3
priority: "P1"
order: 276
editorial_status: "reviewed"
---

# DAT-19

## Original interview question

Two refresh-token requests both invalidate the session. How do you serialize refresh correctly?

## What the interviewer evaluates

Serialize refresh-token rotation and avoid false logout from two concurrent 401 responses.

## Explanation in Arabic

اتنين requests بنفس access token ممكن يرجعوا `401` معًا. لو كل واحدة استخدمت refresh token rotating، الثانية قد تستعمل token اتبطل وتفسّر ده كـlogout. نعمل session-scoped single-flight: بعد lock نعيد قراءة token؛ لو اتغير بسبب الأولى، نعيد request بالجديد. لو لسه نفسه، واحدة تعمل refresh وتحفظ الزوج atomically، والباقي تنتظر. logout generation تمنع refresh متأخرة ترجع session اتقفلت.

## Why it matters and how it works

Bound the number of HTTP follow-ups and avoid authenticating the refresh call with the same looping authenticator. Differentiate permanent refresh rejection from transient network failure; only authoritative invalidation should clear session. The shared coordinator must outlive individual requests but be cancelled/reset on account switch.

## Worked example

Conceptual coordinator; TokenStore and AuthApi include atomic persistence and backend rotation contract.

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class SessionRefresh(private val store: TokenStore, private val api: AuthApi) {
    private val mutex = Mutex()
    suspend fun resolve401(sent: String, generation: Long): String = mutex.withLock {
        if (store.generation() != generation) error("session changed")
        val current = store.access()
        if (current != sent) return@withLock current
        val pair = api.rotate(store.refresh())
        check(store.saveIfGeneration(generation, pair)) { "session changed" }
        pair.access
    }
}
// saveIfGeneration atomically compares the session generation and stores both
// tokens; it returns false after logout or account switch.
```

## Practical walkthrough

rotate-on-use refresh token بيحصل له race بسهولة: A وB شايفين 401، A refresh وتخزن pair v2، B لازم تلاحظ v2 بعد lock وما ترسلش old refresh v1. commit pair مرتبط بـsession generation حتى logout وقت network wait يمنع late result من إعادة login. لو server رفض refresh نهائيًا، clear session بشكل منسق؛ timeout transient ما يتحولش تلقائيًا لlogout مؤكد. في OkHttp Authenticator، synchronous callback + refresh client بنفس interceptor ممكن يعمل recursive 401 أو deadlock. اصنع concurrency test بحاجز يخلي الطلبين يستقبلوا 401 سوا، وتحقق refresh request واحدة فقط.

## Trade-offs and decision criteria

Mutex is easy to reason about but makes waiters share refresh latency. An in-flight Deferred can reduce lock hold time but complicates cancellation ownership. The backend still determines token validity and rotation semantics.

## Failure modes

A refresh call cancelled by one screen must not necessarily cancel the session’s shared refresh for other requests. A late pair saved after logout resurrects credentials. Clearing session on a transient offline error logs users out unnecessarily.

## Production perspective

A multi-tab banking app coordinates refresh per signed-in account, rechecks token after lock, and stores new credentials only if session generation matches. Tests force simultaneous 401s, refresh 5xx, permanent invalid refresh and logout during refresh.

## Interview answer — short

“I serialize refresh per session, recheck the token after locking and reuse another request’s newly refreshed token. I atomically save the new pair only for the current session generation, avoiding false logout and late resurrection.”

## Interview answer — structured

“Two simultaneous 401s are a race when the server rotates refresh tokens. I use one session-owned coordinator. Each caller carries the token it sent; after waiting on the lock it compares that with current storage. If another caller already refreshed, it retries with the new token. Otherwise one refresh executes and saves access plus refresh token atomically. I bound follow-up attempts, exclude the refresh endpoint from recursive handling, and use a generation number so logout invalidates late refresh results.”

## Interview answer — deep senior

The invariant is one logical rotation for a given expired access token and live session. I test this as a concurrency protocol, not just a lock around an HTTP call. Waiters recheck after acquiring the lock, shared refresh ownership is defined so one cancelled screen does not ruin unrelated requests, and token-pair commit is conditional on session generation. A permanent server rejection can end the session; a transient transport failure should be surfaced without falsely declaring revocation. OkHttp’s synchronous Authenticator adapter needs its own execution design and a bounded response chain. I log correlation IDs, never tokens, and verify no stale refresh can resurrect a logged-out account.

I would express this as a state machine keyed by the expired access token and live session generation. A obtains the refresh lock, rotates v1 to v2, and persists both tokens; B then re-reads v2 inside the lock and retries without another rotation. If logout occurred while A waited for the server, its result is discarded rather than resurrecting the session. A permanent refresh rejection differs from a network timeout, and callers need the correct outcome. The synchronous OkHttp Authenticator adapter must use an independent refresh path and bounded attempts to avoid recursive 401 or self-deadlock. I test two simultaneous failures, cancellation, logout, and retry exhaustion deterministically.

## How to answer in the interview

- **Why:** Rotating tokens are invalidated by duplicate refresh calls.
- **How:** Lock by session, recheck inside lock, commit pair conditionally.
- **Trade-offs:** Separate transient network error from permanent invalid grant.
- **Failure cases:** Second rotation, recursive Authenticator, post-logout resurrection.
- **Production solution:** Barrier-based concurrent-401 test with one refresh call.

## Deep-dive talking points

Draw token observed/current comparison, session generation and refresh failure categories.

## Follow-up questions

- [DAT-10](../dat-10/): Why recheck under lock? **Answer:** another request may already have produced a new access token.
- [DAT-09](../dat-09/): Where handle 401? **Answer:** a coordinated auth boundary with bounded retries.

## Self-check rubric

Can I force two 401s, show one rotation, preserve logout and distinguish offline from invalid session?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — Mutex coordination.
- [OkHttp calls guide](https://lysine.dev/okhttp/features/calls/) — 401 authenticator follow-up.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
