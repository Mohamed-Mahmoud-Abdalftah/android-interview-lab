---
id: "DAT-02"
question: "What are HTTP methods, common status codes, and idempotency?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "A"
phase: 3
priority: "P1"
order: 259
editorial_status: "reviewed"
---

# DAT-02

## Original interview question

What are HTTP methods, common status codes, and idempotency?

## What the interviewer evaluates

Explain method semantics, common status classes and why idempotency is a server contract.

## Concept and technical explanation

HTTP request methods and response status codes define the standardized semantic protocol for client-server communication:
- HTTP Methods & Idempotency: An operation is idempotent if making multiple identical requests leaves the server in the identical state as making a single request.
  * GET: Retrieves resource representation; safe and idempotent.
  * PUT: Completely replaces a resource at a known URI; idempotent.
  * DELETE: Removes a resource; idempotent (subsequent requests still result in the resource being absent, even if returning 404).
  * POST: Submits data to process, creating new resources; non-idempotent.
  * PATCH: Applies partial modifications; generally non-idempotent unless designed with strict semantics.
- Status Code Taxonomy:
  * 2xx (Success): 200 OK, 201 Created (resource instantiated), 204 No Content (action completed without body).
  * 3xx (Redirection): 304 Not Modified (conditional caching via ETag/If-None-Match).
  * 4xx (Client Error): 400 Bad Request, 401 Unauthorized (unauthenticated/token expired), 403 Forbidden (authenticated but lacking permissions), 404 Not Found, 409 Conflict, 429 Too Many Requests (rate limited).
  * 5xx (Server Error): 500 Internal Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout.
- Idempotency Keys: Mobile apps must send unique client-generated UUIDs in headers (e.g., X-Idempotency-Key) on POST requests to safely retry network timeouts without duplicating financial transactions.

## Practical walkthrough (English)

Implementing idempotent safe retries and status code parsing in Retrofit/OkHttp:
```kotlin
// Interceptor injecting unique Idempotency Keys for state-changing POST requests
class IdempotencyInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()
        if (original.method.equals("POST", ignoreCase = true) && original.header("X-Idempotency-Key") == null) {
            val idempotentRequest = original.newBuilder()
                .header("X-Idempotency-Key", UUID.randomUUID().toString())
                .build()
            return chain.proceed(idempotentRequest)
        }
        return chain.proceed(original)
    }
}

// Handling HTTP status codes in repository error boundaries
suspend fun <T> safeApiCall(apiCall: suspend () -> T): Result<T> = try {
    Result.success(apiCall())
} catch (e: HttpException) {
    when (e.code()) {
        401 -> Result.failure(AuthExpiredException("Session token invalid", e))
        429 -> Result.failure(RateLimitedException("Rate limit reached, retry later", e))
        in 500..599 -> Result.failure(ServerUnavailableException("Server outage", e))
        else -> Result.failure(GenericNetworkException("HTTP error ${e.code()}", e))
    }
}
```

## Explanation in Arabic

ما هي دوال HTTP (Methods)، وأكواد الحالة الشائعة (Status Codes)، وما هو مبدأ الـ Idempotency الحرج في تطبيقات الهاتف؟

1. دوال HTTP ودلالاتها المعمارية (HTTP Methods Semantics):
   - **GET**: قراءة الموارد فقط. آمنة (Safe) ولا يجب أن تحدث أي تغيير في حالة السيرفر، وقابلة للتخزين المؤقت (Cacheable).
   - **POST**: إرسال بيانات لإنشاء مورد جديد أو تنفيذ عملية غير قابلة للتكرار (مثل خصم رصيد أو طلب شحن). **ليست آمنة وليست Idempotent**.
   - **PUT**: استبدال مورد موجود بالكامل (Replace/Upsert). دالة **Idempotent**.
   - **PATCH**: تحديث جزئي لبعض حقول المورد.
   - **DELETE**: حذف مورد محدد. دالة **Idempotent**.

2. ما هو الـ Idempotency (خاصية التكرار الآمن) ولماذا هي حرجة للموبايل؟
   - **التعريف**: العملية تعتبر Idempotent إذا كان تكرار إرسال نفس الطلب $N$ مرة ينتج عنه نفس الأثر تماماً على السيرفر كإرساله مرة واحدة فقط ($f(f(x)) = f(x)$).
   - **أهميتها في الموبايل**: شبكة الموبايل تنقطع باستمرار (Flaky Networks). إذا أرسل التطبيق طلب `POST /checkout` وانقطع الاتصال قبل وصول الرد، لا يعلم التطبيق هل السيرفر خصم المبلغ أم لا! إذا أعاد التطبيق المحاولة بدون **Idempotency Key**، فقد يُخصم من المستخدم مرتين!

3. أكواد الحالة الأكثر أهمية في Android:
   - `200 OK` / `201 Created`: نجاح العملية.
   - `401 Unauthorized`: التوكن منتهي أو غير صالح (يتطلب تجديد التوكن عبر Refresh Token).
   - `403 Forbidden`: المستخدم مسجل لكنه لا يملك صلاحية هذا المورد (لا تحاول تجديد التوكن!).
   - `404 Not Found`: المورد غير موجود.
   - `409 Conflict`: تعارض في البيانات (مثل تعديل ملف تم تعديله من جهاز آخر - ETag Mismatch).
   - `429 Too Many Requests`: تجاوز حد الطلبات (يتطلب احترام ترويسة `Retry-After`).
   - `500/502/503`: أخطاء في السيرفر (تتطلب إعادة المحاولة مع Exponential Backoff).

## Practical walkthrough

إرسال طلب POST مالي مع Idempotency Key لضمان عدم الخصم المزدوج عند انقطاع الشبكة:
```kotlin
class PaymentRepositoryImpl @Inject constructor(
    private val paymentApi: PaymentApiService,
    private val pendingTransactionsDao: PendingTransactionsDao
) : PaymentRepository {
    override suspend fun chargeOrder(orderId: String, amount: Money): Result<PaymentReceipt> {
        // 1. توليد مفتاح تكرار آمن (Idempotency Key) وحفظه محلياً في Room أولاً:
        val idempotencyKey = "pay_${orderId}_${amount.cents}"
        pendingTransactionsDao.recordPending(idempotencyKey, orderId)
        
        return runCatching {
            // 2. إرسال الطلب في الترويسة:
            // إذا انقطعت الشبكة وأعاد OkHttp أو WorkManager الإرسال،
            // يعرف السيرفر هذا المفتاح ويعيد نفس الإيصال السابق دون خصم جديد!
            paymentApi.processCharge(
                idempotencyKey = idempotencyKey,
                request = ChargeRequest(orderId, amount.cents)
            )
        }.onSuccess {
            pendingTransactionsDao.markConfirmed(idempotencyKey)
        }
    }
}
```

## Why it matters and how it works

HTTP method semantics guide retry safety, but API implementations must honor them. A client cannot infer whether a timed-out POST reached the server. A stable idempotency key, payload matching, server deduplication and status lookup make logical retries safer; `Retry-After` and rate limits shape timing.

## Worked example

Conceptual Kotlin API interface. `ChargeResponse` is an app-defined DTO and the configured Retrofit converter is omitted; the backend must document key retention and duplicate handling.

```kotlin
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST

data class ChargeRequest(val amountCents: Long)
interface PaymentsApi {
    @POST("charges")
    suspend fun charge(
        @Header("Idempotency-Key") key: String,
        @Body body: ChargeRequest,
    ): ChargeResponse
}
```

## Trade-offs and decision criteria

A method’s standard semantics are a starting point, not proof of a specific backend guarantee. POST with a stable server-enforced key can be logically idempotent; GET that changes state violates expectations and creates caching/retry risk. Always read the API contract.

## Failure modes

Retrying a timed-out payment with a new key can charge twice. Treating every 4xx as transient wastes requests; treating 429 as immediate retry worsens throttling. An HTTP 200 can still contain a domain-level rejection requiring validation.

## Production perspective

A payment client persists a stable operation key before POST, marks outcome Pending after timeout and queries status. A feed GET retries transient 5xx with capped backoff and respects server Retry-After where specified.

## Interview answer — short

HTTP methods define semantic actions where GET, PUT, and DELETE are idempotent, whereas POST creates new state and is non-idempotent. Status codes are categorized into 2xx successes, 3xx redirects, 4xx client errors like 401 auth or 429 throttling, and 5xx server outages. For non-idempotent financial actions, unique idempotency keys guarantee safe retry behavior.

## Interview answer — structured

Understanding HTTP semantics, status codes, and idempotency is fundamental for designing fault-tolerant Android networking.
First, idempotency means that executing a request multiple times yields the same server state as a single invocation. GET, PUT, and DELETE are idempotent by specification; retrying them after a network timeout is inherently safe. POST is non-idempotent because multiple calls create duplicate records or charges.
Second, status codes provide clear contractual classifications. 2xx codes indicate success, 304 enables efficient caching, 4xx signals client-side issues like expired credentials on 401 or rate limits on 429, and 5xx reflects server-side infrastructure failures.
Third, in mobile environments with flaky connections, retrying a failed POST request risks double charges. Senior engineers implement client-generated idempotency keys in request headers, allowing backend services to deduplicate retried operations safely.

## Interview answer — deep senior

In production mobile architecture, misunderstanding HTTP semantics and idempotency leads directly to data corruption and duplicate transactions.
When an Android device loses cellular connectivity right after sending a POST payment request, the client cannot know whether the packet was dropped before reaching the server or whether the server processed the transaction and the response was dropped on the return path.
Blindly retrying a non-idempotent POST request causes duplicate charges. To solve this, we generate a deterministic UUID idempotency key attached as an X-Idempotency-Key header stored in Room alongside the pending transaction.
If network failure occurs, WorkManager re-executes the exact same request with the identical key. The backend detects the cached key in Redis and returns the original transaction response without re-executing business logic.
Furthermore, handling status codes requires precise distinction between retryable and non-retryable errors. A 503 Service Unavailable with a Retry-After header or a 504 Gateway Timeout warrants exponential backoff with jitter.
Conversely, a 400 Bad Request or 403 Forbidden is fatal and must fail immediately without wasting radio resources.
Handling 401 Unauthorized triggers our OkHttp Authenticator to refresh JWT tokens, while a 429 Too Many Requests halts automated pollers to prevent IP throttling.
Additionally, we design custom network interceptors that parse cache headers and synthesize standardized domain error wrappers, ensuring that network timeouts or unexpected payload mutations never propagate unhandled into our presentation state machines.

## How to answer in the interview

- **Why:** Retry safety depends on operation semantics, not just a status number.
- **How:** Define common methods and statuses, then explain idempotent intended effect.
- **Trade-offs:** Use key-backed POST retries only under documented server rules.
- **Failure cases:** Treating timeout as failed payment or retrying all 4xx.
- **Production solution:** Persist operation ID, honor `Retry-After`, and reconcile uncertain writes.

## Deep-dive talking points

Explain safe/idempotent distinction, timeout uncertainty, server deduplication and retry classification.

## Follow-up questions

- **Interviewer:** "Does HTTP status code 500 mean the write failed on the server?"
  **Answer:** "Not necessarily! The server could have written to the database and crashed during response serialization. Client retries must use idempotency keys."

- **Interviewer:** "Can `PATCH` be idempotent?"
  **Answer:** "It depends on the payload: `PATCH { "age": 30 }` is idempotent; `PATCH { "incrementAge": 1 }` is non-idempotent."

## Self-check rubric

Can I state method semantics, classify key status codes and design one safe write retry?

## References and reviewed-on date

- [HTTP Semantics RFC 9110](https://httpwg.org/specs/rfc9110.html) — method and status semantics.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — retryable writes.

Technically reviewed against primary documentation on 2026-10-13.
