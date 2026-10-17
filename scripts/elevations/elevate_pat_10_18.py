#!/usr/bin/env python3
"""Elevate PAT-10 through PAT-18 for bilingual parity and senior spoken answers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path("/Volumes/M&M/Android/InterView/untitled folder/android quation")
sys.path.insert(0, str(BASE_DIR / "scripts" / "elevations"))

import elevation_engine as ee

TOPIC_AR = "أنماط التصميم البرمجية (Design Patterns)"
REVIEWED_DATE_AR = "تمت المراجعة الفنية استناداً إلى توثيق أندرويد الرسمي في 2026-10-14."

DATA = {}

# ==========================================
# PAT-10: Compare Factory and Abstract Factory.
# ==========================================
DATA["PAT-10"] = {
    "concept_en": """The Factory Method and Abstract Factory patterns are creational abstractions designed to decouple client code from concrete class instantiation, but they operate at fundamentally different structural scopes. Factory Method defines an interface containing a single creation method, delegating the instantiation of an individual product to subclasses or specialized providers. In contrast, Abstract Factory provides an overarching interface for creating entire families of related or dependent products without specifying their concrete classes. While Factory Method focuses on creating one polymorphic product variant, Abstract Factory guarantees familial consistency, ensuring that products created across multiple factory methods are mutually compatible and visually or operationally cohesive.""",
    "walkthrough_en": """Contrasting Factory Method with Abstract Factory in Kotlin:
```kotlin
// 1. FACTORY METHOD: Creates a single polymorphic product
interface ChartRenderer { fun render(canvas: Canvas) }
interface ChartFactory { fun createRenderer(): ChartRenderer }

class BarChartFactory : ChartFactory {
    override fun createRenderer(): ChartRenderer = BarChartRenderer()
}

// 2. ABSTRACT FACTORY: Creates an entire family of related products
interface DesignSystemFactory {
    fun createPrimaryButton(): ButtonComponent
    fun createInputField(): InputComponent
    fun createCardContainer(): CardComponent
}

class Material3DesignFactory : DesignSystemFactory {
    override fun createPrimaryButton() = Material3Button()
    override fun createInputField() = Material3Input()
    override fun createCardContainer() = Material3Card()
}

class CupertinoDesignFactory : DesignSystemFactory {
    override fun createPrimaryButton() = CupertinoButton()
    override fun createInputField() = CupertinoInput()
    override fun createCardContainer() = CupertinoCard()
}
```""",
    "short_en": """Factory Method focuses on creating a single product by delegating instantiation to a specific method, such as ViewModelProvider.Factory creating a ViewModel. Abstract Factory focuses on creating entire families of related or dependent products without specifying concrete classes, such as a design system factory creating matching buttons, cards, and input fields. Factory Method produces one object, whereas Abstract Factory guarantees familial compatibility across multiple collaborating objects.""",
    "structured_en": """Comparing Factory Method and Abstract Factory requires evaluating their structural scope, object relationships, and operational guarantees.
Factory Method centers on a single product hierarchy. An interface declares a creation signature, leaving implementing subclasses or lambdas to determine the concrete type instantiated. A textbook Android example is ViewModelProvider.Factory, where a single create method produces an individual ViewModel instance based on the requested class token. The client code consumes the resulting product polymorphically without knowing its concrete constructor mechanics.
Abstract Factory elevates this concept to families of interdependent products. Instead of creating an isolated object, an Abstract Factory exposes multiple creation methods that yield distinct products designed to collaborate seamlessly. For instance, in a multi-brand white-label Android application, an Abstract Factory can produce the full suite of UI components, such as headers, cards, and buttons, corresponding to a specific brand theme. Clients interact with the abstract family interface, ensuring that components from different design languages are never accidentally mixed in the same screen hierarchy.
While Factory Method relies heavily on class inheritance or single-method delegation, Abstract Factory relies on object composition, often using individual Factory Methods under the hood to instantiate each family member.""",
    "deep_senior_en": """Under the hood, Abstract Factory is conceptually a composite of multiple Factory Methods bound by an architectural consistency invariant.
In modern Android architecture powered by Dagger and Hilt, Dagger Components and Subcomponents are direct compile-time implementations of the Abstract Factory pattern. When you define an ActivityComponent or SingletonComponent with multiple provision methods, Dagger generates a concrete factory class under the hood that produces mutually compatible graph instances sharing identical scope and lifecycle boundaries.
In pure Kotlin development, traditional Factory boilerplate is frequently replaced by idiomatic language features. A companion object function or top-level constructor-like function often replaces a standalone Factory class when no dynamic state is required. However, senior architects deliberately retain explicit Abstract Factories when designing multi-tenant SDKs, cross-platform design systems, or plugin architectures where entire component suites must be swapped atomically based on remote configuration or runtime device capabilities.
Automated dependency injection engines eliminate manual factory wiring, but understanding Abstract Factory remains essential when authoring custom Dagger assisted factories via AssistedFactory. Assisted injection allows developers to pass runtime screen parameters while letting Dagger inject compile-time dependencies, effectively combining Factory Method flexibility with container-managed dependency graphs without runtime reflection penalties. Additionally, Abstract Factories can be combined with dynamic feature delivery to instantiate brand-specific visual themes on demand, reducing baseline APK size while guaranteeing architectural encapsulation.""",
    "meta_ar": {
        "id": "PAT-10",
        "questionAr": "قارن بين نمط Factory Method ونمط Abstract Factory.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على التمييز الدقيق بين إنشاء منتج فردي متعدد الأشكال وإنشاء عائلات كاملة من المنتجات المترابطة، وإدراك كيفية تطبيق هذه الأنماط في أندرويد المعاصر ومكتبات الحقن مثل Dagger.",
        "why_it_matters_ar": "الخلط بين النمطين يؤدي إلى تصميم مصانع ضخمة ومعقدة لإنشاء كائن واحد، أو العكس بخلط كائنات غير متوافقة في الواجهات المعقدة أو أنظمة التصميم متعددة الثيمات.",
        "worked_example_ar": "مقارنة Factory Method و Abstract Factory:\n```kotlin\n// Factory Method: يصنع منتجاً واحداً فقط\ninterface ViewModelFactory { fun create(): ViewModel }\n// Abstract Factory: يصنع عائلة كاملة متناسقة من المكونات\ninterface ThemeFactory {\n    fun createButton(): Button\n    fun createCard(): Card\n}\n```",
        "trade_offs_ar": "الـ Factory Method أبسط وأقل كوداً لكنه يقتصر على نوع واحد، بينما Abstract Factory يضمن توافق عائلة المنتجات بالكامل لكنه يضيف واجهات وطبقات تجريد متعددة.",
        "failure_modes_ar": "خلط مكونات من عائلات مختلفة كعرض زر من ثيم داكن داخل كارد من ثيم فاتح نتيجة غياب Abstract Factory موحد ينظم إنتاج الثيم كاملاً.",
        "production_perspective_ar": "في تطبيقات أندرويد الضخمة، نستخدم Dagger Components كـ Abstract Factory يولد كل تبعيات الشاشة، ونستخدم AssistedFactory لحقن المعاملات اللحظية في الـ ViewModels.",
        "how_to_answer_ar": "ابدأ بالفارق الجوهري: Factory Method يصنع منتجاً واحداً بينما Abstract Factory يصنع عائلة منتجات مترابطة تضمن التوافق، واضرب مثال ViewModelFactory للأول، ومثال نظام التصميم أو Dagger Components للثاني.",
        "talking_points_ar": "الفارق بين منتج فردي وعائلة منتجات، وتطبيق Dagger Components كـ Abstract Factory، ودور AssistedFactory في كوتلن، وتبسيط المصانع بالـ Companion Objects.",
        "follow_ups_ar": "- **المحاور:** \"كيف يمثل Dagger Component نمط Abstract Factory؟\"\n  **المرشح:** \"الـ Component في Dagger هو إنترفيس بيعلن عن دوال متعددة لتوفير كائنات مختلفة تشترك في نفس الـ Scope ودورة الحياة، وداجر بيولد الكود اللي بينشئ العائلة دي كلها بتوافق تام.\"\n\n- **المحاور:** \"متى نفضل Companion Object create() على كلاس Factory كامل؟\"\n  **المرشح:** \"لو عملية الإنشاء بسيطة ومش محتاجة حقن تبعيات أو تبديل ديناميكي وقت التشغيل، دالة الـ Companion بتوفر كوداً نظيفاً ومباشراً بدون زيادة كلاسات.\"",
        "self_check_ar": "هل وضحت الفارق بين المنتج الفردي وعائلة المنتجات؟ هل ذكرت مثال Dagger؟ وهل بينت متى نستخدم كل منهما عملياً؟",
        "references_ar": f"- [Abstract Factory Pattern](https://refactoring.guru/design-patterns/abstract-factory) — الدليل المرجعي لنمط المصنع المجرد.\n- [Dagger Assisted Injection](https://dagger.dev/dev-guide/assisted-injection.html) — التوثيق الرسمي للمصانع المدعومة في Dagger.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نمط Factory Method بيركز على إنشاء منتج واحد محدد بتفويض عملية البناء لدالة مخصصة، زي `ViewModelProvider.Factory` اللي بتبني ViewModel معين. أما نمط Abstract Factory فبيركز على إنشاء عائلة كاملة من المنتجات المترابطة أو المتوافقة مع بعضها بدون تحديد كلاساتها الملموسة، زي مصنع نظام تصميم بيبني أزرار وكروت ونصوص متناسقة لنفس الثيم. الأول بينتج كائناً منفرداً، والتاني بيضمن توافق وتناسق مجموعة كائنات كاملة.",
        "best_answer_ar": "المقارنة بين Factory Method و Abstract Factory بتعتمد أساساً على نطاق المنتجات والعلاقة الهندسية بينها.\n\nنمط Factory Method بيتعامل مع كائن واحد فقط. بيكون عندك إنترفيس بيعلن عن دالة إنشاء واحدة، والكلاسات اللي بتنفذه هي اللي بتحدد نوع الكائن النهائي. أشهر مثال يومي في أندرويد هو `ViewModelProvider.Factory`؛ الدالة بتاخد كلاس الموديل وترجع لك نسخة واحدة من الـ ViewModel المطلوب، وكود الشاشة بيتعامل مع الناتج كـ ViewModel عام بدون ما يدخل في تفاصيل بنائه.\n\nأما نمط Abstract Factory فبيعلى بالمستوى خطوة، وبيتعامل مع عائلة منتجات كاملة بتشتغل مع بعض. فبدل ما ينشئ حاجة واحدة، الإنترفيس بيحتوي على دوال متعددة لإنشاء كائنات مختلفة لازم تكون متوافقة بنسبة 100%. مثلاً في تطبيق White-label بيدعم كذا علامة تجارية، بنعمل Abstract Factory لواجهة المستخدم؛ المصنع بيطلع الزرار المتوافق مع الكارد المتوافق مع حقل الإدخال لنفس البراند، وده بيمنع تماماً خلط زرار من براند مع خلفية براند تاني.\n\nباختصار، Factory Method هو طريقة مرنة لإنتاج كائن متعدد الأشكال، بينما Abstract Factory هو واجهة عليا بتجمع عدة Factory Methods لإنتاج منظومة متكاملة ومتوافقة.",
        "deep_answer_ar": "تحت الكابوت، نمط Abstract Factory في جوهره عبارة عن كلاس بيجمع عدة Factory Methods يربطها قيد معماري موحد لحفظ التوافق الداخلي.\n\nفي معمارية أندرويد الحديثة المعتمدة على Dagger و Hilt، الـ Dagger Components والـ Subcomponents هي التطبيق الصريح لنمط Abstract Factory في وقت الـ Compilation. لما بتعرف كلاس الـ Component بدوال بتوفر Repositories و UseCases و Database instances، داجر بيولد مصنعاً حقيقياً يضمن إن كل الكائنات دي تشترك في نفس الـ Scope ونفس الـ Lifecycle بأمان تام وبدون أي تضارب بين الخيوط المتزامنة.\n\nوفي لغة Kotlin، استخدام الأنماط دي مبقاش محتاج البويلربليت القديم المعتاد في جافا؛ بنقدر نستبدل الـ Factory الفردي بدوال في الـ Companion Object أو Top-level Functions طالما مش محتاجين نغير التنفيذ وقت التشغيل. لكن في المشاريع الكبيرة، الـ Abstract Factory بيفضل أداة لا غنى عنها في حالات زي الـ Assisted Injection مع `@AssistedFactory`؛ حيث بيسمح بتمرير بارامترات لحظية من الـ SavedStateHandle أو الـ Intent مع ترك باقي التبعيات لـ Hilt لحقنها آلياً.\n\nالمهندسون الكبار بيستخدموا Abstract Factory لعزل الأنظمة الكبيرة كبوابات الدفع أو المحركات الرسومية؛ بحيث الكود يطلب مصنعاً متكاملاً يدير كل المكونات الداخلية المتوافقة مع نوع الجهاز أو نظام التشغيل بدون أي تسريب لكود التنفيذ الملموس."
    }
}

# ==========================================
# PAT-11: Where might Builder be useful in API or SDK design?
# ==========================================
DATA["PAT-11"] = {
    "concept_en": """The Builder pattern is a creational software pattern that separates the progressive, step-by-step configuration of a complex object from its concrete representation and instantiation. While modern Kotlin largely supplants basic Builders in internal application code through named arguments and default parameter values, the Builder pattern remains indispensable in public SDK and enterprise API design. It provides pristine backward-compatible API evolution, guarantees seamless Java interoperability without telescoping constructors, enforces strict cross-field validation rules atomically during terminal build() invocation, and guarantees final object immutability by encapsulating construction mutable state away from the finished domain instance.""",
    "walkthrough_en": """Implementing a resilient SDK Configuration Builder with cross-field validation:
```kotlin
class AnalyticsSdkConfig private constructor(
    val apiKey: String,
    val endpointUrl: String,
    val dispatchIntervalMs: Long,
    val maxBatchSize: Int,
    val enableDebugLogging: Boolean
) {
    class Builder(private val apiKey: String) { // Mandatory fields in builder constructor
        private var endpointUrl: String = "https://default.telemetry.io/v1"
        private var dispatchIntervalMs: Long = 30_000L
        private var maxBatchSize: Int = 50
        private var enableDebugLogging: Boolean = false

        fun setEndpointUrl(url: String) = apply { this.endpointUrl = url }
        fun setDispatchIntervalMs(interval: Long) = apply { this.dispatchIntervalMs = interval }
        fun setMaxBatchSize(size: Int) = apply { this.maxBatchSize = size }
        fun setDebugLogging(enabled: Boolean) = apply { this.enableDebugLogging = enabled }

        fun build(): AnalyticsSdkConfig {
            // Atomic cross-field validation invariants
            require(apiKey.isNotBlank()) { "API Key cannot be blank" }
            require(dispatchIntervalMs >= 5_000L) { "Interval must be >= 5000ms" }
            require(maxBatchSize in 1..500) { "Batch size must be between 1 and 500" }
            return AnalyticsSdkConfig(apiKey, endpointUrl, dispatchIntervalMs, maxBatchSize, enableDebugLogging)
        }
    }
}
```""",
    "short_en": """The Builder pattern is critical in public SDK and API design because it constructs complex configuration objects with many optional parameters while maintaining flawless Java interoperability. Unlike Kotlin named arguments which require recompilation when defaults change, a Builder allows adding new configuration parameters without breaking binary or source compatibility. Furthermore, it enforces cross-field validation atomically inside build() and guarantees final object immutability.""",
    "structured_en": """Evaluating the utility of the Builder pattern in SDK and API design requires analyzing consumer ergonomics, binary compatibility, and validation boundaries.
In application code written purely in Kotlin, data classes with default arguments and named parameters handle most creation needs. However, in public SDKs and libraries that serve both Java and Kotlin consumers, constructor overloads suffer from the telescoping constructor anti-pattern, where dozens of combinatorial constructors must be maintained. A fluent Builder offers a clean, self-documenting interface where consumers specify only the options they care about.
Crucially, Builder provides superior binary and backward compatibility. Adding a new optional parameter to a Kotlin data class alters its synthetic constructor bytecode signature, potentially breaking compiled binary consumers who do not recompile. With a Builder, introducing a new setter method preserves complete binary compatibility with existing published artifacts.
Additionally, Builder centralizes invariant validation. In complex systems, parameters often depend on each other, such as requiring a custom encryption key whenever end-to-end encryption is enabled. The Builder accumulates these settings safely and executes cross-field validation atomically inside the build method, ensuring that invalid, partially initialized objects are never instantiated.""",
    "deep_senior_en": """Under the hood, the Builder pattern resolves difficult trade-offs between mutability during construction and immutability during runtime execution.
An uninitialized or partially configured object exposed to multi-threaded environments risks race conditions where another thread reads default or corrupted state before construction finishes. The Builder pattern isolates mutability inside a temporary, single-threaded Builder instance. The resulting product is constructed with private constructors and exposed via read-only immutable val properties, ensuring absolute thread safety across concurrent Android worker threads.
In enterprise SDK development, API surface stability is enforced by tools like Android's Metalava and Jetpack Binary Compatibility Validator. When an SDK author exposes a data class with copy(), any internal schema modification breaks public ABI (Application Binary Interface). The Builder pattern encapsulates internal state completely, allowing library maintainers to introduce default caching behaviors, internal flags, or updated HTTP dispatch pools without altering consumer-facing contracts.
Prominent Android framework and Jetpack classes rely heavily on Builder for this exact reason, including NotificationCompat.Builder, OkHttpClient.Builder, WorkRequest.Builder, and CameraX configurations. These APIs accommodate dozens of hardware-specific flags, permission checks, and OS-version constraints while maintaining backward compatibility across API level 21 through modern Android releases. Furthermore, builders can implement staged or stepped builder interfaces via fluent generic chaining, mathematically preventing callers from invoking build() until all mandatory configuration parameters are explicitly supplied at compile time.""",
    "meta_ar": {
        "id": "PAT-11",
        "questionAr": "أين تبرز أهمية نمط Builder في تصميم مكتبات SDK وواجهات البرمجة العامة (APIs)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور نمط Builder في تصميم المكتبات العامة، والقدرة على شرح التوافق مع لغة Java، والحفاظ على التوافق الثنائي (Binary Compatibility)، والتحقق من صحة المدخلات المشتركة بشكل ذري (Atomic Validation).",
        "why_it_matters_ar": "الاعتماد على Data Classes في الـ SDKs العامة يكسر الـ Binary Compatibility عند إضافة معاملات جديدة، ويحرم مطوري جافا من كتابة كود مريح، ويزيد مخاطر إنشاء كائنات غير مكتملة أو غير صالحة.",
        "worked_example_ar": "تصميم Builder لمكتبة عامة مع التحقق الذري:\n```kotlin\nclass SdkConfig private constructor(val key: String, val timeout: Long) {\n    class Builder(val key: String) {\n        var timeout = 10_000L\n        fun setTimeout(t: Long) = apply { timeout = t }\n        fun build(): SdkConfig {\n            require(key.isNotEmpty()) { \"Invalid Key\" }\n            return SdkConfig(key, timeout)\n        }\n    }\n}\n```",
        "trade_offs_ar": "يزيد من حجم الكود والبويلربليت مقارنة بـ Data Class بسيطة، لكنه يمنح استقراراً مطلقاً للواجهة العامة وتوافقاً ثنائياً تاماً وتحققاً متقدماً من البيانات.",
        "failure_modes_ar": "توفير دوال Setters عادية على الكائن النهائي مما يجعله قابلاً للتعديل في خيوط متزامنة بعد إنشائه، أو كسر الـ ABI بإضافة معاملات في الكونستركتور مباشرة.",
        "production_perspective_ar": "في مكتبات أندرويد الرسمية زي OkHttpClient و WorkManager و NotificationCompat، يُعتمد الـ Builder كمعيار أساسي لضمان عمل الـ SDK عبر عشرات إصدارات الأندرويد واستقرار الـ Binary ABI.",
        "how_to_answer_ar": "اشرح أن Builder في كوتلن الداخلية يستبدل بـ Named Arguments، لكن في الـ SDKs العامة هو ضرورة لـ: التوافق مع Java، وحفظ التوافق الثنائي (Binary Compatibility)، والتحقق الذري من الحقول داخل `build()`، وضمان عدم قابلية الكائن للتعديل (Immutability).",
        "talking_points_ar": "التوافق الثنائي واستقرار الـ ABI، وحل مشكلة Telescoping Constructors في جافا، والتحقق الذري من القيود المتداخلة، وعزل الـ Mutability أثناء البناء عن الـ Immutability أثناء التشغيل.",
        "follow_ups_ar": "- **المحاور:** \"ليه الـ Named Arguments في كوتلن مش كافية لتصميم مكتبات عامة؟\"\n  **المرشح:** \"لأنها غير مريحة للمطورين اللي بيستخدموا جافا، ولأن إضافة بارامتر افتراضي جديد في داتا كلاس بيغير البايتكود الخاص بالكونستركتور ويكسر التوافق الثنائي للمشاريع المبنية مسبقاً.\"\n\n- **المحاور:** \"إزاي الـ Builder بيحمي من مشاكل التزامن المتعدد (Concurrency)؟\"\n  **المرشح:** \"بيحصر التعديل (Mutation) داخل كائن الـ Builder المؤقت، ولما ينادي `build()` بيرجع كائن نهائي كل حقوله `val` غير قابلة للتغيير إطلاقاً، فيكون Thread-safe تماماً.\"",
        "self_check_ar": "هل بينت الفرق بين استخدامه في الكود الداخلي وتصميم الـ SDKs؟ هل ذكرت التوافق الثنائي والتحقق الذري؟ وهل استشهدت بأمثلة أندرويد الشهيرة؟",
        "references_ar": f"- [Effective Java by Joshua Bloch - Item 2](https://en.wikipedia.org/wiki/Effective_Java) — المرجع الكلاسيكي لنمط Builder في تصميم الـ APIs.\n- [Jetpack WorkRequest.Builder](https://developer.android.com/reference/androidx/work/WorkRequest.Builder) — التوثيق الرسمي لنمط Builder في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نمط Builder مهم جداً في تصميم الـ SDKs والـ APIs العامة لأنه بيسمح ببناء كائنات إعدادات معقدة ببارامترات اختيارية كتيرة مع الحفاظ التام على التوافق مع مطوري جافا. والأهم إنه بيحافظ على التوافق الثنائي (Binary Compatibility) بحيث لو ضفت إعدادات جديدة في المستقبل ميكسرش المشاريع المعتمدة على نسختك القديمة، وبيوفر مكاناً مركزياً لفحص شروط البيانات بشكل ذري داخل دالة `build()`، ويضمن إن الكائن الناتج غير قابل للتعديل (Immutable) وآمن في بيئات التزامن.",
        "best_answer_ar": "في كود تطبيقات كوتلن الداخلية، بنكتفي في الغالب بالـ Data Classes مع الـ Named Arguments والـ Default Values لأن اللغة بتسهل ده جداً. لكن لما نيجي نصمم SDK عام أو Library هيستخدمها آلاف المطورين، نمط Builder بيتحول لضرورة هندسية لا غنى عنها لعدة أسباب رئيسية.\n\nالسبب الأول هو التوافق مع لغة Java؛ مطورو جافا معندهمش Named Arguments، ولو استخدمت كونستركتور عادي هتضطر تعمل عشرات الـ Overloads لتغطية كل الاحتمالات (Telescoping Constructor Anti-pattern)، بينما الـ Builder بيدي للمطور تجربة استخدام سلسة وسهلة القراءة بأسلوب الـ Fluent API.\n\nالسبب الثاني وهو الأهم: التوافق الثنائي (Binary Compatibility). لو ضفت حقل جديد في Data Class، التوقيع الداخلي للكونستركتور في الـ Bytecode هيتغير، وده هيكسر التطبيقات اللي بتستخدم نسختك بدون ما تعيد عمل Compilation. مع الـ Builder، إضافة دالة setter جديدة مش بتكسر أي كود قديم إطلاقاً.\n\nالسبب الثالث هو التحقق الذري (Atomic Validation)؛ لو عندك إعدادات بتعتمد على بعضها زي ضرورة توفير مفتاح تشفير لو خيار الأمان مفعل، الـ Builder بيجمع كل القيم وينفذ الفحص داخل دالة `build()` قبل ما الكائن يتخلق، فبيمنع وجود أي كائن في حالة غير صالحة.",
        "deep_answer_ar": "تحت الكابوت، نمط Builder بيحل معضلة هندسية صعبة جداً وهي التوفيق بين القابلية للتعديل (Mutability) أثناء مرحلة التكوين، والحفاظ على ثبات الكائن (Immutability) أثناء التشغيل الفعلي.\n\nتعريض كائن قابل للتعديل لعدة خيوط متزامنة (Threads) في تطبيق أندرويد بيعرضه لمشاكل Race Conditions خطيرة؛ ممكن خيط يقرأ بيانات غير مكتملة وخيط تاني لسه بيعدل فيها. الـ Builder بيعزل كل التعديلات دي داخل كائن مؤقت، وبمجرد استدعاء `build()` بيولد كائن نهائي كل خصائصه `val` وبكونستركتور خاص (Private)، وده بيمنح الكائن مناعة تامة وتوافقاً ممتازاً مع الـ Thread Safety عبر كل المعالجات.\n\nفي بناء الـ SDKs للمؤسسات الكبرى، بنستخدم أدوات زي Metalava والـ Binary Compatibility Validator لضمان ثبات الـ ABI العام. دوال الـ Data Class التلقائية زي `copy()` بتكشف التفاصيل الداخلية للـ Bytecode، وأي تعديل فيها بيعتبر Breaking Change فوري. نمط Builder بيعزل تفاصيل التخزين والـ Defaults تماماً، فتقدر كصاحب SDK تضيف Flags جديدة أو تحسن إدارة اتصالات الشبكة في الخلفية بدون ما تلمس العقد المبرم مع المستخدمين.\n\nالأمثلة الحية في أندرويد بتأكد الحقيقة دي؛ مكتبات نظام أندرويد الأساسية و Jetpack بتعتمد كلياً على الـ Builder زي `NotificationCompat.Builder` و `OkHttpClient.Builder` و `WorkRequest.Builder`؛ لأنها بتحتاج تدير عشرات الخصائص والقيود المعقدة عبر إصدارات أندرويد المختلفة مع ضمان استقرار الكود المكتوب من سنين."
    }
}

# ==========================================
# PAT-12: How would Facade simplify an unreliable third-party SDK?
# ==========================================
DATA["PAT-12"] = {
    "concept_en": """The Facade pattern is a structural design pattern that provides a clean, unified, and simplified high-level interface over a complex, disparate, or unreliable subsystem. In enterprise Android engineering, a Facade acts as an essential Anti-Corruption Layer (ACL) positioned between fragile vendor SDKs and clean application domain logic. It encapsulates convoluted configuration lifecycles, converts unpredictable vendor threading models and legacy callback listeners into structured Kotlin Coroutines and Results, centralizes error handling, retry policies, and fallback mechanisms, and prevents leaky third-party vendor dependencies from polluting core architecture layers.""",
    "walkthrough_en": """Encapsulating an unreliable vendor SDK behind a resilient Facade:
```kotlin
// Domain Model & Interface (Pure Kotlin, zero vendor types)
data class UserIdentity(val id: String, val verificationToken: String)
interface IdentityVerificationService {
    suspend fun verifyIdentity(documentImage: ByteArray): Result<UserIdentity>
}

// Resilient Facade wrapping messy vendor SDK
class VendorIdentityFacade @Inject constructor(
    private val vendorSdk: FlakyThirdPartyIdentitySdk,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) : IdentityVerificationService {

    override suspend fun verifyIdentity(documentImage: ByteArray): Result<UserIdentity> = withContext(ioDispatcher) {
        suspendCancellableCoroutine { continuation ->
            try {
                vendorSdk.initializeEngine("KEY_123") // Hide noisy multi-step setup
                vendorSdk.startScan(documentImage, object : FlakyVendorCallback {
                    override fun onSuccess(vendorPayload: VendorPayloadBundle) {
                        // Translate vendor-specific types into clean domain model
                        val identity = UserIdentity(vendorPayload.subId, vendorPayload.rawToken)
                        continuation.resume(Result.success(identity))
                    }
                    override fun onError(code: Int, msg: String?) {
                        // Absorb vendor error codes into domain exceptions
                        continuation.resume(Result.failure(DomainVerificationException(code, msg)))
                    }
                })
            } catch (t: Throwable) {
                continuation.resume(Result.failure(t))
            }
            continuation.invokeOnCancellation { vendorSdk.abortCurrentScan() }
        }
    }
}
```""",
    "short_en": """A Facade encapsulates an unreliable third-party SDK behind a simplified, resilient domain interface. It acts as an Anti-Corruption Layer that shields the application from messy multi-step configurations, converts unruly callbacks into modern Kotlin suspending functions, translates vendor exceptions into safe Result types, and centralizes retry and fallback policies. If the vendor SDK is later swapped or upgraded, application domain logic remains entirely untouched.""",
    "structured_en": """Wrapping an unreliable vendor SDK behind a Facade solves critical architectural vulnerabilities regarding stability, maintainability, and clean boundaries.
Third-party vendor SDKs are notorious for leaky abstractions: they often mandate complex static initialization sequences, throw undocumented runtime exceptions, execute callbacks on arbitrary background threads, and force the app to import vendor-specific data structures across multiple layers. If ViewModels or UseCases interact directly with such an SDK, vendor bugs and breaking API changes ripple throughout the entire codebase.
A Facade establishes an architectural boundary known in Domain-Driven Design as an Anti-Corruption Layer. The Facade exposes a concise, application-owned interface that satisfies exactly what the domain needs, hiding internal SDK complexity.
Internally, the Facade handles defensive engineering: it converts callback spaghetti into suspending coroutines using suspendCancellableCoroutine, wraps network calls in defensive try-catch blocks to catch undocumented runtime crashes, injects retry logic or circuit breakers for unreliable endpoints, and maps foreign data types into clean domain entities.
This structural isolation guarantees that the host application remains stable, unit-testable using mock facades, and completely decoupled from external vendor lifecycles.""",
    "deep_senior_en": """Under the hood, a Facade for a third-party SDK manages thread synchronization, cancellation propagation, and process-level crash containment.
Many legacy vendor libraries spawn uncontrolled background threads or retain Activity references, causing memory leaks and uncatchable background exceptions. Within the Facade, senior engineers wrap vendor invocations inside structured Coroutine scopes, leveraging invokeOnCancellation to signal the vendor SDK to abort ongoing operations and release camera, location, or biometric hardware resources immediately when a ViewModel scope cancels.
Furthermore, the Facade provides a strategic seam for fallback orchestration and dynamic feature flagging. If a remote analytics or identity verification SDK crashes frequently or exceeds latency Service Level Objectives (SLOs), the Facade can evaluate Remote Config flags or local circuit breaker state machines to transparently degrade gracefully, routing requests to a secondary fallback provider or returning a cached offline result without client code ever realizing an outage occurred.
From a modularization perspective, the vendor SDK dependency should be restricted to a private :infrastructure:vendor-name Gradle module using implementation dependencies. The rest of the application depends strictly on the domain interface. This compilation boundary cuts build times and ensures that if the vendor releases a breaking update or must be completely decommissioned, only the isolated Facade module requires modification.""",
    "meta_ar": {
        "id": "PAT-12",
        "questionAr": "كيف يبسط نمط الواجهة (Facade Pattern) التعامل مع مكتبة خارجية (Third-party SDK) غير مستقرة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور نمط Facade كطبقة حماية معمارية (Anti-Corruption Layer)، والقدرة على عزل المكتبات غير المستقرة، وتحويل الكولباكات القديمة لكوروتينات، وإدارة الأخطاء وحالات التراجع (Fallbacks) دون تسريب كود المكتبة للتطبيق.",
        "why_it_matters_ar": "استخدام الـ SDKs الخارجية مباشرة في الشاشات أو الـ ViewModels يجعل التطبيق عرضة للانهيار عند حدوث أي خطأ غير موثق في المكتبة، ويجعل استبدال المكتبة لاحقاً عملية شبه مستحيلة ومكلفة جداً.",
        "worked_example_ar": "بناء Facade لعزل مكتبة خارجية غير مستقرة:\n```kotlin\n// واجهة نظيفة يملكها التطبيق\ninterface IdentityService { suspend fun verify(): Result<Token> }\n// الـ Facade يعزل كود المكتبة والكولباك ويهدئ الأخطاء\nclass IdentityFacade(val sdk: BadSdk) : IdentityService {\n    override suspend fun verify() = suspendCancellableCoroutine { cont ->\n        sdk.run(callback = { res -> cont.resume(Result.success(res)) })\n    }\n}\n```",
        "trade_offs_ar": "يضيف طبقة كود تحويلية وتغليفية إضافية، لكنه يوفر حماية مطلقة للتطبيق من انهيارات الـ SDK ويسهل استبدالها في سطر واحد داخل الـ DI.",
        "failure_modes_ar": "تسريب كائنات الـ SDK الخارجية لطبقات الـ Domain والـ UI، أو نسيان إلغاء العمليات عند إلغاء الـ Coroutine مما يسرب موارد الهاردوير كالـ Camera.",
        "production_perspective_ar": "في الشركات الكبرى، نضع أي SDK خارجي في موديول مستقل ومعزول، ونمنع باقي الموديولات من استيراده، ونتعامل معه فقط من خلال Facade و Anti-Corruption Layer.",
        "how_to_answer_ar": "اشرح أن Facade يعمل كطبقة حماية (Anti-Corruption Layer)؛ يبسط العمليات المعقدة، ويحول الكولباكات لكوروتينات معالجة بالأخطاء، ويعزل كائنات المكتبة عن طبقات الدومين، ويسهل تبديل المكتبة مستقبلاً بدون لمس كود التطبيق.",
        "talking_points_ar": "مفهوم Anti-Corruption Layer، وتحويل الكولباك عبر suspendCancellableCoroutine، وتطويق أخطاء المكتبة وحماية الـ Crash، وعزل التبعيات في موديول Gradle منفصل.",
        "follow_ups_ar": "- **المحاور:** \"كيف يتعامل الـ Facade مع إلغاء العمليات (Cancellation) في الكوروتينات؟\"\n  **المرشح:** \"باستخدام `continuation.invokeOnCancellation`؛ بنمرر كود يطلب من الـ SDK إيقاف العملية فوراً وتحرير موارد الهاردوير زي الكاميرا أو الجي بي إس لما الـ Scope يتقفل.\"\n\n- **المحاور:** \"ما الفرق بين Facade و Adapter في هذا السياق؟\"\n  **المرشح:** \"الـ Adapter بيوفق بين واجهتين غير متطابقتين، بينما الـ Facade بيبسط نظاماً فرعياً كاملاً ومعقداً ويقدم واجهة عليا جديدة وسهلة الاستخدام.\"",
        "self_check_ar": "هل وضحت مفهوم Anti-Corruption Layer؟ هل شرحت كيفية تحويل الكولباكات لكوروتينات آمنة؟ وهل بينت ميزة عزل الموديولات؟",
        "references_ar": f"- [Facade Pattern](https://refactoring.guru/design-patterns/facade) — دليل نمط الواجهة في هندسة البرمجيات.\n- [Anti-Corruption Layer pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer) — مفهوم طبقة مكافحة الفساد المعماري من مايكروسوفت.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نمط Facade بيعزل الـ SDK الخارجي غير المستقر ورا واجهة نظيفة ومبسطة يملكها تطبيقنا، ويشتغل كطبقة حماية معمارية (Anti-Corruption Layer). وظيفته إنه يخفي خطوات التجهيز المعقدة للمكتبة، ويحول الكولباكات القديمة المتعبة لدوال معلقة (Suspending functions) بترجع كائنات `Result` آمنة، ويدير المحاولات التلقائية وحالات الطوارئ (Fallbacks) مركزياً، ويمنع تسرب أي كلاسات تابعة للـ SDK لطبقات الـ Domain والـ UI.",
        "best_answer_ar": "المكتبات الخارجية (Third-party SDKs) غالباً بتكون مصدر إزعاج كبير في تطبيقات أندرويد؛ لأنها بتطلب خطوات تهيئة معقدة، وبترمي استثناءات غير متوقعة في وقت التشغيل، وبتجبرك على التعامل مع كولباكات قديمة وأنواع بيانات غريبة مش متوافقة مع معمارية مشروعك.\n\nنمط الـ Facade بيحل الأزمة دي جذرياً بإنه بيبني طبقة عازلة بنسميها في المعمارية النظيفة Anti-Corruption Layer. إحنا بنعرف Interface بسيط جداً ونظيف بيمثل الاحتياج الحقيقي للتطبيق بتاعنا بلغة كوتلن النقية. والـ Facade هو الكلاس الوحيد اللي بيشوف الـ SDK المعقد ده من جوه.\n\nداخل الـ Facade، بنحول الكولباكات العشوائية لكوروتينات أنيقة باستخدام `suspendCancellableCoroutine`، وبنحاوط كل الاستدعاءات بـ `try-catch` متين لامتصاص الانهيارات المفاجئة، وبنحول استجابات الـ SDK لـ Domain Models واضحة، وبنضيف منطق إعادة المحاولة أو التراجع (Retry & Fallback).\n\nالفائدة الكبرى هنا إن لو الـ SDK اتغيرت أو ظهر فيها عيب وقررنا نستبدلها بمكتبة تانية خالص بكرة الصبح، كود التطبيق والشاشات والـ ViewModels مش هيتغير فيهم سطر واحد، والتعديل كله هيفضل محصور داخل كلاس الـ Facade بس.",
        "deep_answer_ar": "تحت الكابوت، الـ Facade للـ SDK الخارجي مش بس مجرد Wrapper شكلي، بل هو صمام أمان لإدارة الخيوط المتزامنة وحماية دورة حياة المكونات وإلغاء العمليات (Cancellation Propagation).\n\nكتير من الـ SDKs القديمة بتفتح خيوط غير خاضعة للرقابة وبتفضل ماسكة في الميموري، وده بيسبب Memory Leaks وانهيارات صامتة. داخل الـ Facade، المهندسون الكبار بيغلفوا استدعاءات المكتبة داخل كوروتينات منضبطة بـ `Dispatchers.IO`، وبيستخدموا `continuation.invokeOnCancellation` علشان يبلغوا الـ SDK يقفل الاتصال ويحرر موارد النظام زي الكاميرا أو البلوتوث بمجرد ما المستخدم يقفل الشاشة والـ Scope ينتهي.\n\nعلاوة على كده، الـ Facade بيمثل المكان المثالي لتطبيق استراتيجيات المرونة العالية (Resilience Strategies) زي الـ Circuit Breaker؛ فلو الـ SDK الخارجي بيعلق كتير أو السيرفر بتاعه واقع، الـ Facade يقدر يكتشف ده ويحول الطلبات تلقائياً لمزود بديل أو يرجع داتا من الكاش المحلي بناءً على إعدادات الـ Remote Config، بدون ما طبقة الـ UI تحس بأي انقطاع في الخدمة.\n\nمعمارياً، بنحط الـ SDK داخل موديول Gradle معزول تماماً بصلاحية `implementation`، وموديولات الميزات والـ UI بتشوف فقط الـ Interface العام. ده بيقلل وقت الـ Compilation، وبيمنع المطورين من استيراد كلاسات الـ SDK بالخطأ في الـ ViewModels، وبيحافظ على نقاء واستقلالية الكود بالكامل."
    }
}

# ==========================================
# PAT-13: How do callback/lifecycle observers relate to Flow and LiveData?
# ==========================================
DATA["PAT-13"] = {
    "concept_en": """The Observer pattern is the foundational behavioral abstraction underpinning asynchronous data communication in Android, evolving across three major architectural eras: primitive Java callback listeners, lifecycle-aware Jetpack LiveData, and modern Kotlin Coroutine Flow pipelines. Primitive callbacks lack lifecycle awareness, requiring manual unregistration and risking catastrophic memory leaks when asynchronous events outlive UI controllers. LiveData introduced automatic lifecycle observation by dispatching events exclusively to active observers (STARTED or RESUMED), but suffered from Main-Thread lock-in and primitive operator capabilities. Modern Kotlin Flow supersedes both as a unified, non-blocking, multiplatform asynchronous stream engine: cold Flows leverage callbackFlow with awaitClose to transform legacy listener registrations into cancellable streams, while hot StateFlow provides explicit, lifecycle-safe state observation via repeatOnLifecycle.""",
    "walkthrough_en": """The evolution of Observer: from callbacks to LiveData to Flow:
```kotlin
// ERA 1: Primitive Callback (Prone to leaks and lifecycle mismatches)
interface LocationListener { fun onLocationChanged(loc: Location) }
class LegacyLocationManager {
    fun register(l: LocationListener) { /* ... */ }
    fun unregister(l: LocationListener) { /* Manual cleanup required in onDestroy! */ }
}

// ERA 2: LiveData (Lifecycle-aware, but tied to Main thread and Android framework)
val userLiveData: MutableLiveData<UserState> = MutableLiveData()
// Observed in Activity via: userLiveData.observe(this) { state -> render(state) }

// ERA 3: Modern Kotlin Flow (Structured concurrency, cold by default, thread-agnostic)
fun LocationManager.observeLocations(): Flow<Location> = callbackFlow {
    val listener = LocationListener { location -> trySend(location) }
    register(listener)
    awaitClose { unregister(listener) } // Automatic lifecycle cancellation!
}.flowOn(Dispatchers.Default)

// In Jetpack Compose: Lifecycle-safe hot observation
@Composable
fun LocationScreen(viewModel: LocationViewModel) {
    val location by viewModel.locationState.collectAsStateWithLifecycle()
    Text("Latitude: ${location?.latitude}")
}
```""",
    "short_en": """Callbacks, LiveData, and Flow all implement the Observer pattern across different Android eras. Callbacks are primitive listeners that require manual cleanup and leak easily. LiveData introduced automatic lifecycle-aware observation tied to the Main thread. Modern Kotlin Flow provides a pure, multiplatform asynchronous stream standard: cold Flows bridge legacy callbacks cleanly via callbackFlow and awaitClose, while hot StateFlow replaces LiveData for UI state with safe observation through repeatOnLifecycle.""",
    "structured_en": """Analyzing the evolution from callback listeners to LiveData and Kotlin Flow reveals how the Observer pattern has been continuously refined to solve lifecycle and concurrency challenges.
The earliest era relied on raw interface callbacks, such as OnClickListener or custom asynchronous listeners. While conceptually simple, callbacks decouple state producers from consumers poorly. They lack lifecycle awareness, meaning an asynchronous background thread attempting to deliver a result to a destroyed Activity triggers NullPointerExceptions, window token leaks, or permanent memory leaks if unregistration is overlooked.
Jetpack LiveData revolutionized this by embedding the LifecycleOwner contract directly into the Observer pattern. LiveData observes lifecycle state machines, automatically dispatching events only when the subscriber is in an active state (STARTED or RESUMED) and automatically removing subscribers upon DESTROYED. However, LiveData has fundamental architectural constraints: it requires the Android framework, operates strictly on the Main Thread, and lacks rich compositional and backpressure operators.
Modern Kotlin Flow represents the current industry standard. Flow is multiplatform, supports cold and hot streams, offers hundreds of rich functional operators, and supports structured concurrency out of the box. By using callbackFlow with awaitClose, legacy listener-based APIs are converted into reactive streams where registration and deregistration happen automatically when coroutine scopes activate and cancel.""",
    "deep_senior_en": """Under the hood, the migration from LiveData to Flow and StateFlow represents a shift from framework-coupled event delivery to compiler-assisted structured concurrency.
LiveData maintains an internal SafeIterableMap of observers and interrogates the LifecycleOwner state on every event dispatch. When an Activity enters the background, LiveData simply halts dispatches while retaining the latest value in memory. However, in data and domain layers, binding to LiveData creates an undesirable compilation dependency on androidx.lifecycle, polluting pure business logic with Android platform baggage.
Kotlin Flow solves this by operating independently of the Android SDK. Cold Flows do not allocate resources or execute upstream producers until a downstream collector calls collect. In callbackFlow, the awaitClose block suspends until the collector's CoroutineContext cancels, ensuring that underlying native listeners, LocationManager clients, or broadcast receivers are deterministically unregistered without manual intervention.
At the presentation boundary, StateFlow maintains a single, read-only state holder that emits updates to multiple observers using atomic memory comparisons. When paired with repeatOnLifecycle or collectAsStateWithLifecycle, the collection job is canceled when the UI drops below the specified Lifecycle.State (such as STOPPED), completely halting upstream producer work, saving CPU cycles, and eliminating background battery drain. This architectural cohesion ensures that background asynchronous jobs do not outlive their UI hosts, preventing wasted computation, network bandwidth consumption, and framework lifecycle mismatches across multi-screen Android flows.""",
    "meta_ar": {
        "id": "PAT-13",
        "questionAr": "كيف ترتبط الكولباكات ومراقبو دورة الحياة بنمطي Flow و LiveData في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم تطور نمط Observer في أندرويد، والقدرة على المقارنة بين Callbacks و LiveData و Flow، وإدراك كيفية تحويل الكولباكات القديمة إلى Flow عبر callbackFlow، وكيفية حماية دورة الحياة في الواجهات الحديثة.",
        "why_it_matters_ar": "استخدام الكولباكات القديمة يسبب تسريبات ذاكرة وانهيارات بسبب دورة حياة أندرويد، واستخدام LiveData في طبقات الدومين يلوث المعمارية النظيفة بتبعيات أندرويد، بينما Flow يوفر الحل الشامل التفاعلي والآمن.",
        "worked_example_ar": "تحويل كولباك إلى Flow آمن بدورة الحياة:\n```kotlin\nfun observeGps(): Flow<Location> = callbackFlow {\n    val listener = GpsListener { trySend(it) }\n    gps.register(listener)\n    awaitClose { gps.unregister(listener) } // أمان تام وإلغاء تلقائي\n}\n```",
        "trade_offs_ar": "الـ Callbacks بسيطة لكنها خطيرة، والـ LiveData مريحة في الـ UI لكنها مقيدة بأندرويد والخيط الرئيسي، والـ Flow قوي ونقي لكنه يحتاج فهماً عميقاً للكوروتينات وحالات الإلغاء.",
        "failure_modes_ar": "جمع الـ Flow في الـ Activity مباشرة بدون `repeatOnLifecycle`، مما يستهلك موارد المعالج ويستمر في استقبال البيانات أثناء وجود التطبيق في الخلفية.",
        "production_perspective_ar": "في المشروعات الحديثة، نمنع استخدام LiveData نهائياً، ونعتمد على Flow النقي في الدومين والداتا، و StateFlow في الـ ViewModel، ونراقبه في الكومبوز بـ `collectAsStateWithLifecycle`.",
        "how_to_answer_ar": "اشرح أن الثلاثة تجسيد لنمط Observer عبر 3 أجيال: Callbacks (بدائي وغير مدرك للـ Lifecycle ويسرب ذاكرة)، LiveData (مدرك للـ Lifecycle ومقيد بالـ Main Thread وأندرويد)، و Flow (المعيار الحديث، نقي، يدعم Structured Concurrency وممتاز في عزل الكولباك بـ callbackFlow).",
        "talking_points_ar": "تطور نمط Observer، ومشاكل الكولباكات مع الـ Memory Leaks، ومزايا LiveData ومحدوديتها، وقوة Flow و callbackFlow و awaitClose، والمراقبة الآمنة بـ repeatOnLifecycle.",
        "follow_ups_ar": "- **المحاور:** \"ليه بنقول إن LiveData مش مناسبة لطبقات الـ Domain والـ Data؟\"\n  **المرشح:** \"لأنها مربوطة بحزمة `androidx.lifecycle` ومحصورة في الـ Main Thread، وده بيلوث نقاء الـ Domain بكود أندرويد ويمنع تشغيلها في Kotlin Multiplatform.\"\n\n- **المحاور:** \"إيه وظيفة `awaitClose` في `callbackFlow`؟\"\n  **المرشح:** \"بتعلق الكوروتين لحد ما القناة تتقفل أو الـ Scope يتلغي، وجواها بنكتب كود إلغاء تسجيل الـ Listener لمنع أي تسريب ذاكرة تلقائياً.\"",
        "self_check_ar": "هل شرحت الأجيال الثلاثة لنمط Observer؟ هل وضحت دور callbackFlow و awaitClose؟ وهل بينت كيفية مراقبة Flow بأمان في الـ UI؟",
        "references_ar": f"- [A safer way to collect flows from Android UIs](https://medium.com/androiddevelopers/a-safer-way-to-collect-flows-from-android-uis-930aa0f18838) — مقال فريق أندرويد الرسمي حول repeatOnLifecycle.\n- [Kotlin Flows in Android](https://developer.android.com/kotlin/flow) — الدليل الرسمي لاستخدام Flow في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الكولباكات و LiveData و Flow كلهم بيمثلوا نمط Observer في أندرويد عبر مراحل تطوره. الكولباكات هي الأسلوب البدائي اللي مبيعرفش أي حاجة عن دورة الحياة وبيسبب تسريبات ذاكرة لو منسيناش إلغاء تسجيله. والـ LiveData حلت المشكلة دي بربط المراقبة بحالة الـ Lifecycle لكنها كانت محبوسة في الخيط الرئيسي ومربوطة بأندرويد. أما Flow فهو المعيار الحديث الشامل؛ كود كوتلن نقي بدون تبعيات أندرويد، بيحول الكولباكات القديمة لتدفقات تفاعلية آمنة بـ `callbackFlow`، وبيراقب الحالة في الواجهة بأعلى كفاءة بـ `StateFlow`.",
        "best_answer_ar": "العلاقة بين الكولباكات و LiveData و Flow هي قصة تطور نمط الـ Observer لمواجهة تحديات دورة الحياة والبرمجة غير المتزامنة في أندرويد.\n\nفي البداية، كنا بنعتمد على الـ Callbacks والـ Listeners العادية. المشكلة الكبرى إن الكولباك أعمى تماماً عن دورة حياة أندرويد؛ فلو عملية غير متزامنة رجعت بنتيجة بعد ما المستخدم قفل الشاشة، الكولباك كان بينادي Activity مدمرة ويسبب NullPointerException أو يسرب الذاكرة بالكامل لو المطور نسي يعمل `unregister` في `onDestroy`.\n\nجوجل قدمت `LiveData` لحل الأزمة دي؛ حيث دمجت الـ LifecycleOwner في قلب نمط الـ Observer. فبقت الـ LiveData ذكية، متسلمش البيانات إلا لو الشاشة في حالة نشطة زي `STARTED` أو `RESUMED`، وتلغي المراقبة تلقائياً لما الشاشة تتدمر. لكن عيبها إنها محكومة بالـ Main Thread ومربوطة بمكتبات أندرويد، وده خلاها غير مناسبة لطبقات الدومين والداتا.\n\nحالياً، Kotlin Flow هو المعيار القياسي المعاصر. هو تدفق تفاعلي غير متزامن نقي تماماً، متعدد المنصات (Multiplatform)، وبيدعم مئات العمليات البرمجية المعقدة والـ Backpressure. بنقدر نحول أي كولباك قديم لـ Flow بأسلوب أنيق جداً باستخدام `callbackFlow` و `awaitClose`، وبنراقب الحالة في الواجهات الحديثة عبر `StateFlow` المدعوم بـ `repeatOnLifecycle`، وده بيمنحنا أعلى درجات الأمان المعماري وتوفير البطارية.",
        "deep_answer_ar": "تحت الكابوت، الانتقال من LiveData إلى Flow و StateFlow بيعكس الانتقال من نظام إشعارات مقيد بنظام التشغيل إلى نظام تدفقات متزامنة مدعوم بالـ Structured Concurrency للغة كوتلن.\n\nالـ LiveData كانت بتدير خريطة داخلية من نوع `SafeIterableMap` للمراقبين، وتفحص حالة الـ LifecycleOwner مع كل انبعاث، وده كان كافي جداً للواجهات البسيطة لكنه كان بيسبب كوارث في طبقات الـ Data والـ Domain لأنها كانت بتجبرنا نضيف مكتبات `androidx.lifecycle` في كود منطق العمل النقي، وده كسر صريح لمبادئ Clean Architecture.\n\nأما Kotlin Flow فبيشتغل باستقلالية تامة عن نظام أندرويد. في التدفقات الباردة (Cold Flows)، مفيش أي كود بيتنفذ ولا أي موارد بتتحجز في الذاكرة إلا لما يبدأ الـ Collector يطلب البيانات بـ `collect`. ودالة `callbackFlow` بتشغل الكوروتين، ولما يوصل لـ `awaitClose` بيعلق التنفيذ بأمان، وأول ما الكوروتين يتلغي بسبب قفل الشاشة، كتلة `awaitClose` بتنفذ إلغاء تسجيل الـ Listener تلقائياً بدون أي تدخل يدوي.\n\nوعلى مستوى الشاشات في Jetpack Compose، بنستخدم `StateFlow` اللي بيعتمد على المقارنات الذرية في الذاكرة (Atomic Reference Equality) لمنع إعادة الانبعاثات المتكررة. ولما ندمجه مع `collectAsStateWithLifecycle`، التطبيق بيوقف جمع التدفق فوراً أول ما الـ Activity تروح في الـ Background تحت حالة `STOPPED`، وده بيوقف كل العمليات الحسابية في المعالج ويوفر استهلاك البطارية بنسبة 100% ويقضي تماماً على أي احتمال لتسريب الذاكرة."
    }
}

# ==========================================
# PAT-14: How can an explicit state machine replace scattered boolean flags?
# ==========================================
DATA["PAT-14"] = {
    "concept_en": """An explicit state machine replaces scattered, independent boolean flags with a formalized mathematical model where a system exists in exactly one discrete, deterministic state at any given point in time. In Android UI architecture, managing screens via uncoordinated flags (such as isLoading, isError, hasData, and isRefreshing) causes combinatorial explosion ($2^N$ potential states), inevitably producing illegal, impossible screen representations (such as simultaneously rendering a loading spinner, an empty view, and an error dialog). An explicit state machine employs Kotlin sealed interfaces, explicit UI actions or intents, and a pure unidirectional reducer to enforce exhaustive compile-time handling, guaranteeing that invalid states are completely unrepresentable in the codebase.""",
    "walkthrough_en": """Refactoring scattered flags into a deterministic sealed state machine:
```kotlin
// BAD ANTI-PATTERN: Scattered boolean flags ($2^4 = 16$ possible combinations!)
class MessyViewModel : ViewModel() {
    var isLoading: Boolean = false
    var isError: Boolean = false
    var isEmpty: Boolean = false
    var data: List<Order>? = null
    // Bug: What happens if isLoading == true AND isError == true simultaneously?
}

// ARCHITECTURAL BEST PRACTICE: Explicit State Machine via Sealed Interface
sealed interface OrderUiState {
    data object Loading : OrderUiState
    data class Content(val orders: List<Order>, val isRefreshing: Boolean = false) : OrderUiState
    data class Empty(val message: String) : OrderUiState
    data class Error(val throwable: Throwable, val canRetry: Boolean) : OrderUiState
}

sealed interface OrderUiIntent {
    data object Load : OrderUiIntent
    data object Refresh : OrderUiIntent
    data class Retry(val orderId: String) : OrderUiIntent
}

// Pure State Reducer: Deterministic transitions without illegal states
fun reduceOrderState(current: OrderUiState, intent: OrderUiIntent): OrderUiState = when (intent) {
    is OrderUiIntent.Load -> OrderUiState.Loading
    is OrderUiIntent.Refresh -> when (current) {
        is OrderUiState.Content -> current.copy(isRefreshing = true)
        else -> current
    }
    is OrderUiIntent.Retry -> OrderUiState.Loading
}
```""",
    "short_en": """Scattered boolean flags create $2^N$ combinatorial states, inevitably producing illegal screen conditions such as displaying a progress spinner and an error banner simultaneously. An explicit state machine replaces independent flags with a single Kotlin sealed interface representing mutually exclusive screen states, paired with explicit user intents and a deterministic reducer function. This architectural pattern guarantees that illegal states are mathematically unrepresentable at compile time.""",
    "structured_en": """Replacing uncoordinated boolean flags with an explicit state machine transforms volatile presentation code into a deterministic, bug-free architecture.
When screen state is represented by multiple mutable booleans like isLoading, isError, isSuccess, and isOffline, the number of potential screen states scales exponentially as two to the power of N. With only four flags, sixteen state combinations exist. In reality, the screen should only occupy one valid mode at a time: either it is loading, displaying content, showing an empty placeholder, or displaying a critical error. Independent booleans invite race conditions and logic oversights where developers forget to reset one flag while toggling another, leading to visual corruption and conflicting UI layouts.
An explicit state machine resolves this by enforcing the principle of making illegal states unrepresentable.
By modeling the screen using a Kotlin sealed interface or sealed class, states such as Loading, Content, and Error become mutually exclusive. A screen cannot simultaneously be in Loading and Error states because the state variable holds a single, discrete type.
Furthermore, user interactions are formalized as explicit Intents, and state transitions are governed by a reducer function. This structure forms the foundation of modern MVI and Unidirectional Data Flow, delivering predictable screen lifecycles, clear telemetry tracking, and effortless unit test verification.""",
    "deep_senior_en": """Under the hood, explicit state machines replace runtime defensive conditional checks with compile-time exhaustive verification using Kotlin's when construct.
When a sealed interface models the state, the Kotlin compiler enforces exhaustive branch evaluation without requiring an else fallback. If a senior engineer adds a new state variant, such as ReauthenticatingRequired or PartialOfflineSync, the compiler immediately flags every when expression across ViewModels, Jetpack Compose renderers, and analytics interceptors that fails to handle the new state. This transforms potential production edge-case crashes into deterministic compilation errors.
Furthermore, separating state representation from transition logic enables unidirectional determinism. In high-performance Android applications, the state machine reducer is modeled as a pure mathematical function: (CurrentState, Intent) -> NextState. Because the reducer has zero side effects, state transitions can be audited, replayed, and verified with deterministic JVM unit tests in milliseconds.
Side effects (such as displaying a temporary Toast, triggering a navigation event, or initiating a biometric prompt) are separated into a dedicated one-off effect channel (such as Channel<UiEffect> with receiveAsFlow), preventing transient events from corrupting the persistent state machine. This architectural boundary ensures that screen state surviving process recreation or configuration changes always represents a valid, cohesive snapshot of application domain state. Additionally, snapshot-based UI testing frameworks can assert pixel-perfect UI rendering against each discrete state variant in isolation, dramatically accelerating regression testing and eliminating visual drift.""",
    "meta_ar": {
        "id": "PAT-14",
        "questionAr": "كيف يمكن لآلة الحالة الصريحة (Explicit State Machine) أن تحل محل الأعلام المنطقية (Boolean Flags) المشتتة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ جعل الحالات غير الصالحة مستحيلة التمثيل (Making illegal states unrepresentable)، والقدرة على شرح مشاكل الانفجار التوافقي (Combinatorial Explosion)، وتطبيق نمط آلة الحالة عبر Sealed Interfaces و Reducers في معمارية MVI/UDF.",
        "why_it_matters_ar": "استخدام متغيرات Boolean متعددة للتحكم في الشاشة ينتج عنه واجهات متضاربة كعرض مؤشر التحميل مع شاشة الخطأ في نفس اللحظة، ويجعل تتبع الأخطاء واختبار الشاشات شديد الصعوبة.",
        "worked_example_ar": "استبدال الـ Booleans بـ Sealed Interface:\n```kotlin\n// كود سيئ: أعلام مشتتة (16 حالة متضاربة)\nvar isLoading = false; var isError = false\n// كود نظيف: آلة حالة صريحة ومانعة للتضارب\nsealed interface ScreenState {\n    data object Loading : ScreenState\n    data class Content(val data: List<Item>) : ScreenState\n    data class Error(val ex: Throwable) : ScreenState\n}\n```",
        "trade_offs_ar": "يتطلب كتابة كلاسات وحالات إضافية في البداية، لكنه يقضي تماماً على حالات التضارب ويوفر فحصاً شاملاً وقت الـ Compilation وسهولة فائقة في الاختبار.",
        "failure_modes_ar": "وضع أحداث لمرة واحدة (One-off events) زي الـ Navigation أو الـ SnackBar داخل كائن الحالة الدائم مما يسبب تكرارها عند تدوير الشاشة.",
        "production_perspective_ar": "في تطبيقات أندرويد المعاصرة المعتمدة على Compose، نلزم كل الشاشات بنموذج UDF؛ حالة واحدة مغلقة (Single Sealed State)، وأحداث صريحة (Intents)، ودالة Reducer نقية لحساب الحالة القادمة.",
        "how_to_answer_ar": "ابدأ بمشكلة الأعلام المشتتة: الانفجار التوافقي (2 أس N) اللي بيسمح بظهور حالات مستحيلة، واشرح الحل عبر آلة حالة صريحة باستخدام Sealed Interfaces حيث توجد حالة واحدة حصرية في أي لحظة، واذكر دور الـ Reducer والتحقق الصارم في وقت الـ Compile time.",
        "talking_points_ar": "مفهوم Making illegal states unrepresentable، ومشاكل الـ Combinatorial Explosion، وقوة Sealed Interfaces والتحقق الإلزامي بـ when، وفصل الـ Side Effects عن الـ State.",
        "follow_ups_ar": "- **المحاور:** \"كيف يتعامل الـ State Machine مع الأحداث المؤقتة زي إظهار Toast أو التنقل؟\"\n  **المرشح:** \"بنعزلها تماماً عن الـ State في قناة أحداث منفصلة (One-off Effects) باستخدام `Channel<Effect>`؛ لأن الحالة بتمثل ما يُعرض دائماً، بينما التأثير هو حدث لحظي يُستهلك مرة واحدة.\"\n\n- **المحاور:** \"ما هي ميزة الـ Reducer النقي (Pure Reducer) في آلة الحالة؟\"\n  **المرشح:** \"لأنه دالة نقية بتاخد الحالة الحالية والحدث وترجع الحالة الجديدة بدون أي Side effects، فبنقدر نختبر كل انتقالات الشاشة في ثوانٍ باختبارات JVM بسيطة ومضمونة.\"",
        "self_check_ar": "هل شرحت الانفجار التوافقي (2 أس N)؟ هل وضحت مبدأ استحالة الحالات غير الصالحة؟ وهل بينت كيفية استخدام Sealed Interface والـ Reducer؟",
        "references_ar": f"- [Guide to UI layer and State production](https://developer.android.com/topic/architecture/ui-layer/state-production) — التوثيق الرسمي لجوجل حول إنتاج حالات الشاشة.\n- [Making Illegal States Unrepresentable](https://kentcdodds.com/blog/make-impossible-states-impossible) — المفهوم المعماري لجعل الحالات المستحيلة غير قابلة للتمثيل.",
        "quick_answer_ar": "الأعلام المنطقية (Boolean Flags) المشتتة زي `isLoading` و `isError` بتخلق انفجاراً توافقياً للاحتمالات ($2^N$)، وده بيسمح بظهور حالات متضاربة ومستحيلة برمجياً زي ظهور لودينج وشاشة خطأ في نفس الوقت. آلة الحالة الصريحة (Explicit State Machine) بتستبدل كل الأعلام دي بكائن واحد مغلق باستخدام Kotlin `sealed interface` بيمثل الحالات الحصرية للشاشة، ومعاها أحداث واضحة ودالة Reducer نقية، وده بيخلي الحالات المستحيلة غير قابلة للتمثيل أصلاً في وقت الـ Compilation.",
        "best_answer_ar": "لما بنبني شاشات أندرويد بالاعتماد على متغيرات Boolean منفصلة زي `isLoading` و `isError` و `hasData` و `isRefreshing`، إحنا بندخل في مصيدة معمارية خطيرة جداً.\n\nالمشكلة الرياضية هنا هي الانفجار التوافقي؛ لو عندك 4 أعلام، بقى عندك 16 احتمال لحالة الشاشة! ومع كثرة الكود والعمليات غير المتزامنة، مفيش أي ضمان إن مطور مينساش يصفر علم الـ Loading لما يحصل Error، والنتيجة إن المستخدم يشوف Spinner بيلف فوق رسالة خطأ، أو شاشة بيضاء مفيهاش أي عناصر.\n\nالحل الهندسي الصحيح هو بناء آلة حالة صريحة (Explicit State Machine) لتطبيق مبدأ جعل الحالات غير الصالحة مستحيلة التمثيل (Making illegal states unrepresentable). بنعرف الشاشة باستخدام Kotlin `sealed interface` بيحتوي على الحالات الحصرية الممكنة فقط: إما `Loading`، أو `Content`، أو `Error`، أو `Empty`. وبكده الشاشة يستحيل تكون في حالتين مع بعض في نفس اللحظة لأن المتغير بيشيل كائناً واحداً فقط.\n\nوبنكمل المنظومة بأحداث صريحة (Intents) بتمر على دالة تحويل نقية (Reducer) بتحسب الحالة التالية بدقة. الطريقة دي بتخلي الشاشة متوقعة بنسبة 100%، وسهلة جداً في الاختبار، وبتوفر تجربة مستخدم خالية تماماً من العيوب البصرية.",
        "deep_answer_ar": "تحت الكابوت، آلة الحالة الصريحة بتستبدل الفحص الدفاعي العشوائي في وقت التشغيل (Runtime Checks) بفحص إلزامي وحاسم من كومبايلر كوتلن في وقت الـ Compilation.\n\nباستخدام الـ `sealed interface`، كومبايلر كوتلن بيجبرك تفحص كل الحالات الممكنة في تعبير `when` بدون الحاجة لكتابة فرع `else` افتراضي. فلو الفريق قرر يضيف حالة جديدة زي `Reauthenticating`، الكومبايلر هيرفض يكمل الـ Build وهيطلع لك أخطاء فورية في كل مكان بيتعامل مع الشاشة لضمان معالجة الحالة الجديدة، وده بيمنع أي Crash مفاجئ عند المستخدمين في الإنتاج.\n\nكمان عزل منطق الانتقالات داخل دالة Reducer نقية: `(CurrentState, Intent) -> NextState` بيدينا ميزة معمارية جبارة؛ لأن الـ Reducer خالي تماماً من الآثار الجانبية (Pure Function)، فبنقدر نختبر كل مسارات وانتقالات التطبيق باختبارات Unit Tests فائقة السرعة على الـ JVM بدون الحاجة لمحاكي أندرويد إطلاقاً.\n\nوبالنسبة للأحداث المؤقتة اللي بتحصل مرة واحدة زي الـ Toast أو الـ Navigation، بنعزلها تماماً عن كائن الحالة الدائم في قناة مستقلة `Channel<UiEffect>`؛ لأن تخزين رسالة الخطأ المؤقتة في الـ State هيخليها تظهر تاني وتالت كل ما المستخدم يدور الشاشة والـ Activity يُعاد إنشاؤها. ده اللي بيضمن إن حالة الشاشة تفضل نقية وممثلة للواقع بدقة."
    }
}

# ==========================================
# PAT-15: Design multiple payment providers with Strategy or Factory. How do you avoid a god-factory?
# ==========================================
DATA["PAT-15"] = {
    "concept_en": """Architecting multiple payment provider integrations requires combining the Strategy pattern for polymorphic payment execution with a decoupled creation mechanism, such as Dagger/Hilt Multibindings, to avoid creating an anti-pattern God Factory. In a naive design, a centralized factory switch-statement hardcodes constructor references to every concrete payment gateway (such as Stripe, PayPal, GooglePay, and Klarna), violating the Open/Closed Principle whenever a new provider is added. By decoupling creation into a distributed map of provider factories using dependency injection multibindings, new payment strategies register themselves modularly at compile time, allowing the system to resolve strategies dynamically without central monolithic coupling.""",
    "walkthrough_en": """Decoupling multiple payment strategies using Dagger Multibindings:
```kotlin
// 1. Unified Domain Strategy Interface
interface PaymentStrategy {
    val method: PaymentMethod
    suspend fun executePayment(amountCents: Long, currency: String): Result<PaymentReceipt>
}

// 2. Concrete Strategy implementations (Isolated in independent modules)
class StripePaymentStrategy @Inject constructor(private val stripeClient: StripeClient) : PaymentStrategy {
    override val method = PaymentMethod.STRIPE
    override suspend fun executePayment(amountCents: Long, currency: String) = stripeClient.charge(amountCents)
}

class PayPalPaymentStrategy @Inject constructor(private val payPalSdk: PayPalSdk) : PaymentStrategy {
    override val method = PaymentMethod.PAYPAL
    override suspend fun executePayment(amountCents: Long, currency: String) = payPalSdk.checkout(amountCents)
}

// 3. Extensible Multi-binding Module (Eliminates God Factory switch-statements!)
@Module
@InstallIn(SingletonComponent::class)
abstract class PaymentModule {
    @Binds @IntoMap @PaymentMethodKey(PaymentMethod.STRIPE)
    abstract fun bindStripe(impl: StripePaymentStrategy): PaymentStrategy

    @Binds @IntoMap @PaymentMethodKey(PaymentMethod.PAYPAL)
    abstract fun bindPayPal(impl: PayPalPaymentStrategy): PaymentStrategy
}

// 4. Client Resolver (Open/Closed: never needs modification when new providers are added!)
class PaymentProcessor @Inject constructor(
    private val strategies: Map<PaymentMethod, @JvmSuppressWildcards Provider<PaymentStrategy>>
) {
    suspend fun process(method: PaymentMethod, amount: Long, currency: String): Result<PaymentReceipt> {
        val strategyProvider = strategies[method] ?: return Result.failure(UnsupportedPaymentException(method))
        return strategyProvider.get().executePayment(amount, currency)
    }
}
```""",
    "short_en": """To design multiple payment providers without a God Factory, combine the Strategy pattern with Dagger/Hilt Multibindings. Define a unified PaymentStrategy interface implemented by isolated payment adapters. Instead of hardcoding all providers into a monolithic factory switch-statement that violates the Open/Closed Principle, use multibindings to inject a Map of provider factories. Adding a new payment provider requires only binding the new strategy in its own module, leaving existing processor code untouched.""",
    "structured_en": """Designing a scalable multi-provider payment architecture requires separating algorithmic strategy execution from provider instantiation mechanics.
The traditional pitfall in payment architecture is creating a God Factory. In this anti-pattern, a single factory class contains a massive switch or when block that directly instantiates Stripe, PayPal, Adyen, and crypto providers. This violates the Open/Closed Principle: every time a payment vendor is added, modified, or decommissioned, the shared factory file must be edited, recompiled, and retested, creating merge conflicts and tight coupling across independent vendor dependencies.
To solve this cleanly, architects implement the Strategy pattern alongside distributed dependency injection.
First, a clean PaymentStrategy interface establishes a common contract for processing transactions, handling two-factor authentication callbacks, and returning standardized receipts. Each concrete payment provider implements this strategy within an isolated feature or infrastructure module.
To avoid the God Factory, the system uses Dagger/Hilt Multibindings to collect strategies into a map: Map<PaymentMethod, Provider<PaymentStrategy>>. Each module contributes its own strategy binding using @IntoMap and a custom key annotation.
The calling PaymentProcessor simply queries the injected map at runtime. Adding a new payment provider involves authoring the new class and registering its binding, achieving complete extensibility without altering a single line of existing orchestrator code.""",
    "deep_senior_en": """Under the hood, using Provider<PaymentStrategy> inside the injected map is essential for memory efficiency, cold-start latency, and classloading optimization.
If the map injected direct strategy instances: Map<PaymentMethod, PaymentStrategy>, the dependency injection container would be forced to eagerly initialize every payment SDK, allocate network pools, and load foreign vendor native libraries during application launch, severely degrading cold startup time even if the user never opens the checkout flow.
By wrapping each map value in a Dagger Provider, strategies are instantiated lazily on demand. The vendor SDK and its associated memory footprint are only allocated when the user explicitly taps that specific payment option.
Furthermore, this architecture enforces strict multi-module compilation boundaries. Each payment gateway can reside in its own isolated Gradle module, such as :feature:payment:stripe and :feature:payment:paypal. These implementation modules depend on the abstract payment contract module, while the app module combines them via Gradle dependencies.
This separation allows Gradle to build payment modules in parallel, isolates sensitive third-party SDK dependencies from core domain logic, and enables dynamic feature delivery where rarely used payment gateways can be downloaded on demand via Android Play Feature Delivery. Furthermore, incorporating Circuit Breaker or Retry decorators around individual payment strategies shields the core checkout flow against transient vendor outages, providing predictable failover mechanisms without polluting strategy logic.""",
    "meta_ar": {
        "id": "PAT-15",
        "questionAr": "كيف تصمم نظاماً يدعم عدة مزودي دفع باستخدام Strategy أو Factory مع تجنب الوقوع في فخ الـ God-Factory؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم نظام مدفوعات متعدد وقابل للتوسع، وتطبيق مبدأ Open/Closed Principle، واستخدام نمط Strategy مع Dagger Multibindings لتفادي المصانع المركزية الضخمة (God Factory).",
        "why_it_matters_ar": "الـ God Factory بيجمع كل تبعيات الـ SDKs في كلاس واحد كبير، وأي إضافة لبوابة دفع جديدة بتجبر الفريق يعدل نفس الكلاس المركزي ويعيد بناء واختبار كل البوابات التانية، وده كسر صريح لمعايير النظافة المعمارية.",
        "worked_example_ar": "تجنب الـ God Factory بحقن خريطة من الـ Strategies عبر Dagger:\n```kotlin\n// إنترفيس موحد للـ Strategy\ninterface PayStrategy { suspend fun pay(amount: Long) }\n// حقن خريطة مزودي الدفع تلقائياً بدون switch/when\nclass PayProcessor @Inject constructor(\n    val map: Map<PayMethod, @JvmSuppressWildcards Provider<PayStrategy>>\n) {\n    suspend fun process(m: PayMethod) = map[m]?.get()?.pay(100)\n}\n```",
        "trade_offs_ar": "يتطلب إعداد Multibindings ورموز مفاتيح مخصصة في Dagger، لكنه يمنح استقلالية تامة للموديولات وإمكانية إضافة بوابات دفع جديدة بدون تعديل الكود القديم نهائياً.",
        "failure_modes_ar": "حقن كائنات الـ Strategy مباشرة بدلاً من `Provider<T>`، مما يجبر التطبيق على تحميل وتهيئة كل مكتبات الدفع في الذاكرة عند بداية التشغيل.",
        "production_perspective_ar": "في تطبيقات التجارة الإلكترونية الكبرى، نضع كل بوابة دفع في موديول مستقل تماماً، ونستخدم Hilt Multibindings لتسجيل البوابات تلقائياً في الـ Checkout Flow بدون أي كلاس مركزي جامع.",
        "how_to_answer_ar": "ابدأ بتعريف الـ God Factory ومخاطرها (كسر Open/Closed وازدحام التبعيات)، ثم اعرض الحل: استخدام نمط Strategy لعقد الدفع، واستخدام Dagger/Hilt Multibindings لحقن خريطة `Map<PaymentMethod, Provider<PaymentStrategy>>`، واشرح ميزة استخدام `Provider` في التحميل الكسول وتوفير الرام.",
        "talking_points_ar": "مبدأ Open/Closed Principle، وعيوب الـ God Factory وكتل when الضخمة، ودور Dagger Multibindings، وأهمية `Provider<T>` في الـ Lazy Initialization وتوفير وقت تشغيل التطبيق.",
        "follow_ups_ar": "- **المحاور:** \"ليه بنستخدم `Provider<PaymentStrategy>` داخل الخريطة مش الكائن مباشرة؟\"\n  **المرشح:** \"عشان الـ Lazy Loading؛ مش معقول أول ما التطبيق يفتح نقوم مهيئين الـ SDK بتاع PayPal و Stripe ونحجز ذاكرة وشبكة لكل المزودين حتى لو المستخدم مش هيشتري حاجة، الـ Provider بينشئ الكائن فقط لحظة الدفع.\"\n\n- **المحاور:** \"إزاي ده بيأثر على تقسيم الموديولات في Gradle؟\"\n  **المرشح:** \"كل مزود دفع بيتحط في موديول منفصل بيعتمد على موديول الـ Contract، والموديولات بتتبني بالتوازي، وبنقدر حتى ننزل المزود كـ Dynamic Feature Module عند الحاجة فقط.\"",
        "self_check_ar": "هل شرحت عيوب الـ God Factory بوضوح؟ هل وضحت آلية Dagger Multibindings؟ وهل بينت أهمية التحميل الكسول عبر Provider؟",
        "references_ar": f"- [Dagger Multibindings](https://dagger.dev/dev-guide/multibindings.html) — الدليل الرسمي لحقن الخرائط والمجموعات في Dagger.\n- [Open–Closed Principle](https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle) — مبدأ الفتح والإغلاق المعماري.",
        "quick_answer_ar": "عشان نصمم نظام بوابات دفع متعددة بدون ما نقع في فخ الـ God Factory، بنجمع بين نمط Strategy ونظام الـ Multibindings في Dagger أو Hilt. بنعرف إنترفيس موحد `PaymentStrategy` بيمثل عقد الدفع، وكل بوابة بتنفذه في كلاس منفصل ومستقل. وبدل ما نعمل كلاس مصنع مركزي فيه switch-case ضخمة بتجمع كل التبعيات وتكسر مبدأ Open/Closed، بنخلي كل بوابة تسجل نفسها تلقائياً في خريطة `Map<PaymentMethod, Provider<PaymentStrategy>>` عبر مكتبة الـ DI. وبكده نقدر نضيف أي بوابة دفع جديدة بدون ما نعدل أو نلمس سطر واحد في الكود القديم.",
        "best_answer_ar": "المشكلة الكبرى اللي بنشوفها في تصميم أنظمة الدفع هي الـ God Factory؛ وهو كلاس مصنع مركزي ضخم بيحتوي على جملة `when` عملاقة بتعمل Initialize لكل بوابات الدفع زي Stripe و PayPal و Google Pay في مكان واحد. الكود ده بيكسر صراحة مبدأ Open/Closed Principle؛ لأنك كل ما تضيف بوابة جديدة، بتضطر تعدل نفس الكلاس المركزي، وتجمع كل الـ SDKs في نفس المكان، وتخلق احتمالات تعارض دمج (Merge Conflicts) مستمرة بين أعضاء الفريق.\n\nالتصميم الهندسي المتين بيعتمد على دمج نمط Strategy مع الـ Multibindings في Dagger أو Hilt.\n\nأول خطوة هي تعريف إنترفيس نظيف `PaymentStrategy` في طبقة الدومين بيمثل عقد الدفع، وكل بوابة دفع بتعمل له تنفيذ خاص بيها في موديولها المستقل.\n\nالخطوة التانية هي تجنب المصنع المركزي؛ بنستخدم ميزة `@IntoMap` في Dagger لربط كل استراتيجية دفع بنوعها في خريطة موحدة: `Map<PaymentMethod, Provider<PaymentStrategy>>`.\n\nالكلاس المسؤول عن الدفع (PaymentProcessor) بيستقبل الخريطة دي جاهزة في الكونستركتور، وبمجرد ما المستخدم يختار وسيلة الدفع، بنجيب الـ Strategy المقابلة من الخريطة ونفذها. بكده لو أردنا إضافة مزود جديد، بنكتب الكلاس بتاعه والـ Binding بتاعه فقط، بدون ما نلمس أي كود موجود مسبقاً في النظام.",
        "deep_answer_ar": "تحت الكابوت، استخدام `Provider<PaymentStrategy>` داخل الخريطة المحقونة مش رفاهية شكلية، بل هو قرار معماري حاسم لأداء الذاكرة وسرعة إقلاع التطبيق (App Cold Start).\n\nلو قمنا بحقن كائنات الاستراتيجيات مباشرة كـ `Map<PaymentMethod, PaymentStrategy>`، حاوية الحقن (DI Container) هتضطر تنشئ كل كائنات بوابات الدفع وتهيء كل الـ SDKs الخارجية وتحجز الـ Connection Pools ومكتبات الـ C++ التابعة ليها في الـ Heap أول ما التطبيق يفتح، حتى لو المستخدم فتح التطبيق عشان يقرا مقال ومش هيشتري حاجة أصلاً. استخدام `Provider` بيضمن التحميل الكسول (Lazy Instantiation)؛ يعني الـ SDK مش هيتم بناؤه ولا استهلاك بايت واحد من الرام عشانه إلا في اللحظة اللي المستخدم يضغط فيها فعلياً على زرار الدفع الخاص بيه.\n\nمعمارياً، التصميم ده بيخدم استراتيجية الـ Modularization بشكل عبقري؛ بنقدر نحط كل بوابة دفع في موديول Gradle منفصل تماماً، زي `:feature:payment:stripe` و `:feature:payment:paypal`، والموديولات دي بتعتمد فقط على موديول الـ Interface العام. ده بيسمح لـ Gradle إنه يبني موديولات الدفع دي بالتوازي (Parallel Build)، وبيقلل وقت الـ CI/CD بشكل ملحوظ.\n\nوفوق كل ده، التصميم ده بيمهد الطريق لتقنية Play Feature Delivery؛ حيث يمكن تنزيل بوابات الدفع الإقليمية أو نادرة الاستخدام كـ Dynamic Feature Modules عند الطلب من متجر جوجل بلاي وتوصيلها في خريطة الـ DI بسلاسة تامة وبدون زيادة الحجم المبدئي للتطبيق عند التحميل."
    }
}

# ==========================================
# PAT-16: You need to swap vendor SDKs with different callbacks. Which patterns and boundaries help?
# ==========================================
DATA["PAT-16"] = {
    "concept_en": """Swapping vendor SDKs with disparate callback architectures requires establishing a strict Anti-Corruption Layer (ACL) using the Adapter and Facade patterns bounded by clean architectural seams. Third-party vendors invariably expose conflicting callback styles, including single-listener interfaces, multi-callback delegates, broadcast intents, or bespoke event dispatchers. By defining an application-owned, domain-level interface and implementing an Adapter that translates vendor-specific event protocols into standard Kotlin Coroutines and asynchronous Flows, the application isolates vendor volatility completely. Placing this adapter inside an independent Gradle compilation module guarantees that switching vendor providers requires changing only the boundary implementation without modifying domain or presentation code.""",
    "walkthrough_en": """Isolating and adapting incompatible vendor SDKs behind an Anti-Corruption Layer:
```kotlin
// 1. DOMAIN BOUNDARY: Application-owned interface (Pure Kotlin, zero vendor types)
interface LocationTracker {
    val locationStream: Flow<GeoCoordinates>
    suspend fun getCurrentLocation(): Result<GeoCoordinates>
}

// 2. ADAPTER FOR VENDOR A (Push-based listener interface)
class VendorALocationAdapter @Inject constructor(
    private val vendorAClient: VendorASdkClient
) : LocationTracker {
    override val locationStream: Flow<GeoCoordinates> = callbackFlow {
        val listener = object : VendorAListener {
            override fun onNewCoord(lat: Double, lng: Double) { trySend(GeoCoordinates(lat, lng)) }
            override fun onFailed(err: String) { close(VendorException(err)) }
        }
        vendorAClient.startTracking(listener)
        awaitClose { vendorAClient.stopTracking() }
    }

    override suspend fun getCurrentLocation(): Result<GeoCoordinates> =
        locationStream.firstOrNull()?.let { Result.success(it) } ?: Result.failure(TimeoutException())
}

// 3. ADAPTER FOR VENDOR B (Delegate-based with distinct callbacks)
class VendorBLocationAdapter @Inject constructor(
    private val vendorBEngine: VendorBEngine
) : LocationTracker {
    override val locationStream: Flow<GeoCoordinates> = callbackFlow {
        val delegate = VendorBDelegate { event ->
            if (event.type == VendorBEvent.GPS_FIX) trySend(GeoCoordinates(event.latitude, event.longitude))
        }
        vendorBEngine.addDelegate(delegate)
        awaitClose { vendorBEngine.removeDelegate(delegate) }
    }

    override suspend fun getCurrentLocation(): Result<GeoCoordinates> = suspendCancellableCoroutine { cont ->
        vendorBEngine.requestSingleUpdate { fix -> cont.resume(Result.success(GeoCoordinates(fix.lat, fix.lng))) }
    }
}
```""",
    "short_en": """To swap vendor SDKs with conflicting callbacks cleanly, establish an Anti-Corruption Layer using the Adapter pattern behind an application-owned domain interface. The Adapter bridges mismatched vendor listeners, delegates, and threading models into standardized Kotlin suspending functions and Flow streams via callbackFlow. Isolating the vendor SDK inside its own Gradle module ensures that swapping vendors touches only the adapter implementation, keeping domain and presentation layers completely decoupled.""",
    "structured_en": """Swapping vendor SDKs with completely different callback interfaces requires disciplined architectural boundary design to prevent vendor churn from destabilizing the core codebase.
The primary danger when integrating third-party SDKs is letting foreign types and idiosyncratic callback contracts leak into UseCases, Repositories, and ViewModels. One analytics or location vendor might use a single callback interface with multiple methods, while another uses individual functional delegates, and a third relies on Android BroadcastReceivers. If application code couples to these specific mechanics, migrating from Vendor A to Vendor B requires rewriting hundreds of callsites across the entire application.
The definitive architectural pattern to solve this is the Adapter pattern operating within an Anti-Corruption Layer.
First, the engineering team defines an application-owned domain interface that describes the required capability using pure Kotlin types, such as exposing a Flow of domain locations or suspending functions returning Result.
Second, an Adapter class encapsulates the concrete vendor SDK. The adapter is responsible for structural translation: it maps vendor initialization sequences, registers internal vendor listeners, and routes asynchronous events into standard Kotlin primitives using callbackFlow with awaitClose for streams and suspendCancellableCoroutine for one-shot requests.
Third, the adapter is isolated within a dedicated Gradle module, ensuring that dependency injection simply swaps the bound adapter implementation without altering any application logic.""",
    "deep_senior_en": """Under the hood, managing asynchronous callback impedance mismatches requires meticulous handling of cancellation, threading, and backpressure translation.
Different vendor SDKs employ radically different threading guarantees: some invoke callbacks on the main UI thread, while others spawn unmanaged background daemon threads. Inside the Adapter, senior engineers normalize threading using flowOn(Dispatchers.IO) or Dispatchers.Default, ensuring that downstream consumers receive predictable execution contexts.
Furthermore, bridging callbacks into Coroutines demands rigorous lifecycle cleanup. When wrapping streaming callbacks inside callbackFlow, the awaitClose block must invoke the vendor's unregistration API. If an unhandled exception or cancellation signal occurs downstream, the Coroutine runtime automatically invokes awaitClose, preventing the vendor SDK from continuing to poll hardware sensors or fire orphaned callbacks.
For one-shot callbacks wrapped via suspendCancellableCoroutine, developers must check continuation.isActive and attach invokeOnCancellation to signal the vendor SDK to abort inflight network requests.
By enforcing this boundary at the Gradle module level using implementation dependencies, the vendor SDK bytecode is physically hidden from other modules, making accidental coupling impossible and allowing seamless provider replacement through a single Hilt @Binds declaration. Moreover, senior engineers implement mock and replay adapters to simulate extreme vendor edge cases, such as simulated satellite signal loss or malformed payload responses, enabling thorough offline automated verification before deploying partner SDKs to production.""",
    "meta_ar": {
        "id": "PAT-16",
        "questionAr": "عند الحاجة لاستبدال مكتبة خارجية (Vendor SDK) بأخرى تملك كولباكات مختلفة تماماً، ما هي الأنماط والحدود المعمارية التي تساعدك؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم كيفية تطبيق نمط Adapter وطبقة مكافحة الفساد (Anti-Corruption Layer)، والقدرة على توحيد آليات الكولباك المختلفة وتحويلها لكوروتينات وتدفقات Flow، وعزل التبعيات على مستوى موديولات Gradle.",
        "why_it_matters_ar": "الاعتماد المباشر على واجهات وكولباكات الشركات الخارجية يجعل التطبيق أسيراً لتلك الشركات؛ وأي استبدال أو تحديث للمكتبة يتحول إلى مشروع إعادة كتابة شامل ومكلف وعالي المخاطر.",
        "worked_example_ar": "عزل كولباكات مزودين مختلفين وراء واجهة أندرويد موحدة:\n```kotlin\n// واجهة الدومين النظيفة\ninterface LocationEngine { val stream: Flow<Location> }\n// محول المزود الأول بـ callbackFlow\nclass ProviderAAdapter(val sdkA: SdkA) : LocationEngine {\n    override val stream = callbackFlow { sdkA.listen { trySend(it) }; awaitClose { sdkA.stop() } }\n}\n```",
        "trade_offs_ar": "يتطلب كتابة كلاسات Adapter ونماذج Mappers إضافية، لكنه يمنح مرونة مطلقة تتيح تبديل المزود الخارجي بالكامل في دقائق عبر تعديل سطر واحد في Hilt.",
        "failure_modes_ar": "تسريب كائنات أو استثناءات الـ SDK الخارجية للـ UseCases، أو نسيان إلغاء تسجيل الكولباك في `awaitClose` مما يسبب تسريب طاقة وبطارية مستمر.",
        "production_perspective_ar": "في التطبيقات الضخمة، تُعزل مكتبات الـ Tracking أو الـ Maps في موديولات مستقلة تماماً، ويتم توحيد كل الكولباكات في `Flow` أو `suspend fun`، ويتم التبديل بين الشركات عبر الـ Remote Config أو الـ DI.",
        "how_to_answer_ar": "اشرح الحل كمنظومة متكاملة: تعريف إنترفيس نظيف في الدومين (Boundary)، واستخدام نمط Adapter لتحويل كولباكات الـ SDK المختلفة إلى Coroutines و Flow عبر `callbackFlow` و `awaitClose`، وعزل الـ SDK داخل موديول Gradle منفصل كـ Anti-Corruption Layer.",
        "talking_points_ar": "نمط Adapter كطبقة Anti-Corruption Layer، وتوحيد الكولباكات عبر callbackFlow و suspendCancellableCoroutine، وإدارة الـ Threading بـ flowOn، وعزل الموديولات بـ Gradle implementation.",
        "follow_ups_ar": "- **المحاور:** \"كيف يتعامل الـ Adapter مع اختلاف الخيوط (Threading) بين الـ SDKs؟\"\n  **المرشح:** \"الـ Adapter بيعمل Normalization للخيوط؛ باستخدام `flowOn(Dispatchers.IO)` أو `withContext` بنضمن إن كل البيانات تخرج للـ Domain على خيط منضبط ومحدد مسبقاً بغض النظر الـ SDK شغال إزاي داخلياً.\"\n\n- **المحاور:** \"ماذا لو كان الـ SDK القديم شغال بـ Push والجديد شغال بـ Polling؟\"\n  **المرشح:** \"الـ Adapter هو اللي بيتحمل الفرق ده؛ في حالة الـ Polling يقدر يعمل Coroutine دورية تسحب البيانات وتبعثها في نفس الـ Flow بدون ما طبقة العرض تعرف أي تفاصيل.\"",
        "self_check_ar": "هل شرحت نمط Adapter ودوره كـ Anti-Corruption Layer؟ هل وضحت استخدام callbackFlow و suspendCancellableCoroutine؟ وهل بينت عزل الموديولات في Gradle؟",
        "references_ar": f"- [Adapter Pattern](https://refactoring.guru/design-patterns/adapter) — الدليل المرجعي لنمط المحول الهيكلي.\n- [Bridging callbacks to Coroutines](https://developer.android.com/kotlin/coroutines/coroutines-adv#manage-cancellation) — التوثيق الرسمي لجوجل حول تحويل الكولباكات لكوروتينات.",
        "quick_answer_ar": "عشان نستبدل مكتبات خارجية بكولباكات مختلفة بدون ما نأذي التطبيق، بنبني طبقة حماية معمارية (Anti-Corruption Layer) بالاعتماد على نمط Adapter. بنعرف إنترفيس نظيف في طبقة الدومين بيمثل الوظيفة المطلوبة بلغة كوتلن النقية. وبنبني كلاس Adapter خاص بكل مكتبة يتولى تحويل الكولباكات الخاصة بيها لدوال معلقة (Suspending functions) أو تدفقات `Flow` باستخدام `callbackFlow` و `awaitClose`. وبنعزل كل مكتبة في موديول Gradle منفصل، وبكده نقدر نبدل المزود بالكامل بمجرد تغيير سطر واحد في Hilt.",
        "best_answer_ar": "الخطر الأكبر في دمج الـ SDKs الخارجية هو تسرب واجهاتها وطرق عملها لقلب التطبيق؛ فلو شركة بتعتمد على Single Listener وشركة تانية بتعتمد على Delegate بكولباكات متعددة، وسمحنا لكود الشاشات بالتعامل المباشر معاهم، استبدال المزود هيتحول لكابوس يعيد كتابة مئات الملفات في التطبيق.\n\nالحل المعماري القياسي بيتكون من 3 خطوات متكاملة:\nأولاً، فرض حد معماري صارم (Architectural Boundary)؛ بنعرف Interface نظيف في موديول الـ Domain بيعبر عن الخدمة بألفاظ التطبيق بتاعنا، وبيرجع بيانات ناتجة على شكل `Flow<T>` للتدفقات أو `Result<T>` للطلبات الفردية.\n\nثانياً، تطبيق نمط Adapter؛ بنبني كلاس Adapter بياخد الـ SDK المعقدة ويترجم أحداثها. فلو الـ SDK بيبعت داتا بكولباكات، المحول بيستخدم `callbackFlow` مع `awaitClose` علشان يحول الكولباكات دي لـ Flow نقي، أو يستخدم `suspendCancellableCoroutine` للطلبات الفردية مع ضمان إلغاء الطلب لو المستخدم خرج.\n\nثالثاً، عزل المكتبة في موديول Gradle منفصل؛ موديول الـ SDK بيكون مغلق تماماً (Private Implementation)، ومحدش في التطبيق بيشوف كلاساته. وقت التبديل لمكتبة جديدة، كل اللي بنعمله هو كتابة Adapter جديد للمكتبة الجديدة وربطه بالـ Interface في Hilt، وباقي التطبيق بيفضل شغال كأن شيئاً لم يكن.",
        "deep_answer_ar": "تحت الكابوت، التحدي الحقيقي في مواءمة كولباكات الـ SDKs المختلفة مش بس اختلاف أسماء الدوال، بل هو التناقض في سلوك الخيوط (Threading)، وإدارة الإلغاء (Cancellation)، ومعدل تدفق البيانات (Backpressure).\n\nكتير من الـ SDKs بتشغل الكولباك بتاعها على الـ Main Thread وده يهدد بسقوط الفريمات، أو على خيوط مجهولة المصدر بتسبب Race Conditions. داخل الـ Adapter، المهندس الكبير بيعمل Thread Normalization؛ فبنستخدم `flowOn(Dispatchers.IO)` أو `withContext` علشان نضمن إن الانبعاثات تخرج للـ Domain على خيوط منضبطة وآمنة تماماً.\n\nكمان في التعامل مع التدفقات بـ `callbackFlow`، كتلة `awaitClose` هي المكان الوحيد اللي بيضمن إيقاف الـ SDK الخارجي؛ فلما الـ CoroutineScope بتاع الشاشة يتلغي، كوتلن بتنادي `awaitClose` فوراً، فبنلغي تسجيل الـ Listener ونوقف حساسات الجهاز زي الـ GPS أو الحساسات الحرارية بدون أي تسريب للبطارية.\n\nوفي العمليات الفردية بـ `suspendCancellableCoroutine`، بنفحص دائماً `continuation.isActive` وبنربط `invokeOnCancellation` علشان نبلغ الـ SDK الخارجي يلغي طلب الشبكة أو المعالجة الجارية فوراً لو المستخدم خرج من الصفحة.\n\nالعزل على مستوى الـ Gradle بصلاحية `implementation` بيمنع الكومبايلر من تصدير كلاسات الـ SDK لباقي الموديولات، وده بيخلي الاعتماد على الـ Interface أمراً حتمياً ومفروضاً بقوة أدوات البناء، وبيجعل استبدال أي شريك خارجي عملية آمنة بنسبة 100% ومضمونة الاختبار."
    }
}

# ==========================================
# PAT-17: A global Singleton makes tests order-dependent. How do you redesign ownership?
# ==========================================
DATA["PAT-17"] = {
    "concept_en": """Global mutable singletons (such as Kotlin object declarations retaining var properties or static instance holders) introduce hidden shared mutable state across an entire JVM process, causing test order dependence, flaky test suites, and concurrency race conditions. When unit test suites run in a shared test process, modifications made by Test A persist in memory and contaminate the execution environment of Test B. To remediate this defect, software architects redesign state ownership by transforming static objects into ordinary instantiable classes, externalizing their lifecycle management to a Dependency Injection container, enforcing constructor injection, and providing fresh, isolated in-memory instances for every individual test execution.""",
    "walkthrough_en": """Refactoring a global mutable singleton into an isolated, test-friendly dependency:
```kotlin
// BAD ANTI-PATTERN: Global Mutable Singleton (Causes test contamination and order dependence!)
object UserSessionManager {
    var activeUser: User? = null // Persists across all unit tests in the same JVM runner!
    fun logout() { activeUser = null }
}

// REDESIGNED: Ordinary instantiable class with clear contract
interface UserSession {
    val currentUser: User?
    fun updateSession(user: User)
    fun clear()
}

class UserSessionImpl @Inject constructor() : UserSession {
    private var _user: User? = null
    override val currentUser: User? get() = _user
    override fun updateSession(user: User) { _user = user }
    override fun clear() { _user = null }
}

// PRODUCTION: Scoped via DI container (Singleton within Application lifetime)
@Module
@InstallIn(SingletonComponent::class)
abstract class SessionModule {
    @Binds @Singleton
    abstract fun bindSession(impl: UserSessionImpl): UserSession
}

// UNIT TESTS: 100% Isolated, order-independent, parallel test runs!
class UserProfileViewModelTest {
    // Fresh instance created per test method, zero state leakage!
    private val fakeSession: UserSession = UserSessionImpl()
    private val viewModel = UserProfileViewModel(fakeSession)

    @Test fun testLoginUpdatesState() {
        fakeSession.updateSession(User("id_1", "Alice"))
        assertEquals("Alice", viewModel.getCurrentUserName())
    }
}
```""",
    "short_en": """A global mutable singleton persists modified state across unit tests running in the same JVM process, making test outcomes depend on execution order. To fix this, redesign ownership by converting the static singleton into an ordinary instantiable class implementing an interface. Enforce constructor injection for all consumers, let a DI container like Hilt manage its application-wide lifecycle scope in production, and instantiate fresh, isolated instances before each test method to guarantee deterministic, order-independent test execution.""",
    "structured_en": """Order-dependent unit tests are a hallmark symptom of architectural contamination caused by global mutable singletons.
When an application uses a Kotlin object or a static Java singleton holding mutable fields, that state lives in the static memory area of the JVM process. When test runners like JUnit execute test classes, all tests within the module frequently share that same JVM process to optimize execution speed. If Test A logs in a user or modifies a configuration flag in the singleton and Test B expects an unauthenticated state, the test suite passes when run in isolation but fails intermittently when run together, creating elusive flaky tests.
Redesigning state ownership requires shifting from global implicit access to explicit scoped dependency injection.
The first step is transforming the static object into a regular class with a private constructor and defining an interface that abstracts its behaviors.
The second step is replacing global static call sites with explicit constructor injection, ensuring that every consuming ViewModel, UseCase, or Repository declares its dependency openly.
The third step is delegating lifecycle ownership to the dependency injection framework. In production, Hilt or Dagger scopes the class to SingletonComponent, ensuring a single shared instance per application runtime.
In test environments, each unit test instantiates a fresh, isolated instance of the class or a lightweight test double during setup, guaranteeing total test independence regardless of execution order.""",
    "deep_senior_en": """Under the hood, static singletons circumvent the JVM garbage collection root lifecycle by hanging directly off the ClassLoader's static reference table.
Because the ClassLoader does not unload classes between individual JUnit test methods, any mutable data structure (such as an in-memory HashMap, token cache, or CoroutineScope) attached to a static field remains resident in memory throughout the entire test process. Attempting to fix this by adding a resetForTesting() method is a fragile anti-pattern: it leaks test-only logic into production bytecode, fails to protect against concurrent parallel test runners, and relies on developer discipline to invoke reset in @After teardown methods.
Senior architects resolve this at the structural root by enforcing Inversion of Control. By decoupling the class definition from its instantiation scope, the class becomes a standard transient object whose lifecycle is governed strictly by whatever container or test harness constructs it.
In modern JVM testing architectures, this enables seamless parallel test execution (junit.jupiter.execution.parallel.enabled = true). Because each test method constructs its own isolated object graph via constructor injection, tests run across multiple CPU cores simultaneously without mutex contention, race conditions, or state contamination.
This redesign also eliminates hidden Android framework dependencies. By replacing static context-dependent singletons with injected abstractions, tests execute as pure, blazing-fast JVM tests without requiring Robolectric or device instrumentation overhead.""",
    "meta_ar": {
        "id": "PAT-17",
        "questionAr": "عندما يجعل كائن Singleton عام الاختبارات معتمدة على ترتيب التنفيذ (Order-dependent)، كيف تعيد تصميم ملكية وإدارة هذا الكائن؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مخاطر الحالة المشتركة القابلة للتعديل (Shared Mutable State) في الـ Singletons، والقدرة على إعادة هيكلة الكود باستخدام Constructor Injection وإدارة النطاقات (Scoping) عبر DI، وتوفير بيئة اختبارات متوازية ومستقلة تماماً.",
        "why_it_matters_ar": "الـ Singletons العامة المليئة بمتغيرات `var` بتسرب البيانات بين الاختبارات في الـ JVM، وده بيخلق اختبارات متقلبة (Flaky Tests) تنجح لوحدها وتسقط لما ترن مع باقي التستات، مما يدمر خطوط الـ CI/CD.",
        "worked_example_ar": "إعادة تصميم Singleton لحماية استقلالية الاختبارات:\n```kotlin\n// كود سيئ: كائن عام يسرب الحالة في التيست\nobject Session { var token: String? = null }\n// كود نظيف: كلاس عادي يُحقن في الكونستركتور\nclass SessionManager @Inject constructor() : SessionContract {\n    var token: String? = null\n}\n// في التيست: إنشاء كائن جديد لكل دالة اختبار\n@Before fun setup() { session = SessionManager() }\n```",
        "trade_offs_ar": "يتطلب إزالة الاستدعاءات المباشرة واستبدالها بحقن التبعيات في كل الكلاسات، لكنه يقضي تماماً على الـ Flaky Tests ويتيح تشغيل الاختبارات بالتوازي على الـ JVM.",
        "failure_modes_ar": "محاولة حل المشكلة بإضافة دالة `resetForTesting()` في الكائن العام، مما يلوث كود الإنتاج ويفشل عند تشغيل الاختبارات بالتوازي في خيوط متعددة.",
        "production_perspective_ar": "في المشروعات الكبيرة، يُمنع منعاً باتاً استخدام Kotlin `object` لتخزين أي State قابلة للتعديل، ويتم إدارة دورات حياة الكائنات الفردية حصرياً عبر `@Singleton` في Hilt.",
        "how_to_answer_ar": "اشرح المشكلة الجذرية: بقاء الحالة في ذاكرة الـ JVM بين الاختبارات مما يجعل النتيجة تعتمد على الترتيب، واعرض خطوات إعادة التصميم: تحويل الكائن لكلاس عادي، واستخدام Constructor Injection، وإسناد إدارة دورة الحياة لـ Hilt في الإنتاج، وإنشاء كائن مستقل جديد في كل اختبار.",
        "talking_points_ar": "مخاطر الـ Shared Mutable State في الـ ClassLoader، ومشاكل الـ Flaky Tests، وعيوب حلول الترقيع زي `resetForTesting()`، وقوة الحقن بالكونستركتور وتشغيل التيستات بالتوازي.",
        "follow_ups_ar": "- **المحاور:** \"ليه دالة `resetForTesting()` تعتبر حلاً سيئاً في الإنتاج؟\"\n  **المرشح:** \"لأنها بتسرب كود تجريبي لنسخة الإنتاج، وبتعتمد على إن المطور ميكنش ناسي يستدعيها، والأهم إنها بتفشل تماماً لو الاختبارات اشتغلت بالتوازي (Parallel Testing) على خيوط مختلفة.\"\n\n- **المحاور:** \"إزاي الـ DI بيضمن إن الكائن يفضل نسخة واحدة في التطبيق وفي نفس الوقت مستقل في التيست؟\"\n  **المرشح:** \"عبر الـ Scoping؛ في التطبيق بنربطه بـ `@Singleton` داخل `SingletonComponent` فيفضل نسخة واحدة، بينما في التيست بننشئ New Instance يدوياً في كل دالة.\"",
        "self_check_ar": "هل شرحت سبب حدوث الـ Order-dependence؟ هل بينت عيوب `resetForTesting()`؟ وهل وضحت خطوات إعادة التصميم بالـ DI؟",
        "references_ar": f"- [Flaky Tests and Shared State](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html) — مقال مدونة جوجل الهندسية حول مشاكل الاختبارات المتقلبة والحالة المشتركة.\n- [Dependency Injection Best Practices](https://developer.android.com/training/dependency-injection) — التوثيق الرسمي لأفضل ممارسات حقن التبعيات في أندرويد.",
        "quick_answer_ar": "اعتماد الاختبارات على ترتيب التنفيذ بيحصل بسبب وجود كائن Singleton عام محتفظ بحالة متغيرة في ذاكرة الـ JVM، فالبيانات اللي بيعدلها اختبار بتفضل موجودة وتلوث بيئة الاختبار اللي بعده. عشان نحل المشكلة دي جذرياً، بنعيد تصميم الملكية؛ بنحول الـ Singleton لكلاس عادي بيستقبل تبعياته بالكونستركتور وبيطبق Interface، وبنوكل إدارة دورة حياته لـ Hilt في الإنتاج عبر `@Singleton`، وفي الاختبارات بننشئ نسخة جديدة ونظيفة ومستقلة في كل دالة تيست لضمان تشغيلها بحيادية تامة وبأي ترتيب.",
        "best_answer_ar": "المشكلة دي بنشوفها كتير في المشاريع، وبتكون السبب الرئيسي لظهور الـ Flaky Tests؛ تلاقي الاختبار ينجح لما تشغله لوحده، ويسقط بشكل عشوائي لما تشغل كل الاختبارات مع بعضها على الـ CI/CD.\n\nالسبب الجذري هو إن كائن الـ `object` في كوتلن أو الـ Static Singleton في جافا بيفضل عايش في ذاكرة الـ JVM المشتركة اللي مشغلة الـ Test Runner. فلما الاختبار رقم 1 يسجل دخول مستخدم، الكائن بيفضل محتفظ ببيانات المستخدم دي، ولما الاختبار رقم 2 يرن ويتوقع إنه بيبدأ من الصفر كمستخدم غير مسجل، بيفشل بسبب التلوث ده.\n\nمحاولة ترقيع المشكلة بإضافة دوال زي `reset()` أو `clearForTesting()` هي فكرة سيئة جداً؛ لأنها بتلوث كود الإنتاج، وبتفشل حتماً لو الاختبارات اشتغلت بالتوازي على كذا Core.\n\nإعادة التصميم المعماري الصح بتتضمن 3 خطوات:\nأولاً، تحويل الـ Singleton لكلاس عادي تماماً بيطبق Interface محدد.\nثانياً، استخدام حقن التبعيات عبر الكونستركتور (Constructor Injection) في كل الكلاسات اللي محتاجاه بدل ما تنادي الكائن بشكل Static.\nثالثاً، في كود التطبيق، بنعرف الكلاس داخل Hilt بنطاق `@Singleton` عشان يفضل نسخة واحدة على مستوى التطبيق. وفي كود الاختبارات، بنعمل `setup` ينشئ نسخة جديدة ونقية في الذاكرة لكل دالة اختبار على حدة، وده بيضمن استقلالية تامة وسرعة هائلة في تنفيذ الاختبارات.",
        "deep_answer_ar": "تحت الكابوت، الكائنات الـ Static في لغة Java و Kotlin بترتبط مباشرة بجدول مراجع الـ ClassLoader، وده بيخليها بمنأى عن عمليات التنظيف المعتادة للـ Garbage Collector طوال فترة تشغيل عملية الـ JVM.\n\nوحيث إن مشغلات الاختبارات زي JUnit بتفضل مشغلة نفس الـ JVM Process لتسريع وقت الـ Build، أي تعديل على متغير `var` أو كاش داخلي في كائن عام بيفضل مستمر في الذاكرة طوال تشغيل مئات التستات. والنتيجة هي كابوس الـ Order Dependence؛ لو التستات رنت بالترتيب أ، ب تنجح، ولو رنت ب، أ تفشل.\n\nإعادة التصميم بتطبق مبدأ فصل تعريف الكائن عن نطاق بقائه في الذاكرة (Decoupling class definition from lifecycle scope). لما نخلي الكلاس عادياً وبيتم حقنه في الكونستركتور، إحنا بنخليه كائن خاضع لإدارة الـ GC الطبيعية ومربوط بالحاوية اللي أنشأته فقط.\n\nالميزة الجبارة للتصميم ده في الشركات الكبيرة هي تمكين ميزة الاختبارات المتوازية (Parallel Test Execution). لما كل دالة اختبار بتنشئ شجرة الكائنات الخاصة بيها عبر الكونستركتور، بنقدر نشغل الاختبارات على كل أنوية المعالج في نفس الوقت بدون أي خوف من الـ Race Conditions أو تضارب الموارد.\n\nعلاوة على كده، الخطوة دي بتعزل كود أندرويد المعقد؛ فبدل ما الـ Singleton يكون ماسك في `Context` ثابت ويجبرنا نشغل Robolectric بطيء أو محاكي أندرويد حقيقي، بنقدر نختبر الـ ViewModels بالكامل على الـ JVM العادي في أجزاء من الثانية وبأعلى موثوقية هندسية ممكنة."
    }
}

# ==========================================
# PAT-18: How can patterns turn into unnecessary indirection? Give an example.
# ==========================================
DATA["PAT-18"] = {
    "concept_en": """Design patterns degrade into unnecessary indirection and architectural over-engineering when abstractions, interfaces, and decoupling mechanisms are introduced preemptively without genuine business complexity, multiple polymorphic implementations, or volatile boundaries to justify them. While design patterns exist to manage architectural friction and change, misapplying them introduces cognitive bloat, boilerplate maintenance overhead, obscured data flows, and slower compilation times. A classic manifestation in modern Android Clean Architecture is the ubiquitous one-line pass-through UseCase that merely delegates a simple read query directly to a single Repository without adding validation, domain logic, or data coordination.""",
    "walkthrough_en": """Contrasting unnecessary UseCase indirection with pragmatic architecture:
```kotlin
// OVER-ENGINEERED ANTI-PATTERN: Completely useless 1-line pass-through indirection
class GetUserProfileUseCase @Inject constructor(
    private val repository: UserRepository
) {
    // Zero logic, zero transformation, zero validation. Pure architectural bloat!
    suspend operator fun invoke(userId: String): Result<UserProfile> = repository.getUserProfile(userId)
}

// ViewModel forced to inject an empty layer
class OverEngineeredViewModel @Inject constructor(
    private val getUserProfileUseCase: GetUserProfileUseCase
) : ViewModel() { /* ... */ }

// PRAGMATIC SENIOR DESIGN: Direct repository observation when no domain policy exists
class PragmaticViewModel @Inject constructor(
    private val userRepository: UserRepository // Clear, direct, zero cognitive tax
) : ViewModel() {
    val userState = userRepository.observeUserProfile(currentUserId)
}

// GENUINE USE CASE: Justified by coordination, business rules, and multi-repo logic
class CheckoutOrderUseCase @Inject constructor(
    private val cartRepo: CartRepository,
    private val paymentRepo: PaymentRepository,
    private val inventoryRepo: InventoryRepository
) {
    suspend operator fun invoke(orderId: String): Result<Receipt> {
        // Enforces genuine business rules, multi-repository orchestration, and transaction rollback!
        inventoryRepo.reserveStock(orderId).getOrThrow()
        val receipt = paymentRepo.charge(orderId).getOrThrow()
        cartRepo.clearCart()
        return Result.success(receipt)
    }
}
```""",
    "short_en": """Design patterns turn into unnecessary indirection when abstractions are introduced without multiple implementations, complex business logic, or genuine volatility. A classic example is a one-line pass-through UseCase that merely forwards a call directly to a Repository. This adds files, interfaces, and cognitive overhead without providing testability or architectural value. Senior engineers apply patterns pragmatically to solve real friction, not as dogmatic boilerplate.""",
    "structured_en": """The transformation of helpful design patterns into destructive indirection occurs when engineers prioritize architectural dogma over practical engineering value.
Design patterns are intended to solve specific friction points: handling variable algorithms, decoupling unstable vendor interfaces, or managing complex object lifecycles. However, when patterns are applied dogmatically as mandatory checklists, they introduce an architectural tax. Every layer of abstraction, interface, and wrapper increases cognitive load, forces developers to navigate through multiple empty files to trace simple data flows, inflates compilation times, and increases the codebase maintenance burden.
A prime example in Android development is the dogmatic mandate that every single ViewModel must interact with a UseCase, even for trivial database reads.
In many codebases, developers write GetUserUseCase, which contains a single line of code invoking userRepository.getUser(). The UseCase performs no validation, orchestrates no secondary repositories, and applies no business rules. It exists solely to satisfy a rigid Clean Architecture diagram.
Pragmatic senior engineering dictates that ViewModels should depend directly on Repositories for straightforward read operations. UseCases should be reserved exclusively for scenarios with genuine domain complexity: coordinating multiple data sources, executing business calculations, or enforcing reusable transactional logic. Abstraction without justification is technical debt.""",
    "deep_senior_en": """Under the hood, unnecessary indirection carries tangible runtime, memory, and developer productivity costs that compound at scale.
From a compiler and JVM runtime perspective, every redundant pass-through class generates extra bytecode, class definitions, and metadata entries in the application's DEX tables. In multi-module enterprise codebases, creating redundant interfaces and wrappers balloons Dagger's dependency graph. Dagger must generate corresponding Factory and Provider classes for every intermediate layer, increasing annotation processing (KSP) times, swelling incremental build durations, and eating into Android's 64K method limit before multidex optimization.
At runtime, while modern JVM JIT compilers can theoretically inline trivial single-caller methods, the Android ART runtime ahead-of-time (AOT) and baseline profile compilation cannot always eliminate these allocations across module boundaries, resulting in unnecessary heap object allocations and stack frame overhead during high-frequency user interactions.
Staff engineers combat this cargo-cult architecture by adhering to principles like YAGNI (You Aren't Gonna Need It) and rule-of-three abstraction. They mandate that interfaces and intermediate pattern layers are introduced only when at least two concrete implementations exist, or when an upcoming business requirement genuinely demands decoupled substitution.
By prioritizing readability, debuggability, and direct data paths, engineering teams build high-velocity systems that remain clean without becoming buried in speculative indirection.""",
    "meta_ar": {
        "id": "PAT-18",
        "questionAr": "كيف يمكن لأنماط التصميم أن تتحول إلى طبقات تجريد غير ضرورية (Unnecessary Indirection)؟ اذكر مثالاً عملياً.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "النضج الهندسي والقدرة على تجنب الإفراط في الهندسة (Over-engineering)، والتمييز بين التجريد المفيد والتجريد الشكلي، وإدراك التكلفة الحقيقية لطبقات الكود الزائدة على سرعة البناء والذاكرة وسهولة القراءة.",
        "why_it_matters_ar": "التطبيق الأعمى لأنماط التصميم و Clean Architecture يخلق كوداً معقداً يحتوي على مئات الكلاسات الفارغة التي تزيد وقت الـ Build وتصعب قراءة وتتبع مسار البيانات بدون تقديم أي فائدة عملية.",
        "worked_example_ar": "مقارنة الـ UseCase الزائد بالكود العملي المباشر:\n```kotlin\n// كود معقد بدون فائدة: UseCase من سطر واحد يمرر للداتا فقط\nclass GetNameUseCase(val repo: Repo) { operator fun invoke() = repo.getName() }\n// كود مهندس ناضج: قراءة مباشرة من الـ Repo، ونترك الـ UseCase للعمليات المعقدة\nclass ProfileViewModel(val repo: Repo) { val name = repo.getName() }\n```",
        "trade_offs_ar": "الالتزام الحرفي بالأنماط يمنح شكلاً نظيفاً على الورق، لكنه يفرض ضريبة إدراكية وبطء في الـ Build وتشتيتاً للفريق بدون أي قيمة مضافة.",
        "failure_modes_ar": "كتابة UseCase لكل عملية بسيطة، أو إنشاء Interface لكل كلاس حتى لو مفيش غير تنفيذ واحد ومستحيل يتغير، مما يضاعف حجم المشروع بدون سبب.",
        "production_perspective_ar": "في الفرق الهندسية المتقدمة، نطبق مبدأ YAGNI؛ لا ننشئ UseCase إلا إذا كان هناك منطق عمل حقيقي (Business Logic) أو تنسيق بين أكثر من Repository.",
        "how_to_answer_ar": "وضح أن الأنماط وُجدت لحل مشاكل وتسهيل التغيير، وعند تطبيقها بشكل أعمى تتحول لـ Over-engineering، واضرب أشهر مثال واقعي: الـ One-line pass-through UseCase الذي يمرر الاستدعاء للـ Repository فقط، واشرح أثر ذلك على الـ Build time والـ DEX methods والجهد الذهني للمطورين.",
        "talking_points_ar": "مفهوم Over-engineering وضريبة التجريد، ومثال الـ Pass-through UseCase، وتكلفة الكلاسات الإضافية على الـ DEX والـ KSP وقت الـ Build، ومبادئ YAGNI والـ Pragmatic Architecture.",
        "follow_ups_ar": "- **المحاور:** \"متى يصبح وجود الـ UseCase مبرراً وضرورياً بالفعل؟\"\n  **المرشح:** \"لما يكون فيه Business Logic حقيقي، زي التحقق من صحة المدخلات، أو التنسيق بين اتنين Repositories مختلفين، أو إعادة استخدام نفس المنطق في أكتر من شاشة ViewModel.\"\n\n- **المحاور:** \"هل إنشاء Interface لكل كلاس دايماً يعتبر Best Practice؟\"\n  **المرشح:** \"لا، دي خرافة شائعة؛ لو الكلاس معندوش غير تنفيذ واحد ومش هيتغير ومش محتاجين نبدله في الـ Test بـ Fake، يبقى الـ Interface مجرد تعقيد إضافي بدون أي فائدة.\"",
        "self_check_ar": "هل عرفت مشكلة الـ Over-engineering؟ هل ذكرت مثال الـ Pass-through UseCase؟ وهل بينت الأثر الحقيقي على وقت البناء وسهولة قراءة الكود؟",
        "references_ar": f"- [You Aren't Gonna Need It (YAGNI)](https://martinfowler.com/bliki/Yagni.html) — مقال مارتن فاولر حول مبدأ YAGNI وتجنب التجريد المسبق.\n- [Clean Architecture: A Pragmatic Approach](https://developer.android.com/topic/architecture/domain-layer) — دليل جوجل حول طبقة الدومين ومتى يكون الـ UseCase ضرورياً.",
        "quick_answer_ar": "أنماط التصميم بتتحول لطبقات تجريد غير ضرورية (Unnecessary Indirection) لما بنطبقها بشكل أعمى بدون وجود تعقيد حقيقي أو احتمالية فعلية للتغيير في المستقبل. أشهر مثال يومي في أندرويد هو الـ UseCase أبو سطر واحد؛ تلاقي كلاس كامل اسمه `GetUserUseCase` وظيفته الوحيدة إنه ينادي `userRepository.getUser()` بدون أي معالجة أو منطق عمل إضافي. الكود ده بيزود عدد الملفات، ويبطئ وقت الـ Build، ويصعب تتبع مسار البيانات في المشروع بدون ما يقدم أي ميزة في الاختبار أو الصيانة.",
        "best_answer_ar": "أنماط التصميم اتعملت علشان تحل مشاكل هندسية حقيقية وتقلل الاحتكاك البرمجي، لكن لما المطورين بيتعاملوا معاها كقواعد مقدسة وقوائم فحص ملزمة، بتتحول لضريبة معمارية معطلة (Architectural Tax) بنسميها الـ Over-engineering.\n\nكل طبقة تجريد أو Interface بتضيفها بتزود الجهد الذهني للمطور، وبتجبر اللي بيقرا الكود إنه يقعد يفتح 4 ملفات ورا بعض عشان يشوف استدعاء بسيط لقاعدة البيانات، وده بيعقد المشروع ويبطئ سرعة التطوير.\n\nالمثال الكلاسيكي الفاضح في معمارية أندرويد الحديثة هو فرض كتابة UseCase لكل شاشة مهما كانت بسيطة. فتلاقي مشروع فيه `GetOrdersUseCase` جواه سطر واحد: `return orderRepository.getOrders()`. الـ UseCase ده معملش أي فحص للمدخلات، ومنسقش بين موديولات، ومعملش أي حسابات رياضية؛ هو مجرد وسيط فارغ موجود عشان يرضي رسمة Clean Architecture نظرية.\n\nالمهندس الناضج بيكون عملي (Pragmatic)؛ الـ ViewModel يقدر يقرأ مباشرة من الـ Repository في العمليات البسيطة. والـ UseCase بنحطه فقط لما يكون فيه منطق عمل حقيقي، زي إنه يجمع بيانات من كذا Repository مع بعض، أو يعالج عملية دفع معقدة محتاجة Rollback، أو منطق متكرر بيستخدم في كذا شاشة. التجريد بدون مبرر هو مجرد دين تقني مقنع.",
        "deep_answer_ar": "تحت الكابوت، طبقات التجريد غير المبررة بتكلف التطبيق تكلفة مادية حقيقية على مستوى أداء الذاكرة ووقت بناء المشروع (Build Times).\n\nكل كلاس زائد بتنشئه بينتج عنه Bytecode إضافي، ومدخلات جديدة في جداول الـ DEX methods، وكلاسات مولدة تلقائياً في مكتبات الـ DI. في المشروعات الضخمة، وجود مئات الـ Pass-through UseCases بيخلي مكتبات زي Dagger و KSP تولد آلاف الـ Factories و Providers الزائدة، وده بيزود وقت الـ Compilation اليومي لخطوط الـ CI/CD ويقرب التطبيق من حدود الـ 64K Method Limit.\n\nوعلى مستوى وقت التشغيل في Android ART Runtime، حتى لو الـ JIT Compiler بيقدر يعمل Inlining لبعض الاستدعاءات الفردية، إلا إن الانتقال عبر حدود الموديولات بيفضل محتفظ بـ Stack Frames وحجوزات كائنات إضافية على الـ Heap مع كل عملية تمرير، وده بيهدر موارد المعالج والذاكرة في التفاعلات السريعة.\n\nالمهندسون الكبار بيتبعوا مبادئ حازمة زي YAGNI (You Aren't Gonna Need It) وقاعدة التجريد الثلاثية (Rule of Three)؛ مبيعملش Interface إلا لو عنده على الأقل تنفيذين حقيقيين ومختلفين، ومبيعملش UseCase إلا لو فيه Domain Logic حقيقي محتاج يختبره بشكل مستقل عن الواجهة.\n\nالهدف النهائي لأي معمارية محترفة هو تبسيط فهم وتطوير النظام، وأفضل كود هو الكود المباشر اللي بيأدي الغرض بأقل عدد ممكن من الملفات والطبقات التجريدية."
    }
}

def main():
    print(f"Elevating {len(DATA)} questions in PAT (PAT-10 to PAT-18)...")
    
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
    ee.save_topic_metadata("pat_10_18", {qid: d["meta_ar"] for qid, d in DATA.items()})

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
        print("\nAll 9 PAT questions (PAT-10 to PAT-18) successfully elevated and passed validation!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

