#!/usr/bin/env python3
"""Elevate ARC-10 through ARC-18 for bilingual parity and senior spoken answers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import elevation_engine as ee

TOPIC_AR = "العمارة النظيفة و MVVM و MVI و UDF"
REVIEWED_DATE_AR = "تمت المراجعة الفنية استناداً إلى توثيق أندرويد الرسمي في 2026-10-14."

DATA = {}

# ==========================================
# ARC-10: Single Source of Truth (SSOT)
# ==========================================
DATA["ARC-10"] = {
    "concept_en": """Single Source of Truth (SSOT) is an architectural pattern dictating that a specific piece of application data has exactly one authoritative owner responsible for its storage, mutation, and distribution. In Android, the Data layer—specifically local persistent storage such as a Room database or an authoritative in-memory StateFlow repository—acts as the SSOT. When remote network payloads arrive from Retrofit or WebSocket streams, they are written directly to local storage rather than dispatched to the UI. The UI observes database tables reactively via Flow. This guarantees consistent offline-first data, prevents conflicting states between concurrent screens, and simplifies application recovery after process death.""",
    "walkthrough_en": """Implementing an offline-first Single Source of Truth with Room and Retrofit:
```kotlin
class OfflineFirstUserRepository(
    private val userDao: UserDao,
    private val userApi: UserApi,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) : UserRepository {
    // 1. SSOT: Room database is the sole data stream exposed to the application
    override fun observeUserProfile(userId: String): Flow<UserProfile> =
        userDao.observeUser(userId).map { it.toDomain() }

    // 2. Network mutations write directly into SSOT, never bypassing it
    override suspend fun refreshUserProfile(userId: String): Result<Unit> = withContext(ioDispatcher) {
        runCatching {
            val remoteUserDto = userApi.fetchUser(userId)
            userDao.upsertUser(remoteUserDto.toEntity()) // DB update automatically emits to downstream Flow
        }
    }
}
```""",
    "short_en": """Single Source of Truth establishes that a single, authoritative component owns and mutates a piece of state. In Android, local storage like Room acts as the SSOT. Network responses update the database, and the UI reacts purely to database flows, ensuring offline consistency and preventing data discrepancies.""",
    "structured_en": """To begin with, Single Source of Truth guarantees data consistency across multi-screen Android applications by establishing one authoritative owner for each data entity.
From an architectural standpoint, the local database—typically Room—functions as the SSOT within the data layer. Instead of the UI observing both network responses and cached models, all read operations observe continuous Flow streams emitted by the database.
In production scenarios, write operations follow an offline-first pipeline. When user actions trigger mutations or background workers fetch remote data from Retrofit, the repository inserts the new records directly into Room. The database then automatically notifies active UI collectors through reactive queries.
As for system reliability, SSOT eliminates race conditions where two screens display conflicting account balances, ensures full offline functionality without special UI branching, and simplifies testing by reducing state validation to inspecting the persistent database store.""",
    "deep_senior_en": """Under the hood, Single Source of Truth transforms the data layer from an imperative request-response bridge into an authoritative reactive store. In flawed architectures, ViewModels often maintain their own in-memory caches or combine network payloads with database records inside presentation coroutines. When a user updates their profile name on one screen, sibling screens or background sync tasks continue displaying stale information because each component references disparate copies of the data.
Enforcing SSOT centralizes data ownership inside a repository backed by a persistent relational database like Room or an authoritative StateFlow in memory. The repository exposes read-only reactive streams using Flow. Upstream consumers, whether ViewModels or background workers, cannot mutate the data directly; they dispatch write requests to the repository, which validates the payload, performs optimistic or pessimistic database writes, and handles backend synchronization.
Because Room's query pipeline observes SQLite table updates via InvalidationTracker, writing to the database triggers automatic recalculation and emission across every active collector in the application simultaneously.
Staff engineers ensure that SSOT is not violated by caching network DTOs in transient ViewModel variables. They also design conflict resolution strategies: when offline modifications conflict with remote server states, the repository reconciles timestamps and operational transforms before committing to the SSOT, guaranteeing enterprise-grade data integrity across device restarts.""",
    "meta_ar": {
        "id": "ARC-10",
        "questionAr": "ما هو المصدر الأوحد للحقيقة (Single Source of Truth - SSOT) في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ المصدر الأوحد للحقيقة، وكيفية بناء معمارية Offline-First باستخدام Room كمصدر أساسي، وإدراك كيفية منع تعارض البيانات بين الشاشات المتعددة.",
        "why_it_matters_ar": "بدون SSOT، تحتفظ كل شاشة بنسختها الخاصة من البيانات، مما يؤدي لظهور أرصدة متضاربة للمستخدم وأخطاء مزامنة كارثية عند انقطاع الإنترنت أو التنقل بين الصفحات.",
        "worked_example_ar": "تطبيق SSOT بحيث تقرأ الواجهة من Room حصرياً وتكتب الشبكة في قاعدة البيانات:\n```kotlin\nclass UserRepositoryImpl(val dao: UserDao, val api: UserApi) : UserRepository {\n    // القراءة دائماً من قاعدة البيانات المحلية\n    override fun getUser(id: String) = dao.observeUser(id).map { it.toDomain() }\n    // التحديث يكتب في قاعدة البيانات مباشرة فتصل الداتا للواجهة تلقائياً\n    override suspend fun sync(id: String) = dao.insert(api.fetchUser(id).toEntity())\n}\n```",
        "trade_offs_ar": "نمط SSOT يضمن اتساق البيانات ودعم العمل بدون إنترنت، لكنه يتطلب تخزين كل البيانات محلياً أولاً واستخدام دوال تحويل إضافية بين الـ Entity والـ Domain.",
        "failure_modes_ar": "تحديث حالة الـ ViewModel مباشرة من استجابة Retrofit قبل حفظها في Room، مما يجعل شاشات أخرى في التطبيق تعرض بيانات قديمة غير محدثة.",
        "production_perspective_ar": "في المشروعات الكبرى، نلزم المطورين بجعل قاعدة بيانات Room هي المالك الحصري للبيانات المعروضة، ونستخدم مشغلات Flow التفاعلية لمزامنة الواجهات تلقائياً مع جداول SQLite.",
        "how_to_answer_ar": "عرف الـ SSOT بأنه المكون الوحيد المسؤول عن تعديل ونشر حالة معينة، واشرح كيف يكون Room هو المصدر الأوحد في أندرويد، وبيّن مسار البيانات: الشبكة تكتب في الداتابيز والشاشة تقرأ من الداتابيز.",
        "talking_points_ar": "مفهوم SSOT، ومعمارية Offline-First، ودور InvalidationTracker في Room، وحل تعارض البيانات بين الشبكة والمحلي.",
        "follow_ups_ar": "- **المحاور:** \"هل الـ SSOT لازم يكون دايماً قاعدة بيانات Room؟\"\n  **المرشح:** \"مش بالضرورة؛ الـ SSOT ممكن يكون StateFlow في الذاكرة لو كانت الداتا مؤقتة مش محتاجة حفظ دائم زي حالة جلسة المستخدم، لكن في معظم التطبيقات بنفضل Room لدعم العمل بدون إنترنت.\"\n\n- **المحاور:** \"إزاي الـ SSOT بيمنع ظهور بيانات متضاربة في شاشتين مختلفتين؟\"\n  **المرشح:** \"لأن الشاشتين بيراقبوا نفس تدفق الـ Flow اللي طالع من نفس جدول قاعدة البيانات؛ فأي تعديل يحصل في الداتابيز بيوصل فوراً وبشكل تلقائي للشاشتين في نفس اللحظة.\"",
        "self_check_ar": "هل وضحت معنى المصدر الأوحد للحقيقة؟ هل شرحت دور Room كمصدر للقراءة؟ وهل بينت مسار كتابة بيانات الشبكة في قاعدة البيانات؟",
        "references_ar": f"- [Guide to app architecture - Single source of truth](https://developer.android.com/topic/architecture/data-layer#single-source-of-truth) — توثيق جوجل الرسمي لمبدأ المصدر الأوحد للحقيقة.\n- [Offline-first architecture](https://developer.android.com/topic/architecture/data-layer/offline-first) — دليل جوجل للتطبيقات الداعمة للعمل بدون إنترنت.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "المصدر الأوحد للحقيقة (SSOT) هو مبدأ معماري بيحدد إن كل جزء من البيانات لازم يملكه ويديره كائن واحد موثوق فقط. في أندرويد، قاعدة بيانات Room المحلية هي الـ SSOT؛ استجابات السيرفر بتنزل تتخزن في قاعدة البيانات، والشاشات بتراقب تدفق البيانات من قاعدة البيانات حصرياً لضمان عدم وجود أي تعارض.",
        "best_answer_ar": "المصدر الأوحد للحقيقة هو الضمانة الهندسية الأساسية لمنع تضارب البيانات في تطبيقات أندرويد الكبيرة.\n\nالفكرة بتعتمد على تحديد مكان واحد ووحيد هو صاحب الكلمة الأخيرة في أي معلومة. في المعمارية الحديثة، طبقة البيانات وتحديداً قاعدة بيانات Room المحلية هي اللي بتشتغل كـ SSOT؛ فلما المستخدم يطلب تحديث البيانات أو يجيلنا تحديث من السيرفر عبر Retrofit، الريبوزيتوري مبيبعتش الداتا للـ ViewModel مباشرة، بل بيكتبها ويحفظها في جداول Room أولاً.\n\nشاشات التطبيق كلها والـ ViewModels بتراقب تدفقات Flow مستمرة من قاعدة البيانات دي؛ وبكده بمجرد ما السجلات تتحدث في SQLite، قاعدة البيانات بتنبه كل الشاشات المفتوحة في نفس اللحظة وتحدث معروضاتها تلقائياً.\n\nالأسلوب ده بيقضي تماماً على مشاكل الـ Race Conditions، وبيضمن إن التطبيق يشتغل بكفاءة تامة بدون إنترنت، وبيمنع أي شاشتين من عرض أرصدة أو أسماء مختلفة لنفس المستخدم.",
        "deep_answer_ar": "تحت الكابوت، مبدأ المصدر الأوحد للحقيقة بيحول طبقة البيانات من مجرد وسيط نداءات تقليدي إلى مخزن تفاعلي موحد يدير حالة التطبيق بدقة متناهية. في التطبيقات التي تفتقر لهذا المبدأ، كل ViewModel بيحتفظ بكاش خاص بيه في الذاكرة أو بيدمج استجابات الشبكة محلياً، فلو المستخدم غير اسمه في شاشة الإعدادات، الشاشة الرئيسية بتفضل عارضة الاسم القديم لغاية ما يعمل إعادة تحميل.\n\nتطبيق SSOT بيحسم الأمر بجعل الـ Repository مالكاً وحيداً لقاعدة بيانات Room أو كائن StateFlow مركزي في الذاكرة. الـ Repository بيعرض واجهات قراءة تفاعلية غير قابلة للتعديل عبر Flow، وأي تعديل بيتم من خلال إرسال أوامر صريحة للمستودع للتحقق منها وتخزينها في قاعدة البيانات.\n\nمكتبة Room بتعتمد داخلياً على آلية InvalidationTracker؛ الآلية دي بتراقب أي تعديل في جداول SQLite وتطلق إعادة استعلام وتحديث فوري لكل المراقبين النشطين في أجزاء من الثانية.\n\nالمهندسون الكبار بيحرصوا على عدم كسر الـ SSOT بتخزين كائنات DTO في متغيرات مؤقتة داخل الـ ViewModel، وبيحطوا استراتيجيات محكمة لحل التعارض (Conflict Resolution) بين التعديلات التي تمت أوفلاين وبيانات السيرفر، لضمان أعلى مستويات الأمان وموثوقية البيانات عند عودة الاتصال بالإنترنت. وده بيعزز استقرار التطبيق ويخلي تجربة المستخدم سلسة وموثوقة حتى في أصعب ظروف الشبكات الضعيفة وغير المستقرة."
    }
}

# ==========================================
# ARC-11: Exposing Loading, Content, Empty, Error
# ==========================================
DATA["ARC-11"] = {
    "concept_en": """In modern Android and Jetpack Compose, UI state must be exposed as a single, immutable, type-safe representation via StateFlow to guarantee predictable recomposition and compile-time exhaustiveness. The four fundamental UI states of a screen are Loading (initial data retrieval or background refresh), Content (populated data models ready for rendering), Empty (valid response containing zero items, prompting onboarding or alternative actions), and Error (failure conditions containing actionable retry metadata). Modeling these states as a sealed interface hierarchy (or an immutable data class with explicit state flags) prevents impossible intermediate states—such as showing both a progress spinner and an error banner simultaneously—and ensures that the UI remains a pure, passive reflection of state.""",
    "walkthrough_en": """Exposing exhaustive UI states with a sealed interface in Jetpack Compose:
```kotlin
// 1. Sealed interface models mutually exclusive screen states
sealed interface ProductsUiState {
    object Loading : ProductsUiState
    data class Content(val products: List<ProductItemUiModel>) : ProductsUiState
    object Empty : ProductsUiState
    data class Error(val errorMessage: String, val canRetry: Boolean) : ProductsUiState
}

// 2. ViewModel exposes single StateFlow
class ProductsViewModel(private val repository: ProductRepository) : ViewModel() {
    val uiState: StateFlow<ProductsUiState> = repository.observeProducts()
        .map { list ->
            if (list.isEmpty()) ProductsUiState.Empty
            else ProductsUiState.Content(list.map { it.toUiModel() })
        }
        .catch { emit(ProductsUiState.Error(it.localizedMessage ?: "Unknown error", canRetry = true)) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), ProductsUiState.Loading)
}

// 3. Compose UI renders exhaustively via when expression
@Composable
fun ProductsScreen(uiState: ProductsUiState, onRetry: () -> Unit) {
    when (uiState) {
        is ProductsUiState.Loading -> CircularProgressIndicator()
        is ProductsUiState.Empty -> Text("No products found")
        is ProductsUiState.Error -> Button(onClick = onRetry) { Text("Retry: ${uiState.errorMessage}") }
        is ProductsUiState.Content -> LazyColumn { items(uiState.products) { ProductRow(it) } }
    }
}
```""",
    "short_en": """Expose UI state as a single, immutable sealed hierarchy or data class through StateFlow. This guarantees compile-time exhaustiveness in Compose when statements, prevents contradictory intermediate states like simultaneous loading and error banners, and models loading, content, empty, and error conditions with explicit type safety.""",
    "structured_en": """To begin with, modeling UI states explicitly eliminates unpredictable visual glitches and simplifies screen rendering logic in Jetpack Compose.
From an architectural standpoint, the ViewModel exposes a single StateFlow rather than multiple disparate Boolean flags. We model states using a sealed interface with discrete variants: Loading for initial data retrieval, Content carrying immutable list models, Empty for zero-result states, and Error encapsulating actionable diagnostic messages.
In production scenarios, when the screen opens, the ViewModel initiates the Loading state. If the repository emits an empty list, the state transitions explicitly to Empty, rendering tailored user guidance rather than a blank canvas. If an exception occurs, the Error state supplies retry actions.
As for maintenance advantages, this pattern enforces compile-time exhaustiveness in UI Composables. When engineers add new state variants—such as an offline cached banner—the compiler forces every screen branch to handle the transition safely without silent runtime failures.""",
    "deep_senior_en": """Under the hood, whether to model UI state as a sealed interface hierarchy or a single comprehensive data class depends on screen complexity and transition overlap. A sealed interface like sealed interface ScreenState containing Loading, Success, Empty, and Error provides mathematical exclusivity: the UI can never accidentally render both an error message and a loading spinner at the same time because only one type exists in the StateFlow at any given millisecond.
However, in production applications with partial screen refreshes—such as swipe-to-refresh or pagination—a sealed hierarchy can be restrictive because transitioning to Loading destroys the existing Success state, wiping content off the screen and causing jarring visual flickers.
In such scenarios, staff engineers prefer a unified immutable data class: data class ScreenUiState containing items, isRefreshing, and userErrorMessage. This approach preserves existing list data while toggling an overlaid isRefreshing spinner or non-blocking Snackbar message.
Furthermore, staff engineers enforce Compose stability by annotating UI state classes with Immutable or Stable and using kotlinx.collections.immutable structures like ImmutableList to avoid unnecessary recomposition passes when parent Composable trees evaluate parameters. This architectural rigor guarantees fluid sixty frames per second rendering across complex state transitions. By rigorously separating presentation states and maintaining exhaustive branch coverage, teams eliminate entire classes of visual regressions and deliver deterministic user experiences.""",
    "meta_ar": {
        "id": "ARC-11",
        "questionAr": "كيف تعرض حالات التحميل والمحتوى والحالة الفارغة والخطأ في واجهة أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم كيفية نمذجة حالات الواجهة ككائن واحد غير قابل للتعديل، واستيعاب الفروق بين Sealed Interface و Data Class، ومعرفة كيفية منع تعارض الحالات وتحسين أداء الـ Recomposition.",
        "why_it_matters_ar": "استخدام متغيرات Boolean متعددة ومنفصلة يجعل الواجهة تدخل في حالات متناقضة، كأن يظهر مؤشر التحميل مع رسالة الخطأ والشاشة الفارغة في نفس الوقت مسبباً وميضاً وتجربة مستخدم سيئة.",
        "worked_example_ar": "نمذجة الحالات الأربعة عبر Sealed Interface في Compose:\n```kotlin\nsealed interface ScreenUiState {\n    object Loading : ScreenUiState\n    data class Content(val items: List<ItemUiModel>) : ScreenUiState\n    object Empty : ScreenUiState\n    data class Error(val message: String) : ScreenUiState\n}\n\n// التعامل الحصري في الـ Composable\n@Composable fun MyScreen(state: ScreenUiState) = when(state) {\n    is ScreenUiState.Loading -> LoadingView()\n    is ScreenUiState.Empty -> EmptyPlaceholder()\n    is ScreenUiState.Error -> ErrorBanner(state.message)\n    is ScreenUiState.Content -> ItemsList(state.items)\n}\n```",
        "trade_offs_ar": "استخدام Sealed Interface يمنع الحالات المتناقضة تماماً، لكنه يجعل عمليات التحديث الجزئي (مثل Swipe-to-refresh) تمسح المحتوى القديم مؤقتاً إلا إذا استخدمنا Data Class مجمعة تحتوي على أعلام للتحديث.",
        "failure_modes_ar": "تعريف متغيرات مستقلة مثل `val isLoading = MutableStateFlow(false)` و `val isError = MutableStateFlow(false)`، مما يسمح بوجود الاثنين في حالة `true` معاً.",
        "production_perspective_ar": "في المشروعات الإنتاجية الكبرى، نستخدم Data Class موحدة إذا كانت الشاشة تدعم التحديث الجزئي مع الاحتفاظ بالمحتوى، ونستخدم Sealed Interface للشاشات التي تتغير بالكامل، مع وسم الكلاسات بـ `@Immutable` لضمان استقرار Compose.",
        "how_to_answer_ar": "ابدأ بشرح أهمية تمثيل حالة الشاشة في كائن واحد مجمع عبر StateFlow، واشرح الحالات الأربع: التحميل والمحتوى والفارغ والخطأ، وفصل بين استخدام Sealed Interface للحصرية واستخدام Data Class للتحديث الجزئي.",
        "talking_points_ar": "نمذجة الحالة ككائن واحد، ومنع الحالات المتناقضة، والمقارنة بين Sealed Interface و Data Class، وتحسين استقرار Compose باستخدام ImmutableList.",
        "follow_ups_ar": "- **المحاور:** \"إمتى تفضل Data Class واحدة على Sealed Interface في تمثيل حالة الشاشة؟\"\n  **المرشح:** \"بفضل Data Class لما الشاشة تكون محتاجة تدعم Swipe-to-refresh أو Pagination؛ لأن في الـ Sealed Interface لو نقلنا الحالة لـ Loading هنمسح المحتوى القديم من الشاشة ويعمل فليكر، بينما الـ Data Class بتحتفظ بالقائمة وتعرض مؤشر التحديث فوقها بسلاسة.\"\n\n- **المحاور:** \"إزاي نضمن إن الـ Composable ميعملش Recomposition بدون داعي لكل الشاشة؟\"\n  **المرشح:** \"عن طريق وسم الـ UI State بـ `@Immutable` واستخدام مجموعات بيانات غير قابلة للتعديل من مكتبة `kotlinx.collections.immutable` زي `ImmutableList` بدلاً من `List` العادية.\"",
        "self_check_ar": "هل وضحت الحالات الأربع؟ هل شرحت ميزة الـ Sealed Interface في الحصرية الرياضية؟ وهل بينت متى نستخدم Data Class مجمعة؟",
        "references_ar": f"- [Guide to app architecture - UI layer state production](https://developer.android.com/topic/architecture/ui-layer/state-production) — توثيق جوجل الرسمي لنمذجة حالات الشاشات.\n- [Compose Performance: Stability](https://developer.android.com/develop/ui/compose/performance/stability) — توثيق جوجل لأداء واستقرار النماذج في Compose.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنعرض حالات الواجهة ككائن واحد غير قابل للتعديل من خلال تدفق StateFlow، باستخدام Sealed Interface أو Data Class متكاملة. ده بيضمن التعامل مع كل الحالات بدقة وقت الكومبايل، ويمنع ظهور حالات متناقضة زي ظهور التحميل والخطأ في نفس اللحظة، وبيسهل رسم الشاشة في Compose.",
        "best_answer_ar": "نمذجة حالات الشاشة ككائن واحد متكامل هو المعيار القياسي لتفادي الأخطاء البصرية في تطبيقات أندرويد الحديثة وواجهات Jetpack Compose.\n\nبدلاً من إننا نعمل متغيرات Boolean متفرقة زي `isLoading` و `isError` اللي ممكن يدخلوا في تناقض لحظي، الـ ViewModel بيعرض تدفق `StateFlow` واحد لحالة الشاشة. بنمثل الحالات الأساسية الأربعة: حالة التحميل أثناء جلب البيانات، وحالة المحتوى لما البيانات ترجع بنجاح، وحالة الشاشة الفارغة لو المستخدم معندوش بيانات لتوجيهه بإرشادات مناسبة، وحالة الخطأ التي تحمل رسالة توضيحية وزر إعادة المحاولة.\n\nفي الـ Compose، استخدام `when` التعبيرية مع الـ Sealed Interface بيجبر المطور يعالج كل الحالات بدون أي احتمالية لنسيان حالة معينة.\n\nالنتيجة هي واجهة مستخدم متوقعة ومستقرة، وشاشات بتشتغل كدوال نقية تعتمد كلياً على الحالة المعروضة، مما يرفع جودة التطبيق ويجعل كتابة اختبارات الشاشات عملية واضحة ومباشرة.",
        "deep_answer_ar": "تحت الكابوت، الاختيار بين استخدام Sealed Interface أو Data Class موحدة بيعتمد على طبيعة التفاعلات في الشاشة وتداخل الحالات. استخدام Sealed Interface بيحقق حصرية رياضية تامة؛ الشاشة يستحيل تعرض مؤشر التحميل ورسالة الخطأ معاً في نفس اللحظة لأن الـ StateFlow مبيشيلش غير كائن واحد فقط في أي ميلي ثانية، وده ممتاز في الشاشات البسيطة وعمليات الدخول.\n\nلكن في التطبيقات الإنتاجية المعقدة اللي بتدعم الـ Swipe-to-refresh أو الـ Pagination، الـ Sealed Interface ممكن تعمل وميض مزعج للمستخدم؛ لأن الانتقال لحالة Loading هيمسح المحتوى القديم من الشاشة فجأة ويرجع يظهره بعد التحميل.\n\nعلشان كده، المهندسون الكبار بيفضلوا في الحالات دي استخدام Data Class موحدة زي `data class ScreenUiState`؛ بتحتفظ بالقائمة المعروضة حالياً، وجنبها أعلام زي `isRefreshing` أو كائن `userMessage` للـ SnackBar، فالمستخدم يفضل شايف بياناته بينما مؤشر التحديث شغال في الخلفية.\n\nكمان بنحرص على وسم كلاسات الـ State بـ `@Immutable` أو `@Stable` واستخدام كولكشنز غير قابلة للتعديل من مكتبة `kotlinx.collections.immutable` زي `ImmutableList`، وده بيمنع Compose من إعادة استدعاء كل الـ Composables بدون داعي ويحافظ على معدل ستين إطاراً في الثانية بثبات تام. وده بيمنع أي وميض بصري مزعج ويحافظ على استقرار الواجهة وسرعة استجابتها لضغطات المستخدم في كل لحظة."
    }
}

# ==========================================
# ARC-12: Domain/Data Errors to UI Errors
# ==========================================
DATA["ARC-12"] = {
    "concept_en": """Domain and data layer errors represent technical, transport, or business invariant failures (such as SocketTimeoutException, HTTP 401/403/500, SQLiteConstraintException, or DomainValidationException). The UI layer must never consume or display raw exceptions directly, as doing so leaks infrastructure details, displays unlocalized cryptic messages to users, and causes main-thread crashes when uncaught exceptions bubble up. Instead, robust architectures apply an error transformation pipeline: the Data layer intercepts raw throwables and categorizes them into typed, domain-safe failure models. The Presentation layer (ViewModel) maps these domain errors into user-actionable UI error representations containing localized string resource identifiers, error severities, and explicit recovery actions (such as retry lambdas, re-authentication triggers, or navigation intents).""",
    "walkthrough_en": """Transforming low-level exceptions into user-actionable UI models:
```kotlin
// 1. DOMAIN LAYER: Typed, framework-agnostic error hierarchy
sealed interface DomainError {
    object NetworkUnavailable : DomainError
    object Unauthorized : DomainError
    data class ServerError(val code: Int) : DomainError
    data class BusinessRuleViolated(val reason: String) : DomainError
}

// 2. PRESENTATION LAYER: Actionable UI error model with string resources
data class ActionableUiError(
    @StringRes val titleRes: Int,
    @StringRes val messageRes: Int,
    @StringRes val actionLabelRes: Int?,
    val recoveryAction: (() -> Unit)?
)

fun DomainError.toUiError(onRetry: () -> Unit, onReAuth: () -> Unit): ActionableUiError = when (this) {
    is DomainError.NetworkUnavailable -> ActionableUiError(
        titleRes = R.string.error_no_internet_title,
        messageRes = R.string.error_no_internet_desc,
        actionLabelRes = R.string.action_retry,
        recoveryAction = onRetry
    )
    is DomainError.Unauthorized -> ActionableUiError(
        titleRes = R.string.error_session_expired_title,
        messageRes = R.string.error_session_expired_desc,
        actionLabelRes = R.string.action_login_again,
        recoveryAction = onReAuth
    )
    else -> ActionableUiError(R.string.error_generic_title, R.string.error_generic_desc, null, null)
}
```""",
    "short_en": """Catch raw low-level exceptions in the data layer, translate them into typed domain errors, and map them in the ViewModel into actionable UI models. UI errors should provide localized string resources and clear recovery actions, such as retry callbacks or re-authentication triggers, rather than raw exception messages.""",
    "structured_en": """To begin with, converting technical exceptions into actionable UI errors is essential for building resilient, user-friendly Android applications.
From an architectural standpoint, raw network exceptions like SocketTimeoutException or HTTP 500 status codes must never leak into the presentation layer. The repository intercepts infrastructure failures and maps them into a typed domain failure hierarchy, such as NetworkUnavailable or SessionExpired.
In production scenarios, the ViewModel translates these domain failures into UI-facing models. Rather than exposing raw strings that violate localization, it binds Android string resource IDs alongside explicit recovery actions, such as triggering a retry lambda or launching an account recovery intent.
As for user experience, this mapping ensures the UI presents empathetic, actionable guidance. The interface informs users exactly what went wrong and how to fix it, whether that means enabling airplane mode, checking card limits, or tapping a retry button.""",
    "deep_senior_en": """Under the hood, robust error architecture follows an anti-corruption pipeline that prevents infrastructure crashes while preserving actionable diagnostic context. When an HTTP client throws a 401 Unauthorized or a database write violates a foreign key constraint, the Data layer catches the throwable and categorizes it into a sealed domain error type. By wrapping operations in a custom domain Result, the system eliminates uncaught runtime exceptions on coroutine dispatchers.
Inside the Presentation layer, the ViewModel maps the domain error into a presentation state model. A major pitfall in legacy applications is passing raw exception messages like java.net.UnknownHostException directly into UI TextViews, which exposes internal implementation details and fails multi-language localization.
Senior engineers model actionable errors as structured data classes: data class UserMessage containing message resource IDs, action labels, and action types. This decouples the Composable from error decisions; Compose simply renders the text resource and invokes the callback when the user taps the action button.
Furthermore, staff engineers distinguish between transient errors—which are presented via Snackbars or dialogs without clearing screen content—and terminal errors, which replace the entire screen with a full-page empty error layout. In production telemetry, raw error details and correlation trace IDs are simultaneously dispatched to crash reporting services like Datadog or Crashlytics while the user receives a graceful, localized recovery experience.""",
    "meta_ar": {
        "id": "ARC-12",
        "questionAr": "كيف يتم تحويل أخطاء الدومين والبيانات إلى أخطاء قابلة للتنفيذ في واجهة المستخدم؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم كيفية التعامل مع الأخطاء كبيانات منضبطة، والقدرة على عزل استثناءات الشبكة وقواعد البيانات عن الواجهة، وتصميم نماذج أخطاء قابلة للتنفيذ (Actionable Errors) تدعم التدويل وتوفر خطط تعافي للمستخدم.",
        "why_it_matters_ar": "عرض رسائل الاستثناءات التقنية الخام مثل `SocketTimeoutException` للمستخدم يسبب ارتباكاً ويفسد تجربة الاستخدام، كما أن تسريبها دون معالجة يتسبب في انهيار التطبيق ومشاكل أمنية بكشف تفاصيل السيرفر.",
        "worked_example_ar": "تحويل خطأ الدومين لرسالة واجهة مستخدم مترجمة مع إجراء تعافٍ:\n```kotlin\n// Domain: تصنيف الخطأ كبيانات\nsealed interface DomainError { object NoInternet : DomainError; object ExpiredToken : DomainError }\n\n// Presentation: تحويل الخطأ لرسالة واجهة قابلة للتنفيذ\nfun DomainError.toUserMessage(onRetry: () -> Unit) = when(this) {\n    DomainError.NoInternet -> UserMessage(R.string.no_net, R.string.retry, onRetry)\n    DomainError.ExpiredToken -> UserMessage(R.string.reauth, R.string.login, onRetry)\n}\n```",
        "trade_offs_ar": "بناء خط أنابيب متكامل لتحويل الأخطاء يتطلب كتابة كود إضافي لكل طبقة، لكنه يضمن استقرار التطبيق بنسبة 100% ويمنع تسريب تفاصيل البنية التحتية للمستخدم.",
        "failure_modes_ar": "عرض نص `e.localizedMessage` مباشرة على الشاشة للمستخدم، أو ابتلاع الأخطاء داخل كتل catch دون إبلاغ المستخدم أو إرسال تقارير للـ Telemetry.",
        "production_perspective_ar": "في التطبيقات المصرفية، نصنف الأخطاء إلى نوعين: أخطاء عابرة (Transient) تظهر كـ SnackBar مع الاحتفاظ بالمحتوى، وأخطاء قاتلة (Terminal) تستبدل الشاشة بصفحة خطأ كاملة وزر إعادة المحاولة، مع إرسال تفاصيل الخطأ الفنية لـ Crashlytics في الخلفية.",
        "how_to_answer_ar": "وضح خط سير الخطأ: المستودع يمسك الاستثناءات الخام ويحولها لـ Domain Errors، والـ ViewModel يحولها لـ UI Errors تحتوي على معرفات نصوص R.string وإجراءات تعافٍ، والشاشة تعرضها بدون اتخاذ قرارات.",
        "talking_points_ar": "الأخطاء كبيانات وليست استثناءات غير متحكم بها، وتوفير خطط تعافٍ (Recovery Actions)، وتدويل الرسائل عبر معرفات الموارد، والفصل بين الأخطاء العابرة والقاتلة.",
        "follow_ups_ar": "- **المحاور:** \"ليه مينفعش نرجع نصوص الخطأ مباشرة من كلاسات الدومين؟\"\n  **المرشح:** \"علشان نحافظ على الدومين مستقل عن كلاسات أندرويد ويدعم اللغات المختلفة؛ الدومين بيرجع كود الخطأ أو نوعه، والـ ViewModel هو اللي بيختار معرف النص المناسب زي `R.string.network_error` بحسب لغة جهاز المستخدم.\"\n\n- **المحاور:** \"إزاي بنتعامل مع خطأ انتهاء صلاحية الجلسة (401 Unauthorized)؟\"\n  **المرشح:** \"المستودع بيحول الـ 401 لـ DomainError.Unauthorized، والـ ViewModel بيحطه في حالة الواجهة كخطأ يتطلب إعادة تسجيل الدخول، فتوجه الشاشة المستخدم لصفحة تسجيل الدخول فوراً.\"",
        "self_check_ar": "هل أكدت على عدم عرض الاستثناءات الخام للمستخدم؟ هل شرحت كيفية تحويل الخطأ لمعرف نص في أندرويد؟ وهل وضحت مفهوم إجراءات التعافي؟",
        "references_ar": f"- [Guide to app architecture - UI layer error handling](https://developer.android.com/topic/architecture/ui-layer#handle-errors) — توثيق جوجل لمعالجة الأخطاء في طبقة العرض.\n- [Modeling errors in Kotlin](https://elizarov.medium.com/kotlin-and-exceptions-8062f581e42c) — مقال رومان إليزاروف حول نمذجة الأخطاء كبيانات في كوتلن.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنمسك الاستثناءات التقنية الخام في طبقة البيانات، ونحولها لأخطاء دومين منضبطة ومصنفة، وبعدها الـ ViewModel بيحولها لنماذج أخطاء واجهة مستخدم تحتوي على نصوص مترجمة قابلة للعرض وإجراءات تعافٍ واضحة، زي زرار إعادة المحاولة أو تسجيل الدخول من جديد.",
        "best_answer_ar": "تحويل الأخطاء البرمجية إلى رسائل مفيدة للمستخدم هو جوهر بناء تطبيقات مستقرة واحترافية.\n\nاستثناءات الشبكة وقواعد البيانات زي `SocketTimeoutException` أو أكواد الـ HTTP مينفعش تخرج أبداً لطبقة العرض أو يشوفها المستخدم. في المعمارية النظيفة، المستودع بيمسك الاستثناءات دي عند الحدود ويحولها لأنواع أخطاء دومين محددة ومجردة داخل Sealed Interface، زي انقطاع الاتصال أو انتهاء صلاحية الجلسة.\n\nالـ ViewModel بياخد خطأ الدومين ويحوله لنموذج خطأ خاص بالشاشة؛ النموذج ده مبيحتويش على نصوص عشوائية، بل بيعتمد على معرفات نصوص أندرويد `R.string` علشان يضمن الترجمة الصحيحة بحسب لغة الموبايل، وبيكون معاه دالة تعافٍ صريحة يقدر المستخدم يضغط عليها.\n\nبكده واجهة المستخدم بتعرض إرشادات واضحة ومريحة تفهم المستخدم إيه المشكلة وازاي يحلها، سواء كان المطلوب تشغيل الواي فاي أو مراجعة رصيد الحساب أو الضغط على زر إعادة المحاولة.",
        "deep_answer_ar": "تحت الكابوت، معمارية معالجة الأخطاء بتشتغل كحائط صد يمنع تسريب تفاصيل البنية التحتية ويحمي التطبيق من التوقف المفاجئ. لما الـ Retrofit يرمي استثناء شبكة أو تفشل قاعدة البيانات في حفظ سجل، طبقة البيانات بتلتقط الـ Throwable وتصنفه ككائن دومين منضبط داخل كلاس Result مخصص، وبكده بنمنع حدوث أي Uncaught Exceptions تنهي التطبيق.\n\nفي طبقة العرض، الـ ViewModel بيترجم أخطاء الدومين لبيانات عرض متكاملة. من أكبر الأخطاء الشائعة في التطبيقات المبتدئة إن المطور ياخد `e.message` ويعرضه في TextView؛ ده بيكشف تفاصيل السيرفر للمستخدم وممكن يعمل مشاكل أمنية ده غير إنه بيفشل تماماً في دعم اللغات المتعددة.\n\nالمهندسون الكبار بيمثلوا الأخطاء في كلاسات منظمة زي `ActionableUiError`؛ بتحمل معرف النص `R.string` وزرار الإجراء ولون التنبيه. وبنفصل هندسياً بين الأخطاء العابرة، اللي بنعرضها كـ SnackBar بدون ما نمسح المحتوى المعروض، وبين الأخطاء القاتلة اللي بتستبدل الشاشة بصفحة فارغة تطلب إعادة المحاولة.\n\nوفي نفس اللحظة اللي المستخدم بيشوف فيها رسالة لطيفة ومترجمة، النظام بيبعت تفاصيل الـ StackTrace الحقيقي وأكواد السيرفر لخدمات التتبع والـ Telemetry زي Crashlytics لتسهيل مراجعتها وحلها من قبل مهندسي الباك إند. وده بيحمي بيانات التطبيق الحساسة وبيعطي المستخدم ثقة كاملة في قدرة النظام على التعامل مع أي مشكلة بهدوء واحترافية."
    }
}

# ==========================================
# ARC-13: Domain Layer: Useful vs Optional
# ==========================================
DATA["ARC-13"] = {
    "concept_en": """Google's official Android architecture guidelines categorize the Domain layer as an optional architectural layer positioned between Presentation and Data. A separate Domain layer is genuinely useful and architecturally warranted when an application exhibits complex business rules, algorithmic validations, multi-repository coordination workflows (such as a checkout flow requiring shopping cart, payment gateway, inventory, and analytics repositories), or business logic shared across multiple ViewModels, background workers, or platforms (Kotlin Multiplatform). Conversely, a domain layer is redundant and introduces harmful over-engineering in simple CRUD scenarios where ViewModels merely fetch and display records without transformation; introducing pass-through Use Cases that merely delegate calls to a repository method creates navigation indirection, boilerplate, and cognitive fatigue without improving testability.""",
    "walkthrough_en": """Contrasting a genuinely useful UseCase with a redundant pass-through UseCase:
```kotlin
// SCENARIO 1: GENUINELY USEFUL - Multi-repository coordination and domain rules
class ExecuteCheckoutUseCase(
    private val cartRepo: CartRepository,
    private val paymentRepo: PaymentRepository,
    private val orderRepo: OrderRepository
) {
    suspend operator fun invoke(cartId: String, paymentMethodId: String): Result<OrderId> {
        val cart = cartRepo.getCart(cartId)
        if (cart.items.isEmpty()) return Result.failure(IllegalStateException("Cart is empty"))
        if (cart.total <= 0.0) return Result.failure(IllegalStateException("Invalid cart total"))

        val paymentResult = paymentRepo.charge(paymentMethodId, cart.total)
        if (paymentResult.isFailure) return Result.failure(paymentResult.exceptionOrNull()!!)

        val orderId = orderRepo.createOrder(cartId, paymentResult.getOrThrow())
        cartRepo.clearCart(cartId)
        return Result.success(orderId)
    }
}

// SCENARIO 2: REDUNDANT PASS-THROUGH - ViewModel connects directly to Repository!
class SimpleUserViewModel(private val userRepository: UserRepository) : ViewModel() {
    // ❌ ANTI-PATTERN: Creating GetUserUseCase that only calls userRepository.getUser()
    // ✅ IDIOMATIC AND PRAGMATIC: Direct repository observation eliminates boilerplate
    val userProfile = userRepository.observeUser()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)
}
```""",
    "short_en": """A domain layer is genuinely useful for complex business logic, multi-repository coordination, multi-platform sharing in KMP, and reuse across ViewModels and workers. It is optional for simple CRUD applications where UseCases would act as pointless pass-through delegates, adding file navigation overhead without improving testability.""",
    "structured_en": """To begin with, deciding whether to incorporate a dedicated Domain layer requires evaluating business complexity against maintenance overhead.
From an architectural standpoint, Google explicitly designates the Domain layer as optional. When a feature merely reads records from a repository and renders them on screen without transformation, adding a pass-through UseCase that does nothing but forward the call introduces unnecessary indirection and file sprawl.
In production scenarios, a separate Domain layer becomes genuinely indispensable when business rules become complex and reusable. Examples include coordinating multi-step transactions across multiple repositories, calculating compound interest, formatting data for regulatory compliance, or sharing business validation between a checkout Composable and a WorkManager background sync.
As for multi-platform architectures, placing core use cases in a pure Kotlin Domain module enables 100% code sharing across Android, iOS, and desktop via Kotlin Multiplatform, keeping core enterprise invariants unified across platforms.""",
    "deep_senior_en": """Under the hood, the decision to extract a dedicated Domain layer boils down to the gravity of business logic versus architectural friction. In small to mid-sized apps or standard content viewers, the Data layer already abstracts storage mechanisms, and ViewModels handle UI state preparation. Introducing a GetNewsUseCase that simply invokes newsRepository.getNews adds zero testability gains because testing the UseCase is identical to testing the Repository itself.
However, when an enterprise application grows, logic naturally leaks into ViewModels if boundaries are absent. When multiple screens need the exact same validation logic—such as determining whether a user is eligible for an instant credit loan—placing that rule inside a ViewModel forces duplication. If the background notification worker also needs to evaluate that rule, code sharing breaks down.
A dedicated Domain layer solves this by providing single-responsibility UseCases containing pure business truth. Because the Domain layer has zero dependencies on Android framework SDKs or UI libraries, these UseCases execute in pure JVM unit tests in milliseconds without Android mock engines.
Staff engineers adopt a pragmatic hybrid strategy: they keep the domain layer optional at the project level, allowing simple feature verticals to connect ViewModels directly to Repositories, while mandating UseCases for complex domains involving multi-source coordination, financial rules, or cross-module workflows. This eliminates dogmatic over-engineering while protecting core enterprise rules across long-term project evolutions.""",
    "meta_ar": {
        "id": "ARC-13",
        "questionAr": "متى تكون طبقة الدومين (Domain Layer) مفيدة حقاً ومتى تكون اختيارية في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اتخاذ قرارات معمارية عملية بعيداً عن التعصب النظري، وفهم الحالات الحقيقية التي تتطلب إنشاء طبقة دومين، وتجنب فخ الـ Over-engineering والـ Pass-through UseCases.",
        "why_it_matters_ar": "فرض طبقة دومين بـ Use Cases فارغة لكل شاشة يضاعف عدد الملفات ويزيد من وقت البناء وصعوبة التنقل في الكود، بينما إهمالها في العمليات المعقدة يسبب تكرار منطق البزنس وتضخم الـ ViewModels.",
        "worked_example_ar": "التمييز العملي بين الحاجة لـ UseCase والاستغناء عنها:\n```kotlin\n// مفيدة جداً: تنسيق بين ريبوزيتوري السلة وريبوزيتوري الدفع مع شروط بزنس\nclass CheckoutUseCase(val cart: CartRepo, val pay: PayRepo) {\n    suspend operator fun invoke() = if (cart.hasItems()) pay.charge(cart.total()) else Result.failure(EmptyCartException())\n}\n\n// غير مفيدة (Over-engineering): مجرد تكرار لدالة الريبوزيتوري\n// الأفضل جعل الـ ViewModel يراقب الـ Repository مباشرة\n```",
        "trade_offs_ar": "طبقة الدومين توفر عزلاً مثالياً ومنطقاً قابلاً للاختبار وإعادة الاستخدام، لكنها تضيف تكلفة صيانة وملفات إضافية غير مبررة في شاشات العرض البسيطة.",
        "failure_modes_ar": "إنشاء Pass-through UseCases لكل دالة في الريبوزيتوري لا تفعل شيئاً سوى تفويض النداء، أو وضع شروط البزنس المعقدة داخل كود الـ ViewModel لمنع إنشاء دومين.",
        "production_perspective_ar": "في المشروعات الكبرى، نعتمد استراتيجية هجينة موصى بها من جوجل؛ الميزات التي تحتوي على عمليات CRUD بسيطة تتصل من الـ ViewModel للـ Repository مباشرة، بينما الميزات الحساسة والمالية تمر حصرياً عبر UseCases مستقلة ومختبرة بدقة.",
        "how_to_answer_ar": "أكد على أن جوجل تصنف الدومين كطبقة اختيارية، واشرح الحالات التي تكون فيها مفيدة حقاً: منطق البزنس المعقد، والتنسيق بين عدة مستودعات، وإعادة الاستخدام، ودعم KMP، وحذر من الـ Pass-through UseCases في الشاشات البسيطة.",
        "talking_points_ar": "اختيارية طبقة الدومين رسمياً، ومصيدة الـ Pass-through UseCases، وإعادة الاستخدام بين ViewModels و WorkManager، وتسهيل مشاركة الكود عبر KMP.",
        "follow_ups_ar": "- **المحاور:** \"هل جوجل بتوصي بإنشاء طبقة Domain في كل تطبيق أندرويد؟\"\n  **المرشح:** \"لا، التوثيق الرسمي لأندرويد بيقول صراحة إن طبقة الدومين اختيارية، وبتتضاف فقط لما يكون فيه منطق أعمال معقد أو محتاجين نعيد استخدام كود معين بين كذا شاشة.\"\n\n- **المحاور:** \"إزاي طبقة الدومين بتساعدنا في مشاركة الكود عبر Kotlin Multiplatform؟\"\n  **المرشح:** \"لأنها مكتوبة بلغة كوتلن الصافية بدون أي اعتماد على Android SDK؛ فبنقدر نحط موديول الدومين في الـ Common Code ونستخدم نفس الـ UseCases في أندرويد و iOS و Desktop بنفس قواعد البزنس بالظبط.\"",
        "self_check_ar": "هل أكدت أن طبقة الدومين اختيارية؟ هل شرحت أضرار الـ Pass-through UseCases؟ وهل ذكرت الحالات الحقيقية التي تتطلب وجودها؟",
        "references_ar": f"- [Guide to app architecture - Domain layer](https://developer.android.com/topic/architecture/domain-layer) — توثيق جوجل الرسمي لطبقة الدومين واستخداماتها.\n- [Modular architecture for Android](https://developer.android.com/topic/modularization) — دليل تقسيم المشروعات لموديولات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "طبقة الدومين بتكون مفيدة جداً لما يكون فيه منطق أعمال معقد، أو حسابات رياضية، أو تنسيق بين كذا ريبوزيتوري، أو كود محتاجين نعيد استخدامه بين كذا ViewModel و WorkManager أو في KMP. وتكون اختيارية وزيادة ملهاش لازمة في شاشات العرض والقراءة البسيطة (CRUD) لتجنب إنشاء كلاسات وسيطة فارغة.",
        "best_answer_ar": "تحديد مدى الحاجة لطبقة الدومين بيعكس نضج المهندس وقدرته على الموازنة بين النقاء المعماري وسرعة الإنجاز بدون تعقيد غير مبرر.\n\nشركة جوجل بتصنف طبقة الدومين رسمياً في توثيق أندرويد على إنها طبقة اختيارية. لو التطبيق بتاعك مجرد تطبيق إخباري أو شاشات قراءة بسيطة بتجيب بيانات من السيرفر وتعرضها على الشاشة، إنشاء Use Case لكل شاشة مش هيقدم أي قيمة هندسية، بل هيزود عدد الملفات ويزود التشتت وصعوبة التنقل في المشروع بدون أي ميزة في الاختبارات.\n\nفي المقابل، طبقة الدومين بتتحول لضرورة حتمية لما يكون فيه منطق أعمال مركب؛ زي خطوات إتمام عملية الشراء اللي بتحتاج تنسق بين ريبوزيتوري السلة وريبوزيتوري بوابات الدفع وريبوزيتوري التحليلات، أو لما نكون بنعمل عمليات حسابية تخص الفوائد البنكية، أو لو نفس قاعدة البزنس محتاجين نشغلها في الشاشة وفي مهمة بالخلفية عبر WorkManager.\n\nكمان في مشاريع Kotlin Multiplatform، طبقة الدومين النقية بتسمح بمشاركة كل قواعد العمل المعقدة بين تطبيقات أندرويد و iOS بنسبة مئة بالمئة.",
        "deep_answer_ar": "تحت الكابوت، قرار بناء طبقة الدومين بيعتمد على وزن منطق الأعمال ومقدار الاحتكاك الهندسي اللي هتسببه الطبقات الإضافية. في المشاريع البسيطة، طبقة البيانات بالفعل بتعزل تفاصيل التخزين، والـ ViewModels بتجهز حالة العرض. فلما نعمل كلاس زي `GetArticlesUseCase` كل اللي بيعمله إنه يستدعي `repository.getArticles()`، إحنا معملناش أي عزل حقيقي بل كررنا الكود وضيعنا وقت المطورين في كتابة واختبار كلاس وسيط فارغ (Pass-through UseCase).\n\nلكن لما حجم التطبيق يكبر وتتعقد قواعد العمل، غياب طبقة الدومين بيخلي كود البزنس يتسرب ويتشتت داخل الـ ViewModels. فلو عندنا شرط بيحدد أهلية المستخدم للحصول على قرض بناءً على حسابات معقدة، كتابته جوه الـ ViewModel هتجبرنا نكرره في كل شاشة محتاجة نفس الفحص، ولو احتجنا نعمل نفس التحقق في كود الإشعارات بالخلفية هنلاقي نفسنا في ورطة معمارية.\n\nوجود UseCases مستقلة ومكتوبة بكوتلن النقية بيحل المشكلة دي من جذورها، وبيخلي اختبارات الوحدة تشتغل على JVM في أجزاء من الثانية بدون الحاجة لأي محاكيات أو مكاتب Mocking معقدة.\n\nالمهندسون الكبار بيتبعوا سياسة هجينة وعملية: بيخلوا طبقة الدومين اختيارية على مستوى الميزات البسيطة، فيسمحوا للـ ViewModel بمراقبة الـ Repository مباشرة، بينما يفرضون وجود UseCases مستقلة ومحكمة للميزات الحساسة والمالية متعددة المصادر لحماية قواعد العمل الحيوية بأعلى كفاءة ممكنة."
    }
}

# ==========================================
# ARC-14: Why UI should not call Retrofit/Room directly
# ==========================================
DATA["ARC-14"] = {
    "concept_en": """Allowing UI components (Composables, Activities, Fragments, or ViewModels) to directly invoke Retrofit network interfaces or Room DAOs violates the Single Responsibility Principle, breaks Separation of Concerns, and destroys architectural boundaries. Direct calls couple the presentation layer tightly to transport protocols (HTTP status codes, REST paths, DTO annotations) and local database schemas (SQLite tables, column names, foreign keys). Any backend API contract change or Room database migration shatters UI code across the application. Furthermore, bypassing the Repository layer eliminates centralized caching policies, prevents single-source-of-truth coordination, scatters background thread dispatching, and renders automated unit testing impossible without heavy network mocks and SQLite instances.""",
    "walkthrough_en": """Contrasting direct DAO/API calls with clean repository mediation:
```kotlin
// ❌ ANTI-PATTERN: ViewModel directly coupled to Retrofit and Room DAO
class BadProductViewModel(
    private val api: ProductRetrofitApi,
    private val dao: ProductRoomDao
) : ViewModel() {
    fun loadProducts() {
        viewModelScope.launch {
            val response = api.fetchProducts() // Couples UI to HTTP response wrappers!
            if (response.isSuccessful) {
                dao.insertAll(response.body()!!.map { it.toEntity() }) // UI manages DB cache manually!
            }
        }
    }
}

// ✅ CLEAN ARCHITECTURE: Repository mediates sources, UI observes pure domain models
class CleanProductViewModel(
    private val repository: ProductRepository
) : ViewModel() {
    val products: StateFlow<List<Product>> = repository.observeProducts()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    fun refresh() {
        viewModelScope.launch { repository.refreshProducts() }
    }
}
```""",
    "short_en": """Calling Retrofit or Room directly from the UI couples presentation logic to network protocols and SQLite schemas. It bypasses offline caching, prevents single-source-of-truth synchronization, and makes UI testing impossible without complex network mocks. Repositories abstract these details, exposing clean domain streams and handling caching transparently.""",
    "structured_en": """To begin with, allowing the UI layer to communicate directly with Retrofit or Room DAOs creates fatal architectural coupling.
From an architectural standpoint, the UI layer is designed to be a passive consumer focused purely on rendering state and dispatching user interactions. When a Composable or ViewModel calls network endpoints or database queries directly, it assumes responsibility for transport mechanics, HTTP headers, SQL queries, and table joins.
In production scenarios, this bypasses the single source of truth. The UI is forced to manually coordinate caching—deciding whether to write to the database or read from the network—leading to fragmented data states and duplicate network traffic across different screens.
As for maintainability and testing, direct coupling makes unit testing presentation logic nearly impossible without mocking network sockets and SQLite cursors, while any minor backend API modification shatters UI controllers across the entire app.""",
    "deep_senior_en": """Under the hood, exposing network clients and database DAOs to the presentation layer destroys architectural boundaries and causes catastrophic lifecycle bugs. Retrofit calls return raw HTTP response wrappers and transport DTOs containing nullable attributes and server metadata. If an Activity or ViewModel directly parses these objects, network parsing exceptions occur directly on the main thread, while business validation logic becomes scattered across dozens of individual UI files.
Similarly, directly invoking Room DAOs from ViewModels couples presentation logic to the local database schema. When a database migration alters column names or normalizes relational tables, UI code breaks. Furthermore, if two independent ViewModels write to the DAO directly without a centralized repository mediator, optimistic concurrency conflicts and write-skew anomalies arise because there is no unified coordination of caching policies or transaction boundaries.
The Repository pattern provides a necessary abstraction layer. It encapsulates the coordination of remote network calls with local database writes, executes background thread dispatching on Dispatchers.IO, handles token re-authentication, and exposes clean, immutable domain models through Flow.
Staff engineers enforce this separation through strict dependency injection rules and modular Gradle boundaries. Feature modules implementing UI and ViewModels are given dependencies only on repository interfaces, completely lacking compile-time visibility of Retrofit interfaces or Room DAO annotations. This guarantees that infrastructure changes never impact the presentation layer.""",
    "meta_ar": {
        "id": "ARC-14",
        "questionAr": "لماذا يجب ألا تتصل واجهة المستخدم (UI) مباشرة بمكتبة Retrofit أو Room DAOs؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبادئ فصل المسؤوليات، وإدراك مخاطر الارتباط المباشر بأطر العمل والشبكات وقواعد البيانات، ومعرفة دور نمط المستودع في عزل تفاصيل البنية التحتية وتسهيل الاختبارات.",
        "why_it_matters_ar": "الاتصال المباشر يجعل شاشات التطبيق مرتبطة بجداول SQLite وأكواد الـ HTTP، وأي تعديل في السيرفر أو تغيير في بنية قاعدة البيانات سيكسر كود الواجهات ويجعل كتابة اختبارات الوحدة مستحيلة بدون تشغيل محاكي وقواعد بيانات حقيقية.",
        "worked_example_ar": "عزل مصادر البيانات خلف واجهة ريبوزيتوري بدلاً من النداء المباشر:\n```kotlin\n// خطأ كارثي: الـ ViewModel يكلم Retrofit و Room مباشرة\n// صح: الـ ViewModel يعتمد فقط على واجهة المستودع النظيفة\nclass ProductViewModel(private val repository: ProductRepository) : ViewModel() {\n    val products = repository.getProducts().stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())\n}\n```",
        "trade_offs_ar": "الوساطة عبر المستودعات تتطلب إنشاء طبقات وواجهات إضافية، لكنها توفر عزلاً معمارياً تاماً وتمنع تكرار كود الكاش في كل شاشة وتتيح استبدال المكتبات بسهولة.",
        "failure_modes_ar": "معالجة أكواد الـ HTTP مثل 404 أو استعلامات SQL داخل الـ ViewModel أو الـ Composable، مما يربط الواجهة بتفاصيل البروتوكولات التقنية.",
        "production_perspective_ar": "في المشروعات الكبرى، نقوم بعزل مكتبات Retrofit و Room داخل موديولات Gradle مستقلة (:core:network و :core:database)، ولا نمنح موديول الواجهة صلاحية رؤيتها، بل نجعلها ترى فقط واجهات المستودع المحددة في موديول الدومين.",
        "how_to_answer_ar": "اشرح أن الواجهة وظيفتها العرض فقط وليست إدارة الشبكة والتخزين، وبيّن أن الاتصال المباشر يكسر مبدأ المصدر الأوحد للحقيقة ويجعل الكود مستحيل الاختبار، واشرح كيف يعزل الـ Repository تفاصيل بروتوكولات الاتصال وجداول الـ SQL.",
        "talking_points_ar": "فصل المسؤوليات، وحماية الواجهة من تغيرات جداول الـ SQL والـ APIs، ومركزية سياسات الكاش والمزامنة، وتسهيل اختبارات الـ Unit Tests على الـ JVM.",
        "follow_ups_ar": "- **المحاور:** \"إيه اللي هيحصل لو غيرنا مكتبة الشبكة من Retrofit لـ Ktor في تطبيق فيه نداءات مباشرة من الـ UI؟\"\n  **المرشح:** \"هنضطر نعدل كود كل الشاشات والـ ViewModels في التطبيق بالكامل لأنها معتمدة على كلاسات Retrofit، بينما بوجود Repository التعديل بيحصل في مكان واحد بس داخل طبقة الداتا بدون لمس شاشة واحدة.\"\n\n- **المحاور:** \"إزاي ده بيأثر على كتابة الـ Unit Tests للـ ViewModel؟\"\n  **المرشح:** \"لو الـ ViewModel بيكلم Retrofit أو Room مباشرة، هنحتاج نعمل Mock لـ HTTP Client وقواعد بيانات SQLite معقدة، بينما بوجود Repository بنعمل Fake بسيط بيرجع ليستة داتا في ثوانٍ.\"",
        "self_check_ar": "هل بينت مخاطر الربط المباشر بجداول SQLite والشبكة؟ هل شرحت أثر ذلك على الاختبارات ومبدأ SSOT؟ وهل وضحت دور موديولات Gradle في منع ذلك؟",
        "references_ar": f"- [Guide to app architecture - Data layer](https://developer.android.com/topic/architecture/data-layer) — توثيق جوجل لأهمية طبقة المستودعات وعزل مصادر البيانات.\n- [Separation of concerns](https://en.wikipedia.org/wiki/Separation_of_concerns) — المبدأ البرمجي لفصل المسؤوليات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الاتصال المباشر من الواجهة بـ Retrofit أو Room بيربط شاشات العرض ببروتوكولات الشبكة وهيكل جداول الـ SQL، وده بيكسر مبدأ المصدر الأوحد للحقيقة وبيصعب إدارة الكاش، وبيخلي اختبارات الوحدة مستحيلة بدون تشغيل قواعد بيانات ومحاكيات حقيقية. الريبوزيتوري بيعزل التفاصيل دي كلها وبيعرض بيانات دومين نقية.",
        "best_answer_ar": "منع الواجهة من الاتصال المباشر بمكتبات الشبكة وقواعد البيانات هو أحد أهم القواعد المعمارية الصارمة في تطوير أندرويد.\n\nطبقة العرض والـ ViewModels وظيفتها الأساسية هي معالجة مدخلات المستخدم ورسم الشاشات، ومش مسؤوليتها تفكيك استجابات الـ HTTP أو كتابة استعلامات SQL وجداول الـ SQLite. لو سمحنا للواجهة تكلم Retrofit أو Room مباشرة، أي تغيير بسيط في الـ API من جهة الباك إند هيكسر كود الشاشات ويجبرنا نعيد كتابة الـ UI بالكامل.\n\nبالإضافة لده، الاتصال المباشر بيدمر مبدأ المصدر الأوحد للحقيقة؛ لأن كل شاشة هتضطر تدير الكاش بنفسها، فتقرر امتى تحفظ في الداتابيز وامتى تطلب من السيرفر، وده بيعمل تضارب فوري في البيانات بين الشاشات واستهلاك مفرط لباقة الإنترنت.\n\nوجود الـ Repository بيحل كل المشاكل دي؛ لأنه بيشتغل كطبقة حماية بتعزل تفاصيل التقنيات وبتتولى المزامنة وإدارة الخيوط في الخلفية، وبترجع للواجهة تدفقات بيانات دومين نقية ومستقرة تماماً.",
        "deep_answer_ar": "تحت الكابوت، ربط كلاسات العرض بـ Retrofit Interfaces أو Room DAOs بيكسر حدود العمارة النظيفة وبيفتح الباب لأخطاء دورة حياة معقدة ومستعصية. استجابات Retrofit بترجع كائنات Response و DTOs مليانة حقول قابلة للقيمة الفارغة وميتاداتا خاصة بالسيرفر؛ فلو كلاس العرض استقبل الحاجات دي مباشرة، أي خطأ في معالجة الـ JSON هيحصل على الـ Main Thread ويجمد الواجهة، غير إن شروط التحقق من صحة البيانات هتتشتت بين ملفات التصميم.\n\nنفس المشكلة بتتكرر مع Room DAOs؛ لو الـ ViewModel بينادي استعلامات الـ SQL مباشرة، كود العرض هيرتبط ارتباطاً وثيقاً بأسماء الأعمدة والمفاتيح الأجنبية في SQLite، وأي Database Migration هتتطلب تعديل كود الـ UI. ده غير إن نداء الـ DAO من كذا شاشة في نفس الوقت بدون مستودع وسيط منظم هيسبب مشاكل Concurrency وتعارض كتابة خطير.\n\nنمط المستودع بيوفر العزل الكامل؛ بيتكفل بالتبديل لـ `Dispatchers.IO`، وحل تعارض البيانات وتحديث الـ Tokens، وتوفير نماذج دومين نقية ومحصنة ضد أي انهيار.\n\nالمهندسون الكبار بيفرضوا القاعدة دي في بناء المشروع عبر موديولات Gradle المستقلة؛ موديول الواجهة مبياخدش أي صلاحية وصول أو Implementation لموديولات الشبكة وقواعد البيانات، بحيث يمنع الكومبايلر أي مطور من استيراد كلاسات Retrofit أو Room داخل طبقة العرض من الأساس."
    }
}

# ==========================================
# ARC-15: When to introduce interfaces vs concrete
# ==========================================
DATA["ARC-15"] = {
    "concept_en": """Interfaces in software architecture decouple contractual abstractions from concrete execution details, enabling polymorphism, the Dependency Inversion Principle, and isolated unit testing. Interfaces should be introduced when: (1) multiple distinct production implementations exist or are planned (such as PaymentGateway implemented via Stripe, PayPal, and Google Pay, or BiometricAuthenticator with platform variants), (2) formal architectural boundaries must be enforced across modules (e.g., Domain defines a Repository interface, while Data provides the concrete implementation), or (3) high-fidelity test fakes are required for deterministic JVM testing without mocking libraries. Conversely, concrete classes are entirely sufficient for internal helpers, data mappers, private repository implementations, and Use Cases that have exactly one logical implementation. Creating 1:1 interfaces (e.g. ILoginUseCase and LoginUseCaseImpl) creates interface pollution, adds navigation indirection, and provides zero architectural value.""",
    "walkthrough_en": """Contrasting necessary boundary interfaces with sufficient concrete classes:
```kotlin
// 1. GENUINE NEED FOR INTERFACE: Architectural boundary & test fakes
interface PaymentGateway {
    suspend fun processPayment(amount: Double): Result<TransactionReceipt>
}
// Concrete production implementation in :core:data
class StripePaymentGateway(private val api: StripeApi) : PaymentGateway { ... }
// Test fake in :core:testing for lightning-fast unit tests
class FakePaymentGateway : PaymentGateway {
    var shouldFail = false
    override suspend fun processPayment(amount: Double) =
        if (shouldFail) Result.failure(Exception("Declined")) else Result.success(TransactionReceipt("TX-1"))
}

// 2. CONCRETE SUFFICIENT: Single-purpose UseCase with pure domain rules
class CalculateLoanInterestUseCase { // ❌ DO NOT create ICalculateLoanInterestUseCase!
    operator fun invoke(principal: Double, rate: Double, tenureMonths: Int): Double {
        return (principal * rate * tenureMonths) / 1200.0
    }
}
```""",
    "short_en": """Introduce interfaces at architectural boundaries to invert dependencies, when multiple implementations exist like different payment gateways, or to enable fake implementations in tests. Concrete classes are sufficient for internal use cases, mappers, and utilities where only one implementation exists and mocking or direct instantiation is straightforward.""",
    "structured_en": """To begin with, deciding between an interface and a concrete class requires evaluating boundary isolation and polymorphic necessity against navigation friction.
From an architectural standpoint, interfaces are essential at architectural boundaries where you need to enforce the Dependency Inversion Principle. For example, declaring a Repository interface in the domain layer allows the data layer to implement it without the domain depending on data implementation details.
In production scenarios, interfaces are mandatory when multiple implementations exist, such as swapping between Google Play Billing and Stripe, or providing high-fidelity test fakes for fast JVM unit tests without mock libraries.
As for concrete classes, they are entirely sufficient for use cases, mappers, and internal repository helpers that have only one reasonable implementation. Creating 1:1 interfaces with names like ILoginUseCase adds navigation indirection and cognitive noise without delivering any real polymorphic or testability advantage.""",
    "deep_senior_en": """Under the hood, dogmatic adherence to the interface-everything rule stems from legacy Java and C# paradigms where mocking libraries required interfaces to generate dynamic proxies. In modern Kotlin and Android development with MockK and native test fakes, creating an interface with a single Impl class for every single component is an anti-pattern known as interface pollution.
Interfaces shine when they define stable contracts across module boundaries. In multi-module Gradle setups, a feature module should depend only on an interface PaymentRepository defined in core model or core domain, while the concrete PaymentRepositoryImpl in core data is wired in via Hilt. This drastically reduces incremental build times because modifying the internal logic of PaymentRepositoryImpl does not invalidate the build cache of the consuming feature module.
Furthermore, interfaces are superior when creating hand-crafted test fakes. While mocking libraries introduce reflection overhead, implementing a lightweight FakeUserRepository backing operations with a simple in-memory list makes unit tests lightning-fast, readable, and deterministic.
Staff engineers apply a clear rule: use interfaces at architectural and module boundaries, when multiple production implementations exist, or for external hardware/SDK wrappers. Use concrete classes for internal business logic, UseCases, and private helpers where polymorphism is absent and 1:1 interfaces merely add visual clutter.""",
    "meta_ar": {
        "id": "ARC-15",
        "questionAr": "متى نستخدم الواجهات (Interfaces) ومتى نكتفي بالكلاسات المباشرة (Concrete Classes)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اتخاذ قرار هندسي متزن في استخدام الواجهات البرمجية، وفهم مبدأ قلب التبعيات وتأثير الواجهات على سرعة البناء في Gradle، وتجنب فخ التوصيف المفرط (Interface Pollution).",
        "why_it_matters_ar": "إنشاء واجهة لكل كلاس في المشروع (مثل ILoginUseCase و LoginUseCaseImpl) يضاعف عدد الملفات ويزيد من صعوبة تتبع الكود دون أي فائدة، بينما إغفال الواجهات عند حدود الموديولات يمنع عزل الطبقات ويعطل بناء الاختبارات المعزولة.",
        "worked_example_ar": "المقارنة بين واجهة ضرورية لعقد متعدد التنفيذ وكلاس مباشر لحالة استخدام نقية:\n```kotlin\n// واجهة ضرورية: عقد لبوابة دفع تدعم Stripe و PayPal وتسهل عمل Fake للاختبار\ninterface PaymentGateway { suspend fun charge(amount: Double): Result<String> }\n\n// كلاس مباشر كافٍ تماماً: UseCase له تطبيق واحد فقط ولا يحتاج واجهة وسيطة\nclass CalculateTaxUseCase {\n    operator fun invoke(amount: Double, rate: Double): Double = amount * rate\n}\n```",
        "trade_offs_ar": "استخدام الواجهات يمنح مرونة عالية في استبدال الأكواد وتسريع اختبارات الـ Fakes، لكنه يضيف ملفات كود وتجريداً إضافياً يتطلب وقتاً في الصيانة والتنقل.",
        "failure_modes_ar": "كتابة واجهات وهمية بنمط `IFoo` لكل كلاس حتى لو كان مخصصاً لغرض داخلي وحيد، أو إهمال الواجهات عند حدود الموديولات مما يسبب ارتباطاً مباشراً بين الموديولات.",
        "production_perspective_ar": "في المشروعات الكبرى، نلزم المطورين بإنشاء Interfaces فقط عند حدود الموديولات (Module Boundaries)، وعند وجود أكثر من تطبيق حقيقي (مثل بوابات الدفع أو الـ Analytics)، بينما نكتفي بـ Concrete Classes للـ UseCases والمحولات والمساعدات الداخلية.",
        "how_to_answer_ar": "حدد الحالات الثلاث التي تستلزم Interface: قلب التبعيات عند الحدود، وتعدد التنفيذات البرمجية، وعمل Test Fakes للاختبارات السريعة. وأكد أن الكلاس المباشر كافٍ للـ Use Cases والمساعدات الداخلية لتجنب الـ Interface Pollution.",
        "talking_points_ar": "مبدأ قلب التبعيات، وتجنب الـ Interface Pollution، وتحسين سرعة الـ Incremental Build في Gradle، واستخدام Test Fakes كبديل للموكينج.",
        "follow_ups_ar": "- **المحاور:** \"ليه بعض المطورين بيصروا يعملوا Interface لكل UseCase زي ILoginUseCase؟\"\n  **المرشح:** \"دي عادة قديمة موروثة من لغة Java زمان لما كانت مكاتب الـ Mocking بتشترط وجود Interface لإنشاء Proxies؛ في كوتلن الحديثة مع مكتبات زي MockK أو حتى إنشاء كلاس مباشر، التكنيك ده بيعتبر كود زيادة (Boilerplate) ملوش أي فايدة برمجية.\"\n\n- **المحاور:** \"إزاي استخدام Interfaces بين الموديولات بيسرع وقت الـ Build في Gradle؟\"\n  **المرشح:** \"لأن الموديول المستهلك بيعتمد على الـ Interface المستقرة، فلو عدلنا الكود الداخلي للـ Implementation في موديول الداتا، Gradle مش هيحتاج يعيد ترجمة (Recompile) لموديول الشاشة لأن الـ ABI الخاص بالـ Interface متغيرش.\"",
        "self_check_ar": "هل حددت الحالات التي تتطلب واجهات؟ هل نبهت إلى مشكلة الـ Interface Pollution؟ وهل بينت أثر الواجهات على سرعة بناء Gradle؟",
        "references_ar": f"- [Interface segregation principle](https://en.wikipedia.org/wiki/Interface_segregation_principle) — مبدأ فصل الواجهات.\n- [Modularization best practices](https://developer.android.com/topic/modularization/patterns) — أنماط التجريد وتصميم الموديولات من جوجل.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنستخدم الواجهات (Interfaces) لما نكون محتاجين نقلب التبعيات عند حدود الموديولات والطبقات، أو لما يكون فيه أكتر من تطبيق فعلي للكود زي بوابات دفع مختلفة، أو علشان نعمل Test Fakes سريعة للاختبارات. وبنكتفي بالكلاسات المباشرة (Concrete Classes) للـ UseCases والمحولات والمساعدات الداخلية اللي ملهاش غير تطبيق واحد لتجنب زيادة الملفات بدون داعٍ.",
        "best_answer_ar": "القرار بين كتابة Interface أو الاكتفاء بـ Concrete Class هو ميزان هندسي بين مرونة التعديل وتكلفة التجريد البرمجي.\n\nالواجهات بتكون ضرورية في ثلاث حالات أساسية: أولاً عند حدود الطبقات والموديولات لتحقيق مبدأ قلب التبعيات، زي إن الدومين يحدد واجهة المستودع وموديول الداتا ينفذها. ثانياً لما يكون عندنا أكتر من تنفيذ حقيقي لنفس العقد في بيئة العمل، زي دعم الدفع عبر فوري وفيزا وباي بال، أو التعامل مع البلوتوث بحسب نوع الجهاز. ثالثاً علشان نقدر نعمل Test Fakes نكتبها بإيدينا للاختبارات المعزولة على JVM بدون الحاجة لمكتبات Mocking.\n\nفي المقابل، كتابة Interface لكل كلاس في المشروع بدون سبب حقيقي بيعتبر فخ برمجي معروف بـ Interface Pollution؛ فالـ UseCases والمحولات والكلاسات المساعدة اللي ملهاش غير تطبيق واحد فقط، الأفضل تتكتب كـ Concrete Classes مباشرة لتسهيل قراءة الكود والتنقل السريع بين الملفات.",
        "deep_answer_ar": "تحت الكابوت، الإصرار على عمل واجهات لكل كلاس نابع من عادات قديمة في بيئات الجافا القديمة حيث كانت مكاتب الـ Mocking القديمة بتعجز عن محاكاة الكلاسات المباشرة بدون Interfaces. في كوتلن الحديثة ومع مكاتب زي MockK أو حتى إنشاء نسخ تجريبية، عمل `ILoginUseCase` و `LoginUseCaseImpl` بيعتبر كود ميت مبيضيفش أي قيمة وبيضاعف عدد الملفات على الفاضي.\n\nالقيمة الحقيقية للواجهات بتظهر عند حدود الموديولات في مشاريع Gradle المتعددة. لما موديول الشاشة يعتمد على `interface PaymentRepository` الموجودة في موديول العقود، وموديول الداتا هو اللي ينفذها عبر `PaymentRepositoryImpl`، إحنا بنكسب ميزة معمارية ضخمة في سرعة الـ Incremental Build؛ لأنك لو عدلت أي كود داخلي في كلاس التنفيذ، الـ Gradle مش هيعيد ترجمة موديول الشاشة نهائياً لأن الـ ABI الخاص بالواجهة ثابت.\n\nكمان الواجهات بتمكننا من بناء Test Fakes خفيفة جداً بتعتمد على قوائم في الذاكرة بدلاً من بطء مكاتب الـ Mocking والـ Reflection، وده بيخلي اختبارات الـ Unit Tests تجري في أجزاء من الثانية.\n\nالمهندسون الكبار بيطبقوا قاعدة ذهبية واضحة: استخدم Interface عند حدود الموديولات، وللمكتبات الخارجية والحساسات، وحيثما وجد تعدد في التطبيقات؛ واعتمد على الكلاسات المباشرة في كل منطق الأعمال والـ Use Cases والمساعدات الداخلية ما دامت لا تتطلب تبديلاً متعدداً."
    }
}

# ==========================================
# ARC-16: Package-by-layer vs Package-by-feature
# ==========================================
DATA["ARC-16"] = {
    "concept_en": """Code organization strategy governs codebase discoverability, coupling boundaries, and scalability. Package-by-layer groups code according to technical roles (e.g. presentation/, domain/, data/, adapters/), pooling all ViewModels, Repositories, and DAOs together. Package-by-feature organizes code into functional user-facing business verticals (e.g. feature/auth/, feature/checkout/, feature/profile/), where each package contains its own UI components, ViewModels, Use Cases, and internal models. While package-by-layer is common in tiny tutorials, it causes low cohesion, tight cross-layer coupling, high merge conflicts, and blocks modularization in enterprise teams. Package-by-feature delivers high cohesion, strict encapsulation, independent team ownership, and directly mirrors multi-module Gradle architectures.""",
    "walkthrough_en": """Contrasting Package-by-layer with Package-by-feature:
```text
// ❌ PACKAGE-BY-LAYER: Low cohesion, cross-cutting sprawl
com.example.app/
├── presentation/
│   ├── LoginFragment.kt, CheckoutFragment.kt, ProfileFragment.kt
│   └── LoginViewModel.kt, CheckoutViewModel.kt, ProfileViewModel.kt
├── domain/
│   └── LoginUseCase.kt, CheckoutUseCase.kt
└── data/
    └── UserRepository.kt, OrderRepository.kt

// ✅ PACKAGE-BY-FEATURE: High cohesion, natural Gradle module boundaries
com.example.app/
├── feature/auth/
│   ├── LoginScreen.kt, LoginViewModel.kt, AuthRepository.kt
├── feature/checkout/
│   ├── CheckoutScreen.kt, CheckoutViewModel.kt, CheckoutUseCase.kt
└── core/database/ (shared foundational infrastructure)
```""",
    "short_en": """Package-by-layer groups code by technical function (all ViewModels together, all Repositories together), causing low cohesion and tight coupling. Package-by-feature groups code by business verticals (authentication, checkout), maximizing cohesion, reducing cross-feature merge conflicts, and serving as the direct stepping stone to multi-module Gradle architectures.""",
    "structured_en": """To begin with, package organization directly impacts codebase scalability, developer velocity, and architectural modularity.
From an architectural standpoint, package-by-layer groups classes according to technical categories: all activities in one package, all viewmodels in another, and all repositories in a third. This creates low cohesion because working on a single feature like user authentication requires navigating across four distinct root packages, making deletion or refactoring cumbersome.
In production scenarios, package-by-feature groups all components belonging to a specific user journey—such as checkout, onboarding, or search—into a dedicated package. Each feature contains its own Composables, ViewModels, and private helpers, keeping related code tightly localized.
As for enterprise growth, package-by-feature maps seamlessly to multi-module Gradle architectures. Teams can easily extract feature modules into isolated Gradle modules, enabling parallel compilation, fine-grained access control, and independent feature team ownership without cross-team merge conflicts.""",
    "deep_senior_en": """Under the hood, the choice between package-by-layer and package-by-feature determines how cleanly code can be decoupled and compiled. In package-by-layer, classes within the same technical package have little semantic relationship—a CheckoutViewModel and an AuthViewModel share nothing except that they both extend the Android Jetpack ViewModel base class. Because dependencies crisscross horizontally between layers, developers easily introduce unintended circular couplings, and deleting a deprecated feature requires hunting down files across every layer folder.
Package-by-feature adheres to the Common Closure Principle: classes that change together should be packaged together. When modifying the checkout user experience, all relevant Composables, ViewModels, and state models reside in the same directory. Features can mark internal helpers with Kotlin's internal visibility modifier, protecting private implementation details from being accidentally imported by unrelated features.
In modern Android enterprise development, this structure directly mirrors the modularization strategy recommended by Google. Core shared functionality lives in core network, core database, and core designsystem, while feature verticals are packaged independently as feature cart, feature payments, and feature settings.
Staff engineers ensure that feature packages never depend on peer feature packages directly. Any cross-feature communication is handled via navigation deep links or core API interfaces, allowing Gradle to build feature modules in parallel and drastically reducing CI build times across large engineering departments.""",
    "meta_ar": {
        "id": "ARC-16",
        "questionAr": "قارن بين تنظيم الكود حسب الطبقات (Package-by-Layer) وحسب الميزات (Package-by-Feature).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم معايير تنظيم الملفات في المشروعات الضخمة، والقدرة على تطبيق مبدأ Common Closure Principle، وإدراك كيف يمهد التنظيم حسب الميزات لتقسيم المشروع لموديولات Gradle مستقلة.",
        "why_it_matters_ar": "التنظيم حسب الطبقات يسبب تشتت المطورين بين مجلدات متباعدة عند تعديل ميزة واحدة، ويزيد من تعارضات الدمج (Merge Conflicts)، ويجعل من المستحيل تحويل المشروع إلى موديولات مستقلة.",
        "worked_example_ar": "المقارنة الهيكلية بين الأسلوبين في مشروع أندرويد:\n```text\n// خطأ: تجميع تقني ضعيف الترابط (Package-by-Layer)\napp/presentation/ (LoginScreen, CartScreen)\napp/data/ (UserRepo, CartRepo)\n\n// صح: تجميع وظيفي عالي الترابط (Package-by-Feature)\nfeature/auth/ (LoginScreen, LoginViewModel, AuthRepo)\nfeature/cart/ (CartScreen, CartViewModel, CartRepo)\ncore/database/ (قاعدة البيانات المشتركة)\n```",
        "trade_offs_ar": "التنظيم حسب الميزات يتطلب تخطيطاً دقيقاً للخدمات المشتركة، لكنه يوفر ترابطاً عالياً (High Cohesion) وعزلاً ممتازاً ويسهل حذف أو استبدال الميزات بالكامل.",
        "failure_modes_ar": "استخدام Package-by-Layer في مشروعات تتجاوز 50 شاشة، مما يجعل حذف ميزة قديمة يتطلب البحث اليدوي في عشرات المجلدات وحذف ملفات متفرقة بحذر شديد.",
        "production_perspective_ar": "في المشروعات الكبرى، نعتمد Package-by-Feature كخطوة تمهيدية لتحويل كل ميزة إلى موديول Gradle منفصل (`:feature:checkout`)، مما يسمح للفرق الهندسية بالعمل بالتوازي وتحسين وقت الـ Build عبر ميزة Parallel Compilation.",
        "how_to_answer_ar": "قارن بينهما من حيث الترابط: الطبقات تجمع الكود بحسب دوره التقني مما يسبب تشتتاً، بينما الميزات تجمع كل ما يخص الشاشة في مجلد واحد، واشرح كيف يمهد الأخير لتقسيم المشروع لموديولات Gradle ومبدأ Common Closure.",
        "talking_points_ar": "مبدأ Common Closure Principle، والترابط العالي والاقتران المنخفض (High Cohesion, Low Coupling)، وسهولة حذف الميزات القديمة، والتجهيز لموديولات Gradle المستقلة.",
        "follow_ups_ar": "- **المحاور:** \"لو ميزتين محتاجين يستخدموا نفس كود البيانات، بنحطه فين في Package-by-Feature؟\"\n  **المرشح:** \"بنفصل الكود المشترك ده في موديول أو باكيدج أساسية في الـ Core، زي `:core:data` أو `:core:model`، بحيث تعتمد عليه الميزتان بدون ما يعتمدوا على بعض بشكل دائري.\"\n\n- **المحاور:** \"إزاي استخدام Package-by-Feature بيساعد في تقليل الـ Merge Conflicts في الـ Git؟\"\n  **المرشح:** \"لأن كل فريق بيشتغل داخل مجلد الميزة الخاصة بيه بدون لمس مجلدات الميزات التانية، بينما في Package-by-Layer كل المطورين بيعدلوا في نفس ملفات ومجلدات الـ presentation والـ data الرئيسية.\"",
        "self_check_ar": "هل قارنت بين الترابط في الأسلوبين؟ هل شرحت مبدأ Common Closure؟ وهل بينت علاقة التنظيم حسب الميزة بتقسيم موديولات Gradle؟",
        "references_ar": f"- [Modularization patterns: Feature and core modules](https://developer.android.com/topic/modularization/patterns) — توثيق جوجل الرسمي لموديولات الميزات والأساسيات.\n- [Clean Architecture: Package by Feature](https://blog.cleancoder.com) — مقالات روبرت سي مارتن حول تنظيم الحزم البرمجية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "التنظيم حسب الطبقات (Package-by-Layer) بيجمع الملفات بحسب وظيفتها التقنية (كل الـ ViewModels مع بعض وكل الـ Repositories مع بعض)، وده بيقلل الترابط ويزود تشتت المطورين. بينما التنظيم حسب الميزات (Package-by-Feature) بيجمع كل ما يخص الميزة الواحدة زي الدخول أو الشراء في مجلد واحد، وده بيحقق ترابط عالي ويسهل تقسيم المشروع لموديولات Gradle.",
        "best_answer_ar": "طريقة تنظيم المجلدات بتحدد بشكل مباشر سرعة الفريق الهندسي وسهولة صيانة وتطوير التطبيق مع مرور الوقت.\n\nالتنظيم حسب الطبقات هو الأسلوب التقليدي اللي بنشوفه في الدروس التعليمية البسيطة؛ بيقسم الكود لمجلدات تقنية زي مجلد لكل شاشات العرض ومجلد للـ ViewModels ومجلد للـ Repositories. المشكلة هنا إن المطور لما ييجي يشتغل على ميزة تسجيل الدخول، بيضطر يفتح أربع مجلدات مختلفة ويعدل ملفات متفرقة، ولو قررنا نحذف الميزة دي بنعاني في تتبع ملفاتها المشتتة.\n\nأما التنظيم حسب الميزات فبيجمع كل الملفات الخاصة برحلة مستخدم معينة داخل نفس الحزمة البرمجية؛ ميزة الدفع فيها الـ Screen والـ ViewModel والـ UseCase الخاصة بيها، وده بيحقق مبدأ برمجي مهم اسمه Common Closure Principle، ومفاده إن الحاجات اللي بتتغير مع بعضها لازم تعيش مع بعضها.\n\nالميزة الأكبر في المشاريع الكبيرة هي إن التنظيم حسب الميزة بيمهد الطريق تلقائياً لتحويل كل ميزة لموديول Gradle مستقل، وده بيسمح بتسريع وقت الكومبايل وتشغيل البناء بالتوازي وتقليل تعارضات الـ Git بين فرق العمل.",
        "deep_answer_ar": "تحت الكابوت، الفارق الجوهري بين الأسلوبين بيرجع لمفاهيم الترابط والاقتران (Cohesion and Coupling). في نظام Package-by-Layer، الكلاسات اللي متجمعة في نفس الفولدر ملهاش أي علاقة منطقية ببعضها؛ كلاس `CheckoutViewModel` ملوش أي علاقة بـ `AuthViewModel` سوى إن الاتنين بيورثوا من كلاس ViewModel بتاع أندرويد. ده بيخلق ارتباطات أفقية معقدة بين الطبقات وممكن يوقع المطورين في مشكلة التبعيات الدائرية.\n\nنظام Package-by-Feature بيحقق أقصى درجات الترابط الداخلي (High Cohesion) وأقل درجات الاقتران الخارجي (Low Coupling). الملفات اللي بتخدم نفس الهدف التجاري بتكون متجاورة، وبنقدر نستخدم الكلمة المفتاحية `internal` في كوتلن لحماية الكلاسات المساعدة داخل الميزة ومنع أي شاشة تانية من استيرادها بالخطأ.\n\nفي المعمارية الحديثة المعتمدة من جوجل، التقسيم ده هو النواة الأساسية لتقسيم المشروع لموديولات Gradle؛ فكل مجلد ميزة بيتحول لـ Feature Module مستقل زي `:feature:checkout`، والمكونات المشتركة بتنزل في موديولات أساسية زي `:core:database` و `:core:designsystem`.\n\nالمهندسون الكبار بيمنعوا تماماً أي موديول ميزة من الاعتماد المباشر على موديول ميزة زميل له، وبيعتمدوا على Navigation Deep Links أو Interfaces مشتركة في الـ Core، وده بيسمح لـ Gradle بعمل Parallel Compilation ويقلل أوقات الـ CI/CD بنسب تصل لسبعين بالمئة. وبكده بنضمن إن الفرق الهندسية الكبيرة تقدر تضيف ميزات جديدة بسرعة بدون ما تعطل شغل الفرق التانية أو تكسر البنية المعمارية العامة للمشروع."
    }
}

# ==========================================
# ARC-17: One-time effects in UDF
# ==========================================
DATA["ARC-17"] = {
    "concept_en": """In Unidirectional Data Flow (UDF), UI state is continuous and persistent, representing what is currently rendered on screen. However, applications constantly produce transient, one-time side effects—such as displaying a Snackbar, showing a Toast, triggering haptic feedback, or executing navigation events. If one-time effects are improperly modeled as raw properties inside persistent StateFlow state, configuration changes (such as device rotation) cause the newly created UI subscriber to re-observe the state and replay the effect (triggering duplicate Snackbars or navigating twice). Architectural solutions include: (1) single-event buffered Kotlin Channels exposed as Flows and collected via LaunchedEffect with repeatOnLifecycle, or (2) modeling effects as consumable message objects inside the UI state with unique IDs, where the UI dispatches a consumption event back to the ViewModel immediately upon rendering.""",
    "walkthrough_en": """Managing one-time effects using a buffered Channel in Jetpack Compose:
```kotlin
// 1. Define transient side effects as a sealed interface
sealed interface CheckoutEffect {
    data class ShowToast(val message: String) : CheckoutEffect
    data class NavigateToReceipt(val orderId: String) : CheckoutEffect
}

// 2. ViewModel exposes buffered Channel as Flow
class CheckoutViewModel : ViewModel() {
    private val _effectChannel = Channel<CheckoutEffect>(Channel.BUFFERED)
    val effects: Flow<CheckoutEffect> = _effectChannel.receiveAsFlow()

    fun onPayClicked(orderId: String) {
        viewModelScope.launch {
            _effectChannel.send(CheckoutEffect.ShowToast("Payment successful!"))
            _effectChannel.send(CheckoutEffect.NavigateToReceipt(orderId))
        }
    }
}

// 3. Compose UI collects effect safely via LaunchedEffect
@Composable
fun CheckoutScreen(viewModel: CheckoutViewModel, onNavigate: (String) -> Unit) {
    val context = LocalContext.current
    LaunchedEffect(Unit) {
        viewModel.effects.collect { effect ->
            when (effect) {
                is CheckoutEffect.ShowToast -> Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
                is CheckoutEffect.NavigateToReceipt -> onNavigate(effect.orderId)
            }
        }
    }
}
```""",
    "short_en": """Manage one-time effects using either a buffered Kotlin Channel exposed as a Flow for fire-and-forget events, or by modeling effects inside the UI state with unique identifiers that the UI marks as consumed. This prevents accidental event replay upon screen rotation or configuration changes.""",
    "structured_en": """To begin with, handling transient side effects like navigation or Snackbars requires preventing event replay during configuration changes.
From an architectural standpoint, persistent UI state models what is currently visible, whereas one-time effects represent discrete, non-persistent events. If an effect is stored as a raw property in StateFlow, rotating the device will cause the newly attached Composable to re-read the state and re-trigger the navigation or Toast.
In production scenarios, we use a buffered Kotlin Channel exposed as a Flow via receiveAsFlow. The UI observes this stream inside a LaunchedEffect scoped to the screen lifecycle, ensuring each event is delivered and consumed exactly once.
As for alternative architectures, teams can model effects directly inside the UI state as a list of consumable message objects with unique IDs. Once the Composable renders the Snackbar, it dispatches an onMessageShown event back to the ViewModel to remove the consumed item from state.""",
    "deep_senior_en": """Under the hood, the handling of one-time events has sparked significant debate in the Android community. Historically, developers used SingleLiveEvent or Event wrappers to prevent event replay on configuration changes. However, when migrating to coroutines and Flow, naive usage of SharedFlow can silently drop events if no collector is currently active—for example, if an event is emitted while the Activity is in the background or navigating between destinations.
Using a buffered Channel—configured as Channel(Channel.BUFFERED) and exposed via channel.receiveAsFlow—guarantees that events are buffered until an active collector subscribes. When the UI collects the flow using LaunchedEffect combined with repeatOnLifecycle(Lifecycle.State.STARTED), events emitted during background transitions remain in the buffer and are processed immediately when the UI resumes.
Conversely, Google's modern architectural guidance leans toward modeling events as part of UI state rather than separate side channels. In this approach, the UI state contains an optional property: data class CheckoutUiState containing userMessage. When the Composable displays the Snackbar, it invokes a callback like viewModel.onMessageDismissed, which resets userMessage to null.
Staff engineers choose the strategy based on team conventions: buffered Channels work exceptionally well for fire-and-forget imperative side effects like navigation actions and haptic triggers, while state-based message objects excel for user-visible notifications where state restoration and synchronization must remain completely predictable across process death.""",
    "meta_ar": {
        "id": "ARC-17",
        "questionAr": "كيف تدير الأحداث التي تحدث لمرة واحدة (One-Time Effects) في عمارة UDF؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم معضلة الأحداث العابرة (One-off Events) في المعمارية أحادية الاتجاه، وتجنب فخ إعادة تشغيل الأحداث (Event Replay) عند تدوير الشاشة، ومعرفة كيفية استخدام Channels أو Consumable State.",
        "why_it_matters_ar": "تخزين الأحداث العابرة كقيم عادية في StateFlow يجعل تدوير الشاشة يعيد عرض الـ Toast أو ينقل المستخدم مرتين لنفس الشاشة، مما يسبب تجربة استخدام سيئة وأخطاء برمجية محرجة.",
        "worked_example_ar": "إدارة الأحداث عبر Channel مخزنة مؤقتاً لتستهلك مرة واحدة فقط:\n```kotlin\nsealed interface Effect { data class Navigate(val id: String) : Effect }\nclass MyViewModel : ViewModel() {\n    private val _effects = Channel<Effect>(Channel.BUFFERED)\n    val effects = _effects.receiveAsFlow()\n    fun onDone(id: String) { viewModelScope.launch { _effects.send(Effect.Navigate(id)) } }\n}\n// في Compose:\nLaunchedEffect(Unit) { viewModel.effects.collect { effect -> /* تنفيذ لمرة واحدة */ } }\n```",
        "trade_offs_ar": "استخدام Channel يضمن استهلاك الحدث مرة واحدة وسهولة الكود، بينما نمذجة الحدث داخل الـ State تتيح النجاة من موت العملية (Process Death) وتتبع الحالة بدقة أكبر ولكنها تتطلب إرسال حدث تأكيد الاستهلاك.",
        "failure_modes_ar": "استخدام `SharedFlow` بدون buffer مما يتسبب في ضياع الأحداث إذا أُطلقت أثناء وجود الشاشة في الخلفية، أو استخدام متغير Boolean عادي داخل StateFlow دون تصفيره.",
        "production_perspective_ar": "في المشروعات الإنتاجية الكبرى، نفضل استخدام `Channel(Channel.BUFFERED)` للأحداث الفورية مثل التنقل والهزاز، بينما نستخدم كائنات الرسائل القابلة للاستهلاك (Consumable Messages مع `onDismiss`) لعرض الـ Snackbars والتنبيهات.",
        "how_to_answer_ar": "اشرح المشكلة أولاً: الأحداث العابرة تختلف عن الحالة المستمرة وتكرارها عند تدوير الشاشة خطأ فادح. ثم اعرض الحلين: استخدام Channel مخزنة مع LaunchedEffect، أو وضع الحدث ككائن مستهلك داخل الـ State يتم حذفه بعد العرض.",
        "talking_points_ar": "الفرق بين State و Events، ومعضلة Event Replay عند تدوير الشاشة، ومخاطر فقدان الأحداث في SharedFlow، واستخدام Buffered Channels مقابل Consumable State.",
        "follow_ups_ar": "- **المحاور:** \"ليه استخدام SharedFlow العادي ممكن يسقط أحداث وميوصلهاش للشاشة؟\"\n  **المرشح:** \"لأن لو الـ SharedFlow ملهوش Buffer أو مفيش مراقب نشط في اللحظة دي (زي لو الشاشة كانت في الـ Background)، الحدث بيضيع تماماً ومبيستناش لغاية ما الشاشة ترجع، بينما الـ Buffered Channel بتحتفظ بالحدث لغاية ما المراقب يصحى ويجمعه.\"\n\n- **المحاور:** \"إيه وجهة نظر جوجل الرسمية في التعامل مع الـ One-off Events؟\"\n  **المرشح:** \"جوجل بتفضل نمذجة الحدث كجزء من الـ UI State نفسها، بحيث يكون كائن شايل ID فريد، والواجهة تعرضه وتبعت أمر للـ ViewModel يقول `onEventConsumed(id)` فيمسحه من الـ State لضمان التناسق الكامل.\"",
        "self_check_ar": "هل شرحت مشكلة تكرار الحدث عند تدوير الشاشة؟ هل قارنت بين Channel و Consumable State؟ وهل حذرت من استخدام SharedFlow بدون buffer؟",
        "references_ar": f"- [Guide to app architecture - UI events](https://developer.android.com/topic/architecture/ui-layer/events) — توثيق جوجل الرسمي لإدارة أحداث واجهة المستخدم.\n- [ViewModel: One-off event antipatterns](https://medium.com/androiddevelopers/viewmodel-one-off-event-antipatterns-16a02b4a15b3) — مقال فريق أندرويد حول الأنماط الخاطئة في إدارة الأحداث العابرة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بندير الأحداث العابرة التي تحدث لمرة واحدة (زي التنقل أو رسائل الـ Toast) إما باستخدام Kotlin Channel مخزنة ومحمية بتدفق receiveAsFlow علشان تستهلك مرة واحدة، أو بوضع الحدث داخل كائن الـ UI State برقم تعريفي فريد والشاشة تبلغ الـ ViewModel بمسحه فور عرضه لمنع تكراره عند تدوير الشاشة.",
        "best_answer_ar": "التعامل مع الأحداث العابرة لمرة واحدة بيمثل تحدياً معمارياً مهماً في نمط التدفق أحادي الاتجاه UDF.\n\nحالة الواجهة (UI State) بطبيعتها مستمرة ومصممة تعبر عن اللي مرسوم على الشاشة حالياً، بينما أحداث المرة الواحدة زي التنقل لصفحة جديدة أو إظهار SnackBar هي أحداث لحظية غير مستمرة. لو خزننا الحدث ده كمتغير عادي جوه StateFlow، تدوير الموبايل هيخلي الشاشة ترجع تقرأ الحالة من أول وجديد وتعرض الـ SnackBar أو تعمل Navigate مرة تانية بدون قصد.\n\nأفضل حل عملي هو استخدام Kotlin Channel مخزنة بنوع `Channel.BUFFERED` ونعرضها كتدفق `Flow`؛ الـ Composable بيراقب التدفق ده داخل `LaunchedEffect`، وبكده بنضمن إن الحدث يتسلم ويتم تنفيذه لمرة واحدة فقط.\n\nالحل التاني المعتمد من جوجل هو وضع الحدث ككائن داخل الـ UI State نفسها مع ID فريد؛ وبمجرد ما الشاشة تعرض الرسالة بتبعت حدث للـ ViewModel ينظف الـ State ويمسح الكائن، وده بيضمن أعلى درجات التوافق والموثوقية.",
        "deep_answer_ar": "تحت الكابوت، إدارة أحداث المرة الواحدة أثارت نقاشات هندسية واسعة في مجتمع أندرويد. في السابق، كان المطورون بيستخدموا `SingleLiveEvent` أو أغلفة Event Wrapper لمنع التكرار أثناء تدوير الشاشة. ومع التحول للـ Coroutines والـ Flow، استخدام `SharedFlow` المباشر بدون buffer كان بيسقط الأحداث في صمت لو انطلقت والشاشة في الخلفية أو أثناء التنقل بين الصفحات.\n\nاستخدام Buffered Channel بمعادلة `Channel(Channel.BUFFERED)` وعرضها عبر `receiveAsFlow` بيضمن حجز الحدث بأمان لغاية ما يظهر مراقب نشط. ولما الشاشة تجمعه باستخدام `LaunchedEffect` مع `repeatOnLifecycle`، الأحداث اللي انطلقت أثناء توقف الشاشة بتفضل محفوظة في الـ Buffer وتتنفذ أول ما الشاشة ترجع تشتغل.\n\nفي المقابل، جوجل بتفضل حديثاً نمذجة الأحداث كجزء لا يتجزأ من الـ UI State؛ يعني الـ Data Class بيكون جواه كائن زي `userMessage: Message?`، والـ Composable بيعرض الـ Snackbar وينادي كولباك فوري `viewModel.onMessageShown()` لتصفير المتغير وإعادته لـ null.\n\nالمهندسون الكبار بيختاروا الأسلوب المناسب بحسب طبيعة الحدث: الـ Channels ممتازة جداً للأحداث الأمرية السريعة زي الهزاز وأوامر التنقل المباشرة، بينما نمذجة الرسائل داخل الـ State بتكون الأفضل للإشعارات المرئية اللي بتحتاج تزامن دقيق واستعادة للحالة عند إعادة بناء الشاشات. وده بيدي تحكم هندسي كامل في طريقة وصول المعلومة للمستخدم بدون أي تكرار أو فقدان للبيانات أثناء تقلبات النظام ودورة الحياة."
    }
}

# ==========================================
# ARC-18: ViewModel Main-Safe and Testable
# ==========================================
DATA["ARC-18"] = {
    "concept_en": """A ViewModel is main-safe when invoking any of its methods or coroutines from the main thread (UI thread) is guaranteed never to block the main thread, drop frames, or trigger Application Not Responding (ANR) dialogs. Main-safety is achieved by adhering to the convention that every suspending function must handle its own thread dispatching: repositories and data sources wrap blocking I/O (Room queries, Retrofit calls, disk writes) and intensive CPU processing (cryptography, large JSON parsing) in withContext(Dispatchers.IO) or withContext(Dispatchers.Default). The ViewModel launches coroutines directly on viewModelScope (which runs on Dispatchers.Main.immediate) without explicit dispatcher switches. To keep the ViewModel fully testable, CoroutineDispatchers must be injected via constructors rather than hardcoded, and the class must maintain zero dependencies on Android framework types (Context, View, Resources).""",
    "walkthrough_en": """Writing a main-safe, testable ViewModel with injected dispatchers:
```kotlin
// 1. Repository ensures internal main-safety via withContext
class AccountRepositoryImpl(
    private val api: AccountApi,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) : AccountRepository {
    override suspend fun updateAccountName(name: String): Result<Unit> = withContext(ioDispatcher) {
        runCatching { api.updateName(name) } // Main-safe: switches internally!
    }
}

// 2. ViewModel launches on viewModelScope and injects dispatchers for tests
class AccountViewModel(
    private val repository: AccountRepository,
    private val defaultDispatcher: CoroutineDispatcher = Dispatchers.Default
) : ViewModel() {
    private val _uiState = MutableStateFlow<AccountUiState>(AccountUiState.Idle)
    val uiState: StateFlow<AccountUiState> = _uiState.asStateFlow()

    fun updateName(name: String) {
        viewModelScope.launch { // Executes on Dispatchers.Main.immediate safely
            _uiState.value = AccountUiState.Loading
            repository.updateAccountName(name)
                .onSuccess { _uiState.value = AccountUiState.Success }
                .onFailure { _uiState.value = AccountUiState.Error(it.message ?: "Failed") }
        }
    }
}
```""",
    "short_en": """Ensure repositories and data sources switch to Dispatchers.IO or Default internally using withContext, making all suspending functions main-safe. Inject CoroutineDispatchers into ViewModels via constructor dependency injection, and use StandardTestDispatcher or UnconfinedTestDispatcher with runTest in unit tests to control execution deterministically.""",
    "structured_en": """To begin with, main-safety and testability are foundational requirements for building responsive, reliable Android ViewModels.
From an architectural standpoint, main-safety mandates that any suspending function can be invoked from the main thread without blocking the UI or dropping frames. Repositories enforce this by wrapping blocking operations—such as Room queries or Retrofit parsing—in withContext using Dispatchers.IO or Dispatchers.Default.
In production scenarios, the ViewModel launches coroutines inside viewModelScope on Dispatchers.Main.immediate, confident that underlying calls will yield the CPU safely. For testing, dispatchers should never be hardcoded; we inject CoroutineDispatchers via constructor parameters using dependency injection.
As for test verification, injecting dispatchers allows unit tests to replace production dispatchers with StandardTestDispatcher or UnconfinedTestDispatcher. Paired with runTest, this eliminates arbitrary sleep statements and gives unit tests total deterministic control over virtual time and asynchronous coroutine execution.""",
    "deep_senior_en": """Under the hood, maintaining main-safety requires adhering to the convention that every suspending function is responsible for its own thread switching. If a ViewModel has to specify withContext(Dispatchers.IO) before calling a repository method, that repository has leaked its threading requirements, violating encapsulation. By shifting the dispatcher switch inside the data source or repository implementation, the ViewModel remains clean and purely orchestrates UI state transitions on the main thread.
For testability, hardcoded dispatchers like Dispatchers.IO create flaky, non-deterministic unit tests because coroutines run on background thread pools outside the test framework's control. By providing an IoDispatcher and DefaultDispatcher via Hilt qualifiers and constructor injection, tests can inject a TestDispatcher instead.
In unit tests, replacing Dispatchers.Main requires configuring Dispatchers.setMain(testDispatcher) inside a JUnit TestWatcher or test rule. Using runTest with StandardTestDispatcher introduces a virtual scheduler where time does not actually pass; calls to delay execute instantaneously when calling advanceTimeBy or advanceUntilIdle.
Staff engineers also ensure testability by eliminating any Android framework dependencies from the ViewModel. ViewModels should never accept an Android Context, View instance, or Resources reference. Instead, error states expose parameterized string resource IDs, keeping the ViewModel a pure Kotlin class that compiles and tests on the local JVM in milliseconds. By adopting this disciplined testing architecture, developers achieve total coverage over complex asynchronous state flows while keeping test suites blazingly fast and maintenance-free.""",
    "meta_ar": {
        "id": "ARC-18",
        "questionAr": "كيف تحافظ على الـ ViewModel آمناً على المسار الرئيسي (Main-Safe) وقابلاً للاختبار؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ Main-Safety في الكوروتينات، وإدراك مسؤولية نقل العمليات الثقيلة إلى Dispatchers المناسبة داخل طبقة البيانات، والقدرة على حقن الـ Dispatchers واختبار الـ ViewModel باستخدام TestDispatcher و runTest.",
        "why_it_matters_ar": "تشغيل عمليات ثقيلة على المسار الرئيسي يؤدي إلى سقوط الإطارات وتجمد الواجهة وحدوث ANR، كما أن كتابة Dispatchers مدمجة بشكل ثابت تجعل اختبارات الوحدة متقلبة وغير مستقرة (Flaky Tests).",
        "worked_example_ar": "جعل الدوال آمنة واستخدام حقن التبعيات للـ Dispatchers:\n```kotlin\n// المستودع يتكفل بالتحويل لـ IO داخلياً\nclass Repo(val api: Api, val io: CoroutineDispatcher = Dispatchers.IO) {\n    suspend fun load() = withContext(io) { api.fetch() }\n}\n// الـ ViewModel يعمل على Main.immediate بثقة ويحقن الـ Dispatcher للاختبار\nclass MyViewModel(val repo: Repo) : ViewModel() {\n    fun fetch() = viewModelScope.launch { repo.load() }\n}\n```",
        "trade_offs_ar": "حقن الـ Dispatchers يتطلب تمريرها عبر الـ Constructor وكتابة Qualifiers في Hilt، لكنه يمنح تحكماً كاملاً في الوقت الافتراضي داخل اختبارات الوحدة السريعة.",
        "failure_modes_ar": "كتابة `withContext(Dispatchers.IO)` داخل الـ ViewModel نفسه، مما يعني تسريب تفاصيل التخزين والثريدز لطبقة العرض بدلاً من إبقائها داخل المستودع.",
        "production_perspective_ar": "في المشروعات الكبرى، نفرض قاعدة Lint تمنع استخدام `Dispatchers.IO` أو `Dispatchers.Default` بشكل مباشر في أي ViewModel أو Repository، وتلزم بحقنها عبر `@IoDispatcher` و `@DefaultDispatcher` في Hilt.",
        "how_to_answer_ar": "وضح شقين أساسيين: الأمان على المسار الرئيسي بجعل كل دالة معلقة مسؤولة عن ثريداتها عبر withContext داخل الريبوزيتوري، وقابلية الاختبار بحقن الـ Dispatchers واستبدالها بـ TestDispatcher مع runTest وخلو الـ ViewModel من أي كلاسات أندرويد.",
        "talking_points_ar": "مفهوم Main-Safety، ومسؤولية الدوال المعلقة في إدارة ثريداتها، وحقن الـ Dispatchers عبر Hilt، واستخدام TestDispatcher و virtual time في اختبارات JVM.",
        "follow_ups_ar": "- **المحاور:** \"ليه مينفعش نكتب Dispatchers.IO مباشرة جوه الـ ViewModel لو بنعمل عملية تخزين؟\"\n  **المرشح:** \"أولاً لأن مسؤولية تحديد نوع الـ Thread مكانها المستودع مش الـ ViewModel، وثانياً لأن كتابة `Dispatchers.IO` بشكل ثابت بتصعب الـ Unit Testing وتمنع التحكم في الوقت التخيلي؛ والأصح هو حقن الـ Dispatcher.\"\n\n- **المحاور:** \"إزاي بنختبر كود الكوروتين اللي جواه دالة delay(10_000) بدون ما نعطل التيست عشر ثواني؟\"\n  **المرشح:** \"باستخدام دالة `runTest` مع `StandardTestDispatcher`؛ الاختبار بيستخدم جدول زمني افتراضي (Virtual Time) فالدالة بتتنفذ في أجزاء من الميلي ثانية عن طريق استدعاء `advanceUntilIdle()`.\"",
        "self_check_ar": "هل شرحت مفهوم Main-Safety؟ هل أكدت أن الريبوزيتوري هو المسؤول عن withContext؟ وهل بينت كيفية حقن الـ Dispatchers واختبارها عبر runTest؟",
        "references_ar": f"- [Coroutines best practices on Android](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — أفضل ممارسات جوجل في التعامل مع الكوروتينات والـ Dispatchers.\n- [Testing Kotlin coroutines](https://developer.android.com/kotlin/coroutines/test) — توثيق جوجل الرسمي لاختبار الكوروتينات والـ ViewModels.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنحافظ على الـ ViewModel آمناً على المسار الرئيسي (Main-Safe) بجعل كل الدوال المعلقة في المستودعات مسؤولة عن نقل شغلها داخلياً لـ Dispatchers.IO أو Default عبر withContext. وبنحافظ عليه قابلاً للاختبار بحقن الـ Dispatchers عبر الـ Constructor وتجنب استيراد أي كلاسات تخص نظام أندرويد، علشان نشغل اختبارات سريعة ومتحكم فيها بالكامل عبر runTest على JVM.",
        "best_answer_ar": "تحقيق الـ Main-Safety وقابلية الاختبار في الـ ViewModel هو الضمان الأساسي لمنع تجمد التطبيق وتسهيل فحص الكود.\n\nمبدأ الـ Main-Safety بيعني إن أي دالة معلقة تقدر تناديها من الـ Main Thread بأمان تام بدون ما تسبب أي تقطيع في الشاشة أو سقوط للإطارات. بنحقق ده باتباع قاعدة إن كل دالة معلقة مسؤولة عن نقل الثريد الخاص بيها؛ يعني طبقة البيانات والمستودعات هي اللي بتنقل نداءات الشبكة وقواعد البيانات لـ `Dispatchers.IO` باستخدام `withContext`، والـ ViewModel بيشغل الكوروتين على `viewModelScope` اللي بيبدأ افتراضياً على المسار الرئيسي بأمان.\n\nوعلشان نخلي الـ ViewModel قابلاً للاختبار بنسبة مئة بالمئة، بنحرص على إننا منكتبش الـ Dispatchers كقيم ثابتة في الكود، بل بنحقنها عبر الـ Constructor باستخدام Hilt. ده بيسمح لنا في الـ Unit Tests نستبدلها بـ `TestDispatcher` مع دالة `runTest`.\n\nبالإضافة لده، بنحرص تماماً إن الـ ViewModel ميعرفش أي كلاسات من أندرويد زي `Context` أو `View`، فيتحول لكلاس كوتلن نقي يختبر في أجزاء من الثانية على الـ JVM.",
        "deep_answer_ar": "تحت الكابوت، الحفاظ على Main-Safety بيتطلب الالتزام الصارم باتفاقية إن كل دالة معلقة مسؤولة عن إدارة وتحديد مسارات التنفيذ الخاصة بيها بنفسها. لو الـ ViewModel اضطر يكتب withContext(Dispatchers.IO) قبل نداء أي دالة في المستودع، فده معناه فوراً إن المستودع سرب تفاصيل تشغيله وكسر مبدأ الكبسلة المعمارية السليمة.\n\nمن حيث الاختبارات، كتابة Dispatchers مدمجة ومباشرة بشكل ثابت داخل الكود بتعمل Flaky Tests وتخلي الاختبارات بطيئة وغير مضمونة على الإطلاق، لأن الكوروتين بيشتغل على Thread Pools خارجية خارجة عن نطاق سيطرة إطار الاختبار الآلي. لما بنحقن الـ Dispatchers عبر Hilt بـ Qualifiers واضحة ومحددة، بنقدر نستبدلها بكل سلاسة بـ TestDispatcher في كود الاختبار للتحكم التام في التزامن.\n\nفي بيئة الـ Unit Tests، بنستبدل Dispatchers.Main باستخدام Dispatchers.setMain(testDispatcher) داخل JUnit TestWatcher أو Test Rule مخصصة، واستخدام دالة runTest مع StandardTestDispatcher بيوفر Virtual Scheduler حقيقي بيخلي دالة delay تمر في جزء من الميلي ثانية عن طريق استدعاء advanceUntilIdle بدون أي تعطيل أو انتظار زمني حقيقي، وده بيضمن فحص كل انبعاثات الحالة بدقة.\n\nالمهندسون الكبار بيحرصوا كمان على استبعاد أي مراجع مباشرة لكلاسات أندرويد من الـ ViewModel؛ فممنوع نهائياً تمرير Context أو View أو Resources، بل بنعتمد على String Resource IDs ومغلفات رسائل داخل الـ UI State، وبكده يفضل الـ ViewModel كلاس كوتلن صافي وخفيف جداً يختبر في أجزاء من الثانية على الـ JVM مع عزل كامل لمنطق الأعمال ومرونة فائقة في الصيانة والتطوير المستقبلي."
    }
}


def main():
    print(f"Elevating {len(DATA)} questions in ARC (ARC-10 to ARC-18)...")
    for qid, data in DATA.items():
        ee.update_canonical_question(
            qid=qid,
            concept_en=data["concept_en"],
            walkthrough_en=data["walkthrough_en"],
            short_en=data["short_en"],
            structured_en=data["structured_en"],
            deep_senior_en=data["deep_senior_en"]
        )

    # Save metadata for this batch
    ee.save_topic_metadata("arc_10_18", {qid: d["meta_ar"] for qid, d in DATA.items()})

    # Merge into main metadata
    ee.merge_all_metadata()

    # Validate each question
    all_ok = True
    for qid in DATA:
        errs = ee.validate_question(qid)
        if errs:
            print(f"❌ {qid} validation errors:")
            for e in errs:
                print(f"   - {e}")
            all_ok = False
        else:
            print(f"✅ {qid} passed validation with 0 errors!")

    if all_ok:
        print("\nAll 9 ARC questions (ARC-10 to ARC-18) successfully elevated and passed validation!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
