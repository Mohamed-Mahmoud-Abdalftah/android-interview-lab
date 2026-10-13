#!/usr/bin/env python3
"""Generator for PAY-09 through PAY-15 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "pay.json"

PAY_09_15 = [
    {
        "id": "PAY-09",
        "arabic_explanation": (
            "كيف تقوم بعزل حزم الـ SDK الخاصة بالعتاد وقراءة البطاقات الذكية (Hardware / EMV SDKs) وراء واجهة برمجية نظيفة وقابلة للاختبار؟\n\n"
            "1. طبيعة الـ EMV SDKs التجارية السيئة:\n"
            "   - حزم الـ SDK الخاصة بماكينات الدفع (مثل Pax, Verifone, Ingenico, Sunmi) غالباً ما تملك أسوأ تصميم برمجي ممكن:\n     * تعتمد على كائنات أحادية ثابتة عامة (`TerminalHelper.getInstance()`).\n     * تستخدم استدعاءات C/C++ معقدة (JNI) ومصفوفات بايت خام (TLV - Tag Length Value).\n     * تستخدم Callbacks قديمة وغير متزامنة وتسبب تسريبات ذاكرة.\n     * يستحيل تشغيلها على محاكي أندرويد العادي لعدم وجود هاردوير حقيقي، مما يعطل كتابة الـ Unit Tests.\n\n"
            "2. نمط التصميم المعماري للعزل (The Hardware Adapter Pattern):\n   - **1. واجهة نظيفة معتمدة على الكوتلن (Domain Interface)**:\n     * تعريف `CardReaderManager` تتعامل مع نماذج نظيفة (`CardData`, `ReaderEvent`) وتستخدم Kotlin `Flow` للأحداث المتدفقة.\n   - **2. محول العتاد الحقيقي (Concrete Hardware Adapter)**:\n     * كلاس `PaxCardReaderAdapter` هو الوحيد الذي يرى الـ SDK، ويقوم بتحويل الـ Callbacks إلى `callbackFlow` مع إدارة آمنة للـ Coroutine Scope وحذف المستمعات عند الإغلاق.\n   - **3. قارئ وهمي كامل للاختبارات (FakeCardReaderManager)**:\n     * يتيح للمطورين محاكاة تمرير البطاقة، وإدخال الـ PIN، ومحاكاة أعطال العتاد بضغطة زر داخل المحاكي دون الحاجة لماكينة حقيقية."
        ),
        "practical_walkthrough": (
            "كود معماري يوضح عزل الـ EMV SDK وراء Kotlin Flow و Interface نظيف:\n"
            "```kotlin\n"
            "// 1. الواجهة العامة في طبقة الـ Domain (نظيفة 100% وخالية من كود العتاد):\n"
            "sealed interface CardReaderEvent {\n"
            "    object WaitingForCard : CardReaderEvent\n"
            "    object CardInserted : CardReaderEvent\n"
            "    object PinRequired : CardReaderEvent\n"
            "    data class CardReadSuccess(val cardToken: String, val maskedPan: String) : CardReaderEvent\n"
            "    data class ReaderError(val errorCode: Int, val message: String) : CardReaderEvent\n"
            "}\n"
            "\n"
            "interface CardReaderManager {\n"
            "    fun startCardInteraction(amountCents: Long): Flow<CardReaderEvent>\n"
            "    suspend fun cancelInteraction()\n"
            "}\n"
            "\n"
            "// 2. المحول الفعلي الذي يعزل الـ SDK الخبيثة باستخدام callbackFlow:\n"
            "class VendorEmvCardReaderAdapter(private val vendorSdk: ProprietaryVendorSdk) : CardReaderManager {\n"
            "    override fun startCardInteraction(amountCents: Long): Flow<CardReaderEvent> = callbackFlow {\n"
            "        val listener = object : ProprietaryEmvListener {\n"
            "            override fun onCardDetected() { trySend(CardReaderEvent.CardInserted) }\n"
            "            override fun onPinRequested() { trySend(CardReaderEvent.PinRequired) }\n"
            "            override fun onEmvComplete(tlvData: ByteArray) {\n"
            "                val parsedToken = parseTlvToToken(tlvData)\n"
            "                trySend(CardReaderEvent.CardReadSuccess(parsedToken, \"4111****1111\"))\n"
            "                close()\n"
            "            }\n"
            "            override fun onError(code: Int, msg: String) {\n"
            "                trySend(CardReaderEvent.ReaderError(code, msg))\n"
            "                close()\n"
            "            }\n"
            "        }\n"
            "        vendorSdk.registerListener(listener)\n"
            "        vendorSdk.startTransaction(amountCents)\n"
            "        awaitClose { vendorSdk.unregisterListener(listener); vendorSdk.abort() }\n"
            "    }\n"
            "    override suspend fun cancelInteraction() { vendorSdk.abort() }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Isolate proprietary hardware and EMV SDKs behind an abstract domain interface (CardReaderManager) using the Adapter pattern. Bridge legacy C/JNI callbacks into idiomatic Kotlin Coroutines Flows via callbackFlow, and provide a full-fidelity Fake implementation for unit testing and emulator-based development.",
        "best_answer": (
            "Proprietary POS hardware and EMV chip-reader SDKs exhibit severe architectural anti-patterns that require strict isolation:\n\n"
            "1. **Defects of Commercial Payment SDKs**:\n"
            "   - Vendor SDKs (Pax, Verifone, Sunmi, Ingenico) frequently mandate static singletons, untyped byte arrays (EMV TLV tags), blocking native JNI calls, and undocumented lifecycle memory leaks. Leaking vendor classes into UI or domain modules irreparably couples the application to specific hardware revisions.\n\n"
            "2. **The Hardware Adapter Pattern**:\n"
            "   - **Pure Domain Abstraction**: Define a clean `CardReaderManager` interface exposing idiomatic Kotlin sealed interfaces (`CardReaderEvent.WaitingForCard`, `CardReaderEvent.PinRequired`, `CardReaderEvent.Success`).\n   - **Reactive Bridge via `callbackFlow`**: The adapter encapsulates vendor callbacks into a cold Kotlin `Flow`. Using `awaitClose { vendorSdk.abort() }` guarantees hardware teardown and unregisters memory-leaking listeners when the subscriber cancels.\n\n"
            "3. **Decoupled Testability via In-Memory Fakes**:\n"
            "   - Because proprietary native `.so` binaries fail to link on host JVMs or standard Android x86 emulators, an in-memory `FakeCardReaderManager` is essential. It enables full UI automated testing and CI verification without requiring physical $500 hardware terminals."
        ),
        "deep_answer": (
            "From an EMV Level 2 kernel compliance and POS threading perspective, adapter implementation requires systems discipline:\n\n"
            "1. **Threading and JNI Isolation**: Vendor EMV kernels often invoke callbacks directly from arbitrary OS native POS threads. The adapter must sanitize thread contexts, dispatching events onto controlled background coroutine dispatchers (`Dispatchers.IO`) before touching Android framework state.\n\n"
            "2. **Hardware Re-Entrancy & Mutexes**: Most physical EMV readers crash or lock up permanently if `startTransaction` is invoked while a previous card read session is in progress. The adapter must wrap hardware invocations in an internal `Mutex` with timeout protection to prevent concurrent native state collisions.\n\n"
            "3. **Multi-Vendor Dependency Injection**: In white-label POS applications supporting multiple hardware vendors (e.g. running on both Pax A920 and Sunmi V2s), use Dagger/Hilt qualifier annotations or build flavor bindings to inject the matching adapter dynamically based on device build manufacturer (`Build.MANUFACTURER`)."
        ),
        "follow_ups": [
            {
                "question": "Why is `callbackFlow` the ideal Kotlin construct for wrapping hardware SDK callbacks?",
                "answer": "Because it converts asynchronous multi-event callbacks into a reactive Flow while ensuring guaranteed hardware cleanup via `awaitClose` upon cancellation."
            },
            {
                "question": "How do you run automated UI tests for POS flows without physical payment terminals?",
                "answer": "By injecting a `FakeCardReaderManager` that simulates card taps, chip reads, and timeouts programmatically in memory on standard emulators."
            }
        ]
    },
    {
        "id": "PAY-10",
        "arabic_explanation": (
            "كيف تجعل تدفق المعاملات المالية عالي المراقبة (Observable) دون تسريب بيانات البطاقات الحساسة (PAN / PIN / CVV) أو انتهاك معايير PCI-DSS؟\n\n"
            "1. معايير أمان بيانات بطاقات الدفع (PCI-DSS Strict Rules):\n"
            "   - **المعيار 3 من PCI-DSS**: يحظر تماماً تخزين أو كتابة أي من البيانات التالية في ملفات الـ Logs أو الذاكرة الدائمة:\n     * **رقم البطاقة الكامل (Full PAN - 16 Digits)**: يُسمح فقط بالنسخة المقنعة (Masked: أول 6 أرقام وآخر 4 أرقام فقط: `4111 11** **** 1111`).\n     * **رمز الأمان (CVV / CVC)**: حظر كامل ومطلق.\n     * **الرقم السري أو كتلته المشفرة (PIN / PIN Block)**: حظر كامل ومطلق.\n     * **بيانات الشريط المغناطيسي (Full Magnetic Stripe Track Data)**: حظر كامل.\n   - تسجيل أي من هذه البيانات في Logcat أو إرسالها لـ Datadog/Crashlytics يعتبر كارثة قانونية تسحب ترخيص الدفع فوراً.\n\n"
            "2. المراقبة الآمنة والقانونية (Safe Observability Architecture):\n   - **1. الاعتماد على المعرفات البديلة والرموز (Tokenized References)**:\n     * استخدام `Correlation ID` و `Payment Token` (مثل `tok_1N3k...`) للربط بين العمليات.\n   - **2. تسجيل أحداث دورة الحياة الدلالية (Semantic State Events)**:\n     * تسجيل: `EVENT_CARD_TAPPED`, `EVENT_CHIP_READ_SUCCESS`, `EVENT_PIN_ENTERED`, `EVENT_AUTH_DISPATCHED`, `EVENT_AUTH_SUCCESS`.\n   - **3. مرشحات السجلات الآلية (Automated Log Sanitizers / Scrubbers)**:\n     * كتابة Custom Tree في Timber أو Logback يحتوي على Regex يفحص السجلات تلقائياً؛ فإذا احتوى أي نص على نمط يشبه 16 رقماً يجتاز خوارزمية Luhn، يقوم باستبداله فوراً بـ `[REDACTED_PAN]`."
        ),
        "practical_walkthrough": (
            "تنفيذ أداة تنقية سجلات آلية (Log Scrubber) لحماية بيانات البطاقات في أندرويد:\n"
            "```kotlin\n"
            "// Timber Tree مخصص يقوم بتنقية وتشفير أي بيانات بطاقات بالخطأ:\n"
            "class PciCompliantLoggingTree : Timber.DebugTree() {\n"
            "    // Regex يلتقط أرقام البطاقات المكونة من 13 إلى 19 رقماً:\n"
            "    private val panRegex = Regex(\"\\\\b(?:[0-9]{4}[- ]?){3}[0-9]{4}\\\\b\")\n"
            "    private val cvvRegex = Regex(\"\\\\b(cvv|cvc|security_code)[\\\\s:=]+([0-9]{3,4})\\\\b\", RegexOption.IGNORE_CASE)\n"
            "\n"
            "    override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {\n"
            "        var sanitizedMessage = message\n"
            "        \n"
            "        // 1. تنقية وتعتيم أرقام الـ PAN:\n"
            "        sanitizedMessage = panRegex.replace(sanitizedMessage) { match ->\n"
            "            val cleanPan = match.value.replace(\"-\", \"\").replace(\" \", \"\")\n"
            "            // إبقاء أول 6 وآخر 4 أرقام فقط:\n"
            "            \"${cleanPan.take(6)}******${cleanPan.takeLast(4)}\"\n"
            "        }\n"
            "\n"
            "        // 2. حجب الـ CVV بالكامل:\n"
            "        sanitizedMessage = cvvRegex.replace(sanitizedMessage) \"$1=***\"\n"
            "\n"
            "        super.log(priority, tag, sanitizedMessage, t)\n"
            "    }\n"
            "}\n"
            "\n"
            "// في كود الدفع: مراقبة دلالية ممتازة وآمنة 100%:\n"
            "Timber.i(\"TxId=%s, Amount=%d, CardScheme=VISA, Status=AUTH_REQUEST_SENT\", txId, amount)\n"
            "```"
        ),
        "quick_answer": "Achieve payment observability without PCI-DSS violations by logging semantic state transitions and timing metrics indexed strictly by safe Correlation IDs and tokenized references. Never log PIN blocks, CVVs, or full PANs; enforce automated logging scrubbers that mask all but the first 6 and last 4 digits of account numbers.",
        "best_answer": (
            "Observability in financial applications must balance deep diagnostic telemetry with non-negotiable PCI-DSS compliance:\n\n"
            "1. **PCI-DSS Requirement 3 Prohibitions**:\n"
            "   - Explicitly forbids storing or transmitting sensitive authentication data (SAD) post-authorization: full Magnetic Stripe Track data, CVV/CVC codes, and PIN blocks. Full Primary Account Numbers (PAN) must be masked to a maximum of the first 6 digits (BIN) and last 4 digits (`411122******1111`).\n\n"
            "2. **Safe Semantic Telemetry Architecture**:\n"
            "   - Structure logs around high-level business milestones rather than raw payloads:\n     - `EVENT_EMV_INITIATED`: Correlation ID, reader type, battery level.\n     - `EVENT_CARD_PRESENTED`: Tech type (Contactless/NFC vs Chip), Card Scheme (Visa/Mastercard), Masked PAN.\n     - `EVENT_ONLINE_AUTHORIZATION`: Gateway latency, response codes (ISO 8583 Field 39: `00 Approved`).\n\n"
            "3. **Automated Defensive Scrubbing**:\n"
            "   - Implement custom logging trees (e.g., Timber/Logback filters) configured with regex patterns that detect high-entropy digit sequences and Luhn-valid card numbers, automatically redacting violations before outputting to Logcat or cloud aggregators."
        ),
        "deep_answer": (
            "From an enterprise audit and zero-trust security architecture perspective, observability requires hardened pipelines:\n\n"
            "1. **Production Logcat Redaction via R8**: In production release builds, stripping Logcat logging via ProGuard rules (`-assumenosideeffects class android.util.Log { *; }`) is mandatory. Even non-sensitive logs left in production Logcat can be read by malicious side-loaded apps on non-rooted Android 12+ devices via `adb logcat`.\n\n"
            "2. **Encrypted In-Memory Telemetry Ring Buffers**: When diagnosing rare transient hardware crashes in the field, maintain a rolling, in-memory circular buffer of the last 100 sanitized diagnostic events. If an unhandled exception or crash occurs, attach this sanitized ring buffer to the Crashlytics non-fatal exception report.\n\n"
            "3. **PCI Point-to-Point Encryption (P2PE)**:\n"
            "   - On certified Smart POS terminals, card data is encrypted directly at the hardware Secure Read Head (SCR) before hitting Android OS RAM. The Android app only receives an opaque encrypted blob (P2PE payload); it literally never possesses the raw PAN, rendering accidental memory leaks physically impossible."
        ),
        "follow_ups": [
            {
                "question": "What portion of a card number (PAN) is legally permissible to display or log under PCI-DSS?",
                "answer": "Only the first 6 digits (the Bank Identification Number - BIN) and the last 4 digits; all intermediate digits must be masked."
            },
            {
                "question": "Why should `android.util.Log` calls be stripped by R8/ProGuard in production financial apps?",
                "answer": "Because plain-text logs emitted to Android Logcat can be snooped by connected ADB debuggers or unauthorized device monitoring utilities."
            }
        ]
    },
    {
        "id": "PAY-11",
        "arabic_explanation": (
            "كيف تقوم باختبار مهلة الاستدعاءات (SDK Callback Timeout) وفصل العتاد المفاجئ (Device Disconnection) برمجياً دون الحاجة لأجهزة حقيقية؟\n\n"
            "1. تحدي اختبارات العتاد في بيئة الـ CI:\n"
            "   - يستحيل توصيل ماكينة POS حقيقية بكل سيرفر في GitHub Actions لنزع كابل الـ USB يدوياً أثناء الاختبارات!\n   - إذا اعتمدت على الاختبار اليدوي، فلن تتمكن من تغطية حالات نادرة مثل: ماذا لو استجاب البنك بعد 29.9 ثانية؟ ماذا لو فُصل قارئ البطاقات اللاسلكي أثناء إدخال الـ PIN؟\n\n"
            "2. استراتيجية الاختبار الهندسي عبر الـ Fake Test Double:\n   - بفضل عزل الـ SDK وراء واجهة `CardReaderManager` (كما صممنا في PAY-09)، يمكننا بناء `FakeCardReaderManager` يحتوي على **مقابض تحكم بالاختبار (Test Knobs)**.\n   - **مقابض الاختبار الأساسية**:\n     * `simulateTimeout()`: محاكاة عدم رد الهاردوير نهائياً لتفعيل مؤقت الـ Timeout.\n     * `simulateHardwareDisconnect()`: إطلاق حدث فصل فوري أثناء المعالجة.\n     * `simulateBadChipError()`: محاكاة تلف الشريحة الإلكترونية.\n\n"
            "3. اختبار الوقت الافتراضي باستخدام `runTest` في Kotlin Coroutines:\n   - استخدام `runTest` للتحكم في الوقت الافتراضي (Virtual Time) عبر `advanceTimeBy(30_000)`.\n   - التحقق من أنه بعد 30 ثانية تحديداً، قام النظام بإلغاء الجلسة، وتحديث الحالة إلى `UNKNOWN`، وإدراج طلب Reversal في قاعدة بيانات Room!"
        ),
        "practical_walkthrough": (
            "اختبار كامل في كوتلن يحاكي انقطاع العتاد ونفاد الوقت ويتحقق من إطلاق الـ Reversal:\n"
            "```kotlin\n"
            "class PaymentOrchestratorTest {\n"
            "    private val fakeCardReader = FakeCardReaderManager()\n"
            "    private val paymentDao = FakePaymentDao()\n"
            "    private val orchestrator = PaymentOrchestrator(fakeCardReader, paymentDao)\n"
            "\n"
            "    @Test\n"
            "    fun `card reader timeout enqueues reversal and aborts transaction`() = runTest {\n"
            "        // 1. ضبط الـ Fake لمحاكاة الصمت التام (عدم الرد):\n"
            "        fakeCardReader.shouldSimulateTimeout = true\n"
            "\n"
            "        val job = launch {\n"
            "            orchestrator.processCardPayment(amountCents = 10000)\n"
            "        }\n"
            "\n"
            "        // 2. تقديم الوقت الافتراضي لـ 30 ثانية لتجاوز مهلة الـ Timeout:\n"
            "        advanceTimeBy(30_001)\n"
            "\n"
            "        // 3. التحقق من أن النظام رصد الـ Timeout وعكس العملية:\n"
            "        val pendingReversals = paymentDao.getAllPendingReversals()\n"
            "        assertEquals(1, pendingReversals.size)\n"
            "        assertEquals(10000, pendingReversals.first().amountCents)\n"
            "        assertEquals(\"TIMEOUT_REVERSAL\", pendingReversals.first().reason)\n"
            "        job.cancel()\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun `abrupt usb disconnect during pin entry emits reader error`() = runTest {\n"
            "        val events = mutableListOf<CardReaderEvent>()\n"
            "        val collectJob = launch {\n"
            "            fakeCardReader.startCardInteraction(5000).collect { events.add(it) }\n"
            "        }\n"
            "\n"
            "        fakeCardReader.emitEvent(CardReaderEvent.PinRequired)\n"
            "        // محاكاة فصل الكابل فجأة أثناء كتابة الـ PIN:\n"
            "        fakeCardReader.simulateDisconnection()\n"
            "\n"
            "        val lastEvent = events.last()\n"
            "        assertTrue(lastEvent is CardReaderEvent.ReaderError)\n"
            "        assertEquals(999, (lastEvent as CardReaderEvent.ReaderError).errorCode)\n"
            "        collectJob.cancel()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test SDK timeouts and hardware disconnects programmatically using a configurable FakeCardReaderManager implementing the domain interface. Use Kotlin Coroutines runTest and advanceTimeBy() to simulate virtual timeouts and trigger simulated disconnections, asserting that the state machine enqueues the reversal and fails gracefully.",
        "best_answer": (
            "Verifying peripheral hardware failures deterministically requires software-mediated fault injection:\n\n"
            "1. **The Configurable Test Double Architecture**:\n"
            "   - Because proprietary payment kernels cannot run in cloud CI environments, implement a full-fidelity `FakeCardReaderManager`. Expose explicit programmatic fault hooks: `simulateTimeout()`, `simulateDisconnection()`, and `simulateTamperEvent()`.\n\n"
            "2. **Virtual Time Testing with `runTest`**:\n"
            "   - In Kotlin Coroutines, test timeout logic using `runTest`. Calling `advanceTimeBy(30_000L)` instantly advances virtual time without delaying CI execution by real clock seconds. Assert that the underlying timeout handler triggers, cancels the active peripheral flow, marks the transaction as `UNKNOWN`, and persists a reversal payload.\n\n"
            "3. **Simulating Asynchronous Disconnection Events**:\n"
            "   - Emit abrupt disconnection errors mid-transaction (e.g. between `PinRequired` and `CardReadSuccess`). Verify that the presentation layer clears confidential screens immediately and logs the hardware fault telemetry without leaving leaked coroutines or corrupted database locks."
        ),
        "deep_answer": (
            "From an Android instrumentation and edge-case testing perspective, integration testing extends to OS hardware simulations:\n\n"
            "1. **USB Host State Simulation via ADB**: On instrumented test devices connected via ADB, developers can simulate USB OTG disconnection by altering Android USB power states via ADB shell: `adb shell am broadcast -a android.hardware.usb.action.USB_DEVICE_DETACHED`. This verifies that Android `BroadcastReceiver` lifecycle handlers fire and gracefully release hardware device handles.\n\n"
            "2. **Chaos Fault Injection in Android Services**: In high-end fintech teams, an automated Chaos Proxy intercepts IPC Binder calls between the main app and vendor hardware daemon services. The proxy randomly injects a 3% rate of dead-object exceptions (`DeadObjectException`) to continuously verify that client retry and recovery state machines are bulletproof.\n\n"
            "3. **Verifying WorkManager Escalation**: Ensure tests verify that when a hardware disconnect causes a timeout reversal, the scheduled `ReversalDispatchWorker` is properly registered with WorkManager and ready for eventual background execution."
        ),
        "follow_ups": [
            {
                "question": "How does Kotlin's `runTest` accelerate timeout testing in CI pipelines?",
                "answer": "It uses virtual time skipping (`advanceTimeBy`), testing a 30-second hardware timeout in a few milliseconds without real-world thread sleep."
            },
            {
                "question": "What Android OS exception occurs when an external hardware service process crashes during an IPC call?",
                "answer": "`android.os.DeadObjectException`, which the client must catch and handle by restarting the connection."
            }
        ]
    },
    {
        "id": "PAY-12",
        "arabic_explanation": (
            "وافق البنك المصدر (Issuer) على معاملة نقطة البيع (POS)، ولكن الماكينة فقدت الطاقة تماماً وانطفأت قبل حفظ الموافقة. اشرح بالتفصيل بروتوكول التعافي والمطابقة (Recovery & Reconciliation)؟\n\n"
            "1. توصيف الكارثة المالية (The Nightmare Scenario):\n"
            "   - التاجر يدخل عملية بيع بـ 1,000 دولار.\n   - يتصل البنك ويوافق ويحجز الـ 1,000 دولار من حساب العميل (Approved).\n   - قبل أن يكتب التطبيق كود الموافقة في قاعدة البيانات، انطفأت الماكينة (فصل الكهرباء أو نزع البطارية)!\n   - العميل تصله رسالة SMS على هاتفه: \"تم خصم 1,000 دولار\".\n   - الماكينة عند إقلاعها: لا تعرف هل تمت العملية أم لا، ولم تطبع إيصالاً، والتاجر يرفض تسليم البضاعة!\n\n"
            "2. بروتوكول التعافي التلقائي عند الإقلاع (Post-Boot Recovery Protocol):\n   - **الخطوة 1: فحص الإقلاع (Startup Ledger Audit)**:\n     * عند إقلاع تطبيق الـ POS، يبحث فوراً في قاعدة البيانات عن أي معاملة في حالة `PROCESSING` أو `INITIATED`.\n     * يجد المعاملة رقم `tx_987` معلقة بدون قرار نهائي.\n   - **الخطوة 2: الاستعلام عن الحالة (Status Inquiry / Query Host)**:\n     * ترسل الماكينة استعلاماً فورياً لخادم الدفع باستخدام الـ `Correlation ID` والـ `Idempotency Key` المحفوظين قبل انقطاع الكهرباء: \"ما هي النتيجة النهائية للمعاملة `tx_987`؟\"\n   - **الخطوة 3: معالجة سيناريوهات الرد**:\n     * **السيناريو أ (الموافقة كانت مؤكدة)**: يرد الخادم ببيانات الموافقة (`AuthCode: 458921`). يقوم التطبيق بتحديث السجل إلى `APPROVED` فوراً، ويطبع إيصالاً بعنوان بارز: **\"إيصال مسترجع - تم الخصم بنجاح (RECOVERED DUPLICATE RECEIPT)\"** لتسليم البضاعة للعميل.\n     * **السيناريو ب (المعاملة لم تكتمل أو معلقة في البنك)**: ترسل الماكينة طلب عكس فوري (**Auto-Reversal 0400**) لإلغاء الحجز فوراً واسترجاع المبلغ لحساب العميل، وتطبع إيصال إلغاء وتطلب من الكاشير إعادة المحاولة."
        ),
        "practical_walkthrough": (
            "مخطط منطق التعافي الآلي عند إقلاع تطبيق أندرويد POS بعد انقطاع الطاقة:\n"
            "```kotlin\n"
            "class StartupRecoveryManager(\n"
            "    private val paymentDao: PaymentDao,\n"
            "    private val gatewayApi: PaymentGatewayApi,\n"
            "    private val receiptPrinter: ReceiptPrinter\n"
            ") {\n"
            "    suspend fun recoverInDoubtTransactionsOnBoot() = withContext(Dispatchers.IO) {\n"
            "        // 1. استخراج أي معاملات كانت قيد المعالجة ولم تكتمل:\n"
            "        val strandedTransactions = paymentDao.getTransactionsByState(\"PROCESSING\")\n"
            "\n"
            "        for (tx in strandedTransactions) {\n"
            "            try {\n"
            "                // 2. الاستعلام عن حالة العملية لدى خادم الدفع باستخدام نفس الـ ID:\n"
            "                val statusResponse = gatewayApi.queryTransactionStatus(tx.idempotencyKey)\n"
            "\n"
            "                if (statusResponse.isApproved) {\n"
            "                    // تم الخصم بنجاح: تأكيد محلي وطباعة إيصال التعافي:\n"
            "                    paymentDao.markApproved(tx.id, statusResponse.authCode)\n"
            "                    receiptPrinter.printDuplicateReceipt(tx, statusResponse.authCode)\n"
            "                } else {\n"
            "                    // لم تكتمل في البنك: إطلاق Reversal لتنظيف أي حجز معلق:\n"
            "                    gatewayApi.sendReversal(tx.toReversalPayload())\n"
            "                    paymentDao.markReversed(tx.id)\n"
            "                    receiptPrinter.printReversalNotice(tx)\n"
            "                }\n"
            "            } catch (e: Exception) {\n"
            "                // تعذر الاتصال بالخادم: إدراجها في Reversal Queue للمطابقة لاحقاً:\n"
            "                paymentDao.markAwaitingReconciliation(tx.id)\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Recover an in-doubt transaction after sudden power loss by auditing the database on boot, querying the payment gateway using the persistent idempotency key via a Status Inquiry, and either marking the transaction Approved and printing a recovered receipt if captured, or dispatching an automated Reversal if unconfirmed.",
        "best_answer": (
            "Handling power loss during the authorization commit window is a core requirement of POS terminal certification:\n\n"
            "1. **The In-Doubt Dilemma**:\n"
            "   - The acquiring host approved the transaction and sent the SMS to the cardholder, but terminal volatile RAM was destroyed before the approval code hit SQLite or the thermal printer engaged.\n\n"
            "2. **The Systematic Recovery Protocol**:\n"
            "   - **Boot-Time Ledger Scan**: Upon application startup, a `StartupRecoveryService` scans the persistent Room ledger for records lingering in `PROCESSING` or `INITIATED` status.\n   - **Host Status Inquiry**: The terminal dispatches a Status Inquiry request (`GET /v1/payments/status`) presenting the durable `idempotency_key` and original `correlation_id`.\n   - **Branch A (Gateway Captured)**: If the host confirms approval, the terminal transitions the local state to `APPROVED`, persists the authorization code, and automatically prints a marked duplicate receipt (`RECOVERED TRANSACTION RECEIPT`) so the merchant can release goods.\n   - **Branch B (Host Incomplete / Pending)**: If the host reports the transaction as pending or unconfirmed, the terminal generates an automated reversal (0400 Reversal message) to release the authorization hold, marks local state as `REVERSED`, and prints a void notification.\n\n"
            "3. **End-of-Day Batch Reconciliation Safety Net**:\n"
            "   - If connectivity fails completely during boot inquiry, the record is flagged for end-of-day batch reconciliation. During clearing, host and terminal ledgers are reconciled before merchant settlement payout."
        ),
        "deep_answer": (
            "From an EMV Level 2 transaction state machine perspective, hardware terminal certification enforces specific rules:\n\n"
            "1. **EMV Second Generate AC (Application Cryptogram) Failure**: In chip transactions, after receiving host authorization, the terminal must feed the issuer script back to the physical chip to generate the final Application Cryptogram (TC - Transaction Certificate). If power is lost before the chip generates TC, the transaction is **legally incomplete under EMV rules**, even if the issuer approved it! In this scenario, EMV compliance mandates issuing an automatic reversal because the chip never confirmed the sale.\n\n"
            "2. **Preventing Cashier Panic Retries**: During boot recovery, the UI must display a non-dismissible modal: 'Reconciling pending transactions, please wait...' This prevents a hurried cashier from attempting a second card swipe before the system has determined the fate of the first charge.\n\n"
            "3. **Merchant Protection Receipts**: The thermal printer must produce physical receipts with clear cryptographic audit markers (STAN, RRN, Auth Code, masked PAN) so the merchant is protected against chargeback disputes."
        ),
        "follow_ups": [
            {
                "question": "What is an EMV Transaction Certificate (TC) and why does power loss break it?",
                "answer": "A cryptographic proof generated by the card chip confirming completion; if power is cut before the chip generates TC, EMV rules mandate reversing the transaction."
            },
            {
                "question": "Why should the POS UI display a blocking dialog during startup recovery?",
                "answer": "To prevent the cashier from initiating a new charge while the terminal is reconciling whether the previous customer was already billed."
            }
        ]
    },
    {
        "id": "PAY-13",
        "arabic_explanation": (
            "معالج نفاد الوقت (Timeout Handler) يغلق شاشة الواجهة (UI) قبل إدراج طلب العكس (Reversal) في الطابور، مما يفقد العملية. كيف تعيد هندسة الملكية والترتيب المعماري لحل المشكلة؟\n\n"
            "1. تشريح العطل المعماري (Architectural Root Cause):\n"
            "   - **خلل الملكية (Ownership Flaw)**: تم ربط منطق الدفع والعكس بدورة حياة واجهة المستخدم (Activity / Fragment / `viewModelScope`).\n   - **خلل الترتيب (Ordering Flaw)**: عند نفاد مهلة الـ 30 ثانية، يستدعي كود الـ UI دالة `activity.finish()` أو يتنقل لشاشة الخطأ **قبل** اكتمال كتابة الـ Reversal في قاعدة البيانات!\n   - عندما تنتهي الـ Activity، يقوم نظام أندرويد بإلغاء كل الـ Coroutines المرتبطة بـ `lifecycleScope`؛ فيتوقف كود إدراج الـ Reversal في منتصفه ويضيع للأبد!\n\n"
            "2. إعادة الهندسة المعمارية الجذرية (Architectural Redesign):\n   - **1. فصل ملكية المعاملات عن الواجهة (Inversion of Ownership)**:\n     * لا تجعل الـ UI تملك تدفق الدفع! اجعل تدفق الدفع مملوكاً لـ **Application-Scoped Service** أو **WorkManager** يعمل بمعزل تام عن بقاء الشاشة مفتوحة أو مغلقة.\n   - **2. عكس ترتيب العمليات (Durable Enqueue BEFORE UI Notification)**:\n     * عند انتهاء المهلة، يقوم الكود أولاً بحفظ نية الـ Reversal ذرياً على القرص في Room (`markInDoubtAndEnqueueReversal`).\n     * **بعد اكتمال الحفظ على القرص بنجاح فقط**، يتم إرسال إشعار للواجهة عبر `StateFlow` لعرض شاشة الخطأ أو إغلاق الشاشة.\n   - **3. الواجهة مجرد مراقب سلبي (Passive UI Observer)**:\n     * الشاشة تراقب فقط حالة المعاملة (`collectAsState()`)؛ وإذا أُغلقت الشاشة، تستمر المعاملة والـ Reversal في الخلفية دون أي تأثر."
        ),
        "practical_walkthrough": (
            "إعادة هيكلة الملكية والترتيب لمنع فقدان الـ Reversals نهائياً:\n"
            "```kotlin\n"
            "// 1. خدمة ذات نطاق عام (Application Scope) تملك دورة حياة المعاملة وتصمد أمام إغلاق الشاشات:\n"
            "@Singleton\n"
            "class PaymentEngine @Inject constructor(\n"
            "    @ApplicationScope private val externalScope: CoroutineScope,\n"
            "    private val paymentDao: PaymentDao,\n"
            "    private val paymentApi: PaymentApi,\n"
            "    private val workScheduler: ReversalWorkScheduler\n"
            ") {\n"
            "    private val _txState = MutableSharedFlow<PaymentState>(replay = 1)\n"
            "    val txState: SharedFlow<PaymentState> = _txState.asSharedFlow()\n"
            "\n"
            "    fun executePaymentWithGuaranteedReversal(txId: String, request: PaymentRequest) {\n"
            "        // يتم الإطلاق في ApplicationScope: حتى لو ماتت الـ Activity بالكامل، الكود يكمل تنفيذه!\n"
            "        externalScope.launch {\n"
            "            try {\n"
            "                withTimeout(30_000L) {\n"
            "                    val response = paymentApi.authorize(request)\n"
            "                    paymentDao.markApproved(txId, response.authCode)\n"
            "                    _txState.emit(PaymentState.Approved(response.authCode))\n"
            "                }\n"
            "            } catch (e: TimeoutCancellationException) {\n"
            "                // ✅ الترتيب الحاسم: الحفظ الدائم على القرص أولاً وقبل إبلاغ الواجهة!\n"
            "                paymentDao.markInDoubtAndEnqueueReversal(txId, request.toReversalPayload())\n"
            "                workScheduler.triggerReversalWork()\n"
            "                \n"
            "                // الآن فقط نخبر الواجهة بأن العملية انتهت بمهلة وعكست بأمان:\n"
            "                _txState.emit(PaymentState.TimedOutAndReversed(txId))\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Redesign ownership and ordering by decoupling payment execution from the UI lifecycle into an Application-scoped coroutine or WorkManager, and inverting operation order so the reversal intent is durably committed to SQLite before the UI is notified or dismissed.",
        "best_answer": (
            "Coupling financial reversal persistence to ephemeral Android UI component lifecycles represents a catastrophic anti-pattern:\n\n"
            "1. **Root-Cause Flaws**:\n"
            "   - **Fragile Ownership**: Launching payment coroutines within `lifecycleScope` or UI ViewModels binds business logic to the screen. When a timeout occurs and the user or handler executes `finish()`, the lifecycle cancels all active coroutine jobs, silently aborting incomplete database inserts.\n   - **Inverted Sequencing**: Notifying the UI before completing disk persistence creates a race condition where the screen tears down the process while the disk write is in-flight.\n\n"
            "2. **Architectural Redesign Blueprint**:\n"
            "   - **Inversion of Ownership**: Transfer transaction ownership to a singleton `PaymentEngine` backed by an uncancelled `ApplicationScope` or persistent WorkManager. Transaction execution continues unhindered regardless of UI navigation, orientation changes, or screen dismissals.\n   - **Strict Persistence-First Sequencing**: Upon timeout detection, the engine must atomically commit the in-doubt state and reversal payload to SQLite *first* (`paymentDao.markInDoubtAndEnqueueReversal()`). Only after disk confirmation does it emit state updates to UI observers.\n   - **Passive State-Driven UI**: The UI becomes a purely passive observer of `StateFlow<PaymentState>`. If the user closes the screen, the reversal worker still dispatches reliably in the background."
        ),
        "deep_answer": (
            "From an Android process lifecycle and Coroutines concurrency standpoint, execution boundaries must be hardened:\n\n"
            "1. **`NonCancellable` Context Protection**: In Kotlin Coroutines, when a timeout block cancels (`TimeoutCancellationException`), standard coroutine blocks immediately terminate. Enqueuing the reversal must be wrapped in `withContext(NonCancellable)` to prevent the active cancellation exception from aborting the emergency database commit.\n\n"
            "2. **Handling Low-Memory Process Termination (LMK)**: Even an `ApplicationScope` will not survive if Android's Low Memory Killer terminates the OS process due to RAM pressure. Pairing `ApplicationScope` with an immediate WorkManager job registration (`ExistingWorkPolicy.REPLACE`) guarantees that if the process is killed mid-write, the Android OS will reschedule and execute the reversal upon system recovery.\n\n"
            "3. **UI Event Back-Pressure**: If the UI exits during timeout, prevent the user from immediately re-entering the checkout flow until the background engine confirms the reversal intent has been durably secured."
        ),
        "follow_ups": [
            {
                "question": "Why must reversal enqueueing logic be wrapped in `withContext(NonCancellable)` inside a timeout catch block?",
                "answer": "Because a timeout cancellation exception cancels the coroutine context, which would abort regular database writes unless protected by `NonCancellable`."
            },
            {
                "question": "What is the danger of binding transaction execution to `viewModelScope`?",
                "answer": "If the user navigates away or the ViewModel is cleared, the scope is cancelled, dropping in-flight transaction and reversal operations."
            }
        ]
    },
    {
        "id": "PAY-14",
        "arabic_explanation": (
            "مكتبة أمان ودفع أصلية (Native C/C++ Dependency) تعمل بنجاح في وضع الـ Debug ولكنها تنهار بكراش فقط في الـ Release على بعض معالجات الهواتف (ABIs). كيف تدير خطة التحقيق والإطلاق الآمن؟\n\n"
            "1. الأسباب الشائعة للأعطال الخاصة بنسخة الـ Release والـ ABIs:\n"
            "   - **1. مشكلة تجريد كود R8/ProGuard (Missing JNI Keep Rules)**:\n     * في وضع الـ Debug، يكون R8 معطلاً فتعمل استدعاءات الـ C++ (JNI) بسلاسة.\n     * في وضع الـ Release، يقوم R8 بضغط وتغيير أسماء الكلاسات والدوال (`Obfuscation`). وعندما يحاول كود C++ استدعاء دالة Kotlin عبر اسمها الأصلي، يفشل بكراش فوري: `NoSuchMethodError` أو `NoSuchFieldError`!\n   - **2. نقص ملفات الـ `.so` في بعض معماريات المعالجات (ABI Split Mismatch)**:\n     * المكتبة تحتوي على ملفات ثنائية لـ `armeabi-v7a` (32-bit)، ولكنها تفتقر لمكتبات `arm64-v8a` (64-bit) أو `x86_64`.\n     * عند تثبيت التطبيق على هاتف حديث 64-bit، يبحث نظام أندرويد عن مكتبة 64-bit ولا يجدها، فينهار التطبيق بـ `UnsatisfiedLinkError`!\n   - **3. أخطاء تجميع الـ C++ والـ Memory Alignment (SIGSEGV)**:\n     * كراشات الذاكرة في C++ تظهر فقط مع تحسينات المترجم القصوى (`-O3`) في الـ Release.\n\n"
            "2. خطة التحقيق والتشخيص الهندسي (Investigation Workflow):\n   - **1. فحص محتويات الـ APK عبر APK Analyzer**: التأكد من وجود ملفات الـ `.so` متطابقة في جميع مجلدات `lib/arm64-v8a/` و `lib/armeabi-v7a/`.\n   - **2. فحص قواعد ProGuard**: إضافة قواعد حماية صريحة لجميع دوال وكلاسات الـ Native:\n     `-keepclasseswithmembernames class * { native <methods>; }`\n   - **3. تتبع كراشات الـ Native Crash في Google Play Console**: تحميل ملفات الـ Native Debug Symbols (`native-debug-symbols.zip`) لفك تشفير الـ Tombstones.\n\n"
            "3. خطة الإطلاق الآمن (Safe Rollout Plan):\n   - إطلاق تحديث تجريبي عبر مسار **Internal Testing** على مصفوفة أجهزة فعلية تمثل مختلف الـ ABIs (Firebase Test Lab).\n   - بدء الـ Staged Rollout في الإنتاج بنسبة 1% ومراقبة مؤشرات Crashlytics الخاصة بالـ `UnsatisfiedLinkError` قبل رفع النسبة."
        ),
        "practical_walkthrough": (
            "حلول Gradle وقواعد ProGuard لتأمين مكتبات الـ Native في أندرويد:\n"
            "```kotlin\n"
            "// 1. app/build.gradle.kts: ضبط قيود الـ ABIs وتوليد ملفات الـ Native Symbols:\n"
            "android {\n"
            "    defaultConfig {\n"
            "        ndk {\n"
            "            // التأكد من دعم المعماريات الرسمية المعتمدة فقط في المتجر:\n"
            "            abiFilters += listOf(\"armeabi-v7a\", \"arm64-v8a\")\n"
            "        }\n"
            "    }\n"
            "    buildTypes {\n"
            "        release {\n"
            "            isMinifyEnabled = true\n"
            "            proguardFiles(getDefaultProguardFile(\"proguard-android-optimize.txt\"), \"proguard-rules.pro\")\n"
            "            ndk {\n"
            "                // توليد ملفات الرموز لفك تشفير الـ C++ stacktraces في Crashlytics:\n"
            "                debugSymbolLevel = \"FULL\"\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "```proguard\n"
            "# 2. proguard-rules.pro: حماية جميع دوال وكلاسات الـ JNI من الحذف أو التعتيم:\n"
            "-keepclasseswithmembernames class * {\n"
            "    native <methods>;\n"
            "}\n"
            "-keep class com.vendor.payments.emv.** { *; }\n"
            "-keepclassmembers class com.vendor.payments.emv.** {\n"
            "    *;\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Investigate native dependency crashes by inspecting APK ABIs with APK Analyzer for missing .so architectures and checking ProGuard/R8 keep rules for stripped JNI methods. Execute a safe rollout using ndk.abiFilters, uploading native debug symbols, testing on Firebase Test Lab device matrices, and deploying via 1% staged rollouts.",
        "best_answer": (
            "Debugging release-only native `.so` crashes across CPU architectures requires systematic binary forensics:\n\n"
            "1. **Root-Cause Diagnostics**:\n"
            "   - **R8 / Obfuscation Stripping**: In debug builds, R8 is disabled. In release builds, R8 renames Kotlin classes and methods. If C++ JNI code attempts to call Kotlin methods via hardcoded reflection signatures (`env->GetMethodID`), it throws an instant fatal `NoSuchMethodError`.\n   - **ABI Packaging Asymmetry**: If a third-party dependency supplies `armeabi-v7a` binaries but omits `arm64-v8a`, Android's 64-bit Zygote loader looks into the app's `lib/arm64-v8a/` directory, fails to find the `.so`, and throws `java.lang.UnsatisfiedLinkError`.\n   - **Native Alignment Crashes (16KB Page Size in Android 15)**: ELF binaries built without 16KB memory alignment crash immediately on modern kernels.\n\n"
            "2. **Inspection and Remediation Steps**:\n"
            "   - **APK Analyzer**: Inspect the final signed release AAB. Verify that every bundled `.so` file exists across all targeted ABI directories.\n   - **JNI ProGuard Rules**: Add strict preservation rules: `-keepclasseswithmembernames class * { native <methods>; }` and keep vendor model packages.\n   - **Native Debug Symbols**: Enable `ndk.debugSymbolLevel = 'FULL'` in Gradle to de-obfuscate native C++ tombstone crashes in Crashlytics and Play Console.\n\n"
            "3. **Safe Rollout Protocol**:\n"
            "   - Validate across physical hardware matrices on Firebase Test Lab spanning ARM32 and ARM64 chipset variants. Roll out via Google Play Staged Rollouts (1% -> 5%) with automated alert gates on `UnsatisfiedLinkError`."
        ),
        "deep_answer": (
            "From an NDK toolchain and Google Play 64-bit compliance angle, architectural considerations include:\n\n"
            "1. **Google Play 64-Bit Requirement Enforcement**: Google Play strictly mandates 64-bit native code for all apps containing native libraries. If a legacy payment SDK only provides 32-bit binaries, you cannot simply filter to `armeabi-v7a` on new uploads. You must either obtain an updated 64-bit binary from the vendor or isolate the legacy component into a separate companion process.\n\n"
            "2. **The 16KB Page Size Memory Mandate**: Starting with Android 15, Android devices support 16KB memory page sizes. Native C++ libraries compiled with standard 4KB page alignment crash with `SIGSEGV` during memory mapping (`mmap`). Ensure all native libraries are compiled with `-Wl,-z,max-page-size=16384`.\n\n"
            "3. **Safe Fallback Wrappers**: Wrap native JNI loading calls (`System.loadLibrary()`) inside a defensive `try/catch(UnsatisfiedLinkError)` block at app startup. If the native library fails to load on an exotic device, the app must gracefully degrade (e.g. disabling local hardware NFC while leaving manual card entry intact) rather than crashing on launch."
        ),
        "follow_ups": [
            {
                "question": "What causes an `UnsatisfiedLinkError` in release builds when a library works fine in debug?",
                "answer": "Either R8 obfuscated the Kotlin methods called by JNI, or the release build targeted a 64-bit ABI (arm64-v8a) where the vendor .so binary was missing."
            },
            {
                "question": "Why is `debugSymbolLevel = 'FULL'` critical for native Android dependencies?",
                "answer": "It uploads unstripped C++ symbols to Google Play and Crashlytics, converting raw memory addresses into readable source file lines."
            }
        ]
    },
    {
        "id": "PAY-15",
        "arabic_explanation": (
            "انقطع اتصال الإنترنت تماماً عندما حان وقت إرسال طلب العكس (Reversal) للبنك. كيف تضمن تسليم الطلب حتماً في المستقبل (Eventual Delivery) دون إرسال طلبات مكررة؟\n\n"
            "1. معضلة انقطاع الشبكة أثناء العكس (Offline Reversals):\n"
            "   - يحتاج التطبيق لإلغاء معاملة معلقة، ولكن الجهاز في وضع عدم الاتصال (Offline) أو في قبو بدون تغطية خلوية.\n   - لا يجوز التراجع عن العكس أو نسيانه؛ لأن أموال العميل ستظل محجوزة لدى البنك للأبد!\n   - ولا يجوز إرسال طلبات عكس عشوائية متكررة عند عودة الشبكة لأنها قد تربك نظام البنك وتعتبر معاملات مكررة (Duplicate Flood).\n\n"
            "2. نمط التخزين والتمرير اللاحق (Store-and-Forward Pattern - SaF):\n   - **1. الحفظ الدائم كـ Pending في SQLite**:\n     * حفظ كائن الـ Reversal في جدول `reversal_queue` مع الـ `idempotency_key` الأصلي.\n   - **2. آلية إعادة المحاولة مع التراجع الأسي (Exponential Backoff with Jitter)**:\n     * استخدام Jetpack WorkManager الذي يتكفل بإعادة المحاولة تلقائياً بمجرد توفر الشبكة (`Constraints.NetworkType.CONNECTED`).\n     * فترات الانتظار تتصاعد تدريجياً: 10 ثوانٍ، ثم 30 ثانية، ثم دقيقة، ثم 5 دقائق لمنع إغراق الخادم بالطلبات (Thundering Herd Problem).\n   - **3. اللاتكرارية في خادم البنك (Server-Side Idempotency)**:\n     * خادم الدفع مصمم ليكون Idempotent على معرف الـ Reversal (`reversal_id` + `original_tx_id`).\n     * إذا استلم الخادم طلب العكس مرتين، ينفذ الأول ويعيد نجاحاً فورياً للطلب الثاني دون أي تكرار.\n   - **4. الحذف الذري بعد التأكيد (Atomic Deletion upon 200 OK)**:\n     * بمجرد استلام رد صريح بنجاح العكس من السيرفر، يتم حذف السجل من جدول الـ `reversal_queue` محلياً."
        ),
        "practical_walkthrough": (
            "تنفيذ محرك Store-and-Forward للـ Reversals باستخدام WorkManager و Room:\n"
            "```kotlin\n"
            "// 1. Worker صامد يعتمد على Store-and-Forward لمعالجة الـ Reversals عند عودة الشبكة:\n"
            "class StoreAndForwardReversalWorker(\n"
            "    context: Context,\n"
            "    params: WorkerParameters,\n"
            "    private val paymentDao: PaymentDao,\n"
            "    private val api: PaymentGatewayApi\n"
            ") : CoroutineWorker(context, params) {\n"
            "\n"
            "    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {\n"
            "        val pendingReversals = paymentDao.getAllPendingReversals()\n"
            "        if (pendingReversals.isEmpty()) return@withContext Result.success()\n"
            "\n"
            "        for (reversal in pendingReversals) {\n"
            "            try {\n"
            "                // إرسال طلب العكس مع Idempotency Key الأصلي:\n"
            "                val response = api.sendReversal(\n"
            "                    idempotencyKey = reversal.idempotencyKey,\n"
            "                    payload = reversal.payload\n"
            "                )\n"
            "                // تم التأكيد بنجاح -> حذفه فورياً من الطابور لمنع التكرار:\n"
            "                if (response.isSuccess || response.isAlreadyReversed) {\n"
            "                    paymentDao.deleteReversal(reversal.id)\n"
            "                } else if (response.isTerminalRejection) {\n"
            "                    // خطأ غير قابل للإعادة (مثل انتهاء الصلاحية) -> تحويله لتقرير التدقيق البشري:\n"
            "                    paymentDao.markAuditRequired(reversal.id)\n"
            "                }\n"
            "            } catch (e: IOException) {\n"
            "                // لا توجد شبكة -> مطالبة WorkManager بإعادة المحاولة لاحقاً مع Backoff:\n"
            "                return@withContext Result.retry()\n"
            "            }\n"
            "        }\n"
            "        Result.success()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Guarantee eventual reversal delivery without duplicates by implementing a persistent Store-and-Forward engine backed by SQLite and WorkManager. Enforce exponential backoff with network constraints, tie dispatches to the original persistent idempotency key for server-side deduplication, and purge local records only upon acknowledged receipt.",
        "best_answer": (
            "Guaranteeing eventual delivery of financial reversals during network blackouts relies on the Store-and-Forward (SaF) architecture:\n\n"
            "1. **Store-and-Forward (SaF) Architecture**:\n"
            "   - When an in-doubt transaction requires reversal while offline, the client durably writes the immutable reversal payload to a local SQLite `reversal_queue` table before acknowledging the failure to the UI.\n\n"
            "2. **Resilient WorkManager Orchestration**:\n"
            "   - Enqueue a unique WorkManager background task (`ExistingWorkPolicy.KEEP`) configured with a `NetworkType.CONNECTED` constraint and `BackoffPolicy.EXPONENTIAL`. WorkManager guarantees OS-level persistent execution attempts once connectivity is restored, surviving device reboots and app closures.\n\n"
            "3. **Duplicate Prevention via Server Idempotency**:\n"
            "   - The outbound reversal message carries the immutable `original_transaction_id` and a unique `reversal_id`. The acquiring gateway treats the reversal idempotently: if the reversal was already processed by a prior retry, the host returns an HTTP 200 / ISO 8583 Code 00 success response rather than flagging a duplicate error.\n\n"
            "4. **Atomic Dequeue on Acknowledged Delivery**:\n"
            "   - The local queue entry is deleted from SQLite only upon receiving an explicit confirmation (HTTP 200 / ISO approved) from the gateway. If a network drop occurs during response delivery, the subsequent retry safely dedupes on the server."
        ),
        "deep_answer": (
            "From an ISO 8583 financial interchange and settlement perspective, SaF engines must handle protocol edge cases:\n\n"
            "1. **Reversal Expiration Windows (The 24-Hour Settlement Cutoff)**: If a POS terminal remains disconnected in an offline van for 4 days, issuing an ISO 8583 reversal against an authorization that was settled 3 days ago will be rejected with `Response Code 94: Duplicate or Expired`. High-reliability fintech apps implement time-to-live (TTL) checks: reversals older than the acquiring cutoff transition into a `DISPUTE_RECONCILIATION_REQUIRED` state for human back-office settlement.\n\n"
            "2. **Jittered Backoff to Prevent Server DDOS**: When an airport or shopping mall Wi-Fi network reconnects after an outage, thousands of POS devices fire reversal retries simultaneously (the Thundering Herd Problem). WorkManager's exponential backoff applies randomized jitter to spread connection spikes smoothly over time.\n\n"
            "3. **Terminal Pre-Flight Blocker**: As mandated in EMV certification, the terminal must prioritize flushing the offline reversal queue before permitting cashiers to initiate new customer sales, guaranteeing ledger synchronization."
        ),
        "follow_ups": [
            {
                "question": "What happens if a reversal request reaches the server after the daily batch settlement cutoff?",
                "answer": "The server rejects the reversal because the transaction has already cleared; the incident must be routed to back-office reconciliation for an automated refund."
            },
            {
                "question": "Why is randomized jitter added to exponential backoff in payment retry engines?",
                "answer": "To prevent thousands of reconnected terminals from hitting the payment gateway simultaneously in a synchronized thundering herd wave."
            }
        ]
    }
]


def main() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing_data: list[dict] = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

    existing_dict = {item["id"]: item for item in existing_data}
    for item in PAY_09_15:
        existing_dict[item["id"]] = item

    all_items = list(existing_dict.values())
    all_items.sort(key=lambda x: x["id"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"Updated {DATA_FILE} with questions PAY-09 to PAY-15. Total questions: {len(all_items)}")


if __name__ == "__main__":
    main()
