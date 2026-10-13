#!/usr/bin/env python3
"""Generator for ARC-02 through ARC-07 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "arc.json"

ARC_02_07 = [
    {
        "id": "ARC-02",
        "arabic_explanation": (
            "شرح طبقات Clean Architecture الثلاث: العرض (Presentation)، النطاق (Domain)، والبيانات (Data):\n\n"
            "1. طبقة النطاق (Domain Layer - The Core):\n"
            "   - هي قلب التطبيق والطبقة الأكثر استقراراً؛ مكتوبة بلغة **Kotlin نقية 100%** بدون أي اعتمادية على Android SDK أو Retrofit أو Room.\n"
            "   - تحتوي على: **Entities** (كائنات الأعمال الحقيقية)، **UseCases / Interactors** (منطق العمليات والقرارات الحسابية وقواعد التحقق)، و **Repository Interfaces** (العقود المجردة لجلب وحفظ البيانات دون معرفة كيفية التنفيذ).\n\n"
            "2. طبقة البيانات (Data Layer):\n"
            "   - مسؤولة عن إدارة وتنسيق مصادر البيانات المتعددة (Network, Local Database, Datastore/Preferences, In-Memory Caches).\n"
            "   - تحتوي على: **DataSources** (Retrofit API Service, Room DAO)، **DTOs & Entities** (كائنات السيرفر وقاعدة البيانات)، و **Repository Implementations** التي تنفذ الواجهات المعرفة في طبقة النطاق وتقوم بـ Mapping للبيانات إلى Domain Entities.\n\n"
            "3. طبقة العرض (Presentation / UI Layer):\n"
            "   - مسؤولة عن كيفية تقديم البيانات للمستخدم والتقاط تفاعلاته.\n"
            "   - تحتوي على: **UI Composables / Activities / Fragments**، و **ViewModels** التي تستدعي الـ UseCases أو Repositories وتحول النتائج إلى تدفق حالة موحد `StateFlow<UiState>`، وتلتقط الأحداث (`UiEvent`)."
        ),
        "practical_walkthrough": (
            "توزيع كود شاشة سلة المشتريات عبر الطبقات الثلاث:\n"
            "```kotlin\n"
            "// 1. DOMAIN LAYER (Pure Kotlin - No Frameworks):\n"
            "data class CartItem(val productId: String, val quantity: Int, val unitPrice: Long)\n"
            "interface CartRepository {\n"
            "    fun observeCart(): Flow<List<CartItem>>\n"
            "    suspend fun updateQuantity(productId: String, quantity: Int)\n"
            "}\n"
            "class CalculateCartTotalUseCase {\n"
            "    operator fun invoke(items: List<CartItem>): Long = items.sumOf { it.quantity * it.unitPrice }\n"
            "}\n"
            "\n"
            "// 2. DATA LAYER (Implements Domain contracts, manages SQLite & Network):\n"
            "class CartRepositoryImpl(\n"
            "    private val cartDao: CartDao,\n"
            "    private val api: CartApi\n"
            ") : CartRepository {\n"
            "    override fun observeCart(): Flow<List<CartItem>> = cartDao.getCartEntities().map { it.toDomain() }\n"
            "    override suspend fun updateQuantity(productId: String, quantity: Int) {\n"
            "        cartDao.update(productId, quantity)\n"
            "        api.syncCart(productId, quantity)\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. PRESENTATION LAYER (Translates domain state into observable UI):\n"
            "@HiltViewModel\n"
            "class CartViewModel @Inject constructor(\n"
            "    private val repository: CartRepository,\n"
            "    private val calculateTotal: CalculateCartTotalUseCase\n"
            ") : ViewModel() {\n"
            "    val uiState: StateFlow<CartUiState> = repository.observeCart().map {\n"
            "        CartUiState.Success(items = it, total = calculateTotal(it))\n"
            "    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), CartUiState.Loading)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Presentation displays UI and translates user gestures into state streams via ViewModels. Domain contains pure business rules, entities, use cases, and repository interfaces without Android framework dependencies. Data implements domain repository interfaces, coordinating network APIs and local databases via mappers.",
        "best_answer": (
            "Modern Android Clean Architecture partitions responsibilities into three distinct architectural layers:\n\n"
            "1. **Domain Layer (The Business Core)**: Represents the innermost layer and contains pure business logic. It has zero dependencies on Android frameworks, network libraries, or databases. It contains:\n"
            "   - **Entities**: Business models encapsulating core data structures and invariant validation.\n"
            "   - **Use Cases (Interactors)**: Single-purpose orchestrators executing specific business scenarios (e.g. `CalculateCartTotalUseCase`).\n"
            "   - **Repository Interfaces**: Abstract contracts specifying what data operations the business requires, completely divorced from storage mechanisms.\n\n"
            "2. **Data Layer (The Source Coordinators)**: Implements domain repository interfaces. It manages raw data sources (Retrofit REST APIs, Room SQLite DAOs, SharedPreferences/DataStore), handles caching strategies, and maps external DTOs into domain entities.\n\n"
            "3. **Presentation Layer (The UI)**: Consists of ViewModels and Composable screens. The ViewModel calls Use Cases, reacts to state updates, and projects data into immutable `StateFlow<UiState>` streams, while capturing user UI events."
        ),
        "deep_answer": (
            "A critical design aspect of this division is the **Inversion of Control (IoC)** achieved through the Dependency Inversion Principle. "
            "Because the Domain layer defines the `Repository` interface and the Data layer implements it, compile-time source code dependencies point inward (`Data -> Domain` and `UI -> Domain`), while runtime execution flows outward.\n\n"
            "This division maximizes testability. "
            "Because the Domain layer is pure Kotlin without Android dependencies, its entire test suite runs as lightning-fast JVM unit tests executing in milliseconds without Robolectric or emulator bootstrapping.\n\n"
            "In enterprise Android modularization, these layers are often represented as separate Gradle modules: `:feature:cart:ui`, `:feature:cart:domain`, and `:feature:cart:data`, enforcing boundary discipline at the compiler level."
        ),
        "follow_ups": [
            {
                "question": "Can the Presentation layer bypass Domain and call Data directly?",
                "answer": "In simpler feature screens with no complex business rules (like simple CRUD lists), Google allows ViewModels to consume Repositories directly. However, in core business flows, bypassing Domain couples the UI to data concerns and bypasses business validations."
            },
            {
                "question": "Why shouldn't the Domain layer import Android `Context`?",
                "answer": "Importing `Context` couples pure business rules to Android framework lifecycles and platform APIs, destroying JVM testability and making cross-platform migration (e.g. Kotlin Multiplatform) impossible."
            }
        ]
    },
    {
        "id": "ARC-03",
        "arabic_explanation": (
            "ما هي قاعدة التبعية (The Dependency Rule)، وفي أي اتجاه يجب أن تشير التبعيات دائماً؟\n\n"
            "1. نص قاعدة التبعية الأساسية:\n"
            "   - **قاعدة التبعية تنص على**: \"لا يمكن لأي اسم أو كود أو كلاس في طبقة داخلية أن يذكر أو يعتمد على أي شيء موجود في طبقة خارجية\".\n"
            "   - التبعيات البرمجية في الكود (Source Code Dependencies) يجب أن تشير **دائماً إلى الداخل فقط (Inward towards the Domain)**.\n\n"
            "2. لماذا يجب أن تشير التبعيات للداخل؟\n"
            "   - لحماية منطق العمل الحساس (Core Business Rules) من التقلبات والتغييرات الخارجية (Framework Churn).\n   - أطر العمل ومكتبات واجهات المستخدم تتغير وتتطور باستمرار (من XML إلى Compose، من RxJava إلى Coroutines، من SQLite المباشر إلى Room).\n   - بفضل قاعدة التبعية، تستطيع تغيير مكتبة الشبكة بالكامل من Retrofit إلى Ktor دون المساس بسطر واحد من كود الـ Domain أو الـ UseCases!\n\n"
            "3. كيف نحقق ذلك عملياً (Dependency Inversion)؟\n"
            "   - كيف تقرأ طبقة الـ Domain بيانات من السيرفر إذا كانت لا تستطيع الاعتماد على طبقة الـ Data؟\n   - الحل هو **عكس التبعية (DIP)**: الـ Domain يُعرّف Interface (`UserRepository`)، وطبقة الـ Data تعتمد على الـ Domain وتقوم بـ `implements UserRepository`. في وقت التشغيل، يقوم محرك الـ DI (Hilt) بحقن الـ Implementation."
        ),
        "practical_walkthrough": (
            "توضيح انتهاك قاعدة التبعية وكيفية تصحيحه عبر Dependency Inversion:\n"
            "```kotlin\n"
            "// ❌ انتهاك صارخ: Domain يعتمد على تفاصيل طبقة Data (Retrofit DTO و Room Entity):\n"
            "// في module:domain:\n"
            "class AuthenticateUserUseCase(\n"
            "    private val api: RetrofitAuthApi // 💥 خطأ كارثي! Domain أصبح يعرف تفاصيل الشبكة الخارجية!\n"
            ") {\n"
            "    suspend fun execute(dto: LoginRequestDto): UserEntity { ... }\n"
            "}\n"
            "\n"
            "// ✅ تطبيق قاعدة التبعية السليمة: التبعية تشير للداخل والـ Data تعتمد على الـ Domain:\n"
            "// في module:domain:\n"
            "interface AuthRepository { // عقد مجرد في قلب الـ Domain\n"
            "    suspend fun authenticate(credentials: Credentials): Result<User>\n"
            "}\n"
            "class AuthenticateUserUseCase(private val authRepository: AuthRepository) {\n"
            "    suspend fun execute(credentials: Credentials): Result<User> = authRepository.authenticate(credentials)\n"
            "}\n"
            "\n"
            "// في module:data (الطبقة الخارجية تعتمد على الـ Domain):\n"
            "class AuthRepositoryImpl(private val api: RetrofitAuthApi) : AuthRepository {\n"
            "    override suspend fun authenticate(credentials: Credentials): Result<User> {\n"
            "        val dto = api.login(credentials.toDto())\n"
            "        return Result.success(dto.toDomain())\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "The Dependency Rule states that source code dependencies must only point inward toward higher-level policies (the Domain layer). Inner layers must have zero awareness of outer layers. Outer layers (UI, Network, Database) depend on interfaces declared by the Domain layer, realized at runtime via Dependency Inversion.",
        "best_answer": (
            "The Dependency Rule is the foundational postulate of Clean Architecture: **source code dependencies must strictly point inward toward higher-level business policies**.\n\n"
            "Under this rule, inner layers (Domain) must know absolutely nothing about outer layers (Data, UI, Frameworks). Nothing declared in an outer circle—such as a database class, a Retrofit API definition, an Android `Activity`, or a JSON parser—may be mentioned or imported by code in an inner circle.\n\n"
            "The direction of dependencies is structured as follows:\n"
            "- `Presentation / UI` -> depends on -> `Domain`\n"
            "- `Data` -> depends on -> `Domain`\n"
            "- `Domain` -> depends on -> **Nothing (Pure Kotlin)**\n\n"
            "This protects core business value from framework churn. If the team migrates from Retrofit to Ktor, or swaps Room for SQLDelight, not a single line of business rule logic in the Domain layer is touched, invalidated, or recompiled."
        ),
        "deep_answer": (
            "A frequent question arises: how can the Domain layer drive data operations if it cannot depend on the Data layer? "
            "This is resolved via the **Dependency Inversion Principle (DIP)**. "
            "The Domain layer defines an abstraction—a `Repository` interface—that specifies the queries and mutations it requires. "
            "The Data layer, residing in the outer circle, imports the Domain module and implements that interface (`RepositoryImpl`).\n\n"
            "At application startup, the Dependency Injection container (Hilt/Koin) wires the concrete Data implementation to the Domain interface contract. "
            "Thus, at compile time, the source code dependency points inward, while at runtime, control flows outward through the interface abstraction.\n\n"
            "In Gradle multi-module codebases, we enforce this rule via module dependencies: `:core:domain` has zero module dependencies, while `:core:data` has `implementation(project(\":core:domain\"))`."
        ),
        "follow_ups": [
            {
                "question": "What happens if a Domain entity imports a Room `@Entity` annotation?",
                "answer": "It violates the Dependency Rule. The Domain becomes coupled to SQLite storage schemas, Room library versions, and Android packaging, breaking purity and JVM test isolation."
            },
            {
                "question": "How does Gradle prevent accidental violations of the Dependency Rule?",
                "answer": "By making `:domain` an independent module without a dependency on `:data` or `:app`. If an engineer tries to import a Data class into Domain, the project fails to compile."
            }
        ]
    },
    {
        "id": "ARC-04",
        "arabic_explanation": (
            "ما هو نمط الـ Repository وما هو الـ UseCase؟ وما هي الفروق الجوهرية بينهما؟\n\n"
            "1. ما هو نمط المستودع (Repository Pattern)؟\n"
            "   - الـ Repository هو **وسيط مجرد (Mediator)** بين مصادر البيانات المختلفة وباقي أجزاء التطبيق.\n   - مهمته الأساسية: توفير واجهة نظيفة وكأن البيانات مقروءة من مجموعة كائنات في الذاكرة (`In-memory collection`).\n   - يخفي تفاصيل من أين أتت البيانات: هل أتت من الـ Cache؟ أم من قاعدة بيانات Room؟ أم من الـ Network عبر Retrofit؟\n   - هو المسؤول الوحيد عن إدارة استراتيجية الـ Caching وقواعد مزامنة البيانات (Offline-first sync).\n\n"
            "2. ما هو كائن حالة الاستخدام (UseCase / Interactor)؟\n"
            "   - الـ UseCase هو كائن يمثل **عملية بيزنس محددة لمرة واحدة (Single Business Action)** تعبر عن رغبة المستخدم أو النظام (مثل `SubmitTransferUseCase`, `GetAccountSummaryUseCase`).\n   - يركز على: قواعد التحقق (Validation)، دمج نتائج أكثر من Repository، وتطبيق الشروط الحسابية.\n   - يتبع مبدأ Single Responsibility: له دالة تنفيذ واحدة (غالباً `operator fun invoke`).\n\n"
            "3. المقارنة الجوهرية:\n"
            "   - **الـ Repository**: يتحدث بلغة البيانات والتخزين (`saveUser`, `getUserById`, `syncCart`).\n   - **الـ UseCase**: يتحدث بلغة المنتج وقواعد العمل (`PlaceOrderUseCase`, `VerifyEligibilityUseCase`)."
        ),
        "practical_walkthrough": (
            "تطبيق عملي يوضح الفرق بين UseCase يدمج مستودعين و Repository يدير الـ Cache:\n"
            "```kotlin\n"
            "// 1. REPOSITORY: يركز على مصادر البيانات والـ Cache:\n"
            "class UserRepositoryImpl(\n"
            "    private val localDao: UserDao,\n"
            "    private val remoteApi: UserApi\n"
            ") : UserRepository {\n"
            "    override fun getUser(id: String): Flow<User> = localDao.getUser(id).onStart {\n"
            "        // استراتيجية مزامنة البيانات والـ Cache:\n"
            "        refreshUser(id)\n"
            "    }\n"
            "    private suspend fun refreshUser(id: String) {\n"
            "        val networkUser = remoteApi.fetchUser(id)\n"
            "        localDao.insertUser(networkUser.toEntity())\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. USE CASE: يركز على سيناريو البيزنس وينسق بين Repositories متعددة:\n"
            "class UpgradeToPremiumUseCase @Inject constructor(\n"
            "    private val userRepository: UserRepository,\n"
            "    private val paymentRepository: PaymentRepository\n"
            ") {\n"
            "    suspend operator fun invoke(userId: String, paymentMethodId: String): Result<Subscription> {\n"
            "        val user = userRepository.getUserSync(userId) ?: return Result.failure(UserNotFoundException())\n"
            "        if (user.isSuspended) return Result.failure(AccountSuspendedException())\n"
            "\n"
            "        val chargeResult = paymentRepository.charge(paymentMethodId, PREMIUM_COST_CENTS)\n"
            "        if (chargeResult.isSuccess) {\n"
            "            userRepository.markAsPremium(userId)\n"
            "        }\n"
            "        return chargeResult\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A Repository mediates between multiple data sources (Network, Room, Cache), abstracting data access behind a collection-like interface and managing caching. A Use Case (Interactor) encapsulates a single business operation, enforcing domain rules and orchestrating multiple repositories.",
        "best_answer": (
            "The Repository and Use Case patterns serve complementary but distinct architectural purposes.\n\n"
            "1. **The Repository Pattern**: Acts as a mediator between domain/business layers and diverse raw data sources (Remote API, Room DB, in-memory cache). Its responsibilities are:\n"
            "   - Presenting a clean, domain-centric collection interface (`Flow<User>`, `suspend fun save()`).\n"
            "   - Encapsulating storage details, offline-first policies, and data synchronization logic.\n"
            "   - Mapping DTOs/Entities into clean Domain Models.\n\n"
            "2. **The Use Case (Interactor)**: Encapsulates a **single granular business operation**. It represents an action the user or system wants to perform (e.g. `CheckoutCartUseCase`, `AuthenticateWithBiometricsUseCase`). Its responsibilities are:\n"
            "   - Enforcing core business rules and validation logic.\n"
            "   - Orchestrating interactions across multiple repositories.\n"
            "   - Exposing a single entry point—conventionally implemented using Kotlin's `operator fun invoke()`."
        ),
        "deep_answer": (
            "A frequent architectural smell is creating 1-to-1 **Passthrough Use Cases** that merely wrap a repository method: `class GetUserUseCase(repo) { invoke(id) = repo.getUser(id) }`. "
            "If a business action involves zero validation, zero coordination, and zero transformation, creating a use case solely for dogma introduces meaningless boilerplate. "
            "Google's official architecture guidance explicitly recommends treating the Domain layer as optional: ViewModels can directly consume Repositories when business logic is absent.\n\n"
            "However, Use Cases become indispensable when business rules must be shared across multiple entry points. "
            "For example, if an `AddToCartUseCase` is executed by a standard product screen, a search screen, and a deep-link notification handler, placing the validation and limit checks inside a UseCase prevents duplicating business logic across three ViewModels."
        ),
        "follow_ups": [
            {
                "question": "When is a Use Case genuinely necessary versus overengineering?",
                "answer": "It is necessary when business rules require validation, orchestrate multiple repositories, or must be reused across multiple ViewModels. It is overengineering when it simply passes a call directly to a single repository method without added value."
            },
            {
                "question": "Why should a UseCase have only one public method (`invoke`)?",
                "answer": "To uphold the Single Responsibility Principle. A UseCase represents a single business action; having multiple disparate public functions turns it into a god class."
            }
        ]
    },
    {
        "id": "ARC-05",
        "arabic_explanation": (
            "ما الذي ينتمي إلى الـ ViewModel مقابل الـ UseCase مقابل الـ Repository؟ وكيف نقسم المسؤوليات بينهم؟\n\n"
            "1. ما ينتمي إلى الـ ViewModel:\n"
            "   - **إدارة دورة حياة الواجهة (UI Lifecycle Management)**: الصمود أثناء تدوير الشاشة (Configuration Changes).\n   - **تجهيز وإدارة الـ UI State**: استقبال البيانات وتحويلها إلى `StateFlow<UiState>` يسهل على Compose عرضه مباشرة.\n   - **معالجة مدخلات المستخدم (User Interactions)**: استقبال نقرات الأزرار، تبديل التبويبات، والتحقق من صحة الفورم البصرية (Form validation).\n   - **لا يحتوي أبداً على**: استدعاءات Retrofit مباشرة، منطق حسابات البزنس المعقدة، أو مراجع لـ Android Views و Context!\n\n"
            "2. ما ينتمي إلى الـ UseCase:\n"
            "   - **قواعد وسياسات العمل (Business Policies)**: حساب الضرائب، التأكد من شروط ترقية العضوية، فحص الصلاحيات.\n   - **التنسيق بين مستودعات متعددة (Cross-Repository Coordination)**: سحب بيانات من `UserRepository` والدفع عبر `PaymentRepository` وتحديث `AnalyticsRepository`.\n   - **إعادة استخدام المنطق عبر شاشات متعددة (Shared Business Logic)**.\n\n"
            "3. ما ينتمي إلى الـ Repository:\n"
            "   - **استراتيجية التخزين والكاش (Caching Strategy)**: متى نقرأ من الـ Database ومتى نسحب من الـ Network.\n   - **مزامنة البيانات (Offline Sync)**: حفظ البيانات محلياً وإرسالها عند توفر الإنترنت.\n   - **Mapping**: تحويل DTOs و SQLite Rows إلى Domain Models."
        ),
        "practical_walkthrough": (
            "مثال عملي يوضح الحدود الصارمة للمسؤوليات:\n"
            "```kotlin\n"
            "// 1. REPOSITORY: إدارة البيانات والكاش والشبكة فقط:\n"
            "class OrderRepositoryImpl(private val api: OrderApi, private val dao: OrderDao) : OrderRepository {\n"
            "    override suspend fun submitOrder(order: Order): Result<OrderConfirmation> = runCatching {\n"
            "        val response = api.postOrder(order.toDto())\n"
            "        dao.insertOrder(response.toEntity())\n"
            "        response.toDomain()\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. USE CASE: قواعد البيزنس والتحقق والتنسيق بين مستودعين:\n"
            "class PlaceOrderUseCase @Inject constructor(\n"
            "    private val orderRepo: OrderRepository,\n"
            "    private val inventoryRepo: InventoryRepository\n"
            ") {\n"
            "    suspend operator fun invoke(order: Order): OrderResult {\n"
            "        if (order.items.isEmpty()) return OrderResult.Error(\"Cart is empty\")\n"
            "        val inStock = inventoryRepo.checkStock(order.items)\n"
            "        if (!inStock) return OrderResult.Error(\"Items out of stock\")\n"
            "        return orderRepo.submitOrder(order).fold(\n"
            "            onSuccess = { OrderResult.Success(it) },\n"
            "            onFailure = { OrderResult.Error(it.message ?: \"Submission failed\") }\n"
            "        )\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. VIEWMODEL: إدارة حالة الواجهة والتفاعل فقط:\n"
            "@HiltViewModel\n"
            "class CheckoutViewModel @Inject constructor(\n"
            "    private val placeOrder: PlaceOrderUseCase\n"
            ") : ViewModel() {\n"
            "    private val _uiState = MutableStateFlow<CheckoutUiState>(CheckoutUiState.Idle)\n"
            "    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()\n"
            "\n"
            "    fun onPlaceOrderClicked(order: Order) {\n"
            "        viewModelScope.launch {\n"
            "            _uiState.value = CheckoutUiState.Loading\n"
            "            when (val result = placeOrder(order)) {\n"
            "                is OrderResult.Success -> _uiState.value = CheckoutUiState.Success(result.confirmation)\n"
            "                is OrderResult.Error -> _uiState.value = CheckoutUiState.Error(result.message)\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "ViewModel manages UI lifecycle and exposes `StateFlow<UiState>` to the presentation layer. UseCase encapsulates business operations, validating policies and coordinating multiple repositories. Repository mediates between network, local database, and in-memory caches, abstracting storage mechanisms.",
        "best_answer": (
            "Clear boundary division among ViewModel, UseCase, and Repository prevents monolithic architectural bloat.\n\n"
            "1. **ViewModel (Presentation Layer)**:\n"
            "   - Owns UI state and survives configuration changes.\n"
            "   - Converts domain outputs into immutable `StateFlow<UiState>` tailored for rendering.\n"
            "   - Translates raw user actions into business commands.\n"
            "   - Never performs I/O directly, never references Android `Context`, and contains zero business calculations.\n\n"
            "2. **UseCase (Domain Layer)**:\n"
            "   - Encapsulates discrete, reusable business rules (e.g. eligibility criteria, tax calculations).\n"
            "   - Coordinates multiple repositories (e.g. querying user balance from `AccountRepository` and deducting inventory from `ProductRepository`).\n"
            "   - Operates strictly on pure Kotlin domain models without UI or database dependencies.\n\n"
            "3. **Repository (Data Layer)**:\n"
            "   - Single source of truth for a specific data aggregate.\n"
            "   - Decides whether to query local database, fetch from network, or return cached memory.\n"
            "   - Maps external schemas (DTOs, Room entities) to clean domain models."
        ),
        "deep_answer": (
            "A frequent anti-pattern is **Fat ViewModel Syndrome**, where ViewModels perform data mapping, HTTP header configuration, and multiple repository joins directly. "
            "This makes ViewModels massive (1,000+ lines) and untestable without heavy mocking.\n\n"
            "Conversely, pushing business rules down into Repositories is an equal architectural mistake. "
            "A Repository should never know business policy (e.g. 'a gold member gets 15% discount'); the Repository simply stores and retrieves orders and user profiles. "
            "Calculating the discount is the strict domain responsibility of a Use Case.\n\n"
            "By strictly adhering to these boundaries, each component remains easily testable in isolation: Repositories are verified via Fake DataSources, UseCases are verified via Fake Repositories, and ViewModels are verified by asserting `uiState` emissions."
        ),
        "follow_ups": [
            {
                "question": "Can a UseCase call another UseCase?",
                "answer": "Yes, when one complex business operation depends on a foundational business policy (e.g. `CheckoutCartUseCase` calling `ValidateCouponUseCase`). However, deep nesting should be avoided to prevent call stack confusion."
            },
            {
                "question": "Why shouldn't a Repository expose a `UiState`?",
                "answer": "A Repository serves the domain, not the UI. Coupling a Repository to `UiState` makes it impossible to reuse across different screens or background workers with different presentation requirements."
            }
        ]
    },
    {
        "id": "ARC-06",
        "arabic_explanation": (
            "أين تعيش كائنات DTOs و Room Entities و Domain Models و UI Models في المعمارية؟ وما دور كل منها؟\n\n"
            "1. كائنات الـ DTOs (Data Transfer Objects):\n"
            "   - **مكانها**: طبقة الـ Data (داخل مجلد `network` / `remote`).\n   - **مهمتها**: مطابقة الـ JSON Schema أو الـ Protobuf القادم من الـ Backend بدقة.\n   - **خصائصها**: تحوي وسوم Serialization مثل `@SerialName` أو `@SerializedName`، وغالباً ما تكون جميع حقولها قابلة للعدم (Nullable) لأن السيرفر قد يغير العقد في أي وقت.\n\n"
            "2. كائنات الـ Room Entities:\n"
            "   - **مكانها**: طبقة الـ Data (داخل مجلد `local` / `db`).\n   - **مهمتها**: تمثيل الجداول والصفوف داخل قاعدة بيانات SQLite المحلية.\n   - **خصائصها**: تحوي وسوم Room مثل `@Entity`, `@PrimaryKey`, `@ColumnInfo`.\n\n"
            "3. كائنات الـ Domain Models:\n"
            "   - **مكانها**: طبقة الـ Domain (داخل مجلد `model`).\n   - **مهمتها**: تمثيل المفاهيم الأساسية للأعمال في التطبيق كـ Pure Kotlin Data Classes.\n   - **خصائصها**: نظيفة تماماً من أي وسوم أو مكتبات خارجية، تضمن ثبات البيانات وسلامتها (Business Invariants).\n\n"
            "4. كائنات الـ UI Models:\n"
            "   - **مكانها**: طبقة الـ Presentation (داخل مجلد `ui` أو `feature`).\n   - **مهمتها**: مطابقة ما يعرضه الـ Composable أو الـ View على الشاشة مباشرة.\n   - **خصائصها**: نصوص منسقة جاهزة للعرض (Formatted strings)، ألوان، وأيقونات (`@StringRes`, `Color`)."
        ),
        "practical_walkthrough": (
            "تتبع نموذج منتج عبر الطبقات الأربع مع الـ Mappers:\n"
            "```kotlin\n"
            "// 1. DATA LAYER (Network DTO): يطابق JSON السيرفر بدقة:\n"
            "@Serializable\n"
            "data class ProductDto(\n"
            "    @SerialName(\"prod_id\") val id: String,\n"
            "    @SerialName(\"cost_in_cents\") val cost: Long,\n"
            "    @SerialName(\"is_active\") val active: Boolean?\n"
            ")\n"
            "\n"
            "// 2. DATA LAYER (Local Database Entity): يطابق جدول SQLite:\n"
            "@Entity(tableName = \"products\")\n"
            "data class ProductEntity(\n"
            "    @PrimaryKey val id: String,\n"
            "    val costCents: Long,\n"
            "    val lastUpdatedTimestamp: Long\n"
            ")\n"
            "\n"
            "// 3. DOMAIN LAYER (Pure Domain Model): نموذج البيزنس النقي المستقر:\n"
            "data class Product(\n"
            "    val id: String,\n"
            "    val price: Long,\n"
            "    val isAvailable: Boolean\n"
            ")\n"
            "\n"
            "// 4. PRESENTATION LAYER (UI Model): نصوص منسقة جاهزة للرسم في Compose:\n"
            "@Immutable\n"
            "data class ProductUiModel(\n"
            "    val id: String,\n"
            "    val formattedPrice: String, // جاهز مثل \"$19.99\"\n"
            "    val statusColor: Color,\n"
            "    val isBuyButtonEnabled: Boolean\n"
            ")\n"
            "```"
        ),
        "quick_answer": "DTOs live in Data/remote matching API schemas. Room entities live in Data/local matching SQLite tables. Domain models live in Domain representing pure business entities without framework annotations. UI models live in Presentation holding formatted, display-ready data.",
        "best_answer": (
            "Separating models across architectural layers guarantees isolation and prevents external schema changes from cascading across the application.\n\n"
            "1. **DTOs (Data Transfer Objects)**: Reside in the **Data Layer** (`remote/dto`). They represent network serialization schemas, annotated with `@Serializable` or `@SerializedName`. They are designed around API payloads and should never leak past the repository boundary.\n\n"
            "2. **Room Entities**: Reside in the **Data Layer** (`local/entity`). They represent SQLite table schemas, annotated with `@Entity`, `@PrimaryKey`, and foreign keys. They reflect persistence requirements (indexes, table relations), not UI or business needs.\n\n"
            "3. **Domain Models**: Reside in the **Domain Layer** (`domain/model`). Pure Kotlin data classes representing business truth. They contain zero serialization or database annotations, enforcing invariant validity across the app.\n\n"
            "4. **UI Models**: Reside in the **Presentation Layer** (`presentation/model`). They contain pre-formatted strings, localized labels, and visual state properties tailored for instant, allocation-free rendering in Compose."
        ),
        "deep_answer": (
            "Why not use a single model class annotated with `@Serializable`, `@Entity`, and consumed directly in Compose? "
            "This shortcut—common in junior tutorials—creates catastrophic tight coupling: changing an API property name alters the local SQLite column, forces a Room database migration, and breaks the UI layout simultaneously!\n\n"
            "Furthermore, UI models optimize rendering performance in Jetpack Compose. "
            "Instead of letting a Composable format dates or currency on every recomposition pass (`format(product.priceCents)`), the ViewModel maps the domain model into a `ProductUiModel` where `formattedPrice = \"$19.99\"` is computed once. "
            "This keeps the Composable function pure, lightweight, and skippable."
        ),
        "follow_ups": [
            {
                "question": "What is the consequence of passing a Room Entity directly to a Composable?",
                "answer": "It leaks SQLite schema details into the UI, forces Compose to re-render when non-visual database metadata updates, and prevents running pure JVM UI tests without Room dependencies."
            },
            {
                "question": "Can a Domain Model and a UI Model be identical in simple apps?",
                "answer": "Yes, if the domain model has no formatting requirements and is already `@Immutable`, the ViewModel can expose it directly to the UI to avoid redundant mapping boilerplate."
            }
        ]
    },
    {
        "id": "ARC-07",
        "arabic_explanation": (
            "لماذا نستخدم محولات النماذج (Mappers) بين الطبقات المختلفة؟ وما الفوائد الحقيقية منها؟\n\n"
            "1. مبدأ العزل والحماية (Decoupling and Insulation):\n"
            "   - الـ Mapper هو المسؤول عن تحويل البيانات عند حدود الطبقات (Architectural Boundaries).\n   - يمنع انتشار التغييرات الخارجية (Schema Ripple Effect): إذا قام فريق الـ Backend بتغيير اسم حقل من `user_name` إلى `handle`، يقتصر التعديل على دالة الـ Mapper في طبقة الـ Data فقط، بينما تظل آلاف الأسطر في الـ Domain والـ UI كما هي دون أي تغيير!\n\n"
            "2. تنظيف البيانات والتحقق من صحتها (Data Sanitization & Null-Safety):\n"
            "   - استجابات الـ JSON غالباً ما تحتوي على حقول مجهولة، أرقام سالبة غير متوقعة، أو حقول Nullable.\n   - تقوم الـ Mappers بتحويل البيانات غير الموثوقة القادمة من السيرفر إلى نماذج بيزنس صارمة ومضمونة السلامة (Strict Domain Invariants) مع توفير قيم افتراضية آمنة.\n\n"
            "3. تجهيز البيانات للواجهة (UI Formatting Optimization):\n"
            "   - تحويل التواريخ من Unix Timestamp (`Long`) إلى نصوص منسقة محلياً (`String`) في مرحلة الـ Mapping، مما يريح الـ Composable من استهلاك المعالج في دوال التنسيق أثناء السكرول."
        ),
        "practical_walkthrough": (
            "تنفيذ مابرات نظيفة باستخدام Extension Functions تضمن سلامة البيانات:\n"
            "```kotlin\n"
            "// 1. Data Layer Mapper: تحويل DTO السيرفر إلى Domain Entity مع تطهير البيانات:\n"
            "fun UserDto.toDomain(): User {\n"
            "    return User(\n"
            "        id = this.id ?: throw InvalidUserDataException(\"User ID cannot be null\"),\n"
            "        displayName = this.fullName ?: \"Anonymous Guest\", // حماية من null\n"
            "        isVerified = this.verificationStatus == \"VERIFIED\",\n"
            "        joinedDate = Instant.ofEpochMilli(this.registeredAt ?: 0L)\n"
            "    )\n"
            "}\n"
            "\n"
            "// 2. Presentation Layer Mapper: تحويل Domain Entity إلى UI Model جاهز للعرض:\n"
            "fun User.toUiModel(dateTimeFormatter: DateTimeFormatter): UserUiModel {\n"
            "    return UserUiModel(\n"
            "        id = this.id,\n"
            "        name = this.displayName,\n"
            "        badgeVisible = this.isVerified,\n"
            "        formattedJoinDate = dateTimeFormatter.format(this.joinedDate) // محسوبة مسبقاً للـ UI\n"
            "    )\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Mappers isolate architectural boundaries so external API or database changes don't break business logic or UI. They sanitize untrusted nullable payloads into validated domain models and transform domain data into pre-formatted, display-ready UI models.",
        "best_answer": (
            "Mappers are the gatekeepers of architectural boundaries, ensuring that each layer operates exclusively on data structures tailored to its purpose.\n\n"
            "1. **Decoupling from External Volatility**: APIs and database schemas evolve constantly. Without mappers, renaming a JSON property cascades through the entire codebase, breaking domain logic and UI layouts. Mappers act as shock absorbers, confining external changes strictly to the data layer.\n\n"
            "2. **Data Sanitization and Invariant Enforcement**: Network payloads are untrusted. Mappers sanitize raw inputs: mapping nullable DTO properties to non-nullable domain types with safe fallbacks, parsing raw string codes into type-safe enums or sealed classes, and rejecting corrupt records before they reach core business rules.\n\n"
            "3. **Presentation Pre-computation**: Presentation mappers convert raw domain metrics (e.g. timestamps, currency in cents) into localized, human-readable strings (`$12.50`) once, keeping composable functions pure and avoiding expensive formatting passes during 120fps scrolling."
        ),
        "deep_answer": (
            "Under the hood, implementing mappers efficiently requires avoiding excessive object allocation churn. "
            "In Kotlin, mappers are best written as top-level or internal extension functions (`fun ProductDto.toDomain()`), avoiding unnecessary mapper class instantiations.\n\n"
            "When dealing with large lists (e.g. 10,000 items), mapping must be executed off the main thread. "
            "Repositories execute DTO-to-Domain mapping within `withContext(Dispatchers.Default)` or `Dispatchers.IO` so that heavy JSON parsing and transformation passes never stutter the Android main looper.\n\n"
            "In unit testing, testing mappers is straightforward: developers write pure JVM unit tests passing edge-case DTOs (null fields, malformed strings, boundary values) to verify that the domain model is always constructed in a valid, robust state."
        ),
        "follow_ups": [
            {
                "question": "Should Mappers be classes or top-level extension functions?",
                "answer": "Top-level extension functions are preferred for stateless mappings because they avoid object allocation. A mapper class is only necessary when it requires injected dependencies like formatters or locale providers."
            },
            {
                "question": "Can mapping become a performance bottleneck?",
                "answer": "Yes, if mapping large collections of thousands of items on the main thread. We optimize this by paginating data with Paging 3 and offloading mapping to `Dispatchers.Default`."
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

    for item in ARC_02_07:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions ARC-02 to ARC-07. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
