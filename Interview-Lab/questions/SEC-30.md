---
id: "SEC-30"
question: "A payment app must mask PAN and avoid sensitive logs. Design a logging/observability policy."
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "C"
phase: 3
priority: "P1"
order: 327
editorial_status: "reviewed"
---

# SEC-30

## Original interview question

A payment app must mask PAN and avoid sensitive logs. Design a logging/observability policy.

## What the interviewer evaluates

- PAN masking, PIN/CVV exclusion and correlation without sensitive payloads.
- Redaction before third-party SDK boundaries and retention.

## Concept and technical explanation

A production payment application subject to PCI-DSS (Payment Card Industry Data Security Standard) must implement strict observability guardrails. Under PCI-DSS Requirement 3, the Primary Account Number (PAN) must be masked wherever displayed or logged, allowing at most the first six digits (BIN) and last four digits to be visible. Sensitive Authentication Data (SAD)—including card verification values (CVV, CVC, CID), PIN blocks, and full magnetic stripe data—must NEVER be logged, cached, or persisted post-authorization under any circumstance. Designing a zero-leakage observability architecture requires defense at multiple boundaries: compiling out Logcat statements via R8 rules, deploying a sanitizing HTTP interceptor that regex-scrubs JSON payloads and strips Authorization headers, masking form fields in crash reporting SDKs, and correlating distributed traces using non-sensitive correlation UUIDs.

## Practical walkthrough (English)

PCI-DSS compliant sanitizing interceptor and R8 log removal:
```kotlin
// 1. OkHttp Redacting Interceptor for secure network telemetry
class SensitiveDataSanitizingInterceptor : Interceptor {
    private val panRegex = Regex("\b(?:\d[ -]*?){13,16}\b")
    private val cvvRegex = Regex(""cvv"\s*:\s*"\d{3,4}"")

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        // Strip sensitive authorization tokens from outgoing log streams
        val sanitizedHeaders = request.headers.newBuilder()
            .set("Authorization", "[REDACTED]")
            .build()

        val response = chain.proceed(request.newBuilder().headers(sanitizedHeaders).build())
        return response
    }
}

// 2. ProGuard/R8 rule stripping Logcat in release builds:
// -assumenosideeffects class android.util.Log {
//     public static *** d(...);
//     public static *** v(...);
//     public static *** i(...);
// }
```

## Explanation in Arabic

تطبيق مدفوعات إلكترونية (Payment App) ملزم بقواعد PCI-DSS ويجب أن يخفي أرقام البطاقات (PAN) ويمنع طباعة البيانات الحساسة في السجلات. كيف تصمم سياسة Logging ومراقبة محكمة؟

1. متطلبات PCI-DSS الصارمة للتعامل مع بيانات الدفع:
   - **رقم الحساب الأساسي (PAN - Primary Account Number)**: يجب إخفاء أرقامه (Masking) عند العرض أو التسجيل؛ يُسمح فقط بعرض أول 6 أرقام (BIN) وآخر 4 أرقام كحد أقصى (مثل `4111 11** **** 1111`).
   - **البيانات الحساسة المحظورة قطعياً (Sensitive Authentication Data - SAD)**: يُمنع منعاً باتاً تخزين أو طباعة رمز الأمان (CVV/CVC)، أو رقم الـ PIN، أو بيانات الشريط المغناطيسي (Track 2) بعد إتمام تفويض العملية تحت أي ظرف!

2. بنية الـ Logging الآمنة في التطبيق:
   - **تعطيل سجلات الـ Logcat في الـ Release**: استخدام R8 لحذف استدعاءات `Log.*` بالكامل.
   - **Sanitizing Interceptor في OkHttp**: اعتراض ومعالجة الـ JSON Request/Response Bodies واستبدال أي حقل يحمل اسم `pan`, `cardNumber`, `cvv`, `password` بـ `[REDACTED]`.
   - **Crashlytics Scrubbing**: فحص جميع الـ Breadcrumbs وتقارير الـ Crash وتصفيتها قبل إرسالها إلى Firebase أو Sentry.
   - **قواعد الـ CI Linter**: بناء Custom Lint Rule تفحص الكود وتفشل الـ Build إذا قام مطور بكتابة كود يطبع متغيراً باسم `pan` أو `cvv`.

## Practical walkthrough

تنفيذ OkHttp Masking Interceptor و دوال مسك الـ PAN المتوافقة مع PCI-DSS:
```kotlin
object PaymentMaskingUtil {
    // 1. دالة إخفاء أرقام البطاقات المتوافقة مع PCI-DSS:
    fun maskPan(pan: String): String {
        val clean = pan.replace(" ", "").replace("-", "")
        if (clean.length < 10) return "*" * clean.length
        val first6 = clean.take(6)
        val last4 = clean.takeLast(4)
        val maskedMiddle = "*".repeat(clean.length - 10)
        return "$first6$maskedMiddle$last4"
    }
}

// 2. OkHttp Interceptor لتطهير السجلات ومنع تسريب بيانات البطاقات:
class PciCompliantLoggingInterceptor : Interceptor {
    private val sensitivePatterns = listOf(
        Regex("\"cvv\"\\s*:\\s*\"[^\"]+\"") to "\"cvv\": \"***\"",
        Regex("\"cardNumber\"\\s*:\\s*\"(\\d{6})\\d+(\\d{4})\"") to "\"cardNumber\": \"$1******$2\""
    )

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        if (BuildConfig.DEBUG) {
            // تطهير الـ URL والهيدرز قبل الطباعة
            val sanitizedUrl = request.url.toString().replace(Regex("token=[^&]+"), "token=REDACTED")
            // تسجيل الـ URL الآمن فقط
        }
        return chain.proceed(request)
    }
}
```

## Why it matters and how it works

Use an allowlist schema and redact at event creation, before crash/analytics upload. Correlation IDs are opaque, non-reversible and separate from card identifiers. Data retention/access controls apply to telemetry too. Card-data handling requirements depend on the certified payment flow and applicable PCI program; do not infer compliance from masking alone.

## Worked example

A typed allowlist prevents accidental raw payload logging. `operationId` must be an opaque random identifier. The sink is a restricted logger/telemetry interface; it never receives PAN, PIN, CVV, bearer tokens, or arbitrary request bodies.

```kotlin
import java.util.UUID

enum class PaymentState { PENDING, CONFIRMED, REVERSED }
enum class SafeReason { TIMEOUT, PROVIDER_REJECTED, NONE }

data class PaymentEvent(
    val operationId: UUID,
    val state: PaymentState,
    val reason: SafeReason,
    val latencyMs: Long,
)

fun recordPayment(event: PaymentEvent, emit: (Map<String, String>) -> Unit) {
    emit(mapOf(
        "operationId" to event.operationId.toString(),
        "state" to event.state.name,
        "reason" to event.reason.name,
        "latencyMs" to event.latencyMs.toString(),
    ))
}
```

The production logger should validate ID shape and retention policy at the sink; typed fields reduce mistakes but do not certify compliance by themselves.

## Trade-offs and decision criteria

Redaction reduces debugging detail, so use precise state codes and provider references that are safe under contract. More detailed data may require a controlled, short-lived diagnostic process with security approval, never blanket raw logging.

## Failure modes

An HTTP interceptor enabled in release logs ISO 8583/card payloads before the app logger redacts them. Audit every sink, including vendor SDKs, and use synthetic canaries in release-like tests. Rotate any exposed credentials and contain logs after incidents.

## Production perspective

Build a telemetry dictionary with prohibited fields, safe event types, retention, role access and automated leak tests. The backend reconciles transaction outcomes using IDs and provider records rather than card values in app logs.

## Interview answer — short

A payment app logging policy strictly complies with PCI-DSS: PAN numbers must be masked to display at most the first six and last four digits, while sensitive authentication data like CVVs and PINs are completely prohibited from logs. We strip Logcat statements via R8, implement an OkHttp redacting interceptor, and sanitize crash payloads.

## Interview answer — structured

Observability in a payment application requires strict architectural boundaries to achieve PCI-DSS compliance and eliminate data leak vectors.
Under PCI-DSS rules, the Primary Account Number must be masked wherever displayed or recorded, allowing only the first six digits for bank identification and the last four digits for customer recognition.
Sensitive Authentication Data including CVV codes, card PINs, and full magnetic stripe data must never be written to logs, disk, or memory dumps under any condition.
In production builds, our R8 configuration strips all Logcat invocations using assumenosideeffects rules to ensure zero developer logs leak to logcat readers.
For necessary network telemetry, we install a custom OkHttp SanitizingInterceptor.
This interceptor parses JSON request and response payloads, replacing credit card number patterns with masked strings and completely stripping CVVs and authorization headers before events reach analytics or APM SDKs.
Crash reporting tools like Crashlytics are configured with custom event transformers that redact user inputs, and distributed transactions are correlated using ephemeral UUIDs rather than personal customer data.

## Interview answer — deep senior

In regulated fintech applications, logging policies directly govern compliance certification and legal liability.
A single unredacted PAN or CVV captured in an application monitoring tool like Datadog or Crashlytics constitutes an immediate PCI-DSS violation with severe financial penalties.
We establish a zero-leakage observability architecture enforcing defense across compile, network, and crash-reporting boundaries.
At compile time, our release ProGuard and R8 rules strip all android.util.Log and Timber debug invocations entirely, neutralizing inadvertent developer log statements.
At the transport boundary, our OkHttp client integrates an automated RedactingInterceptor.
This interceptor utilizes regex patterns to detect sixteen-digit PAN formats, replacing the middle six digits with asterisks to yield compliant six-plus-four masked formats, while explicitly dropping CVV fields, expiration months, and Bearer tokens.
Furthermore, we override crash reporting metadata hooks.
When Crashlytics or Bugsnag captures an unhandled exception, our custom filter scrubs intent extras, bundle arguments, and view hierarchies to prevent text input values from entering breadcrumbs.
For distributed transaction tracing, we inject a cryptographically random correlation UUID into request headers.
Engineers trace requests through microservices by querying this correlation ID, entirely eliminating the need to log account numbers, customer names, or transaction payloads in diagnostic logs. We also configure automated log scrubbing rules in our cloud log ingestion pipelines, ensuring that any stray credentials inadvertently sent to backend collectors are purged before storage.

## How to answer in the interview

- **Why:** observability must explain failures without multiplying sensitive data.
- **How:** allowlist opaque IDs, states, timings, and safe error codes at every sink.
- **Trade-off:** less raw payload requires better correlation tooling.
- **Failure case:** full PAN or authentication data reaches logs.
- **Production solution:** sink inventory, release leak tests, retention limits, and access controls.

## Deep-dive talking points

Prompt for allowlist, every telemetry sink, opaque IDs, canary tests, retention and payment-program review.

## Follow-up questions

- **Interviewer:** "What is the Luhn Algorithm?"
  **Answer:** "A checksum formula (modulus 10) used to validate credit card numbers; logging scrubbers use it to distinguish real card numbers from random digits."

- **Interviewer:** "Can an app be PCI-DSS compliant if it logs masked PAN numbers?"
  **Answer:** "Yes; PCI-DSS allows logging and displaying masked PANs (first 6, last 4), provided Sensitive Authentication Data like CVV is never logged."

## Self-check rubric

Can I specify safe fields, forbidden fields, test a release logger and state residual compliance scope?

## References and reviewed-on date

- [OWASP MASVS storage](https://mas.owasp.org/MASVS/controls/MASVS-STORAGE-1/) — sensitive data minimization.
- [Android security best practices](https://developer.android.com/privacy-and-security/security-best-practices) — logging and data handling.
- [PCI SSC PAN masking FAQ](https://www.pcisecuritystandards.org/faqs/1071/) — display and log masking under PCI DSS 3.4.1.

Technically reviewed against primary documentation on 2026-10-13.
