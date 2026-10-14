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

HTTP methods define operation semantics: GET is safe and idempotent, PUT/DELETE are idempotent, POST is non-idempotent. Idempotency guarantees that executing a request multiple times produces the identical server state as executing it once, which is vital on flaky mobile networks to prevent duplicate payments or orders via client-generated Idempotency Keys.

## Interview answer — structured

Understanding HTTP methods and idempotency is essential for designing resilient mobile APIs.

First, **Method Semantics & Idempotency**. Next, an operation is **idempotent** if making $N$ identical requests has the exact same side-effect on the server as making 1 request ($f(f(x)) = f(x)$).
`GET`, `HEAD`, `OPTIONS` are safe (read-only) and idempotent. `PUT` (full replacement) and `DELETE` (resource removal) are idempotent. Calling `DELETE /users/42` ten times results in user 42 being deleted, regardless of whether subsequent responses return 204 or 404.
`POST` is **non-idempotent**: calling `POST /orders` five times creates five distinct orders and charges the user five times. Finally, with The Mobile Reality of Flaky Networks, on cellular networks, connection drops frequently occur *after* the server processes a `POST` write but *before* the client receives the `200 OK` response. If the client retries blindly, duplicate operations occur. Production mobile apps prevent this by attaching a deterministic **`Idempotency-Key` UUID** in request headers, allowing the server to recognize duplicate submissions and return cached receipts without re-executing writes.


## Interview answer — deep senior

From a protocol perspective, senior engineers handle status codes with explicit architectural responses.

First, 401 Unauthorized` vs. `403 Forbidden is a `401` indicates authentication failure—the OkHttp `Authenticator` should intercept this, pause pending requests, perform a single-flight token refresh, and retry the request. A `403` indicates authorization failure (the user is authenticated, but lacks admin privileges)—**never retry a 403 with a token refresh**, as this triggers an infinite retry loop; navigate to an error state or notify the user. Finally, with 429 Too Many Requests, inspect the `Retry-After` header. If the server says `Retry-After: 30`, suspend coroutine execution for 30 seconds rather than retrying immediately with exponential backoff, respecting server capacity and preventing IP bans.


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
