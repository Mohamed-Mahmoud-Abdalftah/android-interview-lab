#!/usr/bin/env python3
"""Canonical updates and Arabic metadata for AND-21 through AND-25."""

TOPIC_AR = "أساسيات أندرويد ودورة الحياة والسياق (Context)"

CANONICAL_DATA = {}
ARABIC_METADATA = {}

# ==============================================================================
# AND-21: A payment screen is killed by Android mid-operation. What must be reconstructed, and what must not be repeated?
# ==============================================================================
CANONICAL_DATA["AND-21"] = {
    "concept_en": """When a financial checkout or payment flow is abruptly killed by the operating system mid-operation (such as through background Low Memory Killer termination, configuration crashes, or battery death), the application enters an ambiguous state. In distributed systems, a lost client response must never be assumed to indicate that the remote transaction failed; the server may have successfully charged the customer's credit card and updated the ledger just as the client process died.
Engineering a resilient payment flow requires a strict division of responsibilities. What MUST NOT be repeated under any circumstance is the financial mutation call. Resubmitting an unverified payment charge blindly creates catastrophic duplicate billing, chargeback penalties, and severe customer distrust. What MUST be reconstructed is the user's transaction session, shopping cart summary, and durable transaction identifier. By generating a client-side UUID idempotency key before dispatching the payment and persisting it in local storage, the application can safely reconcile state with the backend upon process restoration by querying transaction status rather than issuing duplicate debits.""",

    "walkthrough_en": """Designing a resilient payment ViewModel backed by SavedStateHandle and durable repository synchronization:

```kotlin
class PaymentViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val paymentRepository: PaymentRepository
) : ViewModel() {

    // Reconstructed securely from SavedStateHandle:
    private val orderId: String = checkNotNull(savedStateHandle["order_id"])
    private val idempotencyKey: String = savedStateHandle.get<String>("idempotency_key")
        ?: UUID.randomUUID().toString().also { savedStateHandle["idempotency_key"] = it }

    private val _uiState = MutableStateFlow<PaymentUiState>(PaymentUiState.Loading)
    val uiState: StateFlow<PaymentUiState> = _uiState.asStateFlow()

    fun resumePaymentFlow() {
        viewModelScope.launch {
            // NEVER charge again blindly! Reconcile status first:
            val status = paymentRepository.checkTransactionStatus(orderId, idempotencyKey)
            when (status) {
                is TransactionStatus.Success -> _uiState.value = PaymentUiState.Success(status.receipt)
                is TransactionStatus.Pending -> _uiState.value = PaymentUiState.Processing
                is TransactionStatus.NotFound -> {
                    // Safe to initiate payment because server has not seen this idempotency key
                    executeCharge(orderId, idempotencyKey)
                }
                is TransactionStatus.Failed -> _uiState.value = PaymentUiState.Failed(status.error)
            }
        }
    }

    private suspend fun executeCharge(orderId: String, key: String) {
        // Execute charge with idempotency key attached
    }
}
```

Failure scenario: An app dispatches a payment request without an idempotency key. The user switches to their authenticator app, causing the OS to kill the payment process. Upon returning, the app detects an incomplete order and automatically triggers a fresh payment call, charging the customer's credit card twice for the exact same order.""",

    "short_en": """Never repeat the financial charge mutation blindly; an unreceived response does not prove payment failure. What must be reconstructed is the order ID, cart parameters, and a pre-generated client-side idempotency key preserved in SavedStateHandle and local database. Upon process restoration, query transaction status from the backend to reconcile state before allowing the user to retry.""",

    "structured_en": """To begin with, in financial transactions, a terminated process or lost network response represents an indeterminate outcome, never a confirmed failure. The payment gateway may have committed the charge just as the client was reclaimed by the operating system, meaning we must never re-trigger the charge mutation automatically.
From an architectural standpoint, we enforce idempotency by generating a unique client-side UUID idempotency key before initiating the transaction. This key, along with the order ID and amount, is persisted immediately to durable local storage like Room and mirrored into SavedStateHandle.
In production scenarios where the screen is recreated after process death, the ViewModel checks the transaction status against the backend using the order ID and idempotency key. If the server has already settled the charge, the UI transitions directly to the success confirmation screen. Only if the backend explicitly confirms the transaction was never received or failed safely do we enable a retry.
As for boundary management, user interface state like selected payment methods and form inputs are reconstructed cleanly from SavedStateHandle, while sensitive card details and CVV codes are never persisted locally, ensuring strict compliance with PCI-DSS security standards.""",

    "deep_senior_en": """From a distributed systems and fault-tolerance perspective, handling client death during payment processing is an instance of the Two Generals Problem. When a mobile client initiates an HTTP POST request to /api/v1/charge, several failure domains exist: the network may drop before reaching the server, the server may process the charge through payment processors like Stripe but fail before sending the response, or the Android Low Memory Killer (lmkd) may terminate the app process while the network connection is in flight. Assuming failure and re-executing the charge leads to duplicate card authorizations and chargeback disputes.
To build a bulletproof architecture, the client must generate an idempotency key before any network I/O occurs. This key is written synchronously to an encrypted local database table (Room with SQLCipher) alongside the order state marked as PENDING_AUTHORIZATION. The idempotency key is also injected into SavedStateHandle so that upon activity recreation, the ViewModelProvider restores the exact transaction context.
When the resurrected Activity initializes, the ViewModel enters a reconciliation state. It executes an idempotent status probe (such as GET /api/v1/orders/{orderId}/payment-status or passing the Idempotency-Key header). The backend payment service guarantees that identical idempotency keys yield identical responses without re-executing charges on payment rails. If the status returns SUCCEEDED, the client marks the local order as paid and navigates to the receipt screen. If the payment is still processing, the client subscribes to a WebSocket or polling mechanism with exponential backoff.
From a regulatory standpoint, PCI-DSS strictly prohibits persisting sensitive card verification values (CVV) or raw PANs in SavedStateHandle or local disk storage. Only tokenized payment tokens provided by the payment gateway SDK can be safely retained. By combining client-side idempotency, local transactional states, and server-driven reconciliation, the financial flow remains resilient against any unexpected process termination."""
}

ARABIC_METADATA["AND-21"] = {
    "id": "AND-21",
    "questionAr": "شاشة دفع تم إنهاؤها بواسطة أندرويد أثناء العملية: ما الذي يجب استعادته وما الذي لا يجب تكراره؟",
    "topicAr": TOPIC_AR,
    "evaluates_ar": """- التعامل مع فقدان استجابة العميل كحالة مجهولة النتيجة وليست دليلاً قاطعاً على فشل العملية.
- الفصل الدقيق بين حالة الواجهة القابلة للاسترجاع وبين معرّفات العمليات الدائمة ومفاتيح عدم التكرار (Idempotency).
- تصميم آلية تسوية واستعلام (Reconciliation Flow) قبل السماح للمستخدم بإعادة المحاولة.""",
    "why_it_matters_ar": "موت العملية أثناء تنفيذ العملية المالية يترك التطبيق في حالة غير محددة، لأن السيرفر قد يكون أتم الخصم بالفعل بينما تعطل العميل قبل استلام الرد. إعادة إرسال طلب الخصم تلقائياً عند إعادة فتح الشاشة يسبب كارثة سحب أموال العميل مرتين ومشاكل استرداد مالي (Chargebacks). المعمارية السليمة تتطلب حفظ معرّف العملية الفريد (Idempotency Key) محلياً قبل إرسال الطلب، واستخدامه للاستعلام عن حالة المعاملة عند إعادة إحياء العملية.",
    "worked_example_ar": """هندسة استعادة شاشة الدفع بعد موت العملية في ViewModel:
```kotlin
class PaymentViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val paymentRepository: PaymentRepository
) : ViewModel() {

    private val orderId: String = checkNotNull(savedStateHandle["order_id"])
    private val idempotencyKey: String = checkNotNull(savedStateHandle["idempotency_key"])

    fun resumePayment() {
        viewModelScope.launch {
            // الاستعلام أولاً والامتناع عن تكرار الخصم تلقائياً
            val status = paymentRepository.checkStatus(orderId, idempotencyKey)
            if (status.isSuccess) showReceipt() else allowManualRetry()
        }
    }
}
```""",
    "trade_offs_ar": "توليد Idempotency Key محلياً يضمن سلامة المعاملات لكنه يفرض على السيرفر تخزين هذه المفاتيح لفترة زمنية محددة. التحقق من حالة المعاملة عند كل استعادة يضيف استدعاء شبكة إضافي، لكنه الثمن الضروري لحماية المستخدم من الدفع المزدوج. وحفظ تفاصيل الدفع المؤقتة في SavedStateHandle آمن لمعرّفات الطلبات لكنه محظور تماماً لبيانات البطاقات البنكية الحساسة.",
    "failure_modes_ar": "إعادة تنفيذ كود الخصم فورياً في onCreate عند إعادة إحياء الشاشة يسحب قيمة الطلب مرتين من حساب العميل. تخزين أرقام البطاقات ورموز الـ CVV في SavedStateHandle ينتهك معايير أمان PCI-DSS ويعرض بيانات المستخدم للتسريب. افتراض أن انقطاع الاتصال يعني فشل العملية يضلل المستخدم ويجعله يكرر الدفع بنفسه. يتم التحقق باختبار قطع اتصال الشبكة في لحظة معالجة الدفع ومحاكاة موت العملية عبر adb.",
    "production_perspective_ar": "في تطبيقات التكنولوجيا المالية (FinTech)، يُولّد الـ Idempotency Key ويُحفظ في قاعدة بيانات Room المشفرة قبل إطلاق أي طلب شبكة. عند استعادة الشاشة بعد موت العملية، يدخل التطبيق في وضع Reconciliation للاستعلام عن حالة العملية من الخادم عبر Polling أو WebSockets. تُحظر تماماً كتابة أي بيانات بنكية خام في الذاكرة المؤقتة، وتُسجل كل محاولة استعادة في سجلات الأمان والتدقيق المالي.",
    "how_to_answer_ar": """- **السبب المالي:** وضح أن غياب الرد في الأنظمة الموزعة يمثل نتيجة غير مؤكدة وليس فشلاً.
- **طريقة الشرح:** حدد ما لا يجب تكراره نهائياً (طلب الخصم المالي) ثم ما يجب استعادته (معرّف الطلب ومفتاح عدم التكرار).
- **المفاضلات:** اشرح دور Idempotency Key والتسوية مع السيرفر بدلاً من التكرار الأعمى.
- **أنماط الفشل:** استشهد بالسحب المزدوج (Double Charge) وانتهاك قواعد PCI-DSS عند حفظ بيانات البطاقات.
- **الحل الإنتاجي:** وضح تخزين المفتاح في Room و SavedStateHandle واستعلام الخادم عند استعادة العملية.""",
    "talking_points_ar": "ناقش معضلة الجنرالين (Two Generals Problem) في معاملات الموبايل المالية، وآلية عمل ترويسة Idempotency-Key في بوابات الدفع العالمية مثل Stripe، وقواعد ومعايير PCI-DSS الخاصة بحظر تخزين رموز CVV محلياً، وكيفية تنظيم آلية الاستعلام الدوري (Exponential Backoff Polling) عند استعادة الشاشات.",
    "follow_ups_ar": """- **المحاور:** "كيف يمنع الـ Idempotency Key الخصم المزدوج في السيرفر؟"
  **المرشح:** "العميل بيولد UUID عشوائي ويبعته في الـ Header مع طلب الدفع. السيرفر بيسجل المفتاح ده في قاعدة بياناته أثناء معالجة الطلب؛ لو العميل كرر نفس الطلب بنفس الـ Key بسبب انقطاع الاتصال، السيرفر بيتعرف عليه فوراً ومبيخصمش الفلوس تاني، وبيرجع نفس نتيجة المعاملة الأولى المسجلة عنده."

- **المحاور:** "هل مسموح حفظ بيانات البطاقة في SavedStateHandle لتسهيل إعادة المحاولة؟"
  **المرشح:** "ممنوع تماماً ونهائياً وفقاً لمعايير PCI-DSS. أرقام البطاقات (PAN) ورموز الأمان (CVV) لا يجوز تخزينها في SavedStateHandle أو قواعد البيانات المحلية؛ لأن الـ Bundle بيتبعت لنظام التشغيل وممكن يتسرب في سجلات الذاكرة. إحنا بنحفظ فقط Tokens مشفرة ومؤقتة بيوفرها الـ Payment Gateway SDK." """,
    "self_check_ar": "احظر تكرار طلب الخصم تلقائياً؛ ولّد واحفظ Idempotency Key قبل إرسال الطلب؛ استعلم عن حالة العملية عند إعادة الإحياء؛ والتزم بمعايير PCI-DSS في حماية بيانات البطاقات.",
    "references_ar": """- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — استعادة الحالة في أندرويد.
- [Stripe API Idempotency](https://docs.stripe.com/api/idempotent_requests) — معايير منع تكرار المعاملات المالية.

تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.""",
    "quick_answer_ar": "المبدأ المالي الحاسم هو: إياك تكرر عملية الخصم المالي (Charge Call) نهائياً؛ لأن انقطاع الاتصال أو موت العملية مش معناه إن الدفع فشل. اللي لازم يرجع يتبني هو معرّف الطلب، وحالة الواجهة، والـ Idempotency Key اللي اتحفظ في SavedStateHandle وقاعدة البيانات. ولما الشاشة ترجع بنعمل Reconcile بالاستعلام عن حالة العملية من السيرفر قبل أي محاولة جديدة.",
    "best_answer_ar": """في الأنظمة المالية وتطبيقات الدفع، انقطاع العملية بسبب موت التطبيق في الخلفية (Process Death) بيمثل حالة نتيجتها مجهولة تماماً. السيرفر ممكن يكون خصم الفلوس من حساب العميل والرد تاه في الشبكة أو التطبيق مات قبل ما يستلمه.
علشان كده القاعدة الأولى: ممنوع تكرار طلب الخصم تلقائياً؛ لأن تكرار الخصم بيسحب فلوس مرتين ويدخل الشركة في مشاكل قانونية ونزاعات بنكية (Chargebacks).
اللي لازم نعيد بناءه فوراً هو: تفاصيل الطلب، وعناصر الواجهة، ومعرّف العملية الفريد (Idempotency Key).
المعمارية الصحيحة بتبدأ قبل إرسال طلب الدفع أصلاً؛ بننشئ UUID يمثل Idempotency Key ونحفظه مع الـ Order ID في قاعدة بيانات Room و SavedStateHandle.
لما التطبيق يرجع يفتح بعد الـ Process Death، الـ ViewModel مبيدوسش دفع من جديد؛ هو بيعمل استعلام (Status Check) من السيرفر بنفس الـ Idempotency Key. لو السيرفر أكد إن العملية نجحت بننقله لشاشة الإيصال فوراً؛ ولو العملية متعلقة بننتظر؛ ولو العملية مسجلتش نهائياً ساعتها بس بنسمح للمستخدم يدوس دفع بأمان.""",
    "deep_answer_ar": """المشكلة دي في هندسة البرمجيات والـ Distributed Systems هي تطبيق صريح لمعضلة الـ Two Generals Problem. العميل بعت طلب الخصم لـ Payment Gateway زي Stripe، وفي اللحظة دي الـ LMK في أندرويد بعت SIGKILL للعملية؛ هل الفلوس اتخصمت؟ مستحيل العميل يعرف بدون التحقق من السيرفر.
الحل المعماري الاحترافي بيتكون من 3 ركائز أساسية:
أولاً، الـ Idempotency Key: قبل ما نطلع بأي Network Request، الـ ViewModel بينشئ مفتاح فريد UUID وبيخزنه في قاعدة بيانات مشفرة محلية (Room) مع حالة الطلب PENDING، وبيحطه في SavedStateHandle. السيرفر والـ Payment Gateway بيستخدموا المفتاح ده بحيث لو استقبلوا نفس الـ Key مرتين، مبيخصموش الفلوس مرتين، وبيرجعوا نفس نتيجة المعاملة الأولى.
ثانياً، الـ Reconciliation Flow: أول ما الـ Activity يحصلها Recreate بعد موت العملية، الـ ViewModel بيقرأ الـ Idempotency Key ومعرّف الطلب، ويبعت طلب استعلام حصري GET على orders status. لو السيرفر رد بـ SUCCESS، بنعرض شاشة النجاح؛ لو رد بـ PENDING، بنفتح Polling أو WebSocket؛ ولو رد بـ NOT_FOUND، ساعتها بس بنظهر زرار الدفع للمستخدم من تاني.
ثالثاً، قيود الـ PCI-DSS Security: معمارياً ممنوع تماماً حفظ أرقام الكروت الكاملة (PAN) أو كود الـ CVV السري في SavedStateHandle أو أي Storage محلي لأنها هتتسرب في الـ Memory Dumps أو ملفات الـ OS. إحنا بنتعامل فقط مع Payment Tokens مؤقتة ومشفرة من الـ Gateway. بالتصميم ده بنضمن سلامة أموال المستخدمين وعدم تكرار الخصم مهما حصلت انهيارات للنظام."""
}

# ==============================================================================
# AND-22: A crash occurs only after backgrounding the app for several hours. How would you investigate lifecycle and process restoration?
# ==============================================================================
CANONICAL_DATA["AND-22"] = {
    "concept_en": """Crashes that occur exclusively after an application has remained in the background for extended periods are almost universally caused by unhandled background process death. When an app is placed in the background, its Linux process transitions to a cached state. Under system memory constraints, the Android Low Memory Killer daemon (lmkd) terminates the process without invoking onDestroy.
When the user subsequently relaunches the application from the Overview/Recents screen, the Android framework resurrects the process, invokes Application.onCreate(), and directly recreates the top Activity from the backstack, restoring its saved state via the savedInstanceState Bundle. However, all in-memory static variables, singletons, and non-retained caches that were initialized by antecedent screens in the task flow remain completely uninitialized (null). When the restored Activity attempts to access these assumed in-memory objects, it immediately crashes with a NullPointerException. Investigating and remediating this issue requires simulating process death in development environments, verifying state restoration pipelines, and enforcing durable repository architectures.""",

    "walkthrough_en": """Investigating and resolving process death crashes caused by uninitialized static singletons:

```kotlin
// ❌ Flawed implementation crashing after process death:
class OrderDetailsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Crash! AppSession was initialized by LoginActivity, which did not run upon restoration:
        val userId = AppSession.currentUser.id 
        loadOrder(userId)
    }
}

// ✅ Resilient architecture using SavedStateHandle and durable storage:
@HiltViewModel
class OrderDetailsViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle,
    private val userRepository: UserRepository,
    private val orderRepository: OrderRepository
) : ViewModel() {

    // Preserved across process death via SavedStateHandle:
    private val orderId: String = checkNotNull(savedStateHandle["order_id"])

    val uiState: StateFlow<OrderUiState> = userRepository.getUserIdFlow()
        .flatMapLatest { userId -> orderRepository.getOrderStream(userId, orderId) }
        .map { order -> OrderUiState.Success(order) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), OrderUiState.Loading)
}
```

Failure scenario: An e-commerce app stores the active user session and cart items in an in-memory singleton during checkout. When the user leaves the app in the background overnight, Android kills the process. Tapping the app the next morning restores CheckoutActivity, which immediately crashes with NullPointerException: AppSession.cart is null.""",

    "short_en": """Crashes occurring after hours in the background indicate unhandled process death by the Low Memory Killer. Android recreates the top Activity while all in-memory static singletons and non-retained ViewModels are lost. Reproduce the bug using adb shell am kill, pass stable identifiers through Intent extras and SavedStateHandle, and load data from local databases rather than assuming in-memory state.""",

    "structured_en": """To begin with, crashes that materialize only after an application has spent hours in the background are classic symptoms of unhandled process death. The Low Memory Killer terminates the cached Linux process to reclaim RAM, and when the user returns, Android attempts to resurrect the top Activity while all in-memory static caches and singletons are re-instantiated as null.
From an architectural standpoint, we reproduce this failure deterministically using developer tooling. We background the application and execute adb shell am kill with the package name, or enable Don't keep activities in Developer Options to stress state serialization boundaries. Inspecting logcat reveals whether the crash is a NullPointerException stemming from uninitialized memory.
In production scenarios, screens must never rely on preceding Activities to populate in-memory singletons. Every screen must be fully autonomous, receiving stable entity identifiers via Intent extras or SavedStateHandle, and retrieving fresh domain data directly from durable Room databases or reactive repositories.
As for boundary management, if a session token or essential user credential has expired during the extended background interval, the app must intercept navigation cleanly, redirecting the user to the authentication gateway rather than allowing an unauthenticated screen to crash.""",

    "deep_senior_en": """Under the hood, Android's process management is orchestrated by the ActivityManagerService and the Linux kernel's Low Memory Killer daemon (lmkd). When an application is moved to the background, its oom_score_adj is adjusted to cached priority (CACHED_APP, values 900 to 999). When system RAM drops below kernel watermarks, lmkd sends a SIGKILL signal to the process. Crucially, the operating system saves the task hierarchy and the serialized onSaveInstanceState Bundles in the system server process (ActivityTaskManagerService), while the entire heap and all static class variables in ART are wiped out.
When the user taps the app in Recents, Zygote forks a new process, the runtime calls Application.onCreate(), and ActivityTaskManager restores ONLY the top Activity that was visible, passing the saved Bundle to onCreate(savedInstanceState). Junior architectures often assume a linear navigation pipeline where Splash, Login, Home, and Details always run sequentially. In process restoration, DetailsActivity is created directly without Splash or Home ever executing. Any singleton like UserManager.currentUser that was initialized in an earlier screen will be null, resulting in an immediate crash.
To diagnose these failures in production, we analyze stack traces in Crashlytics. A key signature of process restoration crashes is a NullPointerException occurring on an internal screen within seconds of cold process initialization without antecedent breadcrumbs.
The architectural remedy requires three interventions: First, replace static singleton dependencies with Dependency Injection (Hilt) scoped to repositories. Second, store lightweight entity IDs in SavedStateHandle so the ViewModel can reload state independently. Third, establish an application-level session guard: if the app requires an authenticated session and the local token is missing or invalid upon cold restoration, the navigation router intercepts the launch and routes the task back to the Login gateway gracefully."""
}

ARABIC_METADATA["AND-22"] = {
    "id": "AND-22",
    "questionAr": "يحدث انهيار (Crash) فقط بعد ترك التطبيق في الخلفية لعدة ساعات: كيف تحقق في دورة الحياة واستعادة العملية؟",
    "topicAr": TOPIC_AR,
    "evaluates_ar": """- بناء فرضية موت العملية في الخلفية (Process Death) والتحقق منها دون افتراضات عشوائية.
- إعادة إنتاج استعادة العملية الباردة محلياً باستخدام أدوات النظام وفحص سجلات الانهيار.
- معالجة تبعات موت العملية معمارياً بالاعتماد على SavedStateHandle ومصادر البيانات الدائمة.""",
    "why_it_matters_ar": "النظام بيتحكم في عمر العمليات في الخلفية وينهيها عبر الـ Low Memory Killer عند نقص الذاكرة. حالة الـ Instance State المحفوظة بتستعيد معطيات الواجهة الخفيفة للشاشة العلوية فقط، لكنها لا تحتفظ بكائنات الذاكرة أو الـ Singletons. الـ ViewModel بيموت مع موت العملية ولا ينجو إلا من التدوير. الاعتماد على تهيئة البيانات في شاشات سابقة يسبب كراش فوري بـ NullPointerException عند إعادة إحياء الشاشة المستهدفة بمفردها.",
    "worked_example_ar": """التحقيق البرمجي والحل المعماري الآمن من موت العملية:
```kotlin
// ❌ كود يكرش حتماً بعد ساعات في الخلفية:
class OrderDetailsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // خطأ قاتل: الاعتماد على كائن في الذاكرة ملأته شاشة سابقة
        val user = AppSession.currentUser // null بعد موت العملية!
        render(user.name)
    }
}

// ✅ الحل باستخدام SavedStateHandle والـ Repository:
class OrderDetailsViewModel(
    private val savedState: SavedStateHandle,
    private val repo: OrderRepository
) : ViewModel() {
    val orderId: String = checkNotNull(savedState["order_id"])
    val orderState = repo.getOrder(orderId)
}
```""",
    "trade_offs_ar": "إعادة إنتاج الخطأ عبر قتل العملية بأمر adb يكشف عيوب المعمارية بسرعة، بينما اختبار التدوير وحده لا يختبر موت العملية لأن الـ ViewModel ينجو منه. حفظ البيانات الضخمة في SavedStateHandle يسبب مشاكل أداء وقد يرمي TransactionTooLargeException؛ الحل الأنسب هو حفظ المعرّفات الأولية فقط وقراءة باقي البيانات من Room.",
    "failure_modes_ar": "افتراض أن شاشات Splash أو Login ستعمل حتماً قبل الشاشات الداخلية يسبب كراش فوري بعد موت العملية. محاولة قراءة كائن Singleton تم مسحه من الذاكرة يرمي NullPointerException. إعادة تهيئة الجلسة بشكل خاطئ قد تفتح شاشات المستخدم بدون مصادقة أمنية صحيحة. يتم الفحص بتفعيل خيار Don't keep activities في إعدادات المطور وقتل العملية عبر adb shell am kill.",
    "production_perspective_ar": "في بيئات الإنتاج، تُحلل تقارير الانهيار في Crashlytics بالبحث عن انهيارات تبدأ فور تشغيل التطبيق على شاشات تفاصيل فرعية بدون سجل تنقل سابق. تُربط كل شاشة بمصادر بيانات دائمة ومستقلة، ويُبنى حارس توجيه (Session Router) يعيد توجيه المستخدم لشاشة تسجيل الدخول بنظافة إذا انتهت الجلسة في الخلفية، مع تغطية اختبارات استعادة الحالة آلياً في الـ CI.",
    "how_to_answer_ar": """- **السبب الهندسي:** وضح أن ترك التطبيق لساعات يؤدي حتماً لإنهاء عمليته بواسطة LMK، وأن النظام يعيد بناء الشاشة العلوية فقط.
- **طريقة الشرح:** اشرح آلية موت العملية، ثم خطوات التحقيق وإعادة الإنتاج عبر adb shell am kill.
- **المفاضلات:** فرّق بوضوح بين نجاة ViewModel من التدوير وفنائه التام في موت العملية.
- **أنماط الفشل:** استشهد بخطأ الاعتماد على Singletons الذاكرة المشتركة بين الشاشات.
- **الحل الإنتاجي:** بين استخدام SavedStateHandle لحفظ الـ IDs واستعادة البيانات من Room مع Session Guard.""",
    "talking_points_ar": "ناقش آلية عمل lmkd في نواة لينكس وقيم oom_score_adj للعمليات في الخلفية، ودور Zygote في إنشاء العملية الجديدة، ولماذا لا يعتبر ViewModelStore بديلاً عن SavedStateHandle، وكيف تكشف سجلات Crashlytics سيناريو الـ Process Restoration من فارق التوقيت وتتبع المكدس (Stack Trace).",
    "follow_ups_ar": """- **المحاور:** "كيف تعيد إنتاج هذا الانهيار على جهاز التطوير في ثوانٍ بدلاً من الانتظار لساعات؟"
  **المرشح:** "بنفتح التطبيق وندخل على شاشة التفاصيل، بعدين نضغط Home لنقل التطبيق للخلفية، ومن التيرمينال ننفذ الأمر: `adb shell am kill com.example.app`. بعد كده نفتح التطبيق تاني من الـ Recent Apps؛ النظام هيحاكي موت العملية ويعيد بناء الشاشة العلوية فقط، ولو في مشكلة في استعادة البيانات هيحصل الكراش فوراً."

- **المحاور:** "هل خيار Don't keep activities في إعدادات المطور يحاكي موت العملية بالكامل؟"
  **المرشح:** "لأ، هو بيدمر الـ Activity بمجرد الخروج منها لاختبار onSaveInstanceState والتدوير، لكنه مبيقتلش الـ Process ككل، وبالتالي كائنات الـ Static والـ Singletons والـ Application context بتفضل عايشة في الذاكرة. علشان كده أمر `am kill` أو تقليل حد العمليات بالخلفية لـ 'No background processes' هو المحاكي الدقيق لموت العملية." """,
    "self_check_ar": "حدد دور LMK في قتل العمليات الخلفية؛ أعد إنتاج العطل بأمر adb kill؛ امتنع عن الاعتماد على Singletons الذاكرة؛ واستخدم SavedStateHandle مع قاعدة بيانات دائمة.",
    "references_ar": """- [Processes and app lifecycle](https://developer.android.com/guide/components/activities/process-lifecycle) — دورات حياة العمليات وموتها في أندرويد.
- [Testing process death](https://developer.android.com/topic/libraries/architecture/saving-states#recreate-process) — محاكاة واختبار موت العملية.

تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.""",
    "quick_answer_ar": "الكراش اللي بيحصل بعد ساعات في الـ Background سببه بنسبة 99% هو موت العملية (Process Death) بواسطة الـ Low Memory Killer. النظام بيقتل العملية في الخلفية ولما المستخدم يرجع بيعيد بناء الشاشة الأخيرة فقط من الـ Backstack وبتكون كل الـ Singletons والكاش اللي في الذاكرة بـ null. بنحقق فيها عبر adb shell am kill وبنعالجها بالاعتماد على SavedStateHandle والـ Room.",
    "best_answer_ar": """لما التطبيق يفضل ساعات في الخلفية ويكرش أول ما المستخدم يفتحه، ده العرض الكلاسيكي لموت العملية غير المعالج (Unmanaged Process Death).
اللي بيحصل في كواليس النظام هو إن أندرويد لما بيحتاج ذاكرة لتطبيقات تانية، الـ Low Memory Killer بيقتل عملية تطبيقك تماماً من غير ما يستدعي onDestroy.
ولما المستخدم يرجع يفتح التطبيق من الـ Recent Apps، أندرويد بيعمل حركة خادعة: بينشئ العملية من الصفر، وبيستدعي Application.onCreate، وبعدين يعيد بناء الشاشة الأخيرة اللي المستخدم كان واقف عليها مباشرة ممرراً لها الـ savedInstanceState، من غير ما يعدي على شاشات الـ Splash أو الـ Login أو الشاشات السابقة!
لو المطور باني كوده على افتراض إن الشاشات السابقة اشتغلت وملت بيانات في كائن Singleton أو متغير static، المتغيرات دي هتكون null وهيحصل NullPointerException فوري.
طريقة التحقيق الصحيحة هي محاكاة موت العملية بالأمر:
adb shell am kill مع اسم الحزمة.
والحل المعماري هو إن كل شاشة تكون مستقلة بذاتها؛ تاخد الـ ID بتاعها من الـ SavedStateHandle، وتقرأ بياناتها الحقيقية من قاعدة بيانات Room أو الـ Repository.""",
    "deep_answer_ar": """على مستوى نواة لينكس والـ ART Runtime، لما التطبيق بيدخل في الـ Background، الـ ActivityManagerService بينزل أولوية العملية لقائمة الـ Cached Processes وبيرفع الـ oom_score_adj لأعلى من 900. تحت ضغط الذاكرة، الـ Low Memory Killer daemon بيبعت إشارة SIGKILL للعملية، فبتتمسح مساحة الـ Heap بالكامل بكل المتغيرات الـ static والـ ViewModels، بينما النظام بيحتفظ فقط بسجل الـ Tasks والـ Bundles بتاعة onSaveInstanceState داخل عملية الـ System Server.
الكارثة المعمارية بتحصل لما المستخدم يرجع؛ النظام بيعمل Fork لعملية جديدة عبر Zygote، وبدل ما يبدأ التطبيق من نقطة البداية، بيفتح الشاشة الأخيرة اللي كانت ظاهرة فوراً ويستدعي onCreate(savedInstanceState). المطورين اللي بيعتمدوا على الـ In-Memory State زي AppSession.currentUser أو GlobalDataHolder بيتفاجئوا إن الكائنات دي كلها رجعت للـ default state بتاعتها وهي null؛ لأن شاشة الـ Login أو الشاشات التمهيدية متنفذتش أصلاً في العملية الجديدة!
علشان نحقق في المشاكل دي في الـ Production، بنبص في تقارير Crashlytics على وقت حدوث الكراش مقارنة بوقت الـ App Start؛ لو لقينا الـ Crash حاصل بعد ثوانٍ معدودة من الـ Cold Start على شاشة تفاصيل فرعية وبسبب NullPointer لكائن كاش، ده دليل قاطع على Process Death Crash.
الحل الجذري بيتطلب تطبيق قواعد الـ Staff Architecture:
أولاً، التخلص التام من أي State موجودة في متغيرات static أو Singletons في الذاكرة.
ثانياً، الاعتماد الكامل على SavedStateHandle لحفظ الـ Primitive IDs زي orderId.
ثالثاً، الـ ViewModel يطلب البيانات من الـ Repository اللي بدوره بيقراها من قاعدة بيانات Room المحلية الدائمة.
رابعاً، بناء Session Gate في الـ Navigation؛ لو الجلسة انتهت أثناء ساعات الانتظار في الخلفية، التطبيق يعيد توجيه المستخدم لشاشة تسجيل الدخول بنظافة بدلاً من الكراش."""
}

# ==============================================================================
# AND-23: A Singleton needs a Context. How do you choose the correct lifecycle and prevent a leak?
# ==============================================================================
CANONICAL_DATA["AND-23"] = {
    "concept_en": """In modern Android architecture, classes with a Singleton lifecycle exist in the Java/ART heap for the entire duration of the hosting Linux process. If a Singleton retains a direct or indirect reference to an Activity context, a severe memory leak occurs. When the Activity is destroyed due to screen rotation, configuration changes, or back navigation, the garbage collector cannot reclaim it because the Singleton's strong reference keeps the entire Activity reachable from a Garbage Collection (GC) Root. This retains the Activity, its complete View hierarchy, Drawables, Bitmaps, and window references, consuming tens or hundreds of megabytes of heap memory.
Preventing memory leaks while providing system capabilities to singletons requires strict adherence to context hierarchies. First, evaluate whether the singleton genuinely needs a Context instance at all, or whether it requires a more granular, non-contextual dependency such as a storage directory (File) or a specific system service (NotificationManagerCompat). Second, if a context is genuinely required (for instance, to register application-wide receivers or access database files), the singleton must exclusively hold the ApplicationContext via context.applicationContext. Because the Application object's lifecycle is identical to the process lifetime, retaining it within a singleton introduces zero leakage risk.""",

    "walkthrough_en": """Designing leak-proof singletons with Hilt and Kotlin:

```kotlin
// ❌ Catastrophic design: Leaks the Activity forever if an Activity context is passed:
class BadAnalyticsTracker(private val context: Context) {
    companion object {
        var instance: BadAnalyticsTracker? = null
    }
}

// ✅ 100% Leak-proof design using Application Context and Hilt:
@Singleton
class SafeAnalyticsTracker @Inject constructor(
    @ApplicationContext private val context: Context
) {
    // Alternatively, inject the specific narrower capability:
    private val appVersion: String = context.packageManager
        .getPackageInfo(context.packageName, 0).versionName
}
```

Failure scenario: A networking singleton retains an Activity context passed during initialization in MainActivity.onCreate(). The user rotates their phone ten times. Each rotation destroys the previous Activity and creates a new one, but all ten destroyed Activity instances remain pinned in memory by the singleton, rapidly causing an OutOfMemoryError crash.""",

    "short_en": """A singleton lives as long as the process, so it must never hold an Activity context, which would leak the entire View hierarchy and window resources upon recreation. Always provide the Application Context using context.applicationContext or Hilt's @ApplicationContext. Better yet, challenge the requirement and inject only the specific dependency needed, like a File directory or a system service.""",

    "structured_en": """To begin with, a Singleton persists in memory for the entire lifetime of the application process. Passing an Activity context to a singleton creates an immediate memory leak, because when the Activity is destroyed during screen rotation or navigation, the singleton's strong reference prevents the garbage collector from reclaiming the Activity and its view hierarchy.
From an architectural standpoint, whenever a singleton genuinely requires framework access, it must exclusively retain the ApplicationContext. Because the Application object shares the exact same lifecycle as the hosting process, retaining it introduces zero memory leak overhead.
In production scenarios utilizing dependency injection frameworks like Hilt or Dagger, we enforce this boundary using @ApplicationContext. This guarantees at compile-time that no short-lived visual context is injected into process-scoped components, safeguarding against accidental regressions by team members.
As for boundary management, the cleanest architectural approach is often to avoid injecting Context altogether. By decomposing requirements into narrower abstractions—such as injecting a cache directory File, a DataStore instance, or a specific system service like ConnectivityManager—we eliminate unnecessary framework coupling and simplify unit testing on the JVM.""",

    "deep_senior_en": """Under the hood, memory leaks in the Android Runtime (ART) are traced through the GC Root reference graph. A Singleton is typically held by a static field on a class loaded by the PathClassLoader. Static references are treated as permanent GC Roots. When an Activity context is passed into a singleton's constructor and stored in an instance field, a reference chain is established: GC Root -> Class -> Singleton -> Activity.
When the user rotates the device or finishes the Activity, ActivityManagerService instructs ActivityThread to invoke onDestroy. However, the Garbage Collector cannot collect the Activity because it remains strongly reachable from the static GC Root. Even worse, an Activity instance maintains an internal mWindow reference to PhoneWindow, which holds the DecorView, which in turn retains the entire hierarchical tree of View and ViewGroup objects, along with hardware bitmapped canvases and native allocations. In an app with rich layouts, leaking two or three Activity instances can waste 80 to 150 megabytes of heap memory, triggering frequent concurrent GC pauses and ultimately causing an OutOfMemoryError.
To diagnose and verify context hygiene, we integrate LeakCanary in debug builds and utilize Android Studio's Memory Profiler. In heap dumps, an Activity leak appears with a shortest path to GC Root pointing directly to the Singleton's backing field.
However, developers must also understand the functional limitations of ApplicationContext. While safe for singletons, ApplicationContext is not a visual context: it lacks a WindowToken and is not attached to theme attributes. Attempting to use ApplicationContext to inflate themed views, display an AlertDialog, or launch activities without FLAG_ACTIVITY_NEW_TASK will result in visual glitches or a fatal BadTokenException. Therefore, architectural boundaries must be explicit: use ApplicationContext for process-scoped data managers and singletons, and use ActivityContext strictly for scoped UI rendering."""
}

ARABIC_METADATA["AND-23"] = {
    "id": "AND-23",
    "questionAr": "كائن Singleton يحتاج إلى سياق (Context): كيف تختار دورة الحياة الصحيحة وتمنع تسريب الذاكرة؟",
    "topicAr": TOPIC_AR,
    "evaluates_ar": """- التشكيك في ضرورة حقن كائن Context كامل في Singleton والبحث عن بدائل أدق وأضيق نطاقاً.
- مطابقة اعتمادية عمر العملية (Process Lifetime) مع Application Context وتجنب مراجع الـ Activity.
- تشخيص تسريبات الـ Activity في مكدس الذاكرة وفهم حدود Application Context غير البصرية.""",
    "why_it_matters_ar": "كائن الـ Singleton بيفضل حياً في الذاكرة طوال فترة تشغيل العملية. أي مرجع لـ Activity مخزن جواه بيفضل ممسوكاً ويمنع الـ Garbage Collector من تحرير الشاشة حتى بعد إغلاقها وتدميرها. الـ Application Context بيمتلك دورة حياة متطابقة مع عمر العملية وبالتالي هو الخيار الآمن للاحتفاظ به، بينما مراجع الشاشات والـ Views لازم تتحرر فور انتهاء دورة حياتها.",
    "worked_example_ar": """كتابة Singleton آمن بنسبة 100% باستخدام Hilt و Application Context:
```kotlin
@Singleton
class SafeAnalyticsTracker @Inject constructor(
    @ApplicationContext private val context: Context
) {
    // آمن تماماً لأن Application Context يعيش بعمر العملية
    private val appVersion: String = context.packageManager
        .getPackageInfo(context.packageName, 0).versionName
}
```
أو الأفضل هندسياً: حقن المورد المحدد فقط (مثل `File(context.cacheDir, "analytics")`).""",
    "trade_offs_ar": "استخدام Application Context يحل مشكلة تسريب الذاكرة في الـ Singletons تماماً، لكنه لا يصلح لعرض الـ Dialogs أو تضخيم واجهات معتمدة على ثيم مخصص لغياب الـ Window Token. تمرير مراجع مجردة كالمسارات والواجهات يبسط كتابة اختبارات الـ JVM Unit Tests، بينما حقن Context في كل مكان يزيد الارتباط مع الـ Framework.",
    "failure_modes_ar": "تخزين Activity في كائن Singleton يؤدي لتسريب شجرة الـ Views والـ Bitmaps وموارد النافذة مع كل تدوير للشاشة حتى نفاد الذاكرة بـ OutOfMemoryError. استخدام Application Context لفتح Dialog يرمي فورا خطأ BadTokenException. محاولة بدء Activity من Application Context بدون راية FLAG_ACTIVITY_NEW_TASK تفشل برمي استثناء في أندرويد. يتم كشف التسريب عبر LeakCanary وفحص مسار مراجع GC Roots.",
    "production_perspective_ar": "في التطبيقات الضخمة، بنستخدم Hilt مع تعيين @ApplicationContext بشكل صارم في الموديولات ذات النطاق العام @Singleton. بنمنع حقن الـ Context في طبقات الـ Domain والـ Business Logic تماماً، وبنستبدله بواجهات نظيفة. بنفحص تراكم كائنات الـ Activity في الـ Heap دورياً عبر اختبارات الأداء لضمان خلو التطبيق من التسريبات قبل إطلاق التحديثات.",
    "how_to_answer_ar": """- **السبب الهندسي:** وضح أن عمر الـ Singleton يطابق عمر العملية وأن احتجاز مرجع قصير الأجل كـ Activity يسرب الذاكرة.
- **طريقة الشرح:** ابدأ بالقاعدة الذهبية (استخدام Application Context حصراً)، ثم اقترح الحل الأعمق وهو حقن الإمكانية المطلوبة فقط.
- **المفاضلات:** اشرح متى يصلح Application Context ومتى يفشل لغياب الـ Window Token والثيم.
- **أنماط الفشل:** استشهد بتسريب الـ DecorView والـ Bitmaps وخطأ BadTokenException.
- **الحل الإنتاجي:** وضح استخدام @ApplicationContext مع Hilt وفحص التسريبات عبر LeakCanary.""",
    "talking_points_ar": "ناقش كيف تبني ART مسارات المراجع من الـ GC Roots للـ Static Variables، والمساحة المهولة التي تحجزها PhoneWindow و DecorView في الـ Native Heap، ولماذا لا يعتبر WeakReference حلاً هندسياً سليماً لمشاكل المعمارية، وحدود استخدام ContextWrapper في نظام أندرويد.",
    "follow_ups_ar": """- **المحاور:** "هل استخدام WeakReference لمرجع الـ Activity جوه الـ Singleton حل مناسب لتفادي التسريب؟"
  **المرشح:** "لأ، ده يعتبر Anti-pattern وحل ترقيعي مش سليم هندسياً. الـ WeakReference بيخلي الـ Activity تتنظف من الذاكرة آه، لكن الـ Singleton ممكن في أي لحظة يلاقي المرجع بقى null ويرمي مشاكل في كود الأعمال لو حاول يستدعيه بعد تدمير الشاشة. المعمارية الصح هي إن الـ Singleton ميعرفش أي حاجة عن الـ Activity ويستخدم Application Context أو أحداث Event Bus."

- **المحاور:** "ليه مينفعش نستخدم Application Context لعرض AlertDialog؟"
  **المرشح:** "لأن الـ Dialog بيحتاج Window Token مسجل في WindowManagerService للربط مع نافذة مرسومة بالفعل على الشاشة؛ والـ Application Context معندوش Window Token ولا هو Visual Context مربوط بالـ Theme بتاع الـ Activity، وبالتالي النظام هيرمي خطأ BadTokenException فورا." """,
    "self_check_ar": "احظر تمرير Activity لـ Singleton؛ استخدم Application Context عبر context.applicationContext؛ فضل حقن الموارد المحددة بدلاً من كائن Context؛ وافحص الذاكرة بأداة LeakCanary.",
    "references_ar": """- [Context in Android](https://developer.android.com/reference/android/content/Context) — توثيق كلاس Context وأنواعه.
- [Hilt qualifiers](https://developer.android.com/training/dependency-injection/hilt-android#component-default-bindings) — استخدام @ApplicationContext في Hilt.

تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.""",
    "quick_answer_ar": "الـ Singleton بيعيش في الذاكرة بعمر الـ Process كلها، وبالتالي إياك تمرر له Activity Context لأن ده هيسرب الشاشة والـ Views والـ Bitmaps في الذاكرة للأبد عند التدوير. الحل هو تمرير Application Context حصراً عبر context.applicationContext أو @ApplicationContext في Hilt، والأفضل هندسياً حقن الخدمة أو مسار الملف اللي محتاجه فقط بدون كائن Context كامل.",
    "best_answer_ar": """الـ Singleton كائن بيعيش في الـ Heap طوال فترة حياة العملية (Process Lifetime)، وبالتالي هو مربوط بـ GC Root دائم لا يمكن حذفه.
لو مررت لـ Singleton مرجع لـ Activity Context وخزنته جواه، فأنت عملت أكبر تسريب ذاكرة كلاسيكي في أندرويد؛ لأن المستخدم أول ما يدور الشاشة، الـ Activity المفروض تتدمر والـ GC يمسحها، لكن وجود مرجع ليها جوه الـ Singleton هيمنع مسحها تماماً.
ومع كل تدوير للشاشة، هتتسرب نسخة Activity جديدة بشجرة الـ Views والـ Drawables والـ Bitmaps بتاعتها، والتطبيق هيوصل لـ OutOfMemoryError في دقايق.
القاعدة الصارمة: الـ Singleton لو محتاج Context يبقى لازم وبشكل قاطع ياخد Application Context فقط؛ لأن كائن الـ Application هو كمان بيعيش بعمر الـ Process كلها، فمفيش أي تعارض في دورات الحياة.
وفي مشاريع الإنتاج اللي بنستخدم فيها Hilt، بنحقن @ApplicationContext private val context: Context، أو الأفضل من كده إننا نسأل نفسنا: هل الـ Singleton محتاج Context أصلاً؟ لو محتاج مجلد كاش، نحقن له كائن File، ولو محتاج خدمة نظام، نحقن له NotificationManager مباشرة، وده بيبسط الاختبارات ويعزل الكود عن الـ Framework.""",
    "deep_answer_ar": """على مستوى الـ ART Garbage Collector والذاكرة، الـ Singleton بيكون ممسوك بـ Static Reference في كلاس محمل بالـ PathClassLoader، والـ Static Variables بتعتبر GC Roots دائمة. لما بتخزن Activity جوه الـ Singleton، بيتكون Reference Chain من:
GC Root للـ Singleton للـ Activity للـ PhoneWindow للـ DecorView للـ View Hierarchy.
الـ Root View ده ماسك كل عناصر الواجهة، ومصفوفات الـ Bitmaps، والـ Hardware Canvases، والـ Native Graphics Allocations في الـ C++ Heap. تسريب شاشتين تلاتة بالشكل ده كفيل يحجز أكتر من 100 ميجابايت ويخلي الـ Garbage Collector يشتغل في Stop-the-world pauses مستمرة تسبب تجميد الفريمات، وتنهي برمي OutOfMemoryError.
لكن كمهندس Staff، لازم تنبه الفريق للفرق بين الأمان من التسريب وبين الصلاحية الوظيفية للـ Context. الـ Application Context آمن بنسبة 100% مع الـ Singletons، لكنه مش Visual Context؛ يعني معندوش WindowToken ومش مربوط بالـ Theme الخاص بالشاشة. لو حاولت تستخدم Application Context علشان تعمل تضخيم لـ Layout، الألوان والـ Styles الخاصة بالـ Theme مش هتتطبق وهياخد الـ System Default Theme، ولو حاولت تفتح بيه AlertDialog، التطبيق هيرمي Crash فوري بـ BadTokenException لأن مفيش Window Token مسجل في الـ WindowManagerService.
علشان كده في الـ Clean Architecture، بنفصل الحدود بصرامة:
الـ Singletons ومستودعات البيانات بتاخد @ApplicationContext أو الأفضل تجريدها تماماً وحقن الواجهات البرمجية المحددة زي DataStore أو مسار File.
بينما الـ Visual Operations والـ Dialogs بتفضل مقيدة حصراً بـ Activity Context داخل طبقة الواجهة."""
}

# ==============================================================================
# AND-24: Your app receives an untrusted deep link. What validation should happen before navigation?
# ==============================================================================
CANONICAL_DATA["AND-24"] = {
    "concept_en": """Deep links and universal App Links bridge external web pages, emails, and third-party messaging apps into an application's internal navigation stack. Because incoming URIs and Intent extras originate outside the application's security boundary, they must be treated as completely untrusted input. Malicious actors frequently exploit unvalidated deep links to execute path traversal attacks, trigger arbitrary internal screen navigation (bypassing authentication or payment gates), manipulate query parameters, or abuse open redirectors to phish credentials.
Securing deep link navigation requires a comprehensive validation pipeline across multiple architectural checkpoints. First, apps should prioritize verified Android App Links (https scheme) configured with Digital Asset Links (.well-known/assetlinks.json) over custom URI schemes (myapp://), which lack domain verification and can be hijacked by malicious third-party apps on the same device. Second, the incoming URI must be rigorously parsed against an explicit allowlist of supported schemes, hosts, and paths. Third, all query parameters must undergo strict type validation and regex sanitization to block path traversal sequences (such as ../). Fourth, incoming routes targeting protected resources must be gated behind an authentication and authorization layer, ensuring that unauthenticated users are intercepted and redirected to a login flow before accessing sensitive destinations.""",

    "walkthrough_en": """Implementing a secure, layered deep link validation gateway before dispatching navigation:

```kotlin
class DeepLinkHandler {
    fun parseAndValidate(uri: Uri?, session: UserSession): NavigationTarget? {
        if (uri == null) return null

        // 1. Enforce strict Scheme and Host allowlist:
        if (uri.scheme != "https" || uri.host != "app.mycompany.com") {
            return null
        }

        // 2. Validate Path and sanitize parameters:
        val segments = uri.pathSegments
        return when {
            segments.size == 2 && segments[0] == "product" -> {
                val productId = segments[1]
                // Ensure ID is alphanumeric, preventing injection or traversal:
                if (productId.matches(Regex("^[a-zA-Z0-9_-]{1,32}$"))) {
                    NavigationTarget.ProductDetails(productId)
                } else null
            }

            segments.size == 1 && segments[0] == "checkout" -> {
                // 3. Authorization check before navigation:
                if (session.isAuthenticated) {
                    NavigationTarget.Checkout
                } else {
                    NavigationTarget.Login(returnTarget = NavigationTarget.Checkout)
                }
            }

            else -> null // Reject unrecognized paths
        }
    }
}
```

Failure scenario: A deep link handler accepts myapp://webview?url=... without domain validation. An attacker sends a malicious SMS containing myapp://webview?url=https://phishing-login.com. When tapped, the app opens the internal WebView displaying the attacker's phishing site within the trusted application frame, tricking the user into revealing sensitive banking credentials.""",

    "short_en": """Treat every external deep link as untrusted input. Validate scheme and host against strict allowlists, and prefer verified Android App Links with Digital Asset Links over custom schemes to prevent intent hijacking. Sanitize all path parameters to prevent injection or directory traversal, and route sensitive destinations through an authentication gate to enforce active session verification.""",

    "structured_en": """To begin with, every incoming deep link originates outside the application boundary and must be treated as untrusted user input. We prioritize verified Android App Links using HTTPS and Digital Asset Links over custom URI schemes, preventing rogue applications installed on the device from intercepting our traffic via intent filter collisions.
From an architectural standpoint, the deep link ingress must pass through a centralized validation gateway before invoking navigation. The router matches incoming URIs against a strict allowlist of recognized schemes, domain hosts, and path patterns, instantly dropping unknown or malformed URIs.
In production scenarios, path and query parameters require rigorous sanitization. We parse parameters into strongly typed domain models, enforcing alphanumeric regex constraints to prevent SQL injection, cross-site scripting in WebViews, and directory traversal sequences like ../.
As for boundary management, access to sensitive destinations like account settings or checkout must be gated behind authentication guards. If an incoming link targets a protected screen while the user session is expired or unauthenticated, the router halts navigation, redirects to the login gateway, and caches the validated destination to resume navigation post-authentication.""",

    "deep_senior_en": """From a security engineering perspective, deep link vulnerabilities are among the most exploited vectors on mobile platforms. Custom URI schemes like myapp:// offer zero cryptographic ownership; any application on the device can declare an identical scheme in its manifest, leading to Intent Ambiguity dialogs or silent traffic hijacking. To establish verifiable identity, enterprise applications implement Android App Links, where the operating system's PackageManager verifies domain ownership during app installation by fetching assetlinks.json from the HTTPS domain and matching the SHA-256 fingerprint of the APK's release signing key.
Within the application, deep link handling must adhere to strict defensiveness against Open Redirects and Confused Deputy attacks. A notorious vulnerability pattern occurs when an exported activity takes a url query parameter and loads it directly into an internal WebView that has JavaScript and file access enabled. An external link loading a file URI can exfiltrate local SQLite databases. Our routing engine enforces that all WebView URLs match an explicit domain allowlist with strict subdomain validation.
Furthermore, navigation routing must never couple directly to raw framework Intent objects or Uri strings. In modern Jetpack Compose or Fragment architectures, the ingress Activity parses the raw URI, validates the structure, and maps it into a type-safe navigation destination using Kotlinx Serialization.
Finally, session state verification must occur in the Domain layer, not merely in UI navigation guards. If a deep link opens an order route, the UI destination must not assume user ownership of that order. When the repository fetches the resource, the backend API must validate that the authenticated bearer token owns the requested record, returning an HTTP 403 Forbidden if an attacker attempts horizontal privilege escalation by guessing sequential order identifiers."""
}

ARABIC_METADATA["AND-24"] = {
    "id": "AND-24",
    "questionAr": "تطبيقك استقبل رابطاً عميقاً (Deep Link) غير موثوق: ما هي عمليات التحقق المطلوبة قبل التنقل؟",
    "topicAr": TOPIC_AR,
    "evaluates_ar": """- التعامل مع كل URI ومعطيات Intent خارجية كمدخلات غير موثوقة حتى مع استخدام App Links موثقة.
- التحقق من شكل المسار (Route Shape) وتطهير المعرّفات قبل تمريرها لطبقة الملاحة.
- فحص جلسة المصادقة وصلاحيات الوصول قبل عرض الشاشات المحمية وحسابات المستخدمين.""",
    "why_it_matters_ar": "الـ Activity المخصصة لاستقبال الروابط بتستقبل Intent بيحمل URI تم تشكيله بالكامل خارج حدود التطبيق. فلاتر الـ Manifest والـ App Links الموثقة بتربط الدومين بالتطبيق لكنها لا تضمن أن المعطيات آمنة أو أن المستخدم مصرح له بالوصول للبيانات المستهدفة. فتح الشاشات مباشرة بالاعتماد على معطيات الرابط يفتح ثغرات أمنية خطيرة تشمل تجاوز المصادقة (Auth Bypass) واختراق الـ WebViews وثغرات Open Redirect.",
    "worked_example_ar": """تنفيذ معالج Deep Link آمن ومفحوص:
```kotlin
class DeepLinkHandler {
    fun parseAndValidate(uri: Uri?, session: UserSession): NavigationTarget? {
        if (uri == null) return null
        // 1. التحقق من الدومين والبروتوكول عبر Whitelist
        if (uri.scheme != "https" || uri.host != "app.mycompany.com") return null
        
        val segments = uri.pathSegments
        return when {
            segments.size == 2 && segments[0] == "product" -> {
                val id = segments[1]
                if (id.matches(Regex("^[a-zA-Z0-9_-]+$"))) NavigationTarget.Product(id) else null
            }
            segments.size == 1 && segments[0] == "orders" -> {
                // 2. التحقق من جلسة المستخدم قبل فتح الشاشة المحمية
                if (session.isLoggedIn) NavigationTarget.Orders else NavigationTarget.Login
            }
            else -> null
        }
    }
}
```""",
    "trade_offs_ar": "قصر الروابط على قائمة بيضاء صارمة يمنع مرونة إضافة صفحات جديدة ديناميكياً بدون تحديث التطبيق، لكنه يوفر حماية أمنية لا غنى عنها. الـ Android App Links الموثقة تتطلب إعداد ملف assetlinks.json على السيرفر لكنها تمنع ظهور نافذة التخيير وتمنع سرقة الروابط بواسطة تطبيقات خبيثة تستخدم Custom Schemes.",
    "failure_modes_ar": "تمرير باراميتر رابط خارجي مباشرة لـ WebView يفتح ثغرة Open Redirect وسرقة ملفات التطبيق الحساسة. الاعتماد على معرف الحساب المبعوث في الرابط دون مطابقة توكن المستخدم في السيرفر يفتح ثغرة Horizontal Privilege Escalation. الروابط الموجهة لمسارات غير معروفة تسبب كراش فوري لو لم تتم معالجتها بحالة افتراضية آمنة. يتم الفحص بمحاكاة روابط خبيثة ومحاولات حقن كود عبر adb shell am start.",
    "production_perspective_ar": "في تطبيقات المؤسسات، بنستخدم Deep Link Router مركزي بيفحص كل الروابط قبل تسليمها للـ Navigation Component. بنحول الـ URI لـ Type-Safe Navigation Target عبر Kotlin Serialization، وبنمنع تحميل الروابط الخارجية في الـ WebViews إلا بعد مطابقة الدومين الموثوق. بنسجل محاولات الروابط المشبوهة في سجلات الـ Security Monitoring مع حجب أي بيانات شخصية.",
    "how_to_answer_ar": """- **السبب الأمني:** وضح أن الروابط العميقة هي نقطة اختراق شائعة لأنها مدخل خارجي غير مفحوص.
- **طريقة الشرح:** ابدأ بالتحقق من الـ Scheme والـ Host، ثم تطهير الـ Parameters، وأخيراً فحص الـ Auth Gate.
- **المفاضلات:** قارن بين أمان App Links الرسمية وبين عيوب الـ Custom Schemes غير الموثقة.
- **أنماط الفشل:** استشهد بثغرات Open Redirect وتجاوز شاشات الدفع وتسريب ملفات الـ WebView.
- **الحل الإنتاجي:** وضح التوجيه المركزي عبر Type-Safe Routes ومطابقة ملكية البيانات في السيرفر.""",
    "talking_points_ar": "ناقش آلية التحقق من Digital Asset Links عبر PackageManager عند تثبيت التطبيق، وكيفية حماية الـ WebViews من ثغرات file scheme و JavaScript Injection، ودور Type-Safe Navigation في Compose، ولماذا يجب أن تكون سلطة حماية الموارد في الـ Backend وليس واجهة الموبايل فقط.",
    "follow_ups_ar": """- **المحاور:** "ليه بنفضل الـ Android App Links على الـ Custom Schemes زي `myapp://`؟"
  **المرشح:** "لأن الـ Custom Schemes ملهاش أي حماية أو إثبات ملكية؛ أي تطبيق خبيث على جهاز المستخدم يقدر يسجل نفس الـ Scheme في الـ Manifest ويسرق الروابط والـ Tokens. أما الـ App Links بتعتمد على HTTPS وبتتحقق من ملكية الدومين عبر ملف assetlinks.json وبصمة الـ SHA-256 للـ Keystore بتاعنا، فالنظام بيفتح تطبيقنا حصراً ومفيش أي تطبيق يقدر يعترضها."

- **المحاور:** "لو الرابط العميق فتح شاشة تفاصيل طلب `order/123`، إزاي نمنع مستخدم من التجسس على طلبات مستخدم تاني؟"
  **المرشح:** "الحماية لازم تكون في الـ Backend مش في واجهة التطبيق بس. الشاشة بتاخد الـ orderId وتطلب البيانات من الـ Repository؛ الـ Repository بيبعت التوكن بتاع المستخدم الحالي للسيرفر، والسيرفر بيتأكد إن الـ User صاحب التوكن هو المالك الشرعي للطلب ده، ولو مش بتاعه يرمي 403 Forbidden والتطبيق يعرض رسالة رفض وصول." """,
    "self_check_ar": "اعتمد على Android App Links الموثقة؛ طهر الـ Parameters عبر تعبيرات نمطية صارمة؛ تحقق من جلسة تسجيل الدخول قبل الشاشات المحمية؛ واحمِ الـ WebViews من الروابط الخارجية.",
    "references_ar": """- [Verify Android App Links](https://developer.android.com/training/app-links/verify-site-associations) — توثيق الروابط العميقة.
- [OWASP Mobile Top 10 - Insecure Communication](https://mas.owasp.org/) — معايير تأمين مدخلات التطبيقات.

تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.""",
    "quick_answer_ar": "أي Deep Link خارجي لازم يتعامل كمدخل غير موثوق تماماً. أولاً، بنعتمد على الـ Android App Links الموثقة بـ Digital Asset Links بدل الـ Custom Schemes لمنع سرقة الروابط. ثانياً، بنعمل Allowlist صارمة للـ Scheme والـ Host والـ Paths، وبنطهر الـ Parameters من أي مدخلات خبيثة. وأخيراً، بنمرر الشاشات الحساسة على بوابة تحقق من جلسة تسجيل الدخول قبل التنقل.",
    "best_answer_ar": """الـ Deep Links بتدخل بيانات من خارج حدود التطبيق (زي الويب، والإيميل، والـ SMS)، وبالتالي التعامل معاها كمدخل موثوق هو ثغرة أمنية خطيرة.
المعمارية الآمنة لمعالجة الـ Deep Links بتمر بـ 4 خطوات إلزامية:
أولاً، استبدال الـ Custom Schemes زي myapp:// بـ Android App Links رسمية (https://) موثقة بملف assetlinks.json. ده بيضمن إن نظام أندرويد يفتح تطبيقك مباشرة بدون ما يظهر للمستخدم Dialog اختيار تطبيقات، وبيمنع التطبيقات الخبيثة من ادعاء نفس الـ Scheme وسرقة الروابط.
ثانياً، التحقق من الـ Scheme والـ Host والـ Path عبر Whitelist صارمة، وأي رابط خارج النطاق بيتم رفضه فوراً.
ثالثاً، فحص وتطهير الـ Query Parameters؛ يعني لو الرابط فيه orderId، نتأكد إنه Alphanumeric ومفهوش محاولات Path Traversal زي ../ أو محاولات حقن كود، وممنوع نهائياً فتح أي WebView برابط خارجي غير مفحوص لتجنب ثغرة Open Redirect.
رابعاً، فحص الصلاحيات وجلسة الدخول (Auth Gate)؛ لو الرابط رايح لشاشة دفع أو إعدادات الحساب والمستخدم مش مسجل دخول، بنوقفه عند شاشة الـ Login الأول، وبعد نجاح المصادقة بنكمله للهدف المطلوب.""",
    "deep_answer_ar": """على مستوى الـ Mobile Application Security والـ OWASP MASVS، ثغرات الـ Deep Links بتعتبر من أخطر أبواب الاختراق لأنها بتمكن المهاجم من عمل Authentication Bypass، أو Open Redirect، أو Horizontal Privilege Escalation.
الـ Custom Schemes بتمثل ثغرة أمنية بطبيعتها؛ لأن أي تطبيق خبيث على جهاز المستخدم يقدر يعرف نفس الـ Scheme في ملف الـ Manifest بتاعه. الحل القياسي هو App Links الموثقة رقمياً عبر Digital Asset Links؛ الـ PackageManager أثناء تثبيت التطبيق بيبعت يجيب assetlinks.json من الدومين بتاعك ويطابق الـ SHA-256 للـ Signing Certificate بتاعة التطبيق. لو التطابق تم، النظام بيثبت ملكيتك للدومين ويمنع أي تطبيق تاني من اعتراض الروابط.
داخل التطبيق نفسه، أكبر كارثة بنشوفها في الـ Code Audits هي الـ Open Redirect في الـ WebViews؛ تلاقي التطبيق بيستقبل رابط ويب خارجي وبياخد الـ URL يفتحه مباشرة في WebView مفعل فيها الجافاسكريبت وصلاحيات الوصول للملفات. المهاجم هنا يقدر يبعت رابط يفتح صفحة Phishing باسم تطبيقك، أو يسرق ملفات قاعدة البيانات. علشان كده لازم الرابط يخضع لـ Host Allowlist صارمة جداً.
معمارياً، كود فحص الـ Deep Links لازم ينفصل عن كود الواجهة؛ بنبني DeepLinkParser مستقل بيحول الـ Uri لـ Type-Safe Navigation Target باستخدام Kotlinx Serialization في Compose.
والأهم من كل ده هو إن حماية البيانات لازم تكون في طبقة الـ Backend والـ Domain؛ لو الرابط فتح شاشة طلب معين، ممنوع الواجهة تعرض تفاصيل الطلب لمجرد إن الـ ID جه في الرابط، الـ Repository بيبعت التوكن بتاع المستخدم للسيرفر والسيرفر بيتأكد إن الـ User هو المالك الفعلي للطلب وإلا يرمي 403 Forbidden."""
}

# ==============================================================================
# AND-25: How would you support predictable navigation after notification taps and process recreation?
# ==============================================================================
CANONICAL_DATA["AND-25"] = {
    "concept_en": """When a user taps a local or push notification, they expect to land directly on the relevant detail screen (such as an order delivery status, a chat message, or a breaking news article). However, if the notification launches the destination Activity in isolation while the application process was not previously running, pressing the system Back button or performing a back gesture often causes the app to exit immediately to the Android launcher. This jarring behavior breaks the user's mental model of app navigation.
Providing a predictable and intuitive user experience requires constructing a synthetic back stack. Using TaskStackBuilder in traditional View architectures or deep link destination arguments in Jetpack Navigation, the application ensures that entering a deeply nested destination automatically synthesizes its logical parent hierarchy (such as Home -> Orders -> OrderDetails). Furthermore, because process recreation can occur if system memory was reclaimed while the user was interacting with the notification, the notification's PendingIntent must contain immutable flags (FLAG_IMMUTABLE), specify unique request codes, pass only stable entity identifiers rather than volatile objects, and enable the destination ViewModel to reconstitute its state independently from durable storage.""",

    "walkthrough_en": """Constructing a synthetic back stack for notifications using Android's TaskStackBuilder:

```kotlin
fun createOrderNotification(context: Context, orderId: String): Notification {
    // 1. Target destination intent:
    val detailsIntent = Intent(context, OrderDetailsActivity::class.java).apply {
        putExtra("order_id", orderId)
    }

    // 2. Build synthetic back stack ensuring Back button navigates to Home:
    val pendingIntent: PendingIntent = TaskStackBuilder.create(context).run {
        // Automatically reads android:parentActivityName from Manifest:
        addNextIntentWithParentStack(detailsIntent)
        getPendingIntent(
            orderId.hashCode(),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }

    return NotificationCompat.Builder(context, "orders_channel")
        .setSmallIcon(R.drawable.ic_shipping)
        .setContentTitle("Order Shipped")
        .setContentText("Tap to track your delivery")
        .setContentIntent(pendingIntent)
        .setAutoCancel(true)
        .build()
}
```

Failure scenario: A notification opens an order details screen directly with a basic Intent. The user taps Back expecting to view their order list, but the application abruptly terminates to the home screen because no antecedent activities exist in the back stack.""",

    "short_en": """Construct a synthetic back stack using TaskStackBuilder with android:parentActivityName in the manifest, or declare explicit deep links in Jetpack Navigation. This ensures pressing Back navigates up through the logical app hierarchy rather than exiting to the launcher. Configure the PendingIntent with FLAG_IMMUTABLE and FLAG_UPDATE_CURRENT, passing stable entity IDs to reconstruct state from local storage.""",

    "structured_en": """To begin with, when a notification is tapped while the app process is dead, launching an Activity directly creates an isolated task with a single-entry back stack. Pressing the system Back button abruptly terminates the application to the launcher, breaking user navigation expectations.
From an architectural standpoint, we solve this by constructing a synthetic back stack using TaskStackBuilder. By declaring android:parentActivityName in the manifest or leveraging Jetpack Navigation's deep link builder, the system automatically synthesizes the parent Activity hierarchy beneath the target screen during cold launches.
In production scenarios, we configure the notification's PendingIntent using FLAG_IMMUTABLE for security and FLAG_UPDATE_CURRENT to ensure updated extras are delivered. We assign unique request codes to distinct notifications, preventing the operating system from overwriting pending intents for different entities like separate chat messages or order updates.
As for boundary management, notification intents must never carry serialized domain objects. We pass only stable primitive identifiers like an orderId, allowing the resurrected destination ViewModel to reload fresh, verified state directly from durable Room storage upon process restoration.""",

    "deep_senior_en": """Under the hood, notification navigation is mediated by the ActivityTaskManagerService and the system NotificationManagerService. When a notification is posted, the application hands a PendingIntent token to the system server. If the application process is later killed by the Low Memory Killer, the system server retains this token. When the user taps the notification, the system server invokes the token with the application's identity, launching a new task and process via Zygote.
If the developer supplies a bare Intent targeted at OrderDetailsActivity, the activity is launched at the root of a new TaskRecord. When the user triggers back navigation, the ActivityRecord is popped, the task becomes empty, and the framework closes the task, dropping the user onto the home screen. By contrast, when using TaskStackBuilder.create(context).addNextIntentWithParentStack(detailsIntent), the framework inspects android:parentActivityName in the merged manifest and constructs an array of Intents: [MainActivity, OrdersListActivity, OrderDetailsActivity]. The ActivityTaskManagerService instantiates all three activities in a single task, placing OrderDetailsActivity at the top. When the user presses Back, OrderDetailsActivity finishes, smoothly revealing OrdersListActivity exactly as if the user had navigated there manually.
In modern Jetpack Compose Navigation, a similar mechanism is handled via NavDeepLinkBuilder. When creating a PendingIntent for a Composable destination, NavDeepLinkBuilder analyzes the declared graph hierarchy and automatically synthesizes the NavBackStackEntry chain, populating all parent routes in the in-memory back stack.
From a concurrency and state restoration standpoint, developers must handle onNewIntent when the Activity is already running in the foreground with singleTop launchMode. In this scenario, onCreate does not re-execute; the new intent arrives via onNewIntent(intent), where setIntent(intent) must be invoked so subsequent state restorations and SavedStateHandle instances reflect the updated payload. Finally, passing only stable primitive IDs ensures that even if local cache was cleared or server state mutated during background suspension, the destination loads authoritative truth from the repository upon resumption."""
}

ARABIC_METADATA["AND-25"] = {
    "id": "AND-25",
    "questionAr": "كيف تدعم التنقل المتوقع بعد الضغط على الإشعارات وإعادة بناء العملية؟",
    "topicAr": TOPIC_AR,
    "evaluates_ar": """- بناء مكدس رجوع افتراضي (Synthetic Back Stack) عند الدخول من إشعار في وضع Cold Start.
- تحديد هوية وتغير الـ PendingIntent بدقة واستخدام FLAG_IMMUTABLE مع تمرير المعرّفات الثابتة فقط.
- التعامل مع تنشيط الشاشات الموجودة بالفعل في المقدمة عبر دالة onNewIntent وتحديث الحالة.""",
    "why_it_matters_ar": "الإشعارات بتمثل نقاط دخول خارجية مستقلة للتطبيق. نظام أندرويد ممكن يفتح الـ Activity في Task موجودة بالفعل أو ينشئ Task جديدة تماماً لو كانت العملية ميتة. الـ PendingIntent بيحمل تفويضاً لنظام التشغيل لتشغيل المكون بالنيابة عن التطبيق. بناء مكدس الرجوع الافتراضي بيضمن إن المستخدم لما يدوس Back يرجع للشاشات الأبوية المنطقية في التطبيق بدل ما يخرج فجأة للشاشة الرئيسية للنظام.",
    "worked_example_ar": """بناء Synthetic Backstack حقيقي للإشعارات باستخدام TaskStackBuilder:
```kotlin
fun createOrderNotification(context: Context, orderId: String): Notification {
    val detailsIntent = Intent(context, OrderDetailsActivity::class.java).apply {
        putExtra("order_id", orderId)
    }

    val pendingIntent = TaskStackBuilder.create(context).run {
        // يقرأ الشاشات الأبوية تلقائياً من خاصية android:parentActivityName
        addNextIntentWithParentStack(detailsIntent)
        getPendingIntent(
            orderId.hashCode(),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }

    return NotificationCompat.Builder(context, "orders_channel")
        .setContentTitle("تم شحن طلبك")
        .setContentIntent(pendingIntent)
        .build()
}
```""",
    "trade_offs_ar": "استخدام TaskStackBuilder هو الحل الأمثل لتطبيقات الـ Views الكلاسيكية المعتمدة على عدة Activities، بينما مكتبة Jetpack Navigation و NavDeepLinkBuilder توفر نفس السلوك تلقائياً لشاشات Compose و Single-Activity Architecture. إنشاء شاشات وهمية في الـ Backstack يستهلك ذاكرة إضافية قليلة لكنه ضروري لمنع إحباط المستخدم.",
    "failure_modes_ar": "فتح الشاشة بـ Intent مباشر وبدون Synthetic Backstack يجعل زر Back يغلق التطبيق فوراً. استخدام نفس الـ Request Code لإشعارات متعددة يجعل أندرويد يستبدل بيانات الإشعار القديم ببيانات الأخير. إهمال استدعاء setIntent داخل onNewIntent عند استخدام نمط singleTop يترك الشاشة معتمدة على بيانات الـ Intent القديمة. يتم الفحص بإغلاق التطبيق بالكامل والضغط على الإشعار ثم الضغط على زر Back.",
    "production_perspective_ar": "في تطبيقات الإنتاج الكبيرة، بنحدد android:parentActivityName بوضوح في ملف الـ Manifest لكل شاشة فرعية، أو بنعتمد على NavDeepLinkBuilder في Compose لإنشاء الـ PendingIntent متضمناً مسارات الـ Graph الأبوية. بنستخدم FLAG_IMMUTABLE لأسباب أمنية صارمة، وبنمرر فقط المعرّفات الأولية الثابتة زي orderId مع تحميل البيانات الحديثة من Room عند فتح الشاشة.",
    "how_to_answer_ar": """- **السبب المعماري:** وضح أن تشغيل الشاشة من إشعار في Cold Start ينشئ Task بدون شاشات سابقة مما يكسر توقعات المستخدم عند الرجوع.
- **طريقة الشرح:** ابدأ بشرح كلاس TaskStackBuilder وخاصية android:parentActivityName، ثم بديله في Compose (NavDeepLinkBuilder).
- **المفاضلات:** اشرح تكوين الـ PendingIntent مع FLAG_IMMUTABLE وأهمية توليد Request Code فريد.
- **أنماط الفشل:** استشهد بخروج التطبيق المفاجئ عند الضغط على Back وتجاهل onNewIntent.
- **الحل الإنتاجي:** وضح تمرير المعرّفات الأولية فقط وقراءة البيانات من الـ Repository لضمان دقة البيانات بعد موت العملية.""",
    "talking_points_ar": "ناقش كيف تدير ActivityTaskManagerService سجلات TaskRecord و ActivityRecord، ودور رايات PendingIntent مثل FLAG_UPDATE_CURRENT و FLAG_IMMUTABLE، وكيف يتعامل نمط singleTop مع onNewIntent لتحديث SavedStateHandle، والفرق المعماري بين Single-Activity Navigation و Multi-Activity Tasks.",
    "follow_ups_ar": """- **المحاور:** "ماذا يحدث لو الشاشة كانت مفتوحة بالفعل وضغط المستخدم على إشعار جديد يحمل بيانات مختلفة؟"
  **المرشح:** "لو الشاشة معرّفة بـ launchMode='singleTop'، النظام مش هينشئ نسخة جديدة ومش هيستدعي onCreate، لكنه هيبعت الـ Intent الجديد لدالة onNewIntent(intent). وهنا لازم وضروري جداً نستدعي `setIntent(intent)` داخل onNewIntent علشان نحدث الـ Intent الأصلي للشاشة، ونطلب من الـ ViewModel يحدث بياناته بالـ ID الجديد."

- **المحاور:** "كيف يحل NavDeepLinkBuilder في Jetpack Compose مشكلة مكدس الرجوع الافتراضي؟"
  **المرشح:** "الـ NavDeepLinkBuilder بيقوم بتحليل الـ NavGraph بتاع التطبيق تلقائياً؛ ولما نحدد له الشاشة المستهدفة، بينشئ PendingIntent بيحتوي على مصفوفة بكل المسارات الأبوية الموصلة للشاشة دي في الـ Graph. ولما المستخدم يضغط الإشعار والتطبيق يفتح من الصفر، الـ NavController بيبني الـ NavBackStackEntry لكل الشاشات السابقة تحت الشاشة المستهدفة." """,
    "self_check_ar": "ابنِ Synthetic Backstack بـ TaskStackBuilder؛ حدد parentActivityName في الـ Manifest؛ اضبط رايات PendingIntent بـ FLAG_IMMUTABLE؛ وعالج onNewIntent مع setIntent.",
    "references_ar": """- [Start an Activity from a Notification](https://developer.android.com/develop/ui/views/notifications/navigation) — بناء مكدس الرجوع الافتراضي.
- [TaskStackBuilder API](https://developer.android.com/reference/androidx/core/app/TaskStackBuilder) — فئة بناء المهام والمكدس.

تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.""",
    "quick_answer_ar": "علشان نضمن تنقل متوقع ومنطقي بعد الضغط على الإشعار، بنبني Synthetic Backstack باستخدام TaskStackBuilder وتحديد android:parentActivityName في الـ Manifest، أو بالاعتماد على Deep Links في Jetpack Navigation. ده بيضمن إن المستخدم لو داس Back يرجع للشاشات الأبوية في التطبيق بدل ما يخرج فجأة للـ Launcher. وبنضبط الـ PendingIntent بـ FLAG_IMMUTABLE وبنبعت IDs فقط.",
    "best_answer_ar": """المشكلة الشائعة جداً في تجربة المستخدم مع الإشعارات هي إن التطبيق لو كان مقفول في الخلفية والمستخدم داس على إشعار 'تم شحن طلبك'، الشاشة بتفتح كـ Activity وحيدة في الـ Task؛ وأول ما المستخدم يدوس زرار Back يخرج فجأة لشاشة الهاتف الرئيسية بدل ما يرجع لصفحة طلباتي أو الرئيسية!
علشان نحل المشكلة دي معمارياً، بنبني ما يسمى بـ Synthetic Backstack عبر كلاس TaskStackBuilder. بنعرف الشاشات الأبوية في الـ Manifest بخاصية android:parentActivityName، وبنطلب من الـ TaskStackBuilder يولد الـ PendingIntent ومعه الـ Parent Stack بالكامل.
لما المستخدم يدوس على الإشعار من حالة الـ Cold Start، النظام بيبني سلسلة الشاشات تحت بعض: الرئيسية، ثم قائمة الطلبات، ثم شاشة تفاصيل الطلب في الواجهة؛ وبالتالي لما المستخدم يدوس Back، بيرجع خطوة لورا بشكل طبيعي جداً ومتوافق مع توقعاته.
وفي Jetpack Navigation و Compose، الـ NavDeepLinkBuilder بيقوم بنفس المهمة دي تلقائياً لبناء شجرة الـ Backstack.
وأمنياً، لازم نستخدم FLAG_IMMUTABLE مع FLAG_UPDATE_CURRENT ونمرر فقط المعرّف (زي orderId) ونسيب الشاشة تقرأ البيانات الحديثة من الـ Repository.""",
    "deep_answer_ar": """على مستوى الـ ActivityTaskManagerService والـ Window Manager في نظام أندرويد، لما بتعمل PendingIntent لإشعار، أنت بتسلم النظام Token مع صلاحية تشغيل Activity بالنيابة عن تطبيقك حتى لو العملية ماتت بالكامل.
لو بعتت Intent عادي بيفتح OrderDetailsActivity، النظام هينشئ TaskRecord جديد جواه ActivityRecord واحد فقط. أول ما المستخدم يضغط زر الرجوع، الـ Activity هتدمر والـ Task هتبقى فاضية، فالنظام هيقفل التطبيق ويرجع المستخدم للـ Launcher.
باستخدام TaskStackBuilder.create(context).addNextIntentWithParentStack(detailsIntent)، النظام بيقرأ شجرة الـ Hierarchy المتسجلة في الـ Manifest من خلال android:parentActivityName. ولما المستخدم يضغط على الإشعار، الـ System Server بينشئ مصفوفة Intents كاملة:
الرئيسية، ثم قائمة الطلبات، ثم تفاصيل الطلب،
وبيحطهم كلهم في نفس الـ Task في خطوة واحدة، وبيخلي OrderDetailsActivity هي اللي في الـ Foreground. لما المستخدم يضغط Back، الشاشة بتتدمر بنظافة وبتظهر تحتها OrdersListActivity كأن المستخدم فتح التطبيق ومشي في المسار ده بنفسه.
وفي معمارية Jetpack Compose و Navigation Component الحديثة، بنستخدم NavDeepLinkBuilder اللي بيعمل تحليل للـ NavGraph، وبيحط كل الـ Composable Destinations الأبوية في الـ NavBackStack قبل ما يعرض الشاشة المستهدفة.
نقطة هندسية دقيقة جداً لازم ننتبه ليها: لو التطبيق كان شغال بالفعل في الـ Foreground والشاشة معمولها launchMode='singleTop'، الضغط على الإشعار مش هيستدعي onCreate من جديد، لكنه هيبعت الـ Intent الجديد لدالة onNewIntent. لو المطور معملش setIntent(intent) جوه onNewIntent، أي عملية استرجاع للحالة أو قراءة للـ SavedStateHandle بعد كده هتقرأ بيانات قديمة مش متطابقة مع الإشعار الأخير. ومعمارياً بنمرر فقط Stable IDs ونتجنب تمرير كائنات كبيرة لتفادي كسر الـ Binder Transaction Limits."""
}
