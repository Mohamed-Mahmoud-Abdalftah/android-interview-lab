#!/usr/bin/env python3
"""Generator for ARC-20 through ARC-26 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "arc.json"

ARC_20_26 = [
    {
        "id": "ARC-20",
        "arabic_explanation": (
            "كيف تختبر طبقات العرض (Presentation)، النطاق (Domain)، والبيانات (Data) بشكل مستقل ومعزول؟\n\n"
            "1. اختبار طبقة النطاق (Domain Layer Testing):\n   - **نوع الاختبار**: Pure JVM Unit Tests سريعة للغاية تعمل في أجزاء من الثانية دون أي محاكي.\n   - **الاستراتيجية**: اختبار الـ UseCases بحقن Fake Repositories في الـ Constructor مباشرة.\n   - **ما يتم التحقق منه**: قواعد البيزنس، العمليات الحسابية، استيفاء الشروط، واختبار المسارات البديلة (Happy path & Edge cases).\n\n"
            "2. اختبار طبقة البيانات (Data Layer Testing):\n   - **نوع الاختبار**: مزيج بين JVM Tests واختبارات تكامل (Integration Tests).\n   - **الاستراتيجية**:\n     * لاختبار الـ Repositories: حقن Fake DataSources أو استخدام MockWebServer لفحص استجابات الشبكة، واختبار قواعد المزامنة والـ Caching.\n     * لاختبار Room DAOs: استخدام SQLite In-Memory Database (`Room.inMemoryDatabaseBuilder`) للتحقق من سلامة استعلامات SQL ومعاملات الـ Foreign Keys.\n\n"
            "3. اختبار طبقة العرض (Presentation Layer Testing):\n   - **نوع الاختبار**: Unit Tests للـ ViewModels و Compose UI Tests للواجهات.\n   - **الاستراتيجية**:\n     * الـ ViewModel: اختبار انبعاثات الـ `StateFlow` باستخدام مكتبة Turbine و `StandardTestDispatcher`.\n     * الـ Composable: اختبار الشاشات الـ Stateless باستخدام `createComposeRule()` للتحقق من ظهور العناصر والنقر عليها."
        ),
        "practical_walkthrough": (
            "استراتيجية الاختبار المعزول لكل طبقة من الطبقات الثلاث:\n"
            "```kotlin\n"
            "// 1. DOMAIN TEST: اختبار UseCase كود كوتلن نقي بدون أي أندرويد:\n"
            "class CalculateCartTotalUseCaseTest {\n"
            "    private val useCase = CalculateCartTotalUseCase()\n"
            "    @Test\n"
            "    fun whenCartHasTwoItems_calculatesTotalCorrectly() {\n"
            "        val items = listOf(CartItem(\"1\", 2, 1000L), CartItem(\"2\", 1, 500L))\n"
            "        assertEquals(2500L, useCase(items))\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. DATA TEST: اختبار Repository باستخدام Fake DataSources:\n"
            "class UserRepositoryTest = runTest {\n"
            "    private val fakeDao = FakeUserDao()\n"
            "    private val fakeApi = FakeUserApi()\n"
            "    private val repo = UserRepositoryImpl(fakeDao, fakeApi)\n"
            "\n"
            "    @Test\n"
            "    fun whenNetworkSucceeds_writesToLocalDatabase() = runTest {\n"
            "        fakeApi.stubUser = UserDto(id = \"1\", name = \"Alice\")\n"
            "        repo.refreshUser(\"1\")\n"
            "        assertEquals(\"Alice\", fakeDao.getUser(\"1\")?.name)\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. PRESENTATION TEST: اختبار ViewModel باستخدام Turbine:\n"
            "class CartViewModelTest {\n"
            "    @Test\n"
            "    fun loadCart_emitsLoadingThenSuccess() = runTest {\n"
            "        val fakeRepo = FakeCartRepository(initialItems = listOf(CartItem(\"1\", 1, 100L)))\n"
            "        val vm = CartViewModel(fakeRepo, CalculateCartTotalUseCase())\n"
            "        vm.uiState.test {\n"
            "            assertEquals(CartUiState.Loading, awaitItem())\n"
            "            val success = awaitItem() as CartUiState.Success\n"
            "            assertEquals(100L, success.total)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test Domain independently using pure JVM unit tests with Fake Repositories to verify business rules. Test Data using Fake DataSources or MockWebServer for repositories, and In-Memory Room databases for DAOs. Test Presentation using Turbine and TestDispatchers for ViewModels, and `createComposeRule()` for UI composables.",
        "best_answer": (
            "Architectural layering enables independent, deterministic test suites without brittle end-to-end integration dependencies.\n\n"
            "1. **Domain Layer Testing**:\n"
            "   - **Environment**: Pure JVM tests running in milliseconds.\n"
            "   - **Methodology**: Instantiate Use Cases directly. Inject lightweight in-memory Fake Repositories. Assert business rule calculations, edge-case thresholds, and domain error flows without mock frameworks.\n\n"
            "2. **Data Layer Testing**:\n"
            "   - **Repositories**: Tested via Fake Remote DataSources and Fake DAOs. Verify that repository logic correctly coordinates caching, writes network responses into the database, and maps DTOs into domain models.\n"
            "   - **DAOs**: Tested via `Room.inMemoryDatabaseBuilder()` in JVM tests (via Robolectric) or instrumented tests to verify SQL queries, table relations, and foreign key cascades.\n\n"
            "3. **Presentation Layer Testing**:\n"
            "   - **ViewModels**: Tested via `runTest`, `StandardTestDispatcher`, and Cash App's **Turbine**. Assert that repository emissions produce the exact sequence of `UiState` snapshots.\n"
            "   - **Composables**: Tested via `createComposeRule()` on pure stateless screen composables, asserting semantic trees and user interactions."
        ),
        "deep_answer": (
            "The overarching principle is preferring **Fakes over Mocks**. "
            "Mocking libraries (Mockito/MockK) record interactions (`verify { repo.call() }`), which tightly couples tests to implementation details and makes refactoring brittle. "
            "In contrast, a `FakeUserRepository` implements the `UserRepository` interface backed by a simple in-memory `MutableStateFlow` or `HashMap`. "
            "Tests verify visible outcomes (the state changes) rather than whether a specific method was invoked, dramatically increasing test resilience.\n\n"
            "Furthermore, because Domain and ViewModel tests have zero Android Gradle plugin dependencies, an entire enterprise test suite of 3,000+ tests runs in under 15 seconds in CI, providing immediate developer feedback."
        ),
        "follow_ups": [
            {
                "question": "Why use In-Memory Room databases instead of mocking DAOs?",
                "answer": "Mocking DAOs tests your mock configuration, not your SQL. An In-Memory Room database executes real SQLite queries against the schema, verifying migrations, SQL syntax, and constraint violations accurately."
            },
            {
                "question": "Why should tests prefer Fakes over Mocks?",
                "answer": "Fakes provide realistic in-memory behavior, withstand internal refactorings, avoid brittle interaction verifications, and run significantly faster than dynamic mock proxies."
            }
        ]
    },
    {
        "id": "ARC-21",
        "arabic_explanation": (
            "كيف تقوم بإعادة هيكلة (Refactoring) كلاس ViewModel ضخم يحتوي على 1,000 سطر يجمع بين الشبكة، الـ Mapping، ومنطق البيزنس بشكل تدريجي وآمن؟\n\n"
            "1. استراتيجية الـ Strangler Fig Pattern (التفكيك التدريجي دون إيقاف التطوير):\n   - إياك أن تعيد كتابة الـ ViewModel من الصفر في فرع منفصل (Big Bang Rewrite)؛ هذا يؤدي إلى كوارث دمج ومشاكل لا تنتهي.\n   - نقوم بإعادة الهيكلة بخطوات جراحية تدريجية في عدة PRs صغيرة ومختبرة.\n\n"
            "2. خطوات إعادة الهيكلة خطوة بخطوة:\n   - **الخطوة 1: كتابة Characterization Tests (شبكة أمان)**:\n     * قبل كتابة سطر كود، اكتب اختبارات للـ ViewModel القديم تلتقط سلوكه الحالي بالكامل (حتى أخطائه) لضمان عدم كسر أي شيء.\n   - **الخطوة 2: استخراج طبقة البيانات (Extract Data Layer)**:\n     * سحب استدعاءات Retrofit و SharedPreferences والـ DTO Mappings ووضعها داخل `FeatureRepositoryImpl` خلف `Interface`.\n   - **الخطوة 3: استخراج منطق العمليات المعقدة إلى Use Cases**:\n     * عزل الحسابات والتحققات الضخمة داخل UseCases مخصصة (`ValidateOrderUseCase`, `CalculateShippingUseCase`).\n   - **الخطوة 4: توحيد الـ UI State**:\n     * دمج الـ 10 متغيرات LiveData/StateFlow المتفرقة في كائن `data class ScreenUiState` واحد.\n   - **الخطوة 5: تنظيف الـ ViewModel ليصبح مجرد Coordinator نحيف (Thin ViewModel)**."
        ),
        "practical_walkthrough": (
            "نموذج تحويل تدريجي لـ ViewModel ضخم:\n"
            "```kotlin\n"
            "// المرحلة 1: الـ ViewModel القديم (1000 سطر يجمع كل شيء):\n"
            "class MonolithicCartViewModel : ViewModel() {\n"
            "    // استدعاء شبكة مباشر، وحسابات أسعار، وSharedPreferences وUI State!\n"
            "}\n"
            "\n"
            "// المرحلة 2: سحب الـ Networking والـ Storage إلى Repository:\n"
            "class CartRepositoryImpl(private val api: CartApi, private val prefs: CartPrefs) : CartRepository { ... }\n"
            "\n"
            "// المرحلة 3: سحب العمليات المعقدة إلى Use Cases:\n"
            "class ValidateCartUseCase(private val inventoryRepo: InventoryRepository) { ... }\n"
            "class ApplyPromoCodeUseCase(private val promoRepo: PromoRepository) { ... }\n"
            "\n"
            "// المرحلة 4: الـ ViewModel النظيف الناتج (أقل من 80 سطراً):\n"
            "@HiltViewModel\n"
            "class CleanCartViewModel @Inject constructor(\n"
            "    private val cartRepository: CartRepository,\n"
            "    private val validateCart: ValidateCartUseCase,\n"
            "    private val applyPromo: ApplyPromoCodeUseCase\n"
            ") : ViewModel() {\n"
            "    val uiState: StateFlow<CartUiState> = cartRepository.observeCart()\n"
            "        .map { CartUiState.Success(it) }\n"
            "        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), CartUiState.Loading)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Refactor a 1,000-line ViewModel incrementally using the Strangler Fig pattern: write baseline characterization tests, extract network and database calls into a Repository, extract heavy business rules into dedicated Use Cases, consolidate scattered state variables into a single immutable `UiState`, and verify zero behavior regression at each PR.",
        "best_answer": (
            "Refactoring a monolithic 1,000-line ViewModel requires a surgical, incremental migration strategy without halting feature delivery.\n\n"
            "1. **Step 1: Characterization Testing**: Before modifying code, write baseline unit tests against the existing ViewModel. Capture its current inputs, outputs, and side-effects. This provides a safety net guaranteeing that subsequent extractions cause zero behavioral regressions.\n\n"
            "2. **Step 2: Extract Data Access into a Repository**: Identify raw Retrofit calls, Room DAO queries, and SharedPreferences accesses. Move them into a concrete `FeatureRepositoryImpl` behind a clean interface. Inject the repository into the ViewModel. The ViewModel now consumes repository methods, shedding hundreds of lines of HTTP configuration and mapping.\n\n"
            "3. **Step 3: Extract Domain Rules into Use Cases**: Identify dense business calculations (validation algorithms, discount computations, cross-repository logic). Extract each calculation into a dedicated, single-responsibility Use Case with pure JVM unit tests.\n\n"
            "4. **Step 4: Consolidate State**: Migrate scattered `LiveData` variables (`isLoading`, `user`, `error`, `items`) into a single consolidated `StateFlow<ScreenUiState>`.\n\n"
            "Ship each step as an independent, fully tested Pull Request."
        ),
        "deep_answer": (
            "The cardinal mistake in legacy refactoring is attempting a **Big Bang Rewrite** in an isolated branch for weeks. "
            "By the time the branch is ready, main branch merge conflicts are insurmountable, subtle production bugs are introduced, and business stakeholders are frustrated by halted feature velocity.\n\n"
            "Using the **Strangler Fig pattern**, the legacy ViewModel delegates portions of its work to new clean components while continuing to serve production traffic. "
            "At any point during the multi-sprint refactoring, the application builds, tests pass, and features remain deployable.\n\n"
            "Once all responsibilities are delegated, the legacy ViewModel collapses from 1,000 lines down to a lightweight 60-80 line coordinator whose only job is holding `uiState` and binding user gestures to Use Cases."
        ),
        "follow_ups": [
            {
                "question": "What is a Characterization Test?",
                "answer": "A test written to characterize the current behavior of legacy code as it actually exists, creating a baseline safety net so future refactoring does not alter existing functionality."
            },
            {
                "question": "How do you avoid merge conflicts during a long refactoring project?",
                "answer": "By breaking refactorings into small, bite-sized PRs (extracting one repository or use case at a time) and merging directly to the main trunk behind feature flags if necessary."
            }
        ]
    },
    {
        "id": "ARC-22",
        "arabic_explanation": (
            "عندما يقوم الـ Repository بإرجاع كائن API DTO مباشرة إلى Jetpack Compose: ما هي مخاطر الارتباط (Coupling Risks) المترتبة على ذلك؟\n\n"
            "1. تسريب تفاصيل الشبكة والسيرفر إلى طبقة العرض (Infrastructure Leaks):\n   - الـ DTO مصمم ليطابق بنية JSON القادمة من السيرفر.\n   - إذا اعتمد الـ Composable على `UserDto` مباشرة:\n     * أي تغيير بسيط في الـ API من قبل فريق الـ Backend (مثل تغيير اسم حقل، تحويل حقل إلى Array، أو حذفه) سيكسر ملفات الـ UI والـ Compose Layouts فوراً!\n\n"
            "2. تدهور أداء وسلاسة Jetpack Compose (Performance & Stability Degradation):\n   - كائنات الـ DTO غالباً ما تحوي حقولاً غير مستقرة، أو حقول Nullable متعددة تتطلب فحوصات `if (dto.data != null)` متكررة داخل الـ Composable.\n   - كما تضطر دالة الـ Composable لحساب وتنسيق النصوص والتواريخ في كل فريم (Jank Risk) بدلاً من استقبال نصوص جاهزة محسوبة مسبقاً.\n\n"
            "3. استحالة عمل Offline Caching ومصادر بيانات متعددة:\n   - الـ DTO يمثل استجابة HTTP فقط. إذا أردت جلب البيانات من Room أو Bluetooth، فلن تتوافق الكائنات، مما يدمر فكرة الـ Single Source of Truth."
        ),
        "practical_walkthrough": (
            "تصحيح تسريب الـ DTO وفصل النماذج عبر طبقة وسيطة:\n"
            "```kotlin\n"
            "// ❌ كارثة ارتباط: Composable يعتمد مباشرة على Retrofit DTO:\n"
            "@Composable\n"
            "fun BadUserBadge(userDto: UserNetworkDto) { // تسريب كائن الشبكة للـ UI!\n"
            "    // فحص nulls مستمر وتنسيق تواريخ مكلف داخل الـ Composable:\n"
            "    val formattedDate = SimpleDateFormat(\"yyyy-MM-dd\").format(Date(userDto.timestamp ?: 0L))\n"
            "    Text(\"${userDto.first_name} ${userDto.last_name} - $formattedDate\")\n"
            "}\n"
            "\n"
            "// ✅ كود سليم: فصل تام بنماذج UI نقية ومستقرة:\n"
            "@Immutable\n"
            "data class UserBadgeUiModel(\n"
            "    val fullName: String,\n"
            "    val formattedJoinedDate: String\n"
            ")\n"
            "\n"
            "@Composable\n"
            "fun GoodUserBadge(user: UserBadgeUiModel) {\n"
            "    // عرض نقي وفوري بدون أي null checks أو حسابات ثقيلة:\n"
            "    Text(\"${user.fullName} - ${user.formattedJoinedDate}\")\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Returning API DTOs directly to Compose tightly couples the UI to backend API schema changes, causes stability issues and recomposition jank from unformatted data and nullable fields, eliminates offline database caching, and prevents isolated UI testing.",
        "best_answer": (
            "Allowing API DTOs to cross the repository boundary into Jetpack Compose is a severe architectural smell with immediate stability and maintenance risks.\n\n"
            "1. **Backend Volatility Spilling into UI**: DTOs are volatile models dictated by server API schemas. If the backend team refactors a field (e.g. from `userName` to `user_handle` or wraps an object in an envelope), that network modification immediately breaks Composable layout files and UI tests across the app.\n\n"
            "2. **Compose Performance & Stability Degradation**: DTO classes are not optimized for Compose smart skipping. They often contain mutable properties, standard collections (`List<T>`), or unvalidated nullables, forcing composables to become unskippable and re-render unnecessarily.\n\n"
            "3. **In-Composition Formatting Overhead**: When using raw DTOs, composable functions are forced to format currency, parse ISO dates, and concatenate strings inside the composition pass, creating memory churn and dropped frames during 120fps scrolling.\n\n"
            "4. **Destruction of Offline-First Architecture**: An API DTO represents HTTP traffic. It cannot unify data with Room database entities or in-memory caches, sabotaging Single Source of Truth architecture."
        ),
        "deep_answer": (
            "Under the hood, DTOs prioritize **deserialization ergonomics** (e.g. `@SerialName`, `@JsonClass`, nullable default fallbacks). "
            "In contrast, Compose UI models prioritize **rendering efficiency and immutability** (e.g. `@Immutable`, pre-calculated `AnnotatedString`s, localized string resources).\n\n"
            "The repository's explicit contractual duty is to map raw DTOs into Domain Entities. "
            "The ViewModel then maps Domain Entities into specialized, immutable `UiModel`s. "
            "This insulation allows the backend schema to undergo major revisions while the Composable UI remains 100% stable, untouched, and fully functional."
        ),
        "follow_ups": [
            {
                "question": "What happens to Compose skipping when a DTO class is modified?",
                "answer": "DTO classes from network libraries typically lack Compose stability annotations, making composables that accept them unskippable and forcing full recompositions on parent invalidations."
            },
            {
                "question": "Where should the transformation from DTO to UI model take place?",
                "answer": "DTO to Domain model occurs in the Data layer (Repository). Domain model to UI model occurs in the Presentation layer (ViewModel or Presentation Mapper)."
            }
        ]
    },
    {
        "id": "ARC-23",
        "arabic_explanation": (
            "لديك تطبيق صغير وبسيط جداً: متى تصبح معمارية Clean Architecture زيادة هندسية غير مبررة (Overengineering)؟\n\n"
            "1. متى تكون Clean Architecture عبئاً وضاراً (Overengineering)؟\n   - **تطبيقات الـ CRUD البسيطة (Single-purpose CRUD / Utilities)**: تطبيق مصباح (Flashlight)، تطبيق آلة حاسبة، أو تطبيق يعرض قائمة مقالات من API واحد بدون قاعدة بيانات محلية وبدون قواعد بيزنس.\n   - **التطبيق الصغير ذو المطور الواحد (Solo MVP)**: حيث تكون الأولوية القصوى هي سرعة الإطلاق واختبار السوق (Time-to-Market).\n   - **أعراض الـ Overengineering في التطبيقات الصغيرة**:\n     * إنشاء 4 موديلات مختلفة لكل كائن (DTO, Entity, Domain, UI Model).\n     * إنشاء عشرات الـ UseCases التي لا تفعل شيئاً سوى تمرير الاستدعاء (`repo.call()`).\n     * تقسيم المشروع إلى 8 موديولات Gradle مختلفة لتطبيق يحتوي على شاشتين فقط!\n\n"
            "2. ما هي المعمارية البديلة الأنسب للتطبيقات الصغيرة؟\n   - **Pragmatic MVVM (Simple Architecture)**:\n     * طبقتان فقط: **Presentation Layer** (Composables + ViewModel) و **Data Layer** (Repository + Retrofit/Room).\n     * لا داعي لطبقة Domain ولا UseCases؛ الـ ViewModel يتصل بالـ Repository مباشرة.\n     * نموذج بيانات موحد أو مابينج بسيط جداً.\n\n"
            "3. متى ننتقل إلى Clean Architecture الكاملة؟\n   - فقط عندما يبدأ التطبيق في النمو: عند إضافة قواعد بيزنس معقدة، تعدد الشاشات التي تشارك نفس العمليات، أو انضمام فريق من المطورين."
        ),
        "practical_walkthrough": (
            "المقارنة بين المعمارية البراغماتية المناسبة لتطبيق صغير والمعمارية المفرطة:\n"
            "```kotlin\n"
            "// ❌ OVERENGINEERING لتطبيق بسيط: 5 طبقات وبويلربليت ضخم لمجرد عرض قائمة مدن:\n"
            "// CityDto -> CityEntity -> CityDomain -> CityUiModel\n"
            "// CityApi -> CityDao -> CityRepositoryInterface -> CityRepositoryImpl -> GetCitiesUseCase -> CityViewModel\n"
            "\n"
            "// ✅ PRAGMATIC MVVM (معمارية بسيطة وسريعة وممتازة للتطبيقات الصغيرة):\n"
            "// 1. Data Layer: Repository مباشر بدون Interfaces معقدة:\n"
            "class WeatherRepository(private val api: WeatherApi) {\n"
            "    suspend fun getWeather(city: String): WeatherInfo = api.fetchWeather(city).toWeatherInfo()\n"
            "}\n"
            "\n"
            "// 2. Presentation Layer: ViewModel يتصل بالـ Repository مباشرة:\n"
            "class WeatherViewModel(private val repository: WeatherRepository) : ViewModel() {\n"
            "    val uiState = MutableStateFlow<WeatherInfo?>(null)\n"
            "    fun load(city: String) = viewModelScope.launch {\n"
            "        uiState.value = repository.getWeather(city)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Clean Architecture is overengineering for small apps or simple CRUD utilities with no complex business rules. Forcing separate Domain layers, passthrough Use Cases, multiple mappers, and multi-module splits slows delivery and adds cognitive overhead. Pragmatic MVVM (UI directly consuming Repositories) is the recommended pragmatic architecture.",
        "best_answer": (
            "Architecture is an economic trade-off: abstractions buy decoupling and maintainability at the expense of complexity, file count, and development velocity.\n\n"
            "In small applications (e.g. proof-of-concept MVPs, single-developer tools, simple display apps with no offline sync or complex calculations), full Clean Architecture is textbook **overengineering**.\n\n"
            "The warning signs of overengineering in small projects include:\n"
            "1. **Passthrough Use Cases**: Every Use Case consists of a single line: `invoke() = repo.getData()`.\n"
            "2. **Mapping Exhaustion**: Converting `NewsDto` -> `NewsEntity` -> `NewsDomain` -> `NewsUiModel` when all four classes contain identical properties.\n"
            "3. **Micro-Modularization Overhead**: Splitting a 5-screen app into 12 Gradle modules, multiplying build setup times for zero architectural gain.\n\n"
            "In such scenarios, senior engineers adopt **Pragmatic MVVM**: ViewModels consume concrete Repositories directly, sharing concise data models while retaining reactive state flows."
        ),
        "deep_answer": (
            "Architecture should be **evolutionary, not speculative** (YAGNI - You Aren't Gonna Need It). "
            "Starting with a pragmatic two-tier architecture (Presentation and Data) does not prevent adopting Clean Architecture later. "
            "Because code is properly decoupled at the ViewModel-Repository boundary, extracting a Domain layer and Use Cases takes mere hours once true business complexity or multi-screen logic emerges.\n\n"
            "Google's modern architecture documentation reinforces this pragmatism: the Domain layer is officially documented as optional. "
            "A senior engineer's value lies not in applying the maximum possible abstractions, but in applying the minimum abstractions necessary to satisfy current requirements and near-term maintainability."
        ),
        "follow_ups": [
            {
                "question": "What is the YAGNI principle in software architecture?",
                "answer": "'You Aren't Gonna Need It'—the principle that software engineers should not add functionality or architectural abstractions until they are deemed genuinely necessary."
            },
            {
                "question": "How do you transition from Pragmatic MVVM to Clean Architecture when the app grows?",
                "answer": "Extract business logic from ViewModels into newly created Use Cases, introduce Domain entities where external DTOs must be decoupled, and insert Repository interfaces at the boundary."
            }
        ]
    },
    {
        "id": "ARC-24",
        "arabic_explanation": (
            "كيف تصمم حالة الحساب/الجلسة المشتركة (Cross-Feature Account/Session State) دون الوقوع في مشكلة التبعيات الدائرية (Circular Dependencies)؟\n\n"
            "1. معضلة التبعيات الدائرية في التطبيقات المقسمة لموديولات (Circular Dependencies):\n   - ميزة المدفوعات `:feature:payment` تحتاج لمعرفة بيانات الحساب النشط `:feature:account`.\n   - وميزة الحساب `:feature:account` تريد معرفة حالة الدفع واشتراك المستخدم من `:feature:payment`.\n   - في نظام Gradle، إذا اعتمد موديول A على B واعتمد B على A، يفشل البناء فوراً مع خطأ Circular Dependency!\n\n"
            "2. الحل المعماري القياسي: استخراج موديول مشترك في الطبقة الأساسية (Inversion via Core:User / Core:Session):\n   - **إنشاء وحدة مخصصة للـ Session في الـ Core Layer**: تسمى `:core:session` أو `:core:user`.\n   - هذا الموديول يقع في مستوى أدنى ويعتمد عليه كل من `:feature:payment` و `:feature:account`.\n   - يحتوي على:\n     * `data class UserSession(val userId: String, val authToken: String, val tier: AccountTier)`.\n     * `interface SessionRepository` توفر `val activeSession: StateFlow<UserSession?>`.\n\n"
            "3. إدارة أحداث تسجيل الخروج (Global Logout Handling):\n   - عند انتهاء الجلسة أو استلام HTTP 401 من أي طلب، يتم استدعاء `sessionRepository.clearSession()` في الـ Core.\n   - تستمع شاشة التنقل الرئيسية (Root NavHost) لهذا التدفق، وتقوم بإلغاء كل الشاشات والعودة فورياً لشاشة تسجيل الدخول."
        ),
        "practical_walkthrough": (
            "هيكلة Session State في Core Module مشترك دون أي تبعيات دائرية:\n"
            "```kotlin\n"
            "// 1. في module :core:session (موديول أساسي يعتمد عليه الجميع دون حلقات دائرية):\n"
            "data class UserSession(val userId: String, val token: String, val isPremium: Boolean)\n"
            "\n"
            "interface SessionRepository {\n"
            "    val sessionFlow: StateFlow<UserSession?>\n"
            "    suspend fun updateSession(session: UserSession)\n"
            "    suspend fun terminateSession()\n"
            "}\n"
            "\n"
            "// 2. في module :feature:payment (يعتمد على :core:session فقط):\n"
            "class PaymentViewModel @Inject constructor(\n"
            "    private val sessionRepository: SessionRepository\n"
            ") : ViewModel() {\n"
            "    fun verifyUserCanPay() {\n"
            "        val currentSession = sessionRepository.sessionFlow.value\n"
            "        // التحقق من الجلسة دون أي اعتماد على موديول :feature:account!\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. في module :app أو Root Navigation (مراقبة الجلسة والتوجيه العام):\n"
            "@Composable\n"
            "fun RootAppNav(sessionRepository: SessionRepository) {\n"
            "    val session by sessionRepository.sessionFlow.collectAsStateWithLifecycle()\n"
            "    if (session == null) {\n"
            "        LoginNavGraph() // إذا انتهت الجلسة ننتقل لشاشة تسجيل الدخول تلقائياً\n"
            "    } else {\n"
            "        MainAppNavGraph()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design cross-feature session state by hoisting it into a lower-level `:core:session` or `:core:user` module that feature modules depend on unidirectionally. Expose an immutable `StateFlow<UserSession?>` from a singleton `SessionRepository`, preventing circular Gradle dependencies and enabling global reactive logout handling.",
        "best_answer": (
            "Managing cross-cutting account and session state across features without inducing circular dependencies requires strict architectural layering.\n\n"
            "1. **The Core Session Inversion Pattern**:\n"
            "   - Features (`:feature:checkout`, `:feature:settings`, `:feature:chat`) must never depend on each other horizontally.\n   - Instead, we hoist identity and session contracts into a dedicated foundational module: **`:core:session`** (or `:core:model`).\n   - `:core:session` has zero feature dependencies. All feature modules depend unidirectionally downward onto `:core:session`.\n\n"
            "2. **Reactive Session Repository**:\n   - Inside `:core:session`, a singleton `SessionRepository` manages active authentication credentials, exposing `val activeSession: StateFlow<UserSession?>`.\n   - Feature ViewModels inject `SessionRepository` to inspect user identity or observe permission changes.\n\n"
            "3. **Global Session Invalidation (401 Handling)**:\n   - An OkHttp Authenticator in `:core:network` catches HTTP 401 Unauthorized responses. It calls `sessionRepository.clearSession()`.\n   - The top-level `RootNavHost` in the `:app` module observes `activeSession`. When nullified, it tears down active feature graphs and routes immediately to authentication."
        ),
        "deep_answer": (
            "Under the hood, in Gradle multi-module builds, circular dependencies (`:feature:A -> :feature:B -> :feature:A`) cause fatal compilation graph cycles. "
            "By applying the **Dependency Inversion Principle**, if Feature A needs to trigger an action in Feature B (e.g. Payment completed, navigate to Order History in Account), Feature A must **never import Feature B directly**.\n\n"
            "Instead, we use **API/Impl splits** or **Event/Navigation Hoisting**:\n"
            "- Feature A exposes an output navigation lambda: `onPaymentSuccess: (OrderId) -> Unit`.\n"
            "- The top-level orchestration module (`:app`), which knows both `:feature:payment` and `:feature:account`, wires the navigation call from Payment to Account.\n\n"
            "This preserves complete compilation independence: the payment team can build and test `:feature:payment` in total isolation without compiling the account module."
        ),
        "follow_ups": [
            {
                "question": "What is the role of the `:app` module in feature navigation?",
                "answer": "The `:app` module sits at the top of the dependency graph and depends on all feature modules. It wires navigation flows between features, keeping feature modules decoupled from one another."
            },
            {
                "question": "How do you handle OkHttp token refresh without circular DI dependencies?",
                "answer": "Provide a specialized `TokenProvider` interface in `:core:network` implemented by `:core:session`, or use a custom OkHttp Interceptor/Authenticator injected via Dagger/Hilt."
            }
        ]
    },
    {
        "id": "ARC-25",
        "arabic_explanation": (
            "المقارنة بين MVVM و MVI عند بناء آلة حالات للدفع (Payment State Machine) تحتوي على العديد من التحولات والحالات المعقدة:\n\n"
            "1. طبيعة تدفق الدفع (Payment Flow Complexity):\n   - عمليات الدفع والـ Fintech حساسة للغاية وتحتوي على العديد من الحالات المعقدة: `Idle -> ValidatingCard -> 3DSecureChallenge -> Authorizing -> CapturePending -> Success` أو `Declined / Retrying / BiometricRequired`.\n   - أي تضارب أو حدوث سباق بيانات (Race Condition) قد يتسبب في خصم المبلغ مرتين من العميل!\n\n"
            "2. عيوب MVVM في تدفقات الدفع المعقدة:\n   - في MVVM التقليدي، يميل المطورون لإنشاء عدة متغيرات منفصلة: `isProcessing`, `is3DSecureActive`, `paymentError`, `isSuccess`.\n   - **خطر التضارب الكبير**: يمكن للمستخدم الضغط على زر الدفع مرتين بسرعة، فتتداخل الحالات وتحدث انتقالات غير قانونية (Illegal State Transitions).\n\n"
            "3. لماذا يتفوق MVI بشكل كاسح في سيناريوهات الدفع؟\n   - **آلة حالات قطعية وصارمة (Deterministic Finite State Machine)**:\n     * الحالة عبارة عن `sealed interface PaymentState` واحدة غير قابلة للتجزئة.\n     * التحولات تتم حصرياً عبر كائن **Reducer**: `reduce(currentState, paymentIntent) -> newState`.\n     * إذا استلم الـ Reducer حدث `SubmitPayment` وكانت الحالة الحالية `Authorizing`، يتجاهل الـ Reducer الحدث فورياً ويستحيل تكرار المعاملة!\n   - سهولة الاختبار الخارق: كل انتقال في الـ State Machine يمكن اختباره كـ Pure Function رياضية."
        ),
        "practical_walkthrough": (
            "تنفيذ Payment State Machine بأسلوب MVI المحكم المانع للانتقالات غير القانونية:\n"
            "```kotlin\n"
            "// 1. الحالات المتبادلة حصرياً لعملية الدفع:\n"
            "sealed interface PaymentState {\n"
            "    data object Idle : PaymentState\n"
            "    data object Authorizing : PaymentState\n"
            "    data class Requires3DSecure(val challengeUrl: String) : PaymentState\n"
            "    data class Success(val transactionId: String) : PaymentState\n"
            "    data class Failed(val error: PaymentError, val canRetry: Boolean) : PaymentState\n"
            "}\n"
            "\n"
            "// 2. الأحداث الصادرة من المستخدم أو النظام:\n"
            "sealed interface PaymentIntent {\n"
            "    data class Authorize(val amountCents: Long, val cardId: String) : PaymentIntent\n"
            "    data class Complete3DSecure(val token: String) : PaymentIntent\n"
            "}\n"
            "\n"
            "// 3. الـ Reducer القطعي المانع للانتقالات غير القانونية:\n"
            "class PaymentViewModel : ViewModel() {\n"
            "    private val _state = MutableStateFlow<PaymentState>(PaymentState.Idle)\n"
            "    val state: StateFlow<PaymentState> = _state.asStateFlow()\n"
            "\n"
            "    fun processIntent(intent: PaymentIntent) {\n"
            "        val current = _state.value\n"
            "        when (intent) {\n"
            "            is PaymentIntent.Authorize -> {\n"
            "                // حماية تامة: لا يمكن بدء تفويض إذا كان هناك تفويض جارٍ!\n"
            "                if (current !is PaymentState.Idle && current !is PaymentState.Failed) return\n"
            "                _state.value = PaymentState.Authorizing\n"
            "                executePayment(intent.amountCents, intent.cardId)\n"
            "            }\n"
            "            is PaymentIntent.Complete3DSecure -> { ... }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "For a complex payment state machine, MVI decisively outperforms MVVM. MVVM's scattered multiple state streams risk illegal state combinations and race conditions (e.g. double-charging). MVI models transitions as a deterministic Finite State Machine (FSM) where a pure Reducer transitions a single immutable `PaymentState`, guaranteeing that invalid transitions are rejected.",
        "best_answer": (
            "For mission-critical workflows with dense state transitions—such as a fintech payment pipeline—**MVI is dramatically superior to MVVM**.\n\n"
            "1. **The Fragility of MVVM in High-Stakes Flows**:\n"
            "   - In standard MVVM, state is often scattered across multiple observable properties: `isPaying`, `challengeActive`, `error`, `success`.\n"
            "   - This creates an illegal state vulnerability: rapid user taps or unexpected network retries can place the ViewModel into an indeterminate state where `isPaying = true` and `error != null` coexist, causing race conditions or duplicate transactions.\n\n"
            "2. **The Rigor of MVI as a Finite State Machine (FSM)**:\n"
            "   - MVI enforces a **Deterministic Finite State Machine**: states are modeled as a `sealed interface PaymentState` (`Idle`, `Authorizing`, `Challenge3DS`, `Success`, `Failed`).\n"
            "   - State transitions occur strictly through a **Reducer** taking `(CurrentState, Intent) -> NewState`.\n"
            "   - If an `AuthorizePayment` intent arrives while the state is already `Authorizing`, the reducer rejects the transition deterministically. Invalid states are structurally impossible.\n\n"
            "This mathematical determinism guarantees transaction safety and auditability in enterprise fintech applications."
        ),
        "deep_answer": (
            "Under the hood, implementing an enterprise payment FSM in MVI benefits from **State Transition Logging**. "
            "Because every state transition is a discrete pair of `(OldState, Intent) -> NewState`, we can attach an audit logger that streams state transitions directly to analytics/Datadog. "
            "If a customer experiences a payment drop, customer support can inspect the exact chronological state machine graph to identify where the flow halted.\n\n"
            "Furthermore, testing is exceptionally robust. "
            "Instead of verifying mocks, testing a payment reducer is a pure mathematical function test: `assertEquals(PaymentState.Authorizing, reducer.reduce(PaymentState.Idle, Intent.Authorize))`. "
            "We can run property-based testing across thousands of random intent combinations to mathematically prove that the state machine can never enter an illegal double-charge state."
        ),
        "follow_ups": [
            {
                "question": "What is a Reducer in MVI?",
                "answer": "A pure function that takes the current immutable state and an incoming intent/action, and returns a new immutable state without performing side-effects."
            },
            {
                "question": "How does MVI prevent double-submission on slow network connections?",
                "answer": "The reducer transitions the state to `Authorizing` on the first click. Any subsequent `Submit` intents arriving while in `Authorizing` state are explicitly discarded by the reducer."
            }
        ]
    },
    {
        "id": "ARC-26",
        "arabic_explanation": (
            "كيف تفرض وتضبط حدود المعمارية (Architectural Boundaries) بصرامة دون الغرق في أطنان من الواجهات العقيمة (Boilerplate Interfaces)؟\n\n"
            "1. المعضلة: Interface Boilerplate مقابل الحدود الرخوة (Loose Boundaries):\n   - يعتقد بعض المطورين أن الطريقة الوحيدة لفرض Clean Architecture هي كتابة `interface` لكل كلاس في التطبيق، مما يضاعف عدد الملفات ويصيب الفريق بالإرهاق (Interface Exhaustion).\n   - على الجانب الآخر، إلغاء الواجهات بالكامل يفتح الباب لتسريب التبعيات وتشابك الكود (Spaghetti Code).\n\n"
            "2. الحلول الهندسية الحديثة لفرض الحدود بذكاء:\n   - **فرض الحدود على مستوى الـ Gradle Modules (Compiler-Enforced Boundaries)**:\n     * تقسيم المشروع إلى موديولات مستقلة: `:feature:checkout` و `:core:data`.\n     * الـ Compiler هو الشرطي الذي يمنع التجاوز: يستحيل على كود الـ UI استدعاء كود الـ Database إذا لم يكن هناك `implementation(project(...))` في ملف `build.gradle.kts`!\n   - **استخدام الـ Kotlin Visibility Modifiers (`internal`)**:\n     * داخل الموديول، اجعل الكلاسات الملموسة `internal` واكشف فقط نقطة الدخول العامة.\n   - **أتمتة الفحص عبر Konsist / ArchUnit (Architecture Testing)**:\n     * كتابة اختبارات آلية تفحص قواعد المعمارية في CI/CD وتمنع دمج أي PR يخالف القواعد دون الحاجة لـ Interfaces يدوية في كل مكان!"
        ),
        "practical_walkthrough": (
            "فرض قواعد المعمارية آلياً باستخدام مكتبة Konsist في الـ Unit Tests:\n"
            "```kotlin\n"
            "// اختبار Konsist يعمل في CI للتحقق من أن الـ ViewModels لا تستورد Room أو Retrofit أبداً:\n"
            "class ArchitectureBoundaryTest {\n"
            "    @Test\n"
            "    fun viewModels_mustNotDependOn_dataOrNetwork() {\n"
            "        Konsist.scopeFromProject()\n"
            "            .classes()\n"
            "            .withNameEndingWith(\"ViewModel\")\n"
            "            .withoutName(\"ArchitectureBoundaryTest\")\n"
            "            .assertNot {\n"
            "                it.hasImportWithText { import ->\n"
            "                    import.startsWith(\"retrofit2\") ||\n"
            "                    import.startsWith(\"androidx.room\") ||\n"
            "                    import.contains(\".data.\")\n"
            "                }\n"
            "            }\n"
            "    }\n"
            "\n"
            "    @Test\n"
            "    fun useCases_mustHaveSinglePublicMethod_invoke() {\n"
            "        Konsist.scopeFromProject()\n"
            "            .classes()\n"
            "            .withNameEndingWith(\"UseCase\")\n"
            "            .assert {\n"
            "                it.numPublicDeclarations() == 1 && it.hasFunctionWithText { f -> f.contains(\"operator fun invoke\") }\n"
            "            }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Enforce architectural boundaries without boilerplate interfaces by leveraging Gradle multi-module compilation isolation, Kotlin `internal` visibility modifiers to encapsulate implementation details, and automated architectural linting rules via Konsist or ArchUnit in CI.",
        "best_answer": (
            "Enforcing architectural boundaries does not require suffocating codebases under 1-to-1 boilerplate interfaces (`Foo` / `FooImpl`). Modern Android engineering employs structural, compiler-enforced, and automated tooling mechanisms.\n\n"
            "1. **Compiler-Enforced Gradle Boundaries**: The strongest boundary is compilation failure. By splitting code into independent Gradle modules (`:feature:home`, `:core:domain`, `:core:database`), the build graph physically prevents forbidden calls. If a developer attempts to call a Room DAO from a ViewModel in a feature module that has no dependency on `:core:database`, the project will not compile.\n\n"
            "2. **Kotlin `internal` Visibility Modifiers**: Within a module, mark concrete classes, network DTOs, and helper mappers as `internal`. Expose only the required public entry point or interface. Consuming modules cannot access internal types even if they depend on the module.\n\n"
            "3. **Automated Architecture Tests (Konsist / ArchUnit)**: Rather than relying on manual code reviews, we write executable unit tests using **Konsist** that verify architectural invariants across the entire repository in CI."
        ),
        "deep_answer": (
            "Tools like **Konsist** revolutionize architectural governance. "
            "In just 5 lines of Kotlin test code, an engineering team can enforce contracts such as:\n"
            "- *'No class in `:presentation` may import anything from `androidx.room` or `retrofit2`.'*\n"
            "- *'Every Repository implementation must reside inside the `data` package.'*\n"
            "- *'All UseCases must reside in `:domain` and expose only `operator fun invoke()`.'*\n\n"
            "If any developer violates these rules, the test fails in local builds and blocks GitHub Actions CI. "
            "This eliminates the need for speculative interface wrapping while maintaining ironclad architectural discipline across large distributed teams."
        ),
        "follow_ups": [
            {
                "question": "What is Konsist, and how does it differ from Android Lint?",
                "answer": "Konsist is a Kotlin-first static analysis and architecture linter that allows writing unit tests asserting package structure, class inheritance, import rules, and naming conventions using an idiomatic Kotlin DSL."
            },
            {
                "question": "How does `internal` visibility enhance multi-module architecture?",
                "answer": "`internal` restricts class visibility strictly to the declaring Gradle compilation module, preventing external modules from depending on concrete implementation details."
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

    for item in ARC_20_26:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions ARC-20 to ARC-26. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
