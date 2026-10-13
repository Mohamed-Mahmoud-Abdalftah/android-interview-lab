#!/usr/bin/env python3
"""Generator for PAT-13 through PAT-18 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "pat.json"

PAT_13_18 = [
    {
        "id": "PAT-13",
        "arabic_explanation": (
            "العلاقة بين الـ Observer Pattern التقليدي (Callbacks / Listeners) وبين LiveData و Kotlin Flow في Android:\n\n"
            "1. التطور التاريخي للأوبزرفر في أندرويد:\n"
            "   - **الـ Callbacks و Listeners التقليدية**: كان كل كلاس يعرّف `interface Listener { fun onDataChanged(...) }` وقائمة `listeners = mutableListOf()`. المشكلة الكبرى كانت تسريب الذاكرة (Memory Leaks) إذا نسي المطور إلغاء التسجيل في `onDestroy` أو `onStop`، بالإضافة إلى غياب أي وعي بدورة الحياة (Lifecycle unawareness).\n"
            "   - **LiveData**: ظهرت مع أصل Android Architecture Components لحل مشكلة الـ Lifecycle. هي Hot Observable يخزن آخر قيمة (`current value`) ولا يرسل إشعارات إلا إذا كان الـ Observer في حالة نشطة (`STARTED` أو `RESUMED`). عيوبها: مرتبطة بالـ Main Thread (`setValue` لازم main، و `postValue` يسقط تحديثات إذا كانت متقاربة)، وتعتمد كلياً على Android SDK مما يجعلها غير صالحة لطبقة الـ Domain الخالصة.\n"
            "   - **Kotlin Coroutines Flow**: الحل الحديث القياسي في Kotlin. نوعان أساسيان:\n"
            "     * **Cold Flow (`flow { ... }`)**: لا ينفذ أي كود ولا يستهلك موارد إلا عندما يبدأ Collector في القراءة. يتم إيقافه تلقائياً عند إلغاء الـ Coroutine Scope.\n"
            "     * **Hot Flow (`SharedFlow` و `StateFlow`)**: تظل تبث الأحداث حتى دون وجود مستمعين. `StateFlow` هو البديل العصري لـ LiveData (يحتفظ بآخر قيمة، يقارن بـ `equals` لمنع التكرار، مستقل تماماً عن Android SDK، وThread-safe).\n\n"
            "2. تحويل الـ Legacy Callbacks إلى Flows بأمان:\n"
            "   - استخدام `callbackFlow` مع تعليمة `awaitClose { ... }` الإلزامية. هذا يضمن إزالة الـ Listener فور إلغاء الـ Scope، مما يمنع تسريب الذاكرة نهائياً."
        ),
        "practical_walkthrough": (
            "تحويل Callback إلى Flow آمن بدورة الحياة مقابل النمط القديم المعرض للتسريب:\n"
            "```kotlin\n"
            "// ❌ النمط القديم: تسريب ذاكرة إذا نسي الـ UI فك التسجيل في onDestroy:\n"
            "class LocationTrackerLegacy(private val locationManager: LocationManager) {\n"
            "    private val listeners = mutableListOf<LocationListener>()\n"
            "    fun register(listener: LocationListener) { listeners.add(listener) }\n"
            "    fun unregister(listener: LocationListener) { listeners.remove(listener) } // لو الـ Activity ماتت بدون ده -> Memory Leak!\n"
            "}\n"
            "\n"
            "// ✅ النمط الحديث: callbackFlow مع awaitClose يضمن تحرير الموارد تلقائياً:\n"
            "class LocationTrackerRepository(private val fusedLocationClient: FusedLocationProviderClient) {\n"
            "    fun observeLocation(): Flow<Location> = callbackFlow {\n"
            "        val callback = object : LocationCallback() {\n"
            "            override fun onLocationResult(result: LocationResult) {\n"
            "                result.lastLocation?.let { trySend(it) }\n"
            "            }\n"
            "        }\n"
            "        fusedLocationClient.requestLocationUpdates(locationRequest, callback, Looper.getMainLooper())\n"
            "        \n"
            "        // يتم استدعاء awaitClose فور توقف الـ Collector أو إلغاء الـ Scope:\n"
            "        awaitClose {\n"
            "            fusedLocationClient.removeLocationUpdates(callback)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// في الـ UI (Compose أو LifecycleOwner):\n"
            "// جمع الـ Flow فقط في حالة STARTED لتفادي استهلاك البطارية في الخلفية:\n"
            "viewLifecycleOwner.lifecycleScope.launch {\n"
            "    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n"
            "        viewModel.locationFlow.collect { location -> updateMap(location) }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Callbacks are primitive, lifecycle-unaware Observer implementations prone to leaks. LiveData solved leaks by observing only during active states (STARTED/RESUMED) but is locked to the Main Thread and Android SDK. Flow is Kotlin's modern reactive stream: cold by default, multiplatform, backpressure-capable, and easily bridges callbacks via callbackFlow and awaitClose while StateFlow replaces LiveData for UI state.",
        "best_answer": (
            "All three mechanisms implement the Observer pattern, but they solve fundamentally different lifecycle, threading, and backpressure challenges.\n\n"
            "1. **Callbacks and Listeners**: Primitive and lifecycle-unaware. If an Activity registers a callback on a long-lived singleton and fails to unregister in `onDestroy`, you leak the entire UI hierarchy. Furthermore, error handling, threading, and composition must be wired by hand.\n\n"
            "2. **LiveData**: Built specifically to prevent leaks in Android UI. It is a hot, single-value holder that only dispatches emissions to active lifecycle owners (`STARTED` or `RESUMED`). However, its limitations are severe: it is coupled to the Android framework, confined to the Main Thread, drops rapid updates in `postValue()`, and lacks operators for asynchronous transformations.\n\n"
            "3. **Flow (Cold Flow & StateFlow)**: Flow is pure Kotlin, structured-concurrency native, and completely decoupled from Android SDK. Cold Flows compute on-demand per collector. Hot `StateFlow` replaces LiveData for state retention with thread-safety and conflation. In Android UI, we bridge callback SDKs using `callbackFlow` with `awaitClose`, and collect via `repeatOnLifecycle` to get perfect lifecycle safety without sacrificing Kotlin's rich functional operators."
        ),
        "deep_answer": (
            "When dissecting internal contracts, the key architectural distinction is **Subscription Semantics vs. Backpressure**.\n\n"
            "Callbacks have zero backpressure mechanism; if a sensor emits 120 times a second and the listener takes 50ms per frame, the app either drops events silently or overflows the call stack. LiveData applies primitive conflation: `postValue` overwrites an internal volatile field, so if you call `postValue` five times before the next Looper frame, observers receive only the 5th value.\n\n"
            "In contrast, Kotlin Flow handles backpressure natively via coroutine suspension. If a downstream collector is suspended, an upstream `flow { ... }` suspends at `emit()`. In `callbackFlow`, because callbacks are driven by non-suspending platform threads, we use `trySend()` backed by a `BufferOverflow` strategy (e.g., `BufferOverflow.DROP_OLDEST`) or `channelFlow` with explicit buffering.\n\n"
            "Finally, regarding Lifecycle: LiveData listens directly to `Lifecycle.Event.ON_START` and `ON_STOP`. Flow is lifecycle-agnostic by design. To prevent background battery drain when using Flow in UI layers, Google introduced `repeatOnLifecycle` or `flowWithLifecycle`, which internally cancel the collecting coroutine when the lifecycle drops below `STARTED` and recreate it upon resumption."
        ),
        "follow_ups": [
            {
                "question": "Why is `callbackFlow` dangerous if you forget `awaitClose`?",
                "answer": "Without `awaitClose`, the `callbackFlow` block immediately runs to completion and closes the channel, preventing any future callbacks from being delivered, or worse, fails to clean up listeners causing severe memory leaks."
            },
            {
                "question": "Can StateFlow lose events like a navigation event?",
                "answer": "Yes. StateFlow is conflated and state-oriented. If you emit two rapid navigation events, the second overwrites the first. One-off events should be modeled as discrete actions, channeled commands, or explicit consumed states in StateFlow."
            }
        ]
    },
    {
        "id": "PAT-14",
        "arabic_explanation": (
            "كيف يستبدل نمط آلة الحالة الصريحة (Explicit State Machine) المتغيرات المنطقية المتفرقة (Scattered Boolean Flags)؟\n\n"
            "1. كارثة الـ Boolean Flags المتعددة:\n   - عندما تحتوي شاشة الطلبات أو الدفع على: `var isLoading = false` و `var isSuccess = false` و `var hasError = false` و `var isRetrying = false`.\n   - المشكلة الرياضية: مع 4 أعلام Boolean، لديك $2^4 = 16$ حالة ممكنة في الذاكرة!\n   - حالات غير قانونية (Illegal States): يمكن أن يصبح `isLoading = true` و `isSuccess = true` و `hasError = true` في نفس اللحظة بسبب Race Condition أو خطأ استدعاء، مما يؤدي إلى شاشة تعرض مؤشر التحميل وزر الخطأ ونجاح الدفع معاً!\n\n"
            "2. الحل بـ State Machine و Sealed Interfaces:\n   - حصر الحالات الممكنة في حالات منطقية قانونية فقط (`Idle`, `Loading`, `Success`, `Error`).\n   - من المستحيل فيزيائياً أن يكون التطبيق في أكثر من حالة واحدة في نفس اللحظة.\n   - حصر الأحداث (Events) التي تحرك الانتقالات بين الحالات (Transitions)، بحيث لا يمكن الانتقال من `Success` إلى `Loading` دون حدث صريح ومسموح.\n   - الاستفادة من ميزة الـ Exhaustive `when` في Kotlin التي تجبر المترجم على التحقق من تغطية جميع الحالات، مما يمنع الأخطاء في وقت التشغيل (Compile-time safety)."
        ),
        "practical_walkthrough": (
            "المقارنة بين المتغيرات المنطقية المتفرقة وآلة الحالة المحكمة:\n"
            "```kotlin\n"
            "// ❌ فوضى الـ Scattered Booleans: احتمالية ظهور حالات مستحيلة وغير قانونية:\n"
            "class BadCheckoutViewModel : ViewModel() {\n"
            "    var isLoading = false\n"
            "    var isPaid = false\n"
            "    var hasError = false\n"
            "    \n"
            "    fun pay() {\n"
            "        isLoading = true\n"
            "        // لو حصل Exception وسقط الكود، قد يظل isLoading = true مع hasError = true!\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ آلة حالة صريحة (Explicit State Machine) باستخدام Sealed Interfaces:\n"
            "sealed interface CheckoutState {\n"
            "    object Idle : CheckoutState\n"
            "    data class Submitting(val orderId: String) : CheckoutState\n"
            "    data class Confirmed(val transactionId: String, val receiptUrl: String) : CheckoutState\n"
            "    data class Failed(val errorReason: String, val canRetry: Boolean) : CheckoutState\n"
            "}\n"
            "\n"
            "sealed interface CheckoutEvent {\n"
            "    data class SubmitClicked(val orderId: String) : CheckoutEvent\n"
            "    data class PaymentSucceeded(val txId: String, val receipt: String) : CheckoutEvent\n"
            "    data class PaymentFailed(val reason: String, val canRetry: Boolean) : CheckoutEvent\n"
            "    object RetryClicked : CheckoutEvent\n"
            "}\n"
            "\n"
            "// Reducer نقي يحسب الحالة التالية بناءً على الحالة الحالية والحدث:\n"
            "fun checkoutReducer(current: CheckoutState, event: CheckoutEvent): CheckoutState = when (current) {\n"
            "    is CheckoutState.Idle -> when (event) {\n"
            "        is CheckoutEvent.SubmitClicked -> CheckoutState.Submitting(event.orderId)\n"
            "        else -> current // تجاهل الأحداث غير القانونية في هذه الحالة\n"
            "    }\n"
            "    is CheckoutState.Submitting -> when (event) {\n"
            "        is CheckoutEvent.PaymentSucceeded -> CheckoutState.Confirmed(event.txId, event.receipt)\n"
            "        is CheckoutEvent.PaymentFailed -> CheckoutState.Failed(event.reason, event.canRetry)\n"
            "        else -> current\n"
            "    }\n"
            "    is CheckoutState.Failed -> when (event) {\n"
            "        CheckoutEvent.RetryClicked if current.canRetry -> CheckoutState.Submitting(\"retry_order\")\n"
            "        else -> current\n"
            "    }\n"
            "    is CheckoutState.Confirmed -> current // حالة نهائية، لا تقبل أي انتقالات\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Scattered booleans create $2^N$ combinatorial states, allowing impossible illegal states like showing a loading spinner and an error banner simultaneously. An explicit state machine uses Kotlin sealed interfaces to model only valid domain states, explicit input events, and deterministic state transitions via a pure reducer, making illegal states unrepresentable at compile time.",
        "best_answer": (
            "Scattered boolean flags are one of the biggest sources of UI glitches in Android apps. When a ViewModel tracks `isLoading`, `isError`, and `isPaid` independently, you create $2^N$ possible combinations. It becomes trivially easy for asynchronous race conditions to leave the app in an impossible state where the screen is loading, displaying an error, and showing a success modal simultaneously.\n\n"
            "An explicit State Machine solves this by making illegal states unrepresentable:\n"
            "1. **Sealed State Hierarchy**: We model states as a closed hierarchy (`Idle`, `Submitting`, `Confirmed`, `Failed`). The UI renders exactly one state at any point in time.\n"
            "2. **Explicit Events & Transitions**: State changes can only happen in response to registered domain events through a state reducer or transition table. If a user double-taps 'Pay', the reducer receives a second click event while already in the `Submitting` state and cleanly ignores it.\n"
            "3. **Exhaustive Verification**: Kotlin's compiler forces the UI layer (`when (state)`) to handle every legal state, ensuring zero overlooked edge cases."
        ),
        "deep_answer": (
            "From a formal systems perspective, migrating to a Finite State Machine (FSM) elevates your architecture from ad-hoc procedural code to a deterministic mathematical model.\n\n"
            "In production Android, we enforce three architectural guardrails when designing state machines:\n"
            "1. **Single Source of Truth & Pure Reducers**: The transition logic `(State, Event) -> State` should be a pure function free of side effects. Side effects (network calls, database writes, analytics tracking) are emitted as separate side-effect commands or effects, ensuring the state machine itself is testable in pure JVM unit tests without mocking coroutines.\n"
            "2. **State Machines across Process Death**: A common trap is keeping the state machine purely in memory. For critical transactions like payments, the state must be backed by durable persistence (Room or DataStore) using an idempotency key. If Android OS kills the process during `Submitting`, upon recreation the state machine resumes from `PendingReconciliation`, checking the server status rather than resetting to `Idle` or charging the user twice.\n"
            "3. **Hierarchical State Machines (Statecharts)**: For deeply nested flows (like a multi-step checkout with address selection, payment method, and 3DS verification), nested sealed interfaces represent composite states cleanly without inflating the top-level machine."
        ),
        "follow_ups": [
            {
                "question": "How do you handle asynchronous side-effects inside a pure reducer?",
                "answer": "Reducers must remain pure. Side effects are triggered by emitting one-off SideEffect objects or launching dedicated effect handlers in response to state transitions outside the reducer."
            },
            {
                "question": "What prevents double-clicks from causing race conditions in a state machine?",
                "answer": "In the Submitting state, incoming Click events are not mapped to any transition and are simply discarded by the reducer."
            }
        ]
    },
    {
        "id": "PAT-15",
        "arabic_explanation": (
            "تصميم نظام دفع يدعم مزودي خدمة متعددين (Stripe, PayPal, Google Pay) باستخدام Strategy أو Factory، وكيفية تجنب الـ God Factory:\n\n"
            "1. المشكلة مع الـ God Factory:\n   - وضع جميع تفاصيل المزودين في كلاس واحد `PaymentFactory`: الكلاس يعرف تفاصيل كل SDK، وينشئ الـ UI الخاص بكل مزود، ويعالج الـ Callbacks والـ Retries الخاصة بكل بنك.\n   - النتيجة: كلاس ضخم ينتهك مبدأ Single Responsibility و Open/Closed Principle. كلما أردت إضافة مزود دفع جديد، تضطر لتعديل واختبار `PaymentFactory` من جديد.\n\n"
            "2. الحل المعماري النظيف (Strategy + Factory / DI Multibindings):\n   - **Strategy Interface**: واجهة موحدة ونقية (`PaymentGateway` أو `PaymentStrategy`) تعرف عقداً عاماً لمعالجة الدفع: `suspend fun processPayment(request: PaymentRequest): PaymentResult`.\n   - **Adapters مستقلة لكل مزود**: كلاس مستقل لكل مزود (`StripePaymentAdapter`, `GooglePayAdapter`, `PayPalAdapter`) يغلف الـ SDK الخاص به ويعزل تفاصيله تماماً.\n   - **تجنب الـ God Factory عبر DI Multibindings (Dagger/Hilt)**: بدلاً من كتابة `when(type) { STRIPE -> StripeAdapter(...) }`، نستخدم خريطة محقونة تلقائياً `Map<PaymentType, @JvmSuppressWildcards PaymentStrategy>`. إضافة مزود جديد تتطلب فقط كتابة كلاس جديد وتزويد الـ Module برابط له دون لمس سطر واحد في الكود القائم."
        ),
        "practical_walkthrough": (
            "تنفيذ Strategy Pattern مع DI Multibindings لتفادي الـ God Factory:\n"
            "```kotlin\n"
            "// 1. العقد الموحد (Strategy Interface):\n"
            "interface PaymentStrategy {\n"
            "    val supportedType: PaymentType\n"
            "    suspend fun pay(orderId: String, amount: Money): PaymentResult\n"
            "}\n"
            "\n"
            "// 2. تطبيق مستقل لكل مزود يعزل الـ SDK تماماً (Concrete Strategies):\n"
            "class StripeStrategy @Inject constructor(\n"
            "    private val stripeClient: StripeSdkClient\n"
            ") : PaymentStrategy {\n"
            "    override val supportedType = PaymentType.STRIPE\n"
            "    override suspend fun pay(orderId: String, amount: Money): PaymentResult {\n"
            "        return stripeClient.confirmPayment(orderId, amount.toCents()).toDomain()\n"
            "    }\n"
            "}\n"
            "\n"
            "class GooglePayStrategy @Inject constructor(\n"
            "    private val paymentsClient: PaymentsClient\n"
            ") : PaymentStrategy {\n"
            "    override val supportedType = PaymentType.GOOGLE_PAY\n"
            "    override suspend fun pay(orderId: String, amount: Money): PaymentResult {\n"
            "        return paymentsClient.requestPayment(orderId, amount).toDomain()\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. مدير الدفع النظيف الخالي من الـ God Factory عبر Map Injection:\n"
            "class PaymentProcessor @Inject constructor(\n"
            "    private val strategies: Set<@JvmSuppressWildcards PaymentStrategy>\n"
            ") {\n"
            "    private val strategyMap: Map<PaymentType, PaymentStrategy> by lazy {\n"
            "        strategies.associateBy { it.supportedType }\n"
            "    }\n"
            "\n"
            "    suspend fun executePayment(type: PaymentType, orderId: String, amount: Money): PaymentResult {\n"
            "        val strategy = strategyMap[type] \n"
            "            ?: throw IllegalArgumentException(\"Unsupported payment provider: $type\")\n"
            "        return strategy.pay(orderId, amount)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "To support multiple payment providers without creating a God Factory, define a clean Strategy interface (PaymentStrategy) representing unified payment contracts. Implement isolated Adapters for each provider SDK. Instead of hardcoding all initializations in a massive factory switch-statement, use Dagger/Hilt multibindings to inject a map or set of strategies, adhering strictly to the Open/Closed Principle.",
        "best_answer": (
            "When designing a multi-payment architecture, the common failure is building a monolithic 'God Factory' that imports every vendor SDK, configures their credentials, handles their distinct callback listeners, and manages UI presentation logic in a giant `when` statement.\n\n"
            "A clean production architecture decouples this into three distinct layers:\n"
            "1. **Unified Strategy Contract**: We declare a high-level `PaymentStrategy` interface exposing common transaction semantics: `suspend fun pay(orderId: String, amount: Money): PaymentResult`.\n"
            "2. **Isolated Vendor Adapters**: Each provider (Stripe, PayPal, Google Pay) lives in its own class—or even its own Gradle module. The adapter handles SDK initialization, maps vendor exceptions into typed domain results, and keeps third-party imports quarantined.\n"
            "3. **Registry via DI Multibindings**: Instead of a monolithic factory class, we use Dagger/Hilt multibindings (`@IntoSet` or `@IntoMap`). The `PaymentProcessor` receives an injected `Map<PaymentMethod, PaymentStrategy>`. Adding a new payment provider requires writing one new adapter class and one binding module; existing code is completely untouched, honoring the Open/Closed Principle."
        ),
        "deep_answer": (
            "The subtle architectural challenge in multi-payment systems is that payment providers rarely share identical lifecycle and UI capabilities. For example, Google Pay presents a native Android BottomSheet sheet, Stripe requires a 3D Secure Webview/Activity redirect, while direct card entry requires PCI-DSS compliant tokenization fields.\n\n"
            "If you force all these divergent requirements into a single synchronous `pay()` method, your Strategy abstraction leaks. To address this in enterprise systems:\n"
            "1. **Capability Interfaces**: We break the strategy into capabilities: `DirectCheckoutStrategy` for headless API payments, and `InteractiveCheckoutStrategy` for providers requiring an Activity result launcher (`ActivityResultLauncher`).\n"
            "2. **Idempotency and Reconciliation**: The payment processor must be backed by an idempotency key generated prior to engaging the strategy. If the user completes 3DS verification and the app process dies while returning, the app queries the backend status rather than retrying through the strategy.\n"
            "3. **Feature Flagging & Remote Fallbacks**: Strategies can be decorated with a `CircuitBreakerDecorator` or remote configuration flag. If Stripe experiences an outage in a specific region, the processor dynamically removes Stripe from the UI and falls back to PayPal without deploying a new app binary."
        ),
        "follow_ups": [
            {
                "question": "How do Dagger/Hilt multibindings eliminate factory modification?",
                "answer": "By using `@IntoSet` or `@IntoMap`, each provider module declares its own strategy binding independently. Dagger assembles them into an injected collection automatically without modifying any central factory class."
            },
            {
                "question": "How do you handle providers that require an ActivityResultLauncher?",
                "answer": "Define a capability interface like `ActivityLauncherPaymentStrategy` where the UI provides a registered launcher contract before executing the payment."
            }
        ]
    },
    {
        "id": "PAT-16",
        "arabic_explanation": (
            "تبديل مكتبات خارجية (Vendor SDKs) ذات أنظمة استدعاءات (Callbacks) مختلفة: ما هي الأنماط والحدود المعمارية المناسبة؟\n\n"
            "1. طبيعة المشكلة عند التعامل مع مكتبات خارجية:\n   - شركة ترغب في استبدال مزود التحقق من الهوية (KYC SDK أو OCR Scanner) من Vendor A إلى Vendor B.\n   - Vendor A يعتمد على Java Callbacks قديمة مع `onSuccess(String json)` و `onError(int code)`.\n   - Vendor B يطلب تشغيل Activity عبر `startActivityForResult` ويعيد كائنات مخصصة معقدة.\n   - إذا كانت هذه الـ SDKs مستوردة مباشرة داخل الـ ViewModels أو الـ Composables، فإن استبدال المزود سيتطلب إعادة كتابة التطبيق بالكامل وإعادة اختبار كل الشاشات!\n\n"
            "2. الأنماط المعمارية والحدود الواقية (Boundaries):\n   - **Anti-Corruption Layer (ACL) / Facade Pattern**: طبقة حماية عازلة تحول مفاهيم وأخطاء الـ Vendor الفوضوية إلى نماذج بيانات نقية خاصة بالنطاق الداخلي للتطبيق (Domain Models).\n   - **Adapter Pattern**: محول مخصص لكل Vendor يحول أسلوب الاستدعاء الخاص به (Callbacks أو Intents) إلى `suspend fun` أو `Flow` باستخدام `suspendCancellableCoroutine`.\n   - **Domain Interface (Contract)**: واجهة نقية (`IdentityVerificationGateway`) في طبقة الـ Domain لا تحتوي على أي إشارة لأي نوع أو كلاس من الـ SDK الخارجي.\n   - **Modularization**: وضع كود الـ SDK داخل Gradle module مستقل، بحيث لا تستطيع موديولات الـ UI والـ Features استيراده حتى عن طريق الخطأ."
        ),
        "practical_walkthrough": (
            "بناء Anti-Corruption Layer و Adapter لعزل استدعاءات الـ Vendor المختلفة وتحويلها إلى واجهة نقية:\n"
            "```kotlin\n"
            "// 1. العقد الصافي في طبقة الـ Domain (لا يعلم شيئاً عن أي Vendor):\n"
            "interface DocumentScanner {\n"
            "    suspend fun scanPassport(): Result<PassportData>\n"
            "}\n"
            "\n"
            "// 2. Adapter لمزود يعتمد على Callbacks قديمة (Legacy Vendor A):\n"
            "class VendorAScannerAdapter(private val vendorASdk: LegacyVendorASdk) : DocumentScanner {\n"
            "    override suspend fun scanPassport(): Result<PassportData> = suspendCancellableCoroutine { continuation ->\n"
            "        val listener = object : VendorAListener {\n"
            "            override fun onScanCompleted(vendorModel: VendorADocResult) {\n"
            "                // تحويل الموديل الخاص بالـ Vendor إلى موديل الدومين النظيف:\n"
            "                val domainModel = PassportData(vendorModel.docNumber, vendorModel.expiryDate)\n"
            "                continuation.resume(Result.success(domainModel))\n"
            "            }\n"
            "            override fun onScanFailed(errorCode: Int, message: String) {\n"
            "                continuation.resume(Result.failure(VendorScanException(errorCode, message)))\n"
            "            }\n"
            "        }\n"
            "        \n"
            "        vendorASdk.startScan(listener)\n"
            "        continuation.invokeOnCancellation { vendorASdk.cancel() }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. عند التبديل إلى Vendor B، نكتب فقط Adapter جديد بدون لمس أي ViewModel أو UI:\n"
            "class VendorBScannerAdapter(private val modernVendorB: VendorBClient) : DocumentScanner {\n"
            "    override suspend fun scanPassport(): Result<PassportData> {\n"
            "        return runCatching {\n"
            "            val result = modernVendorB.capture()\n"
            "            PassportData(result.passportNo, result.validUntil)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "To swap vendor SDKs with mismatched callbacks without breaking the app, establish a strict Anti-Corruption Layer (ACL). Define a clean domain interface representing your app's required capability. Implement the Adapter pattern to translate vendor-specific callbacks into standard Kotlin suspending functions or Flows via suspendCancellableCoroutine, keeping all vendor dependencies isolated inside a dedicated module.",
        "best_answer": (
            "When swapping third-party SDKs, the fatal mistake is allowing vendor-specific types, exceptions, and callback signatures to bleed into ViewModels and UI logic. If Vendor A uses listeners and Vendor B returns intents, changing vendors causes a ripple effect across the entire codebase.\n\n"
            "We solve this using three architectural boundaries:\n"
            "1. **Domain Contract**: We define a clean interface in our domain layer (`DocumentScanner` or `PaymentGateway`) expressing the business need using pure Kotlin types, completely agnostic of any vendor.\n"
            "2. **Adapter & Anti-Corruption Layer (ACL)**: Each vendor SDK gets an Adapter that implements this domain contract. The adapter bridges the callback mechanism into modern coroutines using `suspendCancellableCoroutine`, handles vendor lifecycle requirements, and maps vendor error codes into typed domain errors.\n"
            "3. **Physical Module Boundary**: We isolate each vendor SDK in its own Gradle module. The main application module depends on the domain interface, not the vendor SDK, guaranteeing at compile time that no vendor classes can leak into the rest of the application."
        ),
        "deep_answer": (
            "When engineering an Anti-Corruption Layer for vendor SDKs in enterprise Android apps, multiple edge cases must be handled beyond simple signature mapping:\n\n"
            "1. **Thread Hopping & Synchronization**: Vendor callbacks frequently fire on arbitrary background threads or private SDK loopers. The Adapter is responsible for ensuring continuation resumption occurs on appropriate dispatchers (`Dispatchers.Default` for parsing, or handling Android UI thread constraints).\n\n"
            "2. **Cancellation & Resource Cleanup**: If the calling coroutine cancels (e.g. user navigates back while the scanner is running), `suspendCancellableCoroutine.invokeOnCancellation` must instruct the vendor SDK to stop camera hardware, free native memory, or deregister listeners. Otherwise, you leak camera sensors and background threads.\n\n"
            "3. **Unified Error Semantics**: Vendor A might return HTTP 400 for expired documents, while Vendor B throws an unhandled `SdkInvalidStateException`. The Adapter catches all vendor exceptions, translating them into a unified sealed class hierarchy (`ScanFailure.DocumentExpired`, `ScanFailure.Timeout`, `ScanFailure.SecurityViolation`). The UI only ever responds to domain errors, remaining 100% resilient when swapping vendors."
        ),
        "follow_ups": [
            {
                "question": "Why should vendor SDKs live in separate Gradle modules?",
                "answer": "To enforce architectural boundaries at compile time; feature modules cannot accidentally import vendor classes, making vendor swaps zero-risk for UI code."
            },
            {
                "question": "What happens if a vendor callback invokes onSuccess multiple times?",
                "answer": "Inside `suspendCancellableCoroutine`, calling `resume` twice throws `IllegalStateException`. The Adapter must guard continuation resumption with an atomic check or use `callbackFlow` if multiple emissions are expected."
            }
        ]
    },
    {
        "id": "PAT-17",
        "arabic_explanation": (
            "الـ Singleton العام القابل للتعديل (Global Mutable Singleton) يجعل الاختبارات تعتمد على ترتيب التنفيذ (Order-Dependent). كيف تعيد تصميم ملكية البيانات (Ownership)؟\n\n"
            "1. ما هي مشكلة الـ Global Mutable Singleton؟\n   - كلاس معرّف كـ `object UserSession` في Kotlin يحتوي على متغيرات عامة: `var currentUser: User? = null` و `var authToken: String? = null`.\n   - **تلوث بيئة الاختبار (State Pollution)**: عند تشغيل Unit Tests على الـ JVM، تعمل جميع الاختبارات في نفس عملية الـ JVM Process. إذا قام `TestA` بتسجيل دخول مستخدم ونسي تفريغ الكائن، فإن `TestB` سيبدأ مع بيانات مستخدم موجودة مسبقاً، مما يؤدي إلى نجاح الاختبار عند تشغيله بمفرده وفشله الغامض عند تشغيل السلسلة كاملة (Flaky & Order-dependent tests).\n   - **Memory Leaks & Race Conditions**: إذا احتفظ الـ Singleton بمرجع لـ Context أو Activity، فإنه يسرّب الذاكرة طوال فترة حياة التطبيق، كما أن الوصول المتزامن من Threads متعددة بدون مزامنة يسبب تصادمات بيانات (Data Corruption).\n\n"
            "2. كيفية إعادة تصميم الملكية (Redesigning Ownership):\n   - **استبدال الـ `object` بـ Class عادي**: تحويل الـ Singleton من كائن ثابت عالمي إلى كلاس عادي يتم حقنه بواسطة Dependency Injection (`@Singleton` Scope في Hilt).\n   - **Constructor Injection**: تمرير الـ Session Holder عبر الـ Constructor لكل كلاس يحتاجه.\n   - **Test Isolation**: في الـ Unit Tests، يتم إنشاء نسخة جديدة تماماً من الكلاس لكل اختبار على حدة (`@Before fun setup()`), مما يضمن عزل الاختبارات بنسبة 100%."
        ),
        "practical_walkthrough": (
            "المقارنة بين Global Mutable Object وحامل حالة محقون معزول لكل اختبار:\n"
            "```kotlin\n"
            "// ❌ فوضى الـ Global Mutable Singleton: اختبارات ملوثة وتعتمد على الترتيب:\n"
            "object GlobalUserSession {\n"
            "    var token: String? = null // متغير عام يلوث الـ JVM Process في كل الاختبارات!\n"
            "    var userId: String? = null\n"
            "}\n"
            "\n"
            "// Test A يغير الحالة:\n"
            "@Test fun testLogin() {\n"
            "    GlobalUserSession.token = \"token_123\"\n"
            "    assertTrue(AuthManager.isLoggedIn())\n"
            "}\n"
            "// Test B يفشل لو اشتغل بعد Test A لأنه يتوقع مستخدم غير مسجل:\n"
            "@Test fun testLoggedOutState() {\n"
            "    // سيفشل هنا لأن GlobalUserSession.token لا يزال محتفظاً بقيمة token_123 من Test A!\n"
            "    assertFalse(AuthManager.isLoggedIn())\n"
            "}\n"
            "\n"
            "// ✅ الحل النظيف: كلاس عادي محقون بـ Scoped Ownership عبر Constructor Injection:\n"
            "interface SessionManager {\n"
            "    fun getToken(): String?\n"
            "    fun setToken(token: String?)\n"
            "}\n"
            "\n"
            "class DefaultSessionManager @Inject constructor(\n"
            "    private val storage: KeyValueStorage\n"
            ") : SessionManager {\n"
            "    private val _token = MutableStateFlow<String?>(null)\n"
            "    override fun getToken(): String? = _token.value\n"
            "    override fun setToken(token: String?) { _token.value = token }\n"
            "}\n"
            "\n"
            "// في الـ Tests: كل اختبار ينشئ نسخته المستقلة في @Before، عزل تام 100%:\n"
            "class AuthManagerTest {\n"
            "    private lateinit var sessionManager: SessionManager\n"
            "    private lateinit var authManager: AuthManager\n"
            "\n"
            "    @Before\n"
            "    fun setUp() {\n"
            "        sessionManager = FakeSessionManager() // نسخة جديدة طازجة لكل اختبار!\n"
            "        authManager = AuthManager(sessionManager)\n"
            "    }\n"
            "    \n"
            "    @Test fun testLoggedOutState() {\n"
            "        assertFalse(authManager.isLoggedIn()) // ينجح دائماً بغض النظر عن الترتيب!\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Global mutable singletons (`object` with `var`) persist state across test executions in the same JVM process, causing test order dependence and flakiness. Redesign ownership by turning the singleton into a standard class, injecting it via Constructor Injection, controlling its lifecycle scope through a DI container (like Hilt @Singleton), and creating fresh in-memory instances per test.",
        "best_answer": (
            "A global mutable singleton (`object Session { var user: User? }`) violates single ownership and destroys test determinism. Because JVM test runners reuse the same classloader process to run multiple test suites, mutations made by Test A persist into Test B. Tests become order-dependent: running Test B alone passes, but running the whole test suite fails.\n\n"
            "To fix this, we redesign state ownership:\n"
            "1. **Demote `object` to a Standard Class**: We replace the Kotlin `object` with an interface and a concrete class (`SessionManager`). The class encapsulates its state within thread-safe abstractions like `StateFlow`.\n"
            "2. **Explicit Constructor Injection**: Any ViewModel, Repository, or Interactor that needs session information declares `SessionManager` in its constructor. Nothing accesses ambient global state.\n"
            "3. **Container-Managed Scope**: In production, the DI container (Hilt) manages a single instance scoped with `@Singleton`. In JVM tests, we instantiate a fresh `FakeSessionManager` in `@Before`, guaranteeing 100% test isolation and determinism."
        ),
        "deep_answer": (
            "Beyond test ordering bugs, global mutable singletons introduce severe Android runtime vulnerabilities:\n\n"
            "1. **Process Death Vulnerability**: When Android terminates an app process in the background due to low memory, static variables are purged. When the user returns, the Activity is recreated, but the global singleton's state is reset to `null`, causing widespread `NullPointerExceptions` or forcing unexpected logouts. Proper ownership means persisting critical state to Room or encrypted DataStore, with the session manager reloading state reactively.\n\n"
            "2. **Concurrency and Visibility Hazards**: Naive global singletons with `var` fields lack memory barriers. If thread A writes `user = newProfile` and thread B reads it on another thread, thread B can observe stale cached CPU register values unless fields are `@Volatile` or guarded by a Mutex.\n\n"
            "3. **Stateless Utilities vs. State Holders**: Kotlin `object` is perfectly appropriate for stateless utilities (math functions, date formatters, serializers). It becomes toxic only when it holds mutable state. By moving state into injected repositories, we gain observability, thread-safety, and test parallelizability."
        ),
        "follow_ups": [
            {
                "question": "Is Kotlin `object` always bad in Android?",
                "answer": "No. Stateless singletons, single-instance formatters, sealed class objects, and pure utilities are great. It is mutable state (`var`) inside an `object` that causes architectural problems."
            },
            {
                "question": "What is the difference between a Singleton Pattern and a DI Singleton Scope?",
                "answer": "The Singleton Pattern enforces a single instance globally via a private constructor and static access. DI Singleton Scope lets the container create one instance for the app graph, but the class itself remains a normal class that can be easily instantiated multiple times in tests."
            }
        ]
    },
    {
        "id": "PAT-18",
        "arabic_explanation": (
            "كيف تتحول أنماط التصميم إلى تعقيد زائد وتشتت غير ضروري (Unnecessary Indirection)؟ مع مثال عملي:\n\n"
            "1. فخ الإفراط في تطبيق الأنماط (Over-Engineering & Pattern Abuse):\n   - يحدث التعقيد غير المبرر عندما يطبق المطور أنماط التصميم لمجرد تطبيقها، دون وجود مشكلة حقيقية تتطلب ذلك (المرونة الخيالية للمستقبل - Speculative Generality).\n   - النتيجة: شاشة بسيطة جداً تعرض قائمة عناصر ثابتة، تمر بـ 6 طبقات فارغة لا تفعل أي شيء سوى استدعاء الطبقة التي تليها:\n     `Screen -> ViewModel -> GetItemsUseCase -> ItemsFacade -> ItemsRepository -> ItemsAdapter -> ItemsDao`\n   - هذه الطبقات الفارغة تُعرف بـ **Pass-Through Indirection** أو **Middleman Code**.\n\n"
            "2. أضرار الـ Unnecessary Indirection في مشاريع Android:\n   - **صعوبة تتبع الكود واستكشاف الأخطاء (Cognitive Load & Debugging Hell)**: للانتقال من الضغط على الزر إلى قراءة قاعدة البيانات، تضطر للقفز بين 7 ملفات مختلفة لا تحتوي أي منها على منطق برمجي حقيقي.\n   - **بطء التطوير وتضخم الـ Boilerplate**: لإضافة حقل واحد، تضطر لتعديل 6 كلاسات و 6 اختبارات و 6 DTOs مختلفة.\n   - **تضخم الـ DI Graph**: استهلاك وقت تجميع أطول (Build Time) واستهلاك ذاكرة إضافي للكائنات غير الضرورية.\n\n"
            "3. المعيار الواقعي لمهندس البرمجيات الأول (Senior Rule of Thumb):\n   - أضف طبقة تجريد (Indirection) فقط عندما يكون هناك: **تعدد في التطبيقات (Multiple Implementations)**، أو **منطق عمل معقد قابل لإعادة الاستخدام (Reusable Domain Logic)**، أو **حدود استقرار لعزل تبعية خارجية متقلبة (Volatile Boundary)**. إذا كان الـ Use Case يكتفي بسطر واحد `repository.getData()` بدون أي شروط أو دمج، فاحذفه واستدعِ الـ Repository مباشرة من الـ ViewModel."
        ),
        "practical_walkthrough": (
            "المقارنة بين التعقيد الزائد المتكلف وبين التصميم العملي المباشر:\n"
            "```kotlin\n"
            "// ❌ تعقيد غير ضروري (Unnecessary Indirection): 4 طبقات وسيطة لا تفعل شيئاً سوى التمرير!\n"
            "class GetAppThemeUseCase @Inject constructor(private val repo: ThemeRepository) {\n"
            "    suspend operator fun invoke(): Theme = repo.getTheme() // مجرد وسيط فارغ!\n"
            "}\n"
            "class ThemeRepositoryImpl @Inject constructor(private val facade: ThemeFacade) : ThemeRepository {\n"
            "    override suspend fun getTheme(): Theme = facade.fetch() // وسيط آخر!\n"
            "}\n"
            "class ThemeFacade @Inject constructor(private val adapter: ThemeAdapter) {\n"
            "    suspend fun fetch(): Theme = adapter.get() // وسيط ثالث!\n"
            "}\n"
            "\n"
            "// ✅ تصميم مباشر وعملي (Pragmatic & Clean): ViewModel يتحدث مباشرة إلى Repository:\n"
            "interface ThemePreferences {\n"
            "    val isDarkMode: Flow<Boolean>\n"
            "    suspend fun setDarkMode(enabled: Boolean)\n"
            "}\n"
            "\n"
            "@HiltViewModel\n"
            "class SettingsViewModel @Inject constructor(\n"
            "    private val themePreferences: ThemePreferences\n"
            ") : ViewModel() {\n"
            "    val isDarkMode = themePreferences.isDarkMode.stateIn(\n"
            "        scope = viewModelScope,\n"
            "        started = SharingStarted.WhileSubscribed(5000),\n"
            "        initialValue = false\n"
            "    )\n"
            "    \n"
            "    fun toggleDarkMode(enabled: Boolean) {\n"
            "        viewModelScope.launch { themePreferences.setDarkMode(enabled) }\n"
            "    }\n"
            "}\n"
            "// وفرنا 4 كلاسات فارغة، كود مقروء في 10 ثوانٍ، وتكلفة صيانة صفرية!\n"
            "```"
        ),
        "quick_answer": "Design patterns turn into unnecessary indirection when abstractions are introduced without multiple implementations, complex domain logic, or volatile boundaries. A classic example is a 1-line 'pass-through' UseCase wrapping a Repository that wraps a Facade for simple read operations, dramatically increasing cognitive load, boilerplate, and build times without providing any architectural benefit.",
        "best_answer": (
            "Design patterns exist to manage variation and isolate volatile change. When applied dogmatically without actual variation, they create unnecessary indirection—often called 'speculative generality' or 'architecture astronautics'.\n\n"
            "A prime Android example is dogmatic Clean Architecture where every single screen must have a Use Case, even for trivial reads: `ViewModel -> GetUserProfileUseCase -> ProfileRepository -> ProfileDataSource -> Dao`. If `GetUserProfileUseCase` contains literally one line: `repository.getProfile()`, it adds zero value. It provides no validation, no composition, and no caching. Instead, it doubles the file count, bloats the Dagger dependency graph, increases build times, and forces developers to jump through five files just to understand a simple database query.\n\n"
            "A senior engineer practices pragmatic architecture: consume the `ProfileRepository` directly from the `ViewModel` for straightforward CRUD operations. Extract a Use Case only when you have business logic that orchestrates multiple repositories, applies complex calculation rules, or is reused across multiple ViewModels."
        ),
        "deep_answer": (
            "The cost of indirection is measured in **Cognitive Complexity, Build Overhead, and Refactoring Friction**.\n\n"
            "1. **The 'Tax' of an Abstraction**: Every layer requires: an interface, an implementation, DTO mapping functions, Dagger `@Provides` / `@Binds` bindings, and mock setup in unit tests. If the abstraction does not encapsulate volatility, you pay this architectural tax on every sprint without ever reaping the benefits.\n\n"
            "2. **Symptoms of Accidental Complexity in Codebases**:\n   - **Shotgun Surgery**: Adding a single boolean flag to an entity forces edits across 7 distinct files (DTO, Mapper, Domain Model, UseCase, Repository, ViewModel, UI State).\n   - **Pass-through Methods**: Methods whose sole implementation is `return collaborator.execute(args)` without mutation or validation.\n   - **Factories with Single Products**: Writing abstract factories for classes that will only ever have one concrete implementation on Android.\n\n"
            "3. **Pragmatic Heuristics (YAGNI & Rule of Three)**: Never introduce an abstraction for an anticipated future requirement. Wait until you have at least two distinct concrete implementations or concrete business rules before introducing a UseCase or Strategy. Simplicity is an active design decision, not a lack of design."
        ),
        "follow_ups": [
            {
                "question": "When IS a Use Case genuinely necessary in Android?",
                "answer": "When it coordinates multiple repositories (e.g., checkout requiring PaymentRepo, CartRepo, and InventoryRepo), applies complex domain validation rules, or is reused across multiple feature ViewModels."
            },
            {
                "question": "What is the difference between essential complexity and accidental complexity?",
                "answer": "Essential complexity is inherent to the business domain problem itself. Accidental complexity is introduced by the developer's choice of excessive layers, unnecessary patterns, and boilerplate."
            }
        ]
    }
]

def main() -> None:
    if DATA_FILE.exists():
        existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in existing}
    else:
        by_id = {}

    for item in PAT_13_18:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions PAT-13 to PAT-18. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
