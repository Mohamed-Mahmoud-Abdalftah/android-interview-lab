#!/usr/bin/env python3
"""Elevate ARC-19 through ARC-26 for bilingual parity and senior spoken answers."""
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
# ARC-19: Cache and Server Updates in Data Layer
# ==========================================
DATA["ARC-19"] = {
    "concept_en": """Handling cache and server updates within the Data Layer requires establishing the local persistent database (such as Room) as the authoritative Single Source of Truth. In an offline-first architecture, read queries expose continuous Flow streams directly from local storage, allowing the UI to render cached data instantaneously without blocking on remote endpoints. When background synchronizations or explicit user refreshes fetch updated payloads from Retrofit, the repository writes the raw data into the local database inside an atomic transaction. Room's InvalidationTracker automatically detects the table mutations and pushes fresh data downstream to active UI collectors. For interactive user actions, repositories perform optimistic updates by mutating local storage immediately, rolling back changes with compensating transactions if subsequent network calls fail.""",
    "walkthrough_en": """Implementing offline-first cache and server synchronization in a repository:
```kotlin
class ProductRepositoryImpl(
    private val localDao: ProductDao,
    private val remoteApi: ProductApi,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) : ProductRepository {
    // 1. Single Source of Truth: UI always observes local Room database
    override fun observeProducts(): Flow<List<Product>> =
        localDao.observeAllProducts().map { entities -> entities.map { it.toDomain() } }

    // 2. Network sync writes directly into Room inside an atomic transaction
    override suspend fun syncProducts(): Result<Unit> = withContext(ioDispatcher) {
        runCatching {
            val networkDtos = remoteApi.fetchProducts()
            localDao.replaceProductsTransaction(networkDtos.map { it.toEntity() })
        }
    }

    // 3. Optimistic update: mutate local cache immediately, rollback on failure
    override suspend fun toggleFavorite(productId: String, isFav: Boolean): Result<Unit> = withContext(ioDispatcher) {
        localDao.updateFavoriteStatus(productId, isFav) // Immediate UI update via Room Flow
        runCatching {
            remoteApi.postFavoriteStatus(productId, isFav)
        }.onFailure {
            localDao.updateFavoriteStatus(productId, !isFav) // Compensating rollback on network error
        }
    }
}
```""",
    "short_en": """Manage cache and server updates using an offline-first data layer where the local database serves as the single source of truth. The repository exposes a continuous Flow from Room, immediately delivering cached entities to the UI. Concurrently, it triggers background network synchronization, writing fresh remote payloads directly into the database within an atomic transaction. For user mutations, apply optimistic updates locally with compensating rollback mechanisms if network requests fail.""",
    "structured_en": """Handling cache and server synchronization is the primary responsibility of the data layer, isolating UI consumers from transport protocols and storage mechanics.
In an offline-first architecture, the local database acts as the authoritative source of truth. Repositories expose reactive Flow streams directly from persistent storage, guaranteeing instant UI loading with cached data upon screen launch.
Concurrently, the repository dispatches an asynchronous network fetch. When fresh payloads arrive from Retrofit, they are committed to the local database inside an atomic transaction. Room's internal invalidation tracker automatically detects table modifications and pushes fresh snapshots downstream to active collectors without requiring manual UI refresh coordination.
For interactive mutations, we utilize optimistic updates. The repository applies changes immediately to the local database so the interface reacts with zero perceived latency. If the backend network call fails, the repository triggers a compensating rollback and emits an error event. Furthermore, leveraging HTTP ETags and conditional headers avoids re-downloading unchanged server state.""",
    "deep_senior_en": """Under the hood, orchestrating cache and remote synchronizations safely requires formalizing concurrency and conflict resolution. A common architectural defect is having repositories return combined network and database models directly into presentation coroutines, which invites race conditions when multiple screens request refreshes simultaneously.
By enforcing that all write operations route exclusively into persistent storage, the repository serializes mutations. Room handles atomic writes via transactions, guaranteeing that partial ingestion never leaves the local database in a corrupted state.
When dealing with concurrent modifications across distributed clients, repositories must implement explicit conflict resolution policies. In standard mobile workflows, server-authoritative reconciliation takes precedence, where incoming server records overwrite local drafts. However, in collaborative or offline-heavy enterprise applications, field-level merge strategies or last-write-wins based on monotonic server sequence numbers prevent local edits from obliterating remote changes.
At the HTTP layer, configuring an OkHttp Cache alongside ETag and If-None-Match headers allows the backend to respond with HTTP 304 Not Modified. This conserves mobile bandwidth, reduces radio wakeup cycles, and confirms cache validity with zero payload parsing overhead.
Staff engineers also safeguard against racing sync responses by attaching client-side sequence counters or timestamps to outbound requests. If an older network response arrives after a newer one has already been committed, the data layer identifies the stale generation and silently discards the payload, guaranteeing monotonic state progression.""",
    "meta_ar": {
        "id": "ARC-19",
        "questionAr": "كيف تدير تحديثات الكاش (Cache) والسيرفر (Server) داخل طبقة البيانات؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصميم معمارية مزامنة البيانات بين الكاش والسيرفر، وتطبيق مبدأ المصدر الأوحد، والتعامل مع التحديثات التفاؤلية وحل تعارض البيانات وتأكيد المعاملات الذرية.",
        "why_it_matters_ar": "غياب التزامن المنظم بين قاعدة البيانات والشبكة يسبب سباق بيانات (Race Conditions) وتضارب الأرصدة أو اختفاء البيانات وظهور شاشات بيضاء عند انقطاع الاتصال.",
        "worked_example_ar": "تطبيق نمط Offline-First داخل الـ Repository:\n```kotlin\nclass FeedRepositoryImpl(val dao: FeedDao, val api: FeedApi) : FeedRepository {\n    override fun getFeed(): Flow<List<FeedItem>> = dao.observeFeed().map { it.map { e -> e.toDomain() } }\n    override suspend fun syncFeed() = withContext(Dispatchers.IO) {\n        val remote = api.fetchFeed()\n        dao.withTransaction { dao.clearAndInsert(remote.map { it.toEntity() }) }\n    }\n}\n```",
        "trade_offs_ar": "الاعتماد على الكاش أولاً يضمن سرعة الواجهة والعمل دون إنترنت، لكنه يضيف تعقيد إدارة الترحيلات وحل التعارضات وتنظيف البيانات القديمة.",
        "failure_modes_ar": "مسح الكاش قبل التأكد من نجاح اتصال السيرفر مما يترك المستخدم بشاشة خالية تماماً عند انقطاع الشبكة، أو قبول استجابة قديمة متأخرة تمسح تحديثاً أحدث.",
        "production_perspective_ar": "في تطبيقات التجارة والنقل، نعتمد على استراتيجية Optimistic Updates للعمليات التفاعلية مع تخزين معرف العملية، وتأكيد تحديثات السيرفر عبر ETag لتقليل استهلاك البطارية والبيانات.",
        "how_to_answer_ar": "ابدأ بتوضيح مبدأ المصدر الأوحد للحقيقة باعتماد قاعدة البيانات كمرجع أساسي، ثم اشرح آلية المزامنة في الخلفية والتحديثات التفاؤلية وإدارة التعارضات.",
        "talking_points_ar": "استراتيجية Network-Bound Resource، واستخدام ETag مع HTTP 304، والتحديثات التفاؤلية مع Rollback، والمعاملات الذرية في Room عبر `@Transaction`.",
        "follow_ups_ar": "- **المحاور:** \"ما هو الـ Optimistic Update وكيف نتعامل مع فشل الشبكة؟\"\n  **المرشح:** \"التحديث التفاؤلي يقوم بتعديل قاعدة البيانات والواجهة فوراً لإعطاء تجربة سلسة للمستخدم، مع إطلاق الطلب للسيرفر في الخلفية؛ وفي حال فشل الطلب، يتم تنفيذ عملية تراجع (Rollback) وإخطار المستخدم.\"\n\n- **المحاور:** \"كيف تمنع استجابة شبكة بطيئة من مسح بيانات أحدث؟\"\n  **المرشح:** \"عن طريق ربط كل طلب برقم تسلسلي أو Timestamp، ومقارنة التوقيت في طبقة البيانات لرفض أي رد قديم يصل بعد معالجة رد أحدث.\"",
        "self_check_ar": "هل حددت قاعدة البيانات كمصدر أوحد؟ هل شرحت التحديثات التفاؤلية؟ وهل وضحت استراتيجيات حل التعارضات وحماية المعاملات؟",
        "references_ar": f"- [Android offline-first architecture](https://developer.android.com/topic/architecture/data-layer/offline-first) — الدليل الرسمي لبناء تطبيقات تعمل دون اتصال بالإنترنت.\n- [Data Layer guide](https://developer.android.com/topic/architecture/data-layer) — توثيق جوجل لتنسيق البيانات والكاش في المستودعات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بندير تحديثات الكاش والسيرفر بالاعتماد على قاعدة البيانات المحلية كمصدر أوحد للحقيقة. الـ Repository بيعرض Flow مستمر من الـ Database للواجهة علشان تفتح فورياً، وفي نفس الوقت بيطلب البيانات الجديدة من السيرفر في الخلفية ويكتبها داخل الـ Database في Transaction ذرية. وفي العمليات التفاعلية بنطبق Optimistic Updates بتحديث الكاش فوراً مع إمكانية التراجع لو فشل طلب الشبكة.",
        "best_answer_ar": "إدارة التزامن بين الكاش والسيرفر هي المسؤولية الجوهرية لطبقة البيانات لعزل تفاصيل التخزين والشبكة عن واجهة المستخدم.\n\nفي معمارية الـ Offline-First، قاعدة البيانات المحلية مثل Room هي المصدر الأوحد للحقيقة. الـ Repository بيوفر Flow مستمر بيقرأ من الـ Database مباشرة، فالمستخدم يشوف المحتوى المخزن فور فتح التطبيق بدون أي انتظار لشاشات التحميل.\n\nبالتوازي مع العرض الفوري، الـ Repository بيشغل طلب شبكة في الخلفية لجلب أحدث البيانات. ولما الاستجابة ترجع بنجاح، بنسجل البيانات الجديدة داخل قاعدة البيانات في Transaction ذرية، ونظام تتبع التغييرات في Room بيحدث الـ Flow تلقائياً لكل الشاشات المستمعة بدون أي تدخل يدوي.\n\nوفي العمليات التفاعلية زي تسجيل الإعجاب أو حذف عنصر، بنستخدم التحديث التفاؤلي بتعديل الكاش المحلي في التو واللحظة لتوفير تجربة فائقة السرعة، ولو نداء السيرفر فشل بنرجع التعديل لحالته الأصلية. بالإضافة لده، بنستفيد من ترويسات ETag و If-None-Match لتقليل استهلاك الباقة والبطارية إذا لم تتغير البيانات على السيرفر.",
        "deep_answer_ar": "تحت الكابوت، إدارة التزامن بين الكاش والسيرفر بأمان بتتطلب حوكمة دقيقة للتزامن وحل تعارض البيانات. من الأخطاء المعمارية الشائعة إن الـ Repository يرجع بيانات مجمعة من الشبكة والكاش مباشرة للـ ViewModel، وده بيخلق Race Conditions خطيرة لو كذا شاشة طلبت التحديث في نفس الوقت.\n\nالتصميم الهندسي المتين بيلزم إن كل عمليات الكتابة تعدي حصرياً على الـ Database أولاً. الـ Room بيتولى المعاملات عبر Transactions تضمن عدم تسجيل بيانات ناقصة أو مشوهة لو حصل Crash في نص عملية الحفظ.\n\nوعند التعامل مع تعديلات متزامنة من أجهزة مختلفة، لازم طبقة البيانات تتبنى سياسات واضحة لفض التعارض. في معظم التطبيقات العادية بنعتمد سياسة خضوع العميل لبيانات السيرفر بحيث تستبدل التعديلات القادمة من السيرفر أي مسودات قديمة، بينما في التطبيقات التشاركية المعقدة بنطبق دمج على مستوى الحقول أو مقارنة أرقام النسخ لمنع مسح تعديلات حديثة.\n\nوعلى مستوى الـ HTTP، بنفعل الـ Caching في OkHttp مع الـ ETags، بحيث السيرفر يرجع كود 304 Not Modified لو البيانات متطابقة، فنوفر استهلاك المعالج وتفريغ شحن البطارية ونتأكد من صلاحية الكاش المحلي بدون أي مجهود إضافي.\n\nالمهندسون الكبار بيحطوا كمان Sequence Counters أو Timestamps على الطلبات الصادرة، علشان لو رد شبكة قديم وصل متأخر بعد رد أحدث منه، يتم رفضه وتجاهله فوراً لضمان عدم ارتداد حالة البيانات للخلف وحماية اتساق المعاملات عبر الجلسات المتتالية."
    }
}

# ==========================================
# ARC-20: Independent Testing of Presentation, Domain, and Data
# ==========================================
DATA["ARC-20"] = {
    "concept_en": """Testing Presentation, Domain, and Data layers independently requires establishing clear boundary seams and substituting adjacent dependencies with test doubles. The Domain layer comprises pure Kotlin business logic with zero Android dependencies; it is verified through blazingly fast JVM unit tests using lightweight in-memory Fake repositories. The Data layer is tested using Fake remote data sources or MockWebServer to assert network error handling, caching policies, and DTO-to-entity mapping, while Room DAOs are tested against in-memory SQLite instances to validate queries, migrations, and relational integrity. The Presentation layer is tested by driving ViewModels with runTest and TestDispatchers, utilizing Turbine to assert deterministic UiState emissions, and evaluating Compose screens with createComposeRule to verify rendering and semantics without booting device activities.""",
    "walkthrough_en": """Testing Domain, Data, and Presentation layers in complete isolation:
```kotlin
// 1. DOMAIN: Pure Kotlin unit test with in-memory Fake repository
class CalculateCartDiscountUseCaseTest {
    @Test
    fun appliesTenPercentDiscount_whenCartExceedsThreshold() {
        val fakeRepo = FakeCartRepository(initialTotal = 150.0)
        val useCase = CalculateCartDiscountUseCase(fakeRepo)
        val discountedTotal = useCase()
        assertEquals(135.0, discountedTotal, 0.01)
    }
}

// 2. DATA: Room DAO test using in-memory SQLite database
@RunWith(AndroidJUnit4::class)
class ProductDaoTest {
    private lateinit var db: AppDatabase
    private lateinit var dao: ProductDao

    @Before
    fun createDb() {
        db = Room.inMemoryDatabaseBuilder(ApplicationProvider.getApplicationContext(), AppDatabase::class.java).build()
        dao = db.productDao()
    }

    @After
    fun closeDb() = db.close()

    @Test
    fun insertAndObserveProducts() = runTest {
        dao.insert(ProductEntity("1", "Laptop", 1200))
        val products = dao.observeProducts().first()
        assertEquals(1, products.size)
    }
}

// 3. PRESENTATION: ViewModel test asserting state emissions via Turbine
class CheckoutViewModelTest {
    @Test
    fun submitPayment_transitionsFromLoadingToSuccess() = runTest {
        val fakeCheckoutRepo = FakeCheckoutRepository()
        val viewModel = CheckoutViewModel(fakeCheckoutRepo, StandardTestDispatcher(testScheduler))

        viewModel.uiState.test {
            assertEquals(CheckoutUiState.Idle, awaitItem())
            viewModel.onPayClicked()
            assertEquals(CheckoutUiState.Processing, awaitItem())
            assertEquals(CheckoutUiState.Success("txn_99"), awaitItem())
        }
    }
}
```""",
    "short_en": """Test Domain independently using pure JVM unit tests with Fake repositories to verify business rules. Test Data by validating repository caching and mapping against Fake data sources, and verifying Room DAOs using in-memory SQLite databases. Test Presentation using Turbine and TestDispatchers for ViewModels to assert deterministic UiState transitions, and createComposeRule for testing composables in isolation.""",
    "structured_en": """Layered architecture allows each tier of an Android application to be tested in isolation using the fastest and most appropriate verification tools.
For the Domain layer, testing focuses entirely on pure business logic. Because use cases contain no Android SDK references, they execute as JVM unit tests in milliseconds. We inject lightweight in-memory Fake repositories through constructors, verifying calculations, business validations, and error pathways without relying on mock frameworks.
Within the Data layer, we separate repository testing from database verification. Repositories are tested on the JVM using Fake network data sources to ensure caching policies, entity mapping, and synchronization algorithms operate correctly. In contrast, Room DAOs are tested against in-memory SQLite databases to validate raw SQL queries, foreign key constraints, and database migrations under realistic relational behavior.
In the Presentation layer, ViewModel unit tests run on the JVM using runTest and StandardTestDispatcher. By pairing test dispatchers with Turbine, we observe StateFlow streams and assert the exact chronological sequence of UiState emissions. Finally, Compose UI elements are validated using createComposeRule, testing user interactions and visual semantics in isolation.""",
    "deep_senior_en": """Under the hood, a resilient testing strategy across architectural boundaries hinges on favoring Fakes over Mocks. Mocking frameworks like Mockito or MockK encourage interaction testing, asserting that specific methods were invoked a certain number of times. This couples tests to private implementation details; refactoring internal method calls breaks the test suite even when user-visible behavior remains completely intact.
By creating lightweight Fake implementations of repositories and data sources backed by simple HashMaps or MutableStateFlows, tests verify observable state outcomes rather than mechanics. When a ViewModel triggers an action, the test asserts that the resulting UiState contains the expected models.
In the Presentation layer, testing asynchronous coroutines requires deterministic scheduling. Using runTest with a StandardTestDispatcher freezes virtual time. Suspending functions like delay do not stall test execution; developers advance the test scheduler explicitly using advanceUntilIdle to verify intermediate loading states and final emissions without introducing flaky Thread.sleep calls.
For Data layer verification, testing Room DAOs requires executing real SQLite operations because SQLite syntax and constraint violations cannot be simulated through JVM mocks. Using Room.inMemoryDatabaseBuilder allows these tests to run either via Robolectric on the local JVM or as fast instrumented tests, ensuring database schemas match entity definitions.
Staff engineers establish a pyramid where Domain and Presentation JVM tests constitute eighty percent of the suite, completing thousands of checks in seconds on CI, while integration tests validate database and network serialization boundaries.""",
    "meta_ar": {
        "id": "ARC-20",
        "questionAr": "كيف تختبر طبقات الععرض والنطاق والبيانات بشكل مستقل ومعزول؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصميم استراتيجية اختبار معزولة لكل طبقة معمارية، واستخدام Fakes بدلاً من Mocks، واختبار الكوروتينات والـ StateFlow عبر Turbine، وفحص قواعد البيانات عبر In-Memory Room.",
        "why_it_matters_ar": "خلط الطبقات أثناء الاختبار يجعل الـ Unit Tests بطيئة وتتطلب محاكي أندرويد، أو يجعلها هشة وتفشل مع أي إعادة هيكلة داخلية للكود.",
        "worked_example_ar": "اختبار الـ UseCase ككود نقي واختبار الـ ViewModel بـ Turbine:\n```kotlin\n// Domain Test: كوتلن نقي 100%\nclass DiscountTest { @Test fun test() = assertEquals(90, CalcDiscount()(100)) }\n// Presentation Test: اختبار StateFlow عبر Turbine\nclass CartVmTest { @Test fun vmTest() = runTest {\n    val vm = CartViewModel(FakeRepo())\n    vm.state.test { assertEquals(State.Idle, awaitItem()) }\n}}\n```",
        "trade_offs_ar": "استخدام Fakes يتطلب كتابة كلاسات مساعدة إضافية في مجلد الاختبار، لكنه يوفر اختبارات سريعة جداً ومرنة لا تنكسر مع تغيير تفاصيل التنفيذ الداخلية.",
        "failure_modes_ar": "استخدام MockK لعمل verify على استدعاء دوال الـ DAO بدلاً من فحص الحالة الناتجة، مما يؤدي لنجاح الاختبار حتى لو كانت الاستعلامات تعيد نتائج خاطئة في الواقع.",
        "production_perspective_ar": "في الشركات الكبرى، تشكل اختبارات الـ JVM للـ Domain والـ ViewModel نحو 80% من الـ Test Suite وتعمل في أقل من 20 ثانية في الـ CI، مع تشغيل اختبارات Room المدمجة بشكل منفصل.",
        "how_to_answer_ar": "وضح أسلوب اختبار كل طبقة: الـ Domain باختبارات JVM نقية مع Fakes، والـ Data باختبار Room محلياً مع MockWebServer، والـ Presentation باستخدام Turbine و TestDispatcher.",
        "talking_points_ar": "تفضيل Fakes على Mocks، ومكتبة Turbine لفحص تدفقات Flow، والـ In-Memory Database في Room، واستخدام runTest مع StandardTestDispatcher.",
        "follow_ups_ar": "- **المحاور:** \"ليه بنفضل الـ Fakes على الـ Mocks في اختبارات المعمارية النظيفة؟\"\n  **المرشح:** \"لأن الـ Mocks بتركز على تفاصيل التنفيذ واستدعاء الدوال (Interaction Testing) وده بيخلي الاختبارات هشة وبتتكسر مع أي ريفاكتور، بينما الـ Fakes بتركز على فحص الحالة الناتجة وتغيير البيانات الحقيقية.\"\n\n- **المحاور:** \"إزاي بنختبر الـ Room DAOs بدون ما نعتمد على Mocking؟\"\n  **المرشح:** \"باستخدام `Room.inMemoryDatabaseBuilder` لتشغيل قاعدة بيانات SQLite حقيقية في الذاكرة تفحص صحة استعلامات SQL والـ Constraints وتتلاشى فور انتهاء الاختبار.\"",
        "self_check_ar": "هل وضحت كيفية اختبار Domain ككود نقي؟ هل بينت استخدام Turbine مع ViewModel؟ وهل شرحت اختبار Room في الذاكرة؟",
        "references_ar": f"- [Testing in Android](https://developer.android.com/training/testing) — الدليل الرسمي لاستراتيجيات الاختبار في أندرويد.\n- [Testing Coroutines](https://developer.android.com/kotlin/coroutines/test) — توثيق استخدام runTest و TestDispatcher في اختبارات الكوروتينات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنختبر طبقة الـ Domain باختبارات JVM نقية وسريعة جداً باستخدام Fake Repositories لفحص منطق الأعمال. وبنختبر طبقة الـ Data بفحص الـ Repositories ضد Fake DataSources، واختبار الـ DAOs باستخدام In-Memory SQLite في Room. وطبقة الـ Presentation بنختبر الـ ViewModels باستخدام Turbine و TestDispatcher للتأكد من تسلسل الـ UiState، والواجهات بـ createComposeRule.",
        "best_answer_ar": "المعمارية النظيفة بتسمح باختبار كل طبقة بشكل مستقل تماماً باستخدام الأدوات الأنسب والأسرع لكل سياق.\n\nفي طبقة الـ Domain، الاختبارات بتركز بالكامل على قواعد ومنطق الأعمال الصافي. ونظراً لأن الـ Use Cases خالية تماماً من أي تبعيات لأندرويد، فهي بتشتغل كـ JVM Unit Tests في أجزاء من الميلي ثانية. بنحقن Fake Repositories خفيفة في الـ Constructor، ونفحص الحسابات والتحققات ومسارات الأخطاء بدون أي حاجة لمكتبات Mocking معقدة.\n\nفي طبقة الـ Data، بنفصل اختبار المستودعات عن فحص قواعد البيانات. الـ Repositories بنختبرها على الـ JVM باستخدام Fake DataSources للتأكد من سياسات الكاش والتحويل بين DTO و Domain. بينما الـ Room DAOs بنختبرها ضد قاعدة بيانات SQLite في الذاكرة عبر In-Memory Database Builder للتحقق من صحة استعلامات الـ SQL والـ Foreign Keys.\n\nأما في طبقة الـ Presentation، بنختبر الـ ViewModels على الـ JVM باستخدام runTest و StandardTestDispatcher. ومع مكتبة Turbine، بنراقب انبعاثات الـ StateFlow ونتأكد من دقة تسلسل الـ UiState خطوة بخطوة، وبنختبر مكونات الـ Compose المستقلة عبر createComposeRule.",
        "deep_answer_ar": "تحت الكابوت، الاستراتيجية الناجحة لاختبار الطبقات المعمارية بتعتمد على تفضيل الـ Fakes على الـ Mocks. مكتبات الـ Mocking زي Mockito أو MockK بتشجع على Interaction Testing، يعني التحقق من إن دالة معينة تم استدعاؤها بعدد مرات محدد، وده بيربط الاختبار بتفاصيل التنفيذ الداخلية ويخلي التيست هش ويتكسر مع أي ريفاكتور حتى لو كان سلوك التطبيق سليم 100%.\n\nلما بنبني Fake Repositories بتعتمد على HashMaps أو MutableStateFlow داخلي، بنختبر الحالة الظاهرة للمستخدم والنتيجة النهائية بدل ما نختبر ميكانيكية الكود. ولما الـ ViewModel يعمل إجراء، الاختبار بيتحقق من إن الـ UiState اتغيرت للقيم المتوقعة.\n\nفي طبقة العرض، اختبار الكوروتينات بيتطلب تحكماً صارماً في التزامن والوقت. استخدام runTest مع StandardTestDispatcher بيجمد الوقت التخيلي، فدوال زي delay مش بتعطل الاختبارات، وبنقدر نقدم مؤشر الوقت يدوياً عبر advanceUntilIdle لفحص حالات التحميل والانبعاثات المتتالية بدون كتابة Thread.sleep إطلاقاً.\n\nوفي طبقة البيانات، اختبار الـ Room DAOs لازم يشغل كود SQLite حقيقي، لأن استعلامات SQL وأخطاء الـ Constraints مستحيل محاكاتها بدقة عبر الموك. استخدام Room.inMemoryDatabaseBuilder بيسمح بتشغيل الاختبارات عبر Robolectric على الـ JVM أو على أجهزة حقيقية.\n\nالمهندسون الكبار بيصمموا هرم الاختبارات بحيث تشكل اختبارات الـ JVM للـ Domain والـ ViewModel أكثر من 80% من إجمالي الاختبارات وتنفذ في ثوان معدودة على الـ CI مع عزل تام وتغطية شاملة."
    }
}

# ==========================================
# ARC-21: Incremental Refactoring of a 1,000-Line ViewModel
# ==========================================
DATA["ARC-21"] = {
    "concept_en": """Incrementally refactoring a 1,000-line monolithic ViewModel requires adopting the Strangler Fig pattern to surgically extract concerns into decoupled components without halting feature delivery or causing regressions. A monolithic ViewModel typically conflates network requests, persistent caching, DTO transformations, validation rules, and disparate UI state holders. Rather than undertaking a high-risk Big Bang rewrite in an isolated feature branch, senior engineers establish a baseline safety net by writing characterization unit tests against the existing ViewModel. Refactoring then proceeds through discrete, verifiable steps: extracting data transport and storage operations into concrete Repositories, isolating complex business calculations into dedicated Use Cases, consolidating fragmented state primitives into a single immutable UiState, and reducing the ViewModel to a lightweight state orchestrator.""",
    "walkthrough_en": """Incrementally decomposing a 1,000-line monolithic ViewModel:
```kotlin
// Step 1: Characterization test captures existing black-box behavior before touching code
class MonolithicCartViewModelTest {
    @Test
    fun existingCheckoutFlow_emitsExpectedStatus() = runTest {
        val vm = MonolithicCartViewModel(fakeApi, fakeDb)
        vm.checkout("user_123")
        assertEquals(true, vm.isCheckoutSuccess.value)
    }
}

// Step 2: Extract data persistence and network calls into a clean Repository
class CartRepositoryImpl(
    private val cartApi: CartApi,
    private val cartDao: CartDao
) : CartRepository {
    override suspend fun checkoutCart(userId: String): Result<OrderReceipt> = runCatching {
        val remoteOrder = cartApi.submitOrder(userId)
        cartDao.clearCart()
        remoteOrder.toDomain()
    }
}

// Step 3: Extract business rules into a dedicated UseCase
class ValidateCheckoutEligibilityUseCase(private val userRepo: UserRepository) {
    operator fun invoke(cartTotal: Double): CheckoutValidationResult {
        if (cartTotal <= 0.0) return CheckoutValidationResult.EmptyCart
        return CheckoutValidationResult.Eligible
    }
}

// Step 4: Final Refactored ViewModel becomes a thin (<80 line) coordinator
@HiltViewModel
class CleanCartViewModel @Inject constructor(
    private val cartRepository: CartRepository,
    private val validateEligibility: ValidateCheckoutEligibilityUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow<CartUiState>(CartUiState.Idle)
    val uiState: StateFlow<CartUiState> = _uiState.asStateFlow()

    fun onCheckoutClicked(total: Double) {
        when (validateEligibility(total)) {
            is CheckoutValidationResult.EmptyCart -> _uiState.value = CartUiState.Error("Cart is empty")
            is CheckoutValidationResult.Eligible -> processCheckout()
        }
    }

    private fun processCheckout() = viewModelScope.launch {
        _uiState.value = CartUiState.Loading
        cartRepository.checkoutCart("user_id")
            .onSuccess { receipt -> _uiState.value = CartUiState.Success(receipt.orderId) }
            .onFailure { error -> _uiState.value = CartUiState.Error(error.message ?: "Failed") }
    }
}
```""",
    "short_en": """Refactor a 1,000-line ViewModel incrementally using the Strangler Fig pattern: write baseline characterization tests to capture existing behavior, extract network and database calls into a Repository, extract heavy business rules into dedicated Use Cases, consolidate scattered state variables into a single immutable UiState, and verify zero behavior regression with small, atomic pull requests.""",
    "structured_en": """Refactoring a monolithic 1,000-line ViewModel requires a disciplined, step-by-step migration to prevent regression while keeping active development unblocked.
The process begins with establishing characterization tests. Before changing a single line of production code, we write black-box unit tests asserting the ViewModel's existing inputs, outputs, and side-effects. This creates an automated safety net ensuring subsequent extractions preserve system behavior.
Next, we extract data access into a dedicated Repository. Direct Retrofit API calls, Room database transactions, and SharedPreferences operations are migrated into a concrete repository implementation behind an interface. Injecting this repository into the ViewModel immediately eliminates hundreds of lines of HTTP configuration and DTO mappings.
Following data isolation, we extract domain business logic into single-responsibility Use Cases. Validation routines, complex mathematical calculations, and multi-source workflows are isolated into pure Kotlin classes with focused unit tests.
Finally, we consolidate fragmented UI state. Scattered LiveData or StateFlow flags—such as loading booleans, error strings, and data models—are merged into a single immutable UiState data class, transforming the ViewModel into a thin coordinator of under eighty lines.""",
    "deep_senior_en": """Under the hood, attempting a Big Bang rewrite of a massive legacy ViewModel represents one of the highest risks in software engineering. Over months of parallel feature development, isolated rewrite branches suffer severe merge conflicts, miss subtle production bugfixes, and halt regular release cycles.
Employing the Strangler Fig pattern avoids this trap by migrating old functionality slice by slice within the main production branch. At every commit, the application compiles, existing tests pass, and new features continue shipping to production.
During the extraction of data access, engineers must maintain strict boundary isolation. When moving Retrofit calls out of the ViewModel, raw network DTOs must not leak back into presentation code; the newly introduced Repository must map responses into clean Domain models before returning them.
When consolidating UI state, legacy ViewModels often suffer from race conditions where separate StateFlow variables update asynchronously, causing UI composables to render invalid intermediate combinations such as displaying a progress bar while showing an error banner. Merging these primitives into a single sealed hierarchy or cohesive data class guarantees atomic state transitions.
Staff engineers coordinate this refactor across four to five small Pull Requests, accompanied by code coverage metrics and production crash monitoring. By the conclusion of the refactor, the ViewModel is reduced from a messy thousand-line god object to a declarative coordinator focusing solely on UI state binding and event forwarding.""",
    "meta_ar": {
        "id": "ARC-21",
        "questionAr": "كيف تعيد هيكلة ViewModel ضخم يحتوي على 1,000 سطر بشكل تدريجي وآمن؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إتقان استراتيجيات إعادة الهيكلة التدريجية، واستخدام نمط Strangler Fig، وتطبيق Characterization Testing، وتفكيك الكود إلى Repositories و UseCases وتوحيد الـ UI State.",
        "why_it_matters_ar": "إعادة كتابة الكود من الصفر (Big Bang Rewrite) تؤدي لفقدان معالجة الحالات الخاصة وظهور أخطاء غير متوقعة وتوقف تسليم ميزات العمل لفترات طويلة.",
        "worked_example_ar": "خطوات استخراج المسؤوليات تدريجياً:\n```kotlin\n// 1. اختبار السلوك الحالي بـ Characterization Test\n// 2. سحب الشبكة والتخزين إلى CartRepository\n// 3. سحب شروط الدفع إلى ValidateCartUseCase\n// 4. توحيد الـ State داخل StateFlow<CartUiState>\n```",
        "trade_offs_ar": "التحويل التدريجي قد يتطلب وجود بعض الكود الانتقالي المؤقت عبر عدة PRs، لكنه يضمن عدم تعطل التطبيق أو توقف الميزات الجديدة.",
        "failure_modes_ar": "محاولة إعادة كتابة الـ ViewModel بالكامل في فرع منفصل لعدة أسابيع، مما يؤدي لصراعات دمج مستحيلة في Git وظهور ثغرات أمنية وتشغيلية في الإنتاج.",
        "production_perspective_ar": "في المشروعات الكبرى، نقسم إعادة هيكلة الملف الضخم إلى 4 أو 5 طلبات دمج (PRs) صغيرة؛ يبدأ كل PR باختبارات توصيفية، وتتم مراقبة مقاييس الانهيار عبر Crashlytics بعد كل إصدار.",
        "how_to_answer_ar": "اشرح استراتيجية Strangler Fig التدريجية: كتابة Characterization Tests أولاً، ثم استخراج طبقة البيانات للـ Repository، ثم استخراج العمليات المعقدة لـ UseCases، وأخيراً توحيد الـ State.",
        "talking_points_ar": "نمط Strangler Fig، واختبارات التوصيف (Characterization Testing)، وفصل DTOs عن الـ ViewModel، وتوحيد الحالة في كائن UiState واحد.",
        "follow_ups_ar": "- **المحاور:** \"ما هو الـ Characterization Test ولماذا نبدأ به؟\"\n  **المرشح:** \"هو اختبار بنكتبه لتوصيف وحفظ السلوك الحالي للكود القديم كما هو بمدخلاته ومخرجاته حتى لو كان فيه عيوب، لإنشاء شبكة أمان تضمن إن أي ريفاكتور قادم مش هيغير سلوك التطبيق.\"\n\n- **المحاور:** \"كيف تتعامل مع وجود 15 متغير LiveData مختلفين داخل الـ ViewModel القديم؟\"\n  **المرشح:** \"بدمجهم تدريجياً في كائن واحد مختوم أو data class يمثل `UiState`، وده بيمنع تناقض الحالات وتزامنها العشوائي في واجهة المستخدم.\"",
        "self_check_ar": "هل حذرت من الـ Big Bang Rewrite؟ هل شرحت خطوات نمط Strangler Fig؟ وهل وضحت استخراج الـ Repository والـ UseCase وتوحيد الحالة؟",
        "references_ar": f"- [Working Effectively with Legacy Code](https://www.oreilly.com/library/view/working-effectively-with/0131177052/) — المرجع الكلاسيكي لميشيل فيذرز حول اختبار وإعادة هيكلة الكود الضخم.\n- [Android UI Architecture Guide](https://developer.android.com/topic/architecture/ui-layer) — توثيق جوجل الرسمي لتصميم ViewModels خفيفة ومنظمة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنعيد هيكلة الـ ViewModel الضخم تدريجياً باستخدام نمط Strangler Fig عبر عدة خطوات آمنة: بنبدأ بكتابة Characterization Tests لتأمين السلوك الحالي، بعدين بنسحب كود الشبكة والـ SharedPreferences لـ Repository، ونستخرج العمليات الحسابية المعقدة لـ Use Cases، ونوحد المتغيرات المبعثرة في StateFlow بكائن UiState واحد، لحد ما يتحول الـ ViewModel لمنسق خفيف في أقل من 80 سطراً.",
        "best_answer_ar": "إعادة هيكلة ViewModel ضخم بيحتوي على ألف سطر بتتطلب استراتيجية جراحية تدريجية بدون إيقاف تطوير الميزات الجديدة أو التسبب في أخطاء برمجية.\n\nبنبدأ أولاً بكتابة Characterization Tests لتأمين الكود القائم. الاختبارات دي بتلتقط المدخلات والمخرجات الحالية للـ ViewModel كصندوق أسود، فتوفر شبكة أمان آلية تضمن إن الخطوات التالية مش هتغير سلوك النظام.\n\nبعد كده بنستخرج كود الوصول للبيانات في Repository مخصص. بنسحب استدعاءات Retrofit و Room وقراءة الإعدادات المحلية ونضعها خلف Interface للـ Repository ونحقنه داخل الـ ViewModel، وده بيحذف مئات السطور من كود الشبكة والـ DTOs فوراً.\n\nالخطوة التالية هي عزل منطق العمليات والبيزنس المعقد داخل Use Cases مستقلة ومحددة المسؤولية، وتغطيتها باختبارات JVM سريعة.\n\nوأخيراً، بنوحد الحالة المتناثرة؛ فبدل وجود متغيرات LiveData أو StateFlow منفصلة لكل حقل، بنجمعهم في كائن واحد غير قابل للتعديل يمثل UiState، فيتحول الـ ViewModel لكلاس نحيف وأنيق لا يتجاوز ثمانين سطراً.",
        "deep_answer_ar": "تحت الكابوت، محاولة إعادة كتابة كلاس ضخم بالكامل من الصفر فيما يعرف بـ Big Bang Rewrite في فرع منفصل بتعتبر من أكبر المخاطر في مشاريع السوفت وير الكبيرة. على مدار أسابيع العمل، الفرع المنفصل بيواجه صراعات دمج مستحيلة في Git، وبيفقد إصلاحات أخطاء حيوية نزلت في الإنتاج، وبيعطل تسليم ميزات البيزنس.\n\nتطبيق نمط Strangler Fig بيتفادى الفخ ده تماماً عن طريق استخراج المسؤوليات شريحة شريحة داخل الفرع الرئيسي. ومع كل خطوة و PR، التطبيق بيبني بنجاح، الاختبارات بتعدي، والميزات الجديدة بتفضل شغالة.\n\nأثناء استخراج طبقة البيانات، لازم نحافظ على عزل الحدود؛ فممنوع نهائياً تسريب كائنات الـ DTO الخاصة بالشبكة للـ ViewModel، بل الـ Repository الجديد هو اللي بيحولها لـ Domain Models قبل إرجاعها.\n\nوعند توحيد الـ UI State، الـ ViewModels القديمة غالباً بتعاني من Race Conditions لأن المتغيرات المنفصلة بتتحدث في أوقات مختلفة، وده بيخلي الواجهة تعرض حالات متناقضة زي ظهور مؤشر التحميل مع رسالة خطأ في نفس اللحظة. تجميع الحالات في كائن واحد مختوم بيضمن انتقالات ذرية ومتسقة تماماً.\n\nالمهندسون الكبار بيقودوا الريفاكتور ده عبر 4 أو 5 طلبات دمج صغيرة، مع متابعة دقيقة لتغطية الاختبارات ومعدلات الأخطاء في Crashlytics لضمان أعلى مستويات الاستقرار والموثوقية."
    }
}

# ==========================================
# ARC-22: Returning API DTO Directly to Compose
# ==========================================
DATA["ARC-22"] = {
    "concept_en": """Allowing a Repository to return an API Data Transfer Object (DTO) directly to Jetpack Compose violates architectural boundaries and introduces severe coupling risks. DTOs are volatile wire-format models tailored specifically for network transport and JSON deserialization, frequently carrying nullable fields, serialization annotations, and backend-driven structures. Directly exposing DTOs couples UI composables to remote schema changes, degrading Compose recomposition efficiency because DTO classes lack stability guarantees. Furthermore, this practice forces UI components to execute costly date parsing and currency formatting calculations during composition passes, while crippling offline caching by bypassing the local database as the Single Source of Truth.""",
    "walkthrough_en": """Contrasting direct DTO exposure with clean domain and UI model separation:
```kotlin
// ❌ ANTI-PATTERN: Composable coupled directly to network DTO
@Composable
fun OrderRowBad(orderDto: OrderNetworkDto) { // Leaks Retrofit DTO into UI
    // In-composition formatting causes CPU overhead and dropped frames on 120Hz displays
    val formattedDate = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date(orderDto.epochTimestamp ?: 0L))
    Text("Order #${orderDto.order_id}: $${orderDto.total_cents?.div(100.0) ?: 0.0} on $formattedDate")
}

// ✅ CLEAN ARCHITECTURE: Clean separation with immutable UI models
@Immutable
data class OrderRowUiModel(
    val orderNumber: String,
    val formattedPrice: String,
    val formattedDate: String
)

@Composable
fun OrderRowGood(uiModel: OrderRowUiModel) {
    // Pure rendering: Composable is skippable, stable, and completely decoupled from network contracts
    Text("Order #${uiModel.orderNumber}: ${uiModel.formattedPrice} on ${uiModel.formattedDate}")
}
```""",
    "short_en": """Returning API DTOs directly to Compose tightly couples the UI to backend schema changes, degrades recomposition performance due to unstable and unskippable models, forces expensive formatting calculations inside the composition pass, and destroys offline caching by bypassing the local database as a Single Source of Truth.""",
    "structured_en": """Exposing API DTOs across the repository boundary into Jetpack Compose introduces significant architectural coupling and UI performance bottlenecks.
First, it creates vulnerability to backend schema volatility. DTOs mirror wire payloads shaped by server engineers. If an endpoint renames a JSON attribute, changes a type, or converts a field into an array, that network modification immediately breaks Composable functions, UI tests, and previews across the application.
Second, it compromises Jetpack Compose stability and smart recomposition. DTOs generated by serialization libraries rarely satisfy Compose compiler stability requirements. They often contain mutable properties, standard collections, or nullable fields, causing composables that accept them to become unskippable and re-render unnecessarily on parent invalidations.
Third, it introduces formatting overhead within the composition phase. When composables consume raw DTOs, they are forced to parse ISO timestamps, format monetary values, and concatenate localized strings during every frame, resulting in memory allocation churn and frame drops during fast scrolling.
Finally, direct DTO propagation prevents robust offline-first architecture, as wire payloads cannot be reconciled with Room database entities or persistent caching mechanisms.""",
    "deep_senior_en": """Under the hood, DTOs and Compose UI models serve fundamentally opposing architectural purposes. DTOs are optimized for deserialization ergonomics, relying on serialization annotations, nullable fallback defaults, and wire efficiency. In contrast, Compose UI models prioritize rendering efficiency, immutable data structures, and stability annotations like Immutable or Stable to maximize smart skipping during recomposition passes.
When a Composable accepts a raw DTO containing an unannotated List or nullable timestamps, the Compose compiler marks the parameter as unstable. Consequently, whenever the parent composable recomposes, the runtime cannot verify whether the parameter has changed, forcing full recomposition of the child composable.
Furthermore, executing string formatting, date parsing, or currency formatting inside Composable functions creates continuous memory allocation on the UI thread. During 120Hz scrolling across lazy lists, repeated object allocations trigger garbage collection pauses, causing visible frame drops and user interface jank.
The architectural contract mandates a two-stage transformation pipeline: the Data layer maps incoming network DTOs into clean Domain entities, validating data integrity and enforcing domain constraints. Subsequently, the Presentation layer (ViewModel) transforms Domain entities into tailored, pre-formatted, immutable UI models.
Staff engineers enforce this boundary through automated architectural linters and code reviews, ensuring that transport types from Retrofit or Ktor never cross past the Repository boundary.""",
    "meta_ar": {
        "id": "ARC-22",
        "questionAr": "عندما يقوم الـ Repository بإرجاع كائن API DTO مباشرة إلى Compose: ما هي مخاطر الارتباط؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مخاطر تسريب كائنات الشبكة للـ UI، وتأثير DTOs غير المستقرة على Recomposition في Jetpack Compose، ومشاكل الأداء الناتجة عن التنسيق داخل الـ Composable.",
        "why_it_matters_ar": "اعتماد واجهات Compose على كائنات الشبكة مباشرة يجعل أي تعديل بسيط في السيرفر يكسر شاشات التطبيق، ويسبب تقطيع الشاشة (Jank) بسبب الحسابات الثقيلة في كل فريم.",
        "worked_example_ar": "فصل كائن الشبكة عن نموذج الواجهة المستقر:\n```kotlin\n// DTO مخصص للشبكة فقط\ndata class UserDto(val first_name: String?, val created_at: Long?)\n// UI Model نقي ومستقر للواجهة\n@Immutable\ndata class UserUiModel(val fullName: String, val formattedDate: String)\n```",
        "trade_offs_ar": "فصل الموديلات يتطلب كتابة دوال تحويل (Mappers) إضافية، لكنه يوفر استقراراً تاماً للواجهة وأداء فائق السرعة مع دعم Skippable Composables.",
        "failure_modes_ar": "تنسيق التواريخ والعملات داخل دالة `@Composable` مباشرة، مما يستهلك موارد المعالج ويسبب هبوط الإطارات أثناء التمرير السريع في القوائم.",
        "production_perspective_ar": "في المشروعات الكبيرة، نمنع عبر قواعد Lint استيراد كلاسات الـ DTO أو مكتبات الشبكة داخل موديولات الـ UI، ونلزم الـ ViewModel بتحويل كل البيانات لنصوص جاهزة وموديلات مستقرة.",
        "how_to_answer_ar": "وضح أربعة مخاطر رئيسية: هشاشة الواجهة أمام تغييرات الـ API، وتدهور أداء Compose بسبب Unstable Classes، وعبء التنسيق داخل الفريمات، وانهيار معمارية الـ Offline-First.",
        "talking_points_ar": "استقرار الكومبوز (Compose Stability)، والـ Smart Skipping، والتنسيق المسبق للبيانات داخل الـ ViewModel، واستخدام التعليق التوضيحي `@Immutable`.",
        "follow_ups_ar": "- **المحاور:** \"كيف تؤثر كائنات الـ DTO على ميزة Smart Skipping في Jetpack Compose؟\"\n  **المرشح:** \"كائنات الـ DTO غالباً لا تحتوي على كلاسات مستقرة وتحوي قوائم عادية وحقول Nullable، فالـ Compose Compiler بيعتبرها Unstable ويضطر لإعادة رسم الـ Composable بالكامل مع كل فريم حتى لو البيانات متطابقة.\"\n\n- **المحاور:** \"أين يجب أن تتم عملية التنسيق (Formatting) للتواريخ والأموال؟\"\n  **المرشح:** \"داخل طبقة العرض وتحديداً الـ ViewModel أو Presentation Mapper، لتدخل إلى Compose كنصوص جاهزة ومباشرة بدون أي حسابات ثقيلة على مسار الـ UI.\"",
        "self_check_ar": "هل وضحت مخاطر تغييرات الـ API على الواجهة؟ هل شرحت Compose Stability و Smart Skipping؟ وهل بينت مشكلة التنسيق داخل الفريمات؟",
        "references_ar": f"- [Jetpack Compose Stability Explained](https://developer.android.com/develop/ui/compose/performance/stability) — التوثيق الرسمي لمعايير الاستقرار وتخطي إعادة الرسم في كومبوز.\n- [Data Layer Architecture](https://developer.android.com/topic/architecture/data-layer) — توثيق جوجل لفصل نماذج الشبكة عن نماذج النطاق.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "إرجاع كائنات الـ DTO مباشرة إلى Compose بيربط شاشات الواجهة بتغييرات السيرفر فيكسرها فور تعديل أي حقل، ويدهور أداء Compose لأن الـ DTOs بتعتبر كلاسات غير مستقرة تمنع الـ Smart Skipping وتسبب Recomposition متكرر، ويجبر الكومبوزابل على عمل حسابات وتنسيق تواريخ مكلفة على مسار الـ UI مما يسبب تقطيع الشاشة، ويدمر معمارية الـ Offline-First.",
        "best_answer_ar": "تسريب كائنات الـ DTO عبر حدود الـ Repository إلى Jetpack Compose بيعتبر خطأ معماري فادح يسبب مشاكل أداء وصيانة فورية.\n\nأولاً، ده بيخلق هشاشة شديدة أمام تقلبات الـ API؛ فالـ DTOs بتصمم بناءً على متطلبات السيرفر، وأي تعديل في اسم حقل أو نوعه من فريق الـ Backend هيكسر ملفات الـ Composable واختبارات الـ UI فوراً عبر التطبيق.\n\nثانياً، بيضر استقرار وأداء Jetpack Compose؛ لأن كلاسات الـ DTO المأخوذة من مكتبات الـ Serialization نادراً ما تحقق شروط الاستقرار للكومبايلر، فبيعتبرها Unstable ويصبح الكومبوزابل Unskippable ويعيد الرسم في كل فريم بدون داعٍ.\n\nثالثاً، بيفرض عبء تنسيق ثقيل داخل مرحلة الـ Composition؛ فالواجهة بتضطر لتحويل الـ Timestamps وتنسيق العملات داخل الفريمات السريعة، وده بيعمل ضغط على الـ Garbage Collector ويسبب سقوط الإطارات أثناء التمرير.\n\nوأخيراً، بيمنع بناء معمارية Offline-First حقيقية لأن كائنات الـ DTO لا تتوافق مع جداول قاعدة البيانات المحلية ومبدأ المصدر الأوحد للحقيقة.",
        "deep_answer_ar": "تحت الكابوت، كائنات الـ DTO ونماذج الـ Compose UI بتخدم أهدافاً معمارية متناقضة تماماً. الـ DTOs مصممة لمرونة وسرعة فك ترميز JSON عبر الشبكة بحقول اختيارية وترويسات Serialization، بينما نماذج الـ Compose UI بتستهدف كفاءة الرسم والاستقرار الكامل واستخدام تعليقات زي Immutable لتمكين الـ Smart Skipping.\n\nلما دالة Composable تستقبل كائن DTO جواه List عادية أو حقول غير مؤكدة الاستقرار، كومبايلر كومبوز بيصنف المعامل على إنه غير مستقر، وبالتالي كل ما الـ Parent يعيد رسم نفسه، الكومبوز مش بيقدر يضمن إن البيانات ماتغيرتش، فيضطر يعيد تنفيذ الـ Composable بالكامل حتى لو مفيش أي بيانات جديدة وصلت.\n\nبالإضافة لده، كتابة كود تنسيق نصوص وتواريخ وأرقام داخل الـ Composable بتعمل Memory Allocations مستمرة على مسار الـ UI. وفي شاشات التمرير السريع بتردد 120 هرتز، إنشاء الكائنات دي بيكرر تشغيل الـ Garbage Collector ويسبب Drop Frames ملحوظ وتهنيج في الرسوميات.\n\nالمعمارية الصحيحة بتفرض خط تحويل ثنائي: الـ Repository بيحول الـ DTO لـ Domain Model ويفحص صحة البيانات ويسجلها في قاعدة البيانات المحلية، وبعدين الـ ViewModel بيحول الـ Domain Model لـ UiModel غير قابل للتعديل ومجهز بنصوص منسقة مسبقاً، لعزل الواجهة تماماً وضمان أعلى أداء ممكن وثبات كامل للشاشات."
    }
}

# ==========================================
# ARC-23: When Clean Architecture is Overengineering
# ==========================================
DATA["ARC-23"] = {
    "concept_en": """Clean Architecture becomes overengineering when applied dogmatically to small applications, single-purpose utilities, or early-stage proofs-of-concept that lack complex business logic. In simple CRUD applications where the user interface merely displays data retrieved from a single REST endpoint or local storage without algorithmic manipulation, mandating a formal Domain layer, single-line passthrough Use Cases, multiple layers of identical data mappers, and micro-modularized Gradle builds introduces heavy cognitive and development overhead. Senior engineering embraces the YAGNI principle (You Aren't Gonna Need It) and evolutionary architecture, utilizing Pragmatic MVVM (presentation directly consuming repositories) until genuine domain complexity emerges.""",
    "walkthrough_en": """Comparing speculative overengineering with pragmatic architecture for small apps:
```kotlin
// ❌ OVERENGINEERING for a simple weather utility:
// Unnecessary layering: WeatherDto -> WeatherEntity -> WeatherDomain -> WeatherUiModel
// Useless passthrough UseCase that adds ceremony without business rules:
class GetWeatherUseCase(private val repository: WeatherRepository) {
    suspend operator fun invoke(city: String): WeatherDomain = repository.getWeather(city)
}

// ✅ PRAGMATIC MVVM: Clean, maintainable, and proportionate to requirements
// 1. Data Layer: Direct repository without redundant interfaces
class WeatherRepository(private val api: WeatherApi) {
    suspend fun fetchWeather(city: String): WeatherInfo =
        api.getWeather(city).toWeatherInfo()
}

// 2. Presentation Layer: ViewModel consumes repository directly
@HiltViewModel
class WeatherViewModel @Inject constructor(
    private val repository: WeatherRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<WeatherInfo?>(null)
    val uiState: StateFlow<WeatherInfo?> = _uiState.asStateFlow()

    fun loadWeather(city: String) = viewModelScope.launch {
        _uiState.value = repository.fetchWeather(city)
    }
}
```""",
    "short_en": """Clean Architecture is overengineering for small apps or simple CRUD utilities with no complex business rules. Forcing separate Domain layers, passthrough Use Cases, multiple redundant mappers, and multi-module splits slows feature delivery and adds cognitive burden. Pragmatic MVVM, where ViewModels consume Repositories directly, is the recommended architecture.""",
    "structured_en": """Software architecture represents an economic trade-off where abstractions purchase long-term decoupling at the immediate cost of structural complexity and development friction.
In small applications—such as proof-of-concept MVPs, single-screen utilities, or simple CRUD clients with no offline sync or domain calculations—adopting full Clean Architecture is textbook overengineering.
The classic symptoms of overengineering in modest projects include passthrough Use Cases where classes contain only one line delegating directly to a repository method. Another symptom is mapping exhaustion, where developers write tedious mapping functions between network DTOs, domain models, and UI models even though all three classes possess identical attributes. Furthermore, dividing a five-screen application into a dozen Gradle modules multiplies build configuration times without delivering tangible isolation benefits.
In these scenarios, senior engineers adopt Pragmatic MVVM. The Presentation layer interacts directly with concrete Repositories, sharing concise data models while preserving clean reactive state flows.""",
    "deep_senior_en": """Under the hood, professional software architecture must be evolutionary rather than speculative, adhering strictly to the YAGNI principle: You Aren't Gonna Need It. Anticipating enterprise complexity that may never materialize results in premature optimization, where teams spend more engineering hours maintaining plumbing and boilerplate interfaces than delivering user value.
Starting with a pragmatic two-tier architecture comprising Presentation and Data does not preclude adopting Clean Architecture later. Because code remains cleanly decoupled at the ViewModel and Repository seam, extracting a formal Domain layer and dedicated Use Cases requires only minimal effort once genuine business rules, shared workflows, or team scaling demands arise.
Official Android architecture guidance explicitly reinforces this pragmatic approach, designating the Domain layer as completely optional. Use Cases are intended to encapsulate reusable, non-trivial business logic, such as coordinating complex multi-repository validations or cryptographic calculations. When a Use Case merely acts as an anemic passthrough forwarding calls to a repository, it adds zero architectural value while introducing unnecessary indirection and file sprawl.
Staff engineers calibrate architectural complexity against current project scope, team size, and velocity requirements, applying the minimum level of abstraction necessary to guarantee clean testability and near-term maintainability. This pragmatic discipline prevents premature overengineering and ensures that codebases stay lean, understandable, and rapid to iterate upon during critical business phases.""",
    "meta_ar": {
        "id": "ARC-23",
        "questionAr": "لديك تطبيق صغير وبسيط: متى تصبح Clean Architecture زيادة هندسية غير مبررة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على الموازنة بين التعقيد المعماري ومتطلبات المشروع، وتطبيق مبدأ YAGNI، ومعرفة متى تكون الـ UseCases والـ Multi-module عبئاً غير مبرر، وتفضيل Pragmatic MVVM.",
        "why_it_matters_ar": "الإفراط الهندسي (Overengineering) في التطبيقات البسيطة يبطئ وتيرة التطوير، ويزيد وقت البناء (Build Times)، ويصيب المطورين بالإرهاق بسبب كثرة الملفات العقيمة.",
        "worked_example_ar": "المعمارية البراغماتية لتطبيق بسيط:\n```kotlin\n// مستودع مباشر وواضح بدون تعقيد\nclass SimpleRepo(val api: Api) { suspend fun getData() = api.fetch() }\n// ViewModel يتصل بالمستودع مباشرة بدون UseCase وسيط\nclass SimpleVm(val repo: SimpleRepo) : ViewModel() {\n    val data = flow { emit(repo.getData()) }\n}\n```",
        "trade_offs_ar": "تجاوز طبقة الـ Domain يقلل عدد الملفات والبويلربليت ويسرع التطوير، لكنه يتطلب يقظة لاستخراج Use Cases مستقبلاً إذا نمت قواعد البيزنس.",
        "failure_modes_ar": "إنشاء موديولات Gradle متعددة وطبقات UseCases و 4 موديلات متطابقة لتطبيق يعرض شاشتين فقط، مما يعطل إطلاق الـ MVP بدون أي فائدة حقيقية.",
        "production_perspective_ar": "في المشروعات الناشئة، نعتمد Pragmatic MVVM لتسريع الوصول للسوق (Time-to-Market)، ونلتزم بتوثيق جوجل الرسمي الذي يقر بأن طبقة الـ Domain اختيارية تماماً وليست إلزامية.",
        "how_to_answer_ar": "وضح أن المعمارية مبنية على الموازنة، واذكر أعراض الـ Overengineering مثل Passthrough UseCases وإرهاق الـ Mapping، واقترح Pragmatic MVVM كبديل ذكي.",
        "talking_points_ar": "مبدأ YAGNI، والمعمارية التطورية (Evolutionary Architecture)، وطبقة Domain الاختيارية في توثيق جوجل، و Passthrough Use Cases.",
        "follow_ups_ar": "- **المحاور:** \"ما هو الـ Passthrough Use Case ولماذا يعتبر سيئاً في التطبيقات الصغيرة؟\"\n  **المرشح:** \"هو Use Case لا يحتوي على أي منطق بيزنس ويكتفي بكتابة سطر واحد يمرر النداء للمستودع، وده بيضيف ملفات إضافية وتشتيت للمطورين بدون تقديم أي قيمة معمارية حقيقية.\"\n\n- **المحاور:** \"متى نقرر إضافة طبقة الـ Domain والـ Use Cases لتطبيق بسيط؟\"\n  **المرشح:** \"عندما تبدأ قواعد البيزنس في التعقيد، أو تكرار نفس العملية الحسابية عبر عدة شاشات، أو عندما يتوسع الفريق الهندسي ويحتاج لعزل المنطق عن الـ ViewModels.\"",
        "self_check_ar": "هل ذكرت مبدأ YAGNI؟ هل شرحت أعراض الـ Overengineering في التطبيقات البسيطة؟ وهل وضحت بديل Pragmatic MVVM؟",
        "references_ar": f"- [Android Architecture: Domain Layer](https://developer.android.com/topic/architecture/domain-layer) — توثيق جوجل الرسمي الذي يؤكد أن طبقة الـ Domain اختيارية.\n- [Clean Architecture by Robert C. Martin](https://www.oreilly.com/library/view/clean-architecture-a/9780134494272/) — المرجع الأصلي لمبادئ المعمارية وتكاليف التجريد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "معمارية Clean Architecture بتعتبر زيادة هندسية غير مبررة (Overengineering) في التطبيقات الصغيرة أو أدوات الـ CRUD البسيطة اللي مفيهاش أي منطق بيزنس معقد. فرض طبقة Domain و Use Cases بتعمل مجرد تمرير لسطر واحد، وإنشاء 4 موديلات متطابقة، وتقسيم المشروع لـ 10 موديولات لتطبيق شاشتين بيعطل سرعة الإطلاق ويزيد تعقيد الكود. في الحالات دي، معمارية Pragmatic MVVM هي الأنسب والأكثر كفاءة.",
        "best_answer_ar": "تصميم المعمارية هو موازنة اقتصادية وهندسية؛ التجريد بيفيد في فك الارتباط على المدى البعيد، لكنه بيجي بتكلفة فورية في التعقيد الهيكلي وبطء وتيرة العمل.\n\nفي التطبيقات الصغيرة زي نماذج الـ MVP الأولية، أو الأدوات أحادية الغرض، أو تطبيقات العرض البسيطة اللي بتجلب داتا من API واحد بدون كاش معقد أو حسابات، تطبيق معمارية Clean Architecture الكاملة بيكون زيادة غير مبررة تماماً.\n\nأوضح علامات الـ Overengineering في المشاريع البسيطة هي ظهور Passthrough Use Cases، ودي كلاسات مفيهاش أي لوجيك غير سطر واحد بينادي الـ Repository مباشرة. وتاني علامة هي إرهاق الـ Mapping المتكرر بين DTO و Entity و Domain و UiModel مع إن الأربعة بيحتووا على نفس الحقول بالحرف. ده غير تقسيم شاشتين لتسع موديولات Gradle تضاعف وقت البناء.\n\nفي السيناريوهات دي، المهندسون المحترفون بيعتمدوا معمارية Pragmatic MVVM؛ حيث يتعامل الـ ViewModel مع الـ Repository مباشرة بموديلات موحدة مع الحفاظ على تدفقات الحالة التفاعلية.",
        "deep_answer_ar": "تحت الكابوت، المعمارية الهندسية المحترفة لازم تكون تطورية مش تخمينية، التزاماً بمبدأ YAGNI اللي بيأكد إنك مش محتاج تضيف تجريد غير لما تحتاجه فعلياً. التنبؤ بتعقيدات مستقبلية قد لا تحدث بيؤدي لـ Premature Optimization، وبدل ما الفريق يركز على ميزات المستخدم بيفضل يضيع وقته في صيانة واجهات وبويلربليت عقيم.\n\nالبدء بمعمارية براغماتية من طبقتين: عرض وبيانات مش بيمنع إطلاقاً التحول لـ Clean Architecture لاحقاً. ولأن الكود مفصول بشكل سليم عند حدود الـ ViewModel والـ Repository، فاستخراج طبقة Domain و Use Cases مش هياخد غير ساعات معدودة أول ما تظهر قواعد بيزنس حقيقية أو عمليات معقدة مشتركة بين الشاشات.\n\nتوثيق أندرويد الرسمي من جوجل بيدعم التوجه ده بوضوح، وبيعرف طبقة الـ Domain صراحة على إنها طبقة اختيارية. الـ Use Case هدفه احتواء منطق أعمال حقيقي زي معالجة خوارزميات أو دمج أكثر من مستودع، لكن لما يقتصر على تمرير مكالمة للـ Repository، فهو بيضيف Indirection عقيم بدون أي عائد مع زيادة عدد الملفات وصعوبة التتبع.\n\nالمهندسون الكبار بيقيسوا التعقيد المعماري بحجم المشروع الحالي وحجم الفريق واحتياجات السرعة، وبيطبقوا الحد الأدنى من التجريد اللي يحقق سهولة الاختبار والصيانة، وبكده يفضل الكود بسيط وسهل الفهم وجاهز للتوسع بسلاسة لما تظهر الحاجة الحقيقية."
    }
}

# ==========================================
# ARC-24: Cross-Feature Account/Session State Without Circular Dependencies
# ==========================================
DATA["ARC-24"] = {
    "concept_en": """Designing cross-feature account and session state without circular dependencies requires applying the Dependency Inversion Principle by hoisting authentication contracts into a dedicated foundational module, such as :core:session or :core:user. In a modularized Gradle architecture, independent feature modules (like :feature:checkout and :feature:profile) must never declare horizontal dependencies on each other. Instead, the shared session module defines the immutable UserSession data model and an authoritative SessionRepository interface exposing a StateFlow<UserSession?>. All feature modules depend downward on this core contract. A centralized network authenticator invalidates the session upon encountering HTTP 401 Unauthorized responses, while the root navigation graph in the :app module observes session state changes to execute global logout routing.""",
    "walkthrough_en": """Structuring cross-feature session state across independent Gradle modules:
```kotlin
// 1. In module ':core:session' (Foundational module with zero feature dependencies)
data class UserSession(val userId: String, val authToken: String, val isPremium: Boolean)

interface SessionRepository {
    val activeSession: StateFlow<UserSession?>
    suspend fun updateSession(session: UserSession)
    suspend fun clearSession()
}

// 2. In module ':feature:checkout' (Depends solely on ':core:session', NOT on ':feature:profile')
class CheckoutViewModel @Inject constructor(
    private val sessionRepository: SessionRepository
) : ViewModel() {
    val isUserPremium: StateFlow<Boolean> = sessionRepository.activeSession
        .map { it?.isPremium == true }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), false)
}

// 3. In module ':app' (Root orchestration module coordinating global logout)
@Composable
fun RootAppNavigation(sessionRepository: SessionRepository) {
    val session by sessionRepository.activeSession.collectAsStateWithLifecycle()
    if (session == null) {
        AuthNavGraph() // Automatically navigates to Login on session expiration
    } else {
        MainAppNavGraph()
    }
}
```""",
    "short_en": """Design cross-feature session state by hoisting it into a lower-level :core:session module that feature modules depend on unidirectionally. Expose an immutable StateFlow<UserSession?> from an authoritative SessionRepository, preventing circular Gradle compilation errors and enabling automatic global logout coordination through the root navigation graph.""",
    "structured_en": """Managing shared session state across modularized Android features without inducing circular Gradle dependencies requires strict unidirectional architecture.
Feature modules such as checkout, account, and chat must never depend horizontally on one another. If feature payment imports feature account while account requires payment status, Gradle compilation halts with a circular dependency failure.
To resolve this, we hoist session models and contracts downward into a dedicated foundational module: :core:session. This core module has zero dependencies on any feature modules. All feature modules declare a unidirectional downward dependency on :core:session.
Within :core:session, a singleton SessionRepository owns the active authentication credentials, exposing an immutable StateFlow of UserSession. Feature ViewModels inject this repository to observe session state or check user permissions reactively.
For global session termination, such as receiving an HTTP 401 Unauthorized response, an OkHttp authenticator in :core:network calls clearSession on the repository. The root navigation host in the top-level :app module observes the session flow; when the session becomes null, it invalidates active feature graphs and immediately routes to the login screen.""",
    "deep_senior_en": """Under the hood, managing shared identity across a large-scale multi-module build requires preventing module graph cycles and memory leakage. Circular dependencies in Gradle are fatal compile-time errors because the build graph must form a Directed Acyclic Graph (DAG) to determine task ordering and compilation outputs.
By decoupling session state into an API and Implementation structure—such as :core:session-api containing data classes and repository interfaces, and :core:session-data managing encrypted local storage—we minimize compilation dependencies. Feature modules compile against lightweight API interfaces without recompiling data sources when storage implementations change.
When features need to interact across boundaries—for example, when a successful checkout in :feature:checkout must navigate to order history in :feature:profile—features must not navigate directly between each other. Instead, engineers use navigation event hoisting. The checkout feature exposes an output lambda or sealed navigation event such as onOrderCompleted, which the top-level :app orchestrator intercepts to route to the profile screen.
Staff engineers also safeguard session lifecycle by avoiding insecure process-level global singletons. SessionRepository is backed by EncryptedSharedPreferences or encrypted Room storage and securely managed via Hilt in the SingletonComponent.
When a session terminates, the repository cancels active user coroutines and wipes secure storage, guaranteeing that sensitive tokens and cached personal information never leak into subsequent sessions.""",
    "meta_ar": {
        "id": "ARC-24",
        "questionAr": "كيف تصمم حالة الحساب أو الجلسة المشتركة دون الوقوع في تبعيات دائرية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصميم معمارية الموديولات في Gradle، واستخراج Core Modules لمنع التبعيات الدائرية، وإدارة جلسة المستخدم (Session Management)، والتوجيه العام عند تسجيل الخروج.",
        "why_it_matters_ar": "الاعتماد المتبادل بين الموديولات (Circular Dependencies) يمنع الـ Build في Gradle تماماً، وتخزين الجلسة في كائنات عشوائية يسبب تسريب بيانات المستخدمين بعد الخروج.",
        "worked_example_ar": "هيكلة موديول Core مشترك لحالة الجلسة:\n```kotlin\n// داخل :core:session المشترك\ninterface SessionRepository {\n    val session: StateFlow<UserSession?>\n    suspend fun clearSession()\n}\n// داخل :app لمراقبة الخروج العام\nval session by sessionRepo.session.collectAsStateWithLifecycle()\nif (session == null) LoginScreen() else MainScreen()\n```",
        "trade_offs_ar": "استخراج موديول Core إضافي يزيد عدد موديولات المشروع قليلاً، لكنه يضمن استقلالية البناء تماماً وعدم حدوث حلقات دائرية.",
        "failure_modes_ar": "استيراد موديول الميزات لبعضها البعض أفقياً، أو الاحتفاظ ببيانات الجلسة في كائن Singleton ساكن في الذاكرة دون مسحه عند استلام 401 من الشبكة.",
        "production_perspective_ar": "في التطبيقات المالية، نستخدم موديول `:core:session` مشفر بمفاتيح Android Keystore، ويقوم OkHttp Authenticator بمسح الجلسة فور استلام كود 401 من السيرفر.",
        "how_to_answer_ar": "اشرح استخراج موديول أساسي `:core:session` تعتمد عليه الميزات لأسفل، وتوفير StateFlow للجلسة، وتوجيه الـ Logout العام عبر Root NavHost في موديول `:app`.",
        "talking_points_ar": "التبعية أحادية الاتجاه (Unidirectional Dependency)، ونمط API/Impl، ومسح الجلسة عند استلام 401، وتوجيه التنقل عبر Hoisting.",
        "follow_ups_ar": "- **المحاور:** \"كيف تمنع موديول المدفوعات من استيراد موديول الملف الشخصي عند الرغبة في التنقل بينهما؟\"\n  **المرشح:** \"عبر Navigation Event Hoisting؛ موديول المدفوعات بيخرج Lambda زي `onNavigateToProfile`، والموديول الأعلى `:app` اللي بيعرف الاتنين هو اللي بيوصل التنقل بينهم بدون ما يعتمدوا على بعض.\"\n\n- **المحاور:** \"كيف نضمن مسح بيانات الجلسة بالكامل عند انتهاء صلاحية الـ Token؟\"\n  **المرشح:** \"بنربط OkHttp Authenticator بمستودع الجلسة؛ أول ما يرجع 401 بننادي `clearSession()` اللي بيمسح التخزين المشفر ويلغي الـ Coroutines والـ NavHost يرجع لشاشة الدخول فوراً.\"",
        "self_check_ar": "هل شرحت سبب التبعيات الدائرية في Gradle؟ هل وضحت استخراج :core:session؟ وهل بينت آلية تسجيل الخروج الشامل عند 401؟",
        "references_ar": f"- [Guide to Android app modularization](https://developer.android.com/topic/modularization) — الدليل الرسمي لتقسيم المشروعات لموديولات وتجنب الحلقات الدائرية.\n- [Dependency Injection in multi-module apps](https://developer.android.com/training/dependency-injection/hilt-multi-module) — إدارة التبعيات وحقن الجلسة عبر Hilt.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنصمم حالة الجلسة المشتركة برفعها لموديول أساسي في الطبقة السفلية زي `:core:session` تعتمد عليه كل موديولات الميزات في اتجاه واحد لأسفل بدون ما تعتمد على بعضها أفقياً. الموديول ده بيوفر SessionRepository بيعرض StateFlow للجلسة، وبنربطه بـ OkHttp Authenticator لمسح الجلسة فور استلام 401، وشاشة التنقل الرئيسية في موديول `:app` بتراقب التدفق ده وترجع المستخدم لشاشة الدخول تلقائياً.",
        "best_answer_ar": "إدارة حالة الحساب والجلسة عبر موديولات متعددة بدون الوقوع في مشكلة التبعيات الدائرية في Gradle بتتطلب تطبيق معمارية أحادية الاتجاه بصرامة.\n\nموديولات الميزات زي الدفع والملف الشخصي والسلة ممنوع تعتمد على بعضها أفقياً؛ لأن اعتماد موديول A على B واعتماد B على A بيفشل عملية البناء فوراً مع خطأ Circular Dependency.\n\nلحل المعضلة دي، بنستخرج بيانات وعقود الجلسة لموديول أساسي في الـ Core Layer وليكن `:core:session`. الموديول ده مبيعتمدش على أي Feature Module، وكل موديولات الميزات بتعتمد عليه في اتجاه واحد لأسفل.\n\nداخل `:core:session`، بيكون فيه مستودع موحد Singleton باسم SessionRepository بيملك بيانات الاعتماد الحالية، وبيكشف StateFlow غير قابلة للتعديل تمثل حالة الجلسة. والـ ViewModels في الميزات المختلفة بتحقن المستودع ده لمراقبة حالة المستخدم وصلاحياته.\n\nوعلشان ندير تسجيل الخروج العام، بنربط OkHttp Authenticator في موديول الشبكة بمستودع الجلسة؛ فأول ما يرجع كود 401 من أي طلب، بيستدعي مسح الجلسة فوراً. ونظام التنقل الرئيسي في موديول `:app` بيراقب التدفق ده، وأول ما تصبح الجلسة Null بيلغي كل الشاشات المفتوحة ويرجع لشاشة تسجيل الدخول.",
        "deep_answer_ar": "تحت الكابوت، إدارة هوية المستخدم عبر مشروع ضخم مقسم لموديولات بتتطلب منع حلقات الجراف والتأكد من عدم تسريب البيانات في الذاكرة. التبعيات الدائرية في Gradle بتوقف البناء لأن جراف المهام لازم يكون Directed Acyclic Graph لتحديد تسلسل الترجمة وتوليد المخرجات البرمجية.\n\nفصل الجلسة لنمط API و Impl زي `:core:session-api` اللي بيحتوي على الـ Data Classes والـ Interfaces، وموديول منفصل للـ Implementation زي `:core:session-data` بيمنع إعادة ترجمة الموديولات التابعة لو غيرنا تفاصيل التخزين الداخلي أو مكتبات التشفير.\n\nولما ميزة تحتاج تطلب إجراء من ميزة تانية، زي التنقل للملف الشخصي بعد نجاح الدفع، بنلجأ لـ Navigation Event Hoisting؛ فموديول الدفع مبيستوردش موديول الحساب أبداً، بل بيكشف Lambda للمغادرة أو Event مختوم، وموديول `:app` اللي بيعرف الاتنين هو اللي بيربط التنقل بينهم في الـ Root NavHost.\n\nالمهندسون الكبار بيحرصوا كمان على حفظ الجلسة في EncryptedSharedPreferences أو Room مشفر بمفاتيح Android Keystore بدل الـ Singletons العادية في الذاكرة لتأمين الجلسة ضد هجمات الذاكرة. ولما تنتهي الجلسة أو يرجع خطأ 401، المستودع بيمسح التخزين المشفر فوراً ويلغي الـ Coroutines النشطة علشان نضمن عدم تسريب أي Tokens أو بيانات سرية للمستخدم التالي، مما يحقق أعلى معايير الأمان المالي والمؤسسي."
    }
}

# ==========================================
# ARC-25: Comparing MVVM and MVI for a Payment State Machine
# ==========================================
DATA["ARC-25"] = {
    "concept_en": """Comparing MVVM and MVI for a payment state machine with dense transitions demonstrates why MVI is architecturally superior for high-stakes financial workflows. In conventional MVVM, state is frequently distributed across multiple mutable observables (such as isProcessing, is3DSecureActive, error, and transactionReceipt). Concurrent asynchronous events or rapid button clicks can result in illegal hybrid states, such as displaying an error banner while an authorization request is actively executing, potentially leading to catastrophic duplicate charges. Conversely, MVI models the workflow as a strict, mathematical Finite State Machine (FSM). A single immutable sealed interface represents mutual exclusivity, and transitions execute strictly through a deterministic pure Reducer function that rejects invalid transitions.""",
    "walkthrough_en": """Implementing a deterministic payment state machine with MVI and a pure Reducer:
```kotlin
// 1. Mutually exclusive states modeled as a sealed interface
sealed interface PaymentState {
    data object Idle : PaymentState
    data class Authorizing(val transactionId: String) : PaymentState
    data class Requires3DSecure(val challengeUrl: String) : PaymentState
    data class Success(val receiptId: String) : PaymentState
    data class Failed(val reason: String, val canRetry: Boolean) : PaymentState
}

// 2. Explicit user or system intents
sealed interface PaymentIntent {
    data class SubmitPayment(val amountCents: Long, val cardId: String) : PaymentIntent
    data class VerificationCompleted(val token: String) : PaymentIntent
    data object Retry : PaymentIntent
}

// 3. Pure Reducer function guaranteeing mathematical state determinism
fun paymentReducer(state: PaymentState, intent: PaymentIntent): PaymentState = when (state) {
    is PaymentState.Idle -> when (intent) {
        is PaymentIntent.SubmitPayment -> PaymentState.Authorizing("txn_${System.currentTimeMillis()}")
        else -> state // Reject invalid intent
    }
    is PaymentState.Authorizing -> when (intent) {
        is PaymentIntent.SubmitPayment -> state // PREVENT DOUBLE-CHARGE: ignore repeated clicks!
        is PaymentIntent.VerificationCompleted -> PaymentState.Success("rec_123")
        else -> state
    }
    is PaymentState.Failed -> when (intent) {
        is PaymentIntent.Retry -> if (state.canRetry) PaymentState.Idle else state
        else -> state
    }
    else -> state
}
```""",
    "short_en": """For a complex payment state machine, MVI decisively outperforms MVVM. MVVM's scattered multiple state streams risk illegal state combinations and race conditions such as duplicate transactions. MVI models the workflow as a deterministic Finite State Machine where a pure Reducer transitions a single immutable PaymentState, guaranteeing that duplicate clicks and invalid transitions are rejected.""",
    "structured_en": """When building mission-critical workflows with dense, irreversible transitions—such as a fintech payment pipeline—MVI is substantially superior to MVVM.
In standard MVVM architectures, presentation state is frequently fragmented across several independent observable properties: loading booleans, error objects, and success payloads. This fragmentation introduces an illegal state vulnerability. Rapid double-taps or overlapping network retries can place the ViewModel into conflicting states where loading is true while an error exists simultaneously, risking double authorizations and customer overcharging.
In contrast, MVI models the payment process as a deterministic Finite State Machine. States are defined within an exhaustive sealed interface hierarchy comprising Idle, Authorizing, Requires3DSecure, Success, and Failed.
State mutations occur exclusively through a pure Reducer function that accepts the current state and an incoming intent, yielding a new state. If a user rapidly taps the pay button twice, the first intent transitions the machine to Authorizing; when the second intent arrives, the reducer deterministically discards it because Authorizing does not permit re-submission.
This mathematical rigor eliminates race conditions, guarantees transaction idempotency on the client, and enables comprehensive audit logging.""",
    "deep_senior_en": """Under the hood, implementing an enterprise payment workflow with MVI unlocks unparalleled determinism, testability, and auditability. In distributed banking systems, every transaction carries an idempotency key to prevent duplicate charges. MVI complements this backend safeguard on the client side by transforming state management into a formal State Transition Table.
Because the Reducer is a pure, side-effect-free function—taking (CurrentState, Intent) and returning NewState—testing the entire state machine requires zero mocks or coroutine schedulers. Unit tests execute as pure mathematical assertions. Teams can even employ property-based testing, firing thousands of randomized intent sequences at the reducer to prove mathematically that the system can never reach an invalid double-authorization state.
Furthermore, MVI enables deterministic state transition telemetry. By intercepting every reducer call, an engineering team can pipe state transitions directly into monitoring tools like Datadog. When a user encounters a payment drop or timeout, support engineers inspect the chronological transition sequence to identify the exact point of failure.
Staff engineers balance this rigor by utilizing hybrid architectures where complex transactional screens adopt MVI, while simpler static screens utilize lighter MVVM patterns to avoid unnecessary ceremony. This selective application of MVI ensures maximum resilience for business-critical payment operations without imposing architectural overhead across the broader application.""",
    "meta_ar": {
        "id": "ARC-25",
        "questionAr": "قارن بين MVVM و MVI عند بناء آلة حالات للدفع (Payment State Machine) معقدة.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "المقارنة المعمارية الدقيقة بين MVVM و MVI، وتصميم آلات الحالات المحدودة (Finite State Machine)، ومنع تكرار المعاملات المالية (Double-Charging)، والتحقق الرياضي من انتقالات الحالة عبر Reducer.",
        "why_it_matters_ar": "عمليات الدفع حساسة مالياً وقانونياً؛ وأي سباق بيانات (Race Condition) أو ضغط متكرر على زر الدفع قد يخصم المبلغ مرتين من العميل إذا لم تكن المعمارية محكمة قطيعاً.",
        "worked_example_ar": "دالة Reducer نقية تمنع الضغط المزدوج أثناء الدفع:\n```kotlin\nfun reduce(state: PayState, intent: PayIntent): PayState = when (state) {\n    is PayState.Idle -> if (intent is PayIntent.Pay) PayState.Authorizing else state\n    // حماية تامة: تجاهل أي نداء دفع إضافي أثناء التفويض لمنع الخصم المزدوج!\n    is PayState.Authorizing -> state\n    else -> state\n}\n```",
        "trade_offs_ar": "نمط MVI يتطلب كتابة كود إضافي للأحداث والـ Reducer، لكنه يوفر حماية مطلقة وتدقيقاً كاملاً في تدفقات الدفع الحساسة مقارنة بـ MVVM.",
        "failure_modes_ar": "تشتيت حالة الدفع بين متغيرات Boolean متعددة في MVVM، مما يسبب اجتماع `isLoading = true` مع ظهور رسالة خطأ سابقة وحدوث خصم مزدوج عند تكرار النقر.",
        "production_perspective_ar": "في تطبيقات البنوك والتكنولوجيا المالية، نستخدم MVI مع مفتاح Idempotency Key لكل معاملة، ونرسل سجل انتقالات الـ Reducer لـ Datadog للتدقيق وتتبع مسار العمليات.",
        "how_to_answer_ar": "قارن بين هشاشة تعدد المتغيرات في MVVM وقوة الـ Finite State Machine في MVI، واشرح دور الـ Reducer النقي في منع الانتقالات غير القانونية وسهولة الاختبار.",
        "talking_points_ar": "آلة الحالات المحدودة (FSM)، ودالة Reducer النقية، ومنع الخصم المزدوج، وتدقيق الانتقالات (State Transition Auditing)، ومفاتيح Idempotency.",
        "follow_ups_ar": "- **المحاور:** \"كيف يمنع MVI مشكلة الخصم المزدوج لو المستخدم ضغط على زر الدفع مرتين بسرعة؟\"\n  **المرشح:** \"الضغطة الأولى بتحول الحالة لـ Authorizing؛ ولما يوصل حدث الضغط التاني، الـ Reducer بيفحص الحالة الحالية ويتجاهل الحدث تماماً لأن الانتقال غير مسموح به رياضياً.\"\n\n- **المحاور:** \"ما هي ميزة دالة الـ Reducer في اختبارات الوحدة مقارنة بـ MVVM؟\"\n  **المرشح:** \"الـ Reducer دالة نقية (Pure Function) بدون Side-effects، فبنقدر نختبرها بحسابات رياضية مباشرة بدون أي Mocks أو Coroutine Dispatchers، ونقدر ننفذ عليها Property-based Testing.\"",
        "self_check_ar": "هل شرحت عيوب MVVM في التدفقات المالية؟ هل بينت هيكلة FSM والـ Reducer في MVI؟ وهل وضحت منع الخصم المزدوج؟",
        "references_ar": f"- [Android UI Architecture: State Holders](https://developer.android.com/topic/architecture/ui-layer/stateholders) — توثيق جوجل الرسمي لإدارة الحالة والأنماط المعمارية للواجهة.\n- [Managing State in Jetpack Compose](https://developer.android.com/develop/ui/compose/state) — أفضل ممارسات الحالات غير القابلة للتجزئة وتدفق البيانات أحادي الاتجاه.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "في تدفقات الدفع الحساسة، نمط MVI بيتفوق باكتساح على MVVM. في MVVM التقليدي، تشتت الحالة بين متغيرات منفصلة زي التحميل والخطأ بيعرض التطبيق لسباق بيانات وانتقالات غير قانونية ممكن تخصم الفلوس مرتين. بينما في MVI، بنبني آلة حالات قطعية (Finite State Machine) بحالة واحدة مختومة ودالة Reducer نقية، بتمنع الضغط المزدوج وترفض أي حدث غير قانوني بشكل قطعي.",
        "best_answer_ar": "عند بناء تدفقات الدفع والمعاملات المالية الحساسة، معمارية MVI بتتفوق بشكل كاسح على MVVM من حيث الأمان والموثوقية.\n\nفي معمارية MVVM التقليدية، الحالة غالباً بتكون مبعثرة بين عدة متغيرات مستقلة: متغير للتحميل، ومتغير للخطأ، ومتغير للنجاح. التشتت ده بيخلق ثغرة حالات غير قانونية؛ فلو المستخدم نقر بسرعة مرتين على زر الدفع أو حصل تأخير في الشبكة، الـ ViewModel ممكن يدخل في حالة هجينة متناقضة يكون فيها التحميل نشطاً مع وجود رسالة خطأ، وده بيفتح الباب لتكرار المعاملة والخصم المزدوج.\n\nعلى العكس تماماً، MVI بيصمم عملية الدفع كآلة حالات قطعية ومحددة (Finite State Machine). الحالات بتتعرف داخل كائن مختوم واحد بيشمل: الاستعداد، وجاري التفويض، وتحدي 3D Secure، والنجاح، والفشل.\n\nتغيير الحالة بيتم حصرياً عبر دالة Reducer نقية؛ فلو المستخدم ضغط مرتين بسرعة، الضغطة الأولى بتنقل الحالة لـ Authorizing، ولما توصل الضغطة التانية، الـ Reducer بيتجاهلها تماماً لأن الحالة الحالية لا تسمح بإعادة الإرسال. وده بيضمن دقة متناهية وسهولة مطلقة في الاختبار والتدقيق.",
        "deep_answer_ar": "تحت الكابوت، تطبيق MVI في مسارات الدفع المتقدمة بيوفر استقراراً رياضياً وتدقيقاً أمنياً لا يمكن تحقيقه بـ MVVM البسيط. في الأنظمة المالية، كل معاملة لازم تدعم Idempotency لمنع التكرار، و MVI بيطبق الضمانة دي على مستوى العميل بتحويل إدارة الحالة لجدول انتقالات قطعي لا يقبل اللبس.\n\nولأن دالة الـ Reducer دالة نقية تماماً بدون أي Side-effects؛ بتستقبل الحالة الحالية والحدث وترجع الحالة الجديدة، فاختبار الـ State Machine بالكامل مش بيحتاج أي Mocks أو Dispatchers، بل بيختبر كدوال رياضية نقية سريعة للغاية. والفرق بتقدر تشغل Property-based Testing بآلاف الأحداث العشوائية لإثبات استحالة دخول النظام في حالة خصم مزدوج أو تجمد في شاشات الدفع.\n\nبالإضافة لده، MVI بيسمح بعمل State Transition Logging؛ فبنقدر نراقب كل انتقال بين الحالات ونرسله لأدوات المراقبة زي Datadog، ولو مستخدم واجه مشكلة أثناء الدفع، فريق الدعم بيقدر يراجع مسار الحالات الزمني بدقة متناهية لتحديد سبب التوقف ومعالجة المشكلة فوراً.\n\nالمهندسون الكبار بيتبعوا نهجاً متوازناً، بحيث يطبقوا صرامة MVI في الشاشات المالية وشاشات الدفع الحساسة، مع الاكتفاء بـ MVVM الخفيف في الشاشات الثابتة لتفادي البويلربليت غير الضروري، وبكده بنجمع بين أقصى درجات الأمان المالي وسرعة التطوير اليومي وسهولة الصيانة على المدى الطويل."
    }
}

# ==========================================
# ARC-26: Enforcing Boundaries Without Boilerplate Interfaces
# ==========================================
DATA["ARC-26"] = {
    "concept_en": """Enforcing architectural boundaries without succumbing to ceremonial boilerplate interfaces requires utilizing compiler-enforced Gradle modularization, Kotlin language visibility controls, and automated architecture linting tools. The traditional dogma of creating an interface for every single class (such as UserRepository for UserRepositoryImpl) doubles file counts and adds cognitive friction without delivering tangible architectural safety. Instead, senior engineers enforce boundaries at compile-time by structuring the project into focused Gradle modules where forbidden imports physically fail compilation. Implementation details are encapsulated using Kotlin's internal visibility modifier, while architecture enforcement frameworks like Konsist or ArchUnit validate structural rules in continuous integration.""",
    "walkthrough_en": """Enforcing architectural boundaries via Konsist tests and Kotlin internal visibility:
```kotlin
// 1. Module encapsulation: Keep concrete classes internal, exposing only required entry points
// Inside module ':core:database'
internal class RoomUserDao : UserDao { ... } // Inaccessible to presentation modules!

// 2. Automated Architecture Testing in CI with Konsist
class ArchitectureRulesTest {
    @Test
    fun presentationMustNotAccessDatabaseOrNetworkInternals() {
        Konsist.scopeFromProject()
            .classes()
            .withNameEndingWith("ViewModel")
            .assertNot { viewModel ->
                viewModel.hasImportWithText { importPath ->
                    importPath.startsWith("androidx.room") ||
                    importPath.startsWith("retrofit2") ||
                    importPath.contains(".data.local.")
                }
            }
    }

    @Test
    fun useCasesMustResideInDomainAndExposeOnlyInvoke() {
        Konsist.scopeFromProject()
            .classes()
            .withNameEndingWith("UseCase")
            .assert { useCase ->
                useCase.resideInPackage("..domain..") &&
                useCase.numPublicDeclarations() == 1 &&
                useCase.hasFunctionWithText { it.contains("operator fun invoke") }
            }
    }
}
```""",
    "short_en": """Enforce architectural boundaries without boilerplate interfaces by leveraging Gradle multi-module compilation isolation, Kotlin internal visibility modifiers to encapsulate implementation details, and automated architectural linting rules via Konsist or ArchUnit in continuous integration to catch violations before merging.""",
    "structured_en": """Enforcing architectural boundaries does not require suffocating a codebase under ceremonial one-to-one boilerplate interfaces for every repository and helper class. Modern Android architecture relies on structural, compiler-enforced, and automated tooling mechanisms.
The primary mechanism is compiler-enforced Gradle module boundaries. By organizing the codebase into independent Gradle modules—such as feature modules, domain modules, and core database modules—the build graph enforces structural boundaries. If a developer attempts to call a Room database DAO directly from a feature ViewModel without an explicit Gradle dependency, the code fails to compile.
The second mechanism is Kotlin visibility modifiers. By marking concrete implementations, database entities, and network DTOs with the internal modifier, they remain strictly accessible within their declaring Gradle module. External modules cannot access internal types even if they declare a dependency on that module.
The third mechanism is automated architecture testing. Rather than relying on manual code reviews, teams write executable unit tests using Konsist or ArchUnit in CI. These tests automatically assert that ViewModels never import networking libraries and that repositories follow required conventions, providing ironclad architectural guardrails without redundant interface overhead.""",
    "deep_senior_en": """Under the hood, dogmatic adherence to one-to-one interfaces (such as CartRepository alongside CartRepositoryImpl) stems from legacy Java testing limitations where mocking required interfaces. In modern Kotlin and Android development, classes can be tested directly with lightweight fakes or instantiated concretely when design requirements do not involve multiple polymorphic implementations.
Relying solely on interfaces to enforce boundaries is often an illusion: a feature module can still import network DTOs through an interface if both reside in the same package. In contrast, compiler-level modularization provides hard physical guarantees. A Gradle module boundary is inviolable; code outside the module cannot see internal declarations, and missing dependencies halt the build pipeline instantly.
Furthermore, static analysis frameworks like Konsist revolutionize architectural governance. By parsing the Kotlin Abstract Syntax Tree (AST) directly within standard JUnit tests, Konsist allows engineers to write declarative assertions regarding package structures, class inheritance, import rules, and naming conventions.
For example, a five-line Konsist test can mandate that no class in the presentation layer may import anything from Retrofit or Room, and that all UseCases must reside in domain packages and expose exactly one public operator fun invoke.
Staff engineers replace ceremonial interface proliferation with this combination of module boundaries, internal visibility, and automated AST checks, keeping codebases concise, clean, and architecturally disciplined.""",
    "meta_ar": {
        "id": "ARC-26",
        "questionAr": "كيف تفرض حدود المعمارية بصرامة دون الغرق في أطنان من الـ Boilerplate Interfaces؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على حوكمة المعمارية البرمجية، وفهم حدود الـ Gradle Modules الصارمة، واستخدام Kotlin Visibility Modifiers (`internal`)، وتطبيق Architecture Testing باستخدام Konsist أو ArchUnit.",
        "why_it_matters_ar": "كتابة واجهة لكل كلاس في التطبيق يضاعف عدد الملفات ويرهق الفريق، بينما غياب الحدود يسبب تسريب التبعيات وتشابك الكود.",
        "worked_example_ar": "فرض القواعد آلياً عبر اختبارات Konsist:\n```kotlin\nclass ArchitectureTest {\n    @Test fun noRoomInViewModels() {\n        Konsist.scopeFromProject().classes().withNameEndingWith(\"ViewModel\").assertNot {\n            it.hasImportWithText { imp -> imp.startsWith(\"androidx.room\") }\n        }\n    }\n}\n```",
        "trade_offs_ar": "الاعتماد على Gradle Modules واختبارات Konsist يوفر كوداً نظيفاً بدون واجهات عقيمة، لكنه يتطلب ضبط إعدادات الـ Build Graph وقواعد الفحص في CI.",
        "failure_modes_ar": "كتابة واجهات شكلية لكل كلاس مع استمرار تسريب كائنات الـ DTO عبر تلك الواجهات، مما يفشل الهدف الحقيقي من الحدود المعمارية.",
        "production_perspective_ar": "في المشروعات الكبرى، نفرض حدود المعمارية عبر الـ Compiler في Gradle واختبارات Konsist في الـ Pull Requests لمنع أي تجاوزات برمجية دون إجهاد الفريق بكتابة Interfaces زائدة.",
        "how_to_answer_ar": "وضح أن الواجهات ليست الطريقة الوحيدة؛ واشرح ثلاثة بدائل أقوى: عزل الـ Gradle Modules، واستخدام `internal` في كوتلن، وأتمتة الفحص عبر Konsist في CI.",
        "talking_points_ar": "حدود الـ Gradle Compiler، والتعليق `internal`، ومكتبة Konsist لفحص الـ AST، وتجنب فخ الـ 1:1 Interface Dogma.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر إنشاء Interface لكل كلاس مجرد عادة قديمة غير ضرورية أحياناً؟\"\n  **المرشح:** \"لأنها كانت ضرورية في جافا القديمة لعمل Mocking في التيست؛ لكن في كوتلن بنقدر نعمل Fakes أو نختبر الكلاسات مباشرة، وكتابة واجهة لكل كلاس بدون تعدد استخدامات بيضاعف عدد الملفات بدون قيمة حقيقية.\"\n\n- **المحاور:** \"كيف تمنع الـ ViewModel من استدعاء كود الـ Database بدون استخدام Interfaces؟\"\n  **المرشح:** \"بوضع الـ Database في Gradle Module منفصل وجعل الكلاسات `internal`؛ فلو الـ ViewModel حاول يستورد كلاس من موديول الـ DB، الكومبايلر هيرفض يترجم الكود فوراً لأن الموديول مش مضاف في التبعيات.\"",
        "self_check_ar": "هل انتقدت فكرة الواجهة لكل كلاس؟ هل شرحت عزل الموديولات في Gradle؟ وهل بينت استخدام `internal` واختبارات Konsist؟",
        "references_ar": f"- [Konsist: Architecture Linter for Kotlin](https://docs.konsist.lemonappdev.com/) — التوثيق الرسمي لأداة فحص المعمارية في كوتلن.\n- [Modularization boundaries](https://developer.android.com/topic/modularization/patterns) — أنماط تقسيم الموديولات وفرض الحدود المعمارية في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنفرض حدود المعمارية بصرامة بدون إغراق المشروع في واجهات عقيمة بالاعتماد على ثلاث ركائز حديثة: عزل الموديولات في Gradle بحيث يمنع الكومبايلر أي استيراد غير مسموح به، واستخدام كلمة `internal` في كوتلن لإخفاء تفاصيل التنفيذ داخل الموديول، وكتابة اختبارات معمارية آلية باستخدام Konsist في الـ CI للتحقق من عدم استيراد الـ ViewModels لأي كود قاعدة بيانات أو شبكة.",
        "best_answer_ar": "فرض الحدود المعمارية مش معناه خنق المشروع بكتابة Interface لكل كلاس في التطبيق كطقس روتيني عقيم (1:1 Interface Dogma). الهندسة الحديثة في أندرويد بتعتمد على آليات هيكلية وأدوات أتمتة صارمة.\n\nالآلية الأولى والأقوى هي فرض الحدود عبر الـ Gradle Compiler؛ فلما نقسم المشروع لموديولات مستقلة زي موديولات الميزات وموديول الـ Database، الكومبايلر نفسه بيتحول لشرطي بيمنع التجاوزات. فلو مطور حاول يستورد Room DAO داخل ViewModel في موديول مبيعتمدش على قاعدة البيانات، الكود مش هيتبني أصلاً.\n\nالآلية التانية هي استخدام محددات الرؤية في كوتلن وتحديداً كلمة `internal`؛ بحيث نخلي كلاسات الـ DAO والـ DTOs والتحويلات مخفية داخل الموديول، ونكشف فقط نقطة الدخول العامة، فيستحيل على الموديولات الخارجية الوصول لتفاصيل التنفيذ.\n\nوالآلية التالتة هي أتمتة فحص المعمارية عبر اختبارات Konsist أو ArchUnit في الـ CI؛ دي اختبارات Unit Tests عادية بتفحص كود المشروع وتتأكد إن مفيش أي ViewModel بيستورد Retrofit أو Room، وإن كل UseCase موجود في طبقة Domain، وبكده بنفرض حوكمة صارمة بدون أي واجهات زائدة.",
        "deep_answer_ar": "تحت الكابوت، الهوس بكتابة Interface لكل كلاس (زي CartRepo و CartRepoImpl) كان متوارثاً من قيود لغة جافا القديمة حيث كان الـ Mocking مستحيلاً بدون واجهات. في كوتلن وأندرويد الحديث، بنقدر نختبر الكلاسات الملموسة مباشرة عبر Fakes بسيطة طالما مفيش تعدد في التنفيذ (Polymorphism).\n\nالاعتماد على الواجهات وحدها لفرض الحدود بيكون وهمي في أحيان كتير؛ لأن المطور ممكن يستورد DTOs الشبكة من خلال الواجهة نفسها لو الاتنين في نفس الموديول. بينما التقسيم على مستوى الـ Gradle Modules بيوفر ضمانات فيزيائية حقيقية؛ لأن حدود الموديول غير قابلة للاختراق، وغياب التبعية في ملف build.gradle.kts بيوقف البناء في لحظتها.\n\nبالإضافة لده، أدوات فحص الـ AST زي Konsist أحدثت ثورة حقيقية في حوكمة المعمارية. عبر فحص شجرة الكود (Abstract Syntax Tree) في اختبارات JUnit عادية، بنقدر نكتب قواعد واضحة تعبر عن المعمارية.\n\nعلى سبيل المثال، اختبار Konsist من خمسة سطور يقدر يفرض إن ممنوع نهائياً على أي كلاس في Presentation يستورد أي شيء من Room أو Retrofit، وإن كل UseCase لازم يحتوي على دالة عامة واحدة فقط هي `operator fun invoke()`.\n\nالمهندسون الكبار بيستبدلوا فوضى الواجهات الزائدة بالمزيج ده: عزل الموديولات، واستخدام `internal`، واختبارات الـ AST الآلية، للحفاظ على كود نظيف وسريع وسهل الصيانة."
    }
}


def main():
    print(f"Elevating {len(DATA)} questions in ARC (ARC-19 to ARC-26)...")
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
    ee.save_topic_metadata("arc_19_26", {qid: d["meta_ar"] for qid, d in DATA.items()})

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
        print("\nAll 8 ARC questions (ARC-19 to ARC-26) successfully elevated and passed validation!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
