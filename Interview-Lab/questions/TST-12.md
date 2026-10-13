---
id: "TST-12"
question: "How do you test HTTP failures with MockWebServer or equivalent?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 407
editorial_status: "reviewed"
---

# TST-12

## Original interview question

How do you test HTTP failures with MockWebServer or equivalent?

## What the interviewer evaluates

- Controlled HTTP errors, latency and disconnects.
- Distinguishing client mapping from server-side guarantees.

## Explanation in Arabic

كيف تختبر سيناريوهات فشل الشبكة (HTTP Failures, Timeouts, Malformed JSON) باحترافية باستخدام `MockWebServer`؟

1. ما هو `MockWebServer`؟
   - خادم HTTP حقيقي وخفيف يعمل محلياً داخل جهازك أثناء الاختبار (من مكتبة Square OkHttp).
   - يتيح لك اختبار طبقة الشبكة بالكامل (OkHttp, Retrofit, Converters, Interceptors, Repositories) عبر شبكة حقيقية مشفرة محلياً دون الحاجة لاتصال خارجي بالإنترنت!

2. سيناريوهات الفشل التي يجب اختبارها:
   - **أخطاء الخادم (HTTP 500, 502, 503)**: التحقق من أن التطبيق يعرض رسالة خطأ ملائمة للمستخدم ولا ينهار.
   - **أخطاء المصادقة (HTTP 401 Unauthorized)**: التحقق من أن الـ Authenticator يحاول تجديد التوكن أو توجيه المستخدم لشاشة الدخول.
   - **الاستجابات المشوهة (Malformed / Broken JSON)**: إرجاع نص JSON مكسور والتحقق من التقاط خطأ الـ `JsonDataException` بسلاسة.
   - **انقطاع الشبكة ومهلة الانتظار (Socket Timeouts)**: محاكاة انقطاع الاتصال المفاجئ عبر `SocketPolicy.NO_RESPONSE` أو `SocketPolicy.DISCONNECT_AT_START`.

3. فحص الطلبات الصادرة (Verifying Outgoing Requests):
   - استخدام `mockWebServer.takeRequest()` للتحقق من أن التطبيق أرسل الـ Headers الصحيحة (مثل `Authorization: Bearer ...`) والـ Query Parameters والـ Body المطلوب.

## Practical walkthrough

اختبار أخطاء الشبكة والـ 401 والتأكد من هيدرز الطلب الصادر عبر MockWebServer:
```kotlin
class NetworkRepositoryTest {
    private lateinit var server: MockWebServer
    private lateinit var api: UserApiService

    @Before
    fun setup() {
        server = MockWebServer()
        server.start()
        api = Retrofit.Builder()
            .baseUrl(server.url("/"))
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
            .create(UserApiService::class.java)
    }

    @Test
    fun `server 500 internal error returns failure result without crashing`() = runTest {
        // 1. محاكاة استجابة خطأ 500 من الخادم:
        server.enqueue(MockResponse().setResponseCode(500).setBody("Internal Server Error"))

        val repository = UserRepositoryImpl(api)
        val result = repository.fetchUser("123")

        assertTrue(result.isFailure)
    }

    @Test
    fun `verify request outgoing headers and path`() = runTest {
        server.enqueue(MockResponse().setResponseCode(200).setBody("{\"id\":\"123\",\"name\":\"Ali\"}"))

        val repository = UserRepositoryImpl(api)
        repository.fetchUser("123")

        // 2. فحص تفاصيل الطلب الصادر من التطبيق:
        val recordedRequest = server.takeRequest()
        assertEquals("/users/123", recordedRequest.path)
        assertEquals("GET", recordedRequest.method)
    }

    @After
    fun tearDown() = server.shutdown()
}
```

## Why it matters and how it works

A local scripted server receives actual HTTP requests from the client stack, so serialization, interceptors, auth and timeout handling are exercised. Test response bodies and transport failures separately; a timeout after request arrival leaves remote outcome unknown.

## Worked example

Enqueue a 200 response whose body is cut off after server recorded a payment operation. Assert the Android client keeps the same operation ID, reports Unknown and performs status lookup rather than creating a new charge. Also assert Authorization is absent from test logs.

## Trade-offs and decision criteria

Local servers are deterministic and fast but do not reproduce TLS, CDN, backend transactions or provider semantics unless configured. Use backend contract tests and staging drills for those gaps.

## Failure modes

A test mocks Retrofit interface directly and misses an interceptor that retries POST automatically. A MockWebServer test observes actual request count and idempotency header. Distinguish 4xx permanent errors from retryable 5xx under API contract.

## Production perspective

CI covers auth expiry, rate limit, malformed responses, lost body and slow network with a local server. Provider sandbox tests validate unknown-outcome handling across system boundaries.

## Interview answer — short

Test network failures using Square's MockWebServer by enqueuing MockResponse instances with error codes (401, 500), malformed JSON payloads, or SocketPolicy.NO_RESPONSE. Assert that repositories handle failures gracefully, and verify outgoing headers and payload bodies using takeRequest().

## Interview answer — structured

MockWebServer enables hermetic, end-to-end testing of the complete networking stack (OkHttp, Retrofit, interceptors, and serializers) on the local JVM:

1. **Simulating HTTP Error Statuses**:
   - Enqueue explicit response codes: `MockResponse().setResponseCode(500).setBody("Internal Server Error")`.
   - Enqueue `401 Unauthorized` to test whether token refresh interceptors intercept the failure, refresh credentials, and replay the original request.

2. **Simulating Network Timeouts & Abrupt Drops**:
   - Configure low-level socket policies: `MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE)` simulates gateway timeouts, while `SocketPolicy.DISCONNECT_AFTER_REQUEST` tests sudden socket terminations mid-handshake.

3. **Malformed & Incomplete Payloads**:
   - Enqueue truncated or malformed JSON (`MockResponse().setBody("{\"id\": 123, ")`) to verify that JSON deserialization errors (`JsonEncodingException`) are caught and mapped into domain network errors rather than unhandled app crashes.

4. **Asserting Outgoing Requests (`takeRequest()`)**:
   - Inspect `server.takeRequest()` to assert that outgoing authorization tokens, API keys, User-Agent strings, and JSON request bodies strictly match backend contract expectations.

## Interview answer — deep senior

From an enterprise testing architecture perspective, MockWebServer provides deterministic replay capabilities:

1. **Dispatcher for Multi-Endpoint Scenarios**: Instead of using sequential `enqueue()`, configure a custom `Dispatcher`. The dispatcher inspects `request.path` and routes responses dynamically (e.g. returning 200 for `/auth/refresh` while returning 401 for `/v1/orders`), enabling complex multi-request concurrency testing.

2. **Simulating Throttling and Slow Radios**: Test loading spinners and UI cancellation by simulating slow cellular networks using `MockResponse().throttleBody(1024, 1, TimeUnit.SECONDS)`. This streams 1KB per second, giving tests time to verify progress bars and cancel requests mid-stream.

3. **Port Collisions in Parallel CI**: Never hardcode port numbers (e.g. `localhost:8080`). Invoke `server.start()` without parameters; MockWebServer automatically binds to an ephemeral open operating system port, preventing port collisions when multiple Gradle test workers run concurrently.

## How to answer in the interview

- **Why:** timeout, truncated response and HTTP rejection imply different outcomes.
- **How:** script each server response and inspect emitted request identity.
- **Trade-off:** controlled HTTP integration versus real backend guarantee.
- **Failure case:** fake timeout occurs before a simulated server commit.
- **Production solution:** after-commit fault test plus backend concurrency verification.

## Deep-dive talking points

Prompt for transport timing, real interceptor path, stable ID, status mapping and backend contract gap.

## Follow-up questions

- **Interviewer:** "What is the difference between enqueue() and setDispatcher() in MockWebServer?"
  **Answer:** "enqueue() queues responses FIFO regardless of request path; setDispatcher() inspects the request URI and headers to return specific responses dynamically."

- **Interviewer:** "Why should you avoid hardcoding port numbers with MockWebServer?"
  **Answer:** "Hardcoded ports cause BindException collisions when multiple tests run in parallel or when previous server instances fail to release sockets immediately."

## Self-check rubric

Script HTTP status, truncated body and disconnect cases; inspect the emitted request and resulting state. For a lost payment reply, prove the client keeps the operation ID and queries status; say what only the backend can prove.

## References and reviewed-on date

- [OkHttp MockWebServer](https://github.com/square/okhttp/blob/master/README.md) — OkHttp official project documentation.
- [Android network testing](https://developer.android.com/training/testing) — integration test guidance.

Technically reviewed against primary documentation on 2026-10-13.
