#!/usr/bin/env python3
"""
Elevation script for PAY questions: PAY-01 to PAY-08.
Topic: Payment/POS & Security Scenarios (PAY)
Phase 5, Batch 1
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "سيناريوهات الدفع ونقاط البيع (POS) وتأمين المعاملات المالية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# PAY-01: What is a payment state machine (initiated, processing, approved, declined, unknown, reversed)?
# ==========================================
DATA["PAY-01"] = {
    "concept_en": """A payment state machine is a deterministic finite state automaton governing the lifecycle of financial transactions across mutually exclusive, strictly monotonic states:
- The Binary Fallacy in Financial Systems:
  - In ordinary applications, network requests are often modeled as a boolean `Result.Success` or `Result.Failure`.
  - In point-of-sale (POS) and fintech systems, this simplification causes catastrophic double-charging. A network timeout does not mean the transaction failed; the issuing bank may have deducted funds while the mobile client failed to receive the TCP packet.
- The 6 Canonical Payment States:
  1. `Initiated`: Transaction intent, cryptographic correlation ID, and amount are durably committed to SQLite/Room before opening any network socket.
  2. `Processing`: The transaction payload has been dispatched to the payment gateway or bank switch; client awaits cryptographic authorization.
  3. `Approved`: The issuer returns a signed authorization code confirming funds hold; receipt can be printed.
  4. `Declined`: Explicit rejection code from the card issuer (e.g., insufficient balance, expired card, incorrect PIN); a definitive terminal state requiring no retry.
  5. `Unknown` (In-Doubt): The socket dropped, timed out, or process terminated while waiting for response. The ledger state is undefined; funds may or may not be debited.
  6. `Reversed`: An automated reversal (such as ISO 8583 message 0400/0420) was dispatched and acknowledged, releasing any pre-authorized hold on the cardholder's funds.
- Monotonicity and Durability Invariants:
  - State transitions must be strictly unidirectional and written using write-ahead logging (WAL) transactions. Once a transaction reaches `Approved` or `Declined`, it can never transition back to `Processing`.""",
    "walkthrough_en": """Modeling a deterministic financial payment state machine in Kotlin:
```kotlin
sealed interface PaymentState {
    val transactionId: String
    val amountCents: Long

    // 1. Durably recorded in Room prior to network transmission
    data class Initiated(
        override val transactionId: String,
        override val amountCents: Long,
        val createdAtEpoch: Long
    ) : PaymentState

    // 2. In-flight over HTTPS/TCP to gateway
    data class Processing(
        override val transactionId: String,
        override val amountCents: Long,
        val idempotencyKey: String
    ) : PaymentState

    // 3. Terminal success: Authorization code granted
    data class Approved(
        override val transactionId: String,
        override val amountCents: Long,
        val authCode: String,
        val rrn: String // Retrieval Reference Number
    ) : PaymentState

    // 4. Terminal failure: Explicit bank refusal
    data class Declined(
        override val transactionId: String,
        override val amountCents: Long,
        val errorCode: String,
        val reason: String
    ) : PaymentState

    // 5. In-Doubt state: Network timeout or crash during flight
    data class Unknown(
        override val transactionId: String,
        override val amountCents: Long,
        val failureReason: Throwable
    ) : PaymentState

    // 6. Terminal release: Pre-authorization hold cancelled
    data class Reversed(
        override val transactionId: String,
        override val amountCents: Long,
        val reversalReference: String
    ) : PaymentState
}
```""",
    "short_en": """A payment state machine is a deterministic automaton that manages financial lifecycles across six explicit states: Initiated, Processing, Approved, Declined, Unknown, and Reversed. It replaces dangerous boolean success-failure models with durable, crash-resilient transitions, ensuring that network timeouts enter an in-doubt state requiring automated reconciliation or ISO 8583 reversal rather than risking double-charging.""",
    "structured_en": """A deterministic payment state machine is the core architectural safeguard in mobile point-of-sale and fintech engineering.
Standard mobile applications frequently treat network operations as a binary success or failure. In financial systems, this binary assumption leads to double-charging because a socket timeout indicates an ambiguous state where the bank might have debited funds while the client lost connectivity.
The state machine models six mutually exclusive states. Initiated guarantees that the transaction intent and idempotency key are durably saved to local storage before opening a network socket. Processing marks the request in-flight. Approved and Declined represent definitive terminal outcomes from the card issuer.
The critical state is Unknown or In-Doubt, triggered by connection drops or process termination. Transactions in this state are never treated as declined and are never naively retried. Instead, they transition to Reversed via an automated ISO 8583 reversal message or are resolved through backend ledger reconciliation.""",
    "deep_senior_en": """From an ISO 8583 banking switch and EMV terminal architecture perspective, a payment state machine enforces ledger consistency across distributed, unreliable mobile networks.
The most dangerous vulnerability in client-side payments is treating an in-doubt state as a declined transaction. When a merchant taps to charge fifty dollars, a thirty-second gateway timeout can occur after the issuing bank captures the funds but before the mobile client receives the HTTP response. If the client naive logic marks this as failed, the cashier prompts the customer to swipe again, causing a catastrophic duplicate charge and merchant chargeback penalties.
To prevent this, the client architecture must enforce an atomic state machine backed by persistent storage like SQLite Room with Write-Ahead Logging. The transition to Initiated occurs inside a local transaction. When entering Processing, the app assigns an immutable idempotency key and correlation ID.
If a timeout or sudden power failure occurs, the state engine transitions to Unknown. The system immediately enqueues a background task in an isolated reversal queue, utilizing ISO 8583 0400 reversal messages. Furthermore, before initiating any subsequent transaction on the terminal, the POS software queries the gateway status endpoint. If the gateway confirms that authorization succeeded, the local transaction updates monotonically to Approved and prints the customer receipt. If authorization failed or was absent, the reversal releases held funds. This ensures perfect accounting balance regardless of battery pulls or carrier drops.""",
    "meta_ar": {
        "id": "PAY-01",
        "questionAr": "ما هي آلة حالة الدفع (Payment State Machine) وما هي حالاتها الست الأساسية ولماذا تعتبر حاسمة في الأنظمة المالية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصميم آلات الحالات المحددة للمدفوعات، تجنب الفخ الثنائي (Binary Fallacy)، تفصيل الحالات الست (Initiated, Processing, Approved, Declined, Unknown, Reversed)، بروتوكولات معالجة الحالة المعلقة (In-Doubt)، واستخدام رسائل العكس التلقائي ISO 8583.",
        "concept_ar": "تمثل آلة حالة الدفع (Payment State Machine) نموذجاً حتمياً محكماً لإدارة دورة حياة المعاملة المالية عبر حالات صارمة وأحادية الاتجاه: في التطبيقات التقليدية يُكتفى بنتيجة النجاح أو الفشل، أما في الأنظمة المالية ونقاط البيع (POS)، فإن هذا التبسيط يسبب كوارث مالية كالسحب المزدوج (Double-Charging)؛ لأن انقطاع الشبكة بعد خصم الرصيد وقبل استلام الرد يترك المعاملة في حالة غير معلومة. وتتكون الآلة من 6 حالات: الأولى `Initiated` حيث تُسجل نية الدفع ومفتاح الحتمية محلياً في قاعدة البيانات قبل فتح الاتصال؛ والثانية `Processing` حيث يُرسل الطلب للبنك؛ والثالثة `Approved` كحالة نهائية تؤكد استلام كود التفويض وطباعة الإيصال؛ والرابعة `Declined` كرفض صريح ونهائي من البنك لعدم كفاية الرصيد؛ والخامسة `Unknown` أو `In-Doubt` وهي أخطر الحالات وتحدث عند انقطاع الاتصال أو موت التطبيق أثناء المعالجة وتتطلب استعلاماً لاحقاً أو إرسال طلب عكس (Reversal)؛ والسادسة `Reversed` لتأكيد إلغاء حجز الأموال واستعادة رصيد العميل.",
        "walkthrough_ar": """تمثيل آلة حالة الدفع الصارمة باستخدام كوتلن المقفولة (Sealed Interface):
```kotlin
sealed interface PaymentState {
    val transactionId: String
    val amountCents: Long

    // 1. تم الحفظ محلياً في قاعدة البيانات قبل فتح الشبكة
    data class Initiated(
        override val transactionId: String,
        override val amountCents: Long,
        val createdAtEpoch: Long
    ) : PaymentState

    // 2. الطلب قيد الإرسال لمعالج الدفع
    data class Processing(
        override val transactionId: String,
        override val amountCents: Long,
        val idempotencyKey: String
    ) : PaymentState

    // 3. حالة نجاح نهائية: وصل كود التفويض الرسمي
    data class Approved(
        override val transactionId: String,
        override val amountCents: Long,
        val authCode: String,
        val rrn: String // رقم مرجع الاسترجاع
    ) : PaymentState

    // 4. حالة رفض نهائية من البنك المصدر للبطاقة
    data class Declined(
        override val transactionId: String,
        override val amountCents: Long,
        val errorCode: String,
        val reason: String
    ) : PaymentState

    // 5. حالة معلقة خطيرة: انقطاع شبكة أو سقوط التطبيق أثناء الطيران
    data class Unknown(
        override val transactionId: String,
        override val amountCents: Long,
        val failureReason: Throwable
    ) : PaymentState

    // 6. تم إلغاء حجز الأموال بنجاح واستعادة الرصيد
    data class Reversed(
        override val transactionId: String,
        override val amountCents: Long,
        val reversalReference: String
    ) : PaymentState
}
```""",
        "why_it_matters_ar": "التعامل مع عمليات الدفع كقيمة ثنائية نجاح أو فشل يؤدي للسحب المزدوج من حسابات العملاء وغرامات مالية باهظة وخسارة مصداقية المنظومة البنكية.",
        "worked_example_ar": "أثناء شراء وجبة بمبلغ 200 جنيه عبر نقطة بيع، انقطع اتصال الشريحة بعد الخصم مباشرة؛ وضعت آلة الحالة العملية كـ Unknown وأرسلت رسالة عكس تلقائي ISO 8583 ألغت الحجز خلال ثانيتين دون سحب مكرر.",
        "trade_offs_ar": "إلزام كل معاملة بالمرور بجميع الحالات وتسجيلها على القرص يضيف بضع مللي ثوانٍ؛ لكنه يمنع تماماً العجز المالي وضياع القيود المحاسبية في دفاتر التاجر والبنك.",
        "failure_modes_ar": "أخطر الأخطاء هو اعتبار مهلة الاتصال (Timeout) كحالة رفض والسماح للمستخدم بإعادة الدفع فوراً، أو حفظ الحالة في ذاكرة الرام فقط فتضيع المعاملة تماماً عند نفاد البطارية.",
        "production_perspective_ar": "في أنظمة المدفوعات المعتمدة، ترتبط آلة الحالة بمحرك WorkManager وقاعدة بيانات Room مفعل فيها نمط WAL لضمان استئناف معالجة الحالات المعلقة فور إعادة تشغيل الجهاز.",
        "how_to_answer_ar": "ابدأ برفض النموذج الثنائي، واشرح الحالات الست بدقة، وركز على خطورة حالة Unknown وكيف تتطلب إرسال Reversal أو استعلام مطابقة Reconciliation بدلاً من إعادة المحاولة.",
        "talking_points_ar": "آلة حالة الدفع، الفخ الثنائي Binary Fallacy، الحالات الست، حالة الشك In-Doubt، رسائل العكس ISO 8583 0400، ومطابقة القيود المحاسبية Reconciliation.",
        "follow_ups_ar": "كيف تتعامل مع حالة انقطاع الكهرباء أثناء طباعة الإيصال بعد استلام حالة Approved؟ وما هو دور رقم الـ RRN في تتبع المعاملات؟",
        "self_check_ar": "هل شرحت الحالات الست بالكامل، ووضحت خطورة اعتبار مهلة الاتصال فشلاً، وفصلت آلية العكس والمطابقة؟",
        "references_ar": f"- [EMVCo: EMV Integrated Circuit Card Specifications](https://www.emvco.com/emv-technologies/) — المواصفات القياسية العالمية لمعالجة مدفوعات البطاقات الذكية ونقاط البيع.\n- [Stripe Engineering: Designing robust payment state machines](https://stripe.com/blog/designing-robust-payment-systems) — الدليل المعماري لتصميم أنظمة الدفع المقاومة للأعطال والشبكات المتقطعة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """آلة حالة الدفع هي نموذج حتمي يدير المعاملة المالية عبر ست حالات صارمة: البدء Initiated، والمعالجة Processing، والقبول Approved، والرفض Declined، والحالة المعلقة Unknown، والإلغاء Reversed. تلغي الآلة الفخ الثنائي الشائع للنجاح والفشل، وتضمن أن انقطاع الشبكة يضع المعاملة في حالة شك تتطلب عكساً تلقائياً أو مطابقة بدلاً من السحب المزدوج.""",
        "best_answer_ar": """تمثل آلة حالة الدفع الصارمة صمام الأمان المعماري الأول في تطبيقات التكنولوجيا المالية ونقاط البيع المحمولة.
في التطبيقات العادية يتعامل المطور مع الاتصال كقيمة ثنائية نجاح أو فشل، لكن هذا المنطق كارثي في المدفوعات؛ لأن انقطاع الشبكة بعد خصم المبلغ وقبل وصول الرد للهاتف يترك العملية معلقة، فإذا اعتبرناها فاشلة وسحبنا مجدداً يدفع العميل مرتين.
لذلك تقسم المعمارية المعاملة إلى ست حالات حتمية؛ تبدأ بـ Initiated بتسجيل نية الدفع محلياً على القرص قبل لمس الشبكة، ثم Processing أثناء انتقال البيانات. وفي حال نجاح الخصم نصل لـ Approved، أو Declined إذا رفض البنك المعاملة لعدم كفاية الرصيد.
الحالة الأكثر أهمية وخطورة هي Unknown أو In-Doubt التي تنشأ عند انتهاء مهلة الاتصال؛ حيث يحظر النظام إعادة الخصم، ويقوم بدلاً من ذلك بتسجيل طلب عكس تلقائي أو الاستعلام عن حالة العملية لضمان توازن الحسابات التام.""",
        "deep_answer_ar": """من منظور معايير التحويل المصرفي ISO 8583 وهندسة نقاط البيع المعتمدة، تعد آلة حالة الدفع الضامن الوحيد لتطابق الدفاتر المحاسبية عبر الشبكات اللاسلكية غير الموثوقة.
الخلل الأكبر في تصميم تطبيقات الدفع هو التعامل مع مهلة الاتصال كمعاملة مرفوضة؛ فإذا استغرقت الشبكة ثلاثين ثانية بعد إرسال التفويض، قد يكون خادم البنك قد حجز المبلغ بنجاح بالفعل. وبناءً على ذلك، تلزم المعمارية النظام بعدم تكرار الطلب مطلقاً، بل إدخال المعاملة فوراً في حالة الشك Unknown.
يتم تثبيت هذه الحالات داخل قاعدة بيانات محلية كـ Room بنمط كتابة مسبقة WAL لضمان النجاة من موت التطبيق المفاجئ. وعند الدخول في حالة الشك، يُدرج النظام مهمة خلفية ذات أولوية قصوى لإرسال رسالة عكس تلقائي ISO 8583 0400 لتحرير المبلغ المحجوز في حساب العميل فوراً.
كما تفرض البرمجيات المصرفية إجراء استعلام مطابقة Status Inquiry مع معالج الدفع قبل الشروع في أي عملية بيع تالية؛ فإذا أكد المعالج اكتمال العملية بنجاح، تُسجل كـ Approved ويُطبع الإيصال، وإلا يُلغى الحجز تماماً. هذا التتابع الحتمي الصارم يقضي نهائياً على أخطاء السحب المكرر ويحمي التاجر والعميل من النزاعات المالية، مع توثيق كود الخطأ والرد البنكي المشفر في سجلات التدقيق لتوفير أدلة قاطعة عند فحص الحسابات السنوية."""
    }
}

# ==========================================
# PAY-02: What is idempotency, and why does it matter for financial transactions?
# ==========================================
DATA["PAY-02"] = {
    "concept_en": """Idempotency is a mathematical and architectural property whereby performing an operation multiple times produces the exact same outcome as performing it once:
- Mathematical and API Definition:
  - Formally, $f(f(x)) = f(x)$.
  - In financial HTTP/RPC APIs, an idempotent payment endpoint ensures that submitting the identical payment intent multiple times results in exactly one debit from the payer's ledger and returns the identical response payload.
- The Financial Necessity of Idempotency:
  - Mobile networks frequently drop TCP packets during the ACK phase: the gateway processes the charge, but the cellular tower loses connectivity before delivering the response.
  - The client networking layer (or an aggressive retry policy) resends the HTTP request.
  - Without idempotency, the backend interprets the retry as a distinct charge instruction, executing multiple debits for a single physical checkout.
- Mechanics of Idempotency Keys:
  - Unique Identifier: Client generates a cryptographically random UUIDv4 or deterministic composite key (`terminalId + localSequenceNumber + timestamp`).
  - Request Header: Client attaches the key (e.g., `Idempotency-Key: 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d`).
  - Gateway Ledger Cache: Gateway records the key in a distributed lock (e.g., Redis). If a second request arrives with the identical key:
    - If first request is still in-flight: Returns `409 Conflict` or awaits resolution.
    - If first request completed: Replays the cached authorization response without hitting the card processing network.
- Client-Side Durability Requirements:
  - The idempotency key must be generated and persisted alongside the transaction record in local storage before the initial HTTP request. Regenerating keys upon retry destroys idempotency guarantees.""",
    "walkthrough_en": """Implementing resilient client-side idempotency handling in Kotlin:
```kotlin
data class PaymentIntent(
    val orderId: String,
    val amountCents: Long,
    val idempotencyKey: String = UUID.randomUUID().toString()
)

class PaymentRepository(
    private val paymentDao: PaymentDao,
    private val paymentApi: PaymentApiService
) {
    suspend fun executePayment(orderId: String, amount: Long): PaymentResult {
        // Step 1: Ensure durable idempotency key persistence before network dispatch
        val record = paymentDao.getOrCreatePaymentRecord(
            orderId = orderId,
            amount = amount,
            idempotencyKey = UUID.randomUUID().toString()
        )

        // Step 2: Transmit using the persisted, immutable idempotency key
        return try {
            val response = paymentApi.charge(
                idempotencyKey = record.idempotencyKey,
                body = ChargeRequest(record.orderId, record.amount)
            )
            paymentDao.markApproved(record.id, response.authCode)
            PaymentResult.Success(response.authCode)
        } catch (e: IOException) {
            // Network dropped mid-flight: Never generate a new key on retry!
            paymentDao.markInDoubt(record.id)
            PaymentResult.InDoubt(record.idempotencyKey)
        }
    }
}
```""",
    "short_en": """Idempotency guarantees that executing an operation multiple times produces the identical side effect as executing it once. In financial transactions, clients generate a unique idempotency key persisted before dispatch, attaching it to payment requests. When network drops cause retry attempts, the backend recognizes the key and replays the original response instead of double-billing the customer.""",
    "structured_en": """Idempotency is an indispensable architectural guarantee in financial transaction processing.
By mathematical definition, an operation is idempotent if repeating it yields the exact same state as the initial execution. In mobile payment systems, cellular handovers and transient timeouts frequently interrupt connections after the payment switch has approved a charge but before the mobile client receives the confirmation packet.
If an application resends the charge request without an idempotency safeguard, the server treats it as a brand-new transaction, debiting the customer a second time.
To enforce idempotency, the mobile client creates an immutable idempotency key, such as a UUID, and saves it in durable local storage alongside the transaction record. When the request is sent, this key is included in the headers. The payment gateway verifies the key in a distributed cache; if it detects a repeated key, it returns the cached authorization result without re-charging the credit card. Crucially, the client must never regenerate the key during retries.""",
    "deep_senior_en": """From a distributed systems and financial ledger perspective, idempotency is the foundational bridge between at-least-once network delivery and exactly-once business semantics.
Under the CAP theorem and the realities of wireless mobile communications, exactly-once network transmission is physically impossible. Networks can only guarantee at-most-once or at-least-once delivery. Financial engineering mandates an at-least-once retry posture to ensure that transactions are never lost. However, pairing an at-least-once transport layer with non-idempotent ledger endpoints guarantees duplicate debit anomalies.
The implementation requires coordinated discipline across both client and gateway layers. The client must never generate the idempotency key in memory inside a ViewModel or coroutine scope that could be destroyed and re-instantiated. Instead, the key generation must be tied to a local database transaction. The entity schema stores the business order ID, the amount, the status, and the idempotency key as a unique constraint.
When a timeout occurs, any retry mechanism executed by the app or an automated WorkManager task must read the existing idempotency key from the database record. On the backend, the gateway employs distributed locking to prevent race conditions from concurrent duplicate submissions. If a concurrent retry arrives while the first call is being processed by the card network, the gateway halts execution until the lock releases, then returns the original response. This decoupled architectural pattern ensures flawless financial accuracy across volatile networks.""",
    "meta_ar": {
        "id": "PAY-02",
        "questionAr": "ما هي خاصية حتمية التكرار (Idempotency) ولماذا تعتبر جوهرية للمعاملات المالية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "مفهوم حتمية التكرار الرياضي والمعماري، آلية عمل مفاتيح الحتمية (Idempotency Keys)، معالجة انقطاع الشبكة أثناء استلام الرد، منع السحب المكرر (Double Debiting)، وحفظ المفاتيح محلياً على القرص.",
        "concept_ar": "تعني حتمية التكرار (Idempotency) في علوم الحاسوب وهندسة البرمجيات أن تنفيذ العملية عدة مرات ينتج عنه نفس النتيجة والحالة تماماً كأنها نُفذت لمرة واحدة: رياضياً $f(f(x)) = f(x)$. وفي الخدمات المالية، تعتبر خاصية حتمية التكرار ركيزة أساسية لمنع الخصم المزدوج من حساب العميل؛ فعند انقطاع الاتصال اللاسلكي بعد قيام البنك بخصم المبلغ وقبل وصول رسالة التأكيد للهاتف، يقوم التطبيق أو نظام إعادة المحاولة بإعادة إرسال الطلب. ودون مفتاح حتمية (Idempotency Key)، سيتعامل الخادم مع الطلب المكرر كعملية شراء جديدة ويخصم المبلغ مرة ثانية. وتتحقق الحتمية بقيام التطبيق بتوليد معرّف عشوائي فريد وحفظه محلياً في قاعدة البيانات مع بيانات الفاتورة قبل إرسال الطلب، ثم تضمينه في ترويسات الطلب؛ حيث يفحص معالج الدفع المفتاح في ذاكرة مؤقتة موزعة، فإذا وجده مكرراً يرجع نفس الرد السابق المسجل دون لمس الحساب البنكي مجدداً.",
        "walkthrough_ar": """تطبيق نمط مفاتيح الحتمية المحفوظة محلياً في كوتلن:
```kotlin
data class PaymentIntent(
    val orderId: String,
    val amountCents: Long,
    val idempotencyKey: String = UUID.randomUUID().toString()
)

class PaymentRepository(
    private val paymentDao: PaymentDao,
    private val paymentApi: PaymentApiService
) {
    suspend fun executePayment(orderId: String, amount: Long): PaymentResult {
        // 1. توليد وحفظ مفتاح الحتمية محلياً بشكل دائم قبل أي اتصال شبكي
        val record = paymentDao.getOrCreatePaymentRecord(
            orderId = orderId,
            amount = amount,
            idempotencyKey = UUID.randomUUID().toString()
        )

        // 2. إرسال الطلب باستخدام المفتاح الأصلي المحفوظ دون تغييره عند الإعادة
        return try {
            val response = paymentApi.charge(
                idempotencyKey = record.idempotencyKey,
                body = ChargeRequest(record.orderId, record.amount)
            )
            paymentDao.markApproved(record.id, response.authCode)
            PaymentResult.Success(response.authCode)
        } catch (e: IOException) {
            // انقطاع الاتصال: نحافظ على نفس المفتاح للاستعلام أو إعادة الإرسال
            paymentDao.markInDoubt(record.id)
            PaymentResult.InDoubt(record.idempotencyKey)
        }
    }
}
```""",
        "why_it_matters_ar": "غياب حتمية التكرار هو السبب التقني المباشر لخصم المبالغ مرتين أو ثلاث مرات من العميل عند بطء شبكة الهاتف، مما يدمر سمعة التطبيق المالي فوراً.",
        "worked_example_ar": "أرسل تطبيق الدفع طلب خصم 500 جنيه؛ قام الخادم بالخصم ولكن انقطع برج الاتصال قبل إرسال الرد؛ أعاد التطبيق إرسال نفس الطلب بنفس المفتاح، فأرجع الخادم الرد المخزن فوراً دون خصم مليم إضافي.",
        "trade_offs_ar": "تتطلب حتمية التكرار تخزين المفاتيح محلياً وفحصها في ذاكرة موزعة كـ Redis في الخادم، مما يضيف تعقيداً هندسياً طفيفاً لكنه يوفر حماية مطلقة ضد الخصم المزدوج.",
        "failure_modes_ar": "أفدح الأخطاء هو توليد مفتاح حتمية جديد داخل حلقة إعادة المحاولة (Retry Loop)؛ فهذا يدمر مبدأ الحتمية تماماً ويجبر الخادم على معاملتها كعمليات جديدة متعددة.",
        "production_perspective_ar": "في كود الإنتاج، يُربط مفتاح الحتمية برقم الطلب الأساسي عبر قيد فريد (Unique Constraint) في قاعدة بيانات الهاتف؛ لضمان استحالة إنشاء مفتاحين لنفس الفاتورة مهما تكرر النقر.",
        "how_to_answer_ar": "عرّف المفهوم رياضياً ومعمارياً، واشرح سيناريو فقدان حزمة التأكيد عبر الشبكة، ثم وضح دور مفتاح الحتمية وكيفية حفظه محلياً وإرساله في ترويسات الطلب.",
        "talking_points_ar": "حتمية التكرار Idempotency، المعادلة الرياضية، مفتاح الحتمية Idempotency Key، سيناريو فقدان حزمة الرد ACK، التخزين المحلي الدائم، وقفل الخادم الموزع.",
        "follow_ups_ar": "ماذا يحدث لو أرسل العميل طلبين متطابقين بنفس المفتاح في نفس الجزء من الثانية؟ وكيف يتعامل الخادم مع التزامن عبر Distributed Locks؟",
        "self_check_ar": "هل وضحت الفارق بين توليد المفتاح محلياً وتمريره للخادم، وأكدت على عدم تغيير المفتاح أثناء المحاولات المتكررة؟",
        "references_ar": f"- [Stripe API Documentation: Idempotent Requests](https://docs.stripe.com/api/idempotent_requests) — التوثيق المرجعي الأكثر شهرة في صناعة التكنولوجيا المالية لتطبيق مفاتيح الحتمية.\n- [IETF RFC 9651: The Idempotency-Key HTTP Header Field](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/) — المسودة القياسية لهيئة معايير الإنترنت لترويسة حتمية التكرار في بروتوكول HTTP.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """حتمية التكرار تضمن أن تنفيذ المعاملة عدة مرات ينتج عنه نفس الأثر تماماً كأنها نُفذت لمرة واحدة. في الأنظمة المالية، يولد التطبيق مفتاح حتمية فريد ويحفظه محلياً في قاعدة البيانات ويرسله مع الطلب؛ فعند انقطاع الشبكة وإعادة المحاولة يتعرف الخادم على المفتاح ويرجع الرد الأصلي مباشرة دون سحب المبلغ مرة أخرى.""",
        "best_answer_ar": """تعتبر حتمية التكرار الركيزة المعمارية الجوهرية لمنع السحب المزدوج في المعاملات المالية عبر شبكات الهاتف المتقلبة.
تعني الحتمية رياضياً أن تكرار العملية لا يغير من النتيجة النهائية شيئاً. وتظهر أهميتها الحتمية عندما يخصم خادم البنك المبلغ من حساب العميل، ولكن ينقطع الاتصال اللاسلكي قبل وصول الرد للهاتف؛ فتقوم طبقة الشبكة أو المستخدم بإعادة إرسال الطلب.
إذا لم تكن الخدمة حتمية، سيعتبر الخادم كل إعادة محاولة عملية شراء جديدة ويخصم الرصيد مراراً.
ولتفادي هذه الكارثة، يولد تطبيق الهاتف مفتاح حتمية فريد لكل فاتورة ويحفظه بشكل دائم في قاعدة البيانات المحلية قبل إرسال أول بايت عبر الشبكة. ويُرسل هذا المفتاح في ترويسات الطلب؛ حيث يفحص معالج الدفع المفتاح في ذاكرة مؤقتة موزعة، وإذا وجد أن العملية قد تمت بالفعل، يعيد إرسال الرد السابق المخزن دون إجراء أي سحب بنكي جديد، مع الحظر الصارم لتغيير المفتاح أثناء المحاولات المتكررة.""",
        "deep_answer_ar": """من منظور النظم الموزعة ونظريات الاتصال، تمثل حتمية التكرار الجسر الهندسي الوحيد لتحويل التوصيل الشبكي المتكرر إلى تنفيذ محاسبي مفرد ودقيق.
وفقاً لنظرية كاب وتحديات الاتصال اللاسلكي، يستحيل فيزيائياً ضمان توصيل الحزمة لمرة واحدة فقط؛ فالشبكات تقدم إما تسليماً على الأكثر أو تسليماً على الأقل. والأنظمة المالية تلتزم بسياسة إعادة المحاولة لضمان عدم ضياع أي معاملة تجارية. ولكن دمج إعادة المحاولة مع واجهات برمجية تفتقر للحتمية يقود حتماً إلى فوضى الاقتطاع المزدوج.
لذلك تلزم المعمارية المنضبطة بتوليد مفتاح الحتمية كمعرّف دائم مرتبط بالفاتورة في جدول محلي داخل الهاتف بقيد فريد يمنع إنشاء مفاتيح جديدة للطلب ذاته.
وعند إرسال الطلب للواجهة الخلفية، يتم قفل المفتاح عبر آليات التزامن الموزع لمنع أي تداخل إذا أُرسلت طلبات متزامنة في نفس اللحظة. فإذا نجح الطلب الأول، تُخزن استجابة التفويض في سجلات الخادم. وعندما يعيد الهاتف إرسال نفس الطلب بعد مهلة اتصال، يكتشف الخادم وجود المفتاح مسبقاً، متجاوزاً شبكة البطاقات المصرفية بالكامل ليعيد نفس الرد المشفر السابق. هذا التناغم بين التخزين المحلي المتين ومعالجة الخادم يضمن دقة الحسابات المالية تحت أقسى ظروف انقطاع الشبكة، وتجنب فرض أي رسوم تسوية إضافية على التاجر أو إثارة قلق العملاء من الخصومات المتكررة غير المبررة."""
    }
}

# ==========================================
# PAY-03: What are authorization, reversal, void, refund, and reconciliation?
# ==========================================
DATA["PAY-03"] = {
    "concept_en": """The card payment lifecycle consists of distinct financial, cryptographic, and accounting operations governing how funds move between cardholders, merchants, and acquiring banks:
- 1. Authorization:
  - Definition: The cardholder's issuing bank verifies credentials (CVV, 3D Secure, PIN) and places an administrative hold (pre-authorization) on the requested amount.
  - Financial Impact: Funds are reserved in the cardholder's credit limit, but no actual money transfers between bank accounts yet.
- 2. Reversal (Auto-Reversal):
  - Definition: Immediate cancellation of an in-flight or in-doubt authorization (ISO 8583 0400/0420 transaction).
  - Condition: Executed when a terminal crashes, times out, or detects a local printing/hardware failure right after transmitting authorization.
  - Financial Impact: Releases the hold immediately. Zero merchant fees incurred because clearing never began.
- 3. Void:
  - Definition: Cancellation of an approved transaction on the same calendar day *before* the merchant's end-of-day batch settlement cut-off.
  - Condition: Customer immediately cancels purchase at the checkout counter before the register closes.
  - Financial Impact: Erases the transaction from the pending batch. Funds hold drops off within hours; no interchange fees charged.
- 4. Refund:
  - Definition: Transfer of money back to the cardholder *after* batch settlement and funds clearance have completed.
  - Condition: Customer returns physical merchandise days after the original purchase.
  - Financial Impact: Requires a separate financial settlement cycle (3-5 business days) and incurs non-refundable merchant interchange processing fees.
- 5. Reconciliation (Settlement Balancing):
  - Definition: The end-of-day accounting audit (Z-Report) comparing the mobile/POS terminal's local durable transaction journal against the acquirer/switch ledger.
  - Outcome: Detects missing transactions, out-of-balance batches, or orphaned authorizations, ensuring complete ledger parity.""",
    "walkthrough_en": """State mapping and lifecycle semantics in Kotlin domain models:
```kotlin
enum class FinancialOperationType {
    AUTHORIZE,  // Reserves funds (Hold on cardholder account)
    REVERSAL,   // Immediate release of in-doubt hold prior to batch close
    VOID,       // Cancellation of approved charge before end-of-day settlement
    REFUND,     // Credit transfer back to cardholder post-settlement
    RECONCILE   // Batch matching local terminal records vs bank switch
}

data class TransactionRecord(
    val transactionId: String,
    val rrn: String?,          // Retrieval Reference Number
    val authCode: String?,
    val amountCents: Long,
    val state: OperationState,
    val settledAtBatchId: String? // Null if unsettled (eligible for Void)
) {
    val canBeVoided: Boolean
        get() = settledAtBatchId == null && state == OperationState.APPROVED

    val requiresRefund: Boolean
        get() = settledAtBatchId != null && state == OperationState.APPROVED
}
```""",
    "short_en": """Authorization places a hold on cardholder funds without moving money. Reversal cancels an in-doubt authorization immediately due to terminal errors with zero fees. Void cancels an approved transaction before daily batch settlement. Refund returns settled money days later incurring processing fees. Reconciliation audits local terminal journals against bank switch ledgers to resolve financial discrepancies.""",
    "structured_en": """The card payment lifecycle consists of five distinct accounting and settlement operations.
Authorization verifies card validity and places a temporary hold on the customer's funds. Money does not change hands until final capture.
Reversal is an automated emergency operation executed immediately when a terminal experiences a communication timeout or crash while awaiting authorization. It signals the bank to cancel the hold right away, incurring zero merchant fees.
Void cancels an approved transaction within the same business day before the merchant closes and settles the daily batch. The transaction is removed from the settlement file, sparing both parties processing fees.
Refund occurs after batch settlement has finalized and money has moved to the merchant's bank account. Returning funds requires a new transaction that takes several days to clear and incurs processing fees.
Reconciliation is the end-of-day balancing process where the terminal transmits its local transaction journal to the bank switch to detect and reconcile any missing or mismatched records.""",
    "deep_senior_en": """From a payment operations and financial settlement architecture standpoint, distinguishing between these five operations is vital for ledger integrity and merchant fee minimization.
Authorization is purely an administrative hold on the cardholder\'s credit limit. Under EMV and ISO 8583 standards, an authorization code confirms that funds exist and are locked, but actual interbank clearing occurs during nightly batch processing.
The critical distinction between Reversal and Void lies in timing and certainty. A Reversal is an automated, real-time message dispatched when the terminal detects an ambiguous failure, such as a printer paper jam or a socket disconnect after sending an authorization request. Reversals release held funds instantaneously and protect the merchant from chargebacks. A Void, conversely, is an intentional business action taken when a customer returns goods before batch cut-off. Because the transaction has not settled, voiding erases the transaction without interchange fees.
Refunds, on the other hand, occur post-settlement. Once the merchant\'s daily batch is submitted and funds are wired through the clearing house, the original transaction cannot be voided. A refund must be initiated as a separate credit transaction, which takes three to five business days and permanently forfeits merchant processing fees.
Finally, Reconciliation is the audit mechanism that guarantees ledger truth. Every certified POS terminal maintains a local tamper-evident journal. At end-of-day, the terminal executes a settlement handshake, transmitting transaction counts and sums. If discrepancies appear, automated exception reports trigger dispute workflows, ensuring full accounting alignment across banks and merchants.""",
    "meta_ar": {
        "id": "PAY-03",
        "questionAr": "ما هي الفروق الدقيقة بين التفويض (Authorization)، والعكس (Reversal)، والإلغاء (Void)، والاسترداد (Refund)، والمطابقة (Reconciliation)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دورة حياة المعاملة المالية في شبكات الدفع (EMV/ISO 8583)، التمييز المحاسبي بين العمليات الخمس، توقيت حركة الأموال وتكلفة الرسوم، وأهمية المطابقة اليومية (End-of-day Reconciliation).",
        "concept_ar": "تتكون دورة حياة الدفع بالبطاقات من خمس عمليات مصرفية ومحاسبية مميزة تحكم حركة الأموال بين العميل والتاجر والبنك: أولاً التفويض (Authorization) وهو حجز إداري للمبلغ من رصيد العميل دون تحويل فعلي للأموال للتاجر بانتظار التسوية؛ ثانياً العكس (Reversal) وهو إلغاء فوري لعملية تفويض معلقة بسبب عطل في نقطة البيع أو انقطاع الاتصال (رسالة ISO 8583 0400)، مما يحرر الحجز لحظياً دون أي رسوم معالجة؛ ثالثاً الإلغاء (Void) وهو إلغاء معاملة مقبولة في نفس اليوم وقبل إغلاق الدفتر اليومي (Batch Settlement)؛ رابعاً الاسترداد (Refund) وهو إعادة أموال دخلت بالفعل حساب التاجر بعد تسوية الدفعة البنكية وتستغرق عدة أيام وتتحمل رسوم معالجة غير مستردة؛ خامساً المطابقة (Reconciliation) وهي مطابقة الدفاتر اليومية (Z-Report) بين سجلات نقطة البيع المخزنة محلياً ودفاتر البنك لاكتشاف أي فروقات مالية وحلها.",
        "walkthrough_ar": """نموذج كوتلن يوضح منطق العمليات المالية وحالة تسوية الدفعة:
```kotlin
enum class FinancialOperationType {
    AUTHORIZE,  // حجز رصيد العميل دون تحويل مالي فعلي
    REVERSAL,   // إلغاء فوري للحجز عند فشل الاتصال دون رسوم
    VOID,       // إلغاء العملية قبل تسوية الدفعة اليومية
    REFUND,     // رد الأموال للعميل بعد اكتمال التسوية والتحويل
    RECONCILE   // مطابقة السجلات المحلية مع سجلات البنك
}

data class TransactionRecord(
    val transactionId: String,
    val rrn: String?,          // رقم مرجع الاسترجاع
    val authCode: String?,
    val amountCents: Long,
    val state: OperationState,
    val settledAtBatchId: String? // فارغ إذا لم تتم التسوية بعد
) {
    // يمكن الإلغاء المجاني إذا لم تُقفل الدفعة اليومية بعد
    val canBeVoided: Boolean
        get() = settledAtBatchId == null && state == OperationState.APPROVED

    // يتطلب استرداداً بنكياً بعد إقفال الدفعة وتحويل الأموال
    val requiresRefund: Boolean
        get() = settledAtBatchId != null && state == OperationState.APPROVED
}
```""",
        "why_it_matters_ar": "الخلط بين هذه العمليات يكلف التاجر رسوماً بنكية باهظة ويعطل أموال العملاء لأيام في شكاوى الاسترداد ويسبب عجزاً في ميزانية نقاط البيع.",
        "worked_example_ar": "طلب عميل إلغاء شراء هاتف بعد 5 دقائق؛ قام الكاشير بعمل Void فأُلغيت العملية فوراً دون رسوم؛ بينما لو انتظر لليوم التالي لطلب Refund ودفع التاجر 2.5% عمولة بنكية وانتظر العميل 4 أيام.",
        "trade_offs_ar": "إجراء Reversal وVoid يوفر الرسوم ويحرر الرصيد فوراً لكنه محكوم بنافذة زمنية قبل إغلاق الدفعة؛ بينما Refund متاح دائماً لكنه مكلف وبطيء.",
        "failure_modes_ar": "أخطر الأخطاء هو تنفيذ Refund لمعاملة لم تُسجل في الدفعة بعد بدلاً من عمل Void، مما يكلف التاجر رسوم معالجة غير مستردة وقد يتسبب في قيد المبلغ كحركة عكسية خاطئة.",
        "production_perspective_ar": "في أنظمة نقاط البيع POS، يُمنع إغلاق وردية الكاشير إلا بعد تنفيذ أمر المطابقة Reconciliation وتطابق إجمالي المبالغ في الجهاز مع خادم البنك بنسبة 100%.",
        "how_to_answer_ar": "اشرح العمليات الخمس بتسلسل منطقي: التفويض أولاً، ثم العكس للطوارئ، ثم الإلغاء قبل التسوية، ثم الاسترداد بعد التسوية، واختم بالمطابقة المحاسبية اليومية.",
        "talking_points_ar": "التفويض Authorization، العكس الفوري Reversal، الإلغاء Void قبل التسوية، الاسترداد Refund بعد التسوية، ورقة التسوية اليومية Z-Report والمطابقة Reconciliation.",
        "follow_ups_ar": "ما الفارق الزمني والتقني بين تسوية الدفعة Batch Settlement والمقاصة البنكية Clearing؟ وكيف تعالج العمليات المعلقة أثناء المطابقة؟",
        "self_check_ar": "هل فرقت بوضوح بين Reversal وVoid وRefund من حيث الرسوم والوقت وحركة الأموال، ووضحت دور عملية المطابقة؟",
        "references_ar": f"- [PCI Security Standards Council: Glossary of Terms](https://www.pcisecuritystandards.org/) — القاموس المرجعي المعتمد لمصطلحات أمن ومدفوعات البطاقات المصرفية.\n- [Mastercard Processing Standards: Authorization and Clearing](https://www.mastercard.us/en-us/business/overview.html) — المعايير الدولية لشبكة ماستركارد لعمليات التفويض والمقاصة والتسوية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """التفويض هو حجز مؤقت لرصيد العميل دون تحويل مالي؛ والعكس هو إلغاء فوري للتفويض بسبب عطل فني لتحرير الرصيد دون رسوم؛ والإلغاء Void هو شطب المعاملة قبل تسوية الدفعة اليومية مجاناً؛ بينما الاسترداد Refund هو إعادة الأموال بعد تحويلها ويستغرق أياماً مع خصم رسوم؛ والمطابقة هي جرد يومي يطابق سجلات الجهاز مع دفاتر البنك.""",
        "best_answer_ar": """تتكامل العمليات المالية الخمس لتنظيم حركة الأموال ومطابقة القيود المحاسبية في أنظمة المدفوعات ونقاط البيع.
يبدأ المسار بعملية التفويض Authorization للتحقق من البطاقة وحجز المبلغ المطلوب من رصيد العميل، دون أن تنتقل الأموال فعلياً لحساب التاجر في تلك اللحظة.
أما العكس Reversal فهو إجراء طوارئ تلقائي يُنفذ فوراً عند انقطاع الاتصال أو تعطل الطابعة بعد إرسال التفويض، لإلغاء الحجز البنكي وتحرير الرصيد بلحظات دون تكلفة.
ويأتي الإلغاء Void كإجراء يطلبه التاجر أو العميل في نفس يوم المعاملة وقبل إغلاق الدفعة اليومية؛ حيث تُحذف المعاملة من سجل التسوية دون خصم رسوم بنكية.
وعلى النقيض، فإن الاسترداد Refund يتم بعد ترحيل الدفعة البنكية وانتقال الأموال؛ مما يتطلب معاملة تحويل عكسية تستغرق عدة أيام عمل مع خسارة رسوم المعالجة.
وأخيراً، تمثل المطابقة Reconciliation عملية الجرد الختامية لليوم، حيث يرسل الجهاز سجلاته المحلية لمطابقتها مع خادم البنك لتسوية أي فروقات رقمية بدقة مطلقة.""",
        "deep_answer_ar": """من منظور معايير التحويل المصرفي ISO 8583 وهندسة التسويات المالية، يشكل التمييز بين هذه العمليات جوهر السلامة المحاسبية وإدارة تكلفة العمليات للتجار.
التفويض في جوهره ليس حركة أموال بل حجز ائتماني يضمن وجود الرصيد وتجميده حتى يحين موعد المقاصة الليلية.
ويبرز الفارق الجوهري بين العكس والإلغاء في مستوى الحتمية والتوقيت؛ فالعكس Reversal هو استجابة فورية لأعطال النظام اللاسلكي أو البرمجي، حيث تُبث رسالة ISO 8583 0400 لإلغاء الحجز فوراً وتجنيب التاجر مخاطر النزاعات البنكية. أما الإلغاء Void فهو قرار تجاري واعٍ بإلغاء المعاملة المقبولة قبل إرسال ملف التسوية اليومي، مما يعفي التاجر من رسوم التبادل البنكي.
بالمقابل، لا يمكن استخدام الإلغاء بعد تسوية الدفعة وإرسال الأموال للحساب الجاري، بل يتحتم فتح مسار استرداد Refund كامل، والذي يخضع لدورة مصرفية تستغرق من ثلاثة إلى خمسة أيام عمل مع تحمل التاجر لرسوم المعالجة الأصلية غير المستردة.
وتتوج هذه المنظومة بعملية المطابقة Reconciliation؛ حيث يحتفظ الجهاز بدفتر محلي مشفر ومقاوم للتلاعب، وفي نهاية الوردية يُجري الجهاز مصافحة تسوية شاملة لمقارنة أعداد المبالغ وحصيلة العمليات مع المقسم المصرفي. وأي تفاوت يؤدي لإصدار تقرير تسوية استثنائي يوجه التدقيق المحاسبي لمعالجة القيود العالقة وحفظ التوازن المالي لكافة الأطراف."""
    }
}

# ==========================================
# PAY-04: What risks arise when a local payment record is not durably committed?
# ==========================================
DATA["PAY-04"] = {
    "concept_en": """Failing to durably commit a local payment record before transmitting network authorization introduces catastrophic financial, operational, and reconciliation anomalies:
- The Volatile Memory (RAM) Vulnerability:
  - If payment state exists only in ViewModel memory or volatile memory structures, sudden OS process termination (Low Memory Killer), unexpected battery detachment on POS hardware, or kernel panics erase the entire transaction context.
- The Phantom Transaction Disaster:
  - Sequence of Events:
    1. Client collects card details and sends HTTP authorization without writing to disk.
    2. Bank switch approves transaction and debits cardholder account.
    3. Terminal battery drops or app crashes while awaiting response.
  - Consequence:
    - Customer receives an SMS notification confirming funds deducted.
    - Cashier screen reboots with no record; cashier refuses to hand over the purchased goods.
    - Customer files an immediate fraud chargeback, incurring dispute fees and regulatory penalties.
- End-of-Day Reconciliation Ledger Black Hole:
  - During nightly settlement, the bank settlement report lists the captured charge, but the terminal\'s local electronic journal has zero record.
  - The merchant cannot match inventory to sales, creating untraceable accounting discrepancies and severe tax audit violations.
- Mitigation via Write-Ahead Logging (WAL):
  - Every payment intent must be persisted inside an atomic SQLite/Room transaction using Write-Ahead Logging with full disk sync (`PRAGMA synchronous = FULL` or `NORMAL`) before initiating any network socket connection.""",
    "walkthrough_en": """Enforcing durable write-ahead transaction recording before network dispatch in Kotlin:
```kotlin
@Entity(tableName = "payment_journal")
data class PaymentJournalEntity(
    @PrimaryKey val transactionId: String,
    val correlationId: String,
    val amountCents: Long,
    val currency: String,
    val status: String, // INITIATED, APPROVED, DECLINED, UNKNOWN
    val createdAtEpoch: Long
)

class DurablePaymentCoordinator(
    private val database: AppDatabase,
    private val journalDao: PaymentJournalDao,
    private val paymentGateway: PaymentGatewayApi
) {
    suspend fun processPayment(amount: Long, currency: String): PaymentOutcome {
        val txId = UUID.randomUUID().toString()
        val correlationId = "CORR-${System.currentTimeMillis()}-${txId.take(8)}"

        // Critical Invariant: Must durably commit to SQLite disk BEFORE opening network socket
        database.withTransaction {
            journalDao.insert(
                PaymentJournalEntity(
                    transactionId = txId,
                    correlationId = correlationId,
                    amountCents = amount,
                    currency = currency,
                    status = "INITIATED",
                    createdAtEpoch = System.currentTimeMillis()
                )
            )
        }

        return try {
            val response = paymentGateway.authorize(txId, correlationId, amount)
            database.withTransaction {
                journalDao.updateStatus(txId, "APPROVED")
            }
            PaymentOutcome.Success(response.authCode)
        } catch (e: Exception) {
            database.withTransaction {
                journalDao.updateStatus(txId, "UNKNOWN")
            }
            PaymentOutcome.InDoubt(txId)
        }
    }
}
```""",
    "short_en": """Failing to durably commit a payment record to disk before network dispatch creates phantom transactions if the app crashes or the battery detaches mid-flight. The customer is charged by the bank, but the terminal retains no record, forcing the merchant to deny merchandise and triggering severe chargebacks, tax audit failures, and reconciliation imbalances.""",
    "structured_en": """Neglecting durable local persistence prior to network authorization exposes payment systems to severe financial and regulatory risks.
If an application maintains transaction state solely in volatile memory like ViewModels or memory caches, any sudden process kill, system crash, or physical battery removal completely wipes the transaction record.
This creates a phantom transaction: the payment gateway and card issuer debit the customer\'s account, but the mobile device reboots with no trace of the transaction. The merchant refuses to release the merchandise because the screen shows nothing, prompting the enraged customer to initiate a dispute. The merchant loses the funds, pays hefty chargeback penalties, and faces card network sanctions.
Furthermore, during nightly reconciliation, the bank\'s settlement file lists a captured transaction that is missing from the merchant\'s local ledger, breaking accounting parity and complicating audits.
To eliminate this vulnerability, payment systems mandate Write-Ahead Logging in SQLite Room, guaranteeing that transaction intent is flushed to physical storage before any network request begins.""",
    "deep_senior_en": """From an embedded POS hardware engineering and financial compliance standpoint, the non-durable state vulnerability represents an unacceptable architectural flaw that violates fundamental accounting principles.
On mobile Android devices, background processes are subject to aggressive termination by the Low Memory Killer daemon. Handheld POS terminals face additional real-world hazards, such as accidental drops that dislodge the battery pack or sudden power cutoffs when placed on faulty charging cradles. If transaction tracking relies on in-memory coroutine scopes, these events destroy all state.
The resulting customer experience is disastrous. The cardholder receives a push notification confirming that fifty dollars were deducted. However, the cashier\'s POS terminal reboots to an empty home screen. The customer insists they paid; the cashier sees zero evidence and refuses to hand over the items. When the customer files a chargeback, the merchant lacks an electronic transaction journal or Retrieval Reference Number to contest the claim, resulting in an automatic loss of funds plus administrative fines.
From an accounting and taxation perspective, missing transaction records invalidate the electronic journal, leading to regulatory penalties under financial auditing laws.
The architectural remediation requires strict adherence to Write-Ahead Logging protocols. Before the EMV kernel or networking layer formats an ISO 8583 authorization message, the software must execute an atomic database transaction in Room. This record stores the unique transaction ID, correlation ID, timestamp, and amount. If the hardware loses power mid-request, the recovery routine executed on the next boot inspects the journal, discovers the stranded transaction in the Initiated state, and immediately triggers an automated status inquiry or reversal, preserving financial integrity.""",
    "meta_ar": {
        "id": "PAY-04",
        "questionAr": "ما هي المخاطر الكارثية المترتبة على عدم تثبيت سجل المعاملة المالية محلياً بشكل دائم قبل إرسالها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "مخاطر الاحتفاظ بالمعاملة في الذاكرة العشوائية (RAM)، ظاهرة المعاملات الشبحية (Phantom Transactions)، إغلاق النظام وموت البطارية المفاجئ، فشل المطابقة المحاسبية، وتطبيق نمط الكتابة المسبقة (WAL).",
        "concept_ar": "يؤدي إرسال طلب التفويض المالي عبر الشبكة قبل تثبيت بيانات المعاملة بشكل دائم على القرص إلى مخاطر تشغيلية ومحاسبية جسيمة: إذا كانت المعاملة مخزنة في الذاكرة العشوائية (RAM) أو داخل ViewModel فقط، فإن أي إغلاق مفاجئ للتطبيق بواسطة نظام أندرويد لتوفير الذاكرة، أو سقوط الهاتف وفصل البطارية، أو إعادة تشغيل الجهاز يؤدي إلى محو أثر المعاملة بالكامل. وينتج عن ذلك ظاهرة المعاملة الشبحية (Phantom Transaction)؛ حيث يقوم خادم البنك بخصم المبلغ من حساب العميل وإرسال رسالة نصية له، بينما يُعاد تشغيل جهاز التاجر دون أي أثر للعملية فيرفض تسليم البضاعة. يترتب على ذلك تقديم العميل لشكوى نزاع مصرفي (Chargeback) وفرض غرامات باهظة على التاجر. كما تتسبب هذه الفجوة في عجز محاسبي كارثي أثناء المطابقة اليومية لعدم تطابق دفاتر التاجر مع كشوفات البنك. والحل المعماري الإلزامي هو استخدام تقنية الكتابة المسبقة (Write-Ahead Logging) في قاعدة بيانات Room وتثبيت بيانات المعاملة وحالتها كـ Initiated في القرص الصلب قبل فتح الاتصال الشبكي.",
        "walkthrough_ar": """تثبيت سجل المعاملة محلياً في قاعدة البيانات قبل فتح الاتصال الشبكي في كوتلن:
```kotlin
@Entity(tableName = "payment_journal")
data class PaymentJournalEntity(
    @PrimaryKey val transactionId: String,
    val correlationId: String,
    val amountCents: Long,
    val currency: String,
    val status: String, // INITIATED, APPROVED, DECLINED, UNKNOWN
    val createdAtEpoch: Long
)

class DurablePaymentCoordinator(
    private val database: AppDatabase,
    private val journalDao: PaymentJournalDao,
    private val paymentGateway: PaymentGatewayApi
) {
    suspend fun processPayment(amount: Long, currency: String): PaymentOutcome {
        val txId = UUID.randomUUID().toString()
        val correlationId = "CORR-${System.currentTimeMillis()}-${txId.take(8)}"

        // قاعدة ذهبية: الحفظ الدائم على القرص أولاً قبل لمس الشبكة
        database.withTransaction {
            journalDao.insert(
                PaymentJournalEntity(
                    transactionId = txId,
                    correlationId = correlationId,
                    amountCents = amount,
                    currency = currency,
                    status = "INITIATED",
                    createdAtEpoch = System.currentTimeMillis()
                )
            )
        }

        return try {
            val response = paymentGateway.authorize(txId, correlationId, amount)
            database.withTransaction {
                journalDao.updateStatus(txId, "APPROVED")
            }
            PaymentOutcome.Success(response.authCode)
        } catch (e: Exception) {
            database.withTransaction {
                journalDao.updateStatus(txId, "UNKNOWN")
            }
            PaymentOutcome.InDoubt(txId)
        }
    }
}
```""",
        "why_it_matters_ar": "فقدان سجل المعاملة محلياً أثناء خصمها بنكياً يؤدي لمواجهات عنيفة بين الكاشير والعميل ونزاعات مصرفية وتشويه السجل الضريبي للتاجر.",
        "worked_example_ar": "سقط جهاز نقطة البيع وفُصلت البطارية بعد خصم 1000 جنيه من بطاقة العميل؛ ولأن الكود حفظ المعاملة محلياً بنمط WAL، بمجرد تشغيل الجهاز أظهر العملية كـ Unknown واستعلم عن البنك وطبع الإيصال فوراً.",
        "trade_offs_ar": "الكتابة المتزامنة على القرص تزيد زمن المعالجة بضع أجزاء من الثانية؛ لكنها صمام الأمان الوحيد لمنع الكوارث المالية وضياع حقوق التاجر والعميل.",
        "failure_modes_ar": "أخطر الأخطاء هو حفظ المعاملة في SharedPreferences أو المتغيرات الحية دون Flush على القرص، مما يجعلها عرضة للتبخر التام عند موت العملية المفاجئ.",
        "production_perspective_ar": "في أجهزة نقاط البيع المعتمدة، تخضع التطبيقات لاختبار سحب البطارية (Battery Pull Test) أثناء إرسال الحزم؛ ويُرسب الاعتماد فوراً إذا فقد الجهاز سجل المعاملة.",
        "how_to_answer_ar": "ابدأ ببيان كارثة الاعتماد على الذاكرة العشوائية RAM، ثم فصّل سيناريو المعاملة الشبحية وأثرها على العميل والتاجر، واختم بالحل المعماري عبر قاعدة بيانات دائمة بنمط WAL.",
        "talking_points_ar": "الذاكرة العشوائية المتطايرة، المعاملات الشبحية Phantom Transactions، اختبار سحب البطارية Battery Pull، نمط الكتابة المسبقة WAL، ونزاعات البطاقات Chargebacks.",
        "follow_ups_ar": "كيف يضمن تفعيل PRAGMA synchronous = FULL في SQLite أمان البيانات ضد انقطاع الطاقة المفاجئ؟ وما الفرق بينه وبين الوضع الافتراضي؟",
        "self_check_ar": "هل شرحت سيناريو المعاملة الشبحية، وأثرها على المطابقة المحاسبية، وأكدت على الحفظ الدائم قبل فتح الاتصال؟",
        "references_ar": f"- [SQLite Documentation: Write-Ahead Logging](https://www.sqlite.org/wal.html) — التوثيق الرسمي لنمط الكتابة المسبقة وأهميته في ضمان الحفظ الدائم وتفادي تلف البيانات.\n- [Visa Core Rules and Visa Product and Service Rules](https://usa.visa.com/support/consumer/visa-rules.html) — القواعد الصارمة لشبكة فيزا العالمية بشأن النزاعات المصرفية وسجلات المعاملات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """عدم تثبيت سجل المعاملة محلياً على القرص قبل إرسالها يتسبب في كارثة المعاملات الشبحية إذا سقط التطبيق أو فُصلت البطارية؛ حيث يُخصم المبلغ من حساب العميل بينما يُعاد تشغيل الجهاز دون أي سجل للمعاملة، مما يجبر التاجر على حجب البضاعة ويتسبب في نزاعات مصرفية وعجز محاسبي في المطابقة.""",
        "best_answer_ar": """يعد إهمال التثبيت الدائم لسجل المعاملة قبل الاتصال بالشبكة من أخطر العيوب المعمارية في تطبيقات الدفع ونقاط البيع.
إذا تم الاحتفاظ بالمعاملة في الذاكرة العشوائية المؤقتة فقط، فإن أي إغلاق مفاجئ بواسطة النظام لتوفير الذاكرة، أو نفاد البطارية أثناء انتظار رد البنك، يمحو بيانات المعاملة تماماً من الجهاز.
ينتج عن ذلك ظاهرة المعاملة الشبحية؛ حيث يخصم البنك المبلغ من حساب العميل وتصله رسالة التأكيد، بينما يستيقظ جهاز نقطة البيع دون أي أثر للمعاملة. يرفض التاجر تسليم المشتريات لعدم وجود إيصال، فيقوم العميل بتقديم شكوى نزاع مصرفي ونكول في الدفع؛ مما يغرم التاجر رسوماً إضافية.
وعلاوة على ذلك، تفشل المطابقة المحاسبية في نهاية اليوم لوجود عملية مقبولة في البنك ومفقودة في دفاتر التاجر.
ولمنع هذه الكوارث، تفرض المعايير المالية استخدام الكتابة المسبقة في قواعد بيانات متينة مثل Room، مع حفظ نية المعاملة على القرص الصلب وتأكيد كتابتها قبل فتح أي اتصال شبكي.""",
        "deep_answer_ar": """من منظور هندسة أجهزة نقاط البيع المدمجة والامتثال المالي المصرفي، يمثل غياب التخزين الدائم خرقاً صريحاً لمبادئ المحاسبة وسلامة النظم المالية.
في بيئة أجهزة أندرويد المحمولة، تواجه التطبيقات مخاطر دائمة مثل إيقاف العمليات القسري بواسطة نظام الذاكرة، أو السقوط الفيزيائي للجهاز الذي يفصل البطارية لحظياً عن الدوائر الكهربائية. فإذا كانت المعاملة تعتمد على كائنات الذاكرة المؤقتة، تتلاشى كافة بيانات العملية في جزء من الثانية.
هذا الانهيار يخلق أزمة ثقة وتكلفة مالية مضاعفة؛ فالعميل يثبت خصم الأموال من رصيده عبر هاتفه، بينما يقف البائع عاجزاً عن التحقق أو طباعة الإيصال المحاسبي لغياب رقم مرجع الاسترجاع RRN. وعند تصعيد الشكوى كنزاع مصرفي Chargeback، يعجز التاجر عن تقديم الدليل الإلكتروني، فيخسر قيمة المبيعات بالإضافة لتحمل غرامات النزاع المفروضة من شبكات الدفع العالمية كفيزا وماستركارد.
كما يتسبب غياب السجل المحلي في تدمير عملية المطابقة اليومية Reconciliation، حيث تظهر مبالغ مجهولة في كشف البنك لا تقابلها فواتير في السجل الضريبي للتاجر، مما يعرضه لمخالفات قانونية.
ولذلك تعتمد الأنظمة الاحترافية مبدأ الدفتر المتين المقاوم للأعطال؛ فبمجرد قراءة البطاقة، تُنفذ المعمارية حركة كتابة ذرية في SQLite بنمط WAL لحفظ المعاملة بحالة Initiated مع تفاصيل المبلغ ومفاتيح التتبع. وعند إعادة تشغيل الجهاز بعد أي انقطاع مفاجئ، تفحص دالة الإقلاع الدفتر المحلي، لتستأنف التعامل مع المعاملات المعلقة بالاستعلام أو العكس الفوري، محققة التوازن المحاسبي الكامل."""
    }
}

# ==========================================
# PAY-05: What is a transaction correlation ID, and why is it needed?
# ==========================================
DATA["PAY-05"] = {
    "concept_en": """A transaction correlation ID is an immutable, globally unique trace identifier assigned at the moment of transaction inception that propagates across all distributed financial hops:
- Distributed Financial Topology:
  - A modern payment flows through multiple disparate systems:
    `Android POS Terminal -> Payment Gateway API -> Risk/Fraud Engine -> Acquirer Switch -> Card Network (Visa/Mastercard) -> Issuer Core Banking System`.
  - Without a shared correlation token, linking a client-side network timeout to a specific backend database record is nearly impossible.
- Technical Anatomy:
  - Typically generated as a cryptographically random UUIDv4 or a composite structured key (e.g., `POS-${terminalId}-${sequenceNumber}-${epochMs}`).
  - Propagated downstream via HTTP headers (e.g., `X-Correlation-ID: 7f3b89a1-...`), gRPC metadata, and ISO 8583 message elements (Field 37 - Retrieval Reference Number / RRN, and Field 11 - Systems Trace Audit Number / STAN).
- Distinguishing Correlation ID from Idempotency Key:
  - `Idempotency Key`: Dictates business behavior. Ensures that duplicate network submissions execute the financial debit exactly once.
  - `Correlation ID`: Dictates distributed observability and auditability. Links log streams, latency spans, and error traces across disparate microservices without enforcing deduplication logic.
- Crucial Regulatory and Operational Functions:
  - Rapid incident resolution during customer disputes: Pinpointing whether failure occurred at the gateway or card switch.
  - End-to-end distributed tracing using OpenTelemetry to measure sub-second network latency across global banking networks.""",
    "walkthrough_en": """Propagating correlation IDs across OkHttp interceptors and database logs in Kotlin:
```kotlin
class CorrelationIdInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()

        // Extract existing correlation ID from request header or generate a structured POS trace token
        val correlationId = original.header("X-Correlation-ID")
            ?: "POS-TRACE-${UUID.randomUUID()}"

        val authenticatedRequest = original.newBuilder()
            .header("X-Correlation-ID", correlationId)
            .build()

        // Log locally with correlation tag for instant Logcat filtering
        PaymentLogger.d("Dispatching payment [Correlation: $correlationId]")

        return chain.proceed(authenticatedRequest)
    }
}

// Client domain invocation attaching correlation context
data class PaymentContext(
    val transactionId: String,
    val correlationId: String = "TX-${System.currentTimeMillis()}-${UUID.randomUUID().toString().take(8)}"
)
```""",
    "short_en": """A transaction correlation ID is a globally unique identifier attached to a payment at inception that flows across all distributed hops from mobile client to banking switch. While an idempotency key prevents duplicate billing, a correlation ID enables distributed tracing, linking client timeouts to backend logs to resolve customer disputes and reconcile ledgers.""",
    "structured_en": """A transaction correlation ID is an essential observability and audit token in distributed financial architectures.
A single mobile payment traverses a complex multi-hop path: the Android terminal, the cloud payment gateway, risk management engines, bank switches, and the cardholder\'s issuing bank. If a timeout occurs, identifying where the request stalled becomes impossible without a shared identifier.
The client generates an immutable correlation ID at the moment the transaction begins and attaches it to all HTTP headers, database records, and ISO 8583 message fields. Every downstream service preserves and logs this token.
It is critical to distinguish a correlation ID from an idempotency key. An idempotency key enforces business deduplication to ensure funds are debited only once. A correlation ID provides distributed observability, stitching together asynchronous logs across servers.
During transaction disputes or latency spikes, engineers use the correlation ID to trace the exact lifecycle of the payment end-to-end, proving whether funds cleared and identifying the root cause of failures.""",
    "deep_senior_en": """From a distributed tracing, financial forensics, and OpenTelemetry architectural standpoint, the correlation ID is the foundational spine of financial system observability.
In microservice and fintech ecosystems, payment requests cross diverse architectural domains operating on different protocols, including REST over TLS, gRPC, and legacy ISO 8583 binary switch sockets. When an Android POS terminal experiences an SSL handshake timeout or a gateway 504 error, the client UI possesses zero context regarding whether the failure occurred within the cloud ingress, the fraud screening pipeline, or the interbank clearing network.
By assigning an immutable, high-entropy correlation ID at transaction creation, the mobile client establishes a deterministic anchor. This ID is injected into standard HTTP headers such as X-Correlation-ID or W3C TraceContext traceparent, and mapped directly to ISO 8583 Field 37 Retrieval Reference Number and Field 11 Systems Trace Audit Number.
This token enables distributed log correlation across distributed search clusters like Elasticsearch. A single query on the correlation ID reveals the complete distributed span: the exact millisecond the terminal sent the SYN packet, the duration the gateway spent in Redis evaluating idempotency, the precise latency of the bank switch authorization, and the exact packet where the connection dropped.
Crucially, while an idempotency key instructs downstream ledger endpoints to ignore duplicate execution, the correlation ID maintains forensic traceability. In regulatory audits, fraud investigations, and reconciliation dispute resolution, the correlation ID provides indisputable forensic proof of the payment lifecycle across international banking rails.""",
    "meta_ar": {
        "id": "PAY-05",
        "questionAr": "ما هو معرّف ارتباط المعاملة (Correlation ID) ولماذا يُعد إلزامياً في الأنظمة المالية الموزعة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "مفهوم التتبع الموزع (Distributed Tracing)، دور معرّف الارتباط (Correlation ID)، الفرق بينه وبين مفتاح الحتمية (Idempotency Key)، تمريره عبر الترويسات وحقول ISO 8583، واستخدامه في حل النزاعات.",
        "concept_ar": "يمثل معرّف ارتباط المعاملة (Correlation ID) معرّفاً فريداً وغير قابل للتغيير يُولد لحظة إنشاء المعاملة في تطبيق الهاتف ويمر عبر كافة المحطات والأنظمة الموزعة: تمر المعاملة المالية عبر مسار معقد يبدأ من هاتف نقطة البيع، ثم بوابة الدفع السحابية، فأنظمة مكافحة الاحتيال، ثم مقسم البنك الوسيط، وحتى نظام البنك المصدر للبطاقة وشبكات فيزا وماستركارد. وبدون معرّف موحد يربط هذه المحطات، يستحيل تتبع سبب انقطاع الاتصال أو معرفة النقطة التي توقفت عندها المعاملة. ويختلف معرّف الارتباط جوهرياً عن مفتاح الحتمية (Idempotency Key)؛ فمفتاح الحتمية وظيفته منع الخصم المزدوج وتكرار العمليات، بينما معرّف الارتباط وظيفته المراقبة والتدقيق والتتبع اللوجي (Observability & Tracing). ويتم تمرير المعرّف في ترويسات HTTP كـ `X-Correlation-ID` وحقول رسائل ISO 8583 كحقل RRN وحقل STAN؛ مما يتيح تجميع سجلات الخوادم المختلفة في شاشة واحدة وحل نزاعات العملاء بلحظات.",
        "walkthrough_ar": """تضمين معرّف الارتباط وتمريره تلقائياً عبر معترض الشبكة في كوتلن:
```kotlin
class CorrelationIdInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()

        // استخراج معرّف الارتباط الحالي أو توليد معرّف تتبع فريد
        val correlationId = original.header("X-Correlation-ID")
            ?: "POS-TRACE-${UUID.randomUUID()}"

        val authenticatedRequest = original.newBuilder()
            .header("X-Correlation-ID", correlationId)
            .build()

        // تسجيل المعرّف في السجلات المحلية لسهولة الفلترة والبحث
        PaymentLogger.d("Dispatching payment [Correlation: $correlationId]")

        return chain.proceed(authenticatedRequest)
    }
}

// نموذج نية الدفع مزوداً بمعرّف الارتباط الدائم
data class PaymentContext(
    val transactionId: String,
    val correlationId: String = "TX-${System.currentTimeMillis()}-${UUID.randomUUID().toString().take(8)}"
)
```""",
        "why_it_matters_ar": "غياب معرّف الارتباط يحول البحث عن سبب فشل المعاملة في الخوادم إلى مستحيل تقني ويؤخر حل شكاوى العملاء المالية لأسابيع.",
        "worked_example_ar": "اشتكى عميل من تعليق عملية بقيمة 5000 جنيه وظهور رسالة مهلة اتصال؛ وبفضل البحث بـ Correlation ID في سجلات السحابة، اكتشفنا خلال ثوانٍ أن البنك وافق وأن المشكلة كانت انقطاع برج الاتصال.",
        "trade_offs_ar": "توليد وتمرير معرّف الارتباط يستهلك بضع بايتات إضافية في كل طلب؛ في مقابل توفير مئات الساعات من البحث العشوائي في سجلات الخوادم وقواعد البيانات.",
        "failure_modes_ar": "أخطر الأخطاء هو تغيير معرّف الارتباط عند إعادة إرسال الطلب (Retry)، مما يفصل محاولات نفس المعاملة ويجعل تتبع المسار المشترك مستحيلاً.",
        "production_perspective_ar": "في كود الإنتاج، يُربط معرّف الارتباط بمعايير OpenTelemetry ويُسجل تلقائياً في حقل RRN (Field 37) في رسائل البنوك لتسهيل المطابقة السريعة.",
        "how_to_answer_ar": "ابدأ برسم مسار المعاملة الموزع عبر عدة أنظمة، ثم وضح دور المعرّف في ربط السجلات، وفرّق بدقة بينه وبين مفتاح الحتمية، واشرح تمريره في ترويسات HTTP وحقول ISO 8583.",
        "talking_points_ar": "معرّف الارتباط Correlation ID، التتبع الموزع Distributed Tracing، الفرق مع Idempotency Key، معايير OpenTelemetry، حقول RRN وSTAN في ISO 8583.",
        "follow_ups_ar": "كيف يربط معرّف الارتباط بين طلبات HTTP غير المتزامنة ورسائل الـ Webhooks؟ وما هو معيار W3C Trace Context؟",
        "self_check_ar": "هل فرقت بين معرّف الارتباط ومفتاح الحتمية، ووضحت كيفية تدفقه عبر الأنظمة واستخدامه في كشف أسباب المشكلات؟",
        "references_ar": f"- [W3C Recommendation: Trace Context specification](https://www.w3.org/TR/trace-context/) — المعيار القياسي المعتمد عالمياً لتمرير سياق التتبع ومعرّفات العمليات عبر الأنظمة الموزعة.\n- [OpenTelemetry Documentation: Tracing Concepts](https://opentelemetry.io/docs/concepts/signals/traces/) — التوثيق المرجعي لتقنيات التتبع الموزع ومراقبة أداء المعاملات والأنظمة السحابية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """معرّف ارتباط المعاملة هو معرّف فريد يُولد عند بدء الدفع ويمر عبر كافة الأنظمة من الهاتف إلى خوادم البنك لربط السجلات وتتبع المسار الموزع. يختلف عن مفتاح الحتمية الذي يمنع الخصم المزدوج؛ حيث يختص معرّف الارتباط بالتدقيق والمراقبة واستكشاف الأخطاء عند انقطاع الاتصال وحل نزاعات العملاء فورياً.""",
        "best_answer_ar": """يمثل معرّف ارتباط المعاملة ركيزة المراقبة والتدقيق المحاسبي في بنية الأنظمة المالية الموزعة.
تمر المعاملة المالية عبر عدة خوادم وأنظمة مستقلة تبدأ من تطبيق الهاتف وتمر ببوابة الدفع السحابية وخوارزميات الاحتيال ومقسمات البنوك وشبكات البطاقات. فإذا حدث انقطاع في الاتصال، يستحيل معرفة النقطة التي توقفت عندها المعاملة دون معرّف مشترك يربط هذه النظم ببعضها.
يولد التطبيق معرّف الارتباط لحظة ضغط العميل على الدفع ويثبته في سجلاته، ثم يمرره في ترويسات الطلب وحقول رسائل المقاصة البنكية؛ حيث تقوم كافة الخدمات الخلفية بتسجيله ضمن سجلاتها التتبعية.
ومن الضروري التمييز بينه وبين مفتاح الحتمية؛ فمفتاح الحتمية يمنع الخصم المزدوج ويضمن تنفيذ المعاملة لمرة واحدة فقط، بينما معرّف الارتباط يربط سجلات الأحداث وأزمنة الاستجابة عبر الخوادم لحل النزاعات وفهم سبب أي عطل بسرعة متناهية.""",
        "deep_answer_ar": """من منظور هندسة المراقبة الموزعة والتحقيقات الجنائية الرقمية في قطاع التكنولوجيا المالية، يشكل معرّف الارتباط العمود الفقري لتتبع دورة حياة المعاملة المالية.
في الأنظمة البنكية المعقدة، تتنقل حزم البيانات عبر بروتوكولات متباينة تشمل طلبات REST ونداءات gRPC ومقابس ISO 8583 الثنائية المباشرة مع البنوك المركزية. وعندما يواجه هاتف نقطة البيع مهلة اتصال أو استجابة بالخطأ خمسة مئة وأربعة، تفتقر الشاشة لأي تفاصيل تحدد ما إذا كان التأخير ناتجاً عن فحص الاحتيال السحابي أم عن تأخر المقسم المصرفي.
وهنا يبرز دور معرّف الارتباط كمرساة موحدة لا تتغير؛ حيث يُحقن في ترويسات W3C TraceContext ويُطابق مع رقم مرجع الاسترجاع RRN ورقم التدقيق STAN في الرسائل البنكية.
يتيح هذا المعرّف لمهندسي النظم إجراء استعلام موحد في منصات مراقبة السجلات لتجميع كامل المسار الزمني؛ فيظهر بدقة توقيت إرسال الطلب من الهاتف، ووقت معالجته في السحابة، ولحظة خصم الرصيد في البنك، والسبب الدقيق لتعثر استلام الرد على الجهاز.
هذا الفصل الواضح بين الحتمية التي تضمن الأمان المالي، والارتباط الذي يوفر الرؤية التشغيلية الكاملة، يضمن تقديم براهين قاطعة لفض النزاعات وتلبية المتطلبات الرقابية للمصارف المركزية، وتمكين فرق الدعم الفني من حل المشكلات المعقدة خلال دقائق معدودة بدلاً من الغرق في مليارات السجلات العشوائية غير المترابطة."""
    }
}

# ==========================================
# PAY-06: How do you ensure atomic persistence of transaction status and reversal intent?
# ==========================================
DATA["PAY-06"] = {
    "concept_en": """Ensuring atomic persistence of transaction status transitions and reversal intent prevents state skew where a transaction is marked failed locally but the reversal is never dispatched:
- The State Skew Trap (The Dual-Write Hazard):
  - Scenario:
    1. Client transitions transaction status from `PROCESSING` to `UNKNOWN` or `FAILED` in the database.
    2. App attempts to enqueue a background reversal job in WorkManager or a separate table.
    3. The OS kills the process between steps 1 and 2 due to low memory or user swipe.
  - Consequence: The database marks the payment failed, but the reversal intent was never recorded. The issuer keeps the cardholder funds locked indefinitely.
- The Architectural Solution: Atomic Two-Phase Database Transactions:
  - Both mutations must execute within a single atomic database transaction (`db.withTransaction` or `BEGIN IMMEDIATE TRANSACTION`).
  - Table 1: `payment_transactions` (Updates status to `IN_DOUBT`).
  - Table 2: `reversal_queue` (Inserts reversal record containing transactionId, correlationId, STAN, amount, retryCount, and payload).
- SQLite ACID Guarantees:
  - Atomicity ensures that either both mutations are committed to the Write-Ahead Log (WAL) or neither is.
  - Durability ensures that once committed, power disconnection cannot corrupt or revert the queued reversal intent.""",
    "walkthrough_en": """Executing atomic transaction state update and reversal queuing in Kotlin Room:
```kotlin
@Entity(tableName = "reversal_queue")
data class ReversalQueueEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val transactionId: String,
    val correlationId: String,
    val amountCents: Long,
    val originalStan: String,
    val retryCount: Int = 0,
    val createdAtEpoch: Long = System.currentTimeMillis()
)

class PaymentPersistenceCoordinator(
    private val appDatabase: AppDatabase,
    private val paymentDao: PaymentDao,
    private val reversalDao: ReversalDao
) {
    suspend fun markTransactionInDoubtAndQueueReversal(
        transactionId: String,
        correlationId: String,
        amount: Long,
        stan: String
    ) {
        // ATOMIC GUARANTEE: Single SQLite transaction ensures zero state skew
        appDatabase.withTransaction {
            // Step 1: Update transaction journal to IN_DOUBT state
            paymentDao.updateStatus(transactionId, "IN_DOUBT")

            // Step 2: Enqueue reversal intent in the persistent table
            reversalDao.insertReversal(
                ReversalQueueEntity(
                    transactionId = transactionId,
                    correlationId = correlationId,
                    amountCents = amount,
                    originalStan = stan
                )
            )
        }
    }
}
```""",
    "short_en": """Ensure atomic persistence by wrapping the transaction state update and the reversal queue insertion inside a single atomic SQLite database transaction using Room's withTransaction. This eliminates the dual-write hazard, guaranteeing that if a timeout occurs, the in-doubt status and the reversal intent are committed together to the Write-Ahead Log, surviving sudden power loss or process death.""",
    "structured_en": """Atomic persistence of transaction status and reversal intent is necessary to avoid catastrophic state skew in financial applications.
When a transaction encounters a network timeout, the application must mark the transaction as in-doubt and enqueue a reversal instruction to cancel the cardholder hold. If these two operations are executed separately, a process crash or battery removal between them leaves the database showing a failed transaction while the reversal intent vanishes. The customer\'s funds remain locked at the bank with no automated recovery path.
To resolve this, the system executes both mutations inside a single atomic database transaction using Room\'s withTransaction block. The database simultaneously updates the payment record to in-doubt and inserts a new entry into the persistent reversal queue table.
Because SQLite guarantees atomicity and durability via Write-Ahead Logging, either both records are permanently committed to disk or neither is, ensuring that unacknowledged authorizations are always paired with a durable reversal intent.""",
    "deep_senior_en": """From an ACID database guarantees and mission-critical financial engineering perspective, dual-write operations represent the single most common source of payment state desynchronization.
The dual-write problem occurs whenever an application attempts to modify two independent storage constructs or state stores sequentially without distributed transactional semantics. In POS terminals, marking a payment as Unknown in SQLite while registering a reversal task in WorkManager as two separate operations creates an unavoidable race window. If the Low Memory Killer or a user battery disconnection occurs precisely after the database write but prior to the WorkManager enqueue, the reversal intent evaporates. The client considers the transaction terminated, but the card brand ledger maintains an active authorization hold.
The robust engineering solution decouples external job scheduling from state persistence by employing the Transactional Outbox pattern backed by SQLite ACID transactions.
Within a single database transaction using SQLite\'s BEGIN IMMEDIATE mode, the system updates the payment journal record to IN_DOUBT and inserts a corresponding record into a dedicated reversal_queue table. SQLite\'s Write-Ahead Log guarantees that both rows are flushed to non-volatile flash memory simultaneously.
A separate, idempotent background worker continuously polls the reversal_queue table or listens to Room invalidation trackers. Even if the terminal experiences immediate power loss, the recovery engine during device boot detects the pending row in the reversal_queue and dispatches the ISO 8583 reversal message. This architecture guarantees zero orphan transactions and perfect ledger consistency.""",
    "meta_ar": {
        "id": "PAY-06",
        "questionAr": "كيف تضمن التثبيت الذري (Atomic Persistence) لحالة المعاملة ونية العكس في قاعدة البيانات المحلية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "معالجة معضلة الكتابة المزدوجة (Dual-Write Hazard)، تطبيق المعاملات الذرية (Atomic DB Transactions) في Room، نمط صندوق الصادر (Transactional Outbox)، ومنع ضياع نية العكس (Reversal Intent) عند موت التطبيق.",
        "concept_ar": "يعد ضمان التثبيت الذري (Atomic Persistence) لحالة المعاملة ونية العكس ضرورياً لمنع الانفصال المعماري (State Skew) بين ما يعرضه التطبيق وما هو مسجل في البنك: عند انقطاع الاتصال بعد إرسال التفويض، يحتاج التطبيق إلى تحديث حالة المعاملة إلى `IN_DOUBT` وإدراج طلب عكس (Reversal) لإلغاء حجز الأموال في البنك. فإذا نُفذت هاتان العمليتان بشكل منفصل، وسقط التطبيق أو نَفِدت البطارية بين الخطوتين، فستتحدث الحالة محلياً بينما تضيع نية العكس للأبد، ويبقى رصيد العميل محجوزاً في البنك دون أي آلية لإلغائه! والحل الهندسي الحاسم هو دمج العمليتين داخل معاملة ذرية واحدة في قاعدة بيانات SQLite عبر `db.withTransaction` في مكتبة Room؛ حيث يتم تحديث جدول المعاملات وإدراج سجل العكس في جدول طابور الإلغاء في نفس اللحظة. ووفقاً لخصائص ACID ونمط الكتابة المسبقة WAL، فإما أن يُحفظ التعديلان معاً على القرص الصلب أو لا يُحفظ أي منهما، مما يضمن استحالة ضياع طلب العكس مهما كانت الأعطال.",
        "walkthrough_ar": """تطبيق الحفظ الذري لحالة المعاملة وطابور العكس داخل معاملة واحدة في كوتلن:
```kotlin
@Entity(tableName = "reversal_queue")
data class ReversalQueueEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val transactionId: String,
    val correlationId: String,
    val amountCents: Long,
    val originalStan: String,
    val retryCount: Int = 0,
    val createdAtEpoch: Long = System.currentTimeMillis()
)

class PaymentPersistenceCoordinator(
    private val appDatabase: AppDatabase,
    private val paymentDao: PaymentDao,
    private val reversalDao: ReversalDao
) {
    suspend fun markTransactionInDoubtAndQueueReversal(
        transactionId: String,
        correlationId: String,
        amount: Long,
        stan: String
    ) {
        // ضمان الذرية التامة: معاملة قاعدة بيانات واحدة تمنع الفقدان
        appDatabase.withTransaction {
            // 1. تحديث حالة المعاملة في الدفتر إلى معلقة
            paymentDao.updateStatus(transactionId, "IN_DOUBT")

            // 2. إدراج نية العكس في طابور التراجع الدائم بنفس اللحظة
            reversalDao.insertReversal(
                ReversalQueueEntity(
                    transactionId = transactionId,
                    correlationId = correlationId,
                    amountCents = amount,
                    originalStan = stan
                )
            )
        }
    }
}
```""",
        "why_it_matters_ar": "فقدان طلب العكس يترك أموال العميل معلقة في البنك لأسبوعين، ويحرمه من رصيده ويتسبب في شكاوى احتيال ضد التاجر.",
        "worked_example_ar": "عند انقطاع الاتصال، كُتبت حالة IN_DOUBT وسجل طابور العكس داخل معاملة ذرية واحدة؛ وفصل المستخدم البطارية في نفس اللحظة؛ وبإعادة التشغيل وجد النظام سجل العكس في قاعدة البيانات وأرسله للبنك فوراً.",
        "trade_offs_ar": "فتح معاملة ذرية في SQLite يحجز قفل الكتابة لجزء ضئيل من الثانية؛ لكنه يحمي من فقدان نية العكس ويضمن سلامة القيود المالية.",
        "failure_modes_ar": "أخطر الأخطاء هو تحديث حالة المعاملة في قاعدة البيانات ثم الاعتماد على WorkManager غير المتزامن لإدراج العكس لاحقاً، مما يفتح نافذة زمنية لسقوط التطبيق وضياع العكس.",
        "production_perspective_ar": "في كود الإنتاج، يُطبق نمط Transactional Outbox؛ حيث يُقرأ طابور العكس من جدول محلي مستقل بواسطة عامل خلفي دوري فور توفر شبكة الاتصال.",
        "how_to_answer_ar": "اشرح فخ الكتابة المزدوجة Dual-Write Hazard، ووضح كيف يسبب موت التطبيق بين العمليتين ضياع طلب العكس، واشرح الحل عبر withTransaction ونمط Transactional Outbox.",
        "talking_points_ar": "التثبيت الذري Atomic Persistence، فخ الكتابة المزدوجة Dual-Write Hazard، معاملات Room عبر withTransaction، نمط صندوق الصادر Transactional Outbox، وخصائص ACID.",
        "follow_ups_ar": "كيف يضمن نمط Transactional Outbox استئناف إرسال طلبات العكس بعد إعادة تشغيل الهاتف؟ وماذا يحدث لو تعطل الخادم أثناء إرسال العكس؟",
        "self_check_ar": "هل شرحت مخاطر تنفيذ العمليتين بشكل منفصل، ووضحت دور المعاملة الذرية في Room، وربطت الحل بإنقاذ رصيد العميل المحجوز؟",
        "references_ar": f"- [Android Developers: Room withTransaction documentation](https://developer.android.com/reference/kotlin/androidx/room/package-summary#(androidx.room.RoomDatabase).withTransaction(kotlin.coroutines.SuspendFunction0)) — التوثيق الرسمي لتنفيذ المعاملات الذرية المتزامنة في مكتبة Room.\n- [Martin Fowler: Transactional Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html) — المرجع الكلاسيكي لنمط صندوق الصادر لضمان تكامل وموثوقية الرسائل الموزعة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نضمن التثبيت الذري بدمج تحديث حالة المعاملة إلى حالة الشك وتسجيل نية العكس داخل معاملة قاعدة بيانات واحدة عبر withTransaction في Room. يقضي هذا على فخ الكتابة المزدوجة؛ حيث يضمن نمط الكتابة المسبقة في SQLite كتابة السجلين معاً على القرص الصلب في نفس اللحظة، لمنع ضياع طلب العكس إذا سقط التطبيق أو انقطعت الطاقة.""",
        "best_answer_ar": """يمثل التثبيت الذري لحالة المعاملة ونية العكس صمام الأمان لمنع انفصال القيود المالية عند حدوث انقطاع مفاجئ في الاتصال.
تكمن الخطورة في فخ الكتابة المزدوجة؛ فعند انتهاء مهلة الاتصال يحتاج التطبيق إلى تحديث حالة المعاملة إلى حالة الشك وتسجيل طلب عكس لإلغاء حجز الأموال في البنك. فإذا نُفذ التعديلان كخطوتين منفصلتين وسقط التطبيق بينهما بسبب نفاد الذاكرة أو نزع البطارية، تسجل المعاملة كفاشلة محلياً بينما يتبخر طلب العكس؛ فيظل رصيد العميل مجمداً في البنك دون أي آلية لإلغائه.
ولحل هذه المعضلة هندسياً، تُدمج العمليتان داخل معاملة ذرية موحدة في قاعدة البيانات باستخدام withTransaction في مكتبة Room.
تقوم قاعدة البيانات بتحديث جدول المعاملات وإدراج سجل جديد في جدول طابور العكس في نفس الجزء من الثانية وبأمر واحد.
وبفضل مبادئ ACID ونمط الكتابة المسبقة، يضمن النظام إما حفظ العمليتين معاً على القرص الصلب أو التراجع عنهما معاً، مما يضمن بقاء نية العكس محفوظة وجاهزة للإرسال حتى لو أُغلق الهاتف فجأة.""",
        "deep_answer_ar": """من منظور سلامة المعاملات البنكية ومبادئ ACID في قواعد البيانات، تعد مشكلة الكتابة المزدوجة السبب الأكثر شيوعاً لتعليق المبالغ وضياع حقوق العملاء في تطبيقات الدفع.
تحدث هذه الفجوة المعمارية عندما تحاول المنظومة تعديل حالتين مستقلتين بتسلسل زمني عادي دون مظلة ذرية واحدة. ففي أجهزة نقاط البيع المحمولة، يؤدي تحديث سجل المعاملة إلى IN_DOUBT ثم محاولة جدولة مهمة العكس في WorkManager إلى نافذة خطر حرجة؛ فإذا تدخل نظام أندرويد لقتل التطبيق أو سحب المستخدم البطارية في ذلك الجزء من الثانية، يُسجل الفشل محلياً بينما تفقد المنظومة أثر طلب العكس تماماً، ليظل الحجز المصرفي فعالاً لأسابيع في حساب حامل البطاقة.
والعلاج الهندسي الرصين يستند إلى نمط صندوق الصادر التبادلي Transactional Outbox المدعوم بمعاملات SQLite الذرية.
نفتح معاملة حصرية واحدة عبر withTransaction؛ حيث يُحدث جدول الدفاتر المالية ويُدرج في جدول reversal_queue صف جديد يحتوي على المعرف ورقم التدقيق والمبلغ الأصلي. وبفضل نمط الكتابة المسبقة WAL، تُكتب هذه البيانات في القرص الصلب معاً ككتلة واحدة غير قابلة للتجزئة.
وعند إقلاع الجهاز، يقوم عامل خلفي مستقل بفحص جدول العكس وإرسال رسائل الإلغاء ISO 8583 للبنك حتى وصول التأكيد. هذا الإحكام المعماري يضمن تصفية كافة الحجوزات المعلقة ويحقق التطابق المالي التام في جميع الظروف الاستثنائية."""
    }
}

# ==========================================
# PAY-07: How do you design a reversal queue that survives a battery removal?
# ==========================================
DATA["PAY-07"] = {
    "concept_en": """Designing a hardware-resilient payment reversal queue requires persistent queuing, boot-time reconciliation, and transactional gatekeeping:
- The Hardware Threat Model:
  - POS terminals operate in hostile physical environments where cashiers or drops cause instantaneous battery detachment, immediately halting the CPU without OS shutdown hooks.
  - In-flight memory queues, coroutine channels, or standard SharedPreferences are instantly lost or corrupted.
- Core Architectural Pillars:
  1. Durable Storage with Strict Synchronization:
     - The queue lives in SQLite using Room, configured with Write-Ahead Logging (WAL) and `PRAGMA synchronous = FULL` to ensure that every committed reversal record is physically synced to non-volatile NAND flash memory.
  2. Boot-Time and Network Recovery Workers:
     - A BroadcastReceiver listening for `android.intent.action.BOOT_COMPLETED` and `android.net.conn.CONNECTIVITY_CHANGE` initializes a dedicated persistent `CoroutineWorker` via WorkManager using `ExistingWorkPolicy.KEEP`.
  3. Gatekeeping the Transaction Terminal (Stop-the-World Rule):
     - In banking standards (APACS / ISO 8583 / EMVCo), a terminal that possesses an unresolved reversal in its persistent queue must block all subsequent sales until the reversal is either acknowledged by the acquirer or resolved via status inquiry.
  4. Exponential Backoff with Jitter:
     - Retry logic employs exponential backoff capped at 60 seconds with full randomized jitter to avoid thundering-herd spikes on bank switches after network outages.""",
    "walkthrough_en": """Implementing a persistent, crash-proof reversal worker and repository in Kotlin:
```kotlin
@Entity(tableName = "pending_reversals")
data class PendingReversalEntity(
    @PrimaryKey val transactionId: String,
    val correlationId: String,
    val stan: String,
    val rrn: String?,
    val amountCents: Long,
    val attempts: Int = 0,
    val lastAttemptEpoch: Long = 0L
)

class ReversalWorker(
    appContext: Context,
    workerParams: WorkerParameters,
    private val reversalDao: PendingReversalDao,
    private val paymentSwitchApi: PaymentSwitchApi
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val pending = reversalDao.getAllPending()
        if (pending.isEmpty()) return Result.success()

        for (reversal in pending) {
            try {
                // Dispatch ISO 8583 0400 Reversal Message
                val ack = paymentSwitchApi.sendReversal(
                    stan = reversal.stan,
                    amount = reversal.amountCents,
                    correlationId = reversal.correlationId
                )
                if (ack.isSuccess) {
                    reversalDao.delete(reversal.transactionId)
                } else {
                    reversalDao.incrementAttempts(reversal.transactionId, System.currentTimeMillis())
                }
            } catch (e: IOException) {
                // Transient network failure: retry on next scheduled interval
                return Result.retry()
            }
        }
        return Result.success()
    }
}
```""",
    "short_en": """Design a battery-proof reversal queue using SQLite Room with Write-Ahead Logging and synchronous FULL flash syncing. Schedule dispatch via WorkManager triggered on boot and network reconnection with exponential backoff. Crucially, enforce terminal gatekeeping, blocking subsequent retail transactions until any pending reversal is acknowledged by the bank switch.""",
    "structured_en": """Building a payment reversal queue that survives instantaneous battery removal requires hardware-aware data persistence and strict terminal operational rules.
The queue is backed by an SQLite Room table rather than in-memory queues. We configure SQLite with Write-Ahead Logging and synchronous FULL mode to guarantee that transactions are flushed directly to non-volatile flash memory before execution continues.
To handle recovery, an Android BroadcastReceiver detects device boot and schedules a reliable WorkManager task. When connectivity restores, the worker reads the queue and dispatches ISO 8583 reversal messages to the bank switch using exponential backoff with randomized jitter.
The essential financial safeguard is terminal gatekeeping. Under certified payment standards, a POS device with an unresolved reversal in its queue must refuse to process new sales until the reversal is cleared. This prevents the terminal from accumulating un-reconciled transactions and forces immediate resolution of ambiguous ledger states.""",
    "deep_senior_en": """From an embedded POS certification and EMVCo level 2/3 terminal engineering standpoint, building a battery-proof reversal engine requires designing for catastrophic power interruption as a normal operational condition.
Handheld payment terminals in supermarkets and delivery logistics are subjected to constant physical trauma. A battery pack can detach mid-swipe, abruptly depriving the processor of voltage without allowing Android to run clean-up callbacks or execute onTrimMemory routines.
Under these physical constraints, data integrity rests on the storage driver. We configure Room over SQLite with PRAGMA synchronous set to FULL or EXTRA. This forces the underlying Linux storage driver to issue hardware flush commands, ensuring that the reversal row is burned into NAND flash sectors before the thread unblocks.
When the terminal reboots after a battery replacement, a BOOT_COMPLETED receiver schedules a persistent WorkManager job configured with NetworkType.CONNECTED.
More importantly, the payment UI layer incorporates a hardware gatekeeper rule. Before the cashier can enter a new sale amount, the application checks whether any rows exist in the pending_reversals table. If an unresolved reversal is present, the app locks the transaction screen and displays a Reversal In Progress banner. The terminal executes the 0400 reversal message or queries the switch status endpoint. Only upon receiving a signed cryptographic acknowledgement from the acquirer does the terminal purge the record and unlock the sale interface. This strict architectural invariant guarantees that the merchant never operates with unbalanced local ledgers.""",
    "meta_ar": {
        "id": "PAY-07",
        "questionAr": "كيف تصمم طابور عمليات العكس (Reversal Queue) بحيث يصمد أمام نزع البطارية وموت الجهاز المفاجئ؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصميم طوابير العكس المقاومة للأعطال الفيزيائية، ضبط SQLite بنمط الكتابة المسبقة والمزامنة الكاملة (PRAGMA synchronous = FULL)، استئناف العمل عبر WorkManager عند الإقلاع، وقاعدة حظر المبيعات اللاحقة (Terminal Gatekeeping).",
        "concept_ar": "يتطلب تصميم طابور عمليات العكس (Reversal Queue) القادر على النجاة من نزع البطارية المفاجئ الجمع بين التخزين الدائم الصلب وبروتوكولات التعافي الصارمة وحظر العمليات اللاحقة: في بيئات نقاط البيع المحمولة، يتعرض الجهاز للسقوط أو نزع البطارية دون أي فرصة للنظام لتنفيذ دوال الإغلاق؛ لذا يُحظر تماماً حفظ الطابور في الرام. ويعتمد التصميم على 4 ركائز: أولاً، حفظ الطابور في جدول SQLite بـ Room مع ضبط `PRAGMA synchronous = FULL` لضمان إجبار نظام التشغيل على كتابة البيانات في ذاكرة الفلاش NAND الحقيقية فوراً؛ ثانياً، تسجيل مستقبل إقلاع `BOOT_COMPLETED` وجدولة مهمة `WorkManager` مستمرة تعمل فور فتح الشبكة؛ ثالثاً، تطبيق قاعدة حظر المبيعات (Gatekeeping Rule) وفق معايير EMV العالمية، حيث يُمنع الكاشير من إجراء أي بيع جديد وتُقفل الشاشة حتى يتم إرسال طلب العكس المعلق واعتماده من البنك؛ رابعاً، استخدام التراجع الأسي العشوائي (Exponential Backoff with Jitter) لتجنب إغراق خوادم البنك عند عودة الاتصال.",
        "walkthrough_ar": """تصميم طابور العكس الدائم في قاعدة البيانات وعامل التعافي في كوتلن:
```kotlin
@Entity(tableName = "pending_reversals")
data class PendingReversalEntity(
    @PrimaryKey val transactionId: String,
    val correlationId: String,
    val stan: String,
    val rrn: String?,
    val amountCents: Long,
    val attempts: Int = 0,
    val lastAttemptEpoch: Long = 0L
)

class ReversalWorker(
    appContext: Context,
    workerParams: WorkerParameters,
    private val reversalDao: PendingReversalDao,
    private val paymentSwitchApi: PaymentSwitchApi
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val pending = reversalDao.getAllPending()
        if (pending.isEmpty()) return Result.success()

        for (reversal in pending) {
            try {
                // إرسال رسالة العكس القياسية ISO 8583 0400
                val ack = paymentSwitchApi.sendReversal(
                    stan = reversal.stan,
                    amount = reversal.amountCents,
                    correlationId = reversal.correlationId
                )
                if (ack.isSuccess) {
                    reversalDao.delete(reversal.transactionId)
                } else {
                    reversalDao.incrementAttempts(reversal.transactionId, System.currentTimeMillis())
                }
            } catch (e: IOException) {
                // تعثر شبكي مؤقت: إعادة المحاولة تلقائياً عبر WorkManager
                return Result.retry()
            }
        }
        return Result.success()
    }
}
```""",
        "why_it_matters_ar": "فقدان طلبات العكس عند نزع البطارية يعلق أموال العملاء في البنوك لأيام ويؤدي لغرامات فورية في اختبارات الاعتماد المصرفي لنقاط البيع.",
        "worked_example_ar": "نزع الكاشير البطارية عمداً أثناء انتظار رد البنك؛ وعند تشغيل الجهاز، اكتشف النظام وجود طلب عكس في طابور الفلاش، فقفل شاشة البيع وأرسل العكس فوراً للبنك وحرر رصيد العميل قبل السماح بأي عملية جديدة.",
        "trade_offs_ar": "قفل شاشة نقطة البيع لحين إرسال العكس يعطل الكاشير لبضع ثوانٍ؛ لكنه يمنع تراكم فجوات محاسبية غير قابلة للحل بين التاجر والبنك.",
        "failure_modes_ar": "أخطر الأخطاء هو ترك خيار المزامنة في SQLite على الوضع العادي دون Flush صلب، مما يبقي البيانات في الـ Cache ويتسبب في ضياعها عند قطع الكهرباء.",
        "production_perspective_ar": "في المعايير المصرفية العالمية، يُفحص هذا السلوك باختبار نزع البطارية المادي (Blackout Test)؛ وإذا نجح الجهاز في إجراء عملية بيع جديدة قبل تصفية العكس المعلق، يُلغى اعتماده التجاري فوراً.",
        "how_to_answer_ar": "ابدأ ببيان بيئة التشغيل الفيزيائية لنقاط البيع، واشرح ضرورة PRAGMA synchronous = FULL في SQLite، ثم فصّل دور WorkManager ومستقبل الإقلاع، وأكد على قاعدة قفل الشاشة لحين تصفية العكس.",
        "talking_points_ar": "نزع البطارية Battery Pull، ضبط PRAGMA synchronous = FULL، كتابة فلاش NAND، مستقبل BOOT_COMPLETED، جدولة WorkManager، وقاعدة حظر المبيعات Terminal Gatekeeping.",
        "follow_ups_ar": "ماذا تفعل إذا كان خادم البنك معطلاً تماماً وظل طلب العكس عالقاً في الطابور لأكثر من ساعة؟ هل تسمح بالبيع أم يظل الجهاز معطلاً؟",
        "self_check_ar": "هل أكدت على الحفظ الدائم في SQLite، وضبط المزامنة على FULL، وآلية الاستئناف عند الإقلاع، وقاعدة حظر العمليات اللاحقة؟",
        "references_ar": f"- [EMVCo: Terminal Integration Testing Guidelines](https://www.emvco.com/emv-technologies/terminals/) — الإرشادات القياسية لاختبارات اعتماد أجهزة نقاط البيع ومقاومتها لانقطاع الطاقة.\n- [Android Developers: Support persistent work with WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager) — التوثيق الرسمي لجدولة المهام الخلفية الموثوقة والمستمرة عبر إعادة تشغيل الجهاز.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نصمم طابور العكس باستخدام جدول SQLite في Room مع ضبط المزامنة الكاملة PRAGMA synchronous = FULL لضمان تثبيتها في الفلاش قبل أي خطوة. ونربطه بمستقبل إقلاع BOOT_COMPLETED ومهمة WorkManager مستمرة لإرسال العكس فور عودة الشبكة، مع تطبيق قاعدة مصرفية صارمة تقفل شاشة البيع وتمنع أي عملية تالية حتى يتم تأكيد العكس من البنك.""",
        "best_answer_ar": """يتطلب تصميم طابور عمليات العكس المقاوم لفصل البطارية مراعاة الظروف التشغيلية القاسية لأجهزة نقاط البيع المحمولة.
نعتمد في التخزين على جدول دائم في SQLite باستخدام مكتبة Room، مع تفعيل نمط الكتابة المسبقة وضبط إعداد المزامنة PRAGMA synchronous على الوضع الكامل FULL؛ مما يجبر نظام أندرويد على كتابة البيانات مباشرة في شرائح ذاكرة الفلاش قبل تحرير الخيط البرمجي، لحمايتها من التبخر عند انقطاع التيار الكهربائي المفاجئ.
وعند إعادة تشغيل الجهاز، يلتقط مستقبل الإقلاع BOOT_COMPLETED الحدث ويشغل مهمة WorkManager دائمة تعمل في الخلفية بمجرد توفر الاتصال الشبكي، لترسل رسائل العكس القياسية بتراجع أسي مدروس.
والركيزة الأهم في هذا التصميم هي تطبيق قاعدة حظر المبيعات المصرفية Terminal Gatekeeping؛ حيث يفحص التطبيق طابور العكس قبل فتح شاشة الدفع لأي عميل جديد، فإذا وُجدت أي عملية عكس معلقة، تُقفل واجهة البيع وتظهر شاشة جاري تسوية العملية السابقة، ولا يُسمح بإجراء أي حركة جديدة إلا بعد استلام تأكيد رسمي من خادم البنك، لحفظ التوازن المحاسبي التام.""",
        "deep_answer_ar": """من منظور اعتمادات أجهزة نقاط البيع المدمجة ومعايير EMVCo المستوى الثالث، يعد تصميم طابور العكس صمام الأمان الوحيد للتعامل مع انقطاع الطاقة الفيزيائي كحالة تشغيلية اعتيادية.
في البيئات الميدانية ونقاط البيع المتنقلة، يتعرض الجهاز للسقوط الذي يؤدي لخلع البطارية فجأة أثناء المعالجة، مما يحرم معالج الجهاز من الطاقة اللحظية ويمنع تنفيذ أي دوال إغلاق نظامية في نظام أندرويد.
ولمواجهة هذا التحدي الفيزيائي، نبني طابور العكس فوق قاعدة بيانات SQLite مع إلزام مشغل التخزين في نواة لينكس بإصدار أمر تدفق صلب لذاكرة الفلاش عبر تفعيل PRAGMA synchronous = FULL. هذا الإعداد يضمن عدم استقرار السجل في الذاكرة المؤقتة، بل احتراقه في خلايا NAND الفلاشية قبل إتمام المعاملة.
وعند تثبيت البطارية وإقلاع النظام، يُفعل مستقبل الإقلاع مهمة WorkManager بحالة استمرار مصنفة كأولوية حرجة، لتبدأ معالجة الطابور فور استقرار الشريحة الخلوية.
والأهم معمارياً هو فرض بروتوكول قفل نقطة البيع الصارم؛ فبموجب القواعد المصرفية المعتمدة، يُحظر تماماً على جهاز الدفع فتح جلسة بيع جديدة إذا كان دفتره المحلي يحتوي على عملية عكس معلقة. يفرض التطبيق شاشة حظر وتنبيه تفيد بجاري تصفية الحجز المعلق، ويبث رسالة ISO 8583 0400 إلى مقسم البنك. وعند استلام الرد المشفر بحذف التفويض وتحرير رصيد العميل، يُحذف السجل محلياً وتُفتح شاشة المبيعات للكاشير. هذا الانضباط المعماري المتكامل يضمن حماية التاجر والبنك من أي فجوات تدقيق مالي."""
    }
}

# ==========================================
# PAY-08: How do you avoid duplicate payment requests after UI timeout?
# ==========================================
DATA["PAY-08"] = {
    "concept_en": """Preventing duplicate payment requests following a user interface (UI) timeout requires strict architectural separation between UI presentation timeouts and underlying network transaction lifecycles:
- The UI Timeout vs Network Timeout Fallacy:
  - When a payment spinner reaches a UI timeout limit (e.g., 15 seconds), developers often pop the screen or re-enable the \"Pay Now\" button.
  - If the background network socket is still alive or pending at the bank gateway, the user taps \"Pay Now\" a second time, triggering an immediate duplicate charge.
- Key Prevention Mechanisms:
  1. Transactional State Gatekeeping via Local Database:
     - The UI must observe a single source of truth from Room (e.g., `StateFlow<PaymentStatus>`) rather than transient ViewModel or Coroutine states.
     - While a transaction is `INITIATED` or `PROCESSING`, the database enforces an in-flight lock. Any attempt to start a new payment for the same order is rejected with `PaymentInProgressException`.
  2. UI Hard-Disable and Monotonic State Rendering:
     - When the UI timeout fires, the \"Pay Now\" button remains permanently disabled.
     - The UI transitions to an ambiguous inquiry screen (\"Verifying payment status with bank...\").
  3. Status Inquiry Instead of Re-Authorizing:
     - Rather than initiating a new charge, retry buttons after a timeout must route strictly to a Status Polling Endpoint (`GET /v1/payments/{orderId}/status?idempotencyKey=...`).
     - If the status inquiry returns `PENDING`, the app waits; if `APPROVED`, it displays the receipt; if `NOT_FOUND` after a grace period, it triggers the reversal and allows safe re-entry.""",
    "walkthrough_en": """Decoupling UI timeout from transaction lifecycle and routing retries to status polling in Kotlin:
```kotlin
class PaymentViewModel(
    private val paymentRepository: PaymentRepository,
    private val orderId: String
) : ViewModel() {

    private val _uiState = MutableStateFlow<PaymentUiState>(PaymentUiState.Idle)
    val uiState: StateFlow<PaymentUiState> = _uiState.asStateFlow()

    fun onPayClicked(amount: Long) {
        viewModelScope.launch {
            _uiState.value = PaymentUiState.Processing

            try {
                // UI enforce a 15-second visual timeout without killing background transaction
                withTimeout(15_000L) {
                    val result = paymentRepository.executePayment(orderId, amount)
                    _uiState.value = PaymentUiState.Success(result.authCode)
                }
            } catch (e: TimeoutCancellationException) {
                // UI TIMEOUT FIRED: Never re-enable Pay button! Transition to Status Inquiry
                _uiState.value = PaymentUiState.InDoubtCheckStatus
            }
        }
    }

    // Retries strictly query gateway status rather than re-charging!
    fun onCheckStatusClicked() {
        viewModelScope.launch {
            _uiState.value = PaymentUiState.Processing
            val status = paymentRepository.queryPaymentStatus(orderId)
            _uiState.value = when (status) {
                is StatusResult.Approved -> PaymentUiState.Success(status.authCode)
                is StatusResult.NotFound -> PaymentUiState.SafeToRetry
                is StatusResult.Pending -> PaymentUiState.InDoubtCheckStatus
            }
        }
    }
}
```""",
    "short_en": """Avoid duplicate payment requests after a UI timeout by keeping the Pay button disabled and never dispatching a new charge. Instead, transition the screen to an in-doubt verification state that routes retries exclusively to a status inquiry endpoint, checking whether the backend captured the transaction before allowing any safe re-payment.""",
    "structured_en": """Preventing duplicate payment requests after a UI timeout requires decoupling the user interface presentation from the underlying financial transaction lifecycle.
When a loading spinner exceeds a UI timeout threshold, applications must never simply dismiss the screen or restore the Pay button to an active state. If the bank is still processing the initial request, tapping the button again submits a duplicate charge instruction.
To prevent this, the payment lifecycle must be governed by a local database state machine rather than transient UI coroutines. When a UI timeout occurs, the button remains strictly disabled. The UI displays an in-doubt message informing the user that the payment status is being verified.
Furthermore, any user-facing retry action must be rerouted to a status inquiry endpoint rather than an authorization endpoint. The client queries the gateway using the original idempotency key. Only if the gateway authoritatively confirms that no charge was ever recorded does the app safely permit the user to initiate a new checkout.""",
    "deep_senior_en": """From a distributed state coordination and UX resilience perspective, managing UI timeouts in payment workflows addresses a dangerous disconnect between visual perception and network reality.
Network calls on mobile devices frequently endure high latency due to cellular handshakes, DNS resolution, and multi-datacenter bank routing. If an app imposes an arbitrary fifteen-second UI coroutine timeout, cancelling the coroutine scope only aborts the local client socket; the HTTP packet may have already reached the payment gateway and initiated the authorization hold. If the UI then returns to the cart screen and re-enables the checkout button, the user instinctively taps it again, creating a race condition that results in a duplicate financial charge.
The architectural remedy enforces a strict unidirectional state machine backed by persistent storage. When the user taps Pay, the transaction moves to PROCESSING in the local database, locking the order ID. The UI binds directly to this state.
If the UI timer expires, the presentation layer transitions to an In-Doubt reconciliation state while maintaining the checkout button in an immutable disabled state.
Any retry mechanism is strictly bound to an inquiry contract. Instead of invoking the POST charge endpoint, the retry button triggers a GET status check passing the original correlation ID and idempotency key. If the gateway confirms that authorization succeeded, the app navigates directly to the receipt screen. If the transaction is confirmed absent, the app closes the stranded order and allows a clean retry. This guarantees that user frustration never translates into duplicate debits.""",
    "meta_ar": {
        "id": "PAY-08",
        "questionAr": "كيف تتجنب تكرار إرسال طلبات الدفع بعد انتهاء مهلة واجهة المستخدم (UI Timeout)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "الفصل المعماري بين مهلة الواجهة (UI Timeout) ومهلة الشبكة، قفل المعاملة في قاعدة البيانات لمنع النقر المكرر، توجيه إعادة المحاولة إلى الاستعلام (Status Inquiry) بدلاً من إعادة الخصم، وربط الواجهة بـ StateFlow.",
        "concept_ar": "يتطلب تجنب تكرار إرسال طلبات الدفع بعد انتهاء مهلة واجهة المستخدم (UI Timeout) فصلاً معمارياً صارماً بين ما يراه المستخدم على الشاشة ودورة حياة المعاملة على خادم البنك: عند تأخر الرد وظهور مؤشر التحميل لـ 15 ثانية، يقوم بعض المطورين بالخطأ بإلغاء الشاشة أو إعادة تفعيل زر الدفع (Pay Button)، مما يدفع المستخدم للنقر مجدداً بينما الطلب الأول لا يزال قيد المعالجة في البنك؛ فيتم الخصم مرتين! ولمنع ذلك نتبع 3 قواعد حاسمة: أولاً، إبقاء زر الدفع معطلاً بشكل دائم وعدم السماح بالنقر عليه مرة ثانية لنفس الفاتورة؛ ثانياً، تحويل الشاشة فور انتهاء المهلة إلى شاشة تحقق معلقة تفيد بجاري فحص حالة العملية مع البنك؛ ثالثاً، توجيه أي زر إعادة محاولة أو استئناف إلى مسار الاستعلام عن الحالة (Status Inquiry / Polling) بدلاً من طلب خصم جديد؛ حيث يفحص التطبيق الخادم بنفس مفتاح الحتمية الأصلي، فإذا كانت العملية مقبولة يعرض الإيصال مباشرة، ولا يُسمح بالدفع الجديد إلا بعد التأكد التام من أن المعاملة الأولى لم تُخصم ولم تسجل بنكياً.",
        "walkthrough_ar": """فصل مهلة الواجهة وتوجيه إعادة المحاولة للاستعلام عن الحالة في كوتلن:
```kotlin
class PaymentViewModel(
    private val paymentRepository: PaymentRepository,
    private val orderId: String
) : ViewModel() {

    private val _uiState = MutableStateFlow<PaymentUiState>(PaymentUiState.Idle)
    val uiState: StateFlow<PaymentUiState> = _uiState.asStateFlow()

    fun onPayClicked(amount: Long) {
        viewModelScope.launch {
            _uiState.value = PaymentUiState.Processing

            try {
                // مهلة بصرية للواجهة فقط دون قطع اتصال الخلفية
                withTimeout(15_000L) {
                    val result = paymentRepository.executePayment(orderId, amount)
                    _uiState.value = PaymentUiState.Success(result.authCode)
                }
            } catch (e: TimeoutCancellationException) {
                // انتهاء مهلة الشاشة: حظر زر الدفع والتحويل لشاشة التحقق
                _uiState.value = PaymentUiState.InDoubtCheckStatus
            }
        }
    }

    // إعادة المحاولة تستعلم عن العملية السابقة ولا ترسل طلب خصم جديد أبداً!
    fun onCheckStatusClicked() {
        viewModelScope.launch {
            _uiState.value = PaymentUiState.Processing
            val status = paymentRepository.queryPaymentStatus(orderId)
            _uiState.value = when (status) {
                is StatusResult.Approved -> PaymentUiState.Success(status.authCode)
                is StatusResult.NotFound -> PaymentUiState.SafeToRetry
                is StatusResult.Pending -> PaymentUiState.InDoubtCheckStatus
            }
        }
    }
}
```""",
        "why_it_matters_ar": "إعادة تفعيل زر الدفع بعد مهلة الشاشة هو السبب الأول لنقر المستخدم المتعجل وسحب المبلغ مرتين في ثوانٍ معدودة.",
        "worked_example_ar": "تأخر رد البنك 18 ثانية فظهرت رسالة مهلة بالشاشة؛ ظل زر الدفع معطلاً وظهر زر تحقق من العملية؛ وبنقره استعلم التطبيق فاكتشف قبول العملية وطبع الإيصال دون سحب مكرر.",
        "trade_offs_ar": "تحويل الشاشة للاستعلام يمنع المستخدم من الدفع الفوري لثوانٍ؛ لكنه يحميه من السحب المزدوج ويوفر على الشركة تكاليف شكاوى النزاع.",
        "failure_modes_ar": "أخطر الأخطاء هو إلغاء Coroutine Scope الشبكي عند انتهاء مهلة الواجهة؛ فإلغاء اتصال الهاتف لا يعني إلغاء العملية في البنك الذي قد يكون خصم الأموال بالفعل.",
        "production_perspective_ar": "في كود الإنتاج، ترتبط حالة الزر بجدول قاعدة البيانات محلياً؛ فلا يمكن فتح إمكانية الدفع طالما توجد عملية بحالة INITIATED لنفس السلة.",
        "how_to_answer_ar": "فرّق بوضوح بين مهلة الواجهة ومهلة الشبكة، واشرح خطورة إعادة تفعيل زر الدفع، ثم بين الحل عبر قفل الزر وتوجيه المحاولات للاستعلام Status Inquiry.",
        "talking_points_ar": "مهلة الواجهة UI Timeout، مهلة الشبكة Network Timeout، فخ النقر المكرر، تعطيل الزر الدائم، شاشة التحقق In-Doubt، واستعلام الحالة Status Inquiry.",
        "follow_ups_ar": "كيف تستخدم تقنية Polling مع Exponential Backoff للاستعلام التلقائي عن المعاملة بعد مهلة الواجهة دون تدخل المستخدم؟",
        "self_check_ar": "هل أكدت على إبقاء زر الدفع معطلاً، وفرقت بين مهلة الواجهة والخادم، وشرحت توجيه الزر للاستعلام بدلاً من الخصم مجدداً؟",
        "references_ar": f"- [Google Pay API: Integration Checklist and Error Handling](https://developers.google.com/pay/api/android/guides/test-and-deploy/integration-checklist) — الإرشادات الرسمية لشركة جوجل لتفادي المعاملات المزدوجة ومعالجة مهل الاتصال.\n- [Stripe Documentation: Handling incomplete and pending payments](https://docs.stripe.com/payments/handling-payment-outcomes) — الدليل المعماري لإدارة المعاملات المعلقة وتفادي السحب المكرر في تطبيقات الهواتف.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نتجنب تكرار طلبات الدفع بعد مهلة الواجهة بإبقاء زر الدفع معطلاً تماماً وعدم السماح بإرسال خصم جديد لنفس الطلب. وبدلاً من ذلك، نحول الشاشة إلى حالة تحقق معلقة توجه أي إعادة محاولة إلى الاستعلام عن حالة المعاملة لدى البنك، فإذا كانت العملية قد كُتبت بنجاح يُعرض الإيصال فوراً دون سحب مليم إضافي.""",
        "best_answer_ar": """يتطلب تجنب تكرار الدفع بعد انتهاء مهلة الواجهة فصلاً معمارياً دقيقاً بين ما تعرضه الشاشة وحقيقة ما يحدث في خوادم البنك.
عندما يتأخر الرد وتنتهي مهلة مؤشر التحميل في الواجهة، يقع كثير من المطورين في خطأ إعادة تفعيل زر الدفع ظناً منهم أن العملية فشلت، مما يدفع العميل للنقر مرة ثانية فيتم خصم المبلغ مرتين لأن الطلب الأول كان قيد التنفيذ بالبنك.
ولمنع هذا الخطر، تفرض المعمارية إبقاء زر الدفع معطلاً بشكل صارم بعد انتهاء المهلة، مع تحويل الشاشة إلى وضع التحقق المعلق لإعلام المستخدم بجاري مطابقة العملية مع البنك.
وعندما ينقر المستخدم على زر إعادة المحاولة، يُوجه الكود حصرياً إلى مسار الاستعلام عن الحالة باستخدام نفس مفتاح الحتمية ومعرّف الارتباط، بدلاً من إرسال طلب تفويض جديد.
فإذا أكد الخادم نجاح الخصم، تكتمل المعاملة ويُطبع الإيصال، ولا يُفتح باب الدفع الجديد إلا إذا أكد البنك رسمياً عدم وجود أي قيد مالي.""",
        "deep_answer_ar": """من منظور تنسيق الحالات الموزعة وتصميم تجربة المستخدم الموثوقة، يعالج الانضباط المعماري لمهل الواجهة الفجوة الخطيرة بين الإدراك البصري للمستخدم وحقيقة الاتصال الشبكي.
تخضع اتصالات الهاتف المحمول لتقلبات شديدة في زمن الاستجابة؛ فإذا حدد التطبيق مهلة بصرية قدرها خمس عشرة ثانية في كروت الـ Coroutines، فإن قطع النطاق محلياً لا يؤثر مطلقاً على حزمة البيانات التي عبرت خوادم بوابة الدفع وتنتظر الاعتماد المصرفي. وإذا عادت الشاشة للوراء مع تفعيل زر الدفع، فإن النقر التلقائي التالي يطلق معاملة مالية موازية تسبب سحباً مزدوجاً ونزاعاً مصرفياً معقداً.
والحل المعماري الرصين يبدأ بقفل المعاملة داخل قاعدة البيانات المحلية؛ حيث يُسجل الطلب كـ PROCESSING، وترتبط الشاشة بهذا التدفق، مما يمنع زر الدفع من استقبال أي نقرات جديدة.
وعند انتهاء مهلة الواجهة، تنتقل الشاشة لحالة الشك In-Doubt مع إبقاء زر الدفع مغلقاً تماماً، وتتحول وظيفة الواجهة من طلب الخصم إلى طلب الاستعلام عن الحالة.
يرسل زر التحقق استعلاماً عبر مسار GET مصحوباً بمفتاح الحتمية الأصلي؛ فإذا كان البنك قد أنهى العملية، تُسجل فوراً كـ APPROVED ويُعرض الإيصال المحاسبي. وإذا أكد البنك عدم استلام أي طلب بعد فترة سماح، تُغلق العملية الأولى بأمان ويُتاح للعميل الدفع مجدداً. هذا التتابع يمنع إحباط المستخدم من التحول إلى خسارة مالية مؤكدة."""
    }
}

# ==========================================
# Validation & Runner logic
# ==========================================
def validate_words():
    print("Checking word counts and spoken style for PAY-01 to PAY-08...")
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

    ee.save_topic_metadata("pay_01_08", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\nAll {len(DATA)} PAY questions (PAY-01 to PAY-08) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
