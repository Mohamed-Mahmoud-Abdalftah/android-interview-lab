#!/usr/bin/env python3
"""Elevate SOL-01 through SOL-10 for bilingual parity and senior spoken answers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path("/Volumes/M&M/Android/InterView/untitled folder/android quation")
sys.path.insert(0, str(BASE_DIR / "scripts" / "elevations"))

import elevation_engine as ee

TOPIC_AR = "مبادئ SOLID والتصميم الكائني"
REVIEWED_DATE_AR = "تمت المراجعة الفنية استناداً إلى توثيق أندرويد الرسمي في 2026-10-14."

DATA = {}

# ==========================================
# SOL-01: What does SOLID stand for, and why does it matter?
# ==========================================
DATA["SOL-01"] = {
    "concept_en": """SOLID is an acronym representing five foundational object-oriented design principles formulated by Robert C. Martin: Single Responsibility Principle (SRP), Open/Closed Principle (OCP), Liskov Substitution Principle (LSP), Interface Segregation Principle (ISP), and Dependency Inversion Principle (DIP). In professional Android engineering, these principles establish maintainable architectural boundaries, prevent God Objects like monolithic Activities and ViewModels, isolate volatile framework APIs from pure business logic, enable fast JVM unit testing via dependency inversion, and safeguard large multi-module codebases against regression cascades when features evolve.""",
    "walkthrough_en": """Mapping SOLID principles to modern Android Clean Architecture:
```kotlin
// S - Single Responsibility: Class handles only validation logic
class FormInputValidator {
    fun isValidEmail(email: String): Boolean = email.contains("@") && email.contains(".")
}

// O - Open/Closed: Extensible notification strategy without modifying existing sender
interface PushRenderer { fun render(payload: Map<String, String>) }
class OrderStatusPushRenderer : PushRenderer { override fun render(payload: Map<String, String>) { /* ... */ } }

// L - Liskov Substitution: Specialized repository fulfills base contract without surprises
interface UserRepository { suspend fun fetchUser(): Result<User> }
class NetworkUserRepository(private val api: UserApi) : UserRepository {
    override suspend fun fetchUser(): Result<User> = runCatching { api.getUser() }
}

// I - Interface Segregation: Client depends only on what it actually reads
interface ProfileReader { val currentUserName: Flow<String> }
interface ProfileUpdater { suspend fun updateName(newName: String) }

// D - Dependency Inversion: ViewModel depends on abstraction, not Room/Retrofit
class ProfileViewModel @Inject constructor(
    private val profileReader: ProfileReader // Inverted dependency
) : ViewModel() {
    val name = profileReader.currentUserName
}
```""",
    "short_en": """SOLID represents five foundational object-oriented design principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion. In Android engineering, these principles prevent monolithic God Activities, protect business logic from Android framework churn, enable fast parallel JVM unit testing through abstraction seams, and ensure that feature modules can be maintained and refactored independently without triggering application-wide regressions.""",
    "structured_en": """SOLID principles serve as the structural backbone of modern Android software engineering, transforming fragile codebases into modular, testable systems.
Each letter addresses a specific structural vulnerability. Single Responsibility prevents massive God Activities by ensuring each class has only one reason to change, dividing tasks across dedicated ViewModels, UseCases, and Repositories. Open/Closed allows features to be extended using polymorphic interfaces or strategies without editing existing tested code.
Liskov Substitution guarantees that subclasses and interface implementations can replace their parent abstractions without breaking behavioral contracts or throwing unexpected runtime exceptions. Interface Segregation prevents bloated interfaces by splitting monolithic contracts into fine-grained, client-specific APIs so consumers depend only on methods they actually use.
Finally, Dependency Inversion inverts source code dependencies: high-level business rules depend on pure domain abstractions rather than concrete database DAOs or network clients.
Together, these principles establish clear architectural seams, drastically cut down technical debt, and enable multiple engineering squads to scale multi-module Android codebases safely.""",
    "deep_senior_en": """Under the hood, SOLID principles are not academic ideals; they directly govern compilation boundaries, classloader efficiency, and memory allocations in production Android applications.
When a codebase violates Dependency Inversion and Single Responsibility by instantiating Room databases and Retrofit instances directly inside an Activity, the Android framework context becomes inextricably coupled to networking and persistence. This destroys JVM testability, forcing teams to rely on slow, flaky emulator-based instrumentation tests that hinder continuous delivery pipelines.
By enforcing Dependency Inversion via Dagger or Hilt, compilation graphs become directed acyclic graphs where high-level domain modules compile in parallel without depending on infrastructure details.
Furthermore, Interface Segregation and Liskov Substitution protect against binary incompatibility and fragile base class anti-patterns. In large Android teams, fat base classes like BaseActivity accumulate dozens of uncoordinated callbacks, lifecycle hooks, and analytics trackers. When a child screen overrides a method with an empty body or throws an exception, it violates Liskov Substitution and destabilizes UI navigation state machines.
By replacing bloated inheritance hierarchies with fine-grained interfaces and composition, memory footprints remain lean, Garbage Collection pressure decreases, and incremental Gradle build times improve dramatically because changes remain strictly localized within their corresponding module boundaries, ensuring sustainable long-term development velocity. This structural resilience protects large applications against regressions during rapid sprint cycles.""",
    "meta_ar": {
        "id": "SOL-01",
        "questionAr": "ما الذي يرمز إليه اختصار SOLID، ولماذا يُعتبر حيوياً في هندسة تطبيقات أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم المبادئ الخمسة الأساسية للتصميم الكائني (SOLID)، والقدرة على ربطها مباشرة بمعمارية أندرويد، وإدراك دورها في منع كائنات الـ God Objects وتسهيل اختبارات الـ JVM وعزل الموديولات.",
        "why_it_matters_ar": "تجاهل مبادئ SOLID ينتج عنه كود شديد التعقيد والتشابك (Spaghetti Code)، يجمع الـ UI والشبكة وقواعد البيانات في Activity واحدة، مما يجعل التطبيق مستحيلاً في الصيانة والاختبار.",
        "worked_example_ar": "تطبيق المبادئ في أندرويد:\n```kotlin\n// S: كلاس مستقل للتحقق\nclass Validator { fun check(e: String) = e.contains(\"@\") }\n// D: الـ ViewModel يعتمد على Interface وليس كلاس ملموس\nclass MyVM @Inject constructor(val repo: UserRepo) : ViewModel()\n```",
        "trade_offs_ar": "تطبيق SOLID يتطلب كتابة واجهات وكلاسات إضافية في البداية، لكنه يوفر وقتاً هائلاً في الصيانة ويمنع تراكم الديون التقنية ويسرع وقت البناء.",
        "failure_modes_ar": "بناء كلاسات عملاقة (God Activities) تقوم بالرسم والاتصال بالإنترنت والتحقق من المدخلات معاً، مما يكسر مبدأ S و D ويمنع كتابة اختبارات آلية.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد على SOLID لتقسيم المشروع لموديولات مستقلة بـ Clean Architecture، حيث تعتمد كل طبقة على واجهات نقية تتيح الاختبار بـ Fakes على الـ JVM.",
        "how_to_answer_ar": "اذكر المبادئ الخمسة بأسمائها بوضوح، واشرح أثرها المباشر في أندرويد: منع الـ God Activities، وعزل أندرويد عن منطق العمل، وتسهيل Unit Testing على الـ JVM، وتسريع الـ Build عبر عزل الموديولات.",
        "talking_points_ar": "المبادئ الخمسة (SRP, OCP, LSP, ISP, DIP)، ومشاكل كائنات الـ God Object، وعزل أندرويد عن كوتلن النقي، وتسهيل اختبارات الـ JVM السريعة.",
        "follow_ups_ar": "- **المحاور:** \"ما هو المبدأ الأكثر تأثيراً على سرعة كتابة اختبارات الـ Unit Tests؟\"\n  **المرشح:** \"مبدأ Dependency Inversion؛ لأنه بيسمح للـ ViewModel يعتمد على Interface للـ Repository بدل الداتابيز الحقيقية، فنقدر نمرر Fake Repository خفيف ونختبر الشاشة في أجزاء من الثانية على الـ JVM.\"\n\n- **المحاور:** \"هل الإفراط في تطبيق SOLID ممكن يضر المشروع؟\"\n  **المرشح:** \"نعم، لو عملنا تجريد مسبق غير مبرر بإنشاء إنترفيس لكل كلاس بسيط بدون وجود احتمالية لتغييره، وده بيزود عدد الملفات والجهد الذهني بدون فائدة.\"",
        "self_check_ar": "هل ذكرت المبادئ الخمسة بوضوح؟ هل بينت فائدتها في اختبارات JVM وفصل الموديولات؟ وهل دعمت إجابتك بأمثلة من واقع أندرويد؟",
        "references_ar": f"- [Clean Architecture by Robert C. Martin](https://en.wikipedia.org/wiki/Clean_code) — المرجع الأساسي لمبادئ SOLID.\n- [Guide to Android App Architecture](https://developer.android.com/topic/architecture) — دليل جوجل الرسمي لمعمارية التطبيقات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "اختصار SOLID بيمثل 5 مبادئ أساسية للتصميم الكائني: المسؤولية الواحدة (SRP)، والفتح للتوسيع والإغلاق للتعديل (OCP)، واستبدال ليسكوف (LSP)، وفصل الواجهات (ISP)، وقلب الاعتماديات (DIP). أهميتها القصوى في أندرويد إنها بتحمي المشروع من كوارث الـ God Activities، وبتعزل منطق العمل عن إطار عمل أندرويد المتقلب، وبتخلي الكود قابلاً للاختبار بنسبة 100% على الـ JVM، وبتسمح للفرق البرمجية بتطوير موديولات متعددة بدون ما تعديل ميزة يكسر ميزة تانية.",
        "best_answer_ar": "مبادئ SOLID هي البوصلة الهندسية اللي بتحول كود أندرويد من كود فوضوي ومتشابك لنظام مرن ونظيف وسهل الصيانة.\n\nكل حرف في الكلمة بيعالج مشكلة معمارية خطيرة:\nحرف S يعني المسؤولية الواحدة، وبسببه بنبطل نحط الفاليديشن وشغل الشبكة والداتابيز في الـ Activity، ونقسمهم على UseCases و Repositories مستقلة.\nحرف O يعني الكود مفتوح للإضافة ومغلق للتعديل، وده بنطبقه باستخدام الواجهات وأنماط زي Strategy عشان نضيف مزودي دفع أو تحليلات جدد بدون ما نعدل الكلاسات القديمة المختبرة.\nحرف L يعني مبدأ ليسكوف، وبيضمن إن أي كلاس ابن يقدر يحل محل الكلاس الأب بدون ما يكسر تصرف النظام أو يرمي استثناءات غير متوقعة.\nحرف I يعني فصل الواجهات، وبدل ما نعمل Interface عملاق فيه 20 دالة يجبر الكلاسات تنفذ دوال فاضية، بنقسمه لواجهات صغيرة محددة حسب حاجة كل عميل.\nحرف D يعني قلب التبعيات، وهو أساس المعمارية النظيفة؛ الطبقات العليا بتعتمد على Interfaces مجردة مش على كلاسات ملموسة للشبكة أو التخزين.\n\nالمبادئ دي مع بعض هي اللي بتخلينا نقدر نعمل Unit Tests كاملة على الـ JVM في ثوانٍ، ونبني مشاريع كبيرة مقسمة لموديولات متعددة بتتبني بسرعة وبأمان.",
        "deep_answer_ar": "تحت الكابوت، مبادئ SOLID مش مجرد نصائح نظرية، بل هي الأساس الحاكم لحدود الـ Compilation في Gradle وإدارة الذاكرة والـ Classloading في بيئة تشغيل أندرويد.\n\nلما المطورين بيكسروا مبادئ زي DIP و SRP، ويكتبوا كود بيعمل نيو لكلاسات Retrofit و Room داخل الـ UI Controller، هما بيربطوا سياق الـ Activity المعقد بمنطق العمل. النتيجة المباشرة لكده هي تدمير قابلية الاختبار؛ بيستحيل كتابة Unit Tests على الـ JVM، وبيضطر الفريق يعتمد على Instrumentation Tests بطيئة جداً ومتقلبة على المحاكي، وده بيعطل مسار الـ CI/CD اليومي.\n\nتطبيق مبدأ قلب التبعيات باستخدام Dagger و Hilt بيحول شجرة المشروع لـ Directed Acyclic Graph، وده بيسمح لموديولات الـ Domain النظيفة بالبناء بالتوازي في الـ CI/CD بدون ما تحتاج تستورد أي بايت من مكتبات أندرويد.\n\nكمان الجمع بين ISP و LSP هو الدرع الحامي من فخ الـ Fragile Base Class؛ فبدل ما نعمل `BaseActivity` ضخمة محشوة بكولباكات التتبع والدوال المساعدة اللي بتجبر بعض الشاشات تعمل Override بدوال فارغة، بنستبدل الوراثة بتركيب كائنات صغيرة (Composition) وواجهات دقيقة، وده بيقلل استهلاك الـ Heap Memory، وبيخفف الضغط على الـ Garbage Collector، ويضمن استقرار الشاشات وتدفق الملاحة في أصعب ظروف الإنتاج، مع الحفاظ على كفاءة واستهلاك بطارية الجهاز."
    }
}

# ==========================================
# SOL-02: Explain Single Responsibility Principle with an Android example.
# ==========================================
DATA["SOL-02"] = {
    "concept_en": """The Single Responsibility Principle (SRP) states that a class, module, or function should have one, and only one, reason to change, meaning it must be responsible to only a single business actor, stakeholder, or operational role. In Android development, SRP serves as the primary antidote against God Activities, God Fragments, and bloated ViewModels. A component that simultaneously coordinates UI rendering, inflates menus, validates user input, constructs HTTP requests, reads SQLite tables, and logs analytics events has half a dozen reasons to change. Violating SRP couples unrelated business concerns, creating severe regression risks whenever any individual responsibility is modified.""",
    "walkthrough_en": """Refactoring a God ViewModel violating SRP into cohesive, single-purpose components:
```kotlin
// BAD ANTI-PATTERN: Violates SRP (Too many reasons to change: validation, network, DB, UI state)
class BadRegistrationViewModel(private val api: Api, private val db: AppDb) : ViewModel() {
    fun register(email: String, pass: String) {
        if (!email.contains("@")) return // Reason 1: Validation policy changes
        val response = api.registerUser(email, pass) // Reason 2: API endpoints or auth headers change
        db.userDao().insert(response.toEntity()) // Reason 3: Database schema or caching rules change
        // Reason 4: UI presentation formatting changes
    }
}

// ARCHITECTURAL BEST PRACTICE: Single Responsibility per component
class EmailValidator @Inject constructor() { // One reason: Email format policies
    fun isValid(email: String): Boolean = email.isNotBlank() && email.matches(Regex("^[A-Za-z0-9+_.-]+@(.+)\\$"))
}

class RegisterUserUseCase @Inject constructor( // One reason: Registration business orchestration
    private val validator: EmailValidator,
    private val userRepository: UserRepository
) {
    suspend operator fun invoke(email: String, pass: String): Result<User> {
        if (!validator.isValid(email)) return Result.failure(InvalidEmailException())
        return userRepository.register(email, pass)
    }
}

class RegistrationViewModel @Inject constructor( // One reason: Managing Registration UI State
    private val registerUser: RegisterUserUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow<RegUiState>(RegUiState.Idle)
    val uiState: StateFlow<RegUiState> = _uiState.asStateFlow()
    fun onRegisterClicked(email: String, pass: String) { /* Updates UI state only */ }
}
```""",
    "short_en": """The Single Responsibility Principle dictates that a class should have only one reason to change, meaning it serves a single actor or concern. In Android, violating SRP creates God Activities that validate inputs, call network APIs, manage database caching, and format UI layouts. Applying SRP separates these responsibilities into distinct components: a Validator for input rules, a UseCase for business logic, a Repository for data persistence, and a ViewModel strictly for managing UI state.""",
    "structured_en": """The Single Responsibility Principle ensures that software components remain focused, maintainable, and isolated from unrelated feature churn.
In Android development, the most frequent violation of SRP is the God Class anti-pattern. Developers frequently cram entire user journeys into a single Activity or ViewModel. When a single class parses JSON, formats currency strings, interacts with GPS location managers, queries Room databases, and binds views, any change requested by product managers, design teams, or backend architects forces edits to the exact same file. This creates high cognitive friction, frequent merge conflicts, and high regression risks.
To adhere to SRP, responsibilities must be decomposed along natural actor boundaries.
The UI layer (Activity, Fragment, or Compose function) is responsible exclusively for rendering pixels and capturing user gestures. The ViewModel is responsible strictly for holding and exposing UI state machines.
Business rules and multi-repository coordination are encapsulated inside isolated UseCase classes, such as RegisterUserUseCase. Validation logic is moved into pure utility classes like EmailValidator, and data storage policies live inside Repositories.
Each class now has exactly one reason to change, making the codebase intuitive to navigate and trivially easy to unit test in isolation.""",
    "deep_senior_en": """Under the hood, Robert C. Martin refined the definition of SRP to state: 'A module should be responsible to one, and only one, actor.' Understanding this actor-based framing is what separates junior pattern matching from senior architectural design.
An actor represents a cohesive group of users, stakeholders, or system departments requiring changes. For example, marketing defines analytics formatting, the security team defines password hashing constraints, the DBA defines offline caching schemas, and the design team defines UI loading indicators.
If all four concerns live in a single UserProfileViewModel, changes demanded by marketing can inadvertently break authentication hashing or introduce database deadlocks across background threads.
Furthermore, enforcing SRP directly impacts compilation speed and memory utilization. In modern multi-module Gradle setups, dividing responsibilities creates distinct modules: :core:validation, :domain:auth, and :feature:auth. When validation logic changes, Gradle re-compiles only the tiny validation module without recompiling domain logic or presentation bytecode.
At the runtime level, single-responsibility classes adhere closely to the High Cohesion / Low Coupling principle. Their method dispatch tables remain small, optimizing ART inline caching, and their localized memory references ensure high CPU cache locality during execution, avoiding the creation of bloated objects that linger in generation-zero heap memory and trigger unnecessary garbage collection pauses.""",
    "meta_ar": {
        "id": "SOL-02",
        "questionAr": "اشرح مبدأ المسؤولية الواحدة (Single Responsibility Principle) مع ذكر مثال واقعي من أندرويد.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ المسؤولية الواحدة (SRP) ومفهوم سبب التغيير الواحد (One reason to change / Actor)، والقدرة على تفكيك كائنات الـ God Classes إلى مكونات نظيفة ومترابطة (High Cohesion).",
        "why_it_matters_ar": "حشو كل المهام داخل الـ Activity أو الـ ViewModel يجعل أي تعديل بسيط في الواجهة يهدد بكسر منطق الشبكة أو التخزين، ويخلق ملفات ضخمة يصعب قراءتها وتتكرر فيها نزاعات الدمج (Merge Conflicts).",
        "worked_example_ar": "تفكيك كلاس ينتهك SRP إلى مكونات مستقلة:\n```kotlin\n// كود نظيف: كل كلاس له مسؤولية واحدة وممثل واحد\nclass FormValidator { fun check(e: String) = ... }\nclass AuthUseCase(val repo: AuthRepo, val val: FormValidator) { ... }\nclass AuthViewModel(val auth: AuthUseCase) : ViewModel() { ... }\n```",
        "trade_offs_ar": "يزيد من عدد الملفات والكلاسات في المشروع، لكنه يمنح استقلالية تامة للميزات وسهولة فائقة في الـ Unit Testing وتعديل الكود بأمان.",
        "failure_modes_ar": "وضع منطق التحقق من صحة المدخلات وطلبات الـ API وعمليات الكاش في نفس الـ ViewModel، مما يجعله يملك عدة أسباب للتغيير.",
        "production_perspective_ar": "في المشروعات الكبيرة، نلزم المطورين بفصل المسؤوليات: الـ UI للرسم فقط، الـ ViewModel لإدارة الحالة، الـ UseCase لقواعد العمل، والـ Repository لجلب وتخزين البيانات.",
        "how_to_answer_ar": "عرف المبدأ بأن الكلاس يجب أن يملك سبباً واحداً فقط للتغيير (مسؤول أمام جهة واحدة Actor)، واذكر مثال الـ God Activity واشرح كيف نفككه إلى: Validator و UseCase و Repository و ViewModel، ووضح أثر ذلك على الاختبارات والـ Build.",
        "talking_points_ar": "مفهوم سبب واحد للتغيير (Reason to change)، ومفهوم الـ Actor، وتفكيك الـ God Activity، وأثر SRP على تقليل الـ Merge Conflicts وسرعة الـ Compilation.",
        "follow_ups_ar": "- **المحاور:** \"هل تقسيم الكلاس لكلاسات أصغر بزيادة يعتبر دائماً تطبيقاً صحيحاً لـ SRP؟\"\n  **المرشح:** \"لا، التقسيم العشوائي بدون وجود Actor واضح بيخلق تشتيت وتجريد وهمي (Over-engineering)؛ الهدف هو فصل المسؤوليات المتباينة مش تفتيت الكود بدون معنى.\"\n\n- **المحاور:** \"ما هي العلاقة بين SRP ومبدأ التماسك العالي (High Cohesion)؟\"\n  **المرشح:** \"علاقة طردية مباشرة؛ لما الكلاس يكون مسؤولاً عن وظيفة واحدة محددة، بتكون كل الدوال والخصائص اللي جواه بتخدم نفس الغرض وبتشتغل مع بعضها بتماسك شديد.\"",
        "self_check_ar": "هل عرفت المبدأ بدقة (سبب واحد للتغيير)؟ هل ذكرت مثال تفكيك الـ ViewModel؟ وهل ربطت بين المبدأ ومفهوم الـ Actor؟",
        "references_ar": f"- [The Single Responsibility Principle by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — مقال العم بوب حول المفهوم الدقيق لـ SRP والـ Actor.\n- [Android Architecture Best Practices](https://developer.android.com/topic/architecture/ui-layer) — إرشادات جوجل لطبقة العرض.",
        "quick_answer_ar": "مبدأ المسؤولية الواحدة (SRP) بينص على إن الكلاس أو الموديول لازم يكون له سبب واحد بس للتغيير، يعني يكون مسؤول قدام جهة عمل واحدة (Single Actor). في أندرويد، أشهر انتهاك للمبدأ ده هو كائنات الـ God Activity أو الـ God ViewModel اللي بتعمل كل حاجة: تفحص المدخلات، وتكلم السيرفر، وتخزن في Room، وترسم الشاشة. بنطبق المبدأ ده بفصل المهام: كلاس Validator لفحص البيانات، و UseCase لقواعد العمل، و Repository للتخزين والشبكة، و ViewModel لحفظ حالة الشاشة فقط.",
        "best_answer_ar": "مبدأ المسؤولية الواحدة (Single Responsibility Principle) هو خط الدفاع الأول لمنع تحول كود أندرويد لكتل ضخمة مشوهة بنسميها God Classes.\n\nفكرة المبدأ ببساطة مش إن الكلاس يعمل حاجة واحدة بس بالمعنى الحرفي، بل إنه يملك سبباً واحداً فقط للتعديل في المستقبل. يعني لو فريق الـ Backend غير شكل الـ API، وفريق الـ Design غير ألوان الشاشة، وفريق الـ Security غير شروط كلمة السر، مينفعش التغييرات التلاتة دي تجبرنا نعدل في نفس الملف!\n\nفي الكود السيئ، بنلاقي شاشة التسجيل (RegistrationActivity) بتعمل فحص للـ Email، وبتنادي Retrofit مباشرة، وبتحفظ الـ Token في EncryptedSharedPreferences، وبتحدث الـ Views. الكلاس ده عنده 4 أسباب مختلفة للتغيير، وأي تعديل فيه بيهدد بكسر باقي الوظائف.\n\nتطبيق SRP بيخلينا نقسم المنظومة دي باحترافية:\nبنعمل كلاس `EmailValidator` مسؤول عن شروط صحة البريد فقط.\nوبنعمل `RegisterUseCase` مسؤول عن تنسيق عملية التسجيل واستدعاء الخدمات.\nوبنعمل `UserRepository` مسؤول عن إدارة مصادر البيانات والـ Caching.\nوبنخلي الـ `RegistrationViewModel` مسؤول فقط عن توفير حالة الشاشة (UiState) وتمرير ضغطات المستخدم.\n\nالنتيجة إن كل كلاس بقى حجمه صغير، ومركّز جداً، ونقدر نكتب له Unit Test مستقل ومضمون في دقائق معدودة.",
        "deep_answer_ar": "تحت الكابوت، العم بوب (Robert C. Martin) أعاد صياغة المبدأ بتعريف أدق وأعمق: 'يجب أن يكون الموديول مسؤولاً أمام جهة واحدة فقط (Actor)'. فهم نقطة الـ Actor دي هي الفرق الحقيقي بين التطبيق السطحي للأنماط والنضج المعماري العالي.\n\nالـ Actor بيمثل جهة العمل أو المصلحة في الشركة؛ ففريق أمن المعلومات (Security) هو الـ Actor المسؤول عن قيود التشفير، وفريق التسويق (Marketing) مسؤول عن إحصائيات الـ Analytics، وفريق الـ UX مسؤول عن دورة حياة الواجهات. لما نجمع كل المسؤوليات دي في كلاس واحد زي `ProfileViewModel`، أي طلب تعديل من فريق الماركتنج ممكن ينتج عنه Race Condition تكسر التشفير أو تسرب الـ Context!\n\nكمان تطبيق SRP بينعكس إيجابياً وبشكل ملموس على سرعة بناء المشروع (Build Time) في Gradle. لما نفصل الكود لموديولات مستقلة زي `:core:validation` و `:domain:auth` و `:feature:auth`، أي تعديل في شروط الـ Validation هيخلي Gradle يبني موديول الـ Validation الصغير ده بس، بدون ما يحتاج يعيد عمل Compilation لموديول الـ Domain أو طبقة العرض بالكامل.\n\nوعلى مستوى بيئة التشغيل في أندرويد (ART Runtime)، الكلاسات اللي بتطبق SRP بتكون عالية التماسك (High Cohesion) ومنخفضة الارتباط (Low Coupling)، جداول التوجيه لدوالها (Virtual Method Tables) بتكون صغيرة وخفيفة على الـ CPU Cache، واستدعاءاتها بتستفيد من الـ Inlining بكفاءة عالية، مما يحافظ على سلاسة الأداء وسرعة معالجة الفريمات."
    }
}

# ==========================================
# SOL-03: Explain Open/Closed Principle with an Android example.
# ==========================================
DATA["SOL-03"] = {
    "concept_en": """The Open/Closed Principle (OCP) states that software entities (classes, modules, functions) should be open for extension, but closed for modification. This architectural rule mandates that systems must accommodate new functional behaviors, business rules, and third-party integrations without rewriting or mutating existing, fully tested, and verified source code. In Android development, OCP is implemented primarily through polymorphic interfaces, abstract base capabilities, and strategy registries. Rather than scattering monolithic when or switch branches across repositories and UI controllers, engineers define extensible contracts that allow new implementations to plug in seamlessly at compile time or runtime.""",
    "walkthrough_en": """Refactoring a rigid payment processor to adhere to Open/Closed Principle:
```kotlin
// BAD ANTI-PATTERN: Closed for extension, constantly modified when new gateways arrive
class FragilePaymentHandler(private val stripe: StripeSdk, private val paypal: PayPalSdk) {
    fun processPayment(type: String, amount: Long) {
        when (type) {
            "STRIPE" -> stripe.charge(amount)
            "PAYPAL" -> paypal.pay(amount)
            // Adding GooglePay or Klarna forces editing this tested class!
            else -> throw IllegalArgumentException("Unknown type")
        }
    }
}

// ARCHITECTURAL BEST PRACTICE: Open for extension, closed for modification
interface PaymentStrategy {
    fun supports(method: PaymentMethod): Boolean
    suspend fun execute(amount: Long): Result<TransactionReceipt>
}

class StripeStrategy @Inject constructor(private val client: StripeClient) : PaymentStrategy {
    override fun supports(method: PaymentMethod) = method == PaymentMethod.STRIPE
    override suspend fun execute(amount: Long) = client.charge(amount)
}

class PayPalStrategy @Inject constructor(private val client: PayPalClient) : PaymentStrategy {
    override fun supports(method: PaymentMethod) = method == PaymentMethod.PAYPAL
    override suspend fun execute(amount: Long) = client.authorize(amount)
}

// Extensible orchestrator: Never modified when new payment strategies are added!
class PaymentProcessor @Inject constructor(
    private val strategies: Set<@JvmSuppressWildcards PaymentStrategy>
) {
    suspend fun pay(method: PaymentMethod, amount: Long): Result<TransactionReceipt> {
        val strategy = strategies.find { it.supports(method) }
            ?: return Result.failure(UnsupportedOperationException("Unsupported gateway: $method"))
        return strategy.execute(amount)
    }
}
```""",
    "short_en": """The Open/Closed Principle mandates that software should be open for extension but closed for modification. In Android, instead of using sprawling when or switch blocks that inspect type flags and require constant edits whenever new features arrive, we rely on polymorphism and the Strategy pattern. By defining an interface like PaymentStrategy and injecting a collection of implementations, adding a new payment gateway or analytics tracker involves creating a new class without touching existing, tested codebase files.""",
    "structured_en": """The Open/Closed Principle provides stability and scalability by enabling systems to grow through additive changes rather than destructive edits.
In typical Android applications, the most visible violation of OCP appears as massive conditional dispatchers. When implementing payment providers, push notification handlers, or analytics tracking, developers often write centralized when expressions that check string keys or enums. Whenever product managers introduce a new provider like Google Pay or Braze, developers must modify existing, production-tested classes. This introduces high regression risks, requires re-running entire test suites, and creates merge conflicts across feature branches.
Applying OCP decouples execution from concrete variants through polymorphism.
First, an interface establishes a contract for the capability, defining an execution signature and a predicate method to check support.
Second, concrete providers implement this interface in independent, self-contained classes.
Third, the orchestrating class injects a collection of these strategies, querying the appropriate provider polymorphically at runtime.
When a new requirement emerges, developers simply create a new class implementing the interface and bind it via dependency injection. Existing orchestrator classes remain completely closed to modification, eliminating regression risks and ensuring zero disruption to existing business flows.""",
    "deep_senior_en": """Under the hood, the Open/Closed Principle transforms hardcoded control flow branches into dynamic polymorphic dispatch tables (v-tables) or hash-based dependency injection lookups.
In large-scale Android development, coupling systems to monolithic when expressions creates significant compilation bottlenecks. When a single central class references every payment provider SDK, changes to any provider dependency force Gradle to recompile the shared file and all downstream consumers.
By restructuring the system around OCP with Dagger Multibindings (@IntoSet or @IntoMap), each provider lives in an isolated Gradle feature module. Adding a new provider creates a new independent compilation unit that Gradle compiles in parallel, keeping build times constant regardless of application feature growth.
Furthermore, OCP is foundational to Android framework design and modern UI paradigms. In the Android OS, RecyclerView does not contain hardcoded if-statements checking whether to display a text row, an image grid, or a video card. Instead, RecyclerView.Adapter is open for extension via onCreateViewHolder and onBindViewHolder while remaining completely closed to internal framework modifications.
Similarly, Jetpack Compose utilizes slot-based APIs (slots pattern) where composable containers accept generic @Composable () -> Unit lambdas, allowing engineers to extend UI structures arbitrarily without modifying the parent layout mechanics or introducing runtime state regressions. This slot architecture provides effortless extensibility while completely shielding the core layout runtime from unexpected modifications.""",
    "meta_ar": {
        "id": "SOL-03",
        "questionAr": "اشرح مبدأ الفتح والإغلاق (Open/Closed Principle) مع ذكر مثال عملي من أندرويد.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ OCP، والقدرة على استبدال كتل when الشرطية الضخمة بالتعددية الشكلية (Polymorphism) ونمط Strategy، وإدراك فوائد المبدأ في تقليل الـ Regressions وتسريع الـ Build في المشاريع الكبيرة.",
        "why_it_matters_ar": "الاعتماد على جمل when المركزية يجبر المطورين على تعديل كود قديم ومختبر مع كل ميزة جديدة، مما يخلق مخاطر عالية لظهور أخطاء غير متوقعة ونزاعات دمج مستمرة في Git.",
        "worked_example_ar": "تطبيق OCP باستخدام Strategy ونظام الـ Plugins:\n```kotlin\n// إنترفيس مفتوح للإضافة\ninterface PayStrategy { fun pay(amount: Long) }\n// إضافة مزود جديد بكلاس مستقل بدون تعديل الكود القديم\nclass GooglePayStrategy : PayStrategy { override fun pay(amount: Long) { ... } }\n// المنسق مغلق للتعديل ويستقبل أي مزود\nclass PayManager(val strategies: List<PayStrategy>) { ... }\n```",
        "trade_offs_ar": "يضيف واجهات وكلاسات إضافية بدلاً من كتابة when سريعة، لكنه يمنع تماماً أخطاء الـ Regression ويجعل النظام قابلاً للتوسع اللانهائي بأمان.",
        "failure_modes_ar": "استخدام جمل when عملاقة لفحص أنواع الإشعارات أو بوابات الدفع، والاضطرار لتعديل نفس الكلاس عند كل تحديث.",
        "production_perspective_ar": "في المشروعات الضخمة، نستخدم Dagger Multibindings لحقن مجموعات من الـ Strategies (@IntoSet)، مما يتيح لكل فريق إضافة ميزته في موديول مستقل بدون لمس كود الفرق الأخرى.",
        "how_to_answer_ar": "عرف المبدأ: الكود مفتوح للتوسيع ومغلق للتعديل، واشرح عيب كتل when الضخمة ككسر للمبدأ، واعرض الحل بنمط Strategy و Dagger Multibindings، واستشهد بتصميم RecyclerView.Adapter كنموذج من صلب أندرويد.",
        "talking_points_ar": "مفهوم Open for extension / Closed for modification، واستبدال when بـ Polymorphism، وتطبيق Dagger @IntoSet، ومثال RecyclerView.Adapter ونمط الـ Slots في Compose.",
        "follow_ups_ar": "- **المحاور:** \"هل جملة when في كوتلن تعتبر دائماً انتهاكاً لمبدأ OCP؟\"\n  **المرشح:** \"لا، لو بنتعامل مع Sealed Class بتمثل نطاقاً مغلقاً ومحدوداً زي UiState، استخدام when بيكون ممتاز وإلزامي، لكن الانتهاك بيحصل لما نستخدمها لفرز ميزات وأنظمة متغيرة ومفتوحة للإضافة زي بوابات الدفع أو الإشعارات.\"\n\n- **المحاور:** \"كيف يطبق RecyclerView.Adapter مبدأ OCP؟\"\n  **المرشح:** \"كلاس الـ RecyclerView مغلق تماماً للتعديل ولا نلمس كوده، لكنه مفتوح للتوسيع عبر دوال الـ Adapter زي onCreateViewHolder و onBindViewHolder لعرض أي نوع Views نريده.\"",
        "self_check_ar": "هل عرفت المبدأ بدقة؟ هل وضحت عيوب when المتضخمة؟ وهل ذكرت أمثلة أندرويد الواقعية مثل RecyclerView و Compose Slots؟",
        "references_ar": f"- [The Open-Closed Principle by Robert C. Martin](https://web.archive.org/web/20060822033332/http://www.objectmentor.com/resources/articles/ocp.pdf) — الورقة البحثية الأصلية للعم بوب.\n- [Jetpack Compose Slot APIs](https://developer.android.com/develop/ui/compose/layouts/basics#slot-based-layouts) — التوثيق الرسمي لنمط الـ Slots في Compose.",
        "quick_answer_ar": "مبدأ الفتح والإغلاق (Open/Closed Principle) بينص على إن الكيان البرمجي لازم يكون مفتوحاً للإضافة والتوسيع (Open for extension)، ومغلقاً أمام التعديل (Closed for modification). في أندرويد، بدل ما نعمل جمل `when` عملاقة بتفحص أسماء بوابات الدفع أو أنواع الإشعارات وتجبرنا نعدل نفس الملف مع كل ميزة جديدة، بنستخدم الـ Polymorphism ونمط Strategy. بنعرف Interface موحد، ولما نحتاج نضيف مزود دفع جديد، بنعمل كلاس جديد يطبقه بدون ما نلمس سطر واحد في الكلاسات القديمة المختبرة.",
        "best_answer_ar": "مبدأ الفتح والإغلاق (OCP) هو السر وراء بقاء المشروعات الكبيرة قابلة للتوسع بدون ما تنهار مع كل تحديث جديد.\n\nالمعنى الحقيقي للمبدأ هو إنك لما تحتاج تضيف وظيفة جديدة للتطبيق، لازم تضيفها عن طريق كتابة كود جديد تماماً، مش عن طريق تعديل وتشريح كود قديم شغال ومستقر في الإنتاج.\n\nأشهر انتهاك بنشوفه هو كلاسات معالجة المدفوعات أو الإشعارات؛ تلاقي كلاس فيه دالة `processPayment` جواها `when (type)` عملاقة بتفحص Stripe و PayPal. أول ما الشركة تقرر تدعم Google Pay، المطور بيروح يفتح نفس الكلاس القديم ويكتب فرع جديد. الحركة دي بتكسر مبدأ OCP صراحة، لأنها بتعرض الكود المستقر لاحتمالات أخطاء الـ Regression، وبتتطلب إعادة اختبار كل الطرق القديمة، وبتعمل خناقات في دمج الفروع (Merge Conflicts).\n\nالحل المتين هو استخدام التعددية الشكلية (Polymorphism) ونمط Strategy. بنعمل إنترفيس `PaymentStrategy`، وكل بوابة بتنفذه في كلاس مستقل. والكلاس المنسق بيستقبل قائمة أو خريطة من الاستراتيجيات دي عبر الـ Dependency Injection. ولما نحتاج نضيف Google Pay، بنكتب كلاس `GooglePayStrategy` وبنربطه في الـ Module، بدون ما نفتح الكلاس القديم أو نغير فيه حرف واحد.\n\nده نفس الأسلوب اللي مبني عليه نظام أندرويد نفسه في `RecyclerView`؛ فالنظام مبيعدلش كود الـ RecyclerView عشان يعرض عناصر جديدة، بل بيعتمد على إنك تعمل Subclass للـ `Adapter`.",
        "deep_answer_ar": "تحت الكابوت، مبدأ الفتح والإغلاق بيستبدل التفرع الشرطي الثابت في كود المصدر (Hardcoded Branching) بجداول التوجيه الديناميكي (Virtual Method Tables - V-Tables) والبحث الرياضي في قواميس الـ Dependency Injection.\n\nفي المشاريع الضخمة، كسر OCP بيعمل اختناق شديد في وقت الـ Compilation لـ Gradle. لما كلاس مركزي واحد يكون عارف كل مكتبات الـ SDKs الخاصة بالدفع أو التحليلات، أي تعديل في أي مكتبة هيجبر Gradle إنه يعيد بناء الكلاس ده وكل الشاشات اللي معتمدة عليه. بينما لما نطبق OCP مع Dagger Multibindings عبر `@IntoSet` أو `@IntoMap`، كل مزود بيعيش في موديول مستقل تماماً. إضافة مزود جديد بتعتبر موديول إضافي يبنيه Gradle بالتوازي في الـ CI/CD بدون ما يعيد بناء أي جزء قديم من المشروع.\n\nكمان المبدأ ده متجسد في قلب أحدث تقنيات أندرويد زي Jetpack Compose من خلال نمط الـ Slot APIs. الكومبوننت زي `Scaffold` أو `TopAppBar` معندهاش كود داخلي بيحدد شكل الزرار أو الأيقونة بدقة، بل بتسيب Slots مفتوحة على شكل Lambdas: `@Composable () -> Unit`. ده بيسمح لك كمهندس إنك توسع شكل الواجهة وتضيف فيها أي تصميم يعجبك، بينما كود الـ Scaffold الأصلي مغلق ومحمي من أي تعديل.\n\nالمهندسون الكبار بيفرقوا بدقة بين استخدام OCP في الأنظمة المتغيرة، واستخدام `when` المغلقة مع Kotlin Sealed Classes في مجالات النطاق الثابت (Closed Domains)؛ فالأولى للتوسع اللانهائي، والتانية للتحقق الإلزامي من الحالات الحصرية."
    }
}

# ==========================================
# SOL-04: Explain Liskov Substitution Principle with an Android example.
# ==========================================
DATA["SOL-04"] = {
    "concept_en": """The Liskov Substitution Principle (LSP), formulated by Barbara Liskov, asserts that subtypes must be completely substitutable for their base types without altering the correctness, invariants, or expected behaviors of the host program. Formally, behavioral subtyping mandates that preconditions cannot be strengthened in a subtype, postconditions cannot be weakened, and history constraints must be preserved. In Android engineering, LSP violations frequently manifest when subclasses throw UnsupportedOperationException, return arbitrary nulls to bypass inherited contracts, or silently no-op inherited lifecycle methods in bloated base classes (such as BaseFragment or BaseAdapter).""",
    "walkthrough_en": """Contrasting an LSP violation with behavioral subtyping in an Android Repository:
```kotlin
// BAD ANTI-PATTERN: Violates LSP (Subtype breaks base contract by throwing UnsupportedOperationException)
interface CacheableRepository<T> {
    suspend fun get(): T
    suspend fun save(item: T) // Base contract implies all implementations can save!
}

class ReadOnlyRemoteRepository : CacheableRepository<UserConfig> {
    override suspend fun get(): UserConfig = fetchFromRemote()
    override suspend fun save(item: UserConfig) {
        // Blatant LSP Violation! Calling code expecting CacheableRepository crashes at runtime!
        throw UnsupportedOperationException("Read-only repository cannot save data")
    }
}

// ARCHITECTURAL BEST PRACTICE: Segregated contracts adhering to Liskov Substitution
interface ReadableDataSource<T> { suspend fun get(): T }
interface WritableDataSource<T> { suspend fun save(item: T) }

// Fully substitutable readable repository
class ReadOnlyRemoteConfig(private val api: ConfigApi) : ReadableDataSource<UserConfig> {
    override suspend fun get(): UserConfig = api.fetchConfig()
}

// Fully substitutable read-write repository
class LocalDiskCache(private val dao: ConfigDao) : ReadableDataSource<UserConfig>, WritableDataSource<UserConfig> {
    override suspend fun get(): UserConfig = dao.getConfig()
    override suspend fun save(item: UserConfig) = dao.insertConfig(item)
}
```""",
    "short_en": """The Liskov Substitution Principle asserts that any subtype must be completely substitutable for its parent type without breaking application correctness. In Android, violating LSP commonly occurs when a subclass throws UnsupportedOperationException or returns unexpected nulls to avoid executing an inherited method. We adhere to LSP by keeping base interfaces focused, honoring all inherited behavioral contracts, and preferring fine-grained composition over deep inheritance hierarchies.""",
    "structured_en": """The Liskov Substitution Principle ensures that inheritance hierarchies represent genuine behavioral compatibility rather than superficial code reuse.
LSP goes beyond syntactic type matching to enforce behavioral contracts. If class B extends class A, any component designed to operate on an instance of A must function correctly when given an instance of B, without requiring runtime type inspections like instanceof or is checks.
In Android development, LSP is routinely violated in data persistence and base UI hierarchies. A notorious example is defining a general-purpose repository interface with both read and write methods, and then implementing a read-only variant that throws UnsupportedOperationException inside the write method. When background sync workers or UseCases invoke the write method expecting normal execution, the application crashes with an unexpected runtime exception.
Another frequent violation occurs in UI code with bloated BaseFragment or BaseActivity classes that mandate methods like setupToolbar() or enableSwipeRefresh(). When a child screen without a toolbar overrides the method with an empty body, it breaks caller invariants and creates subtle rendering bugs.
To uphold LSP, engineers replace monolithic inheritance hierarchies with fine-grained interfaces. By splitting contracts into distinct Readable and Writable interfaces, every implementing class satisfies its entire contract unconditionally.""",
    "deep_senior_en": """Under the hood, the Liskov Substitution Principle is formalized through Design by Contract: a subtype may weaken preconditions (demand less) and strengthen postconditions (guarantee more), but never the reverse.
In Android runtime execution, violating LSP introduces insidious failure modes that evade compile-time detection. When a subclass strengthens a precondition by requiring non-null arguments where the base contract permitted nullable parameters, or when a subclass weakens postconditions by returning an uninitialized state machine, callers relying on polymorphism execute incorrect branch paths.
A classic Android framework violation occurred in Java collections, where Collections.unmodifiableList() implemented java.util.List but threw UnsupportedOperationException on add(). If an Android engineer passes an unmodifiable list to an adapter expecting a mutable list, crashes occur at runtime.
Staff engineers eliminate these risks in modern Kotlin through type-system design and immutable data modeling. Kotlin explicitly separates List (read-only interface) from MutableList (read-write interface), baking LSP compliance directly into the language standard library.
Furthermore, in modern Jetpack Compose architectures, LSP violations are systematically eradicated because Compose completely abandons deep class inheritance in favor of pure function composition, immutable state data classes, and Modifier chaining, rendering classical inheritance substitute bugs obsolete across all UI presentation layers. By enforcing contract invariants through explicit interfaces, runtime regressions are caught at compile time rather than crashing user devices in production.""",
    "meta_ar": {
        "id": "SOL-04",
        "questionAr": "اشرح مبدأ استبدال ليسكوف (Liskov Substitution Principle) مع ذكر مثال عملي من أندرويد.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ ليسكوف (LSP) والتوافق السلوكي (Behavioral Subtyping)، والقدرة على رصد انتهاكاته الشهيرة كرمي UnsupportedOperationException، وحل مشاكل الوراثة عبر فصل الواجهات والتركيب.",
        "why_it_matters_ar": "انتهاك مبدأ ليسكوف يؤدي لانهيارات مفاجئة في وقت التشغيل (Runtime Crashes)؛ حيث يفترض كود النظام أن الكائن يطبق عقداً معيناً، فيفاجأ باستثناء غير موثق يوقف التطبيق.",
        "worked_example_ar": "تصحيح انتهاك ليسكوف بفصل الإنترفيسات:\n```kotlin\n// كود سيئ: يكسر ليسكوف برمي استثناء\nclass ReadOnlyRepo : Repo { override fun save() = throw UnsupportedOperationException() }\n// كود نظيف: واجهات دقيقة ومتوافقة سلوكياً 100%\ninterface Reader { fun get() }\ninterface Writer { fun save() }\nclass ReadOnlyRepo : Reader { override fun get() = ... }\n```",
        "trade_offs_ar": "يتطلب تفكيك الواجهات الكبيرة إلى واجهات صغيرة محددة، لكنه يضمن موثوقية كاملة ويمنع حدوث أي انهيارات غير متوقعة في وقت التشغيل.",
        "failure_modes_ar": "وراثة كلاس وإعادة كتابة دالة لترمي `UnsupportedOperationException` أو ترك جسم الدالة فارغاً بشكل يكسر توقعات الكلاس الأب.",
        "production_perspective_ar": "في المشروعات الحديثة، نتجنب الوراثة العميقة و `BaseActivity` تماماً، ونعتمد على ميزة كوتلن في فصل `List` عن `MutableList` لضمان التوافق السلوكي وقت الـ Compile time.",
        "how_to_answer_ar": "عرف المبدأ: الكلاس الابن يجب أن يحل محل الكلاس الأب بدون كسر صحة البرنامج، واذكر المثال الشهير للانتهاك: كلاس يرمي UnsupportedOperationException، واشرح الحل بفصل الواجهات واستشهد بفصل List عن MutableList في كوتلن.",
        "talking_points_ar": "مفهوم Behavioral Subtyping، ومخاطر UnsupportedOperationException، وفصل الواجهات كحل لليسكوف، ونقاء Jetpack Compose في تجنب الوراثة كلياً.",
        "follow_ups_ar": "- **المحاور:** \"كيف عالجت لغة كوتلن انتهاك ليسكوف التاريخي في Java Collections؟\"\n  **المرشح:** \"جافا كانت بتخلي `List` فيها دالة `add()` وترمي استثناء لو القائمة Unmodifiable؛ كوتلن حلتها معمارياً بفصل `List` كـ Read-only عن `MutableList` كـ Read-Write في صلب نظام الأنواع.\"\n\n- **المحاور:** \"هل كتابة دالة Override فارغة (Empty body) تعتبر دائماً كسر لليسكوف؟\"\n  **المرشح:** \"لو الدالة الأصلية في العقد الأب كان استدعاؤها مشروطاً بأثر جانبي متوقع من النظام (زي حفظ حالة أو إطلاق كولباك) وتجاهلها سبب خلل في تدفق العمل، نعم تعتبر كسراً لليسكوف.\"",
        "self_check_ar": "هل عرفت المبدأ بدقة؟ هل شرحت مثال رمي الاستثناء؟ وهل ربطت الإجابة بنظام أنواع كوتلن وتصميم Jetpack Compose؟",
        "references_ar": f"- [Behavioral Subtyping by Barbara Liskov](https://en.wikipedia.org/wiki/Liskov_substitution_principle) — المرجع الأكاديمي الأصلي لباربرا ليسكوف.\n- [Kotlin Collections Design](https://kotlinlang.org/docs/collections-overview.html) — توثيق كوتلن الرسمي لتصميم القوائم.",
        "quick_answer_ar": "مبدأ استبدال ليسكوف (LSP) بينص على إن أي كلاس ابن لازم يقدر يحل محل الكلاس الأب بتاعه بالكامل بدون ما يكسر تصرف أو صحة البرنامج. في أندرويد، أشهر انتهاك للمبدأ ده هو إن كلاس ابن يعمل Override لدالة موروثة ويرمي جواها `UnsupportedOperationException` أو يرجع `null` غير متوقع عشان يتهرب من تنفيذها. بنلتزم بالمبدأ ده عن طريق تجنب الكلاسات الممتلئة بالدوال، وتقسيم الواجهات لعقود دقيقة ومحددة، وتفضيل التركيب (Composition) على الوراثة.",
        "best_answer_ar": "مبدأ ليسكوف (Liskov Substitution Principle) هو الضمان الحقيقي لصحة استخدام الوراثة في البرمجة الكائنية.\n\nالمبدأ مش مجرد إن الكود يـ Compile صح، بل إن السلوك البرمجي (Behavioral Contract) يفضل متوافق ومضمون. لو عندك دالة في التطبيق بتاخد كائن من نوع `Repository`، لازم أي Subclass تمرره للدالة دي يشتغل بكفاءة وبدون أي مفاجآت أو شروط خفية.\n\nأشهر مثال لانتهاك ليسكوف في أندرويد بنشوفه في التعامل مع قواعد البيانات؛ تلاقي إنترفيس عام اسمه `UserRepository` فيه دالة `getUser` ودالة `saveUser`. يجي مطور محتاج كاش للقراءة فقط (Read-only)، فيعمل كلاس يطبق نفس الإنترفيس، وفي دالة `saveUser` يرمي `throw UnsupportedOperationException(\"Not supported\")`! لما يجي كود تاني في الخلفية ينادي دالة الحفظ معتمداً على إن الكائن هو `UserRepository`، التطبيق هيحصله Crash فوري في الإنتاج.\n\nنفس المشكلة كانت بتحصل في كلاسات الـ `BaseFragment` العملاقة اللي بتجبر كل الشاشات تعمل Override لدالة `setupToolbar()`. الشاشة اللي مفيهاش Toolbar بتضطر تسيب جسم الدالة فاضي أو ترجع null، وده بيكسر توقعات الكلاس الأب وبيخلق أخطاء بصرية ومشاكل ملاحة غريبة.\n\nالحل الهندسي لمبدأ ليسكوف هو تقسيم العقود؛ نفصل القراءة في واجهة `ReadableDataSource` والكتابة في `WritableDataSource`. بكده الكلاس اللي محتاج قراءة بس هيطبق واجهة القراءة فقط، ويستحيل يحصل كسر للتوقعات أو انهيارات غير متوقعة.",
        "deep_answer_ar": "تحت الكابوت، مبدأ ليسكوف بيتم التعبير عنه رياضياً بنظرية 'التصميم بالعقود' (Design by Contract): الشروط المسبقة (Preconditions) لا يمكن تشديدها في الابن، والشروط اللاحقة (Postconditions) لا يمكن إضعافها، ومحددات الحالة الثابتة (Invariants) يجب الحفاظ عليها بالكامل.\n\nفي بيئة تشغيل أندرويد، كسر ليسكوف هو السبب الخفي وراء أصعب أخطاء الـ Runtime التي تفلت من كومبايلر جافا. المثال التاريخي الشهير هو `Collections.unmodifiableList()` في Java؛ الكائن بيورث `java.util.List` لكنه بيرمي `UnsupportedOperationException` لو ناديت `add()`. كوتلن عالجت العيب المعماري ده جذرياً في لغتها عن طريق فصل `List` غير القابلة للتعديل عن `MutableList` في صلب الـ Type System، مما فرض احترام مبدأ ليسكوف إجبارياً في وقت الـ Compilation.\n\nكمان في المعمارية الحديثة مع Jetpack Compose، مبدأ ليسكوف تم تعزيزه بالتخلي التام عن شجرة الوراثة الكلاسيكية للواجهات. في نظام الـ Views القديم، كل الـ Widgets كانت بتورث من كلاس `View` الضخم اللي فيه آلاف السطور، وأي كاستم فيو بيغير سلوك دالة زي `onMeasure` أو `performClick` كان معرض لكسر الـ Accessibility وتوقعات النظام. الكومبوز استبدل ده كله بدوال نقية وتركيب معتمد على `Modifier` و Data Classes غير قابلة للتعديل، وده قضى تماماً على مشاكل الوراثة المعطوبة في واجهات أندرويد."
    }
}

# ==========================================
# SOL-05: Explain Interface Segregation Principle with an Android example.
# ==========================================
DATA["SOL-05"] = {
    "concept_en": """The Interface Segregation Principle (ISP) dictates that clients should never be forced to depend upon interfaces or methods that they do not use. Instead of authoring monolithic, 'fat' interfaces containing dozens of heterogeneous operational methods, software architects must decompose contracts into small, highly cohesive, client-specific role interfaces. In Android development, fat interfaces create cognitive bloat, force implementing classes to provide meaningless empty-body stubs for irrelevant callbacks, and couple unrelated feature modules together, causing re-compilation ripple effects across the entire dependency graph whenever any single signature in the bloated interface is modified.""",
    "walkthrough_en": """Refactoring a bloated Android listener into segregated, role-specific interfaces:
```kotlin
// BAD ANTI-PATTERN: Fat interface forces implementers to write empty stubs (like legacy TextWatcher)
interface MassiveUserProfileContract {
    fun loadBasicInfo()
    fun updateAvatar(url: String)
    fun processSubscriptionPayment(amount: Long) // Irrelevant to a simple profile view!
    fun exportGdprData() // Irrelevant to normal app sessions!
}

// ARCHITECTURAL BEST PRACTICE: Segregated, role-specific interfaces
interface ProfileReader {
    val userProfile: Flow<UserProfile>
}

interface AvatarUploader {
    suspend fun uploadAvatar(imageBytes: ByteArray): Result<String>
}

interface SubscriptionBilling {
    suspend fun paySubscription(amount: Long): Result<Receipt>
}

// Profile Header component depends ONLY on what it actually needs
class ProfileHeaderPresenter @Inject constructor(
    private val profileReader: ProfileReader // Dependent strictly on read capabilities!
) {
    fun bind(view: ProfileHeaderView) { /* Consumes profileReader exclusively */ }
}
```""",
    "short_en": """The Interface Segregation Principle states that clients should never be forced to depend on methods they do not use. In Android, the classic violation is the legacy Java TextWatcher, where developers wanting only afterTextChanged were forced to implement beforeTextChanged and onTextChanged with empty bodies. Applying ISP breaks fat interfaces into focused, role-specific contracts, such as separating a monolithic repository into ProfileReader and ProfileUpdater interfaces.""",
    "structured_en": """The Interface Segregation Principle ensures that contracts between components remain minimal, purposeful, and decoupled from extraneous functionality.
When an interface accumulates too many responsibilities, it becomes a 'fat interface'. Consumers that require only a fraction of those capabilities are forced to depend on the entire definition. In Android, this creates two major problems: boilerplate clutter and undesirable architectural coupling.
A famous Android framework example is the legacy android.text.TextWatcher interface. It declared three distinct callback methods: beforeTextChanged, onTextChanged, and afterTextChanged. In ninety percent of use cases, developers only care about reacting to the final text in afterTextChanged. Yet, every implementation was forced to declare empty boilerplate overrides for the other two methods. Android Jetpack eventually corrected this with the core-ktx doAfterTextChanged extension lambda.
In application architecture, ISP is vital when designing repositories and data sources. If a single UserRepository interface contains methods for fetching public user info, updating admin permissions, and billing subscriptions, a simple UI header component depends unnecessarily on sensitive billing and admin methods.
By segregating the interface into ProfileReader, RoleManager, and BillingService, consumers depend strictly on the capabilities they actually consume.""",
    "deep_senior_en": """Under the hood, the Interface Segregation Principle directly optimizes binary interface contracts (ABI), incremental compilation graphs, and mock footprint in unit test suites.
In multi-module Android codebases, if Module A depends on a fat interface defined in Module B, any change to an unused method signature in that interface changes Module B's public ABI. This invalidates Gradle's incremental compilation cache, forcing the compiler to re-analyze and recompile Module A and all downstream dependencies, even though Module A never called the modified method.
By segregating fat interfaces into granular role interfaces (often single-abstract-method SAM interfaces in Kotlin), Gradle's compilation avoidance mechanics successfully skip recompiling unaffected consumer modules, drastically accelerating build speeds in enterprise teams.
From a testability standpoint, ISP eliminates mocking friction. When writing unit tests for a ViewModel that consumes a 20-method repository, developers often struggle with verbose mocking configurations where every uncalled method must be stubbed or ignored. With fine-grained role interfaces, writing a lightweight in-memory fake takes less than ten lines of pure Kotlin code.
Furthermore, Kotlin's language features natively reinforce ISP through first-class functional types ((String) -> Unit) and interface delegation (by), allowing classes to compose multiple segregated interfaces cleanly without manual forwarding boilerplate, keeping the runtime footprint exceptionally lightweight.""",
    "meta_ar": {
        "id": "SOL-05",
        "questionAr": "اشرح مبدأ فصل الواجهات (Interface Segregation Principle) مع ذكر مثال واقعي من أندرويد.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ فصل الواجهات (ISP)، والقدرة على تفكيك الواجهات المتضخمة (Fat Interfaces) إلى واجهات دقيقة حسب دور العميل (Role Interfaces)، وإدراك تأثير المبدأ على سرعة الـ Build وسهولة كتابة الـ Fakes في التيست.",
        "why_it_matters_ar": "الواجهات المتضخمة تجبر المطورين على كتابة دوال فارغة لا فائدة منها، وتربط أجزاء التطبيق بوظائف لا تحتاجها، مما يسبب إعادة بناء (Recompilation) للمشروع بالكامل عند تعديل أي دالة غير مستخدمة.",
        "worked_example_ar": "تفكيك TextWatcher أو مستودع متضخم:\n```kotlin\n// كود سيئ: واجهة تفرض دوالاً غير مطلوبة\ninterface UserActions { fun read(); fun write(); fun deleteAccount() }\n// كود نظيف: واجهات مفصولة حسب احتياج العميل\ninterface UserReader { fun read(): User }\ninterface UserWriter { fun write(u: User) }\n```",
        "trade_offs_ar": "يزيد من عدد ملفات الإنترفيسات في المشروع، لكنه يمنح استقلالية تامة للعملاء ويمنع إعادة بناء الموديولات غير المعنية ويسهل الاختبارات.",
        "failure_modes_ar": "إنشاء Interface موحد وشامل لكل عمليات الـ CRUD والـ Billing والـ Auth وإجبار كل شاشة على اعتماده بالكامل.",
        "production_perspective_ar": "في المشروعات الكبيرة، نفضل تمرير Lambdas مباشرة أو استخدام واجهات SAM محددة، ونقسم الـ Repositories لواجهات قراءة وكتابة منفصلة لحماية الشاشات البسيطة.",
        "how_to_answer_ar": "عرف المبدأ: العميل يجب ألا يُجبر على الاعتماد على دوال لا يستخدمها، واذكر مثال أندرويد الكلاسيكي TextWatcher واشرح كيف حلتها KTX بـ doAfterTextChanged، واشرح كيف نقسم مستودع المستخدم لواجهات قراءة وكتابة دقيقة، ووضح أثر ذلك على الـ Build والـ Fakes.",
        "talking_points_ar": "مفهوم Fat Interface مقابل Role Interface، ومثال TextWatcher و doAfterTextChanged، وسرعة البناء بـ Compilation Avoidance في Gradle، وسهولة كتابة الـ Fakes في التيست.",
        "follow_ups_ar": "- **المحاور:** \"كيف حلت مكتبة Android KTX مشكلة TextWatcher؟\"\n  **المرشح:** \"عبر Extension Functions بتستقبل Lambdas فردية زي `doAfterTextChanged`؛ فالمطور بيمرر فقط البلوك اللي محتاجه بدون ما يضطر يعمل كلاس ينفذ الدوال التلاتة.\"\n\n- **المحاور:** \"كيف يؤثر مبدأ ISP على سرعة الـ Compilation في Gradle؟\"\n  **المرشح:** \"عبر الـ Compilation Avoidance؛ لما الواجهة تكون صغيرة ومحددة، تعديل دالة في واجهة تانية مش هيجبر Gradle إنه يعيد بناء الموديولات اللي بتعتمد على الواجهة الأولى.\"",
        "self_check_ar": "هل عرفت المبدأ بدقة؟ هل ذكرت مثال TextWatcher؟ وهل وضحت الفائدة على اختبارات الـ Fakes وسرعة بناء الموديولات؟",
        "references_ar": f"- [Interface Segregation Principle by Robert C. Martin](https://en.wikipedia.org/wiki/Interface_segregation_principle) — المرجع الكلاسيكي لمبدأ فصل الواجهات.\n- [Android KTX Text extensions](https://developer.android.com/reference/kotlin/androidx/core/widget/package-summary) — التوثيق الرسمي لدوال KTX البديلة للـ TextWatcher.",
        "quick_answer_ar": "مبدأ فصل الواجهات (ISP) بينص على إن الكلاس أو العميل ميجبرش أبداً على الاعتماد على دوال في الإنترفيس هو مبيستخدمهاش. في أندرويد، المثال الكلاسيكي الفاضح هو `TextWatcher` القديم في جافا؛ لما كنت تحتاج تراقب النص بعد التعديل، كنت بتضطر تعمل كلاس وتكتب دالتين تانين فاضيين عشان الكومبايلر يوافق. بنطبق ISP بتقسيم الواجهات الكبيرة لإنترفيسات صغيرة ومحددة جداً (Role Interfaces)، زي فصل المستودع لـ `ProfileReader` و `ProfileWriter`.",
        "best_answer_ar": "مبدأ فصل الواجهات (Interface Segregation Principle) بيهدف لمنع ظهور ما نسميه في هندسة البرمجيات بالـ Fat Interfaces، وهي واجهات متضخمة بتحتوي على دوال كتيرة لخدمة أهداف مختلفة.\n\nلما الإنترفيس يكون كبير، أي كلاس بيحتاجه بيلاقي نفسه مجبر يكتب كود أو يعمل Override لدوال هو مش عايزها وملهاش أي علاقة بوظيفته. في أندرويد، كلنا عانينا من `TextWatcher`؛ عشان تراقب حقل إدخال في `afterTextChanged`، كان لازم تكتب `beforeTextChanged` و `onTextChanged` وتسيبهم بأجسام فاضية. جوجل حلت العيب ده في مكتبات KTX عبر Extension functions بتمرر Lambdas مباشرة زي `doAfterTextChanged`.\n\nفي تصميم المعمارية النظيفة، المبدأ ده جوهري جداً لتصميم طبقة البيانات. لو عملت إنترفيس اسمه `UserRepository` وحطيت فيه دوال جلب البروفايل، وتحديث الاسم، وحذف الحساب، ودفع الاشتراك؛ شاشة بسيطة زي Header الصفحة الرئيسية اللي عايزة تعرض اسم المستخدم بس هتكون معتمدة بالكامل على إنترفيس حساس فيه عمليات دفع وحذف!\n\nالتطبيق الصح لـ ISP هو فصل الإنترفيس لعقود صغيرة: `ProfileReader` للواجهات اللي بتقرأ بس، و `AccountManager` للعمليات الإدارية، و `BillingService` للمدفوعات. بكده كل شاشة بتعتمد فقط وبدقة على الدوال اللي بتستخدمها فعلياً.",
        "deep_answer_ar": "تحت الكابوت، مبدأ فصل الواجهات هو الركيزة الأساسية لتمكين ميزة تجنب إعادة البناء (Compilation Avoidance) في نظام Gradle عبر المشاريع متعددة الموديولات.\n\nلما موديول أ يعتمد على Fat Interface موجود في موديول ب، أي تغيير يعمله مطور تاني في توقيع أي دالة داخل الإنترفيس ده (حتى لو موديول أ مبيستخدمهاش إطلاقاً) بيغير الـ ABI العام للموديول، وده بيجبر Gradle إنه يلغي الكاش ويعيد عمل Compilation لموديول أ وكل الموديولات المعتمدة عليه. لما نطبق ISP ونقسم العقود لواجهات صغيرة (Single Abstract Method - SAM Interfaces)، الـ Gradle بيقدر يتخطى إعادة البناء بذكاء لأن الـ ABI الخاص بالواجهة المستهلكة لم يتغير، وده بيوفر ساعات طويلة من وقت الـ Build اليومي لفرق التطوير الكبيرة.\n\nعلاوة على كده، ISP بيقضي تماماً على صعوبة كتابة اختبارات الـ Unit Tests. لما الـ ViewModel يكون معتمد على إنترفيس فيه 20 دالة، كتابة Test Double أو Mock للكلاس ده بتكون كابوس من الإعدادات الفارغة. لكن مع واجهة صغيرة فيها دالة واحدة أو دالتين، تقدر تكتب Fake في الذاكرة في أقل من 5 سطور كود كوتلن نقي.\n\nوفي لغة Kotlin الحديثة، المبدأ مدعوم بشكل مدمج عبر استخدام الـ Functional Types مثل `(String) -> Unit`، وميزة تفويض الكلاسات `by`، اللي بتسمح للكلاس يجمع عدة واجهات مفصولة بسلاسة فائقة وبدون أي بويلربليت يدوي."
    }
}

# ==========================================
# SOL-06: Explain Dependency Inversion Principle with an Android example.
# ==========================================
DATA["SOL-06"] = {
    "concept_en": """The Dependency Inversion Principle (DIP) states that high-level modules should not depend on low-level modules; both must depend on abstractions. Furthermore, abstractions should not depend on details; details must depend on abstractions. In software architecture, source code dependencies traditionally point in the direction of execution flow (UI depends on Business Logic, which depends on Database and Network drivers). DIP completely inverts this dependency direction: business domain policies reside at the architectural center, defining abstract interfaces that external infrastructure layers (such as Room, Retrofit, or DataStore) must implement, isolating application business rules from third-party frameworks.""",
    "walkthrough_en": """Inverting source code dependencies in Android Clean Architecture:
```kotlin
// DOMAIN LAYER (:domain module - Pure Kotlin, Zero Android Framework dependencies)
// High-level business entity and abstraction
data class User(val id: String, val name: String)

interface UserRepository { // Domain defines the contract!
    suspend fun getUser(id: String): Result<User>
}

class GetUserUseCase @Inject constructor(
    private val repository: UserRepository // Depends on Domain abstraction!
) {
    suspend operator fun invoke(id: String): Result<User> = repository.getUser(id)
}

// DATA LAYER (:data module - Low-level details depend on Domain abstraction)
class UserRepositoryImpl @Inject constructor(
    private val localDao: UserDao, // Detail: Room
    private val remoteApi: UserApi // Detail: Retrofit
) : UserRepository { // Implements Domain contract, inverting source dependency!
    override suspend fun getUser(id: String): Result<User> = runCatching {
        localDao.getUser(id)?.toDomain() ?: remoteApi.fetchUser(id).toDomain()
    }
}
```""",
    "short_en": """The Dependency Inversion Principle dictates that high-level business modules should not depend on low-level infrastructure modules; both must depend on abstractions. In Android Clean Architecture, the Domain layer defines the abstract UserRepository interface, and the Data layer implements it using Room and Retrofit. This inverts source code dependencies inward toward pure Kotlin business rules, allowing developers to swap database or networking libraries without touching business or UI logic.""",
    "structured_en": """The Dependency Inversion Principle establishes architectural independence by decoupling business policies from volatile infrastructure details.
In traditional, un-inverted architectures, control flow and compile-time dependencies point in the same downward direction. A ViewModel instantiates a Repository, and the Repository directly constructs and invokes a Retrofit REST client and a Room SQLite DAO. Under this structure, high-level business rules are held hostage by low-level technology choices. If the backend switches from REST to gRPC or WebSockets, or if Room is upgraded, changes cascade upward into business and presentation layers.
Dependency Inversion resolves this by inserting an abstraction boundary.
The high-level Domain layer defines the data contract, such as the UserRepository interface. High-level UseCases depend strictly on this abstraction.
The low-level Data layer implements this interface in UserRepositoryImpl, mapping database tables and network responses into domain entities.
Source code dependencies now point in the exact opposite direction of execution flow. The Domain module remains pure Kotlin with zero external library dependencies, enabling lightning-fast unit tests and total freedom to evolve infrastructure without risking core business stability.""",
    "deep_senior_en": """Under the hood, Dependency Inversion is enforced at compilation time through multi-module Gradle dependency graphs and dependency injection bindings.
In an enterprise multi-module Android application, Gradle project dependencies strictly enforce DIP: the :feature and :data modules depend on the :domain module (implementation(project(":domain"))), but the :domain module has zero dependencies on :data, :feature, or Android SDK libraries. If an engineer attempts to import android.content.Context, androidx.room.Room, or retrofit2.Retrofit inside the :domain module, the Gradle compiler halts with a compilation error, preserving the pure domain boundary automatically.
At runtime, Dependency Injection frameworks like Dagger or Hilt wire the concrete implementations back together at the application assembly root. Using @Binds inside a Hilt module, Dagger binds the Data layer's UserRepositoryImpl to the Domain layer's UserRepository interface seamlessly.
This inversion enables total testability through JVM test doubles. In unit tests for ViewModels or UseCases, developers pass a lightweight fake repository implemented in memory.
Tests execute entirely within standard JVM bytecode at thousands of tests per second, completely eliminating the need for slow Android instrumentation runners, Robolectric reflection overhead, or mock SQLite databases, accelerating continuous integration pipelines significantly. This decoupling allows engineers to substitute storage engines or upgrade network protocols without risking any disruption to domain business logic or presentation state machines.""",
    "meta_ar": {
        "id": "SOL-06",
        "questionAr": "اشرح مبدأ قلب الاعتماديات (Dependency Inversion Principle) مع ذكر مثال واقعي من أندرويد.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ قلب الاعتماديات (DIP)، والقدرة على التمييز بين اتجاه سريان التنفيذ واتجاه التبعيات البرمجية، وتطبيق المبدأ عملياً عبر عزل موديول الـ Domain عن موديول الـ Data في Clean Architecture.",
        "why_it_matters_ar": "بدون قلب الاعتماديات، يصبح منطق العمل رهينة لمكتبات الشبكة وقواعد البيانات، وأي تحديث أو تغيير في Retrofit أو Room يجبر الفريق على إعادة كتابة واختبار منطق العمل والشاشات بالكامل.",
        "worked_example_ar": "تطبيق DIP في موديولات أندرويد النظيفة:\n```kotlin\n// Domain: يملك العقد المجرد بدون أي مكتبات\ninterface UserRepo { suspend fun getUser(): User }\n// Data: تفاصيل التنفيذ تعتمد على عقد الدومين وتنفذه\nclass UserRepoImpl(val api: Api, val db: Db) : UserRepo { ... }\n```",
        "trade_offs_ar": "يتطلب إنشاء موديولات ونماذج تحويل (Mappers) إضافية، لكنه يمنح استقلالية تامة تتيح تبديل البنية التحتية بالكامل بدون لمس حرف واحد في منطق العمل.",
        "failure_modes_ar": "جعل طبقة الـ Domain تعتمد على موديول الـ Data، أو استيراد كلاسات Room و Retrofit داخل الـ UseCases.",
        "production_perspective_ar": "في الشركات الكبرى، يُمنع موديول `:domain` من استيراد أي مكتبة أندرويد في Gradle، ويتم ربط واجهات الـ Repository بالتنفيذات عبر `@Binds` في Hilt عند تجميع التطبيق.",
        "how_to_answer_ar": "عرف المبدأ: الطبقات العليا لا تعتمد على الطبقات الدنيا وكلاهما يعتمد على تجريد، واشرح كيف ينعكس اتجاه التبعيات في Clean Architecture حيث يملك الـ Domain واجهة الـ Repository والـ Data هو الذي ينفذها، ووضح أثر ذلك على الاختبارات بدون أندرويد.",
        "talking_points_ar": "مفهوم Inverting dependency direction، واستقلالية الـ Domain في Gradle، ودور Dagger `@Binds`، وسرعة تشغيل آلاف الـ Unit Tests على الـ JVM.",
        "follow_ups_ar": "- **المحاور:** \"كيف يفرض Gradle مبدأ DIP في المشاريع المقسمة لموديولات؟\"\n  **المرشح:** \"بنجعل موديول `:data` هو اللي يعمل `implementation(project(\":domain\"))`، وموديول `:domain` مبيعرفش أي حاجة عن الداتا، فالكومبايلر نفسه بيمنع أي كسر للمبدأ.\"\n\n- **المحاور:** \"هل الـ DIP يعني بالضرورة استخدام مكتبة Dagger أو Hilt؟\"\n  **المرشح:** \"لا، DIP هو مبدأ معماري لتنظيم الكود والاعتماديات، بينما Dagger هو أداة أتمتة لحقن تلك الاعتماديات؛ تقدر تطبق DIP يدوياً بمجرد تمرير الـ Interface في الكونستركتور.\"",
        "self_check_ar": "هل عرفت شقي المبدأ بدقة؟ هل شرحت اتجاه التبعيات في موديولات Gradle؟ وهل بينت كيف يعزل الـ Domain عن أندرويد؟",
        "references_ar": f"- [The Dependency Inversion Principle by Robert C. Martin](https://en.wikipedia.org/wiki/Dependency_inversion_principle) — المرجع الأصلي لمبدأ قلب الاعتماديات.\n- [Android Architecture: Domain Layer](https://developer.android.com/topic/architecture/domain-layer) — الدليل الرسمي لجوجل حول طبقة الدومين واستقلاليتها.",
        "quick_answer_ar": "مبدأ قلب الاعتماديات (DIP) بينص على إن الوحدات البرمجية العليا (منطق العمل) لازم متعتمدش على الوحدات الدنيا (تفاصيل التخزين والشبكة)، بل الاتنين يعتمدوا على تجريدات (Interfaces). في معمارية أندرويد النظيفة، طبقة الـ Domain بتعرف إنترفيس `UserRepository` كعقد نقي، وطبقة الـ Data هي اللي بتنفذه باستخدام Room و Retrofit. بكده بنقلب اتجاه الاعتماديات للداخل نحو كود كوتلن النقي، وبنقدر نبدل مكتبات الداتابيز أو السيرفر بدون ما نلمس منطق التطبيق إطلاقاً.",
        "best_answer_ar": "مبدأ قلب الاعتماديات (Dependency Inversion Principle) هو الأساس اللي اتبنت عليه كل معماريات البرمجيات الحديثة زي Clean Architecture و Hexagonal Architecture.\n\nفي التصميم القديم بدون قلب الاعتماديات، اتجاه التبعيات في الكود كان بيمشي في نفس اتجاه تشغيل البرنامج: الشاشة بتنادي الـ ViewModel، والـ ViewModel بينادي الـ Repository، والـ Repository بينادي Retrofit و Room مباشرة. الكود ده كان بيخلي منطق العمل الحساس رهينة لمكتبات أندرويد الخارجية، ولو حبيت تغير مكتبة السيرفر من REST لـ GraphQL كنت بتضطر تعدل في كل طبقات التطبيق.\n\nمبدأ DIP بيقلب اتجاه السهم ده 180 درجة.\nبدل ما منطق العمل يعتمد على الداتابيز، إحنا بنحط طبقة الـ Domain في المركز، وبنخليها هي اللي تملك وتحدد شروط الواجهات (Interfaces). فالـ Domain بيعرف إنترفيس `UserRepository` بلغة كوتلن النقية وبدون أي استيراد لمكتبات خارجية.\nوطبقة الـ Data تحت هي اللي بتعتمد على الـ Domain وتنفذ الإنترفيس ده باستخدام Room أو Retrofit.\n\nبكده اتجاه تبعيات كود المصدر اتقلب للداخل؛ منطق العمل بقى مستقلاً وحراً تماماً، وتقدر تختبره بـ Unit Tests سريعة على الـ JVM، وتقدر تستبدل مكتبات التخزين بضغطة زر وبدون أي خوف من كسر قواعد العمل.",
        "deep_answer_ar": "تحت الكابوت، مبدأ قلب الاعتماديات بيتحول لضمانة هندسية صارمة مفروضة بقوة ملفات الـ Gradle في المشاريع المقسمة لموديولات متعددة (Multi-module Architecture).\n\nفي إعدادات Gradle الاحترافية، موديول `:data` وموديول `:feature` هما اللي بيعملوا `implementation(project(\":domain\"))`، بينما موديول `:domain` مبيحتويش على أي تبعية لموديول الداتا أو حتى لحزم نظام أندرويد `androidx.*`. فلو أي مهندس في الفريق حاول بالخطأ يستورد كلاس من Room أو Retrofit أو Context جوه الـ Domain، كومبايلر كوتلن هيرفض يكمل الـ Build وهيطلع خطأ فوري، وده بيحمي حدود المعمارية برمجياً وآلياً.\n\nوعند تشغيل التطبيق، مكتبات الحقن زي Dagger و Hilt هي اللي بتوصل الأسلاك ببعضها في الموديول الرئيسي (`:app`)؛ عن طريق `@Binds` داخل الـ Module، داجر بيعرف إن لما أي UseCase يطلب `UserRepository`، يمرر له نسخة من `UserRepositoryImpl` اللي عايشة في موديول الداتا.\n\nالأثر الأعظم للتصميم ده بيظهر في الاختبارات المؤتمتة؛ لأن الـ ViewModels والـ UseCases معتمدة على الـ Interface النقي، بنقدر نمرر In-memory Fake Repository خفيف جداً، ونشغل آلاف الـ Unit Tests على الـ JVM العادي في ثانيتين وبدون الحاجة لفتح محاكي أندرويد بطيء أو تشغيل بيئة Robolectric المعقدة، وده بيضاعف سرعة دورة التطوير ويضمن استقرار التطبيق قبل نزول أي إصدار للإنتاج."
    }
}

# ==========================================
# SOL-07: Compare DIP and Dependency Injection (DI).
# ==========================================
DATA["SOL-07"] = {
    "concept_en": """The Dependency Inversion Principle (DIP) and Dependency Injection (DI) represent distinct software engineering concepts operating at different levels of abstraction. DIP is a high-level architectural principle belonging to the SOLID suite, dictating that high-level modules must depend on abstractions rather than concrete low-level details. In contrast, Dependency Injection is a concrete creational and structural design pattern (implementing Inversion of Control) that supplies an object's collaborators externally, typically via constructor parameters. While DI is the most common tactical mechanism used to fulfill DIP, an engineer can employ DI without adhering to DIP by injecting concrete classes directly, missing the architectural benefits of decoupled abstractions.""",
    "walkthrough_en": """Contrasting DI without DIP against DI with DIP:
```kotlin
// SCENARIO 1: Dependency Injection WITHOUT Dependency Inversion (Tightly coupled to concrete Room DAO!)
class BadUserViewModel @Inject constructor(
    private val userDao: UserDaoImpl // DI used (constructor injection), but DIP VIOLATED (concrete class!)
) : ViewModel() {
    // Cannot mock or fake on JVM without concrete Room dependencies!
}

// SCENARIO 2: Dependency Injection WITH Dependency Inversion (Decoupled architectural bliss)
// 1. High-level Domain Abstraction (Fulfills DIP)
interface UserRepository {
    suspend fun getUserProfile(): Result<UserProfile>
}

// 2. Concrete Data Implementation
class UserRepositoryImpl @Inject constructor(private val localDao: UserDao) : UserRepository {
    override suspend fun getUserProfile() = runCatching { localDao.getUser().toDomain() }
}

// 3. Presentation Consumer (Fulfills BOTH DIP and DI)
class CleanUserViewModel @Inject constructor(
    private val repository: UserRepository // DI delivers the dependency; DIP guarantees it's an abstraction!
) : ViewModel() {
    // 100% testable on standard JVM using lightweight fakes
}
```""",
    "short_en": """DIP is an architectural principle stating that high-level policies must depend on abstractions rather than concrete details. Dependency Injection is a creational pattern that passes dependencies into an object from the outside, typically through its constructor. You can use DI without DIP by injecting concrete classes directly. True architectural decoupling occurs when DI is used to inject abstract interfaces that satisfy DIP.""",
    "structured_en": """Understanding the relationship between the Dependency Inversion Principle and Dependency Injection requires distinguishing architectural rules from implementation mechanics.
The Dependency Inversion Principle (DIP) is an architectural mandate. It dictates the direction of source code dependencies across module boundaries, asserting that high-level domain rules must remain pure and depend exclusively on abstract contracts, while low-level infrastructure details implement those contracts.
Dependency Injection (DI) is a tactical creational pattern that implements Inversion of Control. Instead of an object constructing its own dependencies using new or static lookups, an external assembler supplies those dependencies, typically via constructor injection.
The two concepts are frequently conflated because DI is the primary tool used to implement DIP. However, using DI does not guarantee DIP compliance. If a ViewModel uses Hilt constructor injection to inject a concrete RoomUserDaoImpl, Dependency Injection is actively practiced, but Dependency Inversion is completely violated. The ViewModel remains tightly coupled to an SQLite implementation detail.
Optimal architecture combines both: DIP establishes the abstract interface boundaries, and DI wires the concrete instances behind those boundaries seamlessly.""",
    "deep_senior_en": """Under the hood, conflating DIP with DI leads to architectural decay in enterprise multi-module Android codebases.
When developers rely on Dagger or Hilt without understanding DIP, they inject concrete implementations across Gradle module boundaries. For example, if a :feature:profile module directly injects an OkHttpNetworkService from :core:network, the feature module's Gradle script must declare an implementation dependency on the network module. This couples UI feature compilation directly to network serialization libraries and third-party HTTP drivers, inflating incremental build times and eliminating parallel compilation across build agents.
When DIP is correctly applied, the :feature module declares an abstract contract in its domain interface, and the DI container binds the implementation at the root :app assembly layer using Dagger's @Binds. The feature module never compiles against the network module, preserving strict physical decoupling.
Furthermore, this distinction impacts testing architectures. Injecting concrete classes with DI still forces unit tests to utilize heavy mocking frameworks like Mockk or bytecode manipulation agents to override final methods on Android classes.
When DI supplies abstractions complying with DIP, unit tests pass simple, zero-reflection Kotlin fake implementations into constructors, executing at maximum JVM speed without memory overhead or runtime proxy generation, keeping developer feedback loops practically instantaneous. Ultimately, DIP provides the architectural decoupling, while DI provides the operational mechanism to instantiate and wire dependencies cleanly.""",
    "meta_ar": {
        "id": "SOL-07",
        "questionAr": "قارن بين مبدأ قلب الاعتماديات (DIP) ونمط حقن التبعيات (DI).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على التمييز الدقيق بين المبدأ المعماري التجريدي (DIP) والنمط التنفيذي التكتيكي (DI)، وتوضيح كيف يمكن استخدام الحقن بدون تحقيق قلب الاعتماديات، وأثر ذلك على الموديولات والاختبارات.",
        "why_it_matters_ar": "الخلط بين المفهومين يجعل المطور يعتقد أن مجرد استخدام Hilt أو `@Inject` يعني أن كوده نظيف ومفصول، بينما هو في الحقيقة يحقن كلاسات ملموسة تكسر العزل المعماري بالكامل.",
        "worked_example_ar": "مقارنة الحقن المباشر بالحقن عبر الواجهات:\n```kotlin\n// DI بدون DIP: حقن كلاس ملموس (ارتباط وثيق)\nclass VM @Inject constructor(val db: RoomDbImpl)\n// DI مع DIP: حقن Interface مجرد (عزل معماري تام)\nclass VM @Inject constructor(val repo: UserRepo)\n```",
        "trade_offs_ar": "استخدام DI بمفرده أسهل ولا يتطلب كتابة واجهات، لكن الجمع بين DI و DIP هو الوحيد الذي يمنح فك ارتباط حقيقي وسرعة بناء واختبارات JVM نقية.",
        "failure_modes_ar": "حقن كلاسات Room DAOs أو مكتبات Retrofit مباشرة في الـ ViewModels عبر Hilt والاعتقاد بأن الكود يطبق مبادئ SOLID.",
        "production_perspective_ar": "في المشروعات الكبيرة، نستخدم Hilt كأداة DI لحقن الواجهات المعرفة في موديول الـ Domain حصرياً، ونمنع حقن أي كلاس ملموس عبر حدود الموديولات.",
        "how_to_answer_ar": "وضح الفارق الجوهري: DIP هو مبدأ معماري استراتيجي (High-level Principle) يفرض الاعتماد على الواجهات، بينما DI هو نمط تكتيكي وآلية تنفيذ (Design Pattern) لتمرير الكائنات من الخارج، واضرب مثال حقن كلاس ملموس لتوضيح كيف يمكن استخدام DI بدون DIP.",
        "talking_points_ar": "الفرق بين المبدأ المعماري والنمط التكتيكي، ومثال DI بدون DIP، ودور Dagger `@Binds` في تحقيق التوافق، وأثر ذلك على حدود موديولات Gradle.",
        "follow_ups_ar": "- **المحاور:** \"هل أقدر أطبق DIP بدون ما أستخدم مكتبة DI زي Hilt أو Dagger؟\"\n  **المرشح:** \"نعم بالتأكيد، تقدر تطبق DIP يدوياً (Manual DI) بمجرد إنك تعتمد على Interfaces وتمرر الكائنات بنفسك في الكونستركتور؛ المكتبات هي مجرد أدوات لتوليد كود الربط آلياً.\"\n\n- **المحاور:** \"ما هو أكبر ضرر لحقن كلاس ملموس في موديول Feature؟\"\n  **المرشح:** \"إنه بيجبر موديول الـ Feature يعتمد على موديول الـ Data في Gradle، وده بيكسر العزل، ويبطئ الـ Build، ويمنع كتابة اختبارات JVM خفيفة بالـ Fakes.\"",
        "self_check_ar": "هل وضحت الفارق بين المبدأ والنمط؟ هل شرحت مثال استخدام DI بدون DIP؟ وهل بينت أثر ذلك على الاختبارات وموديولات Gradle؟",
        "references_ar": f"- [Inversion of Control by Martin Fowler](https://martinfowler.com/articles/injection.html) — المقال المرجعي لمارتن فاولر حول الفرق بين IoC و DI.\n- [Dependency Injection in Android](https://developer.android.com/training/dependency-injection) — التوثيق الرسمي لجوجل لحقن التبعيات.",
        "quick_answer_ar": "مبدأ قلب الاعتماديات (DIP) هو مبدأ معماري استراتيجي بينص على إن الكود لازم يعتمد على تجريدات (Interfaces) مش كلاسات ملموسة. أما حقن التبعيات (DI) فهو نمط تصميمي وتكتيك عملي لتمرير الكائنات للكلاس من الخارج في الكونستركتور بدل ما يبنيها بنفسه. تقدر تستخدم DI بدون DIP لو حقنت كلاس ملموس زي `RoomDatabase` مباشرة؛ لكن قمة النضج المعماري بتتحقق لما تستخدم أداة الـ DI لحقن الواجهات اللي بتحقق الـ DIP.",
        "best_answer_ar": "كتير من المطورين بيخلطوا بين DIP و DI وبيعتبروهم حاجة واحدة، لكن في الحقيقة هما بيشتغلوا على مستويين مختلفين تماماً في هندسة البرمجيات.\n\nالـ Dependency Inversion Principle (DIP) هو مبدأ معماري عالي المستوى من مبادئ SOLID. هو اللي بيحدد قواعد اللعبة: بيفرض إن الطبقات العليا متعتمدش على تفاصيل التخزين والشبكة، وإن الاتنين يعتمدوا على واجهات مجردة (Interfaces) في طبقة الدومين.\n\nأما الـ Dependency Injection (DI) فهو مجرد نمط تصميمي وآلية تكتيكية لتطبيق مبدأ Inversion of Control. وظيفته إنه ينقل عملية إنشاء الكائن خارج الكلاس، ويمرر له الكائنات الجاهزة عبر الكونستركتور (Constructor Injection).\n\nالفارق الجوهري بيبان في المثال ده: لو عندك ViewModel بيستقبل في الكونستركتور بتاعه كلاس ملموس زي `RoomUserDaoImpl` باستخدام `@Inject` في Hilt؛ هنا أنت بتطبق نمط الـ DI بنجاح، لكنك بتنتهك مبدأ الـ DIP بنسبة 100%! لأن الشاشة لسه مربوطة ومقيدة بتفاصيل قاعدة بيانات Room ومتقدرش تختبرها بدون مكتبات أندرويد.\n\nالتصميم المحترف بيجمع بين الاتنين: بنستخدم DIP عشان نعرف Interface نظيف في الدومين، وبنستخدم DI عبر مكتبات زي Hilt عشان نحقن الكائن اللي بينفذ الـ Interface ده تلقائياً في الشاشات.",
        "deep_answer_ar": "تحت الكابوت، الخلط بين DIP و DI هو السبب الرئيسي لانهيار حدود الموديولات وتضخم وقت البناء في مشاريع أندرويد الضخمة.\n\nلما المطورين بيعتمدوا على Hilt بحفظ أعمى بدون فهم الـ DIP، بيقوموا بحقن كلاسات ملموسة بين موديولات الـ Gradle. تلاقي موديول الواجهة `:feature:profile` بيحقن كلاس من موديول الشبكة `:core:network`. ده بيجبر Gradle إنه يربط الموديولين ببعض، ويحرم المشروع من ميزة البناء المتوازي (Parallel Compilation)، ويجعل أي تعديل في مكتبة الـ HTTP يجبر الكومبايلر يعيد بناء شاشات المستخدم كلها.\n\nالتطبيق الصح لمبدأ DIP بيخلي موديول الـ Feature يعلن عن Interface نظيف للخدمة اللي محتاجها، وموديول الـ App الرئيسي هو اللي بيستخدم الـ DI برابط `@Binds` لتوصيل التنفيذ الملموس. بكده موديول الشاشة عمره ما بيشوف موديول الشبكة في الـ Compile time إطلاقاً.\n\nعلاوة على كده، الجمع بين DIP و DI بيغير خريطة الاختبارات في المشروع؛ لو حقنت كلاس ملموس، هتضطر تستخدم مكتبات Mocking ثقيلة زي Mockk وتعمل Mocking لـ Bytecode نهائي في الـ JVM. بينما لما تحقن Interface بيحقق DIP، بتقدر في التيست تمرر Fake Class بسيط مكتوب في 5 سطور، بيشتغل بدون أي Reflection، وبسرعة مذهلة بتسمح بتشغيل مئات التستات في ثوانٍ معدودة."
    }
}

# ==========================================
# SOL-08: Compare SRP and ISP.
# ==========================================
DATA["SOL-08"] = {
    "concept_en": """The Single Responsibility Principle (SRP) and the Interface Segregation Principle (ISP) are complementary SOLID principles addressing cohesion and coupling at different structural granularities. SRP governs implementation cohesion at the class, module, and actor level, mandating that a component must have only one reason to change. ISP governs contract coupling at the interface and consumer level, asserting that no client should be forced to depend on methods it does not invoke. A class can completely satisfy SRP by maintaining a single, highly cohesive responsibility (such as user account management) while simultaneously violating ISP if it exposes a fat, monolithic interface combining administrative, billing, and profile methods to disparate callers.""",
    "walkthrough_en": """Demonstrating a class satisfying SRP while violating ISP, and its refactoring:
```kotlin
// A class that has a single business responsibility (satisfies SRP: User Account Management)
// But its single interface violates ISP because distinct clients need only a fraction of its methods!
interface MonolithicAccountContract { // VIOLATES ISP: Combines disparate client needs
    fun getDisplayName(): String
    fun getAvatarUrl(): String
    fun changePassword(oldPass: String, newPass: String)
    fun processSubscriptionRenewal()
}

// REFACTORED TO SATISFY BOTH SRP AND ISP:
// Segregated Client-Specific Interfaces (ISP Satisfied)
interface UserProfileHeaderViewContract {
    fun getDisplayName(): String
    fun getAvatarUrl(): String
}

interface AccountSecurityContract {
    fun changePassword(oldPass: String, newPass: String)
}

interface SubscriptionBillingContract {
    fun processSubscriptionRenewal()
}

// Cohesive implementation satisfies SRP and multiple role-specific ISP interfaces
class UserAccountService @Inject constructor(
    private val api: AccountApi
) : UserProfileHeaderViewContract, AccountSecurityContract, SubscriptionBillingContract {
    // Single cohesive responsibility: manages account logic, but exposes fine-grained seams to callers!
    override fun getDisplayName() = "Alice"
    override fun getAvatarUrl() = "https://cdn.io/avatar.png"
    override fun changePassword(oldPass: String, newPass: String) { /* ... */ }
    override fun processSubscriptionRenewal() { /* ... */ }
}
```""",
    "short_en": """SRP focuses on classes and actors, dictating that a class should have only one reason to change. ISP focuses on interfaces and clients, dictating that a client should not depend on methods it does not use. A class can satisfy SRP by having a single cohesive responsibility, yet violate ISP if its interface forces callers to depend on unused methods. SRP promotes high internal cohesion, while ISP minimizes external caller coupling.""",
    "structured_en": """Comparing SRP and ISP clarifies how cohesion and coupling operate together across class implementations and interface contracts.
The Single Responsibility Principle evaluates an entity from the inside out and from the perspective of the actors who request changes. It asks: does this class do only one job, and does it serve a single stakeholder? If a class handles validation, networking, and UI rendering, it violates SRP because changes in business rules, backend APIs, or visual designs all force modifications to that single file.
The Interface Segregation Principle evaluates an entity from the outside in and from the perspective of the clients who consume it. It asks: does this caller need every method exposed by this interface? If an interface combines read operations, write operations, and administrative functions, a caller that only reads data is forced to depend on the full contract, violating ISP.
The key insight is that a class can perfectly satisfy SRP while violating ISP. A UserManager class might focus purely on user account domain mechanics, satisfying SRP. However, if it exposes a single 15-method interface to both a lightweight UI header widget and a security settings screen, it violates ISP.
Applying ISP splits the contract into role interfaces, ensuring clients remain decoupled while the underlying implementation maintains its single responsibility.""",
    "deep_senior_en": """Under the hood, SRP and ISP operate at different phases of software development, compilation, and automated verification.
SRP directly impacts codebase maintainability, change velocity, and merge conflict frequency. When classes violate SRP, multiple developers working on different features constantly edit the same source file, leading to high friction in Git branch workflows.
ISP, on the other hand, directly impacts compilation avoidance in Gradle, binary compatibility across SDK boundaries, and mocking overhead in test harnesses.
When a client module depends on a fat interface violating ISP, any addition or modification to an unused method signature changes the interface's public ABI. The Gradle build cache is invalidated, and the client module must be recompiled despite having zero functional interest in the change.
Furthermore, in unit testing, ISP violations lead to fragile test doubles. If a ViewModel depends on a fat 20-method repository interface, tests must supply mock configurations or throwaway stubs for methods that the ViewModel never executes.
When ISP is enforced, testing seams become razor-thin. A test passes a clean fake satisfying a 2-method SAM interface, keeping test setup code concise, deterministic, and resilient against unrelated interface churn across the enterprise codebase, ensuring smooth and rapid continuous delivery. This isolation ensures that client modules remain unaffected when other consumers request contract extensions.""",
    "meta_ar": {
        "id": "SOL-08",
        "questionAr": "قارن بين مبدأ المسؤولية الواحدة (SRP) ومبدأ فصل الواجهات (ISP).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على التمييز الدقيق بين التماسك الداخلي للكلاس (SRP) والارتباط الخارجي للواجهة (ISP)، وفهم كيف يمكن لكلاس أن يلتزم بـ SRP ولكنه ينتهك ISP، وإدراك الأثر المعماري لكل منهما.",
        "why_it_matters_ar": "الخلط بينهما يجعل المطور يعتقد أن الكلاس إذا كان صغيراً ومحدداً فهذا كافٍ، دون أن يدرك أن واجهته قد تفرض دوالاً زائدة على شاشات أخرى وتكسر العزل المعماري.",
        "worked_example_ar": "كلاس يلتزم بـ SRP وينتهك ISP وتصحيحه:\n```kotlin\n// كلاس ممتاز يلتزم بـ SRP (مسؤول عن الحساب فقط)\n// لكن واجهته تكسر ISP لأنها تجمع الاسم مع كلمة السر والاشتراك\n// التصحيح: تقسيم الواجهة لعقود دورية (Role interfaces)\ninterface NameContract { fun getName(): String }\ninterface PassContract { fun changePass() }\nclass AccountService : NameContract, PassContract { ... }\n```",
        "trade_offs_ar": "الجمع بينهما يتطلب تصميماً دقيقاً لواجهات متعددة وكلاسات متماسكة، لكنه يمنح أعلى درجات المرونة وسرعة البناء واستقرار الاختبارات.",
        "failure_modes_ar": "إجبار شاشة بسيطة على اعتماد إنترفيس حساب كامل يحتوي على دوال مالية وأمنية معقدة لا تحتاجها.",
        "production_perspective_ar": "في المشروعات الكبيرة، نطبق SRP لتحديد مسؤولية الكلاس وموديوله، ونطبق ISP لتعريف واجهات دقيقة لكل شاشة (Consumer-driven Contracts).",
        "how_to_answer_ar": "وضح المقارنة بوضوح: SRP يركز على الكلاس والجهة المسؤولة عن تغييره (من الداخل للخارج)، بينما ISP يركز على الإنترفيس والعملاء المستهلكين له (من الخارج للداخل)، واشرح كيف يمكن لكلاس أن يلتزم بـ SRP وينتهك ISP، وبسط أثر ذلك على الاختبارات والـ Build.",
        "talking_points_ar": "التماسك الداخلي للكلاس (Cohesion) مقابل فك الارتباط الخارجي (Coupling)، ومنظور الكلاس مقابل منظور العميل، وكيفية التوافق بين المبدأين، وأثر ISP على كاش Gradle.",
        "follow_ups_ar": "- **المحاور:** \"هل تقسيم الإنترفيسات بيتعارض مع وجود كلاس واحد ينفذهم؟\"\n  **المرشح:** \"إطلاقاً، كلاس واحد يقدر يطبق عدة Interfaces مفصولة، وده قمة التوافق؛ الكلاس محتفظ بمسؤوليته المتماسكة (SRP) وفي نفس الوقت بيعرض لكل عميل الواجهة اللي محتاجها بس (ISP).\"\n\n- **المحاور:** \"إيهما أكثر تأثيراً على سرعة الـ Compilation في Gradle: SRP أم ISP؟\"\n  **المرشح:** \"الـ ISP له تأثير مباشر على ميزة Compilation Avoidance؛ لأن تغيير دالة في إنترفيس غير مستخدم بيجبر Gradle يعيد بناء كل الموديولات اللي شايلاه، فتقسيمه بيوفر وقت بناء هائل.\"",
        "self_check_ar": "هل وضحت الفارق بين منظور الكلاس ومنظور العميل؟ هل بينت حالة كلاس يلتزم بـ SRP وينتهك ISP؟ وهل ذكرت الفائدة في الاختبارات وسرعة الـ Build؟",
        "references_ar": f"- [SRP vs ISP in Clean Architecture](https://blog.cleancoder.com/) — مقالات العم بوب التوضيحية حول حدود المبادئ.\n- [Gradle Compilation Avoidance](https://docs.gradle.org/current/userguide/java_plugin.html#sec:java_compile_avoidance) — توثيق جريدل الرسمي لتجنب إعادة البناء.",
        "quick_answer_ar": "الفرق الجوهري إن مبدأ المسؤولية الواحدة (SRP) بيركز على الكلاس من جوه ومين الجهة المسؤولة عن تغييره (One reason to change)، بينما مبدأ فصل الواجهات (ISP) بيركز على الإنترفيس من بره ومنظور العميل اللي بيستخدمه (Clients shouldn't depend on unused methods). ممكن كلاس يلتزم بـ SRP تماماً ويكون مسؤول عن وظيفة واحدة زي إدارة الحساب، لكن الإنترفيس بتاعه يكسر ISP لأنه بيجبر شاشة بسيطة تعتمد على دوال أمنية ومالية مش محتاجاها.",
        "best_answer_ar": "المقارنة بين SRP و ISP بتوضح إزاي التماسك الداخلي وفك الارتباط الخارجي بيكملوا بعض في المعمارية النظيفة.\n\nمبدأ المسؤولية الواحدة (SRP) بيبص للكلاس من الداخل للخارج؛ بيسأل: هل الكلاس ده بيخدم هدفاً واحداً ومسؤولاً قدام جهة عمل واحدة (Actor)؟ لو الكلاس بيعمل شغل الداتابيز والرسم والشبكة مع بعض، يبقى بيكسر SRP لأن عنده أسباب كتير للتعديل.\n\nأما مبدأ فصل الواجهات (ISP) فبيبص للإنترفيس من الخارج للداخل؛ بيسأل: هل العميل اللي بينادي الإنترفيس ده محتاج كل الدوال المعروضة عليه؟ لو الإنترفيس بيعرض 10 دوال والشاشة محتاجة دالة واحدة بس، يبقى الإنترفيس ده بيكسر ISP لأنه بيكبل العميل بدوال ملهاش لازمة بالنسبة له.\n\nالنقطة الذهبية اللي بيسأل عنها المحاورون الكبار هي: هل ينفع كلاس يلتزم بـ SRP وينتهك ISP في نفس الوقت؟\nالإجابة: نعم جداً! تخيل كلاس اسمه `UserAccountService`؛ الكلاس ده مركز بنسبة 100% في منطق حساب المستخدم، فمحقق SRP تماماً. لكن لو عملنا له إنترفيس واحد عملاق فيه دوال جلب الصورة الشخصية، ودوال تغيير كلمة السر، ودوال تجديد الاشتراك البنكي؛ لما يجي ودجت صغير في أعلى الشاشة عايز يعرض صورة المستخدم بس، هيلاقي نفسه مجبر يعتمد على الإنترفيس الضخم ده بالكامل، وده انتهاك صريح لـ ISP.\n\nالحل إننا نحافظ على الكلاس بمسؤوليته، لكن نقسم عقوده لواجهات صغيرة: `AvatarProvider` للودجت، و `SecurityManager` لشاشة الإعدادات.",
        "deep_answer_ar": "تحت الكابوت، مبدأ SRP بيعالج مشاكل الصيانة وسرعة التطوير اليومية، بينما مبدأ ISP بيعالج مشاكل الـ Binary Compatibility، وكاش الـ Gradle، وثبات الاختبارات المؤتمتة.\n\nانتهاك SRP بيخلق صراعات دمج مستمرة (Merge Conflicts) في Git لأن عدة مطورين بيعدلوا في نفس الملف الكبير لخدمة متطلبات مختلفة. أما انتهاك ISP فبيدمر ميزة الـ Compilation Avoidance في Gradle؛ فلو موديول الواجهة معتمد على Fat Interface، أي تغيير في توقيع دالة فرعية مش مستخدمة هيغير الـ ABI بتاع الموديول المصدر، وهيجبر Gradle إنه يعيد بناء موديول الواجهة وكل الشاشات اللي وراه بدون أي داعٍ.\n\nوفوق كده، انتهاك ISP هو الكابوس الأكبر في كتابة Unit Tests سريعة ومستقرة. لما تيجي تختبر ViewModel بيعتمد على إنترفيس فيه 15 دالة، بتلاقي نفسك بتضيع وقت طويل في عمل Mocking و Stubbing لدوال الـ ViewModel مش هيناديها أصلاً في مسار الاختبار، وأي تعديل مستقبلي في الإنترفيس هيكسر ملف التيست حتى لو منطق الشاشة سليم.\n\nتطبيق ISP بيخليك تصمم الواجهات كعقود يحددها العميل (Consumer-Driven Contracts) وغالباً بتكون واجهات SAM بـ دالة واحدة فقط. ده بيخلي كتابة الـ Fakes على الـ JVM سهلة جداً، وبيخلي كل اختبار معزولاً ومركّزاً على ما يخصه فقط، مما يحافظ على سرعة تنفيذ خطوط الـ CI/CD واستقرارها."
    }
}

# ==========================================
# SOL-09: What is composition over inheritance?
# ==========================================
DATA["SOL-09"] = {
    "concept_en": """Composition over inheritance is a foundational object-oriented design principle asserting that systems should achieve code reuse, polymorphism, and behavioral extension by assembling independent components through 'has-a' reference relationships rather than constructing rigid class hierarchies through 'is-a' inheritance trees. In Android engineering, excessive inheritance results in the notorious Fragile Base Class problem, monolithic BaseActivity and BaseFragment anti-patterns, inflexible compile-time coupling, and namespace pollution. Favoring composition enables dynamic runtime behavioral swapping, clean lifecycle observers, pure JVM testability, and forms the core foundational paradigm of modern Jetpack Compose.""",
    "walkthrough_en": """Refactoring a bloated BaseActivity inheritance tree into decoupled composition:
```kotlin
// BAD ANTI-PATTERN: Bloated BaseActivity (Fragile base class, tight coupling, hard to test)
open class BaseActivity : AppCompatActivity() {
    fun trackAnalytics(event: String) { /* Concrete mixpanel logic */ }
    fun showLoadingDialog() { /* Dialog logic */ }
    fun checkLocationPermission() { /* Activity permission requests */ }
    // Every child activity inherits all 50 methods whether it needs them or not!
}
class CheckoutActivity : BaseActivity() { /* Inherits massive baggage */ }

// ARCHITECTURAL BEST PRACTICE: Composition via dedicated delegates & lifecycle observers
class AnalyticsTracker @Inject constructor() {
    fun trackScreen(screenName: String) { /* Clean isolated analytics */ }
}

class LocationPermissionDelegate(private val activity: ComponentActivity) {
    // Encapsulates permission contracts independently
    fun requestLocation(onGranted: () -> Unit) { /* ... */ }
}

// Clean Activity: Composes only the capabilities it actually requires
@AndroidEntryPoint
class CleanCheckoutActivity : AppCompatActivity() {
    @Inject lateinit var analytics: AnalyticsTracker
    private val locationDelegate by lazy { LocationPermissionDelegate(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        analytics.trackScreen("Checkout")
    }
}
```""",
    "short_en": """Composition over inheritance favors assembling components using 'has-a' relationships over building deep 'is-a' inheritance trees. In Android, inheritance creates bloated BaseActivity anti-patterns where every screen inherits irrelevant analytics, dialog, and permission methods. Composition replaces this by injecting independent, reusable helpers and lifecycle observers, avoiding fragile base class bugs and providing the foundational architectural model for Jetpack Compose.""",
    "structured_en": """The principle of favoring composition over inheritance resolves the architectural fragility inherent in deep class inheritance trees.
Class inheritance creates white-box code reuse where child classes are tightly coupled to the internal implementation mechanics and protected fields of their parents. In Android development, this anti-pattern manifests most visibly in bloated BaseActivity and BaseFragment hierarchies. Over years of development, teams dump analytics tracking, toolbar setup, loading spinners, network retry dialogs, and permission handling into a monolithic base class. Every child screen inherits dozens of methods and lifecycle hooks it does not need, creating namespace collisions, accidental method override bugs, and untestable code.
Composition solves this by treating capabilities as discrete, swappable components assembled via 'has-a' references.
Instead of an Activity inheriting from a base class to gain analytics capabilities, it has an AnalyticsTracker injected into it. Instead of inheriting permission mechanics, it delegates to a LocationPermissionHelper that observes the Activity's Lifecycle.
This approach eliminates the fragile base class problem, makes testing straightforward by allowing individual delegates to be mocked or faked on the JVM, and allows components to be combined flexibly without rigid parent-child hierarchies.""",
    "deep_senior_en": """Under the hood, composition fundamentally transforms memory layout, runtime dispatch, and evolutionary adaptability in Android applications.
Class inheritance fixes behavior statically at compile time: once class CheckoutActivity extends BaseActivity, its class hierarchy, v-table offsets, and superclass constructor chains are permanently baked into DEX bytecode. If the base class constructor allocates expensive resources, every single derived Activity pays that heap and startup latency penalty, even for lightweight splash or deep-link routing screens.
With composition, capabilities are allocated lazily and conditionally. A screen only instantiates delegates it actively uses, keeping the runtime heap footprint minimal.
Furthermore, Kotlin provides native language ergonomics for composition through interface delegation using the by keyword (class SecureStorage(inner: Storage) : Storage by inner). This delivers the syntax convenience of inheritance with the structural safety of composition.
Most importantly, composition is the defining paradigm shift behind Jetpack Compose. In the legacy View framework, every UI element extended the monolithic android.view.View class (which contains over 30,000 lines of code and hundreds of fields). Jetpack Compose completely abandons this inheritance model. A Compose UI tree is constructed purely through function composition, passing modifiers and state holders as parameters, ensuring that UI components remain lightweight, decoupled, and trivially reusable across multiple platforms.""",
    "meta_ar": {
        "id": "SOL-09",
        "questionAr": "ما هو مبدأ تفضيل التركيب على الوراثة (Composition over Inheritance) ولماذا يُعتبر حاسماً في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الفرق الجوهري بين علاقة 'is-a' والتركيب 'has-a'، ومشاكل الوراثة العميقة وفخ الـ Fragile Base Class في BaseActivity، والقدرة على شرح كيف يطبق Jetpack Compose مبدأ التركيب.",
        "why_it_matters_ar": "الاعتماد على الوراثة يخلق كلاسات BaseActivity عملاقة ترثها كل الشاشات ببويلربليت هائل وتسريبات ذاكرة وصعوبة قصوى في الاختبار وتعديل الكود.",
        "worked_example_ar": "استبدال BaseActivity بالتركيب عبر Delegates:\n```kotlin\n// كود سيئ: وراثة تجبر الشاشة على وراثة كل شيء\nclass ScreenA : BaseActivity()\n// كود نظيف: تركيب القدرات المطلوبة فقط\nclass ScreenB : ComponentActivity() {\n    val tracker = AnalyticsTracker()\n    val permissions = PermissionDelegate(this)\n}\n```",
        "trade_offs_ar": "التركيب يتطلب كتابة دوال تفويض أو حقن كائنات متعددة، لكنه يقضي تماماً على تضخم الكلاسات ويمنح مرونة مطلقة وسهولة في الاختبار.",
        "failure_modes_ar": "وضع منطق التتبع والـ Permissions وتحميل الديالوجات في `BaseActivity` وجعل كل شاشات التطبيق ترثه إجبارياً.",
        "production_perspective_ar": "في الفرق الهندسية المتقدمة، يتم حظر إنشاء أي كلاسات `BaseActivity` جديدة، ويتم استخدام Delegates ومراقبي دورة الحياة (DefaultLifecycleObserver) والكومبوز.",
        "how_to_answer_ar": "عرف المبدأ: تفضيل تجميع القدرات بعلاقة 'has-a' على شجرة الوراثة 'is-a'، واشرح مشكلة الـ Fragile Base Class في BaseActivity، واعرض البديل بالـ Delegates ومراقبي الـ Lifecycle، واختم بكونه الأساس المعماري لـ Jetpack Compose.",
        "talking_points_ar": "علاقة is-a مقابل has-a، ومشكلة الـ Fragile Base Class في BaseActivity، والـ Lifecycle Observers والـ Delegates، ومقارنة View بـ Compose.",
        "follow_ups_ar": "- **المحاور:** \"كيف تدعم لغة Kotlin مبدأ التركيب برمجياً؟\"\n  **المرشح:** \"عبر ميزة تفويض الكلاسات (Class Delegation) باستخدام كلمة `by`؛ فتقدر تركب كائن وتنفذ الإنترفيس بتاعه وتفوض الاستدعاءات له بسطر واحد بدون كود وسيط.\"\n\n- **المحاور:** \"كيف يعبر Jetpack Compose عن مبدأ التركيب؟\"\n  **المرشح:** \"الكومبوز تخلى تماماً عن وراثة كلاس `View` الضخم، وبقى بيبني الشاشات بتركيب دوال نقية وتمرير Modifiers، فبقى الزرار أو النص كائن خفيف جداً بدون أي حمل وراثة موروث.\"",
        "self_check_ar": "هل وضحت الفارق بين is-a و has-a؟ هل شرحت عيوب BaseActivity؟ وهل ربطت الإجابة بالـ Delegates و Jetpack Compose؟",
        "references_ar": f"- [Composition over inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance) — المرجع الكلاسيكي لمبدأ التركيب على الوراثة.\n- [Compose Thinking in Compose](https://developer.android.com/develop/ui/compose/mental-model) — الدليل الرسمي للتفكير التكويني في Jetpack Compose.",
        "quick_answer_ar": "مبدأ تفضيل التركيب على الوراثة (Composition over Inheritance) بينص على إننا نجمع ونركب سلوكيات الكلاسات باستخدام علاقات الامتلاك 'has-a' بدل ما نبني شجرات وراثة صلبة ومعقدة بعلاقات 'is-a'. في أندرويد، الوراثة بتخلق فخ الـ `BaseActivity` و `BaseFragment` العملاقة اللي بتجبر كل الشاشات ترث عشرات الدوال والديالوجات اللي مش محتاجاها. التركيب بيحل المشكلة دي بإنه بيخلي الشاشة تمتلك كائنات مساعدة مستقلة (Delegates) حسب حاجتها فقط، وهو الأساس المعماري اللي اتبنى عليه Jetpack Compose بالكامل.",
        "best_answer_ar": "مبدأ تفضيل التركيب على الوراثة هو واحد من أهم مبادئ التصميم اللي بتفرق بين المطور المبتدئ والمهندس المعماري المحترف.\n\nالوراثة بتبني علاقة 'is-a' صلبة جداً، وبتكشف التفاصيل الداخلية للكلاس الأب للابن (White-box reuse). المشكلة الشهيرة في أندرويد هي الـ `BaseActivity`؛ تلاقي المطورين على مدار سنين حاطين فيها منطق الـ Analytics، وفحص الـ Permissions، وإظهار الـ Loading Dialog، ودوال الرجوع. النتيجة إن شاشة بسيطة جداً زي شاشة About تلاقي نفسها وارثة 40 دالة ومحمّلة بـ Listeners في دورة الحياة هي ملهاش أي دعوة بيهم، وأي تعديل في الكلاس الأب ممكن يكسر شاشات تانية في التطبيق (Fragile Base Class Problem).\n\nالتركيب بيعالج الأزمة دي بالاعتماد على علاقة 'has-a'.\nبدل ما الشاشة ترث من BaseActivity عشان تاخد الـ Analytics، الشاشة بتمتلك كائن `AnalyticsTracker` مستقل بيتم حقنه فيها.\nوبدل ما ترث كود الصلاحيات، بنعمل `LocationPermissionDelegate` بيراقب دورة حياة الشاشة باستخدام `DefaultLifecycleObserver`.\n\nالأسلوب ده بيدينا ميزة هائلة في الاختبارات؛ لأنك تقدر تختبر كل Delegate لوحده على الـ JVM، وبيدينا حرية تبديل السلوك وقت التشغيل بدون قيود الوراثة الصارمة.",
        "deep_answer_ar": "تحت الكابوت، التركيب بيغير طريقة إدارة الذاكرة وجداول التوجيه (V-tables) وإقلاع التطبيق في بيئة تشغيل أندرويد ART Runtime.\n\nفي الوراثة الكلاسيكية، شجرة الكلاسات بتتحدد بشكل غير قابل للتغيير في وقت الـ Compilation داخل ملفات الـ DEX. لو الـ `BaseActivity` بتحجز كائنات في الكونستركتور بتاعها، كل شاشة في التطبيق بتدفع ثمن حجز الذاكرة دي في الـ Heap وثمن تأخير إقلاع الشاشة، حتى لو كانت شاشة توجيه سريعة (Routing Activity). مع التركيب، حجز الكائنات بيكون اختياري ولحظي (Lazy & Conditional)، فالشاشة بتحجز فقط الكائنات اللي محتاجاها فعلياً.\n\nلغة كوتلن سهلت تطبيق المبدأ ده بشكل غير مسبوق عبر ميزة الـ Class Delegation باستخدام كلمة `by`؛ فتقدر تركب كلاس وتفوض له تنفيذ واجهة كاملة بسطر واحد وبأداء يضاهي الوراثة لكن بدون عيوبها المعمارية.\n\nوالتحول الأكبر والأعظم للمبدأ ده في أندرويد هو Jetpack Compose. في نظام الـ Views القديم، كل زرار أو كارد كان بيورث من كلاس `android.view.View` العملاق اللي بيحتوي على أكتر من 30 ألف سطر كود ومئات الحقول المحجوزة في الذاكرة. الكومبوز نسف المفهوم ده تماماً، واستبدل الوراثة بالتركيب النقي؛ واجهات الكومبوز عبارة عن دوال برمجية نقية بتتركب فوق بعضها، وتمرير الخصائص بيتم عبر `Modifier`، وده اللي خلى واجهات أندرويد الحديثة خفيفة وسريعة وقابلة للعمل على أنظمة متعددة بسلاسة تامة."
    }
}

# ==========================================
# SOL-10: A BaseFragment requires setupToolbar() but some screens have no toolbar. When does this violate LSP?
# ==========================================
DATA["SOL-10"] = {
    "concept_en": """Mandating a setupToolbar() method in an abstract or open BaseFragment violates the Liskov Substitution Principle (LSP) whenever derived fragments that do not possess a toolbar are forced to override the method by throwing UnsupportedOperationException, returning unexpected nulls, or implementing a silent no-op that breaks base class invariants or lifecycle expectations. When a base class establishes a behavioral contract, any host orchestrator (such as a Navigation component, parent Activity, or test harness) treating derived fragments polymorphically assumes that calling setupToolbar() performs valid configuration. If a subclass cannot fulfill this contract legitimately, it cannot be substituted safely for its base type, violating LSP.""",
    "walkthrough_en": """Refactoring an LSP-violating BaseFragment using optional capability interfaces:
```kotlin
// BAD ANTI-PATTERN: Violates LSP (Forced override throws exception or silent no-ops breaking contracts)
abstract class BadBaseFragment : Fragment() {
    abstract fun setupToolbar(): Toolbar // Contract implies EVERY screen has a valid Toolbar!
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val toolbar = setupToolbar()
        (activity as? AppCompatActivity)?.setSupportActionBar(toolbar)
    }
}

class FullscreenMediaFragment : BadBaseFragment() {
    override fun setupToolbar(): Toolbar {
        // BLATANT LSP VIOLATION: Subclass cannot fulfill contract and crashes the app!
        throw UnsupportedOperationException("Fullscreen screen has no toolbar!")
    }
}

// ARCHITECTURAL BEST PRACTICE: Segregated optional capability contract adhering to LSP
interface ToolbarHost {
    fun configureToolbar(toolbar: Toolbar)
}

// Base Fragment manages ONLY genuine universal concerns (or eliminate BaseFragment entirely!)
abstract class CleanBaseFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Check capability polymorphically without forcing subclasses to fake implementations
        if (this is ToolbarHost) {
            view.findViewById<Toolbar?>(R.id.toolbar)?.let { configureToolbar(it) }
        }
    }
}

// Screens with a toolbar explicitly opt into the contract
class HomeFragment : CleanBaseFragment(), ToolbarHost {
    override fun configureToolbar(toolbar: Toolbar) {
        toolbar.title = "Home"
    }
}

// Fullscreen screen simply does NOT implement ToolbarHost (100% LSP compliant!)
class FullscreenFragment : CleanBaseFragment() { /* No toolbar baggage! */ }
```""",
    "short_en": """Forcing setupToolbar() inside BaseFragment violates the Liskov Substitution Principle when derived screens lack a toolbar and must throw UnsupportedOperationException, return null, or provide a silent no-op that breaks caller expectations. If callers polymorphically invoke setupToolbar() expecting a configured toolbar, the program crashes or corrupts layout state. The fix is removing setupToolbar() from the base class and moving it to an optional capability interface like ToolbarHost.""",
    "structured_en": """Requiring all fragments to implement setupToolbar() exposes a textbook violation of the Liskov Substitution Principle arising from speculative base class design.
When a base class declares abstract fun setupToolbar(): Toolbar or relies on an open method, it establishes a formal contract: every child fragment is guaranteed to have a functional Toolbar and can configure it during view creation.
This violates LSP the moment a screen without a toolbar is introduced, such as a full-screen video player, an onboarding carousel, or a splash screen.
If the developer overrides setupToolbar() to throw UnsupportedOperationException, any polymorphic caller invoking the method triggers a fatal runtime crash, blatantly violating substitutability.
If the developer returns null where a non-null Toolbar was expected, the parent Activity or base class triggers a NullPointerException.
Even if the method is designed to return a nullable Toolbar and the child returns null, or if the method has an empty body, it violates LSP if the base class assumes that a toolbar is present to wire navigation icons, menu inflation, or title updates.
To resolve this cleanly, toolbar configuration should be removed from BaseFragment entirely. Instead, define an optional ToolbarHost capability interface or delegate toolbar configuration to individual screens, ensuring every subclass satisfies its contracts completely.""",
    "deep_senior_en": """Under the hood, this scenario illustrates how inheritance hierarchies conflate shared framework lifecycles with heterogeneous UI capabilities.
A Fragment is a framework lifecycle controller, whereas a Toolbar is an optional presentation widget. Forcing a widget-specific contract into a lifecycle controller's base class creates tight, unworkable coupling.
In enterprise Android development, when BaseFragment invokes setupToolbar() inside onViewCreated(), it assumes the existence of view hierarchy elements before derived classes have even bound their state machines. When a child fragment provides a no-op or returns null, it often causes parent Activity action bar state corruption, where the previous screen's toolbar remains attached to the Activity's window decor, leading to stale menu items and broken back-arrow navigation.
Senior architects resolve this by moving away from inheritance entirely toward composition and capability interfaces.
If using Fragments, the screen implements an optional interface: interface ToolbarProvider { val toolbarResId: Int }. The Activity or a dedicated NavigationListener interrogates the current destination: if (currentFragment is ToolbarProvider), it configures the Action Bar; otherwise, it collapses or hides it.
In modern Jetpack Compose, this entire category of bugs is eradicated by design. In Compose, top app bars are standard composable components declared inside a screen's Scaffold(topBar = { TopAppBar(...) }). Screens that do not need a toolbar simply omit the topBar parameter, achieving complete structural independence without fragile base class inheritance.""",
    "meta_ar": {
        "id": "SOL-10",
        "questionAr": "عندما يفرض كلاس BaseFragment وجود دالة setupToolbar() ولكن بعض الشاشات ليس بها شريط أدوات، متى يعتبر هذا انتهاكاً لمبدأ ليسكوف (LSP) وكيف تحله؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم التطبيق العملي لمبدأ ليسكوف (LSP) في واجهات أندرويد، ورصد عيوب فرض عقود غير عامة في الكلاسات الأساسية (Base Classes)، والقدرة على إعادة التصميم باستخدام واجهات القدرات الاختيارية (Capability Interfaces) أو Jetpack Compose.",
        "why_it_matters_ar": "فرض دوال خاصة بمكونات معينة في الـ BaseFragment يجبر الشاشات التي لا تحتوي على المكون على التهرب برمي استثناءات أو كتابة دوال فارغة، مما يسبب انهيارات وقت التشغيل وأخطاء في شريط الملاحة.",
        "worked_example_ar": "حل انتهاك ليسكوف في BaseFragment:\n```kotlin\n// كود سيئ يكسر ليسكوف: إجبار كل الشاشات على تولبار\nabstract class BaseFrag { abstract fun setupToolbar(): Toolbar }\n// كود نظيف: واجهة قدرة اختيارية (Capability Interface)\ninterface ToolbarHost { fun setupToolbar(t: Toolbar) }\n// الشاشة التي بها تولبار فقط هي التي تطبقها\nclass HomeFrag : Fragment(), ToolbarHost { override fun setupToolbar(t: Toolbar) { ... } }\n```",
        "trade_offs_ar": "يتطلب إزالة الكود الموحد من الـ BaseFragment وكتابته في الشاشات المعنية أو واجهات منفصلة، لكنه يحقق أماناً تاماً ويمنع الانهيارات تماماً.",
        "failure_modes_ar": "رمي `UnsupportedOperationException` داخل شاشة الفيديو أو الشاشة الكاملة لتجنب إرجاع Toolbar، مما يسبب انهيار التطبيق عند فتح الشاشة.",
        "production_perspective_ar": "في التطبيقات الحديثة، نلغي `BaseFragment` تماماً، ونتعامل مع الـ Toolbar كـ Composable عادي داخل `Scaffold` في Jetpack Compose، بحيث تضعه الشاشة التي تحتاجه فقط.",
        "how_to_answer_ar": "بين متى يحدث الكسر: عندما يُجبر كلاس الشاشة التي ليس بها تولبار على رمي UnsupportedOperationException أو إرجاع null يكسر توقعات الكلاس الأب، واعرض الحل المعماري: إزالة الدالة من BaseFragment وجعلها في إنترفيس اختياري ToolbarHost، أو حل المشكلة جذرياً باستخدام Scaffold في Jetpack Compose.",
        "talking_points_ar": "شروط كسر ليسكوف (رمي استثناء أو دالة فارغة تكسر الحالة)، والخلط بين دورة حياة الفراجمنت ومكونات الـ UI، وحل Capability Interface، والتخلص من المشكلة كلياً في Compose Scaffold.",
        "follow_ups_ar": "- **المحاور:** \"ماذا لو عدلنا الدالة لتكون `fun setupToolbar(): Toolbar?` وأرجعنا null في الشاشة التي ليس بها تولبار، هل هذا يحل كسر ليسكوف؟\"\n  **المرشح:** \"لو الكلاس الأب مصمم ليتعامل بأمان مع الـ null بدون ما يفترض وجود تولبار أو يسبب أخطاء في الملاحة، مش هيكون فيه كسر صريح لليسكوف، لكنه بيفضل تصميم سيئ بيخلط مكونات الواجهة بدورة حياة الفراجمنت.\"\n\n- **المحاور:** \"كيف يقضي Jetpack Compose على هذه المشكلة تماماً؟\"\n  **المرشح:** \"في الكومبوز مفيش وراثة أصلاً؛ الشاشة اللي محتاجة تولبار بتعرفه جوه `Scaffold(topBar = { ... })`، والشاشة اللي مش محتاجة بتسيب البارامتر فاضي، بدون أي كلاس أساسي مشترك.\"",
        "self_check_ar": "هل بينت بدقة متى يُعتبر ذلك انتهاكاً لليسكوف؟ هل شرحت عيوب رمي الاستثناء؟ وهل عرضت الحل بالـ Capability Interface وحل الكومبوز؟",
        "references_ar": f"- [Liskov Substitution Principle](https://en.wikipedia.org/wiki/Liskov_substitution_principle) — المرجع الأكاديمي لمبدأ استبدال ليسكوف.\n- [Scaffold and App Bars in Compose](https://developer.android.com/develop/ui/compose/components/scaffold) — دليل استخدام الـ Scaffold في Jetpack Compose.",
        "quick_answer_ar": "بيعتبر انتهاك لمبدأ ليسكوف (LSP) في اللحظة اللي تضطر فيها شاشة معندهاش Toolbar إنها تعمل Override للدالة وترمي `UnsupportedOperationException` أو ترجع `null` غير متوقع أو تعمل دالة فارغة تكسر توقعات الكلاس الأب وتسبب انهيار التطبيق أو تشوه شريط الملاحة. حل المشكلة دي معمارياً هو إننا نشيل `setupToolbar()` من كلاس `BaseFragment` تماماً، وننقلها لـ Interface اختياري زي `ToolbarHost`، الشاشة اللي فيها Toolbar بس هي اللي تطبقه، أو نعتمد على Jetpack Compose اللي بيحل المشكلة دي كلياً بوضع الـ TopAppBar جوه `Scaffold` الشاشة فقط.",
        "best_answer_ar": "الموقف ده مثال كلاسيكي ومشهور جداً لانتهاك مبدأ ليسكوف بسبب التصميم السيئ للكلاسات الأساسية (Base Classes).\n\nلما الـ `BaseFragment` تحط دالة زي `abstract fun setupToolbar(): Toolbar`، هي بتفرض عقداً صارماً على كل الشاشات التابعة ليها: 'أي شاشة هتيجي مني لازم يكون عندها Toolbar حقيقي وجاهز للإعداد'.\n\nأول ما يظهر متطلب جديد لشاشة فيديو كاملة (Fullscreen Video) أو شاشة تسجيل دخول مفيهاش أي Toolbar، المطور بيقع في الفخ. لو عمل Override للدالة ورمى `throw UnsupportedOperationException(\"No toolbar\")`؛ كده مبدأ ليسكوف اتكسر تماماً! لأن الكود المشغل لما يعامل الفراجمنت كـ `BaseFragment` وينادي الدالة دي، التطبيق هيحصله Crash فوري.\nولو خلى الدالة ترجع `null` بينما الكلاس الأب متوقع كائن حقيقي، هيحصل `NullPointerException`. ولو عمل دالة فارغة بتسيب الـ Toolbar بتاع الشاشة اللي فاتت شغال، هيحصل خلل بصري وتضارب في أزرار الرجوع والقوائم.\n\nالحل المعماري الاحترافي بيتكون من خيارين:\nالأول في نظام الفراجمنتس: هو إزالة الدالة من الـ BaseFragment، وتحويلها لـ Capability Interface اختياري اسمه `ToolbarHost`. الشاشة اللي فيها Toolbar بتطبق الإنترفيس ده، والشاشة التانية متطبقهوش، وبكده مفيش أي كلاس بيجبر على تزييف عقده.\nوالحل الثاني والأفضل في المعمارية الحديثة: هو التخلص من وراثة الفراجمنتس تماماً واستخدام Jetpack Compose؛ الشاشة بتعرف الـ `TopAppBar` بتاعها جوه `Scaffold` مستقل، والصفحة اللي مش محتاجة بتسيبه فاضي بكل بساطة وبدون أي وراثة مشوهة.",
        "deep_answer_ar": "تحت الكابوت، المشكلة دي بتكشف خطأ معماري فادح وهو الخلط بين 'متحكم دورة الحياة' (Lifecycle Controller) ومكونات 'العرض البصري' (Presentation Widgets).\n\nالـ Fragment في نظام أندرويد وظيفته إدارة دورة حياة المكون واستعادة الحالة بعد الـ Process Death، بينما الـ Toolbar هو مجرد Widget بصري اختياري. فرض الـ Toolbar في الـ `BaseFragment` بيجبر الكلاس الأب إنه يستدعي الدالة في `onViewCreated` قبل ما الشاشة الابنة تكمل تهيئة متغيراتها، وده بيعمل Race Conditions ومشاكل في ربط الـ Action Bar في الـ Window Decor التابع للـ Activity.\n\nلما الشاشة الابنة ترجع null أو تعمل no-op، كود الـ Activity بيفشل في تنظيف القوائم السابقة (InvalidateOptionsMenu)، فتلاقي أيقونات وقوائم الشاشة اللي قبلها لسه ظاهرة ومعلقة فوق شاشة الفيديو، وممكن تدوس على زرار يفتح شاشة تانية بالخطأ.\n\nالمهندسون الكبار بيحلوا المعضلة دي بتطبيق مبدأ البرمجة المعتمدة على السمات (Feature/Capability Composition). بنعمل إنترفيس مستقل: `interface ToolbarProvider { fun bindToolbar(t: Toolbar) }`. وفي الـ Activity الرئيسية، بنسجل `FragmentLifecycleCallbacks`؛ وبنفحص بنقاء: `if (fragment is ToolbarProvider) { ... }`، وده بيضمن إن العقود تفضل نقية بنسبة 100% ومفيش أي كلاس ينفذ دالة وهمية.\n\nوفي Jetpack Compose، هذا النوع من المشاكل انتهى للأبد؛ لأن الـ Scaffold بيعتمد على الـ Slot APIs المستقلة لكل شاشة، مفيش أي كود مشترك بيجبرك ترسم TopAppBar مش محتاجه، وده بيحقق أعلى درجات الاستقلال والأمان المعماري."
    }
}

def main():
    print(f"Elevating {len(DATA)} questions in SOL (SOL-01 to SOL-10)...")
    
    # Check word counts before touching files
    all_counts_ok = True
    for qid in sorted(DATA.keys()):
        item = DATA[qid]
        en_short = len(item["short_en"].split())
        en_struct = len(item["structured_en"].split())
        en_deep = len(item["deep_senior_en"].split())
        ar_quick = len(item["meta_ar"]["quick_answer_ar"].split())
        ar_best = len(item["meta_ar"]["best_answer_ar"].split())
        ar_deep = len(item["meta_ar"]["deep_answer_ar"].split())
        
        print(f"{qid}: en_s={en_short}, en_st={en_struct}, en_d={en_deep} | ar_q={ar_quick}, ar_b={ar_best}, ar_d={ar_deep}")
        if not (35 <= en_short <= 110):
            print(f"  ❌ {qid} en_short invalid: {en_short}")
            all_counts_ok = False
        if not (100 <= en_struct <= 280):
            print(f"  ❌ {qid} en_struct invalid: {en_struct}")
            all_counts_ok = False
        if not (200 <= en_deep <= 650):
            print(f"  ❌ {qid} en_deep invalid: {en_deep}")
            all_counts_ok = False
        if not (35 <= ar_quick <= 110):
            print(f"  ❌ {qid} ar_quick invalid: {ar_quick}")
            all_counts_ok = False
        if not (90 <= ar_best <= 280):
            print(f"  ❌ {qid} ar_best invalid: {ar_best}")
            all_counts_ok = False
        if not (180 <= ar_deep <= 650):
            print(f"  ❌ {qid} ar_deep invalid: {ar_deep}")
            all_counts_ok = False
            
    if not all_counts_ok:
        print("Pre-validation word count checks failed! Fix counts before updating files.")
        sys.exit(1)
        
    print("\nPre-validation word count checks passed! Updating canonical questions...")
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
    ee.save_topic_metadata("sol_01_10", {qid: d["meta_ar"] for qid, d in DATA.items()})

    # Merge into main metadata
    ee.merge_all_metadata()

    # Validate each question
    all_ok = True
    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"❌ {qid} validation errors:")
            for e in errs:
                print(f"   - {e}")
            all_ok = False
        else:
            print(f"✅ {qid} passed validation with 0 errors!")

    if all_ok:
        print("\nAll 10 SOL questions (SOL-01 to SOL-10) successfully elevated and passed validation!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
