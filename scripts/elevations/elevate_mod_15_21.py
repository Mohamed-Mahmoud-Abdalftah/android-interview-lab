#!/usr/bin/env python3
"""
Elevation script for MOD questions: MOD-15 to MOD-21.
Topic: Gradle Modularization & Dependency Boundaries (MOD)
Phase 4, Batch 3
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "تقسيم المشروع لموديولات (Modularization) وحدود التبعيات"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# MOD-15: How do api/implementation influence compilation boundaries and rebuilds?
# ==========================================
DATA["MOD-15"] = {
    "concept_en": """The distinction between Gradle api and implementation configurations governs compilation avoidance and task up-to-date checking at the bytecode level:
- implementation: Hides transitive dependency types from the downstream consumer's compile classpath, placing them exclusively on the runtime classpath. When internal code within an implementation dependency changes without modifying public method signatures, interfaces, or visible fields, Gradle detects that the declaring module's Application Binary Interface (ABI) remains identical. Downstream consumers are marked UP-TO-DATE, completely bypassing recompilation and preserving build cache performance.
- api: Exposes transitive dependency types onto the compile classpath of every downstream consumer. Any modification to an api dependency—even a minor private method change—forces Gradle to invalidate the compile classpath of all dependent modules, triggering cascading recompilation across the entire build graph. Senior architects enforce implementation by default to maintain resilient compilation firewalls.""",
    "walkthrough_en": """Comparing ABI compilation boundaries between implementation and api:
```kotlin
// In :core:network/build.gradle.kts
dependencies {
    // 1. Implementation keeps OkHttp private to :core:network
    implementation(libs.okhttp)
    // 2. Api exposes Retrofit to all consumers of :core:network
    api(libs.retrofit)
}

// In :feature:checkout/build.gradle.kts
dependencies {
    implementation(project(":core:network"))
}

// Compilation result:
// If OkHttp upgrades from 4.11 to 4.12:
// - :core:network recompiles.
// - :feature:checkout ABI is UNCHANGED; its compileKotlin task is UP-TO-DATE!
// If Retrofit interfaces change:
// - :feature:checkout compile classpath is dirty, forcing full recompilation.
```""",
    "short_en": """The implementation configuration creates a strict ABI compilation firewall, keeping dependencies off downstream compile classpaths and shielding consumers from recompilation when internal implementations change. The api configuration transitively exposes dependencies to consumers, causing cascading recompilations across the entire build graph whenever the dependency is modified.""",
    "structured_en": """Understanding how api and implementation influence compilation boundaries is the key to mastering Gradle build performance.
When a module declares a dependency using implementation, Gradle places that library on the module's compile classpath, but hides it from downstream consumers.
This establishes an Application Binary Interface firewall.
When an engineer refactors internal code or upgrades an internal library, Gradle analyzes the generated class signatures.
Because the module's public ABI has not changed, Gradle marks downstream compilation tasks as UP-TO-DATE, skipping compilation entirely.
Conversely, declaring a dependency with api forces Gradle to place that library on the compile classpath of all downstream modules.
Any change to that library marks the compile classpath dirty for every consumer, triggering cascading rebuilds across dozens of modules.
Defaulting to implementation preserves the remote build cache and keeps incremental compilation fast.""",
    "deep_senior_en": """At the compiler level, Gradle's compilation avoidance mechanism relies on ABI hashing to determine whether downstream tasks can be safely bypassed.
When a module compiles, Gradle computes a cryptographic hash of its public ABI, which includes public and protected method signatures, parameter types, return types, and class hierarchies, while ignoring private methods and method body bytecode.
When we use implementation, the dependency is excluded from our consumers' compile classpath.
If we refactor internal algorithms or modify private helper functions inside our module, our public ABI hash remains identical.
When Gradle evaluates downstream modules, it compares their compile classpath hashes against previous build snapshots.
Finding no change, Gradle skips compileKotlin and marks the task UP-TO-DATE.
If we had used api, the dependency would form part of the consumer's compile classpath.
Any change to that dependency, including updating internal transitive dependencies, invalidates the consumer's compile classpath hash, triggering a cascading rebuild that sweeps across the dependency graph.
In enterprise architectures, we treat api declarations as structural debt.
We enforce implementation across all build scripts, promoting to api only when an external type is an unavoidable component of our module's public contract.
We also configure automated linter rules to flag any PR that introduces domain-specific entity names or endpoint paths inside infrastructure modules, preserving platform purity.""",
    "meta_ar": {
        "id": "MOD-15",
        "questionAr": "كيف تؤثر إعدادات api و implementation على حدود التجميع وإعادة بناء المشروع في Gradle؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التحليل العميق لمسار التجميع العابر Transitive Compile Classpath، وعزل واجهة التطبيق الثنائية ABI، وتأثير التغييرات الداخلية مقابل تغييرات التوقيع العام على استهلاك وقت CI وكاش Gradle.",
        "concept_ar": "يحدد الفارق بين api و implementation في Gradle حدود عزل التجميع عبر واجهة التطبيق الثنائية (ABI) وخاصية تجنب التجميع (Compilation Avoidance): يخفي implementation التبعية عن مسار تجميع الموديولات المستهلكة ويحصرها في مسار التشغيل فقط؛ فعند تعديل كود داخلي لا يغير التوقيع العام للموديول، يكتشف Gradle بقاء الـ ABI ثابتاً ويتخطى إعادة تجميع المستهلكين بحالة UP-TO-DATE. بينما يقوم api بتسريب التبعية عابراً لمسار تجميع كافة المستهلكين، مما يجعل أي تعديل فيها يبطل كاش التجميع للمشروع بالكامل ويؤدي لإعادة بناء متسلسلة (Cascading Rebuild).",
        "walkthrough_ar": """تأثير جدار حماية ABI على إعادة التجميع في Gradle:
```kotlin
// في موديول :core:network
dependencies {
    // 1. OkHttp مخفية بـ implementation
    implementation(libs.okhttp)
    // 2. Retrofit مصدرة بـ api
    api(libs.retrofit)
}

// سيناريو التعديل:
// - تعديل دالة خاصة داخل OkHttp: يُعاد تجميع :core:network فقط، وتظل موديولات الميزات محتفظة بحالة UP-TO-DATE!
// - تعديل دالة عامة في Retrofit: تسريب التبعية يجبر Gradle على إعادة تجميع كافة الميزات المعتمدة على الشبكة!
```""",
        "why_it_matters_ar": "يمثل الفارق الجوهري بين بيئة تطوير تنجز التجميع التزايدي في 5 ثوانٍ وبين بيئة تنتظر دقائق مع كل تعديل، حيث يحمي implementation كاش Gradle ويمنع إهدار موارد المعالج في مهام بناء لا لزوم لها.",
        "worked_example_ar": "مقارنة زمن بناء تطبيق يضم 40 موديولاً عند تعديل دالة خاصة داخل موديول تم ربطه بـ implementation (استغرق 3 ثوانٍ) مقابل نفس التعديل والموديول مربوط بـ api (استغرق 48 ثانية لإعادة تجميع 25 موديولاً).",
        "trade_offs_ar": "استخدام implementation يفرض عليك في بعض الأحيان كتابة كود وسيط وتغليف الكائنات لمنع تسريب الأنواع، ولكنه يمنحك سرعة تجميع فائقة وثباتاً معمارياً يقلل أوقات انتظار المهندسين أثناء التطوير اليومي.",
        "failure_modes_ar": "استخدام api بدافع الكسل البرمجي لتمكين الموديولات من رؤية المكتبات دون كتابة إعدادات التبعية، مما يدمر عزل الـ ABI، وتسريب كلاسات طرف ثالث متقلبة إلى كافة شاشات التطبيق.",
        "production_perspective_ar": "في المشروعات الكبرى، نعتمد على أدوات التحليل الآلي للتبعيات في الـ CI للتحقق من أن كافة الموديولات تطبق implementation افتراضياً، مع وضع تنبيهات فورية تمنع دمج أي اعتماد بـ api دون موافقة معمارية.",
        "how_to_answer_ar": "اشرح آلية عمل Compilation Avoidance وبصمة الـ ABI في Gradle، وقارن مسار التجميع Compile Classpath بين الإعدادين، ووضح كيف يمنع implementation ظاهرة Cascading Recompilation.",
        "talking_points_ar": "مفهوم بصمة الـ ABI Hash، الفارق بين Compile Classpath و Runtime Classpath، ودور Compilation Avoidance في تسريع البناء التزايدي.",
        "follow_ups_ar": "- **المحاور:** \"إذا غيرت اسم دالة خاصة private داخل موديول مربوط بـ implementation، هل يتغير الـ ABI Hash؟\"\n  **المرشح:** \"لا؛ لأن الـ ABI يقتصر على الدوال والكلاسات العامة والمحمية فقط، فتبقى البصمة ثابتة ويتخطى Gradle إعادة تجميع المستهلكين تماماً.\"\n\n- **المحاور:** \"ماذا يحدث لو قمت بتغيير نوع البيانات المرتجع لدالة عامة public في موديول مربوط بـ implementation؟\"\n  **المرشح:** \"هنا يتغير الـ ABI العام للموديول؛ فيقوم Gradle تلقائياً بإعادة تجميع كافة الموديولات المعتمدة عليه مباشرة للتحقق من التوافق البرمجي.\"",
        "self_check_ar": "هل شرحت بدقة مفهوم الـ ABI Hash وتجنب التجميع؟ وهل وضحت الفارق على مسار التجميع وتأثيرهما على أداء Gradle Build Cache؟",
        "references_ar": f"- [Gradle Compilation Avoidance](https://docs.gradle.org/current/userguide/java_plugin.html#sec:compile_avoidance) — التوثيق الرسمي لجرادل حول آلية تجنب إعادة التجميع.\n- [Android Performance: Dependency Configurations](https://developer.android.com/topic/modularization) — إرشادات جوجل لأفضل ممارسات إدارة التبعيات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "ينشئ إعداد implementation جدار حماية لعزل واجهة التطبيق الثنائية ABI، حيث يحجب التبعيات عن مسار تجميع المستهلكين ويحميهم من إعادة التجميع عند تعديل الأكواد الداخلية. بينما يسرب api التبعية لمسار تجميع المستهلكين بشكل عابر، مما يتسبب في إعادة تجميع متسلسلة للمشروع بالكامل عند حدوث أي تعديل في التبعية.",
        "best_answer_ar": "يتحكم الاختيار بين api و implementation في آلية تجنب إعادة التجميع Compilation Avoidance وحساب بصمة واجهة التطبيق الثنائية ABI في محرك Gradle.\n\nعند استخدام implementation، يضع Gradle التبعية في مسار تجميع الموديول المعلن فقط، مع إبقائها على مسار التشغيل Runtime Classpath للموديولات المستهلكة. وإذا قام المطور بإعادة هيكلة كود داخلي أو تحديث مكتبة داخلية دون تغيير توقيعات الدوال العامة، يكتشف Gradle أن بصمة الـ ABI للموديول لم تتغير؛ فيتخطى تجميع الموديولات المعتمدة عليه ويمنحها حالة UP-TO-DATE الفورية، مما يوفر أوقاتاً ثمينة أثناء التطوير.\n\nأما عند استخدام api، فإن التبعية تصبح جزءاً ممتداً من مسار تجميع كافة الموديولات المستهلكة في شجرة التبعيات. وأي تعديل طفيف داخل تلك المكتبة يجعل مسار التجميع غير صالح، مما يجبر Gradle على إطلاق موجة تجميع متسلسلة Cascading Recompilation تعيد بناء عشرات الموديولات التابعة وتعطل فاعلية الـ Build Cache للمشروع.",
        "deep_answer_ar": "في التحليل المعماري المتقدم لسرعة بناء مشاريع أندرويد الضخمة، تدور المعركة الهندسية حول تقليص مسار التجميع Compile Classpath والحفاظ على نقاء بصمة الـ ABI Hash.\n\nيعتمد Gradle في فحص المهام التزايدية على حساب تجزئة تشفيرية للواجهة الثنائية للموديول؛ وتتضمن هذه البصمة توقيعات الدوال العامة والمحمية وأنواع المعاملات والوراثة، وتستبعد تماماً محتوى الدوال البرمجية والمتغيرات الخاصة. فعندما نعتمد على implementation، نعزل تفاصيل التنفيذ عن أعين المستهلكين؛ فإذا غيرنا خوارزمية البحث أو قمنا بتحديث مكتبة معالجة JSON داخل موديول البيانات، يظل الـ ABI ثابتاً، مما يتيح لمحرك البناء تخطي مهام compileKotlin للموديولات المستهلكة بنجاح تام.\n\nأما في حال استخدام api، فإن أنواع بيانات المكتبة الخارجية تصبح جزءاً عضوياً من السطح العام للموديول. هذا يعني أن أي تعديل في المكتبة، ولو كان مجرد تصحيح داخلي، يدمر كاش التجميع للموديولات التابعة ويطلق عمليات تجميع متسلسلة تعيد بناء كافة ميزات التطبيق بلا مبرر.\n\nلذلك نطبق في بيئات الإنتاج سياسة صارمة تحظر استخدام api وتعتمد حصرياً على implementation في كافة ملفات Gradle. وفي الحالات النادرة التي يتطلب فيها العقد تصدير نوع بيانات معين، نلجأ لتغليفه بنماذج داخلية Mappers لحماية حدود التجميع، مع وضع اختبارات آلية في مسار CI ترفض أي Pull Request يحاول تسريب التبعيات دون مسوغ معماري قاطع."
    }
}

# ==========================================
# MOD-16: How do you test and publish a reusable Android library/SDK module?
# ==========================================
DATA["MOD-16"] = {
    "concept_en": """Testing and publishing an enterprise-grade Android library or SDK module requires balancing API stability, packaging standards, and consumer developer experience:
- Maven Publishing: Configuring the maven-publish Gradle plugin to export release AAR artifacts, POM dependencies, and sources JARs (via publishing { singleVariant("release") { withSourcesJar() } }).
- Consumer ProGuard Rules: Declaring consumerProguardFiles("consumer-rules.pro") so consuming applications automatically inherit necessary keep rules for public API symbols and serialization models without manual consumer configuration.
- Binary Compatibility Validation: Enforcing strict backward compatibility using JetBrains' Binary Compatibility Validator (BCV) plugin, which tracks public API dumps in Git and fails CI if a breaking signature change is introduced.
- Multi-Tiered Testing: Executing local JVM unit tests, headless Compose screenshot tests (using Paparazzi or Roborazzi), and instrumented integration tests against an isolated :sample application module.""",
    "walkthrough_en": """Configuring Maven publishing, consumer rules, and binary validation for an SDK:
```kotlin
// In :library:payment-sdk/build.gradle.kts
plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    id("maven-publish")
    alias(libs.plugins.binary.compatibility.validator)
}

android {
    namespace = "com.company.paymentsdk"
    defaultConfig {
        consumerProguardFiles("consumer-rules.pro")
    }
    publishing {
        singleVariant("release") { withSourcesJar() }
    }
}

publishing {
    publications {
        register<MavenPublication>("release") {
            afterEvaluate { from(components["release"]) }
            groupId = "com.company.sdk"
            artifactId = "payment"
            version = "1.4.0"
        }
    }
}
```""",
    "short_en": """Publishing an Android library requires configuring the maven-publish plugin to generate AAR and sources artifacts, embedding consumerProguardFiles to protect public API symbols automatically in consuming apps, and using the Binary Compatibility Validator to prevent breaking changes. Testing combines JVM unit tests, screenshot tests, and sample app integration suites.""",
    "structured_en": """Building and publishing a reusable Android library module requires distinct engineering practices compared to building an application.
First, we configure the maven-publish Gradle plugin inside the library module, specifying Maven coordinates, POM metadata, and publishing singleVariant release with attached sources JARs.
Second, we define consumer ProGuard rules using consumerProguardFiles.
These rules are automatically bundled inside the exported AAR, instructing the consumer's R8 shrinker to preserve our public API signatures without requiring developers to write custom rules.
Third, we enforce binary compatibility using JetBrains' Binary Compatibility Validator plugin.
This tool dumps public API signatures into a tracked text file in Git, failing CI builds if an engineer accidentally alters or removes a public method signature without a major version bump.
Finally, testing combines JVM unit tests, Paparazzi screenshot tests for UI components, and an isolated sample application that validates real-world integration.""",
    "deep_senior_en": """Engineering an internal or commercial Android SDK demands treating your public API surface as an immutable contract.
Unlike an application where refactoring is internal, breaking an SDK's Application Binary Interface breaks builds for external partner teams.
Our publishing architecture centers on three robust pillars: deterministic packaging, automated consumer protection, and strict ABI governance.
In build configuration, we utilize the modern android.publishing DSL with singleVariant release and withSourcesJar, exporting release components via maven-publish to our internal Nexus or Artifactory repository.
We embed consumer-rules.pro using consumerProguardFiles.
This ensures that when consumer apps run R8, our public entry points, reflective serializers, and native JNI bindings are preserved automatically, preventing catastrophic ClassNotFoundException crashes in production client apps.
To enforce semantic versioning programmatically, we integrate JetBrains' Binary Compatibility Validator plugin into our CI pipeline.
The tool maintains an api/payment-sdk.api dump in version control.
If a pull request deletes a public parameter, changes a return type, or alters nullability without an explicit API dump update, the build fails immediately.
Our verification pipeline runs JVM unit tests for business logic, Roborazzi screenshot verification for custom UI widgets, and automated instrumented tests running inside a companion :sample app module, guaranteeing that every published AAR is production-tested prior to release.""",
    "meta_ar": {
        "id": "MOD-16",
        "questionAr": "كيف تختبر وتنشر موديول مكتبة (Android Library / SDK) قابل لإعادة الاستخدام؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "أفضل ممارسات هندسة ونشر حزم AAR، وتكوين maven-publish وإدارة POM و AAR metadata، وفصل واجهات المستهلك عن تفاصيل التنفيذ بـ Consumer Proguard Rules، وضمان التوافق الثنائي بـ Binary Compatibility Validator.",
        "concept_ar": "تتطلب هندسة ونشر مكتبة أو SDK لأندرويد معايير صارمة تضمن استقرار الواجهات وسهولة الاستخدام: إعداد إضافة maven-publish لإنتاج حزمة AAR مع ملفات المصدر Sources JAR والبيانات الوصفية POM، وتضمين قواعد ProGuard للمستهلكين عبر consumerProguardFiles لحماية الرموز العامة تلقائياً عند تجميع تطبيق العميل، وفرض التوافق الثنائي للأكواد عبر أداة Binary Compatibility Validator (BCV) لمنع كسر الـ ABI دون ترقية الإصدار الرئيسي، وبناء منظومة اختبار متكاملة تشمل اختبارات JVM واختبارات لقطات الشاشة وتطبيقاً نموذجياً :sample.",
        "walkthrough_ar": """إعداد نشر المكتبة وتضمين قواعد حماية المستهلك والتحقق الثنائي:
```kotlin
// في build.gradle.kts للمكتبة
plugins {
    id("com.android.library")
    id("maven-publish")
    id("org.jetbrains.kotlinx.binary-compatibility-validator")
}
android {
    defaultConfig {
        // تضمين القواعد داخل حزمة الـ AAR تلقائياً للمستهلكين
        consumerProguardFiles("consumer-rules.pro")
    }
    publishing {
        singleVariant("release") { withSourcesJar() }
    }
}
// أمر التحقق من عدم كسر التوافق الثنائي قبل النشر:
// ./gradlew apiCheck
```""",
        "why_it_matters_ar": "يضمن حماية المطورين المستهلكين للمكتبة من الانهيارات المفاجئة بعد تفعيل R8، ويمنع كسر التوافق البرمجي والتحديثات الكارثية، ويوفر تجربة تكامل سلسة وموثوقة تعزز انتشار المكتبة واعتمادها.",
        "worked_example_ar": "إعداد مسار CI/CD لنشر حزمة SDK للمدفوعات في مستودع Maven داخلي، مع فحص التوافق الثنائي بـ BCV وتشغيل اختبارات Paparazzi للتحقق من سلامة المكونات البصرية.",
        "trade_offs_ar": "تطبيق قواعد التوافق الثنائي الصارمة يحد من حرية التعديل السريع على الكود ويتطلب التزاماً دقيقاً بالترقيم الدلالي Semantic Versioning، ولكنه يحمي آلاف التطبيقات المعتمدة على المكتبة من الانهيار.",
        "failure_modes_ar": "نسيان ملف consumerProguardFiles مما يتسبب في حذف كلاسات المكتبة عبر R8 في تطبيق المستهلك، وكسر الـ ABI بتغيير توقيع دالة عامة في تحديث فرعي، وعدم توفير موديول تجريبي :sample لاختبار التكامل الواقعي.",
        "production_perspective_ar": "في كبرى شركات التكنولوجيا، يُحظر نشر أي إصدار جديد من الـ SDK دون تشغيل مهمة apiCheck في الـ CI للتحقق من تطابق ملف api dump مع قواعد Semantic Versioning المعتمدة.",
        "how_to_answer_ar": "اشرح الخطوات الأربع للنشر المحترف: إعداد maven-publish وتوليد الـ Sources، دور consumerProguardFiles في حماية المستهلك، التحقق الثنائي عبر BCV، ومنظومة الاختبار الشاملة مع موديول :sample.",
        "talking_points_ar": "أهمية consumerProguardFiles في حزم AAR، كيفية عمل أداة Binary Compatibility Validator، واستراتيجيات اختبار المكتبات باستخدام Paparazzi و Sample Apps.",
        "follow_ups_ar": "- **المحاور:** \"ما فائدة consumerProguardFiles للمطور الذي يستخدم مكتبتك؟\"\n  **المرشح:** \"تُدمج القواعد داخل ملف الـ AAR؛ فيقوم R8 بتطبيقها تلقائياً أثناء بناء تطبيق العميل لحماية كلاسات ونماذج الـ SDK دون أن يحتاج المطور لكتابتها يدوياً.\"\n\n- **المحاور:** \"كيف تضمن عدم كسر الكود القديم للمستهلكين عند إطلاق ميزة جديدة في المكتبة؟\"\n  **المرشح:** \"باستخدام أداة Binary Compatibility Validator التي تفحص الـ Public API dump في الـ CI وترفض أي تغيير يكسر التوافق الثنائي دون رفع رقم الإصدار الرئيسي Major Version.\"",
        "self_check_ar": "هل ذكرت maven-publish و consumerProguardFiles؟ وهل شرحت دور أداة Binary Compatibility Validator ومنظومة الاختبار وتطبيق sample؟",
        "references_ar": f"- [Android Library Publishing](https://developer.android.com/build/publish-library) — التوثيق الرسمي لنشر مكتبات أندرويد عبر Gradle.\n- [Kotlin Binary Compatibility Validator](https://github.com/Kotlin/binary-compatibility-validator) — أداة جيتبرينز الرسمية لحماية التوافق الثنائي للمكتبات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يتطلب نشر واختبار مكتبة أندرويد إعداد إضافة maven-publish لتوليد حزم AAR وملفات المصدر، وتضمين consumerProguardFiles لحماية الرموز العامة تلقائياً عند تجميع تطبيق المستهلك، واستخدام أداة Binary Compatibility Validator لمنع كسر الواجهات الثنائية. وتتكامل الاختبارات بين فحص الـ JVM واختبارات لقطات الشاشة وتطبيق تجريبي مستقل :sample.",
        "best_answer_ar": "بناء ونشر مكتبة أو SDK في أندرويد يختلف جذرياً عن بناء التطبيقات العادية؛ حيث تصبح الواجهة البرمجية العامة عقداً ثابتاً لا يجوز الإخلال به.\n\nنبدأ بإعداد إضافة maven-publish الرسمية لتصدير حزمة الـ AAR مع ملفات المصدر Sources JAR والبيانات الوصفية POM إلى مستودع Maven الداخلي أو السحابي. ونحرص بشدة على تضمين ملف consumer-rules.pro عبر خاصية consumerProguardFiles داخل إعدادات الأندرويد؛ مما يضمن أن تطبيق العميل عندما يقوم بتشغيل R8 لحذف الأكواد المهملة، سيحتفظ تلقائياً بكلاسات وواجهات المكتبة العامة دون أن يضطر المطور لكتابة قواعد استثناء يدوية.\n\nولحماية التوافق البرمجي، ندمج أداة Binary Compatibility Validator من جيتبرينز في مسار الـ CI؛ حيث تسجل الأداة كافة التوقيعات العامة في ملف نصي وتفشل أي عملية دمج تلغي دالة عامة أو تغير معاملاتها دون ترقية رقم الإصدار الرئيسي وفق قواعد Semantic Versioning. ونختبر المكتبة عبر اختبارات JVM سريعة، واختبارات لقطات شاشة للمكونات البصرية بـ Paparazzi، وتطبيق تجريبي :sample يحاكي دمج المكتبة ميدانياً.",
        "deep_answer_ar": "في قيادة هندسة المنصات وتطوير مكتبات الـ SDK، نعتبر كسر واجهة التطبيق الثنائية ABI للمكتبة خطأ تشغيلياً لا يغتفر؛ لأنه يتسبب في انهيار تطبيقات الشركاء بمجرد تحديث رقم الإصدار.\n\nتبدأ المعمارية الاحترافية بضبط مسار التجميع عبر دمج أداة Binary Compatibility Validator داخل مسار الـ CI. تحفظ الأداة تفريغاً دقيقاً لكافة الكلاسات والدوال العامة في ملف api dump مراقب في Git؛ فإذا قام مهندس بحذف دالة، أو تغيير قيمة افتراضية، أو تعديل إمكانية قبول القيمة الخالية Nullability، يرفض مسار البناء الـ Pull Request فوراً ما لم يتم اعتماد تغيير الإصدار الرئيسي وفق معايير الترقيم الدلالي SemVer.\n\nوعلى صعيد حماية المستهلكين، نتصدى لمشاكل R8 عبر إرفاق ملف consumerProguardFiles داخل حزمة AAR المصدرة. هذا التضمين يحمي كلاسات الـ SDK العامة والواجهات التفاعلية ونماذج البيانات من الحذف أو التشويش المشوه عند بناء تطبيق العميل النهائي، مما يمنع حدوث أخطاء ClassNotFoundException الكارثية وقت التشغيل.\n\nكما نبني منظومة اختبارات ثلاثية الطبقات: اختبارات JVM سريعة لكافة الخوارزميات، واختبارات لقطات الشاشة عبر مكتبة Roborazzi لتوثيق اتساق المكونات البصرية، وموديول تطبيق تجريبي :sample ينفذ استدعاءات حقيقية لكافة سيناريوهات الـ SDK، مما يضمن أن كل ملف AAR يتم رفعه لمستودع Nexus هو منتج برمجي محصن ومختبر وجاهز للاستخدام الفوري."
    }
}

# ==========================================
# MOD-17: When is a new feature module justified, and when is it unnecessary complexity?
# ==========================================
DATA["MOD-17"] = {
    "concept_en": """The architectural decision to extract a new Gradle feature module requires weighing concrete productivity benefits against build system overhead and organizational friction:
- Justified When:
  1. Autonomous Squad Ownership: A dedicated engineering squad owns the domain slice and release lifecycle independently.
  2. Large, Cohesive Bounded Context: The feature contains significant domain logic, data models, ViewModels, and screens (e.g., :feature:checkout, :feature:streaming) that benefit from parallel compilation and build caching.
  3. Dynamic Delivery Candidate: The capability is heavy, optional, or regional, qualifying for Play Feature Delivery on-demand downloading.
  4. Strict Compliance Isolation: Segregating sensitive regulatory logic (PCI-DSS payment vaults, HIPAA patient records) into an isolated boundary.
- Unnecessary Complexity (Over-Modularization) When:
  1. Trivial Functionality: Static or small screens (e.g., "About App", "Terms of Service") with two classes and no distinct business logic.
  2. Tight Domain Coupling: Features that constantly change together in the same PRs, indicating an artificial split.
  3. Excessive Configuration Penalty: Creating hundreds of tiny modules balloons Gradle configuration time and complicates navigation without delivering parallel compilation returns. Package-by-feature within an existing module is often vastly superior.""",
    "walkthrough_en": """Evaluating feature extraction criteria using an architectural decision matrix:
```kotlin
// ❌ UNJUSTIFIED EXTRACTION: 2 classes in its own Gradle module!
// :feature:about (Contains only AboutActivity.kt and a static string)
// Result: Adds 500ms to Gradle configuration time for zero build cache benefit.

// ✅ JUSTIFIED EXTRACTION: Autonomous bounded context with dedicated logic
// :feature:kyc:api  (KycNavigator, KycStatusContract)
// :feature:kyc:impl (DocumentCaptureScreen, BiometricVerification, KycRepository)
// Owned by Compliance Squad, changes independently, benefits from parallel compilation.
```""",
    "short_en": """A new feature module is justified when an independent squad owns the feature, the domain logic is substantial enough to benefit from parallel compilation and caching, or the capability qualifies for dynamic delivery or compliance isolation. It is unnecessary complexity for trivial screens, tightly coupled flows, or when the Gradle configuration penalty outweighs build gains.""",
    "structured_en": """Deciding when to create a new feature module requires evaluating both build system metrics and team organizational dynamics.
A new feature module is fully justified when an independent engineering squad owns the domain slice and needs to ship updates without merge conflicts.
It is also justified when the feature contains substantial domain logic, private database tables, and UI state machines, allowing Gradle to compile it in parallel and cache its outputs.
Capabilities that qualify for on-demand downloading through Play Feature Delivery or require strict compliance isolation also warrant dedicated modules.
Conversely, creating a module is unnecessary complexity when dealing with trivial screens like an About page or Terms of Service.
If two features constantly change together in the same pull requests, splitting them creates artificial friction.
Over-modularization inflates Gradle configuration time during project syncs and adds needless navigation indirection.""",
    "deep_senior_en": """In enterprise system design, modularization is not a virtue in itself; it is a mechanical trade-off between parallel compilation and configuration overhead.
Every Gradle subproject incurs a fixed tax: project evaluation overhead in the configuration phase, memory footprint in the Gradle daemon, extra IDE indexing tasks, and navigation contract maintenance.
If a proposed module contains only a few simple screens and a repository, the configuration tax and cognitive friction easily outweigh any parallel compilation dividend.
A new feature module is justified only when it fulfills three objective architectural criteria.
First, organizational autonomy: an independent product squad owns the domain boundary, enabling them to work with isolated git histories and clear CODEOWNERS definitions.
Second, substantial computational weight: the module contains dozens of classes, custom Compose layouts, and domain use cases.
Here, Gradle's parallel worker executors and remote build cache deliver massive speedups because the feature compiles independently while neighboring squads work on other modules.
Third, operational lifecycle divergence: the feature targets dynamic feature delivery or requires compliance sandboxing, such as isolating credit card data under PCI-DSS controls.
If these criteria are absent, senior architects mandate package-by-feature organization inside an existing module.
Grouping files into cohesive packages provides eighty percent of encapsulation benefits without paying a single second of Gradle configuration penalty.""",
    "meta_ar": {
        "id": "MOD-17",
        "questionAr": "متى يكون إنشاء موديول ميزة جديد مبرراً، ومتى يُعد تعقيداً هندسياً زائداً؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تقييم الجدوى الاقتصادية والمعمارية لإنشاء موديول جديد، والموازنة بين استقلالية الفرق وزمن تهيئة Gradle، وحساب التكلفة الإضافية في عقود التنقل والـ DI.",
        "concept_ar": "القرار المعماري لإنشاء موديول ميزة (Feature Module) جديد يخضع لحسابات الجدوى الهندسية وموازنة سرعة التجميع المتوازي مقابل تكلفة التهيئة (Configuration Tax): يكون الموديول مبرراً عند وجود فريق برمجي مستقل يمتلك الميزة، أو احتواء الميزة على منطق أعمال وشاشات ضخمة تستفيد من التجميع المتوازي والـ Build Cache، أو كونها ميزة مؤهلة للتنزيل عند الطلب كـ Dynamic Feature، أو لمتطلبات عزل أمني صارم. ويكون تعقيداً هندسياً زائداً عند تقسيم شاشات بسيطة وثابتة كصفحة 'عن التطبيق'، أو عند تشابك ميزتين تتغيران معاً باستمرار، حيث يفضل الاكتفاء بالتقسيم بالمجلدات (Package-by-Feature).",
        "walkthrough_ar": """مصفوفة القرار المعماري لإنشاء الموديول مقابل التقسيم بالمجلدات:
```kotlin
// ❌ تعقيد زائد: موديول كامل لشاشة ثابتة من كلاسين فقط!
// :feature:about -> يرفع زمن تهيئة Gradle دون أي استفادة حقيقية من الكاش.
// الحل الأفضل: مجلد package داخل موديول الإعدادات القائم :feature:settings

// ✅ موديول مبرر تماماً: ميزة مستقلة ومعقدة يمتلكها فريق مخصص
// :feature:onboarding -> يضم 8 شاشات، تحقق بيومتري، تواصل مع السيرفر،
// ويستفيد من التجميع المتوازي أثناء تطوير باقي أجزاء التطبيق.
```""",
        "why_it_matters_ar": "يمنع الوقوع في فخ الإفراط في التقسيم (Over-modularization) الذي يبطئ مزامنة المشروع في أندرويد ستوديو، ويحافظ على التوازن الصحي بين استقلالية الفرق البرمجية وسرعة البناء الإجمالية.",
        "worked_example_ar": "تقييم مقترح لإنشاء موديول لشاشة سياسة الخصوصية ورفضه والاكتفاء بمجلد، مقابل الموافقة على إنشاء موديول مستقل لميزة المحادثة الفورية Chat مع فريق مستقل ومكتبات ثقيلة.",
        "trade_offs_ar": "إنشاء موديول مبرر يسرع التجميع التزايدي ويعزل الكود ولكنه يضيف كود ربط وإعدادات بناء، بينما الامتناع عن الموديولات غير المبررة يحمي زمن تهيئة Gradle ويبقي المشروع بسيطاً وسهل الصيانة.",
        "failure_modes_ar": "إنشاء مئات الموديولات الدقيقة المجهرية Micro-modules مما يرفع زمن الـ Configuration لعدة دقائق، وفصل ميزتين مرتبطتين بشدة مما يجبر المطور على تعديل موديولين في كل PR.",
        "production_perspective_ar": "في الشركات الكبرى، نحدد معايير واضحة في دليل المعمارية؛ فلا يُقبل طلب إنشاء موديول جديد إلا إذا أثبت الفريق وجود أكثر من 15 كلاس برمجي أو الحاجة لـ Dynamic Delivery أو ملكية فريق منفصل.",
        "how_to_answer_ar": "قسم الإجابة لقسمين واضحين: متى يكون الموديول مبرراً (فريق مستقل، حجم كود كبير، Dynamic Delivery، عزل أمني)، ومتى يكون تعقيداً زائداً (شاشات بسيطة، ارتباط دائم، بطء تهيئة Gradle).",
        "talking_points_ar": "ضريبة تهيئة الموديول Configuration Tax في Gradle، ظاهرة Over-modularization، والبديل العملي Package-by-Feature للشاشات الصغيرة.",
        "follow_ups_ar": "- **المحاور:** \"لماذا قد يتسبب وجود مئات الموديولات الصغيرة في بطء بيئة التطوير؟\"\n  **المرشح:** \"لأن Gradle يقوم بمرحلة Evaluation و Configuration لكل موديول على حدة أثناء المزامنة، وتستهلك مساحة الذاكرة في الـ Daemon، وتزيد من زمن الفهرسة في Android Studio.\"\n\n- **المحاور:** \"ما هو البديل الهندسي المناسب بدلاً من إنشاء موديول لشاشة بسيطة؟\"\n  **المرشح:** \"استخدام أسلوب Package-by-Feature بوضع الشاشة داخل مجلد منظم في أقرب موديول ميزات ذي صلة، مما يعطي كبسلة منطقية دون أي ضريبة في أداء البناء.\"",
        "self_check_ar": "هل حددت المعايير الموضوعية لإنشاء الموديول؟ وهل بينت مخاطر الإفراط في التقسيم وتأثيره على زمن تهيئة Gradle والبدائل المناسبة؟",
        "references_ar": f"- [Android Modularization: When to Modularize](https://developer.android.com/topic/modularization) — إرشادات جوجل لتقييم جدوى تقسيم الموديولات.\n- [Gradle Configuration Time Optimization](https://docs.gradle.org/current/userguide/performance.html) — توثيق جرادل لتحسين زمن التهيئة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يكون موديول الميزة مبرراً عندما يمتلكه فريق مستقل، أو يحتوي على منطق وشاشات ضخمة تستفيد من التجميع المتوازي والكاش، أو للتسليم الديناميكي والعزل الأمني. ويُعد تعقيداً زائداً للشاشات البسيطة الثابتة، أو للميزات شديدة الترابط التي تتغير معاً دوماً، حيث يتفوق التقسيم بالمجلدات Package-by-Feature دون إبطاء Gradle.",
        "best_answer_ar": "إنشاء موديول جديد ليس هدفاً بحد ذاته، بل هو قرار معماري يقوم على موازنة مكاسب التجميع المتوازي واستقلالية الفرق مقابل ضريبة تهيئة Gradle وتعقيد التنسيق.\n\nيكون موديول الميزة مبرراً ومطلوباً في أربعة سيناريوهات رئيسية: أولاً، عندما تمتلك الميزة فرقة عمل برمجية مستقلة تحتاج للعمل وإطلاق التحديثات بحرية دون نزاعات دمج؛ ثانياً، عندما تكون الميزة كبيرة وتضم منطق أعمال وشاشات وViewModels معقدة تستفيد فعلياً من ميزة التجميع المتوازي وكاش البناء؛ ثالثاً، عندما تكون الميزة مرشحة للتنزيل عند الطلب كـ Dynamic Feature لتقليص حجم التطبيق؛ ورابعاً، لمتطلبات العزل الأمني المشدد كعزل شاشات الدفع الممتثلة لـ PCI-DSS.\n\nفي المقابل، يتحول الموديول إلى تعقيد هندسي ضار عند الإفراط في التقسيم لإنشاء موديولات لشاشات هامشية مثل شاشة 'سياسة الخصوصية' أو 'عن التطبيق'؛ فكل موديول يستهلك وقتاً إضافياً في مرحلة Configuration Phase لجرادل ويبطئ المزامنة في أندرويد ستوديو. وفي هذه الحالات، يعتبر تنظيم الملفات داخل مجلدات Package-by-feature داخل أقرب موديول خياراً أفضل بكثير يجمع بين الترتيب وسرعة البناء.",
        "deep_answer_ar": "في قيادة هندسة المنصات لتطبيقات أندرويد الكبرى، ننظر إلى الموديول كوحدة تكلفة وفائدة؛ فكل موديول Gradle إضافي يفرض ضريبة إجبارية تتمثل في زمن التقييم أثناء مرحلة Configuration Phase، واستهلاك ذاكرة الـ Gradle Daemon، وتكاليف صيانة مسارات التنقل وحقن التبعيات.\n\nإذا كان الموديول المقترح يحتوي على كلاسين وشاشة بسيطة، فإن تكلفة صيانته وبطء مزامنته تفوق بمراحل أي استفادة وهمية من التجميع المتوازي. لذلك نلزم الفرق بتقديم مبرر معماري يستوفي شروط العزل الحقيقية: استقلالية الملكية البرمجية لفريق محدد، أو الحجم الكودي الثقيل الذي يحقق وفرة زمنية ملموسة عند تخطي تجميعه عبر الـ Build Cache، أو التباين في دورة حياة التوزيع كالميزات الديناميكية.\n\nوعندما تتكامل ميزتان وظيفياً وتتغيران معاً في نفس الـ Pull Requests باستمرار، فإن فصلهما لموديولين مستقلين هو خطأ معماري يخلق احتكاكاً بلا فائدة؛ والأصح هو دمجهما في موديول واحد عالي التماسك. أما للشاشات والميزات الثانوية، فإننا نعتمد سياسة Package-by-feature داخل موديولات قائمة؛ حيث نحصل على ثمانين بالمئة من فوائد الكبسلة والتنظيم المعماري دون أن ندفع ثانية واحدة من وقت بناء جرادل.\n\nولحسم هذه القرارات بشكل علمي وموضوعي، نعتمد على أدوات قياس الأداء مثل Gradle Profiler لمراقبة تأثير كل موديول جديد على سرعة المزامنة والتجميع التزايدي في أجهزة المطورين، مع دمج الموديولات المجهرية متى أثبتت الأرقام أنها تستهلك وقتاً في التهيئة يفوق ما توفره في التجميع، مما يحفظ كفاءة بيئة العمل البرمجية واستقرارها."
    }
}

# ==========================================
# MOD-18: A shared model change forces recompilation of many modules. How would you shrink the impact?
# ==========================================
DATA["MOD-18"] = {
    "concept_en": """When a monolithic shared data model (such as a generic User or Account entity) changes, it acts as a compilation bottleneck that invalidates compile classpaths and forces cascading recompilations across dozens of dependent feature modules. Shrinking this blast radius requires applying structural decoupling techniques:
1. Bounded Context Domain Slicing: Decomposing the "God Model" into cohesive, feature-scoped value objects (e.g., splitting a 50-field User into UserIdentity for auth, UserShippingAddress for checkout, and UserFinancialProfile for billing).
2. Interface Segregation: Exposing focused, read-only interface contracts rather than concrete models, so adding private fields to an implementation does not alter the consumer's ABI.
3. Anti-Corruption Layers (ACL) & Local Mappers: Feature modules define their own internal UI/Domain representations, mapping the external shared model at their ingestion boundary. Internal feature logic never depends directly on the shared model.
4. ABI-Safe Default Parameters: In Kotlin, adding fields with default arguments preserves constructor compatibility, preventing downstream source breaking.""",
    "walkthrough_en": """Slicing a bloated shared model and using local mappers to protect compilation boundaries:
```kotlin
// ❌ MONOLITHIC SHARED MODEL (:core:model)
// Changing one field forces recompilation of 30 feature modules!
// data class User(val id: String, val name: String, val email: String, val creditScore: Int, val address: String, ...)

// ✅ BOUNDED CONTEXT SLICING & LOCAL MAPPING
// 1. :core:model exports minimal, stable identity contract
data class UserIdentifier(val id: String, val username: String)

// 2. :feature:checkout defines its OWN local model with only what it needs
internal data class CheckoutCustomer(val id: String, val shippingAddress: String)

// 3. Local Mapper converts at boundary; changes to financial fields NEVER recompile checkout!
internal fun UserProfileDto.toCheckoutCustomer() = CheckoutCustomer(
    id = this.id,
    shippingAddress = this.defaultAddress
)
```""",
    "short_en": """To shrink the recompilation impact of a shared model change, decompose monolithic data models into focused, bounded-context domain slices. Have features depend on read-only interfaces or define local internal models mapped at the boundary through an Anti-Corruption Layer, isolating feature internals from changes to shared infrastructure models.""",
    "structured_en": """When a widely shared data model changes, it triggers cascading recompilations across the entire multi-module dependency graph.
To shrink this blast radius, we eliminate monolithic God Models by slicing them into focused, bounded-context entities.
Instead of a single User class with fifty fields consumed by every module, we create targeted models like UserIdentity for authentication and ShippingAddress for checkout.
Features only import the lightweight slice relevant to their business domain.
Furthermore, feature modules should establish an Anti-Corruption Layer by defining internal domain representations.
The feature maps the incoming shared model into its internal representation at the repository boundary.
If a field is added, modified, or removed in the shared model, edits are confined to that single boundary mapper.
The feature's ViewModels, Compose screens, and internal tests remain completely insulated from recompilation.""",
    "deep_senior_en": """The 'God Model' is one of the most insidious architectural anti-patterns in multi-module Android systems.
When a shared entity like User, Order, or Transaction sits in a foundational core module and accumulates fields from multiple teams, it acts as a massive compilation dependency bottleneck.
Every time an engineer adds a field to support a profile screen experiment, Gradle's ABI hashing detects a change in the core module's bytecode signatures, invalidating the compile classpath for twenty downstream feature modules.
We resolve this systematically by applying Domain-Driven Design bounded contexts and interface segregation.
First, we slice the bloated entity into lean, role-specific value objects.
A checkout feature has no business knowing a user's credit score or notification preferences; it requires solely a ShippingContact and a PaymentBillingAddress.
Second, we enforce an Anti-Corruption Layer at feature module boundaries.
Feature modules maintain their own internal, immutable domain models.
The feature repository receives data from the shared network or database layer and maps it immediately into internal feature models using extension functions hidden behind internal visibility.
Consequently, when the shared backend DTO or core model changes, the blast radius is strictly confined to that single mapper function.
The feature's domain use cases, ViewModels, and UI layouts remain untouched, preserving the Gradle build cache and shielding engineering squads from cross-team recompilation cascades.""",
    "meta_ar": {
        "id": "MOD-18",
        "questionAr": "تعديل في نموذج بيانات مشترك يتسبب في إعادة تجميع موديولات كثيرة، كيف تقلص نطاق هذا التأثير؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تقنيات تقليص مساحة التأثير (Blast Radius Reduction) لنماذج البيانات المشتركة، واستخدام كائنات القيمة المجزأة، وفصل واجهات القراءة عن التعديل، وتطبيق نمط Anti-Corruption Layer (ACL).",
        "concept_ar": "عندما يتضخم كائن بيانات مشترك (God Model) مثل User أو Order ويستورده عدد كبير من الموديولات، فإن أي تعديل طفيف فيه يغير بصمة الـ ABI ويبطل كاش البناء لكافة الموديولات المعتمدة عليه. يكمن الحل المعماري في تقليص مساحة التأثير (Blast Radius): تجزئة الكائن الضخم إلى كائنات قيمة مجزأة حسب سياق الاستخدام (Bounded Contexts)، واستخدام واجهات قراءة مخصصة (Interface Segregation)، وتطبيق نمط طبقة منع الفساد (Anti-Corruption Layer) عبر إنشاء نماذج بيانات داخلية في كل موديول ميزة وتحويل الكائن المشترك عند حدود الموديول فقط.",
        "walkthrough_ar": """تجزئة الكائن المشترك واستخدام محولات داخلية لحماية حدود الموديول:
```kotlin
// ❌ الكائن المتضخم في :core:model يكسر كاش 20 موديولاً عند أي تعديل!
// data class User(val id: String, val name: String, val address: String, val creditScore: Int, ...)

// ✅ الحل: تجزئة الكائن بحسب سياق الاستخدام في موديول مستقل
data class UserIdentity(val id: String, val name: String) // لموديول الحسابات
data class ShippingDestination(val address: String)      // لموديول الشحن

// داخل موديول الشحن: نموذج داخلي محمي بـ internal ومحول عند الحدود
internal data class LocalOrderAddress(val fullAddress: String)

internal fun ShippingDestination.toLocal() = LocalOrderAddress(this.address)
```""",
        "why_it_matters_ar": "يحمي أداء البناء التزايدي في المشاريع الكبيرة، ويمنع تعطيل المطورين عند قيام فريق آخر بتعديل حقل في كائن مشترك، ويحافظ على استقلالية كل ميزة ونقاء منطقها البرمجي الداخلي.",
        "worked_example_ar": "إعادة هيكلة كائن `Customer` الذي يحتوي على 40 حقلاً وتقسيمه إلى `CustomerAuth` و `CustomerBilling`، وتطبيق محولات محلية في موديول الفواتير، مما عزل كاش الموديول تماماً عن تعديلات بيانات الحساب الشخصي.",
        "trade_offs_ar": "تجزئة النماذج واستخدام المحولات المحلية يتطلب كتابة كود وسيط Mappers وزيادة في عدد كلاسات البيانات، ولكنه يقضي تماماً على التجميع المتسلسل ويوفر ساعات من أوقات البناء الضائعة.",
        "failure_modes_ar": "إنشاء كائن مشترك ضخم يحتوي على كافة خصائص النظام وتمريره في كل مكان، والاعتماد المباشر على نماذج الخادم DTOs داخل شاشات Compose، والتعديل المستمر في كائنات الطبقات الدنيا.",
        "production_perspective_ar": "في الفرق الكبرى، نمنع استخدام الكلاسات التي تتجاوز 10 خصائص في الموديولات المشتركة، ونلزم موديولات الميزات بتحويل أي كائن مشترك إلى كائن Domain داخلي فور دخوله حدود الموديول.",
        "how_to_answer_ar": "ابدأ بشرح سبب المشكلة (تغير الـ ABI في موديول قاعدي يبطل كاش المستهلكين)، ثم اشرح الحلول الثلاثة: تجزئة الكائن بحسب سياق الاستخدام Bounded Contexts، واجهات القراءة، والمحولات المحلية ACL.",
        "talking_points_ar": "مخاطر كائنات God Models على سرعة البناء، مبدأ Bounded Context في التصميم الموجه بالمجال DDD، ونمط Anti-Corruption Layer لعزل الموديولات.",
        "follow_ups_ar": "- **المحاور:** \"كيف يحمي استخدام كائن داخلي داخل موديول الميزة من إعادة التجميع؟\"\n  **المرشح:** \"إذا تغير الكائن المشترك في موديول الأساس، ينحصر التعديل في كود المحول Mapper عند حدود الموديول، بينما تبقى كلاسات الـ ViewModels والشاشات معزولة تماماً ولا تتأثر.\"\n\n- **المحاور:** \"هل إضافة حقل جديد مع قيمة افتراضية default value في كوتلن تمنع إعادة التجميع؟\"\n  **المرشح:** \"تمنع كسر الكود المصدري ولكنها تغير توقيع الـ Bytecode للمنشئ؛ لذلك سيظل Gradle يعيد تجميع المستهلكين ما لم نستخدم العزل المعماري بالواجهات والمحولات.\"",
        "self_check_ar": "هل شرحت سبب المشكلة بالربط بـ ABI وبطء Gradle؟ وهل بينت مفهوم تجزئة الكائنات ونمط Anti-Corruption Layer والمحولات المحلية؟",
        "references_ar": f"- [Domain-Driven Design: Bounded Contexts](https://martinfowler.com/bliki/BoundedContext.html) — مقالات مارتن فاولر حول تجزئة نماذج البيانات.\n- [Reducing Gradle Recompilation with ABI Boundaries](https://docs.gradle.org/current/userguide/performance.html) — توثيق جرادل لحماية حدود التجميع.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "لتقليص مساحة تأثير تعديل نموذج البيانات المشترك، نقسم الكائنات الضخمة إلى كائنات قيمة مجزأة حسب سياق الاستخدام Bounded Contexts. كما نلزم موديولات الميزات بتعريف نماذج داخلية خاصة بها وتحويل الكائن المشترك عند حدود الموديول عبر نمط Anti-Corruption Layer، مما يحمي الشاشات والـ ViewModels من إعادة التجميع.",
        "best_answer_ar": "تعد مشكلة الكائن المشترك المتضخم God Model من أشهر المشكلات المعمارية التي تدمر سرعة البناء في مشاريع أندرويد الضخمة؛ فعندما يستقر كائن مثل User في موديول أساسي ويعتمد عليه 20 موديولاً، فإن إضافة خاصية جديدة فيه تبطل كاش البناء لكافة تلك الموديولات دفعة واحدة.\n\nلتقليص مساحة هذا التأثير هندسياً، نطبق حلين استراتيجيين: أولاً، تجزئة الكائن الضخم إلى كائنات صغيرة ومحددة وفق مبدأ Bounded Contexts في التصميم الموجه بالمجال؛ فبدلاً من كائن مستخدم واحد يحمل 40 حقلاً، ننشئ كائن UserIdentity لموديول التوثيق، وكائن ShippingAddress لموديول الشراء، بحيث لا يستورد كل موديول سوى الحقول التي تلزمه فقط.\n\nثانياً، نلزم موديولات الميزات ببناء طبقة حماية تسمى Anti-Corruption Layer؛ حيث يعرف موديول الميزة كائناته ونماذجه الداخلية الخاصة، ويقوم بتحويل الكائن المشترك عبر دالة محول Mapper داخل المستودع فور استلامه. فإذا تغير الكائن المشترك، ينحصر التعديل وإعادة التجميع في ذلك السطر البرمجي عند حدود الموديول، وتظل الـ ViewModels وشاشات Compose ومئات الاختبارات معزولة تماماً ومحتفظة بحالة UP-TO-DATE في الكاش.",
        "deep_answer_ar": "في إدارة الأداء المعماري لتطبيقات أندرويد، نعتبر كائنات البيانات المشتركة المتضخمة ألغاماً موقوتة تعطل فاعلية الـ Build Cache للمؤسسة ككل.\n\nتنشأ الأزمة عندما تقوم الفرق البرمجية بإضافة حقول تجريبية إلى كائن رئيسي في موديول قاعدي مثل :core:model؛ هنا يرصد مجمع Gradle تغيراً جوهرياً في بصمة الـ ABI للموديول الأساسي، مما يجبره على اعتبار مسار التجميع Compile Classpath لكافة الموديولات المستهلكة غير صالح، وتشتعل موجة إعادة تجميع شاملة تعطل عشرات المطورين في مختلف الفرق.\n\nولتحصين النظام ضد هذا التآكل، نطبق قواعد صارمة مستمدة من Domain-Driven Design؛ فنحظر تماماً وجود كائن جامع يخدم ميزات متباعدة، ونلجأ لتفكيكه إلى كائنات قيمة Value Objects مجتزأة ومركزة حول مهامها الوظيفية. فموديول الدفع لا يحتاج لمعرفة تفاصيل الملف الشخصي أو صورة المستخدم، بل يحتاج فقط لمعرف الحساب وبيانات البطاقة.\n\nكما نفرض تطبيق نمط Anti-Corruption Layer عند بوابات الموديولات؛ حيث تصمم موديولات الميزات نماذجها واستجاباتها الداخلية ككلاسات خاصة محمية بمعامل internal، وتستقبل الكائنات المشتركة كبيانات دخل يتم تحويلها عبر دوال Mappers فورية عند طبقة المستودع. هذا العزل يضمن أن أي تعديل في البنية التحتية المشتركة يظل معزولاً عند نقطة الدخول، وتبقى آلاف الأسطر من كود الشاشات والمنطق التجاري بمنأى تام عن إعادة التجميع، مما يحافظ على كفاءة البناء التزايدي وسرعة استجابة بيئة التطوير اليومية."
    }
}

# ==========================================
# MOD-19: Two feature teams need the same business logic. Where should it live?
# ==========================================
DATA["MOD-19"] = {
    "concept_en": """When two autonomous feature teams require identical business logic, resolving where that logic should live is a fundamental architectural dilemma with distinct trade-offs:
- Anti-Patterns to Avoid:
  1. Direct Feature Coupling: Having Feature B import Feature A breaks horizontal layer isolation, risks circular dependency loops, and compromises team release autonomy.
  2. The Common Garbage Dump: Shoving the logic into :core:common destroys cohesion and turns core into an uncontrolled monolith that invalidates the build cache project-wide.
- Architectural Solutions:
  1. Extract a Focused Shared Domain Module: If the capability represents a genuine, cohesive enterprise business concept (e.g., loan tax calculations, currency conversions), extract it into a leaf domain module: :domain:taxation or :core:domain:currency.
  2. API/Impl Feature Extraction: If one squad legitimately owns the domain (e.g., Identity squad owns biometric verification), they expose a contract in :feature:identity:api and house the logic in :feature:identity:impl for other features to consume.
  3. Controlled Code Duplication (AHA Programming): If the logic superficially appears similar but belongs to distinct bounded contexts with divergent lifecycles, duplicate the code rather than introducing premature, tightly coupled abstractions.""",
    "walkthrough_en": """Extracting shared business logic into an isolated leaf domain module:
```kotlin
// ❌ WRONG: :feature:cart imports :feature:checkout (Horizontal coupling!)
// ❌ WRONG: Logic dumped in :core:common (Cohesion destroyed!)

// ✅ CORRECT: Extract focused leaf domain module :domain:pricing
// domain/pricing/src/main/kotlin/CalculateDiscountUseCase.kt
class CalculateDiscountUseCase @Inject constructor() {
    operator fun invoke(cartTotal: BigDecimal, couponCode: String?): BigDecimal {
        // Pure Kotlin business calculation, zero Android dependencies
        return if (couponCode == "VIP") cartTotal.multiply(BigDecimal("0.80")) else cartTotal
    }
}

// Both :feature:cart and :feature:checkout depend on :domain:pricing
// Maintains clean DAG and enables sub-second JVM unit testing!
```""",
    "short_en": """When two feature teams need the same business logic, never create a direct feature-to-feature dependency or dump it into core:common. Extract the logic into a focused, single-responsibility leaf domain module, or have the owning feature expose an api module. If the logic belongs to separate bounded contexts with different reasons to change, prefer controlled duplication over premature coupling.""",
    "structured_en": """Deciding where shared business logic should live requires balancing code reuse against architectural coupling.
We strictly avoid two common anti-patterns: allowing one feature module to import another directly, or dumping the logic into a monolithic core:common module.
Instead, we apply three structured options.
If the logic represents a distinct enterprise rule like currency exchange or tax calculation, we extract a dedicated leaf domain module like domain:pricing.
Both feature modules import this pure Kotlin module, preserving an acyclic dependency graph and enabling instantaneous JVM testing.
If one squad clearly owns the capability, such as identity verification, that team exposes an interface in an api module while retaining the implementation.
Finally, if the logic only appears similar coincidentally but belongs to different business domains with independent reasons to change, senior architects prefer controlled code duplication rather than coupling the teams with a premature shared abstraction.""",
    "deep_senior_en": """In enterprise mobile architecture, sharing code across team boundaries is primarily an organizational governance decision rather than a simple refactoring exercise.
Engineers frequently suffer from dogmatic DRY (Don't Repeat Yourself) obsession, creating premature abstractions that tightly couple autonomous feature teams.
When two feature teams require shared business logic, we evaluate ownership, volatility, and domain alignment across three clear tiers.
First, if the capability represents an authentic, shared business policy—such as credit risk scoring or tax withholding calculations—we extract a dedicated, leaf-level pure Kotlin domain module, such as :domain:finance:tax.
Because this module has zero dependencies on Android frameworks, UI widgets, or sibling features, it compiles in milliseconds and can be unit-tested thoroughly on the JVM.
Both features declare an implementation dependency on this shared domain module, preserving a clean Directed Acyclic Graph.
Second, if the capability is a service owned by a specific squad—such as user identity verification—that team hosts the logic in its :feature:identity:impl module and publishes a clean interface in :feature:identity:api.
Other teams depend strictly on the :api contract, wiring the implementation via Hilt.
Third, we actively evaluate the AHA (Avoid Hasty Abstractions) principle.
If the shared logic is simply a five-line data transformation that happens to look identical today but serves different product goals—such as order sorting versus search result sorting—we intentionally allow controlled code duplication.
Duplicating a few lines of code is vastly cheaper than introducing an artificial shared module that requires cross-team synchronization and consensus for every future modification.""",
    "meta_ar": {
        "id": "MOD-19",
        "questionAr": "فريقان يحتاجان لنفس منطق الأعمال المشترك، أين يجب أن يستقر هذا الكود؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تحديد الموطن المعماري للمنطق المشترك، والمفاضلة بين استخراج موديول دومين فرعي مستقل مقابل تكرار الكود البرمجي (DRY vs Decoupling)، وحوكمة الملكية المشتركة.",
        "concept_ar": "عندما يحتاج فريقان إلى نفس منطق الأعمال المشترك، يجب تفادي خطأين شائعين: الاعتماد المباشر بين موديولي الميزتين (مما يكسر العزل الأفقي)، ورمي الكود في موديول :core:common المتضخم (مما يدمر التماسك). تكمن الحلول المعمارية الصحيحة في: استخراج موديول دومين طرفي مركز وأحادي المسؤولية (مثل :domain:pricing) ككود كوتلن خالص يعتمد عليه الموديولان، أو قيام الفريق المالك للميزة بنشر واجهة في موديول :api خاص به، أو قبول التكرار المنضبط للكود البرمجي (مبدأ AHA) إذا كانت الاحتياجات قابلة للاختلاف مستقبلاً تجنباً للتجريد المتعجل والمقترن.",
        "walkthrough_ar": """استخراج منطق الحسابات المشترك في موديول دومين طرفي نقي:
```kotlin
// ❌ خطأ: موديول cart يستورد موديول checkout (اقتران أفقي محظور)
// ❌ خطأ: وضع الكود في :core:common (تدمير التماسك وإبطال الكاش)

// ✅ الحل: موديول دومين طرفي نقي :domain:discount
// في domain/discount/src/main/kotlin/CalculateDiscountUseCase.kt
class CalculateDiscountUseCase @Inject constructor() {
    fun execute(total: BigDecimal, code: String?): BigDecimal {
        // منطق أعمال كوتلن خالص خالٍ من أندرويد
        return if (code == "PROMO") total.multiply(BigDecimal("0.90")) else total
    }
}
// يعتمد موديول السلة والدفع على :domain:discount في اتجاه واحد
```""",
        "why_it_matters_ar": "يمنع الاقتران الأفقي الخطير بين موديولات الميزات، ويحمي استقلالية وسرعة الفرق في إطلاق التحديثات، ويمنع تحول موديولات البنية التحتية إلى مستودع فوضوي للأكواد المشتركة.",
        "worked_example_ar": "فصل كود حساب الفوائد البنكية المشترك بين موديول القروض وموديول بطاقات الائتمان إلى موديول `:domain:interest-calculator`، مما أتاح اختباره بنسبة تغطية 100% دون المساس بشاشات الميزات.",
        "trade_offs_ar": "استخراج موديول دومين جديد يضيف موديولاً لشجرة Gradle وإعدادات بناء إضافية، ولكنه يحافظ على العزل المعماري التام وسرعة الاختبارات مقارنة بمخاطر الاقتران المباشر بين الميزات.",
        "failure_modes_ar": "استيراد موديول ميزة داخل ميزة أخرى كحل سريع، ووضع منطق الأعمال داخل موديول الـ design-system أو شبكات core، والربط القسري بين كودين متشابهين ظاهرياً ومختلفين تجارياً.",
        "production_perspective_ar": "في المنظمات الكبرى، نطبق حوكمة معمارية واضحة؛ إذا لم يتجاوز الكود المشترك 10 أسطر وكان عرضة للاختلاف التجاري بين الفريقين، نسمح بتكراره محلياً تجنباً للاعتماديات الزائفة.",
        "how_to_answer_ar": "ابدأ بحظر الحلين السيئين (الاعتماد المباشر بين الميزات، والرمي في common)، ثم اشرح الحلول الثلاثة: استخراج موديول دومين طرفي، أو نمط API/Impl إذا كانت الملكية لفريق محدد، أو التكرار المنضبط لمبدأ AHA.",
        "talking_points_ar": "مبدأ AHA (Avoid Hasty Abstractions) مقابل الهوس بـ DRY، استخراج موديولات الدومين النقية كـ Leaf Modules، وتجنب تلوث موديول core.",
        "follow_ups_ar": "- **المحاور:** \"متى تفضل تكرار الكود المنطقي بدلاً من استخراجه في موديول مشترك؟\"\n  **المرشح:** \"عندما يكون التشابه ظاهرياً فقط؛ كأن تحتاج ميزتان لترتيب عناصر ولكن وفق معايير تجارية قد تتغير لكل فريق بشكل مستقل مستقبلاً.\"\n\n- **المحاور:** \"إذا استخرجنا المنطق في موديول دومين، ما هي المكتبات المسموح بوجودها فيه؟\"\n  **المرشح:** \"مكتبات كوتلن الخالصة فقط مثل Coroutines و Kotlinx Serialization مع Hilt/Inject، ويُحظر تماماً وجود أي مكتبة من مكتبات Android Framework.\"",
        "self_check_ar": "هل حذرت من الاقتران المباشر والرمي في common؟ وهل بينت خيارات استخراج موديول الدومين، وموديول API، وخيار التكرار المنضبط وفق مبدأ AHA؟",
        "references_ar": f"- [AHA Programming: Avoid Hasty Abstractions](https://kentcdodds.com/blog/aha-programming) — فلسفة تجنب التجريد المتعجل في هندسة البرمجيات.\n- [Domain-Driven Design: Shared Kernel](https://martinfowler.com/bliki/SharedKernel.html) — نمط النواة المشتركة في تقسيم الموديولات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "عندما يحتاج فريقان لنفس منطق الأعمال، يُحظر تماماً ربط موديوليهما ببعضهما أو رمي الكود في core:common. نستخرج المنطق في موديول دومين طرفي نقي مثل domain:pricing يعتمد عليه الفريقان، أو يقدم الفريق المالك واجهة في موديول api خاص به. وإذا كان التشابه ظاهرياً وقد يختلف مستقبلاً، نفضل التكرار المنضبط تجنباً للاقتران المبكر.",
        "best_answer_ar": "تحديد المكان المعماري الصحيح للمنطق المشترك بين فريقين يخضع لموازنة حاسمة بين إعادة استخدام الكود واستقلالية الفرق البرمجية.\n\nنستبعد فوراً حلين خاطئين: استيراد موديول ميزة داخل ميزة أخرى لأن ذلك ينشئ اقتراناً أفقياً خطيراً يهدد بحلقات دائرية، أو رمي الكود في موديول core:common مما يفقده التماسك ويحوله لمونوليث مقنع. وبدلاً من ذلك، نتبع ثلاث استراتيجيات مدروسة: أولاً، إذا كان المنطق يمثل قاعدة أعمال مؤسسية حقيقية كحساب الضرائب أو تحويل العملات، نستخرجه في موديول دومين طرفي نقي مثل domain:taxation ككود كوتلن خالص وخفيف الوزن يعتمد عليه الموديولان دون وسيط.\n\nثانياً، إذا كانت الميزة تتبع ملكية واضحة لفريق محدد كفريق الهوية، يقوم ذلك الفريق بنشر واجهة في موديول :api خاص به مع الاحتفاظ بالتنفيذ، لتستدعيها الفرق الأخرى عبر Hilt. وثالثاً، إذا كان الكود مجرد تشابه بسيط وظاهري في معالجة البيانات، نفضل تطبيق مبدأ AHA وقبول تكرار الكود المنضبط محلياً، لأن تكرار بضعة أسطر برمجية أهون بكثير من إنشاء تبعية معمارية تقيد الفريقين وتتطلب تنسيقاً دائماً عند كل تعديل مستقبلي.",
        "deep_answer_ar": "في قيادة هندسة المنصات، نعتبر الهوس الأعمى بمبدأ DRY وتجنب التكرار فخاً يؤدي لبناء تجريدات متعجلة تقيد حركة الفرق البرمجية وتزيد من تشابك شجرة التبعيات.\n\nعندما يتشارك فريقان في منطق برمجي، ندرس أولاً أسباب التغيير المستقبلية لكل ميزة وفق مبادئ Domain-Driven Design؛ فإذا كان المنطق يمثل سياسة عمل عامة ومستقرة، مثل خوارزمية تسعير أو احتساب رسوم الشحن، فإن الإجراء المعماري السليم هو استخراج موديول دومين طرفي خالص كـ :domain:pricing. هذا الموديول يكون خالياً تماماً من أي تبعيات لنظام أندرويد، مما يجعله يُجمع في ثوانٍ معدودة ويخضع لاختبارات دقيقة على JVM، ويعتمد عليه موديولا الفريقين بتدفق أحادي الاتجاه يحافظ على نظافة مخطط DAG.\n\nأما إذا كانت الخدمة تقع ضمن نطاق مسؤولية فريق متخصص كإدارة الجلسات، فإننا نوظف نمط API/Impl؛ حيث يتيح الفريق المالك واجهة مجردة في موديول :api خفيف، ويحتفظ بالتنفيذ في موديول :impl الخاص به، وتستهلك الفرق الأخرى العقد البرمجي فقط مع ربطه بحقن التبعيات بـ Hilt في موديول app الرئيسي.\n\nوعلاوة على ذلك، نطبق بشجاعة مبدأ AHA (Avoid Hasty Abstractions)؛ فإذا كان المنطق المشترك مجرد دالة بسيطة لمعالجة النصوص أو تنسيق العرض تبدو متشابهة اليوم ولكنها تخدم أهدافاً تسويقية مختلفة لكل فريق، فإننا نسمح بتكرارها في كل موديول على حدة. إن تكرار خمسة أسطر برمجية أفضل بمئات المرات من إنشاء موديول مشترك مصطنع يجبر مهندسي الفريقين على عقد اجتماعات تنسيقية ومراجعات مشتركة في كل مرة يرغب فيها أحدهما بتعديل سلوك الميزة."
    }
}

# ==========================================
# MOD-20: How do you migrate a monolith to modules without blocking feature delivery?
# ==========================================
DATA["MOD-20"] = {
    "concept_en": """Migrating an enterprise Android monolith to a multi-module architecture while shipping daily product features requires applying the Strangler Fig Pattern to incrementally dismantle the monolith without big-bang rewrites:
- Step 1: Foundational Bottom-Up Extraction: Extract stable, domain-agnostic leaf modules first (:core:designsystem, :core:network, :core:database). Because these have zero business logic dependencies, they stabilize quickly and establish convention plugins and version catalogs.
- Step 2: Vertical Leaf Feature Extraction: Identify self-contained, low-risk user journeys with minimal inward dependencies (e.g., Settings, About, Onboarding). Extract each into an independent :feature:<name> module using the API/Impl pattern, wiring navigation back to the monolith app module via contract interfaces.
- Step 3: Domain & Repository Decoupling: Extract core data and domain logic into independent modules, leaving backwards-compatible interface adapters in the legacy monolith so legacy screens continue functioning while new features build on modular foundations.
- Step 4: Governance & Enforcement: Introduce CI linters (Konsist) to forbid new code in the legacy monolith, shrinking it until :app becomes a pure composition root.""",
    "walkthrough_en": """Incremental migration using the Strangler Fig pattern and modular adapter bridges:
```text
Phase 1: Foundational Leaf Extraction
[Legacy Monolith :app] ──imports──> [:core:designsystem] & [:core:network]

Phase 2: Vertical Feature Extraction via API Contracts
[Legacy Monolith :app] ──wires──> [:feature:settings:impl] (Implements SettingsApi)
                      └──imports─> [:feature:settings:api]

Phase 3: The Monolith Becomes Pure Composition Root
[Root :app] (Pure DI & Navigation wiring)
  ├── imports :feature:onboarding:impl
  ├── imports :feature:checkout:impl
  └── imports :feature:settings:impl
```""",
    "short_en": """Migrating a monolith without blocking product delivery follows the Strangler Fig pattern. Teams extract horizontal core infrastructure modules first, then extract self-contained vertical feature modules using the API/Impl pattern. By wiring navigation through contract interfaces and freezing legacy monolith packages with CI lint rules, the monolith gradually shrinks into a pure composition root.""",
    "structured_en": """Migrating a monolithic Android codebase to a multi-module architecture requires a phased strategy that never halts product delivery.
Big-bang architectural rewrites are catastrophic because they block business features and generate impossible merge conflicts.
Instead, we apply the Strangler Fig pattern across four distinct phases.
In phase one, we extract stable, domain-agnostic foundational infrastructure from the bottom up, creating core:designsystem and core:network while setting up Version Catalogs and convention plugins.
In phase two, we extract vertical leaf features that have low coupling, such as Settings or Onboarding, splitting them into public api and private implementation modules.
The legacy monolith navigates to these new modules via abstract contracts.
In phase three, we migrate core data repositories into modular layers, providing bridge adapters so legacy monolithic code continues functioning.
In phase four, we establish CI lint rules that forbid adding new code to the legacy monolith, systematically shrinking it until the app module becomes a pure composition root.""",
    "deep_senior_en": """In large-scale Android engineering, attempting a monolithic rewrite by pausing feature development is an organizational death sentence.
Product teams cannot freeze business roadmaps for six months while architects refactor the codebase.
Our proven methodology executes an incremental migration using the Strangler Fig pattern, ensuring that daily feature releases continue uninterrupted.
We begin with foundational leaf extraction.
We pull our visual styles, colors, and atomic Compose components into :core:designsystem, and our HTTP client configurations into :core:network.
Because infrastructure modules have zero business dependencies, this step creates zero regression risk while establishing our Gradle build-logic convention plugins and libs.versions.toml catalog.
Next, we execute vertical slice migrations starting with leaf features.
We identify an isolated, low-risk user flow—such as a Feedback or Profile Settings screen—and extract it completely into :feature:settings:api and :feature:settings:impl.
The legacy monolith in :app retains the navigation launcher, invoking SettingsNavigator wired via Hilt.
To prevent the monolith from regressing, we introduce architectural enforcement in CI using Konsist tests.
We freeze legacy monolithic packages: any pull request that adds new files to legacy app/src/main/java triggers an automated build failure with instructions to create a modular package.
New features are authored exclusively within modular subprojects, consuming the extracted core layers.
Over successive quarters, legacy activities are strangled one by one, until the monolithic :app module contains nothing more than the Application class, Hilt bindings, and top-level navigation graphs, successfully completing the transformation without a single day of blocked feature delivery.""",
    "meta_ar": {
        "id": "MOD-20",
        "questionAr": "كيف تهاجر من تطبيق متجانس (Monolith) إلى موديولات متعددة دون تعطيل تسليم الميزات اليومية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تطبيق استراتيجية الهجرة الخانقة Strangler Fig Pattern، والتفكيك العمودي التدريجي، وعزل البنية التحتية أولاً (Bottom-up vs Top-down)، وإدارة مخاطر مسار Git.",
        "concept_ar": "تعتمد الهجرة الآمنة من تطبيق متجانس (Monolith) إلى موديولات متعددة دون إيقاف تسليم الميزات التجارية على تطبيق نمط شجرة التين الخانقة (Strangler Fig Pattern) بالتدريج: البدء باستخراج موديولات البنية التحتية الطرفية المستقرة من الأسفل للأعلى (:core:designsystem و :core:network) وتأسيس Convention Plugins. ثم استخراج ميزات طرفية عمودية منخفضة المخاطر (مثل الإعدادات والشاشات التعريفية) بنمط API/Impl وربطها بالمونوليث عبر عقود مجردة. ثم ترحيل المستودعات ونماذج البيانات تدريجياً، مع فرض حظر آلي بـ Konsist في مسار الـ CI يمنع إضافة أي كود جديد داخل موديول app القديم حتى يتحول إلى مجرد Composition Root نقي.",
        "walkthrough_ar": """مراحل الهجرة التدريجية بنمط Strangler Fig:
```text
المرحلة 1: استخراج البنية التحتية المستقرة
المونوليث (:app) ──يعتمد على──> [:core:designsystem] & [:core:network]

المرحلة 2: استخراج ميزة طرفية بنمط API/Impl
المونوليث (:app) ──يستدعي──> [:feature:settings:api]
                      └──يربط تنفيذ──> [:feature:settings:impl]

المرحلة 3: المونوليث يتحول إلى Composition Root نقي
:app (تجميع Hilt والتنقل فقط)
  ├── :feature:auth
  ├── :feature:home
  └── :feature:settings
```""",
        "why_it_matters_ar": "يجنب المؤسسة مخاطر إعادة الكتابة الشاملة الفاشلة (Big-Bang Rewrite)، ويسمح باستمرار طرح الميزات للعملاء وتحقيق العوائد المالية، مع تحسين زمن البناء وجودة الكود تدريجياً وبأمان تام.",
        "worked_example_ar": "خطة هجرة تطبيق بنكي متجانس عبر استخراج موديول الشبكة أولاً، ثم استخراج ميزة 'حاسبة القروض' كموديول مستقل، مع حظر التعديل في كود المونوليث عبر قواعد Konsist في مسار الـ CI.",
        "trade_offs_ar": "الهجرة التدريجية تتطلب الحفاظ على كود وسيط Adapters لفترة مؤقتة لتوافق الكود القديم مع الموديولات الجديدة، ولكنها تضمن استمرارية الأعمال وتفادي نزاعات Git الكارثية.",
        "failure_modes_ar": "محاولة إيقاف العمل لعدة أشهر لإعادة كتابة التطبيق بالكامل، والبدء بتفكيك الميزات المعقدة شديدة الترابط بدلاً من الميزات الطرفية، والسماح بكتابة ميزات جديدة داخل المونوليث القديم.",
        "production_perspective_ar": "في كبرى الشركات، نحدد مقياس 'نسبة تفكيك المونوليث' كـ KPI ربع سنوي، ونستخدم أدوات الفحص المعماري لضمان أن كل سبرنت يقلل من حجم كود موديول app لصالح الموديولات الجديدة.",
        "how_to_answer_ar": "ارفض فكرة إعادة الكتابة الشاملة، ثم اشرح استراتيجية Strangler Fig عبر مراحلها الأربع: استخراج البنية التحتية، تفكيك الميزات الطرفية بنمط API، ترحيل البيانات، وتجميد المونوليث القديم بـ Konsist.",
        "talking_points_ar": "نمط Strangler Fig Pattern في معمارية الموبايل، البدء بالبنية التحتية ثم الميزات الطرفية Leaf Features، وكيفية حظر الكود القديم عبر اختبارات Konsist في مسار الـ CI.",
        "follow_ups_ar": "- **المحاور:** \"لماذا تبدأ باستخراج البنية التحتية مثل designsystem والشبكة قبل ميزات الأعمال؟\"\n  **المرشح:** \"لأن موديولات البنية التحتية لا تعتمد على أي منطق تجاري؛ فاستخراجها سريع وخالٍ من المخاطر ويؤسس بيئة الـ Convention Plugins التي ستبنى عليها باقي الميزات.\"\n\n- **المحاور:** \"كيف تمنع المطورين من الاستمرار في إضافة كود داخل المونوليث القديم أثناء الهجرة؟\"\n  **المرشح:** \"نضع اختبارات Konsist في مسار الـ CI تفشل أي Pull Request يضيف كلاسات جديدة داخل مجلد app القديم، وتلزم ببناء الميزات الجديدة داخل موديولات مستقلة.\"",
        "self_check_ar": "هل رفضت الـ Big-Bang Rewrite؟ وهل شرحت نمط Strangler Fig بالترتيب الصحيح (البنية التحتية، الميزات الطرفية، ثم حظر كود المونوليث)؟",
        "references_ar": f"- [Legacy Monolith Migration: Strangler Fig Pattern](https://martinfowler.com/bliki/StranglerFigApplication.html) — مقالات مارتن فاولر حول نمط الهجرة التدريجية.\n- [Modularizing Android Applications Guide](https://developer.android.com/topic/modularization) — إرشادات جوجل الرسمية لتفكيك التطبيقات المتجانسة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تهاجر من المونوليث بأمان دون تعطيل تسليم الميزات بتطبيق نمط Strangler Fig التدريجي. نبدأ باستخراج موديولات البنية التحتية المستقرة من الأسفل مثل core:network و designsystem، ثم نستخرج الميزات الطرفية البسيطة بنمط API/Impl ونربطها بالمونوليث عبر عقود مجردة، مع تجميد موديول app القديم باختبارات Konsist حتى يتحول لمجرد Composition Root نقي.",
        "best_answer_ar": "إيقاف العمل وتجميد خريطة تطوير المنتجات لإعادة كتابة تطبيق متجانس بالكامل هو انتحار تجاري وهندسي؛ فإعادة الكتابة الشاملة Big-Bang دائماً ما تفشل بسبب نزاعات الدمج وتعطل الميزات الجديدة.\n\nالبديل الاحترافي المعتمد هو تطبيق نمط شجرة التين الخانقة Strangler Fig Pattern عبر أربع مراحل متتالية ومنضبطة. نبدأ أولاً باستخراج موديولات البنية التحتية الأفقية مثل core:designsystem و core:network وتأسيس كتالوج التبعيات و Convention Plugins؛ ونظراً لخلو هذه الموديولات من المنطق التجاري، فإن استخراجها آمن ويؤسس المعايير للمراحل التالية.\n\nفي المرحلة الثانية، ننتقل للتفكيك العمودي باختيار ميزات طرفية مستقلة ومنخفضة المخاطر كشاشة الإعدادات أو الشاشات التعريفية، ونفصلها إلى موديولين api و impl، ونربطها بالمونوليث عبر واجهات تنقل مجردة. وفي المرحلة الثالثة، ننقل مستودعات البيانات تدريجياً مع توفير محولات توافق للكود القديم. وأخيراً، نضع اختبارات Konsist آلية في مسار الـ CI تمنع إضافة أي كود جديد للمونوليث، مما يخنق الكود القديم سبرنت تلو الآخر حتى يصبح موديول app مجرد مركز تجميع وتثبيت نقي.",
        "deep_answer_ar": "في قيادة التحول المعماري للتطبيقات المصرفية والتجارية الكبرى، نعتبر الحفاظ على وتيرة تسليم الميزات التجارية للعملاء مقياس النجاح الأول لأي عملية إعادة هيكلة برمجية.\n\nتعتمد استراتيجيتنا على تفكيك المونوليث بنمط Strangler Fig دون التأثير على عمل الفرق الأخرى؛ حيث نبدأ باستخراج موديولات البنية التحتية التحتية المستقرة Leaf Modules كـ :core:designsystem للأزرار والألوان الموحدة و :core:network لمحركات الاتصال. تمنحنا هذه الخطوة فرصة إرساء قواعد البناء الموحدة عبر build-logic دون أي احتكاك مع الميزات القائمة.\n\nثم نبدأ مرحلة التفكيك العمودي بتحديد الميزات الطرفية الأقل تشابكاً مثل ميزات Onboarding والملف الشخصي؛ فنفصل الميزة إلى موديول :api للواجهات وموديول :impl للتنفيذ، وتستدعيها الأنشطة القديمة في المونوليث عبر واجهات تنقل مجردة يربطها Hilt. ولحماية مسار الهجرة من الانتكاس، نبرمج اختبارات Konsist معمارية داخل مسار الـ CI تفرض حظراً كاملاً على إضافة كود جديد داخل مجلد app القديم؛ فإذا حاول أي مطور كتابة كلاس جديد داخل المونوليث، يفشل البناء تلقائياً مع توجيهه لإنشاء موديول ميزة جديد.\n\nتستمر هذه الهجرة التزايدية على مدار عدة أرباع سنوية مع تسليم كافة الميزات التجارية في مواعيدها المحددة، حتى ينحسر كود المونوليث تماماً، ويتحول موديول :app إلى مجرد نقطة تجميع وتثبيت Composition Root خفيفة الوزن لا تحتوي سوى على كلاس Application ومخطط التنقل العام، محققين بذلك نقلة معمارية نوعية دون تعطيل عجلة الإنتاج ليوم واحد."
    }
}

# ==========================================
# MOD-21: When are dynamic feature modules inappropriate because of offline/runtime constraints?
# ==========================================
DATA["MOD-21"] = {
    "concept_en": """While Dynamic Feature Modules (DFMs) effectively shrink initial APK download sizes through Google Play Feature Delivery, they introduce profound operational risks that make them entirely inappropriate in specific mission-critical scenarios:
1. Offline-First and Field Operation Constraints: Applications operating in connectivity-deprived environments (field service, maritime logistics, emergency response, flight management) cannot rely on on-demand downloading; missing features leave users stranded without network fallback.
2. Core Revenue and Critical Funnels: Core revenue journeys (login, user registration, onboarding, primary checkout flows, emergency customer support) must never be dynamic. A transient network timeout, cellular data limit, or Play Store service glitch directly destroys user acquisition and financial conversion.
3. Latency-Sensitive User Experiences: Features requiring immediate responsiveness (real-time camera capture, QR code scanner at a store checkout, instant authentication) degrade user satisfaction if the user must endure a 30-second download progress dialog.
4. Non-Google Play Ecosystems: Devices lacking Google Play Services (Chinese domestic Android stores, Huawei AppGallery, Amazon FireOS, enterprise sideloaded APKs) do not natively support Play Core split installations, requiring complex, fragile multi-APK fallback architectures.
5. Storage and OS Cleanup Risks: On Android Go or low-storage devices, the Android package manager may reclaim storage by clearing split APKs, forcing unexpected redownloads at awkward moments.""",
    "walkthrough_en": """Evaluating dynamic delivery feasibility against operational constraints:
```kotlin
// ❌ DANGEROUS: Putting core onboarding or payment into a Dynamic Feature Module!
// If network drops or Google Play Store fails, user CANNOT register or pay!

// ✅ APPROPRIATE ARCHITECTURAL DECISION:
// Keep Mission-Critical paths inside Base APK:
// - :feature:auth          -> In Base APK (Zero-tolerance for download failures)
// - :feature:checkout      -> In Base APK (Core revenue path must be offline-capable)

// Reserve Dynamic Delivery ONLY for Heavy, Niche, Optional features:
// - :dynamic:ar-viewer     -> 35MB AR Core models, used by < 5% of users.
// - :dynamic:tax-scanner   -> Heavy ML model, used once per year.
```""",
    "short_en": """Dynamic Feature Modules are inappropriate for offline-first applications, core revenue funnels like login and checkout, and latency-critical interactions like payment scanners. They are also unsuitable for apps distributed outside Google Play (such as Amazon FireOS or Huawei AppGallery) and low-end devices where the OS frequently uninstalls split APKs to free up storage.""",
    "structured_en": """While Dynamic Feature Modules optimize initial download sizes, they introduce runtime vulnerabilities that make them unsuitable for critical application workflows.
Dynamic delivery is fundamentally inappropriate for offline-first applications where users operate in environments with spotty or nonexistent internet connectivity.
Similarly, core business funnels such as user onboarding, authentication, checkout, and emergency support must never be placed in dynamic modules.
A single network timeout or Google Play Store error during download prevents users from completing transactions, causing direct revenue loss and customer churn.
Furthermore, dynamic features are impractical for apps distributed across diverse app stores like Huawei AppGallery, Amazon FireOS, or third-party enterprise distribution, as Play Feature Delivery relies strictly on Google Play Services.
High-frequency, latency-sensitive features like QR code scanners should remain in the base APK to eliminate download waiting screens.""",
    "deep_senior_en": """In production mobile architecture, Dynamic Feature Modules represent a calculated gamble: trading runtime reliability for initial download size reduction.
When a feature is packaged dynamically, availability ceases to be a deterministic compile-time guarantee and becomes a volatile runtime network dependency subject to cellular coverage, Google Play Core service health, device storage availability, and roaming data limits.
Consequently, deploying dynamic modules across mission-critical workflows is a catastrophic anti-pattern.
First, core revenue paths must remain in the base APK.
Placing registration, login, or checkout into a dynamic module means that an error code from SplitInstallManager directly translates into aborted customer onboarding and lost revenue.
Second, offline-first architectures demand immediate local availability.
Field engineering tools, warehouse scanners, and healthcare emergency apps cannot tolerate an 'Unable to download module, check your internet connection' error dialog when an ambulance technician or remote inspector opens a screen.
Third, distribution platform fragmentation presents a hard technical blocker.
Play Feature Delivery is fundamentally proprietary to Google Play Services.
If your application targets global markets including China, runs on Huawei HMS devices, or distributes via enterprise MDMs, dynamic modules fail to load unless you maintain complex, parallel multi-flavor fallback architectures that package the dynamic modules back into monolithic APKs.
Finally, Android Go and low-end devices introduce storage volatility.
When physical device storage runs low, the Android OS package manager can silently purge unmounted split APKs, forcing a paying user to re-download a previously installed feature unexpectedly.
Senior architects mandate dynamic modules exclusively for heavy, optional, low-frequency capabilities—such as a 30-megabyte augmented reality preview or an annual tax return scanner—while anchoring all core business capabilities firmly inside the immutable base APK.""",
    "meta_ar": {
        "id": "MOD-21",
        "questionAr": "متى يكون استخدام الموديولات الديناميكية (Dynamic Feature Modules) غير ملائم بسبب قيود العمل دون اتصال أو وقت التشغيل؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تحليل القيود الميدانية لـ Play Feature Delivery، ومخاطر الاعتماد على الشبكة في تجارب المستخدم الحرجة، والبيئات الخالية من خدمات Google Play (China / Huawei / FireOS).",
        "concept_ar": "على الرغم من قدرة موديولات الميزات الديناميكية (DFMs) على تقليص حجم التطبيق، إلا أنها تمثل خطراً تشغيلياً جسيماً في حالات محددة: التطبيقات التي تعمل دون اتصال (Offline-first) كتطبيقات الطوارئ والملاحة والميدان، رحلات المستخدم الحيوية لتوليد الإيرادات (التسجيل، تسجيل الدخول، الدفع) حيث يتسبب فشل التنزيل في فقدان العميل، الميزات الحساسة للتأخير الزمني (مثل ماسح الـ QR عند كاشير الدفع)، والتطبيقات الموجهة لأسواق لا تدعم خدمات Google Play (مثل أجهزة Huawei وسوق الصين وAmazon FireOS)، والأجهزة الاقتصادية التي قد تحذف الـ Split APKs تلقائياً لتحرير مساحة الذاكرة.",
        "walkthrough_ar": """تحديد مسار الميزات بين حزمة الأساس والتحميل الديناميكي:
```kotlin
// قرارات معمارية لفرز الميزات بحسب ملاءمتها للتحميل الديناميكي:

// ❌ محظور جعله Dynamic Feature (مخاطرة تشغيلية عالية):
// :feature:login     -> يجب أن يكون في Base APK (ضروري لفتح التطبيق دون إنترنت)
// :feature:checkout  -> يجب أن يكون في Base APK (شريان الإيرادات لا يتحمل فشل التنزيل)

// ✅ ملائم تماماً كـ Dynamic Feature (حجم كبير، استخدام نادر واختياري):
// :dynamic:ar-viewer      -> حجمه 40MB ويستخدمه أقل من 5% من العملاء
// :dynamic:annual-reports -> تقارير سنوية تستدعى مرة واحدة في السنة
```""",
        "why_it_matters_ar": "يحمي التطبيق من فقدان العملاء والأرباح نتيجة أخطاء التنزيل الشبكي، ويضمن استمرارية عمل الخدمات الحيوية دون اتصال، ويوفر تجربة استخدام سريعة وموثوقة تتناسب مع تنوع الأسواق والأجهزة.",
        "worked_example_ar": "قرار بنك رقمي بإلغاء تحويل شاشة 'فتح الحساب' إلى Dynamic Feature بعد رصد انخفاض بنسبة 12% في تسجيل العملاء الجدد بسبب فشل تنزيل الموديول على شبكات الاتصال الضعيفة.",
        "trade_offs_ar": "الاحتفاظ بالميزات داخل حزمة الأساس يرفع حجم الـ APK الأولي قليلاً، ولكنه يضمن توافر الخدمة بنسبة 100% ويعمل دون اتصال بالإنترنت وعلى كافة المتاجر والأجهزة دون أي تبعيات لخدمات جوجل.",
        "failure_modes_ar": "وضع شاشات تسجيل الدخول أو إتمام الدفع داخل موديول ديناميكي مما يمنع المستخدم من الدفع عند ضعف الشبكة، ونشر التطبيق على متجر Huawei AppGallery دون توفير بديل لـ Play Core، وتجاهل حالات فشل التحميل.",
        "production_perspective_ar": "في التطبيقات العالمية، نلزم كافة ميزات الشريحة الأولى (Tier-1 Features) بالبقاء داخل حزمة الأساس Base APK، ونحصر الموديولات الديناميكية في الميزات الإضافية الثقيلة (Tier-3 Features).",
        "how_to_answer_ar": "اذكر بوضوح أن تقليل الحجم لا يبرر التضحية بتوافر الخدمة، ثم استعرض الحالات الخمس غير الملائمة: العمل دون اتصال، رحلات الإيرادات الحيوية، العمليات الحساسة للتأخير، الأجهزة بدون خدمات جوجل، وحذف النظام للملفات.",
        "talking_points_ar": "مخاطر الاعتماد على الشبكة في رحلات الشراء، مشكلة الأجهزة بدون خدمات Google Play، وسلوك نظام Android Go في حذف حزم الـ Splits لتحرير الذاكرة.",
        "follow_ups_ar": "- **المحاور:** \"إذا اضطررنا لنشر تطبيق يستخدم Dynamic Features على أجهزة Huawei، كيف نتصرف؟\"\n  **المرشح:** \"نستخدم Build Flavors في Gradle لإعادة دمج موديولات الميزات الديناميكية كـ Regular Library Modules داخل الـ APK الأساسي لتلك المتاجر دون استخدام Play Core.\"\n\n- **المحاور:** \"لماذا يحذف نظام أندرويد حزم الـ Split APKs التي تم تنزيلها أحياناً؟\"\n  **المرشح:** \"في الأجهزة الاقتصادية ذات السعة المنخفضة، يقوم Package Manager بحذف الميزات الديناميكية غير المستخدمة لتحرير مساحة تخزين عند امتلاء الهاتف، مما يجبر المستخدم على تنزيلها مجدداً.\"",
        "self_check_ar": "هل حددت الحالات غير الملائمة بدقة (offline، رحلات الإيرادات، الأجهزة بدون خدمات جوجل، حساسية التأخير)؟ وهل وزنت بين تقليص الحجم وتوافر الخدمة؟",
        "references_ar": f"- [Play Feature Delivery Considerations](https://developer.android.com/guide/playcore/feature-delivery) — إرشادات جوجل ومحددات تسليم الميزات الديناميكية.\n- [Offline-first App Architecture](https://developer.android.com/topic/architecture/data-layer/offline-first) — أفضل ممارسات معمارية التطبيقات التي تعمل دون اتصال.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تكون الموديولات الديناميكية غير ملائمة إطلاقاً في التطبيقات التي تعمل دون اتصال، وفي رحلات المستخدم الحيوية كالتسجيل والدفع حيث يتسبب فشل التنزيل في خسارة فورية للأرباح، وللميزات الحساسة للتأخير الزمني. كما أنها غير صالحة للمتاجر التي تفتقر لخدمات Google Play كأجهزة Huawei وفي الهواتف الاقتصادية التي تحذف حزم التثبيت لتحرير المساحة.",
        "best_answer_ar": "على الرغم من الميزة التسويقية لتقليص حجم التطبيق الأولي عبر Dynamic Feature Modules، إلا أن استخدامها يتحول إلى خطأ فادح عندما يهدد توافر واستقرار وظائف التطبيق الأساسية.\n\nتكون الميزات الديناميكية غير ملائمة قطعياً في خمسة سيناريوهات ميدانية: أولاً، في التطبيقات الموجهة للعمل دون اتصال بالإنترنت Offline-first مثل تطبيقات الإسعاف والميدان والملاحة؛ حيث يؤدي غياب التغطية إلى عجز المستخدم عن تشغيل الميزة. ثانياً، في رحلات العمل الحيوية لتوليد الإيرادات Core Revenue Funnels كشاشات تسجيل الدخول، والتسجيل، والدفع؛ فحدوث انقطاع في الشبكة أو عطل في خوادم متجر جوجل أثناء التنزيل يتسبب في انسحاب العميل وخسارة مالية مباشرة.\n\nثالثاً، للميزات الحساسة للسرعة اللحظية كمسح الـ QR عند الكاشير؛ رابعاً، في الأسواق والأجهزة التي تفتقر لخدمات Google Play مثل أجهزة Huawei ومتاجر الصين وAmazon FireOS حيث لا يعمل نظام Play Core؛ وخامساً، في الأجهزة الاقتصادية ذات الذاكرة الضعيفة حيث يميل نظام أندرويد لحذف الموديولات المنفصلة تلقائياً لتحرير الذاكرة، مما يجبر العميل على إعادة تنزيلها مراراً وتكراراً.",
        "deep_answer_ar": "في تقييم المخاطر المعمارية للأنظمة الكبرى، نعتبر تحويل ميزة ما إلى Dynamic Feature Module مقايضة خطيرة؛ فنحن نستبدل التوافر المحلي المضمون وقت التجميع باعتمادية شبكية هشة في وقت التشغيل تتأثر بظروف تغطية الهاتف وسعة الذاكرة واستقرار خوادم متجر Google Play.\n\nبناءً على ذلك، نضع قاعدة هندسية لا تقبل المساومة: مسارات الأعمال الحرجة Tier-1 Capabilities لا يجوز أبداً أن تكون موديولات ديناميكية. فإذا وضعت شاشة الدفع أو التحقق البيومتري في موديول ديناميكي، فإن أي خطأ شبكي من SplitInstallManager يترجم فورياً إلى إحباط العميل وفقدان مباشر للمبيعات. كما تحظر هذه التقنية في التطبيقات الميدانية وتطبيقات الطوارئ والخدمات اللوجستية التي تعمل في أعماق البحار أو المناطق النائية لغياب الاتصال المستمر.\n\nوعلاوة على ذلك، تشكل البيئات الخالية من خدمات جوجل Google Play Services عائقاً تقنياً مستعصياً؛ فإذا كان تطبيقك يستهدف الانتشار العالمي ويوزع عبر متاجر بديلة كمتجر Huawei AppGallery، فإن ميزات Play Core تفشل في العمل ما لم تستثمر مئات الساعات في بناء إعدادات Gradle Flavors معقدة تعيد دمج الميزات ككود ملموس لتلك المتاجر. وفوق كل ذلك، يتصرف Package Manager في هواتف Android Go الاقتصادية بعدوانية شديدة عند امتلاء الذاكرة؛ حيث يقوم بحذف ملفات الـ Split APKs غير المستخدمة لتحرير المساحة، مما يفاجئ العميل بظهور شاشة تحميل بطيئة لميزة كان قد استخدمها سابقاً. لهذه الأسباب مجتمعة، نقصر الميزات الديناميكية حصرياً على القدرات الثقيلة والاختيارية كأدوات الواقع المعزز أو المسح السنوي للوثائق، ونبقي عصب التطبيق محمياً وثابتاً داخل الـ Base APK."
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

    ee.save_topic_metadata("mod_15_21", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print("\nAll 7 MOD questions (MOD-15 to MOD-21) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
