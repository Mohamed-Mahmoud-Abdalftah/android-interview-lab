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

Design a PCI-DSS compliant logging policy by masking PANs to display only the first 6 and last 4 digits, strictly prohibiting CVV/PIN logging, stripping all Logcat output in release builds via R8, deploying sanitizing HTTP interceptors that scrub card fields, and filtering crash reporting breadcrumbs before dispatch.

## Interview answer — structured

A PCI-DSS compliant observability policy on Android requires strict controls across the data ingestion and transmission pipeline.

First, **PCI-DSS Masking Requirements**. Next, with PAN (Primary Account Number), display at most the first 6 (BIN) and last 4 digits (e.g. `411111******1111`). All intermediate digits must be obscured.
Additionally, with SAD (Sensitive Authentication Data), cVV/CVC, full magnetic stripe data, and PIN blocks must **never** be logged, cached on disk, or retained post-authorization under any circumstances. **Network Interceptor Sanitation**.
Configure custom OkHttp interceptors that parse JSON payloads before logging. Apply regex filters replacing `cvv`, `cardNumber`, and `pin` fields with `[REDACTED]`. Set `HttpLoggingInterceptor.Level.NONE` in release variants. **Crash Reporting and Analytics Sanitization**.
Implement a Crashlytics/Sentry `BeforeSendCallback`. Programmatically scrub event messages, stack traces, and breadcrumb trails for 13-19 digit sequences matching the Luhn algorithm. **Build-Time Enforcement**.
Finally, enforce ProGuard/R8 `-assumenosideeffects` rules to strip standard `android.util.Log` invocations from release binaries entirely.


## Interview answer — deep senior

Senior engineers treat compliance not as a documentation exercise, but as an automated architectural boundary.

First, with Custom Android Lint Rules in CI, implement a custom AST-based Android Lint check that flags any invocation of `Log.*`, `Timber.*`, or `println()` accepting parameters containing substrings like `pan`, `card`, `cvv`, `expiry`, or `token`. Fail CI pipelines on lint warnings. Next, a Card Tokenization (Hosted Fields / SDKs) is the most effective security pattern is ensuring the mobile application never touches raw PAN or CVV at all. Integrate direct payment processor SDKs (e.g., Stripe, Adyen, Braintree) where credit card inputs are rendered inside isolated tokenization iframes or encrypted SDK views that return an ephemeral single-use token directly from the processor's PCI-certified servers.
Finally, with Memory Scrubber Verifications, ensure custom credit card input fields in Compose or Views wipe the underlying character buffers immediately after tokenization is completed, preventing memory dump leakage during audit inspections.


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
