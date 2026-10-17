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

## Concept and technical explanation

Testing network communication resilience against HTTP failures requires intercepting network traffic with high protocol fidelity without relying on volatile external staging servers. OkHttp's MockWebServer provides a local, in-process HTTP/HTTPS server that binds to a loopback socket on localhost. Rather than mocking Retrofit interfaces or OkHttp clients—which bypasses the entire networking serialization pipeline—MockWebServer exercises real network protocol negotiation, HTTP connection pooling, authentication interceptors, and JSON deserialization. Engineers simulate deterministic failure matrices by enqueueing mock responses with HTTP 4xx client errors (such as 401 Unauthorized or 404 Not Found), 5xx server outages (500 Internal Server Error, 503 Service Unavailable), malformed JSON payloads, and network socket timeouts or abrupt connection drops via SocketPolicy.

## Practical walkthrough (English)

Simulating 503 Service Unavailable and socket disconnects with MockWebServer:
```kotlin
class UserApiServiceTest {
    private val mockWebServer = MockWebServer()
    private lateinit var apiService: UserApiService

    @Before
    fun startServer() {
        mockWebServer.start()
        apiService = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
            .create(UserApiService::class.java)
    }

    @After
    fun stopServer() = mockWebServer.shutdown()

    @Test
    fun fetchUserProfile_server503Error_throwsHttpException() = runTest {
        // Enqueue an HTTP 503 Service Unavailable response with custom error payload
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(503)
                .setBody("{"error": "Database maintenance", "retry_after": 60}")
        )

        try {
            apiService.getUserProfile("user_42")
            fail("Expected HttpException was not thrown!")
        } catch (e: HttpException) {
            assertEquals(503, e.code())
        }

        // Verify outgoing request headers and path
        val recordedRequest = mockWebServer.takeRequest()
        assertEquals("/users/user_42", recordedRequest.path)
        assertEquals("GET", recordedRequest.method)
    }

    @Test
    fun fetchUserProfile_socketDisconnect_throwsIOException() = runTest {
        // Simulate physical network cable unplug or abrupt TCP reset
        mockWebServer.enqueue(MockResponse().setSocketPolicy(SocketPolicy.DISCONNECT_AT_START))

        try {
            apiService.getUserProfile("user_42")
            fail("Expected IOException on socket disconnect!")
        } catch (e: IOException) {
            // Handled cleanly as a transport-level network exception
            assertNotNull(e.message)
        }
    }
}
```

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

We test HTTP failures using MockWebServer, a local in-process HTTP server on localhost. Rather than mocking Retrofit interfaces, MockWebServer runs real OkHttp networking and JSON deserialization. We enqueue mock responses simulating 4xx client errors, 5xx server outages, malformed payloads, and transport-level connection cuts using SocketPolicy, while takeRequest asserts that outgoing HTTP headers, query parameters, and auth tokens match specifications.

## Interview answer — structured

Verifying application resilience in the face of unpredictable network failures is a primary requirement for production-grade mobile engineering.
A common architectural mistake is mocking the Retrofit API interface directly using MockK.
Mocking Retrofit bypasses OkHttp interceptors, authenticator refresh loops, SSL pinning configurations, and JSON serialization converters, leaving the entire networking pipeline untested.
The industry standard solution is OkHttp's MockWebServer.
MockWebServer launches a lightweight, real HTTP server on the local device loopback interface.
Retrofit is configured with the server's local URL, allowing network requests to traverse the complete production networking stack.
To test failure recovery, engineers enqueue predetermined MockResponse instances onto MockWebServer's queue.
We simulate 401 Unauthorized responses to verify that OkHttp Authenticator interceptors trigger token refresh workflows and retry the original request.
We enqueue 500 and 503 server errors to verify that repositories convert HTTP status codes into domain-friendly failure states and schedule exponential backoff retries.
We inject malformed or incomplete JSON to verify that Kotlinx Serialization exceptions are caught cleanly without crashing the UI.
Finally, using SocketPolicy.DISCONNECT_AT_START or SocketPolicy.NO_RESPONSE, we test how the application handles abrupt TCP disconnects, packet drops, and read timeouts.

## Interview answer — deep senior

Under the hood, MockWebServer operates by creating a genuine ServerSocket bound to an ephemeral loopback port on 127.0.0.1.
When Retrofit executes an HTTP network call, OkHttp's RealCall initiates a complete TCP three-way handshake (SYN, SYN-ACK, ACK) with MockWebServer's active listening socket.
The outbound request traverses OkHttp's full interceptor pipeline: RetryAndFollowUpInterceptor, BridgeInterceptor, CacheInterceptor, ConnectInterceptor, and CallServerInterceptor.
Every outgoing header, including Authorization Bearer tokens, User-Agent strings, and Gzip compression flags, is serialized into wire-format HTTP/1.1 or HTTP/2 frames.
MockWebServer reads the incoming byte stream, logs the parsed payload into an in-memory RecordedRequest queue, and matches it against enqueued MockResponse objects.
When testing socket failures, MockWebServer manipulates the underlying TCP socket channel directly.
Configuring SocketPolicy.DISCONNECT_AT_START forces MockWebServer to close the TCP socket immediately upon accepting the connection, causing OkHttp's SocketChannel to receive an RST packet and throw a raw java.io.IOException or SocketException.
Configuring SocketPolicy.NO_RESPONSE leaves the socket open without writing response bytes, verifying that OkHttp's readTimeoutMillis triggers properly and cleans up allocated connection resources.
Engineers use takeRequest() to assert that request paths, query parameters, custom headers, and JSON mutation bodies strictly adhere to API specifications before test assertions complete.
This rigorous testing approach provides 100% network stack fidelity without depending on external internet connections or flaky staging servers.

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
