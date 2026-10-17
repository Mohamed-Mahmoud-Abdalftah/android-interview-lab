#!/usr/bin/env python3
"""Elevate ARC-01 through ARC-09 for bilingual parity and senior spoken answers."""
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
# ARC-01: What is Clean Architecture?
# ==========================================
DATA["ARC-01"] = {
    "concept_en": """Clean Architecture, popularized by Robert C. Martin, organizes software into concentric layers where high-level business rules reside at the core, completely decoupled from delivery mechanisms, operating system frameworks, databases, and third-party libraries. In Android, the fundamental problem it solves is the tight coupling between Android lifecycle components and enterprise business logic. Without Clean Architecture, Activities, Fragments, and ViewModels become God objects where network DTOs are directly bound to UI widgets, database schemas leak into presentation controllers, and business calculations cannot be tested without heavy Robolectric harnesses or slow emulator instrumentation. By enforcing the inward Dependency Rule through polymorphism and repository contracts, Clean Architecture turns the Android operating system, Jetpack UI toolkits, and persistence drivers into swappable plugins around an immutable, pure Kotlin domain core.""",
    "walkthrough_en": """Demonstrating Clean Architecture layer isolation with pure Kotlin domain rules:
```kotlin
// 1. Domain Layer: Pure Kotlin, zero Android SDK dependencies
data class UserProfile(val id: String, val username: String, val isPremium: Boolean)

interface UserRepository {
    suspend fun getProfile(userId: String): Result<UserProfile>
}

class GetUserProfileUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(userId: String): Result<UserProfile> {
        if (userId.isBlank()) return Result.failure(IllegalArgumentException("Invalid user ID"))
        return repository.getProfile(userId)
    }
}

// 2. Data Layer: Implements domain contract, maps network DTOs
class UserRepositoryImpl(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {
    override suspend fun getProfile(userId: String): Result<UserProfile> = runCatching {
        val cached = dao.getUser(userId)
        if (cached != null) return@runCatching cached.toDomain()
        val networkDto = api.fetchUser(userId)
        dao.insertUser(networkDto.toEntity())
        networkDto.toDomain()
    }
}

// 3. Presentation Layer: StateHolder exposes state to Composables
class ProfileViewModel(private val getUserProfile: GetUserProfileUseCase) : ViewModel() {
    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            getUserProfile(id)
                .onSuccess { _uiState.value = ProfileUiState.Success(it.username) }
                .onFailure { _uiState.value = ProfileUiState.Error(it.message ?: "Failed") }
        }
    }
}
```""",
    "short_en": """Clean Architecture isolates core business rules from frameworks, databases, and UI implementations through concentric abstraction layers. In Android, it prevents UI components from coupling directly to data sources or framework APIs, ensuring business logic remains framework-agnostic, modular, and purely testable on local JVMs without Android runtime dependencies.""",
    "structured_en": """To begin with, Clean Architecture addresses the fundamental vulnerability of Android development where framework volatility and UI lifecycles corrupt enterprise business logic.
From an architectural standpoint, the system is separated into concentric layers governed by the Dependency Rule, dictating that dependencies must point inward toward pure domain entities and use cases. The domain layer contains zero Android dependencies, operating entirely on pure Kotlin data classes and interfaces.
In production scenarios, presentation and data layers act as swappable plugins. The UI consumes view states through ViewModels, while data repositories implement domain contracts via Retrofit, Room, or DataStore.
As for operational advantages, this boundary isolation enables lightning-fast local JVM unit tests, prevents network DTO schema changes from cascading into UI widgets, and allows engineering teams to parallelize development across isolated modules without merge conflicts or architectural degradation.""",
    "deep_senior_en": """Under the hood, Clean Architecture solves coupling and testability bottlenecks by inverting source code dependencies across layer boundaries using polymorphism. In typical legacy Android codebases, an Activity or ViewModel directly imports network clients or database DAOs, binding domain validation directly to JSON schemas or SQLite tables. When backend APIs change or libraries update, the entire presentation layer shatters.
Clean Architecture resolves this by declaring repository interfaces inside the inner domain layer. The outer data layer implements these interfaces and handles DTO-to-domain mapping, meaning the domain layer dictates the contractual data requirements of the enterprise rather than subserviently reacting to external transport protocols.
In production environments, this architectural purity demands pragmatic trade-offs. Introducing use cases, duplicate domain models, and bi-directional mappers for simple CRUD operations introduces boilerplate and navigation indirection that can slow delivery if applied dogmatically.
Staff engineers assess team size, domain complexity, and multi-platform ambitions before committing to full three-layer isolation. While complex domains like fintech checkout flows, offline transaction reconciliation, and risk validation mandate use cases and strict module boundaries, simpler feature verticals often expose repository streams directly to ViewModels to avoid unnecessary layer overhead while maintaining complete testability. By strictly enforcing layer boundaries at compile time through Gradle modules, large engineering teams prevent accidental coupling and maintain pristine architectural hygiene.""",
    "meta_ar": {
        "id": "ARC-01",
        "questionAr": "ما هي العمارة النظيفة (Clean Architecture) وما المشكلة التي تحلها في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم أهداف العمارة النظيفة في عزل منطق الأعمال عن أطر العمل، واستيعاب قاعدة التبعيات للداخل، وإدراك كيفية موازنة الفوائد الهندسية مع تكلفة الطبقات المتعددة في المشروعات الحقيقية.",
        "why_it_matters_ar": "بدون العمارة النظيفة، تتضخم كلاسات العرض وتختلط نداءات الشبكة وقواعد البيانات بدورة حياة الشاشات، مما يجعل الكود هشاً ومستحيلاً في الاختبار بدون تشغيل محاكي بطيء.",
        "worked_example_ar": "عزل منطق الدومين بكود كوتلن نقي بدون أي استيراد لكلاسات أندرويد:\n```kotlin\n// Domain: كود كوتلن صافٍ تماماً\ninterface UserRepository {\n    suspend fun getUserProfile(userId: String): Result<UserProfile>\n}\n\nclass GetUserProfileUseCase(private val repository: UserRepository) {\n    suspend operator fun invoke(userId: String): Result<UserProfile> {\n        if (userId.isBlank()) return Result.failure(IllegalArgumentException(\"Invalid user ID\"))\n        return repository.getUserProfile(userId)\n    }\n}\n```",
        "trade_offs_ar": "العمارة النظيفة توفر استقلالية تامة واختبارات معزولة وسهولة في استبدال المكتبات، لكنها تضيف طبقات كود متعددة ومحولات بيانات تزيد من حجم المشروع وتكلفة الصيانة في الشاشات البسيطة.",
        "failure_modes_ar": "تسريب كلاسات أندرويد مثل Context أو Bundle إلى طبقة الدومين، أو تمرير كائنات DTO القادمة من السيرفر مباشرة إلى شاشات Compose دون تحويلها لنماذج دومين مستقلة.",
        "production_perspective_ar": "في المشروعات المصرفية والأنظمة الضخمة، نلزم المطورين بموديولات Gradle منفصلة تمنع الدومين من رؤية أي مكتبات خارجية، مع كتابة اختبارات وحدة تعمل على JVM في أجزاء من الثانية.",
        "how_to_answer_ar": "ابدأ بتعريف الهدف الأساسي وهو عزل منطق الأعمال عن تفاصيل النظام الخارجي، واشرح قاعدة التبعية للداخل، وبيّن كيف تجعل طبقة الدومين نقية وسهلة الاختبار، ثم وضح متى تكون مفيدة ومتى تكون إفراطاً برمجياً.",
        "talking_points_ar": "قاعدة التبعية للداخل، واستقلال الدومين عن بيئة التشغيل، واستخدام الواجهات لقلب التبعيات، ومعايير اتخاذ القرار بين البساطة والطبقات المعمارية الكاملة.",
        "follow_ups_ar": "- **المحاور:** \"هل كل شاشة في التطبيق محتاجة UseCase خاص بيها؟\"\n  **المرشح:** \"لا، التوثيق الرسمي لأندرويد بيعتبر طبقة الدومين اختيارية؛ لو الشاشة مجرد قراءة بسيطة من الداتا وعرضها بدون أي منطق أعمال مركب، الأفضل للـ ViewModel يكلم الريبوزيتوري مباشرة لتجنب كود التمرير الفارغ.\"\n\n- **المحاور:** \"إزاي نضمن في الـ CI إن مفيش مطور يستورد كلاسات أندرويد جوه الدومين؟\"\n  **المرشح:** \"بنفصل الدومين في موديول Gradle مستقل من نوع java-library أو kotlin(\"jvm\")؛ بكده الكومبايلر هيرفض أي استيراد لكلاسات أندرويد زي Context تلقائياً قبل الدمج.\"",
        "self_check_ar": "هل وضحت قاعدة التبعيات للداخل؟ هل أكدت على نقاء طبقة الدومين؟ وهل بينت المفاضلة الهندسية بين المرونة وتكلفة الكود الإضافي؟",
        "references_ar": f"- [Guide to app architecture](https://developer.android.com/topic/architecture) — التوثيق الرسمي لهندسة التطبيقات من جوجل.\n- [The Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) — المقال الأصلي لمفهوم العمارة النظيفة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "العمارة النظيفة هي أسلوب لتنظيم الكود في طبقات دائرية بتفصل منطق الأعمال الأساسي عن تفاصيل أطر العمل وقواعد البيانات وشاشات العرض. في أندرويد بتحل مشكلة الاعتمادية المباشرة على كلاسات النظام والـ SDK، وبتخلي الدومين كود كوتلن نقي يشتغل ويختبر بسرعة على الـ JVM بدون أي محاكي.",
        "best_answer_ar": "العمارة النظيفة في جوهرها بتعالج أكبر مشكلة بتقابل مطوري أندرويد، وهي تداخل دورة حياة النظام مع منطق الأعمال الحرج للتطبيق.\n\nالفكرة الأساسية بتعتمد على قاعدة التبعية، واللي بتفرض إن كل الاعتماديات تتجه دائماً للداخل نحو طبقة الدومين المستقلة. طبقة الدومين مبتحتويش على أي استيراد لكلاسات أندرويد وبتتعامل بلغة كوتلن الصافية، وده بيخليها القلب النابض للتطبيق.\n\nفي المقابل، طبقات العرض والبيانات بتعتبر إضافات خارجية نقدر نغيرها ونبدلها في أي وقت. الـ ViewModel بياخد حالات العرض ويبعتها للشاشة، والريبوزيتوري بينفذ العقود البرمجية للدومين باستخدام روم أو رتروفيت.\n\nالميزة الإنتاجية الكبرى هي السرعة الفائقة في كتابة وتشغيل الـ Unit Tests على أجهزة المطورين بدون الاحتياج لتشغيل إيموليتور، ده غير حماية شاشات التطبيق من التغيرات المفاجئة في شكل البيانات اللي راجعة من السيرفر، وتسهيل الشغل المتوازي في الفرق الهندسية الكبيرة.",
        "deep_answer_ar": "تحت الكابوت، العمارة النظيفة بتعتمد على مبدأ قلب التبعيات باستخدام الـ Polymorphism علشان تعزل طبقات البرنامج عزلاً كاملاً. في التطبيقات التقليدية، الـ ViewModel بيعمل استيراد مباشر للـ Retrofit API أو الـ Room DAO، وده بيربط منطق الحسابات وشروط الأمان مباشرة بشكل الداتا الخارجية وتفاصيل الـ JSON.\n\nالعمارة النظيفة بتكسر الرابط ده عن طريق تعريف واجهات الريبوزيتوري داخل طبقة الدومين الداخلية. طبقة البيانات الخارجية هي اللي بتنفذ الواجهات دي وبتحول كائنات الـ DTO لنماذج دومين نقية، بكده الدومين هو اللي بيفرض شروطه على العالم الخارجي مش العكس.\n\nفي بيئات العمل الفعلية، لازم المطور السينيور يوازن بين النقاء المعماري والتكلفة الهندسية. إنشاء Use Cases ونماذج بيانات مكررة ومحولات لكل عملية بسيطة ممكن يزود تعقيد الكود والـ Boilerplate بدون داعي حقيقي.\n\nعلشان كده في الأنظمة الكبرى، بنقيس حجم الفريق ومدى تعقيد العمليات قبل ما نلزم كل ميزة بالطبقات الثلاثة. الشاشات المعقدة زي الدفع الإلكتروني ومراجعة المعاملات البنكية بتمر حتماً عبر Use Cases مستقلة وموديولات منفصلة، بينما شاشات القراءة البسيطة بنخلي الـ ViewModel يتصل بالريبوزيتوري مباشرة لتوفير الوقت وتجنب الـ Over-engineering مع الحفاظ التام على إمكانية الاختبار. وبنعتمد على موديولات Gradle الصارمة لضمان استحالة استيراد كلاسات أندرويد داخل الدومين على مستوى الكومبايلر."
    }
}

# ==========================================
# ARC-02: Presentation, Domain, Data layers
# ==========================================
DATA["ARC-02"] = {
    "concept_en": """Google's recommended Android app architecture divides applications into three primary functional layers: Presentation, Domain, and Data. The Presentation layer contains UI elements (Composables, Activities, Fragments) and state holders (ViewModels) that render data and translate user input into unidirectional events. The Domain layer is an optional mediator encapsulating complex, reusable business logic and coordinating multi-repository interactions through single-purpose Use Cases; it operates purely on Kotlin primitives without Android SDK imports. The Data layer encapsulates business data access and caching policies, serving as the single source of truth for the application. It consists of repository interfaces and data source implementations (network clients, local databases, data stores) that expose reactive data streams and domain entities to higher architectural layers.""",
    "walkthrough_en": """Orchestrating the three architectural layers in a modern Android news feed:
```kotlin
// 1. Data Layer: Repository coordinates Room and Retrofit, exposes Domain models
class NewsRepositoryImpl(
    private val api: NewsApi,
    private val dao: NewsDao
) : NewsRepository {
    override fun getArticles(): Flow<List<Article>> =
        dao.observeArticles().map { entities -> entities.map { it.toDomain() } }

    override suspend fun syncArticles() {
        val remoteArticles = api.fetchTopHeadlines()
        dao.upsertArticles(remoteArticles.map { it.toEntity() })
    }
}

// 2. Domain Layer: Encapsulates filtering business rule
class GetBookmarkedArticlesUseCase(private val repository: NewsRepository) {
    operator fun invoke(): Flow<List<Article>> =
        repository.getArticles().map { list -> list.filter { it.isBookmarked } }
}

// 3. Presentation Layer: State holder binds domain streams to UI State
class BookmarksViewModel(
    private val getBookmarkedArticles: GetBookmarkedArticlesUseCase
) : ViewModel() {
    val uiState: StateFlow<BookmarksUiState> = getBookmarkedArticles()
        .map { articles -> BookmarksUiState.Success(articles.map { it.toUiModel() }) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = BookmarksUiState.Loading
        )
}
```""",
    "short_en": """Presentation renders UI and translates user intents into state via ViewModels and Compose. Domain encapsulates isolated, reusable business logic through pure Kotlin UseCases. Data serves as the single source of truth, managing local databases, remote network clients, and caching policies behind clean repository interfaces.""",
    "structured_en": """To begin with, modern Android architecture partitions responsibilities into Presentation, Domain, and Data layers to ensure scalability and strict boundary isolation.
From an architectural standpoint, the Presentation layer consumes state and dispatches user actions. It contains Composables or Fragments observing immutable UI State exposed by ViewModels, ensuring the UI remains passive and declarative without business decision logic.
In production scenarios, the Domain layer is an optional mediator containing single-purpose UseCases. It operates entirely without Android framework imports, encapsulating enterprise business rules, mathematical validations, and multi-repository coordination that multiple ViewModels can share.
As for the Data layer, it acts as the application's single source of truth. Repositories coordinate remote REST or GraphQL APIs with local Room databases, resolving synchronization conflicts, offline caching, and data mapping. This ensures that upstream consumers interact strictly with stable domain entities rather than volatile network payloads or database entities.""",
    "deep_senior_en": """Under the hood, dividing an Android codebase into Presentation, Domain, and Data creates clear boundaries for reactive data flow and compilation modularity. In Google's recommended architecture, data flows unidirectionally: user actions originate in Composables, travel up through ViewModel events to UseCases and Repositories, while updated state streams downward from the Data layer through Domain flows into UI State holders.
The Data layer hides storage mechanics. Whether data originates from in-memory caches, encrypted Room databases, or remote microservices, the repository exposes a unified stream of domain entities. It handles offline-first policies, optimistic writes, and network retry backoffs so upper layers remain oblivious to transport details.
The Domain layer exists specifically to prevent logic duplication. When business algorithms—such as calculating tax rebates or enforcing credit card fraud rules—are needed across both a mobile checkout screen and a background sync worker, extracting that logic into a UseCase guarantees consistency and instant JVM testing.
Staff engineers avoid dogmatic application of all three layers across every screen. The Android team explicitly considers the Domain layer optional; when a feature merely reads and renders data without transformations, routing through a pass-through UseCase that just delegates to a repository method introduces pointless boilerplate and navigation fatigue. In mature codebases, teams enforce modular Gradle boundaries where core domain has zero dependencies on database or network modules, preserving structural integrity while allowing pragmatic direct repository access for simple screens.""",
    "meta_ar": {
        "id": "ARC-02",
        "questionAr": "اشرح وظيفة طبقات العرض (Presentation) والدومين (Domain) والبيانات (Data) في أندرويد.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور كل طبقة من الطبقات الثلاث ومسؤولياتها المحددة، وكيفية تدفق البيانات أحادياً، ومعرفة الحالات التي تكون فيها طبقة الدومين ضرورية أو اختيارية.",
        "why_it_matters_ar": "خلط مسؤوليات العرض والبيانات داخل نفس الكلاس يؤدي إلى تسريب تفاصيل الشبكة وقواعد البيانات لواجهة المستخدم، وصعوبة هائلة في تعديل شكل الـ API أو دعم العمل بدون إنترنت.",
        "worked_example_ar": "توزيع كود التطبيق عبر الطبقات الثلاث بنمط تفاعلي نظيف:\n```kotlin\n// 1. Data Layer: المستودع يتعامل مع قاعدة البيانات والشبكة\nclass ArticleRepositoryImpl(private val api: Api, private val dao: Dao) : ArticleRepository {\n    override fun getArticles(): Flow<List<Article>> = dao.observe().map { it.toDomain() }\n}\n\n// 2. Domain Layer: منطق الأعمال الصافي في UseCase\nclass FilterArticlesUseCase(private val repo: ArticleRepository) {\n    operator fun invoke(): Flow<List<Article>> = repo.getArticles().map { it.filter { it.isValid } }\n}\n\n// 3. Presentation Layer: تحضير حالة الواجهة في ViewModel\nclass ArticlesViewModel(private val filterArticles: FilterArticlesUseCase) : ViewModel() {\n    val state = filterArticles().map { UiState.Success(it) }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), UiState.Loading)\n}\n```",
        "trade_offs_ar": "الفصل بين الطبقات الثلاث يمنح كوداً قابلاً للصيانة والاختبار المستقل وإعادة الاستخدام، ولكنه يتطلب كتابة نماذج بيانات متعددة ومحولات إضافية بين كل طبقة وأخرى.",
        "failure_modes_ar": "جعل الـ Presentation يعتمد مباشرة على DTOs قادمة من Retrofit، أو وضع كود التخزين في الكاش داخل الـ ViewModel بدلاً من طبقة الـ Data.",
        "production_perspective_ar": "في المشروعات الكبرى، نصمم طبقة الـ Data بمبدأ Offline-First حيث يكون Room هو المصدر الأوحد للحقيقة، وتعمل الـ Presentation على مراقبة تدفقات Flow القادمة من الداتا دون علم بكيفية المزامنة مع السيرفر.",
        "how_to_answer_ar": "اشرح كل طبقة بإيجاز ووضوح: العرض لعرض الحالة واستقبال التفاعل، والدومين لمنطق الأعمال المشترك، والداتا كمصدر وحيد للحقيقة، ثم وضح اتجاه تدفق البيانات أحادي الاتجاه والمفاضلة في استخدام الدومين.",
        "talking_points_ar": "مسؤولية كل طبقة، ومفهوم Single Source of Truth في طبقة البيانات، واستقلالية طبقة الدومين، وكيفية التعامل مع الـ Use Cases كطبقة اختيارية.",
        "follow_ups_ar": "- **المحاور:** \"لو التطبيق مفهوش غير عمليات CRUD بسيطة، هل نحتاج طبقة Domain؟\"\n  **المرشح:** \"لا، جوجل نفسها بتوصي بعدم إنشاء طبقة Domain لو مفيش Business Logic مركب؛ الـ ViewModel يقدر يكلم الـ Repository مباشرة، وده بيوفر كود كتير بدون أي إخلال بمبدأ فصل المسؤوليات.\"\n\n- **المحاور:** \"مين المسؤول عن اتخاذ قرار الكاش وعمل المزامنة في الخلفية؟\"\n  **المرشح:** \"طبقة البيانات (Data Layer) وتحديداً الـ Repository؛ هو اللي بيقرر يجيب الداتا من Room ولا يطلبها من الشبكة، والطبقات العليا بتشوف بس Flow فيه الداتا النهائية المحدثة.\"",
        "self_check_ar": "هل حددت بوضوح مسؤولية كل طبقة؟ هل ذكرت أن طبقة الدومين اختيارية؟ وهل بينت آلية تدفق البيانات الأحادية؟",
        "references_ar": f"- [Guide to app architecture - UI Layer](https://developer.android.com/topic/architecture/ui-layer) — توثيق طبقة العرض.\n- [Guide to app architecture - Data Layer](https://developer.android.com/topic/architecture/data-layer) — توثيق طبقة البيانات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "طبقة العرض مسؤولة عن عرض واجهة المستخدم ومعالجة الأحداث عبر الـ ViewModel والـ Compose. طبقة الدومين بتضم منطق الأعمال المعزول والقابل لإعادة الاستخدام عبر UseCases. وطبقة البيانات هي المصدر الأوحد للحقيقة بتدير قواعد البيانات والشبكة والكاش وراء واجهات الريبوزيتوري.",
        "best_answer_ar": "بناء تطبيقات أندرويد الحديثة بيعتمد على تقسيم التطبيق لثلاث طبقات أساسية لضمان سهولة التوسع وعزل المسؤوليات.\n\nطبقة العرض هي الواجهة الخارجية اللي المستخدم بيشوفها ويتفاعل معاها؛ بتشمل شاشات الـ Compose والـ ViewModels اللي بتجهز الـ UI State غير القابلة للتعديل وتستقبل ضغطات الأزرار من غير ما تاخد أي قرارات تخص قواعد العمل.\n\nطبقة الدومين هي وسيط اختياري بيكتب بكوتلن الصافية، بيحتوي على UseCases مستقلة هدفها تجميع قواعد العمل المعقدة، زي حسابات الخصومات أو تنسيق البيانات بين كذا ريبوزيتوري، بحيث نقدر نستخدم نفس المنطق في أكتر من شاشة أو في WorkManager.\n\nطبقة البيانات بتمثل المصدر الوحيد للحقيقة لكل داتا التطبيق. المستودعات بتنسق بين طلبات الشبكة وقواعد بيانات Room المحلية وبتدير استراتيجيات المزامنة والكاش، وبترجع نماذج دومين نقية ومستقرة للطبقات الأعلى بدون ما تكشف أي تفاصيل عن جداول الـ SQL أو مسارات الـ REST.",
        "deep_answer_ar": "تحت الكابوت، تقسيم الكود لطبقات العرض والدومين والبيانات بيحدد المسار الطبيعي لتدفق البيانات أحادي الاتجاه واستقرار البناء البرمجي. حركة البيانات بتمشي في حلقة منتظمة: المستخدم يضغط على زرار في Compose، الـ Event يوصل للـ ViewModel اللي يستدعي الـ UseCase، والـ UseCase يكلم الـ Repository، بينما الداتا المحدثة بتتدفق في مسار عكسي كـ Flow مستمر من طبقة البيانات للـ ViewModel اللي يحولها لـ UI State تعرضه الشاشة.\n\nطبقة البيانات بتعزل تفاصيل التخزين تماماً؛ سواء الداتا جاية من كاش في الذاكرة أو قاعدة بيانات Room مشفرة أو سيرفر خارجي، الريبوزيتوري بيعرض نفس الـ Flow الموحد بنماذج الدومين، وبيتكفل بإعادة المحاولات عند انقطاع الإنترنت وسياسات التخزين المؤقت بحيث الطبقات العليا تفضل شغالة بسلاسة.\n\nطبقة الدومين بتمنع تكرار الكود البرمجي؛ فلو عندنا عملية معقدة زي التحقق من صلاحية بطاقة الائتمان ومطابقة الرصيد، بنحطها في UseCase واحد نقدر نشغله من شاشة الشراء أو من خدمة في الخلفية ونختبره على JVM في ثوانٍ.\n\nالمهندسون المتمرسون بيتجنبوا التطبيق الأعمى للطبقات الثلاثة في كل شاشة؛ فطالما الميزة بتعرض بيانات مباشرة من غير أي تعديل، تمرير الداتا عبر UseCase فارغ بيعتبر تكلفة كود غير مبررة ويفضل وقتها الاتصال المباشر بين الـ ViewModel والـ Repository."
    }
}

# ==========================================
# ARC-03: Dependency Rule
# ==========================================
DATA["ARC-03"] = {
    "concept_en": """The Dependency Rule is the central governance constraint of Clean Architecture: source code dependencies must point exclusively inward, toward higher-level policies and business entities. Inner layers (Domain) must have zero knowledge of outer layers (Presentation, Data, Frameworks, Database, Network), meaning no name, interface, function, or data type declared in an outer circle can be mentioned or imported by an inner circle. To enable inner business logic to communicate with external data sources or dispatch UI callbacks without violating this rule, architects apply the Dependency Inversion Principle (DIP). The inner domain layer declares abstract repository interfaces representing its requirements, while the outer data layer implements those contracts and converts external payloads into domain models. Inversion of control is resolved at application startup using dependency injection frameworks like Hilt or Dagger.""",
    "walkthrough_en": """Enforcing inward dependencies via Dependency Inversion in Kotlin:
```kotlin
// ==========================================
// INNER CIRCLE: :core:domain (Pure Kotlin)
// ==========================================
data class PaymentTransaction(val id: String, val amount: Double, val status: String)

// Domain declares the contract it needs; knows NOTHING about Retrofit or Room
interface PaymentGateway {
    suspend fun executePayment(amount: Double): Result<PaymentTransaction>
}

class ProcessPaymentUseCase(private val gateway: PaymentGateway) {
    suspend operator fun invoke(amount: Double): Result<PaymentTransaction> {
        if (amount <= 0.0) return Result.failure(IllegalArgumentException("Amount must be positive"))
        return gateway.executePayment(amount)
    }
}

// ==========================================
// OUTER CIRCLE: :core:data (Depends on :core:domain)
// ==========================================
class StripePaymentGateway(
    private val stripeApi: StripeApi // Retrofit dependency lives OUTSIDE
) : PaymentGateway { // Implements inward domain interface!
    override suspend fun executePayment(amount: Double): Result<PaymentTransaction> = runCatching {
        val response = stripeApi.charge(StripeChargeRequest(amount))
        response.toDomainTransaction()
    }
}
```""",
    "short_en": """Dependencies must point strictly inward toward pure business logic. Domain depends on nothing; Data and Presentation depend on Domain. We invert control using interfaces declared in Domain and implemented in Data, keeping core business policies completely insulated from framework volatility and third-party libraries.""",
    "structured_en": """To begin with, the Dependency Rule is the foundational governance principle of Clean Architecture dictating that source code dependencies must point exclusively inward.
From an architectural standpoint, inner layers represent high-level business policies and domain models, while outer layers represent volatile implementation mechanisms like UI frameworks, Room databases, and Retrofit network clients. The inner domain layer must know nothing about the outer layers, meaning no class in domain can import classes from data or presentation.
In production scenarios, when the domain layer requires information from an external database or network endpoint, it enforces the Dependency Inversion Principle. The domain layer declares an abstract repository interface representing the required business contract, and the outer data layer implements that interface.
As for dependency injection, frameworks like Dagger and Hilt wire the concrete data implementation into the domain consumer at runtime, keeping compile-time dependencies strictly pointed inward while runtime execution flows outward to external drivers.""",
    "deep_senior_en": """Under the hood, the Dependency Rule decouples the lifespan of core business rules from external technology stacks. In traditional layered architectures, business logic frequently imported database DAOs or network models directly, creating a downstream dependency on third-party libraries and database schema definitions. When libraries change or APIs deprecate, business logic breaks.
By enforcing an inward dependency direction, the domain layer defines its own stable contracts and models. The outer data layer references the domain module and maps external DTOs into domain entities before returning them. This inversion ensures that updating from Retrofit to Ktor or switching from Room to SQLDelight requires zero changes inside domain use cases or business validation rules.
In modular Android architectures, this rule is strictly enforced by Gradle dependency graphs. The core domain module has no implementation dependency on data or presentation. Instead, app and data modules depend on domain, making accidental cyclic dependencies or illegal framework imports fail at compile time.
Staff engineers pay close attention to boundary leaks where developers define domain repository interfaces that inadvertently leak external types—such as Retrofit Response objects or Room exceptions—into domain method signatures. True inward dependency requires all exceptions and responses to be mapped into domain-safe results before crossing the architectural boundary. This ensures complete isolation and allows enterprise applications to swap infrastructure layers with zero regression risk.""",
    "meta_ar": {
        "id": "ARC-03",
        "questionAr": "ما هي قاعدة التبعية (Dependency Rule)، وفي أي اتجاه يجب أن تشير الاعتماديات؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم قاعدة التبعيات للداخل، وإدراك كيفية تطبيق مبدأ قلب التبعيات (Dependency Inversion)، والقدرة على حماية طبقة الدومين من تسريب كائنات أطر العمل الخارجية.",
        "why_it_matters_ar": "إذا أشارت التبعيات للخارج، فإن أي تعديل في مكتبة شبكة مثل Retrofit أو قاعدة بيانات Room سيكسر قواعد عمل التطبيق، مما يفقد النظام مرونته ويجعل اختباراته بطيئة ومعقدة.",
        "worked_example_ar": "تطبيق قلب التبعيات؛ الدومين يحدد الواجهة وطبقة البيانات تنفذها:\n```kotlin\n// Domain: يعرف العقد فقط ولا يعلم شيئاً عن Retrofit\ninterface AuthRepository {\n    suspend fun login(creds: Credentials): Result<User>\n}\n\n// Data: تعتمد على الدومين وتنفذ الواجهة في الموديول الخارجي\nclass AuthRepositoryImpl(private val api: AuthApi) : AuthRepository {\n    override suspend fun login(creds: Credentials): Result<User> = runCatching {\n        api.login(creds.toDto()).toDomain()\n    }\n}\n```",
        "trade_offs_ar": "قاعدة التبعيات تعزل التطبيق وتسهل استبدال المكتبات بدون لمس منطق العمل، لكنها تتطلب كتابة واجهات ومحولات وحقن تبعيات إضافي يزيد من عدد الملفات في المشروع.",
        "failure_modes_ar": "تسريب استثناءات أو كائنات خارجية داخل دوال الدومين، مثل إرجاع `retrofit2.Response` أو `java.sql.SQLException` داخل واجهة معرفة في الدومين.",
        "production_perspective_ar": "في المشروعات الكبرى، نفرض هذه القاعدة عبر إعدادات موديولات Gradle؛ موديول الدومين لا يحتوي على أي dependency على موديول الداتا أو البريزنتيشن، وبالتالي يرفض الكومبايلر أي تسريب تلقائياً.",
        "how_to_answer_ar": "اذكر بوضوح أن التبعيات يجب أن تتجه دائماً للداخل نحو منطق العمل. اشرح دور Dependency Inversion في تعريف الواجهات في الدومين وتنفيذها في الداتا، ثم بيّن دور Hilt في حقنها وقت التشغيل.",
        "talking_points_ar": "اتجاه التبعية نحو الداخل، واستخدام Polymorphism لقلب التحكم، وحماية الدومين من كائنات المكتبات الخارجية، وتطبيق قيود Gradle لمنع المخالفات المعمارية.",
        "follow_ups_ar": "- **المحاور:** \"لو الدومين ميعرفش حاجة عن الداتا، إزاي بيكلم قاعدة البيانات وقت التشغيل؟\"\n  **المرشح:** \"عن طريق مبدأ قلب التبعيات (Dependency Inversion)؛ الدومين بيعرف Interface بتحدد طلباته، وطبقة الداتا بتعمل Implement للواجهة دي، وبنستخدم Hilt أو Dagger علشان يحقن كائن الداتا الفعلي وقت التشغيل.\"\n\n- **المحاور:** \"إيه أشهر خطأ بيقع فيه المطورين بيكسر قاعدة التبعيات دي؟\"\n  **المرشح:** \"إن المطور يرجع كائنات مكتبات خارجية جوه دوال الواجهة في الدومين، زي إنه يرجع `Response<T>` من Retrofit أو يرمي `SQLiteException`، الصح إن كل التفاصيل دي تتحول لكائنات ونتائج تابعة للدومين.\"",
        "self_check_ar": "هل أكدت على اتجاه التبعيات للداخل حصراً؟ هل شرحت مبدأ قلب التبعيات؟ وهل وضحت كيفية منع تسريب كائنات المكتبات الخارجية؟",
        "references_ar": f"- [The Clean Code Blog: The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) — مقال قاعدة التبعيات.\n- [Dependency inversion principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle) — المفهوم الأكاديمي لقلب التبعيات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "التبعيات البرمجية لازم تتجه كلها حصراً للداخل نحو منطق الأعمال الأساسي. طبقة الدومين لا تعتمد على أي طبقة أخرى، بينما طبقات العرض والبيانات تعتمد على الدومين. بنقلب اتجاه التحكم بتعريف واجهات في الدومين وتنفيذها في طبقة البيانات لعزل الكود تماماً عن تقلبات المكتبات الخارجية.",
        "best_answer_ar": "قاعدة التبعية هي القانون الحاكم في العمارة النظيفة، ومفادها إن كل خطوط الاعتمادية في الكود لازم تشير للداخل نحو السياسات وقواعد العمل الأكثر استقراراً.\n\nالطبقات الداخلية زي الدومين بتمثل جوهر التطبيق، ومينفعش تعرف أي حاجة عن الطبقات الخارجية زي واجهات المستخدم أو قواعد بيانات Room أو نداءات Retrofit. وده معناه إن مفيش كلاس في الدومين يقدر يستورد أي كلاس أو نوع بيانات متعرف في طبقة البيانات أو العرض.\n\nعلشان الدومين يقدر يطلب بيانات من قاعدة بيانات أو سيرفر من غير ما يكسر القاعدة دي، بنستخدم مبدأ قلب التبعيات؛ الدومين بيعرف واجهة برمجية مجردة بتعبر عن احتياجاته، وطبقة البيانات هي اللي بتنفذ الواجهة دي في موديول خارجي.\n\nوقت تشغيل التطبيق، محركات حقن التبعيات زي Hilt أو Dagger بتقوم بتوصيل كائن التنفيذ الفعلي بالدومين، وبكده بنحافظ على اتجاه الاعتمادية للداخل وقت الترجمة والكومبايل مع تدفق التنفيذ الفعلي للأجهزة الخارجية.",
        "deep_answer_ar": "تحت الكابوت، قاعدة التبعية بتفصل عمر منطق الأعمال الافتراضي عن عمر المكتبات وأطر العمل الخارجية. في المعماريات القديمة، منطق التطبيق كان بيستورد كلاسات الـ DAO أو موديلات الـ Network مباشرة، وده كان بيخلي قواعد البزنس تابعة وخاضعة لتغييرات الـ Schema وجداول الـ SQLite.\n\nلما بنجبر كل التبعيات تتجه للداخل، طبقة الدومين بتحدد العقود والموديلات الخاصة بيها بمنتهى النقاء والاستقرار. موديول الداتا هو اللي بيعتمد على الدومين وبيحول الـ DTOs لنماذج دومين قبل ما يرجعها؛ الترتيب ده بيضمن إننا لو غيرنا مكتبة الشبكة من Retrofit لـ Ktor، أو استبدلنا Room بـ SQLDelight، الدومين ومعه كل الـ Use Cases هيفضل شغال بدون تغيير سطر كود واحد.\n\nفي المشاريع الكبيرة المبنية على موديولات Gradle متعددة، بنفرض القاعدة دي برمجياً؛ موديول الدومين مبيكونش جواه أي implementation لموديول الداتا، وبكده أي استيراد خاطئ لكلاس خارجي بيترفض فوراً أثناء الـ Build.\n\nالمهندسون الكبار بيركزوا جداً على منع تسريب الأنواع الخارجية في عقود الدومين؛ فمينفعش واجهة في الدومين ترجع كائن Response من رتروفيت أو تسرب SQLiteException، لأن الحفاظ على نقاء العقود بيضمن استقلالية التطبيق وسرعة اختباراته على مدار السنين. وده بيتيح تشغيل مئات الاختبارات المعزولة في ثوانٍ معدودة بدون الحاجة لأي إيموليتور أو تهيئة لبيئة أندرويد المعقدة."
    }
}

# ==========================================
# ARC-04: Repository vs UseCase
# ==========================================
DATA["ARC-04"] = {
    "concept_en": """The Repository pattern and Use Cases (Interactors) represent two complementary architectural abstractions with clearly separated concerns. A Repository belongs to the Data layer and acts as an in-memory collection of domain entities, abstracting underlying data sources (remote network, local database, in-memory caches, datastores) behind clean interfaces. Its responsibility is data access, data synchronization, offline caching policies, and mapping raw storage payloads into domain models. A Use Case resides in the Domain layer and encapsulates a single, granular, reusable unit of business logic or orchestration across repositories. Representing a specific user or system action, a Use Case enforces domain validation rules, coordinates multi-step transactions, and executes domain algorithms without knowledge of UI lifecycles or transport protocols.""",
    "walkthrough_en": """Contrasting a Repository and an orchestrating Use Case in Kotlin:
```kotlin
// 1. Repository: Manages data access, caching, and synchronization
interface CartRepository {
    fun observeCart(): Flow<Cart>
    suspend fun clearCart()
}

interface PaymentRepository {
    suspend fun processPayment(orderId: String, amount: Double): Result<TransactionReceipt>
}

// 2. Use Case: Coordinates business workflow across both repositories
class CheckoutUseCase(
    private val cartRepository: CartRepository,
    private val paymentRepository: PaymentRepository
) {
    suspend operator fun invoke(orderId: String): Result<TransactionReceipt> {
        val currentCart = cartRepository.observeCart().first()
        if (currentCart.items.isEmpty()) {
            return Result.failure(IllegalStateException("Cannot checkout with an empty cart"))
        }
        val totalAmount = currentCart.calculateTotalWithTax()
        val paymentResult = paymentRepository.processPayment(orderId, totalAmount)

        if (paymentResult.isSuccess) {
            cartRepository.clearCart() // State transition upon successful business transaction
        }
        return paymentResult
    }
}
```""",
    "short_en": """A Repository abstracts data sources and caching, presenting a unified collection of domain entities to the application. A UseCase encapsulates a single, focused piece of business logic or orchestration across repositories, representing an actionable user intent.""",
    "structured_en": """To begin with, Repositories and UseCases serve distinct responsibilities within Clean Architecture, separating data management from business execution.
From an architectural standpoint, the Repository pattern mediates between domain logic and disparate data sources like network endpoints, local databases, and memory caches. It exposes clean domain models, implements caching strategies, and acts as the application's single source of truth without exposing SQL queries or HTTP endpoints.
In production scenarios, a UseCase—often called an Interactor—encapsulates a single business task or transaction, such as transferring funds, validating a promo code, or syncing offline edits. It typically exposes an operator invoke function, orchestrating one or more repositories while executing pure business rules.
As for ownership, UseCases prevent ViewModels from becoming bloated coordination centers, allowing critical business workflows to be reused consistently across multiple screens, background workers, or app shortcuts without duplicating validation logic.""",
    "deep_senior_en": """Under the hood, the combination of Repositories and UseCases creates a robust separation between data orchestration and business decision-making. A well-designed Repository manages data synchronization mechanics: it decides whether to emit cached records from Room immediately while triggering a background Retrofit fetch, handles token refreshes, and resolves optimistic write conflicts. By exposing reactive streams via Flow, it keeps the rest of the application synchronized with data mutations.
UseCases, on the other hand, sit above Repositories and should never contain data-caching or transport logic. A UseCase receives domain parameters, validates business constraints, coordinates calls to multiple repositories, and applies domain calculations. For instance, a CheckoutUseCase might call CartRepository to retrieve items, PaymentRepository to execute a transaction, and AnalyticsRepository to record telemetry, wrapping the entire multi-step operation in a transactional domain Result.
Staff engineers adhere to strict naming conventions and architectural discipline: UseCases are named as verbs in present tense and contain a single public operator invoke function. If a UseCase merely forwards a call to a repository without applying business logic, formatting, or coordination, it is an architectural anti-pattern known as a pass-through UseCase. In such scenarios, senior engineers allow ViewModels to observe the Repository directly to eliminate pointless indirection while maintaining complete testability. This pragmatic approach preserves productivity without compromising architectural cleanlines.""",
    "meta_ar": {
        "id": "ARC-04",
        "questionAr": "ما هو نمط المستودع (Repository Pattern)؟ وما هي حالة الاستخدام (UseCase)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على التمييز الدقيق بين إدارة مصادر البيانات وإدارة قواعد الأعمال، ومعرفة متى يتم إنشاء UseCase ومتى يكتفى بالتعامل المباشر مع الـ Repository.",
        "why_it_matters_ar": "الخلط بينهما يجعل الـ Repository يحتوي على منطق شاشات محددة أو يجعل الـ UseCase يدير الكاش والاتصال بالسيرفر، مما يسبب تكرار الكود وفقدان السيطرة على البيانات.",
        "worked_example_ar": "تنسيق عملية الشراء عبر UseCase يستدعي اثنين ريبوزيتوري:\n```kotlin\nclass CheckoutUseCase(\n    private val cartRepo: CartRepository,\n    private val paymentRepo: PaymentRepository\n) {\n    suspend operator fun invoke(orderId: String): Result<Receipt> {\n        val cart = cartRepo.getCart()\n        if (cart.isEmpty()) return Result.failure(IllegalStateException(\"Empty cart\"))\n        val res = paymentRepo.pay(orderId, cart.total)\n        if (res.isSuccess) cartRepo.clear()\n        return res\n    }\n}\n```",
        "trade_offs_ar": "استخدام UseCase يعزل خطوات الأعمال المعقدة ويسهل إعادة استخدامها بين شاشات مختلفة، لكن إنشاء UseCase فارغة لكل دالة في الريبوزيتوري يسبب زيادة هائلة في الملفات دون فائدة ملموسة.",
        "failure_modes_ar": "وضع منطق الكاش أو استدعاء Retrofit داخل UseCase، أو وضع منطق حسابات البزنس المالي داخل كلاس Repository.",
        "production_perspective_ar": "في المشروعات الحقيقية، نطبق مبدأ الدالة الواحدة `operator fun invoke` في كل UseCase، ونمنع الـ ViewModels من تنسيق المعاملات المعقدة متعددة المصادر بأنفسهم لضمان تجربة اختبارات وحدة سريعة ونقية.",
        "how_to_answer_ar": "عرف الـ Repository بأنه المسؤول عن جلب وتخزين ومزامنة البيانات كمصدر وحيد للحقيقة، وعرف الـ UseCase بأنه يمثل فعل محدد في منطق الأعمال ينسق العمليات، وحذر من مصيدة الـ Pass-through UseCases.",
        "talking_points_ar": "مسؤولية المستودع في إدارة مصادر الداتا، ومسؤولية حالة الاستخدام في تطبيق قواعد البزنس، وصيغة التسمية كأفعال، وتجنب الـ Pass-through UseCases.",
        "follow_ups_ar": "- **المحاور:** \"إمتى نعتبر إنشاء UseCase مجرد زيادة كود ملهاش لازمة؟\"\n  **المرشح:** \"لو الـ UseCase مبيعملش أي حاجة غير إنه ينادي دالة واحدة في الريبوزيتوري ويرجع النتيجة زي ما هي بدون أي تحقق أو فلترة أو تنسيق؛ في الحالة دي بنسميه Pass-through UseCase وبيزود تعقيد المشروع بدون أي قيمة، والأفضل الـ ViewModel يكلم الريبوزيتوري مباشرة.\"\n\n- **المحاور:** \"هل الـ UseCase ممكن يعتمد على UseCase تانية؟\"\n  **المرشح:** \"نعم، لو في عملية مركبة بتعتمد على عملية أعمال فرعية مشتركة، مفيش مانع معماري من حقن UseCase داخل UseCase تانية في نفس طبقة الدومين، طالما مفيش تكرار دوري (Circular Dependency).\"",
        "self_check_ar": "هل فرقت بوضوح بين مسؤولية البيانات ومسؤولية منطق الأعمال؟ هل ذكرت نمط operator fun invoke؟ وهل نبهت إلى مشكلة الـ Pass-through UseCases؟",
        "references_ar": f"- [Guide to app architecture - Domain Layer](https://developer.android.com/topic/architecture/domain-layer) — توثيق جوجل لطبقة الدومين وحالات الاستخدام.\n- [Repository pattern](https://developer.android.com/topic/architecture/data-layer#repositories) — توثيق جوجل لنمط المستودع.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "المستودع (Repository) بيعزل مصادر البيانات المختلفة ويدير الكاش والمزامنة كمصدر وحيد للحقيقة للبيانات. بينما حالة الاستخدام (UseCase) بتمثل خطوة أو عملية محددة في منطق الأعمال بتنفذ شروط البزنس وتنسق العمل بين أكتر من مستودع لخدمة هدف المستخدم.",
        "best_answer_ar": "الـ Repository والـ UseCase بيمثلوا مفهومين بيكملوا بعض في العمارة النظيفة مع فصل تام في المسؤوليات.\n\nنمط المستودع بيعيش في طبقة البيانات، ودوره إنه يكون المصدر الأوحد للحقيقة لكل ما يخص جلب وحفظ البيانات. هو اللي بينسق بين شبكة الإنترنت وقاعدة بيانات Room المحلية وسياسات الكاش والـ Offline-first، وبيرجع للمستويات الأعلى نماذج دومين نقية بدون ما يكشف أي تفاصيل عن الـ SQL أو مسارات الـ HTTP.\n\nفي المقابل، الـ UseCase بتعيش في قلب طبقة الدومين وبتمثل عملية بزنس محددة وقابلة لإعادة الاستخدام، زي إتمام عملية الشراء أو حساب الخصومات للمستخدمين المميزين. هي اللي بتطبق شروط التحقق من صحة المدخلات وتنسق العمليات متعدية المصادر.\n\nاستخدام الـ UseCases بيحمي الـ ViewModels من التضخم وبيمنع تكرار منطق الأعمال لو نفس الميزة محتاجين نشغلها من شاشة تانية أو من خلال خلفية النظام عبر WorkManager.",
        "deep_answer_ar": "تحت الكابوت، التكامل بين الـ Repository والـ UseCase بيخلق فصلاً هندسياً دقيقاً بين إدارة تدفق البيانات واتخاذ قرارات الأعمال. المستودع المصمم باحترافية بيدير آليات التزامن المعقدة؛ فهو اللي بيقرر يعرض الداتا المحفوظة في Room فوراً عبر Flow بينما في نفس الوقت بيبعت طلب في الخلفية لـ Retrofit لتحديث السجلات، وبيتعامل مع تجديد الـ Auth Tokens وحل تعارض البيانات.\n\nالـ UseCases مستواها أعلى من المستودعات ومينفعش تحتوي على أي كود يخص الكاش أو تفاصيل التخزين. هي بتستقبل مدخلات العملية، وتتحقق من مطابقتها لقواعد العمل، وتستدعي أكتر من ريبوزيتوري لتنفيذ المعاملة في سياق متكامل. على سبيل المثال، عملية CheckoutUseCase بتطلب محتويات السلة من CartRepository، وتنفذ عملية الدفع من PaymentRepository، وتسجل الحدث في AnalyticsRepository، وترجع في النهاية كائن Result موحد.\n\nالمهندسون الكبار بيتبعوا معايير صارمة في التسمية باستخدام أفعال صريحة وكتابة دالة عامة واحدة هي operator fun invoke. وبيحذروا دائماً من مصيدة الـ Pass-through UseCase؛ فلو الـ UseCase مجرد وسيط فارغ بيمرر استدعاء دالة واحدة في الريبوزيتوري بدون أي منطق أعمال أو فلترة، بيعتبر وجودها زيادة في التعقيد، والحل الهندسي السليم وقتها هو السماح للـ ViewModel بمراقبة الريبوزيتوري مباشرة للحفاظ على بساطة وسرعة المشروع مع إبقاء الكود قابلاً للاختبار بنسبة مئة بالمئة."
    }
}

# ==========================================
# ARC-05: ViewModel vs UseCase vs Repository
# ==========================================
DATA["ARC-05"] = {
    "concept_en": """Architectural boundary discipline dictates clear responsibility allocation among ViewModel, UseCase, and Repository to prevent God classes and maintain modular cohesion. The ViewModel (Presentation) acts as a lifecycle-aware state holder that manages UI state production, handles user interactions, triggers navigation events, survives configuration changes, and formats domain data into presentation models. It must never reference View hierarchies, hold Android Activity Context, or execute business transactions directly. The UseCase (Domain) encapsulates single-responsibility, framework-agnostic business logic, mathematical computations, input validation rules, and cross-repository orchestration. The Repository (Data) serves as the authoritative single source of truth for an aggregate entity, mediating between remote APIs, local databases, and caches while managing data synchronization, offline persistence, and entity mapping.""",
    "walkthrough_en": """Mapping clear separation of concerns in a funds transfer feature:
```kotlin
// 1. DATA LAYER: Data synchronization and remote execution
class TransferRepositoryImpl(private val api: BankingApi, private val dao: AccountDao) : TransferRepository {
    override suspend fun sendMoney(recipientId: String, amount: Double): Result<TransactionId> = runCatching {
        api.postTransfer(TransferRequest(recipientId, amount)).toDomain()
    }
}

// 2. DOMAIN LAYER: Pure business validation and orchestration
class SendMoneyUseCase(
    private val accountRepo: AccountRepository,
    private val transferRepo: TransferRepository
) {
    suspend operator fun invoke(recipientId: String, amount: Double): Result<TransactionId> {
        if (amount <= 0.0) return Result.failure(IllegalArgumentException("Amount must exceed zero"))
        val balance = accountRepo.getCurrentBalance()
        if (balance < amount) return Result.failure(IllegalStateException("Insufficient funds"))
        return transferRepo.sendMoney(recipientId, amount)
    }
}

// 3. PRESENTATION LAYER: UI state management and user action dispatch
class TransferViewModel(
    private val sendMoneyUseCase: SendMoneyUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow<TransferUiState>(TransferUiState.Idle)
    val uiState: StateFlow<TransferUiState> = _uiState.asStateFlow()

    fun onTransferConfirmed(recipientId: String, rawAmount: String) {
        val amount = rawAmount.toDoubleOrNull() ?: run {
            _uiState.value = TransferUiState.Error("Invalid amount format")
            return
        }
        viewModelScope.launch {
            _uiState.value = TransferUiState.Loading
            sendMoneyUseCase(recipientId, amount)
                .onSuccess { _uiState.value = TransferUiState.Success(it.value) }
                .onFailure { _uiState.value = TransferUiState.Error(it.localizedMessage ?: "Transfer failed") }
        }
    }
}
```""",
    "short_en": """ViewModel holds and manages UI state, responding to user actions and surviving configuration changes. UseCase encapsulates specific business rules and multi-repository workflows. Repository manages data sources, caching policies, and data synchronization as a single source of truth.""",
    "structured_en": """To begin with, assigning responsibilities cleanly across ViewModel, UseCase, and Repository prevents monolithic classes and keeps codebases maintainable.
From an architectural standpoint, the ViewModel is a presentation state holder that lives in the presentation layer. It manages UI state lifecycles, observes domain streams, translates raw business data into display-ready UI models, and processes user events while surviving screen rotations.
In production scenarios, the UseCase resides in the domain layer and owns pure business logic. It handles calculations, domain validations, authorization checks, and orchestrates workflows that touch multiple repositories.
As for the Repository, it belongs to the data layer and acts as the single source of truth for an aggregate entity. It coordinates remote network calls, Room database caching, offline synchronization, and local storage, ensuring upper layers remain unaware of whether data originates from memory, disk, or the cloud.""",
    "deep_senior_en": """Under the hood, drawing explicit boundaries between ViewModel, UseCase, and Repository ensures high cohesion and localized failure modes. A common architectural smell in Android applications is the Fat ViewModel, where developers place network API calls, database queries, and business calculations directly inside ViewModel coroutines. This tightly couples presentation logic with business rules, making automated testing cumbersome and causing memory leaks if Android Context is captured.
The rule of thumb for placement is clear: if a concern relates to how data is displayed, screen lifecycle, or navigation events, it belongs in the ViewModel. If a rule must execute regardless of whether the request came from a Composable, a WearOS notification, or a WorkManager background job—such as validating an account balance before a transfer—it belongs in a UseCase. If logic decides whether to read from SQLite or fetch fresh JSON over HTTP, it belongs in the Repository.
Staff engineers enforce that ViewModels never reference Android View hierarchies, Activity contexts, or database DAOs. Furthermore, Repositories never expose UI-specific models or framework errors; they catch low-level IOExceptions and SQLiteExceptions, translating them into domain-safe failure abstractions before passing them upward. This strict separation guarantees that features remain robust, testable, and adaptable to future platform changes.""",
    "meta_ar": {
        "id": "ARC-05",
        "questionAr": "ما الذي ينتمي إلى ViewModel مقابل UseCase مقابل Repository في تطبيقات أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على وضع كل مسؤولية برمجية في مكانها الدقيق لمنع تضخم الكلاسات، ومعرفة حدود التعامل مع دورة حياة أندرويد، وفهم معايير فصل منطق الواجهة عن منطق الأعمال والبيانات.",
        "why_it_matters_ar": "خلط هذه المسؤوليات ينتج كلاسات ضخمة (God ViewModels) يستحيل اختبارها، وتسرب كائنات الـ Context مما يسبب تسريب الذاكرة وتعطل التطبيق عند تغيير اتجاه الشاشة.",
        "worked_example_ar": "توزيع مهام تحويل الأموال بدقة:\n```kotlin\n// Repo: مسؤوليته استدعاء الـ API وحفظ المعاملة محلياً\ninterface TransferRepo { suspend fun send(to: String, amount: Double): Result<Id> }\n\n// UseCase: مسؤوليته التحقق من كفاية الرصيد قبل التحويل\nclass TransferMoneyUseCase(val acc: AccountRepo, val transfer: TransferRepo) {\n    suspend operator fun invoke(to: String, amt: Double) = if (acc.getBalance() >= amt) transfer.send(to, amt) else Result.failure(Exception(\"No balance\"))\n}\n\n// ViewModel: مسؤوليته تحويل النص لرقم وإدارة حالة التحميل والخطأ\nclass TransferViewModel(val useCase: TransferMoneyUseCase) : ViewModel() {\n    fun onSend(to: String, txt: String) { viewModelScope.launch { useCase(to, txt.toDouble()) } }\n}\n```",
        "trade_offs_ar": "الفصل الصارم بين الكلاسات الثلاثة يضمن قابلية اختبار استثنائية وسهولة في الصيانة والتعديل، لكنه يتطلب تمرير وسائط متعددة وكتابة تعريفات إضافية لكل تدفق بيانات.",
        "failure_modes_ar": "تخزين مراجع لـ Activity أو View داخل ViewModel، أو كتابة استعلامات SQL وطلبات Retrofit مباشرة داخل ViewModel دون المرور بالـ Repository.",
        "production_perspective_ar": "في الفرق الهندسية الكبرى، نضع معايير كود صارمة تمنع احتواء ViewModel على أكثر من 300 سطر كود، وتفرض أن تكون كل الحسابات المالية وشروط الأعمال داخل UseCases نقية ومختبرة بنسبة تغطية 100%.",
        "how_to_answer_ar": "قسم الإجابة بوضوح إلى ثلاثة محاور: الـ ViewModel لحالة الواجهة والأحداث، والـ UseCase لمنطق الأعمال والتحقق المشترك، والـ Repository لجلب البيانات والكاش والمزامنة.",
        "talking_points_ar": "مسؤولية كل مكون، وقاعدة الفصل الذهبية، ومخاطر الـ Fat ViewModel، وضمان عدم تسريب كائنات الـ Context إلى الـ ViewModel.",
        "follow_ups_ar": "- **المحاور:** \"لو محتاجين نترجم رسالة خطأ جاية من السيرفر، نعمل ده في ViewModel ولا UseCase؟\"\n  **المرشح:** \"الترجمة والتنسيق للعرض مكانهم الـ ViewModel، الـ UseCase بترجع سبب الخطأ كـ Domain Error أو Enum محايد، والـ ViewModel هو اللي بيحوله لـ String Resource مناسب للغة جهاز المستخدم علشان نحافظ على الدومين مستقل عن كلاسات أندرويد.\"\n\n- **المحاور:** \"إيه الحل لو الـ ViewModel بدأ يتضخم ويوصل لألف سطر كود؟\"\n  **المرشح:** \"ده مؤشر قوي على خلط المسؤوليات؛ الحل هو استخراج منطق الأعمال في UseCases مستقلة، وتوزيع الشاشة لو كانت معقدة لـ ViewModels أصغر خاصة بكل قسم فرعي من الشاشة.\"",
        "self_check_ar": "هل حددت مكان كل مسؤولية بدقة؟ هل حذرت من الـ Fat ViewModel؟ وهل وضحت أين تتم ترجمة وتنسيق النصوص لواجهة المستخدم؟",
        "references_ar": f"- [Guide to app architecture - UI layer](https://developer.android.com/topic/architecture/ui-layer) — توثيق جوجل الرسمي لمسؤوليات طبقة الواجهة والـ ViewModel.\n- [Common architectural mistakes in Android](https://medium.com/androiddevelopers/common-android-architecture-mistakes-6a682859942a) — مقال فريق أندرويد حول الأخطاء المعمارية الشائعة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ ViewModel بيتحكم في حالة واجهة المستخدم واستقبال تفاعل الشاشة والنجاة من تدوير الجهاز. والـ UseCase بيضم شروط وقواعد العمل المعزولة وتنسيق العمليات بين المستودعات. والـ Repository بيدير جلب البيانات والكاش والمزامنة كمصدر وحيد للحقيقة.",
        "best_answer_ar": "توزيع المسؤوليات بدقة بين ViewModel و UseCase و Repository هو الأساس اللي بيحمي المشروع من مشكلة الكلاسات العملاقة المعقدة.\n\nالـ ViewModel بيعيش في طبقة العرض ومسؤوليته إدارة دورة حياة شاشات العرض؛ هو اللي بيراقب تدفقات البيانات، ويحول أرقام الدومين لنصوص وصور جاهزة للعرض على الشاشة، ويتعامل مع ضغطات المستخدم مع الحفاظ على حالته عند تدوير الموبايل.\n\nالـ UseCase بيعيش في قلب طبقة الدومين ومسؤوليته الحصرية هي منطق الأعمال النقي؛ زي التحقق من الشروط البنكية، والتأكد من صحة المدخلات، وتنسيق الخطوات بين كذا ريبوزيتوري، بدون ما يعرف أي حاجة عن دورة حياة أندرويد.\n\nالـ Repository بيعيش في طبقة البيانات ودوره يكون المصدر الموثوق الوحيد لكل داتا التطبيق؛ هو اللي بيقرر امتى يطلب البيانات من السيرفر وامتى يقراها من قاعدة البيانات المحلية، وبيتكفل بعمليات الكاش وتحويل البيانات الخام لنماذج دومين مستقرة.",
        "deep_answer_ar": "تحت الكابوت، رسم حدود واضحة بين ViewModel و UseCase و Repository بيمنع انهيار النظام ويخلي تحديد أماكن الأخطاء عملية مباشرة. أحد أشهر الأخطاء الشائعة في أندرويد هو تضخم الـ ViewModel وتحوله لـ Fat ViewModel، وده بيحصل لما المطور يكتب جواه نداءات الـ API واستعلامات الـ SQL وحسابات البزنس المعقدة، فبينتج عنه كلاس ضخم مرتبط بدورة حياة الشاشة ويستحيل اختباره بشكل معزول.\n\nالقاعدة الذهبية لتوزيع الكود واضحة وبسيطة: لو الحاجة مرتبطة بطريقة عرض البيانات على الشاشة أو التنقل بين الصفحات أو الحفاظ على الحالة أثناء تدوير الجهاز، مكانها الـ ViewModel. لو الشرط لازم يتنفذ في كل الأحوال بصرف النظر عن مين اللي طلبه، سواء كانت شاشة Compose أو إشعار أو مهمة في الخلفية عبر WorkManager، مكانه الـ UseCase. لو الكود بيتعامل مع كاش محلي أو قراءة جداول من SQLite أو نداءات شبكة عبر HTTP، مكانه الـ Repository.\n\nالمهندسون الكبار بيحرصوا على منع الـ ViewModel من استيراد أي كلاسات تخص واجهات أندرويد أو تخزين مراجع للـ Context تجنباً لتسريب الذاكرة، كما يمنعون الـ Repository من تسريب استثناءات الشبكة وقواعد البيانات، بحيث تتحول لأخطاء دومين مفهومة وآمنة قبل ما تطلع للطبقات الأعلى. والتنظيم الصارم ده بيسهل توزيع المهام بين فرق التطوير في الشركات الكبيرة، بحيث يشتغل مهندس على تحسين الشاشات ومهندس تاني على ربط الـ APIs بدون أي تداخل أو تعارض برمجي."
    }
}

# ==========================================
# ARC-06: DTOs, Room entities, Domain, UI models
# ==========================================
DATA["ARC-06"] = {
    "concept_en": """Model segregation across architectural boundaries enforces the Single Responsibility Principle and insulates core business logic from external payload variations. DTOs (Data Transfer Objects) belong strictly to the network module within the Data layer, directly modeling remote JSON/Protobuf schemas with serialization annotations. Room entities reside within the database module of the Data layer, carrying persistence annotations that map directly to SQLite tables, primary keys, and foreign indices. Domain models reside at the core in the Domain layer as pure, unannotated Kotlin data classes representing business truth, constraints, and enterprise invariants. UI models belong to the Presentation layer, structured specifically for rendering ergonomics in Jetpack Compose—flattening nested structures, converting raw timestamps into formatted localized strings, and providing UI flags.""",
    "walkthrough_en": """Differentiating and mapping the four model tiers in a financial ledger app:
```kotlin
// 1. DATA LAYER (Network): DTO mirrors backend JSON schema
@Serializable
data class AccountTransactionDto(
    @SerialName("tx_id") val txId: String,
    @SerialName("amount_cents") val amountCents: Long,
    @SerialName("timestamp_epoch") val timestampEpoch: Long
)

// 2. DATA LAYER (Database): Entity models local SQLite table
@Entity(tableName = "transactions")
data class TransactionEntity(
    @PrimaryKey val id: String,
    val amountCents: Long,
    val timestamp: Long
)

// 3. DOMAIN LAYER: Pure business entity with domain invariants
data class Transaction(
    val id: String,
    val amount: BigDecimal,
    val instant: Instant
)

// 4. PRESENTATION LAYER: UI model optimized for Compose rendering
data class TransactionUiModel(
    val id: String,
    val formattedAmount: String, // e.g. "$12.50"
    val displayDate: String,     // e.g. "Today, 3:45 PM"
    val isDebit: Boolean
)
```""",
    "short_en": """DTOs live in the network module and Room entities live in the database module within the Data layer. Domain models reside in the pure Kotlin Domain layer representing core business concepts. UI models live in the Presentation layer optimized for Composable rendering.""",
    "structured_en": """To begin with, separating data representations across layers prevents external framework changes from polluting internal business models.
From an architectural standpoint, DTOs belong strictly to the network layer, mirroring remote JSON schemas with serialization annotations. Room entities belong to the local database layer, annotated with table and column definitions that reflect SQLite schemas.
In production scenarios, Domain models reside at the architectural core inside the domain layer. They are pure, unannotated Kotlin classes that represent business truth and invariants, completely free from database or network serialization dependencies.
As for UI models, they live in the presentation layer. These models are structured specifically for display ergonomics, containing formatted currency strings, localized date text, and layout visibility flags, allowing Jetpack Compose to render widgets passively without computing formatting logic during recomposition.""",
    "deep_senior_en": """Under the hood, model segregation enforces the Single Responsibility Principle and eliminates subtle coupling across boundaries. A frequent shortcut in rushed codebases is annotating a single entity with both Moshi @Json annotations and Room @Entity annotations, then passing it straight into the UI. While this saves initial lines of code, it binds your database schema, backend API contracts, and UI display logic into a single rigid structure. If the backend renames a JSON property, your local database schema breaks, requiring Room migrations and risking database crashes in production.
By maintaining four distinct model types—DTOs for transport, Entities for persistent storage, Domain models for business logic, and UI models for presentation—each model is free to evolve independently. DTOs accommodate backend breaking changes and nullability quirks; Entities optimize for SQLite indexing, foreign keys, and relational normalization; Domain models enforce business rules and invariants; and UI models are tailored for Compose stability, memoization, and accessibility requirements.
Staff engineers enforce explicit mapping at the boundaries using pure extension functions like toDomain, toEntity, and toUiModel. While this requires mapper boilerplate, it isolates defects: a network contract modification only touches the network mapper, leaving database persistence, business validation, and UI rendering entirely untouched. This structural isolation is the hallmark of resilient enterprise architecture.""",
    "meta_ar": {
        "id": "ARC-06",
        "questionAr": "أين يجب أن تعيش كائنات DTO وكيانات Room ونماذج الدومين ونماذج واجهة المستخدم (UI Models)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور كل نموذج بيانات في طبقته المخصصة، وإدراك مخاطر دمج التوصيفات (Annotations) في كائن واحد، ومعرفة كيفية عزل التغييرات الخارجية عن الواجهة.",
        "why_it_matters_ar": "استخدام نفس الكلاس لقاعدة البيانات والـ API وشاشة العرض يجعل أي تعديل في استجابة السيرفر يتطلب عمل Migration لقاعدة بيانات Room ويكسر واجهات المستخدم ويسبب كوارث برمجية في الإنتاج.",
        "worked_example_ar": "فصل النماذج الأربعة بحسب طبقاتها المعمارية:\n```kotlin\n// Data Network: DTO متطابق مع الـ JSON\n@Serializable data class UserDto(@SerialName(\"first_name\") val firstName: String)\n\n// Data Database: Entity لجدول SQLite\n@Entity(tableName = \"users\") data class UserEntity(@PrimaryKey val id: String, val name: String)\n\n// Domain: كائن كوتلن نقي يمثل منطق الأعمال\ndata class User(val id: String, val fullName: String)\n\n// Presentation: كائن مجهز للعرض في Compose\ndata class UserUiModel(val id: String, val displayName: String, val avatarInitials: String)\n```",
        "trade_offs_ar": "تعدد نماذج البيانات يضيف كود كتابة المحولات وتكرار الحقول، لكنه يعزل أجزاء التطبيق بالكامل ويحمي قاعدة البيانات من التغييرات المفاجئة في الـ API.",
        "failure_modes_ar": "وضع تعليقات `@Entity` و `@Serializable` معاً على نفس الكلاس، أو تمرير كائن الـ DTO مباشرة لشاشة الـ Compose.",
        "production_perspective_ar": "في المشروعات الكبرى، نقسم النماذج عبر موديولات Gradle؛ موديول الـ Network يحتوي على الـ DTOs، وموديول الـ Database يحتوي على الـ Entities، وموديول الـ Domain يحتوي على الـ Domain Models، بينما تظل الـ UI Models داخل موديولات الـ Features.",
        "how_to_answer_ar": "حدد مكان كل نموذج بوضوح: DTO في شبكة الداتا، و Room Entity في قاعدة بيانات الداتا، و Domain Model في قلب الدومين بكوتلن نقية، و UI Model في البريزنتيشن مخصصاً للعرض.",
        "talking_points_ar": "مسؤولية كل نموذج، ومخاطر الكائن متعدد التوصيفات، وتسهيل استقرار الـ Compose، وكيفية حماية قاعدة البيانات من تغيرات الـ API.",
        "follow_ups_ar": "- **المحاور:** \"ليه مينفعش نستخدم كائن الـ Entity بتاع Room مباشرة في شاشة الـ Compose؟\"\n  **المرشح:** \"لأن لو شكل العرض احتاج دمج حقلين أو تنسيق تاريخ، هنضطر نعدل كائن قاعدة البيانات ونغير الـ Schema أو نعمل حسابات جوه الـ Composable نفسه، وده بيبطئ الـ Recomposition ويكسر مبدأ عزل طبقة العرض عن التخزين.\"\n\n- **المحاور:** \"هل الـ Domain Model لازم يكون نسخة طبق الأصل من الـ Entity؟\"\n  **المرشح:** \"مش شرط، الـ Entity بيتصمم بحيث يناسب جداول الـ SQLite والمفاتيح الخارجية والـ Normalization، بينما الـ Domain Model بيتصمم علشان يخدم قواعد العمل وممكن يدمج كذا Entity أو يحسب حقول غير مخزنة مباشرة.\"",
        "self_check_ar": "هل حددت مكان كل نوع من النماذج الأربعة؟ هل بينت مخاطر استخدام كائن واحد للكل؟ وهل وضحت كيف تستفيد Compose من الـ UI Models؟",
        "references_ar": f"- [Guide to app architecture - Data layer](https://developer.android.com/topic/architecture/data-layer#models) — توثيق نماذج طبقة البيانات.\n- [Compose stability and UI models](https://developer.android.com/develop/ui/compose/performance/stability) — توثيق جوجل لأداء واستقرار النماذج في Compose.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "كائنات الـ DTO بتعيش في موديول الشبكة وكيانات Room بتعيش في موديول قاعدة البيانات داخل طبقة البيانات. نماذج الدومين بتعيش في قلب طبقة الدومين ككلاسات كوتلن نقية لتمثيل قواعد العمل. ونماذج الـ UI بتعيش في طبقة العرض مجهزة خصيصاً لتناسب شاشات Compose.",
        "best_answer_ar": "فصل نماذج البيانات عبر الطبقات المختلفة هو الحصن اللي بيحمي التطبيق من تأثير التغييرات الخارجية المفاجئة.\n\nكائنات الـ DTO مكانها موديول الشبكة في طبقة البيانات، وظيفتها تعكس شكل الـ JSON القادم من السيرفر بكل علامات الـ Serialization. وكيانات Room مكانها موديول قاعدة البيانات، وتحدد جداول ومفاتيح الـ SQLite بعلامات الـ Entity.\n\nنماذج الدومين بتعيش في المنتصف داخل طبقة الدومين، وهي كلاسات كوتلن نقية وخالية تماماً من أي Annotations؛ وظيفتها تمثل الحقيقة الأساسية للعمل التجاري والقيود المحاسبية المستقلة عن أي إطار عمل خارجي.\n\nأما نماذج الـ UI فمكانها طبقة العرض، ومصممة خصيصاً علشان تناسب طبيعة الـ Compose، فتحتوي على نصوص منسقة جاهزة، وعملات محولة، وأعلام إظهار وإخفاء العناصر، بحيث ترسم الشاشة بسلاسة بدون ما تحتاج تعمل أي حسابات معقدة أثناء إعادة الرسم.",
        "deep_answer_ar": "تحت الكابوت، فصل النماذج بيطبق مبدأ المسؤولية الواحدة ويمنع الارتباط الخفي بين مكونات النظام. من أسوأ الأخطاء في الكود السريع إن المطور يعمل كلاس واحد يحط عليه تعليقات `@Json` و `@Entity` مع بعض ويمرره للشاشة مباشرة؛ ده بيربط بين تصميم السيرفر وتصميم قاعدة بياناتك وشاشة المستخدم في نقطة واحدة شديدة الهشاشة. فلو السيرفر غير اسم حقل، قاعدة بيانات المستخدمين هتبوظ وممكن تحتاج Room Migration معقدة تعرض التطبيق للانهيار عند التحديث.\n\nبوجود أربعة نماذج مستقلة، كل نموذج بياخد حريته الكاملة في التطور: الـ DTO بيتعامل مع أخطاء السيرفر والقيم الفارغة، والـ Entity بيتصمم لتحقيق أفضل أداء في فهارس SQLite، والـ Domain Model بيفرض قواعد البزنس والأمان، والـ UI Model بيضمن استقرار Compose وخاصية الـ Smart Recomposition وتوافق قارئات الشاشة.\n\nالمهندسون الكبار بيعتمدوا على دوال تحويل نقية زي `toDomain` و `toEntity` و `toUiModel`؛ ورغم إن الخطوة دي بتتطلب كتابة أسطر كود إضافية، إلا إنها بتعزل الأعطال تماماً، وتسمح للفريق بتعديل الواجهات أو تغيير مكتبات الشبكة بدون لمس قاعدة البيانات أو منطق الدومين الأساسي. وبفضل العزل ده، بنقدر نطور التطبيق ليدعم منصات متعددة عبر Kotlin Multiplatform، بحيث تشترك شاشات أندرويد و iOS في نفس كائنات الدومين تماماً بينما يحتفظ كل نظام بنماذج واجهات المستخدم وتفاصيل قواعد البيانات المحلية الخاصة به دون أي قيود."
    }
}

# ==========================================
# ARC-07: Why do we use mappers between models?
# ==========================================
DATA["ARC-07"] = {
    "concept_en": """Mappers serve as architectural boundary translators that preserve the independence, resilience, and encapsulation of each architectural layer. In a multi-tiered Android system, external protocols (network responses, database cursors, platform intents) evolve according to different constraints and lifespans than internal business logic or UI layouts. Mappers act as anti-corruption layers: they absorb external schema modifications, sanitize invalid or null data, resolve primitive types into validated domain value classes, format raw data into localized presentation models, and ensure that framework annotations (@Json, @Entity) never cross layer boundaries. Without mappers, a single contract change in a backend microservice cascades across database schemas, business rules, and UI Composables.""",
    "walkthrough_en": """Implementing pure Kotlin boundary mappers across layers:
```kotlin
// 1. Data Layer: Network DTO to Domain Entity Mapper
fun UserDto.toDomain(): User = User(
    id = this.userId ?: throw IllegalArgumentException("Missing user ID"),
    displayName = "${this.firstName.orEmpty()} ${this.lastName.orEmpty()}".trim(),
    email = this.emailAddress.orEmpty(),
    isActive = this.status?.equals("active", ignoreCase = true) ?: false
)

// 2. Data Layer: Database Entity to Domain Entity Mapper
fun UserEntity.toDomain(): User = User(
    id = this.id,
    displayName = this.fullName,
    email = this.email,
    isActive = this.isActive
)

// 3. Presentation Layer: Domain Entity to UI Model Mapper
fun User.toUiModel(currencyFormatter: (Double) -> String): UserUiModel = UserUiModel(
    id = this.id,
    displayTitle = this.displayName.ifEmpty { "Guest User" },
    initials = this.displayName.split(" ").mapNotNull { it.firstOrNull()?.toString() }.take(2).joinToString(""),
    statusBadgeColor = if (this.isActive) Color.Green else Color.Gray
)
```""",
    "short_en": """Mappers decouple architectural layers by transforming data between external representations (DTOs, Room entities), business models, and UI models. This isolates breaking changes, sanitizes nullability, and prevents database or network dependencies from leaking into core logic.""",
    "structured_en": """To begin with, mappers serve as boundary translators that preserve the independence and stability of each architectural layer.
From an architectural standpoint, without mappers, any modification to a backend JSON payload or a database column ripples across the entire codebase, forcing updates to business logic and UI layouts. Mappers absorb these changes at the boundary, ensuring only the conversion function updates.
In production scenarios, mappers sanitize incoming data. They convert nullable network fields into safe default values or validated domain types, format raw timestamps into localized date strings, and strip sensitive infrastructure tokens before data reaches the presentation layer.
As for implementation, mappers are typically authored as pure, static Kotlin extension functions. Because they have no side effects, they execute with zero allocation overhead and are trivial to unit test with complete coverage.""",
    "deep_senior_en": """Under the hood, mappers establish formal anti-corruption layers between autonomous subsystems. In distributed enterprise systems, backend APIs evolve according to server-side database schemas and microservice constraints that often clash with mobile client requirements. An API might represent monetary values as integer cents, dates as Unix epochs, and user status as arbitrary string flags.
Passing raw DTOs into the domain or presentation layers forces ViewModels and Composables to repeatedly perform parsing, null-checks, and defensive formatting. If a backend contract changes or returns unexpected nulls, uncaught exceptions occur directly on the main thread during UI rendering. Mappers act as firewalls: the data layer repository catches invalid inputs and converts primitives into type-safe domain value classes, keeping domain logic pristine.
Similarly, mapping from domain models to UI models optimizes Jetpack Compose performance. Domain models often contain rich entity relationships and full historical lists that the UI does not need. The UI mapper flattens these structures into immutable UI state models marked with @Immutable or @Stable, ensuring Compose recomposition skips unchanged components efficiently.
Staff engineers balance manual mapping against automated code generation libraries. While reflection-based mappers introduce runtime overhead and obfuscation risks with R8, idiomatic Kotlin extension functions provide compile-time safety, effortless debugging, and zero reflection penalties. This discipline guarantees robust error boundaries and predictable application performance.""",
    "meta_ar": {
        "id": "ARC-07",
        "questionAr": "لماذا نستخدم المحولات (Mappers) بين نماذج البيانات المختلفة في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور المحولات كطبقة حماية (Anti-Corruption Layer) بين الطبقات، والقدرة على تنقية البيانات ومعالجة القيم الفارغة عند الحدود، وإدراك أهميتها في حماية استقرار التطبيق.",
        "why_it_matters_ar": "غياب المحولات يؤدي إلى تسريب كائنات الشبكة للواجهة، فإذا أرسل السيرفر قيمة null غير متوقعة أو تم تغيير اسم حقل، يحدث انهيار فوري (Crash) للشاشات أثناء عمل التطبيق.",
        "worked_example_ar": "دوال تحويل نقية (Extension Functions) لتحويل البيانات بأمان:\n```kotlin\n// تحويل الـ DTO لدومين مع معالجة القيم الفارغة\nfun OrderDto.toDomain(): Order = Order(\n    id = this.orderId ?: \"\",\n    total = BigDecimal(this.amountCents ?: 0).divide(BigDecimal(100)),\n    isPaid = this.status.equals(\"PAID\", ignoreCase = true)\n)\n\n// تحويل الدومين لـ UI Model جاهز للعرض\nfun Order.toUiModel(): OrderUiModel = OrderUiModel(\n    id = this.id,\n    formattedTotal = \"$${this.total}\",\n    statusText = if (this.isPaid) \"تم الدفع\" else \"قيد الانتظار\"\n)\n```",
        "trade_offs_ar": "المحولات تتطلب كتابة كود يدوي واختبارات إضافية لكل نموذج، لكنها توفر عزلاً أمنياً كاملاً وتمنع تسريب تفاصيل التخزين والشبكة إلى منطق التطبيق.",
        "failure_modes_ar": "وضع منطق استدعاءات شبكة أو عمليات IO داخل المحولات، أو استخدام مكتبات تحويل تعتمد على الـ Reflection تسبب بطئاً وتعارضاً مع R8.",
        "production_perspective_ar": "في المشروعات الإنتاجية الكبرى، نكتب المحولات كـ Top-level Kotlin Extension Functions نقية ليس لها أي آثار جانبية (Pure Functions)، ونكتب لها Unit Tests تغطي كافة احتمالات الـ Nullability والـ Edge Cases.",
        "how_to_answer_ar": "بين أن المحولات تعمل كطبقة حماية ضد التغييرات الخارجية، واشرح دورها في تنظيف البيانات وتحويل القيم الفارغة وصياغة النصوص للشاشات، وأكد على كتابتها كدوال نقية.",
        "talking_points_ar": "مفهوم Anti-Corruption Layer، وتنقية القيم الفارغة عند الحدود المعمارية، وتجهيز النصوص للـ UI، واستخدام دوال الامتداد النقية بدون Reflection.",
        "follow_ups_ar": "- **المحاور:** \"ليه منستخدمش مكتبات أوتوماتيكية زي ModelMapper أو MapStruct بدلاً من كتابة الكود يدوياً؟\"\n  **المرشح:** \"المكتبات اللي بتعتمد على الـ Reflection بتبطئ التطبيق على الموبايل وبتعمل مشاكل مع R8 و ProGuard، بينما دوال الامتداد العادية في كوتلن بتدينا فحص كامل وقت الكومبايل (Compile-time safety) وصفر تكلفة أداء.\"\n\n- **المحاور:** \"أين نضع كود المحولات في هيكل المجلدات؟\"\n  **المرشح:** \"المحول اللي بيحول من DTO أو Entity لدومين بيتحط في طبقة البيانات، والمحول اللي بيحول من دومين لـ UI Model بيتحط في طبقة العرض، بحيث يفضل الدومين نظيف وميعرفش أي حاجة عن المحولات الخارجية.\"",
        "self_check_ar": "هل شرحت مفهوم طبقة الحماية (Anti-corruption layer)؟ هل وضحت دور المحولات في معالجة الـ Nullability؟ وهل بينت أين توضع دوال التحويل؟",
        "references_ar": f"- [Anti-Corruption Layer pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer) — المفهوم المعماري لطبقات الحماية.\n- [Data Layer Architecture](https://developer.android.com/topic/architecture/data-layer) — توثيق جوجل الرسمي لمستودعات البيانات والمحولات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "المحولات بتعزل طبقات النظام عن بعضها عن طريق تحويل كائنات الشبكة وقواعد البيانات إلى نماذج دومين نقية ثم إلى نماذج واجهة مستخدم. ده بيحمي التطبيق من التغيرات المفاجئة في السيرفر، ويعالج القيم الفارغة عند الحدود، ويمنع تسريب تفاصيل أطر العمل لقلب التطبيق.",
        "best_answer_ar": "المحولات بتمثل حائط الصد الأساسي بين طبقات التطبيق المختلفة لحمايتها من الانهيار عند حدوث أي تعديل خارجي.\n\nفي المشاريع الكبيرة، السيرفرات وقواعد البيانات بتتغير باستمرار وبترجع قيم بتخدم التخزين والاتصالات، زي التواريخ كأرقام ثواني أو الأسعار بالسنت. لو مررنا الكائنات دي للواجهة مباشرة، أي تغيير في اسم حقل في السيرفر هيكسر شاشات التطبيق فوراً ويجبرنا نعدل كود العرض.\n\nالمحولات بتشتغل كطبقة حماية عند الحدود؛ بتستقبل كائنات الـ DTO وتحولها لنماذج دومين سليمة، وبتعوض القيم الفارغة بقيم افتراضية آمنة، وبتتحقق من صحة البيانات قبل ما توصل للمستخدم.\n\nكمان المحولات بتساعد شاشات الـ Compose إنها تعرض نصوص منسقة وألوان جاهزة مباشرة بدون ما تضيع وقت المعالج في تنسيق النصوص والعملات أثناء إعادة الرسم، وده بينتج عنه أداء فائق وسرعة ملحوظة في تجربة المستخدم.",
        "deep_answer_ar": "تحت الكابوت، المحولات بتبني ما يعرف معمارياً بـ Anti-Corruption Layer بين الأنظمة المستقلة. في تطبيقات أندرويد المعقدة، واجهات السيرفر بتتصمم وفق قيود قواعد البيانات المركزية وتنسيقات المايكروسيرفيسز، واللي في الغالب بتتعارض مع متطلبات الموبايل. السيرفر ممكن يبعت الأرقام كأعداد صحيحة والتواريخ كـ Timestamps والحالة كنصوص غير منضبطة.\n\nلو مررنا كائنات الـ DTO مباشرة لطبقة العرض أو الـ ViewModels، هنلاقي نفسنا بنكتب نداءات التحقق من القيم الفارغة وتنسيق النصوص في كل شاشة، وأي تغيير بسيط من السيرفر هيتسبب في NullPointerException يوقف التطبيق على أجهزة المستخدمين. المحولات بتشتغل كفلتر حماية صارم: الريبوزيتوري بيمسك البيانات الخام ويحولها لكائنات دومين ذات قيم آمنة ومضمونة.\n\nكذلك، التحويل من كائنات الدومين لكائنات الـ UI Models بيحسن أداء Jetpack Compose بدرجة كبيرة؛ كائنات الدومين غالباً بتحتوي على قوائم تاريخية وتفاصيل لا تحتاجها الشاشة، والمحول بيبسط الهيكل ده لكائن UI مسطح وغير قابل للتعديل وموسوم بـ Immutable، وده بيخلي Compose تتخطى إعادة رسم العناصر الثابتة بكفاءة.\n\nالمهندسون الكبار بيفضلوا كتابة المحولات كـ Kotlin Extension Functions نقية وخالية من الآثار الجانبية، لأنها بتضمن فحص الأخطاء وقت الكومبايل وبتتفادى مشاكل الـ Reflection وبطء المعالجة مع R8 في النسخ النهائية. والأسلوب ده بيضمن حماية التطبيق من الانهيارات غير المتوقعة الناتجة عن تغييرات السيرفر المفاجئة، وبيسهل كتابة اختبارات دقيقة لكل سيناريوهات البيانات المحتملة."
    }
}

# ==========================================
# ARC-08: Compare MVC, MVP, MVVM, MVI, UDF
# ==========================================
DATA["ARC-08"] = {
    "concept_en": """The architectural progression from MVC through MVP, MVVM, MVI, and Unidirectional Data Flow (UDF) charts Android's transition from imperative, lifecycle-coupled callback controllers to reactive, predictable state machines. MVC coupled View and Controller inside Activities, producing massive, untestable God classes. MVP decoupled business logic into a Presenter through a 1:1 View interface, but suffered from rigid interface coupling, state synchronization race conditions, and lack of lifecycle survival across configuration changes. MVVM leveraged Jetpack ViewModel and observable streams (LiveData, StateFlow) to survive configuration changes and decouple UI observation from business execution. MVI and UDF evolved this by modeling presentation state as a single immutable state machine where user actions dispatch immutable Intent/Event objects to a reducer, producing an updated State snapshot that flows strictly downward to declarative Composables.""",
    "walkthrough_en": """Contrasting MVP interface callbacks with modern MVI / UDF reactive loops:
```kotlin
// 1. LEGACY MVP: Tight 1:1 interface coupling, imperative updates
interface LoginView {
    fun showProgress()
    fun hideProgress()
    fun showError(message: String)
}

class LoginPresenter(private val view: LoginView, private val api: AuthApi) {
    fun onLoginClicked(user: String, pass: String) {
        view.showProgress() // Imperative side-effect
        // Vulnerable to async race conditions if view is destroyed
    }
}

// 2. MODERN MVI / UDF: Unidirectional loop, single immutable state
sealed interface LoginIntent {
    data class Submit(val user: String, val pass: String) : LoginIntent
}

data class LoginState(val isLoading: Boolean = false, val error: String? = null)

class LoginViewModel(private val authUseCase: AuthUseCase) : ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    fun handleIntent(intent: LoginIntent) {
        when (intent) {
            is LoginIntent.Submit -> executeLogin(intent.user, intent.pass)
        }
    }

    private fun executeLogin(user: String, pass: String) {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }
            authUseCase(user, pass)
                .onSuccess { _state.update { it.copy(isLoading = false) } }
                .onFailure { err -> _state.update { it.copy(isLoading = false, error = err.message) } }
        }
    }
}
```""",
    "short_en": """MVC couples View and Controller inside Android Activities. MVP decouples logic via a 1:1 Presenter interface. MVVM uses observable ViewModels surviving configuration changes. MVI enforces a single immutable state updated via user Intents. UDF is the underlying principle where events flow up and state flows down.""",
    "structured_en": """To begin with, the evolution of Android presentation patterns reflects the industry's shift toward declarative UIs, immutability, and predictable state management.
From an architectural standpoint, early MVC combined View and Controller inside Activities, producing massive, untestable classes. MVP introduced 1:1 Presenter interfaces that decoupled UI from presentation logic, but suffered from tight interface coupling and manual lifecycle management during configuration changes.
In production scenarios, MVVM replaced MVP by introducing architecture component ViewModels that survive configuration changes and expose observable state streams. Jetpack Compose and modern coroutines evolved MVVM into MVI and Unidirectional Data Flow, where user interactions are dispatched as explicit Intent or Event objects.
As for predictability, UDF and MVI ensure that state flows strictly downward while user events flow upward. A single immutable ViewState eliminates race conditions, guarantees reproducible bug reproduction, and simplifies UI rendering into a pure function of state.""",
    "deep_senior_en": """Under the hood, comparing these architectural paradigms reveals how Android transitioned from imperative callback trees to reactive state machines. In MVP, the Presenter directly invoked methods on a View interface—such as view.showLoading or view.displayUser. Because multiple asynchronous callbacks could complete in arbitrary orders, the View frequently entered inconsistent intermediate states, such as showing both a loading spinner and an error message simultaneously.
MVVM solved lifecycle retention through ViewModelStore, allowing state to survive activity recreation. However, classic MVVM often exposed multiple independent LiveData or StateFlow streams—such as isLoading, userData, and errorMessage. When multiple flows emit asynchronously, the UI can briefly observe contradictory states, causing UI flickers and rendering anomalies.
MVI resolves this problem mathematically by treating state transitions as a finite state machine: (PreviousState, Intent) -> NewState. In modern Jetpack Compose applications, MVVM and MVI have converged under Unidirectional Data Flow. The ViewModel exposes a single StateFlow containing an immutable data class, while the UI dispatches sealed interface actions.
Staff engineers evaluate the cognitive load of pure MVI. While single-state reducers provide perfect event sourcing and time-travel debugging, modeling transient one-off side effects—such as showing Snackbars or triggering navigation—requires careful handling via shared channels or single-event wrappers to avoid replaying events on configuration changes. This architectural maturity ensures rock-solid UI stability across complex user flows.""",
    "meta_ar": {
        "id": "ARC-08",
        "questionAr": "قارن بين أنماط MVC و MVP و MVVM و MVI والتدفق أحادي الاتجاه (UDF) في أندرويد.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم التطور التاريخي لأنماط المعمارية في أندرويد، وإدراك الفروق الجوهرية بين استدعاءات الـ Interfaces وحالات التدفق التفاعلي، ومعرفة كيفية تطبيق مبدأ التدفق أحادي الاتجاه.",
        "why_it_matters_ar": "اختيار نمط خاطئ أو الخلط بينها يسبب حالات تعارض في واجهة المستخدم (تزامن شاشة التحميل مع رسالة الخطأ) وصعوبة في إدارة دورة حياة النشاطات عند تدوير الشاشة.",
        "worked_example_ar": "المقارنة العملية بين استدعاءات MVP وحلقة UDF / MVI الحديثة:\n```kotlin\n// MVI / UDF: حالة واحدة غير قابلة للتعديل وأحداث صريحة\nsealed interface UserIntent { object Refresh : UserIntent }\ndata class UserState(val isLoading: Boolean = false, val data: List<User> = emptyList())\n\nclass UserViewModel : ViewModel() {\n    private val _state = MutableStateFlow(UserState())\n    val state = _state.asStateFlow()\n    fun process(intent: UserIntent) {\n        when(intent) { UserIntent.Refresh -> _state.update { it.copy(isLoading = true) } }\n    }\n}\n```",
        "trade_offs_ar": "أنماط MVI و UDF تضمن حالة وحيدة متسقة وسهولة في تتبع الأخطاء، لكنها تتطلب كتابة كود إضافي لحزم الحالات (Boilerplate) والتعامل بحذر مع الأحداث العابرة مثل الـ Snackbars.",
        "failure_modes_ar": "إطلاق أحداث متعددة غير متزامنة في MVVM تسبب وميضاً في الواجهة، أو الاحتفاظ بمرجع View داخل Presenter مما يسبب تسريب ذاكرة عند إغلاق الشاشة.",
        "production_perspective_ar": "في تطبيقات Jetpack Compose الحديثة، نعتمد نمط UDF بشكل قياسي؛ حيث تستقبل شاشات الـ Composable كائن State غير قابل للتعديل وتطلق Lambda Events للأعلى، مما يجعل الشاشات خالية تماماً من منطق إدارة الحالة.",
        "how_to_answer_ar": "تتبع التسلسل الزمني بإيجاز: كيف دمج MVC كل شيء في Activity، وكيف فصل MVP المنطق بواجهات، وكيف حل MVVM مشكلة تدوير الشاشة، وكيف حقق MVI و UDF الاتساق الكامل بحالة واحدة غير قابلة للتعديل.",
        "talking_points_ar": "التطور التاريخي للأنماط، ومشكلة الحالات المتعارضة في MVP، وحفظ الحالة عبر ViewModelStore، ومعادلة الـ Reducer في MVI، وتطبيق UDF مع Compose.",
        "follow_ups_ar": "- **المحاور:** \"إيه المشكلة الأساسية في MVP خلت مجتمع أندرويد يتخلى عنها لصالح MVVM؟\"\n  **المرشح:** \"المشكلة كانت الارتباط القوي بالـ View Interface وصعوبة التعامل مع دورة حياة أندرويد؛ الـ Presenter مكنش بيعيش بعد تدوير الشاشة، وكان لازم نفصل الـ View يدوياً علشان منسربش الذاكرة، ده غير تعارض الحالات بسبب نداءات الكولباك المتفرقة.\"\n\n- **المحاور:** \"إزاي بنتعامل مع الـ One-off Events زي الـ Navigation أو الـ Toast في نمط MVI؟\"\n  **المرشح:** \"بنتعامل معاها إما عبر Channel خاصة بالأحداث العابرة (Side Effects) تستهلك مرة واحدة، أو بوضعها كحدث مؤقت داخل الـ State ويتم عمل Reset له فور استهلاكه لمنع تكرار التنفيذ عند تدوير الشاشة.\"",
        "self_check_ar": "هل قارنت بين الأنماط الخمسة بدقة؟ هل شرحت مبدأ التدفق أحادي الاتجاه (UDF)؟ وهل بينت ميزة الحالة الواحدة في MVI؟",
        "references_ar": f"- [Guide to app architecture - UI Layer state production](https://developer.android.com/topic/architecture/ui-layer/state-production) — توثيق جوجل الرسمي لإنتاج حالات الواجهة ونمط UDF.\n- [MVI architecture pattern](https://developer.android.com/topic/architecture) — دليل جوجل المعماري.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نمط MVC دمج العرض والتحكم في كلاسات الأنشطة مسبباً تضخمها. نمط MVP فصل المنطق عبر واجهات Presenter لكنه عانى من مشاكل تدوير الشاشة. نمط MVVM قدم الـ ViewModel لحفظ الحالة بمراقبة تفاعلية. بينما MVI و UDF طوروا المفهوم لحالة واحدة متكاملة وغير قابلة للتعديل بتضمن تدفق الأحداث للأعلى وتدفق البيانات للأسفل.",
        "best_answer_ar": "تطور أنماط العمارة في أندرويد بيعكس رحلة الانتقال من البرمجة الأمرية إلى البرمجة التفاعلية وإدارة الحالة الصريحة.\n\nفي البداية، نمط MVC كان بيجمع كود العرض والتحكم داخل الـ Activity، وده عمل كلاسات عملاقة يستحيل اختبارها. بعده جه نمط MVP وفصل المنطق في كلاس Presenter بيكلم الشاشة من خلال Interface، لكنه كان معقد في متابعة دورة حياة النشاط وعرضة لتسريب الذاكرة عند تدوير الموبايل.\n\nنمط MVVM عمل نقلة نوعية بتقديمه كلاس ViewModel اللي بينجو من تدوير الشاشة تلقائياً وبيعرض تدفقات داتا المراقبة. ومع ظهور Jetpack Compose، اتجهنا لنمط MVI والتدفق أحادي الاتجاه UDF.\n\nفي UDF و MVI، المستخدم بيطلق أحداث صريحة تطلع للـ ViewModel، والـ ViewModel بيعالجها ويرجع كائن حالة وحيد وغير قابل للتعديل يتدفق للأسفل؛ وده بيمنع أي تعارض في الشاشة ويخلي تتبع الأخطاء أمراً مضموناً ومحسوباً بدقة.",
        "deep_answer_ar": "تحت الكابوت، مقارنة الأنماط دي بتوضح إزاي أندرويد اتنقل من شجرة الكولباك الأمرية لآلات الحالة التفاعلية المحكمة. في نمط MVP، الـ Presenter كان بيستدعي دوال في واجهة العرض بشكل أمري زي `showLoading` و `showError`. ولأن الاستجابات غير المتزامنة ممكن ترجع بترتيب عشوائي، الشاشة كانت بتدخل في حالات متناقضة، زي إنها تعرض مؤشر التحميل ورسالة الخطأ في نفس اللحظة.\n\nنمط MVVM حل مشكلة دورة الحياة عن طريق الـ ViewModelStore، فبقت الداتا بتعيش أثناء تدوير الشاشة. لكن العيب في MVVM التقليدي إنه كان بيعرض تدفقات منفصلة زي `isLoading` و `userData`، وتحديثهم المستقل كان ممكن يعمل وميض وتعارض لحظي في الواجهة.\n\nنمط MVI حل المعضلة دي رياضياً عن طريق تحويل إنتاج الحالة لمعادلة واضحة: الحالة السابقة زائد الحدث الجديد ينتج الحالة الجديدة. وفي تطبيقات Compose الحديثة، اندمج MVVM مع MVI تحت مظلة التدفق أحادي الاتجاه UDF؛ الـ ViewModel بيعرض تدفق `StateFlow` واحد فيه Data Class غير قابلة للتعديل، والشاشة بتستجيب لها وتطلق الأحداث للأعلى.\n\nالمهندسون الكبار بيحسبوا التكلفة المعمارية بدقة؛ فرغم إن MVI بيدي استقراراً تاماً وتتبعاً مثالياً للأخطاء، إلا إنه بيتطلب مهارة في إدارة الأحداث العابرة التي تحدث لمرة واحدة زي عرض الـ SnackBar أو التنقل بين الشاشات، وده بنعالجه إما عن طريق قنوات Channel أو بأحداث داخل الـ State بيتعمل لها استهلاك وتصفير فوري لمنع تكرارها."
    }
}

# ==========================================
# ARC-09: UI state vs Domain state
# ==========================================
DATA["ARC-09"] = {
    "concept_en": """Differentiating UI state from business/domain state is a foundational architectural boundary that prevents transient presentation mechanics from contaminating core enterprise data models. Domain state represents the persistent, authoritative business truth of an application—such as an authenticated user profile, bank account balance, or items in a shopping cart. It is governed by enterprise invariants, maintained in repositories, persisted in databases or remote backends, and survives screen transitions. UI state represents the transient, presentation-specific configuration of what is currently rendered on screen—such as loading progress indicators, accordion expand/collapse toggles, text field focus, selected tabs, or localized validation error banners. UI state is derived from domain streams, owned by ViewModels, scoped strictly to screen lifecycles, and discarded upon screen completion.""",
    "walkthrough_en": """Contrasting persistent domain state with transient UI state in a banking dashboard:
```kotlin
// 1. DOMAIN STATE: Persistent, authoritative, business truth
data class AccountBalance(
    val accountId: String,
    val availableBalance: BigDecimal,
    val currency: Currency,
    val isFrozen: Boolean
)

// 2. UI STATE: Transient, display-specific projection
data class AccountDashboardUiState(
    val isLoading: Boolean = false,
    val formattedBalance: String = "",       // e.g. "$12,450.00"
    val isBalanceVisible: Boolean = true,     // Toggle eye icon (UI only)
    val isTransferButtonEnabled: Boolean = false,
    val userErrorMessage: String? = null
)

// 3. ViewModel derives UI state by combining domain stream with UI toggle flow
class AccountDashboardViewModel(
    private val accountRepository: AccountRepository
) : ViewModel() {
    private val isBalanceVisibleFlow = MutableStateFlow(true)

    val uiState: StateFlow<AccountDashboardUiState> = combine(
        accountRepository.observeBalance(),
        isBalanceVisibleFlow
    ) { balance, isVisible ->
        AccountDashboardUiState(
            isLoading = false,
            formattedBalance = if (isVisible) "$${balance.availableBalance}" else "••••••",
            isBalanceVisible = isVisible,
            isTransferButtonEnabled = !balance.isFrozen && balance.availableBalance > BigDecimal.ZERO,
            userErrorMessage = if (balance.isFrozen) "Account is temporarily locked" else null
        )
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), AccountDashboardUiState(isLoading = true))

    fun toggleBalanceVisibility() {
        isBalanceVisibleFlow.update { !it } // Modifies transient UI state only!
    }
}
```""",
    "short_en": """Business or domain state represents persistent, core enterprise truth independent of screens, such as account balances or user roles. UI state is transient and screen-specific, defining what is visually rendered at any moment, including loading spinners, input validation errors, and selected tabs.""",
    "structured_en": """To begin with, distinguishing UI state from domain state prevents presentation concerns from corrupting enterprise business models.
From an architectural standpoint, domain state represents the persistent, authoritative truth of the application. It includes user credentials, shopping cart contents, and transaction histories managed by repositories and databases, existing independently of whether any screen is actively visible.
In production scenarios, UI state is a transient, presentation-focused projection of that domain data combined with screen-specific UI conditions. It models what the user sees at a particular moment, encompassing loading indicators, accordion expansion states, selected tabs, and localized input error messages.
As for lifecycle and derivation, domain state survives navigation and process death, whereas UI state is owned by a ViewModel and scoped to a specific user journey, continuously derived from underlying domain streams and discarded when the screen finishes.""",
    "deep_senior_en": """Under the hood, conflating UI state with domain state introduces major architectural bugs, memory leaks, and synchronization failures. Domain state is governed by business rules and backend invariants; it changes only when explicit business transactions occur, such as finalizing a purchase or receiving a WebSocket price update. It is typically modeled as immutable domain entities stored in local databases like Room or encrypted secure storage.
UI state, conversely, is ephemeral and dynamic. In Jetpack Compose, UI state must be modeled as a single, immutable data class or sealed hierarchy exposed via StateFlow. It contains presentation-only properties that have zero meaning to the enterprise domain—such as isSwipeRefreshing, searchQueryInputText, scaffoldSnackbarMessage, or isBiometricPromptVisible.
When designing reactive pipelines, senior engineers treat UI state as a derived projection. The ViewModel combines multiple domain repository flows alongside local UI event flows using operators like combine or map, producing a unified screen state. If the user navigates away, the UI state vanishes from memory, while the underlying domain state remains intact in the data layer.
Staff engineers maintain strict architectural hygiene: domain entities must never hold UI-specific primitives like Android string resource IDs or format strings, while UI state classes should flatten complex domain graphs into simple, primitive-backed display models that guarantee fast Compose recomposition without unnecessary object allocations. This separation ensures rock-solid state management across process recreation and deep-link navigation.""",
    "meta_ar": {
        "id": "ARC-09",
        "questionAr": "كيف تختلف حالة واجهة المستخدم (UI State) عن حالة العمل/الدومين (Domain State)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الفرق بين البيانات المستمرة والحالات المؤقتة، وإدراك كيفية اشتقاق حالة العرض من تدفقات الدومين، ومعرفة دورة حياة كل منهما في التطبيق.",
        "why_it_matters_ar": "خلط حالة العرض مع حالة الدومين يجعل كائنات البزنس تحتوي على نصوص وألوان تخص شاشة معينة، مما يفسد منطق الدومين ويسبب مشاكل مزامنة عند التنقل بين الشاشات.",
        "worked_example_ar": "اشتقاق حالة العرض من حالة الدومين عبر مشغل combine:\n```kotlin\n// Domain State: بيانات الحساب المستمرة\ndata class Account(val balance: BigDecimal, val isLocked: Boolean)\n\n// UI State: حالة الشاشة المؤقتة\ndata class DashboardUiState(val displayBalance: String, val canTransfer: Boolean, val isHidden: Boolean)\n\n// الاشتقاق في الـ ViewModel\nval uiState = combine(repo.observeAccount(), isHiddenFlow) { acc, hidden ->\n    DashboardUiState(if (hidden) \"***\" else \"$${acc.balance}\", !acc.isLocked, hidden)\n}.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), DashboardUiState(\"\", false, false))\n```",
        "trade_offs_ar": "فصل الحالتين يتطلب إنشاء نماذج بيانات واشتقاق تفاعلي مستمر، لكنه يحافظ على نقاء منطق الأعمال ويمنع تسريب تفاصيل الشاشات لقواعد البيانات.",
        "failure_modes_ar": "تخزين أعلام مؤقتة مثل `isLoading` أو `isPasswordVisible` داخل كائنات الدومين أو جداول قاعدة البيانات المحلية.",
        "production_perspective_ar": "في المشروعات الإنتاجية الكبرى، نعتبر الـ UI State نتاج دالة اشتقاق نقية (Pure State Derivation) تعتمد على تدفقات الدومين مع أحداث المستخدم المؤقتة، ونحظر تماماً وجود أي كلاسات أندرويد داخل الـ Domain State.",
        "how_to_answer_ar": "عرف حالة الدومين بأنها الحقيقة المستمرة للبزنس التي تعيش في المستودعات، وعرف حالة العرض بأنها لقطة مؤقتة لما يراه المستخدم على الشاشة حالياً وتعيش في الـ ViewModel.",
        "talking_points_ar": "دورة حياة الحالتين، واشتقاق UI State عبر combine، وتجنب وضع أعلام العرض في الدومين، وتحسين أداء الـ Recomposition في Compose.",
        "follow_ups_ar": "- **المحاور:** \"لو المستخدم قفل الشاشة ورجع، مين فيهم اللي بيعيش ومين بيختفي؟\"\n  **المرشح:** \"حالة الدومين بتعيش لأنها محفوظة في الـ Repository أو قاعدة البيانات المحلية، بينما حالة الـ UI بتنتهي بمجرد تدمير الـ ViewModel، إلا لو حفظنا بعض المدخلات المؤقتة زي نص البحث في SavedStateHandle للنجاة من موت العملية (Process Death).\"\n\n- **المحاور:** \"هل مسموح للـ Domain State تحتوي على معرفات موارد أندرويد زي R.string؟\"\n  **المرشح:** \"ممنوع تماماً؛ الدومين لازم يفضل كود كوتلن نقي، والـ ViewModel هو المسؤول عن أخذ أكواد أو Enums الخطأ من الدومين وتحويلها لـ String Resources مناسبة للغة التطبيق.\"",
        "self_check_ar": "هل ميزت بوضوح بين استمرارية الدومين وعابرة الـ UI؟ هل شرحت كيفية اشتقاق UI State؟ وهل حذرت من تخزين أعلام العرض في الدومين؟",
        "references_ar": f"- [Guide to app architecture - UI Layer State modeling](https://developer.android.com/topic/architecture/ui-layer/state-production#mutating-ui-state) — توثيق جوجل الرسمي لنمذجة وإنتاج حالات العرض.\n- [State and Jetpack Compose](https://developer.android.com/develop/ui/compose/state) — توثيق إدارة الحالة في Compose.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "حالة العمل أو الدومين بتمثل الحقيقة المستمرة لبيانات التطبيق المستقلة عن الشاشات، زي أرصدة الحسابات ومعلومات المستخدم. بينما حالة العرض هي حالة مؤقتة بتحدد ما يظهر على الشاشة في اللحظة الحالية، زي مؤشرات التحميل وفتح القوائم وأخطاء التحقق من المدخلات.",
        "best_answer_ar": "الفصل بين حالة العرض وحالة الدومين هو الخط الفاصل اللي بيحمي نماذج الأعمال من التلوث بمتطلبات الشاشات العابرة.\n\nحالة الدومين بتمثل الحقيقة الأساسية والمستمرة للتطبيق؛ زي بيانات الحساب البنكي، أو السلع الموجودة في سلة التسوق. الحالة دي بيحكمها منطق البزنس وقواعد الأمان، ومكانها المستودعات وقواعد البيانات والسيرفر، وتعيش بشكل مستقل تماماً عن وجود أو غياب أي شاشة.\n\nفي المقابل، حالة العرض هي إسقاط مؤقت للبيانات دي مدمجة مع ظروف الشاشة الحالية؛ بتعبر عن اللي المستخدم شايفه قدامه، زي مؤشر التحميل، أو إخفاء وإظهار كلمة السر، أو التبويب المختار، أو رسائل التحقق من صحة الإدخال.\n\nمن حيث دورة الحياة، حالة الدومين بتعيش حتى لو المستخدم خرج من الشاشة، بينما حالة العرض بتكون مملوكة للـ ViewModel وبتنتهي مع انتهاء الشاشة، وبيتم اشتقاقها باستمرار من تدفقات الدومين بحيث تعكس أي تغيير يحصل في البيانات بشكل فوري وتفاعلي.",
        "deep_answer_ar": "تحت الكابوت، الخلط بين حالة العرض وحالة الدومين بيسبب مشاكل معمارية معقدة وتسريب للذاكرة وتعارض في تزامن البيانات. حالة الدومين بتخضع لقواعد الأعمال وقيود السيرفر؛ مبتتغيرش إلا لما يحصل حدث تجاري حقيقي زي تنفيذ عملية دفع أو استلام تحديث جديد من السيرفر، وغالباً بنحفظها كنماذج دومين نقية في قاعدة بيانات محكمة زي Room أو التخزين المشفر.\n\nحالة العرض، على العكس، كائن ديناميكي عابر. في Jetpack Compose بنمثلها كـ Data Class وحيدة غير قابلة للتعديل وبنعرضها من خلال StateFlow. الكائن ده بيحتوي على خصائص شكلية ملهاش أي معنى في عالم البزنس، زي isRefreshing أو searchQuery أو isPasswordVisible.\n\nفي المشاريع الاحترافية، بنتعامل مع حالة العرض كنتاج دالة اشتقاق نقية؛ الـ ViewModel بيدمج تدفقات الدومين مع تدفقات الأحداث المؤقتة باستخدام مشغلات زي combine أو map لإنتاج الـ State النهائية الموحدة للشاشة. لو المستخدم قفل الصفحة، حالة الـ UI بتختفي فوراً من الذاكرة وتتحرر الموارد بينما بيانات الدومين بتفضل محفوظة ومستقرة في طبقة البيانات.\n\nالمهندسون الكبار بيحافظوا على النقاء المعماري بصرامة: مستحيل كائن دومين يحتوي على كلاسات أندرويد زي @StringRes أو ألوان Compose، بينما كلاسات حالة العرض بتفكك العلاقات المعقدة وتحولها لبيانات بدائية مسطحة تضمن أقصى سرعة في إعادة الرسم بدون أي إهدار للذاكرة."
    }
}


def main():
    print(f"Elevating {len(DATA)} questions in ARC (ARC-01 to ARC-09)...")
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
    ee.save_topic_metadata("arc_01_09", {qid: d["meta_ar"] for qid, d in DATA.items()})

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
        print("\nAll 9 ARC questions (ARC-01 to ARC-09) successfully elevated and passed validation!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
