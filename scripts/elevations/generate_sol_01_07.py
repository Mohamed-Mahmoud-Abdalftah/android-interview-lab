#!/usr/bin/env python3
"""Generator for SOL-01 through SOL-07 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "sol.json"

SOL_01_07 = [
    {
        "id": "SOL-01",
        "arabic_explanation": (
            "ما هي مبادئ SOLID الخمسة ولماذا تُعد حجر الأساس في هندسة تطبيقات Android الاحترافية؟\n\n"
            "1. ما الذي ترمز إليه حروف SOLID؟\n"
            "   - **S - Single Responsibility Principle (SRP)**: كل كلاس يمتلك مسؤولية واحدة فقط وسبباً واحداً للتغيير.\n"
            "   - **O - Open/Closed Principle (OCP)**: الكيانات البرمجية مفتوحة للتوسيع (Extension) ومغلقة للتعديل (Modification).\n"
            "   - **L - Liskov Substitution Principle (LSP)**: الكلاسات الفرعية يجب أن تحل محل الكلاسات الأساسية دون كسر صحة وسلوك البرنامج.\n"
            "   - **I - Interface Segregation Principle (ISP)**: تقسيم الواجهات الضخمة إلى واجهات صغيرة محددة؛ لا تُجبر كوداً على تنفيذ دوال لا يحتاجها.\n"
            "   - **D - Dependency Inversion Principle (DIP)**: الوحدات العليا لا تعتمد على الوحدات الدنيا؛ كلاهما يعتمد على التجريدات (Abstractions).\n\n"
            "2. لماذا تُعتبر حيوية في Android الحديث؟\n"
            "   - بدون SOLID، يتحول المشروع إلى **كود هش (Fragile Code)**: أي تعديل في شاشة يكسر شاشة أخرى، وتتضخم الـ Activities إلى God Classes يستحيل اختبارها.\n"
            "   - تطبيق SOLID يضمن: سهولة الصيانة، قابلية الاختبار بنسبة 100% على الـ JVM، وسهولة تقسيم المشروع إلى Gradle Modules مستقلة."
        ),
        "practical_walkthrough": (
            "نظرة سريعة على كود ينتهك SOLID وكود يعتمد عليها في Android:\n"
            "```kotlin\n"
            "// ❌ انتهاك صارخ لمبادئ SOLID: God Activity تجمع كل شيء:\n"
            "class MonolithicProfileActivity : AppCompatActivity() {\n"
            "    // تنتهك SRP: تجمع الرسم، واستدعاء Retrofit، وحفظ SQLite، والـ Validation!\n"
            "    // تنتهك OCP: إضافة نوع مستخدم جديد يتطلب تعديل if/else في 5 دوال.\n"
            "    // تنتهك DIP: تعتمد على كائنات ملموسة مباشرة new Retrofit().\n"
            "}\n"
            "\n"
            "// ✅ تطبيق SOLID: تفكيك المسؤوليات إلى مكونات متماسكة ومعزولة:\n"
            "class ProfileViewModel @Inject constructor(\n"
            "    private val getProfile: GetProfileUseCase, // DIP & SRP\n"
            "    private val analytics: AnalyticsTracker // ISP & OCP\n"
            ") : ViewModel() {\n"
            "    val uiState: StateFlow<ProfileUiState> = ...\n"
            "}\n"
            "```"
        ),
        "quick_answer": "SOLID stands for Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion. In Android, these principles prevent monolithic God Activities, isolate business rules from framework churn, enable pure JVM unit testing, and maintain high code cohesion in multi-module codebases.",
        "best_answer": (
            "SOLID represents five foundational object-oriented design principles aimed at creating maintainable, testable, and scalable software systems.\n\n"
            "1. **Single Responsibility (SRP)**: A class should have one, and only one, reason to change.\n"
            "2. **Open/Closed (OCP)**: Software entities should be open for extension (adding new features via polymorphism or composition) but closed for modification (not editing existing tested code).\n"
            "3. **Liskov Substitution (LSP)**: Subtypes must be substitutable for their base types without altering program correctness or throwing unexpected exceptions.\n"
            "4. **Interface Segregation (ISP)**: Clients should not be forced to depend on interfaces they do not use; prefer many fine-grained interfaces over one fat interface.\n"
            "5. **Dependency Inversion (DIP)**: High-level business policies should not depend on low-level infrastructure details; both should depend on abstractions.\n\n"
            "In Android, violating SOLID leads to fragile 'God Activities', tight coupling to SDK lifecycles, and impossible unit testing. Adhering to SOLID keeps domain logic decoupled from framework churn."
        ),
        "deep_answer": (
            "Under the hood, SOLID principles are not dogmatic laws—they are tools to manage **coupling and cohesion**. "
            "High cohesion means code that changes together stays together; loose coupling means changes in one module do not ripple into others.\n\n"
            "In modern Android architectures (Clean Architecture + Jetpack Compose + Kotlin Coroutines), SOLID principles manifest concretely:\n"
            "- SRP drives the separation between ViewModels, Use Cases, Repositories, and DataSources.\n"
            "- OCP enables feature extensions via Strategy patterns and polymorphic sealed classes.\n"
            "- LSP eliminates rigid, deeply nested inheritance hierarchies like bloated `BaseActivity` classes in favor of composable delegates.\n"
            "- ISP creates focused repository interfaces (`UserReader`, `UserWriter`) rather than monolithic CRUD interfaces.\n"
            "- DIP powers inversion of control where the Domain layer defines repository contracts implemented by the Data layer.\n\n"
            "We balance SOLID against the YAGNI principle to prevent speculative overengineering in early-stage features."
        ),
        "follow_ups": [
            {
                "question": "Which SOLID principle is most commonly violated in legacy Android codebases?",
                "answer": "The Single Responsibility Principle (SRP), typically resulting in massive 'God Activities' or 'God Fragments' managing UI inflation, network calls, SQLite transactions, and business calculations in a single file."
            },
            {
                "question": "How does Kotlin's language design support SOLID out of the box?",
                "answer": "Kotlin promotes SOLID via first-class composition (delegation via `by`), pure functions, interface default implementations, immutability by default (`val`), and sealed hierarchies for type-safe extension."
            }
        ]
    },
    {
        "id": "SOL-02",
        "arabic_explanation": (
            "شرح مبدأ المسؤولية الواحدة (Single Responsibility Principle - SRP) مع مثال عملي واقعي في Android:\n\n"
            "1. تعريف مبدأ المسؤولية الواحدة (SRP):\n"
            "   - ينص المبدأ على: **\"يجب أن يمتلك الكلاس سبباً واحداً فقط للتغيير (Single Reason to Change)\"**.\n"
            "   - أو بتعبير روبرت مارتن الأعمق: **\"يجب أن يكون الكلاس مسؤولاً أمام مستخدم أو جهة مصلحة واحدة فقط (Single Actor)\"**.\n\n"
            "2. ما الذي ينتهك SRP في Android؟\n"
            "   - كلاس `UserRegistrationActivity` يقوم بالتحقق من صحة الإيميل (Business Rule)، وطلب السيرفر بـ Retrofit (Networking)، وعرض ProgressDialog (UI)، وحفظ الـ Token في SharedPreferences (Storage).\n   - أسباب التغيير متعددة: إذا تغير تصميم الشاشة، أو تغيرت قواعد الإيميل، أو تغيرت الـ API، أو تغير التخزين إلى DataStore—كل هذه الأسباب المختلفة تجبرك على تعديل نفس الكلاس!\n\n"
            "3. كيف نطبق SRP بشكل سليم؟\n   - **EmailValidator**: مسؤول عن قواعد التحقق فقط (سبب التغيير: قرار قسم الـ Product).\n   - **AuthRepository**: مسؤول عن الشبكة والتخزين (سبب التغيير: قرار قسم الـ Backend أو الـ Infrastructure).\n   - **RegisterViewModel**: ينسق بين الواجهة والبيزنس.\n   - **RegisterScreen**: مسؤول عن الرسم والتفاعل فقط (سبب التغيير: قرار مصمم الـ UI/UX)."
        ),
        "practical_walkthrough": (
            "تطبيق مبدأ SRP بفصل المسؤوليات المعزولة في شاشة التسجيل:\n"
            "```kotlin\n"
            "// ❌ انتهاك صارخ لـ SRP: كلاس واحد يقوم بالتحقق، والشبكة، والتخزين، وتحديث الواجهة:\n"
            "class BadRegistrationActivity : AppCompatActivity() {\n"
            "    fun onRegisterClicked(email: String, pass: String) {\n"
            "        if (!email.contains(\"@\")) return // منطق بيزنس!\n"
            "        api.register(email, pass) { response -> // اتصال شبكة!\n"
            "            prefs.edit().putString(\"token\", response.token).apply() // تخزين محلي!\n"
            "            showSuccessDialog() // رسم واجهة!\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ تطبيق SRP السليم: كل كائن له مسؤولية وحيدة وسبب واحد للتعديل:\n"
            "class EmailValidator { // سبب التغيير: تعديل قواعد الإيميل من الـ Business\n"
            "    fun isValid(email: String): Boolean = email.isNotBlank() && Patterns.EMAIL_ADDRESS.matcher(email).matches()\n"
            "}\n"
            "\n"
            "class RegisterUserUseCase(private val authRepo: AuthRepository, private val validator: EmailValidator) {\n"
            "    suspend operator fun invoke(email: String, pass: String): Result<UserSession> {\n"
            "        if (!validator.isValid(email)) return Result.failure(InvalidEmailException())\n"
            "        return authRepo.register(email, pass)\n"
            "    }\n"
            "}\n"
            "\n"
            "// الـ ViewModel مسؤول حصرياً عن إدارة الـ UI State وإطلاق الـ UseCase:\n"
            "@HiltViewModel\n"
            "class RegisterViewModel @Inject constructor(private val registerUser: RegisterUserUseCase) : ViewModel() { ... }\n"
            "```"
        ),
        "quick_answer": "Single Responsibility Principle dictates that a class should have only one reason to change (one business actor). In Android, instead of letting an Activity handle validation, network calls, storage, and UI rendering, we divide responsibilities into a Validator, a UseCase, a Repository, and a ViewModel.",
        "best_answer": (
            "The Single Responsibility Principle (SRP) states that a software component should have one, and only one, reason to change.\n\n"
            "A 'reason to change' aligns directly with the business actor who requests the modification. If a single class caters to requests from the UI designer, the security officer, and the database administrator simultaneously, it severely violates SRP.\n\n"
            "In Android, a textbook SRP violation is a monolithic Activity or ViewModel that performs:\n"
            "1. Input validation (e.g. password complexity rules).\n"
            "2. Network API invocation and HTTP header management.\n"
            "3. SQLite / SharedPreferences token persistence.\n"
            "4. UI layout manipulation and dialog animations.\n\n"
            "To resolve this, we break responsibilities into cohesive units:\n"
            "- `PasswordValidator`: Pure validation rules (responds to security policy changes).\n"
            "- `AuthRepository`: Encapsulates network communication and token persistence (responds to backend API/storage changes).\n"
            "- `RegisterUserUseCase`: Orchestrates the registration business flow.\n"
            "- `RegisterViewModel`: Projects results into `RegisterUiState` (responds to UI workflow changes)."
        ),
        "deep_answer": (
            "A subtle pitfall when applying SRP is **over-fragmentation** (creating a new class for every single function). "
            "SRP is about **cohesion around a single actor**, not making classes microscopic. "
            "If five utility functions all serve the exact same business responsibility and change together, keeping them in one cohesive class respects SRP.\n\n"
            "In unit testing, SRP delivers immediate gains. "
            "Testing `PasswordValidator` requires a 10-line JVM unit test verifying strings. "
            "If password rules were buried inside `RegistrationActivity`, testing them would require booting an Android Activity, finding view IDs, and dealing with Robolectric or espresso overhead."
        ),
        "follow_ups": [
            {
                "question": "What is the relationship between SRP and Cohesion?",
                "answer": "Cohesion measures how closely related the functions within a class are. SRP maximizes cohesion by ensuring all methods in a class serve a single unified purpose."
            },
            {
                "question": "How do you detect an SRP violation during code review?",
                "answer": "Look at the class imports: if a ViewModel imports SQLite, OkHttp, and Android View classes, or if the class description requires using the word 'AND' ('This class fetches data AND validates AND formats UI'), it violates SRP."
            }
        ]
    },
    {
        "id": "SOL-03",
        "arabic_explanation": (
            "شرح مبدأ الفتح والإغلاق (Open/Closed Principle - OCP) مع مثال عملي واقعي في Android:\n\n"
            "1. تعريف مبدأ الـ OCP:\n"
            "   - ينص المبدأ على: **\"يجب أن تكون الكيانات البرمجية مفتوحة للتوسيع (Open for Extension) ومغلقة للتعديل (Closed for Modification)\"**.\n   - **مفتوحة للتوسيع**: يمكنك إضافة ميزات وسلوكيات جديدة للتطبيق بسهولة.\n   - **مغلقة للتعديل**: إضافة الميزة الجديدة لا تتطلب تعديل الأكواد القديمة المكتوبة والمختبرة مسبقاً في الإنتاج!\n\n"
            "2. ما الذي ينتهك OCP في Android؟\n   - استخدام كتل `when` أو `if-else` الضخمة المعتمدة على Enums أو String types لمعالجة أنواع مختلفة (مثل طرق الدفع: Visa, PayPal, ApplePay).\n   - كلما طلبت الشركة إضافة طريقة دفع جديدة (مثل Google Pay أو Fawry)، يضطر المطور لفتح الكلاس القديم وتعديل الـ when block، مما قد يكسر طرق الدفع القديمة!\n\n"
            "3. كيف نطبق OCP في Android؟\n   - باستخدام **نمط الاستراتيجية (Strategy Pattern)** أو **Polymorphism** عبر Interface مجرد (`PaymentProcessor`).\n   - إضافة طريقة دفع جديدة تعني ببساطة إنشاء كلاس جديد `GooglePayProcessor : PaymentProcessor` وحقنه في النظام دون لمس سطر واحد في كود الدفع الأصلي!"
        ),
        "practical_walkthrough": (
            "تطبيق نمط Strategy لتحقيق OCP في نظام معالجة المدفوعات:\n"
            "```kotlin\n"
            "// ❌ انتهاك صارخ لـ OCP: إضافة طريقة دفع جديدة تجبرنا على تعديل الكود القديم المعتمد:\n"
            "class BadPaymentService {\n"
            "    fun process(type: String, amount: Long) {\n"
            "        if (type == \"CREDIT_CARD\") { /* كود قديم */ }\n"
            "        else if (type == \"PAYPAL\") { /* كود قديم */ }\n"
            "        else if (type == \"APPLE_PAY\") { /* كود جديد تم حشره هنا! */ }\n"
            "        // 💥 أي خطأ هنا سيكسر الدفع بالبطاقات القديمة!\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ تطبيق OCP: مفتوح لإضافة طرق دفع جديدة دون تعديل الكود القائم إطلاقاً:\n"
            "interface PaymentProcessor {\n"
            "    val paymentMethod: PaymentMethod\n"
            "    suspend fun pay(amountCents: Long): PaymentResult\n"
            "}\n"
            "\n"
            "class CreditCardProcessor : PaymentProcessor { ... }\n"
            "class PayPalProcessor : PaymentProcessor { ... }\n"
            "// إضافة طريقة دفع جديدة لا تتطلب سوى كلاس جديد مستقل:\n"
            "class GooglePayProcessor : PaymentProcessor { ... }\n"
            "\n"
            "// الكلاس المنسق مغلق للتعديل ويعتمد على خريطة الموزعين:\n"
            "class PaymentRouter @Inject constructor(\n"
            "    private val processors: Set<PaymentProcessor>\n"
            ") {\n"
            "    suspend fun executePayment(method: PaymentMethod, amount: Long): PaymentResult {\n"
            "        val handler = processors.firstOrNull { it.paymentMethod == method } ?: error(\"Unsupported method\")\n"
            "        return handler.pay(amount)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Open/Closed Principle states that code should be open for extension but closed for modification. In Android, rather than using massive `when` statements checking payment or notification types, we use polymorphism and the Strategy pattern (`PaymentProcessor` interface), allowing new providers to be added without editing existing, tested classes.",
        "best_answer": (
            "The Open/Closed Principle (OCP) requires that software entities (classes, modules, functions) should be **open for extension, but closed for modification**.\n\n"
            "- **Open for extension**: The system's behavior can be enhanced as business requirements evolve.\n"
            "- **Closed for modification**: Adding new behaviors does not require modifying, recompiling, or risking regressions in existing, production-tested code.\n\n"
            "The primary violator of OCP in Android is type branching via long `when (type)` or `if-else` chains. For instance, an analytics engine or payment router that inspects string types: adding 'Google Pay' requires opening `PaymentManager.kt`, editing the conditional statements, and re-testing every existing payment method.\n\n"
            "We adhere to OCP using **Polymorphic Abstraction (The Strategy Pattern)**:\n"
            "1. Declare a common interface: `PaymentStrategy`.\n"
            "2. Implement distinct classes: `CreditCardStrategy`, `PayPalStrategy`, `GooglePayStrategy`.\n"
            "3. Inject a set of strategies via Dagger/Hilt Multibindings (`@IntoSet`).\n"
            "To introduce a new payment method, developers simply create a new class and bind it in a Dagger module; zero existing payment code is touched."
        ),
        "deep_answer": (
            "In modern Kotlin, **Sealed Hierarchies** offer an intentional balance with OCP. "
            "When using `sealed interface UiState`, the compiler enforces exhaustive `when` expressions, which intentionally requires modifying the UI when a new state is added. "
            "This is desirable when the set of states is closed and known at compile time.\n\n"
            "However, for **domain extensibility** (plugins, analytics trackers, payment gateways, validation rules), open interfaces and DI multibindings are strictly preferred over sealed classes. "
            "This allows feature modules to register new plugins dynamically without touching core orchestration modules."
        ),
        "follow_ups": [
            {
                "question": "How do Dagger Multibindings (`@IntoSet`, `@IntoMap`) enable OCP?",
                "answer": "Multibindings allow feature modules to contribute implementations to a central collection without the consuming class knowing about concrete implementations at compile time."
            },
            {
                "question": "Does OCP mean you should never modify existing code?",
                "answer": "No. Bug fixes, performance tuning, and refactoring inherently require modifying existing code. OCP specifically targets behavioral feature additions."
            }
        ]
    },
    {
        "id": "SOL-04",
        "arabic_explanation": (
            "شرح مبدأ استبدال لسكوف (Liskov Substitution Principle - LSP) مع مثال عملي واقعي في Android:\n\n"
            "1. تعريف مبدأ لسكوف (LSP):\n"
            "   - ينص المبدأ على: **\"إذا كان الكائن S كلاس فرعي من T، فيجب أن يكون من الممكن استبدال كائنات T بكائنات S دون كسر صحة وسلوك البرنامج أو تغيير خصائصه المرغوبة\"**.\n   - الكلاس الفرعي يجب ألا يكسر الوعود والتوقعات (Contracts) التي قطعها الكلاس الأساسي.\n\n"
            "2. ما الذي ينتهك LSP في Android؟\n   - **رمي استثناءات غير متوقعة (UnsupportedOperationException)**: مثل كلاس `BaseFragment` يجبر جميع الشاشات على تنفيذ `setupToolbar()`، ولكن هناك شاشة شريط سفلي (Bottom Sheet) لا تمتلك Toolbar، فيقوم المطور بـ `override fun setupToolbar() { throw UnsupportedOperationException() }` أو تركها فارغة!\n   - **تعديل الشروط المسبقة أو اللاحقة (Preconditions & Postconditions)**: كلاس أساسي يقبل أرقام سالبة، وكلاس فرعي يرمي Crash إذا كان الرقم سالباً.\n\n"
            "3. كيف نطبق LSP بشكل سليم في Android؟\n   - **استبدال الوراثة بالتركيب (Composition over Inheritance)**: بدلاً من فرض كل شيء في كلاس `BaseActivity` أو `BaseFragment` ضخم، نستخدم Component مستقلة أو Lifecycle Delegates، أو تقسيم الواجهات إلى عقود صغيرة."
        ),
        "practical_walkthrough": (
            "المقارنة بين انتهاك LSP في كلاسات الـ Base وكود متوافق مع LSP عبر الـ Delegates:\n"
            "```kotlin\n"
            "// ❌ انتهاك صارخ لـ LSP: إجبار الكلاس الفرعي على سلوك لا يدعمه مما يكسر التوقعات:\n"
            "open class BaseFragment : Fragment() {\n"
            "    open fun setupToolbar() {\n"
            "        // يتوقع الكود أن كل Fragment يمتلك Toolbar صالحاً للربط\n"
            "    }\n"
            "}\n"
            "\n"
            "class FullScreenVideoFragment : BaseFragment() {\n"
            "    override fun setupToolbar() {\n"
            "        // 💥 يكسر LSP: يرمي استثناء أو يتجاهل العقد لأن شاشة الفيديو بدون Toolbar!\n"
            "        throw UnsupportedOperationException(\"Video screen does not have a toolbar\")\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ تطبيق LSP السليم: فصل السلوك الاختياري في واجهة أو Delegate مستقل:\n"
            "interface ToolbarConfigurable {\n"
            "    fun configureToolbar(toolbar: Toolbar)\n"
            "}\n"
            "\n"
            "class HomeFragment : Fragment(), ToolbarConfigurable {\n"
            "    override fun configureToolbar(toolbar: Toolbar) { /* إعداد Toolbar للشاشات التي تحتاجه فقط */ }\n"
            "}\n"
            "\n"
            "class VideoFragment : Fragment() {\n"
            "    // لا ينفذ ToolbarConfigurable؛ لا استثناءات غير متوقعة ولا كسر للعقود!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Liskov Substitution Principle states that subclasses must be substitutable for their base classes without breaking program correctness. In Android, violating LSP manifests as throwing `UnsupportedOperationException` in subclasses (e.g. `BaseFragment.setupToolbar()`). We solve this by favoring composition or fine-grained interfaces over fat base classes.",
        "best_answer": (
            "The Liskov Substitution Principle (LSP), formulated by Barbara Liskov, requires that **subtypes must be completely substitutable for their base types without altering program correctness**.\n\n"
            "A subclass must adhere strictly to the behavioral contract established by its superclass. Specifically:\n"
            "1. **Preconditions cannot be strengthened**: A subclass cannot demand stricter validation inputs than its parent.\n"
            "2. **Postconditions cannot be weakened**: A subclass cannot return less or fail to fulfill state guarantees made by the parent.\n"
            "3. **Invariants must be preserved**: Any rules that hold true for the superclass must hold true for all subclasses.\n\n"
            "In Android, the most pervasive LSP violation is the bloated **`BaseFragment` / `BaseActivity` anti-pattern**. A `BaseFragment` declares abstract methods like `setupToolbar()`, `enableSwipeToRefresh()`, and `getBottomNavIndex()`.\n"
            "When a developer creates a fullscreen modal or onboarding slide that lacks a toolbar, they either override the method with an empty no-op or throw `UnsupportedOperationException(\"Not supported\")`. Calling code expecting a valid toolbar crashes or behaves unpredictably."
        ),
        "deep_answer": (
            "The architectural remedy for LSP violations in Android is **Composition over Inheritance**.\n\n"
            "Instead of forcing every screen to inherit from an arbitrary 800-line `BaseFragment`, we extract modular capabilities into dedicated lifecycle-aware delegates:\n"
            "- A `ToolbarDelegate` that attaches to screens that explicitly implement `ToolbarConfigurable`.\n"
            "- A `NetworkStateDelegate` that observes connectivity.\n\n"
            "In Jetpack Compose, LSP violations are naturally minimized because Compose entirely abandons inheritance hierarchies. "
            "A composable screen does not inherit from `BaseScreen`; instead, screens compose reusable composable decorators (`Scaffold`, `TopAppBar`, `PullToRefreshBox`) purely through function composition."
        ),
        "follow_ups": [
            {
                "question": "Why is throwing `UnsupportedOperationException` a classic sign of an LSP violation?",
                "answer": "Because the base class promised that the operation could be invoked. Throwing an exception unexpectedly breaks the caller's reasonable expectations."
            },
            {
                "question": "How does Jetpack Compose naturally eliminate LSP violations in UI?",
                "answer": "Compose uses functional composition instead of OOP inheritance hierarchies. UI components don't subclass `View` or `Activity`; they are pure functions that accept parameters."
            }
        ]
    },
    {
        "id": "SOL-05",
        "arabic_explanation": (
            "شرح مبدأ فصل الواجهات (Interface Segregation Principle - ISP) مع مثال عملي واقعي في Android:\n\n"
            "1. تعريف مبدأ فصل الواجهات (ISP):\n"
            "   - ينص المبدأ على: **\"لا ينبغي إجبار أي كود أو عميل (Client) على الاعتماد على واجهات (Interfaces) تحتوي على دوال لا يستخدمها\"**.\n   - الأفضل دائماً إنشاء عدة واجهات صغيرة متخصصة (Fine-grained interfaces) بدلاً من واجهة واحدة ضخمة تجمع كل شيء (Fat Interface).\n\n"
            "2. ما الذي ينتهك ISP في Android الكلاسيكي؟\n   - كلاس `TextWatcher` الشهير في Java Android! إذا أردت مراقبة النص فقط بعد تغييره، فأنت مجبر على تنفيذ 3 دوال: `beforeTextChanged`, `onTextChanged`, و `afterTextChanged`، وتترك أول دالتين فارغتين بلا فائدة!\n   - مستودع ضخم `interface FullUserRepository` يحتوي على 20 دالة (قراءة البروفايل، تحديث الصورة، حذف الحساب، دفع الفاتورة، تسجيل الدخول)؛ في حين أن شاشة العرض البسيطة تحتاج فقط لدالة قراءة الاسم!\n\n"
            "3. كيف نطبق ISP في Android الحديث؟\n   - تقسيم الواجهات الكبيرة إلى واجهات دقيقة حسب الاستخدام:\n     * `interface UserReader { fun getUser(): Flow<User> }`\n     * `interface UserWriter { suspend fun updateUser(user: User) }`\n   - في Kotlin، استخدام الـ Lambdas المباشرة (مثل `doAfterTextChanged { ... }`) أو واجهات أحادية الدالة (Functional Interfaces - `fun interface`)."
        ),
        "practical_walkthrough": (
            "المقارنة بين واجهة ضخمة تنتهك ISP وواجهات مجزأة دقيقة:\n"
            "```kotlin\n"
            "// ❌ انتهاك صارخ لـ ISP: واجهة ضخمة تجبر الكلاسات على تنفيذ دوال لا تحتاجها:\n"
            "interface UserManagementService {\n"
            "    fun readProfile(): User\n"
            "    fun updateProfile(user: User)\n"
            "    fun deleteAccount()\n"
            "    fun processSubscriptionPayment(amount: Long)\n"
            "}\n"
            "\n"
            "// شاشة العرض البسيطة تضطر للتعامل مع دوال الحذف والدفع الحساسة بلا داعٍ!\n"
            "class ReadOnlyProfileWidget(private val service: UserManagementService) { ... }\n"
            "\n"
            "// ✅ تطبيق ISP السليم: واجهات دقيقة مقسمة حسب الصلاحيات والاحتياج:\n"
            "fun interface UserProfileReader {\n"
            "    fun readProfile(): Flow<User>\n"
            "}\n"
            "\n"
            "interface UserProfileWriter {\n"
            "    suspend fun updateProfile(user: User)\n"
            "}\n"
            "\n"
            "interface AccountTerminator {\n"
            "    suspend fun deleteAccount()\n"
            "}\n"
            "\n"
            "// يمكن لكلاس الـ Repository في طبقة Data تنفيذ الواجهات الثلاث معاً، ولكن الـ Widget يستهلك Reader فقط:\n"
            "class ReadOnlyProfileWidget(private val reader: UserProfileReader) {\n"
            "    // آمن تماماً، ولا يعرف أي شيء عن الحذف أو الدفع!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Interface Segregation Principle states that clients should not be forced to depend on methods they do not use. In Android, rather than creating a bloated 20-method repository interface or implementing the cumbersome 3-method `TextWatcher`, we split contracts into fine-grained single-purpose interfaces like `UserProfileReader` and `UserProfileWriter`.",
        "best_answer": (
            "The Interface Segregation Principle (ISP) states that **no client should be forced to depend on methods it does not use**.\n\n"
            "When an interface becomes a 'fat interface' (accumulating dozens of methods across multiple feature areas), any change to an unrelated method forces recompilation and re-testing across all consumers. Furthermore, mock implementations in unit tests become bloated with empty stub methods.\n\n"
            "Classic Android examples of ISP violations include:\n"
            "- **`TextWatcher`**: Forces implementers to override `beforeTextChanged()`, `onTextChanged()`, and `afterTextChanged()` even if they only care about text changes. (Modern Android resolved this with `core-ktx` extension `doAfterTextChanged { ... }`).\n"
            "- **`Animator.AnimatorListener`**: Forces four method implementations (`onAnimationStart`, `End`, `Cancel`, `Repeat`) for a simple end callback.\n\n"
            "In modern architecture, we segregate data contracts based on consumer roles: splitting a monolithic `UserRepository` into `UserReader` and `UserWriter`. A read-only home widget injects only `UserReader`, ensuring it has zero visibility or coupling to sensitive account deletion or password change operations."
        ),
        "deep_answer": (
            "Kotlin provides exceptional language support for ISP via **Functional (SAM) Interfaces** (`fun interface`). "
            "A functional interface contains exactly one abstract method and can be implemented via a concise lambda: `val reader = UserProfileReader { flowOf(currentUser) }`. "
            "This makes mocking in unit tests practically instantaneous without heavy mocking libraries.\n\n"
            "ISP also protects security and modularization. "
            "In enterprise fintech applications, the payment SDK might implement `PaymentAuditor`, `PaymentExecutor`, and `PaymentConfigurator`. "
            "The standard checkout UI module is injected only with `PaymentExecutor`, while administrative modules receive `PaymentConfigurator`. "
            "This compiler-level segregation prevents feature developers from accidentally exposing administrative configurations."
        ),
        "follow_ups": [
            {
                "question": "How did Android KTX resolve ISP violations in legacy Android listeners?",
                "answer": "KTX introduced extension functions accepting single lambdas with default no-op parameters (e.g. `view.doAfterTextChanged { }`, `animator.doOnEnd { }`), freeing developers from overriding unused methods."
            },
            {
                "question": "Can a single concrete class implement multiple segregated interfaces?",
                "answer": "Yes. A single `UserRepositoryImpl` can implement both `UserReader` and `UserWriter`, while clients inject only the specific interface abstraction they require."
            }
        ]
    },
    {
        "id": "SOL-06",
        "arabic_explanation": (
            "شرح مبدأ عكس التبعية (Dependency Inversion Principle - DIP) مع مثال عملي واقعي في Android:\n\n"
            "1. تعريف مبدأ عكس التبعية (DIP):\n   - ينص المبدأ على قاعدتين أساسيتين:\n     * **القاعدة 1**: الوحدات عالية المستوى (High-level modules) يجب ألا تعتمد على الوحدات منخفضة المستوى (Low-level modules). كلاهما يجب أن يعتمد على التجريدات (Abstractions).\n     * **القاعدة 2**: التجريدات يجب ألا تعتمد على التفاصيل (Details)؛ التفاصيل هي التي يجب أن تعتمد على التجريدات.\n\n"
            "2. ما الذي ينتهك DIP في Android؟\n   - عندما يقوم كلاس `CheckoutViewModel` (High-level) بإنشاء أو استدعاء كلاس `RetrofitOrderApi` أو `RoomOrderDatabase` (Low-level infrastructure) مباشرة!\n   - أي تغيير في تفاصيل قاعدة البيانات أو السيرفر يجبرك على تغيير كود العرض والبيزنس عالي المستوى.\n\n"
            "3. كيف نطبق DIP في Android؟\n   - نقوم بإنشاء **Interface مجرد في طبقة الـ Domain** يسمى `OrderRepository`.\n   - الـ `CheckoutViewModel` يعتمد على الـ `OrderRepository` interface فقط.\n   - الـ `OrderRepositoryImpl` في طبقة الـ Data يعتمد على الـ `OrderRepository` interface وينفذه.\n   - محرك الـ DI (Hilt) يقوم بحقن الـ Implementation في وقت التشغيل."
        ),
        "practical_walkthrough": (
            "تطبيق مبدأ DIP في كود Kotlin في Android:\n"
            "```kotlin\n"
            "// ❌ انتهاك صارخ لـ DIP: High-level ViewModel يعتمد مباشرة على Low-level Retrofit Service:\n"
            "class BadOrderViewModel {\n"
            "    // ارتهان مباشر بتفاصيل البنية التحتية:\n"
            "    private val api = Retrofit.Builder().baseUrl(\"https://api.com\").build().create(OrderApi::class.java)\n"
            "}\n"
            "\n"
            "// ✅ تطبيق DIP السليم: كلاهما يعتمد على التجريد (Abstraction):\n"
            "// 1. التجريد (Abstraction) يعيش في الـ Domain:\n"
            "interface OrderRepository {\n"
            "    suspend fun submitOrder(order: Order): Result<OrderConfirmation>\n"
            "}\n"
            "\n"
            "// 2. High-level module (ViewModel) يعتمد على التجريد فقط:\n"
            "@HiltViewModel\n"
            "class GoodOrderViewModel @Inject constructor(\n"
            "    private val orderRepository: OrderRepository // اعتماد نقي على Interface\n"
            ") : ViewModel() { ... }\n"
            "\n"
            "// 3. Low-level module (Data layer) يعتمد على التجريد وينفذ تفاصيله:\n"
            "class OrderRepositoryImpl @Inject constructor(\n"
            "    private val api: OrderApi,\n"
            "    private val dao: OrderDao\n"
            ") : OrderRepository {\n"
            "    override suspend fun submitOrder(order: Order): Result<OrderConfirmation> { ... }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Dependency Inversion Principle dictates that high-level modules (business/UI) must not depend on low-level modules (networking/database); both must depend on abstractions. In Android, the Domain layer defines the `Repository` interface, and the Data layer implements it, inverting the source code dependency.",
        "best_answer": (
            "The Dependency Inversion Principle (DIP) establishes that **high-level policies should not depend on low-level details; both should depend on abstractions**.\n\n"
            "In procedural or coupled architectures, control and dependencies flow in the same direction: a ViewModel (high-level) directly instantiates a Database or Retrofit client (low-level). Consequently, if the database schema or network library changes, the high-level business code is forced to change.\n\n"
            "DIP inverts this relationship:\n"
            "1. The high-level layer (Domain/Presentation) defines the abstraction: `interface UserRepository`.\n"
            "2. The low-level infrastructure layer (Data) imports that interface and implements it: `class UserRepositoryImpl : UserRepository`.\n"
            "3. At compile time, the source code dependency points inward toward the high-level abstraction. At runtime, the Dependency Injection container (Hilt) resolves and injects the implementation.\n\n"
            "This insulates critical business rules: the network library can be swapped from Retrofit to Ktor without altering a single line of business logic."
        ),
        "deep_answer": (
            "DIP is the foundational mechanism that powers the **Dependency Rule in Clean Architecture**. "
            "Without DIP, Clean Architecture would be impossible because the core domain would be forced to depend on database drivers and network libraries to fetch data.\n\n"
            "In Gradle multi-module architecture, DIP is enforced via Gradle configuration:\n"
            "- `:core:domain` defines `interface AuthRepository`. It has zero dependencies on network or database modules.\n"
            "- `:core:data` has `implementation(project(\":core:domain\"))` and provides `AuthRepositoryImpl`.\n"
            "- The compile graph physically forbids `:core:domain` from accessing `:core:data`.\n\n"
            "This inversion enables 100% pure JVM unit testability: we can test `AuthUseCase` by passing an in-memory `FakeAuthRepository` without touching SQLite or mocking HTTP calls."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between DIP and Dependency Injection (DI)?",
                "answer": "DIP is an architectural design principle about the direction of code dependencies. DI is a practical creational design pattern/technique (used by Hilt/Koin) to provide instances of dependencies to a class at runtime."
            },
            {
                "question": "Where should the abstraction (interface) live according to DIP?",
                "answer": "In the higher-level module (Domain layer), alongside the client that consumes it, NOT in the low-level infrastructure module."
            }
        ]
    },
    {
        "id": "SOL-07",
        "arabic_explanation": (
            "المقارنة الجوهرية بين مبدأ عكس التبعية (DIP) وحقن التبعيات (Dependency Injection - DI):\n\n"
            "1. ما هو مبدأ عكس التبعية (DIP - Dependency Inversion Principle)؟\n   - هو **مبدأ تصميم معماري عالي المستوى (High-level Architectural Principle)**.\n   - يركز على: **اتجاه التبعيات (Direction of Dependencies)** وهيكلة العلاقات بين الطبقات.\n   - يقول: \"لا تجعل الكود العالي يعتمد على التفاصيل، بل اجعل كلاهما يعتمد على واجهات مجردة (Abstractions)\".\n\n"
            "2. ما هو حقن التبعيات (DI - Dependency Injection)؟\n   - هو **نمط تصميم عملي / أسلوب تنفيذي (Creational Design Pattern / Technique)**.\n   - يركز على: **كيفية تزويد الكائنات بالاعتماديات التي تحتاجها من الخارج بدلاً من إنشائها بنفسها بالداخل** (`new` أو instantiation).\n   - يتم تنفيذه برمجياً عبر Constructor Injection أو عبر أطر عمل مثل Hilt و Koin و Dagger.\n\n"
            "3. هل يمكن استخدام أحدهما دون الآخر؟\n   - **نعم!**:\n     * يمكنك استخدام DI بدون DIP: إذا قمت بحقن كلاس ملموس مباشر `class ViewModel(val api: RetrofitApi)`، فأنت استخدمت Dependency Injection، ولكنك انتهكت مبدأ DIP لأنك ارتهنت بكلاس منخفض المستوى دون أي تجريد!\n     * الـ DI هو الأداة التقنية التي تجعل تطبيق مبدأ DIP سهلاً وعملياً في أندرويد."
        ),
        "practical_walkthrough": (
            "توضيح الفرق بين DI بدون DIP و DI مع DIP:\n"
            "```kotlin\n"
            "// ❌ حقن تبعيات (DI) لكن بدون عكس التبعية (Violates DIP):\n"
            "// هنا استخدمنا Constructor Injection (DI)، لكن الـ ViewModel يعتمد على كلاس ملموس مباشر من طبقة الشبكة:\n"
            "class LoginViewModel @Inject constructor(\n"
            "    private val retrofitService: RetrofitLoginService // 💥 DI مطبق لكن DIP منتهك!\n"
            ") : ViewModel() { ... }\n"
            "\n"
            "// ✅ DI متناغم مع DIP بنسبة 100%:\n"
            "// 1. DIP: اعتماد على abstraction نقي في Domain:\n"
            "interface AuthRepository {\n"
            "    suspend fun login(creds: Credentials): Result<User>\n"
            "}\n"
            "\n"
            "// 2. DI + DIP: حقن الـ Abstraction في ViewModel وربط الـ Implementation عبر Hilt Module:\n"
            "@HiltViewModel\n"
            "class LoginViewModel @Inject constructor(\n"
            "    private val authRepository: AuthRepository // DIP مطبق بامتياز!\n"
            ") : ViewModel() { ... }\n"
            "\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "abstract class AuthModule {\n"
            "    @Binds\n"
            "    abstract fun bindAuthRepository(impl: AuthRepositoryImpl): AuthRepository // DI يقوم بتوصيل الأسلاك\n"
            "}\n"
            "```"
        ),
        "quick_answer": "DIP is an architectural principle stating that high-level modules should depend on abstractions rather than low-level details. DI is a creational pattern/technique of supplying dependencies from the outside (via constructor injection or Hilt). You can use DI without DIP by injecting concrete classes directly.",
        "best_answer": (
            "While frequently conflated, Dependency Inversion Principle (DIP) and Dependency Injection (DI) operate at fundamentally different architectural levels.\n\n"
            "1. **DIP (The Architectural Principle)**:\n"
            "   - Formulated as the 'D' in SOLID.\n   - Dictates **coupling direction**: high-level business policies must depend on abstractions (interfaces), and low-level detail implementations must depend on those same abstractions.\n   - It answers: *'How should my software layers be decoupled structurally?'*\n\n"
            "2. **DI (The Creational Technique / Pattern)**:\n"
            "   - A concrete implementation pattern (typically powered by frameworks like Hilt, Dagger, or Koin).\n   - Dictates **how dependencies are instantiated**: instead of a class instantiating its collaborators (`val repo = UserRepository()`), they are passed into its constructor from an external assembler.\n   - It answers: *'How does a class obtain references to its collaborators at runtime?'*\n\n"
            "Crucially, **using DI does not automatically satisfy DIP**. Injecting a concrete `RetrofitApi` into a `ViewModel` uses Dependency Injection, but severely violates the Dependency Inversion Principle because the high-level ViewModel remains tightly coupled to low-level networking details."
        ),
        "deep_answer": (
            "Under the hood, DI acts as the practical enabler of DIP. "
            "When you apply DIP, a class depends on an abstract interface (`UserRepository`). "
            "However, at runtime, a concrete instance (`UserRepositoryImpl`) must actually be created and passed to that class. "
            "Without DI, the class or its caller would have to manually call `UserRepositoryImpl()`, resurrecting the compile-time coupling DIP was designed to eliminate.\n\n"
            "Dagger/Hilt resolves this using **`@Binds`**: it maintains a compile-time dependency graph that maps the Domain abstraction `UserRepository` to the Data implementation `UserRepositoryImpl`, injecting it seamlessly.\n\n"
            "In unit testing, DI allows passing an in-memory `FakeUserRepository` without any DI framework, making tests fast and deterministic."
        ),
        "follow_ups": [
            {
                "question": "Can you have DIP without a DI framework like Hilt?",
                "answer": "Yes. You can invert dependencies using pure interfaces and wire them up manually using manual dependency injection (pure Constructor Injection in Application class) without any third-party framework."
            },
            {
                "question": "What is the `@Binds` annotation in Hilt/Dagger, and how does it relate to DIP?",
                "answer": "`@Binds` tells Hilt which concrete implementation class to provide when an abstract interface is requested, directly wiring DIP abstractions at compile time without generating extra factory code."
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

    for item in SOL_01_07:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions SOL-01 to SOL-07. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
