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

connectTimeout bounds TCP/TLS handshake duration. readTimeout bounds inactivity gaps between incoming data packets. writeTimeout bounds inactivity gaps when transmitting packets. callTimeout sets an absolute, end-to-end deadline spanning DNS, handshakes, retries, and complete response consumption.

## Interview answer — structured

OkHttp divides timeouts into granular socket-level phases and a top-level end-to-end deadline.

First, connectTimeout is the maximum time allotted to establish a physical connection to the remote host. It includes DNS resolution, TCP handshake, and TLS session negotiation. If the server is unreachable or cellular towers drop the SYN packet, OkHttp aborts with a connection timeout. Next, readTimeout is the maximum duration of inactivity allowed between two incoming bytes read from the socket. Crucially, **this is NOT the total download timeout**. A 100MB download taking 10 minutes will never trigger a `readTimeout` as long as data packets continue arriving within the configured threshold.
Additionally, writeTimeout is the maximum duration of inactivity allowed when pushing bytes to the socket, essential during large multipart image or video uploads. Finally, with callTimeout, introduced in OkHttp 3.12 as an absolute upper bound for the **entire HTTP transaction**. It encompasses DNS, redirects, multi-hop proxy chains, authentication retries, and full body reading. If the entire operation exceeds this threshold, OkHttp immediately aborts the call.


## Interview answer — deep senior

From an error-handling and idempotency perspective, distinguishing between `connectTimeout` and `readTimeout` is vital in production.

First, a **`connectTimeout`** guarantees that **the server never received the request**. The TCP connection never established. Retrying this request immediately (even a `POST` payment request) is 100% safe because no server state was altered. Finally, a **`readTimeout`** guarantees that **the server received the request, and may have already committed the database transaction**. The socket timeout occurred only while waiting for the response. Retrying a `readTimeout` blindly on a non-idempotent endpoint risks duplicate operations and double charges.

Senior architectures treat `readTimeout` on mutating operations as an *uncertain state*, querying the server via an idempotency reconciliation check rather than issuing a raw retry.


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
