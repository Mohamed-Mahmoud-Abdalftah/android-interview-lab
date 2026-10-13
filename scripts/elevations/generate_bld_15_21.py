#!/usr/bin/env python3
"""Generator for BLD-15 through BLD-21 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "bld.json"

BLD_15_21 = [
    {
        "id": "BLD-15",
        "arabic_explanation": (
            "كيف تحقق في تعارض إصدارات التبعيات (Dependency Version Conflicts) وانحدار سرعة البناء (Build-Speed Regressions)؟\n\n"
            "1. التحقيق في تعارض التبعيات (Dependency Conflicts):\n   - **كيف يحل Gradle التعارض افتراضياً؟**: إذا طلبت مكتبة A إصدار `okhttp:4.9.0` وطلبت مكتبة B إصدار `okhttp:4.12.0`، يقوم Gradle باختيار **أحدث إصدار تلقائياً (Latest Version Wins)**. هذا قد يسبب مشاكل توافق إذا كان الإصدار الأحدث يحتوي على Breaking Changes!\n   - **أدوات التشخيص الرسمية**:\n     * `./gradlew :app:dependencies`: يطبع شجرة التبعيات بالكامل مع توضيح الترقيات التلقائية (`-> 4.12.0`).\n     * `./gradlew :app:dependencyInsight --dependency okhttp --configuration releaseRuntimeClasspath`: يشرح بالضبط أي مكتبات طلبت OkHttp ولماذا اختار Gradle هذا الإصدار تحديداً.\n   - **الحل الهندسي**: تثبيت الإصدارات عبر **Gradle Version Catalogs (`libs.versions.toml`)** أو استخدام `strictly` / `force` في `resolutionStrategy`.\n\n"
            "2. التحقيق في انحدار سرعة البناء (Build-Speed Regressions):\n   - **Gradle Build Scan (`./gradlew assembleDebug --scan`)**: الأداة الأقوى عالمياً؛ تحلل زمن كل Task، والـ Cache Misses، وزمن الـ Annotation Processing، والـ Garbage Collection pauses.\n   - فحص الـ Non-Cacheable Tasks ومقارنة الـ Build Scans الحالية بسجلات سابقة لاكتشاف الـ Commit المتسبب في التراجع."
        ),
        "practical_walkthrough": (
            "أوامر تشخيص التبعيات وفرض الإصدارات الصريحة في build.gradle.kts:\n"
            "```bash\n"
            "# 1. معرفة سبب اختيار إصدار معين والمسار الدقيق في شجرة التبعيات:\n"
            "./gradlew :app:dependencyInsight --dependency okhttp --configuration releaseRuntimeClasspath\n"
            "\n"
            "# 2. إنشاء تقرير Build Scan كامل لتحليل أسباب بطء البناء:\n"
            "./gradlew :app:assembleRelease --scan\n"
            "```\n\n"
            "```kotlin\n"
            "// 3. فرض إصدار معين وحظر الترقية التلقائية في build.gradle.kts:\n"
            "configurations.all {\n"
            "    resolutionStrategy {\n"
            "        // إجبار المشروع بالكامل ومكتباته على استخدام إصدار موحد ومفحوص:\n"
            "        force(\"com.squareup.okhttp3:okhttp:4.12.0\")\n"
            "        \n"
            "        // أو إفشال الـ Build فوراً عند حدوث أي تعارض لإجبار المطورين على حله:\n"
            "        failOnVersionConflict()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Investigate dependency conflicts using Gradle's dependencyInsight task to trace conflict graphs, enforcing unified versions via Version Catalogs or resolutionStrategy.force(). Investigate build speed regressions using Gradle Build Scans (--scan) to identify slow tasks, cache misses, and annotation processing bottlenecks.",
        "best_answer": (
            "Diagnosing dependency friction and build performance regressions requires targeted Gradle diagnostic tooling:\n\n"
            "1. **Dependency Conflict Investigation**:\n"
            "   - By default, Gradle's conflict resolution selects the highest requested version (`latest version wins`). This can introduce silent binary incompatibilities if a transitive upgrade introduces breaking API changes.\n   - Run `./gradlew :app:dependencyInsight --dependency <name> --configuration <classpath>`. Gradle prints the exact dependency graph path and selection rationale explaining why a specific version was resolved.\n   - Enforce consistency across the codebase using Gradle Version Catalogs (`libs.versions.toml`) and `resolutionStrategy.force()`, or enable `failOnVersionConflict()` in CI to catch divergent transitive dependencies early.\n\n"
            "2. **Build-Speed Regression Profiling**:\n"
            "   - Generate a **Gradle Build Scan** using `./gradlew assembleDebug --scan`.\n   - Inspect the Timeline view to identify non-parallel task bottlenecks, measure KAPT/KSP annotation processing durations, identify tasks failing incremental execution, and pinpoint cache misses across remote and local build caches."
        ),
        "deep_answer": (
            "From a staff platform architecture viewpoint, maintaining dependency and build velocity requires continuous guardrails:\n\n"
            "1. **Rich Version Constraints (Strict vs. Require)**: Modern Gradle supports rich versioning. Specifying `strictly(\"1.5.0\")` prevents any transitive dependency from bumping the version, causing a build failure if incompatible constraints are encountered.\n\n"
            "2. **Task Cache Miss Forensics**: When a task fails to pull from the build cache, inspect Gradle's cache key inputs with `--info` or Build Scans. The most frequent culprit is non-hermetic tasks with volatile inputs, such as un-annotated directory inputs or hardcoded machine-specific absolute file paths in compiler arguments.\n\n"
            "3. **Dependency Analysis Plugins**: Integrate AutonomousApps' `dependency-analysis-android-plugin` in CI. It automatically identifies unused direct dependencies, transitively used dependencies that should be declared directly, and dependencies leaking across `api` rather than `implementation` boundaries."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between implementation and api scope regarding dependency resolution?",
                "answer": "implementation hides the dependency from downstream consumers, preventing compilation leakage and rebuild cascading; api exposes the dependency transitively to all consumers."
            },
            {
                "question": "What does failOnVersionConflict() do?",
                "answer": "It instructs Gradle to abort the build immediately whenever two dependencies request different versions of the same library, requiring explicit resolution."
            }
        ]
    },
    {
        "id": "BLD-16",
        "arabic_explanation": (
            "كيف تقوم بإعداد البناء القابل للتكرار حتمياً (Reproducible Builds) والتحقق من التبعيات (Dependency Verification) لحماية سلسلة التوريد (Supply Chain)؟\n\n"
            "1. مخاطر هجمات سلسلة التوريد البرمجية (Software Supply Chain Attacks):\n   - يعتمد تطبيق أندرويد على مئات المكتبات الخارجية من خوادم Maven (Google Maven, Maven Central).\n   - إذا تم اختراق حساب أحد المطورين أو استبدال ملف JAR خبيث بنفس الاسم ورقم الإصدار على خادم وسيط (Dependency Confusion / Compromised Mirror)، سيقوم Gradle بتنزيله وتضمينه في تطبيقك دون أن تدري!\n\n"
            "2. التحقق من التبعيات في Gradle (Dependency Verification):\n   - ميزة رسمية مدمجة في Gradle تقوم بالتحقق من **البصمة التشفيرية (SHA-256 Checksum)** أو **التوقيع الرقمي (PGP Signature)** لكل ملف JAR و AAR و Gradle Plugin يتم تنزيله.\n   - يُحفظ سجل البصمات في ملف `gradle/verification-metadata.xml` داخل الـ Git. إذا قام أي شخص بتعديل بايت واحد في مكتبة منشورة، يفشل البناء فوراً برمي خطأ أمني!\n\n"
            "3. البناء القابل للتكرار حتمياً (Reproducible Builds):\n   - يعني أن تجميع الكود من نفس الـ Commit على أي جهاز كمبيوتر أو خادم CI في أي وقت يخرج **نفس ملف الـ APK بنفس البصمة التشفيرية بايت-بايت** (Byte-for-Byte Bitwise Identical).\n   - يتطلب: تثبيت إصدار JDK عبر `jvmToolchain`، توحيد ترتيب الملفات داخل الـ ZIP (`reproducibleFileOrder = true`)، وتجريد التواريخ الزمنية المتغيرة (`preserveFileTimestamps = false`)."
        ),
        "practical_walkthrough": (
            "توليد ملف التحقق من التبعيات وإعداد البناء الحتمي في Gradle:\n"
            "```bash\n"
            "# 1. توليد ملف verification-metadata.xml آلياً لجميع التبعيات الحالية عبر Gradle CLI:\n"
            "./gradlew --write-verification-metadata sha256 help\n"
            "\n"
            "# يتم إنشاء ملف gradle/verification-metadata.xml ويتم إضافته إلى مستودع الـ Git\n"
            "```\n\n"
            "```kotlin\n"
            "// 2. إعداد مهام الحزم لتكون حتمية وقابلة للتكرار في build.gradle.kts:\n"
            "tasks.withType<Zip>().configureEach {\n"
            "    isReproducibleFileOrder = true       // ضمان ترتيب الملفات بشكل أبجدي موحد\n"
            "    isPreserveFileTimestamps = false     // تجريد التواريخ الزمنية لتجنب اختلاف الـ Hashes\n"
            "}\n"
            "\n"
            "kotlin {\n"
            "    jvmToolchain(17) // ضمان استخدام نفس إصدار الـ JDK بالضبط على جميع الأجهزة والـ CI\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Set up reproducible builds and supply-chain security by enabling Gradle's dependency verification via gradle/verification-metadata.xml to enforce SHA-256 and PGP checksums on all external artifacts, standardizing JDK toolchains via jvmToolchain, and enforcing reproducible ZIP file ordering without volatile timestamps.",
        "best_answer": (
            "Software supply chain integrity and reproducible builds guarantee artifact immutability and provenance:\n\n"
            "1. **Gradle Dependency Verification**:\n"
            "   - Protects against compromised Maven repositories, man-in-the-middle attacks, and malicious dependency substitutions. Gradle validates the cryptographic SHA-256 checksum or PGP signature of every downloaded JAR, AAR, and Gradle plugin.\n   - Generate the initial lockfile via `./gradlew --write-verification-metadata sha256 help`. Commit `gradle/verification-metadata.xml` to Git. If an upstream artifact is altered or replaced on Maven Central, Gradle aborts the build with a verification failure.\n\n"
            "2. **Reproducible Builds (Byte-for-Byte Parity)**:\n"
            "   - Guarantees that compiling identical source code on different machines produces bitwise-identical binary artifacts.\n   - Eliminate non-deterministic inputs: enforce identical compiler toolchains using Gradle's `jvmToolchain(17)`.\n   - Configure ZIP archive tasks with `isReproducibleFileOrder = true` and `isPreserveFileTimestamps = false` to eliminate file-system order variances and timestamps from APK ZIP headers."
        ),
        "deep_answer": (
            "From an enterprise security and compliance perspective, reproducible builds enable external independent auditing:\n\n"
            "1. **Third-Party Verifiable Provenance**: Open-source and high-assurance financial applications (e.g., Signal, Tor, Bitcoin wallets) use reproducible builds so independent security researchers can compile the public Git commit and verify that the resulting SHA-256 matches the binary distributed on Google Play, proving the release contains zero backdoors.\n\n"
            "2. **Dynamic Dependency Ban**: Enforce strict repository boundaries. Ban dynamic version ranges (e.g. `implementation(\"com.lib:sdk:1.+\")`) and SNAPSHOT dependencies in release configurations, as they pull untracked binary changes without code modifications.\n\n"
            "3. **Repository Priority Hardening**: Explicitly order repositories in `settings.gradle.kts`: Google Maven first, followed by Maven Central. Use `content { includeGroup(...) }` filtering to restrict specific libraries to designated repositories, thwarting **Dependency Confusion** attacks."
        ),
        "follow_ups": [
            {
                "question": "What is a Dependency Confusion attack?",
                "answer": "An attack where an adversary publishes a public package on Maven Central with the same name as an internal private library, tricking the build into pulling the malicious public artifact."
            },
            {
                "question": "Why do timestamps in ZIP archives prevent reproducible builds?",
                "answer": "Because ZIP headers store the creation timestamp for every file; compiling at different times changes binary headers, resulting in completely different SHA-256 hashes."
            }
        ]
    },
    {
        "id": "BLD-17",
        "arabic_explanation": (
            "تطبيق يُثبت ويعمل بشكل مثالي في بيئة الـ Debug، ولكنه ينهار فور الفتح (Crash on Launch) في بيئة الـ Release بسبب أسماء كلاسات تم تشويشها. كيف تثبت السبب الجذري برهانياً وتصلحه؟\n\n"
            "1. إثبات السبب الجذري برهانياً (Step-by-Step Proof):\n   - **الخطوة 1: استخراج الـ Crash Stack Trace الأصلي**: تشغيل الـ Release APK عبر ADB وقراءة الخطأ المشوش في Logcat:\n     `java.lang.ClassNotFoundException: a.b.c`.\n   - **الخطوة 2: فك التشفير عبر `retrace`**: تمرير الـ Stack Trace لـ `retrace mapping.txt` لاكتشاف اسم الكلاس الأصلي (مثلاً `com.example.ui.MainActivity` أو كلاس Fragment).\n   - **الخطوة 3: البرهان في `usage.txt`**: فتح ملف `usage.txt`؛ إذا كان اسم الكلاس موجوداً فيه، فهذا إثبات قطعي بأن R8 اعتبره كوداً ميتاً وحذفه.\n   - **الخطوة 4: فحص ملف الـ AndroidManifest المدمج**: فتح الـ APK في APK Analyzer وفحص `AndroidManifest.xml`. إذا كان الـ Manifest يشير إلى `com.example.ui.MainActivity` بينما R8 شوش اسم الكلاس إلى `a.b.c`، فهذا يثبت سبب الانهيار فور الفتح.\n\n"
            "2. الحل الجذري:\n   - إضافة قاعدة Keep Rule صريحة أو استخدام تعليق `@Keep` على الكلاس المستهدف."
        ),
        "practical_walkthrough": (
            "خطوات التحقيق العملي في انهيار تشويش الكلاسات وحله بقاعدة Keep Rule دقيقة:\n"
            "```bash\n"
            "# 1. التقاط الـ Crash المشوش من الهاتف:\n"
            "adb logcat -d *:E | grep -E \"FATAL EXCEPTION|ClassNotFoundException\"\n"
            "# المخرجات: Caused by: java.lang.ClassNotFoundException: Didn't find class \"com.example.auth.AuthRouter\"\n"
            "\n"
            "# 2. التحقق من ملف usage.txt لإثبات أن R8 حذفه أو شوش اسمه:\n"
            "grep \"com.example.auth.AuthRouter\" app/build/outputs/mapping/release/usage.txt\n"
            "```\n\n"
            "```kotlin\n"
            "// 3. الحل في كود Kotlin بإضافة تعليق @Keep الصريح:\n"
            "@Keep // يمنع R8 من حذف الكلاس أو تغيير اسمه نهائياً\n"
            "class AuthRouterImpl : AuthRouter {\n"
            "    // Implementation\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Prove the cause by retrieving the crash from Logcat, retracing it with mapping.txt to identify the original class, confirming its deletion in usage.txt, and inspecting the merged manifest or reflection call site in APK Analyzer. Remediate by applying a targeted @Keep annotation or surgical ProGuard rule.",
        "best_answer": (
            "Proving and remediating an immediate startup crash caused by obfuscated or stripped classes follows a forensic debugging pipeline:\n\n"
            "1. **Capture & Retrace the Exception**:\n"
            "   - Extract the startup crash log via `adb logcat -d *:E`. Run the trace through `retrace mapping.txt`. The deobfuscated trace pinpoints the exact class (e.g. `ClassNotFoundException: Didn't find class com.example.analytics.AppInitializer`).\n\n"
            "2. **Definitive Proof via R8 Diagnostic Reports**:\n"
            "   - Search for the class inside `app/build/outputs/mapping/release/usage.txt`. If present, R8 explicitly determined it was unreferenced dead code and pruned it from `classes.dex`.\n   - If the class exists in `classes.dex` under an obfuscated name (`a.b.c`), but dynamic instantiation points (e.g., `Class.forName(\"com.example.analytics.AppInitializer\")` or an unmerged manifest entry) look for the original string name, the failure is proven.\n\n"
            "3. **Surgical Remediation**:\n"
            "   - Decorate the class with `@androidx.annotation.Keep` or add a surgical rule in `proguard-rules.pro`: `-keep class com.example.analytics.AppInitializer { <init>(); }`.\n   - Rebuild and verify that the class now appears in `seeds.txt` and the app boots cleanly."
        ),
        "deep_answer": (
            "From an architectural systems perspective, startup obfuscation crashes frequently result from Manifest Merging and DI service loading:\n\n"
            "1. **ServiceLoader & Provider Reflection**: Libraries using Java `ServiceLoader` (e.g. Kotlin Coroutines `AndroidDispatcherFactory`, OkHttp platform engines) rely on metadata files inside `META-INF/services/`. If R8 obfuscates the implementing class without rewriting the service provider configuration file, `ServiceLoader` throws runtime initialization exceptions on startup. Configure R8 with `-keepnames` for service provider classes.\n\n"
            "2. **Manifest Class Reference Obfuscation**: AGP automatically preserves any Activity or Service declared in the application's merged manifest. However, if an activity is declared in an external library manifest that was modified dynamically via manifest placeholders or instantiated via custom classloaders, AGP may miss the reference. Always verify the merged manifest inside `intermediates/merged_manifests/release/`.\n\n"
            "3. **Automated Release Smoke Testing in CI**: Before deploying, CI release pipelines must execute an automated monkey test or startup smoke test (`adb shell monkey -p <pkg> 500`) against the signed release APK on an emulator to assert that startup initialization succeeds."
        ),
        "follow_ups": [
            {
                "question": "Why does AGP automatically keep Activities declared in AndroidManifest.xml?",
                "answer": "AGP automatically generates ProGuard keep rules for all component classes referenced in the merged AndroidManifest.xml as compilation entry points."
            },
            {
                "question": "What is the difference between ClassNotFoundException and NoClassDefFoundError?",
                "answer": "ClassNotFoundException occurs when dynamic loading (Class.forName) fails to find the class; NoClassDefFoundError occurs when a class was present at compile time but missing from the runtime classpath."
            }
        ]
    },
    {
        "id": "BLD-18",
        "arabic_explanation": (
            "أثناء دمج ملفات الـ Manifest في نسخة الـ Release، تم إسقاط (Drop) عنوان ContentProvider مطلوب. ما هو الفحص الآلي (CI Check) الذي يكشف هذه الكارثة قبل النشر؟\n\n"
            "1. كيف تسقط عناصر الـ Manifest أثناء الـ Merge؟\n   - في أندرويد، يتم دمج ملفات الـ `AndroidManifest.xml` الواردة من كل الموديولات والمكتبات الخارجية مع الـ Manifest الرئيسي.\n   - إذا استخدمت مكتبة خارجية أو Flavor قاعدة `tools:node=\"remove\"` أو حدث تعارض في `tools:replace=\"android:authorities\"`، قد يقوم الـ Manifest Merger بحذف الـ ContentProvider بالكامل من الـ APK النهائي دون إظهار أي خطأ أثناء الترجمة!\n   - النتيجة: عند تشغيل التطبيق أو استدعائه، ينهار برمي استثناء فادح أو يفشل تكامل الـ SDK.\n\n"
            "2. الفحوصات الآلية في الـ CI/CD لكشف المشكلة:\n   - **1. فحص تقرير دمج الـ Manifest (Manifest Merger Report)**: ملف `app/build/outputs/logs/manifest-merger-release-report.txt` يحتوي على سجل تفصيلي لكل عنصر تمت إضافته أو حذفه.\n   - **2. اختبار فحص آلي في الـ CI (Automated Manifest Assertion Test)**: كتابة سكريبت بايثون أو اختبار Unit Test في الـ CI يقوم بقراءة ملف الـ Manifest المدمج النهائي والتحقق من وجود الـ `<provider>` والـ `authorities` المطلوبة صراحة."
        ),
        "practical_walkthrough": (
            "تنفيذ فحص آلي في CI/CD للتحقق من وجود الـ ContentProvider في ملف الـ Manifest المدمج النهائي:\n"
            "```kotlin\n"
            "// اختبار Unit Test يعمل في CI للتحقق من سلامة الـ Merged Manifest:\n"
            "class ManifestIntegrityTest {\n"
            "    @Test\n"
            "    fun verifyRequiredContentProvidersAreNotDropped() {\n"
            "        val mergedManifestFile = File(\"build/intermediates/merged_manifests/release/AndroidManifest.xml\")\n"
            "        assertTrue(\"Merged manifest must exist\", mergedManifestFile.exists())\n"
            "\n"
            "        val manifestContent = mergedManifestFile.readText()\n"
            "        val expectedAuthority = \"com.example.app.secureprovider\"\n"
            "\n"
            "        assertTrue(\n"
            "            \"Critical Error: Authority '$expectedAuthority' was dropped during manifest merge!\",\n"
            "            manifestContent.contains(\"android:authorities=\\\"$expectedAuthority\\\"\")\n"
            "        )\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Catch dropped manifest components by inspecting the manifest-merger-release-report.txt log and running an automated CI assertion script or test that parses the final merged AndroidManifest.xml to verify the presence of mandatory provider authorities.",
        "best_answer": (
            "Manifest merging conflicts can silently strip essential components via conflicting `tools:node` attributes or namespace collisions:\n\n"
            "1. **Root Causes of Manifest Drops**:\n"
            "   - Upstream libraries declaring `tools:node=\"remove\"` targeting shared component names.\n   - Conflicting `android:authorities` attributes across product flavors or merged dependencies resolved incorrectly via `tools:replace`.\n\n"
            "2. **The Manifest Merger Report**:\n"
            "   - AGP generates a detailed audit log: `app/build/outputs/logs/manifest-merger-release-report.txt`. It documents the line-by-line origin, merge decision, and justification for every element included or rejected.\n\n"
            "3. **Automated CI Validation Checks**:\n"
            "   - Implement a post-build CI test or custom Gradle task hooked after `processReleaseManifest`. The task parses `build/intermediates/merged_manifests/release/AndroidManifest.xml` using an XML parser and asserts that all critical `<provider>`, `<service>`, and `<activity>` authorities and exported attributes match expected security baselines, failing the build on discrepancies."
        ),
        "deep_answer": (
            "From an enterprise release governance viewpoint, manifest integrity auditing extends beyond simple text matching:\n\n"
            "1. **Custom Android Lint Rules (`Detector.XmlScanner`)**: Write an in-house Android Lint rule that runs during `./gradlew lintRelease`. The detector scans the merged XML AST for expected component authorities and flags errors if authorities do not match the expected variant namespace pattern.\n\n"
            "2. **AAPT2 Dump Manifest Verification**: To guarantee that what is packaged inside the binary matches expectations, run `aapt2 dump badging app-release.apk` inside the release CI runner. Inspect the output to verify declared providers in the final compiled `.arsc` table.\n\n"
            "3. **Security Implications of Dropped Providers**: If an initialization provider (such as AndroidX App Startup `androidx.startup.InitializationProvider`) is dropped, dependent security or tracing SDKs fail to initialize silently, leaving the application running in an uninitialized, insecure state."
        ),
        "follow_ups": [
            {
                "question": "What does tools:node=\"remove\" do in AndroidManifest.xml?",
                "answer": "It instructs the manifest merger to completely remove the specified element from the final merged manifest, ignoring declarations from lower-priority manifests."
            },
            {
                "question": "Where is the merged AndroidManifest.xml file located in AGP builds?",
                "answer": "Inside app/build/intermediates/merged_manifests/<variant>/AndroidManifest.xml."
            }
        ]
    },
    {
        "id": "BLD-19",
        "arabic_explanation": (
            "تم توقيع ملف الـ Release Bundle بمفتاح خاطئ (Wrong Signing Key). كيف تحتوي المشكلة وتصحح الـ Pipeline فورياً؟\n\n"
            "1. تقييم الموقف وتحديد نطاق الضرر (Blast Radius Assessment):\n   - **الحالة أ: تم التوقيع ولكن لم يتم الرفع إلى Google Play بعد**: لا يوجد ضرر! يتم إلغاء الـ Artifact فوراً، وإصلاح مسارات المفاتيح في CI، وإعادة البناء.\n   - **الحالة ب: تم الرفع إلى Google Play Console بمفتاح Upload Key خاطئ**: سيرفض Google Play Console الـ AAB فوراً برمي خطأ `The upload key does not match the app's upload certificate`، ولن يصل الملف لأي مستخدم.\n   - **الحالة ج: تم توقيع وتوزيع APK مباشر (Enterprise MDM أو Direct Download)**: المستخدمون الحاليون لن يتمكنوا من تثبيت التحديث وستظهر رسالة `App not installed: Update incompatible`.\n\n"
            "2. إجراءات الاحتواء والتصحيح الفورية (Containment & Recovery):\n   - إيقاف الـ Pipeline فوراً وسحب الـ Artifact من خوادم التوزيع.\n   - إذا فُقد الـ Upload Key الأصلي تماماً، يقوم مالك الحساب (Account Owner) بتقديم طلب رسمي عبر Google Play Console لإعادة تعيين الـ Upload Key.\n\n"
            "3. تحصين مسار الـ CI/CD لمنع تكرار الخطأ:\n   - استخدام **Protected Environments في GitHub Actions** تتطلب موافقة يدوية (Manual Approval) للوصول لمفاتيح الإنتاج.\n   - إضافة خطوة فحص آلية في CI تقرأ الـ SHA-256 الخاص بالـ Keystore وتقارنه بالبصمة الرسمية قبل بدء التوقيع."
        ),
        "practical_walkthrough": (
            "فحص بصمة مفتاح التوقيع في CI قبل رفع الـ Artifact ومنع استخدام المفاتيح الخاطئة:\n"
            "```bash\n"
            "# 1. فحص بصمة الـ SHA-256 للملف الموقع للتحقق من هويته قبل رفعه إلى المتجر:\n"
            "keytool -printcert -jarfile app/build/outputs/bundle/release/app-release.aab | grep \"SHA256:\"\n"
            "\n"
            "# 2. التحقق برمجياً في الـ CI Script ومقارنة البصمة بالبصمة الرسمية المعتمدة:\n"
            "EXPECTED_SHA256=\"A1:B2:C3:D4:E5:F6:...\"\n"
            "ACTUAL_SHA256=$(keytool -printcert -jarfile app-release.aab | awk '/SHA256:/ {print $2}')\n"
            "\n"
            "if [ \"$ACTUAL_SHA256\" != \"$EXPECTED_SHA256\" ]; then\n"
            "    echo \"CRITICAL ERROR: Signing key mismatch! Build was signed with untrusted key.\"\n"
            "    exit 1\n"
            "fi\n"
            "```"
        ),
        "quick_answer": "If uploaded to Google Play, the console automatically rejects bundles signed with the wrong upload key. For external MDM distribution, halt deployments immediately. Correct the pipeline by adding a CI verification step that asserts the artifact's SHA-256 certificate fingerprint matches the authorized production key before publishing.",
        "best_answer": (
            "Containing and rectifying an artifact signed with the incorrect cryptographic key depends on the distribution channel:\n\n"
            "1. **Google Play Containment (Safe by Default)**:\n"
            "   - If enrolled in Play App Signing, Google Play Console enforces certificate verification on upload. Uploading an AAB signed with an unrecognized key fails with an immediate rejection error (`The upload key does not match`). Zero production users are impacted.\n\n"
            "2. **Alternative Distribution / Direct APK Blast Radius**:\n"
            "   - For enterprise MDM or direct APK distribution, devices reject the update with `INSTALL_FAILED_UPDATE_INCOMPATIBLE`. Users cannot be compromised, but the update channel is blocked.\n   - Immediately halt the rollout track and purge the invalid artifact from distribution CDNs.\n\n"
            "3. **Pipeline Remediation & Hardening**:\n"
            "   - Audit CI secret variables. Ensure the release workflow extracts signing credentials exclusively from a **Protected GitHub Environment** restricted to protected release branches and tags.\n   - Add an automated pre-publish CI assertion task: execute `keytool -printcert -jarfile <artifact>` and assert that the certificate's SHA-256 fingerprint matches the pinned production upload certificate, aborting the job on any divergence."
        ),
        "deep_answer": (
            "From a cryptographic identity governance perspective, key recovery requires clear protocols:\n\n"
            "1. **Upload Key Reset Protocol**: If the original upload key was irrevocably lost or corrupted, the Google Play Console account owner navigates to Setup -> App Signing and requests an Upload Key Reset. Provide the public PEM certificate of the newly generated upload key. Google updates the registration within 48 hours without affecting the master App Signing Key or installed user base.\n\n"
            "2. **Self-Signed Enterprise Keystore Rotation**: If the app is distributed outside Google Play without Play App Signing and the original private key is lost, updating the installed user base is technically impossible. The developer must register a new Application ID, forcing users to uninstall and reinstall—demonstrating why Play App Signing is vital.\n\n"
            "3. **HSM & Cloud KMS Integration**: Mitigate credential handling entirely by using Gradle plugins that sign via Google Cloud KMS or AWS KMS remote signing APIs, eliminating `.jks` file handling on CI runners."
        ),
        "follow_ups": [
            {
                "question": "Can an app update be installed if signed with a different key on Android?",
                "answer": "No; Android package manager strictly enforces signature matching across updates to prevent application hijacking."
            },
            {
                "question": "How long does a Google Play Upload Key reset take to become active?",
                "answer": "Typically between 24 to 48 hours after Google support confirms the public PEM certificate update."
            }
        ]
    },
    {
        "id": "BLD-20",
        "arabic_explanation": (
            "ميزة برمجية تعمل بكفاءة على معمارية `arm64-v8a` ولكنها تنهار على معمارية أخرى (مثل `armeabi-v7a` أو `x86_64`). كيف تستكشف وتصلح أخطاء الحزم البرمجية (Packaging)؟\n\n"
            "1. الأسباب الشائعة للفشل على معمارية معينة دون غيرها:\n   - **غياب مكتبة Native مخصصة للمعمارية (Missing .so binary)**: مكتبة خارجية وفرت كود لـ ARM64 فقط وتجاهلت 32-bit أو x86.\n   - **أخطاء في محاذاة الـ 16KB Page Alignment (Android 15+)**: أندرويد 15 يتطلب محاذاة صفحات الذاكرة لمكتبات الـ Native على 16KB بدلاً من 4KB. إذا كانت المكتبة مجمعة بـ NDK قديم، تفشل في العمل على الأجهزة الحديثة.\n   - **استدعاء دوال غير مدعومة في المعالج (CPU Instruction Incompatibilities)**: كود C++ يستخدم تعليمات خاصة بمعالجات معينة (مثل ARM NEON instructions) دون فحص دعم المعالج عبر CPU Features.\n\n"
            "2. خطوات التشخيص:\n   - فحص مجلدات الـ `lib/` في الـ APK عبر `unzip -l app.apk \"lib/*\"`.\n   - تشغيل الـ APK على محاكي بالمعمارية الفاشلة ومراقبة سجلات `adb logcat | grep -E \"DEBUG|linker\"` لمعرفة اسم الملف أو الدالة المفقودة.\n\n"
            "3. الحلول الهندسية:\n   - إعادة تجميع كود الـ C++ عبر الـ NDK لجميع الـ ABIs المطلوبة.\n   - ضبط `ndk.abiFilters` في `build.gradle.kts` لاستبعاد المعماريات غير المدعومة رسمياً."
        ),
        "practical_walkthrough": (
            "تشخيص وفحص محاذاة صفحات الـ 16KB والتأكد من دعم المعماريات المختلفة:\n"
            "```bash\n"
            "# 1. فحص محاذاة صفحات الـ ELF لمكتبات الـ Native (16KB Page Size Alignment):\n"
            "readelf -l app/build/intermediates/merged_native_libs/release/mergeReleaseNativeLibs/out/lib/arm64-v8a/libnative.so | grep LOAD\n"
            "# يجب أن تكون قيمة الـ Align هي 0x4000 (16KB) لدعم أجهزة Android 15+\n"
            "\n"
            "# 2. التحقق من تكامل ملفات الـ .so عبر جميع مجلدات المعماريات:\n"
            "apkanalyzer apk summary app-release.apk\n"
            "```\n\n"
            "```kotlin\n"
            "// 3. ضبط CMake / NDK في build.gradle.kts لضمان التجميع لجميع المعماريات المطلوبة:\n"
            "android {\n"
            "    defaultConfig {\n"
            "        externalNativeBuild {\n"
            "            cmake {\n"
            "                abiFilters(\"arm64-v8a\", \"armeabi-v7a\", \"x86_64\")\n"
            "                arguments(\"-DANDROID_STL=c++_shared\")\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Debug ABI packaging issues by inspecting the APK's lib/ subfolders with unzip or APK Analyzer to confirm whether required .so files exist for the failing architecture. Check for missing 32-bit binaries, Android 15 16KB page alignment violations using readelf, or CPU instruction set incompatibilities.",
        "best_answer": (
            "When features execute correctly on `arm64-v8a` but fail on other architectures, the failure is typically caused by packaging asymmetry or native instruction incompatibility:\n\n"
            "1. **Packaging Asymmetry Audit**:\n"
            "   - Extract the native binary tree: `unzip -l app.apk \"lib/*\"`.\n   - Verify that the failing architecture (e.g. `armeabi-v7a` or `x86_64`) contains the exact identical set of `.so` shared libraries as `arm64-v8a`. If a transitive SDK only bundles ARM64, loading native components fails on 32-bit devices.\n\n"
            "2. **Android 15 16KB Page Alignment Requirements**:\n"
            "   - Android 15 introduces support for 16KB memory page sizes. Native libraries compiled with older NDK versions aligned to 4KB fail to load on 16KB devices. Inspect alignment using `readelf -l libxyz.so | grep -A 1 LOAD` to verify `Align` equals `0x4000` (16KB).\n\n"
            "3. **CPU Instruction Set & NEON Compatibility**:\n"
            "   - Native C/C++ routines employing hardware-accelerated instructions (e.g., ARM NEON SIMD) crash with `SIGILL (Illegal Instruction)` if executed on CPUs or emulators lacking those specific hardware execution registers. Implement runtime feature probing (`cpufeatures` library) before invoking vector extensions."
        ),
        "deep_answer": (
            "From a multi-architecture testing and CI perspective, validating native stability requires matrix testing:\n\n"
            "1. **CI Architecture Emulation Matrix**: Run automated instrumentation tests against multiple emulator architectures in CI: ARM64 system images on Apple Silicon/ARM runners, and x86_64 system images on Intel/AMD runners, catching ABI packaging gaps before deployment.\n\n"
            "2. **Packaging PickFirsts & Duplicate JNI Libraries**: If two dependencies bundle conflicting versions of `libc++_shared.so`, AGP fails the build with a duplicate file collision. Setting `packaging { jniLibs.pickFirsts.add(\"**/libc++_shared.so\") }` resolves compilation, but can crash at runtime if the picked version has an incompatible C++ ABI. Ensure all native dependencies compile against identical NDK toolchain versions.\n\n"
            "3. **NDK abiFilters Alignment**: Explicitly declare `ndk.abiFilters` in `build.gradle.kts` matching the target distribution: `arm64-v8a` and `armeabi-v7a` for consumer devices, plus `x86_64` for developer emulators."
        ),
        "follow_ups": [
            {
                "question": "What is the 16KB page size requirement in Android 15?",
                "answer": "Android 15 supports devices configured with 16KB memory pages; native ELF binaries must be compiled and aligned with 16KB boundaries (Align 0x4000) or they fail to load."
            },
            {
                "question": "What happens if an app loads a native library built with a newer NDK STL than other libraries?",
                "answer": "Symbol resolution collisions or memory layout incompatibilities in libc++_shared.so can trigger SIGSEGV crashes at runtime."
            }
        ]
    },
    {
        "id": "BLD-21",
        "arabic_explanation": (
            "كيف تقوم بطرح تحديث جديد للتطبيق بشكل آمن (Staged Rollout)، وكيف تتراجع عنه (Rollback) فوراً إذا ظهرت مشكلة كارثية؟\n\n"
            "1. الطرح التدريجي الآمن (Staged Rollout Strategy):\n   - **ممنوع نشر تحديث لـ 100% من المستخدمين مرة واحدة**!\n   - استخدم جدول النشر التدريجي في Google Play Console:\n     `1% (اليوم 1) -> 5% (اليوم 2) -> 20% (اليوم 3) -> 50% (اليوم 4) -> 100% (اليوم 5)`.\n   - أثناء الطرح، راقب **Android Vitals** ومعدل الـ Crash Rate والـ ANRs في Crashlytics. إذا زاد معدل الانهيار عن 0.5%، أوقف الطرح فوراً.\n\n"
            "2. الحقيقة الصادمة حول التراجع (The Rollback Reality in Android):\n   - **نظام أندرويد لا يدعم التراجع (Downgrade Rollback) للعميل**! لا يمكن للمستخدم تثبيت إصدار قديم (`versionCode 100`) فوق إصدار أحدث (`versionCode 101`)؛ نظام Android OS سيرفض التثبيت لحماية بيانات المستخدم من التلف.\n\n"
            "3. كيف تنفذ التراجع عملياً (The Three-Tier Rollback Plan):\n   - **1. إيقاف الطرح فوراً (Halt Rollout)**: يمنع وصول التحديث لباقي الـ 95% من المستخدمين.\n   - **2. تفعيل مفتاح الإلغاء عن بُعد (Remote Kill Switch / Feature Flag)**: تعطيل الميزة التالفة فورياً عبر Remote Config للمستخدمين الذين قاموا بتنزيل التحديث بالفعل.\n   - **3. إطلاق تحديث طارئ (Expedited Hotfix Release)**: بناء إصدار جديد برقم أعلى (`versionCode 102`) يحتوي على كود التراجع (Revert Commit) وطلب مراجعة مستعجلة من Google Play."
        ),
        "practical_walkthrough": (
            "إدارة سيناريو الطوارئ وإيقاف الطرح ونشر التحديث التصحيحي عبر Fastlane / Play Console:\n"
            "```bash\n"
            "# 1. إيقاف الطرح التدريجي فوراً عبر Fastlane Supply:\n"
            "bundle exec fastlane supply halt --track production\n"
            "\n"
            "# 2. التراجع عن الـ Commit المتسبب في الكارثة في Git:\n"
            "git revert HEAD --no-edit\n"
            "\n"
            "# 3. زيادة versionCode وبناء Hotfix جديد برقم أعلى:\n"
            "# (مثلاً: versionCode 102 أعلى من النسخة المعطوبة 101)\n"
            "./gradlew :app:bundleRelease\n"
            "\n"
            "# 4. رفع الـ Hotfix فوراً ونشره بنسبة 100% مع طلب فحص أولوية:\n"
            "bundle exec fastlane supply --aab app-release.aab --track production --rollout 1.0\n"
            "```"
        ),
        "quick_answer": "Roll out safely using Google Play Staged Rollouts (1% -> 5% -> 20% -> 100%) while monitoring Android Vitals. Because Android package manager strictly forbids downgrading versionCode, rollback requires halting the rollout, toggling remote feature flag kill switches, and immediately publishing a hotfix with an incremented versionCode.",
        "best_answer": (
            "Safely rolling out and rolling back Android releases requires understanding app store release mechanics and OS installation invariants:\n\n"
            "1. **Staged Rollout Cadence**:\n"
            "   - Never release directly to 100% of production. Follow a phased rollout schedule: 1% -> 5% -> 20% -> 50% -> 100% across 5–7 days.\n   - Continuously monitor Google Play Android Vitals and Crashlytics dashboards. If the crash-free user rate drops below 99.5% or ANR rate exceeds 0.47%, halt the rollout immediately.\n\n"
            "2. **The Android Downgrade Invariant**:\n"
            "   - The Android OS package manager rejects installing an APK with a lower `versionCode` than the currently installed version (`INSTALL_FAILED_VERSION_DOWNGRADE`). You cannot 'unpublish' a bad release to force users back to an older version.\n\n"
            "3. **Incident Containment Protocol**:\n"
            "   - **Halt Rollout**: Stop the rollout in Google Play Console, preventing the remaining percentage from downloading the defective build.\n   - **Remote Kill Switch**: Toggle the offending feature flag off remotely via LaunchDarkly/Firebase to remediate users who already updated.\n   - **Emergency Expedited Hotfix**: Revert the bad commit in Git, increment the `versionCode` (e.g. from 201 to 202), build a fresh AAB, and release it directly to 100%."
        ),
        "deep_answer": (
            "From an operational release management perspective, incident containment requires post-deployment safeguards:\n\n"
            "1. **Google Play Expedited Review Request**: When publishing an emergency hotfix resolving a catastrophic production crash or security regression, submit an expedited review request via the Play Console help portal, reducing review turnaround to under 2 hours.\n\n"
            "2. **In-App Immediate Update Enforcement**: When the hotfix is approved, flag the previous broken version in your backend config. When users on the broken version launch the app, trigger Google Play's **Immediate In-App Update** flow (`AppUpdateType.IMMEDIATE`). This full-screen modal forces users to download the hotfix before accessing the app.\n\n"
            "3. **Blameless Post-Mortem & CI Hardening**: After incident resolution, conduct a post-mortem to determine why testing missed the defect. Implement automated regression tests and pre-release canary tracks to prevent identical failures."
        ),
        "follow_ups": [
            {
                "question": "Can an Android user downgrade an app to an older version without losing data?",
                "answer": "No; the OS forbids downgrading; the only way to install an older version is to uninstall the current app first, which deletes all local data."
            },
            {
                "question": "What is the Google Play badging threshold for Android Vitals crash rate?",
                "answer": "Google Play enforces a bad behavior threshold of 1.09% overall crash rate and 0.47% ANR rate; exceeding these hurts store ranking."
            }
        ]
    }
]


def update_bld_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in BLD_15_21:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions BLD-15 to BLD-21. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_bld_data()
