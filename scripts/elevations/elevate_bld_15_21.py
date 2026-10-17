#!/usr/bin/env python3
"""
Elevation script for BLD questions: BLD-15 to BLD-21.
Topic: Build & Gradle (BLD)
Phase 4, Batch 3
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "أنظمة البناء و Gradle و AGP و R8 والـ Signing وإصدار التطبيقات"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# BLD-15: How do you investigate dependency version conflicts and build-speed regressions?
# ==========================================
DATA["BLD-15"] = {
    "concept_en": """Diagnosing dependency conflicts and build performance regressions requires targeted profiling across Gradle's build lifecycle phases:
- Dependency Conflict Resolution Mechanics:
  1. Conflict Strategy: Gradle defaults to 'latest version wins'. If transitive dependencies pull disparate library revisions (e.g. OkHttp 4.9.0 vs 4.12.0), Gradle automatically upgrades to the highest version. This can introduce silent binary breaking changes or runtime NoSuchMethodError.
  2. Diagnostic Tooling:
     - ./gradlew :app:dependencies --configuration releaseRuntimeClasspath: Prints the comprehensive tree with upgrade notations (-> 4.12.0).
     - ./gradlew :app:dependencyInsight --dependency okhttp --configuration releaseRuntimeClasspath: Dissects exact incoming graph paths and explains selection reasons.
  3. Resolution Governance: Enforce consistency via Gradle Version Catalogs (libs.versions.toml) and strict rich constraints (strictly). Avoid blind resolutionStrategy.force() which silences compiler warnings but masks binary breakage.
- Build-Speed Regression Profiling:
  1. Lifecycle Phase Separation: Profile configuration phase (isolated via Gradle Configuration Cache), task execution phase, and compiler/annotation processing overhead.
  2. Gradle Build Scans: Execute ./gradlew assembleDebug --scan to generate deep diagnostics analyzing the critical path, task cache misses, non-incremental task inputs, and Garbage Collection pauses.
  3. Gradle Profiler: Use gradle-profiler for controlled statistical benchmarking across commits.""",
    "walkthrough_en": """Diagnostic CLI commands and conflict resolution configuration in build.gradle.kts:
```bash
# 1. Trace why a specific dependency version was selected and which modules requested it:
./gradlew :app:dependencyInsight --dependency okhttp --configuration releaseRuntimeClasspath

# 2. Profile build performance and cache misses with a Gradle Build Scan:
./gradlew :app:assembleRelease --scan
```

```kotlin
// 3. Enforce strict versioning and conflict detection in build.gradle.kts:
configurations.all {
    resolutionStrategy {
        // Fail the build immediately whenever two dependencies request divergent versions
        failOnVersionConflict()

        // Force a verified, audited library version across all transitive dependencies
        force("com.squareup.okhttp3:okhttp:4.12.0")
    }
}
```""",
    "short_en": """Investigating dependency conflicts requires running Gradle dependencyInsight to inspect selection rationale and path origins across configurations, resolving discrepancies through Version Catalogs or strict constraints. For build speed regressions, we generate Gradle Build Scans to isolate configuration bottlenecks, identify cache-miss triggers in non-incremental tasks, and measure annotation processing overhead on the critical path.""",
    "structured_en": """When diagnosing dependency friction and compilation slowdowns, senior engineers follow a structured diagnostic pipeline.
To investigate dependency conflicts, we avoid blind version forcing. Running Gradle dependencyInsight for the affected runtime classpath prints the exact dependency graph path and selection rationale. Gradle defaults to selecting the highest version, which frequently introduces silent binary incompatibilities if a transitive upgrade introduces breaking API changes. We resolve these conflicts systematically using Gradle Version Catalogs and rich version constraints, or enable failOnVersionConflict in continuous integration to catch divergent transitive dependencies early.
To investigate build speed regressions, we never rely on subjective local observations. We generate a Gradle Build Scan to separate configuration overhead from task execution. The build timeline highlights tasks on the critical execution path, distinguishes incremental executions from full rebuilds, and pinpoints cache misses caused by non-hermetic task inputs. Furthermore, we audit annotation processing durations between KAPT and KSP, ensuring code generators run incrementally without invalidating downstream compilation caches.""",
    "deep_senior_en": """From a platform engineering leadership perspective, maintaining dependency hygiene and compilation velocity requires continuous architectural guardrails rather than reactive troubleshooting.
When handling transitive dependency conflicts, using resolutionStrategy.force is a dangerous anti-pattern because it overrides the graph indiscriminately, masking underlying binary incompatibilities until runtime NoSuchMethodError crashes occur in production. Instead, we implement Gradle rich version constraints. Using strictly prevents any transitive dependency from upgrading a library beyond an audited release. Additionally, we integrate dependency analysis plugins in our pipeline to detect unused direct dependencies and transitive dependencies that leak across compilation boundaries.
When tackling build speed regressions, the most frequent culprits fall into three categories: configuration bloat, cache invalidation, and annotation processing. If developers execute arbitrary file operations, network calls, or dynamic Git queries during the configuration phase, every build incurs a heavy penalty regardless of task caching. We eliminate this by enabling the Gradle Configuration Cache and validating that all plugins conform to isolated configuration inputs.
For task execution regressions, a single task with unstable inputs breaks caching for all downstream dependents. Unstable inputs typically arise from un-annotated directory parameters, volatile timestamps in generated source headers, or absolute machine-specific file paths passed into compiler flags. By inspecting Build Scan task inputs and diffing cache keys between local and continuous integration environments, we isolate the exact input property invalidating the cache. Finally, migrating legacy KAPT processors to Kotlin Symbol Processing reduces annotation overhead significantly by generating code directly from Kotlin compiler AST without generating Java stubs.""",
    "meta_ar": {
        "id": "BLD-15",
        "questionAr": "كيف تحقق في تعارض إصدارات التبعيات (Dependency Version Conflicts) وانحدار سرعة البناء (Build-Speed Regressions)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التحقيق في تعارض التبعيات عبر dependencyInsight، وفهم آلية اختيار أحدث إصدار وتأثيرها على التوافق الثنائي، واستخدام Build Scans لتحليل مسار البناء الحرج والـ Cache Misses، وتطبيق القيود الصارمة في Version Catalogs.",
        "concept_ar": "يتطلب تشخيص تعارض التبعيات وتراجع سرعة البناء فحصاً دقيقاً لدورة حياة Gradle: في تعارض التبعيات، يعتمد Gradle افتراضياً قاعدة اختيار أحدث إصدار تلقائياً، مما قد يؤدي لترقية مكتبة وسيطة تحمل تغييرات كاسرة تسبب خطأ NoSuchMethodError أثناء التشغيل. ونستخدم أمر dependencyInsight لتتبع مسار التبعية وسبب اختيار الإصدار، مع تفضيل القيود الغنية strictly و Version Catalogs بدلاً من فرض الإصدارات عشوائياً. وفي انحدار سرعة البناء، نفصل زمن التهيئة عن زمن التنفيذ؛ وننشئ تقرير Gradle Build Scan لتحليل المسار الحرج للمهام، وأسباب فشل التخزين المؤقت، وتأثير معالجات الـ Annotations مثل KAPT مقارنة بـ KSP.",
        "walkthrough_ar": """أوامر تشخيص التبعيات وفرض الإصدارات الصريحة في build.gradle.kts:
```bash
# 1. معرفة سبب اختيار إصدار معين والمسار الدقيق في شجرة التبعيات:
./gradlew :app:dependencyInsight --dependency okhttp --configuration releaseRuntimeClasspath

# 2. إنشاء تقرير Build Scan كامل لتحليل أسباب بطء البناء:
./gradlew :app:assembleRelease --scan
```
```kotlin
// 3. فرض قيود الإصدارات واكتشاف التعارض مبكراً في build.gradle.kts:
configurations.all {
    resolutionStrategy {
        // إفشال البناء في الـ CI عند وجود أي تعارض لإجبار المطورين على حله
        failOnVersionConflict()
        // تثبيت إصدار موحد ومفحوص
        force("com.squareup.okhttp3:okhttp:4.12.0")
    }
}
```""",
        "why_it_matters_ar": "يمنع انهيار التطبيقات في الإنتاج بسبب عدم التوافق الثنائي للمكتبات الوسيطة، ويحافظ على إنتاجية مئات المهندسين بمنع تراكم بطء البناء في الـ CI.",
        "worked_example_ar": "ترقية مكتبة تحليلات أدت لترقية OkHttp إلى إصدار فرعي كسر مكتبة دفع بنكية؛ باستخدام dependencyInsight تم كشف المسار وتثبيت الإصدار بـ strictly، وتم تسريع البناء بـ 35% بتحويل KAPT إلى KSP.",
        "trade_offs_ar": "تفعيل failOnVersionConflict يضمن دقة التبعيات ولكنه يتطلب تدخلاً يدوياً عند كل ترقية؛ وإنشاء Build Scans يوفر شفافية هائلة لكنه يتطلب تأمين السجلات لعدم تسريب بيانات حساسة.",
        "failure_modes_ar": "استخدام force عشوائياً لحل تعارض يسبب أخطاء NoSuchMethodError في الإنتاج، أو مقارنة زمن البناء النظيف ببناء يعتمد على الكاش مما يعطي قياسات مضللة.",
        "production_perspective_ar": "نعتمد Version Catalogs المركزية ونفعل Configuration Cache في الـ CI، مع تشغيل سكريبتات دورية عبر dependency-analysis-android-plugin لحذف التبعيات غير المستخدمة.",
        "how_to_answer_ar": "ابدأ بالتشخيص المنهجي للتبعيات بـ dependencyInsight ثم علاجها بالقيود لا بالفرض، وانتقل لقياس أداء البناء بـ Build Scans ومسار المهام الحرج وحالات الـ Cache Misses.",
        "talking_points_ar": "أمر dependencyInsight، استراتيجية latest version wins، القيود الغنية strictly، تقارير Build Scans، وعزل مدخلات الـ Tasks لمنع إبطال الكاش.",
        "follow_ups_ar": "- **المحاور:** 'ما الفرق الجوهري بين implementation و api في سياق تعارض التبعيات وسرعة البناء؟'\n  **المرشح:** 'المكتبة المضافة بـ implementation تقتصر على الموديول الحالي ولا تتسرب لمستهلكيه، مما يمنع إعادة تجميع الموديولات الأخرى ويسرع البناء؛ بينما api تعيد تصدير المكتبة لكافة الموديولات التابعة مما يزيد من مخاطر تعارض الإصدارات.'\n\n- **المحاور:** 'لماذا قد تفشل مهمة معينة في الاستفادة من Build Cache رغم عدم تعديل أي كود؟'\n  **المرشح:** 'يرجع ذلك لوجود مدخلات متغيرة وغير مستقرة في المهمة مثل التواريخ الزمنية أو مسارات الملفات المطلقة الخاصة بجهاز المطور، مما يغير الـ Cache Key ويجبر Gradle على إعادة تشغيلها من الصفر.'",
        "self_check_ar": "هل شرحت تشخيص التبعيات بـ dependencyInsight وقيود strictly، وتحليل بطء البناء بـ Build Scans ومصائد الكاش؟",
                "references_ar": f"- [Gradle: Inspecting and debugging dependencies](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html) — التوثيق الرسمي لتشخيص وفحص شجرة التبعيات في Gradle.\n- [Gradle: Understanding build performance](https://docs.gradle.org/current/userguide/performance.html) — الدليل الشامل لتحسين أداء وسرعة البناء.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """يتم التحقيق في تعارض التبعيات باستخدام أمر dependencyInsight لتتبع شجرة التبعيات ومعرفة سبب اختيار الإصدار، مع تثبيت الإصدارات عبر Version Catalogs والقيود الصارمة. وفي تراجع سرعة البناء نولد تقرير Build Scan لتحليل زمن المهام في المسار الحرج واكتشاف أسباب ضياع التخزين المؤقت ومعالجات الـ Annotations البطيئة.""",
        "best_answer_ar": """عند مواجهة تعارض في إصدارات التبعيات أو تباطؤ في سرعة البناء، نتبع مساراً تشخيصياً يعتمد على القياس الدقيق للأدوات الرسمية.
في تعارض التبعيات، يقوم Gradle افتراضياً باختيار أعلى إصدار مطلوب تلقائياً، وهو ما قد يقود إلى عدم توافق ثنائي في الدوال إذا حمل الإصدار الجديد تغييرات كاسرة. للتحقيق في ذلك، نشغل أمر dependencyInsight على مسار الكلاسات التنفيذي للنسخة المحددة؛ حيث يعرض السجل مسار الاستدعاء الكامل والموديول المسؤول عن طلب الإصدار. ونعالج ذلك باستخدام قيود صارمة في Version Catalogs أو تفعيل failOnVersionConflict لاكتشاف التباين مبكراً.
أما في انحدار سرعة البناء، فنبتعد عن التخمين وننشئ تقرير Gradle Build Scan. يتيح لنا هذا التقرير فحص المخطط الزمني وفصل زمن التهيئة عن زمن التنفيذ، وتحديد المهام الواقعة على المسار الحرج، ومعرفة المهام التي فشلت في استخدام التخزين المؤقت بسبب مدخلات متغيرة، بالإضافة إلى قياس زمن معالجة الأكواد التوليدية بين KAPT و KSP.""",
        "deep_answer_ar": """في هندسة منصات أندرويد للمشاريع الضخمة، تمثل إدارة التبعيات وسرعة البناء ركيزتين أساسيتين لاستقرار النظام وإنتاجية الفرق البرمجية.
إن اللجوء السريع إلى فرض الإصدارات عبر resolutionStrategy.force يمثل نمطاً هندسياً خطيراً؛ فهو يخفي التعارض دون معالجة عدم التوافق البرمجي، مما يؤدي إلى انهيار التطبيق أثناء التشغيل بخطأ NoSuchMethodError عند استدعاء دوال حُذفت في الإصدار المرفوع. والحل المعماري السليم هو استخدام القيود الغنية بكلمة strictly؛ حيث تمنع الترقية الصامتة لأي تبعية وسيطة وتجبر المطور على مراجعة التغييرات والتأكد من توافق واجهات البرمجة. كما ندمج أدوات فحص التبعيات الآلية في خطوط الـ CI لاكتشاف التبعيات الميتة والتبعيات المتسربة عبر حدود الموديولات.
وفيما يتعلق بانهيار سرعة البناء، ينقسم التحقيق إلى ثلاثة محاور رئيسية. المحور الأول هو زمن مرحلة التهيئة Configuration Phase؛ حيث نمنع أي عمليات قراءة ملفات أو استعلامات Git ديناميكية خارج المهام، ونفعل ميزة Gradle Configuration Cache لعزل التهيئة بالكامل. المحور الثاني هو فحص أسباب فشل التخزين المؤقت؛ فإذا كانت المهمة تعتمد على مسارات ملفات مطلقة تتغير بين جهاز وآخر أو تستخدم طوابع زمنية، يتغير مفتاح الكاش وتُعاد المهمة دون داعٍ. والمحور الثالث هو معالجات الـ Annotations؛ حيث نوجه الفرق نحو استبدال KAPT بمحرك KSP الذي يتكامل مباشرة مع الـ Compiler ويتفادى توليد ملفات Java Stubs، مما يقلل وقت التجميع بنسبة تتجاوز ثلاثين بالمائة في المشاريع الكبرى."""
    }
}

# ==========================================
# BLD-16: How do you set up reproducible builds and dependency verification?
# ==========================================
DATA["BLD-16"] = {
    "concept_en": """Establishing reproducible builds and dependency verification secures the software supply chain against tampering and guarantees deterministic artifact creation:
- Software Supply Chain Vulnerabilities:
  1. Compromised Repositories: Malicious or compromised mirrors replacing published AAR/JAR binaries with backdoored variants sharing identical artifact coordinates.
  2. Dependency Confusion: Attackers publishing public packages on Maven Central whose group and artifact IDs mimic internal private corporate modules.
  3. Dynamic Resolution Tampering: Version ranges (e.g. 1.+) or dynamic SNAPSHOTs pulling unreviewed code modifications automatically.
- Gradle Dependency Verification:
  - Cryptographic Verification: Native Gradle mechanism checking SHA-256 checksums and PGP cryptographic signatures for all downloaded dependencies, POM files, and Gradle plugins.
  - Verification Metadata: Stored in gradle/verification-metadata.xml and tracked in Git version control. Generated via ./gradlew --write-verification-metadata sha256,pgp help.
  - Hardened Repositories: Explicit repository ordering and content filtering via content { includeGroup(...) } ensuring private artifacts only resolve from internal authenticated feeds.
- Reproducible Builds Mechanics (Bitwise Identical Binaries):
  - Deterministic Toolchain: Enforce strict JVM compilation baselines via jvmToolchain(17) to eliminate local JDK compiler variances.
  - Archive Determinism: Configure ZIP and APK packaging tasks with isReproducibleFileOrder = true and isPreserveFileTimestamps = false to strip variable file creation timestamps and enforce alphabetical file sorting.
  - R8 Determinism: Guaranteeing identical dictionary obfuscation seeds across environments.""",
    "walkthrough_en": """Generating verification metadata and enforcing reproducible builds:
```bash
# 1. Generate the initial cryptographic verification metadata lockfile:
./gradlew --write-verification-metadata sha256,pgp help

# This creates gradle/verification-metadata.xml, which must be committed to Git.
```

```kotlin
// 2. Configure reproducible packaging and JDK toolchain in build.gradle.kts:
tasks.withType<Zip>().configureEach {
    isReproducibleFileOrder = true       // Guarantees deterministic alphabetical entry ordering
    isPreserveFileTimestamps = false     // Strips variable file creation timestamps from ZIP headers
}

kotlin {
    jvmToolchain(17) // Enforces identical JDK bytecode target across all developer machines and CI
}

// 3. Repository content filtering to prevent Dependency Confusion in settings.gradle.kts:
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
        maven {
            url = uri("https://internal.repo.company.com/maven")
            content {
                includeGroup("com.company.internal") // Only internal packages resolve here
            }
        }
    }
}
```""",
    "short_en": """Setting up reproducible builds and supply chain security requires enabling Gradle dependency verification to enforce cryptographic SHA-256 checksums and PGP signatures stored in verification-metadata.xml. For deterministic artifact creation, we enforce unified compiler versions using jvmToolchain and configure packaging tasks to enforce alphabetical file sorting while stripping volatile filesystem timestamps.""",
    "structured_en": """Securing the software build pipeline against supply chain tampering and ensuring reproducible builds requires dual-layer verification.
To protect third-party dependencies, we activate Gradle native dependency verification. Generating gradle/verification-metadata.xml records the cryptographic SHA-256 checksum and PGP digital signature of every downloaded JAR, AAR, and build plugin. When committed to source control, Gradle validates these checksums during compilation. If a compromised Maven mirror or man-in-the-middle proxy attempts to serve a modified binary, Gradle immediately halts the build with an integrity error. Additionally, we enforce repository content filtering to protect internal module namespaces against dependency confusion attacks.
To achieve reproducible builds where identical source commits generate bitwise-identical APKs across any machine, we eliminate environmental variance. We configure Gradle jvmToolchain to guarantee identical JDK compiler implementations between local workstations and continuous integration runners. Finally, we configure all packaging tasks with reproducible file ordering and disabled file timestamps, preventing operating system filesystem variations and creation timestamps from altering binary archive signatures.""",
    "deep_senior_en": """From an enterprise security and platform architecture viewpoint, reproducible builds and dependency verification provide verifiable proof of software provenance and supply chain resilience.
In high-security environments, relying blindly on public artifact coordinates introduces severe vulnerability. Attackers frequently exploit compromised package maintainer accounts or publish malicious packages on public registries matching private internal namespaces. By configuring Gradle dependency verification with both SHA-256 checksums and PGP keys, we ensure that an artifact cannot be altered upstream without triggering an explicit build failure. To guard against dependency confusion, our repository management explicitly maps internal corporate groups exclusively to our private authenticated Maven instances using repository content filtering.
Achieving bitwise reproducible builds requires addressing non-deterministic compilation inputs at every stage of the pipeline. Standard ZIP and APK generation embeds file modification timestamps into archive headers, meaning identical code compiled two seconds apart produces different cryptographic hashes. By setting isPreserveFileTimestamps to false and isReproducibleFileOrder to true, Gradle standardizes entry timestamps to a fixed epoch and forces deterministic alphabetical sorting.
Similarly, compiler toolchain divergence creates subtle bytecode differences. Developers running varying patch releases of Java produce different classfile constant pool arrangements; enforcing Gradle jvmToolchain standardizes the exact compiler runtime across all environments.
Finally, deterministic R8 compilation requires fixing random dictionary seeds and stripping path-dependent debug symbols. With these controls in place, independent security auditors can compile the application from source and verify that the resulting SHA-256 matches the public Google Play distribution exactly, proving the release is free of hidden backdoors.""",
    "meta_ar": {
        "id": "BLD-16",
        "questionAr": "كيف تقوم بإعداد البناء القابل للتكرار حتمياً (Reproducible Builds) والتحقق من التبعيات (Dependency Verification) لحماية سلسلة التوريد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "حماية سلسلة التوريد البرمجية عبر ملف verification-metadata.xml وفحص بصمات SHA-256 وتواقيع PGP، وتوحيد بيئة البناء بـ jvmToolchain، وضمان تطابق مخرجات الـ APK بايت-بايت بتجريد التواريخ وترتيب الملفات.",
        "concept_ar": "يحمي البناء القابل للتكرار حتمياً والتحقق من التبعيات سلسلة التوريد البرمجية من التلاعب: تعتمد آلية Dependency Verification في Gradle على فحص البصمة التشفيرية SHA-256 وتوقيع PGP لكل مكتبة أو إضافة يتم تنزيلها، ومطابقتها بملف verification-metadata.xml المحفوظ في Git؛ فإذا تم استبدال مكتبة على خادم خارجي بكود خبيث يفشل البناء فوراً. كما نطبق فلترة المستودعات content filtering لمنع هجمات Dependency Confusion. ولتحقيق البناء الحتمي المتطابق بايت-بايت، نوحد إصدار الـ JDK عبر jvmToolchain، ونجرد ملفات الـ ZIP والـ APK من التواريخ الزمنية المتغيرة ونلزمها بترتيب أبجدي موحد لضمان تطابق بصمة الـ APK النهائية على أي خادم.",
        "walkthrough_ar": """توليد ملف التحقق من التبعيات وضبط البناء الحتمي في build.gradle.kts:
```bash
# 1. توليد ملف verification-metadata.xml لجميع التبعيات والإضافات:
./gradlew --write-verification-metadata sha256,pgp help
```
```kotlin
// 2. إعداد مهام الحزم والـ Toolchain في build.gradle.kts:
tasks.withType<Zip>().configureEach {
    isReproducibleFileOrder = true       // توحيد ترتيب الملفات داخل الأرشيف
    isPreserveFileTimestamps = false     // تجريد التواريخ الزمنية لمنع اختلاف الـ Hash
}

kotlin {
    jvmToolchain(17) // توحيد إصدار الـ JDK على جميع الأجهزة وسيرفرات الـ CI
}
```""",
        "why_it_matters_ar": "يحمي التطبيق من تضمين مكتبات خارجية مخترقة، ويوفر دليلاً برهانياً لمدققي الأمان بأن ملف الـ APK المنشور يطابق كود المصدر بالضبط.",
        "worked_example_ar": "محاولة استبدال مكتبة داخلية بحزمة عامة خبيثة على Maven Central؛ تم إحباط الهجوم بفضل قيود verification-metadata.xml و content filtering وتوقف البناء فوراً في الـ CI.",
        "trade_offs_ar": "التحقق من التوقيعات يضيف خطوة مراجعة عند ترقية أي مكتبة لتحديث ملف البيانات، ولكنه يوفر حماية أمنية لا غنى عنها للتطبيقات المالية.",
        "failure_modes_ar": "تجاهل ملف verification-metadata.xml أو إضافته لملف .gitignore، واستخدام إصدارات ديناميكية مثل 1.+ تجلب أكواداً غير مفحوصة.",
        "production_perspective_ar": "نعتمد فحص البصمات في كافة خطوط الإنتاج، ونمنع استخدام SNAPSHOT في فروع الـ Release، ونربط مستودعات Maven الخاصة بمصادقة مشفرة.",
        "how_to_answer_ar": "اشرح أولاً حماية التبعيات بـ verification-metadata.xml والبصمات الرقمية، ثم انتقل لآليات البناء الحتمي بتوحيد الـ JDK وتجريد التواريخ وترتيب الـ ZIP.",
        "talking_points_ar": "ملف verification-metadata.xml، بصمات SHA-256 و PGP، هجمات Dependency Confusion، أداة jvmToolchain، وترتيب الحزم وتجريد التواريخ.",
        "follow_ups_ar": "- **المحاور:** 'ما هو هجوم Dependency Confusion وكيف نتصدى له في Gradle؟'\n  **المرشح:** 'هو هجوم ينشر فيه المخترق مكتبة عامة على Maven Central بنفس اسم موديول داخلي للشركة؛ ونتصدى له في settings.gradle بتحديد نطاقات المجموعات عبر includeGroup بحيث تقتصر حزم الشركة على مستودعها الخاص فقط.'\n\n- **المحاور:** 'لماذا تختلف بصمة الـ APK عند بنائه مرتين متتاليتين من نفس الكود في الوضع الافتراضي؟'\n  **المرشح:** 'لأن أرشيف الـ ZIP يسجل التوقيت الزمني لإنشاء كل ملف بداخله، فاختلاف الثواني يغير ترويسة الملفات الثنائية؛ ولذلك نضبط preserveFileTimestamps إلى false لتوحيد التوقيت.'",
        "self_check_ar": "هل غطيت التحقق من التبعيات بـ verification-metadata.xml وتفادي التباين البيئي بـ jvmToolchain وضوابط الـ ZIP؟",
                "references_ar": f"- [Gradle: Verifying dependencies](https://docs.gradle.org/current/userguide/dependency_verification.html) — توثيق التحقق التشفيري من التبعيات في Gradle.\n- [Reproducible Builds: Android Guide](https://reproducible-builds.org/docs/) — دليل إعداد البناء القابل للتكرار حتمياً.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """يتطلب إعداد البناء القابل للتكرار تفعيل ميزة التحقق من التبعيات في Gradle بمطابقة بصمات SHA-256 وتواقيع PGP في ملف verification-metadata.xml، وتوحيد بيئة الترجمة باستخدام jvmToolchain، وضبط مهام الحزم لتوحيد الترتيب الأبجدي للملفات وتجريد التواريخ الزمنية المتغيرة لضمان تطابق الـ APK بايت-بايت.""",
        "best_answer_ar": """لحماية سلسلة توريد البرمجيات وضمان بناء حتمي ومطابق بايت-بايت، نطبق إجراءات تحقق صارمة على مستويين.
المستوى الأول هو التحقق من التبعيات الخارجية؛ حيث نفعل أداة Dependency Verification الرسمية في Gradle وننشئ ملف verification-metadata.xml الذي يحفظ البصمات التشفيرية SHA-256 وتواقيع PGP لكافة المكتبات والإضافات. ويتم حفظ هذا الملف في Git؛ فإذا حاول خادم وسيط تقديم حزمة معدلة خبيثة، يفشل البناء فوراً. كما نحدد نطاقات المجموعات لمستودعاتنا الداخلية لمنع هجمات Dependency Confusion.
المستوى الثاني هو ضمان قابلية البناء للتكرار الحتمي؛ حيث نزيل العوامل المتغيرة التي تسبب اختلاف البصمة النهائية للتطبيق. نلزم الجميع باستخدام نفس إصدار الـ JDK عبر jvmToolchain لتفادي الفروق الدقيقة في مترجم جافا. وأخيراً، نضبط مهام بناء الأرشيفات عبر إلغاء حفظ التواريخ الزمنية للملفات وتفعيل الترتيب الأبجدي الحتمي لمحتويات الـ ZIP، مما يضمن خروج نفس ملف الـ APK بنفس البصمة على أي جهاز خادم.""",
        "deep_answer_ar": """من منظور قيادة الأمان وهندسة البنية التحتية للتطبيقات عالية المخاطر، مثل التطبيقات المالية وتطبيقات الخصوصية، يعد البناء القابل للتكرار حتمياً وتدقيق التبعيات حجر الزاوية للموثوقية البرمجية.
إن الاعتماد الأعمى على مستودعات Maven الخارجية دون بصمات تشفيرية يجعل المشروع عرضة لهجمات استبدال الحزم واختراق حسابات المطورين. فمن خلال تفعيل ملف verification-metadata.xml، نضمن أن أي تغيير في بايت واحد لمكتبة خارجية يوقف خط البناء فوراً. وعلاوة على ذلك، نقوم بتأمين ملف settings.gradle بتوجيه طلبات الحزم الداخلية للشركة حصرياً نحو خوادم Maven الخاصة المشفرة عبر خاصية content filtering، مما يقضي على هجمات Dependency Confusion تماماً.
أما على صعيد البناء الحتمي Reproducible Builds، فالهدف هو تمكين أي مدقق أمني مستقل من تجميع الكود المصدري والحصول على نفس بصمة الـ APK المنشورة في المتجر لإثبات خلوها من الأبواب الخلفية. ولتحقيق ذلك، نعالج مصادر العشوائية في ملفات الثنائيات: أولاً، توحيد بيئة المترجم عبر jvmToolchain لمنع اختلاف مخرجات الـ Bytecode باختلاف نسخ الـ JDK المثبتة محلياً. ثانياً، ضبط أرشيفات ZIP و APK لإسقاط التواريخ المتغيرة وتوحيد ترتيب الملفات، لأن ترويسات ZIP التقليدية تحفظ توقيت الضغط مما يغير الـ Hash بالكامل. ثالثاً، نلزم محرك R8 باستخدام قاموس تشويش حتمي وثابت، ونمنع استخدام التبعيات الديناميكية مثل علامة الزائد أو نسخ SNAPSHOT في إصدارات الإنتاج، مما يضمن استقرار البصمة التشفيرية ومطابقتها مئة بالمائة."""
    }
}

# ==========================================
# BLD-17: An app installs in debug but crashes on launch in release due to renamed classes. How do you prove the cause?
# ==========================================
DATA["BLD-17"] = {
    "concept_en": """Proving startup crashes caused by R8 class renaming requires an evidence-based forensic investigation:
- Root Cause Analysis:
  1. Reflection & Dynamic Class Loading: Code calling Class.forName("com.example.FeatureRouter") or ServiceLoader.load() with hardcoded string identifiers fails because R8 obfuscated the class to an arbitrary short name (e.g. a.b.c).
  2. Manifest Declarations: Dynamically added or placeholder components whose names diverged between manifest merger and DEX shrinking.
  3. Dependency Injection Service Bridges: Reflection-based factories or serialization adapters missing constructor keep rules.
- Step-by-Step Forensic Proof:
  - Step 1: Capture the crash trace via adb logcat -d *:E. Identify the obfuscated token triggering ClassNotFoundException or NoClassDefFoundError.
  - Step 2: De-obfuscate the stack trace using retrace and the build's exact mapping.txt to retrieve the original fully-qualified class name.
  - Step 3: Inspect usage.txt: If the class is listed, R8 treated it as dead code and removed it entirely. If absent from usage.txt but missing at runtime, R8 renamed it without rewriting the dynamic reflection call site.
  - Step 4: Inspect classes.dex with APK Analyzer or dexdump: Verify the presence, package location, and method signatures of the compiled class.
- Remediation: Apply targeted @Keep annotations or surgical keep rules in proguard-rules.pro.""",
    "walkthrough_en": """Forensic CLI commands and targeted keep annotations:
```bash
# 1. Capture the crash stack trace from device:
adb logcat -d *:E | grep -E "FATAL EXCEPTION|ClassNotFoundException"

# 2. De-obfuscate the crash trace using mapping.txt and Retrace:
retrace.sh -verbose app/build/outputs/mapping/release/mapping.txt crash_log.txt

# 3. Prove whether R8 stripped the class by checking usage.txt:
grep "com.example.router.AuthRouter" app/build/outputs/mapping/release/usage.txt
```

```kotlin
// 4. Surgical fix in Kotlin code:
@Keep // Instructs R8 to preserve class name, members, and constructors
class AuthRouterImpl : AuthRouter {
    // Implementation details
}
```""",
    "short_en": """We prove the cause by capturing the startup crash in Logcat, de-obfuscating the trace using mapping.txt and Retrace to identify the target class, and inspecting usage.txt to confirm if R8 pruned it. We inspect DEX contents with APK Analyzer to verify reflection call sites, then apply targeted @Keep annotations to resolve it.""",
    "structured_en": """When an application crashes on launch exclusively in release builds due to renamed classes, senior engineers follow an evidence-based forensic methodology rather than guessing ProGuard rules.
We capture the raw fatal exception from device Logcat. The stack trace typically displays a ClassNotFoundException referencing an obfuscated symbol like a.b.c. We de-obfuscate this trace using Google's Retrace tool paired with the exact mapping.txt generated during that release build, revealing the original fully qualified class name.
Next, we definitively prove the failure mechanism by auditing R8 diagnostic outputs. Searching for the class name in usage.txt confirms whether R8 flagged it as dead code and completely stripped it from the binary. If the class is absent from usage.txt, we inspect the compiled classes.dex using APK Analyzer to verify that the bytecode exists but was renamed, proving that a reflection call site such as Class.forName or a ServiceLoader configuration file failed to resolve the new symbol.
We resolve the defect surgically by applying an explicit @Keep annotation or authoring a targeted ProGuard rule preserving the class and its default constructor, then verify that the class appears in seeds.txt.""",
    "deep_senior_en": """From a platform runtime and bytecode architecture perspective, startup obfuscation crashes occur when dynamic reflection boundaries intersect with static compiler optimization.
During compilation, R8 constructs an execution call graph starting from defined entry points, such as Activities declared in the merged AndroidManifest. When classes are instantiated dynamically—through Java reflection, ServiceLoader mechanisms, or custom dependency injection factories—R8 cannot trace the invocation statically. Consequently, R8 either renames the class during obfuscation or prunes it entirely during tree shaking, leading to immediate ClassNotFoundException crashes on application cold start.
To prove this conclusively, our forensic process relies on three diagnostic artifacts. First, mapping.txt maps obfuscated bytecode coordinates back to original source lines. Second, usage.txt provides undeniable proof of dead code stripping; if a class or its default constructor appears there, R8 actively removed it. Third, seeds.txt lists all symbols explicitly protected by keep rules; if the failing class is absent, our configuration failed to protect it.
Additionally, we inspect META-INF services directories inside the APK. Libraries relying on java.util.ServiceLoader require provider configuration files containing the fully qualified class name. If R8 renames the implementing class without rewriting the service provider file, initialization fails silently or crashes on launch.
Surgical remediation requires avoiding broad package wildcards that bloat DEX size. We decorate the specific implementation with AndroidX Keep or add targeted keepclassmembers rules. To prevent these regressions from ever reaching release stages, our continuous integration pipeline executes an automated sanity launch test against the signed release build on emulators before promoting artifacts to store tracks.""",
    "meta_ar": {
        "id": "BLD-17",
        "questionAr": "تطبيق يُثبت ويعمل في الـ Debug ولكنه ينهار فور الفتح في الـ Release بسبب تشويش الكلاسات. كيف تثبت السبب وتعالجه؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إثبات السبب الجذري برهانياً عبر Logcat وأداة Retrace، وتدقيق تقارير R8 التشخيصية (usage.txt و seeds.txt و mapping.txt)، واستخدام APK Analyzer لفحص ملفات الـ DEX، وتطبيق قواعد Keep جراحية.",
        "concept_ar": "يتطلب إثبات انهيار التطبيق عند بدء التشغيل بسبب تشويش الكلاسات تحقيقاً برهانياً بالأدلة: يحدث الخطأ عندما يعتمد الكود على الـ Reflection أو Class.forName أو ServiceLoader للوصول لكلاس بينما قام R8 بتغيير اسمه إلى رمز مشوش أو حذفه باعتباره كوداً ميتاً. ونثبت السبب عبر أربع خطوات: أولاً التقاط الـ Stack Trace عبر Logcat وفك تشفيره باستخدام mapping.txt وأداة Retrace لمعرفة الكلاس الأصلي. ثانياً فحص ملف usage.txt؛ فإذا وجد اسم الكلاس فيه فهذا دليل قطعي على أن R8 حذفه. ثالثاً فحص ملفات classes.dex بـ APK Analyzer للتأكد من وجود الكلاس باسمه المشوش وفشل استدعائه النصي. ورابعاً معالجة المشكلة جراحياً بإضافة تعليق @Keep والتأكد من ظهوره في seeds.txt.",
        "walkthrough_ar": """خطوات التحقيق في انهيار تشويش الكلاسات وحله بقاعدة جراحية:
```bash
# 1. التقاط تقرير الانهيار من الهاتف:
adb logcat -d *:E | grep -E "FATAL EXCEPTION|ClassNotFoundException"

# 2. فك تشفير الكراش باستخدام mapping.txt وأداة Retrace:
retrace.sh -verbose app/build/outputs/mapping/release/mapping.txt crash_trace.txt

# 3. إثبات حذف الكلاس بفحص ملف usage.txt:
grep "com.example.router.AuthRouter" app/build/outputs/mapping/release/usage.txt
```
```kotlin
// 4. الحل الجراحي بإضافة تعليق @Keep الصريح:
@Keep // يمنع R8 من حذف الكلاس أو تغيير اسمه أو تفريغ مشيداته
class AuthRouterImpl : AuthRouter {
    // التنفيذ البرمجي
}
```""",
        "why_it_matters_ar": "يمنع توقف التطبيق فور الفتح أمام المستخدمين بعد النشر، ويوفر منهجية علمية لتشخيص أخطاء R8 بدلاً من التخمين العشوائي.",
        "worked_example_ar": "انهيار التطبيق فور التشغيل في الإنتاج بسبب كلاس موجه المصادقة AuthRouter المستدعى بالـ Reflection؛ بفك التشفير وبحث usage.txt ثبت حذفه وعولج بـ @Keep.",
        "trade_offs_ar": "استخدام @Keep على كلاسات معينة يحافظ على استقرار التشغيل مع بقاء سائر التطبيق خاضعاً للتقليص والتشويش الكامل دون زيادة حجم الـ APK.",
        "failure_modes_ar": "إضافة قاعدة عامة مثل -keep class com.** مما يعطل التشويش والتقليص لمئات الكلاسات ويزيد حجم الحزمة، أو محاولة فك التشفير بملف mapping لإصدار مختلف.",
        "production_perspective_ar": "نلزم الـ CI بتشغيل اختبار تشغيل سريع (Startup Smoke Test) على نسخة الإنتاج المصغرة، ونرفع ملفات الـ mapping آلياً إلى منصة مراقبة الكراشات.",
        "how_to_answer_ar": "استعرض خطوات الإثبات بالترتيب: فك التشفير بـ Retrace، فحص usage.txt للبرهان، تدقيق DEX بـ APK Analyzer، والحل الجراحي بـ @Keep.",
        "talking_points_ar": "أداة Retrace، ملف usage.txt للكود المحذوف، ملف seeds.txt للكود المحمي، فحص DEX بـ APK Analyzer، ومخاطر القواعد العامة.",
        "follow_ups_ar": "- **المحاور:** 'ما الفرق بين ملف usage.txt وملف seeds.txt في تشخيص أخطاء R8؟'\n  **المرشح:** 'ملف usage.txt يحتوي على كافة الكلاسات والدوال التي حذفها R8 باعتبارها غير مستخدمة؛ بينما ملف seeds.txt يسرد الكلاسات والعناصر التي تم حمايتها بقواعد الحفظ Keep Rules ولم تمس.'\n\n- **المحاور:** 'كيف تتعامل مع كلاسات ServiceLoader الموجودة داخل META-INF/services؟'\n  **المرشح:** 'إذا شوش R8 أسماء الكلاسات المزودة للخدمة دون تحديث الملف النصي داخل META-INF، يفشل ServiceLoader فوراً؛ ولذلك نضيف قاعدة keepnames لكافة الكلاسات التي تطبق واجهات الخدمات.'",
        "self_check_ar": "هل بينت خطوات فك التشفير واستخدام usage.txt و seeds.txt وفحص DEX والحل بـ @Keep؟",
                "references_ar": f"- [Android Developers: R8 Retrace Tool](https://developer.android.com/tools/retrace) — توثيق أداة فك تشفير تقارير الأخطاء المشوشة.\n- [Android Developers: Troubleshoot R8 Shrinking](https://developer.android.com/build/shrink-code#troubleshoot) — الدليل الرسمي لاستكشاف أخطاء تقليص الكود بـ R8.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نثبت السبب الجذري بالتقاط الـ Stack Trace من Logcat وفك تشفيره بـ Retrace وملف mapping.txt لتحديد الكلاس الأصلي، ثم فحص ملف usage.txt لإثبات حذفه بواسطة R8، ومراجعة ملفات DEX عبر APK Analyzer للتأكد من وجود الكلاس المشوش ومكانه، ثم نعالج المشكلة جراحياً بتعليق @Keep.""",
        "best_answer_ar": """عندما ينهار التطبيق فور الفتح في نسخة الإنتاج فقط بسبب تشويش الكلاسات، نتبع مساراً برهانياً قائماً على الأدلة لتحديد السبب الجذري وعلاجه بدقة.
نلتقط سجل الخطأ من Logcat الذي يظهر استثناء ClassNotFoundException يشير إلى اسم مشوش مثل a.b.c. ونمرر هذا السجل لأداة Retrace مع ملف mapping.txt الخاص بنفس الإصدار، مما يكشف الاسم الكامل للكلاس الأصلي ومكان استدعائه.
بعد ذلك، نثبت السبب بشكل قاطع عبر تقارير R8؛ حيث نبحث عن الكلاس داخل ملف usage.txt، فإذا كان مسجلاً هناك فهذا يثبت أن R8 اعتبره كوداً ميتاً وحذفه لعدم وجود استدعاء صريح مباشر. وإذا لم يكن محذوفاً، نفتح الحزمة بأداة APK Analyzer لفحص classes.dex ونتأكد من أن الكلاس موجود ولكن تم تغيير اسمه بينما يحاول كود الـ Reflection أو ServiceLoader الوصول للاسم القديم كنص جامد.
ونصلح المشكلة بإضافة تعليق @Keep على الكلاس المستهدف لحمايته ومشيداته، ونتأكد من ظهوره في ملف seeds.txt.""",
        "deep_answer_ar": """من منظور معماري لتحليل الـ Bytecode وسلوك بيئة التشغيل ART، تنشأ انهيارات بدء التشغيل عند تقاطع الاستدعاء الديناميكي بالـ Reflection مع التحسينات الحادة لمحرك R8.
يبني R8 أثناء الترجمة مخطط استدعاء يبدأ من نقاط الدخول المعلنة صراحة في الـ Manifest. فإذا كان التطبيق يستخدم نمط ServiceLoader أو يعتمد على Class.forName لتحميل موديولات التوجيه والمصادقة، لا يستطيع R8 اكتشاف هذا الرابط الثابت، فيقوم بحذف الكلاس أو تشويش اسمه، مما يفجر استثناء فادحاً عند إقلاع التطبيق.
ولإثبات السبب برهانياً، نستند إلى ثلاثة ملفات تشخيصية رئيسية. الملف الأول هو mapping.txt لفك تشفير تقرير الخطأ بـ Retrace ومعرفة الكلاس الحقيقي. الملف الثاني هو usage.txt؛ فوجود الكلاس فيه يمثل دليلاً قاطعاً على حذفه، مما يؤكد غياب قواعد الحفظ. الملف الثالث هو seeds.txt؛ حيث نتحقق منه للتأكد من أن قواعد الحفظ الحالية لم تطبق على الكلاس. كما نفحص ملفات مجلد META-INF services داخل ملف الـ APK؛ إذ إن تغيير اسم الكلاس المنفذ للخدمة دون تحديث ملف التعريف النصي يؤدي لفشل فوري أثناء التهيئة.
ولعلاج المشكلة هندسياً، نتجنب تماماً استخدام القواعد العامة التي تعطل التشويش عن حزم كاملة، ونطبق تعليق Keep الجراحي أو نحدد المشيدات المطلوبة فقط في ملف ProGuard. ولمنع تكرار هذه الانهيارات، نلزم خطوط الـ CI بتشغيل اختبار إقلاع آلي على أجهزة حقيقية أو محاكيات باستخدام نسخة الـ Release الموقعة قبل اعتماد النسخة للتوزيع."""
    }
}

# ==========================================
# BLD-18: A release manifest merge drops a required ContentProvider authority. What CI check would catch it?
# ==========================================
DATA["BLD-18"] = {
    "concept_en": """Detecting dropped manifest components and authorities during release builds requires automated verification of the merged manifest artifact:
- Root Causes of Dropped Manifest Authorities:
  1. Manifest Merging Directives: An upstream library or build flavor using tools:node="remove" targeting a shared component, inadvertently stripping it.
  2. Attribute Conflicts: Incompatible tools:replace="android:authorities" resolving to an incorrect value or stripping secondary providers.
  3. Product Flavor Overrides: A flavor manifest lacking the provider declaration overriding lower-priority manifests.
  4. Silent Failures: Missing authorities prevent dynamic ContentProvider initialization (e.g. AndroidX App Startup, Firebase Init Provider), causing silent downstream SDK failures or runtime crashes.
- Verification & Diagnostic Tools:
  - Manifest Merger Report: app/build/outputs/logs/manifest-merger-release-report.txt documents the origin, decision rationale, and rejection reasons for every XML element.
  - Merged Manifest Artifact: Located at app/build/intermediates/merged_manifests/release/AndroidManifest.xml.
- Automated CI Guardrails:
  - Automated Unit/CI Test: Parsing the merged manifest XML and asserting that mandatory authorities, permissions, and exported attributes exist.
  - AAPT2 Binary Assertion: Executing aapt2 dump badging app-release.apk to inspect the compiled binary resource table.
  - Custom Android Lint Rule: Authoring an XmlScanner detector running during lintRelease to flag missing provider authorities.""",
    "walkthrough_en": """Automated CI test and diagnostic verification commands:
```kotlin
// 1. Automated CI Test verifying critical ContentProvider authorities in the merged manifest:
class ManifestIntegrityTest {
    @Test
    fun verifyRequiredContentProvidersAreNotDropped() {
        val manifestFile = File("build/intermediates/merged_manifests/release/AndroidManifest.xml")
        assertTrue("Merged manifest must exist", manifestFile.exists())

        val content = manifestFile.readText()
        val expectedAuthority = "com.example.app.authprovider"

        assertTrue(
            "CRITICAL: Authority '$expectedAuthority' was dropped during release manifest merge!",
            content.contains("android:authorities=\"$expectedAuthority\"")
        )
    }
}
```

```bash
# 2. Inspecting the merge report for drop justification:
grep -A 5 "android:authorities=\"com.example.app.authprovider\"" \
  app/build/outputs/logs/manifest-merger-release-report.txt

# 3. Binary assertion via AAPT2 in CI runner:
aapt2 dump badging app/build/outputs/apk/release/app-release.apk | grep "provider"
```""",
    "short_en": """We catch dropped manifest authorities in CI by asserting their presence directly in the final merged AndroidManifest.xml after the processReleaseManifest task. We run automated unit tests parsing the merged XML for required authorities, inspect manifest-merger-release-report.txt for unexpected removal actions, and verify binary badging via AAPT2 before artifact signing.""",
    "structured_en": """When a release manifest merge drops an essential ContentProvider authority, the application can suffer silent SDK failures or runtime initialization crashes.
To prevent this in continuous integration, we implement automated assertions hooked directly after the processReleaseManifest task. A dedicated CI test parses the merged manifest located in build intermediates using an XML parser. It asserts that mandatory ContentProvider authorities, exported flags, and permission attributes exist exactly as expected. If an upstream dependency declared tools:node=\"remove\" or a flavor conflict stripped the authority, the CI job fails immediately with a descriptive error.
For diagnostic investigations, we audit the manifest-merger-release-report.txt log generated by AGP. This report provides a complete audit trail recording the origin and justification for every element included, replaced, or discarded during the merge.
Finally, we execute a post-packaging binary verification step using aapt2 dump badging against the release APK. Verifying that the compiled Android resource table contains the declared provider guarantees that the binary distributed to users matches our architectural contracts.""",
    "deep_senior_en": """From a release engineering and platform governance standpoint, manifest merging represents a critical vulnerability surface because downstream dependencies and build flavors can silently mutate application declarations without causing compilation errors.
In modern Android architecture, initialization providers such as AndroidX App Startup or Firebase Init Provider manage essential runtime bootstrapping. If an upstream SDK or conflicting flavor configuration introduces a tools:node=\"remove\" or poorly scoped tools:replace directive, the provider authority is dropped. At runtime, components attempting to resolve content URIs crash with IllegalArgumentException, or dependent security SDKs fail to initialize silently, leaving the application running in an insecure state.
To construct robust CI guardrails against these regressions, we implement a multi-layered verification strategy. First, we write an in-house Android Lint rule implementing Detector.XmlScanner. This detector runs during lintRelease, inspecting the merged XML AST for mandatory provider authorities and verifying that android:exported attributes conform to security baselines.
Second, we implement a custom Gradle verification task registered to run immediately after processReleaseManifest and before R8 execution. This task parses the merged AndroidManifest.xml and validates expected provider authorities against an architectural manifest baseline, failing the build on any missing entry.
Third, in our post-packaging release pipeline, we run aapt2 dump badging against the finalized APK. This validates what is actually compiled into the binary resource table, ensuring that obfuscation and resource packaging did not alter manifest metadata. By combining compile-time linting, intermediate manifest assertions, and binary dump auditing, we guarantee complete manifest integrity across all release variants.""",
    "meta_ar": {
        "id": "BLD-18",
        "questionAr": "أثناء دمج ملفات الـ Manifest في الـ Release تم إسقاط عنوان ContentProvider مطلوب. ما الفحص الآلي في الـ CI الذي يكشفه؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "كشف حذف عناصر الـ Manifest المدمجة، وفحص تقرير manifest-merger-release-report.txt، وبناء اختبارات CI آلية تفحص ملف AndroidManifest المدمج، والتحقق عبر AAPT2 وقواعد Lint المخصصة.",
        "concept_ar": "يتطلب اكتشاف إسقاط عناصر الـ Manifest وعناوين الـ ContentProvider في الـ Release إعداد فحوصات آلية في خط الـ CI: يحدث الإسقاط عندما تستخدم مكتبة خارجية أو نكهة بناء قاعدة tools:node=\"remove\" أو يحدث تعارض في tools:replace=\"android:authorities\"، مما يؤدي لحذف الـ Provider بصمت دون أي خطأ في الترجمة. ويترتب على ذلك انهيار التطبيق عند استدعاء الـ URI أو فشل تهيئة مكتبات مثل AndroidX App Startup. ونكشف ذلك عبر: أولاً فحص تقرير manifest-merger-release-report.txt الذي يسجل سبب حذف كل عنصر. ثانياً كتابة اختبار آلي في الـ CI يقرأ ملف AndroidManifest.xml المدمج في مجلد intermediates ويتأكد من وجود الـ authority والخصائص الأمنية. وثالثاً فحص الحزمة النهائية بأمر aapt2 dump badging للتأكد من وجود الـ Provider في جدول الموارد الثنائي.",
        "walkthrough_ar": """تنفيذ فحص آلي في الـ CI للتأكد من عدم إسقاط الـ ContentProvider:
```kotlin
// اختبار آلي يعمل في الـ CI لفحص الـ Manifest المدمج النهائي:
class ManifestIntegrityTest {
    @Test
    fun verifyRequiredContentProvidersAreNotDropped() {
        val manifest = File("build/intermediates/merged_manifests/release/AndroidManifest.xml")
        assertTrue("Merged manifest must exist", manifest.exists())

        val content = manifest.readText()
        val expectedAuthority = "com.example.app.authprovider"

        assertTrue(
            "CRITICAL: Authority '$expectedAuthority' was dropped during manifest merge!",
            content.contains("android:authorities=\"$expectedAuthority\"")
        )
    }
}
```
```bash
# فحص الحزمة النهائية بأداة AAPT2 في الـ CI:
aapt2 dump badging app-release.apk | grep "provider"
```""",
        "why_it_matters_ar": "يمنع نشر نسخ معطوبة تفشل فيها عمليات تهيئة التطبيق الأساسية ومكتبات التتبع والأمان بسبب الحذف الصامت لعناصر الـ Manifest.",
        "worked_example_ar": "مكتبة خارجية استخدمت tools:node=\"remove\" أسقطت مزود تهيئة AndroidX Startup؛ كشفه اختبار CI آلي يفحص الـ Merged Manifest وأوقف النشر قبل وصوله للإنتاج.",
        "trade_offs_ar": "إضافة اختبارات فحص الـ Manifest في الـ CI تزيد وقت البناء بضع ثوانٍ ولكنها تحمي التطبيق من انهيارات صامتة يصعب تتبعها.",
        "failure_modes_ar": "الاعتماد على نجاح التجميع فقط دون فحص الـ Manifest المدمج، أو استخدام tools:replace عشوائياً لإسكات تحذيرات الدمج.",
        "production_perspective_ar": "نعتمد قواعد Lint داخلية للتحقق من الـ Manifest، ونفحص الـ Merged Manifest في كل Pull Request يغير التبعيات أو نكهات البناء.",
        "how_to_answer_ar": "وضح أسباب إسقاط العناصر بـ tools:node، ثم اشرح الفحص الآلي لملف الـ Manifest المدمج في CI، وتقارير الدمج، وفحص الحزمة بـ AAPT2.",
        "talking_points_ar": "تقرير manifest-merger-release-report.txt، فحص Merged Manifest برمجياً في الـ CI، أداة aapt2 dump badging، ومخاطر tools:node remove.",
        "follow_ups_ar": "- **المحاور:** 'ما الدور الذي يلعبه ملف manifest-merger-release-report.txt في تتبع المشكلة؟'\n  **المرشح:** 'هذا الملف يمثل سجلاً تدقيقياً كاملاً يوثق مصدر كل عنصر وقرار الدمج؛ فإذا تم حذف Provider، يوضح التقرير السطر الدقيق والمكتبة أو النكهة التي طلبت إزالته وسبب القرار.'\n\n- **المحاور:** 'ما الخطر الأمني إذا تم إسقاط مزود تهيئة مثل androidx.startup.InitializationProvider؟'\n  **المرشح:** 'إذا سقط مزود التهيئة، تفشل كافة مكتبات الأمان والتحليلات المعتمدة عليه في التهيئة التلقائية عند تشغيل التطبيق، مما يترك التطبيق يعمل في حالة غير مهيأة وغير مؤمنة.'",
        "self_check_ar": "هل شرحت أسباب إسقاط الـ Provider واختبار الـ CI الآلي وفحص AAPT2 وتقارير الدمج؟",
                "references_ar": f"- [Android Developers: Manage manifest files](https://developer.android.com/build/manage-manifests) — توثيق إدارة ودمج ملفات الـ Manifest في أندرويد.\n- [Android Developers: Manifest Merger Tool](https://developer.android.com/tools/manifest-merger) — تفاصيل عمل أداة دمج ملفات الـ Manifest وقواعدها.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نكتشف إسقاط عنوان ContentProvider في الـ CI بإضافة اختبار آلي يفحص ملف AndroidManifest.xml المدمج في مجلد intermediates بعد مهمة processReleaseManifest ويتأكد من وجود الـ authority، مع تدقيق تقرير manifest-merger-release-report.txt، وفحص الـ APK النهائي بأداة aapt2 dump badging قبل النشر.""",
        "best_answer_ar": """عندما يؤدي دمج ملفات الـ Manifest إلى إسقاط عنوان ContentProvider مطلوب، قد ينهار التطبيق عند التشغيل أو تفشل تهيئة مكتبات الأمان بصمت.
لمنع وصول هذه المشكلة إلى الإنتاج، نعتمد فحصاً آلياً في خط الـ CI يعمل فور انتهاء مهمة processReleaseManifest. يقوم الاختبار بقراءة ملف AndroidManifest المدمج داخل مجلد intermediates والتحقق باستخدام محلل XML من وجود الـ Provider وعنوانه الصريح والخصائص الأمنية مثل exported والأذونات المطلوبة؛ وإذا تم إسقاط العنصر بسبب تعارض في نكهات البناء أو قاعدة tools:node=\"remove\" من مكتبة وسيطة، يفشل البناء فوراً مع رسالة واضحة.
وللتحقيق في سبب الإسقاط، نراجع تقرير manifest-merger-release-report.txt الذي يسجل أصل كل عنصر وقرار الدمج بالتفصيل. كما ننفذ خطوة فحص نهائية على الـ APK الموقع باستخدام أداة aapt2 dump badging للتأكد من وجود الـ Provider في جدول الموارد الثنائي الفعلي قبل رفعه للمتجر.""",
        "deep_answer_ar": """من منظور حوكمة الإصدارات وهندسة المنصات، يمثل دمج ملفات الـ Manifest ثغرة خفية لأن التبعيات الخارجية ونكهات البناء يمكنها تعديل بيانات التطبيق دون إظهار أي أخطاء أثناء الترجمة.
في المعمارية الحديثة، تعتمد مكتبات التهيئة مثل AndroidX App Startup على مزودات محتوى تعمل تلقائياً عند إقلاع العملية لتجهيز المكونات الحساسة. فإذا تضمنت مكتبة وسيطة قاعدة tools:node=\"remove\" تستهدف نفس العنصر أو حدث تعارض في tools:replace، يتم حذف الـ Provider بالكامل. والنتيجة هي فشل صامت لمكتبات التشفير أو انهيار فوري عند محاولة النظام الوصول إلى الـ ContentProvider.
ولبناء شبكة أمان صارمة في الـ CI، نطبق نظام فحص ثلاثي الأبعاد. أولاً، نكتب قاعدة فحص خاصة عبر Android Lint تمسح شجرة الـ XML للـ Manifest المدمج للتأكد من توافق العناوين مع المعايير الأمنية. ثانياً، نضيف مهمة Gradle مخصصة تعمل بعد معالجة الـ Manifest وتقارن المكونات المدمجة بالقائمة المرجعية المعتمدة للمشروع وتوقف البناء عند أي نقص. ثالثاً، نشغل فحصاً ثنائياً باستخدام aapt2 dump badging على ملف الـ APK النهائي داخل الـ CI للتأكد من أن عملية التقليص والحزم لم تؤثر على تعريفات المكونات. وبذلك نضمن سلامة الـ Manifest مئة بالمائة عبر كافة نكهات وإصدارات الإنتاج، وندمج هذا الفحص كشرط إلزامي لقبول أي تعديل على كود المشروع لحماية استقرار التطبيق وموثوقيته."""
    }
}

# ==========================================
# BLD-19: A release bundle was signed with the wrong key. How do you contain it and correct the pipeline?
# ==========================================
DATA["BLD-19"] = {
    "concept_en": """Containing and remediating an artifact signed with the incorrect cryptographic key depends on distribution architecture and key management governance:
- Blast Radius Assessment Across Channels:
  1. Google Play Console (Play App Signing Enrolled): Play Console verifies upload certificates automatically. Uploading an AAB signed with an unrecognized key fails immediately with an upload certificate mismatch error. Zero production users are impacted.
  2. Alternative Distribution & Direct APK/MDM: Android's package manager strictly enforces signature matching across updates. Updating an existing install with a divergent signature fails with INSTALL_FAILED_UPDATE_INCOMPATIBLE. Existing installs remain untouched, but the update rollout is blocked.
- Containment Protocol:
  - Halt the deployment track immediately in CI/CD and deployment dashboards (Play Console, Fastlane, or internal MDM).
  - Purge and revoke defective artifacts from all distribution registries and CDNs.
- Google Play Upload Key Reset Protocol:
  - If the original upload key was lost or compromised, the Google Play Console Account Owner navigates to Setup -> App Signing and requests an Upload Key Reset.
  - Submit the public PEM certificate of a newly generated upload key. Google updates the registration within 24 to 48 hours without affecting the master App Signing Key or user base.
- CI/CD Pipeline Correction & Hardening:
  - Isolate signing keystores and credentials within Protected GitHub Environments requiring mandatory manual approval for production tags.
  - Implement a pre-publish CI assertion task: Run keytool or apksigner to verify the artifact's SHA-256 fingerprint against the pinned production certificate before allowing upload.""",
    "walkthrough_en": """Cryptographic inspection commands and automated CI pre-flight verification:
```bash
# 1. Inspect the cryptographic certificate fingerprint of the signed bundle:
keytool -printcert -jarfile app/build/outputs/bundle/release/app-release.aab | grep "SHA256:"

# 2. Automated CI pre-flight verification script:
EXPECTED_SHA256="A1:B2:C3:D4:E5:F6:12:34:56:78:90:AB:CD:EF:11:22:33:44:55:66:77:88:99:00:AA:BB:CC:DD:EE:FF"
ACTUAL_SHA256=$(keytool -printcert -jarfile app-release.aab | awk '/SHA256:/ {print $2}')

if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "CRITICAL SECURITY FAILURE: Signing key mismatch! Expected $EXPECTED_SHA256 but got $ACTUAL_SHA256"
    exit 1
fi

# 3. Halt release track via Fastlane:
bundle exec fastlane supply halt --track production
```""",
    "short_en": """If uploaded to Google Play with Play App Signing, the console rejects mismatched upload keys automatically. For direct APK distribution, we halt deployments immediately to prevent installation failures. We correct the pipeline by securing keystores in protected CI environments with mandatory peer approvals and adding pre-flight fingerprint checks asserting expected SHA-256 signatures before publishing.""",
    "structured_en": """Containing and rectifying an artifact signed with the incorrect cryptographic key requires swift containment followed by pipeline hardening.
First, we evaluate the blast radius. If the project utilizes Google Play App Signing, the Play Console automatically validates the upload certificate and rejects the artifact with an explicit signature mismatch error. This guarantees zero impact on end-users. If the artifact was distributed directly via enterprise MDM or external channels, Android package manager rejects the update with an incompatible update error. In this scenario, we halt the deployment pipeline immediately and purge the invalid artifact from distribution networks.
Second, if the upload key was irrevocably lost, the Play Console account owner initiates an official Upload Key Reset request submitting the public PEM certificate of a newly generated key, which Google activates within forty-eight hours without disrupting the installed user base.
Finally, we harden the continuous integration pipeline against recurrence. We move signing credentials into protected GitHub environments requiring mandatory senior approvals for release executions, and insert an automated pre-flight assertion task that extracts the artifact's SHA-256 certificate fingerprint using keytool, aborting the build immediately on any divergence.""",
    "deep_senior_en": """From a cryptographic identity governance and release operations perspective, an app signed with the wrong key exposes fundamental pipeline vulnerabilities that demand systemic mitigation.
Under Android's operating system security model, cryptographic signatures establish application identity and govern shared user IDs, signature-level permissions, and update integrity. When an update signature diverges from the installed base, the package manager rejects the update outright to prevent application hijacking. If Play App Signing is configured, Google maintains the master app signing key in secure cloud infrastructure, meaning a compromised or incorrect upload key only prevents uploading to the console and cannot compromise distributed binaries.
If an upload key is lost or corrupted, the account owner requests an upload key reset in Google Play Console. This requires generating a fresh keystore, exporting its public X.509 certificate in PEM format, and submitting it through the support workflow. Google verifies account ownership and updates the allowed upload certificate within one to two business days without forcing existing users to reinstall.
To eliminate this risk permanently in the build pipeline, we implement automated cryptographic guardrails. Signing configurations must never reference local developer keys or fallback debug keystores in release builds. We encapsulate production signing secrets in protected CI environments restricted strictly to protected release branches and tags, requiring multi-party approval before execution.
Furthermore, our continuous integration workflow executes a mandatory pre-publish validation step using apksigner or keytool. This step parses the compiled bundle or APK, extracts the SHA-256 certificate fingerprint, and compares it against an immutable pinned value stored in repository governance configuration. If the fingerprint fails to match, the pipeline aborts before publishing artifacts, eliminating human error.""",
    "meta_ar": {
        "id": "BLD-19",
        "questionAr": "تم توقيع ملف الـ Release بمفتاح خاطئ (Wrong Key). كيف تحتوي المشكلة وتصحح الـ Pipeline فورياً؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تقييم نطاق الضرر في Google Play والـ MDM، وإجراءات الاحتواء الفوري، وبروتوكول إعادة تعيين Upload Key في Play Console، وتحصين مسار الـ CI بـ Protected Environments وفحص بصمة SHA-256.",
        "concept_ar": "يعتمد احتواء وتصحيح توقيع الحزمة بمفتاح خاطئ على تقييم نطاق الضرر وقنوات التوزيع: إذا كان التطبيق مسجلاً في Play App Signing، يرفض Google Play Console الحزمة فوراً برسالة خطأ في شهادة الرفع، فلا يتأثر أي مستخدم نهائي. أما في التوزيع المباشر أو الـ MDM، يرفض نظام أندرويد تثبيت التحديث بخطأ INSTALL_FAILED_UPDATE_INCOMPATIBLE حماية لبيانات المستخدم. ونحتوي المشكلة بإيقاف مسار النشر فوراً وسحب النسخة من خوادم التوزيع. وإذا فُقد مفتاح الرفع الأصلي، يطلب مالك الحساب إعادة تعيين Upload Key بتقديم شهادة PEM العامة ليتم تفعيلها خلال 48 ساعة دون المساس بمفتاح التوقيع الرئيسي أو المستخدمين. ولتحصين الـ CI، نعزل المفاتيح في بيئات محمية تتطلب موافقة يدوية، ونضيف خطوة فحص آلية تقارن بصمة SHA-256 بالبصمة الرسمية قبل الرفع.",
        "walkthrough_ar": """فحص بصمة مفتاح التوقيع في الـ CI قبل رفع الحزمة للمتجر:
```bash
# 1. فحص بصمة الـ SHA-256 لشهادة التوقيع في ملف الـ AAB:
keytool -printcert -jarfile app-release.aab | grep "SHA256:"

# 2. التحقق الآلي في سكريبت الـ CI ومقارنة البصمة بالبصمة المعتمدة:
EXPECTED_SHA256="A1:B2:C3:D4:E5:F6:12:34:56:78:90:AB:CD:EF:11:22:33:44:55:66:77:88:99:00:AA:BB:CC:DD:EE:FF"
ACTUAL_SHA256=$(keytool -printcert -jarfile app-release.aab | awk '/SHA256:/ {print $2}')

if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "CRITICAL ERROR: Signing key mismatch! Expected $EXPECTED_SHA256 but got $ACTUAL_SHA256"
    exit 1
fi
```""",
        "why_it_matters_ar": "يحمي هوية التطبيق التشفيرية، ويمنع تعطل تحديثات التطبيق لدى المستخدمين وفقدان الاتصال بالمتجر.",
        "worked_example_ar": "توقيع نسخة المتجر بمفتاح بيئة الـ Staging بالخطأ؛ رفضها Google Play Console فورياً، وتم تصحيح سكريبت الـ CI بإضافة فحص البصمة لمنع تكرار الخطأ.",
        "trade_offs_ar": "الاعتماد على Play App Signing يحمي من فقدان المفتاح الرئيسي ويتيح تدوير مفتاح الرفع، ولكنه يمنح جوجل حق توقيع النسخة النهائية الموزعة.",
        "failure_modes_ar": "تخزين مفاتيح الإنتاج في مستودع الـ Git أو السماح بتوقيع نسخ الـ Release بمفاتيح debug افتراضية عند غياب متغيرات البيئة.",
        "production_perspective_ar": "نستخدم GitHub Actions Protected Environments التي تتطلب موافقة مهندسين اثنين للوصول لمفاتيح الإنتاج، مع فحص بصمة SHA-256 قبل الرفع.",
        "how_to_answer_ar": "ابدأ بتقييم نطاق الضرر في المتجر مقارنة بالـ MDM، ثم خطوات الاحتواء وإعادة تعيين Upload Key، وأخيراً تحصين خط الـ CI بالفحص الآلي والموافقات.",
        "talking_points_ar": "خدمة Play App Signing، خطأ UPDATE_INCOMPATIBLE، بروتوكول Upload Key Reset، فحص بصمة SHA-256 بـ keytool، و Protected Environments.",
        "follow_ups_ar": "- **المحاور:** 'ماذا يحدث إذا فقدت الشركة المفتاح الأصلي لتطبيق موزع خارج Google Play دون Play App Signing؟'\n  **المرشح:** 'إذا فُقد المفتاح الأصلي في التوزيع الخارجي، يستحيل تحديث النسخ المثبتة على هواتف المستخدمين؛ ويضطر المطور لتغيير Application ID وإجبار المستخدمين على حذف التطبيق وإعادة تثبيته مع فقدان كافة البيانات المحلية.'\n\n- **المحاور:** 'كم من الوقت تستغرق جوجل لتفعيل مفتاح رفع Upload Key جديد بعد طلب إعادة التعيين؟'\n  **المرشح:** 'تستغرق العملية عادة ما بين 24 إلى 48 ساعة بعد تقديم الشهادة العامة بصيغة PEM والتحقق من هوية مالك الحساب، وبعدها يمكن رفع النسخ الجديدة فوراً.'",
        "self_check_ar": "هل شرحت نطاق الضرر في المتجر والـ MDM وبروتوكول Upload Key Reset وفحص بصمة SHA-256 في CI؟",
                "references_ar": f"- [Google Play: Use Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756) — الدليل الرسمي لخدمة Play App Signing وإدارة مفاتيح الرفع.\n- [Android Developers: Sign your app](https://developer.android.com/build/sign-build) — توثيق توقيع التطبيقات والمفاتيح التشفيرية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """إذا تم رفع الحزمة لـ Google Play يرفضها المتجر تلقائياً لعدم تطابق مفتاح الرفع، أما في التوزيع المباشر فنوقف النشر فوراً لتجنب فشل التثبيت. ونصحح الـ Pipeline بعزل المفاتيح في بيئات محمية بـ CI تتطلب موافقة يدوية، وإضافة فحص آلي يطابق بصمة SHA-256 لشهادة الحزمة بالبصمة الرسمية قبل النشر.""",
        "best_answer_ar": """يتطلب احتواء وتصحيح توقيع التطبيق بمفتاح خاطئ تقييماً فورياً لنطاق الضرر يليه تحصين هندسي لمسار الـ CI.
إذا كان التطبيق مسجلاً في خدمة Play App Signing، فإن وحدة تحكم Google Play تكتشف الخطأ لحظياً وترفض رفع الحزمة لعدم تطابق شهادة الرفع، مما يضمن عدم وصول أي ملف خاطئ للمستخدمين. أما في التوزيع المباشر خارج المتجر، فإن نظام أندرويد يرفض تثبيت التحديث حماية لبيانات التطبيق؛ وفي هذه الحالة نوقف مسار التوزيع فوراً ونسحب الحزمة من الخوادم.
وإذا فُقد مفتاح الرفع الأصلي، يقدم مالك الحساب طلباً رسمياً في Google Play لإعادة تعيين مفتاح الرفع عبر إرسال الشهادة العامة بصيغة PEM، وتحدث جوجل المفتاح خلال يومين دون الإضرار بالمفتاح الرئيسي أو بالمستخدمين.
ولمنع تكرار الحادثة، نعزل مفاتيح الإنتاج في Protected Environments تتطلب موافقة يدوية من كبار المهندسين، ونضيف خطوة فحص آلية في الـ CI تستخرج بصمة SHA-256 لشهادة الملف بـ keytool وتقارنها بالبصمة الرسمية المعتمدة وتوقف البناء فوراً عند أي اختلاف.""",
        "deep_answer_ar": """من منظور حوكمة الهوية التشفيرية وإدارة المخاطر في عمليات الإصدار، يمثل توقيع حزمة بمفتاح خاطئ خللاً هيكلياً في بيئة الـ CI يتطلب معالجة حاسمة.
في نظام تشغيل أندرويد، يمثل التوقيع الرقمي هوية التطبيق التي تحمي أذونات التوقيع والبيانات المشتركة؛ ولذلك يرفض مدير الحزم أي تحديث يحمل توقيعاً مغايراً بخطأ INSTALL_FAILED_UPDATE_INCOMPATIBLE لحماية المستخدم من انتحال التطبيقات. وتوفر خدمة Play App Signing حماية ممتازة؛ حيث تفصل مفتاح الرفع الخاص بالمطور عن مفتاح توقيع التطبيق الرئيسي المحفوظ في خوادم جوجل الآمنة، مما يعني أن الخطأ في مفتاح الرفع يمنع قبول النسخة في المتجر فقط دون المساس بالمفتاح الرئيسي.
وإذا تعرض مفتاح الرفع للتلف أو الفقدان، يتبع الفريق بروتوكول Upload Key Reset الرسمي في Play Console؛ حيث يتم توليد Keystore جديد واستخراج شهادته العامة بصيغة PEM وتقديمها للدعم الفني ليتم تفعيلها خلال 24 إلى 48 ساعة دون التأثير على المستخدمين المثبت لديهم التطبيق.
ولتحصين خط الـ CI ومنع تكرار الخطأ نهائياً، نمنع تضمين أي مسارات لمفاتيح تجريبية كبدائل تلقائية في كود Gradle. ونحفظ مفاتيح وكلمات سر الإنتاج في بيئات محمية على GitHub Actions تتطلب موافقة يدوية وتقتصر على الفروع المحمية فقط. كما نلزم الـ Pipeline بتنفيذ فحص تشفيري آلي باستخدام أداة keytool أو apksigner لاستخراج بصمة SHA-256 للملف ومطابقتها بالبصمة الرسمية الصريحة قبل الرفع للمتجر، مما يمنع نشر أي حزمة موقعة بمفتاح خاطئ مهما كانت الأسباب."""
    }
}

# ==========================================
# BLD-20: A feature works on arm64 but fails on another ABI. How do you debug packaging?
# ==========================================
DATA["BLD-20"] = {
    "concept_en": """Diagnosing feature failures on specific CPU ABIs (such as armeabi-v7a or x86_64) while passing on arm64-v8a requires inspecting native packaging and architecture compatibility:
- Primary Root Causes of Single-ABI Failures:
  1. Packaging Asymmetry: An upstream transitive library bundles .so shared objects for arm64-v8a but omits them for 32-bit ARM or x86. Android's dynamic linker loads the 32-bit runtime on 32-bit devices and fails with dlopen failed: library not found.
  2. Android 15 16KB Page Alignment Violations: Android 15 introduces support for 16KB memory page sizes. Native libraries compiled with older NDKs targeting 4KB boundaries fail to load on 16KB-configured devices with memory alignment faults.
  3. CPU Instruction Incompatibilities: Native C/C++ routines invoking architecture-specific vector registers (e.g. ARM NEON SIMD) without runtime CPU capability detection crash with SIGILL (Illegal Instruction) on incompatible hardware or emulators.
  4. C++ Runtime Collisions: Multiple native dependencies bundling mismatched libc++_shared.so versions resolved via pickFirsts, creating memory layout incompatibilities.
- Systematic Packaging Debugging Protocol:
  - Step 1: Inspect native directories inside the APK via unzip -l app.apk "lib/*" or APK Analyzer to verify parity across all ABI subfolders.
  - Step 2: Audit ELF memory page alignment using readelf -l libname.so | grep -A 1 LOAD to verify that Align equals 0x4000 (16KB).
  - Step 3: Run the app on an emulator targeting the failing ABI and capture linker diagnostics via adb logcat | grep -E "linker|DEBUG".
- Remediation: Enforce ndk.abiFilters in build.gradle.kts, update NDK toolchains to r27+, and implement CPU runtime feature probing.""",
    "walkthrough_en": """Native binary inspection commands and Gradle ABI configuration:
```bash
# 1. Audit native library parity across all bundled ABI directories:
unzip -l app/build/outputs/apk/release/app-release.apk "lib/*"

# 2. Check 16KB memory page size alignment for Android 15+ compatibility:
readelf -l app/build/intermediates/merged_native_libs/release/mergeReleaseNativeLibs/out/lib/arm64-v8a/libnative.so | grep -A 1 LOAD
# Verify that Align equals 0x4000 (16KB)

# 3. Capture dynamic linker errors on failing emulator:
adb logcat | grep -E "linker|DEBUG"
```

```kotlin
// 4. Configure ABI filters and CMake compilation in build.gradle.kts:
android {
    defaultConfig {
        ndk {
            abiFilters.addAll(listOf("arm64-v8a", "armeabi-v7a", "x86_64"))
        }
        externalNativeBuild {
            cmake {
                arguments("-DANDROID_STL=c++_shared")
            }
        }
    }
}
```""",
    "short_en": """We debug ABI-specific packaging failures by inspecting the APK lib directory using unzip or APK Analyzer to verify that all architectures contain identical shared native libraries. We inspect dynamic linker errors in Logcat, verify Android 15 16KB page alignment using readelf, audit CPU instruction compatibility, and align ndk.abiFilters in Gradle.""",
    "structured_en": """When an Android feature functions seamlessly on arm64-v8a but fails on other architectures, senior engineers isolate packaging asymmetry and runtime ABI constraints.
First, we audit the compiled binary. Running unzip on the APK or opening it in APK Analyzer reveals the native directory structure under lib. If a transitive dependency bundles native libraries exclusively for arm64-v8a while omitting them for armeabi-v7a or x86_64, the operating system dynamic linker throws an immediate UnsatisfiedLinkError on 32-bit devices because the expected shared library is missing from that ABI slice.
Second, on Android 15 devices supporting 16KB memory pages, we check ELF binary alignment. Executing readelf on native shared objects verifies whether the LOAD segment alignment equals 0x4000. Libraries built with older NDK toolchains aligned to 4KB crash during process loading on 16KB kernels.
Third, we capture logcat output on the failing architecture emulator. If native C++ code executes vector instructions like ARM NEON without runtime CPU feature detection, it triggers SIGILL crashes.
We remediate these issues by updating to modern NDK toolchains, aligning ndk.abiFilters, and compiling native code with 16KB page alignment.""",
    "deep_senior_en": """From a systems programming and multi-architecture runtime perspective, ABI execution divergences arise from packaging disparity, linker constraints, and hardware vector instruction incompatibilities.
In Android's process model, the Zygote selects an application's 32-bit or 64-bit runtime environment based on available native libraries. If an APK contains a primary native library for both arm64-v8a and armeabi-v7a, but a secondary third-party dependency only packages arm64-v8a, the app boots into a 32-bit process on 32-bit devices. When the app attempts to load the secondary library via System.loadLibrary, dlopen fails catastrophically because the 32-bit linker cannot find or load 64-bit binaries.
Another critical issue in modern releases is the Android 15 16KB memory page size mandate. Devices configured with 16KB page sizes reject ELF binaries whose segments are aligned to legacy 4KB boundaries, crashing the process before native code can execute. We verify compliance across all native dependencies by running readelf and asserting an alignment value of 0x4000, updating NDK compilation flags to enforce 16KB alignment.
Additionally, native C++ dependencies often collide on shared runtime libraries like libc++_shared.so. When developers use packaging jniLibs.pickFirsts to resolve duplicate file collisions between libraries compiled against different NDK versions, subtle C++ ABI incompatibilities cause runtime memory corruption and SIGSEGV crashes.
To permanently prevent ABI packaging failures, our continuous integration runs an automated testing matrix executing instrumented tests on both ARM64 and x86_64 emulator system images, ensuring native binaries load cleanly across all targeted architectures before release approval.""",
    "meta_ar": {
        "id": "BLD-20",
        "questionAr": "ميزة تعمل على معمارية arm64 ولكنها تنهار على معمارية أخرى. كيف تستكشف وتصلح أخطاء الحزم (Packaging)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تشخيص عدم تناظر مكتبات الـ Native بين مجلدات الـ ABIs، وفحص محاذاة صفحات الذاكرة 16KB لأندرويد 15 بـ readelf، وتتبع أخطاء الـ Dynamic Linker، وضبط ndk.abiFilters.",
        "concept_ar": "يتطلب تشخيص فشل الميزات على معماريات معينة (مثل armeabi-v7a أو x86_64) بينما تعمل على arm64-v8a فحصاً لمنظومة حزم مكتبات الـ Native وتوافق المعالجات: يحدث الفشل غالباً لثلاثة أسباب: أولاً عدم تناظر الحزم Packaging Asymmetry؛ حيث توفر مكتبة وسيطة ملف .so لمعمارية ARM64 فقط وتهمل 32-bit، فعند تشغيل التطبيق على جهاز 32-bit يفشل الـ Linker برمي UnsatisfiedLinkError لغياب المكتبة. ثانياً محاذاة صفحات الذاكرة 16KB في أندرويد 15؛ حيث تفشل المكتبات المبنية بـ NDK قديم بمحاذاة 4KB في التحميل على هواتف أندرويد 15 الحديثة. وثالثاً استخدام تعليمات معالج غير مدعومة مثل ARM NEON دون فحص دعم المعالج برمجياً مما يسبب انهيار SIGILL. ونشخص ذلك بفحص مجلد lib داخل الـ APK بـ unzip أو APK Analyzer، وفحص الـ ELF بـ readelf للتأكد من محاذاة 0x4000، ومراقبة سجلات logcat.",
        "walkthrough_ar": """فحص تناظر مكتبات الـ Native ومحاذاة صفحات الـ 16KB:
```bash
# 1. فحص تناظر ملفات الـ .so في مجلدات الـ lib لكافة المعماريات:
unzip -l app-release.apk "lib/*"

# 2. فحص محاذاة صفحات الذاكرة (16KB Page Alignment) لأندرويد 15+:
readelf -l app/build/intermediates/merged_native_libs/release/mergeReleaseNativeLibs/out/lib/arm64-v8a/libnative.so | grep -A 1 LOAD
# يجب أن تكون قيمة Align هي 0x4000 (16KB)

# 3. مراقبة سجلات الـ Linker عند تشغيل المحاكي:
adb logcat | grep -E "linker|DEBUG"
```
```kotlin
// 4. ضبط المعماريات المدعومة في build.gradle.kts:
android {
    defaultConfig {
        ndk {
            abiFilters.addAll(listOf("arm64-v8a", "armeabi-v7a", "x86_64"))
        }
    }
}
```""",
        "why_it_matters_ar": "يضمن عمل التطبيق بكفاءة على كافة هواتف أندرويد القديمة والحديثة والمحاكيات دون انهيارات مفاجئة في مكتبات الـ C++.",
        "worked_example_ar": "مكتبة معالجة صور تنهار على أجهزة أندرويد 15 ذات الـ 16KB Pages؛ تم فحصها بـ readelf وتبين أنها 4KB، وتمت إعادة تجميعها بـ NDK الحديث لتتوافق مع 16KB.",
        "trade_offs_ar": "تضمين مكتبات الـ Native لكافة المعماريات يزيد حجم الـ APK، ولذلك يفضل نشر التطبيق بصيغة Android App Bundle (AAB) لتقسيم المعماريات للمستخدمين.",
        "failure_modes_ar": "استخدام jniLibs.pickFirsts لحل تعارض مكتبة libc++_shared.so بين نسختين مختلفتين من NDK، مما يسبب فساد الذاكرة وانهيارات SIGSEGV.",
        "production_perspective_ar": "نلزم خط الـ CI باختبار التطبيق على مصفوفة محاكيات تشمل ARM64 و x86_64، ونفحص محاذاة الـ 16KB آلياً قبل كل إصدار رسمي.",
        "how_to_answer_ar": "استعرض أسباب المشكلة: عدم تناظر ملفات الـ .so، محاذاة 16KB في أندرويد 15، وتعليمات المعالج، ثم اشرح خطوات الفحص بـ unzip و readelf وضبط abiFilters.",
        "talking_points_ar": "تناظر مجلدات lib، محاذاة الـ 16KB بـ readelf، أخطاء UnsatisfiedLinkError، استدعاء تعليمات NEON، وحل تعارضات libc++_shared.",
        "follow_ups_ar": "- **المحاور:** 'ما هي متطلبات محاذاة الـ 16KB Page Size في أندرويد 15 وكيف نفحصها؟'\n  **المرشح:** 'يدعم أندرويد 15 أجهزة تعمل بصفحات ذاكرة 16KB؛ ويجب محاذاة مكتبات الـ ELF على حدود 16KB أي قيمة Align تساوي 0x4000 في أمر readelf، وإلا يرفض النظام تحميلها تماماً.'\n\n- **المحاور:** 'لماذا يفضل استخدام Android App Bundle بدلاً من APK الشامل عند التعامل مع معماريات متعددة؟'\n  **المرشح:** 'لأن الـ AAB يتيح لـ Google Play توليد APK مخصص لكل جهاز يحتوي فقط على مكتبات المعمارية التي يدعمها هاتفه، مما يقلل حجم التنزيل على المستخدم بنسبة كبيرة.'",
        "self_check_ar": "هل بينت أسباب عدم تناظر الـ ABIs ومحاذاة الـ 16KB وأمر readelf وضبط abiFilters؟",
                "references_ar": f"- [Android Developers: Support 16 KB page sizes](https://developer.android.com/guide/practices/page-sizes) — الدليل الرسمي لدعم صفحات الذاكرة 16KB في أندرويد 15.\n- [Android Developers: Configure ABI splits](https://developer.android.com/build/configure-apk-splits#configure-abi-split) — توثيق تقسيم وإعداد معماريات المعالجات في Gradle.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نستكشف أخطاء الحزم بفحص مجلد lib داخل الـ APK بـ unzip أو APK Analyzer للتأكد من وجود نفس مكتبات الـ Native لكافة المعماريات، وتدقيق أخطاء الـ Linker في Logcat، وفحص محاذاة صفحات الذاكرة 16KB لأندرويد 15 باستخدام readelf، وضبط المعماريات المدعومة في ndk.abiFilters.""",
        "best_answer_ar": """عندما تعمل ميزة برمجية على معمارية arm64-v8a وتنهار على غيرها، يعود السبب في الغالب إلى عدم تناظر في حزم مكتبات الـ Native أو عدم توافق تعليمات المعالج.
الخطوة الأولى هي فحص محتويات ملف الـ APK بأمر unzip أو عبر APK Analyzer لمقارنة ملفات الـ .so داخل مجلدات lib لكافة المعماريات؛ فإذا كانت إحدى المكتبات الخارجية قد وفرت كوداً لـ ARM64 فقط وأهملت معمارية 32-bit أو x86، فإن نظام أندرويد يفشل في تحميلها برمي استثناء UnsatisfiedLinkError فور استدعائها.
الخطوة الثانية هي فحص متطلبات أندرويد 15 لمحاذاة صفحات الذاكرة على 16KB؛ حيث نستخدم أمر readelf للتحقق من أن قيمة Align تساوي 0x4000، لأن المكتبات القديمة بمحاذاة 4KB تفشل في التحميل على أجهزة أندرويد 15 الحديثة.
الخطوة الثالثة هي فحص سجلات Logcat لاكتشاف انهيارات SIGILL التي تحدث إذا استخدم كود الـ C++ تعليمات متقدمة مثل ARM NEON دون فحص دعم المعالج لحظياً. ونحل المشكلة بإعادة تجميع الكود عبر NDK الحديث وضبط المعماريات بدقة في ndk.abiFilters.""",
        "deep_answer_ar": """من منظور برمجة النظم وهندسة بيئة التشغيل، ينشأ التباين بين المعماريات من ثلاثة عوامل: تباين حزم الـ Native، قيود محاذاة الذاكرة في نواة النظام، وتعارض بيئات C++ Runtime المشتركة.
عندما تنشئ نواة النظام عملية التطبيق عبر Zygote، تختار العمل بنمط 32-bit أو 64-bit بناءً على المكتبات المتوفرة في الحزمة. فإذا تضمن التطبيق مكتبة مجمعة لـ ARM64 فقط إلى جانب مكتبات أخرى تدعم المعماريتين، يختار النظام نمط 32-bit على الأجهزة القديمة، وعندما يحاول الكود استدعاء المكتبة غير الموجودة يفشل الرابط الديناميكي فوراً.
والتحدي الأحدث في أجهزة أندرويد 15 هو دعم صفحات الذاكرة بحجم 16KB بدلاً من 4KB التقليدية؛ فالمكتبات المجمعة بإصدارات NDK سابقة تنهار فوراً أثناء محاولة النواة تحميل ملف الـ ELF في الذاكرة. ولضمان التوافق، نلزم خطوط البناء بفحص ثنائيات الـ Native باستخدام أمر readelf والتحقق من أن محاذاة شرائح LOAD مضبوطة على 0x4000.
بالإضافة إلى ذلك، نعالج مشكلة تصادم مكتبة التشغيل libc++_shared.so؛ فعندما تجلب عدة مكتبات نسخاً مختلفة من مكتبة C++، يلجأ بعض المطورين لخيار pickFirsts الذي يخفي التعارض ولكنه قد يسبب انهيار SIGSEGV أثناء التشغيل نتيجة لاختلاف تخطيط الذاكرة للـ ABI.
ولمنع هذه الأخطاء جذرياً، نوحد إصدار الـ NDK عبر كافة التبعيات، ونلزم خط الـ CI بتشغيل مصفوفة اختبارات أتمتة على محاكيات ARM64 و x86_64 للتأكد من استقرار الميزات عبر كافة المعماريات قبل اعتماد النسخة للتوزيع."""
    }
}

# ==========================================
# BLD-21: How would you safely roll out and then roll back a bad Android release?
# ==========================================
DATA["BLD-21"] = {
    "concept_en": """Safely releasing and rolling back an Android application requires understanding store distribution mechanics, telemetry guardrails, and OS installation invariants:
- Staged Rollout Strategy:
  1. Phased Distribution Schedule: Never release directly to 100% of users. Follow a controlled progression: 1% (Day 1) -> 5% (Day 2) -> 20% (Day 3) -> 50% (Day 4) -> 100% (Day 5-7).
  2. Health & Telemetry Guardrails: Monitor Android Vitals and Crashlytics in real time. Google Play bad behavior thresholds enforce an overall crash rate below 1.09% and an ANR rate below 0.47%. If crash-free user percentage falls below 99.5%, halt the rollout immediately.
- The Android Downgrade Invariant:
  - Android OS package manager strictly forbids downgrading versionCode (INSTALL_FAILED_VERSION_DOWNGRADE). An app cannot be "rolled back" on client devices by republishing an older build.
- The 3-Tier Production Incident Mitigation Protocol:
  - Tier 1: Halt Rollout. Stop distribution immediately in Google Play Console or Fastlane to protect the remaining 95%+ of un-updated users.
  - Tier 2: Remote Kill Switch. Disable defective features or revert backend endpoints via Firebase Remote Config or LaunchDarkly, neutralizing bugs for users who already installed the update.
  - Tier 3: Emergency Expedited Hotfix (Roll-forward). Revert the bad commit in Git, increment versionCode (e.g. from 201 to 202), rebuild the AAB, and submit with an Expedited Review Request to Google Play.
  - Tier 4: Immediate In-App Update. Enforce AppUpdateType.IMMEDIATE to force users on the broken build to update before launching.""",
    "walkthrough_en": """Incident response CLI workflows and In-App Update enforcement:
```bash
# 1. Halt staged rollout immediately via Fastlane Supply:
bundle exec fastlane supply halt --track production

# 2. Revert the problematic commit in Git:
git revert HEAD --no-edit

# 3. Increment versionCode in build.gradle.kts (e.g., from 101 to 102), then build fresh AAB:
./gradlew :app:bundleRelease

# 4. Release hotfix directly to 100% with expedited review:
bundle exec fastlane supply --aab app/build/outputs/bundle/release/app-release.aab --track production --rollout 1.0
```

```kotlin
// 5. In-App Update enforcement in MainActivity to force immediate hotfix download:
val appUpdateManager = AppUpdateManagerFactory.create(context)
appUpdateManager.appUpdateInfo.addOnSuccessListener { info ->
    if (info.updateAvailability() == UpdateAvailability.UPDATE_AVAILABLE
        && info.isUpdateTypeAllowed(AppUpdateType.IMMEDIATE)
    ) {
        appUpdateManager.startUpdateFlowForResult(info, AppUpdateType.IMMEDIATE, activity, REQUEST_CODE)
    }
}
```""",
    "short_en": """We roll out safely using Google Play Staged Rollouts while monitoring Android Vitals and Crashlytics. Because Android's package manager strictly forbids downgrading versionCode, rollback requires a three-tier response: halting the rollout in Play Console, toggling remote feature flag kill switches, and immediately releasing an expedited hotfix with an incremented versionCode.""",
    "structured_en": """Safely rolling out and rolling back Android applications requires understanding app store release mechanics and the operating system installation invariant.
We mitigate deployment risk by using Google Play staged rollouts, progressing gradually from one percent to five, twenty, fifty, and one hundred percent over several days. Throughout the rollout, we monitor Google Play Android Vitals and Crashlytics telemetry. If the crash rate exceeds one percent or the ANR rate exceeds zero point forty-seven percent, we halt the rollout immediately.
When mitigating a defective release, we cannot execute a traditional server rollback. Android package manager strictly forbids installing an APK with a lower versionCode than what is currently installed, rejecting downgrades to prevent data corruption.
Therefore, incident containment follows a three-tier mitigation protocol. First, we halt the staged rollout in Play Console, containing the blast radius to the small percentage who already updated. Second, we activate remote kill switches via Firebase Remote Config to deactivate the broken feature dynamically. Third, we roll forward by reverting the bad commit in Git, incrementing the versionCode, and publishing an expedited hotfix directly to production.""",
    "deep_senior_en": """From an operational release management and mobile platform engineering perspective, managing production incidents requires pre-engineered deployment governance and telemetry guardrails.
Unlike backend microservices where traffic can be shifted instantly back to a previous container version, Android client binaries are distributed asynchronously across millions of physical devices. The Android OS package manager enforces an immutable security invariant: installing an APK with a lower versionCode fails with INSTALL_FAILED_VERSION_DOWNGRADE. The only way an end-user could downgrade is by completely uninstalling the app, which irrevocably wipes all local SQLite databases and encrypted credentials.
Because client-side downgrade is impossible, safe deployment relies on staged rollouts combined with multi-layer mitigation. We configure our CI/CD pipeline with automated phased rollouts, progressing through 1%, 5%, 20%, 50%, and 100% gates. Between gates, automated health monitors query the Google Play Developer API and Crashlytics APIs to verify that crash-free user sessions remain above ninety-nine point five percent and startup latencies meet performance baselines.
When telemetry detects a catastrophic regression, our incident response protocol activates immediately. Halting the staged rollout stops distribution to the remaining un-updated population. For users who already installed the broken release, we toggle remote feature flags via Firebase Remote Config or LaunchDarkly, instantly neutralizing the offending code path without waiting for app store review.
Simultaneously, the engineering team prepares an emergency roll-forward hotfix. We revert the defective commit in Git, increment the versionCode, build a release AAB, and submit it to Google Play along with an Expedited Review Request to secure approval within hours. When the hotfix lands, we trigger Google Play Immediate In-App Updates, presenting a blocking full-screen modal that forces affected users to install the fix before accessing the app.""",
    "meta_ar": {
        "id": "BLD-21",
        "questionAr": "كيف تطرح تحديثاً جديداً بشكل آمن (Staged Rollout)، وكيف تتراجع عنه (Rollback) عند حدوث كارثة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إدارة الطرح التدريجي عبر Google Play، ومراقبة Android Vitals و Crashlytics، وفهم حظر التراجع (Downgrade) في نظام أندرويد، وتطبيق خطة الاحتواء ثلاثية المستويات ومفاتيح الإلغاء عن بُعد والتحديث الإجباري.",
        "concept_ar": "يتطلب طرح تحديثات أندرويد وسحبها فهماً لآليات التوزيع ومؤشرات الأداء وقيود نظام التشغيل: يُمنع نشر أي إصدار لـ 100% من المستخدمين مباشرة، بل نعتمد الطرح التدريجي (Staged Rollout) بنسب 1% ثم 5% ثم 20% ثم 50% ثم 100% مع مراقبة مؤشرات Android Vitals ومعدل الانهيار في Crashlytics. وإذا ظهرت مشكلة كارثية، فإن نظام تشغيل أندرويد لا يدعم التراجع (Downgrade) إطلاقاً؛ حيث يرفض تثبيت أي إصدار يحمل versionCode أقل من المثبت حالياً لحماية بيانات المستخدم. ولذلك نتبع خطة احتواء ثلاثية: أولاً إيقاف الطرح فوراً في Play Console لحماية باقي المستخدمين. ثانياً تفعيل مفتاح الإلغاء عن بُعد (Remote Kill Switch) عبر Remote Config لتعطيل الميزة التالفة لمن قام بالتحديث. وثالثاً إطلاق تحديث طارئ سريع (Roll-forward Hotfix) برقم versionCode أعلى والتراجع عن الـ Commit المعطوب، وتفعيل التحديث الفوري الإجباري عبر In-App Updates.",
        "walkthrough_ar": """إدارة الطوارئ وإيقاف الطرح ونشر التحديث التصحيحي عبر Fastlane:
```bash
# 1. إيقاف الطرح التدريجي فوراً عبر Fastlane Supply:
bundle exec fastlane supply halt --track production

# 2. التراجع عن الـ Commit المتسبب في الكارثة في Git:
git revert HEAD --no-edit

# 3. زيادة versionCode وبناء Hotfix جديد برقم أعلى:
./gradlew :app:bundleRelease

# 4. نشر الـ Hotfix فوراً بنسبة 100% مع طلب مراجعة مستعجلة:
bundle exec fastlane supply --aab app-release.aab --track production --rollout 1.0
```
```kotlin
// 5. تفعيل التحديث الإجباري الفوري في الكود:
appUpdateManager.startUpdateFlowForResult(appUpdateInfo, AppUpdateType.IMMEDIATE, activity, REQUEST_CODE)
```""",
        "why_it_matters_ar": "يقلل نطاق الضرر عند حدوث أخطاء غير متوقعة، ويحمي سمعة التطبيق وتقييمه في المتجر وبيانات ملايين المستخدمين.",
        "worked_example_ar": "تحديث أحدث انهياراً في شاشة الدفع لـ 2% من المستخدمين؛ تم إيقاف الطرح فوراً وتعطيل بوابة الدفع بـ Remote Config ونشر Hotfix برقم أعلى خلال ساعتين.",
        "trade_offs_ar": "الطرح التدريجي يستغرق عدة أيام للوصول لكافة المستخدمين لكنه يمنع الكوارث العامة، بينما التراجع يتطلب بناء إصدار جديد برقم أعلى لعدم إمكانية الـ Downgrade.",
        "failure_modes_ar": "محاولة رفع نسخة قديمة بنفس الـ versionCode القديم مما يرفضه المتجر والنظام، أو النشر المباشر لـ 100% دون مراقبة Android Vitals.",
        "production_perspective_ar": "نربط خطوط النشر الآلي بـ Fastlane مع تنبيهات لحظية من Crashlytics، ونلزم كافة الميزات الجديدة بمفاتيح Feature Flags قبل إطلاقها.",
        "how_to_answer_ar": "اشرح نسب الطرح التدريجي ومؤشرات المراقبة، ثم بين حقيقة حظر الـ Downgrade في أندرويد، واستعرض خطة الطوارئ: إيقاف الطرح، مفاتيح الإلغاء، ونشر Hotfix جديد.",
        "talking_points_ar": "جدول Staged Rollout، مؤشرات Android Vitals، حظر الـ Downgrade بنظام أندرويد، خطة الطوارئ ثلاثية المستويات، والتحديث الإجباري In-App Updates.",
        "follow_ups_ar": "- **المحاور:** 'لماذا لا يسمح نظام تشغيل أندرويد بتثبيت إصدار قديم يحمل versionCode أقل؟'\n  **المرشح:** 'يرفض مدير حزم أندرويد تثبيت إصدار أقل بخطأ INSTALL_FAILED_VERSION_DOWNGRADE لحماية بيانات المستخدم من التلف؛ لأن قواعد بيانات التطبيق والملفات قد تكون خضعت لترقيات Schema غير متوافقة مع الكود القديم.'\n\n- **المحاور:** 'كيف يساعد Google Play Immediate In-App Update في معالجة النسخ المعطوبة؟'\n  **المرشح:** 'يتيح إظهار شاشة إجبارية تمنع المستخدم من استخدام النسخة المعطوبة وتلزمه بتنزيل الـ Hotfix الجديد فور فتحه للتطبيق دون الحاجة للدخول لصفحة المتجر يدوياً.'",
        "self_check_ar": "هل غطيت جدول الطرح التدريجي وحظر الـ Downgrade وخطة الاحتواء الثلاثية ومفاتيح الـ Feature Flags؟",
                "references_ar": f"- [Google Play: Release app updates with staged rollouts](https://support.google.com/googleplay/android-developer/answer/6346149) — دليل الطرح التدريجي الآمن في Google Play.\n- [Android Developers: In-app updates](https://developer.android.com/guide/playcore/in-app-updates) — التوثيق الرسمي لفرض التحديثات الفورية داخل التطبيق.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نطرح التحديث تدريجياً عبر Staged Rollouts مع مراقبة مؤشرات Android Vitals. ولأن نظام أندرويد يحظر التراجع للوراء بتثبيت versionCode أقل، فإن التراجع يتطلب خطة احتواء ثلاثية: إيقاف الطرح فوراً في Play Console، وتفعيل مفاتيح الإلغاء عن بُعد عبر Remote Config، وإطلاق تحديث طارئ Hotfix برقم versionCode أعلى ونشره فورياً.""",
        "best_answer_ar": """يتطلب الطرح الآمن للتحديثات والتراجع عنها فهماً دقيقاً لآليات المتاجر ولقيود نظام تشغيل أندرويد في تثبيت التطبيقات.
نبدأ بنشر التحديث تدريجياً بنسب تصاعدية تبدأ من واحد بالمائة ثم خمسة وعشرين وخمسين وصولاً إلى مئة بالمائة عبر عدة أيام، مع المراقبة اللحظية لمؤشرات Android Vitals ونسبة الجلسات الخالية من الانهيارات في Crashlytics؛ فإذا تجاوز معدل الانهيارات واحد بالمائة، نوقف الطرح فوراً.
وعند حدوث خطأ كارثي، لا يمكننا تطبيق التراجع التقليدي؛ لأن مدير حزم أندرويد يمنع تثبيت أي حزمة تحمل versionCode أقل لحماية بيانات المستخدم من التلف.
لذا، نطبق خطة احتواء ثلاثية المستويات: أولاً، إيقاف الطرح في Google Play لحصر المشكلة في النسبة القليلة التي استلمت التحديث. ثانياً، تفعيل مفاتيح الإلغاء عن بُعد عبر Firebase Remote Config لتعطيل الميزة المعطوبة فورياً لدى المستخدمين المتضررين. ثالثاً، التراجع عن الـ Commit في Git وزيادة رقم الـ versionCode وبناء Hotfix جديد ورفعه مباشرة مع طلب فحص مستعجل وتفعيل التحديث الإجباري In-App Updates.""",
        "deep_answer_ar": """من منظور قيادة العمليات وإدارة منصات الموبايل، يختلف التعامل مع طوارئ تطبيقات الهواتف جذرياً عن الأنظمة الخلفية؛ حيث لا يمكن تحويل حركة المرور بنقرة زر إلى إصدار قديم، لأن التطبيق موزع كملف ثنائي على هواتف المستخدمين.
يفرض نظام أندرويد قيداً أمنياً صارماً يمنع خفض رقم الـ versionCode بخطأ INSTALL_FAILED_VERSION_DOWNGRADE؛ لأن جداول قاعدة بيانات SQLite وملفات التفضيلات تخضع لترقيات هيكلية يستحيل قراءتها بالإصدار الأقدم، والطريقة الوحيدة لتثبيت إصدار سابق هي حذف التطبيق بالكامل مما يمسح كافة بيانات المستخدم الحساسة.
ولهذا، يعتمد الأمان التشغيلي على مسارين متكاملين: المسار الأول هو الطرح التدريجي المنضبط بنسب تبدأ من 1% ثم 5% ثم 20% ثم 100%؛ حيث نربط خطوط النشر بإنذارات آلية تقيس مؤشرات الأداء الحيوية في Google Play وCrashlytics للتأكد من بقاء نسبة الجلسات السليمة أعلى من 99.5% وتوقف الطرح آلياً عند أي تدهور.
المسار الثاني هو خطة الطوارئ ثلاثية الأبعاد؛ فبمجرد رصد الانهيار، نوقف الطرح فوراً في Play Console لمنع وصول النسخة المعطوبة لباقي المستخدمين. وبالنسبة للمستخدمين الذين قاموا بالتحديث، نستخدم مفاتيح Feature Flags عبر Firebase Remote Config أو LaunchDarkly لإيقاف الميزة التالفة من السيرفر دون انتظار مراجعة المتجر.
وبالتوازي مع ذلك، ينفذ الفريق الهندسي تحديثاً تصحيحياً سريعاً Roll-forward؛ حيث نتراجع عن الـ Commit في Git، ونرفع رقم الـ versionCode برقم أعلى، ونرفع الحزمة لـ Google Play مع تقديم طلب مراجعة مستعجلة يتم قبوله خلال ساعات. وعند اعتماد التحديث، نفعل آلية التحديث الفوري المباشر Immediate In-App Updates لإجبار المستخدمين المتضررين على تحديث النسخة فور فتح التطبيق لضمان استقرار الخدمة وسلامة البيانات."""
    }
}

# ==========================================
# Runner & Word Count Validation
# ==========================================
import re

def validate_words():
    for qid, d in sorted(DATA.items()):
        short_w = len(d["short_en"].split())
        struct_w = len(d["structured_en"].split())
        deep_w = len(d["deep_senior_en"].split())

        meta = d["meta_ar"]
        quick_ar_w = len(meta["quick_answer_ar"].split())
        best_ar_w = len(meta["best_answer_ar"].split())
        deep_ar_w = len(meta["deep_answer_ar"].split())

        print(f"[{qid}] Words -> EN: short={short_w}, struct={struct_w}, deep={deep_w} | AR: quick={quick_ar_w}, best={best_ar_w}, deep={deep_ar_w}")

        assert 35 <= short_w <= 110, f"{qid}: short_en word count {short_w} out of range [35, 110]"
        assert 100 <= struct_w <= 280, f"{qid}: structured_en word count {struct_w} out of range [100, 280]"
        assert 200 <= deep_w <= 650, f"{qid}: deep_senior_en word count {deep_w} out of range [200, 650]"

        assert 35 <= quick_ar_w <= 110, f"{qid}: quick_answer_ar word count {quick_ar_w} out of range [35, 110]"
        assert 90 <= best_ar_w <= 280, f"{qid}: best_answer_ar word count {best_ar_w} out of range [90, 280]"
        assert 180 <= deep_ar_w <= 650, f"{qid}: deep_answer_ar word count {deep_ar_w} out of range [180, 650]"

        for name, text in [
            ("short_en", d["short_en"]),
            ("structured_en", d["structured_en"]),
            ("deep_senior_en", d["deep_senior_en"]),
            ("quick_answer_ar", meta["quick_answer_ar"]),
            ("best_answer_ar", meta["best_answer_ar"]),
            ("deep_answer_ar", meta["deep_answer_ar"]),
        ]:
            assert not re.search(r"^\s*[-*•]\s*", text, re.M), f"{qid}: {name} contains bullets"
            assert not re.search(r"^\s*\d+[\.\)]\s*", text, re.M), f"{qid}: {name} contains numbered list"

        assert "First," not in d["structured_en"] or "Next," not in d["structured_en"], f"{qid}: structured_en has formulaic enumeration"
        assert "على الجانب الآخر، فيما يخص" not in meta["best_answer_ar"], f"{qid}: best_answer_ar contains cliché"
        assert "على الجانب الآخر، فيما يخص" not in meta["deep_answer_ar"], f"{qid}: deep_answer_ar contains cliché"

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

    ee.save_topic_metadata("bld_15_21", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\nAll {len(DATA)} BLD questions (BLD-15 to BLD-21) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
