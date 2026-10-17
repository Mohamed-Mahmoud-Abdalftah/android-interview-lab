#!/usr/bin/env python3
"""
Elevation script for PAY questions: PAY-09 to PAY-15.
Topic: Payment/POS & Security Scenarios (PAY)
Phase 5, Batch 2
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "سيناريوهات الدفع ونقاط البيع (POS) وتأمين المعاملات المالية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# PAY-09: How do you isolate a hardware/EMV SDK behind a clean interface?
# ==========================================
DATA["PAY-09"] = {
    "concept_en": """Isolating vendor-specific point-of-sale hardware and EMV chip kernels behind a domain-level abstraction layer protects core business logic from vendor lock-in, lifecycle leaks, and threading chaos:
- The Architectural Hazard of Proprietary SDKs:
  - Hardware vendors (Pax, Ingenico, Verifone, Sunmi) provide proprietary SDKs that rely heavily on native C/C++ libraries via JNI, global singletons, mutable listener callbacks, and raw hardware threads.
  - Directly referencing vendor SDK classes inside ViewModels or Activities creates tight coupling, complicates JVM unit testing, and risks memory leaks if hardware callbacks outlive the UI lifecycle.
- The Hexagonal Ports-and-Adapters Pattern:
  - 1. Domain Port (Interface): A pure Kotlin interface defined in the domain layer (e.g., `interface CardReaderPort`). It exposes business-level inputs and outputs without importing any vendor symbols.
  - 2. Vendor Adapter: An isolated infrastructure module (e.g., `class PaxHardwareAdapter : CardReaderPort`) that translates domain calls into vendor SDK commands and wraps multi-threaded vendor callbacks into idiomatic Kotlin `Flow<ReaderEvent>`.
  - 3. Domain Model Translation: Maps low-level EMV Tag-Length-Value (TLV) hexadecimal strings into type-safe domain entities (`CardData`, `EmvTags`), filtering sensitive parameters at the boundary.
- Concurrency and Lifecycle Isolation:
  - The adapter manages dedicated background dispatchers (`Dispatchers.IO` or a single-threaded hardware executor) to prevent slow chip-card UART/USB operations from blocking the Android Main thread. It scopes hardware operations to a robust application-level lifecycle, ignoring UI teardown.""",
    "walkthrough_en": """Designing a clean hardware abstraction layer for card readers in Kotlin:
```kotlin
// 1. Pure Domain Port: Completely decoupled from vendor SDK symbols
interface CardReaderPort {
    fun monitorCardEvents(): Flow<CardReaderEvent>
    suspend fun startTransaction(amountCents: Long): TransactionInitResult
    suspend fun cancelOperation(): Boolean
}

sealed interface CardReaderEvent {
    data object WaitingForCard : CardReaderEvent
    data class CardInserted(val cardType: String) : CardReaderEvent
    data object ProcessingChip : CardReaderEvent
    data class PinRequested(val remainingAttempts: Int) : CardReaderEvent
    data class CardDataExtracted(val maskedPan: String, val emvTlvData: String) : CardReaderEvent
    data class HardwareError(val code: Int, val message: String) : CardReaderEvent
}

// 2. Vendor-Specific Infrastructure Adapter (e.g., Pax SDK)
class PaxCardReaderAdapter(
    private val paxNativeSdk: PaxDeviceService,
    private val hardwareDispatcher: CoroutineDispatcher = Dispatchers.IO
) : CardReaderPort {

    override fun monitorCardEvents(): Flow<CardReaderEvent> = callbackFlow {
        val listener = object : PaxNativeListener {
            override fun onCardDetected(type: Int) {
                trySend(CardReaderEvent.CardInserted(if (type == 1) "CHIP" else "NFC"))
            }
            override fun onError(code: Int, msg: String) {
                trySend(CardReaderEvent.HardwareError(code, msg))
            }
        }

        paxNativeSdk.registerListener(listener)
        awaitClose { paxNativeSdk.unregisterListener(listener) }
    }.flowOn(hardwareDispatcher)

    override suspend fun startTransaction(amountCents: Long): TransactionInitResult =
        withContext(hardwareDispatcher) {
            val result = paxNativeSdk.startEmv(amountCents)
            if (result.isSuccess) TransactionInitResult.Success else TransactionInitResult.Failure(result.error)
        }

    override suspend fun cancelOperation(): Boolean = withContext(hardwareDispatcher) {
        paxNativeSdk.abort()
    }
}
```""",
    "short_en": """Isolate hardware and EMV SDKs using the Hexagonal Ports-and-Adapters pattern. Define a pure Kotlin interface in the domain layer that exposes reactive Flows of reader events, implemented by a vendor-specific adapter module. This confines proprietary JNI libraries, TLV parsing, and background hardware dispatching to the infrastructure layer, enabling instant mock testing and multi-vendor portability.""",
    "structured_en": """Isolating proprietary hardware and EMV SDKs behind a clean architectural interface is vital for maintainability and testability in POS development.
Hardware manufacturers like Pax, Verifone, and Sunmi provide disparate SDKs with idiosyncratic callback interfaces, native C libraries, and distinct error codes. Directly invoking these vendor classes in UI components couples the codebase to specific hardware, prevents automated JVM unit testing, and complicates future hardware migrations.
We resolve this by applying the Hexagonal Ports-and-Adapters pattern. The domain layer defines a clean, technology-agnostic interface, such as CardReaderPort, which models interactions using sealed Kotlin event classes and Flows.
The infrastructure layer houses vendor-specific adapters that encapsulate the proprietary SDK. The adapter executes hardware I/O on a dedicated background dispatcher, translates low-level EMV Tag-Length-Value buffers into domain models, and converts vendor callbacks into structured coroutine streams.
This separation allows engineering teams to swap hardware suppliers without touching business logic and permits comprehensive unit testing using simulated card readers.""",
    "deep_senior_en": """From an enterprise POS system architecture and certified payment terminal engineering standpoint, hardware abstraction is a mandatory prerequisite for multi-tenant scalability and hardware lifecycle management.
In commercial payment deployments, an organization frequently runs software across diverse hardware fleets: countertop terminals from Verifone, mobile smart POS devices from Pax, and mPOS Bluetooth dongles from Ingenico. If the application codebase directly imports vendor-specific classes, supporting multiple devices requires cumbersome build flavor branching or messy conditional statements littered throughout the presentation layer.
The senior architectural solution establishes a robust Hardware Abstraction Layer adhering to the Ports and Adapters paradigm. The domain port declares contract methods such as startTransaction, cancelOperation, and a reactive Flow of reader events.
Inside the infrastructure module, the adapter encapsulates the vendor SDK. This adapter handles several critical responsibilities: converting imperative vendor C-style listeners into backpressure-aware reactive callbackFlows, sanitizing raw EMV Tag-Length-Value hexadecimal strings into validated domain models, and managing hardware thread confinement.
Hardware SDKs often spawn unmanaged OS threads that interact with low-level UART serial ports. The adapter forces all hardware communication onto a controlled background thread pool, preventing UI thread starvation.
Furthermore, this architectural boundary dramatically accelerates software velocity. In continuous integration environments, automated test suites execute against a FakeCardReaderPort that simulates card insertions, chip read failures, and PIN timeouts in milliseconds on headless JVMs, guaranteeing high reliability before deploying firmware updates to physical hardware fleets.""",
    "meta_ar": {
        "id": "PAY-09",
        "questionAr": "كيف تعزل حزم تطوير عتاد نقاط البيع وقارئات البطاقات (EMV/Hardware SDK) خلف واجهة برمجية نظيفة ومجردة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تطبيق نمط المنافذ والمحولات (Ports & Adapters) في عتاد الدفع، عزل حزم العتاد الاحتكارية (Pax, Verifone, Sunmi)، تحويل دوال رد النداء العتادية إلى Kotlin Flow، واختبار الكود عبر محاكيات وهمية (Fakes).",
        "concept_ar": "يتطلب عزل حزم تطوير عتاد نقاط البيع (POS) وقارئات البطاقات الذكية (EMV SDKs) استخدام نمط المعمارية السداسية (Ports and Adapters / Hexagonal Architecture) لفصل منطق العمل عن تفاصيل العتاد الاحتكارية: توفر الشركات المصنعة للعتاد مثل باكس وإنفينيكو وفيريفون حزم SDK معقدة تعتمد على مكتبات C++ أصلية عبر JNI وخيوط نظام تشغيل عشوائية ومستمعين متعددي الحالات. وإذا كُتبت هذه الحزم مباشرة داخل الـ ViewModel أو الشاشات، يصبح الكود شديد التعقيد ومستحيل الاختبار على حواسيب المطورين دون وجود جهاز فعلي. ويتحقق العزل عبر خطوتين: أولاً، تعريف منفذ نطاق مجرد (Domain Port) يمثل واجهة كوتلن نقية لا تستورد أي مكتبة عتاد؛ ثانياً، بناء محول بنية تحتية (Hardware Adapter) يترجم دوال العتاد ويحول استدعاءات الـ Callbacks إلى دفقات تفاعلية `Flow<CardReaderEvent>` مع حصر العمليات على خيط خلفي مخصص `Dispatchers.IO`، مما يتيح تغيير نوع جهاز نقطة البيع أو تشغيل محاكي برمجيات دون تعديل سطر واحد في واجهة المستخدم.",
        "walkthrough_ar": """بناء طبقة تجريد العتاد وتحويل استدعاءات قارئ البطاقات إلى Flow في كوتلن:
```kotlin
// 1. منفذ النطاق المجرد: مستقل تماماً عن أي حزمة عتاد خارجية
interface CardReaderPort {
    fun monitorCardEvents(): Flow<CardReaderEvent>
    suspend fun startTransaction(amountCents: Long): TransactionInitResult
    suspend fun cancelOperation(): Boolean
}

sealed interface CardReaderEvent {
    data object WaitingForCard : CardReaderEvent
    data class CardInserted(val cardType: String) : CardReaderEvent
    data object ProcessingChip : CardReaderEvent
    data class PinRequested(val remainingAttempts: Int) : CardReaderEvent
    data class CardDataExtracted(val maskedPan: String, val emvTlvData: String) : CardReaderEvent
    data class HardwareError(val code: Int, val message: String) : CardReaderEvent
}

// 2. محول البنية التحتية المخصص لجهاز باكس (Pax SDK Adapter)
class PaxCardReaderAdapter(
    private val paxNativeSdk: PaxDeviceService,
    private val hardwareDispatcher: CoroutineDispatcher = Dispatchers.IO
) : CardReaderPort {

    override fun monitorCardEvents(): Flow<CardReaderEvent> = callbackFlow {
        val listener = object : PaxNativeListener {
            override fun onCardDetected(type: Int) {
                trySend(CardReaderEvent.CardInserted(if (type == 1) "CHIP" else "NFC"))
            }
            override fun onError(code: Int, msg: String) {
                trySend(CardReaderEvent.HardwareError(code, msg))
            }
        }

        paxNativeSdk.registerListener(listener)
        awaitClose { paxNativeSdk.unregisterListener(listener) }
    }.flowOn(hardwareDispatcher)

    override suspend fun startTransaction(amountCents: Long): TransactionInitResult =
        withContext(hardwareDispatcher) {
            val result = paxNativeSdk.startEmv(amountCents)
            if (result.isSuccess) TransactionInitResult.Success else TransactionInitResult.Failure(result.error)
        }

    override suspend fun cancelOperation(): Boolean = withContext(hardwareDispatcher) {
        paxNativeSdk.abort()
    }
}
```""",
        "why_it_matters_ar": "ربط الشاشات بحزم العتاد مباشرة يمنع اختبار التطبيق ويعطل استبدال الأجهزة عند تغيير المورد ويجعل الكود عرضة لتسريب الذاكرة وتعليق الشاشة.",
        "worked_example_ar": "عندما قررت الشركة التحول من أجهزة Pax إلى أجهزة Sunmi، قمنا بكتابة SunmiCardReaderAdapter يطبق نفس CardReaderPort، فعمل التطبيق بالكامل على الأجهزة الجديدة في يومين دون لمس كود الدفع والشاشات.",
        "trade_offs_ar": "بناء طبقة التجريد يضيف كوداً أولياً لصياغة الواجهات وتنسيق الأحداث؛ لكنه ينقذ المشروع من إعادة الكتابة الشاملة عند تنوع أجهزة نقاط البيع بالميدان.",
        "failure_modes_ar": "أخطر الأخطاء هو تنفيذ أوامر العتاد على خيط الواجهة Main Thread مما يجمد التطبيق أثناء قراءة الشريحة، أو نسيان إلغاء تسجيل المستمع في awaitClose مما يسرب الذاكرة.",
        "production_perspective_ar": "في كود الإنتاج، تُبنى حزمة اختبارات كاملة باستخدام FakeCardReaderPort لاختبار تدفقات الدفع في ثوانٍ على الـ CI دون الحاجة لربط أي أجهزة فيزيائية.",
        "how_to_answer_ar": "ابدأ بشرح مخاطر الارتباط المباشر بحزم العتاد، واطرح نمط Ports and Adapters كحل معماري، ثم وضح تحويل الاستدعاءات إلى Flows، واختم بفوائد الاختبار واستبدال الموردين.",
        "talking_points_ar": "المعمارية السداسية Ports & Adapters، واجهة CardReaderPort، تحويل دوال callbackFlow، حصر العمليات على خيوط I/O، عزل نصوص TLV المشفرة، واستخدام Fakes في الاختبار.",
        "follow_ups_ar": "كيف تدير دورة حياة الاتصال التسلسلي (UART Serial / USB) مع قارئ البطاقات؟ وماذا يحدث إذا أُزيلت البطاقة فجأة أثناء معالجة الشريحة؟",
        "self_check_ar": "هل أكدت على عزل رموز العتاد عن النطاق، وتحويل الأحداث إلى Flow، وتشغيل العمليات في الخلفية، وفائدة المحاكيات البرمجية؟",
        "references_ar": f"- [EMVCo: Architecture and Application Design](https://www.emvco.com/) — المعايير الدولية لتصميم تطبيقات نقاط البيع والتعامل مع قارئات الشرائح الذكية.\n- [Martin Fowler: Hexagonal Architecture (Ports and Adapters)](https://martinfowler.com/) — المرجع الهندسي الكلاسيكي لتصميم نظم مستقلة عن العتاد والتقنيات الخارجية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نعزل حزم عتاد الدفع بتطبيق نمط Ports and Adapters؛ حيث نعرّف واجهة نقية في النطاق مثل CardReaderPort ترجع أحداث القراءة كـ Flow تفاعلي. ونبني محولاً خاصاً بالشركة المصنعة للعتاد ينفذ العمليات على خيط خلفي ويترجم الأحداث، مما يتيح استبدال أجهزة نقاط البيع واختبار الكود عبر محاكيات برمجية دون لمس شاشات التطبيق.""",
        "best_answer_ar": """يمثل عزل حزم تطوير العتاد وقارئات البطاقات خلف طبقة تجريد نظيفة ركيزة أساسية لمرونة واستقرار تطبيقات نقاط البيع.
تعتمد حزم الشركات المصنعة مثل Pax وVerifone على مكتبات C++ أصلية ومستمعين متعددي الحالات، وربطها المباشر بالشاشات يقيد التطبيق بجهاز معين ويمنع كتابة اختبارات آلية ويجمد واجهة المستخدم.
ولحل هذه المعضلة، نطبق نمط المعمارية السداسية بتعريف منفذ نطاق CardReaderPort كواجهة كوتلن مجردة تعبر عن أحداث القراءة مثل إدخال البطاقة وطلب الرقم السري كـ Sealed Classes عبر Flow.
وفي طبقة البنية التحتية، نبني محولاً مستقلاً يستورد حزمة العتاد وينفذ الاتصال التسلسلي داخل خيط خلفي مخصص لمنع تجميد خيط العرض الرئيسي، مع ترجمة مصفوفات البايتات المشفرة إلى نماذج بيانات آمنة.
هذا الفصل المعماري يتيح للشركة استبدال موديلات نقاط البيع أو دعم عدة موردين في نفس الوقت بسلاسة، كما يمكننا من اختبار كافة السيناريوهات المحتملة على بيئة البناء المؤتمت باستخدام محاكيات برمجية دون الحاجة لربط أي عتاد فيزيائي.""",
        "deep_answer_ar": """من منظور معمارية حلول نقاط البيع المؤسسية وهندسة الأنظمة المدمجة، يعد تجريد العتاد شرطاً حتمياً لإدارة أساطيل الأجهزة المتباينة وضمان استمرارية الأعمال.
في الواقع العملي للشركات المالية الكبرى، يمتلك التاجر أجهزة دفع متعددة المنشأ تشمل أجهزة ذكية وأجهزة كاونتر ثابتة وقارئات بلوتوث متنقلة. وإذا تغلغلت فئات حزمة العتاد في طبقات العرض والـ ViewModel، فإن دعم موديل جديد يتطلب تشعيب المشروع إلى إصدارات بناء معقدة وتكرار المنطق التجاري مراراً.
وتتمثل المعالجة المعمارية الرفيعة في تأسيس طبقة تجريد عتادية HAL تفصل النطاق عن البنية التحتية؛ حيث تعلن الواجهة المجردة عن تعاقدات واضحة تطلق دفقات أحداث كوتلن تفاعلية.
يتولى المحول العتادي مهام دقيقة تشمل تحويل استدعاءات C القديمة ومستمعي المقابس إلى دفقات callbackFlow منضبطة، وضمان حصر التواصل العتادي مع منافذ UART التسلسلية على موزع خلفي مخصص يحمي خيط أندرويد الرئيسي من التهنيج التام أثناء فحص الشريحة.
كما يضمن المحول تفكيك كتل EMV TLV المعقدة وتنقيتها من أي بيانات حساسة قبل وصولها لمنطق الأعمال.
والأهم هندسياً هو تحقيق قفزة هائلة في سرعة الاختبار والتطوير؛ حيث يُختبر التطبيق على خوادم الـ CI عبر محاكيات برمجية FakeCardReader تُحاكي أعطال القراءة وتعليق العتاد في أجزاء من الثانية، مما يضمن خروج التحديثات البرمجية بموثوقية بنكية مطلقة قبل بثها لأجهزة الميدان."""
    }
}

# ==========================================
# PAY-10: How do you make a payment workflow observable without logging PAN/PIN or secrets?
# ==========================================
DATA["PAY-10"] = {
    "concept_en": """Making a financial payment workflow thoroughly observable while strictly complying with payment security standards requires zero-trust structured telemetry and automated secret redaction:
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
  - ProGuard/R8 configurations strip out debug logging bytecodes in production release builds.""",
    "walkthrough_en": """Implementing a PCI-DSS compliant payment telemetry logger in Kotlin:
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
```""",
    "short_en": """Make payments observable securely by adopting an allowlist telemetry schema compliant with PCI-DSS Requirement 3. Log safe correlation tokens, latencies, entry modes, and masked PANs showing only the first six and last four digits, while strictly redacting full PANs, CVVs, and PIN blocks via custom logger interceptors and R8 bytecode stripping.""",
    "structured_en": """Observability in financial workflows requires balancing incident diagnostics with uncompromising payment security regulations.
Under PCI-DSS Requirement 3, logging sensitive authentication data, such as unmasked Primary Account Numbers, CVV codes, Track 2 data, or PIN blocks, is strictly illegal and subject to severe financial penalties.
To achieve observability safely, we adopt an allowlist-driven structured telemetry architecture. Instead of dumping raw network payloads or vendor callback objects, we define immutable metric events containing only approved operational fields.
Safe parameters include correlation IDs, terminal identifiers, network latencies, ISO response codes, card entry modes like EMV Chip or Contactless, and masked PANs exposing only the first six digits for issuer routing and the last four digits for customer receipts.
We enforce defense-in-depth by routing all diagnostic output through a custom logging wrapper that strips unmasked card patterns using regular expressions and by using R8 rules to completely eliminate debug log bytecodes in production releases.""",
    "deep_senior_en": """From a PCI-DSS Level 1 compliance, cloud observability, and financial security audit perspective, payment telemetry must be designed with a zero-trust posture toward logging infrastructure.
A frequent source of catastrophic security breaches in mobile applications is accidental data leakage into log aggregation pipelines like Logcat, Crashlytics, or Datadog. When a developer writes Log.d("Response: " + rawJson), the cardholder\'s full sixteen-digit PAN, expiration date, and CVV are uploaded in cleartext to cloud log clusters, placing the entire corporate infrastructure into high-risk audit failure under PCI-DSS Requirement 3.
The senior architectural design establishes an allowlist telemetry domain model. All instrumentation is driven by structured event objects.
These events capture vital operational signals: DNS resolution latency, TLS handshake duration, gateway processing time, EMV kernel TVR (Terminal Verification Results), and ISO 8583 response codes.
Card data is strictly constrained to the industry-standard masking format: the first six digits representing the Bank Identification Number and the last four digits representing the account identifier, with all intervening digits replaced with asterisks.
At the architectural boundary, we deploy multiple layers of defense. The HTTP client attaches custom redaction interceptors that overwrite sensitive JSON keys before any logger touches the stream. In our logging pipeline, an aggressive regex validation engine scans outgoing strings and immediately aborts if any consecutive thirteen to nineteen-digit sequence is detected.
Finally, release builds configure ProGuard and R8 rules with -assumenosideeffects to strip standard Android Log calls entirely from compiled dex binaries. This guarantees that deep system visibility never compromises cardholder confidentiality.""",
    "meta_ar": {
        "id": "PAY-10",
        "questionAr": "كيف تجعل تدفق المعاملات المالية قابلاً للمراقبة والتدقيق دون تسريب أرقام البطاقات (PAN) أو الرموز السرية (PIN)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "الامتثال لمعايير أمان البطاقات المصرفية (PCI-DSS)، حظر تسجيل بيانات المصادقة الحساسة (PAN/PIN/CVV)، تصميم مصفوفات المراقبة الآمنة (Allowlist Telemetry)، وتقنيات حجب الأرقام وقواعد R8.",
        "concept_ar": "يتطلب جعل تدفق المعاملات المالية قابلاً للمراقبة والتدقيق مع الالتزام التام بمعايير أمن صناعة بطاقات الدفع (PCI-DSS) اعتماد استراتيجية الثقة المعدومة (Zero-Trust) وقوائم السماح الصارمة: يحظر البند الثالث من معيار PCI-DSS بشكل قاطع تخزين أو تسجيل أي بيانات مصادقة حساسة مثل رقم البطاقة الكامل (PAN)، ورمز التحقق (CVV)، وبيانات الشريط الممغنط Track 2، وكتل الرمز السري (PIN Block)؛ وتكلف مخالفة ذلك غرامات بملايين الدولارات وسحب رخصة معالجة المدفوعات فوراً. ولتحقيق المراقبة الفنية بأمان، نعتمد على نموذج القياس المسموح (Allowlist Schema)؛ حيث نسجل فقط المعطيات التشغيلية مثل: معرّف المعاملة، ومعرّف الارتباط، ورقم نقطة البيع، وأزمنة الاستجابة بالمللي ثانية، وطريقة إدخال البطاقة (شريحة أو تلامسي)، وأكواد رد البنك مثل `00` للقبول و`51` لعدم كفاية الرصيد. أما رقم البطاقة فيُحجب إلزامياً ليظهر منه أول 6 أرقام لمعرفة البنك المصدر وآخر 4 أرقام لطباعة الإيصال فقط، مع تفعيل قواعد R8 لحذف أي أوامر تسجيل أخطاء (Log) تلقائياً من النسخة النهائية.",
        "walkthrough_ar": """تطبيق نظام مراقبة المدفوعات الآمن مع حجب الأرقام الحساسة في كوتلن:
```kotlin
object PaymentTelemetry {
    // نموذج قياس معتمد: يحتوي حصراً على البيانات التشغيلية المسموحة
    data class PaymentMetricEvent(
        val eventName: String,
        val correlationId: String,
        val maskedPan: String,       // يظهر فقط 411111******1111
        val cardBrand: String,       // فيزا أو ماستركارد
        val entryMode: String,       // شريحة EMV أو تلامسي NFC
        val latencyMs: Long,
        val responseCode: String? = null,
        val timestamp: Long = System.currentTimeMillis()
    )

    fun logPaymentStep(event: PaymentMetricEvent) {
        // فحص أمني حاسم: منع خروج أي رقم بطاقة كامل غير مشفر
        require(!event.maskedPan.matches(Regex("^[0-9]{13,19}$"))) {
            "خرق أمني خطير: تم رصد رقم بطاقة كامل غير محجوب في مصفوفة القياس!"
        }

        // إرسال القياسات لمنصة المراقبة السحابية (Datadog / Splunk)
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

    // دالة حجب أرقام البطاقة القياسية
    fun maskPan(rawPan: String): String {
        return if (rawPan.length >= 10) {
            "${rawPan.take(6)}${"*".repeat(rawPan.length - 10)}${rawPan.takeLast(4)}"
        } else {
            "**********"
        }
    }
}
```""",
        "why_it_matters_ar": "تسجيل رقم بطاقة كامل أو رمز سري في ملفات السجلات أو خوادم التتبع يعرض الشركة لفقدان رخصة مزاولة النشاط المالي وغرامات رادعة من البنوك المركزية.",
        "worked_example_ar": "قام مطور بتسجيل رد الشبكة كاملاً في السجلات لمعرفة سبب خطأ؛ التقطه نظام الفحص الأمني ومنعه من الرفع للإنتاج؛ واستبدلناه بتسجيل كود الاستجابة وزمن المعالجة ورقم البطاقة المحجوب فقط.",
        "trade_offs_ar": "حجب البيانات يمنع رؤية الأرقام الحقيقية أثناء التحقيق في المشكلات؛ لكنه يوفر حماية مطلقة لبيانات العملاء ويطابق اللوائح المصرفية الدولية.",
        "failure_modes_ar": "أخطر الأخطاء هو طباعة كائن استجابة الـ SDK كاملاً عبر toString() أو اعتراض حزم الشبكة دون معترض حجب، مما يرسل بيانات البطاقة الحساسة إلى Logcat أو Crashlytics.",
        "production_perspective_ar": "في الشركات المصرفية الكبرى، تفرض خطوط البناء فحصاً آلياً بالكود للبحث عن أي نمط يطابق 16 رقماً متتالياً، مع استخدام قواعد R8 لحذف كود الـ Log تماماً من حزم Release.",
        "how_to_answer_ar": "ابدأ ببيان حظر تسجيل البيانات الحساسة بموجب معايير PCI-DSS، واشرح نموذج القوائم المسموحة Allowlist، وفصّل العناصر الآمنة التي يمكن تسجيلها، واختم بالحجب وقواعد R8.",
        "talking_points_ar": "معايير PCI-DSS البند الثالث، بيانات المصادقة الحساسة SAD، القوائم المسموحة Allowlist، حجب أرقام البطاقات Masking، معترضات الشبكة، وحذف السجلات عبر R8.",
        "follow_ups_ar": "كيف تحمي السجلات عند إرسال تقارير الأعطال (Crash Reports) من التقاط شاشات إدخال الرمز السري؟ وما هو دور تشفير End-to-End Encryption؟",
        "self_check_ar": "هل أكدت على حظر تسجيل PAN وPIN وCVV، وشرحت تنسيق الحجب 6+4، وفصلت البيانات الآمنة المسموح تسجيلها لمراقبة الأداء؟",
        "references_ar": f"- [PCI Security Standards Council: PCI-DSS v4.0 Requirement 3](https://www.pcisecuritystandards.org/document_library/) — المعيار الأمني الدولي الرسمي لحماية بيانات حاملي البطاقات وحظر تخزين بيانات التحقق الحساسة.\n- [Android Developers: Shrink, obfuscate, and optimize your app with R8](https://developer.android.com/build/shrink-code) — الدليل الرسمي لحذف نداءات السجلات البرمجية وفحص الشيفرة المترجمة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نجعل المعاملات قابلة للمراقبة بأمان بتطبيق معايير PCI-DSS عبر نموذج القوائم المسموحة Allowlist؛ حيث نسجل فقط أزمنة الاستجابة ومعرّفات التتبع وأكواد الخطأ، مع حجب أرقام البطاقات بإظهار أول 6 أرقام وآخر 4 أرقام فقط. ويُحظر تماماً تسجيل أرقام البطاقات الكاملة أو الرموز السرية أو كود CVV، مع استخدام قواعد R8 لحذف السجلات نهائياً في الإنتاج.""",
        "best_answer_ar": """تتطلب مراقبة تدفق المعاملات المالية تحقيق توازن دقيق بين وضوح المؤشرات التشغيلية والامتثال الصارم لمعايير أمن بطاقات الدفع PCI-DSS.
يحظر المعيار الدولي بنده الثالث تخزين أو تسجيل بيانات المصادقة الحساسة مثل رقم البطاقة الكامل PAN أو كود الأمان CVV أو كتل الرمز السري PIN في أي سجلات أو ملفات تتبع تحت طائلة العقوبات البنكية الجسيمة.
ولتحقيق المراقبة الموثوقة دون خرق أمني، نعتمد على استراتيجية القوائم المسموحة بتعريف كائنات قياس محددة لا تقبل سوى المعطيات التشغيلية الآمنة.
نسجل معرّفات الارتباط لتتبع المسار الموزع، وأزمنة استجابة الشبكة ومعالجة الشريحة، وطريقة الدفع، وأكواد الرد المصرفي، مع قصر بيانات البطاقة على الصيغة المحجوبة التي تظهر أول ستة أرقام لتعريف البنك وآخر أربعة أرقام للإيصال المحاسبي.
كما نطبق دفاعاً متعدد الطبقات عبر معترضات شبكة تعقم أي نصوص، واستخدام قواعد R8 لحذف استدعاءات التسجيل العادية من النسخة النهائية لمنع أي تسريب غير مقصود للبيانات.""",
        "deep_answer_ar": """من منظور تدقيق الامتثال الأمني لمعايير PCI-DSS المستوى الأول وهندسة منصات المراقبة السحابية، يرتكز تتبع المدفوعات على مبدأ الثقة المعدومة في أدوات التسجيل ومجمعات السجلات.
الخطأ الأكثر كارثية في تطبيقات الدفع هو طباعة كائنات الاستجابة الخام في السجلات أثناء استكشاف الأخطاء، مما يتسبب في رفع أرقام البطاقات وأكواد الحماية الحساسة إلى خوادم مثل Logcat أو منصات تحليل الأعطال السحابية كـ Crashlytics، وهو ما يُعد خرقاً أمنياً يستوجب سحب رخصة معالجة المدفوعات فوراً.
ولذلك نلزم المعمارية بنموذج أحداث تشغيلية صارم يعتمد على قوائم السماح الحصرية؛ حيث لا يمرر الكود سوى قياسات الأداء المحايدة مثل زمن مصافحة التشفير TLS، والمدة المستغرقة داخل نواة الشريحة الذكية EMV، وأكواد ISO 8583 المشفرة.
أما رقم البطاقة فيخضع لخوارزمية حجب إلزامية تُبقي فقط على أول ستة أرقام الممثلة لمعرّف البنك المصدر BIN وآخر أربعة أرقام للتعرف على الحساب، مع استبدال باقي الأرقام بنجوم مشفرة.
وتعزز المنظومة هذه الرقابة بفلاتر تعبيرات منتظمة تفحص النصوص وتوقف التطبيق فوراً إذا رصدت 16 رقماً متتالياً. وأخيراً، تُضبط ملفات ProGuard وR8 لحذف أوامر Log تماماً من الشيفرة المترجمة في الإنتاج، مما يضمن أعلى درجات المراقبة التشغيلية دون المساس بسرية بيانات العملاء."""
    }
}

# ==========================================
# PAY-11: How would you test SDK callback timeout and device disconnection?
# ==========================================
DATA["PAY-11"] = {
    "concept_en": """Testing asynchronous hardware SDK callback timeouts, physical disconnections, and partial failure modes requires deterministic test doubles, synthetic clock control, and fault-injection pipelines:
- The Physical vs Virtual Testing Dilemma:
  - Waiting for physical hardware to experience a genuine timeout or manually yanking USB cables is non-deterministic, agonizingly slow, and impossible to scale across automated Continuous Integration (CI) build pipelines.
  - Relying exclusively on physical hardware leaves edge cases untested until they fail catastrophically in production retail environments.
- Architectural Testing Strategy:
  1. Unit and State Machine Testing via Fakes (Virtualization):
     - Leverage the Hexagonal `CardReaderPort` abstraction.
     - Implement a `FakeCardReaderPort` that provides test controls: `simulateTimeout()`, `simulateUsbDisconnect()`, `simulateCorruptedTlv()`.
     - Use `kotlinx.coroutines.test.StandardTestDispatcher` and `TestScope` to advance virtual time deterministically (`advanceTimeBy(30_000L)`), verifying that state machines immediately transition to `IN_DOUBT` and enqueue ISO 8583 reversal tasks without waiting 30 physical seconds.
  2. Integration Testing via Fault-Injection Native Proxies:
     - Wrap vendor JNI bindings in an interceptable proxy that injects IOExceptions, drops listener callbacks, or delays responses on local emulator builds.
  3. Hardware-in-the-Loop (HIL) Smoke Testing:
     - A small, dedicated lab test rack running physical Android POS terminals connected to programmable USB relays that physically sever data lines to validate hardware recovery circuits under real firmware conditions.""",
    "walkthrough_en": """Testing hardware callback timeouts deterministically using a Fake Card Reader in Kotlin:
```kotlin
class FakeCardReaderPort : CardReaderPort {
    private val eventFlow = MutableSharedFlow<CardReaderEvent>(replay = 1)
    var delayDurationMs: Long = 0L
    var shouldSimulateDisconnect: Boolean = false

    override fun monitorCardEvents(): Flow<CardReaderEvent> = eventFlow.asSharedFlow()

    override suspend fun startTransaction(amountCents: Long): TransactionInitResult {
        if (shouldSimulateDisconnect) {
            eventFlow.emit(CardReaderEvent.HardwareError(code = -101, message = "USB_DISCONNECTED"))
            throw IOException("Device detached unexpectedly")
        }
        if (delayDurationMs > 0) {
            delay(delayDurationMs) // Controlled via TestDispatcher virtual time
        }
        return TransactionInitResult.Success
    }

    override suspend fun cancelOperation(): Boolean = true
}

// Deterministic Unit Test verifying State Machine behavior on Timeout
class PaymentStateMachineTest {
    private val testDispatcher = StandardTestDispatcher()
    private val testScope = TestScope(testDispatcher)
    private val fakeReader = FakeCardReaderPort()
    private val fakeReversalDao = FakeReversalDao()

    @Test
    fun `when reader times out, transaction transitions to IN_DOUBT and queues reversal`() = testScope.runTest {
        val coordinator = PaymentCoordinator(fakeReader, fakeReversalDao, timeoutMs = 10_000L)
        fakeReader.delayDurationMs = 15_000L // Exceeds threshold

        val job = launch { coordinator.initiateCardPayment(amountCents = 5000L) }

        // Fast-forward virtual time by 11 seconds instantly
        testDispatcher.scheduler.advanceTimeBy(11_000L)

        val transaction = coordinator.getCurrentTransaction()
        assertEquals(TransactionStatus.IN_DOUBT, transaction.status)
        assertTrue(fakeReversalDao.hasPendingReversal(transaction.id))

        job.cancel()
    }
}
```""",
    "short_en": """Test SDK timeouts and device disconnections deterministically by utilizing a FakeCardReader implementing the domain port, controlling virtual time via kotlinx-coroutines-test. Inject synthetic disconnects and delays to verify that the state machine enters the in-doubt state and commits a persistent reversal without physical delays, validating on hardware using programmable USB relays.""",
    "structured_en": """Testing hardware SDK callback timeouts and physical disconnections requires a multi-tiered strategy combining deterministic software fakes with automated hardware-in-the-loop validation.
Relying solely on physical POS terminals for timeout testing is slow and unreliable because physical timeouts take tens of seconds and cannot be triggered reliably in CI environments.
Our primary testing tier relies on the CardReaderPort abstraction. We implement a FakeCardReader that allows test cases to trigger simulated hardware disconnections and delayed responses on command.
Using kotlinx-coroutines-test and virtual TestDispatchers, unit tests fast-forward time instantly, proving that when an EMV callback exceeds the timeout threshold, the payment state machine transitions to In-Doubt and enqueues an atomic reversal record in Room.
For the secondary integration tier, we use native test proxies to simulate JNI crashes. Finally, a physical hardware-in-the-loop rack equipped with programmable USB switches cuts connection cables programmatically to verify that recovery workers execute accurately on physical firmware.""",
    "deep_senior_en": """From a test engineering, mission-critical fault injection, and hardware-in-the-loop architectural perspective, validating hardware failure modes demands absolute determinism and zero dependency on human manual intervention.
In embedded Android POS systems, edge-case failures like a customer yanking an NFC card during APDU exchange or a loose USB cable disconnecting mid-EMV pinpad authorization represent the primary causes of terminal freezes and un-reconciled transactions. Attempting to test these edge cases manually on physical desks produces non-repeatable results and fails to integrate into automated GitHub Actions or GitLab CI runners.
The senior testing architecture employs a robust three-tier testing pyramid.
At the base tier, we execute lightning-fast deterministic unit tests on local JVMs using FakeCardReaderPort. By leveraging Kotlin coroutine TestScope and StandardTestDispatcher, we simulate an un-responsive vendor SDK that hangs for forty seconds. Virtual clock manipulation via advanceTimeBy fast-forwards through the timeout window in under two milliseconds. The test asserts that the coordinator cleanly cancels the coroutine, logs the hardware timeout event, updates the Room database status to IN_DOUBT, and registers an ISO 8583 0400 reversal record in the persistent queue.
At the integration tier, we inject synthetic faults directly into the JNI bridge using custom dynamic mock libraries, verifying that native SIGSEGV signals and C++ hardware exceptions are caught and mapped to domain exceptions rather than crashing the Android zygote process.
At the apex tier, hardware-in-the-loop test benches utilize programmable USB power relays to electronically sever the hardware data lines while automated Appium or UI Automator scripts drive a real payment swipe. This multi-layered verification framework ensures complete operational resilience before software reaches retail stores.""",
    "meta_ar": {
        "id": "PAY-11",
        "questionAr": "كيف تختبر حالات انتهاء مهلة استدعاءات العتاد (Callback Timeout) وانقطاع اتصال قارئ البطاقات برمجياً وبكفاءة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "اختبار أعطال العتاد برمجياً دون الحاجة لأجهزة فيزيائية، استخدام المحاكيات البرمجية (Fakes) والتحكم في الوقت الافتراضي (Virtual Time)، فحص انتقال الحالة إلى IN_DOUBT وتسجيل العكس، واختبارات العتاد المؤتمتة (HIL).",
        "concept_ar": "يتطلب اختبار حالات انتهاء مهلة استدعاءات العتاد (Callback Timeout) وانقطاع اتصال قارئ البطاقات اللاسلكي أو السلكي اتباع استراتيجية متعددة الطبقات تعتمد على المحاكيات البرمجية والتحكم في الزمن الافتراضي وحقن الأعطال: الاعتماد على نزع الكابل يدوياً أو انتظار انتهاء المهلة الزمنية في أجهزة حقيقية عملية شديدة البطء ولا يمكن تشغيلها في خوادم البناء المؤتمت (CI/CD). لذا نعتمد على 3 مستويات هندسية: أولاً، بناء محاكي وهمي `FakeCardReaderPort` ينفذ واجهة المنفذ المجرد ويوفر دوال للتحكم في الاختبار مثل محاكاة انقطاع الاتصال وتأخير الرد؛ ثانياً، استخدام `kotlinx-coroutines-test` والتحكم في موزع الوقت الافتراضي `StandardTestDispatcher` لتقديم الساعة الافتراضية 30 ثانية في أجزاء من المللي ثانية، والتأكد من انتقال آلة الحالة فوراً إلى `IN_DOUBT` وتسجيل طلب العكس في قاعدة البيانات؛ ثالثاً، إجراء اختبارات عتادية دورية (Hardware-in-the-loop) باستخدام أجهزة نقاط بيع حقيقية متصلة برحلات تحكم إلكترونية تقطع اتصال الـ USB برمجياً لاختبار سلوك النظام الفعلي تحت ظروف التشغيل الميدانية.",
        "walkthrough_ar": """بناء محاكي وهمي واختبار مهلة القارئ بالوقت الافتراضي في كوتلن:
```kotlin
class FakeCardReaderPort : CardReaderPort {
    private val eventFlow = MutableSharedFlow<CardReaderEvent>(replay = 1)
    var delayDurationMs: Long = 0L
    var shouldSimulateDisconnect: Boolean = false

    override fun monitorCardEvents(): Flow<CardReaderEvent> = eventFlow.asSharedFlow()

    override suspend fun startTransaction(amountCents: Long): TransactionInitResult {
        if (shouldSimulateDisconnect) {
            eventFlow.emit(CardReaderEvent.HardwareError(code = -101, message = "USB_DISCONNECTED"))
            throw IOException("انقطع اتصال القارئ فجأة")
        }
        if (delayDurationMs > 0) {
            delay(delayDurationMs) // يُتحكم فيه بالوقت الافتراضي في بيئة الاختبار
        }
        return TransactionInitResult.Success
    }

    override suspend fun cancelOperation(): Boolean = true
}

// اختبار وحدة حتمي وسريع للتأكد من سلوك النظام عند انتهاء المهلة
class PaymentStateMachineTest {
    private val testDispatcher = StandardTestDispatcher()
    private val testScope = TestScope(testDispatcher)
    private val fakeReader = FakeCardReaderPort()
    private val fakeReversalDao = FakeReversalDao()

    @Test
    fun `when reader times out, transaction transitions to IN_DOUBT and queues reversal`() = testScope.runTest {
        val coordinator = PaymentCoordinator(fakeReader, fakeReversalDao, timeoutMs = 10_000L)
        fakeReader.delayDurationMs = 15_000L // محاكاة تأخر يفوق المهلة المحددة

        val job = launch { coordinator.initiateCardPayment(amountCents = 5000L) }

        // تقديم الزمن الافتراضي 11 ثانية بلحظة واحدة دون انتظار فيزيائي
        testDispatcher.scheduler.advanceTimeBy(11_000L)

        val transaction = coordinator.getCurrentTransaction()
        assertEquals(TransactionStatus.IN_DOUBT, transaction.status)
        assertTrue(fakeReversalDao.hasPendingReversal(transaction.id))

        job.cancel()
    }
}
```""",
        "why_it_matters_ar": "عدم اختبار أعطال العتاد وانقطاع الاتصال يجعل التطبيق يتجمد في أيدي الكاشير عند سحب البطاقة أو اهتزاز الكابل ويفشل في حماية أموال العملاء.",
        "worked_example_ar": "باستخدام FakeCardReaderPort، اختبرنا 50 حالة حافة لانقطاع الاتصال ونفاد بطارية القارئ خلال 3 ثوانٍ على خادم الـ CI، واكتشفنا ثغرة كانت تمنع إرسال العكس عند نزع الكابل.",
        "trade_offs_ar": "المحاكيات البرمجية فائقة السرعة لكنها لا تختبر سلوك دوائر الهاردوير الحقيقية؛ لذا نجمع بين الاختبارات البرمجية السريعة ومنصة اختبارات عتادية دورية.",
        "failure_modes_ar": "أخطر الأخطاء هو كتابة اختبارات نوم حقيقية مثل Thread.sleep(30000) مما يجعل الاختبارات بطيئة جداً ويمنع تشغيلها، أو إهمال فحص تسجيل طلب العكس في الدفتر.",
        "production_perspective_ar": "في الفرق الهندسية المتقدمة، يُشترط تمرير مصفوفة اختبارات الأعطال الافتراضية كاملة قبل السماح بدمج أي تحديث برمجي في خط الإنتاج.",
        "how_to_answer_ar": "ابدأ ببيان صعوبة الاختبار اليدوي على الأجهزة، واشرح استخدام FakeCardReader لاختبار النطاق، ووضح دور الوقت الافتراضي في TestDispatcher، واختم باختبارات العتاد المؤتمتة HIL.",
        "talking_points_ar": "المحاكيات البرمجية Fakes، الوقت الافتراضي Virtual Time، موزع StandardTestDispatcher، دالة advanceTimeBy، حقن الأعطال Fault Injection، واختبارات العتاد HIL.",
        "follow_ups_ar": "كيف تختبر أعطال انهيار مكتبات C++ الأصلية عبر JNI دون التسبب في سقوط تطبيق أندرويد بالكامل؟",
        "self_check_ar": "هل وضحت كيفية اختبار الأعطال دون عتاد فعلي، واستخدام الوقت الافتراضي السريع، والتأكد من الانتقال لحالة الشك وتسجيل العكس؟",
        "references_ar": f"- [Kotlin Coroutines: Testing asynchronous code with kotlinx-coroutines-test](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — الدليل الرسمي لاستخدام الوقت الافتراضي واختبار الشيفرات غير المتزامنة بدقة.\n- [Martin Fowler: Mocks Aren't Stubs and Fakes](https://martinfowler.com/articles/mocksArentStubs.html) — المرجع الهندسي الكلاسيكي لتصميم المحاكيات البرمجية واختبار النظم المعقدة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نختبر مهلة العتاد وانقطاع الاتصال برمجياً عبر بناء محاكي FakeCardReader يطبق منفذ القارئ المجرد مع استخدام kotlinx-coroutines-test للتحكم في الوقت الافتراضي. يتيح ذلك تقديم الساعة الافتراضية لعشرات الثواني في جزء من الثانية للتحقق من انتقال المعاملة لحالة الشك وتسجيل العكس، مدعوماً برحلات اختبار فيزيائية دورية.""",
        "best_answer_ar": """يتطلب اختبار مهل استدعاءات العتاد وانقطاع الاتصال الفجائي منهجية برمجية منضبطة تعتمد على المحاكاة الافتراضية وحقن الأعطال لتفادي البطء الشديد للاختبار اليدوي.
فالانتظار الفيزيائي لانتهاء مهلة القارئ على أجهزة حقيقية يستغرق عشرات الثواني لكل اختبار ويستحيل تشغيله في خطوط البناء المؤتمتة السريعة.
ولحل ذلك، نستند إلى طبقة التجريد CardReaderPort ونبني محاكياً برمجياً FakeCardReader يتيح لنا عبر دوال برمجية بسيطة محاكاة انقطاع كابل الـ USB أو تأخير استجابة الشريحة.
وباستخدام مكتبة kotlinx-coroutines-test وموزع الوقت الافتراضي StandardTestDispatcher، نقوم بتسريع الزمن الافتراضي لأكثر من ثلاثين ثانية في بضع أجزاء من المللي ثانية؛ لنتحقق بدقة وحتمية من أن آلة الحالة تلتقط المهلة فوراً، وتحول حالة المعاملة إلى In-Doubt، وتدرج أمر العكس في قاعدة البيانات دون أي تأخير.
ولضمان التوافق مع العتاد الفيزيائي، يُستكمل ذلك بمعمل اختبارات عتادية HIL يستخدم مفاتيح إلكترونية لقطع مسار البيانات برمجياً والتحقق من سلوك المنظومة بالكامل.""",
        "deep_answer_ar": """من منظور هندسة اختبارات الجودة وحقن الأعطال المنهجي في الأنظمة المدمجة، يتطلب التحقق من أعطال العتاد مستويات صارمة من الحتمية البرمجية دون الاعتماد على التدخل البشري اليدوي.
في بيئات نقاط البيع الميدانية، تمثل سيناريوهات سحب البطاقة التلامسية أثناء تبادل الأوامر أو انفصال القارئ بسبب خلل في الكابل السبب الرئيسي لتعليق التطبيقات وامتلاء الدفاتر بمعاملات معلقة. ومحاولة اختبار هذه الحالات الحافة يدوياً على مكاتب المطورين تعطي نتائج عشوائية لا يمكن الاعتماد عليها في بيئات التكامل المستمر.
لذلك نؤسس هرماً متكاملاً لاختبار الموثوقية؛ يرتكز في قاعدته على اختبارات وحدة حتمية فائقة السرعة تعمل على بيئة JVM مجردة عبر FakeCardReaderPort. وباستخدام TestScope وموزع الاختبارات الافتراضي، نُحاكي تعليق حزمة العتاد لأربعين ثانية، ثم نُقدم المؤشر الزمني عبر advanceTimeBy لينتهي الفحص بالكامل في أقل من ملي ثانيتين.
يتحقق الاختبار من إلغاء نطاق الكوروتين بنظافة، وتسجيل حدث المهلة، وتحديث جدول المعاملات إلى IN_DOUBT، وإدراج سجل العكس ISO 8583 0400 في طابور الفلاش الدائم.
وفي الطبقة المتقدمة، يُربط النظام بمنصة Hardware-in-the-loop تحتوي على أجهزة نقطة بيع حقيقية متصلة بمرحلات تحكم مبرمجة تقطع التوصيل الكهربائي لخطوط USB أثناء إرسال البيانات، للتأكد التام من استجابة برامج التشغيل والبرمجيات المدمجة لنفس المعايير الصارمة قبل طرح التطبيق للأسواق."""
    }
}

# ==========================================
# PAY-12: A POS transaction is approved by issuer but the terminal loses power before saving it. Describe recovery and reconciliation.
# ==========================================
DATA["PAY-12"] = {
    "concept_en": """When a payment is approved by the card issuer but the terminal loses electrical power before persisting the approval response, the system enters a split-brain state requiring disciplined boot-time recovery and batch reconciliation:
- The Split-Brain Disaster:
  - Bank Ledger State: The issuer approved the transaction, assigned an authorization code and Retrieval Reference Number (RRN), and locked or deducted the cardholder's funds.
  - Terminal Ledger State: The local database record remains in `INITIATED` or `PROCESSING` because the device lost power before flushing the `APPROVED` state to flash memory.
- Multi-Stage Recovery Architecture:
  1. Boot-Time Journal Scan:
     - Upon reboot (`android.intent.action.BOOT_COMPLETED`), the application startup coordinator inspects the local Room database before opening any cashier UI.
     - Any transaction stranded in `INITIATED` or `PROCESSING` is immediately flagged as `IN_DOUBT`.
  2. Authoritative Status Inquiry (Check Before Reverse):
     - The terminal dispatches an authenticated Status Inquiry request to the payment gateway using the immutable `idempotencyKey` and `correlationId`.
     - Scenario A (Approved on Gateway): The gateway returns the original authorization response. The terminal updates the local journal to `APPROVED`, saves the RRN, and automatically prints a receipt marked \"RECOVERED TRANSACTION - DUPLICATE RECEIPT\".
     - Scenario B (Unknown / Expired on Gateway): The terminal dispatches an ISO 8583 0400 Reversal to release any orphaned funds hold.
  3. End-of-Day Settlement Reconciliation (Z-Report):
     - If the terminal remains offline throughout the business day, the end-of-day batch settlement process compares the terminal's journal against the acquirer's switch ledger. Any unmatched authorization is automatically flagged for merchant review and resolved without double-billing.""",
    "walkthrough_en": """Implementing boot-time payment recovery and status reconciliation in Kotlin:
```kotlin
class BootRecoveryCoordinator(
    private val journalDao: PaymentJournalDao,
    private val paymentGatewayApi: PaymentGatewayApi,
    private val receiptPrinter: PosReceiptPrinter
) {
    suspend fun recoverStrandedTransactions() {
        val strandedTransactions = journalDao.getStrandedInFlightTransactions()

        for (tx in strandedTransactions) {
            // Mark as IN_DOUBT locally to prevent conflicting cashier actions
            journalDao.updateStatus(tx.id, "IN_DOUBT")

            try {
                // Authoritative Status Inquiry using the original immutable idempotency key
                val statusResult = paymentGatewayApi.queryStatus(
                    orderId = tx.orderId,
                    idempotencyKey = tx.idempotencyKey
                )

                when (statusResult) {
                    is GatewayStatus.Approved -> {
                        // Issuer approved it: Reconcile locally and print recovered receipt
                        journalDao.markApproved(tx.id, statusResult.authCode, statusResult.rrn)
                        receiptPrinter.printCustomerReceipt(
                            orderId = tx.orderId,
                            amount = tx.amountCents,
                            authCode = statusResult.authCode,
                            isRecovered = true
                        )
                    }
                    is GatewayStatus.NotFoundOrDeclined -> {
                        // Gateway has no record or failed: Execute Reversal to guarantee customer safety
                        paymentGatewayApi.sendReversal(tx.id, tx.correlationId)
                        journalDao.markReversed(tx.id)
                    }
                    is GatewayStatus.Pending -> {
                        // Gateway is still processing: Keep in-doubt and retry on next cycle
                    }
                }
            } catch (e: IOException) {
                // Network unavailable: will be reconciled during nightly settlement
            }
        }
    }
}
```""",
    "short_en": """When a terminal loses power before recording an issuer approval, a split-brain state occurs. On reboot, the terminal identifies the stranded transaction, flags it as in-doubt, and performs an authoritative status inquiry using the original idempotency key. If approved, it records the authorization and prints a recovered receipt; if absent, it dispatches an automated reversal, resolving offline discrepancies during end-of-day reconciliation.""",
    "structured_en": """Handling a sudden power loss after bank approval but before local persistence requires an automated recovery and reconciliation protocol.
In this failure scenario, a split-brain condition arises: the cardholder\'s issuing bank has captured the funds, but the terminal\'s local database remains in an in-flight processing state.
To restore accounting consistency, the terminal executes a recovery routine during device boot before permitting any new sales. It scans the local database for stranded in-flight records and transitions them to In-Doubt.
Next, the terminal initiates a status inquiry to the payment gateway utilizing the persisted idempotency key and correlation ID.
If the gateway confirms that the authorization succeeded, the terminal updates the transaction to Approved, saves the authorization code and reference numbers, and prints a duplicate receipt for the merchant and customer.
If the gateway reports that the transaction was never captured, the terminal issues an ISO 8583 reversal message to release any potential funds hold. If the device remains offline, the discrepancy is reconciled during the end-of-day batch settlement.""",
    "deep_senior_en": """From an ISO 8583 transaction processing and financial audit reconciliation perspective, a power failure occurring precisely between bank authorization and local persistence represents one of the most critical operational edge cases in retail engineering.
In this split-brain failure mode, the issuing bank has debited or held the customer\'s funds, and the payment gateway has recorded a successful transaction. However, because electrical power was cut before the terminal\'s SQLite database committed the response payload, the terminal boots up with no record of success. If the cashier assumes the payment failed and requests another card swipe, the customer is double-billed, leading to severe chargeback disputes.
The robust architectural solution divides resolution into immediate boot recovery and deferred batch reconciliation.
At boot time, triggered by the BOOT_COMPLETED intent, the startup manager queries Room for records stuck in INITIATED or PROCESSING. The system immediately locks the terminal cashier interface to prevent further transactions.
The recovery engine then dispatches a Status Inquiry request to the gateway, supplying the original immutable idempotency key and correlation ID. The gateway looks up the transaction in its distributed ledger.
If the gateway returns an Approved status, the terminal executes an atomic database transaction updating the record to APPROVED with the original authCode and RRN, immediately spooling a customer receipt clearly stamped \"RECOVERED TRANSACTION - DUPLICATE\".
If the gateway reports that the transaction timed out or was declined, the terminal enqueues an ISO 8583 0400 reversal to release any pending holds.
Finally, as an ironclad safety net, if connectivity cannot be re-established, the nightly Z-Report batch reconciliation compares the terminal\'s offline journal with the acquirer switch summary. Any unpaired transaction is flagged in an exception report, enabling finance teams to balance the books without manual customer friction.""",
    "meta_ar": {
        "id": "PAY-12",
        "questionAr": "وافقت جهة الإصدار على عملية بيع في نقطة البيع لكن الجهاز فقد الطاقة قبل حفظ النتيجة محلياً. كيف تصمم مسار الاستعادة والمطابقة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "معالجة انشطار الحالة المالية (Split-Brain Scenario)، بروتوكول التعافي عند الإقلاع (Boot-Time Recovery)، الاستعلام عن الحالة باستخدام مفتاح الحتمية، طباعة الإيصال المسترجع، والمطابقة الليلية (Batch Settlement).",
        "concept_ar": "عندما يوافق البنك المصدر للبطاقة على عملية الشراء ولكن ينقطع التيار الكهربائي عن جهاز نقطة البيع فجأة قبل حفظ الرد في قاعدة البيانات المحلية، ينشأ انشطار في الحالة (Split-Brain)؛ حيث تكون الأموال مخصومة في دفاتر البنك بينما لا يمتلك الجهاز أي إثبات محلي على نجاح العملية. وإذا قام الكاشير بإعادة الدفع، سيُخصم من العميل مرتين! ولحل هذه الأزمة، نطبق مسار تعافي دقيق على 3 مراحل: أولاً، عند إعادة تشغيل الجهاز والتقاط حدث `BOOT_COMPLETED`، يفحص النظام الدفتر المحلي ويكتشف المعاملة العالقة بحالة `PROCESSING` ويحولها فوراً إلى `IN_DOUBT` مع قفل شاشة البيع؛ ثانياً، يقوم الجهاز بإرسال استعلام موثق عن الحالة (Status Inquiry) إلى خادم البنك بنفس مفتاح الحتمية ومعرّف الارتباط الأصلي؛ فإذا أكد البنك نجاح العملية، يحدث الجهاز حالته محلياً إلى `APPROVED` ويطبع إيصالاً مدموغاً بعبارة 'إيصال مسترجع - نسخة مكررة'؛ وإذا لم يجد البنك أثراً للعملية، يرسل الجهاز رسالة عكس فورية ISO 8583؛ ثالثاً، إذا استمر انقطاع الإنترنت طوال اليوم، تُحل المعاملة أثناء المطابقة الختامية (Z-Report) بمقارنة دفاتر الجهاز مع كشوفات المقسم المصرفي.",
        "walkthrough_ar": """بناء منسق التعافي عند الإقلاع والمطابقة الآلية مع خادم البنك في كوتلن:
```kotlin
class BootRecoveryCoordinator(
    private val journalDao: PaymentJournalDao,
    private val paymentGatewayApi: PaymentGatewayApi,
    private val receiptPrinter: PosReceiptPrinter
) {
    suspend fun recoverStrandedTransactions() {
        val strandedTransactions = journalDao.getStrandedInFlightTransactions()

        for (tx in strandedTransactions) {
            // تحويل المعاملة العالقة لحالة شك فوراً لمنع تكرار المحاولات العشوائية
            journalDao.updateStatus(tx.id, "IN_DOUBT")

            try {
                // استعلام حاسم عن الحالة باستخدام مفتاح الحتمية الأصلي المحفوظ
                val statusResult = paymentGatewayApi.queryStatus(
                    orderId = tx.orderId,
                    idempotencyKey = tx.idempotencyKey
                )

                when (statusResult) {
                    is GatewayStatus.Approved -> {
                        // البنك أكد الخصم: نحدث الدفتر محلياً ونطبع الإيصال المسترجع
                        journalDao.markApproved(tx.id, statusResult.authCode, statusResult.rrn)
                        receiptPrinter.printCustomerReceipt(
                            orderId = tx.orderId,
                            amount = tx.amountCents,
                            authCode = statusResult.authCode,
                            isRecovered = true
                        )
                    }
                    is GatewayStatus.NotFoundOrDeclined -> {
                        // لا وجود للمعاملة في البنك: نرسل رسالة عكس لتحرير أي حجز
                        paymentGatewayApi.sendReversal(tx.id, tx.correlationId)
                        journalDao.markReversed(tx.id)
                    }
                    is GatewayStatus.Pending -> {
                        // المعاملة ما زالت قيد المعالجة: تبقى معلقة للمحاولة التالية
                    }
                }
            } catch (e: IOException) {
                // تعذر الاتصال: سيتم حسم المعاملة في المطابقة الختامية للدفعة
            }
        }
    }
}
```""",
        "why_it_matters_ar": "فقدان رد الموافقة بسبب انقطاع الكهرباء يجعل الكاشير يطالب العميل بالدفع مجدداً مما يتسبب في خصم مزدوج وشكاوى نزاع مصرفي وخسارة مالية للتاجر.",
        "worked_example_ar": "فُصل كابل الطاقة لحظة موافقة البنك على عملية بقيمة 1500 جنيه؛ وعند إعادة تشغيل الجهاز اكتشف العملية العالقة واستعلم عن البنك بنفس المفتاح، فأكد البنك الموافقة وطبع الجهاز إيصالاً مكرراً للعميل فوراً دون خصم جديد.",
        "trade_offs_ar": "إلزام الجهاز بفحص الدفتر والاستعلام عند كل إقلاع يؤخر بدء تشغيل الشاشة لثانيتين؛ لكنه يحمي من كوارث السحب المكرر وفقدان أموال التجار.",
        "failure_modes_ar": "أخطر الأخطاء هو حذف المعاملة غير المكتملة عند الإقلاع للبدء من جديد، مما يترك العميل مخصوماً منه المبلغ دون استلام مشترياته ودون إمكانية التتبع.",
        "production_perspective_ar": "في أنظمة نقاط البيع المعتمدة، يُطبع الإيصال المسترجع تلقائياً بمجرد تأكيد البنك ليكون دليلاً محاسبياً بيد العميل والكاشير على اكتمال المعاملة الأولى.",
        "how_to_answer_ar": "صف سيناريو انشطار الحالة بدقة، واشرح فحص الدفتر عند الإقلاع BOOT_COMPLETED، ثم وضح خطوة الاستعلام عن الحالة، ومساري الموافقة مع الطباعة أو العكس، واختم بالمطابقة الليلية.",
        "talking_points_ar": "انشطار الحالة Split-Brain، فحص الإقلاع BOOT_COMPLETED، حالة الشك IN_DOUBT، استعلام الحالة Status Inquiry، الإيصال المسترجع، والمطابقة الختامية Z-Report.",
        "follow_ups_ar": "ماذا تفعل إذا لم يستجب خادم البنك للاستعلام وظل العميل واقفاً أمام الكاشير يريد أخذ البضاعة؟",
        "self_check_ar": "هل شرحت مسار التعافي خطوة بخطوة، وأكدت على استخدام نفس مفتاح الحتمية، ووضحت طباعة الإيصال المكرر أو إرسال العكس؟",
        "references_ar": f"- [EMVCo: Terminal Recovery and Power Failure Specifications](https://www.emvco.com/) — المعايير المصرفية الدولية لتعافي أجهزة الدفع من انقطاع الطاقة المفاجئ.\n- [Mastercard Settlement and Reconciliation Manual](https://www.mastercard.us/) — الدليل الإرشادي لمطابقة الدفاتر المحاسبية ومعالجة الفروقات في تسوية الدفعات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """عند فقدان الطاقة بعد موافقة البنك، ينشأ انشطار في الحالة؛ حيث يخصم البنك المبلغ بينما لا يمتلك الجهاز أي إثبات. يعالج النظام ذلك عند الإقلاع بفحص المعاملات العالقة وتحويلها لحالة الشك، ثم إرسال استعلام عن الحالة بنفس مفتاح الحتمية. فإذا أكد البنك القبول، تُحدث المعاملة ويُطبع إيصال مسترجع مكرر، وإلا يُرسل طلب عكس وتُطابق الفروقات في نهاية اليوم.""",
        "best_answer_ar": """يمثل انقطاع الطاقة عن نقطة البيع فور موافقة البنك وقبل حفظ الرد محلياً سيناريو انشطار الحالة المالية الأشد خطورة في أنظمة الدفع.
في هذه اللحظة، تكون أموال العميل قد خُصمت بالفعل في سجلات البنك، بينما لا يزال سجل المعاملة في قاعدة بيانات الجهاز معلقاً، مما قد يدفع الكاشير للمطالبة بالدفع مجدداً والتسبب في خصم مزدوج.
ولمعالجة ذلك، تفرض المعمارية مسار تعافٍ إلزامي ينطلق فور إقلاع الجهاز بموجب حدث BOOT_COMPLETED وقبل فتح شاشة البيع.
يفحص المنسق سجلات قاعدة البيانات ويكتشف المعاملة العالقة ويضعها فوراً في حالة الشك، ثم يرسل استعلاماً موثقاً لخادم الدفع باستخدام نفس مفتاح الحتمية ومعرّف الارتباط الأصليين.
فإذا أكد الخادم أن التفويض تم بنجاح، يُحدث الجهاز سجله إلى مقبول ويُصدر فوراً إيصالاً ورقياً مطبوعاً عليه إيصال مسترجع للعميل.
أما إذا أكد الخادم عدم تسجيل المعاملة، فيبث الجهاز رسالة عكس تلقائي ISO 8583 لتحرير أي حجز مؤقت، مع حسم أي فروقات متبقية أثناء مطابقة الدفاتر الختامية في نهاية الوردية.""",
        "deep_answer_ar": """من منظور معايير التحويل المصرفي ISO 8583 وهندسة التسويات والمطابقة المالية، يمثل انقطاع الطاقة اللحظي بين استلام التفويض وتثبيته في القرص الصلب أخطر اختبار لسلامة الدفاتر المحاسبية الموزعة.
في هذا الفشل الانشطاري، يحمل خادم البنك قيداً محاسبياً مؤكداً برقم تفويض ورقم مرجع RRN، بينما يستيقظ جهاز نقطة البيع بذاكرة محلية خالية من أي إثبات على النجاح. وإذا تصرف النظام بسذاجة واعتبر المعاملة فاشلة، سيعيد الكاشير العملية ليدفع العميل مرتين، مما يولد نزاعاً بنكياً مكلفاً يضر بمصداقية التاجر.
والتصميم المعماري الرصين يحل هذه الأزمة عبر مسار تعافٍ استباقي مقسم إلى مرحلتين:
المرحلة الأولى تنطلق فور إقلاع نظام أندرويد؛ حيث يمسح عامل التعافي جدول المعاملات في SQLite ويكتشف أي صف لا يزال عالقاً بحالة المعالجة، فيقوم بقفل واجهة البيع تماماً وتحويل المعاملة إلى IN_DOUBT.
ثم يبث الجهاز نداء استعلام عن الحالة إلى بوابة الدفع بالاعتماد على مفتاح الحتمية الأصلي. وعندما يرجع الخادم بيانات التفويض المسجلة، تُجري المعمارية حركة كتابة ذرية لتثبيت حالة APPROVED في الدفتر المحلي، وتأمر الطابعة الحرارية بنفث الإيصال المحاسبي حاملاً خاتم معاملة مسترجعة لتسليمه للعميل مع البضاعة.
وفي حال أفاد البنك بأن العملية لم تكتمل، يُدرج الجهاز طلب عكس فوري ISO 8583 0400 لإلغاء أي حجز معلق.
أما المرحلة الثانية فتتمثل في المطابقة المحاسبية الختامية Z-Report في نهاية اليوم؛ حيث تُقارن سجلات الجهاز غير المحسومة مع كشف المقسم البنكي لتسوية أي تباين متبقٍ وحفظ التوازن المالي لكافة الأطراف دون أي تدليس أو تكرار."""
    }
}

# ==========================================
# PAY-13: A timeout handler exits the UI before enqueueing a reversal. How do you redesign ownership and ordering?
# ==========================================
DATA["PAY-13"] = {
    "concept_en": """Allowing a UI presentation timeout handler to dismiss the screen or cancel coroutines before a financial reversal is durably enqueued creates an orphaned hold vulnerability:
- The Flawed Architecture (UI-Owned Financial Lifecycle):
  - In flawed architectures, the financial transaction and reversal logic reside inside an Activity or ViewModel `viewModelScope`.
  - When a timeout occurs, the UI layer catches the timeout, immediately pops the backstack or navigates away, terminating the coroutine scope before the background network reversal request can be scheduled or dispatched.
  - Consequence: The customer's funds remain held at the issuing bank indefinitely; the app never retries because the task was bound to the dead UI component.
- The Redesigned Architecture (Application-Owned Coordination):
  1. Separation of Concerns & Ownership Inversion:
     - The financial state machine and reversal queue belong to a singleton Application-scoped Coordinator (`applicationScope` / persistent `PaymentRepository`), completely independent of Android Activity or ViewModel lifecycles.
     - The ViewModel acts purely as an observer, collecting state from a domain `StateFlow`.
  2. Inverted Transactional Ordering (Write Intent First):
     - Order of Operations:
       1. Timeout detected at the domain repository layer.
       2. The repository updates the transaction to `IN_DOUBT` and commits the reversal record into the persistent SQLite `reversal_queue` table inside a single atomic database transaction.
       3. Only *after* the local database confirms durable disk persistence does the repository emit the `Timeout` state to the UI.
     - Even if the user destroys the Activity, powers off the screen, or Android kills the UI process, the reversal intent is already safely burned into flash memory, ready for background dispatch.""",
    "walkthrough_en": """Redesigning ownership and transactional ordering for payment timeouts in Kotlin:
```kotlin
// 1. Domain Coordinator owned by Application Scope, NOT ViewModel
class PaymentCoordinator(
    private val appScope: CoroutineScope, // Injected ApplicationScope (SupervisorJob + Dispatchers.Default)
    private val appDatabase: AppDatabase,
    private val journalDao: PaymentJournalDao,
    private val reversalDao: ReversalDao,
    private val paymentGatewayApi: PaymentGatewayApi
) {
    private val _paymentState = MutableStateFlow<PaymentState>(PaymentState.Idle)
    val paymentState: StateFlow<PaymentState> = _paymentState.asStateFlow()

    fun executeTransaction(orderId: String, amount: Long) {
        // Launch in ApplicationScope: Outlives UI teardown and screen navigation
        appScope.launch {
            _paymentState.value = PaymentState.Processing

            try {
                withTimeout(20_000L) {
                    val auth = paymentGatewayApi.authorize(orderId, amount)
                    _paymentState.value = PaymentState.Approved(auth.code)
                }
            } catch (e: TimeoutCancellationException) {
                // CRITICAL ORDERING: Commit to disk FIRST before notifying UI
                appDatabase.withTransaction {
                    journalDao.markInDoubt(orderId)
                    reversalDao.insert(ReversalEntity(orderId, amount, System.currentTimeMillis()))
                }

                // Safe to notify UI now: Reversal intent is already durably persisted
                _paymentState.value = PaymentState.InDoubtTimeout
            }
        }
    }
}
```""",
    "short_en": """Redesign ownership and ordering by decoupling the payment lifecycle from the UI, moving coordination into an Application-scoped repository. Invert the operational sequence: when a timeout occurs, durably persist the in-doubt state and reversal queue entry inside an atomic SQLite transaction first, and only notify the UI after disk commit succeeds.""",
    "structured_en": """Allowing a UI timeout to dismiss a screen before enqueueing a reversal causes catastrophic orphaned holds.
This flaw occurs when financial logic is coupled to UI lifecycles like ViewModel scopes. If a timeout timer cancels the scope or the user navigates away, execution terminates prematurely, leaving the customer\'s funds locked at the bank without a reversal.
To correct this, we execute an ownership redesign and an ordering inversion.
First, we transfer ownership of the payment state machine from the UI to an application-scoped domain coordinator. The coordinator runs in a persistent application coroutine scope or background service that survives Activity destruction. The UI simply observes state updates.
Second, we invert the execution ordering. When a network timeout occurs, the coordinator never notifies the UI immediately. Instead, it executes an atomic SQLite transaction that updates the transaction status to in-doubt and inserts a reversal task into the persistent queue table.
Only after the database write is confirmed does the coordinator emit the timeout state to the UI, guaranteeing that user navigation can never abort reversal dispatch.""",
    "deep_senior_en": """From a software architecture, reactive state boundaries, and financial mission-critical resilience perspective, coupling payment execution to Android UI lifecycles is an architectural anti-pattern that directly causes ledger desynchronization.
Activities and Fragments in Android are inherently ephemeral: they are destroyed and recreated during screen rotations, configuration changes, user back-presses, and system memory pressure. If a payment flow is launched inside viewModelScope and the timeout handler immediately triggers a navigation event like findNavController().popBackStack(), Android cancels the active coroutine job. Any subsequent code intended to enqueue a reversal task in Room or dispatch an ISO 8583 0400 cancellation is dropped mid-execution. The cardholder\'s account remains charged with an orphaned authorization hold, and the system loses all automated recovery momentum.
The senior architectural solution enforces two uncompromising principles: Application Scope Ownership and Inverted Transactional Ordering.
We decouple the transaction coordinator entirely from the UI layer, injecting an ApplicationScope backed by a SupervisorJob. The ViewModel becomes a passive presentation observer that exposes a StateFlow to Compose or XML views.
Furthermore, we enforce strict ordering invariants. When a timeout occurs, the domain engine catches the exception and immediately enters an atomic SQLite transaction using Room withTransaction. It updates the payment journal record to IN_DOUBT and inserts a persistent reversal task into the reversal_queue table.
Only after the Linux kernel flushes the SQLite Write-Ahead Log to physical NAND storage does the coordinator emit the Timeout UI state.
Even if the user vigorously mashes the home button, swipes away the app, or unplugs the POS device, the reversal intent has already been durably anchored to disk, ensuring that background workers will reliably dispatch the reversal to the bank switch.""",
    "meta_ar": {
        "id": "PAY-13",
        "questionAr": "أنهى معالج المهلة الزمنية شاشة واجهة المستخدم قبل تسجيل عملية العكس. كيف تعيد تصميم ملكية المهمة وترتيب العمليات؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصحيح ملكية دورة حياة المعاملات المالية، فصل منطق الدفع عن دورة حياة الشاشة (Activity/ViewModel Lifecycle)، نمط الملكية على مستوى التطبيق (Application Scope)، وتعديل الترتيب بالحفظ الدائم أولاً.",
        "concept_ar": "يؤدي ربط منطق الدفع ومعالجة المهلة الزمنية بدورة حياة واجهة المستخدم (UI Lifecycle) إلى كارثة تعليق أموال العملاء إذا أغلقت الشاشة قبل تسجيل طلب العكس: عندما يُكتب كود الدفع داخل `viewModelScope`، فإن انتهاء المهلة الزمنية وقيام الكود بإغلاق الشاشة أو الرجوع للخلف يلغي نطاق الكوروتين فوراً، مما يمنع إرسال طلب العكس أو تسجيله في قاعدة البيانات، وتظل أموال العميل محجوزة في البنك دون أي وسيلة لإلغائها! وتصحيح هذه المعمارية يتطلب ركيزتين: أولاً، نقل ملكية المعاملة من الشاشة إلى منسق عام على مستوى التطبيق (Application-Scoped Coordinator) يعمل بنطاق مستقل لا يتأثر بموت أو إغلاق الشاشات، ويكون دور الـ ViewModel مقتصراً على مراقبة الحالة فقط؛ ثانياً، عكس ترتيب العمليات (Inverted Ordering)؛ فعند حدوث المهلة الزمنية، يُحظر إشعار الشاشة أو إغلاقها، بل يُنفذ أولاً أمر كتابة ذرية في قاعدة البيانات لتحديث حالة العملية إلى `IN_DOUBT` وحفظ نية العكس في طابور الفلاش، وبعد تأكيد الحفظ على القرص فقط يتم إرسال حالة انتهاء المهلة للواجهة.",
        "walkthrough_ar": """إعادة تصميم ملكية المعاملة على نطاق التطبيق وعكس ترتيب حفظ العكس في كوتلن:
```kotlin
// 1. منسق الدفع مملوك لنطاق التطبيق بالكامل ومستقل عن الشاشات
class PaymentCoordinator(
    private val appScope: CoroutineScope, // نطاق التطبيق العام المحقون (SupervisorJob + Default)
    private val appDatabase: AppDatabase,
    private val journalDao: PaymentJournalDao,
    private val reversalDao: ReversalDao,
    private val paymentGatewayApi: PaymentGatewayApi
) {
    private val _paymentState = MutableStateFlow<PaymentState>(PaymentState.Idle)
    val paymentState: StateFlow<PaymentState> = _paymentState.asStateFlow()

    fun executeTransaction(orderId: String, amount: Long) {
        // إطلاق المهمة في نطاق التطبيق ليصمد أمام إغلاق الشاشة والرجوع
        appScope.launch {
            _paymentState.value = PaymentState.Processing

            try {
                withTimeout(20_000L) {
                    val auth = paymentGatewayApi.authorize(orderId, amount)
                    _paymentState.value = PaymentState.Approved(auth.code)
                }
            } catch (e: TimeoutCancellationException) {
                // ترتيب جوهري حاسم: الحفظ الدائم على القرص أولاً قبل إشعار الشاشة
                appDatabase.withTransaction {
                    journalDao.markInDoubt(orderId)
                    reversalDao.insert(ReversalEntity(orderId, amount, System.currentTimeMillis()))
                }

                // الآن فقط نحدث حالة الواجهة بأمان تام لأن العكس محفوظ في الفلاش
                _paymentState.value = PaymentState.InDoubtTimeout
            }
        }
    }
}
```""",
        "why_it_matters_ar": "إلغاء مهمة العكس بسبب إغلاق الشاشة يترك رصيد العميل مجمداً في البنك لأسابيع دون أن يدري التاجر، مما يولد شكاوى نزاع وخسائر مادية.",
        "worked_example_ar": "انتهت مهلة الـ 20 ثانية وضغط العميل زر الرجوع؛ ولأن الكود يعمل في ApplicationScope وحفظ العكس في SQLite أولاً، أُغلقت الشاشة بينما استمر النظام في إرسال رسالة العكس للبنك بنجاح.",
        "trade_offs_ar": "فصل منطق الدفع عن الـ ViewModel يضيف طبقة منسق مستقلة؛ لكنه يضمن نجاة العمليات المالية من دورات حياة أندرويد المعقدة وتقلبات الشاشات.",
        "failure_modes_ar": "أخطر الأخطاء هو تنفيذ findNavController().popBackStack() داخل كتلة catch قبل إنهاء كتابة طلب العكس في قاعدة البيانات، مما يجهض عملية الحفظ فوراً.",
        "production_perspective_ar": "في كود الإنتاج، يُحقن ApplicationScope في المنسق المالي، وتخضع الشاشات لاختبار التدوير السريع ونقر زر الرجوع للتأكد من عدم ضياع أي أمر عكس.",
        "how_to_answer_ar": "ابدأ ببيان خطورة ربط المعاملات بالـ ViewModel وسقوط الكوروتين عند الرجوع، ثم اشرح الحل بنقل الملكية لـ ApplicationScope، وأكد على قاعدة عكس الترتيب بحفظ العكس في قاعدة البيانات أولاً.",
        "talking_points_ar": "ملكية دورة الحياة Lifecycle Ownership، نطاق التطبيق ApplicationScope، عكس الترتيب Inverted Ordering، فخ إلغاء الشاشة، الحفظ الذري المسبق في Room، وتدفق StateFlow.",
        "follow_ups_ar": "كيف تضمن عدم إطلاق معاملتين متزامنتين من نطاق التطبيق إذا ضغط المستخدم زر الدفع عدة مرات بسرعة؟",
        "self_check_ar": "هل أكدت على فصل المعاملة عن دورة حياة الشاشة، وشرحت نقل الملكية لـ ApplicationScope، وأكدت على حفظ العكس في القرص قبل إشعار الواجهة؟",
        "references_ar": f"- [Android Developers: Coroutines & Patterns for work that shouldn't be cancelled](https://medium.com/androiddevelopers/coroutines-patterns-for-work-that-shouldnt-be-cancelled-e26c40f142ad) — الدليل الرسمي لإدارة مهام الكوروتين التي يجب ألا تُلغى عند موت الشاشات.\n- [Martin Fowler: Separating Presentation from Business Logic](https://martinfowler.com/) — المرجع الهندسي لفصل منطق الأعمال والعمليات الحرجة عن واجهة المستخدم.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نعيد تصميم المعمارية بنقل ملكية المعاملة بالكامل من الشاشة إلى منسق عام يعمل بنطاق التطبيق ApplicationScope بحيث ينجو من إغلاق الشاشات والرجوع للخلف. ونعكس ترتيب العمليات بحيث يُحفظ سجل الشك وطلب العكس في قاعدة البيانات أولاً عبر معاملة ذرية، ثم تُشعر الواجهة بعد ضمان الحفظ الدائم على القرص.""",
        "best_answer_ar": """يمثل ربط دورة حياة المعاملة المالية بشاشة واجهة المستخدم خطأً معمارياً فادحاً يهدد بتعليق أموال العملاء دون إلغاء.
فعندما يتم إطلاق المعاملة داخل نطاق الشاشة كـ viewModelScope، فإن انتهاء المهلة الزمنية وإغلاق الشاشة يلغي نطاق الكوروتين فوراً، مما يجهض عملية تسجيل طلب العكس أو إرساله للبنك، ويبقى رصيد العميل مجمداً لأيام.
ولعلاج هذا الخلل الجذري، نتبع خطوتين حاسمتين:
أولاً، نقل ملكية المعاملة إلى منسق مستقل يعمل بنطاق التطبيق العام ApplicationScope؛ حيث تستمر المعاملة في العمل حتى لو دُمرت الـ Activity أو ضغط المستخدم زر الرجوع، ويكون دور الشاشة مراقبة الحالة عبر StateFlow فقط.
ثانياً، عكس ترتيب العمليات التنفيذية؛ فعند رصد انتهاء المهلة الزمنية، يُحظر إشعار الشاشة أولاً، بل يقوم المنسق بفتح معاملة ذرية في SQLite لحفظ حالة المعاملة كمعلقة وإدراج طلب العكس في طابور الفلاش الدائم.
وبعد تأكيد الكتابة الصلبة على القرص فقط، يُرسل إشعار المهلة للواجهة، مما يضمن استحالة ضياع طلب العكس مهما تصرف المستخدم.""",
        "deep_answer_ar": """من منظور معمارية البرمجيات وهندسة الأنظمة عالية الموثوقية، يعد ربط العمليات المالية بدورة حياة عناصر العرض في أندرويد عيباً تصميمياً ينسف ضمانات التكامل المحاسبي.
فالأنشطة والشاشات كائنات عابرة في أندرويد تُهدم وتُعاد برمجتها عند تدوير الشاشة أو ضغط زر الرجوع أو تدخل مدمر الذاكرة LMK. فإذا رصد كود الواجهة انتهاء المهلة وقام باستدعاء دوال الرجوع قبل جدولة العكس، يتم إلغاء الـ Coroutine Job فوراً، لتتبخر نية العكس ويبقى الحجز المصرفي معلقاً في البنك دون أي أثر محلي للمتابعة.
والتصحيح الهندسي الصارم يرتكز على مبدأين: تجريد الملكية وعكس الترتيب التنفيذي.
نلغي وصاية الـ ViewModel تماماً ونجعل إدارة المعاملة مسؤولية منسق دائم محقون بنطاق ApplicationScope معزز بـ SupervisorJob وموزع خلفي.
كما نطبق انضباطاً صارماً في تتابع الأوامر؛ فعند انقضاء المهلة الزمنية، يمسك المنسق بالخطأ ويُنفذ حركة كتابة ذرية في Room باستخدام withTransaction؛ حيث يُثبت في جدول المعاملات ويدرج أمر العكس في جدول reversal_queue ككتلة بيانات واحدة.
ولا يُطلق المنسق حدث المهلة للواجهة إلا بعد أن يؤكد مشغل التخزين في نواة لينكس اكتمال حرق السجل في خلايا الذاكرة غير المتطايرة.
بهذا الفصل الصارم، حتى لو ألقى المستخدم الهاتف أو خرج فوراً للشاشة الرئيسية، فإن نية العكس تظل مصونة ومثبتة في القرص، لتتولى عمال الخلفية بثها إلى المقسم المصرفي وتحرير رصيد العميل بنجاح."""
    }
}

# ==========================================
# PAY-14: A release-only native dependency fails on some hardware ABIs. What is your investigation and safe rollout plan?
# ==========================================
DATA["PAY-14"] = {
    "concept_en": """Resolving release-only native library failures across heterogeneous hardware Application Binary Interfaces (ABIs) requires deep binary triage, root-cause identification, and a guarded canary rollout:
- Common Root Causes of Release-Only Native Crashes:
  1. JNI Obfuscation by R8/ProGuard: In debug builds, symbol names match. In release builds, R8 renames Kotlin classes or native JNI bindings, causing `java.lang.UnsatisfiedLinkError` at runtime.
  2. ABI Incomplete Packaging: Third-party vendor `.so` files support `armeabi-v7a` but omit `arm64-v8a` or `x86_64`. When Android attempts to load a 64-bit zygote process, the 32-bit library fails to link.
  3. 16KB Page Size Alignment: Modern Android devices (Android 15+) require native `.so` ELF binaries to be aligned to 16KB boundaries; unaligned legacy binaries crash instantly with SIGSEGV.
  4. Native Compiler Optimizations: Aggressive `-O3` or link-time optimization (LTO) in release configurations triggering undefined behavior or memory alignment faults.
- Forensic Investigation Toolkit:
  - APK Analyzer: Inspect the `lib/` directory inside the generated APK/AAB to verify that all ABIs contain identical `.so` sets.
  - `readelf -d` and `objdump`: Inspect ELF headers for missing SONAMEs, 16KB alignment, and dynamic library dependencies.
  - Native Crash Tombs: Retrieve `/data/tombstones` or logcat traces and symbolize using `ndk-stack` with release symbol `.so` files.
- Controlled Canary Rollout Strategy:
  - Stage 1: Device-targeted internal testing on physical test racks covering all supported ABIs (`arm64-v8a`, `armeabi-v7a`, `x86_64`).
  - Stage 2: Phased Google Play rollout: 1% -> 5% -> 20% -> 100%, monitored against real-time crash dashboards (Firebase Crashlytics filtered by ABI and SoC).
  - Stage 3: Remote Config Feature Flag / Dynamic Kill-Switch: Capable of disabling the native hardware feature or falling back to software emulation if native crash rates exceed 0.05%.""",
    "walkthrough_en": """Investigating ABI issues and configuring defensive Gradle packaging in Kotlin DSL:
```kotlin
// build.gradle.kts (App level)
android {
    defaultConfig {
        ndk {
            // Explicitly define and filter supported target ABIs
            abiFilters.addAll(listOf("armeabi-v7a", "arm64-v8a"))
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            // Retain unstripped native debug symbols for crash symbolication
            ndk {
                debugSymbolLevel = "FULL"
            }
        }
    }
}

// proguard-rules.pro
// 1. Preserve JNI bridge classes and native method signatures
-keepclasseswithmembernames class * {
    native <methods>;
}
-keep class com.vendor.pos.nativebridge.** { *; }

// 2. Safe Dynamic Loading with Fallback Pattern in Kotlin
object NativeDriverLoader {
    private var isLoaded = false

    fun loadDriverSafely(): Boolean {
        if (isLoaded) return true
        return try {
            System.loadLibrary("vendor_emv_driver")
            isLoaded = true
            true
        } catch (e: UnsatisfiedLinkError) {
            PaymentLogger.e("FATAL: Native driver failed on ABI: ${Build.SUPPORTED_ABIS.joinToString()}", e)
            false // Graceful degradation to fallback software mode
        }
    }
}
```""",
    "short_en": """Investigate release-only native ABI crashes by inspecting APK ELF headers with readelf, symbolising tombstone stack traces with ndk-stack, and verifying R8 ProGuard keep rules for JNI bridges. Mitigate risks using strict Gradle ABI filters and execute a phased canary rollout with remote feature flags and graceful software fallback to prevent broad fleet outages.""",
    "structured_en": """Diagnosing and mitigating release-only native dependency crashes across hardware ABIs requires systematic forensic analysis and a staged deployment strategy.
These failures typically stem from R8 obfuscating JNI method signatures in release builds, mismatched 32-bit and 64-bit `.so` libraries across ABIs, or missing 16KB page alignments on newer Android OS versions.
Our investigation begins by examining the APK structure using APK Analyzer and readelf to verify binary symmetry and page alignment across all ABI folders. We inspect native tombstone crash dumps from affected devices, utilizing ndk-stack with unstripped debug symbols to locate the exact crashing C++ instruction.
To ensure a safe rollout, we configure ProGuard keep rules for all native bindings and define explicit ABI filters in Gradle.
We then execute a phased canary rollout via Google Play or our MDM platform, starting at one percent and progressing to five, twenty, and one hundred percent. Real-time Crashlytics dashboards track crash-free sessions sliced by hardware architecture, backed by a remote kill-switch that gracefully falls back to a software emulator if native initialization fails.""",
    "deep_senior_en": """From an Android NDK systems engineering, ABI toolchain compatibility, and enterprise release management perspective, release-only native crashes are among the most insidious bugs encountered on specialized POS hardware.
The discrepancy between debug and release behavior is primarily driven by three factors: the R8 shrinking pipeline, compiler optimization levels, and ABI library omissions.
In debug builds, R8 is disabled, preserving JNI class names; in release builds, unless explicit -keep rules protect both the native method declarations and the Java classes accessed via JNI reflection, the runtime throws UnsatisfiedLinkError or NoSuchMethodError. Furthermore, POS hardware fleets often mix legacy 32-bit armeabi-v7a chipsets with modern 64-bit arm64-v8a architectures. If a vendor supplies a closed-source .so file built only for 32-bit, the Android 64-bit zygote process will fail to link it unless the APK explicitly forces a 32-bit runtime environment via abiFilters.
The forensic investigation leverages readelf -l to verify that ELF memory segments adhere to 16KB boundary alignments required by modern Android runtimes. We extract device tombstones from /data/tombstones and pass them through ndk-stack mapped against the unstripped .so debug artifacts preserved during Gradle release builds.
For the rollout, we enforce a strict multi-tier containment plan. First, Gradle specifies full debugSymbolLevel to enable precise symbolication in Crashlytics.
Second, native driver initialization is wrapped in a defensive try-catch block catching UnsatisfiedLinkError, preventing application launch crashes and falling back to a cloud-assisted or software-degraded processing mode.
Third, deployment proceeds via a gradual canary schedule, gating progression behind zero-tolerance crash thresholds monitored by SoC and ABI slices. A remote kill-switch provides instantaneous rollback capability without requiring emergency hotfix releases.""",
    "meta_ar": {
        "id": "PAY-14",
        "questionAr": "تفشل مكتبة أصلية تعتمد على كود C/C++ في نسخ الإنتاج فقط على بعض معماريات العتاد (Hardware ABIs). كيف تحقق وتضع خطة إطلاق آمنة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تشخيص أخطاء المكتبات الأصلية (NDK/JNI Crashes)، تأثير أداة R8/ProGuard على دوال الـ Native، مشكلات عدم تطابق معماريات العتاد (arm64-v8a vs armeabi-v7a)، تحليل السجلات بـ ndk-stack، وخطة الإطلاق التدريجي الآمن (Canary Rollout).",
        "concept_ar": "يتطلب تشخيص وعلاج انهيار المكتبات الأصلية (Native .so Libraries) في نسخ الإنتاج فقط على بعض معماريات العتاد (ABIs) فحصاً ثنائياً دقيقاً ووضع استراتيجية نشر تدريجية محكمة: تحدث هذه المشكلة لعدة أسباب تقنية؛ أبرزها قيام أداة R8 في نسخة الإنتاج بتشويش أسماء الدوال أو الفئات التي يستدعيها كود C++ عبر JNI، أو عدم اكتمال ملفات المكتبات عبر كافة المعماريات (مثل توفر ملف `armeabi-v7a` وغياب `arm64-v8a`)، أو عدم توافق المكتبة القديمة مع محاذاة صفحات الذاكرة 16KB في إصدارات أندرويد الحديثة. ويشمل التحقيق فحص ملف الـ APK بأداة `readelf` ومحلل APK Analyzer للتأكد من تناسق مجلدات `lib/`، وتحليل سجلات الانهيار (Tombstones) باستخدام `ndk-stack` وملفات الرموز المشفرة. أما خطة الإطلاق الآمنة فتعتمد على: وضع قواعد ProGuard لحماية دوال JNI، وإلزام Gradle بمعماريات محددة، والإطلاق التدريجي بنسب تبدأ من 1% ثم 5% ثم 20%، وتغليف تحميل المكتبة بكتلة حماية تلتقط `UnsatisfiedLinkError` للتحول لوضع تشغيل برمجي بديل عند فشل العتاد.",
        "walkthrough_ar": """ضبط حماية دوال NDK في Gradle وكتابة كود التحميل الآمن في كوتلن:
```kotlin
// إعدادات ملف build.gradle.kts لتحديد المعماريات وحفظ الرموز
android {
    defaultConfig {
        ndk {
            // حصر المعماريات المدعومة رسمياً من أجهزة نقاط البيع
            abiFilters.addAll(listOf("armeabi-v7a", "arm64-v8a"))
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            // حفظ ملفات الرموز كاملة لفك شفرة الانهيارات في Crashlytics
            ndk {
                debugSymbolLevel = "FULL"
            }
        }
    }
}

// كود التحميل الآمن للمكتبة الأصلية مع توفير مسار بديل عند الفشل
object NativeDriverLoader {
    private var isLoaded = false

    fun loadDriverSafely(): Boolean {
        if (isLoaded) return true
        return try {
            System.loadLibrary("vendor_emv_driver")
            isLoaded = true
            true
        } catch (e: UnsatisfiedLinkError) {
            PaymentLogger.e("فشل تحميل مشغل العتاد للمعمارية الحالية: ${Build.SUPPORTED_ABIS.joinToString()}", e)
            false // التحول للوضع البرمجي البديل دون انهيار التطبيق
        }
    }
}
```""",
        "why_it_matters_ar": "انهيار المكتبات الأصلية في الإنتاج يتسبب في إغلاق التطبيق فوراً في أيدي الكاشير وشلل نقاط البيع بالمتاجر وخسائر تجارية هائلة.",
        "worked_example_ar": "انهار التطبيق على أجهزة POS الحديثة ذات معمارية 64-bit لأن مكتبة المورد كانت 32-bit فقط؛ اكتشفنا ذلك بـ APK Analyzer وألزمنا Gradle بالعمل بنمط 32-bit حتى قام المورد بتحديث مكتبته.",
        "trade_offs_ar": "حفظ ملفات الرموز واستخدام قواعد ProGuard الصارمة يمنع ضغط الكود لأقصى درجة؛ لكنه يمنع انهيار النظام ويضمن سرعة تشخيص أخطاء الذاكرة.",
        "failure_modes_ar": "أخطر الأخطاء هو ترك System.loadLibrary دون try-catch؛ فإذا فشلت المكتبة ينهار التطبيق عند الفتح فوراً دون قدرة على إرسال تقرير خطأ.",
        "production_perspective_ar": "في الشركات الكبرى، يُحظر إطلاق أي تحديث لـ 100% من الأجهزة دفعة واحدة، ويُستخدم نظام الإطلاق المرحلي Canary مقسماً حسب معمارية المعالج SoC.",
        "how_to_answer_ar": "ابدأ ببيان أسباب حدوث الخطأ في Release فقط (R8 وJNI والمعماريات)، واشرح أدوات التحقيق مثل readelf وndk-stack، ثم اعرض خطة الإطلاق التدريجي Canary والتحميل الآمن.",
        "talking_points_ar": "أخطاء UnsatisfiedLinkError، معمارية العتاد ABIs، تشويش R8، تحليل Tombstones عبر ndk-stack، قواعد ProGuard، الإطلاق التدريجي Canary، وقواطع الأعطال Kill-Switch.",
        "follow_ups_ar": "كيف تتأكد من توافق ملفات الـ .so مع معيار محاذاة صفحات الذاكرة 16KB في أندرويد 15؟",
        "self_check_ar": "هل فرقت بين سلوك Debug وRelease، وشرحت أدوات التحقيق، وأكدت على قواعد الحماية والإطلاق التدريجي مع مسار بديل؟",
        "references_ar": f"- [Android NDK: ABI Management and 64-bit compatibility](https://developer.android.com/ndk/guides/abis) — الدليل الرسمي لإدارة معماريات المعالجات المختلفة وتوافق مكتبات C++ في أندرويد.\n- [Android Developers: Support 16 KB page sizes](https://developer.android.com/guide/practices/page-sizes) — الدليل الإرشادي الإلزامي لضمان محاذاة المكتبات الأصلية لصفحات الذاكرة 16KB.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نحقق في انهيار المكتبات الأصلية في الإنتاج بفحص ملفات الـ APK بأداة readelf للتأكد من وجود المكتبة لكافة المعماريات، وفك شفرة سجلات الانهيار بـ ndk-stack، وضمان عدم تشويش دوال JNI بواسطة R8. ونضع خطة إطلاق آمنة تلتقط UnsatisfiedLinkError لمنع الانهيار، مع الإطلاق التدريجي Canary من 1% وربطه بقاطع أعطال سحابي.""",
        "best_answer_ar": """يتطلب حل مشكلة انهيار المكتبات الأصلية في نسخ الإنتاج فقط تحقيقاً تقنياً في ملفات البناء وخطة نشر محكمة تحمي أسطول أجهزة نقاط البيع.
يحدث هذا الخلل عادة لثلاثة أسباب رئيسية: قيام أداة R8 بتشويش أسماء فئات JNI في نسخة الإنتاج، أو عدم اكتمال ملفات المكتبة عبر كافة معماريات العتاد كتوفر ملفات 32-bit وغياب 64-bit، أو عدم التوافق مع محاذاة الذاكرة 16KB.
يبدأ التحقيق بفحص ملف الـ APK عبر APK Analyzer وreadelf للتأكد من تماثل مجلدات lib وتوافق ترويسات ELF، مع استخدام أداة ndk-stack وملفات الرموز المحفوظة لتحليل سجلات الانهيار Tombstones ومعرفة سطر C++ المسبب للمشكلة.
ولضمان الإطلاق الآمن، نضيف قواعد حماية صارمة في ProGuard لمنع المساس بدوال JNI، ونغلف تحميل المكتبة بكتلة حماية ترصد خطأ UnsatisfiedLinkError وتنتقل لوضع برمجي بديل بدلاً من انهيار التطبيق.
ثم نطلق التحديث عبر مراحل تدريجية تبدأ بنسبة واحد بالمئة ثم خمسة ثم عشرين بالمئة، مع مراقبة مؤشرات الاستقرار حسب نوع المعالج واستخدام قاطع أعطال سحابي للإيقاف الفوري عند الضرورة.""",
        "deep_answer_ar": """من منظور هندسة بيئات أندرويد المدمجة وتوافق أدوات NDK وإدارة الإصدارات المؤسسية، تمثل انهيارات الكود الأصلي في نسخ الإنتاج أخطر العيوب التي قد تصيب أساطيل أجهزة الدفع.
يرجع التباين بين نسختي التطوير والإنتاج إلى سلوك أداة الضغط R8 ومستويات تحسين المترجم؛ ففي نسخة التطوير تبقى الرموز كما هي، بينما تقوم أداة R8 في الإنتاج بتغيير أسماء الفئات والواجهات البرمجية، فإذا استدعى كود C++ عبر واجهة JNI دالة جافا محرفة الاسم ينهار المعالج فوراً بخطأ UnsatisfiedLinkError. وعلاوة على ذلك، يجمع أسطول نقاط البيع بين شرائح معالجة قديمة تعمل بمعمارية armeabi-v7a وشرائح حديثة تعمل بـ arm64-v8a؛ فإذا أهمل المورد تضمين مكتبات 64-bit يفشل النظام في ربط الدوائر البرمجية.
ويعتمد التحقيق الجنائي على استخراج ملفات الانهيار من مسار tombstones وتمريرها عبر ndk-stack مدعومة بملفات الرموز الكاملة المخرجة من البناء لتحديد السطر المنهار في كود C++. كما نتحقق بأمر readelf من محاذاة قطاعات الذاكرة لحدود 16KB الإلزامية في أندرويد الحديث.
أما خطة الإطلاق الآمن فتعتمد على استراتيجية الاحتواء؛ حيث نلزم Gradle بحصر المعماريات المعتمدة، ونحمي دوال JNI بقواعد keep صارمة.
كما نغلف عملية استدعاء المكتبة بنمط تحميل دفاعي يلتقط الخطأ البرمجي ويتحول فوراً للوضع البرمجي الاحتياطي لمنع سقوط شاشة الكاشير.
ثم نطلق التحديث بنظام المراحل Canary، مراقبين مؤشرات Crashlytics المفصلة حسب معمارية المعالج ومزودة بقاطع تشغيل عن بُعد يتيح تعطيل الميزة بلحظة واحدة دون انتظار مراجعات المتاجر."""
    }
}

# ==========================================
# PAY-15: The server is unreachable when a reversal is due. How do you guarantee eventual delivery without duplicates?
# ==========================================
DATA["PAY-15"] = {
    "concept_en": """Guaranteeing eventual delivery of financial reversals during prolonged server outages without risking duplicate execution requires a persistent transactional outbox, idempotent protocol design, and exponential backoff:
- The Distributed Outage Dilemma:
  - When a transaction times out, a reversal must reach the banking switch to void the hold.
  - However, if the bank switch or cellular gateway remains unreachable for hours, volatile retries will fail and terminate upon device reboot or app closure.
- The Architectural Solution:
  1. Persistent Reversal Outbox:
     - The reversal intent is saved in a local SQLite table (`reversal_queue`) with Write-Ahead Logging and `PRAGMA synchronous = FULL`.
     - The record contains the original transaction's immutable parameters: `originalStan` (Systems Trace Audit Number), `originalRrn` (Retrieval Reference Number), `originalAmount`, and `correlationId`.
  2. Background Execution Engine (WorkManager):
     - A periodic and one-time `CoroutineWorker` is scheduled with `BackoffPolicy.EXPONENTIAL` and network constraints (`NetworkType.CONNECTED`).
     - Survives device reboots via `ExistingWorkPolicy.KEEP` and continues retrying over hours or days without battery drain.
  3. Strict Idempotent Banking Semantics:
     - ISO 8583 message 0400/0420 reversals are inherently idempotent by design when referencing the original transaction identifiers.
     - If the switch receives the same reversal multiple times due to unacknowledged delivery packets, it recognizes the original STAN/RRN, marks the hold as already reversed, and returns a success response (`00`) without creating duplicate balance credits.
  4. Poison-Pill Quarantine:
     - If the server responds with a definitive non-retryable response (e.g., `Invalid Card`, `Batch Already Settled`), the record is moved to an `orphaned_reversals` dead-letter table for end-of-day manual ledger reconciliation rather than retrying indefinitely.""",
    "walkthrough_en": """Implementing a resilient persistent reversal delivery worker in Kotlin:
```kotlin
class ResilientReversalWorker(
    appContext: Context,
    workerParams: WorkerParameters,
    private val reversalDao: ReversalQueueDao,
    private val paymentSwitchApi: PaymentSwitchApi
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val pending = reversalDao.getNextPendingReversal() ?: return Result.success()

        return try {
            // Reversals MUST use the exact original STAN and RRN to guarantee backend idempotency
            val response = paymentSwitchApi.sendIsoReversal(
                originalStan = pending.originalStan,
                originalRrn = pending.originalRrn,
                amountCents = pending.amountCents,
                correlationId = pending.correlationId
            )

            when (response.actionCode) {
                // 00 = Approved/Reversed successfully, 94 = Already Reversed (Idempotent Success)
                "00", "94" -> {
                    reversalDao.delete(pending.id)
                    Result.success()
                }
                // Terminal rejection codes: Quarantine to dead-letter queue for manual reconciliation
                "25", "12" -> {
                    reversalDao.markQuarantined(pending.id, response.actionCode)
                    Result.success()
                }
                else -> {
                    // Transient switch error: trigger exponential backoff retry
                    reversalDao.incrementAttempt(pending.id)
                    Result.retry()
                }
            }
        } catch (e: IOException) {
            // Network completely unreachable: WorkManager will back off and retry automatically
            reversalDao.incrementAttempt(pending.id)
            Result.retry()
        }
    }
}
```""",
    "short_en": """Guarantee eventual delivery of reversals during server outages using a persistent SQLite Outbox table managed by WorkManager with exponential backoff and network constraints. Prevent duplicate credits by strictly reusing original transaction identifiers like STAN and RRN, ensuring the banking switch processes the reversal idempotently regardless of delivery attempts.""",
    "structured_en": """Guaranteeing eventual delivery of payment reversals when the server is unreachable requires combining local persistence with idempotent messaging protocols.
When a transaction times out and a reversal is required, relying on in-memory retries is insufficient because an extended network outage or terminal reboot will erase the task.
Instead, we implement the Transactional Outbox pattern. The reversal payload is durably written to a dedicated SQLite table using Room, preserving original identifiers like the Systems Trace Audit Number and Retrieval Reference Number.
A WorkManager worker configured with network connectivity constraints and exponential backoff polls this table. It operates persistently across device restarts and battery recharges, repeatedly attempting delivery once connectivity returns.
To guarantee that retrying never creates duplicate credits, the reversal request is designed to be strictly idempotent. By referencing the original transaction STAN and amount, the banking switch processes the first arrival and safely acknowledges any subsequent duplicate submissions with an idempotent success code, purging the local queue cleanly.""",
    "deep_senior_en": """From an ISO 8583 protocol engineering, distributed ledger consistency, and store-and-forward architectural standpoint, delivering reversals across extended network partitions is a classic manifestation of the Guaranteed Delivery pattern.
In rural or mobile retail environments, an Android POS terminal can lose cellular connectivity for hours due to localized tower failures or tunnel transit. If a transaction enters an in-doubt state right before connectivity drops, failing to deliver the reversal leaves the cardholder\'s credit line tied up in a pending authorization hold, sparking customer outrage and merchant chargebacks.
The enterprise architectural solution deploys a hardened Store-and-Forward (SaF) engine backed by SQLite and WorkManager.
The reversal intent is recorded into a persistent queue table as an immutable record. Crucially, the payload must replicate the exact cryptographic and operational identifiers of the original authorization: the Systems Trace Audit Number (STAN), the Retrieval Reference Number (RRN), the local transaction timestamp, and the exact amount.
WorkManager orchestrates execution using a BackoffPolicy.EXPONENTIAL policy, ensuring that retries do not exhaust battery life or flood recovering network towers.
The ultimate safeguard against duplicate financial execution is backend protocol idempotency. Under ISO 8583 standards, message types 0400 and 0420 are intrinsically idempotent when anchored by the original STAN and RRN. When the server receives the first reversal packet, it voids the authorization and releases the cardholder funds. If network instability drops the server\'s ACK packet and the terminal retransmits the reversal ten minutes later, the switch detects that the referenced authorization has already been reversed, suppresses any secondary credit mutations, and returns a benign success response (Action Code 00 or 94).
Upon receiving this authoritative acknowledgement, the terminal purges the record from the queue, achieving absolute ledger parity across intermittent networks.""",
    "meta_ar": {
        "id": "PAY-15",
        "questionAr": "الخادم غير متاح عندما حان موعد إرسال رسالة العكس (Reversal). كيف تضمن التسليم الحتمي للرسالة دون تكرارها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "نمط التخزين والإرسال لاحقاً (Store-and-Forward / Outbox Pattern)، جدولة المهام المستمرة بـ WorkManager مع التراجع الأسي، حتمية بروتوكول العكس في ISO 8583، ومنع تكرار القيود المالية.",
        "concept_ar": "يتطلب ضمان التسليم الحتمي لرسائل العكس (Reversals) عند انقطاع خادم البنك دون تكرار العملية المالية الجمع بين نمط صندوق الصادر الدائم (Transactional Outbox) وحتمية بروتوكول الدفع: عند تعذر الوصول للخادم لساعات، تفشل المحاولات اللحظية وتتبخر مع إغلاق الجهاز؛ لذا يُحفظ طلب العكس في جدول دائم بقاعدة بيانات SQLite بـ Room، متضمناً المعطيات الأصلية للمعاملة: رقم التدقيق (STAN)، ورقم المرجع (RRN)، والمبلغ الأصلي، ومعرّف الارتباط. ثم تُسند مهمة الإرسال لـ WorkManager مقترناً بشرط توفر الشبكة `NetworkType.CONNECTED` وسياسة تراجع أسي (Exponential Backoff)؛ فيصمد الطابور عبر انقطاع الكهرباء وإعادة التشغيل. وتتحقق الوقاية من التكرار بفضل الطبيعة الحتمية لرسائل العكس ISO 8583 0400؛ فحين يستقبل الخادم نفس رسالة العكس مكررة بسبب انقطاع باقة التأكيد، يتعرف على رقم التدقيق الأصلي STAN ويعلم أن العملية ملغاة بالفعل، فيرجع كود نجاح `00` أو `94` دون تكرار إضافة أي أموال؛ مما يسمح للتطبيق بحذف السجل من الطابور بأمان تام.",
        "walkthrough_ar": """تطبيق عامل إرسال العكس الحتمي المقاوم لانقطاع الخادم في كوتلن:
```kotlin
class ResilientReversalWorker(
    appContext: Context,
    workerParams: WorkerParameters,
    private val reversalDao: ReversalQueueDao,
    private val paymentSwitchApi: PaymentSwitchApi
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val pending = reversalDao.getNextPendingReversal() ?: return Result.success()

        return try {
            // إرسال العكس بنفس أرقام STAN وRRN الأصلية لضمان الحتمية في البنك
            val response = paymentSwitchApi.sendIsoReversal(
                originalStan = pending.originalStan,
                originalRrn = pending.originalRrn,
                amountCents = pending.amountCents,
                correlationId = pending.correlationId
            )

            when (response.actionCode) {
                // 00 = تم العكس بنجاح، 94 = معكوسة مسبقاً (نجاح حتمي)
                "00", "94" -> {
                    reversalDao.delete(pending.id)
                    Result.success()
                }
                // أكواد الرفض النهائي: تُعزل في طابور الحالات الخاصة للمراجعة اليدوية
                "25", "12" -> {
                    reversalDao.markQuarantined(pending.id, response.actionCode)
                    Result.success()
                }
                else -> {
                    // عطل مؤقت في خادم البنك: إعادة المحاولة بتراجع أسي
                    reversalDao.incrementAttempt(pending.id)
                    Result.retry()
                }
            }
        } catch (e: IOException) {
            // الشبكة مقطوعة بالكامل: سيعيد WorkManager المحاولة تلقائياً لاحقاً
            reversalDao.incrementAttempt(pending.id)
            Result.retry()
        }
    }
}
```""",
        "why_it_matters_ar": "فقدان رسالة العكس عند تعطل خادم البنك يعلق رصيد العميل لأسابيع ويؤدي لغرامات تدقيق مالي وشكاوى احتيال ضد التاجر.",
        "worked_example_ar": "انقطع خادم الدفع لمدة ساعتين؛ حفظ الجهاز طلب العكس في جدول الفلاش بـ STAN محدد؛ وبمجرد عودة الخادم أرسل WorkManager الطلب تلقائياً، فألغى البنك الحجز بنجاح دون أي تكرار.",
        "trade_offs_ar": "التخزين الدائم وإعادة المحاولة المستمرة تستهلك جهداً برمجياً في بناء طابور Outbox؛ لكنها تحمي النظام من الفجوات المحاسبية والنزاعات القضائية.",
        "failure_modes_ar": "أخطر الأخطاء هو توليد رقم STAN جديد لطلب العكس بدلاً من استخدام الرقم الأصلي؛ مما يدفع البنك لاعتبارها عملية جديدة ويرفضها أو يعلق القيود.",
        "production_perspective_ar": "في كود الإنتاج المصرفي، تُعزل الطلبات التي تفشل لأسباب نهائية (مثل تسوية الدفعة مسبقاً) في جدول Dead-Letter Queue لحسمها يدوياً في تقرير Z-Report.",
        "how_to_answer_ar": "ابدأ بشرح نمط Store-and-Forward وصندوق الصادر Outbox، ووضح دور WorkManager في البقاء عبر إعادة التشغيل، ثم أكد على حتمية رسائل ISO 8583 عبر أرقام STAN الأصلية.",
        "talking_points_ar": "نمط التخزين والإرسال Store-and-Forward، صندوق الصادر Outbox، جدولة WorkManager، التراجع الأسي، حتمية رسائل ISO 8583، وأكواد الرد 00 و94.",
        "follow_ups_ar": "ماذا تفعل إذا أرجع البنك كود يفيد بأن الدفعة اليومية قد أُغلقت بالفعل (Batch Closed) قبل وصول رسالة العكس؟",
        "self_check_ar": "هل أكدت على التخزين الدائم في SQLite، واستخدام نفس أرقام المعاملة الأصلية، وشرحت كيف تمنع الحتمية في البنك تكرار القيود؟",
        "references_ar": f"- [ISO 8583 Financial Transaction Card Originated Messages Specifications](https://www.iso.org/standard/31628.html) — المعيار الدولي المعتمد لرسائل التبادل المالي وعمليات العكس والحتمية المصرفية.\n- [Martin Fowler: Transactional Outbox and Guaranteed Delivery](https://martinfowler.com/) — النمط المعماري لضمان تسليم الرسائل عبر الشبكات المتقطعة دون فقدان أو تكرار.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نضمن تسليم رسالة العكس الحتمي عند انقطاع الخادم بتخزينها بشكل دائم في جدول Outbox بقاعدة بيانات SQLite وإدارتها عبر WorkManager بتراجع أسي وشرط توفر الشبكة لتعمل حتى بعد إعادة تشغيل الهاتف. ونمنع التكرار المالي بإعادة إرسال نفس أرقام المعاملة الأصلية STAN وRRN؛ فيتعامل البنك معها بحتمية تامة ويلغي الحجز دون مضاعفة القيود.""",
        "best_answer_ar": """يتطلب ضمان التسليم الحتمي لرسائل العكس أثناء انقطاع خوادم الدفع الجمع بين الحفظ الدائم محلياً والتصميم الحتمي لبروتوكول الاتصال المصرفي.
فعند تعذر الاتصال بالخادم، لا يمكن الاعتماد على محاولات الذاكرة العشوائية لأن إعادة تشغيل الجهاز ستمحو المهمة تماماً.
ولحل ذلك، نطبق نمط صندوق الصادر التبادلي Transactional Outbox؛ حيث يُحفظ طلب العكس في جدول دائم بقاعدة بيانات SQLite بـ Room حاملاً المعرفات الأصلية للعملية كرقم التدقيق STAN ورقم المرجع RRN والمبلغ.
وتتولى مهمة خلفية مستمرة عبر WorkManager إدارة عملية الإرسال؛ حيث تُضبط بشرط توفر الاتصال الشبكي وسياسة تراجع أسي تحمي البطارية وتصمد أمام انقطاع الطاقة وإعادة التشغيل.
أما صمام الأمان ضد تكرار القيود المالية فهو الحتمية الأصيلة لبروتوكول ISO 8583؛ حيث يضمن استخدام نفس أرقام العملية الأصلية أن الخادم عند استلام الطلب مكرراً يتعرف عليه ويلغي التفويض دون إنشاء أي قيود دفع مكررة، مؤكداً استلام العملية بكود نجاح رسمي لحذفها من طابور الهاتف نهائياً.""",
        "deep_answer_ar": """من منظور معايير التحويل المالي الدولية ISO 8583 وهندسة التخزين والإرسال لاحقاً Store-and-Forward، يمثل إرسال العكس عبر شبكات منقطعة تطبيقاً عملياً صارماً لنمط التسليم المضمون Guaranteed Delivery.
في بيئات العمل الميدانية، قد تفقد أجهزة نقاط البيع الاتصال اللاسلكي لساعات نتيجة أعطال الأبراج الخلوية أو العمل في طوابق سفلية. فإذا نشأت حالة شك في تلك اللحظة وتلاشت مهمة العكس من الذاكرة، تظل أموال العميل مجمدة في البنك، مما يعرض التاجر لخسائر فادحة ونزاعات مصرفية.
والتصميم المعماري الرصين يبدأ بتثبيت طلب العكس داخل جدول reversal_queue بقاعدة بيانات SQLite بنمط الكتابة المسبقة؛ ليبقى السجل محصناً ضد نفاد الطاقة.
ويجب أن يحمل هذا السجل صورة طبق الأصل من محددات التفويض الأصلي: رقم التدقيق المصرفي STAN، ورقم مرجع الاسترجاع RRN، والوقت الدقيق، والمبلغ المحجوز.
يتولى محرك WorkManager إدارة الجدولة بسياسة تراجع أسي مدروسة تحافظ على موارد الجهاز.
وعند استعادة الاتصال ووصول الرسالة للخادم، تتدخل قواعد الحتمية المصرفية؛ فخادم المقسم البنكي يطابق رسالة ISO 8583 0400 مع سجل التفويض الأصلي، فيقوم بإلغاء الحجز فوراً. وإذا تسببت تقلبات الشبكة في إعادة إرسال نفس الطلب بعد دقائق، يكتشف الخادم أن العملية معكوسة بالفعل، فيمتنع عن إجراء أي تعديل مالي مكرر ويرجع كود النجاح الحتمي 00 أو 94، مما يمكن نقطة البيع من تنظيف الطابور وإتمام دورة المعاملة بتطابق محاسبي بنسبة مئة بالمئة."""
    }
}

# ==========================================
# Validation & Runner logic
# ==========================================
def validate_words():
    print("Checking word counts and spoken style for PAY-09 to PAY-15...")
    for qid, d in sorted(DATA.items()):
        # Short answer (35 - 110)
        c_short = len(d["short_en"].split())
        assert 35 <= c_short <= 110, f"{qid}: short_en word count {c_short} out of range (35-110)"

        # Structured answer (100 - 280)
        c_struct = len(d["structured_en"].split())
        assert 100 <= c_struct <= 280, f"{qid}: structured_en word count {c_struct} out of range (100-280)"

        # Deep senior answer (200 - 650)
        c_deep = len(d["deep_senior_en"].split())
        assert 200 <= c_deep <= 650, f"{qid}: deep_senior_en word count {c_deep} out of range (200-650)"

        meta = d["meta_ar"]
        # Quick answer AR (35 - 110)
        c_qar = len(meta["quick_answer_ar"].split())
        assert 35 <= c_qar <= 110, f"{qid}: quick_answer_ar word count {c_qar} out of range (35-110)"

        # Best answer AR (90 - 280)
        c_bar = len(meta["best_answer_ar"].split())
        assert 90 <= c_bar <= 280, f"{qid}: best_answer_ar word count {c_bar} out of range (90-280)"

        # Deep answer AR (180 - 650)
        c_dar = len(meta["deep_answer_ar"].split())
        assert 180 <= c_dar <= 650, f"{qid}: deep_answer_ar word count {c_dar} out of range (180-650)"

        # Check spoken style (no bullets, no numbered lists)
        for field_name, text in [
            ("structured_en", d["structured_en"]),
            ("deep_senior_en", d["deep_senior_en"]),
            ("best_answer_ar", meta["best_answer_ar"]),
            ("deep_answer_ar", meta["deep_answer_ar"]),
        ]:
            assert not any(line.strip().startswith(("-", "*", "•")) for line in text.splitlines()), f"{qid}: {field_name} contains bullets"
            assert not any(line.strip() and line.strip()[0].isdigit() and line.strip()[1:3] in (". ", ") ") for line in text.splitlines()), f"{qid}: {field_name} contains numbered list"

        assert "على الجانب الآخر، فيما يخص" not in meta["best_answer_ar"], f"{qid}: best_answer_ar contains cliché"
        assert "على الجانب الآخر، فيما يخص" not in meta["deep_answer_ar"], f"{qid}: deep_answer_ar contains cliché"

    print("Pre-validation word count checks passed! Updating canonical questions...")

def apply_elevations():
    validate_words()

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"],
            short_en=d["short_en"],
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("pay_09_15", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\nAll {len(DATA)} PAY questions (PAY-09 to PAY-15) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
