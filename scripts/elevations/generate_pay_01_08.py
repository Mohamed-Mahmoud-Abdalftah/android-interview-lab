#!/usr/bin/env python3
"""Generator for PAY-01 through PAY-08 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "pay.json"

PAY_01_08 = [
    {
        "id": "PAY-01",
        "arabic_explanation": (
            "ما هي آلة حالة الدفع (Payment State Machine) وما هي الحالات الأساسية (Initiated, Processing, Approved, Declined, Unknown, Reversed) ولماذا تعتبر حاسمة في التطبيقات المالية؟\n\n"
            "1. خطورة التعامل مع المدفوعات كـ Boolean (Success/Failure):\n"
            "   - في التطبيقات العادية، قد تكفيك نتيجة `true` أو `false`.\n   - في الأنظمة المالية ونقاط البيع (POS/Fintech)، **هذا التبسيط يؤدي لكوارث مالية (Double-charging أو خسارة أموال التاجر)**!\n   - الشبكة قد تنقطع بعد خصم الأموال من حساب العميل وقبل وصول الرد للهاتف؛ فإذا اعتبرت العملية \"فاشلة\"، سيقوم العميل بالدفع مرة أخرى ويُخصم منه مرتين!\n\n"
            "2. الحالات الست الصارمة لآلة حالة الدفع (The 6 Payment States):\n   - **1. Initiated (تم البدء)**: تم إنشاء الطلب محلياً وتوليد معرف ارتباط فريد (Correlation ID) وحفظه في قاعدة البيانات المحلية (Room) قبل إرسال أي بايت عبر الشبكة.\n   - **2. Processing (قيد المعالجة)**: تم إرسال الطلب إلى معالج الدفع (Payment Gateway / Bank Switch) وننتظر الرد.\n   - **3. Approved (مقبول ومؤكد)**: وصل رد رسمي وبتوقيع رقمي من البنك يؤكد حجز الأموال بنجاح.\n   - **4. Declined (مرفوض)**: رد صريح من البنك بالرفض (رصيد غير كافٍ، بطاقة منتهية، كلمة سر خاطئة). حالة نهائية لا تتطلب إعادة محاولة.\n   - **5. Unknown / In-Doubt (حالة معلقة وغير محددة)**: **أهم وأخطر حالة**! انقطاع اتصال (Timeout)، سقوط الخادم، أو إعادة تشغيل الهاتف أثناء انتظار الرد. لا يجوز اعتبارها نجاحاً ولا فشلاً، بل تتطلب استعلاماً لاحقاً (Reconciliation) أو عملية عكس (Reversal).\n   - **6. Reversed (معكوس / ملغى)**: تم إرسال طلب إلغاء فوري للبنك لحذف الحجز واستعادة رصيد العميل بسبب عطل محلي."
        ),
        "practical_walkthrough": (
            "تمثيل آلة حالة الدفع الصارمة باستخدام Kotlin Sealed Class في كود معماري آمن:\n"
            "```kotlin\n"
            "sealed interface PaymentState {\n"
            "    val transactionId: String\n"
            "    val amountInCents: Long\n"
            "\n"
            "    // 1. تم إنشاء المعاملة وحفظها محلياً في Room:\n"
            "    data class Initiated(override val transactionId: String, override val amountInCents: Long) : PaymentState\n"
            "\n"
            "    // 2. تم إرسال الطلب للبنك وننتظر الرد:\n"
            "    data class Processing(override val transactionId: String, override val amountInCents: Long, val idempotencyKey: String) : PaymentState\n"
            "\n"
            "    // 3. تأكيد نهائي بالخصم:\n"
            "    data class Approved(override val transactionId: String, override val amountInCents: Long, val authCode: String) : PaymentState\n"
            "\n"
            "    // 4. رفض صريح من البنك:\n"
            "    data class Declined(override val transactionId: String, override val amountInCents: Long, val reason: String) : PaymentState\n"
            "\n"
            "    // 5. حالة معلقة (انقطاع شبكة أثناء المعالجة - تتطلب تحقيق ومطابقة):\n"
            "    data class Unknown(override val transactionId: String, override val amountInCents: Long, val error: Throwable) : PaymentState\n"
            "\n"
            "    // 6. تم إلغاء المعاملة واسترجاع الرصيد بنجاح:\n"
            "    data class Reversed(override val transactionId: String, override val amountInCents: Long, val reversalRef: String) : PaymentState\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A payment state machine governs financial transaction lifecycles across explicit states: Initiated (locally persisted), Processing (in-flight), Approved (issuer authorized), Declined (issuer rejected), Unknown (network drop/timeout during transit), and Reversed (undone via auto-reversal). It prevents double-charging and catastrophic state ambiguity.",
        "best_answer": (
            "A deterministic payment state machine is the foundational architectural safeguard in fintech and POS engineering:\n\n"
            "1. **Eliminating the Binary Fallacy**:\n"
            "   - Financial transactions must never be modeled as a boolean (success/failure). Network timeouts produce ambiguous states where funds were deducted at the issuer bank but never acknowledged on the mobile terminal.\n\n"
            "2. **The Six Canonical Transaction States**:\n"
            "   - **Initiated**: Transaction intent, idempotency key, and payload are durably written to disk (Room/SQLite) before opening any socket connection.\n   - **Processing**: The payload is in transit to the payment gateway or EMV switch.\n   - **Approved**: Cryptographically signed confirmation received with an authorization code.\n   - **Declined**: Explicit rejection code (e.g., insufficient funds, expired card); a terminal state requiring no automatic retries.\n   - **Unknown / In-Doubt**: Network timeout, socket hangup, or terminal reboot occurs mid-flight. Funds may or may not have been captured.\n   - **Reversed**: An automated reversal (0400/0420 ISO 8583 message) has released held funds back to the cardholder.\n\n"
            "3. **State Transition Guarantees**:\n"
            "   - Transitions must be strictly monotonic and persisted atomically in local databases to survive sudden process termination or hardware battery pulls."
        ),
        "deep_answer": (
            "From an ISO 8583 and payment terminal compliance perspective, managing the 'Unknown' state dictates ledger consistency:\n\n"
            "1. **The 'In-Doubt' Protocol**: When a transaction enters the `Unknown` state due to a 30-second gateway read timeout, client apps must **never immediately retry the authorization request**. Doing so risks charging the customer twice. The terminal must enqueue an automated Reversal (ISO 8583 0400 reversal message) and mark the local record as pending reversal.\n\n"
            "2. **Terminal Status Inquiry vs. Auto-Reversal**: High-reliability POS devices execute a Status Inquiry (`/v1/payments/{id}/status`) before issuing a reversal. If the gateway confirms the charge was captured, the client reconciles the transaction as Approved and prints the receipt; if not captured or still pending, it executes the reversal.\n\n"
            "3. **Crash-Resistant State Machine Engines**: In Android, state machines must be tied to persistent WorkManager tasks and Room database observers rather than ViewModel in-memory state. If Android kills the app process due to low memory while in `Processing`, upon next launch the app inspects Room and resumes the reconciliation workflow."
        ),
        "follow_ups": [
            {
                "question": "Why is treating a network timeout as a 'Declined' payment dangerous in financial apps?",
                "answer": "Because the issuer may have already approved and deducted the funds; treating it as declined causes the customer to pay twice upon re-trying."
            },
            {
                "question": "What is the primary objective of an ISO 8583 reversal message?",
                "answer": "To instruct the issuer to release pre-authorized funds and void an in-doubt transaction when the client terminal did not receive confirmation."
            }
        ]
    },
    {
        "id": "PAY-02",
        "arabic_explanation": (
            "ما هي خاصية الـ Idempotency (اللاتكرارية)، ولماذا تعتبر أمراً حيوياً وإلزامياً في المعاملات المالية؟\n\n"
            "1. ما هو الـ Idempotence في علوم الحاسوب والشبكات؟\n"
            "   - هو خاصية تعني أن **تنفيذ نفس العملية عدة مرات ينتج نفس النتيجة تماماً دون أي آثار جانبية إضافية (Side-effects)**.\n   - رياضياً: $f(f(x)) = f(x)$.\n   - في بروتوكول HTTP: طلبات `GET` و `PUT` و `DELETE` تعتبر Idempotent افتراضياً، بينما طلبات `POST` (المستخدمة في الدفع) **ليست Idempotent بطبيعتها** وتنشئ مورداً جديداً مع كل استدعاء إذا لم يتم تأمينها!\n\n"
            "2. لماذا تعتبر قاتلة في التطبيقات المالية؟\n   - تخيل عميلاً يضغط زر \"ادفع 100 دولار\".\n   - يرسل التطبيق الطلب، ويخصم البنك 100 دولار من الحساب، ولكن شبكة الجوال تسقط قبل أن تعود الاستجابة إلى هاتف العميل (HTTP Timeout).\n   - يرى العميل شاشة تحميل متوقفة، فيضغط الزر مرة ثانية!\n   - إذا لم يكن النظام Idempotent: سيخصم البنك 100 دولار أخرى (Double Charge)! ويفقد العميل ثقته في التطبيق وتتعرض الشركة لغرامات نزاعات الدفع (Chargebacks).\n\n"
            "3. كيف تعمل تقنية الـ Idempotency Key؟\n   - يولد التطبيق **معرفاً عشوائياً فريداً عالمياً (UUID v4)** ويخزنه محلياً مع الطلب.\n   - يرسل هذا المعرف في ترويسة الطلب: `Idempotency-Key: 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d`.\n   - يقوم خادم الدفع (Payment Gateway مثل Stripe) بتخزين المفتاح في Redis. إذا استلم نفس المفتاح مرة أخرى خلال 24 ساعة، **لا ينفذ الخصم ثانية**، بل يعيد نفس الاستجابة المخزنة مسبقاً فوراً!"
        ),
        "practical_walkthrough": (
            "تطبيق نمط الـ Idempotency Key في كود كوتلن باستخدام OkHttp Interceptor:\n"
            "```kotlin\n"
            "// Interceptor يضمن إرفاق Idempotency-Key فريد ومحفوظ محلياً لكل معاملة مالية:\n"
            "class IdempotencyInterceptor(private val transactionDao: TransactionDao) : Interceptor {\n"
            "    override fun intercept(chain: Interceptor.Chain): Response {\n"
            "        val request = chain.request()\n"
            "\n"
            "        // فحص ما إذا كان الطلب معاملة مالية حساسة تتطلب Idempotency:\n"
            "        if (request.header(\"X-Financial-Tx\") == \"true\") {\n"
            "            val txId = request.header(\"X-Transaction-Id\")\n"
            "                ?: throw IllegalStateException(\"Transaction ID missing!\")\n"
            "\n"
            "            // استخراج المفتاح المخزن في قاعدة البيانات المحلية لنفس المعاملة لمنع إنشاء مفتاح جديد عند إعادة المحاولة:\n"
            "            val idempotencyKey = transactionDao.getIdempotencyKey(txId)\n"
            "\n"
            "            val newRequest = request.newBuilder()\n"
            "                .header(\"Idempotency-Key\", idempotencyKey)\n"
            "                .build()\n"
            "\n"
            "            return chain.proceed(newRequest)\n"
            "        }\n"
            "        return chain.proceed(request)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Idempotency guarantees that executing an operation multiple times produces the identical outcome with zero additional side effects. In financial transactions, it prevents catastrophic double-charging when network timeouts cause mobile clients or users to retry payment submissions.",
        "best_answer": (
            "Idempotency is the cornerstone of distributed transaction safety in mobile financial applications:\n\n"
            "1. **The Core Financial Hazard**:\n"
            "   - Because mobile payment authorizations rely on HTTP `POST` over unreliable cellular connections, packets are routinely dropped on the return leg after the issuer bank has captured the charge. Without idempotency, automatic retries or repeated user button taps result in duplicate credit card charges.\n\n"
            "2. **Mechanics of the Idempotency Key Architecture**:\n"
            "   - **Client Generation**: The mobile client generates a cryptographically unique identifier (UUID v4) and durably commits it to local storage (Room) alongside the payment entity *before* making the network call.\n   - **Header Transmission**: The key is attached to the HTTP header (`Idempotency-Key: <UUID>`).\n   - **Server Atomic Deduplication**: The payment gateway (e.g. Stripe, Adyen) caches the key in an atomic distributed lock (Redis). If an identical key arrives while processing, the server queues or rejects the duplicate; if it arrives after completion, the server returns the cached response without debiting the customer again.\n\n"
            "3. **Idempotency Lifetime Contract**:\n"
            "   - Keys are typically valid for a 24-hour window, ensuring that retry queues, offline reconciliations, and user retries safely resolve to the identical single ledger entry."
        ),
        "deep_answer": (
            "From an API design and distributed consensus perspective, client-side idempotency implementation contains subtle traps:\n\n"
            "1. **The 'Key Regeneration on Retry' Bug**: The most dangerous junior bug is generating a fresh `UUID.randomUUID().toString()` inside the network retry loop or ViewModel method. If a timeout occurs and the retry function generates a *new* idempotency key, the backend treats it as a brand-new distinct charge, completely defeating the safeguard! The key must be tied to the immutable domain `Transaction` entity.\n\n"
            "2. **Idempotency Payload Fingerprinting**: High-security payment backends hash the request payload along with the idempotency key. If a client sends the same key with an altered amount ($100 vs $200), the server flags a tampering conflict (HTTP 422 / 409 Conflict) and halts execution.\n\n"
            "3. **Offline Sync & Mesh POS Terminals**: In offline POS environments (e.g. airplane in-flight purchases), terminals store offline payment cryptograms tagged with hardware-derived sequence counters and idempotency keys, guaranteeing deterministic processing once backhaul connectivity restores."
        ),
        "follow_ups": [
            {
                "question": "What happens if a developer generates a new UUID inside the network retry loop of a payment request?",
                "answer": "Idempotency is completely broken; the server treats each retry as a separate distinct transaction, causing multiple duplicate charges."
            },
            {
                "question": "Why do payment servers return HTTP 409 or 422 if an idempotency key is reused with a different request payload?",
                "answer": "To prevent payload tampering or accidental key reuse across distinct commercial orders."
            }
        ]
    },
    {
        "id": "PAY-03",
        "arabic_explanation": (
            "ما هي الفروق الجوهرية بين العمليات المالية الأساسية: التفويض (Authorization)، والعكس (Reversal)، والإلغاء (Void)، والاسترداد (Refund)، والمطابقة (Reconciliation)؟\n\n"
            "1. التفويض (Authorization - Auth):\n"
            "   - عملية حجز المبلغ في حساب حامل البطاقة والتأكد من وجود رصيد كافٍ وصلاحية البطاقة دون سحب المبلغ فوراً إلى حساب التاجر.\n   - يتم سحب المبلغ فعلياً لاحقاً في مرحلة تسمى **التسوية (Capture / Settlement)**.\n\n"
            "2. العكس التلقائي (Reversal):\n   - عملية إلغاء فورية وفنية تُطلقها ماكينة الدفع أو التطبيق **أثناء المعاملة نفسها وقبل إتمام الجلسة**.\n   - تحدث عندما يفشل الهاتف في استلام الرد، أو ينفد ورق الطابعة، أو يفشل قارئ البطاقات الذكية (EMV Chip Failure). يقوم البنك بإلغاء حجز المبلغ فوراً وإعادته للعميل في ثوانٍ.\n\n"
            "3. الإلغاء اليدوي (Void):\n   - إلغاء معاملة كاملة وافق عليها البنك بالفعل، ولكن **قبل إغلاق دورة العمل اليومية وتسوية الحسابات (Before Batch Settlement)**.\n   - ميزته: لا يتم خصم أي رسوم معالجة (Interchange fees) على التاجر أو العميل لأن الأموال لم تنتقل بعد بين البنوك.\n\n"
            "4. الاسترداد (Refund):\n   - إعادة الأموال للعميل **بعد إغلاق الدورة المالية وانتقال الأموال لحساب التاجر (After Settlement)** (مثلاً بعد يومين عندما يرجع العميل البضاعة).\n   - تستغرق من 3 إلى 10 أيام عمل لتظهر في كشف حساب العميل وتتحمل الشركة رسوم معالجة.\n\n"
            "5. المطابقة اليومية (Reconciliation):\n   - فحص وتطابق السجلات المحلية المخزنة في ماكينة الـ POS مع سجلات البنك وخادم الدفع في نهاية كل يوم؛ للتأكد من عدم وجود أي مبالغ مفقودة أو معاملات معلقة."
        ),
        "practical_walkthrough": (
            "جدول مقارنة شامل للعمليات المالية ودورة حياة المعاملة:\n"
            "```markdown\n"
            "| العملية المالية | التوقيت (Timing) | التأثير على الرصيد | الرسوم (Fees) | زمن الظهور للعميل |\n"
            "|---|---|---|---|---|\n"
            "| **Authorization** | لحظة الشراء | حجز المبلغ (Hold) | لا توجد رسوم نهائية | فوري |\n"
            "| **Reversal** | فوري (ثوانٍ بعد عطل فني) | إلغاء الحجز فوراً | صفر | ثوانٍ إلى دقائق |\n"
            "| **Void** | نفس اليوم (قبل إغلاق الـ Batch) | إلغاء العملية بالكامل | صفر رسوم انتقال | 24 إلى 48 ساعة |\n"
            "| **Refund** | بعد أيام (بعد إغلاق الـ Batch) | تحويل عكسي من التاجر للعميل | يتحمل التاجر رسوم المعالجة | 3 إلى 7 أيام عمل |\n"
            "| **Reconciliation** | يومياً في نهاية الـ Shift | مطابقة دفاتر الحسابات | - | تقرير تدقيق مالي |\n"
            "```\n"
            "نموذج الكود لإصدار Reversal فوري عند فشل محلي في أندرويد:\n"
            "```kotlin\n"
            "suspend fun executePaymentWithSafeReversal(paymentRequest: PaymentRequest) {\n"
            "    val txId = paymentDao.insertPending(paymentRequest)\n"
            "    try {\n"
            "        val authResponse = paymentGateway.authorize(paymentRequest)\n"
            "        // إذا انقطع التيار الكهربائي هنا أو تعطل طبع الإيصال، يجب إطلاق Reversal!\n"
            "        printReceiptOrThrow(authResponse)\n"
            "        paymentDao.markCompleted(txId, authResponse.authCode)\n"
            "    } catch (e: ReceiptPrintException) {\n"
            "        // عطل محلي بعد الموافقة -> إطلاق Reversal فوري للبنك لحماية العميل:\n"
            "        reversalQueueManager.enqueueImmediateReversal(txId, paymentRequest)\n"
            "        throw PaymentAbortedException(\"Hardware failure; transaction reversed.\", e)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Authorization holds funds on the card. Reversal immediately cancels an in-flight authorization due to technical failure before completion. Void cancels an approved transaction on the same day before batch settlement with no interchange fees. Refund transfers settled funds back days later incurring fees. Reconciliation audits terminal records against bank ledgers.",
        "best_answer": (
            "Understanding financial lifecycle operations is essential for architects building transactional mobile systems:\n\n"
            "1. **Authorization (Auth)**:\n"
            "   - Verifies card authenticity and places a temporary hold on the customer's credit line. Does not transfer money; funds are transferred only upon subsequent 'Capture' or batch settlement.\n\n"
            "2. **Reversal (Auto-Reversal / 0400 Message)**:\n"
            "   - An automated, immediate technical rollback executed by terminal firmware or client code when a transaction succeeds at the bank but fails locally (e.g. printer paper jam, EMV chip reader failure, or client timeout). Releases the hold within seconds.\n\n"
            "3. **Void**:\n"
            "   - A merchant-initiated cancellation of an approved transaction executed **prior to end-of-day batch settlement**. The transaction is dropped from the clearing batch; no interchange fees are incurred, and the hold drops off.\n\n"
            "4. **Refund**:\n"
            "   - Executed **post-settlement** when funds have already migrated into the merchant's acquiring bank. It initiates an inverse funds transfer, incurring interchange transaction processing fees and taking 3–7 business days.\n\n"
            "5. **Reconciliation**:\n"
            "   - The operational auditing process matching local terminal transaction storage records against payment gateway settlement logs, isolating discrepancies and stranded balances."
        ),
        "deep_answer": (
            "From an EMV L2 kernel and payment network compliance perspective, subtle operational nuances exist:\n\n"
            "1. **The 'Void vs. Reversal' Architecture Nuance**: Developers often confuse Voids and Reversals. A Reversal undoes an authorization that never successfully finished its complete terminal protocol handshake. A Void cancels a transaction that was 100% completed, printed, and approved, but the merchant manually voids it before midnight settlement.\n\n"
            "2. **Partial Reversals in Split Tenders**: In multi-tender checkouts (e.g. paying $50 with Gift Card and $50 with Visa), if the Visa authorization succeeds but the Gift Card fails, the client engine must trigger a Partial Reversal strictly against the Visa transaction while restoring the cart state.\n\n"
            "3. **Reconciliation Batch Balancing**: In Smart POS Android devices (Pax, Poynt, Sunmi), closing the business batch sends an ISO 8583 0500 Batch Upload message summarizing total counts and debit volumes. If terminal and host totals mismatch by even 1 cent, the host halts settlement and forces a manual transaction-by-transaction reconciliation audit."
        ),
        "follow_ups": [
            {
                "question": "Why is a Void commercially preferred over a Refund if a customer cancels an order on the same day?",
                "answer": "Because a Void cancels the transaction before settlement, eliminating payment gateway interchange processing fees for the merchant."
            },
            {
                "question": "What is the difference between Authorization and Settlement (Capture)?",
                "answer": "Authorization holds the funds on the cardholder's credit limit; Settlement captures and transfers the actual money from the issuer to the merchant bank."
            }
        ]
    },
    {
        "id": "PAY-04",
        "arabic_explanation": (
            "ما هي المخاطر الكارثية التي تحدث عندما لا يتم حفظ سجل المعاملة المالية محلياً بشكل دائم ومؤكد (Durably Committed) في أندرويد؟\n\n"
            "1. خطورة الاعتماد على ذاكرة التطبيق (In-Memory State):\n"
            "   - إذا احتفظت ببيانات الدفع في كلاس Kotlin عادي، أو في `ViewModel`، أو في كاش مؤقت غير متزامن مع القرص.\n   - نظام أندرويد يملك كامل الصلاحية لقتل الـ Process في أي جزء من الثانية (Low Memory Killer)، أو قد تنفد بطارية الهاتف فجأة، أو يغلق المستخدم التطبيق قسراً.\n\n"
            "2. المخاطر المالية والتشغيلية المترتبة:\n   - **1. المعاملات الشبحية وفقدان الأموال (Phantom / Stranded Transactions)**:\n     * يرسل التطبيق طلب الدفع للبنك، ويوافق البنك ويخصم 500 دولار من العميل.\n     * قبل أن يحفظ التطبيق الرد في قاعدة البيانات، تنفد البطارية وينطفئ الهاتف!\n     * عند إعادة التشغيل: التطبيق لا يملك أي سجل عن العملية، والتاجر لم يسلم البضاعة للعميل، بينما العميل خُصم منه المبلغ بالفعل! هذه كارثة قانونية وشكاوى نزاع (Chargebacks).\n   - **2. استحالة عمل Reversal أو إلغاء**:\n     * بما أن السجل غير موجود محلياً، لا تستطيع الماكينة إرسال طلب إلغاء (Reversal) للبنك لأنها لا تملك الـ Transaction Reference.\n   - **3. فشل المطابقة اليومية (Reconciliation Blindness)**:\n     * عند مطابقة الحسابات في نهاية اليوم، ستظهر فجوة مالية بين كشف حساب البنك ودفاتر التاجر المحلية.\n\n"
            "3. الحل الهندسي الإلزامي (Durable Persistence First):\n   - **الحفظ المتزامن والمؤكد قبل كل خطوة (Write-Ahead Logging / WAL)**:\n   - تسجيل المعاملة في Room/SQLite مع استدعاء `fsync` الحقيقي للقرص في حالة `Initiated` قبل فتح أي اتصال بالشبكة، وتحديث الحالة ذرياً مع كل خطوة."
        ),
        "practical_walkthrough": (
            "كود Room يوضح الحفظ الدائم والمؤكد للمعاملة قبل بدء الاتصال بالشبكة:\n"
            "```kotlin\n"
            "@Entity(tableName = \"payment_ledger\")\n"
            "data class PaymentRecordEntity(\n"
            "    @PrimaryKey val transactionId: String,\n"
            "    val amountCents: Long,\n"
            "    val currency: String,\n"
            "    val state: String, // INITIATED, PROCESSING, APPROVED, REVERSED\n"
            "    val idempotencyKey: String,\n"
            "    val createdAtTimestamp: Long,\n"
            "    val authorizationCode: String? = null\n"
            ")\n"
            "\n"
            "// الإجراء الهندسي الصارم:\n"
            "class PaymentRepository(private val db: AppDatabase, private val api: PaymentApi) {\n"
            "    suspend fun processPayment(request: PaymentRequest): PaymentResult = withContext(Dispatchers.IO) {\n"
            "        // 1. الحفظ الدائم أولاً على القرص (Durable Commit) قبل الشبكة:\n"
            "        db.runInTransaction {\n"
            "            db.paymentDao().insert(PaymentRecordEntity(\n"
            "                transactionId = request.txId,\n"
            "                amountCents = request.amount,\n"
            "                currency = \"USD\",\n"
            "                state = \"INITIATED\",\n"
            "                idempotencyKey = request.idempotencyKey,\n"
            "                createdAtTimestamp = System.currentTimeMillis()\n"
            "            ))\n"
            "        }\n"
            "\n"
            "        // 2. الآن فقط يُسمح بفتح اتصال الشبكة بأمان:\n"
            "        val response = api.charge(request)\n"
            "        \n"
            "        // 3. تحديث الحالة فوراً على القرص:\n"
            "        db.paymentDao().updateState(request.txId, \"APPROVED\", response.authCode)\n"
            "        PaymentResult.Success(response.authCode)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Failing to durably commit local payment records risks stranded transactions where customers are billed without receiving goods, leaves systems unable to execute auto-reversals after crashes, and causes unreconciled balance discrepancies between merchant terminals and acquiring banks.",
        "best_answer": (
            "In financial systems architecture, volatile in-memory transaction tracking violates foundational ACID guarantees:\n\n"
            "1. **The Stranded Transaction Catastrophe**:\n"
            "   - If transaction state exists merely in ViewModel memory or unflushed cache buffers, an abrupt Android OS process kill or physical battery detachment during payment processing destroys the record. If the payment gateway approved the transaction, the cardholder is debited, but the merchant app boots back up with zero knowledge of the purchase, producing furious customers and severe chargeback penalties.\n\n"
            "2. **Inability to Reconcile or Reverse**:\n"
            "   - To issue an ISO 8583 reversal or query status, the terminal requires the original transaction identifiers (STAN, RRN, correlation ID, amount). Without durable disk persistence, the terminal has no metadata to issue a reversal, stranding customer funds in an indefinite authorization hold.\n\n"
            "3. **Audit and Legal Non-Compliance**:\n"
            "   - Payment standards (PCI-DSS, EMVCo) mandate non-repudiation and immutable transaction audit trails. Failing to durably persist transactions violates payment terminal certification rules.\n\n"
            "4. **The Write-Ahead Persistence Pattern**:\n"
            "   - Strict financial architectures enforce Write-Ahead logging: records are durably committed to SQLite/Room using synchronous write transactions *before* emitting network bytes."
        ),
        "deep_answer": (
            "From an SQLite file-system and hardware storage architecture perspective, durability requires understanding flash storage semantics:\n\n"
            "1. **The SQLite `fsync` and PRAGMA synchronous Guarantee**: Simply calling `db.insert()` does not guarantee the bits have hit physical NAND flash. Android's SQLite uses Write-Ahead Logging (WAL). If `PRAGMA synchronous = OFF` is set, data sits in Linux kernel page cache; a battery removal loses unwritten pages. High-reliability fintech apps mandate `PRAGMA synchronous = FULL` or `NORMAL` to ensure disk barriers flush.\n\n"
            "2. **Atomic State Transition Ledgers**: Payment records should never be updated in-place via loose `UPDATE` statements. Use an append-only transaction ledger (`payment_events` table). Every state change (INITIATED -> PROCESSING -> APPROVED) is inserted as an immutable event row. This provides complete tamper-evident auditability for bank forensic audits.\n\n"
            "3. **Storage Encryption (Encrypted Room)**:\n"
            "   - Persistent payment ledgers containing transaction metadata must be encrypted on disk using SQLCipher backed by the Android Keystore to prevent physical flash extraction attacks on rooted POS hardware."
        ),
        "follow_ups": [
            {
                "question": "What is Write-Ahead Logging (WAL) in financial transaction persistence?",
                "answer": "Writing and flushing transaction intent to persistent storage before executing network or hardware actions, ensuring full recovery after sudden power failure."
            },
            {
                "question": "Why is an append-only event ledger preferred over updating a single status column in payment databases?",
                "answer": "It preserves an immutable, chronological audit trail of every state transition, preventing state corruption and facilitating bank forensic audits."
            }
        ]
    },
    {
        "id": "PAY-05",
        "arabic_explanation": (
            "ما هو معرف ارتباط المعاملة (Transaction Correlation ID)، ولماذا يعتبر ضرورياً عبر جميع طبقات النظام المالي؟\n\n"
            "1. ما هو الـ Correlation ID؟\n"
            "   - هو معرف فريد عالمياً (Globally Unique Identifier - UUID v4) يتم توليده عند نقطة انطلاق المعاملة الأولى (على هاتف أو ماكينة العميل)، ويتم تمريره ومشاركته عبر جميع الأنظمة والخدمات التي تمر بها المعاملة.\n\n"
            "2. رحلة المعاملة المالية عبر الطبقات (Multi-Tier Journey):\n   - ماكينة أندرويد (POS Terminal)\n   -> خادم وسيط الموبايل (Mobile BFF / API Gateway)\n   -> خدمة المدفوعات الأساسية (Core Payment Service)\n   -> معالج الدفع الخارجي (Payment Switch / Adyen / Stripe)\n   -> شبكة البطاقات (Visa / Mastercard)\n   -> البنك المصدر لبطاقة العميل (Issuer Bank).\n\n"
            "3. لماذا يستحيل تشغيل نظام مالي بدونه؟\n   - **1. التتبع الشامل عند حدوث أعطال (Distributed Tracing)**: عندما يشتكي عميل من خصم مبلغ دون استلام تذكرة، كيف تبحث بين ملايين السجلات في Elasticsearch أو Datadog؟ باستخدام الـ Correlation ID، يمكنك استخراج كل سطر Log كُتب في الهاتف وفي 10 سيرفرات مختلفة ببحث واحد في ثانية واحدة!\n   - **2. ربط طلبات الإلغاء والعكس (Reversal & Void Correlation)**: عند إرسال طلب عكس للبنك، يربط البنك طلب الإلغاء بالعملية الأصلية عبر نفس المعرف.\n   - **3. منع تضارب المعاملات المزدوجة (Deduplication Anchor)**: يعمل كمرجع أساسي للـ Idempotency."
        ),
        "practical_walkthrough": (
            "تطبيق نمط الـ Correlation ID في معمارية تطبيق أندرويد مالي وتمريره في الـ Headers والـ Logs:\n"
            "```kotlin\n"
            "// 1. توليد الـ Correlation ID عند بدء تدفق الدفع:\n"
            "data class PaymentSession(\n"
            "    val correlationId: String = \"tx_\" + UUID.randomUUID().toString(),\n"
            "    val amount: Long,\n"
            "    val currency: String\n"
            ")\n"
            "\n"
            "// 2. حقن المعرف في كل طلب شبكة عبر OkHttp Interceptor:\n"
            "class CorrelationIdInterceptor(private val sessionManager: SessionManager) : Interceptor {\n"
            "    override fun intercept(chain: Interceptor.Chain): Response {\n"
            "        val correlationId = sessionManager.currentCorrelationId ?: \"unknown\"\n"
            "        \n"
            "        val authenticatedRequest = chain.request().newBuilder()\n"
            "            .header(\"X-Correlation-ID\", correlationId)\n"
            "            .header(\"X-Request-ID\", UUID.randomUUID().toString()) // معرف فريد لهذا الطلب الفردي\n"
            "            .build()\n"
            "\n"
            "        // 3. تضمين المعرف في سجلات المراقبة المحلية (Structured Logging):\n"
            "        MDC.put(\"correlation_id\", correlationId) // Logback / SLF4J diagnostic context\n"
            "        Timber.tag(\"PaymentFlow\").i(\"Dispatching authorization request for %s\", correlationId)\n"
            "\n"
            "        return chain.proceed(authenticatedRequest)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A transaction correlation ID is an immutable globally unique identifier generated at transaction inception that travels across every architectural tier (client, gateway, core banking, card switch). It enables end-to-end distributed tracing, binds reversals and refunds to the original charge, and anchors distributed deduplication.",
        "best_answer": (
            "A Transaction Correlation ID is the universal thread stitching together distributed financial architectures:\n\n"
            "1. **The Distributed Traversal Problem**:\n"
            "   - A single mobile payment spans multiple boundaries: Android client -> API Gateway -> Payment Orchestrator -> Fraud Engine -> Payment Processor -> Card Scheme (Visa/Mastercard) -> Issuer Bank. Without a persistent identifier generated at the client origin, correlating logs across disconnected microservice silos is impossible.\n\n"
            "2. **Critical Functional Roles**:\n"
            "   - **Distributed Observability**: Enables support and SRE teams to trace an entire transaction's lifecycle across Datadog, OpenTelemetry, and Splunk logs in seconds.\n   - **Reversal and Reconciliation Binding**: When an automated reversal (0400), capture, or refund is triggered, attaching the original correlation ID guarantees the bank switch matches the rollback to the exact ledger entry.\n   - **Idempotency Anchoring**: Serves as the immutable root for idempotency keys, preventing race conditions across concurrent client retries.\n\n"
            "3. **Implementation Standard**:\n"
            "   - Generated as a UUID v4 prefixed with a domain tag (`tx_cor_...`) and transmitted via standard HTTP headers (`X-Correlation-ID`) and ISO 8583 message fields."
        ),
        "deep_answer": (
            "From an OpenTelemetry standards and PCI compliance perspective, correlation IDs govern telemetry hygiene:\n\n"
            "1. **Correlation ID vs. Request ID Distinction**: Senior architects distinguish between `Correlation-ID` and `Request-ID`. The `Correlation-ID` remains identical across the entire multi-step business journey (card tap, 3DS challenge, authorization retry, receipt print). A `Request-ID` is unique to each individual HTTP attempt. Both headers must be transmitted simultaneously.\n\n"
            "2. **PCI-DSS Log Sanitization**: Correlation IDs provide a safe diagnostic handle that eliminates any excuse for logging sensitive Cardholder Data (CHD). Engineers must never log PANs (card numbers) or CVVs for debugging; all telemetry must be indexed exclusively by the safe correlation ID.\n\n"
            "3. **B2B Clearing and Settlement Traceability**: In POS payment hardware, correlation IDs are mapped to ISO 8583 Retrieval Reference Numbers (RRN - Field 37) and Systems Trace Audit Numbers (STAN - Field 11) to maintain end-to-end trace parity with legacy banking mainframes."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between a Correlation ID and a Request ID?",
                "answer": "A Correlation ID persists across the entire multi-step business transaction, while a Request ID is unique to each single HTTP network request."
            },
            {
                "question": "Why does the Correlation ID enhance PCI-DSS compliance?",
                "answer": "It provides a unique search handle for logs and telemetry, eliminating any need to log sensitive cardholder data like PAN or CVV for debugging."
            }
        ]
    },
    {
        "id": "PAY-06",
        "arabic_explanation": (
            "كيف تضمن التخزين الذري الحتمي (Atomic Persistence) لحالة المعاملة ونية العكس (Reversal Intent) في أندرويد؟\n\n"
            "1. خطورة انعدام الذرية (Non-Atomic Persistence Hazard):\n"
            "   - تخيل السيناريو التالي في كود الدفع:\n     1. نقوم بتحديث حالة المعاملة إلى `FAILED`.\n     2. في خطوة منفصلة، نقوم بإضافة طلب إلى جدول الـ `reversal_queue`.\n   - إذا انطفأ الهاتف أو قُتلت العملية بين الخطوتين: أصبحت المعاملة معلمة كـ `FAILED`، ولكن **طلب الـ Reversal لم يُسجل أبداً**!\n   - النتيجة: البنك يحتجز أموال العميل، والتطبيق يعتقد أن العملية فشلت، ولا يوجد أي كود في الخلفية يعرف أنه يجب إرسال Reversal!\n\n"
            "2. مفهوم الذرية (Atomicity) في قواعد البيانات:\n   - كل العمليات تنفذ معاً ككتلة واحدة غير قابلة للتجزئة: إما أن **تنجح جميعها بالكامل (Commit)**، أو **تفشل جميعها وتتراجع كأن شيئاً لم يكن (Rollback)**.\n\n"
            "3. الحل الهندسي: معاملات Room/SQLite الذرية (`@Transaction`):\n   - فتح معاملة ذرية واحدة تدمج:\n     1. تحديث حالة المعاملة الأصلية إلى `IN_DOUBT_NEEDS_REVERSAL`.\n     2. إدراج عنصر جديد في جدول `reversal_queue` يحتوي على كل بيانات الـ ISO 8583 payload.\n     3. جدولة مهمة WorkManager فورية لتنفيذ العكس.\n   - هذا يضمن 100% أن نية العكس محفوظة ومحمية على القرص مهما كانت ظروف تعطل الجهاز."
        ),
        "practical_walkthrough": (
            "تطبيق المعاملات الذرية لحفظ نية العكس في Room باستخدام `@Transaction`:\n"
            "```kotlin\n"
            "@Dao\n"
            "interface PaymentDao {\n"
            "    @Query(\"UPDATE transactions SET status = :newStatus WHERE id = :txId\")\n"
            "    suspend fun updateTransactionStatus(txId: String, newStatus: String)\n"
            "\n"
            "    @Insert(onConflict = OnConflictStrategy.REPLACE)\n"
            "    suspend fun insertReversalIntent(intent: ReversalIntentEntity)\n"
            "\n"
            "    // ✅ المعاملة الذرية الصارمة: مستحيل تنفيذ خطوة دون الأخرى!\n"
            "    @Transaction\n"
            "    suspend fun markInDoubtAndEnqueueReversal(\n"
            "        txId: String,\n"
            "        intent: ReversalIntentEntity\n"
            "    ) {\n"
            "        updateTransactionStatus(txId, \"UNKNOWN_AWAITING_REVERSAL\")\n"
            "        insertReversalIntent(intent)\n"
            "    }\n"
            "}\n"
            "\n"
            "// الاستخدام داخل الـ Repository عند حدوث انقطاع في الشبكة:\n"
            "suspend fun handleTimeoutFailure(txId: String, request: PaymentRequest) {\n"
            "    val reversalIntent = ReversalIntentEntity(\n"
            "        reversalId = UUID.randomUUID().toString(),\n"
            "        originalTxId = txId,\n"
            "        amountCents = request.amount,\n"
            "        payload = request.toIso8583ReversalPayload(),\n"
            "        status = \"PENDING_DISPATCH\"\n"
            "    )\n"
            "    // الذرية تضمن كتابة كلاهما للقرص معاً:\n"
            "    paymentDao.markInDoubtAndEnqueueReversal(txId, reversalIntent)\n"
            "    // إطلاق مهمة WorkManager لمعالجة الطابور:\n"
            "    reversalWorkScheduler.scheduleReversalWorker()\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Ensure atomic persistence of transaction status and reversal intent by executing both operations inside a single database transaction (@Transaction in Room/SQLite). If a sudden power loss occurs, SQLite WAL guarantees that both the status update and the reversal queue insertion succeed together or rollback completely.",
        "best_answer": (
            "Atomic persistence prevents state divergence between payment status records and outbound reversal queues:\n\n"
            "1. **The Dual-Write Vulnerability**:\n"
            "   - When handling an ambiguous payment outcome (such as a gateway read timeout), two state mutations must occur: (1) transitioning the transaction status to `IN_DOUBT`, and (2) enqueuing a reversal payload in the pending dispatch queue. If performed as separate uncoordinated queries, a crash in between drops the reversal intent while recording a failed status, permanently leaking held customer funds.\n\n"
            "2. **SQLite ACID Transaction Guarantees**:\n"
            "   - Wrap both operations in an atomic database transaction using Room's `@Transaction` annotation or `db.runInTransaction { ... }`. SQLite's Write-Ahead Log (WAL) ensures that either both mutations are durably committed to the database file or neither takes effect, preventing partial state writes.\n\n"
            "3. **Deterministic WorkManager Triggering**:\n"
            "   - Following the successful database transaction commit, schedule a persistent `OneTimeWorkRequest` with exponential backoff to dispatch the reversal. If the device powers off immediately after the commit, WorkManager inspects the pending table upon boot and resumes dispatch automatically."
        ),
        "deep_answer": (
            "From an ACID transaction isolation and POS hardware crash perspective, atomicity requires hardware-aware sequencing:\n\n"
            "1. **Isolation Levels in Android SQLite**: SQLite operates with `SERIALIZABLE` transaction isolation by default in WAL mode. This guarantees that background sync workers reading the `reversal_queue` cannot observe a half-written transaction state while the UI thread is committing an in-doubt payment.\n\n"
            "2. **Immutable Reversal Enqueueing**: Store the exact raw cryptographic payload required for the reversal (e.g. original STAN, terminal ID, card cryptogram, transaction amount) inside the `reversal_queue` table. Do not rely on recomputing the payload later, as volatile context variables will be lost if the process restarts.\n\n"
            "3. **Battery-Removal Defense**: On Android POS smart terminals, users frequently pull the battery pack to force-reset frozen screens. By executing `markInDoubtAndEnqueueReversal` before attempting any UI teardown or navigation, the reversal intent is guaranteed to survive the hard reset."
        ),
        "follow_ups": [
            {
                "question": "What catastrophic state occurs if transaction status and reversal queue insertion are not atomic?",
                "answer": "The app records the transaction as failed but loses the reversal intent, leaving the customer debited at the bank with no automated recovery."
            },
            {
                "question": "Why should the reversal queue record store the complete pre-computed reversal payload?",
                "answer": "Because volatile memory context and ephemeral tokens are wiped if the process dies, making it impossible to reconstruct the payload later."
            }
        ]
    },
    {
        "id": "PAY-07",
        "arabic_explanation": (
            "كيف تصمم طابوراً لمعالجة طلبات العكس (Reversal Queue) يصمد أمام نزع البطارية المفاجئ (Battery Pull Survival) في أجهزة الـ POS؟\n\n"
            "1. سيناريو نزع البطارية في أجهزة نقاط البيع (The Battery Pull Scenario):\n"
            "   - في محطات الوقود والمتاجر، إذا تجمدت الشاشة أو تأخرت الشبكة، يقوم الكاشير بنزع بطارية ماكينة الـ POS فجأة لإعادة تشغيلها قسراً!\n   - أي بيانات كانت مخزنة في الـ RAM، أو في Coroutines عادية، أو في SharedPreferences غير محفوظة تنمحي تماماً في أجزاء من الألف من الثانية.\n\n"
            "2. ركائز التصميم المعماري الصامد للصدمات (Battery-Proof Reversal Queue):\n   - **1. قاعدة بيانات Room/SQLite محلية ومحصنة بـ WAL و Sync**:\n     * كل طلب Reversal يتم تخزينه كصف في جدول `reversal_queue` يحتوي على: المعرف الأصلي، المبلغ، كود الـ ISO 8583، وعدد المحاولات السابقة.\n   - **2. استخدام Jetpack WorkManager كجهة تنفيذ إجبارية**:\n     * جدولة مهمة `PeriodicWorkRequest` أو `OneTimeWorkRequest` ذات قيود شبكة (`NetworkType.CONNECTED`).\n     * ميزة WorkManager: يحفظ مهامه في قاعدة بيانات SQLite داخلية خاصة بنظام أندرويد، ويستمع لحدث إقلاع النظام (`BOOT_COMPLETED`)؛ بمجرد إعادة وضع البطارية وإقلاع الجهاز، يعمل الـ Worker تلقائياً في الخلفية!\n   - **3. أسبقية طابور الـ Reversals على أي عملية جديدة (Pre-Flight Reversal Check)**:\n     * **القاعدة الذهبية في الـ POS**: عند فتح التطبيق، أو قبل السماح بأي عملية دفع جديدة، يقوم النظام بفحص `reversal_queue` أولاً؛ وإذا وجد أي Reversal معلق، **يمنع أي عملية دفع جديدة حتى يتم إرسال الـ Reversal المعلق وتفريغ الطابور**!"
        ),
        "practical_walkthrough": (
            "تصميم نظام Reversal Queue متكامل يصمد أمام انقطاع الطاقة المفاجئ:\n"
            "```kotlin\n"
            "// 1. Worker صامد يعتمد على WorkManager لمعالجة طابور الـ Reversals:\n"
            "class ReversalDispatchWorker(\n"
            "    context: Context,\n"
            "    params: WorkerParameters,\n"
            "    private val paymentDao: PaymentDao,\n"
            "    private val paymentApi: PaymentApi\n"
            ") : CoroutineWorker(context, params) {\n"
            "\n"
            "    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {\n"
            "        val pendingReversals = paymentDao.getAllPendingReversals()\n"
            "        for (reversal in pendingReversals) {\n"
            "            try {\n"
            "                val response = paymentApi.sendReversal(reversal.payload)\n"
            "                if (response.isSuccess) {\n"
            "                    paymentDao.deleteReversal(reversal.id)\n"
            "                } else {\n"
            "                    paymentDao.incrementRetryCount(reversal.id)\n"
            "                }\n"
            "            } catch (e: IOException) {\n"
            "                // خطأ شبكة -> إعادة المحاولة التلقائية وفق Backoff Policy:\n"
            "                return@withContext Result.retry()\n"
            "            }\n"
            "        }\n"
            "        Result.success()\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. فحص إلزامي يمنع إجراء أي معاملة جديدة إذا كان هناك Reversal معلق:\n"
            "class PaymentOrchestrator(private val paymentDao: PaymentDao) {\n"
            "    suspend fun canInitiateNewPayment(): Boolean {\n"
            "        val pendingCount = paymentDao.countPendingReversals()\n"
            "        // إذا نزع الكاشير البطارية وأعاد تشغيلها، نرفض أي دفع جديد حتى تصفية المعلقات:\n"
            "        return pendingCount == 0\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design a battery-pull-resilient reversal queue by persisting pre-computed reversal payloads into SQLite using synchronous transactions, binding dispatch execution to Jetpack WorkManager with BOOT_COMPLETED triggers, and enforcing a mandatory pre-flight gate that blocks new transactions until all pending reversals clear.",
        "best_answer": (
            "Engineering a reversal engine capable of surviving sudden physical battery removal requires a three-tiered architecture:\n\n"
            "1. **Durable Storage with Synchronous Flash Flush**:\n"
            "   - Reversals must be committed to a dedicated SQLite `reversal_queue` table before any UI timeout resolution. Enforce `PRAGMA synchronous = NORMAL` or `FULL` to ensure kernel page buffers flush to physical flash memory before control flow returns.\n\n"
            "2. **Resilient Execution via Jetpack WorkManager**:\n"
            "   - Enqueue reversal dispatches via `WorkManager.enqueueUniqueWork()` using an `ExistingWorkPolicy.APPEND_OR_REPLACE` policy with `Constraints(NetworkType.CONNECTED)`.\n   - WorkManager registers system broadcast receivers (`ACTION_BOOT_COMPLETED`, `ACTION_MY_PACKAGE_REPLACED`). When the battery is re-inserted and Android boots up, WorkManager automatically resurrects the worker without user intervention.\n\n"
            "3. **The Pre-Flight Terminal Lockout Gate**:\n"
            "   - Financial certification (EMV/PCI) mandates that a terminal must clear historical reversals before accepting new card insertions. On app cold start or before launching a new transaction flow, the system queries the reversal queue. If entries exist, it halts new sales and flushes the queue first."
        ),
        "deep_answer": (
            "From an EMV L2 payment kernel and regulatory certification perspective, reversal queues follow strict protocol rules:\n\n"
            "1. **Reversal Retry Limits and Poison Pill Mitigation**: If a reversal request is rejected by the issuer host with a definitive non-retryable response (e.g. `ISO 8583 Response Code 12: Invalid Transaction` or `Code 94: Duplicate Transmission`), retrying forever locks the POS terminal indefinitely. The reversal worker must inspect response codes: definitive rejections transition the record to an `AUDIT_ALERT_FAILED` state, unblocking the terminal while alerting engineering telemetry.\n\n"
            "2. **FIFO Queue Ordering**: Reversals must be dispatched in strict First-In-First-Out order. Discarding ordering risks reversing a subsequent authorization instead of the intended original transaction.\n\n"
            "3. **Hardware Keystore Signature Durability**: Reversal payloads often contain encrypted EMV card cryptograms (ARQC / AAC) generated during the physical chip read. Because the physical chip is gone upon battery restart, this exact cryptogram must be safely encrypted in the persistent reversal queue record using the Android Keystore."
        ),
        "follow_ups": [
            {
                "question": "Why must an Android POS terminal block new card transactions if a pending reversal exists in the queue?",
                "answer": "Payment certification rules require clearing in-doubt balance discrepancies with the host before creating new potential financial exposures."
            },
            {
                "question": "How does WorkManager guarantee execution resumption after a physical battery removal?",
                "answer": "WorkManager persists tasks in internal SQLite storage and registers system `BOOT_COMPLETED` receivers to reschedule pending workers upon device reboot."
            }
        ]
    },
    {
        "id": "PAY-08",
        "arabic_explanation": (
            "كيف تمنع طلبات الدفع المكررة (Duplicate Payment Requests) الناتجة عن نفاد وقت واجهة المستخدم (UI Timeout) أو نقر العميل المتكرر؟\n\n"
            "1. سيناريوهات التكرار الشائعة في واجهة المستخدم (UI Hazards):\n"
            "   - **1. النقر المزدوج المتسارع (Double-Tapping / Rapid Clicks)**: ينقر المستخدم على زر \"تأكيد الدفع\" مرتين بسرعة قبل أن يتم تعطيل الزر (Disable).\n   - **2. نفاد وقت الواجهة (UI Timeout)**: تستغرق استجابة البنك 25 ثانية، بينما شاشة التطبيق مضبوطة على إظهار رسالة خطأ بعد 15 ثانية! يرى المستخدم رسالة فشل، فيضغط الزر مرة ثانية بينما الطلب الأول ما زال قيد المعالجة في البنك!\n   - **3. استدارة الشاشة (Configuration Changes)**: تدوير الشاشة يعيد إنشاء الـ Activity فيقوم بكود البدء مرة أخرى إذا لم تكن المعمارية سليمة.\n\n"
            "2. آليات المنع متعددة الطبقات (Multi-Layer Defense):\n   - **الطبقة 1: واجهة المستخدم (UI Layer - Debounce & State)**:\n     * تعطيل زر الدفع فوراً عند أول نقرة (`enabled = false`) وإظهار مؤشر تحميل (Loading Spinner).\n     * استخدام `throttleFirst(1000ms)` في تدفقات Compose أو Coroutines لمنع النقرات المتتالية.\n   - **الطبقة 2: طبقة إدارة الحالة (ViewModel & State Machine)**:\n     * استخدام كائن حالة أحادي (`PaymentUiState.Processing`)؛ إذا كان الـ ViewModel في حالة `Processing`، يتجاهل أي حدث دفع جديد فوراً.\n   - **الطبقة 3: طبقة النطاق والبيانات (Repository & Mutex)**:\n     * استخدام **Kotlin `Mutex`** لمنع إطلاق دالتين للدفع بالتوازي لنفس الـ Session.\n   - **الطبقة 4: طبقة الشبكة (Network - Idempotency Key)**:\n     * ربط الطلب بـ Idempotency-Key محفوظ في Room، بحيث يرفض الخادم أي طلب مكرر لنفس المعاملة."
        ),
        "practical_walkthrough": (
            "تنفيذ هندسي متكامل لمنع تكرار طلبات الدفع عبر الطبقات الثلاث:\n"
            "```kotlin\n"
            "// 1. في الـ ViewModel: حماية عبر Mutex وحالة المعالجة الأحادية:\n"
            "class CheckoutViewModel(private val repository: PaymentRepository) : ViewModel() {\n"
            "    private val paymentMutex = Mutex()\n"
            "    private val _uiState = MutableStateFlow<CheckoutUiState>(CheckoutUiState.Idle)\n"
            "    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()\n"
            "\n"
            "    fun onPayClicked(orderId: String, amount: Long) {\n"
            "        viewModelScope.launch {\n"
            "            // حماية Mutex: إذا كان هناك دفع جاري، يتم تجاهل النقرة فوراً:\n"
            "            if (!paymentMutex.tryLock()) return@launch\n"
            "            try {\n"
            "                _uiState.value = CheckoutUiState.Processing\n"
            "                val result = repository.executePayment(orderId, amount)\n"
            "                _uiState.value = CheckoutUiState.Success(result)\n"
            "            } catch (e: Exception) {\n"
            "                _uiState.value = CheckoutUiState.Error(e.message ?: \"Payment failed\")\n"
            "            } finally {\n"
            "                paymentMutex.unlock()\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. في واجهة Compose: زر معطل ومحمي ضد النقر المتكرر:\n"
            "@Composable\n"
            "fun CheckoutScreen(viewModel: CheckoutViewModel) {\n"
            "    val state by viewModel.uiState.collectAsStateWithLifecycle()\n"
            "    val isProcessing = state is CheckoutUiState.Processing\n"
            "\n"
            "    Button(\n"
            "        onClick = { viewModel.onPayClicked(\"ord_123\", 5000) },\n"
            "        enabled = !isProcessing // تعطيل الزر فورياً عند بدء الدفع\n"
            "    ) {\n"
            "        if (isProcessing) {\n"
            "            CircularProgressIndicator(modifier = Modifier.size(24.dp))\n"
            "        } else {\n"
            "            Text(\"Pay $50.00\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Prevent duplicate payments by implementing multi-layered safeguards: immediately disable buttons and display loading spinners on the UI, protect ViewModel dispatch using a Kotlin Mutex or single-flight state guards, calibrate UI timeouts to exceed backend gateway SLAs, and anchor requests with persistent Idempotency Keys.",
        "best_answer": (
            "Preventing duplicate payment requests requires an end-to-end defense-in-depth architecture across UI, presentation, and data layers:\n\n"
            "1. **Presentation & UI Layer Defenses**:\n"
            "   - **Instant Click Debouncing & Button Disabling**: The moment a user taps 'Pay', the button transitions to `enabled = false` and displays an explicit indeterminate progress spinner. Event handlers use `throttleFirst` to drop rapid taps.\n   - **ViewModel State Guards via Mutex**: Protect execution blocks using Kotlin `Mutex.tryLock()`. If a payment operation is currently active, subsequent invocations return immediately without launching duplicate coroutines.\n\n"
            "2. **Timeout SLA Alignment**:\n"
            "   - A frequent architectural flaw is setting a 15-second client UI timeout when the payment gateway has a 30-second acquiring SLA. The UI prematurely times out and shows a retry button while the backend transaction is still processing. Client timeouts must exceed gateway read timeouts, and timeouts must transition to an 'In-Doubt Checking' screen rather than a generic failure screen.\n\n"
            "3. **Persistent Idempotency Layer**:\n"
            "   - If the user manages to force-retry (e.g. by killing and restarting the app), the order entity retains the original `idempotency_key`. The subsequent network call presents the identical key to the payment gateway, which returns the original result rather than debiting the customer again."
        ),
        "deep_answer": (
            "From an Android lifecycle and process death perspective, state handling requires lifecycle-proof architecture:\n\n"
            "1. **Configuration Changes & Process Recreation**: If a user rotates the screen during payment processing, a naive Activity might re-invoke `onCreate` and trigger duplicate payment logic. Managing payment operations inside an injected Application-scoped or WorkManager-backed service unbinds transaction execution from transient UI component lifecycles.\n\n"
            "2. **The 'In-Doubt' Loading Screen**: When an inevitable client-side timeout occurs after 35 seconds, never display a simple 'Transaction Failed — Try Again' dialog. Display: 'Verifying payment with your bank... Please do not re-submit.' Query the transaction status endpoint before allowing the user to initiate a new checkout session.\n\n"
            "3. **Backend Race Condition Mitigation**: What if two duplicate requests arrive at the backend within 5 milliseconds due to multi-threaded glitches? Distributed Redis locks on `idempotency_key` ensure only one worker thread enters the payment processing block, returning an HTTP 409 Conflict to the concurrent duplicate."
        ),
        "follow_ups": [
            {
                "question": "Why should client UI timeouts always be longer than backend payment gateway timeouts?",
                "answer": "To prevent premature client failure dialogs while the backend is still actively and legitimately capturing funds."
            },
            {
                "question": "How does `Mutex.tryLock()` prevent duplicate payment executions in Kotlin Coroutines?",
                "answer": "It atomically attempts to acquire the lock without suspending; if already held by an in-flight payment, it returns false and exits immediately."
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
    for item in PAY_01_08:
        existing_dict[item["id"]] = item

    all_items = list(existing_dict.values())
    all_items.sort(key=lambda x: x["id"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"Updated {DATA_FILE} with questions PAY-01 to PAY-08. Total questions: {len(all_items)}")


if __name__ == "__main__":
    main()
