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

طلبان متزامنان لتجديد التوكن (Refresh Token) أديا معاً إلى إبطال جلسة المستخدم وتسجيل خروجه بالخطأ. كيف تضبط تسلسل التجديد وتمنع هذا الخطأ؟

1. تشريح المشكلة (Why Concurrent Requests Invalidate the Session):
   - معظم خوادم الـ OAuth 2.0 الحديثة تطبق حماية **Refresh Token Rotation (RTR)**: عند استخدام Refresh Token، يُصدر السيرفر توكن جديد ويحرق (Revoke) التوكن القديم فوراً.
   - إذا أرسل التطبيق طلبين متزامنين بـ Access Token منتهي، يستقبل الاثنان `401 Unauthorized`.
   - إذا قام كلا الطلبين باستدعاء endpoint التجديد باستخدام نفس الـ Refresh Token القديم:
     * الطلب الأول يصل السيرفر وينجح ويحرق الـ Refresh Token القديم.
     * الطلب الثاني يصل بعده بـ 10 ميلي ثانية حاملاً نفس الـ Refresh Token القديم المحروق!
     * يكتشف السيرفر محاولة استخدام توكن ملغى، ويعتبر ذلك هجوماً واختراقاً (Breach Detection)، فيقوم فوراً بإبطال جميع توكنز المستخدم وحظر الجلسة!

2. المعمارية الصحيحة لتسلسل التجديد (Serialized Single-Flight Protocol):
   - **قفل تسلسلي إجباري (Serialized Mutex)**: لا يجوز لأكثر من خيط واحد التحدث إلى endpoint التجديد في نفس الوقت.
   - **فحص التوكن المزدوج (Double-Check under Lock)**: عند حصول أي خيط على القفل، يقارن التوكن الذي سبب الـ 401 بالتوكن المخزن حالياً. إذا كان التوكن قد تم تحديثه بالفعل بواسطة خيط سابق، يتخطى طلب التجديد ويعيد المحاولة بالتوكن الجديد فوراً.
   - **جيل الجلسة (Session Generation Counter)**: عداد يمنع أي استجابة تجديد متأخرة من إعادة تنشيط جلسة تم تسجيل خروجها عمداً بواسطة المستخدم.

## Practical walkthrough

التنفيذ البرمجي المانع لسباق تجديد التوكن في OkHttp Authenticator:
```kotlin
class ThreadSafeAuthenticator @Inject constructor(
    private val sessionStore: SessionStore,
    private val refreshApi: DedicatedRefreshClient
) : Authenticator {

    private val lock = Any()

    override fun authenticate(route: Route?, response: Response): Request? {
        // 1. استخراج التوكن الذي فشل في هذا الطلب المحدد:
        val failedToken = response.request.header("Authorization")?.removePrefix("Bearer ")

        synchronized(lock) {
            val currentToken = sessionStore.getAccessToken()

            // 2. الفحص المزدوج الحاسم:
            // إذا كان التوكن الحالي يختلف عن التوكن الذي فشل، فهذا يعني أن خيطاً آخر
            // قد أكمل التجديد بنجاح أثناء انتظار هذا الخيط في الطابور!
            if (currentToken != null && currentToken != failedToken) {
                // أعد المحاولة مباشرة بالتوكن الجديد بدون استدعاء السيرفر:
                return response.request.newBuilder()
                    .header("Authorization", "Bearer $currentToken")
                    .build()
            }

            // 3. إذا كنا الخيط الأول: استدعاء التجديد مرة واحدة فقط:
            val refreshToken = sessionStore.getRefreshToken() ?: return null
            val refreshResult = refreshApi.executeRefreshToken(refreshToken)

            return if (refreshResult.isSuccessful && refreshResult.tokens != null) {
                // حفظ التوكن الجديد و Refresh Token الجديد ذرياً:
                sessionStore.updateTokens(refreshResult.tokens.access, refreshResult.tokens.refresh)
                
                response.request.newBuilder()
                    .header("Authorization", "Bearer ${refreshResult.tokens.access}")
                    .build()
            } else {
                // فشل حقيقي في التجديد -> مسح الجلسة وإلغاء المحاولات:
                sessionStore.clearSession()
                null
            }
        }
    }
}
```

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

## Trade-offs and decision criteria

Mutex is easy to reason about but makes waiters share refresh latency. An in-flight Deferred can reduce lock hold time but complicates cancellation ownership. The backend still determines token validity and rotation semantics.

## Failure modes

A refresh call cancelled by one screen must not necessarily cancel the session’s shared refresh for other requests. A late pair saved after logout resurrects credentials. Clearing session on a transient offline error logs users out unnecessarily.

## Production perspective

A multi-tab banking app coordinates refresh per signed-in account, rechecks token after lock, and stores new credentials only if session generation matches. Tests force simultaneous 401s, refresh 5xx, permanent invalid refresh and logout during refresh.

## Interview answer — short

Prevent dual refresh invalidation by strictly serializing refresh calls behind a Mutex or synchronized lock with double-checked token validation. When a thread acquires the lock, it checks if the active token was already updated by a preceding thread. If updated, it replays immediately without calling the refresh endpoint.

## Interview answer — structured

Under modern OAuth 2.0 Refresh Token Rotation (RTR), using an expired refresh token triggers backend breach detection, instantly revoking all active client sessions. When two concurrent requests receive 401s, both attempting to refresh using the same stale token inevitably invalidates the session.

To serialize refresh correctly and prevent false logouts.

First, with Lock Funneling, wrap the refresh block inside a thread-safe lock (`synchronized(lock)` in OkHttp Authenticator or a coroutine `Mutex`). Next, with The Double-Check Token Protocol, before making any network call, extract the `failedToken` from the triggering request header and compare it to `sessionStore.getAccessToken()`.
If `currentToken != failedToken`, another thread already executed the refresh while this thread was waiting on the lock. **Skip the refresh call entirely** and retry the request using `currentToken`. If `currentToken == failedToken`, this thread is the first to arrive. Execute exactly one refresh network request.
Finally, with Atomic Session Mutation, save both the new access token and the rotated refresh token atomically before releasing the lock.


## Interview answer — deep senior

A critical edge case is the **Stale Response Race Across Logout**:

Consider this sequence.

First, thread A fires a token refresh request. Next, while the refresh is in flight on the network, the user explicitly taps 'Log Out'. The app clears credentials from storage.
Finally, thread A's refresh network request succeeds 1 second later and writes fresh tokens back into storage, accidentally resurrecting a logged-out session!

To prevent this, implement a **Session Generation Counter**.

First, maintain an atomic `sessionGeneration: Long` that increments on every explicit logout or login. Next, capture the generation ID before initiating the refresh.
Finally, before committing new tokens to storage, verify that `currentGeneration == capturedGeneration`. If mismatched, discard the newly fetched tokens.


## How to answer in the interview

- **Why:** Rotating tokens are invalidated by duplicate refresh calls.
- **How:** Lock by session, recheck inside lock, commit pair conditionally.
- **Trade-offs:** Separate transient network error from permanent invalid grant.
- **Failure cases:** Second rotation, recursive Authenticator, post-logout resurrection.
- **Production solution:** Barrier-based concurrent-401 test with one refresh call.

## Deep-dive talking points

Draw token observed/current comparison, session generation and refresh failure categories.

## Follow-up questions

- **Interviewer:** "What is Refresh Token Rotation (RTR)?"
  **Answer:** "An OAuth 2.0 security mechanism where the server issues a new refresh token and revokes the old one on every single refresh, preventing replay attacks."

- **Interviewer:** "Why must the refresh HTTP client be independent of the primary OkHttpClient?"
  **Answer:** "If the refresh client shares the primary client's Authenticator, an unexpected 401 on the refresh endpoint triggers recursive authentication calls, causing a deadlock."

## Self-check rubric

Can I force two 401s, show one rotation, preserve logout and distinguish offline from invalid session?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — Mutex coordination.
- [OkHttp calls guide](https://lysine.dev/okhttp/features/calls/) — 401 authenticator follow-up.

Technically reviewed against primary documentation on 2026-10-13.
