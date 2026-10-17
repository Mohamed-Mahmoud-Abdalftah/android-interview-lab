---
id: "DAT-03"
question: "What are connect, read, write, and call timeouts?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "A"
phase: 3
priority: "P1"
order: 260
editorial_status: "reviewed"
---

# DAT-03

## Original interview question

What are connect, read, write, and call timeouts?

## What the interviewer evaluates

Distinguish connection establishment, socket inactivity and whole-call deadlines.

## Concept and technical explanation

OkHttp provides granular timeout dimensions to handle flaky mobile networks and prevent hung sockets:
- Connect Timeout: The maximum duration allowed to establish the initial connection with the target server. This includes DNS resolution, TCP three-way handshake, and TLS cryptographic negotiation. If connection fails within this window, OkHttp aborts or attempts alternative IP addresses.
- Write Timeout: The maximum duration allowed between transmitting consecutive bytes of the request to the server. It governs pushing the request headers and streaming upload payloads. If the socket blocks longer than this duration between byte writes, a SocketTimeoutException is thrown.
- Read Timeout: The maximum duration allowed between receiving consecutive bytes of the response from the server. It does not measure the total download time; rather, it ensures the server has not stalled or abandoned the connection midway through streaming.
- Call Timeout: A macro-level wall-clock timeout introduced in OkHttp 3.12 that spans the entire lifecycle of an HTTP invocation. It encompasses DNS lookup, connection establishment, request writing, server processing, response reading, and any transparent HTTP redirects or retries. It acts as an absolute safety net against runaway coroutine executions.

## Practical walkthrough (English)

Configuring granular timeouts and call-level safety nets in OkHttp:
```kotlin
val okHttpClient = OkHttpClient.Builder()
    // 1. Connection phase (DNS + TCP + TLS)
    .connectTimeout(10, TimeUnit.SECONDS)
    // 2. Inter-byte socket write threshold (uploading payload)
    .writeTimeout(15, TimeUnit.SECONDS)
    // 3. Inter-byte socket read threshold (server response gap)
    .readTimeout(15, TimeUnit.SECONDS)
    // 4. End-to-end wall-clock timeout for the entire request lifecycle
    .callTimeout(30, TimeUnit.SECONDS)
    .build()

// Overriding timeouts per-call for large file uploads
val uploadRequest = Request.Builder()
    .url("https://api.example.com/v1/media/upload")
    .post(fileRequestBody)
    .tag(Invocation::class.java, null)
    .build()

// Call-level timeout configuration via OkHttp client customization
val longRunningClient = okHttpClient.newBuilder()
    .callTimeout(120, TimeUnit.SECONDS)
    .writeTimeout(60, TimeUnit.SECONDS)
    .build()
```

## Explanation in Arabic

ما هي مهلات الاتصال في OkHttp:
`connectTimeout`، و `readTimeout`، و `writeTimeout`، و `callTimeout`، وما الفرق الجوهري بينها؟

1. تفصيل كل نوع مهلة في OkHttp:
   - **`connectTimeout` (مهلة فتح الاتصال)**:
     * الوقت الأقصى المسموح به لإتمام مصافحة TCP الثلاثية (TCP Handshake) ومصافحة TLS/SSL مع السيرفر.
     * إذا استغرق فتح السوكيت وقتاً أطول (مثلاً بسبب برج اتصالات ضعيف أو سيرفر معطل)، يتم إطلاق `SocketTimeoutException: Connect timed out`.
     * القيمة الافتراضية في OkHttp: 10 ثوانٍ.
   - **`readTimeout` (مهلة قراءة البيانات من السوكيت)**:
     * الوقت الأقصى بين وصول حزمتين متتاليتين من البيانات (Maximum gap between two data packets).
     * **ليس الوقت الكلي لتحميل الملف**! طالما أن السيرفر يرسل بايتات بانتظام كل ثانيتين، لن يحدث timeout حتى لو استغرق تنزيل الملف ساعة.
     * يحدث عندما يتوقف السيرفر عن إرسال البيانات فجأة في منتصف الاتصال.
   - **`writeTimeout` (مهلة كتابة البيانات إلى السوكيت)**:
     * الوقت الأقصى بين إرسال بايتين متتاليين إلى السيرفر (مثل رفع صورة أو فيديو كبير).
   - **`callTimeout` (مهلة الطلب الإجمالية من البداية للنهاية)**:
     * أُضيفت في OkHttp 3.12.
     * تضع حداً زمنياً صارماً لكامل دورة حياة الطلب: من استعلام DNS، وفتح الاتصال، والـ Redirects، والـ Authentication Retries، حتى اكتمال قراءة الرد بالكامل.
     * إذا تجاوزت العملية ككل هذه المهلة، يتم إلغاء الطلب فوراً بـ `InterruptedIOException`.

2. قاعدة هندسية في التعامل مع الـ Timeouts:
   - وقوع مهلة قراءة (`readTimeout`) لا يعني أبداً أن السيرفر لم ينفذ العملية! السيرفر قد يكون نفذ العملية في قاعدة البيانات وتأخر فقط في إرسال الرد.

## Practical walkthrough

إعداد مهلات OkHttp المتوازنة لتطبيق إنتاجي:
```kotlin
val okHttpClient = OkHttpClient.Builder()
    // 1. مهلة إنشاء الاتصال ومصافحة الـ TLS:
    .connectTimeout(15, TimeUnit.SECONDS)
    
    // 2. مهلة انتظار وصول الحزمة التالية من السيرفر:
    .readTimeout(20, TimeUnit.SECONDS)
    
    // 3. مهلة إرسال الحزم في الرفع:
    .writeTimeout(20, TimeUnit.SECONDS)
    
    // 4. المهلة الشاملة للطلب ككل (مفيدة للـ Endpoints الحرجة التي لا يجب أن تعلق):
    .callTimeout(45, TimeUnit.SECONDS)
    .build()

// تخصيص مهلة خاصة لعمليات رفع الملفات الكبيرة بدون التأثير على العميل العام:
val uploadClient = okHttpClient.newBuilder()
    .writeTimeout(120, TimeUnit.SECONDS)
    .callTimeout(300, TimeUnit.SECONDS) // مهلة 5 دقائق للرفع بالكامل
    .build()
```

## Why it matters and how it works

OkHttp timeout APIs govern different transport phases. A coroutine `withTimeout` is another caller-level deadline and may cancel waiting, but blocking/remote work may continue. Choose values from product latency and network conditions, test slow connect/read/write, and reconcile writes with an operation ID.

## Worked example

OkHttp conceptual configuration; exact values are illustrative, not universal production defaults.

```kotlin
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

val client = OkHttpClient.Builder()
    .connectTimeout(10, TimeUnit.SECONDS)
    .readTimeout(20, TimeUnit.SECONDS)
    .writeTimeout(20, TimeUnit.SECONDS)
    .callTimeout(30, TimeUnit.SECONDS)
    .build()
```

## Trade-offs and decision criteria

Short deadlines improve responsiveness but can fail on poor networks; long deadlines tie up resources and UX. A whole-call deadline bounds overall wait, while phase timeouts diagnose particular stalls. Different upload/download sizes may need different policies.

## Failure modes

Increasing read timeout alone does not fix DNS/connect stall. Applying a two-second coroutine timeout around a payment request can return Pending while the server commits later. Treating timeout as a definite failure creates unsafe retry behavior.

## Production perspective

A media client uses longer write timeout for uploads and exposes progress; a search client has shorter call deadline. Logs distinguish timeout phase and correlation ID. Payments persist operation IDs and reconcile after ambiguous timeout.

## Interview answer — short

Connect timeout limits the time to complete DNS, TCP, and TLS handshakes. Write timeout limits delays between transmitting request bytes, while read timeout limits delays between receiving response bytes. Call timeout acts as an overarching wall-clock limit governing the entire invocation lifecycle including all redirects and retries.

## Interview answer — structured

Managing timeouts properly in OkHttp is essential for mobile network stability and resource conservation.
First, connect timeout bounds the initial handshake phase. It covers DNS lookup, establishing the TCP socket, and completing TLS negotiation. A typical mobile setting is 10 to 15 seconds.
Second, write timeout governs sending request data. It measures the maximum permitted inactivity gap between consecutive bytes written to the socket, preventing uploads from hanging indefinitely on stalled uplinks.
Third, read timeout governs receiving server responses. Crucially, it measures the time between consecutive bytes received rather than total download duration, ensuring an active download is never terminated prematurely as long as data packets arrive.
Finally, call timeout sets an absolute ceiling on the entire request execution. It bounds connection, writing, server computation, reading, redirects, and retries under a single aggregate threshold.

## Interview answer — deep senior

In enterprise mobile applications operating across volatile cellular networks, misconfigured timeouts directly degrade battery life, exhaust connection pools, and lock up coroutine worker threads.
Developers frequently misunderstand read timeout, assuming it represents total response download duration.
In reality, read timeout in OkHttp is an inter-byte socket inactivity timer implemented via Okio's AsyncTimeout.
If a 200-megabyte file download takes three minutes but packets arrive every two hundred milliseconds, a fifteen-second read timeout will never trigger because the inter-byte deadline is continuously reset.
Conversely, if an edge server accepts the TCP connection but stalls for sixteen seconds while executing a heavy database query, the read timeout fires, throwing a SocketTimeoutException.
To establish a hard boundary against unbounded processing, we configure call timeout.
Introduced in OkHttp 3.12, call timeout wraps the entire Call.execute() or enqueue() pipeline.
Even if an API request encounters multiple 302 redirects or OkHttp attempts failover connections across multiple IP addresses returned by DNS, the aggregate elapsed time cannot exceed the call timeout.
For production setups, we tune timeouts contextually: lightweight JSON RPC endpoints receive short 10-second connect and read timeouts, whereas file upload and telemetry endpoints utilize a dedicated OkHttp client instance with expanded write and call timeouts.
Furthermore, when handling critical socket cancellations, OkHttp cancels the active HTTP/2 stream via RST_STREAM frames without tearing down the underlying TCP connection, conserving radio battery and preserving the warm connection in the pool.

## How to answer in the interview

- **Why:** Different stalls need different budgets and diagnosis.
- **How:** Walk through connect, read, write and whole-call phases.
- **Trade-offs:** Tune by endpoint and network conditions, not one tiny global timeout.
- **Failure cases:** Confusing local cancellation with rollback of a server write.
- **Production solution:** Measure timeout phase and reconcile ambiguous submissions.

## Deep-dive talking points

Draw call lifecycle and show where each timeout applies; distinguish client wait from server commit.

## Follow-up questions

- **Interviewer:** "Can you configure timeouts dynamically per individual Retrofit call?"
  **Answer:** "Yes, by passing a custom OkHttp Interceptor that inspects a custom `@Headers("Timeout: 30")` annotation and clones the client with updated timeouts."

- **Interviewer:** "What is the consequence of setting `connectTimeout` to 1 second on mobile networks?"
  **Answer:** "On 3G or congested cellular networks, DNS lookup and TLS 1.3 handshakes regularly take 1.5–3 seconds; an aggressive 1-second timeout causes massive false connection failures."

## Self-check rubric

Can I map all four deadlines, choose by operation and handle ambiguous writes?

## References and reviewed-on date

- [OkHttpClient.Builder API](https://github.com/lysine-dev/okhttp/blob/main/okhttp/src/commonJvmAndroid/kotlin/okhttp3/OkHttpClient.kt) — timeout definitions.
- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — caller deadline.

Technically reviewed against primary documentation on 2026-10-13.
