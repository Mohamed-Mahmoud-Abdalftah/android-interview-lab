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

`GET` قراءة safe غالبًا، `PUT` يستبدل resource و`DELETE` لهما semantics idempotent في HTTP، و`POST` غالبًا ينشئ action ومش آمن نعيده بلا عقد. `2xx` نجاح، `3xx` redirect، `4xx` مشكلة في الطلب/صلاحية، `5xx` فشل server؛ `401` auth، `403` منع، `404` غير موجود، `409` conflict، `429` rate limit. idempotency معناها تكرار نفس العملية له نفس الأثر المقصود، مش إن الشبكة نفذتها مرة واحدة.

## Why it matters and how it works

HTTP method semantics guide retry safety, but API implementations must honor them. A client cannot infer whether a timed-out POST reached the server. A stable idempotency key, payload matching, server deduplication and status lookup make logical retries safer; `Retry-After` and rate limits shape timing.

## Worked example

Conceptual Kotlin API interface; backend must document key retention and duplicate handling.

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

“HTTP methods describe intent; GET is safe, PUT and DELETE are idempotent by semantics, while POST often is not. Status codes classify outcomes, but timeout is ambiguous. I retry writes only under a documented server idempotency contract.”

## Interview answer — structured

“I explain both protocol and business meaning. GET is a read; PUT sets a resource representation; DELETE removes one; POST commonly creates or triggers work. 2xx succeeds, 4xx usually needs client action, 5xx may be transient, and 429 asks us to slow down. Idempotency means repeating the same request has the same intended effect, not that only one packet traversed the network. For payments I use a stable key backed by server deduplication and reconcile uncertain outcomes rather than blindly resending. Always read the API contract.”

## Interview answer — deep senior

“A robust retry decision combines method semantics, endpoint contract, status code and operation identity. HTTP defines safe and idempotent methods, but a backend can implement them badly, and a POST can be made logically repeat-safe with a documented idempotency-key system. On timeout, I cannot know if the server committed. I persist one operation ID, reuse the same key within its retention policy, query authoritative status and avoid duplicate UI actions. I distinguish 401 refresh, 403 denial, 409 conflict, 429 throttling and transient 5xx. I set bounded backoff and honor Retry-After; I never claim exactly-once network execution from a key.”

## Deep-dive talking points

Explain safe/idempotent distinction, timeout uncertainty, server deduplication and retry classification.

## Follow-up questions

- [DAT-14](../dat-14/): Which failures deserve retry? **Answer:** classified transient failures with bounded backoff and safe endpoint semantics.
- [DAT-20](../dat-20/): What if response is lost? **Answer:** reconcile by stable operation ID before another charge.

## Self-check rubric

Can I state method semantics, classify key status codes and design one safe write retry?

## References and reviewed-on date

- [HTTP Semantics RFC 9110](https://httpwg.org/specs/rfc9110.html) — method and status semantics.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — retryable writes.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
