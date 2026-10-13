#!/usr/bin/env python3
"""Generator for SOL-15 through SOL-20 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "sol.json"

SOL_15_20 = [
    {
        "id": "SOL-15",
        "arabic_explanation": (
            "كيف تقوم بتقسيم واجهة ضخمة (Fat Interface) تحتوي على دوال كثيرة غير مستخدمة؟ وما هي الخطوات العملية؟\n\n"
            "1. تشخيص الواجهة المتضخمة (Fat Interface Diagnosis):\n   - واجهة مثل `interface MediaPlaybackListener` فيها 12 دالة (play, pause, stop, seek, buffer, volumeChanged, trackChanged, error, metadataLoaded, subtitleAvailable, bitrateChanged, qualityDropped).\n   - معظم الشاشات المستهلكة (Clients) تحتاج فقط لمعرفة `onPlaybackStateChanged` و `onError`، وتضطر لتنفيذ باقي الدوال كـ No-op فارغة!\n\n"
            "2. استراتيجية التقسيم بناءً على أدوار العملاء (Role-Based Segregation):\n   - تطبيق مبدأ **ISP (Interface Segregation Principle)**: تجميع الدوال بناءً على من يستخدمها وكيف تتغير معاً:\n     * `interface PlaybackStateListener` (للتشغيل والإيقاف المؤقت).\n     * `interface MediaTrackListener` (للترجمات والمسارات الصوتية).\n     * `interface PlaybackMetricsListener` (للتحليلات والـ Bitrate).\n\n"
            "3. استخدام ميزات Kotlin الحديثة:\n   - توفير **Default Implementations** في الـ Interface: `fun onBuffering() {}` بحيث لا يجبر المستدعي على كتابتها.\n   - استخدام **SAM / Functional Interfaces** (`fun interface`) والـ Extension functions مع Lambdas (مثل `player.onPlayStateChange { ... }`)."
        ),
        "practical_walkthrough": (
            "تقسيم واجهة تشغيل وسائط ضخمة إلى واجهات متخصصة:\n"
            "```kotlin\n"
            "// ❌ واجهة ضخمة تجبر كل الشاشات على تنفيذ 6 دوال معظمها غير مستخدم:\n"
            "interface FatAudioListener {\n"
            "    fun onPlay()\n"
            "    fun onPause()\n"
            "    fun onTrackChanged(track: String)\n"
            "    fun onVolumeChanged(volume: Float)\n"
            "    fun onBitrateDrop(bitrate: Int)\n"
            "    fun onError(error: String)\n"
            "}\n"
            "\n"
            "// ✅ تقسيمها حسب الأدوار وحاجة العملاء (ISP):\n"
            "fun interface PlaybackStateListener {\n"
            "    fun onStateChanged(isPlaying: Boolean)\n"
            "}\n"
            "\n"
            "fun interface TrackChangeListener {\n"
            "    fun onTrackChanged(track: String)\n"
            "}\n"
            "\n"
            "fun interface MediaErrorListener {\n"
            "    fun onError(error: String)\n"
            "}\n"
            "\n"
            "// في المشغل: دعم تسجيل المستمعين المتخصصين بشكل منفصل وبسيط عبر Lambdas:\n"
            "class AudioPlayer {\n"
            "    fun addStateListener(listener: PlaybackStateListener) { ... }\n"
            "    fun addErrorListener(listener: MediaErrorListener) { ... }\n"
            "}\n"
            "\n"
            "// شاشة العرض البسيطة تسجل فقط ما تحتاجه بضغطة واحدة:\n"
            "player.addStateListener { isPlaying -> updatePlayButtonIcon(isPlaying) }\n"
            "```"
        ),
        "quick_answer": "Split a large interface by analyzing client call sites, grouping methods by cohesion and consumer role into smaller functional interfaces (`PlaybackStateListener`, `MediaErrorListener`), providing interface default method implementations, and utilizing Kotlin SAM lambdas.",
        "best_answer": (
            "Splitting a bloated 'Fat Interface' requires role-based refactoring governed by the Interface Segregation Principle (ISP).\n\n"
            "1. **Audit Call Sites and Consumer Personas**: Analyze every client implementing the interface. Identify distinct clusters of methods that are invoked together by specific consumers. For example, in a massive `MediaController` interface, the UI widget only cares about play/pause, the metadata notification only cares about track titles, and the analytics telemetry service only cares about buffer underruns and bitrates.\n\n"
            "2. **Extract Role Interfaces**: Deconstruct the interface into cohesive, fine-grained contracts:\n"
            "   - `PlaybackStateListener`: `onPlay()`, `onPause()`\n   - `TrackMetadataListener`: `onTrackChanged()`\n   - `StreamingQualityListener`: `onBitrateDrop()`, `onBufferStall()`\n\n"
            "3. **Leverage Kotlin SAM & Default Implementations**:\n   - Convert single-method contracts into `fun interface` (Single Abstract Method), allowing callers to pass simple trailing lambdas.\n   - Provide default no-op method bodies (`fun onBuffering() {}`) in interfaces for truly optional callbacks, preventing implementers from writing redundant stub methods."
        ),
        "deep_answer": (
            "To migrate safely without breaking existing production consumers, apply the **Adapter or Composite Interface pattern** during refactoring. "
            "Declare the new segregated interfaces first. "
            "Then, define the legacy interface as a composite that inherits the new interfaces: `interface LegacyMediaListener : PlaybackStateListener, TrackMetadataListener`. "
            "Mark the legacy interface `@Deprecated(message = \"Use specific segregated listeners\")`.\n\n"
            "Existing legacy code continues compiling without modification, while all new feature developments adopt the fine-grained role interfaces.\n\n"
            "In unit testing, this reduces mocking boilerplate exponentially: testing a play button requires passing a 1-line lambda rather than a 15-method mock instance."
        ),
        "follow_ups": [
            {
                "question": "What is a SAM (Single Abstract Method) interface in Kotlin?",
                "answer": "An interface declared as `fun interface` containing exactly one abstract method. In Kotlin, callers can implement it concisely using a standard lambda expression without anonymous class boilerplate."
            },
            {
                "question": "How do interface default methods prevent breaking changes?",
                "answer": "In Kotlin and Java 8+, adding a method with a default implementation to an existing interface does not force existing implementers to override it, preventing compile-time breakages."
            }
        ]
    },
    {
        "id": "SOL-16",
        "arabic_explanation": (
            "كيف تحدد وتكتشف المسؤوليات المتماسكة (Cohesive Responsibilities) داخل كلاس متضخم (God Class)؟\n\n"
            "1. ما هو الـ God Class في Android؟\n   - كلاس ضخم (1,500 إلى 3,000 سطر) يسيطر على كل شيء؛ يقرأ الحساسات، ويطلب الشبكة، ويعدل قاعدة البيانات، وينسق الرسوم، ويتعامل مع الأذونات (مثل كلاس `OrderManager` أو `MainActivity`).\n\n"
            "2. المنهجية العلمية لتحديد المسؤوليات المتماسكة داخل الكلاس:\n   - **فحص استخدام المتغيرات المشتركة (LCOM - Lack of Cohesion of Methods)**:\n     * انظر إلى خصائص الكلاس (Fields): ستجد مجموعة دوال (A, B, C) تستخدم فقط `LocationManager` و `gpsCoordinates`.\n     * ومجموعة أخرى (D, E, F) تستخدم فقط `RetrofitOrderApi` و `authToken`.\n     * ومجموعة ثالثة تستخدم فقط `Dialog` و `Toast`.\n     * هذه المجموعات المنفصلة هي كلاسات جديدة تنادي عليك لاستخراجها فوراً!\n   - **فحص أصحاب المصلحة (Stakeholders / Business Actors)**:\n     * اسأل نفسك: من يطلب تعديل هذا الجزء؟ هل هو فريق الـ UI؟ أم فريق الـ Backend؟ أم فريق الأمان؟\n   - **فحص التسميات (Naming Smells)**: الدوال التي تبدأ بـ `calculate...`, `validate...`, `format...` غالباً ما تكون وظائف Domain يجب فصلها عن وظائف التخزين `save...` و `fetch...`."
        ),
        "practical_walkthrough": (
            "تحليل وتفكيك God Class إلى مكونات متماسكة:\n"
            "```kotlin\n"
            "// ❌ God Class يجمع حقولاً غير متجانسة إطلاقاً:\n"
            "class MonolithicCartManager {\n"
            "    // Cluster 1: موقع جغرافي لحساب التوصيل\n"
            "    var userLat: Double = 0.0\n"
            "    var userLng: Double = 0.0\n"
            "    fun updateGpsLocation() { ... }\n"
            "\n"
            "    // Cluster 2: حسابات الضرائب والخصومات (Domain Rules)\n"
            "    fun applyDiscountCoupon(code: String) { ... }\n"
            "    fun calculateVatTax(subtotal: Long): Long { ... }\n"
            "\n"
            "    // Cluster 3: التخزين وقاعدة البيانات (Data Storage)\n"
            "    fun persistCartToDatabase() { ... }\n"
            "    fun syncWithBackendApi() { ... }\n"
            "}\n"
            "\n"
            "// ✅ التفكيك إلى كلاسات عالية التماسك (High Cohesion):\n"
            "// 1. DeliveryLocationProvider (مسؤول عن الموقع فقط)\n"
            "class DeliveryLocationProvider { ... }\n"
            "\n"
            "// 2. CartPricingEngine (مسؤول عن حسابات الضرائب والخصومات في Domain)\n"
            "class CartPricingEngine { ... }\n"
            "\n"
            "// 3. CartRepository (مسؤول عن حفظ البيانات ومزامنة السيرفر في Data)\n"
            "class CartRepository { ... }\n"
            "```"
        ),
        "quick_answer": "Identify cohesive responsibilities in a God Class by analyzing field-method clustering (identifying groups of methods that operate on isolated subsets of class variables), grouping methods by the business actors requesting changes, and isolating orthogonal concerns like validation, storage, and UI into dedicated classes.",
        "best_answer": (
            "Dismantling a God Class requires an objective, metric-driven analysis of internal cohesion rather than subjective guesswork.\n\n"
            "1. **Variable-Method Clustering (LCOM - Lack of Cohesion of Methods)**:\n   - Map out the class fields and observe which methods access which properties.\n   - In a God Class, methods naturally form isolated clusters: Methods A, B, and C only read and write location coordinates; Methods D and E only touch the network client; Methods F and G only manipulate formatting and UI dialogs.\n   - Each distinct cluster represents a distinct cohesive class waiting to be extracted.\n\n"
            "2. **Actor Alignment (Single Reason to Change)**:\n   - Group methods by the business stakeholder who commands their changes:\n     * Methods requested by UI designers belong in the Presentation/UI layer.\n     * Methods requested by accountants or product rules (tax rules, loyalty points) belong in Domain Use Cases.\n     * Methods requested by infrastructure or backend changes belong in the Data Repository.\n\n"
            "3. **Linguistic Clustering (Naming & Verb Analysis)**:\n   - Look for method prefixes: `validate*()` indicates a Validator, `format*()` indicates a Mapper/Formatter, `sync*()` or `save*()` indicates a Repository."
        ),
        "deep_answer": (
            "Static analysis tools (like SonarQube, Detekt, or Konsist) formalize this process. "
            "Detekt flags classes violating `ComplexInterface`, `LargeClass` (e.g. >600 LOC), or `TooManyFunctions` (>15 methods). "
            "When these metrics trigger, we run an automated dependency structure matrix (DSM) in IntelliJ/Android Studio to visualize coupling blocks.\n\n"
            "Once clusters are identified, refactor using the **Extract Class refactoring technique**:\n"
            "- Step 1: Create the new focused class (`DeliveryCalculator`).\n"
            "- Step 2: Delegate the God Class's methods to an instance of the new class.\n"
            "- Step 3: Update client callers to inject the new class directly, gradually strangling the legacy God Class."
        ),
        "follow_ups": [
            {
                "question": "What is LCOM (Lack of Cohesion of Methods)?",
                "answer": "A software metric that measures the disparity between methods and fields in a class. High LCOM indicates low cohesion, proving that a class is doing too many unrelated things and should be split."
            },
            {
                "question": "How do God Classes negatively affect team velocity and Git workflows?",
                "answer": "Multiple developers working on different features simultaneously edit the same massive file, creating frequent and painful merge conflicts, broken builds, and duplicated regression testing."
            }
        ]
    },
    {
        "id": "SOL-17",
        "arabic_explanation": (
            "عندما يضطر كلاس فرعي (Subclass) لرمي `UnsupportedOperationException` لتجاهل سلوك مفروض عليه من الكلاس الأساسي: ما هو المبدأ الذي تم انتهاكه؟ وكيف يُعالج؟\n\n"
            "1. المبدأ المنتهك حتماً: مبدأ لسكوف للاستبدال (Liskov Substitution Principle - LSP):\n   - رمي `UnsupportedOperationException` هو الدليل القاطع والجريمة المشهودة على انتهاك **LSP**!\n   - الكلاس الأساسي (Superclass) قطع وعداً بأن هذه العملية مدعومة ومتاحة. عندما يقوم الكلاس الفرعي بنقض هذا الوعد ورمي استثناء، فإنه **يضعف الشروط اللاحقة (Weakens Postconditions)** ويفشل في العمل كبديل صالح لكلاسه الأساسي.\n\n"
            "2. ما هي الآثار الجانبية لهذا الانتهاك؟\n   - انهيار البرنامج في وقت التشغيل (Runtime Crashes)؛ الكود المستدعي الذي يتعامل مع الكلاس الأساسي لا يتوقع هذا الاستثناء، مما يفجر أخطاء غير معالجة.\n   - إجبار الكود الخارجي على عمل `if (instance is SpecificSubclass)` قبل الاستدعاء، مما يكسر مبدأ Polymorphism تماماً!\n\n"
            "3. كيف يُعالج هندسياً؟\n   - **إزالة السلوك من الكلاس الأساسي**: الكلاس الأساسي يجب أن يحتوي فقط على القاسم المشترك الأعظم (Greatest Common Divisor) للسلوكيات الحقيقية لجميع الأبناء دون استثناء.\n   - **استبدال الوراثة بالتركيب (Composition)**: فصل السلوك غير المشترك في واجهة مستقلة (Capability Interface) أو Delegate خارجي."
        ),
        "practical_walkthrough": (
            "تصحيح انتهاك LSP الذي يرمي UnsupportedOperationException:\n"
            "```kotlin\n"
            "// ❌ انتهاك صارخ لـ LSP: طائر لا يستطيع الطيران يرمي استثناء في دالة موروثة!\n"
            "open class Bird {\n"
            "    open fun fly(): Altitude = Altitude(1000)\n"
            "}\n"
            "\n"
            "class Penguin : Bird() {\n"
            "    override fun fly(): Altitude {\n"
            "        // 💥 يكسر LSP: المستدعي يتوقع طيراناً، والبطريق يرمي Crash!\n"
            "        throw UnsupportedOperationException(\"Penguins cannot fly!\")\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الحل المعماري السليم: تقسيم الشجرة أو استخدام Composition:\n"
            "open class Bird // طائر عام (يأكل، ينام، يتكاثر)\n"
            "\n"
            "interface Flyable {\n"
            "    fun fly(): Altitude\n"
            "}\n"
            "\n"
            "class Eagle : Bird(), Flyable {\n"
            "    override fun fly(): Altitude = Altitude(2000)\n"
            "}\n"
            "\n"
            "class Penguin : Bird() {\n"
            "    // لا ينفذ Flyable؛ الكود الذي يبحث عن طيران لن يستدعيه، ولن يحدث أي استثناء!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "The Liskov Substitution Principle (LSP) is violated. Subclasses must be substitutable for their superclass without breaking behavioral contracts. Throwing `UnsupportedOperationException` breaks caller expectations. Fix it by removing the unsupported behavior from the base class and extracting it into a separate interface or composable delegate.",
        "best_answer": (
            "Throwing `UnsupportedOperationException` from an overridden subclass method is the textbook signature of a **Liskov Substitution Principle (LSP)** violation.\n\n"
            "When a superclass declares a public method, it establishes an explicit behavioral contract with calling code: *'Any instance of this type or its subtypes can execute this operation and will return a valid result without throwing unexpected state errors.'*\n\n"
            "When a subclass overrides that method with `throw UnsupportedOperationException()`, it violates this contract:\n"
            "1. It is no longer substitutable for its parent type.\n"
            "2. Any generic polymorphic collection processing instances of the superclass (`birds.forEach { it.fly() }`) crashes at runtime upon reaching this subtype.\n"
            "3. It forces calling code to write defensive `if (item !is Penguin)` type checks, which recursively violates the Open/Closed Principle (OCP).\n\n"
            "**The Architectural Resolution**:\n"
            "- Prune the method from the superclass hierarchy.\n"
            "- Segregate optional capabilities into dedicated interfaces (`Flyable`, `Editable`, `Shareable`).\n"
            "- Use **Composition over Inheritance**: rather than inheriting a base class with unwanted baggage, inject only the specific behaviors required."
        ),
        "deep_answer": (
            "In Android architecture, this appears in repositories and storage implementations. "
            "Suppose a base `interface CacheStorage<T>` declares `read()`, `write()`, and `clear()`. "
            "A read-only `AssetStorage` implementation backed by the APK's read-only assets directory throws `UnsupportedOperationException(\"Cannot write to APK assets\")` inside `write()`.\n\n"
            "The resolution requires applying ISP and LSP together: split the contract into `ReadableStorage<T>` and `WritableStorage<T>`. "
            "`AssetStorage` implements only `ReadableStorage`, ensuring that clients requiring write operations can never accidentally be passed an un-writable storage instance at compile time."
        ),
        "follow_ups": [
            {
                "question": "How does throwing UnsupportedOperationException force calling code to violate OCP?",
                "answer": "Callers are forced to add `if (item is SpecificClass)` checks to skip the unsupported operation. Every time a new non-supporting subclass is created, callers must be modified with new `if/else` checks, violating OCP."
            },
            {
                "question": "Can Java's Collections API be criticized for this exact LSP violation?",
                "answer": "Yes! `java.util.Collections.unmodifiableList()` returns a `List` whose `add()` method throws `UnsupportedOperationException`, which is a famous language-level violation of LSP in the standard Java library."
            }
        ]
    },
    {
        "id": "SOL-18",
        "arabic_explanation": (
            "عندما يتطلب إضافة مزود دفع جديد (New Payment Provider) تعديل 10 كلاسات موجودة مسبقاً في التطبيق: ما هي المبادئ الهندسية التي تعالج ذلك؟\n\n"
            "1. المبادئ الهندسية المنتهكة والتي يجب تطبيقها:\n   - **المبدأ الأول: مبدأ الفتح والإغلاق (OCP - Open/Closed Principle)**:\n     * وجود الحاجة لتعديل 10 كلاسات يعني أن الكود **مغلق للتوسيع ومفتوح للتعديل** (عكس OCP تماماً!).\n     * الحل: تحويل نظام الدفع إلى **Strategy Pattern** حيث يتم تعريف واجهة `PaymentProvider`، وإضافة أي مزود جديد تعني فقط إنشاء كلاس جديد دون لمس الكلاسات القديمة.\n   - **المبدأ الثاني: مبدأ المسؤولية الواحدة (SRP - Single Responsibility Principle)**:\n     * تشتت منطق الدفع عبر 10 كلاسات يعني غياب التماسك وتشتت المسؤوليات؛ كلاسات الـ UI والـ Navigation وقواعد البيانات تفحص نوع الدفع بنفسها!\n     * الحل: تركيز كل ما يخص الدفع داخل `PaymentRepository` و `PaymentRouter` واحد.\n   - **المبدأ الثالث: مبدأ عكس التبعية (DIP - Dependency Inversion Principle)**:\n     * الكلاسات الـ 10 تعتمد على كلاسات ملموسة لمزودي الدفع السابقين بدلاً من الاعتماد على تجريد موحد.\n\n"
            "2. النتيجة بعد تطبيق المبادئ:\n   - إضافة المزود رقم 11 ستتطلب إنشاء **ملف واحد جديد فقط** وتسجيله في الـ DI دون المساس بأي من الكلاسات الـ 10!"
        ),
        "practical_walkthrough": (
            "إعادة هندسة تدفق الدفع ليكون محكوماً بـ OCP و Strategy Pattern:\n"
            "```kotlin\n"
            "// ❌ الكود المكسور القديم: إضافة مزود جديد تجبرك على فتح 10 كلاسات وتعديل when(type):\n"
            "// 1. CheckoutViewModel.kt -> when(type)\n"
            "// 2. PaymentValidator.kt -> when(type)\n"
            "// 3. ReceiptFormatter.kt -> when(type)\n"
            "// 4. AnalyticsTracker.kt -> when(type)...\n"
            "\n"
            "// ✅ الحل المعماري المحكم: دمج المسؤوليات في Strategy Component متكاملة:\n"
            "interface PaymentGateway {\n"
            "    val methodId: PaymentMethodId\n"
            "    fun validate(details: PaymentDetails): Boolean\n"
            "    suspend fun executePayment(amount: Long, details: PaymentDetails): PaymentResult\n"
            "    fun formatReceipt(result: PaymentResult): ReceiptUiModel\n"
            "}\n"
            "\n"
            "// إضافة مزود جديد (مثل Fawry أو ApplePay) يتطلب ملفاً واحداً فقط يجمع كل تفاصيله:\n"
            "class FawryPaymentGateway @Inject constructor(...) : PaymentGateway {\n"
            "    override val methodId = PaymentMethodId.FAWRY\n"
            "    override fun validate(details: PaymentDetails) = ...\n"
            "    override suspend fun executePayment(amount: Long, details: PaymentDetails) = ...\n"
            "    override fun formatReceipt(result: PaymentResult) = ...\n"
            "}\n"
            "\n"
            "// الـ Router يستقبل Set<PaymentGateway> عبر Hilt؛ لا تعديل في أي كلاس قديم!\n"
            "class PaymentRouter @Inject constructor(private val gateways: Set<PaymentGateway>) { ... }\n"
            "```"
        ),
        "quick_answer": "The primary principle to apply is Open/Closed Principle (OCP) using the Strategy Pattern and Polymorphism, supported by Single Responsibility Principle (SRP) to stop spreading payment logic across disparate classes, and Dependency Inversion Principle (DIP) to decouple orchestrators from concrete provider SDKs.",
        "best_answer": (
            "If integrating a single new payment provider requires editing 10 existing classes across your application, the codebase is suffering from severe **shotgun surgery** caused by violating core SOLID principles.\n\n"
            "1. **Open/Closed Principle (OCP) - The Primary Cure**:\n   - The 10 classes are littered with type checks (`when (paymentType)` or `if (type == \"STRIPE\")`).\n   - **The Fix**: Abstract provider behavior behind a cohesive `PaymentGateway` interface (The Strategy Pattern). The payment orchestrator dynamically delegates to an injected collection (`Set<PaymentGateway>`), closing existing classes to modification.\n\n"
            "2. **Single Responsibility Principle (SRP)**:\n   - Payment details (validation, fee calculation, API invocation, receipt rendering) are smeared across 10 unrelated classes (Activities, ViewModels, Analytics, Storage).\n   - **The Fix**: Encapsulate all provider-specific behaviors inside the concrete `PaymentGateway` implementation. A new provider now requires authoring **exactly one new class**.\n\n"
            "3. **Dependency Inversion Principle (DIP)**:\n   - Consumers depend directly on concrete third-party payment SDKs (Stripe SDK, PayPal SDK) rather than an internal domain abstraction.\n   - **The Fix**: The domain layer defines the payment abstraction, and adapters in the data layer isolate third-party SDK dependencies."
        ),
        "deep_answer": (
            "In software metrics, this code smell is called **Shotgun Surgery** (a single conceptual change requires making lots of little edits to many different classes), which is the exact polar opposite of **Divergent Change** (one class is commonly changed in different ways for different reasons).\n\n"
            "Shotgun surgery introduces high regression risk: if an engineer forgets to update class #9 or #10, the bug only surfaces in production under specific edge cases.\n\n"
            "By encapsulating the provider behind a Strategy interface and leveraging Dagger Multibindings (`@IntoSet`), adding a new provider becomes an **additive-only change**: create `GooglePayGateway.kt`, bind it in Hilt, and create its dedicated unit test. Zero existing classes are touched, zero merge conflicts occur, and existing payment flows remain completely safe."
        ),
        "follow_ups": [
            {
                "question": "What is 'Shotgun Surgery' in code smell taxonomy?",
                "answer": "A code smell where a single conceptual modification requires making many small changes to multiple classes across the codebase, indicating poor encapsulation and OCP violations."
            },
            {
                "question": "How do you verify in CI that OCP is respected for new payment providers?",
                "answer": "By inspecting Git diffs in pull requests: adding a new payment feature should only add new files (additions) without modifying existing payment routing files (zero modifications to existing lines)."
            }
        ]
    },
    {
        "id": "SOL-19",
        "arabic_explanation": (
            "متى يجب عليك قبول قليل من التكرار (Duplication) عمداً بدلاً من التسرع في بناء تجريد غير ناضج (Premature Abstraction)؟\n\n"
            "1. حكمة ساندي ميتز الشهيرة (Sandi Metz's Law):\n   - **\"التكرار المؤقت أرخص بكثير من التجريد الخاطئ (Duplication is far cheaper than the wrong abstraction)\"**.\n   - التسرع في دمج كودين يتشابهان شكلياً في كلاس تجريدي واحد (DRY Dogmatism) يؤدي إلى كوارث معمارية عندما يبدأ الكودان في التطور باتجاهات مختلفة.\n\n"
            "2. التكرار العرضي (Accidental Duplication) مقابل التكرار الحقيقي (True Duplication):\n   - **التكرار الحقيقي (True Duplication)**: كودان يمثلان نفس قاعدة البيزنس الحقيقية ويخدمان نفس الهدف (مثل دالة حساب ضريبة القيمة المضافة لطلبات الشراء)؛ هنا يجب توحيدهما فوراً.\n   - **التكرار العرضي (Accidental Duplication)**: شاشتان (شاشة المنتجات وشاشة المستخدمين) تحتوي كل منهما على دالة لعرض بطاقة مستطيلة بداخلها صورة ونص؛ هذا مجرد تشابه بصري عارض (Accidental similarity) وليس بيزنس موحد! إذا قمت بدمجهما في كائن تجريدي واحد، فبمجرد أن يطلب مصمم الـ UI تعديل شاشة المستخدم، ستضطر لوضع شروط `if (isUser)` داخل التجريد، حتى يتحول إلى وحش مليء بالاستثناءات!\n\n"
            "3. متى تقبل التكرار عمداً؟\n   - في بداية بناء ميزة جديدة قبل وضوح اتجاه تطورها.\n   - بين موديولات الـ Feature المستقلة لحمايتها من الاقتران غير المبرر (Loose Coupling between modules).\n   - حتى تطبق قاعدة الثلاثة (Rule of Three): لا تجرد إلا عندما ترى التكرار لثالث مرة بوضوح تام."
        ),
        "practical_walkthrough": (
            "المقارنة بين التجريد الخاطئ وقبول التكرار العرضي لسلامة الكود:\n"
            "```kotlin\n"
            "// ❌ تجريد خاطئ كارثي: دمج كارتين مختلفين في تجريد واحد بسبب تشابه عارض:\n"
            "// شاشة الكتالوج وشاشة البروفايل كانتا متشابهتين، فقام المطور بدمجهما:\n"
            "@Composable\n"
            "fun FrankensteinGenericCard(item: Any, isUser: Boolean, showBadge: Boolean) {\n"
            "    // 💥 كود مليء بشروط if/else ومقترن بكيانين لا علاقة لهما ببعض!\n"
            "    if (isUser) UserSpecificLayout(item as User) else ProductLayout(item as Product)\n"
            "}\n"
            "\n"
            "// ✅ قبول قليل من التكرار العرضي للحفاظ على الاستقلالية التامة والتطور النظيف:\n"
            "@Composable\n"
            "fun ProductCard(product: Product) {\n"
            "    // كارت منتج مستقل يتطور مع متطلبات التجارة الإلكترونية\n"
            "    Text(product.name)\n"
            "}\n"
            "\n"
            "@Composable\n"
            "fun UserAvatarCard(user: User) {\n"
            "    // كارت بروفايل مستقل يتطور مع متطلبات الحسابات دون المساس بالمنتجات\n"
            "    Text(user.displayName)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Deliberately accept slight duplication when code looks syntactically similar but represents distinct business concepts evolving for different actors (accidental duplication), or across feature module boundaries to avoid tight coupling. Sandi Metz's rule applies: 'Duplication is far cheaper than the wrong abstraction.'",
        "best_answer": (
            "Software engineering maturity is recognizing that **premature abstraction is far more dangerous than temporary duplication**.\n\n"
            "As phrased by Sandi Metz: *'Duplication is far cheaper than the wrong abstraction.'* When engineers dogmatically enforce DRY (Don't Repeat Yourself) at the syntax level, they frequently merge two pieces of code that look identical today but evolve for completely different reasons tomorrow.\n\n"
            "**When to Deliberately Accept Duplication**:\n"
            "1. **Accidental Duplication vs True Duplication**: If two mapping routines in `:feature:catalog` and `:feature:profile` look identical, but one responds to catalog marketing needs and the other responds to user account settings, the duplication is accidental. Unifying them creates an artificial coupling between two unrelated business domains.\n\n"
            "2. **Feature Module Boundaries**: In multi-module architectures, forcing two independent feature modules to share an abstraction just to eliminate 15 lines of UI formatting creates a shared compile-time dependency, slowing builds and creating merge friction. Duplicating those 15 lines preserves independent module deployability.\n\n"
            "3. **Early Stage / Exploratory Features**: When a feature is brand-new, requirements mutate rapidly. Prematurely creating a rigid generic base class forces engineers to add boolean parameter flags (`isCaseB = true`) until the abstraction becomes an unmaintainable monster."
        ),
        "deep_answer": (
            "The life cycle of the **Wrong Abstraction** follows a predictable, destructive pattern:\n"
            "1. Developer A sees two similar routines and unifies them into `GenericHelper`.\n"
            "2. Feature requirements diverge. Developer B needs a slight difference, so they add an `if (flag)` parameter.\n"
            "3. Developer C needs another variation, adding another flag.\n"
            "4. A year later, `GenericHelper` takes 8 boolean flags, has 20 conditional branches, and nobody dares touch it.\n\n"
            "We adhere strictly to the **Rule of Three**: allow duplication to happen twice. "
            "Only when the exact same pattern recurs a third time across stable, mature requirements do we extract an abstraction, because by the third time, the true invariant shape of the abstraction is obvious."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between Accidental Duplication and Essential Duplication?",
                "answer": "Essential duplication occurs when multiple places implement the exact same business rule (e.g. tax formula) that must change together. Accidental duplication occurs when two components have similar syntax or layout purely by coincidence."
            },
            {
                "question": "How does accepting slight duplication help multi-module compile times?",
                "answer": "It avoids creating unnecessary shared modules. When feature modules share no unnecessary common dependencies, Gradle can compile and test them concurrently in parallel."
            }
        ]
    },
    {
        "id": "SOL-20",
        "arabic_explanation": (
            "كيف تشرح توازنات ومقايضات SOLID (SOLID Trade-offs) لفريق يقوم بهندسة مفرطة (Overengineering) لميزة صغيرة وبسيطة؟\n\n"
            "1. الفهم السليم لمبادئ SOLID (Principles, not Dogma):\n   - مبادئ SOLID هي **أدوات إرشادية لحل مشاكل التعقيد والاقتران**، وليست قوانين دينية مقدسة يجب تطبيقها بحذافيرها على كل سطر كود!\n   - التجريد (Abstraction) له تكلفة حقيقية: زيادة عدد الملفات، تعقيد التصفح، زيادة وقت الـ Build، وبطء وتيرة الإنجاز (Velocity Loss).\n\n"
            "2. خطة الحوار والإقناع في الفريق (Engineering Coaching):\n   - **البدء بالقيمة التجارية (Business Value & Time-to-Market)**: تذكير الفريق أن الهدف الأساسي هو تقديم قيمة للمستخدم وليس إرضاء الـ Design Patterns. تطبيق 5 طبقات لميزة قراءة نص بسيط يؤخر طرح الميزة أسبوعين بلا أي مبرر!\n   - **التذكير بمبدأ YAGNI و KISS**:\n     * **YAGNI (You Aren't Gonna Need It)**: لا تبنِ نظام استراتيجيات معقد لاحتمال نظري قد يحدث بعد سنتين.\n     * **KISS (Keep It Simple, Stupid)**: أبسط كود يعمل ويفي بالشروط هو الكود الأفضل.\n   - **إيضاح سهولة التعديل المستقبلي (Evolutionary Architecture)**:\n     * الكود البسيط سهل القراءة يمكن إعادة هيكلته (Refactored) في ساعتين عندما يظهر التعقيد الحقيقي، بينما الكود المفرط في التجريد (Over-abstracted) يستحيل فك تشابكه!\n\n"
            "3. وضع معيار عملي متفق عليه (Team Rule):\n   - ابدأ بـ Simple MVVM مباشرة: ViewModel + Repository.\n   - استخرج UseCase أو Interface فقط عندما يتكرر الكود في مكانين مختلفين، أو تظهر قواعد بيزنس معقدة تتطلب اختبارات خاصة."
        ),
        "practical_walkthrough": (
            "توجيه الفريق لتبسيط ميزة بسيطة تم الإفراط في هندستها:\n"
            "```kotlin\n"
            "// ❌ ما كتبه الفريق (Overengineered): 6 ملفات لعرض جملة ترحيبية:\n"
            "// GreetingDto -> GreetingEntity -> GreetingDomain -> GreetingUiModel\n"
            "// interface IGreetingRepository -> GreetingRepositoryImpl\n"
            "// interface IFetchGreetingUseCase -> FetchGreetingUseCaseImpl\n"
            "// GreetingViewModel -> GreetingScreen\n"
            "\n"
            "// ✅ ما يجب التوجيه إليه (Pragmatic & Clean): ملفان يؤديان الغرض بامتياز:\n"
            "class GreetingRepository(private val api: GreetingApi) {\n"
            "    suspend fun getGreeting(): String = api.fetch().message\n"
            "}\n"
            "\n"
            "@HiltViewModel\n"
            "class GreetingViewModel @Inject constructor(\n"
            "    private val repository: GreetingRepository\n"
            ") : ViewModel() {\n"
            "    val greeting = flow { emit(repository.getGreeting()) }\n"
            "        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), \"Hello!\")\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Coach the team that SOLID principles are heuristics to manage complexity, not dogma. Every abstraction carries real costs: cognitive overhead, build time, and delayed delivery. Reframe architecture around YAGNI, KISS, and economic trade-offs: start with simple pragmatic code, because clean simple code is easy to refactor when genuine complexity emerges.",
        "best_answer": (
            "Coaching an engineering team suffering from premature abstraction requires reframing architecture as an economic balance between maintainability and delivery velocity.\n\n"
            "1. **Principles are Heuristics, Not Dogma**:\n   - SOLID principles exist to solve concrete software pain points (high coupling, fragile changes, untestable code). Applying heavy solutions when those pain points do not exist is architectural waste.\n   - Every abstraction introduces real overhead: doubled file counts, IDE navigation friction, Dagger binding ceremony, and longer Gradle build times.\n\n"
            "2. **Anchor on Pragmatic Engineering Principles (YAGNI & KISS)**:\n   - **YAGNI (You Aren't Gonna Need It)**: Speculative extensibility (e.g. building a strategy engine because 'marketing might want 4 alternative providers next year') wastes sprint capacity on hypothetical futures that rarely materialize.\n   - **KISS (Keep It Simple, Stupid)**: The simplest code that fulfills current requirements, handles errors, and passes unit tests is the superior engineering choice.\n\n"
            "3. **Evolutionary Architecture Assurance**:\n   - Assure the team that simple code is not low-quality code. Plain, decoupled Kotlin code without gratuitous interfaces can be refactored into Use Cases and Strategies in under two hours when requirements genuinely expand.\n   - Conversely, untangling a premature, multi-layered generic abstraction is notoriously painful."
        ),
        "deep_answer": (
            "In engineering leadership, a senior architect guides the team to establish **Complexity Thresholds**:\n"
            "- *Tier 1 (Display / Simple CRUD)*: Direct ViewModel-to-Repository communication. Zero interfaces, zero Use Cases. Priority: Time to market.\n"
            "- *Tier 2 (Interactive Features with Logic)*: ViewModel consumes Use Cases for reusable business operations. Repositories manage offline caching.\n"
            "- *Tier 3 (Core Domain / Multi-Entry / Fintech)*: Full Clean Architecture with strict DIP interfaces, Strategy routers, and FSM state machines.\n\n"
            "This empowers teams to modulate architectural ceremony proportionally to feature risk, eliminating overengineering while maintaining excellence in mission-critical domains."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between junior, mid-level, and senior engineering perspectives on SOLID?",
                "answer": "Junior engineers write spaghetti code unaware of SOLID. Mid-level engineers apply SOLID dogmatically to every class regardless of context. Senior engineers understand the economic trade-offs of abstractions and apply SOLID pragmatically where complexity demands it."
            },
            {
                "question": "How do you challenge an overengineered PR without demotivating a developer?",
                "answer": "Praise their architectural understanding, explain the maintenance and compilation costs of the abstractions, highlight YAGNI, and collaborate on simplifying the PR while agreeing on future refactoring triggers."
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

    for item in SOL_15_20:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions SOL-15 to SOL-20. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
