#!/usr/bin/env python3
"""Elevate remaining COR questions (COR-11, COR-12, COR-13, COR-14, COR-15, COR-32)
for bilingual parity and authentic senior spoken answers.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import elevation_engine as ee

DATA = {}

# ==========================================
# COR-11: coroutineScope vs supervisorScope
# ==========================================
DATA["COR-11"] = {
    "concept_en": """In Kotlin coroutines, coroutineScope and supervisorScope are suspending scope functions that establish structured concurrency boundaries within a coroutine hierarchy. Both scope builders suspend their calling coroutine until all launched child tasks reach a terminal state, and both guarantee downward cancellation propagation when the enclosing parent job is cancelled. The critical distinction lies in their upward failure propagation mechanics. A coroutineScope creates a standard Job that enforces an all-or-nothing transactional contract: an unhandled exception in any single child immediately cancels the parent scope, which subsequently cancels all surviving sibling coroutines and rethrows the failure to the caller. Conversely, supervisorScope creates a SupervisorJob that isolates direct child failures. When a child coroutine within a supervisorScope fails with an uncaught exception, the supervisor scope suppresses upward cancellation, allowing sibling coroutines to continue executing unhindered while leaving error handling to the individual child caller.""",
    "walkthrough_en": """Illustrating all-or-nothing transactions versus independent dashboard widgets:
```kotlin
// Scenario A: All-or-nothing checkout transaction using coroutineScope
suspend fun executeCheckout(orderId: String): CheckoutResult = coroutineScope {
    // If tax calculation fails with a 500 server error, payment processing is cancelled immediately:
    val taxDeferred = async { taxService.calculateTax(orderId) }
    val paymentDeferred = async { paymentGateway.charge(orderId) }
    
    CheckoutResult(tax = taxDeferred.await(), receipt = paymentDeferred.await())
}

// Scenario B: Resilient dashboard using supervisorScope
suspend fun loadDashboard(): DashboardState = supervisorScope {
    val userProfile = async {
        try { userService.fetchProfile() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
    }
    val promotionBanners = async {
        try { promoService.fetchBanners() } catch (e: CancellationException) { throw e } catch (e: Exception) { emptyList() }
    }
    
    // A network failure in banners does not cancel the profile fetch:
    DashboardState(user = userProfile.await(), banners = promotionBanners.await())
}
```""",
    "short_en": """coroutineScope and supervisorScope both establish structured concurrency boundaries that wait for child completion, but differ in upward failure propagation. coroutineScope enforces fail-fast all-or-nothing semantics: if one child fails, it cancels the parent and all siblings. supervisorScope isolates direct child failures, allowing siblings to finish their tasks while the failed child handles its own error.""",
    "structured_en": """To begin with, both coroutineScope and supervisorScope establish structured concurrency boundaries that suspend until every child task completes execution.
From an architectural standpoint, the fundamental divergence is how they handle upward failure propagation. A standard coroutineScope enforces strict transactional consistency. If any child coroutine encounters an unhandled exception, it immediately cancels its parent Job, which cascades cancellation to all sibling coroutines and rethrows the root exception. This fail-fast behavior is essential for dependent operations such as atomic financial transactions where partial completion would corrupt application state.
In production scenarios, supervisorScope provides resilience by decoupling sibling lifecycles. It installs a SupervisorJob under the hood, meaning that an unhandled failure in one child does not cancel the supervisor parent and does not interrupt sibling tasks. This makes supervisorScope the premier choice for multi-widget user interfaces like e-commerce home screens, where a failure in a promotional banner must not prevent the user profile or notification counter from rendering.
As for boundary management, engineers must remember that downward cancellation remains identical in both builders. If the outer caller or ViewModelScope cancels, all child coroutines inside either scope builder are terminated immediately.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines, coroutineScope and supervisorScope differ in how their internal Job nodes respond to the childCancelled callback in JobSupport. In a coroutineScope, the underlying ScopeCoroutine node maintains a bidirectional relationship with its children. When a child throws an unhandled exception, it invokes parent.childCancelled(cause). The parent transitions its internal state machine from Active to Cancelling, posts cancellation tokens to its NodeList, and terminates all active siblings before rethrowing the exception from the scope's continuation.
In contrast, supervisorScope instantiates a SupervisorCoroutine. Its implementation overrides childCancelled to return false unconditionally. When a direct child fails, the supervisor acknowledges the notification without transitioning into the Cancelling state, effectively severing the upward failure chain. However, this isolation applies strictly to direct children. If a direct child of a supervisorScope launches grandchild coroutines using standard launch or async without establishing a nested supervisor, an unhandled failure in a grandchild will still tear down that direct child and its immediate siblings.
Furthermore, exception routing requires careful handling under supervision. In a supervisorScope, if an unhandled exception occurs inside a direct launch builder, the exception cannot travel up to the supervisor; therefore, it delegates immediately to the thread-level uncaught exception handler or CoroutineExceptionHandler, crashing the application if unhandled. With async builders, the exception is encapsulated inside the Deferred handle and remains dormant until await is invoked. Senior architects ensure that independent background tasks inside a supervisorScope either wrap their work in domain-safe try-catch blocks rethrowing CancellationException or attach dedicated exception handlers to prevent unexpected process crashes.""",
    "meta_ar": {
        "id": "COR-11",
        "questionAr": "قارن بين coroutineScope و supervisorScope مع توضيح آلية انتشار الأخطاء والإلغاء.",
        "topicAr": "الـ Coroutines والتزامن في Kotlin",
        "evaluates_ar": "- فهم شجرة الـ Job Hierarchy وتسلسل انتشار الإلغاء والأخطاء للأعلى وللأسفل.\n- التمييز بين نموذج المعاملة الواحدة (All-or-Nothing) ونموذج عزل المكونات (Fault Isolation).\n- التعامل الصحيح مع الاستثناءات المباشرة لتجنب انهيار التطبيق داخل supervisorScope.",
        "why_it_matters_ar": "كلا النطاقين يعلقان التنفيذ حتى اكتمال جميع المهام الفرعية التابعة لهما حفاظاً على الـ Structured Concurrency. لكن الاختيار الخاطئ بينهما يسبب كوارث برمجية؛ فاستخدام coroutineScope في شاشات لوحة التحكم يجعل فشل إعلان فرعي يسقط شاشة المستخدم بالكامل، بينما استخدام supervisorScope في المعاملات المالية المترابطة يسمح بخصم الرصيد حتى لو فشلت عملية تسجيل الفاتورة.",
        "worked_example_ar": "مقارنة عملية بين النطاقين في المعاملات الحسابية ولوحات التحكم:\n```kotlin\n// أولاً: معاملة تجميعية تتطلب النجاح الكامل:\nsuspend fun checkout(id: String) = coroutineScope {\n    val tax = async { calculateTax(id) }\n    val charge = async { chargeCard(id) }\n    Receipt(tax.await(), charge.await())\n}\n\n// ثانياً: شاشة متعددة الأجزاء تتطلب عزل الفشل:\nsuspend fun loadHome() = supervisorScope {\n    val user = async { fetchUser() }\n    val ads = async { fetchAds() } // لو فشل الإعلان، يستمر تحميل المستخدم بنجاح\n    HomeUi(user.await(), ads.await())\n}\n```",
        "trade_offs_ar": "يوفر coroutineScope أماناً حتمياً لمنع العمليات الجزئية المعلقة ويوقف الهدر البرمجي فوراً بمجرد سقوط أول مهمة. بينما يوفر supervisorScope مرونة عالية لعرض أجزاء الشاشة المستقلة، ولكنه يلقي بمسؤولية معالجة أخطاء كل طفل على عاتق المطور لمنع سقوط التطبيق.",
        "failure_modes_ar": "إطلاق كوروتين باستخدام launch داخل supervisorScope بدون التقاط الأخطاء أو وضع CoroutineExceptionHandler، مما يؤدي لانهيار التطبيق بالكامل لأن الخطأ لا يصعد للأب بل يذهب مباشرة للـ Thread Default Handler. خطأ آخر هو افتراض أن supervisorScope يعزل الأحفاد؛ بينما هو يعزل الأبناء المباشرين فقط.",
        "production_perspective_ar": "في تطبيقات التجارة والتكنولوجيا المالية، نستخدم coroutineScope لحساب السلة والدفع وحركات المخزن لمنع أي تناقض مالي. ونستخدم supervisorScope في الشاشات الرئيسية لعزل بطاقات الأخبار والتقييمات، مع تغليف كل استدعاء بكتلة Result آمنة تعيد رمي CancellationException صراحة.",
        "how_to_answer_ar": "- **التشابه المبدئي:** ابدأ بالتأكيد على أن كلاهما يعلق حتى انتهاء كل الأبناء ويدعم الإلغاء الهابط.\n- **الفارق الجوهري:** اشرح أن coroutineScope تطبق مبدأ All-or-Nothing بينما supervisorScope تعزل فشل الأبناء.\n- **سلوك الاستثناءات:** وضح مسار الصعود للأب في الأول، وتوقف الخطأ عند الطفل في الثاني.\n- **أمثلة الإنتاج:** قارن بين شاشة سداد الفاتورة وشاشة الـ Dashboard الرئيسية.\n- **تحذير هندسي:** نبه إلى أن الإلغاء القادم من الأب الخارجي يلغي كل الأطفال في الحالتين دون استثناء.",
        "talking_points_ar": "ناقش التعديل الداخلي لدالة childCancelled في SupervisorCoroutine حيث تعيد false دائماً، ومسار الاستثناءات غير الممسوكة في launch مقابل async، واستراتيجيات التعامل مع شاشات Compose متعددة المكونات.",
        "follow_ups_ar": "- **المحاور:** \"لو ألغينا الـ Scope الخارجي الحاوي لـ supervisorScope، ماذا يحدث للأبناء؟\"\n  **المرشح:** \"الإلغاء الهابط يعمل بنفس القوة في الحالتين؛ إلغاء الـ Scope الأكبر يلغي كل الكوروتينات التابعة له فوراً بغض النظر عن كون النطاق الداخلي Supervisor.\"\n\n- **المحاور:** \"ماذا يحدث لو أطلقنا launch داخل supervisorScope ورمى استثناء غير معالج؟\"\n  **المرشح:** \"لأن supervisorScope لا يستقبل الخطأ من ابنه، الاستثناء لن يصعد للأعلى، بل سيتوجه مباشرة للـ Thread Uncaught Exception Handler ويسبب انهيار التطبيق (Crash) ما لم يكن هناك CoroutineExceptionHandler مخصص.\"",
        "self_check_ar": "هل بينت أن كلاهما يعلق التنفيذ؟ هل وضحت صعود الفشل في coroutineScope وعزله في supervisorScope؟ وهل نبهت لسلوك الإلغاء القادم من الأعلى؟",
        "references_ar": "- [Kotlin Coroutines Scope Builders](https://kotlinlang.org/docs/coroutines-basics.html#scope-builder) — التوثيق الرسمي لبناة النطاقات.\n- [Supervision in Coroutines](https://kotlinlang.org/docs/exception-handling.html#supervision) — آليات العزل والتعامل مع أخطاء الأبناء.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "كلا النطاقين بيعلقوا التنفيذ لحد ما كل الأطفال يخلصوا ويدعموا انتشار الإلغاء للأسفل، لكن الفرق في مسار الأخطاء للأعلى؛ في coroutineScope لو طفل فشل بيلغي الأب وكل الإخوة فوراً بنظام الكل أو لا شيء. أما في supervisorScope ففشل الطفل معزول تماماً ومبيلغيش الأب ولا بيعطل باقي الإخوة.",
        "best_answer_ar": "الفرق الجوهري بين النطاقين بيتلخص في كيفية التعامل مع الأخطاء غير المتوقعة وصعودها في شجرة الكوروتينات.\n\nفي coroutineScope، التصميم مبني على مبدأ الكل أو لا شيء؛ لو بتنفذ تلات عمليات تابعة لطلب شراء زي حساب الضريبة وسحب الرصيد وتحديث المخزن، وفشل حساب الضريبة، النطاق هيلغي الأب فوراً والأب هيلغي باقي العمليات قبل ما تسحب فلوس المستخدم بدون داعي.\n\nأما supervisorScope فبيطبق مبدأ عزل الأعطال؛ مصمم لشاشات العرض المجمعة زي الصفحة الرئيسية لتطبيق توصيل، لو عندك استدعاء لبيانات العميل واستدعاء لصور الإعلانات واستدعاء للإشعارات، وسيرفر الإعلانات وقع، الـ supervisorScope بيسمح للطلب الفاشل ينتهي لوحده ويترك بيانات العميل والإشعارات تكمل وتتعرض بنجاح على الشاشة.\n\nوالنقطة المعمارية اللي لازم ننتبه ليها دايماً هي إن الإلغاء القادم من الأب الخارجي بيلغي الأطفال في الحالتين بنفس الطريقة؛ العزل بيخص فقط صعود الفشل من الأبناء للأعلى.",
        "deep_answer_ar": "على مستوى التصميم الداخلي لمكتبة kotlinx.coroutines، النطاقين بيعتمدوا على كلاسات مختلفة بتورث من ScopeCoroutine داخل ملفات JobSupport. في coroutineScope، الكائن الداخلي بيربط الأبناء برابطة ثنائية وثيقة؛ فلما طفل يرمي استثناء بينادي دالة parent.childCancelled، فبينتقل الأب لحالة Cancelling ويبث إشارات إلغاء لجميع العقد المسجلة في الـ NodeList.\n\nفي المقابل، supervisorScope بينشئ كائن SupervisorCoroutine بيعمل Override لدالة childCancelled بحيث ترجع دايماً false بدون ما تغير حالة الأب من Active لـ Cancelling، وده اللي بيكسر سلسلة انتشار الفشل للأعلى وبيحمي باقي الإخوة من التوقف المفاجئ.\n\nلكن في نقطة دقيقة جداً بيقع فيها كتير من المطورين في الإنتاج؛ العزل في supervisorScope بينطبق حصراً على الأبناء المباشرين فقط. لو أطلقت طفل مباشر، والطفل ده جواه أطلق أطفال تانيين بكوروتين scope عادي، أي فشل في الحفيد هيلغي الابن المباشر وإخوته داخل ذلك النطاق الفرعي لأن الإشراف لا يورث تلقائياً لأسفل الشجرة.\n\nكمان في التعامل مع دوال الإطلاق؛ لو استخدمت launch مباشر داخل supervisorScope بدون try-catch، الاستثناء مش هيطلع للأب ومش هيمسكه الـ Scope، بل هيتحول مباشرة للـ UncaughtExceptionHandler الخاص بالـ Thread ويفجر التطبيق بكراش كامل لو مفيش CoroutineExceptionHandler مثبت في الجذر. وأخيراً، في حالة إلغاء النطاق الأبوي نفسه، فإن إشارة الإلغاء تتدفق لأسفل وتنهي جميع الأبناء في كلا النطاقين فوراً دون استثناء للحفاظ على الذاكرة ومنع تسريب الثريدات."
    }
}

# ==========================================
# COR-12: Job vs SupervisorJob
# ==========================================
DATA["COR-12"] = {
    "concept_en": """In Kotlin's structured concurrency model, Job and SupervisorJob are the core implementations of the Job interface governing lifecycle, state management, and cancellation propagation. A standard Job enforces bidirectional cancellation propagation: if any child coroutine fails with an unhandled exception, that failure cancels the parent Job, which subsequently cancels all remaining child coroutines attached to it. This guarantees that operations operate as unified transactions where partial work is discarded upon error. A SupervisorJob alters this contract by enforcing unidirectional cancellation propagation: cancellation cascades downwards from the supervisor to its children, but failures within child coroutines do not propagate upwards to cancel the SupervisorJob or sibling jobs. This fault-isolation mechanism allows long-lived controllers, such as Android ViewModels and Application services, to execute independent concurrent tasks without allowing one failing routine to destroy the entire lifecycle scope.""",
    "walkthrough_en": """Demonstrating cancellation differences and the common parent-context trap:
```kotlin
// 1. Pitfall: Passing SupervisorJob directly as a context argument to a child builder
val scope = CoroutineScope(Dispatchers.Default)
scope.launch(SupervisorJob()) { // Ineffective: this creates a detached supervisor that is immediately overwritten!
    launch { throw RuntimeException("Child A died") }
    launch { delay(1000); println("Child B survived") } // Cancelled anyway because the parent launch is a standard Job!
}

// 2. Production Pattern: SupervisorJob at the scope root
class OrderManager : CoroutineScope {
    private val supervisor = SupervisorJob()
    override val coroutineContext = Dispatchers.Default + supervisor

    fun processOrders() {
        launch { syncInventory() } // Failure here does NOT cancel payment logging
        launch { logPaymentTelemetry() }
    }

    fun shutdown() {
        supervisor.cancel() // Downward cancellation terminates all active children cleanly
    }
}
```""",
    "short_en": """A standard Job propagates failure bidirectionally: if any child fails, it cancels its parent and all sibling coroutines. A SupervisorJob propagates cancellation only downwards: child failures do not cancel the parent or siblings. SupervisorJob is used at scope roots to isolate independent tasks, but cancelling the supervisor itself still terminates all children.""",
    "structured_en": """To begin with, the distinction between Job and SupervisorJob represents the foundation of lifecycle control and error containment in Kotlin coroutines.
From an architectural standpoint, a standard Job enforces bidirectional cancellation. When a child coroutine encounters an uncaught exception, it marks the parent Job as failed, causing the parent to immediately cancel all other active siblings. This fail-fast transactional design guarantees that tightly coupled subtasks do not waste device resources when a critical dependency fails.
In production scenarios, SupervisorJob implements fault isolation through unidirectional cancellation. Direct children manage their own failures independently; an uncaught exception in one child does not cancel the supervisor parent and does not interrupt sibling coroutines. This pattern forms the architectural backbone of framework scopes like Android's viewModelScope, where independent user interactions like fetching account details and tracking analytics must not interfere with each other.
As for boundary management, engineers must be cautious when passing SupervisorJob into builder parameters. Passing a SupervisorJob as an argument to launch creates a new job node that acts as a parent for that child's internal hierarchy, but does not convert an existing standard parent into a supervisor, often leading to surprising cancellation cascades if misconfigured.""",
    "deep_senior_en": """At the runtime implementation layer, both Job and SupervisorJob rely on JobSupport, which orchestrates a strict internal state machine comprising New, Active, Completing, Cancelling, and Cancelled states. The fundamental mechanical divergence lies in how child failure callbacks are processed. In a standard Job, when a child throws a non-cancellation exception, it notifies its parent via parentHandle.childCancelled(cause). JobSupport verifies the exception, transitions its state to Cancelling, and dispatches cancellation tokens to its internal NodeList, invoking cancel on every attached child continuation before transitioning to Cancelled.
SupervisorJob alters this pipeline through its SupervisorJobImpl specialization. It overrides the childCancelled method to return false unconditionally. When an uncaught exception occurs in a child, the supervisor acknowledges the completion but does not transition into the Cancelling state, leaving its other child nodes completely untouched in their Active state.
A critical nuance often tested in staff-level interviews involves the scope of supervision. Supervision is strictly one-level deep. If a SupervisorJob has a child launched with launch, that child is by default a standard Job. If that child subsequently launches its own subroutines, any uncaught exception among those subroutines will cancel that child and all its siblings at that lower tier, because supervision does not automatically inherit down arbitrary levels of the hierarchy unless explicitly constructed with supervisorScope.
Finally, lifecycle destruction requires explicit supervision management. In custom architectural components, engineers must retain a handle to the root SupervisorJob. Invoking supervisor.cancel() cascades downward through the entire tree, ensuring complete garbage collection and socket teardown when the component is destroyed.""",
    "meta_ar": {
        "id": "COR-12",
        "questionAr": "ما الفرق بين Job و SupervisorJob في كوتلن؟ ومتى تختار كلاً منهما؟",
        "topicAr": "الـ Coroutines والتزامن في Kotlin",
        "evaluates_ar": "- التمييز بين انتشار الإلغاء ثنائي الاتجاه في Job وأحادي الاتجاه في SupervisorJob.\n- إدراك حدود العزل ومصيدة تمرير SupervisorJob داخل معاملات دوال الإطلاق الفرعية.\n- توظيف SupervisorJob لإدارة دورة حياة المكونات الكبرى زي ViewModelScope.",
        "why_it_matters_ar": "الـ Job العادي يطبق سياسة الإلغاء التبادلي؛ سقوط أي ابن يلغي الأب وجميع الأبناء الآخرين. والـ SupervisorJob يعزل سقوط الأبناء المباشرين ويسمح للأب بالبقاء حياً. الفهم الخاطئ لهذه الآلية يسبب إلغاء مهام التطبيق الحيوية عند فشل نداء شبكة ثانوي، أو تسريب مهام خلفية لا تتوقف عند إغلاق الشاشة.",
        "worked_example_ar": "المقارنة وتفادي المصيدة الشائعة عند تمرير الـ Job:\n```kotlin\n// ❌ مصيدة شائعة: تمرير SupervisorJob داخل دالة الإطلاق لا يعزل الإخوة في النطاق الخارجي:\nscope.launch(SupervisorJob()) { \n    launch { error(\"Crash\") }\n    launch { delay(100); println(\"Won't print\") } // سيتلغي لأن الأب المباشر launch عادي!\n}\n\n// ✅ الاستخدام الهندسي الصحيح في جذر الـ Scope:\nclass AccountManager : CoroutineScope {\n    private val job = SupervisorJob()\n    override val coroutineContext = Dispatchers.Main + job\n\n    fun loadData() {\n        launch { fetchProfile() } // فشل هذا النداء لن يلغي نداء التنبيهات بالأسفل\n        launch { fetchNotifications() }\n    }\n    fun clear() = job.cancel() // الإلغاء الهابط يغلق كل العمليات بنظافة\n}\n```",
        "trade_offs_ar": "الـ Job العادي ممتاز للمهام الذرية المتكاملة لمنع ترك عمليات يتيمة قيد التنفيذ عند فشل أحد أركانها. بينما الـ SupervisorJob ممتاز للجذور الإدارية الكبرى مثل الشاشات والـ Services لعزل الأعطال، مع تحمله عبء مراقبة ومعالجة استثناءات كل مهمة منفردة.",
        "failure_modes_ar": "تمرير `SupervisorJob()` كمعامل داخل `launch` ظناً من المطور أنه يحول النطاق الخارجي إلى مشرف، في حين أنه ينشئ وظيفة فرعية معزولة فقط ويظل الأب عادياً يلغي باقي المهام. خطأ آخر هو نسيان استدعاء `cancel()` على الـ SupervisorJob عند تدمير المكون مما يسرب الذاكرة والثريدات.",
        "production_perspective_ar": "تعتمد بيئة أندرويد الرسمية على الـ SupervisorJob في بناء `viewModelScope` و `lifecycleScope`. هذا يضمن للمطور أن ضغط المستخدم على زر بحث فاشل لن يعطل عمل الـ ViewModel أو يلغي باقي عمليات تدفق البيانات، مع ضمان إيقاف جميع الكوروتينات فور خروج المستخدم من الشاشة.",
        "how_to_answer_ar": "- **الفرق المحوري:** وضح أن الـ Job ثنائي الاتجاه في الإلغاء والـ SupervisorJob أحادي الاتجاه (هابط فقط).\n- **آلية العمل:** بيّن كيف يلغي الابن الفاشل إخوته في الأول، وكيف يعزل الفشل في الثاني.\n- **سياق الاختيار:** Job للمهام المتكاملة المترابطة، و SupervisorJob لجذور الشاشات والخدمات.\n- **المصيدة الشائعة:** حذر من تمرير `SupervisorJob()` كمعامل لـ `launch`.\n- **دورة الحياة:** أكد أن إلغاء الـ SupervisorJob نفسه يلغي كل ما تحته هبوطاً.",
        "talking_points_ar": "اشرح التعديل البرمجي في SupervisorJobImpl لدالة childCancelled، والفرق بين المستويات المباشرة والأحفاد، وكيفية تصدير الأحداث عبر CoroutineExceptionHandler في المهام المعزولة.",
        "follow_ups_ar": "- **المحاور:** \"لو ألغينا SupervisorJob يدوياً، ماذا يحدث للأبناء المتصلين به؟\"\n  **المرشح:** \"سيلغى جميع الأبناء فوراً؛ الـ SupervisorJob يعزل صعود الفشل من الأسفل للأعلى فقط، لكن الإلغاء الهابط من الأعلى للأسفل يعمل بكامل طاقته الطبيعية.\"\n\n- **المحاور:** \"لماذا لا يجعل أندرويد كل الكوروتينات SupervisorJob افتراضياً؟\"\n  **المرشح:** \"لأن الفلسفة المعمارية للـ Coroutines قائمة على Structured Concurrency؛ المهام المرتبطة ببعضها يجب أن تفشل معاً لتفادي الهدر واستنزاف بطارية الهاتف في مهام فقدت قيمتها بعد فشل العملية الأساسية.\"",
        "self_check_ar": "هل فرقت بين الاتجاهين؟ هل حددت حالات استخدام كل منهما؟ هل وضحت مصيدة تمرير SupervisorJob في معاملات launch؟ وهل أكدت على الإلغاء الهابط؟",
        "references_ar": "- [Kotlin Coroutines Job documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-job/) — التوثيق الرسمي لواجهة Job.\n- [SupervisorJob specification](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-supervisor-job.html) — آلية عمل SupervisorJob وعزل الأخطاء.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "الـ Job العادي بيلغي الأب وباقي الإخوة لو أي طفل جواه فشل، بنظام الإلغاء ثنائي الاتجاه. أما الـ SupervisorJob فبيسمح بانتشار الإلغاء للأسفل فقط؛ لو طفل فشل، الأب بيفضل شغال وباقي الإخوة بيكملوا عادي، وده اللي مبني عليه الـ viewModelScope لعزل استدعاءات الشاشة المستقلة عن بعضها.",
        "best_answer_ar": "الفرق الجوهري بين Job و SupervisorJob هو في اتجاه انتشار الإلغاء والأخطاء داخل شجرة الـ Coroutines.\n\nفي الـ Job العادي، العلاقة ثنائية الاتجاه؛ لو عندك ثلاث عمليات شغالة بالتوازي وفشلت واحدة منهم باستثناء غير معالج، الفشل ده بيصعد للأب ويلغيه، والأب بيلغي تلقائياً باقي الإخوة. ده السلوك الافتراضي المثالي للمهام الذرية زي معالجة الصور أو الحسابات المالية التجميعية.\n\nأما الـ SupervisorJob فالاتجاه فيه أحادي من الأعلى للأسفل فقط. لو طفل من الأبناء المباشرين فشل، الـ SupervisorJob بيتجاهل إشارة الإلغاء وبيفضل نشط وبيسيب باقي الإخوة يكملوا شغلهم بنجاح. علشان كده بنستخدمه دايماً في جذور النطاقات الحيوية زي الـ viewModelScope علشان فشل تحميل إعلان أو صورة ميعطلش شاشة التطبيق كلها.\n\nبس لازم نحذر من مصيدة مشهورة، وهي تمرير SupervisorJob كمعامل داخل دالة `launch`؛ الحركة دي مش بتخلي الـ Scope الأصلي مشرف، دي بتعمل Job فرعي مستقل ومبتمنعش إلغاء الإخوة التابعين للأب الرئيسي.",
        "deep_answer_ar": "على مستوى الـ Low-level State Machine داخل كلاس JobSupport، كائنات Job بتدير دورة حياتها عبر حالات تبدأ من Active وتتحول لـ Completing أو Cancelling وتنتهي بـ Cancelled. لما طفل يواجه استثناء غير ممسوك، بيستدعي `parent.childCancelled(cause)`. في الـ Job القياسي، الاستدعاء ده بيحرك الأب فوراً لحالة Cancelling، وبيمر على قائمة الـ NodeList المترابطة ويلغي كل الـ Continuations المفتوحة.\n\nالـ SupervisorJob بيطبق نفس المنظومة دي بالظبط مع اختلاف جوهري واحد في كلاس `SupervisorJobImpl`؛ وهو إنه بيعمل Override لدالة `childCancelled` بحيث تعيد duma `false`. ده معناه إن الأب بيستلم إشعار انتهاء الطفل، لكن مبيتحولش لحالة Cancelling، وبكده بتفضل باقي العقد في الـ NodeList شغالة في حالة Active بدون أي مساس.\n\nالنقطة المعمارية العميقة اللي بنسأل فيها مهندسي الـ Senior هي نطاق العزل (Scope of Supervision)؛ الإشراف مبيورثش تلقائياً لجميع مستويات الشجرة. لو الـ SupervisorJob أطلق ابناً عادياً باستخدام launch، الابن ده هيكون Job عادي؛ ولو الابن ده أطلق أطفال تحته وواحد فيهم فشل، الابن وأطفاله هيتدمروا بالكامل لأن العزل محصور في الأبناء المباشرين للمشرف فقط.\n\nوأخيراً في إدارة الذاكرة، الـ SupervisorJob مبيخلصش لوحده أبداً حتى لو كل أطفاله انتهوا؛ لازم المطور يستدعي `cancel()` صراحة عند تدمير المكون المرتبط به في بيئة العمل لتفكيك شجرة المراجع وتفادي تسريب الذاكرة."
    }
}

# =======================================================
# COR-13: Child coroutine failure (Parent & Siblings)
# =======================================================
DATA["COR-13"] = {
    "concept_en": """When a child coroutine fails with an uncaught exception, the behavior of its parent and siblings is governed entirely by the parent's Job type within structured concurrency. In a standard Job hierarchy (such as inside coroutineScope or plain launch), an uncaught exception in a child is propagated upward to the parent immediately. The parent cancels all other active sibling coroutines with a CancellationException, terminates itself, and rethrows the original triggering exception to its own parent or caller. This fail-fast mechanism prevents orphaned tasks and state inconsistencies. Conversely, in a supervised hierarchy (such as supervisorScope or a scope backed by a SupervisorJob), upward cancellation is severed: the parent ignores the child's failure and remains active, and surviving siblings continue their execution unaffected. However, in both models, if the failure cause is a CancellationException, it represents normal cooperative cancellation and never cancels the parent or siblings.""",
    "walkthrough_en": """Demonstrating parent and sibling fate in standard versus supervised hierarchies:
```kotlin
// 1. Standard Hierarchy: Child failure cancels parent and siblings immediately
runBlocking {
    val parentJob = launch {
        val child1 = launch {
            delay(500)
            println("Child 1 completed") // Never executes!
        }
        val child2 = launch {
            delay(50)
            throw IllegalStateException("Child 2 failed unexpectedly") // Triggers cascade
        }
    }
    parentJob.join() // Parent fails and throws IllegalStateException
}

// 2. Supervised Hierarchy: Sibling isolation
runBlocking {
    supervisorScope {
        val child1 = launch {
            delay(200)
            println("Child 1 survived and completed successfully!") // Prints successfully
        }
        val child2 = launch {
            delay(50)
            // Error logged by CEH; child1 continues unaffected:
            throw IllegalStateException("Child 2 failed")
        }
    }
}
```""",
    "short_en": """In a standard Job hierarchy, an uncaught exception in a child immediately cancels the parent, which cancels all sibling coroutines (fail-fast). In a supervised hierarchy (SupervisorJob or supervisorScope), the parent survives, siblings continue running undisturbed, and only the failing child terminates. CancellationException never cancels parents or siblings in either hierarchy.""",
    "structured_en": """To begin with, predicting the fate of a parent and sibling coroutines upon child failure is a core structured concurrency requirement.
From an architectural standpoint, the outcome depends strictly on whether the parent node is a standard Job or a SupervisorJob. In a standard Job tree, failure propagation is immediate and bidirectional. An uncaught exception causes the child to invoke cancellation on its parent, which instantly cancels all sibling coroutines with CancellationException before cancelling itself and escalating the error upward. This fail-fast approach guarantees that dependent operations do not waste CPU cycles or produce corrupted partial state.
In production scenarios, supervised trees decouple sibling fates. Under a SupervisorJob or supervisorScope, the parent intercepts the child's termination without transitioning to a cancelled state, allowing remaining siblings to complete their operations successfully. This isolation is mandatory in user-facing dashboards where independent network calls should not terminate one another.
As for boundary management, an essential exception to this rule is CancellationException. When a child coroutine is cancelled via CancellationException, it unbinds cleanly without affecting its parent or siblings under both standard and supervised hierarchies.""",
    "deep_senior_en": """At the internal coroutines runtime level, when a coroutine encounters an uncaught throwable, its completion handler invokes notifyParent with the failure cause. The parent JobSupport evaluates whether the throwable is a CancellationException. If the throwable is an operational failure like IOException or NullPointerException, a standard Job marks itself as Cancelling, constructs a parent-originated CancellationException wrapping the root cause, and traverses its child NodeList to notify all sibling ChildHandles. Each sibling continuation is resumed with this CancellationException, tearing down their respective stack frames cooperatively.
Once all siblings acknowledge cancellation and finish their active blocks, the parent aggregates any secondary exceptions that occurred during teardown into suppressed exceptions attached to the primary root cause. The parent then completes exceptionally and passes the aggregated exception to its outer continuation or uncaught exception handler.
Under a SupervisorJob, the childCancelled callback intercepts the notification and returns false. The parent neither transitions into Cancelling nor touches the NodeList of siblings. Because the parent refuses to handle the error, the responsibility for the uncaught exception shifts back to the child coroutine. If the child was created using launch, the exception is dispatched to the thread's CoroutineExceptionHandler. If the child was created with async, the exception is cached inside the Deferred result until await is called.
Staff engineers design architectures around these mechanics: wrapping parallel async operations in coroutineScope when results are mutually dependent, and using supervisorScope with individual try-catch blocks when partial rendering is acceptable.""",
    "meta_ar": {
        "id": "COR-13",
        "questionAr": "ماذا يحدث للأب والإخوة عندما تفشل كوروتين فرعية (Child Coroutine)؟",
        "topicAr": "الـ Coroutines والتزامن في Kotlin",
        "evaluates_ar": "- معرفة المسار الكامل لانتشار الفشل عبر شجرة الـ Job ومصير الإخوة والأب.\n- التمييز بين الاستثناءات التشغيلية الحقيقية وبين إشارة الإلغاء التعاوني CancellationException.\n- فهم تجميع الاستثناءات الثانوية (Suppressed Exceptions) عند إلغاء الأب.",
        "why_it_matters_ar": "التحكم في مصير العمليات المتزامنة عند حدوث عطل هو جوهر الـ Structured Concurrency. الجهل بسلوك الإلغاء يؤدي إلى استمرار مهام عديمة الجدوى في استنزاف الموارد، أو انهيار عمليات حيوية بالتتابع لمجرد تعثر عملية ثانوية واحدة.",
        "worked_example_ar": "سلوك الكوروتينات عند فشل طفل في بيئة عادية وبيئة مشرفة:\n```kotlin\n// في بيئة عادية: سقوط الطفل الثاني يلغي الأول فوراً:\ncoroutineScope {\n    launch { delay(500); println(\"لن يطبع أبداً\") }\n    launch { delay(100); throw RuntimeException(\"فشل الطفل 2\") }\n}\n\n// في بيئة مشرفة: يستمر الطفل الأول في العمل بنجاح:\nsupervisorScope {\n    launch { delay(500); println(\"سيكتمل ويطبع بنجاح\") }\n    launch { delay(100); throw RuntimeException(\"فشل الطفل 2\") }\n}\n```",
        "trade_offs_ar": "إلغاء الإخوة التلقائي في الـ Job العادي يمنع هدر المعالج والذاكرة ويحمي من تناقض البيانات، لكنه يضحي بالمرونة. بينما عزل الإخوة في المشرف يزيد من مرونة الواجهة، لكنه يفرض على المطور كتابة كود مخصص لإلغاء العمليات المرتبطة يدوياً إذا تطلب المنطق ذلك.",
        "failure_modes_ar": "الاعتقاد بأن `CancellationException` سيلغي الأب والإخوة، في حين أن النظام يتجاهله كإنهاء طبيعي. خطأ آخر هو نسيان أن الإخوة الذين ينفذون عمليات حظر غير قابلة للتعليق (Blocking I/O) لن يتوقفوا فوراً عند وصول إشارة الإلغاء مما يتطلب فحص `isActive` دورياً.",
        "production_perspective_ar": "في شاشات التحميل المزدوج، نحدد التبعية بوضوح؛ إذا كان الكود يحسب سلة الشراء فإننا نعتمد على الإلغاء الفوري للجميع لتفادي طلبات ناقصة. وإذا كانت الشاشة تعرض بيانات الملف الشخصي والصورة وبطاقة العضوية، فإننا نعتمد على المشرف لعزل كل بطاقة على حدة.",
        "how_to_answer_ar": "- **القاعدة الذهبية:** الإجابة تعتمد على نوع الأب: هل هو Job عادي أم SupervisorJob؟\n- **حالة الـ Job العادي:** اشرح الإلغاء السريع (Fail-Fast) للأب وجميع الإخوة.\n- **حالة المشرف:** وضح بقاء الأب واستمرار الإخوة وعزل الطفل الفاشل.\n- **استثناء الإلغاء:** أكد أن `CancellationException` لا يلغي الأب أو الإخوة في الحالتين.\n- **العمق الداخلي:** اذكر تجميع الأخطاء الثانوية كـ Suppressed Exceptions.",
        "talking_points_ar": "اشرح تفاصيل رسائل NodeList الداخلية، وتجميع الاستثناءات في كائن Throwable واحد، والفرق في وصول الخطأ للـ CoroutineExceptionHandler بين launch و async.",
        "follow_ups_ar": "- **المحاور:** \"لو طفل فرعي رمى `CancellationException`، هل سيلغى الأب والإخوة؟\"\n  **المرشح:** \"لا إطلاقاً، الـ `CancellationException` يُعامل كإشارة تحكم وليس كعطل برمجي؛ ينتهي الطفل بهدوء ويظل الأب وباقي الإخوة يعملون بنشاط كامل في كلا النطاقين.\"\n\n- **المحاور:** \"لو حدثت عدة أخطاء أثناء إلغاء الإخوة في نفس اللحظة، كيف يحتفظ كوتلن بها؟\"\n  **المرشح:** \"الخطأ الأول الذي فجر الإلغاء يكون هو الاستثناء الأساسي، وباقي الاستثناءات التي تحدث في الإخوة يتم إلحاقها به كـ Suppressed Exceptions عبر دالة `Throwable.addSuppressed()`.\"",
        "self_check_ar": "هل فرقت بين الـ Job العادي والمشرف؟ هل استثنيت CancellationException؟ وهل بينت مصير الاستثناءات الثانوية؟",
        "references_ar": "- [Exception handling in Kotlin Coroutines](https://kotlinlang.org/docs/exception-handling.html) — الدليل الرسمي لانتشار الأخطاء والإلغاء.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "الإجابة بتعتمد تماماً على نوع الأب؛ لو الأب Job عادي ففشل الطفل باستثناء غير معالج بيلغي الأب فوراً، والأب بيلغي كل الإخوة الشغالين معاه بنظام Fail-Fast. أما لو الأب SupervisorJob، فالأب بيفضل حي وباقي الإخوة بيكملوا شغلهم عادي، والـ CancellationException مبيأثرش على الأب أو الإخوة في الحالتين.",
        "best_answer_ar": "المصير اللي بيلقاه الأب وباقي الإخوة بيتحدد بنوع الـ Parent Job اللي بتنتمي له الكوروتين.\n\nفي الشجرة العادية المعتمدة على Job قياسي، السلوك بيكون Fail-Fast وصارم جداً؛ بمجرد ما يضرب استثناء غير معالج في كوروتين فرعية، الخطأ بيصعد فوراً للأب، والأب بيبعت إشارات إلغاء لجميع الإخوة الشغالين بالتوازي ويلغي نفسه كمان، وده سلوك ممتاز بيحمي النظام من استهلاك موارد في عمليات ملهاش فائدة بعد فشل جزء أساسي منها.\n\nأما لو الشجرة معتمدة على SupervisorJob أو supervisorScope، فآلية العزل بتشتغل؛ الأب بيتجاهل فشل الابن ده وبيفضل في حالة Active، وباقي الإخوة بيكملوا تنفيذ دوالهم بدون أي مقاطعة، والابن الفاشل بس هو اللي بينتهي.\n\nونقطة مهمة جداً لازم نوضحها في المقابلة: لو كان سبب فشل الطفل هو `CancellationException` صريح، ده مش بيعتبر عطل، ومبيلغيش الأب ولا بيمس باقي الإخوة إطلاقاً في أي من الحالتين.",
        "deep_answer_ar": "على مستوى الـ Runtime الخاص بـ kotlinx.coroutines، لما كوروتين فرعية تضرب استثناء، دالة الـ Completion بتستدعي إشعار `notifyParent(cause)`. لو الاستثناء مش CancellationException، الـ JobSupport الخاص بالأب العادي بيتحول فوراً لحالة Cancelling، وبيمشي في حلقة على الـ NodeList المرتبطة بيه وينادي `child.cancel()` لكل الإخوة التانيين عبر الـ ChildHandles الخاصة بيهم.\n\nكل الإخوة بيستلموا إشارة الإلغاء كـ CancellationException بيلتف حول السبب الأصلي، والـ Continuations بتاعتهم بتتفكك تباعاً. ولو أي أخ منهم ضرب استثناء تاني أثناء محاولة التنظيف في finally، الـ Runtime بيجمع الاستثناءات دي ويلحقها بالاستثناء الرئيسي كـ Suppressed Exceptions باستخدام آلية `Throwable.addSuppressed` في الـ JVM قبل ما يصعد الخطأ للأعلى.\n\nأما في حالة الـ SupervisorJob، فاستدعاء `childCancelled` بيرجع false فوراً، فالأب مبيغيرش حالته ومبيلمسش الـ NodeList نهائياً، وده اللي بيسيب الإخوة في حالة شغالين بأمان.\n\nلكن العبء هنا بيتحول للابن نفسه؛ لو كان شغال بـ launch، الخطأ اللي مش ممسوك هيروح للـ Thread Default Uncaught Exception Handler ويسبب كراش لو مفيش CoroutineExceptionHandler، ولو كان شغال بـ async، الخطأ هيفضل محبوس جوه الـ Deferred لحد ما حد يستدعي await. وده اللي بيخلينا نلتزم بقاعدة معمارية صارمة: تغليف العمليات المتوازية في `coroutineScope` لو النتائج معتمدة على بعضها، واستخدام `supervisorScope` مع `try-catch` محلية لو بنبني واجهات مستقلة تقبل العرض الجزئي."
    }
}

# =======================================================
# COR-14: CoroutineExceptionHandler
# =======================================================
DATA["COR-14"] = {
    "concept_en": """CoroutineExceptionHandler (CEH) is an optional CoroutineContext element that serves as a global last-resort safety net for unhandled exceptions in Kotlin coroutines. It operates analogously to Thread.setDefaultUncaughtExceptionHandler in standard Java concurrency. Crucially, CEH executes only when installed on a root coroutine launched with the launch builder, or when installed on a root SupervisorJob/supervisorScope. It does not run for child coroutines, because child coroutines unconditionally delegate their uncaught exceptions up to their parent job in the hierarchy. Furthermore, CEH does not handle exceptions originating from the async builder, because async encapsulates failures inside its Deferred result. Most importantly, CEH is purely a diagnostic and reporting mechanism: by the time CEH is invoked, the coroutine has already terminated and its call stack has unwound, meaning CEH cannot recover execution, retry operations, or prevent scope cancellation.""",
    "walkthrough_en": """Demonstrating valid CEH placement versus common silent failure scenarios:
```kotlin
// 1. Ineffective placement: CEH installed on a child coroutine (Silently ignored!)
val scope = CoroutineScope(Dispatchers.Default)
val childHandler = CoroutineExceptionHandler { _, exception ->
    println("Caught: $exception") // NEVER RUNS!
}
scope.launch {
    launch(childHandler) { // Child delegates to parent; childHandler is ignored!
        throw IllegalStateException("Child failure")
    }
}

// 2. Production Placement: CEH installed at the root scope
val rootHandler = CoroutineExceptionHandler { _, exception ->
    FirebaseCrashlytics.getInstance().recordException(exception)
    Telemetry.logFatalCoroutineError(exception)
}

val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default + rootHandler)
applicationScope.launch {
    // Uncaught exception here reaches rootHandler cleanly without crashing the process
    performBackgroundSync()
}
```""",
    "short_en": """CoroutineExceptionHandler is a last-resort logging element for uncaught exceptions. It only runs when attached to a root coroutine launched with launch or on a root supervisor scope. It does not run on child coroutines (which delegate to their parent), does not handle async errors (which are held in Deferred), and cannot recover or resume execution.""",
    "structured_en": """To begin with, CoroutineExceptionHandler functions as a global uncaught exception listener rather than an inline error-handling control structure.
From an architectural standpoint, the handler executes only under two strict conditions. First, it must be installed either on a root CoroutineScope or directly on a root launch builder. Second, the operation must be launched via launch rather than async. When an unhandled exception reaches the root of the coroutine hierarchy without being caught by try-catch blocks, the framework delegates the uncaught throwable to the CoroutineExceptionHandler.
In production scenarios, engineers frequently misunderstand where the handler does not help. It is completely ignored when installed on a child coroutine, because child tasks automatically delegate failure propagation to their parent Job. Furthermore, it does not catch exceptions thrown inside async builders, because async encapsulates failures inside the returned Deferred instance until await is invoked.
As for boundary management, CoroutineExceptionHandler is strictly a terminal reporting tool. It is designed to log crashes to telemetry engines like Crashlytics or present generic error dialogues; it cannot recover the failed operation, suppress scope cancellation, or retry the transaction.""",
    "deep_senior_en": """At the lower plumbing level of kotlinx.coroutines, exception handling follows a strict escalation ladder defined in handleCoroutineException. When a coroutine launched with launch terminates with an uncaught exception, it attempts to notify its parent via childCancelled. If the parent is a standard Job, the parent absorbs the error and propagates it upward. This upward delegation continues recursively until the error reaches the root of the hierarchy.
Only when the root Job completes exceptionally does the runtime invoke handleCoroutineException(context, exception). The runtime inspects the root CoroutineContext for a registered CoroutineExceptionHandler. If discovered, its handleException method is invoked synchronously. If no handler is found in the context, the runtime iterates through Java ServiceLoader instances of CoroutineExceptionHandler, and finally falls back to the current Thread's uncaughtExceptionHandler, which typically terminates the Android OS process with a fatal crash.
This mechanism illuminates why attaching a handler to an async coroutine does nothing. The async builder instantiates a DeferredCoroutine, which overrides handleJobException to return false, suppressing invocation of handleCoroutineException. The exception is stored in the internal state of the DeferredCoroutine until await is called, at which point the continuation unrolls and rethrows the original exception directly at the await call site.
Staff Android engineers enforce three rules: use inline try-catch or runSuspendCatching at repository boundaries for recoverable business logic; attach a CoroutineExceptionHandler to global application scopes exclusively for telemetry and crash reporting; and never rely on handlers for control flow.""",
    "meta_ar": {
        "id": "COR-14",
        "questionAr": "متى يعمل CoroutineExceptionHandler وأين يفشل ولا يقدم أي فائدة؟",
        "topicAr": "الـ Coroutines والتزامن في Kotlin",
        "evaluates_ar": "- الفهم الدقيق للشروط الصارمة لتفعيل CoroutineExceptionHandler في شجرة الكوروتينات.\n- معرفة الأماكن التي يتم تجاهل الـ Handler فيها تماماً (الأبناء، وبناة async).\n- إدراك طبيعة الـ Handler كأداة تسجيل أخطاء نهائية وليست آلية تعافي أو إعادة محاولة.",
        "why_it_matters_ar": "الـ CoroutineExceptionHandler هو الملاذ الأخير لالتقاط الاستثناءات غير المعالجة، والخلط بينه وبين كتل try-catch العادية يسبب كراشات مباغتة في الإنتاج؛ لأن وضعه على كوروتين فرعية أو مع async لا يحمي التطبيق من الانهيار ولا يمنع إلغاء شجرة المهام.",
        "worked_example_ar": "الموضع الصحيح والموضع الخاطئ للـ CoroutineExceptionHandler:\n```kotlin\n// ❌ موضع عديم الفائدة: وضعه على طفل فرعي (لن يستدعى أبداً!):\nscope.launch {\n    launch(CoroutineExceptionHandler { _, e -> println(\"لن يعمل!\") }) {\n        throw RuntimeException(\"الطفل يسلم الخطأ للأب ويتجاهل الـ Handler\")\n    }\n}\n\n// ✅ الموضع الإنتاجي الصحيح: وضعه في جذر الـ Scope لتسجيل الأعطال:\nval crashHandler = CoroutineExceptionHandler { _, exception ->\n    FirebaseCrashlytics.getInstance().recordException(exception)\n}\nval appScope = CoroutineScope(SupervisorJob() + Dispatchers.IO + crashHandler)\nappScope.launch {\n    performUnsafeBackgroundSync()\n}\n```",
        "trade_offs_ar": "استخدام الـ Handler في جذر التطبيق يمنع انهيار العملية (Process Crash) ويسجل الأعطال في أدوات المراقبة، لكنه لا يعيد تشغيل المهمة الفاشلة. المعالجة المحلية عبر try-catch تتيح التعافي وإظهار رسائل مخصصة للمستخدم لكنها تتطلب كتابة كود إضافي في كل طبقة.",
        "failure_modes_ar": "تثبيت الـ Handler على دالة `async` وتوقع التقاط الخطأ، في حين أن `async` تحتفظ بالاستثناء داخل `Deferred` حتى استدعاء `await()`؛ وإذا لم يستدعَ `await()` وظل النطاق حياً قد يفلت الخطأ بصمت أو يسقط الأب. خطأ آخر هو محاولة استئناف الكوروتين من داخل الـ Handler؛ فالكوروتين تكون قد ماتت بالفعل.",
        "production_perspective_ar": "في تطبيقات المؤسسات، نربط CoroutineExceptionHandler وحيد على مستوى ApplicationScope لنقل الأخطاء غير المتوقعة إلى Firebase Crashlytics و Datadog، مع منع استخدامه لإدارة منطق الأعمال العادي الذي يُدار حصراً داخل المستودعات عبر أنماط النتيجة الآمنة.",
        "how_to_answer_ar": "- **التعريف المعماري:** هو شبكة أمان أخيرة (Last-resort) تشبه UncaughtExceptionHandler في الجافا.\n- **شروط العمل:** يعمل فقط في الكوروتين الجذرية (Root) ومع دالة `launch` حصراً.\n- **أين يفشل:** لا يعمل مع الأبناء (لأنهم يسلمون للأب)، ولا مع `async`، ولا يتيح التعافي أو إعادة المحاولة.\n- **حالة الكوروتين:** أكد أن الكوروتين تكون قد انتهت بالفعل عند استدعائه.\n- **الاستخدام في الإنتاج:** تسجيل تقارير الانهيار في الـ Telemetry.",
        "talking_points_ar": "اشرح مسار تصعيد الخطأ الداخلي عبر handleCoroutineException، واستخدام ServiceLoader للبحث عن Handlers عامة، وسلوك DeferredCoroutine في قمع الإبلاغ اللحظي.",
        "follow_ups_ar": "- **المحاور:** \"لو وضعنا الـ Handler على `async` في جذر الـ Scope، هل سيعمل؟\"\n  **المرشح:** \"لا، لأن `async` مصممة لتغليف نتيجتها (سواء كانت نجاحاً أو فشلاً) داخل كائن `Deferred`. الخطأ لن يخرج للـ Handler بل سيُرمى حصراً عند استدعاء `await()` في الكود المستدعي.\"\n\n- **المحاور:** \"هل يمكنني إعادة تشغيل الكوروتين من داخل `CoroutineExceptionHandler`؟\"\n  **المرشح:** \"لا يمكن إطلاقاً؛ لأن الكوروتين عند وصول الخطأ للـ Handler تكون قد تدمرت وتفكك الـ Stack الخاص بها تماماً. وظيفة الـ Handler تنحصر في المراقبة وتسجيل الأخطاء وإظهار تنبيهات عامة.\"",
        "self_check_ar": "هل حددت شرطي العمل (جذر + launch)؟ هل أوضحت لماذا يفشل مع الأبناء ومع async؟ وهل أكدت على استحالة التعافي بعد استدعائه؟",
        "references_ar": "- [CoroutineExceptionHandler documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-exception-handler/) — التوثيق الرسمي ومحددات الاستخدام.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "الـ CoroutineExceptionHandler هو شبكة أمان أخيرة للأخطاء غير الممسوكة؛ بيشتغل في حالة واحدة بس: لما يكون محطوط في الـ Root Coroutine ومع دالة `launch` حصراً. ومبيشتغلش مع الأبناء لأنهم بيسلموا أخطاءهم للأب، ومبيشتغلش مع `async` لأنها بتخزن الخطأ جوه الـ Deferred، وميقدرش يعيد تشغيل الكوروتين لأنها بتكون ماتت بالفعل.",
        "best_answer_ar": "الـ CoroutineExceptionHandler مش بديل للـ try-catch ومش أداة لإدارة تدفق العمليات اليومية، ده مجرد Global Safety Net شبيه بـ UncaughtExceptionHandler بتاع الجافا.\n\nعلشان يشتغل، لازم يتوفر شرطين صارمين: أولاً يكون محطوط في جذر النطاق (Root Scope) أو على دالة `launch` جذرية مباشرة. ثانياً تكون العملية معمولة بـ `launch` مش `async`؛ فلو اتحط على كوروتين فرعية (Child)، هيتم تجاهله تماماً لأن الطفل بموجب قواعد الـ Structured Concurrency بيسلم خطأه للأب فوراً.\n\nأما الأماكن اللي ملوش فيها أي لازمة: أولاً مع دوال `async`؛ لأن `async` بتحبس الاستثناء جوا كائن الـ `Deferred` ومش بتطلعه إلا عند استدعاء `await()`. ثانياً في محاولات استئناف الكود أو الـ Retry؛ لأن لما الـ Handler بيتم استدعاؤه، الكوروتين بتكون اتلغت وتفككت وانتهت دورة حياتها بالفعل.\n\nفي بيئات العمل، بنستخدمه في مكان واحد بس: بنربطه بالـ Application Scope لحفظ وتصدير تقارير الأخطاء غير المتوقعة لمنصات الـ Telemetry زي Crashlytics.",
        "deep_answer_ar": "على مستوى الـ Low-level Call Stack في `kotlinx.coroutines`، لما كوروتين تفشل بينادي النظام دالة `handleCoroutineException(context, exception)`. الدالة دي بتبدأ تفتش في سياق الكوروتين الجذرية عن كائن مسجل لنوع `CoroutineExceptionHandler.Key`.\n\nلو الكوروتين كانت طفل وسيط، كلاس `JobSupport` بيحول الخطأ للأعلى عبر `parent.childCancelled` وبالتالي الـ Context الخاص بالطفل بيتم تجاوزه بالكامل، وده السبب الهندسي اللي بيخلي أي Handler محطوط على طفل عديم القيمة تماماً.\n\nأما في حالة `async`، الكلاس المسؤول هو `DeferredCoroutine`، والكلاس ده بيعمل Override لدالة `handleJobException` بحيث ترجع `false` وتكتم الإبلاغ اللحظي، فالمكتبة بتفترض إن المستدعي هيستلم النتيجة عبر `await()` ويتعامل معاها، فمبيتمش استدعاء أي Handler حتى لو كان في الجذر.\n\nولو مفيش أي Handler مسجل في جذر النطاق، النظام بيبحث عن طريق الـ Java ServiceLoader عن أي كلاسات مثبتة على مستوى الـ Classpath، وأخيراً بيصعد الخطأ لـ `Thread.currentThread().uncaughtExceptionHandler`، وده اللي بيفجر التطبيق بكراش كامل في أندرويد.\n\nعلشان كده مهندسي الـ Staff بيعتبروا الـ CEH مجرد أداة رصد وتشخيص في أعلى طبقة من التطبيق، بينما منطق الأعمال بيتم حمايته محلياً باستخدام `runSuspendCatching` والتأكد من إعادة رمي `CancellationException`. وبالتالي في التطبيقات الإنتاجية الضخمة بنمنع الاعتماد على الـ CEH لإدارة منطق الأعمال أو إعادة المحاولة، وبنحصره فقط في طبقة الـ Crash Reporting."
    }
}

# =======================================================
# COR-15: launch exceptions vs async exceptions
# =======================================================
DATA["COR-15"] = {
    "concept_en": """The critical distinction between launch and async in Kotlin coroutines lies in their return abstractions and exception propagation timelines. The launch builder is a fire-and-forget orchestrator that returns a Job. Exceptions thrown inside launch propagate eagerly and immediately up the job hierarchy to the parent and thread-level uncaught exception handlers. Conversely, async returns a Deferred handle representing a future computation result. In a root coroutine, async encapsulates exceptions inside the Deferred instance, remaining dormant until the consumer explicitly invokes await, at which point the stored exception is rethrown directly into the caller's call stack. However, when async is invoked as a child inside a standard coroutineScope, its unhandled exception immediately propagates upward to cancel the parent scope, regardless of whether await was ever called.""",
    "walkthrough_en": """Comparing exception timing in launch versus root async and child async:
```kotlin
// 1. launch: Eager and immediate propagation
scope.launch {
    throw IllegalStateException("Fails immediately!") // Crashes process or hits CEH immediately
}

// 2. Root async: Exception is encapsulated until await() is called
val deferred = scope.async {
    throw IllegalStateException("Deferred failure")
}
delay(1000) // Exception remains completely silent here!
try {
    deferred.await() // The exception is rethrown right here!
} catch (e: IllegalStateException) {
    println("Caught during await: ${e.message}")
}

// 3. Child async trap: Inside coroutineScope, child async cancels parent immediately!
coroutineScope {
    val task = async { throw RuntimeException("Child async failed") }
    // Even if we NEVER call task.await(), the parent scope is cancelled right now!
}
```""",
    "short_en": """launch exceptions propagate eagerly and immediately up the job hierarchy, triggering cancellation and uncaught exception handlers. Root async exceptions are encapsulated inside the Deferred handle and are only rethrown when await() is called. However, a child async inside coroutineScope still cancels its parent immediately even before await() is invoked.""",
    "structured_en": """To begin with, the fundamental divergence between launch and async centers on exception delivery timing and result representation.
From an architectural standpoint, launch is designed for fire-and-forget side effects and returns a Job. When an uncaught exception occurs inside launch, it propagates eagerly and immediately up the job hierarchy. If unhandled, it cancels the parent scope and dispatches to the CoroutineExceptionHandler or crashes the application thread.
In production scenarios, async is designed for computations that return values, producing a Deferred instance. When async operates as a root coroutine, it encapsulates unhandled exceptions inside the Deferred container. The exception remains completely dormant and unobserved until a consumer invokes await, which unpacks the result and rethrows the original exception directly at the await call site where standard try-catch blocks can recover it.
As for boundary management, engineers must be aware of the child async trap. When async is invoked as a child inside a standard coroutineScope, structured concurrency still applies upward failure propagation immediately, cancelling the parent and sibling coroutines even if await is never invoked.""",
    "deep_senior_en": """At the lower runtime tier, launch and async instantiate StandaloneCoroutine and DeferredCoroutine respectively. Both extend AbstractCoroutine, but override exception handling hooks differently. In StandaloneCoroutine, when an unhandled exception triggers completion, handleJobException invokes handleCoroutineException immediately, escalating the failure to the context hierarchy.
DeferredCoroutine alters this contract by overriding handleJobException to return false. Instead of escalating the error, it transitions its internal state machine to CompletedExceptionally, packaging the Throwable into an internal CompletedExceptionally wrapper. When a caller subsequently invokes await, the continuation checks the state machine; if exceptionally completed, it unpacks the throwable and throws it into the caller's stack frame via recoverStackTrace, preserving both the asynchronous dispatch trace and the current suspension point.
However, this encapsulation is frequently misunderstood in the context of child hierarchies. When async is called within a standard coroutineScope, the child still notifies its parent via parentHandle.childCancelled(cause). Unless the parent is a supervisorScope or backed by a SupervisorJob, the parent Job immediately enters the Cancelling state, tearing down all sibling coroutines before the consumer ever reaches the await statement.
Staff engineers enforce strict patterns: use launch with structured exception handlers for terminal background actions; use async wrapped inside supervisorScope with local try-catch blocks around await calls when parallel tasks must be isolated; and never leave a Deferred handle un-awaited in long-lived scopes.""",
    "meta_ar": {
        "id": "COR-15",
        "questionAr": "ما الفرق الجوهري في معالجة الاستثناءات بين launch و async؟",
        "topicAr": "الـ Coroutines والتزامن في Kotlin",
        "evaluates_ar": "- استيعاب توقيت ظهور الاستثناءات بين الإطلاق الفوري (Eager) في launch والتأجيل في async.\n- فهم دور كائن Deferred في احتجاز وتغليف الأخطاء حتى استدعاء await.\n- إدراك فخ الـ Child async داخل coroutineScope وإلغائه للأب حتى بدون await.",
        "why_it_matters_ar": "الخلط بين launch و async في معالجة الأخطاء يسبب مشاكل معقدة في الإنتاج؛ إما ابتلاع أخطاء حرجة بصمت لأن المطور نسي استدعاء await على async، أو سقوط شاشة التطبيق بالكامل لأن المطور اعتقد أن async تعزل أخطاءها تلقائياً داخل coroutineScope العادي.",
        "worked_example_ar": "توقيت ظهور الخطأ في launch مقابل async وفخ الكوروتين الفرعية:\n```kotlin\n// 1. launch: الخطأ ينفجر فوراً ويصعد للأعلى:\nscope.launch {\n    throw RuntimeException(\"ينفجر فوراً\")\n}\n\n// 2. الجذرية async: الخطأ يظل محبوساً حتى await():\nval deferred = scope.async {\n    throw RuntimeException(\"محبوس في الـ Deferred\")\n}\ndelay(1000) // لا يحدث أي كراش هنا!\ntry {\n    deferred.await() // ينفجر الخطأ هنا حصراً\n} catch (e: Exception) {\n    println(\"تم التقاط الخطأ بنجاح\")\n}\n\n// 3. فخ الطفل async: يلغي الأب فوراً حتى لو لم ننادِ await():\ncoroutineScope {\n    val task = async { error(\"فشل\") } // يلغي الـ Scope فوراً!\n}\n```",
        "trade_offs_ar": "توفر launch وضوحاً في تنفيذ المهام التي لا تنتج قيمة (Fire-and-forget) مع ظهور فوري للأعطال. بينما توفر async إمكانية انتظار القيم ومعالجة أخطائها موضعياً عند استدعاء await، لكنها تتطلب انتباهاً دائماً لمنع بقاء استثناءات معلقة دون استهلاك.",
        "failure_modes_ar": "إطلاق مهام بـ async دون استدعاء `await()` أبداً، مما يخفي استثناءات خطيرة في السيرفر إذا كان النطاق مستقلاً. خطأ آخر هو محاولة تغليف استدعاء `async` نفسه بكتلة `try-catch` بدلاً من تغليف استدعاء `await()`، فالخطأ لا يرمى وقت إنشاء الكوروتين بل وقت استهلاك النتيجة.",
        "production_perspective_ar": "في طبقات الـ Repository والـ UseCases، نعتمد على الدوال المعلقة `suspend` الصريحة التي تعيد `Result<T>`. وإذا احتجنا للتوازي عبر `async`، نغلف العمليات داخل `supervisorScope` ونستدعي `await()` داخل كتل `try-catch` مخصصة تعيد رمي `CancellationException`.",
        "how_to_answer_ar": "- **الفارق الأساسي:** launch للأفعال المجردة واستثناءاتها فورية؛ و async للقيم واستثناءاتها مؤجلة في Deferred.\n- **توقيت الاستثناء:** وضح متى يرمى الخطأ في async (عند await حصراً).\n- **فخ الـ Child Async:** بيّن أن async كطفل داخل coroutineScope يلغي الأب فوراً حتى لو لم تستدعِ await.\n- **مكان الـ try-catch:** أكد على وضع الـ catch حول `await()` وليس حول `async { }`.\n- **حل الإنتاج:** الجمع بين supervisorScope و try-catch حول await.",
        "talking_points_ar": "ناقش الفرق الداخلي بين StandaloneCoroutine و DeferredCoroutine، وكيفية تغليف الخطأ في CompletedExceptionally، وآلية recoverStackTrace لإظهار مسار التعليق في سجل الأخطاء.",
        "follow_ups_ar": "- **المحاور:** \"لو وضعت `try-catch` حول دالة `async { throw Exception() }`، هل ستمسك الخطأ؟\"\n  **المرشح:** \"لا، لأن إنشاء الكوروتين بـ async ينجح فوراً ويعيد كائن Deferred؛ الاستثناء يحدث داخل الكوروتين في الخلفية ولا يرمى في خيط الاستدعاء إلا عند مناداة `await()`، لذلك الـ try-catch يجب أن تحيط بـ `deferred.await()`.\"\n\n- **المحاور:** \"ماذا يحدث لو كان لدينا async كطفل داخل `coroutineScope` ولم نستدعِ `await()` أبداً؟\"\n  **المرشح:** \"سيلغى الـ coroutineScope بالكامل وتلغى باقي الكوروتينات الشقيقة فوراً؛ لأن كونه طفلاً يجعله يبلغ الأب بالفشل عبر structured concurrency بغض النظر عن استدعاء await من عدمه.\"",
        "self_check_ar": "هل وضحت الفارق في توقيت الاستثناء؟ هل بينت دور Deferred و await؟ وهل حذرت من فخ الطفل async داخل coroutineScope؟",
        "references_ar": "- [Async builders and exception handling](https://kotlinlang.org/docs/exception-handling.html#async-and-await) — التوثيق الرسمي لتعامل async مع الاستثناءات.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "استثناءات `launch` بتظهر فوراً وبتصعد للأعلى في شجرة الـ Job وتلغي الأب أو تروح للـ Handler، لأنها مهام بدون ناتج مباشر. أما استثناءات `async` الجذرية بتتحبس جوه كائن الـ `Deferred` ومبتظهرش إلا لما تستدعي `await()`. لكن لو `async` كانت طفل جوه `coroutineScope` عادي، هتلغي الأب فوراً حتى لو مناديتش `await()`.",
        "best_answer_ar": "الفارق الجوهري بين launch و async بيتلخص في توقيت وكيفية تسليم الخطأ للمستدعي.\n\nدالة `launch` مصممة لمهام Fire-and-forget ومبترجعش قيمة، فعلشان كده استثناءاتها بتكون فورية؛ أول ما يحصل عطل بيصعد في الشجرة ويلغي الأب ويبلغ الـ CoroutineExceptionHandler أو يفجر كراش لو مفيش معالجة.\n\nأما دالة `async` فمصممة لحساب قيمة مستقبلية وترجع كائن `Deferred`. في الكوروتين الجذرية، الاستثناء بيتم تغليفه واحتجازه داخل الـ Deferred ويفضل نايم وميعملش أي صوت لحد ما المستدعي يطلب النتيجة بـ `await()`. وساعتها بس الخطأ بيترمي في وش المستدعي ويقدر يمسكه بكتلة `try-catch` عادية.\n\nولكن فيه فخ معماري خطير بيقع فيه كتير من المهندسين؛ لو `async` اتعملت كطفل فرعي جوه `coroutineScope` عادي، قواعد الـ Structured Concurrency الصارمة بتخلي الطفل يبلغ الأب فوراً بالعطل، فالـ Scope كله بيتلغي وباقي الإخوة بيقفوا لحظياً حتى لو المطور مكنش استدعى `await()` أصلاً.\n\nعلشان كده في الإنتاج، لو محتاجين ننتظر نتائج متوازية مع عزل الأعطال، بنشغل الـ async جوه `supervisorScope` وبنحط `try-catch` حول نداء `await()` نفسه.",
        "deep_answer_ar": "على مستوى الـ Implementation الداخلي لمكتبة الكوروتينات، دالة launch بتنشئ كائن `StandaloneCoroutine` بينما async بتنشئ `DeferredCoroutine`. الاتنين بيرثوا من `AbstractCoroutine`، لكن الاختلاف الجوهري بيكون في دالة `handleJobException`.\n\nفي `StandaloneCoroutine`، الدالة دي بتنادي `handleCoroutineException` فوراً لتصعيد الخطأ. أما في `DeferredCoroutine`، فالدالة بتعمل Override وترجع `false` وتكتم التصعيد المباشر؛ وبدل كده بتحول الـ State Machine لحالة `CompletedExceptionally` وبتغلف الـ Throwable جوه كائن داخلي.\n\nولما يجي الكود ينادي `await()`، الـ Continuation بتفحص حالة الكائن؛ لو لقت فيه عطل استثنائي بتفكك الغلاف وترمي الاستثناء الأصلي جوه الـ Call stack بتاع المستدعي باستخدام آلية `recoverStackTrace` علشان تدمج الـ Stack trace بتاع التعليق غير المتزامن مع مكان الاستدعاء الحالي وتسهل تصحيح الكود.\n\nالمأزق بيظهر لما تكون `DeferredCoroutine` شغالة كطفل تابع لـ Job قياسي؛ لأن آلية انتهاء الكوروتين الفرعية بتستدعي إشعار الأب عبر `childCancelled` حتى مع كتمان `handleJobException`. فالأب العادي بيتحول لحالة Cancelling ويفكك كل الأبناء التانيين فوراً.\n\nعلشان كده كـ Senior Engineers، بنمنع تماماً ترك كائنات `Deferred` يتيمة بدون استدعاء `await()`، وبنلزم الفرق بتغليف التوازي داخل `supervisorScope` مع معالجة الأخطاء عند استدعاء `await` وضمان استمرار انتشار `CancellationException`. كما يجب التأكد من عدم استخدام async للمهام التي لا تنتج قيمة لتفادي حبس الاستثناءات بصمت، واستبدالها صراحة بـ launch مع مراقبة دورة حياة النطاق الحاوي."
    }
}

# =======================================================
# COR-32: Testing cancellation, supervision, timeouts
# =======================================================
DATA["COR-32"] = {
    "concept_en": """Testing asynchronous Kotlin coroutines deterministically requires eliminating real-world time dependencies, thread race conditions, and arbitrary delays such as Thread.sleep. The official kotlinx-coroutines-test library achieves this through runTest, TestScope, and the StandardTestDispatcher backed by a virtual TestCoroutineScheduler. In this testing environment, time is completely simulated: delaying calls like delay(10_000) do not block real CPU time, but instead enqueue scheduled execution tokens into the virtual scheduler. Test authors control time progression explicitly using advanceTimeBy, runCurrent, and advanceUntilIdle. This enables deterministic verification of edge cases including timeout triggers (such as withTimeoutOrNull), cooperative cancellation cascades, and sibling isolation under supervision, ensuring that multi-threaded concurrent edge cases execute reproducibly in milliseconds in continuous integration environments.""",
    "walkthrough_en": """Testing timeout triggers and supervisor fault isolation deterministically:
```kotlin
// In a unit test using kotlinx-coroutines-test:
@Test
fun testSearchTimeoutAndSupervisorIsolation() = runTest {
    val testDispatcher = StandardTestDispatcher(testScheduler)
    val repository = SearchRepository(dispatcher = testDispatcher)

    // 1. Test timeout triggering without real-world delay:
    var searchResult: SearchOutcome? = null
    launch {
        searchResult = withTimeoutOrNull(5000) {
            repository.searchRemote("query") // internally delays 6000ms
        }?.let { SearchOutcome.Success(it) } ?: SearchOutcome.TimedOut
    }

    advanceTimeBy(4999)
    assertEquals(null, searchResult) // Still awaiting

    advanceTimeBy(2) // Advances past the 5000ms timeout boundary
    assertEquals(SearchOutcome.TimedOut, searchResult)

    // 2. Test supervision isolation deterministically:
    var task1Completed = false
    var task2Failed = false
    supervisorScope {
        launch {
            delay(1000)
            task1Completed = true
        }
        launch {
            delay(200)
            task2Failed = true
            throw RuntimeException("Task 2 network crash")
        }
    }
    advanceUntilIdle()
    assertTrue(task1Completed) // Sibling survived and executed
    assertTrue(task2Failed)
}
```""",
    "short_en": """Testing coroutines deterministically requires runTest and StandardTestDispatcher from kotlinx-coroutines-test. Delay calls register on a virtual TestCoroutineScheduler rather than blocking real threads. Using advanceTimeBy, runCurrent, and advanceUntilIdle, tests advance virtual time instantly to verify timeouts, cancellation, and supervision deterministically without flakiness.""",
    "structured_en": """To begin with, testing concurrent coroutines deterministically requires replacing real wall-clock delays with simulated virtual time.
From an architectural standpoint, the kotlinx-coroutines-test library provides runTest and the StandardTestDispatcher, which share a centralized TestCoroutineScheduler. When coroutines invoke delay or withTimeout, execution frames are queued onto the virtual scheduler rather than sleeping operating system threads. This allows tests that simulate multi-minute timeouts to execute deterministically in just a few milliseconds.
In production scenarios, test authors control coroutine interleaving using explicit scheduler primitives. Calling advanceTimeBy moves virtual time forward by an exact millisecond interval, allowing precise assertions before and after timeout boundaries. Calling runCurrent executes any pending tasks scheduled for the exact current virtual timestamp, while advanceUntilIdle flushes all queued coroutines until the queue is completely drained.
As for boundary management, deterministic testing requires strict dependency injection of CoroutineDispatchers. Repositories and ViewModels must never hard-code Dispatchers.IO or Dispatchers.Default, but instead accept CoroutineDispatcher instances via constructor injection, enabling test suites to inject the TestScope's StandardTestDispatcher or UnconfinedTestDispatcher.""",
    "deep_senior_en": """Under the hood of kotlinx-coroutines-test, runTest constructs a TestScope backed by a TestCoroutineScheduler that intercepts all time-delayed continuation resumptions. The scheduler maintains an internal priority queue of scheduled tasks ordered by virtual target timestamps. When a coroutine invokes delay(N), it registers a CancellableContinuation with the scheduler at currentTime + N and suspends.
The distinction between StandardTestDispatcher and UnconfinedTestDispatcher is critical when testing complex state machines. StandardTestDispatcher queues all launched coroutines into the scheduler, executing them only when the test explicitly advances the clock or invokes runCurrent. This provides complete control over execution interleaving, enabling developers to simulate race conditions and thread interleaving with mathematical precision. Conversely, UnconfinedTestDispatcher eagerly runs coroutines until their first suspension point, which simplifies simple synchronous assertions but obscures concurrent execution ordering.
Testing cancellation and supervision requires verifying continuation states and exception handling contracts. When testing withTimeout, moving virtual time past the threshold throws a TimeoutCancellationException that cancels the inner scope; asserting that resources such as database locks are freed inside finally blocks verifies leak-free teardown. When testing supervisor hierarchies, tests can assert that an uncaught exception in one child leaves sibling continuations intact in the scheduler queue, completing successfully when advanceUntilIdle is called.
In enterprise CI pipelines, senior engineers forbid Thread.sleep and arbitrary polling loops. By combining runTest with injected test dispatchers and strict TestScope assertions, teams achieve 100% deterministic, zero-flakiness test suites running at native CPU execution speeds.""",
    "meta_ar": {
        "id": "COR-32",
        "questionAr": "كيف تختبر الإلغاء والتزامن والإشراف والمهلات الزمنية (Timeouts) في الكوروتينات بشكل حتمي؟",
        "topicAr": "الـ Coroutines والتزامن في Kotlin",
        "evaluates_ar": "- توظيف مكتبة kotlinx-coroutines-test ودالة runTest والـ StandardTestDispatcher.\n- التحكم في الوقت الافتراضي (Virtual Time) عبر advanceTimeBy و advanceUntilIdle.\n- حقن الـ Dispatchers معمارياً لاختبار المهلات الزمنية والإلغاء دون بطء أو فحص عشوائي.",
        "why_it_matters_ar": "الاعتماد على التأخير الزمني الفعلي زي `Thread.sleep` أو `delay` الحقيقي يجعل اختبارات الوحدة بطيئة جداً ومتقلبة (Flaky Tests) وتسقط في بيئات الـ CI بسبب تباين سرعة المعالجات. الاختبار الحتمي باستخدام الوقت الافتراضي يختبر سيناريوهات التزامن المعقدة والمهلات الطويلة في أجزاء من الألف من الثانية وبدقة 100%.",
        "worked_example_ar": "اختبار مهلة زمنية وعزل المشرف باستخدام الوقت الافتراضي بدون أي تأخير حقيقي:\n```kotlin\n@Test\nfun testTimeoutAndSupervision() = runTest {\n    val dispatcher = StandardTestDispatcher(testScheduler)\n    var completed = false\n\n    // اختبار timeout قدره 5 ثوانٍ يكتمل افتراضياً في ميلي ثانية واحدة:\n    val job = launch(dispatcher) {\n        withTimeout(5000) {\n            delay(6000) // يتجاوز المهلة\n            completed = true\n        }\n    }\n    advanceTimeBy(5001) // تقديم الوقت الافتراضي لتفجير المهلة فوراً\n    advanceUntilIdle()\n    assertTrue(job.isCancelled) // تم الإلغاء الحتمي بنجاح\n    assertFalse(completed)\n}\n```",
        "trade_offs_ar": "الـ StandardTestDispatcher يوفر تحكماً حتمياً كاملاً في ترتيب تداخل الخيوط ولكنه يتطلب استدعاء دوال تحريك الوقت يدوياً. بينما الـ UnconfinedTestDispatcher ينفذ الكود فوراً وبشكل أبسط لكنه يخفي تفاصيل تداخل المهام المتزامنة الحساسة.",
        "failure_modes_ar": "استخدام `Thread.sleep` داخل اختبارات الكوروتينات، مما يحظر الخيط الفعلي ولا يقدم الوقت الافتراضي فيفشل الاختبار. خطأ آخر هو تثبيت `Dispatchers.IO` بشكل صلب داخل الكلاسات بدلاً من حقنه، مما يجعل الكود يهرب من بيئة الاختبار الافتراضية ويعمل على خيوط حقيقية تسبب فشلاً عشوائياً.",
        "production_perspective_ar": "في الفرق الهندسية الكبيرة، نمنع دمج أي كود يحتوي على `Thread.sleep` عبر قواعد فحص آلية. نحقن `CoroutineDispatcher` عبر Hilt أو Koin، ونبني اختبارات ViewModel تعتمد على `MainDispatcherExtension` لضبط خيط الـ Main الافتراضي، مما يضمن تشغيل آلاف الاختبارات في ثوانٍ معدودة وبدون أي Flakiness.",
        "how_to_answer_ar": "- **الأساس الهندسي:** استخدام مكتبة kotlinx-coroutines-test ودالة `runTest` للتحكم في الوقت الافتراضي.\n- **محرك الاختبار:** اشرح دور `StandardTestDispatcher` والـ `TestCoroutineScheduler`.\n- **دوال التحكم:** وضح الفرق بين `advanceTimeBy` للمهلات و `advanceUntilIdle` لإفراغ الطابور و `runCurrent`.\n- **المتطلب المعماري:** أكد على ضرورة حقن الـ Dispatchers لمنع تثبيت IO أو Default.\n- **الموثوقية:** بيّن كيف يمنع هذا النهج الـ Flaky Tests في الـ CI.",
        "talking_points_ar": "ناقش الفرق بين StandardTestDispatcher و UnconfinedTestDispatcher، وآلية إدارة طابور الأولويات في TestCoroutineScheduler، واختبار استثناءات TimeoutCancellationException وتفكيك الموارد في finally.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق بين `advanceUntilIdle()` و `runCurrent()` في الاختبارات؟\"\n  **المرشح:** \"دالة `runCurrent()` بتنفذ فقط المهام المجدولة في اللحظة الزمنية الحالية (Current Virtual Timestamp) بدون تقديم الوقت. أما `advanceUntilIdle()` فبتفضل تقدم الوقت وتنفذ كل المهام المؤجلة في الطابور لحد ما الطابور يفضى تماماً.\"\n\n- **المحاور:** \"كيف تختبر ViewModel بيستخدم `Dispatchers.Main` بدون ما يضرب كراش في الـ Unit Tests؟\"\n  **المرشح:** \"بنعمل JUnit Test Rule أو Extension بتستدعي `Dispatchers.setMain(testDispatcher)` قبل بدء الاختبار، وبتعمل `Dispatchers.resetMain()` في الـ tearDown، وده بيخلي كل العمليات الموجهة للـ Main تشتغل على الـ Test Scheduler الافتراضي.\"",
        "self_check_ar": "هل شرحت فكرة الوقت الافتراضي ومكتبة الاختبار؟ هل فرقت بين دوال تحريك الوقت؟ وهل أكدت على حقن الـ Dispatchers كشرط أساسي؟",
        "references_ar": "- [Testing Kotlin Coroutines](https://developer.android.com/kotlin/coroutines/test) — إرشادات أندرويد الرسمية لاختبار الكوروتينات.\n- [kotlinx-coroutines-test guide](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — توثيق بيئة runTest والـ Schedulers.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
        "quick_answer_ar": "بنختبر الكوروتينات بحتمية وسرعة باستخدام مكتبة `kotlinx-coroutines-test` ودالة `runTest` مع `StandardTestDispatcher`. ده بيخلي الوقت افتراضي بالكامل؛ فاستدعاءات `delay` مبتحظرش خيوط حقيقية، وبنقدر نقدم الوقت بالملي ثانية عبر `advanceTimeBy` لاختبار الـ Timeouts ونفرغ العمليات بـ `advanceUntilIdle` بدون أي بطء أو Flakiness.",
        "best_answer_ar": "اختبار الكوروتينات بدون Flakiness بيتطلب الاستغناء التام عن الوقت الحقيقي وعن دوال زي `Thread.sleep`.\n\nبنعتمد على دالة `runTest` من مكتبة `kotlinx-coroutines-test`، ودي بتشغل الكود داخل بيئة بتتحكم في الوقت الافتراضي (Virtual Time) عن طريق `TestCoroutineScheduler`. لما الكود ينادي `delay(10000)`، النظام مش بينام عشر ثواني؛ هو بيسجل المهمة في طابور افتراضي، وبنقفل أو نختبر المهلة في جزء من الألف من الثانية.\n\nوعلشان نختبر سيناريوهات دقيقة، بنستخدم دوال التحكم في الـ Scheduler: دالة `advanceTimeBy` بنحرك بيها الوقت لقيمة محددة علشان نتأكد هل الـ Timeout ضرب ولا لسه، ودالة `runCurrent` بتنفذ المهام المجدولة في نفس اللحظة، ودالة `advanceUntilIdle` بتخلص كل العمليات المعلقة في الخلفية.\n\nوالشرط المعماري الأهم لنجاح الاختبارات دي هو حقن الـ Dispatchers (Dependency Injection)؛ لازم الكلاسات متكونش مثبتة `Dispatchers.IO` بداخلها، بل تستقبل الـ Dispatcher في الـ Constructor علشان نقدر نمرر ليها الـ TestDispatcher أثناء الاختبار.",
        "deep_answer_ar": "على مستوى الـ Test Framework، دالة `runTest` بتنشئ كائن `TestScope` مربوط بـ `TestCoroutineScheduler` بيدير طابور أولويات (Priority Queue) منظم بحسب التوقيت الافتراضي للـ Continuations المعلقة.\n\nالفرق الجوهري بين `StandardTestDispatcher` و `UnconfinedTestDispatcher` هو في توقيت تشغيل الكوروتين؛ الـ Standard بيحط كل الكوروتينات الجديدة في الـ Queue ومبيشغلش ولا سطر كود إلا لما الـ Test يستدعي صراحة `runCurrent` أو يقدم الوقت. ده بيدي الـ Senior Engineer تحكم رياضي كامل في محاكاة الـ Race Conditions وترتيب تداخل الخيوط.\n\nأما الـ Unconfined فبيشغل الكوروتين فورياً لحد أول نقطة تعليق، وده مفيد في الاختبارات البسيطة لكنه مبيسمحش باختبار دقيق للـ Concurrency المعقدة.\n\nوفي اختبارات الإلغاء والمهلات الزمنية (Timeouts)، دالة `withTimeout` بترمي `TimeoutCancellationException` لما الوقت الافتراضي يتجاوز الحد عبر `advanceTimeBy`. بنختبر هنا إن كتل الـ finally اشتغلت وحررت الموارد بدون تسريب. وفي الـ Supervised Scope، بنختبر إن سقوط كوروتين فرعية معينة ساب باقي الـ Continuations الشقيقة موجودة في الـ Scheduler Queue واكتملت بنجاح لما استدعينا `advanceUntilIdle`.\n\nوفي بيئات الـ CI للشركات الكبيرة، بنمنع أي اختبار يعتمد على توقيت حقيقي، وبكده بنشغل آلاف اختبارات التزامن في ثوانٍ معدودة مع ضمان حتمية النتائج 100%. كما يجب الانتباه إلى تنظيف الـ TestScope دائماً والتحقق من عدم وجود أي استثناءات غير ممسوكة متبقية، وده بيضمن بيئة فحص نقية ومتطابقة تماماً بين الأجهزة المختلفة ومخدمات البناء."
    }
}

def run():
    print(f"Elevating {len(DATA)} remaining COR questions: {sorted(DATA.keys())}")
    
    # 1. Update canonical markdown files
    for qid in sorted(DATA.keys()):
        data = DATA[qid]
        ee.update_canonical_question(
            qid=qid,
            concept_en=data["concept_en"],
            walkthrough_en=data["walkthrough_en"],
            structured_en=data["structured_en"],
            deep_senior_en=data["deep_senior_en"],
            short_en=data["short_en"],
        )
        print(f"Updated canonical question {qid}")

    # 2. Save Arabic metadata dictionary
    meta_dict = {qid: DATA[qid]["meta_ar"] for qid in sorted(DATA.keys())}
    meta_file = SCRIPT_DIR / "data" / "metadata_cor_remaining.json"
    meta_file.write_text(json.dumps(meta_dict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved Arabic metadata to {meta_file}")

    # 3. Merge all metadata
    ee.merge_all_metadata()

    # 4. Validate each question
    all_passed = True
    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            all_passed = False
            print(f"❌ {qid} validation failed with {len(errs)} errors:")
            for e in errs:
                print("  -", e)
        else:
            print(f"✅ {qid} passed validation with 0 errors!")

    if not all_passed:
        print("Some questions failed validation!", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"All {len(DATA)} COR questions successfully elevated and passed validation!")

if __name__ == "__main__":
    run()
