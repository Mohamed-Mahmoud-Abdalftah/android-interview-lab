---
id: "DAT-10"
question: "How do you avoid concurrent refresh-token races?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 267
editorial_status: "reviewed"
---

# DAT-10

## Original interview question

How do you avoid concurrent refresh-token races?

## What the interviewer evaluates

Prevent concurrent refresh-token rotation races with a single-flight, double-check protocol.

## Explanation in Arabic

لو طلبين استقبلوا `401` في نفس اللحظة وكل واحد عمل refresh، السيرفر اللي يدوّر refresh token ممكن يبطل واحد منهم ويعمل logout غلط. نستخدم Mutex/single-flight على session owner: بعد الدخول للـlock نقارن token الذي فشل بالـtoken الحالي؛ لو اتغير نعيد الطلب بالجديد من غير refresh. لو لم يتغير، نعمل refresh واحد ونحفظ access+refresh atomically.

## Why it matters and how it works

Lock must be shared across calls for the same session, not recreated per request. Bound refresh attempts and handle permanent invalid refresh as session expiration. Cancellation of one waiter should not necessarily cancel a refresh owned by the session; define ownership explicitly, and reject refresh results after logout generation changes.

## Worked example

Conceptual coroutine coordinator; TokenStore and refresh API are app-owned, and the adapter to synchronous OkHttp Authenticator requires careful threading.

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class TokenRefresh(private val store: TokenStore, private val api: AuthApi) {
    private val lock = Mutex()
    suspend fun tokenAfter401(sent: String): String = lock.withLock {
        val generation = store.generation()
        val current = store.accessToken()
        if (current != sent) return@withLock current
        val pair = api.refresh(store.refreshToken())
        check(store.replaceIfGeneration(generation, pair)) { "session changed" }
        pair.access
    }
}
// TokenStore must atomically compare session generation and replace both tokens;
// a logout increments the generation. These are app-owned contracts.
```

## Practical walkthrough

mutex حوالين refresh لوحده مش كفاية؛ لازم recheck للـaccess token بعد ما caller يستنى lock. مثال: A وB اتلقوا 401 لتوكن v1؛ A يحدّث لـv2، B يدخل lock بعده فيلاحظ v2 ويرجع retry به بدل refresh تاني. خزّن access+refresh كزوج في عملية واحدة، واربطه بـsession generation عشان logout أثناء refresh ما يتراجعش. لو refresh server رجّع invalid_grant، أنهِ session حسب العقد؛ لو timeout، ما تعلنش logged out تلقائيًا. في OkHttp Authenticator sync، تجنب lock coroutine مع blocking `runBlocking` على نفس dispatcher/client من غير تصميم دقيق.

## Trade-offs and decision criteria

Mutex simplifies correctness but holds waiters during network refresh; use a session-level Deferred/single-flight if many callers should await one refresh without holding a lock. A server refresh-token family/rotation policy matters. Do not overwrite credentials after logout.

## Failure modes

A per-request Mutex protects nothing across two requests. Refreshing without recheck duplicates rotation. A stale refresh response can resurrect a logged-out account unless session generation is checked before commit.

## Production perspective

A session repository stores tokens with generation, serializes refresh and replaces the pair in one protected step. The backend invalidates rotated credentials per its policy. Concurrency tests start two 401s simultaneously and assert one refresh and both retries use the new token.

## Interview answer — short

“I use one session-scoped refresh coordinator. After acquiring the lock, I recheck whether the failed request’s token is already obsolete; only if it is current do I refresh once and atomically save the new pair.”

## Interview answer — structured

“The race appears when two requests fail with the same access token. Both can try to rotate the refresh token, and the second may invalidate the first or trigger an incorrect logout. I serialize refresh in a session-scoped coordinator, recheck the stored access token after entering the lock, and let later callers reuse the token another request produced. The new access/refresh pair is stored atomically. I bound retry loops and use a session generation so a refresh completing after logout cannot restore credentials. A server refresh-token family/rotation policy matters. Do not overwrite credentials after logout.”

## Interview answer — deep senior

I design refresh as a single-flight state transition. The key invariant is one refresh operation per observed expired token for a session. A lock or in-flight Deferred coordinates callers, and every waiter rechecks current token after waiting. Token-pair persistence and session generation checks must be atomic with respect to logout; otherwise a late response can resurrect a cleared session. In an OkHttp Authenticator integration I remember that the callback is synchronous and avoid recursion through the same auth client or exhausting its executor. I test two, ten and cancelled callers, server token rotation, refresh failure and logout during refresh. Permanent invalid credentials clear session; transient network failure does not automatically mean the user is unauthenticated. Refreshing without recheck duplicates rotation.

The invariant is one logical refresh per expired token in one live session. I would coordinate callers with a lock or in-flight task, then recheck the stored access token after waiting: if another request already replaced v1 with v2, I retry with v2 instead of rotating again. I store the new access and refresh token together, conditional on the session generation so logout cannot be undone by a late response. I treat permanent invalid-grant differently from a transient network error. Because OkHttp’s Authenticator is synchronous, the adapter must not block a dispatcher or connection path needed by its own refresh call. Concurrency tests should force both 401 responses at once.

## How to answer in the interview

- **Why:** Multiple expired requests must share one logical rotation.
- **How:** Lock, recheck token inside lock, refresh once, persist pair conditionally.
- **Trade-offs:** Coordinate waiters without coupling to a cancelled screen scope.
- **Failure cases:** Double rotation, stale post-logout write, refresh deadlock.
- **Production solution:** Deterministic concurrent-401 and logout-race tests.

## Deep-dive talking points

Draw two callers racing, recheck-after-lock and logout generation safeguards.

## Follow-up questions

- [DAT-09](../dat-09/): Where attach token? **Answer:** transport boundary, with coordinated 401 handling.
- [DAT-19](../dat-19/): How avoid false session invalidation? **Answer:** one refresh plus generation-aware commit.

## Self-check rubric

Can I prove one refresh, atomic pair save, bounded retries and no logout resurrection?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — Mutex coordination.
- [OkHttp calls guide](https://lysine.dev/okhttp/features/calls/) — authentication follow-up.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
