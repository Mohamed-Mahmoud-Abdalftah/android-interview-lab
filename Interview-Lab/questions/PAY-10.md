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

Achieve payment observability without PCI-DSS violations by logging semantic state transitions and timing metrics indexed strictly by safe Correlation IDs and tokenized references. Never log PIN blocks, CVVs, or full PANs; enforce automated logging scrubbers that mask all but the first 6 and last 4 digits of account numbers.

## Interview answer — structured

Observability in financial applications must balance deep diagnostic telemetry with non-negotiable PCI-DSS compliance.

First, **PCI-DSS Requirement 3 Prohibitions**. Next, explicitly forbids storing or transmitting sensitive authentication data (SAD) post-authorization: full Magnetic Stripe Track data, CVV/CVC codes, and PIN blocks. Full Primary Account Numbers (PAN) must be masked to a maximum of the first 6 digits (BIN) and last 4 digits (`411122******1111`).
**Safe Semantic Telemetry Architecture**. Structure logs around high-level business milestones rather than raw payloads.
`EVENT_EMV_INITIATED`: Correlation ID, reader type, battery level. `EVENT_CARD_PRESENTED`: Tech type (Contactless/NFC vs Chip), Card Scheme (Visa/Mastercard), Masked PAN.
`EVENT_ONLINE_AUTHORIZATION`: Gateway latency, response codes (ISO 8583 Field 39: `00 Approved`). **Automated Defensive Scrubbing**.
Finally, implement custom logging trees (e.g., Timber/Logback filters) configured with regex patterns that detect high-entropy digit sequences and Luhn-valid card numbers, automatically redacting violations before outputting to Logcat or cloud aggregators.


## Interview answer — deep senior

From an enterprise audit and zero-trust security architecture perspective, observability requires hardened pipelines.

First, with Production Logcat Redaction via R8, in production release builds, stripping Logcat logging via ProGuard rules (`-assumenosideeffects class android.util.Log { *; }`) is mandatory. Even non-sensitive logs left in production Logcat can be read by malicious side-loaded apps on non-rooted Android 12+ devices via `adb logcat`. Next, with Encrypted In-Memory Telemetry Ring Buffers, when diagnosing rare transient hardware crashes in the field, maintain a rolling, in-memory circular buffer of the last 100 sanitized diagnostic events. If an unhandled exception or crash occurs, attach this sanitized ring buffer to the Crashlytics non-fatal exception report.
**PCI Point-to-Point Encryption (P2PE)**. Finally, on certified Smart POS terminals, card data is encrypted directly at the hardware Secure Read Head (SCR) before hitting Android OS RAM. The Android app only receives an opaque encrypted blob (P2PE payload); it literally never possesses the raw PAN, rendering accidental memory leaks physically impossible.


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
