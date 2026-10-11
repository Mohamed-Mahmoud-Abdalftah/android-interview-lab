---
id: "DAT-09"
question: "How do you implement authentication interceptors and refresh-token logic safely?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 266
editorial_status: "reviewed"
---

# DAT-09

## Original interview question

How do you implement authentication interceptors and refresh-token logic safely?

## What the interviewer evaluates

Design token attachment and refresh handling without loops, leakage or racing requests.

## Explanation in Arabic

Interceptor يضيف access token للطلبات المناسبة من session store، وAuthenticator يعالج `401` بعملية refresh مضبوطة. لازم نستثني login/refresh endpoints، نمنع infinite retry، وما نستخدمش نفس client بطريقة تعمل recursion/deadlock. عدة requests تلاقي 401 معًا: نعمل single-flight refresh أو Mutex مع recheck للتوكن بعد lock، ونبطل session فقط لو refresh فشل بشكل نهائي.

## Why it matters and how it works

Authenticate against server authority. Compare the token used in failed request with current token; if another caller already refreshed, retry with current. Otherwise serialize refresh and persist new credentials atomically. Bound follow-up attempts and clear session safely on invalid refresh. Keep credentials out of logs and backups according to threat model.

## Worked example

Conceptual Kotlin coordinator; real OkHttp Authenticator is synchronous, so integration must use a safe blocking boundary/independent refresh client and avoid main-thread work.

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class RefreshCoordinator(private val refresh: suspend () -> Token) {
    private val mutex = Mutex()
    suspend fun newToken(observed: Token, current: suspend () -> Token): Token =
        mutex.withLock {
            val now = current()
            if (now != observed) now else refresh()
        }
}
// Token, persistence and OkHttp Authenticator adapter are app-specific.
```

## Trade-offs and decision criteria

Authenticator is a natural 401 challenge point but runs under OkHttp’s synchronous API; avoid blocking the same exhausted dispatcher or recursive client. An application interceptor can attach a snapshot token, but proactive expiry checks still need race handling. Server session invalidation must be authoritative.

## Failure modes

Two concurrent 401s can both rotate refresh tokens, invalidating one another. An infinite 401 retry loops and drains battery. Logging Authorization headers leaks credentials. Calling the refresh endpoint through the same auth path can recurse.

## Production perspective

A banking app has a session repository with atomic token replacement and one refresh coordinator. Logout increments a session generation and cancels old calls; late refresh cannot resurrect a logged-out session. Tests force simultaneous 401s, refresh failure and logout race.

## Interview answer — short

“I attach tokens at a transport boundary, handle 401 with a bounded refresh path, and serialize refresh using a recheck under a lock. I avoid recursive clients, log no credentials and treat logout/session invalidation as authoritative.”

## Interview answer — structured

“The interceptor reads a current access token and adds it only to protected requests. On 401, an authenticator or coordinated layer compares the failed request’s token with the latest stored token; if another request refreshed it, it retries with that token. Otherwise one caller refreshes while peers wait, then credentials are replaced atomically. I bound retries, exclude the refresh endpoint from the same loop, and clear session only on authoritative invalidation. The OkHttp Authenticator API is synchronous, so I design its adapter and client threading carefully. Authenticator is a natural 401 challenge point but runs under OkHttp’s synchronous API; avoid blocking the same exhausted dispatcher or recursive client. An application interceptor can attach a snapshot token, but proactive expiry checks still need race handling.”

## Interview answer — deep senior

“Token refresh is a concurrency and security boundary. Multiple requests can receive 401 together; without a single-flight lock they may rotate one-time refresh credentials twice and invalidate the session. My coordinator acquires a mutex, rechecks the token inside it, refreshes once and stores the new pair atomically. It rejects a late result if logout or account switch changed session generation. The OkHttp challenge handler must not recursively call itself or block all available dispatch threads, and it must stop after a bounded follow-up count. I redact Authorization and refresh tokens from logs, use HTTPS and a defined local storage/backup threat model, and test simultaneous 401s, refresh rejection, cancellation and logout races. Compare the token used in failed request with current token; if another caller already refreshed, retry with current. Otherwise serialize refresh and persist new credentials atomically. Bound follow-up attempts and clear session safely on invalid refresh. Keep credentials out of logs and backups according to threat model. Two concurrent 401s can both rotate refresh tokens, invalidating one another. An infinite 401 retry loops and drains battery. Logging Authorization headers leaks credentials. Calling the refresh endpoint through the same auth path can recurse. A banking app has a session repository with atomic token replacement and one refresh coordinator.”

## Deep-dive talking points

Trace two 401s, token rotation, logout generation and synchronous Authenticator constraints.

## Follow-up questions

- [DAT-10](../dat-10/): Why recheck after lock? **Answer:** another caller may have refreshed while this one waited.
- [DAT-19](../dat-19/): What if refresh itself invalidates session? **Answer:** serialize and reject stale generation results.

## Self-check rubric

Can I prevent recursion and duplicate refresh, bound retries and protect logout state?

## References and reviewed-on date

- [OkHttp calls guide](https://lysine.dev/okhttp/features/calls/) — Authenticator follow-up requests.
- [Android security configuration](https://developer.android.com/privacy-and-security/security-config) — transport security.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
