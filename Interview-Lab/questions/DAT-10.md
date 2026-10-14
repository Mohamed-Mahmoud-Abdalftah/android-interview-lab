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

كيف تتجنب سباق طلبات تجديد التوكن المتزامنة (Concurrent Refresh-Token Races)؟

1. سيناريو الكارثة في التطبيقات متعددة الخيوط (The Race Condition):
   - عند فتح التطبيق، يطلق الـ Dashboard ثلاثة طلبات متزامنة في نفس اللحظة: جلب الملف الشخصي، جلب الإشعارات، وجلب السلة.
   - انتهت صلاحية الـ Access Token، فتعود الطلبات الثلاثة بـ `401 Unauthorized` في نفس الجزء من الثانية!
   - إذا قامت كل خيط (Thread) باستدعاء سيرفر التجديد بـ Refresh Token:
     * السيرفر يدعم أمان Refresh Token Rotation (RTR): أول طلب ينجح ويحرق الـ Refresh Token القديم.
     * الطلب الثاني والثالث يصلان بالـ Refresh Token القديم الذي تم حرقه!
     * يعتبر السيرفر ذلك هجوماً واختراقاً أمنياً (Token Theft)، فيقوم بحظر حساب المستخدم وحذف جميع الجلسات وإجباره على تسجيل الدخول!

2. الحل المعماري الصارم (Single-Flight Lock & Double-Check Protocol):
   - **قفل التزامن (Mutex / Synchronized)**: خيط واحد فقط يُسمح له بطلب التجديد في أي لحظة.
   - **فحص التوكن المزدوج (Double-Check)**: عند دخول الخيط الثاني بعد انتهاء الخيط الأول، يقارن التوكن الفاشل بالتوكن الحالي في الذاكرة. إذا وجده قد تغير، لا يتصل بالسيرفر! بل يعيد الطلب الأصلي بالتوكن الجديد فوراً.
   - **Single-Flight Deferred**: أو تعليق الطلبات الأخرى على `Deferred` ينتظر اكتمال الطلب الأول ويستخدم نتيجته.

## Practical walkthrough

تنفيذ بروتوكول Single-Flight مع فحص التوكن المزدوج لمنع سباق التجديد:
```kotlin
class SafeTokenManager @Inject constructor(
    private val tokenStorage: SecureTokenStorage,
    private val refreshApi: RefreshApi
) {
    private val refreshMutex = Mutex()

    suspend fun getOrRefreshValidToken(failedToken: String?): Result<String> {
        // قفل متزامن يمنع أي خيط آخر من بدء طلب تجديد جديد:
        refreshMutex.withLock {
            val currentToken = tokenStorage.getAccessToken()
            
            // الفحص المزدوج الحاسم (Double-Check):
            // لو خيط آخر قام بالتجديد أثناء انتظار هذا الخيط في الطابور:
            if (currentToken != null && currentToken != failedToken) {
                // التوكن تم تجديده بالفعل! نرجع التوكن الجديد فوراً بدون لمس السيرفر:
                return Result.success(currentToken)
            }

            // إذا كنا نحن الخيط الأول: ننفذ طلب تجديد واحد فقط (Single-Flight):
            val refreshToken = tokenStorage.getRefreshToken() ?: return Result.failure(SessionExpiredException)
            
            return try {
                val response = refreshApi.refreshToken(refreshToken)
                tokenStorage.saveTokens(response.accessToken, response.newRefreshToken)
                Result.success(response.accessToken)
            } catch (e: Exception) {
                tokenStorage.clearSession()
                Result.failure(e)
            }
        }
    }
}
```

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

## Trade-offs and decision criteria

Mutex simplifies correctness but holds waiters during network refresh; use a session-level Deferred/single-flight if many callers should await one refresh without holding a lock. A server refresh-token family/rotation policy matters. Do not overwrite credentials after logout.

## Failure modes

A per-request Mutex protects nothing across two requests. Refreshing without recheck duplicates rotation. A stale refresh response can resurrect a logged-out account unless session generation is checked before commit.

## Production perspective

A session repository stores tokens with generation, serializes refresh and replaces the pair in one protected step. The backend invalidates rotated credentials per its policy. Concurrency tests start two 401s simultaneously and assert one refresh and both retries use the new token.

## Interview answer — short

Avoid concurrent refresh-token races using a synchronized single-flight lock with a double-check protocol. When multiple concurrent requests hit 401 simultaneously, serialize them behind a Mutex. The first thread refreshes tokens; subsequent threads detect that the active token already changed and replay immediately without calling the refresh API.

## Interview answer — structured

When an app launches, multiple parallel network calls (profile, notifications, feed) often receive `401 Unauthorized` simultaneously. If each thread independently issues a refresh call under Refresh Token Rotation (RTR), the server treats subsequent calls using the old single-use token as credential theft, forcibly revoking the user's session.

The industry-standard solution is the **Single-Flight Lock with Double-Check Protocol**.

First, with Synchronized Lock, all 401 handling is funneled through a shared lock (`Mutex` in coroutines, or `synchronized` in OkHttp Authenticator). Next, with Double-Check Verification, when a thread acquires the lock, it compares the token that triggered its 401 against the current in-memory token. If another thread already completed a refresh while this thread was waiting, `currentToken != failedToken`. The thread immediately skips the refresh API call and retries with the new token.
Finally, an Atomic Session Update is the winning thread executes exactly one refresh call, atomically saving both the new access token and the new refresh token to secure storage before releasing the lock.


## Interview answer — deep senior

In modern asynchronous architectures using Kotlin Coroutines, senior teams often implement this using **`CompletableDeferred` or `SharedFlow` single-flight coordination**.

Instead of blocking JVM threads with `synchronized`, the token manager maintains an atomic reference to an active refresh job: `private val activeRefresh = AtomicReference<Deferred<String>?>()`. When a coroutine hits 401, it inspects the atomic reference. If an active job exists, it simply awaits the existing `Deferred`. If no job exists, it creates a new `async` job, atomically swaps it into the reference, and notifies all awaiting coroutines upon completion, clearing the reference in a `finally` block. This yields 100% non-blocking coroutine safety.


## How to answer in the interview

- **Why:** Multiple expired requests must share one logical rotation.
- **How:** Lock, recheck token inside lock, refresh once, persist pair conditionally.
- **Trade-offs:** Coordinate waiters without coupling to a cancelled screen scope.
- **Failure cases:** Double rotation, stale post-logout write, refresh deadlock.
- **Production solution:** Deterministic concurrent-401 and logout-race tests.

## Deep-dive talking points

Draw two callers racing, recheck-after-lock and logout generation safeguards.

## Follow-up questions

- **Interviewer:** "Why shouldn't you fire refresh-token requests in an OkHttp Interceptor instead of Authenticator?"
  **Answer:** "Interceptors do not naturally serialize 401 retries; Authenticator was designed specifically by OkHttp to manage retries and handle concurrent 401 responses cleanly."

- **Interviewer:** "What happens if the single refresh call fails with network timeout?"
  **Answer:** "Release the lock and let callers retry transiently, but do NOT clear user session credentials on transient network timeouts—only on explicit 400/401 refresh responses."

## Self-check rubric

Can I prove one refresh, atomic pair save, bounded retries and no logout resurrection?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — Mutex coordination.
- [OkHttp calls guide](https://lysine.dev/okhttp/features/calls/) — authentication follow-up.

Technically reviewed against primary documentation on 2026-10-13.
