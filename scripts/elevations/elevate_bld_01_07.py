#!/usr/bin/env python3
"""
Elevation script for BLD questions: BLD-01 to BLD-07.
Topic: Build & Gradle (BLD)
Phase 4, Batch 1
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "أنظمة البناء و Gradle و AGP و R8 والـ Signing وإصدار التطبيقات"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# BLD-01: Explain Gradle, Android Gradle Plugin (AGP), and Kotlin compiler roles.
# ==========================================
DATA["BLD-01"] = {
    "concept_en": """The Android build system separates orchestration, platform specialization, and language compilation across three primary components:
- Gradle (Build Orchestration Engine): A language-agnostic build automation tool. It evaluates configuration scripts (build.gradle.kts), computes task dependencies into a Directed Acyclic Graph (DAG), executes tasks in parallel, and manages input-output caching and incremental task states. It has no native knowledge of Android APKs, DEX files, or Android resources.
- Android Gradle Plugin (AGP): A Google-developed plugin that adapts Gradle for Android development. AGP registers Android-specific tasks and DSL extensions into the build DAG. It compiles Android resources using AAPT2, merges AndroidManifest.xml files, generates BuildConfig and R.java, orchestrates D8/R8 byte-code desugaring and dexing, and packages final APK and AAB release artifacts.
- Kotlin Compiler (kotlinc): Compiles Kotlin source files (.kt) into JVM bytecode (.class). Orchestrated by AGP tasks, kotlinc executes Kotlin Symbol Processing (KSP) and integrates compiler plugins (such as the Jetpack Compose compiler and Kotlinx Serialization) before emitting bytecode to downstream AGP desugaring and dexing pipelines.""",
    "walkthrough_en": """Inspecting the build pipeline execution order across Gradle, AGP, and Kotlinc:
```kotlin
// 1. settings.gradle.kts: Gradle plugin management & orchestration
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

// 2. build.gradle.kts (app module): AGP DSL configuration and Kotlin integration
plugins {
    alias(libs.plugins.android.application) // AGP plugin
    alias(libs.plugins.kotlin.android)      // Kotlin Android compiler plugin
    alias(libs.plugins.compose.compiler)    // Compose compiler plugin
}

android {
    namespace = "com.example.platform"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.example.platform"
        minSdk = 24
        targetSdk = 35
    }
}

// Build pipeline phases in DAG:
// Task 1: :app:checkKotlinGradlePluginConfigurationErrors
// Task 2: :app:processDebugResources (AAPT2 via AGP)
// Task 3: :app:compileDebugKotlin (kotlinc via Kotlin Plugin)
// Task 4: :app:dexBuilderDebug (D8 via AGP)
// Task 5: :app:packageDebug (AGP APK packaging)
```""",
    "short_en": """Gradle serves as the general build orchestration engine that constructs the task graph and manages caching. The Android Gradle Plugin extends Gradle with Android-specific tasks including manifest merging, resource compilation, and dex transformation. The Kotlin compiler transforms Kotlin sources into JVM bytecode while supporting compiler plugins like Compose and Serialization.""",
    "structured_en": """The Android build process is partitioned across Gradle, the Android Gradle Plugin, and the Kotlin compiler.
First, Gradle acts as the language-agnostic build automation engine. It evaluates project build scripts, resolves binary dependencies from remote repositories, constructs the directed acyclic task graph, and manages incremental execution and build caching.
Second, the Android Gradle Plugin adapts Gradle to the Android platform. AGP injects Android-specific domain extensions, processes Android resources via AAPT2, merges AndroidManifest files, coordinates D8 and R8 desugaring and dexing, and packages APK or App Bundle binaries.
Third, the Kotlin compiler transforms Kotlin source files into JVM bytecode. Operating within tasks scheduled by AGP, kotlinc processes annotations via KSP and integrates compiler plugins like Jetpack Compose before handing generated class files to downstream desugaring and dexing stages.""",
    "deep_senior_en": """Understanding the distinct boundaries between Gradle, the Android Gradle Plugin, and the Kotlin compiler is fundamental when troubleshooting CI build failures and optimizing pipeline throughput.
Gradle itself knows nothing about Android.
It is an extensible orchestration runtime that resolves dependencies into a deterministic lockfile, constructs a Directed Acyclic Graph of execution tasks, and evaluates input-output hashes to enable task up-to-date checks and build caching.
Google's Android Gradle Plugin hooks directly into Gradle's lifecycle.
AGP creates the Android build matrix across flavors and build types.
It compiles resources via AAPT2, validates and merges manifests, executes D8 and R8 transformations, and bundles DEX files, native libraries, and assets into final distribution artifacts.
Meanwhile, the Kotlin compiler operates as a specialized code generator within this pipeline.
Kotlinc parses source code, executes type resolution, and emits JVM bytecode.
Crucially, modern Android pipelines rely heavily on Kotlin compiler plugins: Jetpack Compose leverages a compiler plugin to transform composable functions into positional memoization calls, and Kotlin Symbol Processing executes lightweight annotation processing before byte compilation.
When a build breaks, a senior engineer diagnoses whether the root cause is a Gradle configuration failure, an AGP artifact merge conflict, or a kotlinc bytecode generation error. This architectural separation empowers engineering teams to isolate bottlenecks, maintain reproducible builds, and optimize continuous integration throughput across modern Android applications.""",
    "meta_ar": {
        "id": "BLD-01",
        "questionAr": "اشرح الأدوار المعمارية والفروق الجوهرية بين محرك Gradle وملحق أندرويد (AGP) ومترجم لغة كوتلن (Kotlin Compiler).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم منظومة بناء أندرويد، والفرق بين أداة تنسيق المهام العامة Gradle والملحق المخصص AGP ومترجم اللغة kotlinc، ومراحل تحويل الكود والموارد إلى DEX.",
        "concept_ar": "تنقسم عملية بناء تطبيقات أندرويد عبر ثلاث طبقات معمارية مستقلة ومتكاملة: محرك Gradle وهو نظام أتمتة عام يدير دورة حياة المشروع وحل الاعتماديات وبناء شجرة المهام DAG وإدارة التخزين المؤقت Build Cache دون دراية بطبيعة منصة أندرويد. وملحق أندرويد AGP وهو إضافة طورتها جوجل تخصص Gradle لبيئة أندرويد؛ حيث يضيف مهام معالجة الموارد بـ AAPT2 ودمج ملفات المانيفست وتوليد كلاسات R.java وتحويل البايت كود إلى ملفات DEX عبر محركي D8 و R8 وتجميع حزم APK و AAB. ومترجم كوتلن kotlinc وهو المسؤول عن تحويل كود كوتلن إلى بايت كود للـ JVM، ويتكامل مع ملحقات المترجم كـ Compose Compiler ومولدات الأكواد KSP قبل تسليم المخرجات لمراحل الـ Dexing التابعة لـ AGP.",
        "walkthrough_ar": """تتبع تسلسل تنفيذ مراحل البناء بين Gradle و AGP ومترجم كوتلن:
```kotlin
// 1. ملف settings.gradle.kts: إدارة محرك Gradle للملحقات
pluginManagement {
    repositories { google(); mavenCentral() }
}

// 2. ملف build.gradle.kts: تطبيق AGP ومترجم كوتلن
plugins {
    alias(libs.plugins.android.application) // AGP
    alias(libs.plugins.kotlin.android)      // Kotlinc
    alias(libs.plugins.compose.compiler)    // Compose Plugin
}

// تسلسل التنفيذ في شجرة المهام DAG:
// 1. :app:processDebugResources (AAPT2 عبر AGP)
// 2. :app:compileDebugKotlin (تحويل الكود إلى كلاسات JVM عبر kotlinc)
// 3. :app:dexBuilderDebug (تحويل الكلاسات إلى DEX عبر D8/AGP)
// 4. :app:packageDebug (تجميع ملف APK عبر AGP)
```""",
        "why_it_matters_ar": "يساعد المهندس الأول على تشخيص أعطال البناء المعقدة في الـ CI بدقة، ومعرفة الأداة المسؤولة عن كل خطأ لتسريع زمن التجميع وتفادي التخبط.",
        "worked_example_ar": "ظهور خطأ Unresolved Reference يحدد أن المشكلة في kotlinc، بينما فشل Duplicate Resources ينتمي لـ AAPT2 في AGP، وخطأ Circular Dependency يعود لإعدادات Gradle.",
        "trade_offs_ar": "الاعتماد على هذه المنظومة يوفر مرونة وأتمتة هائلة للتطبيقات الضخمة ولكنه يضيف تعقيداً كبيراً في استهلاك الرام وزمن إعداد شجرة المهام Configuration Phase.",
        "failure_modes_ar": "تحديث إصدار Gradle دون تحديث AGP المتوافق معه مما يعطل عملية البناء، أو تحميل مسؤولية أخطاء الموارد لمترجم كوتلن في حين أنها صادرة من AAPT2.",
        "production_perspective_ar": "في الشركات الكبرى، نثبت إصدارات Gradle Wrapper و AGP و Kotlin بدقة في الـ Version Catalog، ونراقب زمن كل مرحلة عبر Gradle Enterprise لتقليل وقت الـ CI.",
        "how_to_answer_ar": "ابدأ ببيان دور كل أداة بجملة مركزة: Gradle للمهام والاعتماديات، AGP لمنصة أندرويد ومواردها و DEX، و kotlinc لتوليد بايت كود كوتلن وتشغيل Compose.",
        "talking_points_ar": "مفهوم شجرة المهام DAG في Gradle، دور AAPT2 و D8/R8 في AGP، وتكامل Compose مع مترجم كوتلن.",
        "follow_ups_ar": "- **المحاور:** 'كيف يتكامل مترجم Compose Compiler مع هذه المنظومة؟'\n  **المرشح:** 'يعمل كمكون إضافي لمترجم كوتلن Kotlin Compiler Plugin؛ فيعترض دوال @Composable أثناء مرحلة توليد البايت كود ويضيف معلمات Composer وسياق التحديث اللحظي قبل تحويلها لـ DEX.'\n\n- **المحاور:** 'ما الفرق بين D8 و R8 في دور ملحق AGP؟'\n  **المرشح:** 'يقوم D8 بمجرد تحويل البايت كود إلى صيغة DEX مع الـ Desugaring، بينما يدمج R8 وظائف D8 مع تقليص الكود والتحسين وحذف الأجزاء الميتة وإخفاء الأسماء في خطوة واحدة.'",
        "self_check_ar": "هل وضحت الفروق الجوهرية بين الأدوات الثلاث؟ وهل بينت تسلسل التنفيذ في شجرة المهام وموقع Compose Compiler؟",
        "references_ar": f"- [Android Developers: Configure your build](https://developer.android.com/studio/build) — التوثيق الرسمي لمنظومة بناء أندرويد.\n- [Gradle User Manual: Build Lifecycle](https://docs.gradle.org/current/userguide/build_lifecycle.html) — الدليل الشامل لدورة حياة مهام Gradle.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يمثل Gradle محرك إدارة وتنسيق المهام وحل الاعتماديات وبناء شجرة التنفيذ، بينما يضيف ملحق أندرويد AGP مهام النظام المتخصصة كمعالجة الموارد بـ AAPT2 ودمج المانيفست وتوليد ملفات DEX، ويتولى مترجم كوتلن تحويل الأكواد إلى بايت كود للـ JVM مع تشغيل ملحقات مثل Compose.",
        "best_answer_ar": "تنقسم عملية بناء تطبيقات أندرويد بدقة بين محرك Gradle وملحق AGP ومترجم Kotlin.\n\nيقوم Gradle بدور المحرك التنفيذي العام غير المرتبط بنظام أندرويد؛ حيث يقرأ ملفات الإعدادات، ويبني شجرة المهام DAG، ويدير حل وتنزيل الاعتماديات وتخزين نتائج المهام Build Cache لتسريع البناء.\n\nويأتي ملحق أندرويد AGP كحزمة متخصصة من جوجل لتوسيع قدرات Gradle؛ فهو يضيف مهام خاصة بنظام أندرويد مثل معالجة الموارد عبر AAPT2، ودمج ملفات AndroidManifest، وتحويل بايت كود الجافا إلى صيغة DEX عبر D8 و R8، وتجميع حزم APK و AAB.\n\nأما مترجم كوتلن kotlinc، فيتولى تحويل كود كوتلن المصدري إلى بايت كود للـ JVM؛ ويتكامل مع ملحق AGP لتشغيل ملحقات المترجم الحيوية مثل مترجم Compose ومعالجات الرموز KSP قبل تسليم الملفات لمرحلة الـ Dexing.",
        "deep_answer_ar": "في هندسة البنية التحتية لتطبيقات أندرويد الضخمة، يعتبر التمييز بين مكونات منظومة البناء ركيزة أساسية لتشخيص أعطال خطوط الـ CI وتحسين سرعة التجميع.\n\nمحرك Gradle لا يعرف شيئاً عن ملفات أندرويد بطبيعته؛ فهو مجرد بيئة عامة تدير دورة حياة المشروع، وتقوم بحل شجرة الاعتماديات، وتحديد الاعتماديات المكررة، وجدولة المهام وفق شجرة موجهة لا حلقية DAG، وإدارة التخزين المؤقت للمهام Build Cache لضمان عدم إعادة تنفيذ ما لم يتغير.\n\nوهنا يتدخل ملحق أندرويد AGP ليغرس منطق منصة أندرويد بالكامل؛ فهو الذي ينشئ أبعاد البناء Flavors و Build Types، ويستدعي أداة AAPT2 لضغط وتوليد معرفات الموارد R.java، ويدمج ملفات المانيفست، ويشرف على تشغيل D8 لتحويل البايت كود إلى DEX وتشغيل R8 لتقليص الكود وحمايته.\n\nوفي المنتصف، يعمل مترجم كوتلن kotlinc كأداة توليد الكود؛ فهو لا يكتفي بترجمة الكود إلى كلاسات JVM، بل يدير تشغيل Kotlin Compiler Plugins كملحق Jetpack Compose الذي يحول الدوال إلى شجرة Positional Memoization، ومعالجات KSP لتوليد الكود قبل مرحلة التحويل النهائي للـ DEX، مما يمنح الفريق رؤية دقيقة لتحديد مصدر أي عطل في بيئة البناء. ويسمح هذا التمييز الهندسي الدقيق لفرق المنصات بتحسين كفاءة خطوط الـ CI وعزل المشاكل البرمجية وتوفير بيئة بناء حتمية ومستقرة لكافة المطورين."
    }
}

# ==========================================
# BLD-02: What are build types, product flavors, variants, and source sets?
# ==========================================
DATA["BLD-02"] = {
    "concept_en": """The Android Gradle Plugin structures multi-target releases across four foundational build abstractions:
- Build Types: Configure technical packaging, compilation, and optimization parameters for different deployment phases (e.g., debug vs release). They control code minification and shrinking (R8), debuggability flags, signing configurations, and applicationIdSuffix properties (e.g., .debug).
- Product Flavors: Represent distinct functional, commercial, or environmental variations of the app (e.g., free vs paid, or staging vs production). Flavors are organized under flavorDimensions to prevent naming collisions.
- Build Variants: The Cartesian product combining every configured product flavor across all dimensions with every build type. For example, two dimensions with two flavors each combined with two build types yields eight distinct build variants (e.g., demoStagingRelease).
- Source Sets: Directory structures (such as src/main, src/debug, src/demo, and src/demoStagingRelease) containing code and resources. AGP merges manifests hierarchically, overrides XML resources and assets by variant priority, but enforces strict class-path exclusivity where Java/Kotlin classes with identical fully-qualified names cannot coexist across overlapping active source sets.""",
    "walkthrough_en": """Configuring flavor dimensions, build types, and examining source set overrides:
```kotlin
android {
    flavorDimensions += listOf("environment", "tier")

    productFlavors {
        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
        }
        create("production") {
            dimension = "environment"
        }
        create("free") {
            dimension = "tier"
            buildConfigField("Boolean", "SHOW_ADS", "true")
        }
        create("premium") {
            dimension = "tier"
            buildConfigField("Boolean", "SHOW_ADS", "false")
        }
    }

    buildTypes {
        getByName("debug") {
            isDebuggable = true
            isMinifyEnabled = false
        }
        getByName("release") {
            isDebuggable = false
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}

// Resulting build variants matrix:
// 1. stagingFreeDebug, stagingFreeRelease
// 2. stagingPremiumDebug, stagingPremiumRelease
// 3. productionFreeDebug, productionFreeRelease
// 4. productionPremiumDebug, productionPremiumRelease
```""",
    "short_en": """Build types configure packaging and optimization settings like debugging and minification. Product flavors customize functional or environmental variations like staging versus production. Build variants represent the Cartesian product combining each flavor and build type. Source sets define hierarchical directories that merge code, resources, and manifests according to variant priority.""",
    "structured_en": """Configuring complex Android applications requires understanding the modular matrix composed of build types, product flavors, variants, and source sets.
First, build types define technical packaging properties for distinct development stages, configuring R8 minification, debuggability, signing configurations, and applicationId suffixes such as debug or release.
Second, product flavors customize application features, branding, or server environments along defined flavor dimensions, such as creating demo versus full versions or internal versus production endpoints.
Third, build variants represent the Cartesian product combining every configured flavor across dimensions with each build type, such as demoInternalRelease.
Fourth, source sets structure the project directory hierarchy. AGP merges manifests, XML resources, and assets according to strict priority where variant-specific source sets override flavor-specific sets, which in turn override the main codebase.""",
    "deep_senior_en": """Architecting multi-tenant or enterprise Android repositories requires mastering how Gradle and AGP compute build variants and merge source sets.
Build types govern packaging and optimization flags: the debug build enables debugging and disables R8 to preserve fast compilation, whereas release enforces R8 shrinking, obfuscation, and production signing.
Product flavors allow teams to maintain distinct versions of an application from a single codebase: we declare flavor dimensions such as environment (staging, production) and distribution (googlePlay, amazon).
AGP multiplies these dimensions against build types to compute the build variant matrix: two environments times two distributions times two build types yields eight distinct build variants.
Source sets provide the physical folder structure corresponding to this matrix.
Understanding AGP's merging rules is essential for production stability.
Manifest files merge hierarchically using the Manifest Merger tool, where variant-specific manifests take precedence over flavor manifests, and flavor manifests override src/main/AndroidManifest.xml.
Resources such as XML strings and drawables follow an identical override precedence.
However, Kotlin and Java source files cannot overlap: defining a class with the same fully-qualified name in both src/main and a flavor source set results in a duplicate class compilation error, requiring engineers to place polymorphic implementations in separate flavor source sets or extract shared logic into dedicated feature modules.""",
    "meta_ar": {
        "id": "BLD-02",
        "questionAr": "ما هي أنواع البناء (Build Types) ونكهات المنتج (Product Flavors) ومتغيرات البناء (Build Variants) ومجموعات المصادر (Source Sets)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مصفوفة بناء أندرويد، والفروق بين إعدادات التغليف والخصائص الوظيفية، وأبعاد النكهات وحساب الـ Variants، وقواعد دمج المصادر والموارد والمانيفست.",
        "concept_ar": "تنظم مصفوفة بناء أندرويد في AGP إصدارات التطبيق عبر أربعة مفاهيم أساسية: أنواع البناء (Build Types) وتحدد إعدادات التحسين والتغليف التقنية (مثل تفعيل التصحيح أو تفعيل تقليص الكود بـ R8 وتحديد لاحقة المعرف والتوقيع الرقمي). ونكهات المنتج (Product Flavors) وتحدد التباينات الوظيفية والبيئية للتطبيق (مثل نسخة مجانية مقابل مدفوعة أو بيئة اختبار مقابل إنتاج) وتنتظم تحت أبعاد تسمى flavorDimensions. ومتغيرات البناء (Build Variants) وهي ناتج الضرب الديكارتي لكافة النكهات عبر الأبعاد مع كل نوع بناء (مثل stagingFreeRelease). ومجموعات المصادر (Source Sets) وهي المجلدات التي تحتضن الكود والموارد؛ حيث تدمج ملفات المانيفست والموارد والصور هرمياً بحيث تلغي موارد المتغير موارد النكهة وتلغي النكهة موارد الكود الرئيسي، مع حظر تكرار أسماء كلاسات كوتلن لمنع أخطاء Duplicate Class.",
        "walkthrough_ar": """ضبط أبعاد النكهات وأنواع البناء واستعراض المتغيرات الناتجة:
```kotlin
android {
    flavorDimensions += listOf("env", "tier")

    productFlavors {
        create("staging") { dimension = "env"; applicationIdSuffix = ".stg" }
        create("prod") { dimension = "env" }
        create("free") { dimension = "tier" }
        create("paid") { dimension = "tier" }
    }

    buildTypes {
        getByName("debug") { isMinifyEnabled = false }
        getByName("release") { isMinifyEnabled = true }
    }
}
// ينتج 8 متغيرات: stagingFreeDebug, stagingFreeRelease, إلخ
```""",
        "why_it_matters_ar": "يتيح بناء تطبيقات متعددة البيئات والخصائص من مشروع واحد دون تكرار الكود، مما يسهل صيانة التطبيقات الكبرى وتوزيعها بكفاءة.",
        "worked_example_ar": "تطبيق يدعم بيئة تجريبية بمفتاح API مخصص ونسخة مجانية بإعلانات؛ يتم توليد نسخة stagingFreeDebug للاختبار الداخلي ونسخة prodPaidRelease للمتجر من نفس المشروع.",
        "trade_offs_ar": "تعدد النكهات يمنح مرونة عالية ولكنه يزيد تعقيد كود البناء ويضاعف عدد المهام ووقت الـ CI ويجعل اختبار كافة المتغيرات أمراً مكلفاً زمنياً.",
        "failure_modes_ar": "تسمية كلاس كوتلن بنفس الاسم والمسار في src/main وفي مجلد النكهة مما يسبب خطأ Duplicate Class وقت التجميع، أو تداخل صلاحيات المانيفست المدمجة.",
        "production_perspective_ar": "في المشروعات الكبرى، نقلل عدد النكهات إلى أدنى حد ممكن لتفادي بطء الـ CI، ونعتمد على ميزات الحسابات وحقن الاعتماديات بدلاً من النكهات المفرطة.",
        "how_to_answer_ar": "عرف كل مصطلح بجملة واضحة: Build Types للإعدادات التقنية، Flavors للخصائص والبيئات، Variants للناتج المدمج، و Source Sets للمجلدات وقواعد الدمج.",
        "talking_points_ar": "الضرب الديكارتي لأبعاد النكهات، أسبقية دمج المانيفست والموارد، وحظر تكرار كلاسات كوتلن بين المصادر المشتركة.",
        "follow_ups_ar": "- **المحاور:** 'لماذا لا يمكن تكرار نفس كلاس كوتلن في مجلد main ومجلد النكهة؟'\n  **المرشح:** 'لأن مترجم كوتلن لا يدمج الكلاسات البرمجية بل يقوم بتجميعها معاً في مسار كلاس واحد Classpath؛ ووجود نفس الكلاس مرتين يسبب تعارض Duplicate Class Definition، ولذا يوضع الكلاس المشترك في واجهة Interface وتنفذ بشكل منفصل في كل نكهة.'\n\n- **المحاور:** 'كيف يتم التعامل مع تعارض قيم المانيفست عند دمج النكهات؟'\n  **المرشح:** 'تعتمد أداة Manifest Merger قواعد أولوية واضحة؛ حيث يملك متغير البناء الكلمة العليا، يليه كود النكهة، ثم main، ويمكن استخدام أدوات التحكم مثل tools:replace لحسم التعارض صراحة.'",
        "self_check_ar": "هل شرحت الفرق بين Build Types و Flavors؟ وهل بينت مفهوم الضرب الديكارتي وقواعد دمج الموارد والمجلدات؟",
        "references_ar": f"- [Android Developers: Build variants overview](https://developer.android.com/build/build-variants) — الدليل الرسمي لإدارة متغيرات ونكهات البناء.\n- [Manifest Merger Tool](https://developer.android.com/build/manage-manifests) — قواعد أولوية دمج ملفات المانيفست في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تحدد Build Types إعدادات التغليف والتحسين كالتصحيح والتقليص بـ R8، بينما تمثل Product Flavors خصائص التطبيق كبيئات التجربة والإنتاج. وتنتج Build Variants من ضرب النكهات بأنواع البناء، في حين تحدد Source Sets مجلدات الكود والموارد التي تدمج هرمياً بحسب أولوية المتغير.",
        "best_answer_ar": "تشكل مصفوفة بناء أندرويد نظاماً متكاملاً لإدارة إصدارات التطبيق المختلفة من قاعدة كود برمجية واحدة.\n\nتحدد أنواع البناء Build Types إعدادات التجميع والتحسين الهندسي؛ مثل تفعيل تصحيح الأخطاء في نسخة Debug، أو تفعيل تقليص الكود بـ R8 والتوقيع الرقمي في نسخة Release.\n\nأما نكهات المنتج Product Flavors، فتحدد الاختلافات الوظيفية والبيئية للتطبيق عبر أبعاد Flavors؛ مثل إنشاء نسخة مجانية وأخرى مدفوعة، أو التبديل بين خوادم الاختبار Staging وخوادم الإنتاج Production.\n\nوتمثل متغيرات البناء Build Variants ناتج الضرب الديكارتي بين كافة النكهات وأنواع البناء؛ فدمج نكهتين مع نوعي بناء ينتج أربعة متغيرات مستقلة.\n\nوتوفر مجموعات المصادر Source Sets الهيكل الشجري للمجلدات؛ حيث يقوم نظام أندرويد بدمج ملفات المانيفست والموارد والصور وفق أولوية صارمة تعطي الأسبقية للمتغير المحدد على حساب النكهة ثم الكود الرئيسي.",
        "deep_answer_ar": "في قيادة المشروعات الكبرى، يتيح الاستخدام المتقن لمتغيرات البناء ومجموعات المصادر دعم عشرات العملاء والبيئات التشغيلية دون تكرار الكود المصدري.\n\nتتحكم Build Types في خصائص التحويل البرمجي والأمان؛ فنحن نخصص نسخة Debug بتعطيل R8 لتسريع زمن التجميع اليومي وإضافة لاحقة .debug للمعرف لمنع تعارض التثبيت، بينما نضبط Release لتقليص الكود وحمايته. وتأتي Product Flavors لتفصل بين بيئات التشغيل أو باقات الاشتراك عبر أبعاد مخصصة كـ environment و tier.\n\nويقوم AGP بحساب مصفوفة الـ Build Variants بضرب هذه الأبعاد؛ فوجود بعدين لكل منهما خياران مع نوعي بناء يولد ثمانية متغيرات مستقلة مثل stagingPaidRelease.\n\nوهنا تبرز أهمية فهم قواعد دمج مجموعات المصادر Source Sets؛ فملفات المانيفست والموارد كالنصوص والصور تدمج هرمياً بحيث تلغي موارد المتغير موارد النكهة وتلغي موارد النكهة كود src/main. ولكن يختلف الوضع تماماً في كود كوتلن؛ حيث يحظر تكرار نفس الكلاس في main ونكهة فرعية لتفادي أخطاء Duplicate Class، مما يلزمنا بعزل الاختلافات في واجهات Interfaces وتطبيقها داخل نكهات مستقلة لضمان معمارية نظيفة. كما نلزم الفرق بإنشاء اختبارات وحدة آلية لكل نكهة على حدة، لضمان توافق مصادر الأكواد المدمجة مع المتغيرات المستهدفة ومنع أي مفاجآت برمجية عند تجميع نسخ الإنتاج."
    }
}

# ==========================================
# BLD-03: Compare APK and Android App Bundle (AAB).
# ==========================================
DATA["BLD-03"] = {
    "concept_en": """Android binary distribution distinguishes between standalone deployment archives and optimized dynamic publishing artifacts:
- APK (Android Package): The legacy, standalone container executable directly by Android's package manager. A universal APK bundles compiled DEX code, assets, and uncompressed native libraries (.so) across all device ABIs (armeabi-v7a, arm64-v8a, x86, x86_64) alongside all screen density assets and language resources. It is ideal for local development, QA testing, internal enterprise sideloading, and alternative stores, but results in substantial download and disk bloat for end users.
- AAB (Android App Bundle): The modern publishing standard mandated by Google Play. An AAB is an uncompressed zip containing modular code, compiled resources, and protocol buffer metadata that cannot be installed directly on a device. Google Play processes the bundle via bundletool to dynamically generate and sign configuration-split APKs tailored to each user's specific processor architecture, display density, and active language, reducing download footprints by up to 35% while unlocking Dynamic Feature Modules on-demand.""",
    "walkthrough_en": """Inspecting App Bundle configuration and testing local split generation with bundletool:
```bash
# 1. Generate AAB using Gradle
./gradlew :app:bundleRelease

# 2. Use Google's bundletool to test split APK generation for a connected device
bundletool build-apks \
    --bundle=app/build/outputs/bundle/release/app-release.aab \
    --output=app-splits.apks \
    --connected-device

# 3. Install the tailored split APK set onto the hardware
bundletool install-apks --apks=app-splits.apks

# Resulting Split APKs installed on device:
# - base-master.apk (Core DEX and application code)
# - base-arm64_v8a.apk (Target ABI native binaries only)
# - base-xxhdpi.apk (Target screen density drawables only)
# - base-ar.apk (Active device locale strings only)
```""",
    "short_en": """An APK is a monolithic, installable archive containing code and resources for all densities, ABIs, and languages, suitable for direct device sideloading. An Android App Bundle is a publishing artifact required by Google Play that uses dynamic delivery to generate optimized, device-specific split APKs, significantly reducing user download sizes.""",
    "structured_en": """Evaluating APK and Android App Bundle requires distinguishing standalone device installers from dynamic publishing artifacts.
First, an APK is the legacy packaging format directly executable by the Android OS package manager. A universal APK bundles every compiled DEX file, native library for all ABIs (armeabi-v7a, arm64-v8a, x86_64), and resource qualifiers, making it convenient for local debugging and enterprise sideloading but bloated for end users.
Second, an Android App Bundle is Google Play's mandatory publishing standard. An AAB contains compiled modules and metadata but cannot be installed directly on hardware.
Third, Google Play processes the uploaded AAB via bundletool to generate split APKs. Each user receives a custom tailored APK set containing only the base code, their device's specific screen density, active language, and target processor ABI, reducing app download sizes by up to thirty-five percent.""",
    "deep_senior_en": """In modern Android release engineering, understanding the transition from monolithic APKs to Android App Bundles is vital for app performance, download conversion, and modular architecture.
A universal APK carries immense operational waste.
When a user on an arm64-v8a device with an xxhdpi display downloads a fat APK, they download megabytes of unused 32-bit and x86 native binaries, alongside unneeded low-density assets and dozens of unselected localized language strings.
This unnecessary bloat increases abandonment rates on cellular connections.
Google resolved this by introducing the Android App Bundle format.
An AAB is an uncompressed publishing archive containing protocol buffer metadata, compiled DEX code, and resources partitioned into modules.
When published to Google Play, the Play Console leverages bundletool to generate a configuration-split APK set.
When a user installs the application, Google Play serves a minimal base APK paired with split APKs matching their exact device architecture, screen density, and device locale.
This split delivery reduces user download footprints by fifteen to thirty-five percent.
Furthermore, AABs unlock advanced distribution capabilities that APKs cannot support: Dynamic Feature Modules allow large non-critical features, such as AR cameras or checkout modules, to be downloaded on-demand at runtime via the Play Core library, keeping the initial install payload lightweight.""",
    "meta_ar": {
        "id": "BLD-03",
        "questionAr": "قارن بين حزمة التطبيق التقليدية (APK) وحزمة نشر أندرويد الحديثة (AAB).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الفرق بين حزم التثبيت المباشرة وحزم النشر السحابية، وآلية عمل التوزيع الديناميكي Dynamic Delivery عبر bundletool، ومفهوم Split APKs وتوفير المساحة.",
        "concept_ar": "يميز نظام أندرويد بين وسائط التثبيت المباشرة ووسائط النشر المحسنة: حزمة APK هي الصيغة التقليدية القابلة للتثبيت المباشر على النظام عبر مدير الحزم PackageManager أو التثبيت اليدوي Sideloading؛ وتحتوي الحزمة الشاملة Universal APK على كافة ملفات الـ DEX والمكتبات المترجمة C++ لكافة المعالجات (arm64, x86) وكافة أحجام الصور واللغات، مما يجعلها ملائمة للاختبار الداخلي ولكنها متضخمة جداً للمستخدم النهائي. أما حزمة AAB فهي صيغة النشر الإلزامية في متجر Google Play؛ وهي أرشيف وسيط يضم الكود والموارد الموصفة بـ Protocol Buffers ولا يثبت على الهاتف مباشرة، بل تعالجه جوجل عبر أداة bundletool لإنتاج حزم مجزأة Split APKs ترسل لكل جهاز ما يحتاجه فقط بحسب معالجه وشاشته ولغته، مما يوفر حتى 35% من الحجم ويدعم الميزات الديناميكية عند الطلب.",
        "walkthrough_ar": """بناء حزمة AAB واختبار توليد الحزم المجزأة محلياً بـ bundletool:
```bash
# 1. توليد حزمة AAB عبر Gradle
./gradlew :app:bundleRelease

# 2. توليد الحزم المجزأة للجهاز المتصل عبر bundletool
bundletool build-apks \
    --bundle=app/build/outputs/bundle/release/app-release.aab \
    --output=app.apks --connected-device

# 3. تثبيت الحزم المجزأة المخصصة على الهاتف
bundletool install-apks --apks=app.apks
# الحزم المثبتة: base.apk + arm64.apk + xxhdpi.apk + ar.apk
```""",
        "why_it_matters_ar": "يقلل حجم تنزيل التطبيق بشكل كبير مما يرفع معدلات اكتمال التثبيت من المتاجر ويوفر باقة الإنترنت وسعة التخزين لدى المستخدم.",
        "worked_example_ar": "تطبيق يحتوي مكتبات C++ ضخمة؛ بحزمة APK يبلغ حجمه 85 ميجابايت، وبتحويله لـ AAB وتجزئته يستقبل مستخدم هاتف Pixel حزمة بحجم 28 ميجابايت فقط.",
        "trade_offs_ar": "حزمة AAB توفر حجماً فائق الصغر وتدعم الميزات الديناميكية ولكنها لا تثبت مباشرة وتلزم المطور بالاعتماد على خوادم Google Play لتوليد الحزم النهائية وتوقيعها.",
        "failure_modes_ar": "محاولة تثبيت ملف .aab مباشرة على الهاتف بأمر adb install مما يفشل فوراً، أو عدم اختبار الحزم المجزأة محلياً بـ bundletool قبل إطلاق الإصدار.",
        "production_perspective_ar": "في المشروعات الكبرى، نصدر AAB للمتجر الرسمي، ونولد حزم Universal APK عبر CI لتوزيعها على فرق الاختبار الداخلي وعبر منصات Firebase App Distribution.",
        "how_to_answer_ar": "ابدأ بالمقارنة الجوهرية: APK حزمة تثبيت مدمجة لكافة الأجهزة، بينما AAB حزمة نشر سحابية يجزئها المتجر عبر bundletool لتوليد Split APKs مخصصة لكل هاتف.",
        "talking_points_ar": "مفهوم Split APKs، دور أداة bundletool، تقليص الحجم بنسبة 35%، ودعم Dynamic Feature Modules.",
        "follow_ups_ar": "- **المحاور:** 'كيف يمكنك اختبار حزمة AAB على جهاز حقيقي قبل رفعها للمتجر؟'\n  **المرشح:** 'باستخدام أداة bundletool الرسمية من جوجل؛ فنقوم ببناء ملف apks مخصص للجهاز المتصل بـ build-apks --connected-device ثم تثبيته بأمر install-apks للتأكد من عمل كافة المكونات المجزأة.'\n\n- **المحاور:** 'ما هي الميزات الديناميكية Dynamic Feature Modules التي تدعمها AAB؟'\n  **المرشح:** 'هي وحدات برمجية تعزل الميزات غير الأساسية مثل الواقع المعزز أو الدفع المتقدم ليتم تنزيلها لاحقاً عبر Play Core عند فتح المستخدم لتلك الشاشة فقط، مما يبقي حجم التثبيت الأولي خفيفاً.'",
        "self_check_ar": "هل وضحت لماذا لا يمكن تثبيت AAB مباشرة؟ وهل شرحت دور bundletool وتوفير الحجم والميزات الديناميكية؟",
        "references_ar": f"- [Android Developers: About Android App Bundles](https://developer.android.com/guide/app-bundle) — التوثيق الرسمي لحزم النشر AAB ومزاياها.\n- [bundletool Documentation](https://developer.android.com/tools/bundletool) — أداة سطر الأوامر لمعالجة حزم AAB واختبار الحزم المجزأة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يمثل APK حزمة تثبيت مدمجة وكاملة تضم كافة اللغات والمعالجات وكثافات الشاشات وتثبت مباشرة على الأجهزة، بينما يمثل AAB صيغة نشر إلزامية لمتجر Google Play تتيح تجزئة التطبيق لتوليد حزم split APKs مخصصة لمواصفات كل جهاز، مما يقلل حجم التنزيل بشكل هائل.",
        "best_answer_ar": "تختلف حزمة التطبيق التقليدية APK عن حزمة النشر الحديثة AAB من حيث بنية التوزيع وتجربة المستخدم.\n\nحزمة APK هي ملف التثبيت المباشر القابل للتشغيل على نظام أندرويد عبر التثبيت اليدوي Sideloading أو بيئة التطوير؛ ولكنها حزمة ضخمة وشاملة تحتوي على كود كافة المعالجات ABIs مثل arm64 و x86، وكافة كثافات الصور واللغات، مما يهدر سعة التخزين وباقة الإنترنت للمستخدم.\n\nأما حزمة AAB، فهي صيغة النشر القياسية الإلزامية في متجر Google Play؛ وهي لا تثبت على الجهاز مباشرة، بل يقوم المتجر بمعالجتها عبر أداة bundletool لتوليد حزم مجزأة Split APKs.\n\nوعند قيام المستخدم بالتحميل، يرسل المتجر حزمة أساسية مدمجة مع ملفات تتطابق حصرياً مع معالج هاتفه وكثافة شاشته ولغته المختارة، مما يوفر حتى 35 بالمئة من حجم التنزيل ويدعم تحميل الميزات الإضافية Dynamic Features عند الطلب.",
        "deep_answer_ar": "في هندسة المنصات، يمثل الانتقال من حزم APK إلى AAB نقلة نوعية في تحسين مؤشرات التحميل وتقليل معدلات التراجع أثناء التنزيل من المتاجر.\n\nالحزمة التقليدية Fat APK تجبر مستخدم هاتف حديث يعمل بمعالج arm64 وشاشة فائقة الدقة على تنزيل مكتبات C++ لمعالجات x86 القديمة وكافة أحجام الصور من mdpi إلى xxxhdpi وعشرات اللغات غير المستخدمة، مما يضخم حجم الملف ويستهلك باقة الهاتف ويقلل من معدل اكتمال التثبيت بنسب ملحوظة.\n\nلذلك أصبح تنسيق Android App Bundle هو المعيار الإلزامي؛ فهو ملف وسيط منظم يحتوي على كود المشروع مقسماً لوحدات وموصوفاً ببيانات Protocol Buffers. وتتولى منصة Google Play استخراج حزم مقسمة Split APKs عبر أداة bundletool؛ بحيث يستقبل هاتف المستخدم حزمة كود أساسية مرفقة بحزم منفصلة لمعالجه وشاشته ولغته فقط.\n\nوبالإضافة لتقليص الحجم بنسبة تتجاوز ثلاثين بالمئة، تتيح حزم AAB معمارية الوحدات الديناميكية Dynamic Feature Modules؛ حيث نتمكن من عزل الميزات الضخمة مثل مسح المستندات أو الواقع المعزز وتنزيلها برمجياً عبر Play Core فقط عند حاجة المستخدم إليها، مما يجعل التطبيق الأساسي فائق الصغر وسريع التثبيت. كما نوظف ميزة حزم الأصول Play Feature Delivery لتسليم الملفات الصوتية والتصميمات الضخمة للمستخدمين حسب الحاجة، مما يحسن تجربة المستخدم ويزيد معدلات الاحتفاظ بالتطبيق."
    }
}

# ==========================================
# BLD-04: What is the difference between debug and release signing?
# ==========================================
DATA["BLD-04"] = {
    "concept_en": """Application signing in Android guarantees cryptographic identity, author authentication, and update integrity across the application lifecycle:
- Debug Signing: Utilizes an automatically generated keystore (~/.android/debug.keystore) provisioned with well-known default credentials (alias androiddebugkey, password android) and a 30-year validity window. Its purpose is to facilitate immediate local development, debugging, and emulator testing without administrative friction. Because debug certificates are public and non-repudiable, they offer zero real-world security and are strictly rejected by public app stores.
- Release Signing: Utilizes a cryptographically protected private keystore (JKS or PKCS12) protected by strong passwords and enterprise key management. Release signing establishes immutable cryptographic author ownership. Android's PackageManager strictly enforces signature continuity: an installed application cannot be updated unless the incoming package signature matches the existing installation's signing certificate, defending private SQLite databases and Keystore secrets against unauthorized package replacement.
- Play App Signing: Modern industry standard where the developer signs uploads using an Upload Key, while Google Play retains the master App Signing Key within tamper-resistant infrastructure, safely signing and distributing device-specific split APKs.""",
    "walkthrough_en": """Configuring signing configurations securely using environment variables:
```kotlin
android {
    signingConfigs {
        create("release") {
            // Retrieve secrets securely from CI environment or Key Management System
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "keystore/release.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = System.getenv("KEY_ALIAS")
            keyPassword = System.getenv("KEY_PASSWORD")
            enableV1Signing = true // JAR Signature Scheme
            enableV2Signing = true // APK Signature Scheme v2 (Full binary hash)
        }
    }

    buildTypes {
        getByName("debug") {
            // Uses standard debug keystore automatically
        }
        getByName("release") {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
        }
    }
}
```""",
    "short_en": """Debug signing uses an auto-generated, insecure keystore with known credentials for local development and debugging on emulators. Release signing requires a protected, cryptographically strong private keystore that establishes application identity, guarantees update continuity, and gates production distribution, often secured via Google Play App Signing.""",
    "structured_en": """Distinguishing debug from release signing is essential for mobile application security and distribution integrity.
First, debug signing uses an automated keystore generated by the Android SDK upon installation. Stored locally with default passwords and a thirty-year lifespan, it enables frictionless local deployment across developer workstations and emulators, but offers zero cryptographic security and is rejected by production stores.
Second, release signing secures the production application binary using a private, encrypted keystore protected by strict access controls and strong cryptographic hashing algorithms.
Third, Android's package manager enforces signature continuity upon app updates: an existing app rejects upgrades signed with an alternate certificate.
Fourth, modern distribution leverages Google Play App Signing, decoupling the developer's upload key from the master distribution key maintained within Google's secure hardware infrastructure.""",
    "deep_senior_en": """In Android security architecture, cryptographic signing is not an optional publishing step; it forms the bedrock of application identity, inter-process security permissions, and update continuity.
The debug keystore is intentionally insecure.
Generated automatically at ~/.android/debug.keystore, it uses hardcoded credentials (password 'android' and alias 'androiddebugkey').
Its sole purpose is allowing developers to deploy code locally without managing key hierarchies.
Because debug credentials are universally known, shipping an app with debug signing would allow any malicious actor to forge updates and hijack user sandboxes.
In contrast, release signing uses an encrypted PKCS12 or JKS keystore generated with strong cryptographic algorithms like RSA 4096-bit or Elliptic Curve.
The signature certificate guarantees provenance: Android's PackageManager verifies that every incoming APK update matches the signing certificate of the installed application before allowing an upgrade, protecting the app's SQLite databases, EncryptedSharedPreferences, and signature-level custom permissions from tampering.
For modern enterprise deployments, we enforce Google Play App Signing.
We generate an Upload Key to sign release bundles in our CI pipeline.
Google Play validates the upload signature, replaces it with the master app signing key stored within Google's tamper-resistant Key Management Service, and distributes the final split APKs.
This isolates developers from catastrophic key-loss scenarios, allowing secure upload key rotation without stranding existing production users.""",
    "meta_ar": {
        "id": "BLD-04",
        "questionAr": "ما هو الفارق بين التوقيع الرقمي للتصحيح (Debug Signing) وتوقيع الإصدارات الرسمية (Release Signing) في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم منظومة التوقيع الرقمي في أندرويد، والفروق الأمنية بين المفاتيح، ومبدأ استمرارية التوقيع Signature Continuity، ومفهوم خدمة توقيع جوجل Play App Signing.",
        "concept_ar": "يمثل التوقيع الرقمي في أندرويد الركيزة المشفرة لتحديد هوية المطور وضمان سلامة التحديثات: توقيع التصحيح (Debug Signing) يعتمد على مفتاح يولد تلقائياً في جهاز المطور ببيانات مكشوفة للجميع وصلاحية 30 عاماً، وهدفه تسهيل اختبار التطبيق محلياً دون تعقيدات، ويحظر استخدامه للمتاجر الرسمية لغياب الأمان. وتوقيع الإنتاج (Release Signing) يستخدم مفتاحاً سرياً مشفراً بدرجة حماية عسكرية وخوارزميات تشفير قوية؛ وهو الذي يثبت ملكية المطور للتطبيق ويحمي بياناته التخزينية؛ فنظام أندرويد يرفض تثبيت أي تحديث قادم بمفتاح مغاير للمفتاح الأصلي عبر مبدأ استمرارية التوقيع (Signature Continuity). وتعتمد التطبيقات الحديثة على خدمة Play App Signing؛ حيث يوقع المطور الحزمة بمفتاح رفع Upload Key، بينما تتولى خوادم جوجل تأمين مفتاح التوقيع الرئيسي في بنية تحتية سحابية مشفرة وتوقيع الحزم المجزأة للمستخدمين بأمان تام.",
        "walkthrough_ar": """تأمين إعدادات توقيع الـ Release عبر المتغيرات البيئية:
```kotlin
android {
    signingConfigs {
        create("release") {
            // جلب الأسرار بأمان من متغيرات بيئة الـ CI
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "keystore.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = System.getenv("KEY_ALIAS")
            keyPassword = System.getenv("KEY_PASSWORD")
            enableV1Signing = true
            enableV2Signing = true // توقيع أندرويد v2 للتحقق من سلامة البايتات
        }
    }
    buildTypes.getByName("release") {
        signingConfig = signingConfigs.getByName("release")
    }
}
```""",
        "why_it_matters_ar": "يحمي التطبيق من التزوير وانتحال الشخصية، ويضمن عدم تعطل تحديثات التطبيق لدى ملايين المستخدمين بسبب فقدان المفاتيح الرقمية.",
        "worked_example_ar": "محاولة تثبيت تحديث لتطبيق بنكي موقع بمفتاح مختلف عن المفتاح المثبت على الهاتف؛ يرفض نظام أندرويد العملية فوراً بخطأ INSTALL_FAILED_UPDATE_INCOMPATIBLE لحماية بيانات المستخدم.",
        "trade_offs_ar": "إدارة مفاتيح الـ Release محلياً تتطلب حماية فائقة لمنع تسربها أو ضياعها، بينما يمنح Play App Signing أماناً كبيراً ومرونة تدوير المفاتيح على حساب الاعتماد على جوجل.",
        "failure_modes_ar": "تضمين ملف Keystore وكلمات السر صراحة في كود Git العام، أو فقدان مفتاح الـ Release الأصلي دون تفعيل Play App Signing مما يعطل تحديث التطبيق للأبد.",
        "production_perspective_ar": "في الشركات الكبرى، نمنع نهائياً حفظ المفاتيح في المستودع ونمررها لـ CI عبر أسرار مشفرة أو Vault، ونلزم المشروعات بالاشتراك في Play App Signing.",
        "how_to_answer_ar": "قارن بين الغرض: Debug للتطوير السريع بمفتاح افتراضي، و Release للحماية وإثبات الهوية، واشرح مبدأ Signature Continuity ودور خدمة Play App Signing.",
        "talking_points_ar": "مخاطر مفتاح Debug الافتراضي، مبدأ استمرارية التوقيع، دور مخططي التوقيع V1 و V2، ومزايا Play App Signing في حماية المفتاح الرئيسي.",
        "follow_ups_ar": "- **المحاور:** 'ماذا يحدث إذا فقدت مفتاح التوقيع Release Key لتطبيق منشور دون استخدام Play App Signing؟'\n  **المرشح:** 'يصبح من المستحيل تقنياً إصدار أي تحديث للتطبيق؛ لأن نظام أندرويد ومتجر Google Play سيرفضان أي مفتاح بديل، ويضطر المطور لرفع تطبيق جديد كلياً باسم حزمة Package Name جديد وفقدان كافة المستخدمين الحاليين.'\n\n- **المحاور:** 'ما الفرق بين مخطط التوقيع APK Signature Scheme v1 و v2؟'\n  **المرشح:** 'مخطط v1 يوقع الملفات الفردية داخل الأرشيف كملف JAR مما يسمح بتعديل محتويات الميتا داتا، بينما يوقع v2 كامل بايتات ملف الـ APK عبر فحص التجزئة الثنائي Binary Hash، مما يجعله أسرع في التحقق عند التثبيت وأكثر مناعة ضد التلاعب.'",
        "self_check_ar": "هل وضحت الفارق الأمني بين المفتاحين؟ وهل شرحت مبدأ Signature Continuity والنتائج المترتبة على فقدان المفتاح ودور Play App Signing؟",
        "references_ar": f"- [Android Developers: Sign your app](https://developer.android.com/studio/publish/app-signing) — الدليل الشامل لتوقيع التطبيقات في أندرويد.\n- [Google Play: Use Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756) — التوثيق الرسمي لخدمة إدارة مفاتيح التوقيع السحابية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يستخدم Debug Signing مفتاحاً مؤقتاً تلقائي التوليد ببيانات معروفة ومكشوفة للتطوير المحلي، بينما يتطلب Release Signing مفتاحاً سرياً مشفراً ومحمياً يحدد هوية التطبيق ويضمن استمرارية التحديثات في أندرويد، وتديره المتاجر الحديثة عبر خدمة توقيع التطبيقات Play App Signing.",
        "best_answer_ar": "يمثل التوقيع الرقمي ركيزة الأمان الأساسية لهوية التطبيق وصلاحية التحديثات في نظام أندرويد.\n\nتوقيع التصحيح Debug Signing يعتمد على ملف keystore يولد تلقائياً في جهاز المطور بكلمات سر افتراضية مكشوفة وصلاحية 30 عاماً؛ وهدفه تسهيل تجربة وتشغيل التطبيق على المحاكي وأجهزة الاختبار دون أي إجراءات أمنية، ويحظر رفع التطبيقات الموقعة به للمتاجر.\n\nأما توقيع الإنتاج Release Signing، فيستخدم مفتاحاً سرياً مشفراً بدرجة حماية عسكرية وخوارزميات تشفير قوية؛ وهو الذي يثبت ملكية المطور للتطبيق ويحمي بياناته التخزينية؛ فنظام أندرويد يرفض تثبيت أي تحديث قادم بمفتاح مغاير للمفتاح الأصلي.\n\nوفي التطبيقات الحديثة، نعتمد على خدمة Play App Signing من جوجل؛ حيث نوقع الحزمة بمفتاح رفع Upload Key، بينما تتولى جوجل حماية مفتاح التوقيع الرئيسي في بنيتها التحتية الآمنة، مما يمنع ضياع التطبيق في حال فقدان المفتاح المحلي.",
        "deep_answer_ar": "في هندسة أمان منصات الموبايل، لا يعد التوقيع الرقمي مجرد خطوة شكلية، بل هو هوية التطبيق الأساسية التي تحمي حاويات التخزين وأذونات الـ Signature Permissions عبر النظام.\n\nمفتاح الـ Debug مصمم للتطوير فقط؛ فهو يولد تلقائياً في مجلد المستخدم ببيانات سرية مكشوفة للجميع بكلمة سر android، واستخدامه في الإنتاج يمثل كارثة تتيح لأي مخترق تزوير التطبيق وسرقة بيانات المستخدمين.\n\nفي المقابل، يتطلب توقيع الإنتاج Release Signing ملف JKS أو PKCS12 محمي بخوارزميات تشفير متقدمة مثل RSA 4096-bit. وتكمن أهميته في أن مدير حزم أندرويد PackageManager يفرض مبدأ استمرارية التوقيع Signature Continuity؛ فلا يمكن لأي هاتف تثبيت تحديث لتطبيق بنكي ما لم يكن التحديث موقعاً بنفس الشهادة الرقمية للمحافظة على قواعد بيانات SQLite ومساحة التخزين المشفرة.\n\nولتأمين خطوط الإنتاج المؤسسية، نعتمد على Google Play App Signing؛ فنقوم بإنشاء Upload Key تستخدمه خوادم الـ CI للتوقيع، وعند الرفع تتولى جوجل فحص المفتاح واستبداله بمفتاح التوقيع الفعلي المخزن داخل خوادم الأمان العتادية KMS التابعة لجوجل، مما يوفر حماية مطلقة ويتيح تدوير مفتاح الرفع عند تسربه دون الإضرار بالمستخدمين القائمين. ونحرص دائماً على تطبيق التوقيع المزدوج V1 و V2 لدعم إصدارات أندرويد القديمة والحديثة بالتوازي، مما يضمن أقصى حماية للبيانات مع توافق شامل مع كافة أجهزة المستخدمين."
    }
}

# ==========================================
# BLD-05: What are build cache, configuration cache, and incremental compilation?
# ==========================================
DATA["BLD-05"] = {
    "concept_en": """Gradle accelerates multi-module build velocity through three distinct optimization tiers operating across different phases of the build lifecycle:
- Incremental Compilation: Operates within specific compilation tasks (such as compileKotlin or compileJava). Instead of recompiling all source files across a module, the compiler tracks source changes and re-processes only the modified files and their affected ABI consumers, drastically slashing iteration loops during local active development.
- Build Cache: Operates across the task execution phase. It maps immutable task inputs (source files, dependencies, compiler options, environment flags) to a cryptographic hash. If a task's hash matches an entry in the local or remote cache, Gradle skips task execution entirely and unpacks the pre-computed outputs directly into the build directory (FROM-CACHE). Remote Build Caching allows CI build results to be shared with local developer machines.
- Configuration Cache: Operates during Gradle's initial evaluation phase. It caches the resulting Directed Acyclic Graph (DAG) of tasks after evaluating settings.gradle.kts and build.gradle.kts files. On subsequent builds where build scripts remain untouched, Gradle bypasses project configuration entirely and proceeds straight to task execution, saving tens of seconds on multi-module codebases.""",
    "walkthrough_en": """Configuring build cache, configuration cache, and remote caching in Gradle:
```kotlin
// 1. gradle.properties: Enable modern caching optimizations
org.gradle.caching=true
org.gradle.configuration-cache=true
kotlin.incremental=true
org.gradle.parallel=true
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC

// 2. settings.gradle.kts: Configure local and remote build caching
buildCache {
    local {
        isEnabled = true
        removeUnusedEntriesAfterDays = 7
    }
    remote<HttpBuildCache> {
        url = uri("https://cache.internal.company.com/cache/")
        isPush = System.getenv("CI") == "true" // Only CI pushes to remote cache
        credentials {
            username = System.getenv("CACHE_USER")
            password = System.getenv("CACHE_PASSWORD")
        }
    }
}
```""",
    "short_en": """Incremental compilation recompiles only modified source files within a task. Build caching skips task execution entirely by reusing stored outputs matched by input hashes, shareable via remote CI caches. Configuration caching serializes the task graph, skipping build script evaluation when configuration has not changed to achieve instantaneous execution starts.""",
    "structured_en": """Optimizing Android build performance requires understanding how Gradle accelerates execution across distinct build phases.
First, incremental compilation operates within compiler tasks. The Kotlin compiler tracks changes and re-processes only edited classes and direct ABI dependents rather than recompiling entire modules.
Second, the build cache operates across task execution. By hashing task inputs including source code, dependencies, and build flags, Gradle matches pre-computed outputs from local disk or a shared remote cache, skipping execution completely with a FROM-CACHE status.
Third, the configuration cache optimizes Gradle's initial phase. Evaluating complex multi-module build scripts into a task graph consumes significant time; the configuration cache records this graph to disk, skipping build script evaluation entirely on subsequent runs whenever build configuration remains unchanged.""",
    "deep_senior_en": """In large enterprise Android repositories spanning dozens or hundreds of Gradle modules, build times dictate developer velocity and engineering costs.
We treat build acceleration through a three-tier performance pyramid.
At the bottom tier sits incremental compilation.
Managed by the Kotlin Gradle Plugin, it observes source file modifications.
If an engineer modifies private implementation details inside a class without changing its public Abstract Binary Interface (ABI), kotlinc recompiles only that isolated file without invalidating downstream dependent modules.
In the middle tier sits Gradle's Build Cache.
While incremental compilation optimizes within a single task, build caching eliminates task execution altogether.
Gradle computes an SHA-256 fingerprint of all task inputs: source bytecodes, compiler flags, and classpath dependencies.
If an exact match exists, Gradle fetches the stored artifact, producing a FROM-CACHE outcome.
In our platform CI, we maintain a remote HTTP build cache: CI pipelines seed the cache with master branch artifacts, allowing developers pulling fresh branches to download pre-compiled DEX and class files instead of rebuilding locally.
At the top tier sits the Configuration Cache.
Evaluating hundreds of build.gradle.kts files to construct the task graph often consumes thirty to sixty seconds before any code compiles.
Configuration caching serializes the resolved task graph to disk; on subsequent invocations, Gradle bypasses script evaluation entirely, instantly beginning task execution.""",
    "meta_ar": {
        "id": "BLD-05",
        "questionAr": "ما هي ذاكرة التخزين المؤقت للبناء (Build Cache) والتخزين المؤقت للإعدادات (Configuration Cache) والتجميع التزايدي (Incremental Compilation) في Gradle؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم آليات تسريع زمن البناء في Gradle، والتمييز بين مراحل الـ Configuration والـ Execution، والتحقق التزايدي على مستوى المهام، والتخزين السحابي المشترك Remote Build Cache.",
        "concept_ar": "تعتمد Gradle على ثلاث طبقات هندسية متكاملة لتسريع دورات البناء وتقليل أوقات الانتظار في المشروعات الضخمة: أولاً التجميع التزايدي (Incremental Compilation) ويعمل على مستوى مهام التحويل البرمجي الفردية؛ حيث يتتبع المترجم التغييرات ويعيد ترجمة الملفات المعدلة وتوابعها فقط دون إعادة بناء كامل الموديول. ثانياً ذاكرة التخزين المؤقت للبناء (Build Cache) وتعمل في مرحلة التنفيذ عبر ربط مدخلات كل مهمة بتجزئة مشفرة؛ فإذا تطابقت المدخلات مع نتائج محفوظة محلياً أو سحابياً، يتخطى Gradle تنفيذ المهمة ويسترجع المخرجات فوراً كحالة FROM-CACHE مما يتيح مشاركة مخرجات الـ CI مع أجهزة المطورين. ثالثاً ذاكرة التخزين المؤقت للإعدادات (Configuration Cache) وتعمل في مرحلة التهيئة؛ حيث تحفظ شجرة المهام DAG الناتجة عن قراءة ملفات gradle.kts، وتتخطى مرحلة التهيئة بالكامل في عمليات البناء التالية طالما لم تتغير ملفات الإعدادات، مما يوفر عشرات الثواني في المشروعات متعددة الموديولات.",
        "walkthrough_ar": """تفعيل ميزات التسريع والتخزين السحابي في إعدادات Gradle:
```kotlin
// gradle.properties: تفعيل الكاش التزايدي والإعدادات
org.gradle.caching=true
org.gradle.configuration-cache=true
kotlin.incremental=true

// settings.gradle.kts: ضبط الكاش المحلي والسحابي المشترك
buildCache {
    local { isEnabled = true }
    remote<HttpBuildCache> {
        url = uri("https://cache.internal.company.com/")
        isPush = System.getenv("CI") == "true" // خوادم CI فقط ترفع للكاش
    }
}
```""",
        "why_it_matters_ar": "يوفر ساعات من أوقات الانتظار اليومية للمطورين ويسرع خطوط بناء الـ CI، مما يقلل تكاليف الخوادم ويزيد إنتاجية الفرق الهندسية.",
        "worked_example_ar": "تعديل سطر كود واحد في موديول عميق؛ يقوم التجميع التزايدي بترجمة هذا الكلاس فقط في 3 ثوانٍ بدلاً من استغراق 4 دقائق في إعادة بناء المشروع بالكامل.",
        "trade_offs_ar": "تفعيل هذه الميزات يتطلب كتابة مهام Gradle بطريقة نظيفة خالية من الآثار الجانبية، وإلا قد يؤدي التخزين الخاطئ لنتائج غير مطابقة للكود الفعلي.",
        "failure_modes_ar": "استخدام مهام مخصصة لا تعلن مدخلاتها ومخرجاتها بوضوح مما يعطل Build Cache، أو قراءة متغيرات النظام في مرحلة الإعداد مما يعطل Configuration Cache.",
        "production_perspective_ar": "في الشركات الكبرى، نعتمد على Gradle Enterprise لمراقبة وتتبع الكاش السحابي ومعدل Cache Hit Ratio للتأكد من تجاوز نسبة الاسترجاع 80%.",
        "how_to_answer_ar": "قسم الإجابة حسب مراحل البناء: Incremental Compilation أثناء ترجمة الكود، Build Cache أثناء تنفيذ المهام واسترجاع النواتج، و Configuration Cache أثناء قراءة ملفات الإعدادات.",
        "talking_points_ar": "الفرق بين المهام Up-to-date وحالة FROM-CACHE، دور الكاش السحابي Remote Cache، وتجنب تعطيل Configuration Cache.",
        "follow_ups_ar": "- **المحاور:** 'ما الفرق بين مهمة UP-TO-DATE ومهمة FROM-CACHE في مخرجات Gradle؟'\n  **المرشح:** 'حالة UP-TO-DATE تعني أن مخرجات المهمة موجودة بالفعل في مجلد build محلياً ولم تتغير مدخلاتها، بينما FROM-CACHE تعني أن مجلد build كان فارغاً ولكن Gradle استرجع النواتج الجاهزة من التخزين المؤقت المحلي أو السحابي.'\n\n- **المحاور:** 'كيف يمكن لمهمة مخصصة Custom Task أن تعطل ميزة Configuration Cache؟'\n  **المرشح:** 'إذا قامت المهمة بالإشارة إلى كائن Project أثناء وقت التنفيذ أو حاولت قراءة متغيرات خارجية غير معلنة في خصائص المدخلات @Input، يرفض Gradle تفعيل Configuration Cache لحماية اتساق شجرة المهام.'",
        "self_check_ar": "هل ميزت بدقة بين المستويات الثلاثة؟ وهل شرحت دور الكاش السحابي وفائدة Configuration Cache للمشاريع الضخمة؟",
        "references_ar": f"- [Gradle Documentation: Configuration Cache](https://docs.gradle.org/current/userguide/configuration_cache.html) — الدليل الرسمي للتخزين المؤقت لمرحلة الإعداد.\n- [Android Developers: Optimize your build speed](https://developer.android.com/build/optimize-your-build) — إرشادات جوجل لتسريع بناء تطبيقات أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يعيد التجميع التزايدي بناء الملفات المعدلة وتوابعها فقط داخل المهمة، بينما تتخطى Build Cache تنفيذ المهام كلياً باسترجاع المخرجات السابقة عبر تجزئة المدخلات ومشاركتها سحابياً، وتقوم Configuration Cache بحفظ شجرة المهام لتخطي مرحلة التهيئة وتسريع بدء البناء في المشروعات الضخمة.",
        "best_answer_ar": """تعتمد Gradle على منظومة ثلاثية الأبعاد لتسريع عمليات البناء في مشروعات أندرويد المعقدة.

المستوى الأول هو التجميع التزايدي Incremental Compilation، ويعمل داخل مترجم كوتلن؛ حيث يتتبع التعديلات البرمجية ويعيد ترجمة الملفات المعدلة وتوابعها المباشرة فقط، متجنباً إعادة بناء الموديول بالكامل عند تغيير سطر كود بسيط.

المستوى الثاني هو ذاكرة التخزين المؤقت للبناء Build Cache، وتعمل على مستوى المهام التنفيذية؛ حيث تقوم بحساب تجزئة مشفرة لكافة مدخلات المهمة، فإذا تطابقت مع نتائج سابقة، يتم استرجاع الملفات فوراً دون تشغيل المعالجات بحالة FROM-CACHE، وتتيح مشاركة هذه النتائج سحابياً بين خوادم الـ CI وأجهزة المطورين.

المستوى الثالث هو التخزين المؤقت للإعدادات Configuration Cache، ويوفر وقتاً هائلاً بتخزين شجرة المهام الناتجة عن قراءة ملفات gradle.kts؛ مما يتيح لـ Gradle بدء التجميع فوراً وتخطي مرحلة التهيئة الثقيلة.""",
        "deep_answer_ar": """في المشروعات الضخمة التي تحتوي على عشرات أو مئات الموديولات، يعتبر زمن البناء عائقاً كبيراً لإنتاجية المطورين، ولذا ندير تحسين الأداء عبر ثلاثة محاور أساسية.

المحور الأول هو التجميع التزايدي Incremental Compilation الذي يقوده مترجم كوتلن؛ فإذا قام المطور بتعديل كود داخلي دون تغيير الواجهة العامة العامة ABI للكلاس، يقتصر التجميع على هذا الملف فقط دون المساس بالموديولات التي تعتمد عليه.

المحور الثاني هو Build Cache؛ حيث يحلل Gradle مدخلات المهمة كالأكواد والإعدادات، فإذا كانت مطابقة لعملية بناء سابقة، يتخطى التنفيذ كلياً ويفرغ المخرجات فوراً. ونحن نفعل التخزين المؤقت السحابي Remote Cache بحيث ترفع خوادم الـ CI نواتج البناء، ليسترجعها المطورون على أجهزتهم دون الحاجة لإعادة تجميع الكود محلياً.

المحور الثالث هو Configuration Cache؛ فقراءة ملفات الإعدادات وتقييم شجرة المهام DAG في المشروعات الضخمة قد تستغرق وحدها ما بين 30 إلى 60 ثانية قبل بدء أي تجميع. وبفضل هذه الميزة، يحفظ Gradle شجرة المهام على القرص، وعند تكرار البناء يتخطى قراءة ملفات gradle.kts بالكامل وينتقل للتنفيذ في أجزاء من الثانية. ونراقب باستمرار صحة الكاش السحابي عبر تنبيهات فورية، مع عزل المهام غير الحتمية Non-deterministic لمنع تلوث الذاكرة المؤقتة وضمان حصول المطورين على نتائج دقيقة وموثوقة بنسبة مئة بالمئة."""
    }
}

# ==========================================
# BLD-06: What are R8, shrinking, optimization, and obfuscation?
# ==========================================
DATA["BLD-06"] = {
    "concept_en": """R8 is Google's integrated compiler tool that directly converts Java/Kotlin bytecode into optimized, secure Dalvik Executable (DEX) code in a single processing step, superseding the legacy ProGuard and D8 toolchain:
- Code Shrinking (Tree Shaking): Statically analyzes the application codebase starting from declared entry points (Activities, Services, BroadcastReceivers, and explicitly retained classes via -keep). Any classes, interfaces, methods, or fields not in the reachable execution graph are stripped from the final binary, drastically reducing DEX method counts.
- Resource Shrinking: Configured via shrinkResources = true, it works in tandem with code shrinking to identify unreferenced XML files, drawables, and raw assets, replacing them with empty dummy stubs before final packaging.
- Optimization: Modifies code structure to enhance execution efficiency and reduce byte size: inlining short functions, removing unused parameter arguments, rewriting enum switch statements to integer tables, eliminating dead conditionals, and collapsing class hierarchies.
- Obfuscation: Renames remaining classes, methods, and member variables to short, ambiguous alphanumeric identifiers (a, b, c). This prevents casual reverse engineering, shortens identifier tables in the DEX header, and emits a cryptographic mapping.txt file essential for de-obfuscating production stack traces.""",
    "walkthrough_en": """Enabling the complete R8 optimization pipeline in release builds:
```kotlin
// build.gradle.kts (app module)
android {
    buildTypes {
        getByName("release") {
            isMinifyEnabled = true        // Activates R8 code shrinking, optimization & obfuscation
            isShrinkResources = true      // Activates resource shrinking
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

// proguard-rules.pro: Protecting reflective models from being stripped
-keepclassmembers class com.example.models.** {
    <fields>;
}

// Resulting de-obfuscation mapping file:
// build/outputs/mapping/release/mapping.txt
```""",
    "short_en": """R8 is Google's integrated shrinker, optimizer, and dexer. It applies tree shaking to eliminate unreferenced code and resources, performs optimizations like function inlining and dead code elimination, and obfuscates remaining identifiers into short names to impede reverse engineering while emitting a mapping.txt file for crash trace de-obfuscation.""",
    "structured_en": """R8 consolidates code shrinking, optimization, obfuscation, and dexing into a unified compilation stage within the Android Gradle Plugin.
First, code shrinking utilizes static tree shaking to discard unreferenced classes, methods, and fields starting from manifest entry points and explicit keep rules, accompanied by resource shrinking to discard unreferenced XML and drawables.
Second, optimization transforms the remaining bytecode to maximize execution speed and minimize binary size by inlining short functions, removing unused parameter declarations, and collapsing single-implementation interfaces.
Third, obfuscation renames classes and members into short alphanumeric characters like a or b. This hinders reverse engineering and shrinks DEX string tables.
Because obfuscation disguises production crash traces, R8 generates a mapping.txt file used by tools like Retrace to restore readable stack traces.""",
    "deep_senior_en": """In modern Android engineering, R8 serves as the indispensable gatekeeper between raw JVM bytecode and production-ready Dalvik Executable binaries.
Replacing the legacy two-step pipeline of ProGuard and D8, R8 executes shrinking, optimization, and dexing in a single pass, resulting in faster compilation and deeper cross-method optimizations.
Code shrinking acts as an exhaustive tree-shaking engine.
Starting from root entry points—such as Activities declared in AndroidManifest.xml, public service endpoints, and explicit -keep directives—R8 traverses the call graph.
Any class, method, or field that cannot be proven reachable is stripped from the APK.
Resource shrinking then inspects resource IDs referenced in compiled code, stripping orphaned drawables and layouts.
Beyond dead code elimination, R8 performs aggressive bytecode optimization.
It inlines small functions to eliminate call-frame overhead, rewrites Kotlin null-check assertions, flattens class hierarchies, and strips unused parameters.
Finally, obfuscation replaces package, class, method, and field identifiers with short characters such as a.b.c.
This not only protects intellectual property against casual APK decompilation with tools like Jadx, but also drastically shrinks the DEX string pool.
However, because obfuscation scrambles runtime stack traces into unreadable symbols, senior engineers mandate that CI pipelines archive the resulting mapping.txt artifact alongside release binaries and upload it to crash reporting systems.""",
    "meta_ar": {
        "id": "BLD-06",
        "questionAr": "ما هو محرك R8؟ وما هي مراحل تقليص الكود (Shrinking) والتحسين (Optimization) والإخفاء والتشويش (Obfuscation)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور R8 كبديل مدمج لـ ProGuard و D8، وآلية الـ Tree Shaking في حذف الكود والموارد الميتة، والتحسينات المتقدمة كـ Inlining، وتقنيات التشويش وحماية التطبيق وملف mapping.txt.",
        "concept_ar": "يعد R8 محرك جوجل الموحد لمعالجة وتحويل بايت كود الجافا وكوتلن إلى ملفات DEX محسنة ومضغوطة في خطوة واحدة، بديلاً عن منظومة ProGuard و D8 السابقة: تقليص الكود البرمجي (Tree Shaking) يقوم بتحليل الكود بدءاً من نقاط الدخول الرئيسية كالمكونات المعلنة في المانيفست وقواعد -keep؛ فيحذف كافة الكلاسات والدوال غير المستخدمة لتقليل عدد دوال الـ DEX. وتقليص الموارد (Resource Shrinking) يعمل بالتوازي مع تقليص الكود لحذف ملفات الصور والتنسيقات غير المستخدمة واستبدالها بحشوات فارغة. والتحسين الهندسي (Optimization) يعيد هيكلة الكود لرفع كفاءة المعالجة مثل دمج الدوال القصيرة Inlining وحذف المعاملات غير المستخدمة ودمج الكلاسات الفارغة. وأخيراً إخفاء وتشويش الكود (Obfuscation) يعيد تسمية الكلاسات والدوال لأسماء مقتضبة وغير مفهومة كـ a و b لحماية التطبيق من الهندسة العكسية وتقليص حجم ترويسة ملفات DEX، مع توليد ملف mapping.txt الإلزامي لفك تشفير تقارير الكراش في الإنتاج.",
        "walkthrough_ar": """تفعيل R8 وتقليص الموارد وضبط قواعد الحماية في ملف البناء:
```kotlin
android {
    buildTypes.getByName("release") {
        isMinifyEnabled = true    // تفعيل R8 للتقليص والتحسين والتشويش
        isShrinkResources = true  // تفعيل حذف الصور والموارد غير المستخدمة
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro"
        )
    }
}
// ملف mapping.txt الناتج في: build/outputs/mapping/release/mapping.txt
```""",
        "why_it_matters_ar": "يقلل حجم التطبيق بما يصل إلى النصف، ويحمي الشفرة المصدرية من السرقة والهندسة العكسية، ويحسن سرعة الإقلاع والأداء التشغيلي.",
        "worked_example_ar": "تطبيق يضم مكتبة إحصاءات ضخمة يستخدم منها دالتين فقط؛ يقوم R8 بحذف 95% من كلاسات المكتبة غير المستخدمة ويغير أسماء الكلاسات المتبقية لأحرف مختصرة.",
        "trade_offs_ar": "يوفر R8 حماية فائقة وحجماً صغيراً ولكنه يزيد زمن بناء نسخة الـ Release في الـ CI وقد يكسر الكود المعتمد على الـ Reflection إذا لم تضبط قواعد Keep.",
        "failure_modes_ar": "تشغيل R8 دون حماية نماذج البيانات المستخدمة في الـ Serialization كـ Retrofit مما يسبب أخطاء تحويل فارغة، أو فقدان ملف mapping.txt بعد النشر.",
        "production_perspective_ar": "في المشروعات الكبرى، نلزم خطوط الـ CI بأرشفة ملف mapping.txt ورفعه آلياً لمنصة Firebase Crashlytics لضمان قراءة تقارير الكراش بوضوح.",
        "how_to_answer_ar": "عرف R8 كبديل مدمج لـ ProGuard و D8، ثم اشرح الخطوات الأربع بالتسلسل: حذف الكود الميت، حذف الموارد، تحسين البايت كود، والتشويش مع أهمية mapping.txt.",
        "talking_points_ar": "مفهوم Tree Shaking، التحسين بـ Function Inlining، دور التشويش في تقليص String Pool، وأهمية ملف mapping.txt لفك التشفير.",
        "follow_ups_ar": "- **المحاور:** 'كيف يمكنك قراءة تتبع الكراش المشفر الناتج عن نسخة مجمعة بـ R8؟'\n  **المرشح:** 'باستخدام أداة Retrace المدمجة مع أندرويد وتمرير ملف mapping.txt المطابق لنفس الإصدار؛ فتقوم الأداة بمطابقة الأحرف المبهمة مثل a.b() مع الأسماء الأصلية للكلاسات والأسطر البرمجية.'\n\n- **المحاور:** 'ما الفرق بين ملف proguard-android.txt وملف proguard-android-optimize.txt؟'\n  **المرشح:** 'الملف الأول يقتصر على التقليص والتشويش الأساسي، بينما يفعل الملف الثاني proguard-android-optimize خوارزميات التحسين الهجومية مثل دمج الدوال Inlining وحذف الوسائط، مما يوفر حجماً أصغر وأداء أسرع.'",
        "self_check_ar": "هل شرحت مراحل R8 الأربع بوضوح؟ وهل بينت دوره في استبدال D8 ودور ملف mapping.txt؟",
        "references_ar": f"- [Android Developers: Shrink, obfuscate, and optimize your app](https://developer.android.com/build/shrink-code) — الدليل الشامل لمحرك R8 وتطبيقاته.\n- [R8 Retrace Tool](https://developer.android.com/tools/retrace) — توثيق أداة فك تشفير تقارير الكراش عبر ملف المخطط.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يمثل R8 محرك التحسين والتقليص المدمج في أندرويد؛ حيث يحذف الكود والموارد الميتة بأسلوب Tree Shaking، ويحسن الأداء بدمج الدوال القصيرة وحذف التوابع غير المستخدمة، ويشوش الكود بتغيير الأسماء لرموز مقتضبة لحمايته وتقليص حجمه، مع توليد ملف mapping.txt لفك التشفير.",
        "best_answer_ar": """يعد R8 محرك التحويل والتحسين المتكامل الذي دمجته جوجل لتقليص وتحسين بايت كود أندرويد وتحويله إلى صيغة DEX في خطوة واحدة كبديل لمنظومة ProGuard القديمة.

تقوم مرحلة تقليص الكود Shrinking بتحليل شجرة الاستدعاءات بدءاً من مكونات المانيفست وقواعد Keep، لحذف كافة الكلاسات والدوال غير المستخدمة، ويتكامل معها تقليص الموارد لحذف الصور والملفات المهملة.

وتقوم مرحلة التحسين Optimization بإعادة هيكلة الكود لتحسين سرعته وتقليل حجمه؛ مثل دمج الدوال الصغيرة Inlining وحذف المعاملات غير المستغلة.

وتأتي مرحلة الإخفاء والتشويش Obfuscation لتغيير أسماء الكلاسات والدوال إلى أحرف عشوائية قصيرة مثل a و b؛ مما يصعب الهندسة العكسية ويقلص حجم ملفات DEX، مع إصدار ملف mapping.txt الإلزامي لإعادة قراءة تقارير الأخطاء والكراش في بيئة الإنتاج.""",
        "deep_answer_ar": """في هندسة إصدار تطبيقات أندرويد، يعتبر محرك R8 الأداة الأكثر تأثيراً على حجم التطبيق وأمانه وأدائه في الإنتاج؛ فهو يدمج وظائف التقليص والتحسين والتشويش والـ Dexing في مسار واحد متكامل.

يبدأ R8 بمرحلة تقليص الكود بأسلوب Tree Shaking؛ حيث يتتبع شجرة الكود بدءاً من نقاط الدخول في AndroidManifest وقواعد الحفظ -keep، ويحذف أي دالة أو كلاس لا يوجد مسار تنفيذي يصل إليه، وتتبعه ميزة تقليص الموارد بحذف ملفات الصور والتنسيقات المعزولة.

وفي مرحلة التحسين، يطبق R8 تعديلات جذرية على البايت كود؛ فيقوم بدمج الدوال القصيرة Inlining لتوفير تكلفة استدعاء الذاكرة، ويحذف المتغيرات غير المستغلة، ويدمج الكلاسات المتطابقة في كلاس واحد لتقليل عدد المؤشرات.

ثم تأتي مرحلة التشويش Obfuscation التي تستبدل الأسماء الصريحة بأحرف مبهمة كـ a و b، مما يحمي المنطق البرمجي من أدوات الهندسة العكسية كـ Jadx ويقلص مساحة جدول النصوص في ترويسة ملفات DEX. ولأن هذه المرحلة تجعل تقارير الكراش مشوهة بالكامل، تلتزم فرق الهندسة بأرشفة ملف mapping.txt الناتج في خط الـ CI ورفعه لمنصات Crashlytics لإعادة فك شفرة الأخطاء وتتبع المشاكل بدقة. كما ندمج فحص تقارير التعيين mapping.txt ضمن خطوط الـ CI للتأكد من عدم تسرب أي أسماء حساسة في كود الإنتاج، مما يوفر أعلى معايير الأمان الموصى بها في التطبيقات المصرفية."""
    }
}

# ==========================================
# BLD-07: What is consumerProguardFiles for Android libraries?
# ==========================================
DATA["BLD-07"] = {
    "concept_en": """consumerProguardFiles is a specialized Android Gradle Plugin configuration directive dedicated to Android Library (com.android.library) modules:
- How It Operates: Rules declared in consumerProguardFiles (such as consumer-rules.pro) are packaged directly inside the compiled Android Archive (.aar) binary under the root directory as proguard.txt.
- Automatic Consumer Merging: When an application module or another library adds a dependency on this AAR, AGP's build pipeline automatically extracts proguard.txt and appends its -keep and optimization rules directly into the host application's active R8 shrinking pipeline.
- Solving the Reflection & Serialization Trap: If a library uses reflection, JNI native bindings, or JSON serialization, its internal models or interfaces will break at runtime if the consuming app enables R8 minification. Declaring appropriate keep rules in consumerProguardFiles guarantees that any downstream consumer can minify their app safely without manually copying ProGuard rules into their own project.
- Crucial Distinction: proguardFiles applies exclusively to the library itself if minification is enabled during library compilation. In contrast, consumerProguardFiles is ignored during library compilation and takes effect solely inside the consumer's R8 pipeline.""",
    "walkthrough_en": """Declaring consumer ProGuard rules in an Android library module:
```kotlin
// Library module: build.gradle.kts
plugins {
    alias(libs.plugins.android.library)
}

android {
    namespace = "com.example.analytics.sdk"

    defaultConfig {
        // Bundled inside the published AAR archive as proguard.txt
        consumerProguardFiles("consumer-rules.pro")
    }

    buildTypes {
        getByName("release") {
            // Rules applied when minifying the library itself
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}

// Inside consumer-rules.pro: protects library models automatically in consuming apps
-keepclassmembers class com.example.analytics.sdk.models.** {
    <fields>;
}
-keepattributes *Annotation*
```""",
    "short_en": """consumerProguardFiles packages ProGuard rules directly inside a published Android library AAR. When an app depends on the library, AGP automatically merges these rules into the app's R8 configuration, safeguarding the library's internal reflection, serialization, and JNI bindings from breaking without requiring consumers to configure rules manually.""",
    "structured_en": """Configuring consumerProguardFiles in Android library modules ensures downstream consumer applications can minify their release builds without breaking library functionality.
First, consumerProguardFiles packages the specified rule file directly into the published AAR archive under the name proguard.txt.
Second, when an application consumes this AAR as a dependency, AGP's R8 pipeline automatically extracts and appends these rules to the app's overall shrinking and obfuscation configuration.
Third, this mechanism guarantees that classes relying on reflection, JSON serialization, or native JNI methods within the library are protected by mandatory keep rules automatically, preventing runtime ClassNotFoundException crashes.
Fourth, understand the distinction: proguardFiles dictates rules applied when compiling the library itself, whereas consumerProguardFiles applies exclusively to downstream applications consuming the compiled library.""",
    "deep_senior_en": """In modular Android architecture and SDK development, consumerProguardFiles is the critical mechanism that decouples library authors from consumer configuration headaches.
When an engineering team builds an Android Library that relies on reflection, runtime annotations, or native JNI bindings, shipping that library without consumer rules is a major operational failure.
If a consuming app enables isMinifyEnabled in release, R8 will strip or obfuscate the library's internal models, causing runtime NoSuchMethodError or deserialization failures exclusively in production.
Declaring consumerProguardFiles solves this by embedding the rules file directly inside the compiled AAR as proguard.txt.
When AGP builds the consuming application, it aggregates all proguard.txt files across transitive library dependencies and merges them into the app's primary R8 invocation.
However, senior SDK developers exercise extreme discipline when authoring consumer rules.
Because merged consumer rules are global to the consuming app's R8 pipeline, poorly written wildcards—such as -keep class com.google.** { *; } or broad interface preserves—pollute the app's entire compilation, disabling dead code elimination and unnecessarily bloating the final APK size.
Consumer rules must be laser-focused, preserving only the library's private reflective members and internal data classes.
Finally, distinguish this from proguardFiles: proguardFiles controls minification when building the library itself, whereas consumerProguardFiles is ignored during library compilation and evaluated exclusively inside the consumer's build.""",
    "meta_ar": {
        "id": "BLD-07",
        "questionAr": "ما هي خاصية consumerProguardFiles في مكتبات أندرويد (AAR)؟ وما هو الفارق بينها وبين proguardFiles العادية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور consumerProguardFiles في حزم AAR، وكيفية تصدير قواعد R8/ProGuard لمستهلكي المكتبة تلقائياً، والتمييز بين قواعد بناء المكتبة وقواعد التطبيق المستهلك لتفادي أخطاء الـ Reflection.",
        "concept_ar": "تعد خاصية consumerProguardFiles تعليمة خاصة في إعدادات AGP مخصصة لمكتبات أندرويد (AAR) لإدارة قواعد الحماية تلقائياً: يتم تضمين ملف القواعد المحدد في هذه الخاصية داخل حزمة المكتبة الناتجة AAR تحت اسم proguard.txt. وعندما يقوم تطبيق بالاعتماد على هذه المكتبة، يستخرج محرك AGP تلك القواعد تلقائياً ويدمجها في منظومة R8 الخاصة بالتطبيق المستهلك. وتحمي هذه الآلية نماذج البيانات والكود المعتمد على الـ Reflection أو الربط بلغة C++ عبر JNI داخل المكتبة من الحذف أو التشويش عند تفعيل تقليص الكود في التطبيق النهائي دون إلزام المطور بكتابة قواعد يدوية. ويكمن الفارق الجوهري في أن proguardFiles تطبق على المكتبة نفسها عند تجميعها، بينما تطبق consumerProguardFiles حصرياً على التطبيقات التي تستهلك تلك المكتبة.",
        "walkthrough_ar": """تحديد قواعد المستهلك في موديول المكتبة وفحص تصديرها:
```kotlin
// في موديول المكتبة: build.gradle.kts
plugins { alias(libs.plugins.android.library) }

android {
    defaultConfig {
        // يتم حزم هذا الملف داخل الـ AAR باسم proguard.txt
        consumerProguardFiles("consumer-rules.pro")
    }
}

// داخل ملف consumer-rules.pro لحماية نماذج المكتبة تلقائياً:
-keepclassmembers class com.example.sdk.models.** {
    <fields>;
}
```""",
        "why_it_matters_ar": "يمنع كراش التطبيقات التي تستخدم المكتبة في بيئة الإنتاج بسبب حذف كود الـ Reflection، ويغني المطورين عن البحث عن قواعد الحماية وإضافتها يدوياً.",
        "worked_example_ar": "مكتبة تستخدم Gson لتحويل البيانات؛ بدون consumerProguardFiles ينهار تطبيق العميل في نسخة الـ Release، وبإضافتها تدمج القواعد تلقائياً ويعمل التطبيق بسلاسة.",
        "trade_offs_ar": "توفر سهولة هائلة للمستهلك ولكن أي خطأ في كتابة القواعد أو استخدام Keep واسع النطاق سيؤثر سلباً على كافة التطبيقات المستهلكة ويمنع حذف الكود الميت لديها.",
        "failure_modes_ar": "كتابة قواعد عامة مثل -keep class com.** مما يعطل تقليص الكود في تطبيق العميل بأكمله، أو وضع القواعد في proguardFiles ونسيان consumerProguardFiles.",
        "production_perspective_ar": "في فرق تطوير الـ SDKs، نلزم المهندسين بكتابة قواعد دقيقة جداً ومحصورة في كلاسات الحزمة الخاصة بالمكتبة فقط، ونختبرها عبر تطبيق عينة مجمع بـ R8.",
        "how_to_answer_ar": "وضح أن consumerProguardFiles تحزم قواعد الحماية داخل ملف proguard.txt في الـ AAR وتدمج تلقائياً في R8 للتطبيق المستهلك، وميزها بوضوح عن proguardFiles العادية.",
        "talking_points_ar": "مفهوم proguard.txt داخل الـ AAR، الدمج التلقائي في تطبيق العميل، خطورة القواعد العامة، والفرق الجوهري مع proguardFiles.",
        "follow_ups_ar": "- **المحاور:** 'لماذا يجب الحذر الشديد عند كتابة قواعد في consumerProguardFiles؟'\n  **المرشح:** 'لأن هذه القواعد تدمج بشكل عام Global في منظومة R8 الخاصة بالتطبيق المستهلك بأكمله؛ فإذا وضع مطور المكتبة قاعدة واسعة مثل -dontobfuscate أو حفظ حزم خارجية، سيعطل حماية وتقليص تطبيق العميل بالكامل ويضخم حجم الـ APK النهائي دون علمه.'\n\n- **المحاور:** 'كيف يمكنك فحص القواعد المدمجة القادمة من المكتبات في تطبيقك؟'\n  **المرشح:** 'يقوم R8 بإنشاء ملف تجميعي لكافة القواعد في مسار build/outputs/mapping/release/configuration.txt؛ فيمكن للمطور فتحه وفحص كافة القواعد المدمجة من ملفات AAR واكتشاف أي مكتبة تفرض قواعد مسيئة.'",
        "self_check_ar": "هل شرحت آلية عمل consumerProguardFiles وحزم proguard.txt؟ وهل ميزت بينها وبين proguardFiles وحذرت من القواعد العامة؟",
        "references_ar": f"- [Android Developers: Configure ProGuard for Android Libraries](https://developer.android.com/build/shrink-code#configuration-files) — الدليل الرسمي لقواعد الحماية في المكتبات.\n- [AAR Format Specification](https://developer.android.com/studio/projects/android-library#aar-contents) — محتويات حزمة الأرشيف AAR وملف proguard.txt.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تقوم consumerProguardFiles بتضمين قواعد R8 داخل حزمة المكتبة AAR؛ وعندما يعتمد تطبيق على المكتبة، يدمج AGP هذه القواعد تلقائياً في R8 الخاص بالتطبيق لحماية كود الـ Reflection و JNI من التلف دون إلزام المطور بكتابة قواعد يدوية في مشروعه.",
        "best_answer_ar": """تعتبر خاصية consumerProguardFiles أداة أساسية في تطوير مكتبات أندرويد وحزم AAR لضمان استقرار التطبيقات المستهلكة.

تسمح هذه الخاصية لمطور المكتبة بتضمين ملف قواعد R8 مخصص داخل ملف الـ AAR الناتج تحت اسم proguard.txt؛ وبمجرد أن يضيف أي تطبيق هذه المكتبة كاعتمادية، يقوم نظام AGP تلقائياً باستخراج القواعد ودمجها في عملية تقليص الكود R8 الخاصة بالتطبيق.

وتحمي هذه الآلية كلاسات النماذج المعتمدة على الـ Reflection أو تحويل الـ JSON أو دوال C++ من الحذف أو التشويش في نسخة الـ Release للتطبيق النهائي دون حاجة المطور لنسخ قواعد الحماية يدوياً.

ويكمن الفارق الجوهري في أن proguardFiles تطبق على كود المكتبة أثناء تجميعها فقط، بينما تطبق consumerProguardFiles حصرياً على التطبيقات التي تستخدم هذه المكتبة.""",
        "deep_answer_ar": """في هندسة تطوير حزم SDK والمكتبات المشتركة، تعتبر خاصية consumerProguardFiles صمام الأمان لمنع انهيار التطبيقات عند تفعيل تقليص الكود في الإنتاج.

عندما تحتوي المكتبة على كود يعتمد على الـ Reflection أو واجهات JNI أو تحويل JSON، فإن تفعيل R8 في التطبيق النهائي سيحذف تلك الحقول أو يشوش أسماءها، مما يسبب أخطاء NoSuchMethodException أثناء التشغيل. وبدلاً من إجبار مطوري التطبيقات على نسخ قواعد معقدة في ملفاتهم، نحدد تلك القواعد في consumerProguardFiles ليقوم AGP بحزمها كملف proguard.txt داخل الـ AAR ودمجها تلقائياً لدى كل مستهلك.

ولكن يحذر مهندسو المنصات من كتابة قواعد عشوائية واسعة؛ لأن قواعد المكتبة تصبح عامة Global على مستوى التطبيق بأكمله؛ فكتابة قاعدة غير منضبطة كحفظ كافة كلاسات الحزمة يمنع R8 من حذف الكود الميت ويضخم حجم التطبيق النهائي، ولذا نلزم القواعد بحماية الحقول الانعكاسية الدقيقة فقط.

وأخيراً، يجب التمييز بوضوح بين الأداتين: خاصية proguardFiles تتحكم في تقليص كود المكتبة نفسها أثناء بنائها، بينما تهمل خاصية consumerProguardFiles محلياً ولا تنشط إلا داخل خط بناء التطبيق الذي يستهلك تلك المكتبة. ونعتمد في تطوير الـ SDKs على كتابة اختبارات تكامل مؤتمتة تتحقق من عمل كود المكتبة بعد تشغيل R8، مما يضمن تجربة خالية من العيوب لكافة التطبيقات الشريكة في بيئة الإنتاج."""
    }
}

# ==========================================
# Runner & Word Count Validation
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

    ee.save_topic_metadata("bld_01_07", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\nAll {len(DATA)} BLD questions (BLD-01 to BLD-07) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()