---
id: "PAY-10"
question: "How do you make a payment workflow observable without logging PAN/PIN or secrets?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 480
editorial_status: "reviewed"
---

# PAY-10

## Original interview question

How do you make a payment workflow observable without logging PAN/PIN or secrets?

## What the interviewer evaluates

- Observability of state transitions without PAN/PIN or secret leakage.
- Correlation IDs, redaction and unresolved-operation alerts.

## Concept and technical explanation

Making a financial payment workflow thoroughly observable while strictly complying with payment security standards requires zero-trust structured telemetry and automated secret redaction:
- The Regulatory Mandate (PCI-DSS Standard):
  - Requirement 3 of the Payment Card Industry Data Security Standard (PCI-DSS) strictly forbids storing, writing, or logging sensitive authentication data after authorization:
    - Never log: Full Primary Account Numbers (PAN), CVV/CVC codes, PIN blocks, or full Track 2 magnetic stripe buffers.
    - Violations result in severe card brand fines, immediate loss of payment processing licensing, and catastrophic brand liability during security audits.
- Safe Observability Schema (Allowlist Paradigm):
  - Rather than attempting to block-list bad keys, secure telemetry enforces an explicit allow-list schema for every emitted event:
    - Safe identifiers: `transactionId`, `correlationId`, `terminalId`, `merchantId`.
    - Safe card metadata: Masked PAN (First 6 digits for BIN routing, and Last 4 digits for customer receipts, e.g., `411111******1111`), card brand (`VISA`, `MASTERCARD`), card entry method (`CHIP`, `CONTACTLESS`, `SWIPE`), expiry year/month.
    - Operational performance indicators: Network latency in milliseconds, SSL handshake time, EMV kernel processing duration, ISO 8583 response codes (e.g., `00` for Approved, `51` for Insufficient Funds).
- Architectural Defense-in-Depth:
  - Custom Logcat and Telemetry wrappers automatically intercept and scrub regex patterns matching 13-19 digit card numbers.
  - ProGuard/R8 configurations strip out debug logging bytecodes in production release builds.

## Practical walkthrough (English)

Implementing a PCI-DSS compliant payment telemetry logger in Kotlin:
```kotlin
object PaymentTelemetry {
    // Whitelisted telemetry event: strictly contains zero sensitive authentication data
    data class PaymentMetricEvent(
        val eventName: String,
        val correlationId: String,
        val maskedPan: String,       // Formatted as 411111******1111
        val cardBrand: String,       // VISA, MC
        val entryMode: String,       // CHIP, CONTACTLESS
        val latencyMs: Long,
        val responseCode: String? = null,
        val timestamp: Long = System.currentTimeMillis()
    )

    fun logPaymentStep(event: PaymentMetricEvent) {
        // Enforce runtime regex guard: guarantees no unmasked 16-digit PAN leaks
        require(!event.maskedPan.matches(Regex("^[0-9]{13,19}$"))) {
            "CRITICAL SECURITY VIOLATION: Unmasked PAN detected in telemetry payload!"
        }

        // Transmit structured metrics to observability platform (e.g., Datadog, Splunk)
        val metricPayload = mapOf(
            "event" to event.eventName,
            "trace_id" to event.correlationId,
            "pan_masked" to event.maskedPan,
            "brand" to event.cardBrand,
            "mode" to event.entryMode,
            "duration_ms" to event.latencyMs,
            "rc" to (event.responseCode ?: "NA")
        )
        ExternalAnalytics.track(metricPayload)
    }

    // Safe masking utility
    fun maskPan(rawPan: String): String {
        return if (rawPan.length >= 10) {
            "${rawPan.take(6)}${"*".repeat(rawPan.length - 10)}${rawPan.takeLast(4)}"
        } else {
            "**********"
        }
    }
}
```

## Explanation in Arabic

كيف تجعل تدفق المعاملات المالية عالي المراقبة (Observable) دون تسريب بيانات البطاقات الحساسة (PAN / PIN / CVV) أو انتهاك معايير PCI-DSS؟

1. معايير أمان بيانات بطاقات الدفع (PCI-DSS Strict Rules):
   - **المعيار 3 من PCI-DSS**: يحظر تماماً تخزين أو كتابة أي من البيانات التالية في ملفات الـ Logs أو الذاكرة الدائمة:
     * **رقم البطاقة الكامل (Full PAN - 16 Digits)**: يُسمح فقط بالنسخة المقنعة (Masked: أول 6 أرقام وآخر 4 أرقام فقط: `4111 11** **** 1111`).
     * **رمز الأمان (CVV / CVC)**: حظر كامل ومطلق.
     * **الرقم السري أو كتلته المشفرة (PIN / PIN Block)**: حظر كامل ومطلق.
     * **بيانات الشريط المغناطيسي (Full Magnetic Stripe Track Data)**: حظر كامل.
   - تسجيل أي من هذه البيانات في Logcat أو إرسالها لـ Datadog/Crashlytics يعتبر كارثة قانونية تسحب ترخيص الدفع فوراً.

2. المراقبة الآمنة والقانونية (Safe Observability Architecture):
   - **1. الاعتماد على المعرفات البديلة والرموز (Tokenized References)**:
     * استخدام `Correlation ID` و `Payment Token` (مثل `tok_1N3k...`) للربط بين العمليات.
   - **2. تسجيل أحداث دورة الحياة الدلالية (Semantic State Events)**:
     * تسجيل: `EVENT_CARD_TAPPED`, `EVENT_CHIP_READ_SUCCESS`, `EVENT_PIN_ENTERED`, `EVENT_AUTH_DISPATCHED`, `EVENT_AUTH_SUCCESS`.
   - **3. مرشحات السجلات الآلية (Automated Log Sanitizers / Scrubbers)**:
     * كتابة Custom Tree في Timber أو Logback يحتوي على Regex يفحص السجلات تلقائياً؛ فإذا احتوى أي نص على نمط يشبه 16 رقماً يجتاز خوارزمية Luhn، يقوم باستبداله فوراً بـ `[REDACTED_PAN]`.

## Practical walkthrough

تنفيذ أداة تنقية سجلات آلية (Log Scrubber) لحماية بيانات البطاقات في أندرويد:
```kotlin
// Timber Tree مخصص يقوم بتنقية وتشفير أي بيانات بطاقات بالخطأ:
class PciCompliantLoggingTree : Timber.DebugTree() {
    // Regex يلتقط أرقام البطاقات المكونة من 13 إلى 19 رقماً:
    private val panRegex = Regex("\\b(?:[0-9]{4}[- ]?){3}[0-9]{4}\\b")
    private val cvvRegex = Regex("\\b(cvv|cvc|security_code)[\\s:=]+([0-9]{3,4})\\b", RegexOption.IGNORE_CASE)

    override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
        var sanitizedMessage = message
        
        // 1. تنقية وتعتيم أرقام الـ PAN:
        sanitizedMessage = panRegex.replace(sanitizedMessage) { match ->
            val cleanPan = match.value.replace("-", "").replace(" ", "")
            // إبقاء أول 6 وآخر 4 أرقام فقط:
            "${cleanPan.take(6)}******${cleanPan.takeLast(4)}"
        }

        // 2. حجب الـ CVV بالكامل:
        sanitizedMessage = cvvRegex.replace(sanitizedMessage) "$1=***"

        super.log(priority, tag, sanitizedMessage, t)
    }
}

// في كود الدفع: مراقبة دلالية ممتازة وآمنة 100%:
Timber.i("TxId=%s, Amount=%d, CardScheme=VISA, Status=AUTH_REQUEST_SENT", txId, amount)
```

## Why it matters and how it works

Instrument the state machine at its durable transition boundary so events reflect committed state, not only UI clicks. Correlate terminal, backend and provider with a stable ID and map provider references in restricted storage. Redact before third-party crash/analytics SDKs receive data.

## Worked example

For `operationId=6f…`, safe events are `intent_persisted`, `authorization_sent`, `outcome_unknown`, `status_lookup_succeeded`, and `reversal_confirmed`, with latency and SDK build. A dashboard flags unknown older than the expected provider SLA.

## Trade-offs and decision criteria

Fine-grained events improve incident diagnosis but add volume and privacy risk. Use short retention and access controls. Do not use a PAN-derived hash as a “safe” correlation ID; it can still be linkable.

## Failure modes

Logging a vendor callback object via `toString()` may include track/card fields. Review SDK payloads and use an explicit allowlist DTO; inject canary PAN/PIN values in tests and assert they never appear in collected telemetry.

## Production perspective

Operations dashboards show pending age, retry count and divergence between ledgers. Alerts route unresolved payments to reconciliation staff with an opaque ID and controlled lookup access.

## Interview answer — short

Make payments observable securely by adopting an allowlist telemetry schema compliant with PCI-DSS Requirement 3. Log safe correlation tokens, latencies, entry modes, and masked PANs showing only the first six and last four digits, while strictly redacting full PANs, CVVs, and PIN blocks via custom logger interceptors and R8 bytecode stripping.

## Interview answer — structured

Observability in financial workflows requires balancing incident diagnostics with uncompromising payment security regulations.
Under PCI-DSS Requirement 3, logging sensitive authentication data, such as unmasked Primary Account Numbers, CVV codes, Track 2 data, or PIN blocks, is strictly illegal and subject to severe financial penalties.
To achieve observability safely, we adopt an allowlist-driven structured telemetry architecture. Instead of dumping raw network payloads or vendor callback objects, we define immutable metric events containing only approved operational fields.
Safe parameters include correlation IDs, terminal identifiers, network latencies, ISO response codes, card entry modes like EMV Chip or Contactless, and masked PANs exposing only the first six digits for issuer routing and the last four digits for customer receipts.
We enforce defense-in-depth by routing all diagnostic output through a custom logging wrapper that strips unmasked card patterns using regular expressions and by using R8 rules to completely eliminate debug log bytecodes in production releases.

## Interview answer — deep senior

From a PCI-DSS Level 1 compliance, cloud observability, and financial security audit perspective, payment telemetry must be designed with a zero-trust posture toward logging infrastructure.
A frequent source of catastrophic security breaches in mobile applications is accidental data leakage into log aggregation pipelines like Logcat, Crashlytics, or Datadog. When a developer writes Log.d("Response: " + rawJson), the cardholder's full sixteen-digit PAN, expiration date, and CVV are uploaded in cleartext to cloud log clusters, placing the entire corporate infrastructure into high-risk audit failure under PCI-DSS Requirement 3.
The senior architectural design establishes an allowlist telemetry domain model. All instrumentation is driven by structured event objects.
These events capture vital operational signals: DNS resolution latency, TLS handshake duration, gateway processing time, EMV kernel TVR (Terminal Verification Results), and ISO 8583 response codes.
Card data is strictly constrained to the industry-standard masking format: the first six digits representing the Bank Identification Number and the last four digits representing the account identifier, with all intervening digits replaced with asterisks.
At the architectural boundary, we deploy multiple layers of defense. The HTTP client attaches custom redaction interceptors that overwrite sensitive JSON keys before any logger touches the stream. In our logging pipeline, an aggressive regex validation engine scans outgoing strings and immediately aborts if any consecutive thirteen to nineteen-digit sequence is detected.
Finally, release builds configure ProGuard and R8 rules with -assumenosideeffects to strip standard Android Log calls entirely from compiled dex binaries. This guarantees that deep system visibility never compromises cardholder confidentiality.

## How to answer in the interview

- **Why:** responders need state evidence without making logs a card-data store.
- **How:** emit structured events at committed transitions with opaque IDs.
- **Trade-off:** redaction reduces raw detail but preserves safe diagnosis.
- **Failure case:** SDK exception or payload logs leak PAN, PIN block, or CVV.
- **Production solution:** allowlisted fields, retention controls, access review, and alerting on unknown age.

## Deep-dive talking points

Prompt for event-on-commit, operation versus attempt IDs, canary leak tests, backlog alerts and restricted provider mapping.

## Follow-up questions

- **Interviewer:** "What portion of a card number (PAN) is legally permissible to display or log under PCI-DSS?"
  **Answer:** "Only the first 6 digits (the Bank Identification Number - BIN) and the last 4 digits; all intermediate digits must be masked."

- **Interviewer:** "Why should `android.util.Log` calls be stripped by R8/ProGuard in production financial apps?"
  **Answer:** "Because plain-text logs emitted to Android Logcat can be snooped by connected ADB debuggers or unauthorized device monitoring utilities."

## Self-check rubric

Can I specify an allowlisted event schema and operational alert without card data?

## References and reviewed-on date

- [OWASP MASVS storage](https://mas.owasp.org/MASVS/controls/MASVS-STORAGE-1/) — sensitive-data minimization.
- [Android app architecture data layer](https://developer.android.com/topic/architecture/data-layer) — durable data ownership.
- [PCI SSC FAQ on sensitive authentication data](https://www.pcisecuritystandards.org/faqs/1533/) — PIN block and card verification data must not be retained after authorization.

Technically reviewed against primary documentation on 2026-10-13.
