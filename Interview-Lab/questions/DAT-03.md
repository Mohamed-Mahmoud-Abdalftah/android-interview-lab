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

`connectTimeout` يحد وقت إنشاء الاتصال، `readTimeout` وقت انتظار read على socket، `writeTimeout` وقت write، و`callTimeout` يحد عمر الـcall ككل في OkHttp. مش كل واحد deadline إجمالية لنفس الشيء؛ DNS/TLS/redirects/retries ممكن يدخلوا في عمر call. timeout من العميل معناه ما استلمناش نتيجة موثوقة، مش إن السيرفر ما نفذش write.

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

## Practical walkthrough

في mobile network، اتصال ممكن يعلق قبل TCP/TLS، أو server يبدأ الرد وبعدين bytes تتأخر، أو upload body يتعطل. `connectTimeout` لمرحلة الاتصال، `readTimeout` انتظار قراءة bytes، `writeTimeout` للكتابة، و`callTimeout` سقف للcall كلها من بدايتها لنهايتها. لو request فيها redirect/retry، whole-call deadline يمنعها تتمط للأبد. Coroutine `withTimeout` يحط deadline لانتظار caller، لكن لو side effect وصل server، cancellation ما ترجّعوش. اختار budgets حسب endpoint وحجم payload، سجّل phase اللي حصل فيها timeout من غير أسرار، واختبر شبكة بطيئة وresponse ضايع منفصلين.

## Trade-offs and decision criteria

Short deadlines improve responsiveness but can fail on poor networks; long deadlines tie up resources and UX. A whole-call deadline bounds overall wait, while phase timeouts diagnose particular stalls. Different upload/download sizes may need different policies.

## Failure modes

Increasing read timeout alone does not fix DNS/connect stall. Applying a two-second coroutine timeout around a payment request can return Pending while the server commits later. Treating timeout as a definite failure creates unsafe retry behavior.

## Production perspective

A media client uses longer write timeout for uploads and exposes progress; a search client has shorter call deadline. Logs distinguish timeout phase and correlation ID. Payments persist operation IDs and reconcile after ambiguous timeout.

## Interview answer — short

“Connect, read and write timeouts bound different transport waits; call timeout bounds the whole OkHttp call. A timeout is a local observation, not proof that a server-side write failed.”

## Interview answer — structured

“I set timeouts from user experience and operation size. Connect timeout limits establishing a connection, read and write timeouts bound socket I/O inactivity, and call timeout bounds the whole call. A coroutine deadline can further limit how long a caller waits, but it does not guarantee rollback. I test slow phases separately. For a read I may retry transient timeout; for a payment write I persist one operation and query status before retrying with the same server-supported key.”

## Interview answer — deep senior

Timeouts are not interchangeable. A call can fail during DNS/connection, stall on response bytes, or take too long overall through redirects and retries. OkHttp exposes phase-specific and whole-call controls; I configure them per endpoint class, observe timeout type and avoid universally tiny defaults on mobile networks. A coroutine `withTimeout` adds a structured caller deadline, but an uncooperative SDK or server action may continue after it fires. For uploads I report progress and use appropriate write/call deadlines. For money I interpret a lost response as unknown, persist a stable operation ID, and reconcile authoritative status before any repeat. Tests simulate each phase and cancellation.

I set timeouts by failure phase and by the user’s total waiting budget. Connect covers establishing a connection, read and write cover socket I/O inactivity, and call timeout bounds the complete call including redirects or retries. An application deadline may be shorter for an autocomplete request than for an upload, but an extremely small universal value would fail on real mobile networks. A coroutine timeout cancels local waiting; it cannot prove that a server-side write was not committed. For an order submit I therefore pair a call deadline with a persisted request ID and reconciliation. I test slow connect, stalled response, and lost reply separately to see which timeout fired.

## How to answer in the interview

- **Why:** Different stalls need different budgets and diagnosis.
- **How:** Walk through connect, read, write and whole-call phases.
- **Trade-offs:** Tune by endpoint and network conditions, not one tiny global timeout.
- **Failure cases:** Confusing local cancellation with rollback of a server write.
- **Production solution:** Measure timeout phase and reconcile ambiguous submissions.

## Deep-dive talking points

Draw call lifecycle and show where each timeout applies; distinguish client wait from server commit.

## Follow-up questions

- [COR-17](../cor-17/): Does withTimeout stop server work? **Answer:** no, it cancels local coroutine waiting.
- [DAT-20](../dat-20/): How recover a lost response? **Answer:** query status using durable operation identity.

## Self-check rubric

Can I map all four deadlines, choose by operation and handle ambiguous writes?

## References and reviewed-on date

- [OkHttpClient.Builder API](https://github.com/lysine-dev/okhttp/blob/main/okhttp/src/commonJvmAndroid/kotlin/okhttp3/OkHttpClient.kt) — timeout definitions.
- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — caller deadline.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
