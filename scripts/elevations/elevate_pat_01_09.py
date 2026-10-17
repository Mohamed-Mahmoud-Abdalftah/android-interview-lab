#!/usr/bin/env python3
"""Elevate PAT-01 through PAT-09 for bilingual parity and senior spoken answers."""
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
# PAT-01: What is a design pattern, and how is it different from architecture?
# ==========================================
DATA["PAT-01"] = {
    "concept_en": """A design pattern is a reusable, localized solution to a commonly occurring structural, creational, or behavioral problem within a specific software context, operating at the granularity of individual classes and localized object collaborations. In contrast, software architecture defines the macro-level organizational blueprint of an entire system, establishing structural boundaries, layer separation, dependency rules, data flow paradigms, and cross-cutting system characteristics. While architecture dictates high-level governance (such as Clean Architecture, Unidirectional Data Flow, or multi-module packaging), design patterns (such as Adapter, Strategy, or Factory) serve as tactical building blocks employed within those architectural layers to solve concrete engineering mechanics without impacting global system topology.""",
    "walkthrough_en": """Contrasting macro architecture with localized design patterns:
```kotlin
// ARCHITECTURE LEVEL: Clean Architecture Layer Separation (Domain Layer)
interface PaymentRepository { // Macro Boundary: Domain interface isolated from data details
    suspend fun processTransaction(orderId: String, amount: Long): Result<TransactionReceipt>
}

// PATTERN LEVEL: Strategy Pattern implemented inside the Data Layer
interface PaymentStrategy { // Tactical Pattern: Encapsulates specific payment calculation & API call
    suspend fun executePayment(amount: Long): TransactionReceipt
}

class StripePaymentStrategy @Inject constructor(private val stripeApi: StripeApi) : PaymentStrategy {
    override suspend fun executePayment(amount: Long) = stripeApi.charge(amount)
}

class PayPalPaymentStrategy @Inject constructor(private val payPalSdk: PayPalSdk) : PaymentStrategy {
    override suspend fun executePayment(amount: Long) = payPalSdk.authorize(amount)
}

// Data layer repository uses Strategy pattern to satisfy the macro architectural contract
class PaymentRepositoryImpl @Inject constructor(
    private val strategies: Map<PaymentMethod, @JvmSuppressWildcards Provider<PaymentStrategy>>
) : PaymentRepository {
    override suspend fun processTransaction(orderId: String, amount: Long): Result<TransactionReceipt> = runCatching {
        val strategy = strategies[PaymentMethod.STRIPE]?.get() ?: error("Unsupported gateway")
        strategy.executePayment(amount)
    }
}
```""",
    "short_en": """A design pattern is a tactical, reusable solution to a localized class-level problem, such as adapting an interface or encapsulating an algorithm. Software architecture is the strategic blueprint that governs global system boundaries, data flow rules, and layer separation across the entire application. Architecture dictates how modules and layers interact, while design patterns solve specific implementation mechanics within those layers.""",
    "structured_en": """Understanding the difference between a design pattern and software architecture requires analyzing scale, scope, and impact on system evolvability.
Software architecture represents the strategic macro-level blueprint of an application. It defines foundational system boundaries, dependency direction rules, cross-cutting concerns, and information flow. For example, adopting Clean Architecture and Unidirectional Data Flow establishes that UI components observe ViewModels, ViewModels interact with UseCases, and Domain logic remains completely isolated from database drivers and network frameworks. Modifying system architecture is exceptionally expensive because it restructures foundational boundaries across entire module graphs.
In contrast, design patterns represent localized tactical solutions applied to recurring structural or behavioral challenges within individual components. Patterns operate at the micro level, describing collaborations between a few interacting classes. Within a Clean Architecture data layer, an engineer might use the Adapter pattern to wrap an unruly vendor SDK, or the Strategy pattern to interchange discount algorithms.
Changing or refactoring a design pattern is localized and low-risk, affecting only a handful of files without destabilizing application-wide architectural boundaries.""",
    "deep_senior_en": """Under the hood, architecture establishes invariant compilation boundaries and dependency flow rules enforced by Gradle dependency graphs and static linters, whereas design patterns establish object collaboration protocols within those boundaries.
In large-scale Android development, confusing patterns with architecture leads to severe architectural degradation. A notorious anti-pattern is treating the Singleton pattern as an architectural foundation by storing global application state in static singletons, which destroys Clean Architecture boundaries, introduces hidden concurrency coupling, and prevents parallel unit testing.
Staff engineers view architecture as the enforcement of high-level constraints: data flows inward toward domain abstractions, feature modules compile in parallel without lateral dependencies, and presentation components observe state streams reactively. Within those constraints, design patterns solve tactical impedance mismatches.
For instance, the Repository pattern mediates between domain entities and multiple data sources. The Adapter pattern bridges legacy Java callbacks to modern Kotlin Coroutines. The Factory pattern delegates complex object construction to dependency injection engines.
By keeping design patterns strictly subordinate to architectural boundaries, engineering organizations ensure that class-level refactoring remains isolated, predictable, and fully verifiable without causing system-wide regressions. Automated architectural testing tools like Konsist or ArchUnit can formally assert that tactical design patterns never violate module layer boundaries, leak database entities into domain models, or reverse architectural dependency flow rules across the enterprise codebase.""",
    "meta_ar": {
        "id": "PAT-01",
        "questionAr": "ما هو نمط التصميم (Design Pattern)، وما الفرق بينه وبين المعمارية البرمجية (Software Architecture)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على التمييز الدقيق بين المخطط المعماري الكلي للمشروع (Macro Architecture) والحلول التكتيكية الموضعية (Micro Patterns)، وإدراك تأثير كل منهما على صيانة الكود وحدود الموديولات وقابلية التوسع.",
        "why_it_matters_ar": "الخلط بين المعمارية والأنماط يدفع المطورين للتعامل مع Singleton أو Factory كبديل للمعمارية النظيفة، مما يؤدي إلى كود متشابك يخفي التبعيات ويفقد المشروع قابلية الاختبار والصيانة.",
        "worked_example_ar": "المعمارية تحدد طبقات Clean Architecture، بينما النمط يحل مشكلة تبديل طرق الدفع داخل طبقة الداتا عبر نمط Strategy:\n```kotlin\n// معمارية: واجهة الدومين مفصولة\ninterface PayRepo { suspend fun pay() }\n// نمط: Strategy لتنفيذ بوابات الدفع تكتيكياً\nclass StripeStrategy : PayStrategy {}\n```",
        "trade_offs_ar": "المعمارية قرار استراتيجي شامل يصعب تغييره لاحقاً، بينما أنماط التصميم تكتيكات موضعية مرنة يسهل استبدالها وتعديلها داخل نطاق الكلاسات المعنية فقط.",
        "failure_modes_ar": "استخدام نمط Singleton كمعمارية لإدارة حالة التطبيق بالكامل عبر متغيرات Static، مما يدمر استقلالية الطبقات ويسبب تسريبات ذاكرة وتضارب في الخيوط المتزامنة.",
        "production_perspective_ar": "في الشركات الكبرى، نحدد معمارية MVI و Clean Architecture كإطار ملزم لكل الموديولات، ونترك للمهندسين حرية استخدام أنماط زي Adapter أو Strategy لحل مشاكل برمجية محددة داخل طبقاتهم.",
        "how_to_answer_ar": "عرف نمط التصميم كحل تكتيكي موضعي على مستوى الكلاسات (Micro)، وعرف المعمارية كالمخطط الهيكلي الاستراتيجي للنظام (Macro)، واضرب مثالاً عملياً يوضح كيف يعمل نمط Strategy داخل طبقة في معمارية Clean Architecture.",
        "talking_points_ar": "الفرق بين Macro Architecture و Micro Patterns، وتأثير التغيير المعماري مقابل التغيير النمطي، وحدود Clean Architecture، ومخاطر استخدام الأنماط كبديل للمعمارية.",
        "follow_ups_ar": "- **المحاور:** \"هل الـ MVVM يعتبر نمط تصميم ولا معمارية؟\"\n  **المرشح:** \"MVVM في أصله نمط تصميم لطبقة العرض (Architectural UI Pattern)، لكن لما ندمجه مع Clean Architecture وتقسيم الموديولات بيتحول لجزء من المعمارية الشاملة للتطبيق.\"\n\n- **المحاور:** \"ما هو أكبر خطر للإفراط في استخدام أنماط التصميم داخل المشروع؟\"\n  **المرشح:** \"خلق طبقات تجريد وهمية (Over-engineering) تصعب قراءة الكود وتتبع مسار البيانات بدون تقديم أي فائدة عملية حقيقية.\"",
        "self_check_ar": "هل وضحت الفارق بين النطاق الكلي والنطاق الموضعي؟ هل بينت تكلفة تعديل المعمارية مقارنة بالنمط؟ وهل دعمت إجابتك بمثال أندرويد حقيقي؟",
        "references_ar": f"- [Guide to app architecture](https://developer.android.com/topic/architecture) — دليل جوجل الرسمي لمعمارية تطبيقات أندرويد.\n- [Design Patterns: Elements of Reusable Object-Oriented Software](https://en.wikipedia.org/wiki/Design_Patterns) — المرجع الكلاسيكي لعصابة الأربعة (GoF).\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نمط التصميم هو حل تكتيكي موضعي ومتكرر لمشكلة برمجية محددة بين كلاسين أو أكثر، زي تحويل واجهة بـ Adapter أو عزل خوارزمية بـ Strategy. أما المعمارية البرمجية فهي المخطط الهيكلي الشامل للمشروع بأكمله، اللي بيحدد حدود الموديولات، واتجاه سريان البيانات، وفصل الطبقات زي Clean Architecture. المعمارية قرار كلي يصعب تغييره، بينما النمط قرار جزئي مرن يسهل تعديله داخل طبقته.",
        "best_answer_ar": "الفرق الجوهري بين نمط التصميم والمعمارية البرمجية هو فرق في النطاق والتأثير المعماري على النظام.\n\nالمعمارية البرمجية بتمثل المخطط الاستراتيجي العام للتطبيق (Macro Level). هي اللي بتحدد القواعد الصارمة لإدارة النظام: إزاي بنقسم الكود لموديولات، وإزاي البيانات بتتحرك في اتجاه واحد (UDF)، وإزاي بنفصل طبقة الـ Domain عن الـ Data والـ UI في معمارية Clean Architecture. تغيير المعمارية بعد بناء المشروع بيكون مكلف جداً ومؤلم لأنه بيعيد تشكيل كل حدود الموديولات.\n\nفي المقابل، نمط التصميم هو أداة تكتيكية موضعية (Micro Level) بنستخدمها لحل مشكلة محددة داخل طبقة معينة من طبقات المعمارية. يعني داخل معمارية الـ Clean Architecture، بنستخدم نمط Repository لعزل مصادر البيانات، ونمط Adapter لربط مكتبة دفع خارجية بالكود بتاعنا، ونمط Strategy للتبديل بين طرق حساب الخصم.\n\nلو قررنا نغير نمط تصميم في كلاس معين، التعديل ده هيفضل محصور في ملفات معدودة ومش هيأثر على باقي التطبيق، بينما تغيير المعمارية بيهز استقرار النظام بالكامل.",
        "deep_answer_ar": "تحت الكابوت، المعمارية بتفرض قيودها على مستوى حدود الـ Compilation وعلاقات Gradle بين الموديولات؛ فالمعمارية النظيفة بتمنع موديول الـ Domain من رؤية أي كود في Room أو Retrofit، بينما أنماط التصميم بتعيش داخل تلك الموديولات كبروتوكولات تعاون بين الكائنات في وقت التشغيل.\n\nفي المشروعات الكبيرة، الخلط بين المفهومين بيؤدي لكوارث حقيقية؛ أشهرها معاملة نمط Singleton كبديل للمعمارية، حيث يلجأ بعض المطورين لتخزين حالة التطبيق ومستخدميه في كائنات Static عامة، وده بيدمر كل حدود الأمان، ويخلق ارتباطاً متزامناً خفياً (Concurrency Coupling)، ويمنع كتابة اختبارات Unit Tests متوازية.\n\nالمهندسون الكبار بيستخدموا المعمارية لفرض النظام الشامل: تدفق البيانات للداخل نحو الـ UseCases، واستخدام StateFlow لمراقبة الحالة برمجياً، وتجميع الميزات في موديولات مستقلة. وداخل كل طبقة، بنوظف أنماط التصميم لحل مشاكل هندسية تكتيكية: الـ Adapter لتحويل الكولباكات القديمة لكوروتينات، والـ Decorator لإضافة فلاتر تسجيل للشبكة، والـ Factory لتفويض إنشاء الكائنات المعقدة لـ Hilt.\n\nالحفاظ على تبعية أنماط التصميم للحدود المعمارية هو الضمان الحقيقي لبقاء الكود قابلاً للصيانة وإعادة الهيكلة دون التسبب في انهيارات غير متوقعة لخدمات الإنتاج. وعلاوة على ذلك، في بيئات الإنتاج الحديثة، بنستخدم أدوات الفحص المعماري المؤتمت زي Konsist لفرض قواعد المعمارية برمجياً؛ فنتأكد آلياً إن أنماط التصميم التكتيكية زي Adapter أو Factory متجاوزتش حدود موديولاتها ومسربتش أي تفاصيل خاصة بقواعد البيانات أو مكتبات الشبكة لطبقة الدومين، مما يحافظ على نظافة واستقلالية التصميم على المدى الطويل."
    }
}

# ==========================================
# PAT-02: Compare creational, structural, and behavioral patterns.
# ==========================================
DATA["PAT-02"] = {
    "concept_en": """The Gang of Four design patterns are fundamentally categorized into creational, structural, and behavioral classifications based on their underlying architectural intent. Creational patterns (such as Singleton, Factory Method, Abstract Factory, and Builder) abstract and manage object instantiation mechanisms, decoupling systems from how objects are created, configured, and represented in memory. Structural patterns (such as Adapter, Facade, Decorator, and Proxy) address class and object composition, establishing flexible interfaces and transparent wrappers that enable disparate types to collaborate cleanly. Behavioral patterns (such as Observer, Strategy, State, Command, and Chain of Responsibility) govern algorithmic execution, responsibility assignment, and communication protocols between collaborating components without tightly coupling senders and receivers.""",
    "walkthrough_en": """Categorizing pattern archetypes across Android engineering:
```kotlin
// 1. CREATIONAL PATTERN: Factory Method / Builder
class NetworkClient private constructor(val baseUrl: String, val timeoutMs: Long) {
    class Builder { // Creational: Safely configures and instantiates complex objects
        var baseUrl: String = ""
        var timeoutMs: Long = 10_000
        fun build() = NetworkClient(baseUrl, timeoutMs)
    }
}

// 2. STRUCTURAL PATTERN: Adapter Pattern
interface ModernCryptoEngine { fun encrypt(data: ByteArray): ByteArray }
class LegacyJavaCipherWrapper(private val cipher: javax.crypto.Cipher) : ModernCryptoEngine {
    // Structural: Adapts legacy imperative API to modern contract
    override fun encrypt(data: ByteArray): ByteArray = cipher.doFinal(data)
}

// 3. BEHAVIORAL PATTERN: Strategy Pattern
interface RetryPolicy { fun nextDelayMs(attempt: Int): Long } // Behavioral: Swappable algorithm
class ExponentialBackoff : RetryPolicy {
    override fun nextDelayMs(attempt: Int): Long = (1000L * (1 shl attempt)).coerceAtMost(30_000L)
}
```""",
    "short_en": """Creational patterns abstract object instantiation to decouple creation from execution, such as Builder and Factory. Structural patterns organize classes and interfaces into cohesive compositions and wrappers, such as Adapter and Facade. Behavioral patterns govern communication protocols, state transitions, and interchangeable algorithms between collaborating objects, such as Observer and Strategy. Each category solves a fundamentally distinct dimension of software design.""",
    "structured_en": """The classification of design patterns into creational, structural, and behavioral categories is based on the specific dimension of software construction each addresses.
Creational patterns focus on the mechanics of object creation. In complex applications, hardcoding direct constructor calls creates rigid coupling to concrete classes and complicates lifecycle management. Creational patterns like Factory Method, Abstract Factory, and Builder encapsulate instantiation logic, allowing the system to determine what gets instantiated, who instantiates it, and how it is configured without exposing creation internals to consumers.
Structural patterns focus on composition and relationships between classes. They solve interface mismatches and manage subsystem complexity by creating wrappers, proxies, or composite trees. For instance, the Adapter pattern allows incompatible classes to work together, while the Facade pattern provides a simplified entry point to a complex subsystem.
Behavioral patterns focus on communication and the distribution of responsibilities. They decouple objects that request actions from the objects that execute them. Patterns like Observer, Strategy, and State model dynamic interactions, event propagation, and swappable algorithms, ensuring that state transitions and behavioral changes occur without rigid mutual dependencies.""",
    "deep_senior_en": """Under the hood, these three categories operate at distinct phases of an object's lifecycle in memory: creational patterns control allocation and initial graph wiring; structural patterns define memory layouts, delegation wrappers, and interface dispatch tables; behavioral patterns govern runtime message dispatch and state mutations.
In modern Android development using Kotlin, language features have fundamentally reshaped how these categories are implemented. Many classic creational patterns like Builder are rendered obsolete by Kotlin's named arguments and default parameter values. Dependency injection frameworks like Hilt handle creational lifecycles natively, replacing manual factories with compile-time Directed Acyclic Graphs.
For structural patterns, Kotlin's class delegation by-interface (class LoggingList(inner: List) : List by inner) provides first-class language support for the Decorator pattern without manual forwarding boilerplate.
For behavioral patterns, higher-order functions and lambdas frequently replace single-method Strategy interfaces, while Kotlin Coroutines and Flow serve as the definitive standard for the Observer pattern across reactive presentation layers.
Staff engineers select patterns based on architectural friction rather than textbook dogma. If a problem is creational, they delegate to Hilt. If it is structural, they isolate third-party SDKs behind Facades and Adapters. If it is behavioral, they leverage reactive UDF state machines. Furthermore, Kotlin value classes and sealed hierarchies allow modern behavioral patterns to represent distinct domain states with zero runtime memory allocation overhead, combining compile-time safety with superior heap efficiency on Android runtimes.""",
    "meta_ar": {
        "id": "PAT-02",
        "questionAr": "قارن بين أنماط التصميم الإنشائية (Creational) والهيكلية (Structural) والسلوكية (Behavioral).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم تصنيفات أنماط التصميم الكلاسيكية (GoF)، والقدرة على التمييز بين أهداف كل عائلة، ومعرفة كيف غيرت لغة Kotlin وأطر العمل الحديثة طريقة تطبيق هذه الأنماط في أندرويد.",
        "why_it_matters_ar": "الخلط بين طبيعة الأنماط يجعل المطور يحاول حل مشكلة سلوكية بنمط إنشائي أو العكس، وفهم التصنيفات يساعد على اختيار الأداة الهندسية الصحيحة لكل مرحلة من دورة حياة الكائن.",
        "worked_example_ar": "مقارنة العائلات الثلاث برمجياً:\n```kotlin\n// إنشائي: بناء الكائن (Builder/Factory)\nval client = OkHttpClient.Builder().build()\n// هيكلي: مواءمة واجهة (Adapter)\nclass ListAdapter : RecyclerView.Adapter<VH>()\n// سلوكي: التفاعل وتبادل البيانات (Observer/Flow)\nflow.collect { state -> render(state) }\n```",
        "trade_offs_ar": "الأنماط الإنشائية تعزل البناء وتزيد الكود، والهيكلية تعالج عدم التوافق وتضيف طبقات وسيطة، والسلوكية تفك ارتباط التواصل وتزيد عدد الإنترفيسات.",
        "failure_modes_ar": "محاولة بناء كود معقد لنمط Builder في كوتلن بينما تدعم اللغة Named Arguments و Default Values أصلاً، أو كتابة Strategy معقد لكلاس كامل بدلاً من تمرير Lambda بسيطة.",
        "production_perspective_ar": "في المشروعات الحديثة، نوكل الأنماط الإنشائية لـ Hilt، ونستخدم الأنماط الهيكلية كـ Adapters لعزل الـ SDKs الخارجية، ونعتمد على Flow و Coroutines كأساس للأنماط السلوكية.",
        "how_to_answer_ar": "عرف كل عائلة بهدفها الأساسي: الإنشائية لإدارة وبناء الكائنات، والهيكلية لتنظيم العلاقات وتركيب الكلاسات، والسلوكية لتنظيم التواصل وتبادل الرسائل، واذكر مثالاً واقعياً من أندرويد لكل عائلة.",
        "talking_points_ar": "أهداف العائلات الثلاث، وتأثير لغة Kotlin الحديثة على الأنماط الكلاسيكية، ودور Hilt في الأنماط الإنشائية، ودور Flow في الأنماط السلوكية.",
        "follow_ups_ar": "- **المحاور:** \"كيف غيرت لغة كوتلن تطبيق نمط Builder الكلاسيكي؟\"\n  **المرشح:** \"كوتلن دعمت Named Arguments و Default Parameters في الـ Data Classes، وده خلى استخدام كلاس Builder منفصل غير ضروري إلا في حالات نادرة جداً كبناء كائنات الـ SDK المعقدة.\"\n\n- **المحاور:** \"إيه النمط السلوكي الأكثر استخداماً في واجهات Jetpack Compose الحديثة؟\"\n  **المرشح:** \"نمط الـ Observer المطبق عبر الـ State و Snapshot State؛ حيث يعيد الكومبوز رسم الواجهة تلقائياً بمجرد تغير الحالة.\"",
        "self_check_ar": "هل عرفت العائلات الثلاث بدقة؟ هل ذكرت أمثلة واضحة من أندرويد لكل منها؟ وهل بينت أثر ميزات Kotlin على هذه الأنماط؟",
        "references_ar": f"- [Design Patterns Classification](https://refactoring.guru/design-patterns/catalog) — الدليل الشامل لتصنيف أنماط التصميم البرمجية.\n- [Kotlin Idioms and Patterns](https://kotlinlang.org/docs/idioms.html) — التوثيق الرسمي لأساليب كوتلن البديلة للأنماط التقليدية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الأنماط الإنشائية (Creational) بتهتم بطريقة إنشاء وتكوين الكائنات وعزلها عن الاستخدام زي Factory و Builder. الأنماط الهيكلية (Structural) بتهتم بتركيب الكلاسات مع بعضها ومواءمة الواجهات المختلفة لتكوين هياكل أكبر وأكثر مرونة زي Adapter و Facade. الأنماط السلوكية (Behavioral) بتهتم بتنظيم التواصل، وتوزيع المسؤوليات، وحركة البيانات بين الكائنات بدون ارتباط وثيق زي Observer و Strategy. كل عائلة بتعالج مرحلة مختلفة في حياة الكود.",
        "best_answer_ar": "تصنيف أنماط التصميم إلى إنشائية وهيكلية وسلوكية بيساعد المهندس على اختيار الحل المناسب حسب طبيعة التحدي البرمجي.\n\nالأنماط الإنشائية (Creational) هدفها الأساسي هو عزل عملية بناء الكائنات عن منطق تشغيلها. فبدل ما نكتب `new` أو ننادي الكونستركتور مباشرة في كل مكان، بنستخدم أنماط زي Factory و Builder و Dependency Injection للتحكم في كيفية ولادة الكائن وإدارة دورة حياته في الذاكرة.\n\nالأنماط الهيكلية (Structural) هدفها تنظيم العلاقات وتركيب الكلاسات. بتركز على كيفية جعل كلاسات مختلفة تشتغل مع بعض بسلاسة حتى لو واجهاتها مش متطابقة. من أشهر أمثلتها نمط Adapter اللي بيحول واجهة كلاس قديم لواجهة جديدة بيفهمها نظامنا، ونمط Facade اللي بيبسط مكتبة خارجية معقدة ورا واجهة موحدة وسهلة.\n\nالأنماط السلوكية (Behavioral) بتهتم بكيفية تواصل الكائنات وتوزيع الأدوار بينها. بتركز على سريان البيانات وتنفيذ الخوارزميات بدون ما الكلاس اللي بيطلب الأكشن يكون مربوط بالكلاس اللي بينفذه. أشهر أمثلتها نمط Observer المتمثل في Flow لمراقبة تدفق الداتا، ونمط Strategy لتغيير خوارزمية العمل وقت التشغيل.",
        "deep_answer_ar": "تحت الكابوت، كل عائلة بتتعامل مع مرحلة محددة في حياة الكائن داخل الذاكرة: الإنشائية بتتحكم في حجز المساحة بالـ Heap وتوصيل شجرة الروابط؛ الهيكلية بتحدد جداول التوجيه (Dispatch Tables) والتفويض بين الكائنات؛ والسلوكية بتدير تمرير الرسائل والـ State Mutations أثناء التشغيل.\n\nفي عالم أندرويد الحديث مع لغة Kotlin، طريقة تطبيق العائلات دي اتغيرت جذرياً وبقت أكتر أناقة وخفة. فالأنماط الإنشائية زي Builder استبدلت في الغالب بـ Named Arguments و Default Values، ومسؤولية الـ Factory اتنقلت لمكتبات الـ DI زي Hilt اللي بتولد الـ DAG في وقت الـ Compilation.\n\nوفي الأنماط الهيكلية، ميزة الـ Class Delegation في كوتلن بكلمة `by` خلت تطبيق نمط Decorator مدمجاً في لغة البرمجة بدون الحاجة لكتابة دوال وسيطة يدوياً. أما في الأنماط الهيكلية زي Facade و Adapter، فبقت حائط الصد الأساسي لعزل الـ SDKs الخارجية ومواءمتها مع مكتبات Coroutines.\n\nوفي الأنماط السلوكية، الـ Lambdas والـ Higher-order Functions حلت محل الإنترفيسات المعقدة في نمط Strategy، بينما تحول نمط Observer إلى معيار أساسي عبر Kotlin Flow في طبقات الـ Presentation والـ Data.\n\nالمهندسون الكبار مبيطبقوش الأنماط دي بحفظ أعمى، بل بيختاروا الأداة الأبسط بلغة كوتلن لحل المشكلة دون زيادة غير مبررة في تعقيد المشروع."
    }
}

# ==========================================
# PAT-03: Explain Singleton, Factory, Abstract Factory, and Builder.
# ==========================================
DATA["PAT-03"] = {
    "concept_en": """Creational patterns abstract the instantiation process to make systems independent of how their collaborating objects are created, composed, and represented. Singleton restricts class instantiation to a single shared instance per process or scope, providing a global point of access. Factory Method defines an interface for creating an object while allowing implementing subclasses or providers to decide the concrete class instantiated. Abstract Factory elevates this abstraction by providing an interface for creating families of related or dependent objects without specifying their concrete classes. Builder separates the step-by-step construction of a complex object from its internal representation, allowing the identical construction process to yield different representations and immutable instances.""",
    "walkthrough_en": """Comparing Creational Patterns in modern Kotlin and Android:
```kotlin
// 1. SINGLETON: Process-wide single instance (via Kotlin object or Hilt @Singleton)
@Singleton
class InMemoryTokenStore @Inject constructor() {
    private var token: String? = null
    fun saveToken(newToken: String) { token = newToken }
}

// 2. FACTORY METHOD: Encapsulates creation of a specific interface variant
interface AnalyticsTracker { fun log(event: String) }
class FirebaseTracker : AnalyticsTracker { override fun log(event: String) {} }

class TrackerFactory @Inject constructor() {
    fun create(isProd: Boolean): AnalyticsTracker = 
        if (isProd) FirebaseTracker() else ConsoleTracker()
}

// 3. ABSTRACT FACTORY: Creates families of related products
interface DialogThemeFactory {
    fun createButton(context: Context): Button
    fun createHeader(context: Context): TextView
}
class Material3DialogThemeFactory : DialogThemeFactory {
    override fun createButton(context: Context) = MaterialButton(context)
    override fun createHeader(context: Context) = TextView(context).apply { textSize = 20f }
}

// 4. BUILDER: Step-by-step construction of complex immutable objects
class NotificationRequest private constructor(
    val title: String,
    val body: String,
    val channelId: String
) {
    class Builder(private val title: String) {
        var body: String = ""
        var channelId: String = "default"
        fun setBody(text: String) = apply { this.body = text }
        fun build() = NotificationRequest(title, body, channelId)
    }
}
```""",
    "short_en": """Singleton guarantees a single shared instance throughout a defined lifecycle. Factory Method encapsulates object instantiation behind a method to decouple callers from concrete classes. Abstract Factory provides an interface to create families of related objects without binding to concrete implementations. Builder constructs complex objects incrementally through step-by-step parameterization, ensuring immutability upon completion. Each creational pattern targets a distinct creation complexity.""",
    "structured_en": """Creational patterns provide structured strategies for managing object construction while preserving loose coupling.
The Singleton pattern ensures that a class has exactly one instance and provides a centralized access point. In Kotlin, this can be declared via the object keyword or managed via Hilt's @Singleton scope. Singletons are appropriate for state-free or thread-safe shared resources like Room databases or token caches, though indiscriminate usage introduces global state and testing pollution.
The Factory Method pattern defines a method for object creation, allowing the instantiation logic to vary independently from the client that uses the object. It decouples the caller from concrete subclasses, enabling dynamic runtime decisions based on configuration or environment.
The Abstract Factory pattern extends this concept to families of related objects. Instead of creating a single product, an Abstract Factory exposes multiple creation methods that yield consistent, coordinated components, such as platform-specific UI widgets or environment-specific encryption engines.
The Builder pattern solves the telescoping constructor problem. When an object requires numerous configuration parameters, optional properties, or validation rules before becoming valid, a Builder constructs the object step-by-step, producing an immutable, fully-validated instance at the terminal build invocation.""",
    "deep_senior_en": """Under the hood, these creational patterns directly influence memory layout, thread synchronization, and class-loading dynamics.
In traditional Java, Singleton required complex Double-Checked Locking with volatile fields to guarantee thread safety without synchronization bottlenecks. In Kotlin, the object keyword implements lazy thread-safe initialization via static JVM initialization blocks. However, staff engineers prefer dependency-injected singletons managed by Hilt's SingletonComponent, because framework scoping allows unit tests to substitute lightweight fakes easily, whereas static JVM singletons cannot be reset without reflection.
Factory and Abstract Factory patterns govern dynamic dispatch. By returning an abstract interface rather than a concrete class, these patterns introduce a layer of virtual method table indirection. While this carries negligible CPU overhead, the architectural gain is massive: it enables strict modularization where feature modules declare contracts and factories while concrete implementations reside in hidden internal modules.
Regarding Builder, senior engineers recognize that Kotlin's language features diminish its necessity for internal data models. Default arguments and named parameters in data classes provide clean, readable construction with compile-time validation. However, the Builder pattern remains critical in public SDK design, Java interoperability layers, and complex framework configurations like OkHttpClient and Retrofit where validation logic must execute atomically across multiple interrelated properties before instance emission.""",
    "meta_ar": {
        "id": "PAT-03",
        "questionAr": "اشرح أنماط Singleton و Factory و Abstract Factory و Builder مع توضيح الفروق بينها.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الأنماط الإنشائية الأربعة الأكثر استخداماً، والقدرة على شرح فلسفة كل نمط وحالته الاستخدامية، ومعرفة كيفية تنفيذها بأمان في Kotlin وبيئة أندرويد الحديثة.",
        "why_it_matters_ar": "الاستخدام الخاطئ للأنماط الإنشائية يملأ التطبيق بكائنات ثابتة تلتهم الذاكرة أو ينشئ كوداً تكرارياً غير مبرر في مشاريع كوتلن التي توفر حلولاً لغوية مدمجة.",
        "worked_example_ar": "أمثلة الأنماط الأربعة:\n```kotlin\n// Singleton: كائن وحيد في الذاكرة\nobject NetworkConfig {}\n// Factory: إنشاء كائن محدد\nfun createPlayer(type: Type): Player\n// Abstract Factory: إنشاء عائلة كائنات متوافقة\ninterface ThemeFactory { fun btn(): Button; fun txt(): TextView }\n// Builder: بناء كائن معقد خطوة بخطوة\nRetrofit.Builder().baseUrl(\"...\").build()\n```",
        "trade_offs_ar": "الـ Singleton يوفر تكرار الإنشاء لكنه يحجز الرام، والـ Factory يعزل التفاصيل لكنه يزيد عدد الكلاسات، والـ Builder يسهل القراءة لكنه يتطلب كلاس مساعد.",
        "failure_modes_ar": "تخزين Activity داخل كائن Singleton مما يسبب تسريب ذاكرة، أو كتابة كلاس Builder معقد لكلاس بيانات عادي بدلاً من استخدام Data Class بمعاملات افتراضية.",
        "production_perspective_ar": "في المشروعات الكبرى، نستبدل الـ Singleton الكلاسيكي بـ `@Singleton` في Hilt لضمان سهولة عمل Mocking في الـ Tests، ونستخدم Builder في الـ SDKs الموجهة لعملاء خارجيين فقط.",
        "how_to_answer_ar": "اشرح كل نمط في سطرين بوضوح: Singleton للنسخة الواحدة، Factory لإنشاء منتج محدد، Abstract Factory لعائلة منتجات مترابطة، و Builder للبناء التدريجي للكائنات المعقدة، ووضح كيف تديرها في كوتلن.",
        "talking_points_ar": "فروق الأنماط الإنشائية الأربعة، والفرق بين Factory و Abstract Factory، وحل مشكلة Telescoping Constructor بـ Builder، وتفضيل Hilt Scopes على Singletons الثابتة.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق الجوهري بين Factory Method و Abstract Factory؟\"\n  **المرشح:** \"الـ Factory Method بتنتج منتجاً واحداً محدداً عبر دالة، بينما الـ Abstract Factory هي مصنع لمصانع بتنتج عائلة كاملة من الكائنات المترابطة اللي بتشتغل مع بعض بتناسق.\"\n\n- **المحاور:** \"هل الـ Kotlin object آمن للتزامن (Thread-safe)؟\"\n  **المرشح:** \"نعم، الـ JVM بيهيئ كائن الـ object داخل static initializer block مضمون ومحمي بواسطة كلاس لودر الـ JVM تلقائياً.\"",
        "self_check_ar": "هل شرحت الأنماط الأربعة بوضوح؟ هل فرقت بين Factory و Abstract Factory؟ وهل وضحت بدائل كوتلن لنمط Builder؟",
        "references_ar": f"- [Creational Patterns in Kotlin](https://refactoring.guru/design-patterns/creational-patterns) — الدليل التفاعلي للأنماط الإنشائية.\n- [Effective Java by Joshua Bloch](https://en.wikipedia.org/wiki/Effective_Java) — المرجع الكلاسيكي لأنماط Builder و Singleton.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نمط Singleton بيضمن وجود نسخة واحدة فقط من الكائن في الذاكرة مع نقطة وصول عامة. نمط Factory Method بيعزل إنشاء كائن محدد ورا إنترفيس عشان المستهلك ميعرفش الكلاس الحقيقي. نمط Abstract Factory بيصعد التجريد خطوة لإنشاء عائلة كاملة من الكائنات المترابطة معاً بدون تحديد كلاساتها الملموسة. نمط Builder بيبني كائن معقد خطوة بخطوة عبر إعداد المعاملات تدريجياً لإنتاج كائن ثابت وغير قابل للتعديل عند استدعاء `build()`.",
        "best_answer_ar": "الأنماط الإنشائية الأربعة دي بتغطي درجات مختلفة من تعقيد بناء الكائنات في هندسة البرمجيات.\n\nالـ Singleton بنستخدمه لما نكون محتاجين نسخة وحيدة تشارك موارد عامة في التطبيق زي الـ Database أو كاش التوكن. في كوتلن بنعمله بكلمة `object`، لكن في المشاريع الكبيرة بنفضل نعمله عبر `@Singleton` في Hilt لتفادي مشاكل الـ Static State وتسهيل الاختبارات.\n\nالـ Factory Method بنلجأ له لما يكون الكلاس محتاج ينشئ كائن بيحقق Interface معين، ومش عايز يربط نفسه بنوع الكائن الحقيقي. فبدل ما ينادي `new`، بيستدعي دالة المصنع اللي بتحدد التنفيذ المناسب حسب البيئة أو المدخلات.\n\nالـ Abstract Factory بيوسع المفهوم ده لعائلات من الكائنات المترابطة. فبدل ما ينتج كائناً واحداً، المصنع ده بيحتوي على عدة دوال لإنتاج مكونات متناسقة مع بعضها، زي مصنع واجهات المستخدم اللي بينتج أزرار ونصوص وقوائم متوافقة مع Dark Theme أو Light Theme.\n\nالـ Builder بيحل مشكلة الـ Telescoping Constructor، لما يكون الكائن محتاج معاملات كتير جداً بعضها إجباري وبعضها اختياري. فبدل ما نعمل كونستركتور فيه 15 بارامتر، الـ Builder بيسمح للمطور بضبط الإعدادات خطوة بخطوة وبشكل مقروء، وينتج كائناً نهائياً غير قابل للتعديل (Immutable) مع التأكد من صحة البيانات.",
        "deep_answer_ar": "تحت الكابوت، الأنماط دي بتنعكس بشكل مباشر على كفاءة الذاكرة ومسارات الـ Virtual Method Table (vtable) في بيئة الـ JVM و ART.\n\nفي الـ Singleton، كوتلن بتطبق نمط الـ `object` عبر حقل `static final` يتم تهيئته ذرّياً داخل الـ Static Class Initializer بدون أي تكلفة Synchronized إضافية بعد التهيئة الأولى. لكن المهندسين الكبار بيتجنبوا الـ Static Objects في المعماريات الحديثة، وبيستبدلوها بـ Scoped Singletons عبر Hilt؛ لأن مراجع الـ Static بتمسك الذاكرة ومبتسمحش بعمل Fakes أثناء اختبارات الـ Unit Tests المتوازية.\n\nفي الـ Factory و Abstract Factory، الفائدة المعمارية مش بس التجريد، بل إمكانية تقسيم المشروع لموديولات (Modularization) صارمة. موديولات الـ Features بتعتمد فقط على الـ Abstract Factory interfaces، بينما الكلاسات الحقيقية بتعيش مستخبية في موديولات داخلية (Internal)، وده بيمنع أي تسريب لتفاصيل التنفيذ ويسرع الـ Build Time.\n\nأما بخصوص الـ Builder، لغة Kotlin قللت جداً من الحاجة لكتابة Builders يدوية بفضل ميزة الـ Named Arguments والـ Default Parameters في الـ Data Classes. بنحتفظ بنمط الـ Builder حصرياً في تصميم الـ Public SDKs، ومكتبات التعامل مع الشبكة زي Retrofit و OkHttpClient؛ لأنها بتتطلب فحصاً معقداً للعلاقات بين المتغيرات (Cross-field Validation) قبل السماح بإنشاء الكائن في الذاكرة."
    }
}

# ==========================================
# PAT-04: Explain Adapter, Facade, Decorator, and Proxy.
# ==========================================
DATA["PAT-04"] = {
    "concept_en": """Structural patterns address class and object composition, creating flexible abstractions that allow disparate systems to collaborate seamlessly without architectural friction. Adapter converts the existing interface of an incompatible class into an expected target interface, enabling classes with mismatched signatures to interoperate. Facade provides a simplified, unified high-level interface to a complex subsystem, shielding external consumers from underlying implementation intricacies and reducing subsystem dependencies. Decorator attaches additional responsibilities and dynamic behaviors to an object transparently by wrapping it within an identical interface contract, serving as a flexible alternative to subclassing. Proxy provides a surrogate, placeholder, or access-control intermediary for another object, governing access, lazy initialization, logging, or remote inter-process communication transparently.""",
    "walkthrough_en": """Demonstrating Adapter, Facade, Decorator, and Proxy in Android:
```kotlin
// 1. ADAPTER: Converts third-party vendor signature to domain interface
class VendorPaymentSdk { fun chargeCard(cents: Int, cardNum: String): Boolean = true }
interface PaymentGateway { suspend fun pay(amountDollars: Double): Boolean }

class VendorPaymentAdapter(private val sdk: VendorPaymentSdk) : PaymentGateway {
    override suspend fun pay(amountDollars: Double): Boolean =
        sdk.chargeCard((amountDollars * 100).toInt(), "tokenized_card")
}

// 2. FACADE: Simplifies complex Android Biometric & Keyguard subsystem
class BiometricAuthFacade(private val activity: FragmentActivity) {
    fun authenticate(onSuccess: () -> Unit, onError: (String) -> Unit) {
        // Encapsulates BiometricPrompt, PromptInfo, and Executor complexity
        val prompt = BiometricPrompt(activity, ContextCompat.getMainExecutor(activity),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) = onSuccess()
                override fun onAuthenticationError(code: Int, err: CharSequence) = onError(err.toString())
            })
        prompt.authenticate(BiometricPrompt.PromptInfo.Builder().setTitle("Login").build())
    }
}

// 3. DECORATOR: Wraps component to dynamically add logging behavior
interface OrderService { suspend fun submitOrder(id: String) }
class LoggingOrderDecorator(private val delegate: OrderService) : OrderService by delegate {
    override suspend fun submitOrder(id: String) {
        println("Submitting order: $id")
        delegate.submitOrder(id) // Delegates execution
        println("Order submitted successfully")
    }
}

// 4. PROXY: Controls lazy initialization and permission validation
class ProtectedDocumentProxy(private val userRole: String) {
    private val realDocument: HeavyDocument by lazy { HeavyDocument() }
    fun read(): String = if (userRole == "ADMIN") realDocument.getContent() else error("Forbidden")
}
```""",
    "short_en": """Adapter transforms an incompatible interface into one the client expects. Facade provides a simplified high-level entry point to a complex subsystem. Decorator dynamically enhances an object with additional responsibilities by wrapping it within an identical interface. Proxy controls access to an underlying object, managing lazy instantiation, security checks, or inter-process communication. Each structural pattern wraps an underlying collaborator with a distinct architectural intent.""",
    "structured_en": """Structural patterns resolve composition and integration challenges by providing clear abstraction boundaries between components.
The Adapter pattern acts as a translator between incompatible interfaces. When integrating an external library, legacy module, or hardware SDK whose API does not match your domain contracts, an Adapter wraps the external component and exposes the expected clean interface. In Android, RecyclerView.Adapter is a classic framework example, adapting raw domain lists into ViewHolders.
The Facade pattern provides a simplified, unified interface to a complex collection of interacting classes or subsystems. It reduces coupling by presenting consumers with an ergonomic entry point. In mobile engineering, facades are frequently written around complicated Android system services, such as wrapping BiometricPrompt, KeyguardManager, and Keystore crypto operations behind a clean, single-method authentication service.
The Decorator pattern dynamically adds behavior to an object without modifying the original class or resorting to rigid class inheritance. By implementing the same interface as the wrapped object, the decorator intercepts calls, adds functionality like caching or logging, and forwards execution to the delegate.
The Proxy pattern controls and manages access to an underlying target object. While structurally identical to Decorator, its intent is access control: providing lazy instantiation for expensive resources, verifying user permissions, or managing Android IPC through Binder proxies.""",
    "deep_senior_en": """Under the hood, these four structural patterns share a common delegation mechanism: an outer wrapper class holds an internal reference to a target collaborator and delegates method calls. The senior differentiator lies entirely in architectural intent and lifecycle governance.
Adapter changes an interface to resolve an incompatibility between two systems that cannot be modified. It operates at architectural seams, translating third-party SDK models into internal domain models.
Facade creates a new, simplified interface to hide subsystem spaghetti. It does not wrap a single object; it orchestrates multiple interacting classes (network clients, disk caches, encryption ciphers) into a cohesive service, dramatically reducing compilation dependencies across feature modules.
Decorator maintains an identical interface while augmenting runtime behavior. In Android networking, OkHttp Interceptors represent the canonical decorator implementation, where each interceptor wraps request execution to inject auth headers, compress payloads, or log network metrics. Kotlin's by-interface delegation syntax (class AuthClient(inner: Api) : Api by inner) makes decorator authoring zero-boilerplate.
Proxy also maintains an identical interface, but governs the lifecycle and accessibility of the underlying object. In Android's operating system, every AIDL client interface is a remote Proxy (BinderProxy) that marshals method arguments across process boundaries into the system server.
Staff engineers enforce these patterns at architectural boundaries to maintain high cohesion and prevent vendor lock-in across enterprise mobile codebases.""",
    "meta_ar": {
        "id": "PAT-04",
        "questionAr": "اشرح أنماط Adapter و Facade و Decorator و Proxy مع توضيح الفروق الجوهرية بينها.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الأنماط الهيكلية الأربعة وتفريقها من حيث الهدف المعماري (Intent)، ومعرفة كيف تستخدم في بيئة أندرويد لعزل مكتبات الطرف الثالث، وتبسيط الأنظمة المعقدة، وحماية الموارد.",
        "why_it_matters_ar": "هذه الأنماط الأربعة تبدو متشابهة برمجياً لأنها تعتمد على التغليف (Wrapping)، وغياب الفهم الدقيق لأهدافها يقود لتصميم طبقات وسيطة مشوشة وغير مفيدة.",
        "worked_example_ar": "أمثلة الأنماط الأربعة في أندرويد:\n```kotlin\n// Adapter: مواءمة واجهة (RecyclerView.Adapter)\n// Facade: واجهة مبسطة للبصمة والـ Keystore (BiometricFacade)\n// Decorator: إضافة سلوك للشبكة (OkHttp Interceptor)\n// Proxy: وسيط تحكم في الوصول (AIDL BinderProxy)\n```",
        "trade_offs_ar": "هذه الأنماط تضيف عمقاً في استدعاء الدوال (Call Stack Depth) وكوداً وسيطاً، لكنها تمنح فك ارتباط هائل وعزلاً كاملاً للمكتبات الخارجية.",
        "failure_modes_ar": "بناء Facade معقد يتحول لكائن إلهي (God Object)، أو استخدام Decorator بشكل مبالغ فيه مما يجعل تتبع الأخطاء في الـ Stack Trace معقداً ومظللاً.",
        "production_perspective_ar": "في المشروعات الكبرى، نفرض استخدام Adapter و Facade على أي SDK خارجي (زي بوابات الدفع أو الـ Analytics) لمنع انتشار كود المكتبة في طبقات التطبيق وسهولة استبدالها لاحقاً.",
        "how_to_answer_ar": "بين أن الكلاسات الأربعة بتعتمد على التغليف لكن النوايا مختلفة: Adapter لتغيير الواجهة، Facade لتبسيط نظام معقد، Decorator لإضافة مسؤوليات، و Proxy للتحكم في الوصول أو تأجيل البناء.",
        "talking_points_ar": "فروق النوايا المعمارية (Architectural Intent)، ومثال RecyclerView.Adapter، وتبسيط الخدمات المعقدة بـ Facade، وشبكة الفلاتر بـ Decorator، والـ Binder Proxy في أندرويد.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق الجوهري بين Decorator و Proxy بما إن الاتنين ليهم نفس الواجهة الأصلية للكائن؟\"\n  **المرشح:** \"الـ Decorator بيضيف وظائف جديدة (Enhancement) بدون ما يتحكم في وجود الكائن، بينما الـ Proxy هدفه الأساسي هو التحكم في الوصول (Access Control) أو تأجيل إنشائه (Lazy Loading) أو إدارة الـ IPC.\"\n\n- **المحاور:** \"إزاي أندرويد بيستخدم نمط Proxy في التعامل بين العمليات (IPC)؟\"\n  **المرشح:** \"عبر الـ AIDL والـ Binder؛ الكود بتاعك بيكلم كائن BinderProxy محلي في نفس عمليتك، والبروكسي بيعمل Marshal للداتا ويبعتها للـ System Server في العملية التانية.\"",
        "self_check_ar": "هل وضحت الفروق الجوهرية في النوايا المعمارية؟ هل ضربت أمثلة من أندرويد لكل نمط؟ وهل بينت كيف تمنع ارتباط الكود بالمكتبات الخارجية؟",
        "references_ar": f"- [Structural Patterns in Software Architecture](https://refactoring.guru/design-patterns/structural-patterns) — التوثيق التفاعلي للأنماط الهيكلية.\n- [Android Binder Architecture](https://source.android.com/docs/core/architecture/kernel/binder) — الدليل التقني لكيفية عمل Binder Proxy في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الأنماط الأربعة بتعتمد على تغليف كائن وسيط، لكن الهدف المعماري مختلف تماماً. نمط Adapter بيغير واجهة كائن غير متوافقة عشان يخليها متوافقة مع نظامك. نمط Facade بيقدم واجهة جديدة مبسطة تختصر نظاماً كاملاً ومعقداً من الكلاسات. نمط Decorator بيحافظ على نفس الواجهة الأصلية للكائن لكن بيضيف عليها وظائف ومسؤوليات إضافية زي الفلاتر وتسجيل البيانات. نمط Proxy بيحافظ برضه على نفس الواجهة لكن وظيفته هي التحكم في الوصول للكائن، زي الحماية أو تأجيل البناء في الذاكرة أو التواصل عبر العمليات في أندرويد (IPC).",
        "best_answer_ar": "الأنماط الهيكلية الأربعة دي بتبان متشابهة من برة لأن كلها كلاسات بتغلف كائنات تانية، لكن النية المعمارية (Intent) لكل نمط هي اللي بتحدد استخدامه الصح.\n\nنمط الـ Adapter بنلجأ له لما يكون عندنا مكتبة خارجية أو كود قديم بواجهة معينة، والتطبيق بتاعنا متوقع واجهة تانية خالص. الـ Adapter بياخد دور المترجم اللي بيوفق بين الواجهتين بدون ما نعدل كود المكتبة نفسها، زي الـ `RecyclerView.Adapter` في أندرويد.\n\nنمط الـ Facade بيستخدم لتبسيط نظام معقد جداً. لو عندك مكتبة بتتطلب مناداة 5 كلاسات وضبط إعدادات مشربكة زي الـ BiometricPrompt مع الـ Keystore، بنعمل كلاس Facade يوفر دالة واحدة بسيطة `authenticate()` تخفي كل اللفة دي وراها وتريح المطورين.\n\nنمط الـ Decorator بيضيف مسؤوليات وإمكانيات جديدة لكائن موجود بدون ما نعدل الكلاس الأصلي أو نعمل وراثة صلبة. الميزة إنه بيحتفظ بنفس الـ Interface الأصلي، زي الـ OkHttp Interceptors اللي بتغلف طلب الشبكة وتضيف عليه Logging أو Headers.\n\nنمط الـ Proxy بيحتفظ بنفس الواجهة برضه، لكن هدفه مش إضافة وظائف جديدة، بل التحكم في الوصول للكائن الأصلي. بنستخدمه للـ Lazy Loading لكائنات تقيلة، أو لفحص صلاحيات الأمان، أو لإدارة التواصل بين عمليتين مختلفتين عبر الـ Binder في أندرويد.",
        "deep_answer_ar": "تحت الكابوت، الأنماط الأربعة دي بتشترك في آلية التفويض (Delegation Mechanism)؛ كلاس خارجي ماسك مرجع لكائن داخلي وبيوجه النداءات إليه. النقطة الفاصلة في مقابلات الـ Senior هي التمييز الدقيق في الـ Lifecycle والـ Structural Intent.\n\nالـ Adapter بيشتغل على حدود الـ Architecture (Architectural Seams) لحماية الدومين من التلوث بنماذج الـ 3rd-party SDKs؛ فبنعمل Adapter يحول كولباكات مكتبة الدفع لـ Kotlin Result Coroutine. الـ Facade من ناحية تانية مش بيغلف كائن واحد، بل بينسق أوركسترا كاملة من الكلاسات (Ciphers, Prompts, Preferences) لتقليل الـ Coupling وتسريع زمن الـ Compilation عبر الموديولات.\n\nأما المقارنة الأكثر دقة فهي بين Decorator و Proxy لأن الاتنين بيحققوا نفس الـ Interface الأصلي للكائن. الفارق الجوهري هو: الـ Decorator بيوسع السلوك (Enhances Behavior)؛ والعميل هو اللي بيحدد ترتيب التغليف زي سلاسل الـ Interceptors في الشبكة. في المقابل، الـ Proxy بيتحكم في دورة حياة ووجود الكائن الأصلي (Controls Access)؛ الكائن الأصلي ممكن ميكونش اتخلق أصلاً في الذاكرة لحد ما البروكسي يقرر إن الصلاحيات سليمة ومستاهلة تنشئه.\n\nوفي نظام أندرويد الداخلي، الـ IPC كله مبني على الـ Proxy Pattern؛ كل استدعاء لخدمة زي `LocationManager` بيعدي على كائن `BinderProxy` بيحول الميثود لـ Parcel ويبعتها عبر درايفر اللينكس لعملية الـ System Server بدون ما المطور يحس بأي تعقيد."
    }
}

# ==========================================
# PAT-05: Explain Observer, Strategy, State, Command, and Chain of Responsibility.
# ==========================================
DATA["PAT-05"] = {
    "concept_en": """Behavioral patterns govern dynamic algorithmic execution, responsibility distribution, and messaging protocols between collaborating objects, decoupling the invocation of an operation from its concrete execution. Observer establishes a one-to-many subscription model where state changes in a subject automatically notify registered observers reactively. Strategy encapsulates a family of interchangeable algorithms behind a common contract, allowing the algorithm to vary independently from consuming clients. State allows an object to alter its behavioral logic dynamically as its internal state changes, modeling state transitions cleanly without fragile conditional branching. Command encapsulates a request as a standalone object, enabling request parameterization, queueing, and undoable transactions. Chain of Responsibility decouples the sender of a request from its potential receivers by passing the request along a sequential handler pipeline until handled.""",
    "walkthrough_en": """Behavioral Pattern implementations across Android and Kotlin:
```kotlin
// 1. OBSERVER: Reactive emission via Flow
class CounterSubject {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()
    fun increment() { _count.value += 1 }
}

// 2. STRATEGY: Interchangeable validation algorithms
interface ValidationStrategy { fun isValid(input: String): Boolean }
class EmailValidationStrategy : ValidationStrategy {
    override fun isValid(input: String) = android.util.Patterns.EMAIL_ADDRESS.matcher(input).matches()
}

// 3. STATE PATTERN: Clean state transition machine
sealed interface DownloadState {
    fun handlePause(context: DownloadContext)
}
object Downloading : DownloadState {
    override fun handlePause(context: DownloadContext) { context.state = Paused }
}
object Paused : DownloadState {
    override fun handlePause(context: DownloadContext) { /* Already paused */ }
}
class DownloadContext { var state: DownloadState = Downloading }

// 4. COMMAND: Encapsulated undoable user action
interface EditorCommand { fun execute(); fun undo() }
class InsertTextCommand(private val doc: Document, private val text: String) : EditorCommand {
    override fun execute() = doc.append(text)
    override fun undo() = doc.deleteLast(text.length)
}

// 5. CHAIN OF RESPONSIBILITY: Pipeline processing (OkHttp Interceptor model)
interface Interceptor {
    fun intercept(chain: Chain): Response
    interface Chain { fun proceed(request: Request): Response }
}
```""",
    "short_en": """Observer notifies multiple subscribers reactively when subject state changes. Strategy encapsulates swappable algorithms behind a common interface. State dynamically alters an object's behavior based on internal state transitions. Command encapsulates a request as an object to support queuing, logging, and undo operations. Chain of Responsibility passes a request along a pipeline of sequential handlers until processed. Each behavioral pattern decouples execution mechanics from invoking components.""",
    "structured_en": """Behavioral patterns provide decoupled mechanisms for managing communication, state coordination, and algorithmic execution across application components.
The Observer pattern establishes a subscription model where state-holders notify dependents automatically when changes occur. In Android, Kotlin StateFlow, SharedFlow, and LiveData are canonical implementations, enabling reactive UI updates that respond to data stream emissions without tight coupling between presentation and domain layers.
The Strategy pattern defines a family of interchangeable algorithms, encapsulating each behind a shared interface. Consumers hold a reference to the strategy contract, allowing algorithmic policies such as sorting, caching, or discount calculations to be swapped dynamically at runtime or substituted during testing.
The State pattern allows an object to alter its behavior when its internal state changes. Instead of scattering complex, error-prone when or if-else ladders across methods, state-specific behavior is encapsulated inside dedicated state objects that manage their own transitions.
The Command pattern turns a request into a standalone object encapsulating the action, receiver, and execution parameters. This facilitates transactional queueing, offline action synchronization, and reversible operations like undo and redo.
The Chain of Responsibility pattern passes a request sequentially through a pipeline of handlers. Each handler inspects the request and chooses whether to process it, short-circuit execution, or pass it to the next link in the chain, as seen in OkHttp network interceptors and Android touch event dispatching.""",
    "deep_senior_en": """Under the hood, behavioral patterns manage runtime message dispatch and decoupling, directly impacting call stack execution, thread safety, and memory retention.
In modern Android architecture, language evolutions in Kotlin have streamlined these classic patterns. The Observer pattern has evolved from error-prone callback interfaces with manual unsubscription to structured, lifecycle-aware Kotlin Coroutine Flows that automatically cancel upon coroutine scope teardown, completely eliminating listener memory leaks.
The Strategy pattern, which traditionally required creating dozens of boilerplate Java classes, is frequently replaced in Kotlin by first-class functions and lambdas (typealias DiscountStrategy = (Double) -> Double), maintaining clean decoupling with zero class overhead.
The State pattern has converged with modern Unidirectional Data Flow (UDF) paradigms. Rather than mutating state internally inside state objects, senior engineers leverage Kotlin sealed interfaces to model immutable state hierarchies emitted across StateFlow pipelines. ViewModels process user intents through pure functional reducers, achieving deterministic state transitions that are trivial to verify in unit tests.
Chain of Responsibility remains the premier architecture for pipeline processing. In OkHttp's RealInterceptorChain, handlers wrap each other recursively, allowing cross-cutting concerns like caching, authentication retry, and gzip compression to execute transparently before socket I/O.
Staff engineers leverage these behavioral patterns to maintain clean boundaries between event triggers and execution pipelines, ensuring high maintainability and testability.""",
    "meta_ar": {
        "id": "PAT-05",
        "questionAr": "اشرح أنماط Observer و Strategy و State و Command و Chain of Responsibility في بيئة أندرويد.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الأنماط السلوكية الخمسة الأساسية، والقدرة على شرح كيفية إدارة التفاعل والتواصل بين الكائنات، ومعرفة تجسيداتها الحقيقية في أندرويد مثل Flow و Interceptors وتوزيع أحداث اللمس.",
        "why_it_matters_ar": "هذه الأنماط هي العمود الفقري لتنظيم تدفق البيانات والأحداث في تطبيقات أندرويد الحديثة، وفهمها بعمق يمنع فوضى الشروط المتشعبة (If-Else Hell) وتسريبات الذاكرة الناتجة عن الـ Listeners.",
        "worked_example_ar": "أمثلة الأنماط السلوكية في أندرويد:\n```kotlin\n// Observer: Flow/StateFlow لمراقبة الداتا\n// Strategy: تبديل خوارزميات التحقق أو الخصم\n// State: آلة حالة الشاشة (Sealed UI State)\n// Command: أمر قابل للإلغاء (Undo/Redo)\n// Chain of Responsibility: فلاتر OkHttp Interceptors\n```",
        "trade_offs_ar": "الأنماط السلوكية تعزل المنطق وتمنع التكرار، لكنها قد تزيد عدد الكلاسات وملفات الـ State ما لم تستخدم ميزات كوتلن الذكية كـ Lambdas و Sealed Interfaces.",
        "failure_modes_ar": "نسيان إلغاء الاشتراك في Listeners نمط Observer التقليدي مما يسبب تسريب ذاكرة، أو استخدام مصفوفة شروط معقدة `if/else` بدلاً من نمط State للتحكم في مشغل الفيديو.",
        "production_perspective_ar": "في المشروعات الكبرى، نمثل نمط Observer بـ Kotlin Flow حصرياً، ونستخدم Chain of Responsibility لإدارة مصادقة وتجديد توكنات الشبكة، ونعتمد على State في إدارة دورات حياة الشاشات.",
        "how_to_answer_ar": "عرف كل نمط بكلمات محددة: Observer للمراقبة التفاعلية، Strategy للخوارزميات القابلة للتبديل، State لتغيير السلوك حسب الحالة، Command لتغليف الأوامر وعمليات التراجع، و Chain of Responsibility لتمرير الطلب عبر سلسلة معالجات.",
        "talking_points_ar": "تطور الأنماط السلوكية في أندرويد، وتحول Observer إلى StateFlow، واستبدال Strategy بـ Lambdas، واستخدام Chain of Responsibility في OkHttp وأحداث اللمس (TouchEvent).",
        "follow_ups_ar": "- **المحاور:** \"كيف يطبق نظام أندرويد نمط Chain of Responsibility في معالجة اللمسات على الشاشة؟\"\n  **المرشح:** \"عبر سلسلة دوال `dispatchTouchEvent` ثم `onInterceptTouchEvent` ثم `onTouchEvent`، حيث يمرر الـ ViewGroup اللمسة لأبنائه حتى يقرر أحدهم معالجتها وإيقاف السلسلة.\"\n\n- **المحاور:** \"ما الفرق بين نمطي Strategy و State برمجياً؟\"\n  **المرشح:** \"في Strategy العميل بيختار الخوارزمية من الخارج واستخدامها مستقل، بينما في State الكائن هو اللي بيغير حالته وسلوكه داخلياً من حالة لأخرى.\"",
        "self_check_ar": "هل شرحت الأنماط الخمسة بدقة؟ هل ربطت Observer بـ Flow؟ وهل بينت تطبيق Chain of Responsibility في OkHttp ولمسات الشاشة؟",
        "references_ar": f"- [Behavioral Patterns Guide](https://refactoring.guru/design-patterns/behavioral-patterns) — الدليل التفاعلي للأنماط السلوكية.\n- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html) — التوثيق الرسمي لنمط Observer الحديث في كوتلن.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الأنماط السلوكية بتنظم طريقة تواصل الكائنات مع بعضها وسريان البيانات. نمط Observer بيسمح لكائنات متعددة بمراقبة مصدر بيانات واحد والتفاعل تلقائياً مع أي تغيير زي StateFlow. نمط Strategy بيعزل خوارزميات قابلة للتبديل ورا واجهة موحدة زي طرق التحقق من الإدخال. نمط State بيخلي الكائن يغير تصرفاته تماماً لما حالته الداخلية تتغير بدون تعقيد الشروط زي حالات مشغل الميديا. نمط Command بيغلف الطلب ككائن مستقل لتنفيذ طوابير المهام أو التراجع عن العمليات. ونمط Chain of Responsibility بيمرر الطلب عبر سلسلة معالجات متتالية لحد ما حد فيهم يقرر يعالجه زي OkHttp Interceptors.",
        "best_answer_ar": "الأنماط السلوكية الخمسة دي بتمثل القواعد الذهبية لتنظيم منطق العمل وتدفق الأحداث في أندرويد بدون كتابة كود متشابك.\n\nنمط الـ Observer هو الأساس التفاعلي لأندرويد؛ الكلاس صاحب البيانات بينشر التحديثات، والمستهلكين بيراقبوا التغييرات ويتفاعلوا معاها بدون ما صاحب البيانات يعرف مين بيراقبه، وده متجسد في StateFlow و SharedFlow.\n\nنمط الـ Strategy بيفصل الخوارزميات عن الكلاس المستهلك. لو عندك تطبيق تجارة إلكترونية بيحسب الخصم بطرق مختلفة، بتعرف إنترفيس `DiscountStrategy` وتعمل كلاسات مختلفة للخصم، والـ ViewModel يقدر يبدل بينهم بسلاسة.\n\nنمط الـ State بيحل مشكلة تعقيد الشروط `if-else` عند تتبع حالات الأنظمة؛ الكائن بينتقل من حالة لحالة، وكل حالة بتحدد السلوك المتاح. في مشغل الفيديو مثلاً، الضغط على زرار التشغيل في حالة `Buffering` بيعمل تصرف مختلف تماماً عن ضغطه في حالة `Playing`.\n\nنمط الـ Command بيحول الأكشن لكائن مستقل بيحتوي على كل بيانات التنفيذ. ده بيسمح بتنظيم طوابير المهام (Queuing)، وتأجيل العمليات عند انقطاع الإنترنت، ودعم التراجع والتقدم (Undo/Redo) في تطبيقات التعديل.\n\nنمط الـ Chain of Responsibility بيمرر الطلب في خط أنابيب من المعالجات (Pipeline)؛ كل معالج بيفحص الطلب ويقرر إما ينفذه، أو يعدل فيه ويمرره للي بعده، وده النموذج المثالي اللي مبني عليه الـ OkHttp Interceptors ونظام توزيع لمسات الشاشة (Touch Events) في أندرويد.",
        "deep_answer_ar": "تحت الكابوت، الأنماط السلوكية بتدير سريان الرسائل وحركة البيانات في الـ Stack والـ Heap، وبتلعب دوراً محورياً في منع تسريبات الذاكرة وتنظيم التزامن.\n\nلغة Kotlin الحديثة طورت الأنماط دي ونقلتها لمستوى هندسي أرقى بكثير: نمط Observer تحول من كولباكات قديمة كانت بتسرب الذاكرة لو نسي المطور يلغي تسجيلها، إلى Kotlin Flow المدمج مع الـ Coroutines ومرتبط بدورة حياة الكومبوننت (Lifecycle-aware)، حيث يتوقف الاشتراك ويتحرر تلقائياً بمجرد تدمير الـ CoroutineScope.\n\nنمط الـ Strategy اللي كان بيتطلب كتابة كلاسات Java منفصلة لكل خوارزمية، بقى ممكن صياغته في كوتلن كـ First-class Function أو Lambda بسيطة تتمرر في دالة واحدة بدون أي كود زائد.\n\nأما نمط الـ State فاندحر أمامه كابوس الـ Boolean Flags المتناثرة، وامتزج مع معمارية Unidirectional Data Flow (UDF)؛ حيث يتم نمذجة الحالات كـ Sealed Interfaces غير قابلة للتعديل وتمريرها في الـ StateFlow، وتقوم الـ Reducer Functions بتطبيق الانتقالات بطريقة وظيفية نقية (Pure Functional Transitions) تسهل اختبارها بالـ Unit Tests.\n\nوفي الـ Chain of Responsibility، بنشوف عظمة التنفيذ العودي في `RealInterceptorChain` الخاص بـ OkHttp؛ كل فلتر بيغلف اللي بعده لمعالجة مهام أمنية كإضافة التوكن وإعادة المحاولة وضغط البيانات في مسار واحد متناسق قبل الوصول لطبقة الـ Network Socket.\n\nالمهندسون الكبار بيستخدموا الأنماط دي لفك الارتباط التام بين مُطلق الحدث ومُنفذه، مما يضمن كوداً عالي المرونة وقابلاً للاختبار بسهولة فائقة."
    }
}

# ==========================================
# PAT-06: Where does Repository fit as an architectural/data-access pattern?
# ==========================================
DATA["PAT-06"] = {
    "concept_en": """The Repository pattern is an architectural data-access abstraction that mediates between domain business logic and data-mapping layers, mimicking an in-memory collection of domain entities. Originating from Domain-Driven Design (DDD), it centralizes data retrieval, storage, caching policies, and synchronization rules while completely concealing storage mechanisms, network protocols, and persistence drivers from UseCases and ViewModels. In modern Android architecture, the Repository acts as the Single Source of Truth (SSOT), exposing reactive data streams (such as Flow<T>) powered by local persistence engines while orchestrating asynchronous remote network refreshes, error translations, and offline synchronization transparently.""",
    "walkthrough_en": """Implementing Single Source of Truth in a Repository:
```kotlin
// Domain Entity (Pure Kotlin, zero Room or Retrofit dependencies)
data class UserProfile(val id: String, val name: String, val email: String)

// Repository Interface in Domain Layer
interface UserRepository {
    fun observeUserProfile(userId: String): Flow<UserProfile>
    suspend fun refreshUserProfile(userId: String): Result<Unit>
}

// Concrete Implementation in Data Layer (Mediates Room and Retrofit)
class UserRepositoryImpl @Inject constructor(
    private val localDao: UserDao,
    private val remoteApi: UserApiService,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) : UserRepository {

    // Single Source of Truth: UI observes local database stream exclusively
    override fun observeUserProfile(userId: String): Flow<UserProfile> =
        localDao.observeUser(userId).map { entity -> entity.toDomainModel() }

    // Remote refresh fetches from network, persists into Room, triggering Flow emission
    override suspend fun refreshUserProfile(userId: String): Result<Unit> = withContext(ioDispatcher) {
        runCatching {
            val response = remoteApi.fetchUser(userId)
            localDao.upsertUser(response.toEntity()) // Database update emits automatically!
        }
    }
}
```""",
    "short_en": """The Repository pattern acts as an in-memory collection mediating between domain logic and disparate data sources. It hides networking, local persistence, and caching mechanisms from ViewModels and UseCases. In Android Clean Architecture, the Repository establishes a Single Source of Truth, exposing reactive streams from the local database while orchestrating background network synchronization and offline-first capabilities.""",
    "structured_en": """The Repository pattern serves as the critical bridge connecting application domain logic to low-level data infrastructure.
Without a Repository, ViewModels or UseCases directly invoke network clients, database DAOs, and shared preferences. This scattering of data access logic introduces tight coupling, duplicates caching algorithms, leaks infrastructure details into UI logic, and makes automated testing nearly impossible.
The Repository pattern resolves this by encapsulating data access behind a domain interface that behaves like an in-memory collection of domain objects. Calling layers simply request or observe data without any knowledge of whether it originates from a remote REST API, an in-memory cache, or an encrypted SQLite database.
In recommended Android architecture, the Repository is responsible for enforcing the Single Source of Truth principle. The repository exposes continuous reactive Flow streams sourced from local Room tables. When a refresh is requested, the repository asynchronously fetches data from the network, saves it into the local database, and relies on database reactivity to notify the UI automatically. This architecture provides seamless offline-first support, isolates caching policies, and establishes clean boundaries for unit testing.""",
    "deep_senior_en": """Under the hood, the Repository pattern enforces the Dependency Inversion Principle across multi-module boundaries.
In enterprise Android modularization, the repository contract (UserRepository interface) resides inside the :domain or :core:model module, which contains pure Kotlin code with zero Android framework dependencies. The concrete implementation (UserRepositoryImpl) resides in a separate :data module that encapsulates Room, Retrofit, and DataStore dependencies. By inverting this dependency via Hilt or Dagger, the domain and presentation layers remain immune to infrastructure churn: swapping Retrofit for Ktor or Room for SQLDelight requires zero changes to domain UseCases or ViewModels.
Furthermore, senior engineers use repositories to coordinate complex synchronization algorithms such as offline write queues, optimistic UI updates, conflict resolution, and background sync via WorkManager. When an offline write occurs, the repository writes an unconfirmed entity to Room, triggering an immediate UI update. A background worker then attempts remote synchronization, reconciling timestamps or version vectors without leaking network state machines into presentation code.
Staff engineers enforce strict testability seams through this pattern. Because ViewModels depend exclusively on the abstract repository interface, unit tests verify UI state machines using lightweight in-memory fake repositories, avoiding fragile mocking frameworks and eliminating Android instrumentation test overhead. Additionally, the repository orchestrates in-memory LRU memory caching alongside SQLite persistence, managing cache staleness policies, time-to-live invalidation timers, and network backoff strategies transparently without exposing cache complexity to consumers.""",
    "meta_ar": {
        "id": "PAT-06",
        "questionAr": "أين يقع نمط المستودع (Repository Pattern) في معمارية أندرويد وما هي وظيفته في الوصول للبيانات؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور الـ Repository كطبقة وسيطة بين الـ Domain ومصادر البيانات، وتطبيق مبدأ المصدر الموحد للحقيقة (Single Source of Truth)، وإدارة الكاش والبيانات غير المتصلة (Offline-first)، وفصل التبعيات المعمارية.",
        "why_it_matters_ar": "استدعاء Retrofit أو Room مباشرة من الـ ViewModel هو خطأ معماري فادح يربط الواجهة بتفاصيل التخزين، ويجعل الكود عاجزاً عن العمل بدون إنترنت ومستحيلاً في الاختبارات المؤتمتة.",
        "worked_example_ar": "تطبيق SSOT في الـ Repository:\n```kotlin\n// الواجهة تراقب قاعدة البيانات كـ SSOT\nfun observeUser(): Flow<User> = dao.observe().map { it.toDomain() }\n// والتحديث يسحب من السيرفر ويكتب في الداتابيز فقط\nsuspend fun refresh() { val net = api.get(); dao.insert(net) }\n```",
        "trade_offs_ar": "يضيف طبقة تجريد ونماذج تحويل (Mappers) إضافية، لكنه يمنح فك ارتباط مطلق وإمكانية تشغيل التطبيق بالكامل Offline بسهولة.",
        "failure_modes_ar": "جعل الـ ViewModel يقرر متى يقرأ من الكاش ومتى يقرأ من السيرفر، أو إرجاع الـ Entity التابعة لـ Room مباشرة لطبقة الـ UI مما يكسر العزل المعماري.",
        "production_perspective_ar": "في المشروعات الكبرى، تُعرف واجهات الـ Repository في موديول `:domain` الخالي من أندرويد، وتُنفذ في موديول `:data`، ويتم مراقبة الداتابيز دائماً كـ Single Source of Truth.",
        "how_to_answer_ar": "عرف الـ Repository كوسيط يعامل البيانات كمجموعة في الذاكرة، واشرح دوره كمصدر موحد للحقيقة (SSOT) يراقب الداتابيز بـ Flow ويحدثها من الشبكة، ووضح فائدته في الـ Offline-first وفصل الموديولات.",
        "talking_points_ar": "مفهوم Single Source of Truth (SSOT)، وفصل الـ Domain عن الـ Infrastructure، وإدارة الكاش والـ Offline-first، وتسهيل اختبارات الـ ViewModels باستخدام Fakes.",
        "follow_ups_ar": "- **المحاور:** \"يعني إيه Single Source of Truth (SSOT) في سياق الـ Repository؟\"\n  **المرشح:** \"معناه إن فيه مكان واحد فقط بيعتبر المرجع النهائي للبيانات في التطبيق، وغالباً بيكون الـ Local Database؛ الواجهة بتراقب الداتابيز فقط، والشبكة وظيفتها تغذي الداتابيز دي مش تكلم الـ UI مباشرة.\"\n\n- **المحاور:** \"ليه بنعرف Interface للـ Repository في موديول Domain والتنفيذ في موديول Data؟\"\n  **المرشح:** \"تطبيقاً لمبدأ Dependency Inversion؛ عشان طبقة الـ Domain تفضل كود كوتلن نقي ميعرفش أي حاجة عن Room أو Retrofit، ونقدر نبدل مكتبات التخزين بدون ما نلمس الـ Business Logic.\"",
        "self_check_ar": "هل بينت دور الـ Repository كـ SSOT؟ هل شرحت أثره على الـ Offline-first؟ وهل وضحت فصل واجهة الـ Domain عن تنفيذ الـ Data؟",
        "references_ar": f"- [Data layer and the Repository pattern](https://developer.android.com/topic/architecture/data-layer) — الدليل الرسمي لجوجل حول طبقة البيانات ونمط المستودع.\n- [Domain-Driven Design by Eric Evans](https://en.wikipedia.org/wiki/Domain-driven_design) — المرجع الأصلي لمفهوم الـ Repository في معمارية البرمجيات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نمط المستودع (Repository) بيشتغل كطبقة وسيطة بتفصل منطق العمل (UseCases و ViewModels) عن تفاصيل ومصادر البيانات التحتية زي قواعد البيانات والشبكة. وظيفته في معمارية أندرويد إنه بيكون المصدر الموحد للحقيقة (Single Source of Truth)؛ بحيث الواجهة بتراقب قاعدة البيانات المحلية عبر Flow، والـ Repository بيتولى سحب البيانات من السيرفر في الخلفية، وتحديث الداتابيز، وإدارة الكاش والعمل بدون إنترنت (Offline-first) بدون ما الـ UI يعرف أي تفاصيل.",
        "best_answer_ar": "نمط الـ Repository هو حجر الأساس لإدارة البيانات في معمارية أندرويد النظيفة، ومكانه بيكون في طبقة البيانات (Data Layer).\n\nمن غير Repository، الـ ViewModel هيضطر ينادي Retrofit مباشرة ويجيب الداتا، وبعدين ينادي Room عشان يحفظها، ولو النت قطع يدور في الـ SharedPreferences. الطريقة دي بتخلق ارتباطاً وثيقاً وفوضى عارمة، وبتخلي كود الشاشات معتمد على مكتبات التخزين والشبكة ويستحيل اختباره.\n\nالـ Repository بيحل المشكلة دي بإنه بيقدم واجهة موحدة كأنها مجموعة عناصر في الذاكرة (In-memory collection). الـ ViewModel بيطلب منه البيانات، والـ Repository هو اللي يدير السياسة: هل البيانات دي في الكاش؟ هل محتاجة تحديث من السيرفر؟ إزاي نوفق بين النت والداتابيز؟\n\nفي التصميم الحديث اللي بتوصي بيه جوجل، الـ Repository بيطبق مبدأ المصدر الموحد للحقيقة (Single Source of Truth). الـ Repository بيعرض `Flow` مستمر بيقرأ من الـ Room Database مباشرة. ولما الـ ViewModel يطلب Refresh، الـ Repository بيجيب البيانات من الشبكة في الخلفية، ويخزنها في قاعدة البيانات. وبمجرد ما قاعدة البيانات تتحدث، الـ Flow بيبعت التحديث الجديد تلقائياً للواجهة، وده بيدي للمستخدم تجربة سريعة جداً وتطبيق شغال كلياً Offline.",
        "deep_answer_ar": "تحت الكابوت، نمط الـ Repository هو التطبيق العملي لمبدأ قلب التبعيات (Dependency Inversion Principle) عبر موديولات الـ Gradle المتعددة. واجهة الـ `UserRepository` بتتعرف داخل موديول الـ `:domain` ككود كوتلن نقي بدون أي استيراد لمكتبات أندرويد، بينما كلاس التنفيذ `UserRepositoryImpl` بيعيش في موديول منفصل `:data` هو اللي ماسك تبعيات Room و Retrofit.\n\nالربط ده بيعزل المعمارية تماماً عن تغيرات التكنولوجيا؛ لو قررنا بكرة الصبح نستبدل Retrofit بـ Ktor Client أو نغير Room بـ SQLDelight، الـ ViewModels والـ UseCases مش هيتغير فيهم حرف واحد.\n\nعلاوة على كده، الـ Repository هو المكان الوحيد المسؤول عن خوارزميات التزامن المعقدة زي Offline Write Queuing و Optimistic Updates؛ فلما المستخدم يكتب تعليق بدون إنترنت، الـ Repository بيكتب كائن مؤقت في Room فبيظهر فوراً في الـ UI، ويجهز المهمة لـ WorkManager علشان يرفعها للسيرفر أول ما النت يرجع ويحل أي تعارض (Conflict Resolution) بدون تلويث طبقة العرض.\n\nالمهندسون الكبار بيعتمدوا على الـ Repository لخلق Testing Seams ممتازة؛ لأن الـ ViewModels بتعتمد على الـ Interface، فبنقدر نختبر شاشات التطبيق بنسبة 100% في الـ JVM Unit Tests بتمرير Fake Repository خفيف بيشتغل في الذاكرة في أجزاء من الثانية وبدون الحاجة لتشغيل محاكي أو تشغيل بيئة أندرويد كاملة."
    }
}

# ==========================================
# PAT-07: What does Dependency Injection as a pattern accomplish?
# ==========================================
DATA["PAT-07"] = {
    "concept_en": """Dependency Injection (DI) is a structural and creational architectural pattern implementing Inversion of Control (IoC), whereby an object's collaborators and operational dependencies are provided by an external assembler rather than created internally by the object itself. In software design, classes that instantiate their own dependencies violate the Single Responsibility and Dependency Inversion principles by coupling business algorithms directly to concrete infrastructure implementations. By externalizing instantiation through constructor injection, Dependency Injection decouples classes from concrete collaborator types, eliminates hidden global state, establishes explicit architectural testing seams for automated test doubles, and centralizes component lifecycle and resource management.""",
    "walkthrough_en": """Contrasting tightly coupled instantiation with Dependency Injection:
```kotlin
// Anti-pattern: Object constructs its own infrastructure dependencies
class BadOrderViewModel : ViewModel() {
    // Tightly coupled to concrete Room database, OkHttp, and Retrofit!
    private val api = Retrofit.Builder().baseUrl("https://api.com").build().create(OrderApi::class.java)
    private val db = Room.databaseBuilder(App.context, OrderDb::class.java, "orders").build()
    // Impossible to unit test on JVM without mocking static contexts and network!
}

// Architectural Best Practice: Dependency Injection via Constructor Injection
class CleanOrderViewModel @Inject constructor(
    private val repository: OrderRepository // Injected interface contract!
) : ViewModel() {
    val orderState = repository.observeOrders()
}

// Zero-overhead Unit Test: Easily pass in-memory test fakes
class OrderViewModelTest {
    private val fakeRepository = FakeOrderRepository()
    private val viewModel = CleanOrderViewModel(fakeRepository) // Direct JVM test
}
```""",
    "short_en": """Dependency Injection implements Inversion of Control by supplying an object's collaborators externally rather than allowing the object to instantiate them internally. It decouples high-level business policies from low-level infrastructure, establishes explicit constructor contracts, eliminates hidden global state, and creates clean testing seams that allow developers to substitute real network and database engines with fakes during testing.""",
    "structured_en": """Dependency Injection transforms software design by fundamentally separating object construction from object execution.
Without Dependency Injection, classes instantiate their own collaborators using concrete constructors or static singletons. This practice tightly binds business logic to specific database drivers, network libraries, and Android contexts. It obscures a class's true dependency graph and makes unit testing extraordinarily difficult, as tests cannot substitute mock or fake objects without complex bytecode manipulation or reflection hacks.
Dependency Injection resolves this by inverting control. Classes declare what they require to function through explicit constructor parameters, leaving the responsibility of instantiating and assembling those collaborators to an external injector, such as Hilt or Dagger.
This pattern accomplishes four vital architectural goals. It enforces the Dependency Inversion Principle, ensuring high-level domain logic depends on abstractions rather than volatile implementations. It maximizes automated testability by allowing unit tests to supply lightweight test doubles directly into constructors. It centralizes resource management, ensuring that expensive instances like HTTP connection pools and database connections are scoped and reused appropriately. Finally, it enables clean multi-module architectures where feature modules remain decoupled from infrastructure modules.""",
    "deep_senior_en": """Under the hood, Dependency Injection is not merely an alternative syntax for the new operator; it is the structural cornerstone that enables compile-time verification of an application's Directed Acyclic Graph (DAG).
When using modern compile-time DI frameworks like Dagger and Hilt, the dependency injection pattern converts runtime errors into deterministic build-time failures. If an engineer introduces a circular dependency (Class A requires Class B, which requires Class A) or fails to provide a binding for an interface, the annotation processor or KSP compiler rejects the build immediately with diagnostic traces, preventing runtime crashes in production.
Furthermore, Dependency Injection formalizes lifecycle boundaries through hierarchical scoping. Without DI, developers inevitably create uncontrolled global singletons that leak Activity contexts and hoard memory. With structured DI, components are scoped strictly to their natural lifecycles: SingletonComponent for application-wide thread-safe services, ActivityRetainedComponent for ViewModels across configuration changes, and ActivityComponent for transient UI helpers.
Staff engineers leverage Dependency Injection as a modularization firewall. In enterprise multi-module codebases, feature modules declare abstract interfaces that they consume, while implementation modules supply concrete providers bound via @Binds. The DI framework resolves these bindings at the application assembly root, allowing feature modules to compile in parallel and drastically reducing incremental build times.""",
    "meta_ar": {
        "id": "PAT-07",
        "questionAr": "ما الذي يحققه نمط حقن التبعيات (Dependency Injection) كنمط تصميمي معماري؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ قلب التحكم (IoC)، والقدرة على شرح الفوائد المعمارية لفصل إنشاء الكائنات عن استخدامها، وإدراك دور الـ DI في تسهيل الاختبارات وعزل الموديولات وحماية الذاكرة من خلال إدارة دورات الحياة.",
        "why_it_matters_ar": "كتابة كود ينشئ كائناته بنفسه ينتج عنه نظام صلب ومترابط بإحكام (Tightly Coupled)، يعجز الفريق عن كتابة Unit Tests له، ويفقد المشروع القدرة على التوسع أو استبدال المكتبات.",
        "worked_example_ar": "مقارنة الإنشاء الذاتي بالحقن عبر الكونستركتور:\n```kotlin\n// كود سيئ: ينشئ قاعدة البيانات بنفسه\nclass BadRepo { val db = Room.databaseBuilder(...).build() }\n// كود نظيف: يستقبل التبعيات في الكونستركتور\nclass CleanRepo @Inject constructor(val api: Api, val dao: Dao) {}\n```",
        "trade_offs_ar": "يضيف طبقة بناء ومكتبات مساعدة ومنحنى تعلم أولي، لكنه يمنح مرونة مطلقة في الاختبارات وعزل الموديولات والتحقق من الروابط وقت الـ Build.",
        "failure_modes_ar": "استخدام نمط Service Locator كبديل للـ DI، مما يخفي الاعتماديات الحقيقية للكلاس ويؤدي لانهيارات في وقت التشغيل (Runtime Crashes) عند نسيان تسجيل كائن.",
        "production_perspective_ar": "في تطبيقات الإنتاج الكبرى، يُمنع إنشاء أي شبكة أو قاعدة بيانات يدوياً داخل الكلاسات، ويتم تمرير كل شيء كـ Interfaces عبر Hilt لتسهيل عزل الموديولات وكتابة الـ Fakes في التيست.",
        "how_to_answer_ar": "عرف الـ DI بأنه تطبيق لمبدأ قلب التحكم (Inversion of Control)، واذكر الفوائد الأربعة الكبرى: فك الارتباط المعماري، وسهولة الاختبارات بالـ Fakes، وإدارة دورة حياة الذاكرة مركزياً، والتحقق من صحة شجرة الكود في وقت الترجمة (Compile time).",
        "talking_points_ar": "مبدأ Inversion of Control، وفصل الإنشاء عن الاستخدام، ونقاء حقن الكونستركتور، وسهولة الـ Unit Testing بدون أندرويد، والتحقق الرياضي من الـ DAG في وقت الـ Compile time.",
        "follow_ups_ar": "- **المحاور:** \"هل الـ Dependency Injection يتطلب بالضرورة استخدام مكتبات زي Hilt أو Dagger؟\"\n  **المرشح:** \"لا إطلاقاً، الـ DI هو نمط تصميمي يمكن تطبيقه يدوياً بمجرد تمرير التبعيات في الكونستركتور، لكن المكتبات بتوفر أتمتة توليد الكود وإدارة الـ Scoping والتحقق من الـ Graph وقت الترجمة.\"\n\n- **المحاور:** \"ما الفرق بين Dependency Injection ونمط Service Locator؟\"\n  **المرشح:** \"في الـ DI الكلاس يعلن صراحة عن احتياجاته في الكونستركتور، بينما في Service Locator الكلاس بيطلب تبعياته بنفسه من حاوية وسيطة، مما يخفي اعتماداته الحقيقية ويصعب اختباره.\"",
        "self_check_ar": "هل عرفت الـ IoC بوضوح؟ هل شرحت فوائد الاختبارات وفك الارتباط؟ وهل بينت أثر الـ DI على سرعة الـ Compilation واستقرار الذاكرة؟",
        "references_ar": f"- [Dependency Injection in Android](https://developer.android.com/training/dependency-injection) — الدليل الرسمي لمفهوم حقن التبعيات في أندرويد.\n- [Inversion of Control Containers by Martin Fowler](https://martinfowler.com/articles/injection.html) — المقال المرجعي لمارتن فاولر حول مبادئ DI و IoC.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نمط حقن التبعيات (DI) بيطبق مبدأ Inversion of Control؛ وفكرته الأساسية إن الكلاس ميبنيش الأشياء اللي بيعتمد عليها بنفسه، بل يستقبلها جاهزة من الخارج في الكونستركتور. النمط ده بيفك الارتباط بين الكود وتفاصيل التنفيذ، وبيجعل الكود قابلاً للاختبار بنسبة 100% بالـ Unit Tests لأنك تقدر تمرر Fakes بسهولة، وبيوحد إدارة دورة حياة الكائنات والذاكرة في مكان مركزي آمن.",
        "best_answer_ar": "حقن التبعيات (Dependency Injection) بينقل مسؤولية إنشاء الكائنات وإدارتها من الكلاس نفسه لنظام تجميع خارجي، وده بيحل أخطر المشاكل المعمارية في هندسة البرمجيات.\n\nمن غير DI، الكلاس بيضطر ينادي الكونستركتور للكائنات التانية بنفسه أو يعتمد على كائنات Static عامة. ده بيخلق ارتباطاً وثيقاً (Tight Coupling)، وبيخلي الكلاس مخفياً وراه شبكة من التبعيات المعقدة، ويجعل كتابة Unit Test للكلاس ده شبه مستحيلة لأنك مقدرش تستبدل السيرفر الحقيقي أو قاعدة البيانات بنسخة تجريبية (Mock أو Fake).\n\nباستخدام حقن التبعيات، بنحقق أربع فوائد معمارية جوهرية:\nالأولى هي فك الارتباط؛ الكلاس بيعتمد على Interfaces مجردة مش كلاسات ملموسة.\nالثانية هي إمكانية الاختبار الفائقة؛ بنقدر ننشئ الكلاس في اختبارات الـ JVM ونمرر له نسخ تجريبية في الكونستركتور في ميكروثانية.\nالثالثة هي مركزية إدارة الموارد؛ بنضمن إن الكائنات المكلفة زي عميل الشبكة وقواعد البيانات بيتم إنشاؤها مرة واحدة وتشارك بأمان.\nالرابعة هي تنظيم المشاريع المقسمة لموديولات متعددة؛ حيث تعتمد موديولات الميزات على الواجهات، بينما تتكفل مكتبة الـ DI بتوصيل التنفيذات الحقيقية عند بناء التطبيق.",
        "deep_answer_ar": "تحت الكابوت، حقن التبعيات مش مجرد أسلوب لتجنب كلمة `new`، بل هو الركيزة الرياضية لبناء شجرة تبعيات موجهة وخالية من الدورات (Directed Acyclic Graph - DAG) يتم التحقق منها وقت الـ Compilation.\n\nباستخدام أدوات حديثة زي Dagger و Hilt، نمط الـ DI بيحول أخطاء التشغيل الكارثية إلى أخطاء بناء فورية؛ فلو نسيت توفر رابط لكائن معين أو عملت تبعية دائرية (Circular Dependency) حيث كلاس أ محتاج ب و ب محتاج أ، معالج الـ KSP بيوقف الـ Build فوراً في الـ IDE مع رسائل تشخيص دقيقة قبل ما الكود يوصل للإنتاج.\n\nكمان الـ DI بيفرض انضباطاً صارماً في حدود دورات الحياة والذاكرة من خلال الـ Hierarchical Scoping؛ فبدل ما المطورين يعملوا Singletons عشوائية تسرب سياق الـ Activity وتلتهم الرام، Hilt بتنظم الكائنات في مكونات هرمية دقيقة: كائنات دائمية في `SingletonComponent`، وكائنات تعيش مع الـ ViewModel عبر تدوير الشاشة في `ViewModelComponent`، وكائنات مؤقتة خاصة بالشاشات في `ActivityComponent`.\n\nالمهندسون الكبار بيستخدموا الـ DI كجدار حماية معماري بين موديولات الـ Gradle؛ موديولات الميزات تعتمد فقط على الـ Core Interfaces، وموديولات الداتا بتوفر التنفيذات عبر `@Binds`، والمشروع الرئيسي بيجمع الروابط، وده بيسمح ببناء الموديولات بالتوازي (Parallel Compilation) ويقلل وقت الـ Build في خطوط الـ CI بشكل كبير."
    }
}

# ==========================================
# PAT-08: Where do Singleton, Adapter, and Observer show up in Android?
# ==========================================
DATA["PAT-08"] = {
    "concept_en": """The Android operating system, Jetpack libraries, and application runtimes are architected around foundational Gang of Four design patterns that govern resource management, UI composition, and asynchronous data streaming. Singleton manifests across process-wide Android system services accessed via getSystemService() (such as LayoutInflater, WindowManager, and ConnectivityManager) and in application-level databases managed via Room. Adapter serves as the core UI composition engine in RecyclerView.Adapter and ListView adapters, converting heterogeneous domain data structures into reusable ViewHolders and interactive View hierarchies. Observer represents the foundational paradigm for reactive Android programming, powering Android framework components via BroadcastReceiver and ContentObserver, and driving modern UDF state pipelines through Jetpack LiveData, StateFlow, and Compose Snapshot State.""",
    "walkthrough_en": """Android Framework manifestation of Singleton, Adapter, and Observer:
```kotlin
// 1. SINGLETON in Android: System Services and Database instances
val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
val database = AppDatabase.getInstance(context.applicationContext)

// 2. ADAPTER in Android: Bridging domain list to UI ViewHolders
class UserAdapter(private val users: List<User>) : RecyclerView.Adapter<UserViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder =
        UserViewHolder(ItemUserBinding.inflate(LayoutInflater.from(parent.context), parent, false))
    override fun onBindViewHolder(holder: UserViewHolder, position: Int) = holder.bind(users[position])
    override fun getItemCount(): Int = users.size
}

// 3. OBSERVER in Android: Reactive UI updates via StateFlow and Lifecycle
@Composable
fun UserListScreen(viewModel: UserViewModel) {
    // CollectAsStateWithLifecycle observes StateFlow, acting as modern lifecycle-safe Observer
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    LazyColumn { items(state.items) { item -> Text(item.title) } }
}
```""",
    "short_en": """In Android, Singleton appears in process-wide system services like ConnectivityManager and Room database instances. Adapter appears prominently in RecyclerView.Adapter and ListView adapters, converting domain models into ViewHolders. Observer powers reactive UI updates through Kotlin StateFlow, Jetpack LiveData, Android BroadcastReceivers, and Compose Snapshot State. These three patterns form the core foundation of Android development.""",
    "structured_en": """Singleton, Adapter, and Observer are deeply integrated into the core architecture of the Android operating system and Jetpack libraries.
The Singleton pattern appears throughout the Android OS framework in system services accessed through Context.getSystemService(), such as ConnectivityManager, WindowManager, and NotificationManager. At the application layer, Room databases and network clients like OkHttpClient and Retrofit are maintained as singletons via Hilt or custom containers, ensuring that expensive disk and socket connection pools are shared process-wide.
The Adapter pattern is most visible in Android's UI presentation framework through RecyclerView.Adapter and ListAdapter. The adapter acts as a structural bridge between disparate domain data models and the underlying View and ViewHolder layout hierarchy. It manages item binding, view recycling, and view-type layout inflation without coupling data models to Android UI components.
The Observer pattern is the ubiquitous foundation of Android asynchronous programming. At the OS level, it appears in BroadcastReceiver for system-wide broadcasts and ContentObserver for database changes. In modern Jetpack development, Observer drives reactive Unidirectional Data Flow through StateFlow, SharedFlow, LiveData, and Jetpack Compose state tracking, ensuring that UI components automatically re-render whenever underlying domain state emits updates.""",
    "deep_senior_en": """Under the hood, these framework pattern implementations reflect decades of Android performance tuning and lifecycle evolution.
In the Android operating system, system service singletons are actually managed through ServiceManager using the Service Locator pattern combined with IBinder IPC proxies. When an app requests ConnectivityManager, the OS returns a lightweight local singleton proxy that communicates with the centralized system_server process, minimizing process memory while sharing OS resources.
In RecyclerView.Adapter, the adapter pattern is tightly coupled to the Recycler memory pool. The adapter does not simply convert objects to views; it collaborates with RecyclerView.Recycler to reuse scrapped views from the heap, avoiding expensive LayoutInflater XML parsing and preventing garbage collection frame drops during 120Hz flings.
The evolution of the Observer pattern reflects Android's ongoing struggle with lifecycle management. Early implementations using raw Java callbacks or BroadcastReceivers frequently caused catastrophic memory leaks when developers forgot to unregister listeners in onStop() or onDestroy(). Jetpack LiveData mitigated this by checking LifecycleOwner states before dispatching events. Today, senior engineers mandate Kotlin StateFlow with repeatOnLifecycle or collectAsStateWithLifecycle, which automatically suspends and resumes flow collection based on lifecycle state, achieving zero-leak, high-performance UI observation. In modern Jetpack Compose, snapshot observation builds directly upon this observer lineage by tracking state reads during composition phases, automatically scheduling micro-recompositions only for the exact composable scopes that access mutated state properties.""",
    "meta_ar": {
        "id": "PAT-08",
        "questionAr": "أين تظهر أنماط Singleton و Adapter و Observer في نظام أندرويد ومكتبات Jetpack؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على ربط المفاهيم النظرية لأنماط التصميم بالتطبيق العملي في نظام أندرويد، وفهم كيفية عمل System Services، و RecyclerView.Adapter، وتطور نمط Observer من BroadcastReceiver إلى StateFlow و Compose.",
        "why_it_matters_ar": "معرفة كيف يطبق أندرويد هذه الأنماط داخلياً يمنح المهندس قدرة على استغلال موارد النظام بكفاءة، وتفادي تسريبات الذاكرة، وبناء واجهات سلسة تحترم دورات حياة المكونات.",
        "worked_example_ar": "ظهور الأنماط الثلاثة في أندرويد:\n```kotlin\n// Singleton: خدمة النظام وقاعدة البيانات\nval cm = context.getSystemService(ConnectivityManager::class.java)\n// Adapter: مواءمة القوائم للشاشة\nclass MyAdapter : RecyclerView.Adapter<VH>()\n// Observer: مراقبة الـ StateFlow في الواجهة\nval state by vm.state.collectAsStateWithLifecycle()\n```",
        "trade_offs_ar": "الـ Singletons توفر بناء الموارد لكنها تتطلب حذر الـ Context، والـ Adapter يعزل الواجهة لكنه يضيف كود وسيط، والـ Observer يوفر تفاعلية فورية لكنه يتطلب إدارة واعية لدورة الحياة.",
        "failure_modes_ar": "تسريب سياق الـ Activity داخل Singleton تابع للنظام، أو نسيان إلغاء تسجيل BroadcastReceiver مما يسبب تسريب ذاكرة مستمر.",
        "production_perspective_ar": "في المشروعات الحديثة، نراقب الـ StateFlow دائماً باستخدام `collectAsStateWithLifecycle` لتفادي جمع البيانات في الخلفية، ونستخدم ListAdapter المدمج بـ DiffUtil لتحقيق أعلى كفاءة عرض.",
        "how_to_answer_ar": "اذكر أمثلة واضحة ومباشرة لكل نمط من صلب أندرويد: Singleton في System Services و Room، و Adapter في RecyclerView، و Observer في BroadcastReceiver و StateFlow و Compose، واشرح التطور المعماري الحديث لها.",
        "talking_points_ar": "خدمات النظام و ServiceManager، وآلية إعادة تدوير الكائنات في RecyclerView.Adapter، وتطور Observer من LiveData إلى StateFlow و Compose، وحماية دورة الحياة عبر `repeatOnLifecycle`.",
        "follow_ups_ar": "- **المحاور:** \"كيف يتعامل RecyclerView.Adapter مع نمط Adapter لتوفير استهلاك الذاكرة؟\"\n  **المرشح:** \"الـ Adapter مش بس بيحول الداتا لواجهة، ده بيتعاون مع الـ Recycler Pool لإعادة استخدام الـ ViewHolders المعروضة وتحديث بياناتها فقط بـ `onBindViewHolder`، وده بيمنع نفخ XML جديد وتوقف الفريمات.\"\n\n- **المحاور:** \"ليه بنفضل `collectAsStateWithLifecycle` على `collectAsState` في Jetpack Compose؟\"\n  **المرشح:** \"لأن الأولى بتوقف جمع الـ Flow تلقائياً لما التطبيق يروح في الـ Background تحت حالة `Lifecycle.State.STARTED`، وده بيوفر موارد المعالج والبطارية.\"",
        "self_check_ar": "هل ذكرت أمثلة نظام أندرويد لكل نمط؟ هل شرحت آلية عمل RecyclerView؟ وهل بينت أحدث طرق مراقبة الـ Observer في Compose؟",
        "references_ar": f"- [Android System Services](https://developer.android.com/reference/android/content/Context#getSystemService(java.lang.Class%3CT%3E)) — التوثيق الرسمي لخدمات نظام أندرويد.\n- [Create dynamic lists with RecyclerView](https://developer.android.com/develop/ui/views/layout/recyclerview) — الدليل الرسمي لنمط Adapter في RecyclerView.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "في أندرويد، نمط Singleton بيظهر في خدمات النظام الموحدة زي `ConnectivityManager` و `NotificationManager` اللي بنطلبها عبر `getSystemService()`، وفي قواعد بيانات Room ومكتبات الشبكة. نمط Adapter بيظهر بوضوح في `RecyclerView.Adapter` لتحويل مصفوفات البيانات لكائنات ViewHolders معروضة على الشاشة. نمط Observer هو أساس البرمجة التفاعلية في أندرويد، وبيظهر في الـ BroadcastReceiver و ContentObserver على مستوى النظام، وفي StateFlow و LiveData و Compose Snapshot State لمراقبة تدفقات البيانات وتحديث الشاشات تلقائياً.",
        "best_answer_ar": "أنماط Singleton و Adapter و Observer مدمجة بعمق في تصميم نظام أندرويد ومكتبات Jetpack، وتعتبر الأساس اليومي لتطوير التطبيقات.\n\nنمط الـ Singleton متجسد في خدمات نظام أندرويد (System Services). لما تطلب `context.getSystemService(Context.CONNECTIVITY_SERVICE)`، النظام بيرجع لك نسخة واحدة مشتركة تدير اتصال الشبكة للتطبيق بالكامل. وفي كود تطبيقاتنا، بنطبقه على كائن الـ Room Database وعميل الـ OkHttpClient لضمان مشاركة اتصالات الداتابيز ومقابس الشبكة بدون تكرار مكلف.\n\nنمط الـ Adapter بيظهر بأوضح صوره في `RecyclerView.Adapter` و `ListAdapter`. دوره هنا هو التوفيق الهيكلي؛ عندك مصفوفة كائنات زي `List<User>` والـ UI محتاج `Views`. الـ Adapter بياخد الداتا ويحولها لـ ViewHolders ويدير عملية تضخيم الـ XML وعرض الحقول بدون ما كلاس الـ User يعرف أي حاجة عن واجهة أندرويد.\n\nنمط الـ Observer هو العمود الفقري للتفاعل في أندرويد. زمان كان متجسد في `BroadcastReceiver` للتنصت على أحداث النظام زي تغير حالة البطارية. ومع تطور المعمارية النظيفة، بقى النمط ده هو الأساس في إدارة الحالة؛ الشاشات بتراقب الـ `StateFlow` أو `LiveData` القادم من الـ ViewModel، وبمجرد ما الداتا تتغير، الواجهة بتعيد رسم نفسها فوراً وبأمان تام مع دورة حياة المكونات.",
        "deep_answer_ar": "تحت الكابوت، تطبيق الأنماط دي في أندرويد بيعكس سنين طويلة من تحسين استهلاك الموارد وأداء الرام وحماية دورة حياة المكونات.\n\nفي الـ Singleton على مستوى النظام، الـ System Services بتدار داخلياً بنمط Service Locator عبر `ServiceManager`. الكائن اللي في إيدك في التطبيق هو مجرد `BinderProxy` خفيف بيتواصل عبر الـ IPC مع العملية المركزية `system_server`، وده بيسمح للنظام بمشاركة الموارد وإدارتها مركزياً بدون تضخيم ذاكرة التطبيقات.\n\nوفي `RecyclerView.Adapter`، نمط الـ Adapter مش مجرد محول شكلي، بل هو جزء من منظومة معقدة بتتعاون مع `RecyclerView.Recycler Pool`. لما الشاشة تسكرول، الـ Adapter مش بينفخ View جديدة، بل بيعيد استخدام نفس كائن الـ ViewHolder المحفوظ في الرام ويعمل له Bind للبيانات الجديدة فقط، وده بيمنع حدوث عمليات Garbage Collection متكررة ويضمن ثبات معدل الفريمات على 120 هرتز.\n\nأما تطور نمط الـ Observer فبيحكي قصة معالجة تسريبات الذاكرة في أندرويد. قديماً، الـ Listeners والـ BroadcastReceivers كانت بتسبب تسريب ذاكرة هائل لو المطور نسي يلغي تسجيلها في `onDestroy`. جوجل حلت المشكلة بـ LiveData كـ Lifecycle-aware Observer، وحالياً في العصر الحديث مع Kotlin Coroutines، المهندسون الكبار بيستخدموا `StateFlow` مع دالة `collectAsStateWithLifecycle` في Jetpack Compose، والتي توقف المراقبة تلقائياً لما الشاشة تروح في الخلفية (Stop state)، مما يوفر المعالج والبطارية بنسبة 100% ويقضي على التسريبات تماماً."
    }
}

# ==========================================
# PAT-09: Compare State and Strategy with concrete examples.
# ==========================================
DATA["PAT-09"] = {
    "concept_en": """The State and Strategy patterns share identical Unified Modeling Language (UML) structural class diagrams based on interface delegation, but diverge fundamentally in their behavioral intent, contextual ownership, and state transition mechanics. In the Strategy pattern, the client explicitly chooses, configures, or injects a specific algorithm from the outside; strategies are typically stateless, independent of one another, and execute interchangeable algorithmic calculations without knowing about other strategies. In the State pattern, the context object encapsulates dynamic behavioral modes where the internal state alters its behavior autonomously; concrete state subclasses are tightly coupled to state transition graphs, actively driving transitions to subsequent state nodes as internal lifecycle events unfold.""",
    "walkthrough_en": """Contrasting Strategy vs State implementations in Kotlin:
```kotlin
// 1. STRATEGY PATTERN: Client injects interchangeable algorithm from outside
interface ShippingCostStrategy { fun calculateCost(weightKg: Double): Double }
class StandardShipping : ShippingCostStrategy { override fun calculateCost(weightKg: Double) = weightKg * 5.0 }
class ExpressShipping : ShippingCostStrategy { override fun calculateCost(weightKg: Double) = weightKg * 15.0 + 20.0 }

class OrderCheckout(var shippingStrategy: ShippingCostStrategy) {
    // Client or UI sets strategy based on user selection; strategies don't know each other
    fun finalizeOrder(weightKg: Double): Double = shippingStrategy.calculateCost(weightKg)
}

// 2. STATE PATTERN: Internal autonomous state transition machine
sealed interface MediaPlayerState {
    fun play(player: MediaPlayerContext)
    fun pause(player: MediaPlayerContext)
}

class PlayingState : MediaPlayerState {
    override fun play(player: MediaPlayerContext) { /* Already playing */ }
    override fun pause(player: MediaPlayerContext) {
        println("Pausing audio playback")
        player.state = PausedState() // State itself drives the transition!
    }
}

class PausedState : MediaPlayerState {
    override fun play(player: MediaPlayerContext) {
        println("Resuming audio playback")
        player.state = PlayingState() // State itself drives the transition!
    }
    override fun pause(player: MediaPlayerContext) { /* Already paused */ }
}

class MediaPlayerContext { var state: MediaPlayerState = PausedState() }
```""",
    "short_en": """Strategy and State share identical interface delegation structures but have opposing intents. Strategy encapsulates interchangeable algorithms chosen by the client from the outside, with strategies remaining independent and unaware of each other. State encapsulates dynamic behavioral modes where the context's behavior changes autonomously, and concrete state classes actively drive transitions to other states as events occur.""",
    "structured_en": """While the State and Strategy patterns appear structurally identical in class diagrams, their architectural purpose and operational dynamics are completely distinct.
In the Strategy pattern, the primary intent is providing interchangeable implementations of a specific algorithmic capability. The consuming client or caller explicitly selects, configures, or injects the strategy from the outside. Strategies are typically stateless and operate in total isolation; an ExpressShippingStrategy has no knowledge of or relationship to a StandardShippingStrategy. The client changes the strategy when a functional preference changes, such as selecting a payment gateway or sorting criteria.
In the State pattern, the primary intent is modeling an autonomous state machine where an object's observable behavior changes completely based on its internal state. The client does not manually swap state implementations; rather, state transitions occur internally in response to events and lifecycle triggers. Crucially, concrete state implementations know about each other, actively instantiating and transitioning the context to subsequent state nodes.
In Android, Strategy is ideal for dynamic policies like discount calculations and retry backoffs, while State is ideal for lifecycle-rich components like media players, connection session holders, and complex checkout workflows.""",
    "deep_senior_en": """Under the hood, both patterns delegate work through an interface reference held by a context object, utilizing polymorphic virtual method dispatch. The senior distinction lies in transition ownership and mutability dynamics.
Strategy represents a 'has-a' relationship representing a swappable tool. Because strategies are usually stateless, they can be instantiated as immutable singletons and shared across multiple threads safely without synchronization overhead. In Kotlin, trivial strategies are often simplified into first-class lambdas (val sortStrategy: (Item, Item) -> Int), entirely bypassing class generation.
State represents an evolving lifecycle mode. Concrete state classes frequently require bidirectional access to the context object to trigger transitions (context.setState(NewState)). In legacy object-oriented designs, this created cyclic references and mutable state leak hazards.
Modern Android engineering reconciles the State pattern with reactive Unidirectional Data Flow (UDF). Rather than utilizing mutating state classes that pass context references around, senior engineers model state as an immutable sealed interface hierarchy (sealed interface PlayerState: Idle, Buffering, Playing, Error). A ViewModel or StateMachine reducer acts as the single transition authority, receiving user intents and emitting new immutable states across a StateFlow.
This functional state transition paradigm provides all the encapsulation benefits of the classic GoF State pattern while eliminating mutable state bugs, simplifying unit testing, and integrating seamlessly with Jetpack Compose re-composition cycles.""",
    "meta_ar": {
        "id": "PAT-09",
        "questionAr": "قارن بين نمطي State و Strategy مع توضيح الفروق بأمثلة عملية من أندرويد.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على كشف الفارق المعماري الدقيق بين نمطين يمتلكان نفس الرسم الهيكلي (UML)، ومعرفة متى يتم استخدام كل منهما، والتمييز بين التدخل الخارجي في Strategy والانتقال الذاتي الداخلي في State.",
        "why_it_matters_ar": "الكثير من المطورين يخلطون بين النمطين لتطابق الكود، مما يقود لتصميم آلات حالة معقدة بنمط Strategy أو محاولة تبديل الخوارزميات بنمط State.",
        "worked_example_ar": "مقارنة النمطين برمجياً:\n```kotlin\n// Strategy: العميل يمرر طريقة الشحن من الخارج\nclass Cart(val shipping: ShippingStrategy)\n// State: الكائن يغير حالته وسلوكه ذاتياً من الداخل\nclass PlayingState : MediaState {\n    override fun pause(ctx: Player) { ctx.state = PausedState() }\n}\n```",
        "trade_offs_ar": "الـ Strategy يتميز باستقلالية الخوارزميات وانعدام الحالة، بينما الـ State ينمذج مسارات الانتقال المعقدة لكنه يربط الحالات ببعضها.",
        "failure_modes_ar": "جعل كلاسات الـ Strategy تعتمد على بعضها أو تغير حالة الكائن الحاضن، أو كتابة مصفوفة شروط معقدة `when(state)` داخل كل دالة بدلاً من نمط State.",
        "production_perspective_ar": "في تطبيقات أندرويد الحديثة، نطبق Strategy بتمرير Lambdas، ونطبق State عبر Sealed Interfaces غير قابلة للتعديل مع ViewModel يمثل آلة الحالة في معمارية MVI.",
        "how_to_answer_ar": "وضح أن النمطين متطابقان هيكلياً في الـ UML لكن مختلفان في النية والتحكم: في Strategy العميل يختار الخوارزمية من الخارج والكلاسات لا تعرف بعضها، بينما في State الكائن يغير تصرفاته داخلياً والحالات تعرف مسارات الانتقال لبعضها.",
        "talking_points_ar": "تطابق الـ UML واختلاف النوايا (Intent)، ومفهوم التبديل الخارجي مقابل الانتقال الداخلي، وأمثلة مشغل الميديا وحساب تكلفة الشحن، والتحول الحديث نحو Sealed Interfaces و UDF.",
        "follow_ups_ar": "- **المحاور:** \"ليه في نمط State الكلاسات بتعرف بعضها بينما في Strategy ميعرفوش بعض؟\"\n  **المرشح:** \"لأن في State الهدف هو نمذجة آلة حالة (State Machine) فيها مسار انتقال حتمي، فكلاس Playing لازم يعرف إنه لما يتعمل Pause هينتقل لـ PausedState، بينما استراتيجيات الشحن ملهاش أي علاقة ببعضها.\"\n\n- **المحاور:** \"كيف نطبق نمط State في Jetpack Compose بطريقة نظيفة؟\"\n  **المرشح:** \"باستخدام `sealed interface UiState` يمثل الحالات المختلفة، ودالة Composable بتعمل `when(state)` لعرض الواجهة المطابقة، بينما الـ ViewModel هو المسؤول الوحيد عن إرسال الحالات الجديدة.\"",
        "self_check_ar": "هل بينت تطابق الهيكل واختلاف الهدف؟ هل شرحت من يملك قرار الانتقال في كل منهما؟ وهل ربطت نمط State بمعمارية MVI و Sealed Interfaces الحديثة؟",
        "references_ar": f"- [State vs Strategy Pattern](https://refactoring.guru/design-patterns/state) — المقارنة المرجعية الدقيقة بين نمطي الحالة والاستراتيجية.\n- [Unidirectional Data Flow in Android](https://developer.android.com/topic/architecture/ui-layer#udf) — الدليل الرسمي لتدفق البيانات الأحادي ونمذجة الحالات في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نمط Strategy ونمط State بيمتلكوا نفس الهيكل البرمجي بالظبط في الـ UML، لكن الفارق الجوهري في مين اللي بيقرر وإزاي بيحصل التغيير. في Strategy، العميل الخارجي هو اللي بيختار الخوارزمية ويحقنها في الكائن من برة، والاستراتيجيات مستقلة ومبتعرفش أي حاجة عن بعض زي اختيار طريقة الدفع أو الشحن. أما في State، الكائن بيغير سلوكه ذاتياً من جوة بناءً على حالته الداخلية المتغيرة، وكلاسات الحالات نفسها بتكون عارفة بعضها وبتقود الانتقال من حالة للتانية زي مشغل الفيديو اللي بينتقل ذاتياً بين التوقف المؤقت والتشغيل والتحميل.",
        "best_answer_ar": "الفارق بين نمطي State و Strategy هو أحد أشهر الأسئلة في مقابلات الـ Senior، لأن النمطين شكلهم متطابق تماماً في الكود كإنترفيس وتفويض، لكن النية المعمارية (Intent) وطريقة الانتقال مختلفة تماماً.\n\nفي نمط الـ Strategy، الهدف هو توفير خوارزميات بديلة ومتبادلة لنفس المهمة. المتحكم هنا هو المستهلك الخارجي (Client)؛ هو اللي بيحدد الاستراتيجية اللي عايزها ويمررها للكونستركتور. الاستراتيجيات ملهاش أي علاقة ببعض، وكلاس `StandardShipping` ميعرفش أصلاً إن فيه كلاس اسمه `ExpressShipping`. الكلاسات دي بتكون في الغالب Stateless وخالية من الحالة، ومفيش أي انتقال بينها.\n\nفي نمط الـ State، الهدف هو نمذجة آلة حالة (State Machine) بيتغير فيها سلوك الكائن بالكامل حسب وضعه الداخلي. المتحكم هنا هو النظام الداخلي والأحداث اللي بتحصل. كلاسات الحالة بتكون عارفة بعضها ومسؤولة عن توجيه الانتقال؛ فمثلاً كلاس `PlayingState` في مشغل الصوتيات لما يجيله أمر `pause()`، هو بنفسه اللي بيمسك الكائن الحاضن ويغير حالته لكائن `PausedState`.\n\nفي أندرويد، بنستخدم Strategy لما نكون عايزين نبدل طريقة معالجة زي خوارزميات الضغط أو بوابات الدفع، وبنستخدم State لما نكون بنبني مكون له دورة حياة ومسارات انتقال محكومة زي شاشات الشراء أو جلسات الاتصال.",
        "deep_answer_ar": "تحت الكابوت، النمطين بيعتمدوا على الـ Polymorphic Virtual Dispatch من خلال مرجع إنترفيس داخل كلاس الحاوية (Context). الفارق التقني الحقيقي بيظهر في إدارة الحالة وثبات الكائنات (Immutability) ومسارات التزامن.\n\nالـ Strategy غالباً بتكون Stateless، وده بيخليها آمنة تماماً لمشاركتها عبر خيوط المعالجة كـ Singletons بدون أي قفل متزامن (Synchronization Lock)، وفي لغة Kotlin بنستبدلها ببساطة بـ First-class Functions زي `typealias CalculationStrategy = (Double) -> Double`.\n\nأما الـ State الكلاسيكي في الـ OOP، فكان بيحمل خطورة معمارية بسبب الاعتماد الدائري (Cyclic Dependency)؛ كلاس الحالة ماسك مرجع للـ Context والـ Context ماسك كائن الحالة عشان يعمل الانتقال، وده كان بيفتح الباب لتسريبات الذاكرة وتضارب التعديل عبر الـ Threads.\n\nفي هندسة أندرويد المعاصرة، نمط الـ State تم تطويره ليتكامل مع معمارية Unidirectional Data Flow (UDF) و Jetpack Compose؛ فبدل ما الحالات تعدل الكائن، بنمثل الحالات كـ `sealed interface` غير قابل للتعديل (Immutable UI State). الـ ViewModel بيلعب دور آلة الحالة المركزية (State Machine Reducer) اللي بيستقبل الـ Intents ويصدر حالات جديدة نقية عبر `StateFlow`. ده بيعطينا كل القوة المعمارية لنمط الـ State لمنع الشروط المتشعبة، مع الحفاظ على نقاء الكود وسهولة اختباره بنسبة 100% في الـ Unit Tests."
    }
}


def main():
    print(f"Elevating {len(DATA)} questions in PAT (PAT-01 to PAT-09)...")
    
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
    ee.save_topic_metadata("pat_01_09", {qid: d["meta_ar"] for qid, d in DATA.items()})

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
        print("\nAll 9 PAT questions (PAT-01 to PAT-09) successfully elevated and passed validation!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
