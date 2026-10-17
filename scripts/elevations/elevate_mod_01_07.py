#!/usr/bin/env python3
"""
Elevation script for MOD questions: MOD-01 to MOD-07.
Topic: Gradle Modularization & Dependency Boundaries (MOD)
Phase 4, Batch 1
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "تقسيم المشروع لموديولات (Modularization) وحدود التبعيات"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# MOD-01: What is modularization, and what trade-offs does it introduce?
# ==========================================
DATA["MOD-01"] = {
    "concept_en": """Modularization is the architectural discipline of decomposing an Android application from a monolithic codebase into discrete, loosely coupled Gradle subprojects. Each module establishes an isolated physical build and ownership boundary with its own build.gradle.kts file, private dependency scope, and compilation artifacts. The primary advantages include dramatically accelerated incremental compilation through Gradle parallel task execution and remote build caching, clear organizational code ownership across autonomous engineering squads, strict encapsulation via Kotlin internal visibility, and the enablement of dynamic feature delivery. However, modularization introduces substantial engineering trade-offs: increased Gradle project configuration time, configuration overhead with multi-module dependency catalogs and convention plugins, complex inter-module navigation and dependency injection graphs, potential circular dependency traps, and cognitive overhead for smaller teams.""",
    "walkthrough_en": """Configuring modular boundaries and isolated build units in settings.gradle.kts and build.gradle.kts:
```kotlin
// settings.gradle.kts
include(
    ":app",
    ":core:network",
    ":core:designsystem",
    ":feature:checkout:api",
    ":feature:checkout:impl"
)

// feature/checkout/impl/build.gradle.kts
plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "com.example.feature.checkout.impl"
}

dependencies {
    // Depend strictly on public API contracts, not internal implementations
    implementation(project(":feature:checkout:api"))
    implementation(project(":core:network"))
    implementation(project(":core:designsystem"))
}
```""",
    "short_en": """Modularization decomposes a monolithic Android app into decoupled Gradle subprojects that serve as independent build and ownership boundaries. It delivers faster incremental builds through parallel compilation and build caching, strengthens code encapsulation, and allows teams to work autonomously. The primary trade-offs are increased Gradle configuration overhead, complex cross-module navigation, and dependency coordination.""",
    "structured_en": """Modularization transforms an Android codebase from a single monolithic project into a collection of cohesive, independent Gradle modules.
Rather than treating modules as arbitrary folders, each module acts as a physical build boundary with dedicated dependency scopes and compiler outputs.
This architecture brings major performance and organizational benefits to large teams.
On the build performance side, Gradle leverages parallel task execution to compile independent leaf modules concurrently, while the remote build cache skips compiling unchanged modules entirely.
Organizationally, distinct engineering squads own individual modules, enforcing code boundaries through Kotlin internal visibility and preventing accidental dependencies.
However, modularization introduces real operational costs that must be managed deliberately.
Every additional module increases Gradle configuration time during project syncs.
Managing dependencies requires version catalogs and custom convention plugins to prevent build script drift.
Cross-module navigation and dependency injection demand decoupled contract interfaces rather than direct references, adding structural indirection.""",
    "deep_senior_en": """In enterprise Android engineering, modularization is fundamentally an organizational and build-system scaling strategy rather than a purely aesthetic design choice.
When a monolithic codebase scales beyond twenty developers, build times degrade into multi-minute bottlenecks and merge conflicts compound because team ownership boundaries are purely conventional.
By splitting code into discrete Gradle subprojects, we establish physical compilation boundaries.
Gradle executes compilation tasks across available CPU cores in parallel and reuses cached task outputs from remote CI builders.
A modification inside a private feature screen re-executes compilation solely for that specific feature module, keeping developer feedback loops fast.
From an architectural perspective, modularization enforces encapsulation: internal classes cannot be referenced outside their containing module, preventing architectural erosion over time.
Yet, premature or granular over-modularization presents severe architectural hazards.
Having hundreds of tiny modules introduces configuration time regressions that can offset parallel compilation gains during clean builds.
Furthermore, maintaining consistent compiler flags, static analysis linters, and dependency versions requires investing in Gradle convention plugins written in buildSrc or composite builds.
Inter-module communication also requires designing explicit public API modules and navigation contracts, shifting coupling risks from compile-time references to contract management. We also configure automated Gradle enterprise metrics to track task duration trends and configuration cache hit rates, ensuring our modular boundaries deliver measurable developer productivity gains.""",
    "meta_ar": {
        "id": "MOD-01",
        "questionAr": "ما هو تقسيم المشروع لموديولات (Modularization)، وما هي المفاضلات والتكاليف التي يفرضها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تعريف الموديولات كحدود بناء وملكية برمجية مستقلة وليس مجرد مجلدات، والربط بين الكبسلة المعمارية وتوازي التجميع وسرعة البناء، وتحليل تكاليف الإعداد وحوكمة الـ API.",
        "concept_ar": "تقسيم المشروع لموديولات (Modularization) هو تفكيك التطبيق المتجانس (Monolith) إلى موديولات Gradle فرعية مستقلة ومترابطة بحدود واضحة. يمثل كل موديول وحدة بناء وفيزيائية وملكية برمجية مستقلة بملف إعدادات build.gradle.kts خاص به. يوفر التقسيم تسريعاً هائلاً لزمن البناء التزايدي عبر التجميع المتوازي واستخدام Build Cache، ويعزز كبسلة الكود وحرية الفرق في العمل، ولكنه يفرض تكاليف في زمن التهيئة Configuration Time وتعقيد الربط وإدارة الاعتماديات.",
        "walkthrough_ar": """تنظيم هيكل الموديولات المستقلة وتحديد مسار التبعيات في ملفات Gradle:
```kotlin
// settings.gradle.kts
include(
    ":app",
    ":core:network",
    ":feature:payment:api",
    ":feature:payment:impl"
)

// feature/payment/impl/build.gradle.kts
dependencies {
    implementation(project(":feature:payment:api"))
    implementation(project(":core:network"))
}
```""",
        "why_it_matters_ar": "يمثل الحل المعماري الأساسي لقابلية توسع التطبيقات الكبيرة؛ حيث يمنع التداخل البرمجي بين الفرق، ويحمي استقرار الكود، ويحول أوقات التجميع الطويلة من عائق إنتاجي إلى عملية تزايدية وسريعة تعيد بناء الأجزاء المعدلة فقط.",
        "worked_example_ar": "تحويل شاشة تسجيل الدخول إلى موديول مستقل `:feature:login` مع قياس وقت التجميع قبل وبعد التحويل، وملاحظة تجنب إعادة تجميع باقي أجزاء التطبيق عند تعديل كود الشاشة.",
        "trade_offs_ar": "الموديولات تسرع التجميع التزايدي وتعزز كبسلة الكود ولكنها تزيد من زمن تهيئة Gradle Configuration Time وتتطلب تصميماً دقيقاً لواجهات API والتنقل، بينما التطبيق المتجانس أسهل في التعديل المباشر ولكنه بطيء التجميع ويعاني من تشابك الكود.",
        "failure_modes_ar": "الإفراط في التقسيم بإنشاء مئات الموديولات الصغيرة جداً مما يرفع زمن التهيئة، وتكوين موديول `:core:common` ضخم يتحول لمونوليث مقنع، وحدوث تبعيات دائرية Circular Dependencies بين الموديولات.",
        "production_perspective_ar": "في الشركات التقنية الكبرى، نعتمد على اتفاقيات Gradle Convention Plugins لتوحيد إعدادات الموديولات، ونراقب زمن البناء أسبوعياً عبر أدوات مثل Gradle Enterprise لضمان جدوى التقسيم ومردوده الإنتاجي.",
        "how_to_answer_ar": "ابدأ بتعريف الموديول كوحدة بناء وملكية فيزيائية، ثم اشرح المكاسب في التجميع المتوازي والكاش وكبسلة الكود، ثم فصّل التكاليف في Configuration Time وإدارة الاعتماديات.",
        "talking_points_ar": "دور Gradle Build Cache والتجميع المتوازي، مخاطر الإفراط في الموديولات على الـ Configuration Time، وكيفية استخدام Convention Plugins لتوحيد بيئة البناء.",
        "follow_ups_ar": "- **المحاور:** \"متى تقرر أن الميزة تستحق موديولاً خاصاً بها بدلاً من مجلد؟\"\n  **المرشح:** \"عندما يمتلكها فريق مستقل، أو تتطلب دورة تجميع منفصلة، أو يُراد تسليمها كـ Dynamic Feature، أو لحماية كبسلتها الصارمة عن باقي التطبيق.\"\n\n- **المحاور:** \"لماذا قد يبطئ تقسيم المشروع زمن البناء النظيف Clean Build؟\"\n  **المرشح:** \"بسبب استهلاك Gradle لوقت أطول في مرحلة الـ Configuration وتوليد مهام مستقلة لكل موديول؛ الفائدة الكبرى تظهر في البناء التزايدي واستخدام الـ Cache.\"",
        "self_check_ar": "هل عرفت الموديول كوحدة بناء وملكية وليس مجرد مجلد؟ وهل وازنت بين فوائد التجميع المتوازي وتكاليف الـ Configuration Time؟",
        "references_ar": f"- [Guide to Android App Modularization](https://developer.android.com/topic/modularization) — الدليل الرسمي من جوجل لتقسيم تطبيقات أندرويد.\n- [Gradle Multi-Project Builds](https://docs.gradle.org/current/userguide/multi_project_builds.html) — توثيق جرادل لإدارة المشاريع متعددة الموديولات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "النمطية هي تفكيك التطبيق المتجانس إلى موديولات Gradle مستقلة تمثل حدوداً فيزيائية للبناء والملكية البرمجية. تحقق المعمارية تسريعاً كبيراً في البناء التزايدي بفضل التجميع المتوازي واستخدام الكاش، وتعزز كبسلة الكود بين الفرق المستقلة، بينما تكمن مقايضاتها في زيادة زمن تهيئة Gradle وتعقيد إدارة الاعتماديات ومسارات التنقل.",
        "best_answer_ar": "التقسيم لموديولات في أندرويد ليس مجرد تنظيم للملفات في مجلدات، بل هو إنشاء وحدات بناء برمجية مستقلة تمتلك كل منها ملف build.gradle.kts خاصاً بها ومخرجات تجميع معزولة.\n\nيوفر هذا الهيكل ميزتين رئيسيتين للتطبيقات الكبيرة: تسريع وقت البناء التزايدي من خلال استغلال Gradle للتجميع المتوازي على أنوية المعالج وتفعيل الـ Build Cache لتخطي تجميع الموديولات غير المعدلة، وتحديد ملكية الكود بوضوح بين الفرق البرمجية المختلفة مع فرض الكبسلة باستخدام معرّف الرؤية internal في لغة كوتلن.\n\nفي المقابل، يفرض هذا التقسيم تكاليف هندسية يجب مراعاتها؛ فكل موديول إضافي يزيد من زمن مرحلة تهيئة المشروع في Gradle، ويتطلب توحيد الإعدادات المشتركة عبر Convention Plugins ومشاركة واجهات العقود البرمجية المجردة لإدارة التنقل وحقن التبعيات دون خلق ارتباطات وثيقة بين الموديولات.",
        "deep_answer_ar": "في قيادة هندسة الأنظمة الكبيرة، نعتبر Modularization أداة استراتيجية لتوسيع نطاق العمل البرمجي وضمان استقرار بيئة التطوير مع نمو عدد المهندسين.\n\nعندما يتجاوز الفريق عشرين مطوراً، يتحول التطبيق المتجانس إلى عبء يعطل الإنتاجية بسبب بطء التجميع وتكرار النزاعات البرمجية. ومن خلال تفكيك المشروع لموديولات Gradle مستقلة، ننشئ حدود عزل فيزيائية تتيح للنظام تجميع الموديولات غير المترابطة بالتوازي وتخزين مخرجاتها في Remote Build Cache المشترك؛ بحيث ينحصر زمن البناء عند تعديل شاشة معينة في إعادة تجميع موديول تلك الشاشة فقط.\n\nكما يضمن هذا العزل فرض حدود معمارية صارمة لا يمكن اختراقها؛ فالأكواد المصنفة كـ internal تصبح محصنة ومحمية من الوصول العشوائي من الموديولات الأخرى، مما يمنع التآكل المعماري مع مرور الوقت. ولكننا نحذر من الوقوع في فخ الإفراط في التقسيم بإنشاء عشرات الموديولات الهامشية، لأن كل موديول يستهلك موارد إضافية في مرحلة Configuration Phase لجرادل.\n\nلذلك نعتمد على موديولات عقود API مجردة للتواصل بين الميزات، ونوحد ملفات التكوين عبر Composite Builds ومكتبات Version Catalogs المركزية لضمان بقاء سرعة البناء وصيانة النظام في أفضل مستوياتها الإنتاجية. كما ندمج أدوات قياس زمن المهام لمراقبة أداء Gradle بانتظام، ونفعل خاصية Configuration Cache لتفادي إعادة تقييم ملفات البناء غير المعدلة، مما يوفر تجربة تطوير سريعة ومستقرة للمهندسين يومياً."
    }
}

# ==========================================
# MOD-02: Compare app, feature, core, data, domain, and design-system modules.
# ==========================================
DATA["MOD-02"] = {
    "concept_en": """In a clean multi-module Android architecture, modules are classified by responsibility and layer into distinct categories:
- :app: The top-level assembly coordinator that compiles features and core into the installable APK/AAB and initializes global frameworks (Hilt application component, crash analytics).
- :feature: High-level business slices implementing user flows, Compose UI, and ViewModels (e.g., :feature:checkout). Features never depend on sibling features directly.
- :core: Low-level, non-business infrastructure utilities and platform wrappers (e.g., :core:network, :core:database).
- :data: Manages persistence, network data sources, and repository implementations.
- :domain: Pure Kotlin/Java business logic containing use cases, entities, and repository interfaces without Android framework coupling.
- :design-system: UI tokens, themes, typography, and reusable atomic Compose widgets. It maintains visual consistency without depending on business features or data layers.""",
    "walkthrough_en": """Layered dependency flow and separation of concerns across module types:
```kotlin
// 1. :core:designsystem (No feature dependencies)
@Composable
fun PrimaryFintechButton(text: String, onClick: () -> Unit) { /* ... */ }

// 2. :domain (Pure Kotlin, no Android imports)
data class UserProfile(val id: String, val balance: BigDecimal)
interface UserRepository {
    suspend fun fetchProfile(): Result<UserProfile>
}

// 3. :feature:profile (Depends on domain, core:ui, designsystem)
class ProfileViewModel @Inject constructor(
    private val getUserProfileUseCase: GetUserProfileUseCase
) : ViewModel() { /* ... */ }

// 4. :app (Root composition root)
// dependencies { implementation(project(":feature:profile")) }
```""",
    "short_en": """Layered modular architecture divides responsibilities across module types: app acts as the root assembly coordinator; feature modules implement distinct user journeys; core provides shared platform infrastructure like networking; data encapsulates repositories and persistence; domain houses pure business use cases; and design-system centralizes reusable UI components and themes.""",
    "structured_en": """In a mature multi-module Android architecture, every module type has a distinct responsibility within the directed dependency graph.
The app module sits at the top as the composition root, wiring together features and initializing application-level dependency injection without holding business logic.
Feature modules encapsulate discrete user flows like login or checkout, containing screens, ViewModels, and UI state machines while remaining isolated from sibling features.
The domain module contains pure business logic, entities, and repository interfaces, remaining completely free of Android framework dependencies to enable fast unit testing.
The data module implements these repository interfaces, managing remote network clients and local database persistence.
Core modules provide foundational infrastructure such as networking, crypto utilities, and database drivers that any layer can consume.
The design-system module supplies shared UI components, colors, typography, and design tokens, ensuring visual consistency across all feature modules without importing domain models or business rules.""",
    "deep_senior_en": """Architecting a scalable Android dependency graph requires categorizing modules into clear horizontal layers and vertical slices.
The root app module serves strictly as an assembly coordinator; it applies the Android application plugin, binds Hilt modules, configures navigation graphs, and bundles features into the final binary.
Feature modules represent vertical business slices that deliver user-facing value.
To maintain high cohesion, feature modules must never depend directly on sibling feature modules.
When cross-feature communication is required, it must route through dedicated public API modules or shared navigation contracts.
Horizontally, the domain layer represents the core business policy of the enterprise.
By maintaining domain as a pure Kotlin library free from Android framework dependencies, use cases execute instantaneously in JVM unit tests without needing Robolectric or device emulators.
The data module implements domain repository contracts, mapping network DTOs and Room entities into immutable domain models.
Underneath, core modules provide reusable platform capabilities such as :core:network for Retrofit instances and :core:database for SQLite drivers.
In the visual presentation layer, :core:designsystem acts as the single source of truth for the company's visual language, isolating Compose components and theme tokens from feature-specific logic.
Enforcing this strict layered flow ensures that the dependency graph remains acyclic, predictable, and resilient to refactoring. This separation empowers individual product squads to ship feature updates independently while maintaining rock-solid architectural cohesion across the entire mobile application.""",
    "meta_ar": {
        "id": "MOD-02",
        "questionAr": "قارن بين أنواع الموديولات: app و feature و core و data و domain و design-system.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تحديد مسؤوليات وحدود كل نوع من الموديولات في المعمارية متعددة الطبقات، وتجنب التعميم العشوائي في موديولات core، وحوكمة مسار التبعيات لضمان مخطط غير دائري.",
        "concept_ar": "تنظم المعمارية متعددة الموديولات المشروع في طبقات وشرائح محددة المسؤولية: موديول app هو نقطة التجميع النهائية والتثبيت، موديولات feature تمثل شاشات ورحلات المستخدم المستقلة، موديولات domain تحوي منطق العمل الخالص ككود كوتلن مجرد، موديولات data تدير المستودعات ومصادر البيانات وقواعد البيانات، موديولات core توفر البنية التحتية المشتركة كالشبكات، وموديول design-system يوفر المكونات البصرية والسمات الموحدة.",
        "walkthrough_ar": """نموذج تدفق التبعيات النظيف بين أنواع الموديولات المختلفة:
```kotlin
// feature/checkout يعتمد على:
// - domain (للـ UseCases والكيانات)
// - core:designsystem (للأزرار والسمات البصرية)
// - core:network (لتعريفات الـ API العامة)

// data/payment يعتمد على:
// - domain (لتنفيذ واجهات الـ Repositories)
// - core:database (لقواعد بيانات Room)
```""",
        "why_it_matters_ar": "يمنع خلط المسؤوليات وتشابك الأكواد، ويجعل اختبار منطق الأعمال فورياً على JVM دون محاكي، ويسهل على الفرق المختلفة العمل بالتوازي على ميزات مستقلة دون إحداث تعارضات برمجية.",
        "worked_example_ar": "بناء مسار تحويل مالي يمر من واجهة موديول `:feature:transfer` إلى كلاس الـ UseCase في موديول `:domain` ثم إلى المستودع في موديول `:data` المستند إلى عميل `:core:network`.",
        "trade_offs_ar": "فصل موديول domain المستقل يوفر اختبارات فائقة السرعة واستقلالية لمنطق الأعمال ولكنه يضيف كود ربط وكيانات وسيطة Mappers إضافية، مقارنة بدمج الدومين داخل موديول data لتوفير الجهد في التطبيقات البسيطة.",
        "failure_modes_ar": "استيراد موديول feature داخل موديول feature آخر مما يخلق اقتراناً شديداً، وتضمين أكواد أندرويد في موديول domain مما يفقدها ميزة الاختبار السريع على JVM، وتحويل موديول core إلى سلة مهملات لكافة الأكواد غير المصنفة.",
        "production_perspective_ar": "في الفرق الكبرى، نطبق قواعد فحص آلية على التبعيات في الـ CI عبر أدوات مثل Dependency Analysis Gradle Plugin للتأكد من عدم قيام أي موديول باستيراد طبقة محظورة معمارياً.",
        "how_to_answer_ar": "اشرح وظيفة كل موديول بإيجاز بدءاً من الأعلى (app) نزولاً للأسفل (core و design-system)، واذكر قاعدة عدم اعتماد موديولات الميزات على بعضها، وأهمية تجرد موديول domain من أندرويد.",
        "talking_points_ar": "أهمية خلو موديول domain من مكتبات أندرويد لتسريع الاختبارات، دور design-system في منع تكرار واجهات المستخدم، ومسؤولية موديول app كنقطة ربط وحقن التبعيات.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نفضل أن يكون موديول domain موديول Kotlin خالصاً وليس Android Library؟\"\n  **المرشح:** \"لأنه يضمن عدم اقتران منطق العمل بنظام التشغيل، ويتيح تنفيذ اختبارات الـ Unit Tests بسرعة البرق على JVM دون الحاجة لبيئة تشغيل أندرويد.\"\n\n- **المحاور:** \"كيف تتواصل موديولات الـ Feature مع بعضها إذا كان يُحظر اعتمادها المباشر؟\"\n  **المرشح:** \"من خلال موديولات العقود المجردة Feature-API، أو الروابط العميقة Deep Links، أو عبر واجهات تنقل يربطها موديول الـ app الرئيسي.\"",
        "self_check_ar": "هل حددت دور كل موديول بوضوح؟ وهل أكدت على استقلالية موديولات feature عن بعضها وتجرد موديول domain من أندرويد؟",
        "references_ar": f"- [Android Architecture: Modularization Layers](https://developer.android.com/topic/modularization/patterns) — أنماط تقسيم الموديولات والتسلسل الهرمي للطبقات.\n- [Now in Android Modularization Architecture](https://github.com/android/nowinandroid) — المستودع المرجعي الرسمي من جوجل للمعمارية متعددة الموديولات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تقسم المعمارية النمطية الموديولات بحسب مسؤولياتها: موديول app للتجميع النهائي وربط التبعيات، وموديولات feature لشاشات وتجارب المستخدم المستقلة، وموديول domain لمنطق الأعمال الصافي الخالي من أندرويد، وموديول data للمستودعات ومصادر البيانات، وموديولات core للبنية التحتية المشتركة كالشبكات، وموديول design-system للسمات والمكونات البصرية الموحدة.",
        "best_answer_ar": "في المعمارية متعددة الموديولات المصممة بعناية، يؤدي كل نوع من الموديولات دوراً محدداً بدقة داخل المخطط المعماري.\n\nفي قمة الهرم، يعمل موديول app كنقطة تجميع شاملة لربط واجهات التطبيق وتثبيت الـ Hilt Components وإطلاق التطبيق دون احتواء أي منطق عمل. وتأتي موديولات feature لتمثل شرائح عمودية مستقلة لكل رحلة مستخدم مثل الدفع أو الملف الشخصي، مع حظر اعتمادها على بعضها البعض بشكل مباشر منعاً للتشابك.\n\nوفي الطبقات الأفقية، يمثل موديول domain القلب النابض لمنطق الأعمال؛ فهو كود كوتلن خالص خالٍ تماماً من مكتبات أندرويد لتسهيل اختباره الفوري على الـ JVM. وتتولى موديولات data تنفيذ هذه الواجهات وإدارة قواعد بيانات Room واستدعاءات Retrofit. وتأتي موديولات core لتوفر الأدوات الأساسية المشتركة، بينما يضمن موديول design-system توحيد لغة التصميم والألوان ومكونات Jetpack Compose عبر كافة الشاشات.",
        "deep_answer_ar": "تعتمد المعمارية النمطية القابلة للتوسع على الفصل الدقيق بين الشرائح العمودية للميزات والطبقات الأفقية للبنية التحتية لضمان تدفق أحادي الاتجاه للتبعيات.\n\nيقتصر دور موديول app على العمل كـ Composition Root؛ فهو يربط موديولات الميزات وينشئ كائن Application ويربط موديولات حقن التبعيات في ملف التجميع النهائي، دون أن يتضمن كوداً برمجياً للشاشات. وتعمل موديولات feature كوحدات وظيفية مستقلة تخدم المستخدم، وتتواصل فيما بينها عبر عقود برمجية مجردة API Modules لتفادي أي اقتران مباشر بين الميزات.\n\nوعلى المستوى الأفقي، يمثل عزل موديول domain كـ Pure Kotlin Module مكسباً استراتيجياً كبيراً؛ حيث يسمح بتشغيل آلاف اختبارات الـ Unit Tests لمنطق الأعمال في بضع ثوانٍ على معالج الكمبيوتر مباشرة دون تحميل محاكي أو تشغيل أجهزة وهمية. ويقوم موديول data بربط هذه القواعد بقواعد بيانات Room ومصادر الشبكة، وتحويل كائنات DTOs إلى كيانات Domain نقية.\n\nوتقدم موديولات core خدمات أساسية معزولة تماماً عن منطق الأعمال مثل أدوات التشفير والاتصال بالشبكة، في حين يمثل design-system الواجهة البصرية الموحدة للمنظومة، مما يمنع التكرار ويضمن تطابق الهوية البصرية لكافة شاشات التطبيق عبر الموديولات المختلفة. كما يساعد هذا التقسيم المعماري الدقيق على توزيع المهام بسلاسة بين الفرق المتخصصة، حيث يركز مهندسو واجهات المستخدم على السمات البصرية، بينما تتفرغ فرق البنية التحتية لتطوير خدمات البيانات المشتركة."
    }
}

# ==========================================
# MOD-03: What is a dependency graph? Why must it be acyclic?
# ==========================================
DATA["MOD-03"] = {
    "concept_en": """A dependency graph in a multi-module Gradle project is a formal directed graph where vertices represent independent modules (subprojects) and directed edges represent compile-time or runtime dependencies between them. The graph MUST be acyclic—meaning it forms a Directed Acyclic Graph (DAG)—because build systems depend on topological sorting to compute a deterministic compilation order. If Module A depends on Module B, Module B must finish compilation and produce its symbols and AAR artifact before Module A can begin compilation. If a cycle exists (e.g., A depends on B, and B depends on A), topological sorting is mathematically impossible: neither module can compile first, resulting in infinite recursion or an immediate Gradle build failure with a circular dependency error. Resolving cycles requires inverting dependencies (DIP), extracting shared interface contracts into a third module, or mediating interactions via dependency injection.""",
    "walkthrough_en": """Resolving circular dependencies by extracting a shared API contract module:
```kotlin
// ❌ CIRCULAR DEPENDENCY TRAP:
// :feature:cart depends on :feature:checkout
// :feature:checkout depends on :feature:cart
// FAILS: Circular dependency between project ':feature:cart' and project ':feature:checkout'

// ✅ RESOLUTION VIA API EXTRACTION:
// 1. Create :feature:checkout:api containing only the interface
// feature/checkout/api/src/main/kotlin/CheckoutContract.kt
interface CheckoutNavigator {
    fun openCheckout(context: Context, cartId: String)
}

// 2. :feature:cart depends ONLY on :feature:checkout:api (DAG is preserved)
// 3. :feature:checkout:impl implements CheckoutNavigator
// 4. :app binds CheckoutNavigator implementation via Hilt
```""",
    "short_en": """A dependency graph represents modules as nodes and their dependencies as directed edges. It must be strictly acyclic because Gradle uses topological sorting to determine task execution order. A circular dependency creates an impossible chicken-and-egg compilation loop where neither module can build first, breaking builds and paralyzing incremental caching.""",
    "structured_en": """In multi-module Gradle engineering, the dependency graph models how modules connect across the codebase.
Each module serves as a vertex, while implementation and api declarations define directed edges pointing toward dependencies.
This graph must strictly form a Directed Acyclic Graph, meaning following the arrows never leads back to the originating module.
Gradle relies on topological sorting to calculate the exact execution order of compilation tasks.
When Module A depends on Module B, Gradle compiles Module B first, producing the necessary class files and symbol tables before starting compilation on Module A.
If a cycle occurs, such as Module A depending on Module B while Module B simultaneously depends on Module A, Gradle encounters an unresolvable circular dependency error.
To resolve cyclical dependencies in production, engineers apply the Dependency Inversion Principle.
By extracting shared data models or contract interfaces into an independent API module, both features depend downward on the contract without depending directly on each other.""",
    "deep_senior_en": """The dependency graph is the foundational blueprint of your Android build performance and architectural health.
From a graph theory perspective, Gradle treats tasks as nodes within an execution DAG, resolving task dependencies such as compileKotlin and packageDebug through topological sorting.
If an edge introduces a cycle, the graph loses its partial ordering property, making it mathematically impossible for the compiler to schedule tasks without deadlock.
Beyond direct two-module loops, large codebases frequently suffer from insidious multi-hop cycles, where module A depends on B, B on C, and C imports an internal helper from A.
These transitive loops instantly crash project synchronization and break build caching.
In enterprise architectures, we enforce acyclic dependency rules using continuous integration linters such as Gradle Dependency Analysis Plugin or custom Konsist unit tests that assert forbidden dependency paths.
When an apparent cycle arises between two domain features—such as user profile needing payment data while payment requires user address details—we refuse to merge the modules.
Instead, we extract an explicit interface contract into a lightweight API module or invert the dependency using Hilt.
Feature A consumes the interface, Feature B implements it, and the root app module wires the binding at runtime.
This maintains a clean, single-direction DAG that maximizes Gradle parallel compilation lanes across developer workstations.""",
    "meta_ar": {
        "id": "MOD-03",
        "questionAr": "ما هو مخطط التبعيات (Dependency Graph)، ولماذا يجب أن يكون غير دائري (Acyclic)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مخطط التبعيات كشبكة موجهة DAG تربط وحدات البناء، واستيعاب مخاطر التبعيات الدائرية في شل التصنيف وتوليد الأخطاء، وكيفية فك الحلقات عبر موديولات الواجهات والـ DI.",
        "concept_ar": "مخطط التبعيات (Dependency Graph) هو تمثيل رياضي موجه يربط موديولات المشروع، حيث تمثل العقد الموديولات وتمثل الأسهم علاقات التبعية بينها. يجب أن يكون المخطط غير دائري حتماً (Directed Acyclic Graph - DAG) لأن أدوات البناء مثل Gradle تعتمد على خوارزمية الترتيب الطوبولوجي (Topological Sorting) لتحديد ترتيب تجميع الموديولات. حدوث تبعية دائرية يجعل تحديد البداية مستحيلاً ويشل عملية البناء بخطأ Circular Dependency Error.",
        "walkthrough_ar": """فك التبعية الدائرية عبر استخراج موديول واجهات وسيط (API Extraction):
```kotlin
// الخطأ: موديول cart يعتمد على checkout وموديول checkout يعتمد على cart!
// الحل الهندسي:
// 1. إنشاء موديول :feature:checkout:api يحتوي على واجهة التنقل فقط
interface CheckoutNavigator {
    fun navigateToCheckout(cartId: String)
}

// 2. موديول cart يعتمد على :feature:checkout:api فقط
// 3. موديول checkout ينفذ الواجهة
// 4. موديول app يربط التنفيذ عبر Hilt دون أي حلقة دائرية
```""",
        "why_it_matters_ar": "يمثل المخطط غير الدائري الشرط الرياضي الأساسي لعمل Gradle ومترجمات الكود؛ فبدونه يتعطل البناء التزايدي تماماً، وتفشل أنظمة الـ CI، ويصبح من المستحيل تحديد تسلسل المهام البرمجية.",
        "worked_example_ar": "اكتشاف حلقة دائرية بين موديول `:feature:orders` وموديول `:feature:tracking`، وحلها بإنشاء عقد وسيط `:feature:orders:api` واعتماد الموديولين عليه في اتجاه واحد.",
        "trade_offs_ar": "الحفاظ على المخطط غير الدائري يتطلب في بعض الأحيان استخراج موديولات عقود API وسيطة إضافية مما يرفع عدد الموديولات، ولكنه الضمان الوحيد لاستقرار عملية البناء وتفادي الأخطاء الكارثية.",
        "failure_modes_ar": "حدوث تبعيات دائرية خفية عبر موديولات وسيطة متعددة (A -> B -> C -> A)، واللجوء لدمج الموديولات معاً كحل عشوائي وسريع للتخلص من الدائرة بدلاً من فكها معمارياً.",
        "production_perspective_ar": "في الشركات الكبرى، نضع اختبارات معمارية مؤتمتة باستخدام Konsist أو ArchUnit في مسارات الـ CI تفحص مخطط المشروع باستمرار وترفض أي Pull Request يضيف تبعية قد تؤدي لتكوين حلقة دائرية.",
        "how_to_answer_ar": "عرف مخطط DAG واشرح مفهوم الترتيب الطوبولوجي لجرادل، ثم وضح لماذا تؤدي الدائرة لحالة Deadlock برمجية، واختم بالحلول الهندسية مثل استخراج موديول الـ API وتطبيق Dependency Inversion.",
        "talking_points_ar": "مفهوم الترتيب الطوبولوجي في Gradle، كيفية اكتشاف الحلقات متعددة المستويات، واستخدام مبدأ عكس التبعيات (DIP) وحقن التبعيات لحل التشابك.",
        "follow_ups_ar": "- **المحاور:** \"إذا احتجت لاستدعاء شاشة في موديول A من موديول B والعكس، كيف تحل هذا دون حلقة دائرية؟\"\n  **المرشح:** \"ننشئ موديولين للواجهات :feature:a:api و :feature:b:api، أو نستخدم Deep Links للتنقل، أو نعتمد على موديول الـ app الرئيسي للتنسيق بينهما دون اعتماد مباشر بين الموديولين.\"\n\n- **المحاور:** \"هل يمكن لـ Gradle تجميع موديولين في نفس اللحظة إذا لم تكن بينهما علاقة تبعية؟\"\n  **المرشح:** \"نعم، وهذا هو جوهر التجميع المتوازي Parallel Compilation؛ حيث يجمع جرادل الموديولات المستقلة في مسارات متوازية على أنوية المعالج المختلفة.\"",
        "self_check_ar": "هل شرحت سبب إلزامية كون المخطط Acyclic بالربط بالترتيب الطوبولوجي؟ وهل قدمت حلاً هندسياً واضحاً لفك الحلقات الدائرية؟",
        "references_ar": f"- [Gradle Task Execution and DAG](https://docs.gradle.org/current/userguide/build_lifecycle.html) — دورة حياة بناء جرادل ومخطط المهام الموجه.\n- [Dependency Inversion in Android](https://developer.android.com/topic/architecture) — دليل تطبيق مبدأ عكس التبعيات في بنية أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "مخطط التبعيات هو شبكة موجهة تمثل الموديولات وعلاقات الاعتماد بينها. يجب أن يكون المخطط غير دائري حتماً لأن Gradle يعتمد على الترتيب الطوبولوجي لتحديد تسلسل تجميع الموديولات خطوة بخطوة. وإذا وجدت تبعية دائرية، يستحيل تحديد أي موديول يبدأ بناؤه أولاً، مما يتسبب في فشل فوري لعملية التجميع.",
        "best_answer_ar": "في إدارة مشاريع أندرويد متعددة الموديولات، يمثل مخطط التبعيات شبكة موجهة تربط كل موديول بالموديولات التي يعتمد عليها برمجياً.\n\nيجب أن يكون هذا المخطط غير دائري Acyclic بشكل مطلق؛ لأن نظام Gradle يعتمد على خوارزميات الترتيب الطوبولوجي لحساب الترتيب المنطقي لعمليات البناء. فعندما يعتمد موديول أ على موديول ب، يلتزم Gradle بإنهاء تجميع موديول ب أولاً وتوليد ملفات الكلاسات ومخرجات AAR الخاصة به قبل الشروع في تجميع موديول أ.\n\nفإذا حدثت حلقة دائرية كأن يعتمد أ على ب ويعتمد ب على أ في نفس الوقت، يدخل النظام في معضلة رياضية يستحيل حلها، حيث ينتظر كل موديول انتهاء الآخر، مما يوقف التجميع بخطأ Circular Dependency. ولحل هذه المشكلة هندسياً، نطبق مبدأ عكس التبعية Dependency Inversion؛ فنستخرج الواجهات المشتركة في موديول عقود API منفصل، ليعتمد كلا الموديولين عليه في اتجاه واحد نظيف.",
        "deep_answer_ar": "يمثل مخطط التبعيات غير الدائري DAG الركيزة الرياضية التي تحكم أداء واستقرار منظومة التجميع التزايدي في Gradle.\n\nتتعامل محركات البناء مع الموديولات كعقد داخل شبكة موجهة؛ وتقوم بحساب المسار الحرج وتحديد التوازي الممكن بين أنوية المعالج. وما لم يكن المخطط خالياً تماماً من الحلقات، يفقد النظام خاصية الترتيب الجزئي الرياضي، مما يجعل جدولة مهام compileKotlin مستحيلة ويؤدي لتعطل البناء فوراً.\n\nفي المشاريع الضخمة، لا تظهر الحلقات الدائرية بشكل ثنائي مباشر وبسيط، بل تأتي غالباً عبر مسارات متعددة ومعقدة عبر موديولات وسيطة؛ كأن يستورد موديول الدفع أداة من موديول الملف الشخصي الذي يعتمد بدوره على موديول الإشعارات المرتبط بموديول الدفع. هذه الحلقات الخفية تشل الـ Build Cache وتمنع التجميع التزايدي.\n\nوللحفاظ على نقاء المخطط في بيئة الإنتاج، نضع قواعد معمارية صارمة في مسار الـ CI باستخدام أدوات مثل Konsist لرفض أي علاقة تبعية دائرية فور إنشائها. وعند حاجة ميزتين للتواصل المشترك، نحظر دمجهما معاً ونتجه فوراً لفصل واجهات العقود المجردة في موديولات API مستقلة أو استخدام حقن التبعيات بـ Hilt، لضمان تدفق خطي أحادي الاتجاه يمنح الفريق أعلى كفاءة تجميع متوازية ممكنة. كما نقوم بأرشفة مخطط الموديولات بيانياً وتوليد رسوم توضيحية مؤتمتة في كل عملية بناء، مما يمنح الفريق رؤية واضحة ومستمرة لشجرة التبعيات ويمنع تشابك المسارات البرمجية."
    }
}

# ==========================================
# MOD-04: What is high cohesion and low coupling?
# ==========================================
DATA["MOD-04"] = {
    "concept_en": """High cohesion and low coupling are fundamental software engineering principles that dictate the boundary design and health of modular systems:
- High Cohesion: Elements within a single module are strongly related in purpose, operate on a shared domain model, and change together for a unified business reason (following the Single Responsibility Principle at the module level). A cohesive module has a razor-sharp focus (e.g., :feature:authentication encapsulates only login, registration, and password recovery).
- Low Coupling: Modules maintain minimal, well-defined, and abstract surface areas with external modules. Changes to internal implementation details inside one module do not ripple into downstream consumers.
Violating these principles results in either a monolithic core module (low cohesion, high coupling) or fractured micro-modules that require distributed modifications across the codebase (shotgun surgery).""",
    "walkthrough_en": """Demonstrating high cohesion and low coupling via modular contract boundaries:
```kotlin
// ❌ LOW COHESION & HIGH COUPLING (:core:common dumps unrelated features)
// class CommonGodObject { fun formatCurrency(); fun openCamera(); fun parseJwt() }

// ✅ HIGH COHESION (:feature:scanner focuses strictly on barcode capture)
// feature/scanner/src/main/kotlin/BarcodeScannerManager.kt
class BarcodeScannerManager(private val cameraProvider: CameraProvider) {
    fun startScanning(onDetected: (String) -> Unit) { /* ... */ }
}

// ✅ LOW COUPLING (Consumer interacts via abstract interface, not camera internals)
interface ScannerContract {
    fun launchScanner(launcher: ActivityResultLauncher<Intent>)
}
```""",
    "short_en": """High cohesion means everything inside a module belongs together and serves a single focused purpose, changing for the same business reason. Low coupling means modules maintain minimal dependencies on each other and interact through stable, abstract interfaces. Together, they prevent cascading changes and ensure modules can evolve and compile independently.""",
    "structured_en": """High cohesion and low coupling represent the dual metrics of architectural quality in a multi-module system.
Cohesion measures how focused and unified the responsibilities are within a single module.
In a highly cohesive module, all classes, state models, and utilities work together toward a single business goal, such as user authentication or audio playback.
When business requirements for that capability change, edits remain localized within that specific module.
Coupling, on the other hand, measures the degree of interdependence between different modules.
Low coupling ensures that a module exposes only a minimal, stable public interface while hiding its internal implementation details.
Consumers depend on abstract contracts rather than concrete implementation classes.
If high cohesion is ignored, modules become chaotic dumping grounds for unrelated code.
If low coupling is ignored, a change in one module triggers cascading compilation failures and bugs across the entire application.""",
    "deep_senior_en": """In enterprise Android system design, high cohesion and low coupling govern how we partition bounded contexts into Gradle subprojects.
Cohesion reflects the Single Responsibility Principle elevated to the architectural level: a module should have one, and only one, reason to change.
A feature module like :feature:checkout exhibits high cohesion when its payment form, cart review, and shipping address flows operate around a coherent checkout domain model.
Conversely, dumping payment utilities, image loaders, and date formatters into a single :core:common module destroys cohesion, creating a disguised monolith where unrelated feature teams constantly conflict over shared files.
Coupling dictates the blast radius of change across the dependency graph.
When modules are tightly coupled, modifying an internal database query or refactoring a ViewModel forces downstream consumers to modify their call sites, breaking the Gradle build cache and triggering full recompilations.
We enforce low coupling by applying the Dependency Inversion Principle and separating features into public :api and private :impl modules.
The :api module contains only lightweight interfaces and immutable data transfer objects, while :impl holds internal logic hidden behind Kotlin's internal visibility modifier.
Downstream features import solely the :api module.
This design guarantees that implementation refactors remain strictly contained within their private module boundaries, preserving build cache hits and decoupling feature release lifecycles.""",
    "meta_ar": {
        "id": "MOD-04",
        "questionAr": "ما هو التماسك العالي (High Cohesion) والاقتران المنخفض (Low Coupling) في سياق تقسيم الموديولات؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تطبيق مبادئ هندسة البرمجيات الكلاسيكية على حدود موديولات Gradle، والتمييز بين أسباب التغيير المستقلة، وتجنب موديولات الـ Common المتضخمة التي تكسر التماسك وتزيد الاقتران.",
        "concept_ar": "التماسك العالي (High Cohesion) والاقتران المنخفض (Low Coupling) هما المعياران الأساسيان لجودة تصميم الموديولات: التماسك العالي يعني أن جميع العناصر داخل الموديول ترتبط ارتباطاً وثيقاً بهدف وظيفي واحد وتتغير لنفس السبب التجاري (مبدأ المسؤولية الواحدة للموديول). الاقتران المنخفض يعني تقليل الاعتماد المتبادل ومساحة السطح بين الموديولات المختلفة، بحيث تتواصل عبر واجهات مجردة ومستقرة، مما يمنع انتقال التغييرات الداخلية لموديولات أخرى.",
        "walkthrough_ar": """تطبيق التماسك العالي والاقتران المنخفض عملياً عبر فصل الواجهات والمسؤوليات:
```kotlin
// التماسك العالي: موديول الدفع يهتم بعمليات الدفع فقط
package com.example.feature.payment

class PaymentProcessor @Inject constructor(
    private val paymentGateway: PaymentGateway // اقتران منخفض بواجهة مجردة
) {
    fun processTransaction(amount: Money): TransactionResult {
        return paymentGateway.charge(amount)
    }
}
```""",
        "why_it_matters_ar": "يحدد مدى سهولة صيانة وتطوير النظام؛ فالتماسك العالي يجعل فهم وتعديل الميزة سهلاً ومركّزاً، والاقتران المنخفض يحصر تأثير التعديلات داخل الموديول الواحد ويمنع حدوث أخطاء غير متوقعة في باقي أجزاء التطبيق.",
        "worked_example_ar": "إعادة هيكلة موديول `:core:common` المتضخم عبر فصل أدوات الصور إلى `:core:image-loader` وأدوات التنسيق إلى `:core:formatters`، وتجريد اعتماد موديولات الشاشات عليها عبر واجهات مستقرة.",
        "trade_offs_ar": "تحقيق أقصى درجات الاقتران المنخفض يتطلب إنشاء واجهات تجريدية وموديولات عقود API متعددة مما يرفع حجم البنية التحتية البرمجية، ولكنه يحمي المشاريع الكبيرة من الانهيار المعماري وتكلفة الصيانة الباهظة.",
        "failure_modes_ar": "إنشاء موديول Common عام يحوي أكواداً غير متجانسة مما يفقده التماسك، وربط الموديولات ببعضها عبر الكلاسات الملموسة مباشرة مما يخلق اقتراناً شديداً يجعل أي تعديل بسيط يتطلب تعديل عشرات الموديولات الأخرى.",
        "production_perspective_ar": "في الشركات الكبرى، نراجع تاريخ التعديلات Git History للموديولات؛ فإذا وجدنا أن تعديل ميزة معينة يتطلب فتح PR يمس أكثر من 5 موديولات مختلفة باستمرار (Shotgun Surgery)، فهذا دليل قاطع على خلل في التماسك والاقتران.",
        "how_to_answer_ar": "عرف المفهومين بدقة، ثم اضرب مثالاً لموديول متماسك ومنخفض الاقتران مقابل موديول Common سيء، واشرح كيف ينعكس ذلك على سرعة البناء وصيانة الكود.",
        "talking_points_ar": "ظاهرة Shotgun Surgery كدليل على الاقتران العالي، خطورة موديول Common على التماسك، وكيفية استخدام واجهات الـ API لعزل التغييرات الداخلية.",
        "follow_ups_ar": "- **المحاور:** \"كيف يؤثر الاقتران العالي High Coupling على زمن بناء التطبيق في Gradle؟\"\n  **المرشح:** \"الاقتران العالي يجعل أي تعديل في موديول ما يتسبب في كسر الكاش وإعادة تجميع كافة الموديولات المعتمدة عليه، مما يدمر ميزة التجميع التزايدي.\"\n\n- **المحاور:** \"ما هي العلامة المعمارية التي تدل على أن موديولاً ما يعاني من ضعف التماسك Low Cohesion؟\"\n  **المرشح:** \"عندما تجد الموديول يحتوي على كود يتغير لأسباب تجارية متعددة وغير مترابطة، مثل احتواء موديول المستخدم على كود لتوليد التقارير وأكواد للتعامل مع البلوتوث!\"",
        "self_check_ar": "هل فرقت بدقة بين التماسك والاقتران؟ وهل وضحت تأثيرهما على صيانة الكود وزمن التجميع التزايدي في جرادل؟",
        "references_ar": f"- [Coupling and Cohesion in Software Engineering](https://martinfowler.com/) — مقالات مارتن فاولر حول أسس التصميم المعماري النظيف.\n- [Android App Modularization Guidelines](https://developer.android.com/topic/modularization) — إرشادات جوجل لتقسيم الموديولات وتحديد حدودها.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "التماسك العالي يعني أن جميع مكونات الموديول تعمل لتحقيق هدف وظيفي موحد وتتغير لنفس السبب التجاري، بينما الاقتران المنخفض يعني تقليل الاعتماد المتبادل بين الموديولات وتواصلها عبر واجهات مجردة ومستقرة. يحقق هذا المزيج حصر نطاق التعديلات وتفادي الأخطاء المتسلسلة وضمان كفاءة التجميع التزايدي.",
        "best_answer_ar": "يمثل التماسك العالي والاقتران المنخفض المقياس الحقيقي لجودة التقسيم المعماري في أنظمة أندرويد الحديثة.\n\nيعبر التماسك العالي عن مدى تركيز الموديول حول مسؤولية وظيفية محددة؛ ففي موديول تسجيل الدخول مثلاً، تجد شاشات الدخول واستعادة كلمة المرور ونماذج التوثيق تعمل معاً بتناغم لخدمة غرض واحد، مما يجعل أي تعديل في سياسة التوثيق محصوراً داخل هذا الموديول دون تشتت.\n\nأما الاقتران المنخفض، فيقيس درجة ارتباط الموديول بغيره من موديولات النظام؛ حيث يحرص الموديول منخفض الاقتران على إخفاء تفاصيله الداخلية واعتماد موديولات النظام الأخرى على واجهات مجردة ومستقرة بدلاً من الكلاسات الملموسة. وإذا اختل هذا التوازن بزيادة الاقتران، فإن تعديل سطر واحد في موديول فرعي قد يؤدي لانهيار التجميع في خمسة موديولات أخرى، مما يعطل توازي البناء ويزيد من احتمالية ظهور الأخطاء غير المتوقعة في بيئة الإنتاج.",
        "deep_answer_ar": "في هندسة البرمجيات المتقدمة، نطبق التماسك العالي والاقتران المنخفض لترسيم الحدود الفاصلة بين الموديولات وفق نظرية Bounded Contexts في التصميم الموجه بالمجال DDD.\n\nيجسد التماسك العالي مبدأ المسؤولية الواحدة على مستوى الموديول؛ فالموديول يجب أن يمتلك سبباً واحداً فقط للتغيير. فعندما ننشئ موديولاً لميزة السلة `:feature:cart`، نحرص على أن تكون كافة مكوناته خادمة لعملية إدارة المشتريات حصرياً. ونحذر بشدة من فخ تجميع أدوات عشوائية كمعالجة الصور وتنسيق التواريخ في موديول `:core:common`؛ لأن ذلك ينسف التماسك ويجعل الموديول عرضة لتعارضات التعديل الدائمة بين الفرق المختلفة.\n\nوعلى الجانب المقابل، يحمينا الاقتران المنخفض من ظاهرة Shotgun Surgery؛ حيث نضمن عدم تسرب التفاصيل البرمجية الداخلية عبر حدود الموديولات. ونحقق ذلك هندسياً بفصل كل ميزة إلى موديولين: موديول `:api` عام وموديول `:impl` داخلي وخاص. موديول الـ API يحتوي على الواجهات المجردة والكيانات الثابتة، بينما تُحمى كلاسات الـ impl بمعرّف internal الخاص بكوتلن.\n\nهذا الفصل يضمن أن موديولات المستهلكين تعتمد على واجهات ثابتة لا تتغير، مما يسمح لفريق العمل بإعادة هيكلة وتطوير الكود الداخلي بحرية تامة دون كسر عقود التجميع أو إبطال مخرجات الـ Build Cache للمشروع ككل. كما نلزم المطورين بمراجعة التبعيات المستحدثة قبل دمجها، لضمان بقاء كل موديول مركزاً حول نطاق عمله الأصلي ومنع تداخل المسؤوليات الوظيفية بين الميزات المختلفة."
    }
}

# ==========================================
# MOD-05: Compare Gradle api and implementation dependencies.
# ==========================================
DATA["MOD-05"] = {
    "concept_en": """In modern Gradle dependency management (via java-library and com.android.library plugins), the implementation and api configurations dictate how dependencies leak across compilation boundaries:
- implementation: Hides the dependency from the compile classpath of downstream consumers. Types from the dependency are available at runtime and to the declaring module at compile time, but any module that imports the declaring module cannot resolve those types. This establishes an ABI (Application Binary Interface) boundary: changes to implementation dependencies do not trigger recompilation of downstream modules, dramatically improving incremental build times.
- api: Transitively exports the dependency onto the compile classpath of all downstream consumers. It is required when a module exposes types from the dependency in its own public method signatures, interfaces, or return types. Overusing api destroys compilation isolation, creating cascading recompilations across the entire build graph whenever the dependency changes.""",
    "walkthrough_en": """Demonstrating compilation isolation between implementation and api in Gradle:
```kotlin
// module: :core:network/build.gradle.kts
dependencies {
    // OkHttp is an internal engine implementation detail
    implementation(libs.okhttp)
    // Retrofit interfaces exposed in public API methods require 'api'
    api(libs.retrofit)
}

// module: :feature:news/build.gradle.kts
dependencies {
    implementation(project(":core:network"))
}

// Inside :feature:news source code:
// val service: Retrofit = ... // COMPILES! (Retrofit is exposed via 'api')
// val client: OkHttpClient = ... // COMPILER ERROR! (OkHttp is hidden via 'implementation')
```""",
    "short_en": """The implementation configuration keeps a dependency private to the declaring module, preventing downstream consumers from seeing its types at compile time and shielding them from recompilation when internal code changes. The api configuration exports the dependency transitively to consumers, required only when types appear in public signatures but causing cascading rebuilds when overused.""",
    "structured_en": """Understanding the difference between Gradle api and implementation configurations is essential for building performant multi-module architectures.
The implementation configuration keeps the dependency internal to the declaring module.
Types from that library are omitted from the compile classpath of any downstream consumer that depends on the module.
This creates a strict compilation firewall: as long as the module's public ABI remains unchanged, modifications to its implementation dependencies will not trigger recompilations of downstream modules.
Conversely, the api configuration transitively exposes the dependency to the compile classpath of all downstream modules.
You should use api only when types from the underlying library are exposed in the module's public method signatures, interface contracts, or public property definitions.
Defaulting to api is an architectural anti-pattern that tightly couples modules and invalidates the Gradle build cache across the entire project.""",
    "deep_senior_en": """At the compiler level, the distinction between api and implementation hinges on the Application Binary Interface boundary.
When Gradle analyzes task dependencies for compileKotlin, it evaluates the compile classpath of each subproject.
By utilizing implementation, a module encapsulates its internal dependencies.
If module B depends on module A using implementation, and module A refactors an internal library or upgrades an implementation dependency, Gradle determines that module A's ABI has not changed.
Consequently, module B's compileKotlin task is marked as UP-TO-DATE, bypassing recompilation entirely.
If module A had declared the dependency using api, Gradle would be forced to assume that module B's compile classpath is dirty, triggering cascading recompilation downstream across dozens of dependent feature modules.
In enterprise multi-module codebases, our governing rule is: default to implementation everywhere.
We only promote a dependency to api when an exported type from that library is an inescapable part of our module's public API contract.
Even then, senior architects prefer wrapping third-party types in internal domain models rather than leaking external library types across module boundaries, preserving complete control over our compilation topology. We enforce this policy through automated static architecture checks in CI, automatically detecting when an implementation dependency is inadvertently exposed and preventing build cache invalidation regressions across downstream feature modules.""",
    "meta_ar": {
        "id": "MOD-05",
        "questionAr": "قارن بين إعدادات التبعيات api و implementation في Gradle وتأثيرهما على التجميع.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "الفروق الجوهرية في تسريب التبعيات على مسار تجميع المستهلكين Compile Classpath، وتأثير ABI على إعادة التجميع وGradle Build Cache، وقواعد الاختيار في المشاريع الكبرى.",
        "concept_ar": "يحدد كل من implementation و api كيفية انتشار التبعيات عبر حدود الموديولات في Gradle: إعداد implementation يحصر التبعية داخل الموديول المعلن فقط ويخفيها عن مسار تجميع الموديولات المستهلكة (Compile Classpath)، مما ينشئ جدار حماية ABI يمنع إعادة تجميع باقي الموديولات عند حدوث أي تعديل داخلي. بينما يقوم api بتمرير التبعية بشكل عابر (Transitive) لكافة الموديولات التابعة، ويستخدم فقط عندما تظهر كلاسات التبعية في الواجهات والـ Signatures العامة للموديول.",
        "walkthrough_ar": """توضيح الفرق العملي بين api و implementation وتأثيره على مسار التجميع:
```kotlin
// في موديول :core:network
dependencies {
    // مكتبة OkHttp داخلية ولا تظهر في الواجهات العامة
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    // مكتبة Retrofit تظهر في الواجهات العامة وتمرر للمستهلكين
    api("com.squareup.retrofit2:retrofit:2.11.0")
}

// في موديول :feature:profile
dependencies {
    implementation(project(":core:network"))
}
// داخل كود profile:
// استخدام Retrofit يعمل بنجاح لأنها معرفة بـ api
// استخدام OkHttp يعطي خطأ تجميع لأنها مخفية بـ implementation
```""",
        "why_it_matters_ar": "يمثل العامل الحاسم في سرعة التجميع التزايدي (Incremental Build Time) للمشاريع الكبيرة؛ فالاعتماد على implementation يحمي كاش Gradle ويمنع إعادة تجميع مئات الكلاسات عند تعديل سطر برمجي داخلي في أحد الموديولات.",
        "worked_example_ar": "قياس زمن تجميع مشروع بعد تحويل 10 موديولات من استخدام api العشوائي إلى implementation، ورصد انخفاض عدد المهام المعاد تجميعها من 45 مهمة إلى مهمتين فقط عند تعديل دالة داخلية.",
        "trade_offs_ar": "استخدام implementation يفرض عليك في بعض الأحيان كتابة كود وسيط Wrappers لعدم تسريب أنواع المكتبات الخارجية، ولكنه يمنحك سرعة تجميع فائقة وحماية معمارية صلبة مقارنة بسهولة api التي تدمر سرعة البناء.",
        "failure_modes_ar": "استخدام api كخيار افتراضي في كافة الموديولات لسهولة الوصول، مما يجعل أي تعديل في موديول منخفض يعيد تجميع التطبيق بالكامل، وتسريب كلاسات نيتف أو مكتبات طرف ثالث غير مستقرة للمستهلكين.",
        "production_perspective_ar": "في الفرق الكبرى، نستخدم إضافة Dependency Analysis Gradle Plugin لاكتشاف حالات التبعيات المصرح عنها بـ api والتي يمكن تخفيضها بأمان إلى implementation، ونمنع دمج أي PR يستخدم api دون مبرر معماري.",
        "how_to_answer_ar": "ابدأ بالفارق الأساسي في Compile Classpath وتسريب التبعيات، ثم اشرح تأثير جدار حماية ABI على سرعة البناء التزايدي والكاش، واختم بالقاعدة الإنتاجية: implementation افتراضياً و api للضرورة القصوى.",
        "talking_points_ar": "مفهوم جدار حماية ABI (Application Binary Interface)، كيفية تجنب Cascading Recompilations، ودور أداة Dependency Analysis Plugin في فحص مسارات التجميع.",
        "follow_ups_ar": "- **المحاور:** \"إذا عدلت في كود دالة داخل موديول تم ربطه بـ implementation، هل يُعاد تجميع الموديولات المعتمدة عليه؟\"\n  **المرشح:** \"لا؛ طالما لم يتغير توقيع الدالة العام (ABI)، فإن Gradle يعتبر مخرجات تجميع الموديولات المستهلكة UP-TO-DATE ولا يعيد تجميعها مطلقاً.\"\n\n- **المحاور:** \"متى نكون مجبرين معمارياً على استخدام api؟\"\n  **المرشح:** \"عندما تُرجع إحدى الدوال العامة في الموديول كائناً من تلك المكتبة، أو يرث كلاس عام منها، بحيث يحتاج المستهلك معرفة النوع لتجميع كوده.\"",
        "self_check_ar": "هل شرحت الفرق بدقة على مسار التجميع Compile Classpath؟ وهل وضحت تأثير ABI على سرعة البناء التزايدي في جرادل؟",
        "references_ar": f"- [Gradle Java Library Plugin: API vs Implementation](https://docs.gradle.org/current/userguide/java_library_plugin.html) — التوثيق الرسمي لجرادل للفروق بين api و implementation.\n- [Android Performance: Modularization and Build Speed](https://developer.android.com/topic/modularization) — إرشادات تسريع البناء عبر إدارة التبعيات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يحصر إعداد implementation التبعية داخل الموديول المعلن فقط ويخفيها عن مسار تجميع الموديولات المستهلكة، مما يحمي المشروع من إعادة التجميع عند تغير الكود الداخلي. بينما يقوم api بتمرير التبعية بشكل عابر للمستهلكين، ويقتصر استخدامه على الحالات التي تظهر فيها أنواع المكتبة في التوقيعات البرمجية العامة، تجنباً لبطء البناء.",
        "best_answer_ar": "الفارق الجوهري بين api و implementation في Gradle يدور حول مسار التجميع Compile Classpath وحماية حدود واجهة التطبيق الثنائية ABI.\n\nعند استخدام implementation، تظل التبعية خاصة بالموديول المعلن؛ فإذا كان موديول الميزات يعتمد على موديول الشبكة المرتبط بـ OkHttp عبر implementation، فإن كود الميزات يعجز تماماً عن استيراد أو رؤية كلاسات OkHttp أثناء التجميع. هذه الكبسلة تنشئ جدار حماية يضمن لجرادل أن أي تعديل داخلي في كود OkHttp لن يؤثر على كود الميزات، فيتخطى إعادة تجميعه تماماً ويوفر وقتاً ثميناً في البناء التزايدي.\n\nأما عند استخدام api، فإن Gradle يسرب التبعية بصورة عابرة لكافة الموديولات المعتمدة. ويلزم استخدام api فقط عندما يكون نوع البيانات من المكتبة الخارجية جزءاً من دالة عامة أو واجهة يراها المستهلك. ولكن الإفراط في استخدام api يكسر العزل المعماري؛ فإذا تغيرت المكتبة، يُجبر Gradle على إعادة تجميع كافة موديولات المشروع المتأثرة بالتسريب المتسلسل.",
        "deep_answer_ar": "في قيادة هندسة النظم البرمجية، يشكل الاختيار بين api و implementation حجر الزاوية في ضبط أداء التجميع عبر الـ Build Cache وتقليل زمن دورة التطوير Feedback Loop.\n\nيعتمد Gradle في فحص التغيرات على تحليل واجهة التطبيق الثنائية ABI للموديول؛ فإذا استخدمنا implementation، فإن التعديل في تفاصيل التنفيذ الداخلية للموديول لا يغير بصمة الـ ABI الخارجية. هذا يعني أن مهمة compileKotlin لكافة الموديولات المستهلكة تظل محتفظة بحالة UP-TO-DATE ولا تعيد التجميع نهائياً. أما استخدام api فيجعل التبعية جزءاً لا يتجزأ من السطح العام للموديول، مما يدمر هذه الميزة ويؤدي لظاهرة التجميع المتسلسل Cascading Recompilation عبر عشرات الموديولات المستهلكة.\n\nلذلك نطبق في بيئات الإنتاج سياسة صارمة: الاعتماد الافتراضي المطلق على implementation في كافة ملفات البناء. ولا نسمح باستخدام api إلا بعد مراجعة معمارية تثبت أن نوع البيانات الخارجي يمثل عقداً عاماً لا غنى عنه للمستهلكين.\n\nبل نفضل كإجراء وقائي تغليف الكائنات الخارجية بأنماط Wrapper أو Domain Mappers داخلية؛ لضمان عدم تسريب أي كائن من مكتبة طرف ثالث إلى الموديولات الأخرى، مما يبقي شجرة التبعيات نقية ويمنحنا القدرة على استبدال المكتبات الأساسية دون المساس بأي موديول مستهلك في التطبيق. كما نستخدم إضافات فحص التبعيات الآلية في مسار البناء لاكتشاف أي تسريب غير مقصود للمكتبات، مما يحمي المشروع من إعادة التجميع الشاملة ويحافظ على سرعة التطوير اليومية."
    }
}

# ==========================================
# MOD-06: What are Dynamic Feature Modules / Play Feature Delivery?
# ==========================================
DATA["MOD-06"] = {
    "concept_en": """Dynamic Feature Modules (DFMs) and Google Play Feature Delivery allow Android applications to separate features into isolated modules that can be downloaded conditionally, deferred in the background, or retrieved on demand at runtime via the Google Play Core library (SplitInstallManager). Unlike standard library modules where the base application module depends on the feature, DFMs invert the Gradle dependency direction: the dynamic feature module declares a dependency on the base :app module (via implementation(project(":app"))), while the :app module declares dynamicFeatures = [":feature:ondemand"]. This structural inversion means the base APK cannot directly reference dynamic feature classes at compile time. Cross-boundary navigation requires reflection, dynamic service locator registries, or deep link URIs. DFMs reduce the initial app download size dramatically, but introduce operational complexity: network latency during downloads, offline error handling, and Play Core testing requirements.""",
    "walkthrough_en": """Configuring dynamic delivery and loading a feature on-demand using SplitInstallManager:
```kotlin
// feature/scanner/build.gradle.kts
plugins {
    alias(libs.plugins.android.dynamic.feature)
}
dependencies {
    implementation(project(":app"))
}

// Requesting on-demand download at runtime in the base app:
fun downloadAndLaunchScanner(context: Context) {
    val splitInstallManager = SplitInstallManagerFactory.create(context)
    val request = SplitInstallRequest.newBuilder()
        .addModule("scanner")
        .build()

    splitInstallManager.startInstall(request)
        .addOnSuccessListener { sessionId ->
            // Module downloaded! Launch via explicit component reflection or deep link
            val intent = Intent().setClassName(context, "com.example.scanner.ScannerActivity")
            context.startActivity(intent)
        }
        .addOnFailureListener { exception ->
            // Handle network failure, insufficient disk space, or offline state
        }
}
```""",
    "short_en": """Dynamic Feature Modules enable Play Feature Delivery, allowing apps to download features on-demand, conditionally by device spec, or deferred in the background. They invert the standard Gradle dependency direction because the dynamic module depends on the app module. This slashes initial install size but requires handling runtime network download latency, offline failures, and reflection-based navigation.""",
    "structured_en": """Dynamic Feature Modules provide an advanced packaging mechanism through Google Play Feature Delivery to optimize application install size.
Standard Android modules are compiled directly into the base APK, forcing all users to download every feature upon initial install.
With dynamic features, secondary or specialized capabilities like augmented reality viewers, heavy document scanners, or onboarding wizards are isolated into separate delivery units.
These units can be downloaded on-demand when the user opens the feature, conditionally based on device hardware like camera features or country, or deferred silently in the background.
Architecturally, dynamic modules invert the Gradle dependency graph: the dynamic feature module depends on the base app module, while the base app specifies the dynamic module in its build configuration.
Because the base app cannot see dynamic classes at compile time, navigation must be decoupled through deep links, reflection, or dynamic dependency injection.
Teams must build robust UI states to handle download progress, network disconnections, and storage errors.""",
    "deep_senior_en": """From an engineering and product perspective, Dynamic Feature Modules represent a trade-off between initial user acquisition conversion rates and runtime operational complexity.
Google Play data shows that for every six megabytes added to initial APK download size, install conversion rates drop by roughly one percent.
By offloading niche or heavy features into dynamic modules, we keep our initial download size well below cellular network warning thresholds.
However, the architectural cost of dynamic delivery is profound due to Gradle dependency inversion.
In conventional builds, :app imports features.
In dynamic delivery, the dynamic module applies com.android.dynamic-feature and imports :app as an implementation dependency, while :app lists the module inside dynamicFeatures.
This inversion breaks direct compile-time code references from the base APK.
To open a dynamic feature screen, we cannot invoke a standard Intent referencing the Activity class literal.
We must either navigate via deep link URIs, register interface providers in a dynamic service registry upon split loading, or invoke classes reflectively after SplitInstallManager signals successful installation.
Furthermore, dynamic features require SplitCompat.install(context) initialization in Application and Activity contexts to resolve resources correctly.
Production engineering demands designing comprehensive fallback user flows: displaying progress indicators during download, handling network failures gracefully without stranding the user, and mocking SplitInstallManager during local automated testing using FakeSplitInstallManager.""",
    "meta_ar": {
        "id": "MOD-06",
        "questionAr": "ما هي موديولات الميزات الديناميكية (Dynamic Feature Modules) و Play Feature Delivery؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "معمارية الموديولات القابلة للتنزيل عند الطلب، وعكس اتجاه تبعية Gradle نحو موديول app، والتعامل مع سيناريوهات التحميل دون اتصال وحالات فشل الشبكة.",
        "concept_ar": "موديولات الميزات الديناميكية (Dynamic Feature Modules) هي معمارية توزيع متقدمة عبر Play Feature Delivery تتيح تنزيل أجزاء من التطبيق عند الطلب (On-Demand) أو بشروط معينة (Conditional) أو في الخلفية (Deferred) بدلاً من تضمينها في حزمة التثبيت الأساسية. تعكس هذه الموديولات اتجاه تبعيات Gradle التقليدي؛ حيث يعتمد موديول الميزة الديناميكية على موديول app الأساسي، مما يمنع التطبيق الأساسي من استيراد كلاسات الميزة وقت التجميع ويتطلب التنقل عبر الروابط العميقة أو الانعكاس البرمجي (Reflection).",
        "walkthrough_ar": """تهيئة موديول ديناميكي وطلب تنزيله في وقت التشغيل عبر SplitInstallManager:
```kotlin
// feature/scanner/build.gradle.kts
plugins { id("com.android.dynamic-feature") }
dependencies { implementation(project(":app")) }

// في الكود الأساسي: طلب التنزيل عند طلب المستخدم
val splitInstallManager = SplitInstallManagerFactory.create(context)
val request = SplitInstallRequest.newBuilder()
    .addModule("scanner")
    .build()

splitInstallManager.startInstall(request)
    .addOnSuccessListener {
        // تم التنزيل بنجاح، يتم فتح الشاشة عبر Deep Link أو Reflection
    }
    .addOnFailureListener {
        // معالجة انقطاع الإنترنت أو نقص مساحة التخزين
    }
```""",
        "why_it_matters_ar": "يقلل حجم التنزيل الأولي للتطبيق في متجر Google Play بشكل هائل، مما يرفع معدلات تثبيت التطبيق وتجربة المستخدم، ويتيح تقديم ميزات ثقيلة متخصصة (مثل الواقع المعزز) لمن يحتاجها فقط.",
        "worked_example_ar": "فصل ميزة تصوير الشيكات البنكية بالذكاء الاصطناعي إلى Dynamic Feature وتنزيلها فقط عند دخول العميل لشاشة الإيداع، مع إظهار شريط تقدم التنزيل ومعالجة انقطاع الاتصال.",
        "trade_offs_ar": "تقليص حجم التطبيق بنسبة تصل لـ 40% مقابل زيادة التعقيد المعماري في إدارة حالات التنزيل، وتأخير فتح الميزة لأول مرة، وصعوبة اختبار دورة حياة التنزيل محلياً دون أدوات محاكاة.",
        "failure_modes_ar": "افتراض اتصال الإنترنت الدائم وفشل فتح الميزة دون اتصال، ونسيان تهيئة SplitCompat.install في سياق التطبيق مما يؤدي لانهياره لعدم العثور على الموارد، ومحاولة استدعاء كلاسات الميزة مباشرة في كود التطبيق الأساسي.",
        "production_perspective_ar": "في التطبيقات الإنتاجية، نستخدم FakeSplitInstallManager في اختبارات الـ UI المؤتمتة لمحاكاة حالات التحميل البطيء وانقطاع الشبكة، ونوفر شاشات بديلة تتيح للمستخدم إعادة المحاولة بسلاسة.",
        "how_to_answer_ar": "ابدأ بهدف تقليص حجم الـ APK عبر ميزات Play Delivery، ثم اشرح الانعكاس المعماري لتبعية Gradle (الميزة تعتمد على app)، ووضح كيفية التنقل والمعالجة الآمنة للشبكة وأخطاء التنزيل.",
        "talking_points_ar": "عكس التبعية في Gradle، دور SplitInstallManager و SplitCompat، وكيفية التنقل دون استيراد مباشر للكلاسات باستخدام Deep Links.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتمد موديول الـ Dynamic Feature على موديول الـ app وليس العكس؟\"\n  **المرشح:** \"لأن التطبيق الأساسي يجب أن يُبنى ويُثبت أولاً كـ Base APK، ثم تُركب الميزات الديناميكية فوقه كـ Split APKs؛ لذلك تملك الميزة حق الوصول لكود الأساس وليس العكس.\"\n\n- **المحاور:** \"كيف تتنقل لشاشة داخل Dynamic Feature إذا كان كودها غير مرئي للـ app؟\"\n  **المرشح:** \"نستخدم الروابط العميقة Deep Links، أو نحدد اسم الكلاس كنص صريح عبر Intent(className)، أو نسجل واجهات تقديم الخدمة Service Locator بعد اكتمال التنزيل.\"",
        "self_check_ar": "هل وضحت ظاهرة عكس التبعية في Gradle؟ وهل بينت كيفية إدارة التنزيل والتعامل مع حالات انقطاع الشبكة وتهيئة SplitCompat؟",
        "references_ar": f"- [Google Play Feature Delivery](https://developer.android.com/guide/playcore/feature-delivery) — الدليل الرسمي لتسليم الميزات الديناميكية عند الطلب.\n- [Reduce App Size with Dynamic Delivery](https://developer.android.com/topic/performance/reduce-app-size) — إرشادات جوجل لتقليل حجم التطبيقات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "موديولات الميزات الديناميكية تتيح تنزيل أجزاء من التطبيق عند الطلب أو بشروط معينة عبر Play Feature Delivery لتقليص حجم التثبيت الأولي. تتميز معمارياً بعكس اتجاه تبعيات Gradle؛ حيث يعتمد موديول الميزة على التطبيق الأساسي، مما يتطلب إدارة التنزيل بـ SplitInstallManager والتنقل عبر الروابط العميقة ومعالجة حالات انقطاع الشبكة.",
        "best_answer_ar": "تعتبر موديولات الميزات الديناميكية حلاً معمارياً متقدماً موفراً عبر نظام Google Play Feature Delivery يهدف لتحسين معدل تنزيل التطبيقات بتقليص حجمها المبدئي.\n\nبدلاً من إجبار كافة المستخدمين على تحميل كل ميزات التطبيق دفعة واحدة، نفصل الميزات النادرة أو الثقيلة كأدوات الواقع المعزز ومسح المستندات في وحدات مستقلة. يتم تنزيل هذه الموديلات إما عند فتح المستخدم للشاشة لأول مرة، أو تلقائياً في الخلفية، أو بشروط عتادية محددة كوجود مستشعر كاميرا معين.\n\nمن الناحية المعمارية، تفرض هذه الموديولات انعكاساً فريداً في شجرة تبعيات Gradle؛ حيث يعتمد موديول الميزة الديناميكية على موديول app الأساسي، بينما يكتفي موديول app بذكر الميزة في إعدادات dynamicFeatures. ونظراً لأن كلاسات الميزة غير مرئية للتطبيق الأساسي وقت التجميع، نعتمد على الروابط العميقة Deep Links للتنقل، مع بناء واجهات تفاعلية ترصد تقدم التنزيل وتتعامل بمرونة مع انقطاع الإنترنت أو امتلاء الذاكرة.",
        "deep_answer_ar": "في استراتيجيات النمو للتطبيقات الكبرى، ترتبط نسبة تثبيت التطبيق ارتباطاً وثيقاً بحجمه الأولي على المتجر؛ حيث تؤكد دراسات جوجل أن زيادة 6 ميجابايت تفقد التطبيق 1% من معدل التثبيت. ومن هنا تنبع الأهمية الاستراتيجية لـ Dynamic Feature Modules.\n\nتكمن الصعوبة المعمارية لهذه التقنية في التفكيك الجذري لنموذج البناء التقليدي؛ فبينما تعتمد التطبيقات العادية على استيراد الميزات داخل موديول app، نجد أن موديول الـ dynamic-feature هو الذي يمتلك تبعية على :app. هذا الانعكاس يحرمنا من استدعاء كلاسات الميزة بشكل مباشر؛ فنلجأ لحلول متقدمة مثل تسجيل موفري الخدمات ديناميكياً بعد التنزيل أو استخدام الروابط العميقة المشروطة بالتحقق من اكتمال التثبيت.\n\nكما تتطلب هذه الموديولات تهيئة دقيقة لسياق التطبيق عبر SplitCompat.install لضمان قدرة أندرويد على قراءة الموارد البرمجية للموديول الجديد دون انهيار. وفي بيئة الإنتاج، لا نترك المستخدم في فراغ أثناء التنزيل؛ بل نبني آلة حالات تدير أحداث SplitInstallStateUpdatedListener لعرض نسبة التقدم، وتوفير آليات إعادة محاولة ذكية عند ضعف التغطية، مع محاكاة بيئة التنزيل في الاختبارات الآلية باستخدام FakeSplitInstallManager لضمان متانة وسلاسة رحلة المستخدم بالكامل. كما نوفر آليات استرجاع سحابية تتيح إلغاء تثبيت الموديولات غير المستخدمة لتحرير مساحة تخزين الهاتف، ونراقب معدلات نجاح التنزيل عبر أدوات التحليل لاتخاذ قرارات هندسية قائمة على البيانات الميدانية الدقيقة."
    }
}

# ==========================================
# MOD-07: Design a multi-module structure for a large app.
# ==========================================
DATA["MOD-07"] = {
    "concept_en": """Designing an enterprise multi-module architecture requires harmonizing horizontal architectural layers with vertical feature slices into a coherent Directed Acyclic Graph (DAG). An optimal structure establishes three primary tiers:
1. Root Tier (:app): Pure composition root that configures Hilt dependency injection, builds the application class, and packages release artifacts.
2. Feature Tier (:features:<name>): Subdivided into :api (public contracts, interfaces, and navigation destinations) and :impl (UI screens, ViewModels, and internal business logic). Cross-feature dependencies are strictly restricted to :api modules, completely preventing inter-feature implementation coupling.
3. Core Infrastructure Tier (:core:<name>): Highly cohesive, domain-agnostic platform modules including :core:network (Retrofit, OkHttp, cert pinning), :core:database (Room, encryption), :core:designsystem (Compose components, typography, theme), and :core:common (dispatchers, logging abstractions).
This taxonomy maximizes parallel build lanes, enforces clean code ownership, and prevents dependency spaghetti.""",
    "walkthrough_en": """Scalable enterprise multi-module directory and dependency structure:
```text
root/
├── app/                        (Composition root, builds APK)
├── core/
│   ├── designsystem/          (Compose theme, atomic UI components)
│   ├── network/               (Retrofit, OkHttp engine, token refresh)
│   ├── database/              (Room database, DAOs, migrations)
│   └── common/                (Coroutines dispatchers, extensions)
└── features/
    ├── checkout/
    │   ├── api/               (CheckoutNavigator, CheckoutResult contract)
    │   └── impl/              (CheckoutScreen, CheckoutViewModel, CheckoutRepository)
    └── catalog/
        ├── api/               (CatalogRoute contract)
        └── impl/              (CatalogScreen, depends on :features:checkout:api ONLY)
```""",
    "short_en": """An enterprise multi-module structure organizes the codebase into a clean DAG: an app composition root at the top, vertical feature modules split into public api contracts and private implementation details, and horizontal core modules underneath covering networking, database, design-system, and platform utilities. Features communicate strictly through api interfaces, preventing direct coupling and maximizing build parallelism.""",
    "structured_en": """Designing a multi-module architecture for a large application requires balancing feature autonomy with centralized infrastructural consistency.
At the top level, the app module serves as the composition root, initializing application-level dependency injection and assembling features into the final binary without containing business logic.
Feature modules represent vertical domain slices such as checkout, search, or profile.
To prevent coupling, each feature is divided into a public api module and a private implementation module.
When one feature needs to trigger an action in another, it imports only the public api contract, keeping internal screens and ViewModels completely hidden.
Beneath the feature layer, horizontal core modules provide foundational capabilities.
These include core:designsystem for reusable UI components, core:network for authenticated HTTP clients, and core:database for local persistence.
This structure maintains an acyclic dependency graph where compilation tasks run concurrently across available CPU cores.""",
    "deep_senior_en": """When architecting a multi-module codebase for an organization with multiple engineering squads, our primary objectives are optimizing build parallelism, isolating blast radiuses, and enforcing team autonomy.
A flat structure where features import one another degenerates into an unmaintainable web of dependencies.
Our architecture enforces a strict tripartite topology: the assembly layer, the feature layer, and the core platform layer.
The feature layer is structured around the API/Implementation pattern.
For example, :feature:payment contains two distinct Gradle subprojects: :feature:payment:api and :feature:payment:impl.
The api module contains solely pure interfaces, such as PaymentLauncher, and immutable navigation arguments, compiling in milliseconds because it has zero UI or data dependencies.
When :feature:cart requires payment functionality, it declares an implementation dependency strictly on :feature:payment:api.
The private implementation details in :feature:payment:impl—including payment gateways, Room database entities, and Compose payment dialogs—remain completely encapsulated behind Kotlin internal modifiers.
The root app module imports both implementations and binds them via Hilt at application start.
Horizontally, core modules are kept strictly domain-agnostic: :core:designsystem holds our visual design tokens, :core:network provides configured Retrofit builders, and :core:common distributes test dispatchers.
This strict structural governance preserves a pure Directed Acyclic Graph, guarantees predictable remote build caching, and allows multiple product squads to ship features in parallel without stepping on one another.""",
    "meta_ar": {
        "id": "MOD-07",
        "questionAr": "صمم هيكلاً متعدد الموديولات (Multi-Module Structure) لتطبيق كبير في بيئة إنتاجية.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصميم هيكل معماري متوازن يجمع بين التقسيم حسب الطبقات والتقسيم حسب الميزات، وحوكمة الموديولات المشتركة، وإدارة واجهات API و DI والتنقل.",
        "concept_ar": "تصميم هيكل متعدد الموديولات للأنظمة الكبيرة يعتمد على المزج المتوازن بين الشرائح العمودية للميزات (Feature Slicing) والطبقات الأفقية للبنية التحتية (Layered Architecture) لتشكيل مخطط غير دائري DAG نقي. يقسم النظام إلى ثلاثة مستويات: موديول app كمركز تجميع وحقن للتبعيات، موديولات الميزات مقسمة إلى موديول عقود عام :api وموديول تنفيذ خاص :impl، وموديولات البنية الأساسية الأفقية المشتركة مثل :core:network و :core:database و :core:designsystem.",
        "walkthrough_ar": """الهيكل المعماري الموصى به للمشاريع الكبيرة ومسارات التبعيات:
```text
app/ (نقطة التجميع وبناء الـ APK وحقن Hilt)
core/
  ├── designsystem/ (الألوان والأزرار ومكونات Compose الموحدة)
  ├── network/      (عميل Retrofit والتوثيق والـ Interceptors)
  ├── database/     (قواعد بيانات Room والـ DAOs)
  └── common/       (أدوات Coroutines والامتدادات العامة)
features/
  ├── checkout/
  │   ├── api/      (واجهات التنقل وعقود الدفع العامة)
  │   └── impl/     (شاشات Compose ومنطق الدفع الداخلي)
  └── catalog/
      ├── api/      (عقود عرض المنتجات)
      └── impl/     (يعتمد فقط على :features:checkout:api للتنقل)
```""",
        "why_it_matters_ar": "يسمح لعشرات المهندسين بالعمل المتزامن دون تعارضات، ويحقق أقصى استفادة من التجميع المتوازي في Gradle، ويحمي استقرار التطبيق بعزل أي عطل أو تغيير داخل موديوله الخاص.",
        "worked_example_ar": "بناء هيكل تطبيق بنكي يضم ميزات `:features:transfer` و `:features:cards`، والتواصل بينهما عبر موديول `:features:transfer:api`، مع تشارك مكونات التصميم عبر `:core:designsystem`.",
        "trade_offs_ar": "نمط تقسيم الميزات إلى :api و :impl يضاعف عدد موديولات الميزات ويتطلب إدارة دقيقة للواجهات، ولكنه يمنح المشروع سرعة بناء خرافية وعزلاً معمارياً يحمي النظام مع نمو الكود لسنوات.",
        "failure_modes_ar": "اعتماد موديولات الميزات على بعضها مباشرة مما يخلق حلقات دائرية، وتضخم موديول core بتحويله لحاوية عشوائية للأكواد غير المصنفة، ووضع كود واجهات أو شاشات داخل موديول الـ app الرئيسي.",
        "production_perspective_ar": "في كبرى الشركات، نستخدم قوالب آلية Module Templates عبر أدوات سطر الأوامر لتوليد أي موديول جديد بالهيكل القياسي وإعدادات الـ Plugins الرسمية بضغطة زر واحدة لضمان الاتساق.",
        "how_to_answer_ar": "ارسم الهيكل ثلاثي المستويات (app، features بتقسيم api/impl، core)، واشرح كيف تتواصل الميزات عبر الـ api فقط، وبين كيف يضمن هذا الهيكل توازي البناء في Gradle واستقلالية الفرق.",
        "talking_points_ar": "نمط API/Impl في موديولات الميزات، دور موديول app كـ Composition Root فقط، وفصل موديولات البنية التحتية الأفقية في core.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نقسم كل ميزة إلى موديولين api و impl بدلاً من موديول واحد؟\"\n  **المرشح:** \"موديول الـ api يحوي واجهات نقية ويتم تجميعه في ثوانٍ؛ عندما تحتاج ميزة أخرى للتواصل معها، تعتمد على الـ api فقط وتظل محمية من إعادة التجميع عند تعديل تفاصيل الـ impl الداخلية.\"\n\n- **المحاور:** \"ما هي محتويات موديول الـ app في هذا التصميم المعماري؟\"\n  **المرشح:** \"يحتوي فقط على كلاس Application، ومكونات Hilt Singleton، وتجميع مسار التنقل الرئيسي Navigation Graph، وربط موديولات الـ impl بالـ APK النهائي دون أي كود تجاري.\"",
        "self_check_ar": "هل رسمت هيكلاً معمارياً متكاملاً يوضح المستويات الثلاثة؟ وهل شرحت بوضوح نمط api/impl للميزات ودور موديول app وموديولات core؟",
        "references_ar": f"- [Guide to Android App Modularization Architecture](https://developer.android.com/topic/modularization/patterns) — دليل الأنماط الهيكلية لتقسيم تطبيقات أندرويد.\n- [Now in Android Architecture Blueprint](https://github.com/android/nowinandroid) — المعمارية المرجعية المعتمدة من فريق أندرويد بجوجل.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الهيكل الإنتاجي المثالي يقسم التطبيق إلى مخطط موجه غير دائري: موديول app في القمة للتجميع وحقن التبعيات، وموديولات الميزات في الوسط مقسمة إلى موديول عقود api عام وموديول impl خاص، وموديولات البنية التحتية الأفقية في الأسفل مثل core:network و core:designsystem. تتواصل الميزات عبر واجهات api فقط لمنع الاقتران وتحقيق أقصى توازٍ في البناء.",
        "best_answer_ar": "يتطلب تصميم هيكل متعدد الموديولات لتطبيق ضخم تحقيق التوازن بين الاستقلالية الوظيفية للفرق والاتساق المعماري للنظام ككل.\n\nنعتمد هيكلاً ثلاثي الطبقات يشكل مخططاً غير دائري DAG نقي. في القمة، يعمل موديول app كنقطة تجميع شاملة Composition Root؛ يقتصر دوره على تهيئة كلاس Application وموديولات حقن التبعيات بـ Hilt وحزم الميزات في ملف الـ APK دون كتابة أي كود للشاشات أو العمليات التجارية.\n\nفي الطبقة الوسطى، نقسم موديولات الميزات عمودياً وفق نمط API/Impl؛ فموديول الدفع مثلاً ينقسم إلى موديول `:features:payment:api` يحتوي على واجهات التنقل والتعاقدات العامة فقط، وموديول `:features:payment:impl` يحتوي على الشاشات والمستودعات والكود الداخلي. وعندما تحتاج ميزة السلة لاستدعاء الدفع، فإنها تستورد موديول api فقط؛ مما يبقي كود impl معزولاً ومحمياً بـ internal. وفي الطبقة السفلى، توفر موديولات core البنية التحتية الأفقية المشتركة مثل شبكات الاتصال وقواعد البيانات والسمات البصرية، مما يضمن أقصى توازٍ في البناء التزايدي وسهولة صيانة لا متناهية.",
        "deep_answer_ar": "في قيادة هندسة المنصات لتطبيقات تضم عشرات الفرق البرمجية، نهدف من تصميم الهيكل المعماري إلى تحقيق ثلاثة أهداف استراتيجية: أقصى سرعة بناء توازي عبر Gradle، كبسلة صارمة تحمي الفرق من التداخل، وتقليص مساحة التأثير Blast Radius لأي تعديل برمجي.\n\nيحقق الهيكل ثلاثي المستويات هذه الأهداف بصرامة؛ ففي قمة المخطط، يعمل موديول app كمنظم تجميع فقط، مما يبقيه خفيفاً ويمنع تحوله إلى كتلة ضخمة يصعب تعديلها. وفي طبقة الميزات، يعد تطبيق نمط API/Implementation نقلة معمارية نوعية؛ حيث يتم تجميع موديول الـ api فائق الخفة في بضع ثوانٍ نظراً لعدم احتوائه على موارد بصرية أو منطق معقد. فعندما يعتمد موديول الكتالوج على موديول الـ api الخاص بالدفع، يستطيع فريق الدفع إعادة كتابة موديول الـ impl بالكامل أو تحديث مكتبات Compose فيه دون أن يتأثر موديول الكتالوج أو يعيد التجميع، مما يحافظ على كاش البناء التزايدي للمشروع بأكمله.\n\nوعلى المستوى الأفقي للبنية الأساسية، نعزل موديول `:core:designsystem` كمصدر وحيد للحقيقة للغة التصميم البصرية المشتركة، بينما يوفر موديول `:core:network` عميل HTTP موحد يدير تجديد الرموز التشفيرية والتثبيت الأمني للشهادات، وموديول `:core:common` لموزعات Coroutines Dispatchers. هذا التنظيم النقي يضمن مخطط تبعيات أحادي الاتجاه وخالياً تماماً من الحلقات الدائرية، ويتيح إضافة ميزات جديدة مستقبلاً بسلاسة وتوسع هندسي لا محدود."
    }
}

# ==========================================
# Runner & Validation
# ==========================================
def validate_words():
    for qid, d in sorted(DATA.items()):
        short_w = len(d["short_en"].split())
        struct_w = len(d["structured_en"].split())
        deep_w = len(d["deep_senior_en"].split())
        assert 35 <= short_w <= 110, f"{qid} short_en {short_w} out of [35, 110]"
        assert 100 <= struct_w <= 280, f"{qid} struct_en {struct_w} out of [100, 280]"
        assert 200 <= deep_w <= 650, f"{qid} deep_en {deep_w} out of [200, 650]"

        q_ar_w = len(d["meta_ar"]["quick_answer_ar"].split())
        b_ar_w = len(d["meta_ar"]["best_answer_ar"].split())
        d_ar_w = len(d["meta_ar"]["deep_answer_ar"].split())
        assert 35 <= q_ar_w <= 110, f"{qid} quick_ar {q_ar_w} out of [35, 110]"
        assert 90 <= b_ar_w <= 280, f"{qid} best_ar {b_ar_w} out of [90, 280]"
        assert 180 <= d_ar_w <= 650, f"{qid} deep_ar {d_ar_w} out of [180, 650]"
        print(f"{qid}: en_s={short_w}, en_st={struct_w}, en_d={deep_w} | ar_q={q_ar_w}, ar_b={b_ar_w}, ar_d={d_ar_w}")
    print("Pre-validation word count checks passed! Updating canonical questions...")

def apply_elevations():
    validate_words()

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"],
            short_en=d["short_en"],
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("mod_01_07", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print("\nAll 7 MOD questions (MOD-01 to MOD-07) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
