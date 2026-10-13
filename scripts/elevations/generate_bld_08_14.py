#!/usr/bin/env python3
"""Generator for BLD-08 through BLD-14 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "bld.json"

BLD_08_14 = [
    {
        "id": "BLD-08",
        "arabic_explanation": (
            "كيف تستكشف وتصلح الانهيارات (Crashes) التي تحدث فقط في نسخة الـ Release بينما يعمل التطبيق بشكل مثالي في بيئة الـ Debug؟\n\n"
            "1. الأسباب الجذرية لانهيارات الـ Release-Only:\n   - **تقليص أو حذف كود مستخدم بالـ Reflection (R8 Stripping)**: استدعاء كلاس أو دالة ديناميكياً؛ R8 لا يرى أي استدعاء مباشر فيعتقد أنها Dead Code ويحذفها، فتحدث `ClassNotFoundException` أو `NoSuchMethodException`.\n   - **تشويش أسماء حقول الـ Serialization**: مكتبات مثل GSON أو Moshi تبحث عن أسماء الحقول في الـ JSON (مثل `user_id`). بعد التشويش، يتغير اسم الحقل في الـ DEX إلى `a`، فتفشل السيريالايزيشن أو تصبح كل الحقول `null` مما يسبب `NullPointerException`.\n   - **حذف كود الـ JNI / Native Code**: دوال الـ Native التي تستدعي كود Java بالاسم الصريح تفشل بعد التشويش.\n   - **تقليص الموارد (Resource Shrinking)**: استخدام `resources.getIdentifier(\"icon_\" + name, \"drawable\", packageName)`؛ R8 يعتقد أن الصورة غير مستخدمة ويستبدلها بملف تالف.\n\n"
            "2. كيفية إعادة إنتاج المشكلة محلياً (Reproducing Locally):\n   - **إنشاء Build Type مخصص للتشخيص (`releaseTest` أو `benchmark`)**: يحتوي على `isMinifyEnabled = true` ولكن مع `isDebuggable = true` و `signingConfig = debug` لتشغيل الـ Debugger وفحص الـ Stack Trace مباشرة.\n\n"
            "3. أدوات التحقيق في مخرجات R8:\n   - فحص ملف `usage.txt` (الموجود في `build/outputs/mapping/release/`): يسرد كل الكلاسات والدوال التي حذفها R8 لمعرفة ما إذا كان الكلاس المنهار قد تم حذفه بالخطأ."
        ),
        "practical_walkthrough": (
            "إنشاء Build Type هجين محلياً لاكتشاف مشاكل R8 واستخدام ملفات seeds.txt و usage.txt:\n"
            "```kotlin\n"
            "// في build.gradle.kts: إنشاء نوع بناء مخصص يماثل الـ Release تماماً ولكن يقبل الـ Debugger:\n"
            "android {\n"
            "    buildTypes {\n"
            "        create(\"debugMinified\") {\n"
            "            initWith(getByName(\"release\"))\n"
            "            // تمكين الـ Debugging مع الحفاظ على نفس قواعد R8 والـ Obfuscation:\n"
            "            isDebuggable = true\n"
            "            signingConfig = signingConfigs.getByName(\"debug\")\n"
            "            matchingFallbacks += listOf(\"release\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "```bash\n"
            "# أوامر تشخيص مخرجات R8 عبر الـ CLI:\n"
            "# 1. معرفة الكلاسات التي حذفها R8 وظن أنها غير مستخدمة:\n"
            "grep \"com.example.model.UserProfile\" app/build/outputs/mapping/release/usage.txt\n"
            "\n"
            "# 2. معرفة الكلاسات التي حافظ عليها R8 بناءً على الـ Keep Rules:\n"
            "grep \"com.example.model.UserProfile\" app/build/outputs/mapping/release/seeds.txt\n"
            "```"
        ),
        "quick_answer": "Debug release-only crashes by creating a debuggable minified build type (isDebuggable = true with isMinifyEnabled = true), deobfuscating the stack trace with retrace and mapping.txt, and checking usage.txt to verify if R8 stripped reflection, serialization, or JNI entry points.",
        "best_answer": (
            "Release-only crashes almost universally stem from bytecode optimizations, identifier obfuscation, or tree shaking executed by R8:\n\n"
            "1. **Common Failure Vectors**:\n"
            "   - **Reflection Stripping**: Classes instantiated via `Class.forName()` or dynamic reflection appear unreachable in static call graphs, causing R8 to strip them (`ClassNotFoundException`).\n   - **Serialization Mismatches**: Reflection-based serializers (GSON) expect exact field names. Obfuscation renames fields to `a`, leaving deserialized objects populated with `null` values.\n   - **JNI Breakage**: Native C/C++ code referencing Java methods via JNI signatures fails when R8 renames or inlines the Java method.\n   - **Dynamic Resource Lookups**: Using `Resources.getIdentifier()` fails when `shrinkResources = true` strips drawables flagged as unreferenced.\n\n"
            "2. **Local Reproduction Strategy**:\n"
            "   - Add a hybrid build type (`debugMinified`) that mirrors `release` (`isMinifyEnabled = true`, identical ProGuard rules), but sets `isDebuggable = true` and debug signing. This allows developers to attach Android Studio's debugger and reproduce the exact crash locally.\n\n"
            "3. **Investigating R8 Diagnostic Reports**:\n"
            "   - Inspect `build/outputs/mapping/release/usage.txt` to confirm if R8 pruned the missing class.\n   - Inspect `seeds.txt` to verify whether keep rules successfully preserved intended entry points."
        ),
        "deep_answer": (
            "From an advanced compiler engineering perspective, release-only crashes also involve timing and aggressive method inlining:\n\n"
            "1. **Aggressive Method Inlining & Class Merging**: With `proguard-android-optimize.txt`, R8 merges single-implementation interfaces directly into concrete classes and inlines short methods. If an SDK inspects the runtime class hierarchy or checks `instanceof` on merged interfaces, type casting exceptions (`ClassCastException`) arise exclusively in release builds.\n\n"
            "2. **Concurrency & Timing Discrepancies**: Release builds run significantly faster than debug builds because debug assertions are eliminated and bytecode is optimized. Race conditions or thread safety defects in asynchronous Coroutines that were masked by debug overhead can surface as timing bugs in optimized release binaries.\n\n"
            "3. **Deobfuscating Production Traces**: When diagnosing in the field, run Google's `retrace` CLI locally with the matching `mapping.txt`: `retrace mapping.txt obfuscated_trace.txt`. Ensure CI archives `mapping.txt` as a required build artifact for every released version code."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between seeds.txt and usage.txt?",
                "answer": "seeds.txt lists all classes and members preserved by keep rules; usage.txt lists all code stripped by R8 as dead code."
            },
            {
                "question": "Why does GSON fail more often in release builds than Moshi with codegen?",
                "answer": "GSON uses runtime reflection requiring broad keep rules; Moshi with KSP generates explicit adapter classes at compile time, eliminating reflection lookups."
            }
        ]
    },
    {
        "id": "BLD-09",
        "arabic_explanation": (
            "كيف تحدد وتكتب قواعد R8 Keep Rules الدقيقة لنماذج الـ Reflection، والـ Serialization، والـ JNI، ومكتبات الـ SDKs دون إفساد تقليص حجم التطبيق؟\n\n"
            "1. أنواع أوامر الـ Keep في ProGuard/R8:\n   - **`-keep`**: يحافظ على الكلاس وجميع أعضائه بالاسم الأصلي ويمنع حذفه وتشويشه كلياً (يستخدم بحذر شديد).\n   - **`-keepclassmembers`**: يحافظ على أعضاء الكلاس (Fields/Methods) فقط إذا كان الكلاس نفسه مستخدماً في الكود، مما يسمح بحذف الكلاس إذا كان غير مستخدم.\n   - **`-keepnames`**: يسمح بتقليص وحذف الكلاس إذا لم يكن مستخدماً، لكن إذا تم استخدامه يُمنع تغيير اسمه الأصلي.\n\n"
            "2. القواعد الدقيقة لكل مجال:\n   - **الـ Serialization (DTOs)**: نحتاج فقط للحفاظ على أسماء الحقول (Fields) وليس كل الكلاس: `-keepclassmembers class com.example.dto.** { <fields>; }`.\n   - **الـ JNI (Native Methods)**: نحافظ على الدوال الموسومة بـ `native` والكلاسات التي تحتويها: `-keepclasseswithmembernames class * { native <methods>; }`.\n   - **الـ Reflection**: استخدام `@Keep` من مكتبة `androidx.annotation.Keep` مباشرة على الكلاس أو الدالة بدلاً من كتابة قواعد عريضة في ملف ProGuard.\n\n"
            "3. الخطيئة الكبرى (Wildcard Poisoning):\n   - كتابة `-keep class com.example.** { *; }` تلغي فائدة R8 بالكامل وتعطل الـ Shrinking والـ Optimization للمشروع."
        ),
        "practical_walkthrough": (
            "أمثلة عملية لقواعد ProGuard الاحترافية والدقيقة للمجالات الحساسة:\n"
            "```text\n"
            "# 1. حماية كلاسات ودوال الـ Native المربوطة بـ C/C++ عبر JNI:\n"
            "-keepclasseswithmembernames,includedescriptorclasses class * {\n"
            "    native <methods>;\n"
            "}\n"
            "\n"
            "# 2. حماية حقول نماذج السيريالايزيشن الخاصة بالـ Network DTOs فقط لمنع تشويش الأسماء:\n"
            "-keepclassmembers,allowobfuscation class * implements java.io.Serializable {\n"
            "    static final long serialVersionUID;\n"
            "    private static final java.io.ObjectStreamField[] serialPersistentFields;\n"
            "}\n"
            "\n"
            "# 3. حماية الـ Enums من حذف دالتي values() و valueOf() المستخدمتين بالـ Reflection:\n"
            "-keepclassmembers enum * {\n"
            "    public static **[] values();\n"
            "    public static ** valueOf(java.lang.String);\n"
            "}\n"
            "\n"
            "# 4. استخدام @Keep البرمجي كبديل أنظف وأسهل في صيانة الكود:\n"
            "-keep @androidx.annotation.Keep class * { *; }\n"
            "-keepclasseswithmembers class * {\n"
            "    @androidx.annotation.Keep <methods>;\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Formulate R8 keep rules precisely: use -keepclassmembers for serialization DTO fields to retain names without locking the whole class, -keepclasseswithmembernames for JNI native methods, and targeted @Keep annotations for reflection targets, strictly avoiding broad wildcards that defeat shrinking.",
        "best_answer": (
            "Crafting surgical R8 keep rules preserves runtime functionality while maximizing dead-code elimination and obfuscation:\n\n"
            "1. **Serialization Models (DTOs)**:\n"
            "   - Avoid broad `-keep class com.my.model.** { *; }`. Instead, preserve only the field names required by reflection serializers:\n     `-keepclassmembers class com.example.dto.** { <fields>; }`.\n   - Better yet, adopt Kotlinx Serialization or Moshi Codegen with KSP, which generate explicit adapters at compile time and require zero reflection keep rules.\n\n"
            "2. **JNI Native Invocations**:\n"
            "   - Native C/C++ libraries resolve Java methods using explicit class and descriptor signatures. Preserve all native methods and their parameter types:\n     `-keepclasseswithmembernames,includedescriptorclasses class * { native <methods>; }`.\n\n"
            "3. **Reflection Targets**:\n"
            "   - Rather than maintaining fragile string patterns in `proguard-rules.pro`, decorate reflection-instantiated classes with `@Keep` (from AndroidX annotations). AGP bundles default rules preserving any class or member annotated with `@Keep`.\n\n"
            "4. **Third-Party SDKs**:\n"
            "   - Rely on the SDK's bundled `consumerProguardFiles`. Only author manual keep rules for legacy libraries that fail to publish their own consumer rules."
        ),
        "deep_answer": (
            "From an architectural code-shrinkage perspective, broad keep rules constitute silent technical debt:\n\n"
            "1. **The allowshrinking and allowobfuscation Modifiers**: ProGuard rules support granular modifier flags. For example, `-keepnames` is equivalent to `-keep,allowshrinking`. It permits R8 to delete the class if unused, but prevents renaming if the class survives. This is ideal for analytics DTOs.\n\n"
            "2. **Auditing Rule Impact with -whyareyoukeeping**: When investigating why an unused class was unexpectedly retained in the final DEX, inject `-whyareyoukeeping class com.example.UnusedClass` into `proguard-rules.pro`. During build execution, R8 prints the exact chain of reachability references and keep rules that forced its preservation.\n\n"
            "3. **Automated CI Size Regression Testing**: Enforce a maximum binary size ceiling in CI. Overly broad keep rules introduced in PRs immediately trigger size alert regressions, enforcing strict scrutiny during code reviews."
        ),
        "follow_ups": [
            {
                "question": "What does -whyareyoukeeping do in R8?",
                "answer": "It instructs R8 to print the exact dependency path and root keep rule explaining why a specific class was not stripped during shrinking."
            },
            {
                "question": "What is the difference between -keep and -keepnames?",
                "answer": "-keep prevents both shrinking and obfuscation; -keepnames allows shrinking if unused, but prevents obfuscation if kept."
            }
        ]
    },
    {
        "id": "BLD-10",
        "arabic_explanation": (
            "كيف تستخدم أداة `retrace` مع ملفات `mapping.txt` لفك تشفير وتتبع تقارير الانهيارات (Stack Traces) في الإنتاج؟\n\n"
            "1. المشكلة في تقارير أخطاء الـ Production:\n   - عندما ينهار التطبيق في الإنتاج بعد تفعيل R8، يكون الـ Stack Trace مشوشاً وغير مفهوم:\n     `java.lang.NullPointerException: at a.b.c.d(SourceFile:12)`.\n   - يستحيل على المطور معرفة الكلاس أو رقم السطر الحقيقي الذي تسبب في المشكلة بدون عملية **Deobfuscation**.\n\n"
            "2. ما هو ملف الـ `mapping.txt`؟\n   - ملف نصي يولده R8 أثناء بناء نسخة الـ Release في المجلد:\n     `app/build/outputs/mapping/release/mapping.txt`.\n   - يحتوي على خريطة ثنائية الاتجاه تربط كل اسم مشوش باسمه الأصلي مع أرقام الأسطر.\n   - **قاعدة حرجة**: لكل `versionCode` ملف `mapping.txt` فريد وخاص به؛ استخدام ملف mapping من إصدار مختلف سيعطي نتائج خاطئة تماماً!\n\n"
            "3. استخدام أداة `retrace`:\n   - أداة CLI رسمية مدمجة في Android SDK Command-Line Tools (`$ANDROID_HOME/cmdline-tools/latest/bin/retrace`).\n   - تقوم بقراءة ملف الـ mapping والنص المشوش وإعادة بناء الـ Stack Trace الأصلي كاملاً بأرقام الأسطر الحقيقية."
        ),
        "practical_walkthrough": (
            "استخدام retrace عبر سطر الأوامر وأتمتة رفع ملفات الـ mapping في CI/CD:\n"
            "```bash\n"
            "# 1. فك تشفير Stack Trace مشوش محلياً باستخدام أداة retrace:\n"
            "retrace app/build/outputs/mapping/release/mapping.txt obfuscated_trace.txt\n"
            "\n"
            "# 2. يمكن أيضاً تمرير الـ Stack Trace مباشرة عبر الـ Pipe:\n"
            "adb logcat -d | retrace app/build/outputs/mapping/release/mapping.txt\n"
            "```\n\n"
            "```kotlin\n"
            "// 3. أتمتة رفع ملف الـ mapping تلقائياً إلى Firebase Crashlytics في build.gradle.kts:\n"
            "plugins {\n"
            "    alias(libs.plugins.firebase.crashlytics)\n"
            "}\n"
            "\n"
            "android {\n"
            "    buildTypes {\n"
            "        release {\n"
            "            firebaseCrashlytics {\n"
            "                // يضمن رفع ملف الـ mapping.txt المتطابق تلقائياً مع كل Build يخرج من الـ CI\n"
            "                mappingFileUploadEnabled = true\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Use the retrace CLI tool bundled in Android SDK command-line tools with the release build's mapping.txt to translate obfuscated stack traces back into human-readable class, method, and line numbers. In automated production, configure Crashlytics or Sentry Gradle plugins to upload mapping files during CI release builds.",
        "best_answer": (
            "Retrace is the canonical deobfuscation utility translating R8-mangled runtime stack traces into actionable debugging source locations:\n\n"
            "1. **The Mapping Table (`mapping.txt`)**:\n"
            "   - Generated by R8 in `app/build/outputs/mapping/<variant>/mapping.txt`. It stores a bidirectional translation table mapping mangled symbols (e.g. `a.b.c(SourceFile:4)`) back to original package names, class names, method signatures, and original source line numbers.\n   - Every distinct build produces a unique `mapping.txt`; using a mismatched mapping file produces incorrect or nonsense symbols.\n\n"
            "2. **Manual CLI Execution**:\n"
            "   - Run: `retrace mapping.txt obfuscated_crash.txt`.\n   - The tool parses the obfuscated input, matches class and line ranges, and outputs the pristine Kotlin/Java stack trace.\n\n"
            "3. **Automated Production Triage**:\n"
            "   - In enterprise CI/CD, crash reporting providers (Firebase Crashlytics, Sentry, Bugsnag) integrate dedicated Gradle tasks (e.g. `uploadCrashlyticsMappingFileRelease`) that automatically archive and upload `mapping.txt` matching the release `versionCode` to cloud dashboards."
        ),
        "deep_answer": (
            "From a release engineering and forensics viewpoint, mapping file management requires strict lifecycle governance:\n\n"
            "1. **Line Number Table Compaction (-keepattributes LineNumberTable)**:\n"
            "   - By default, R8 compacts line number tables to save DEX space, rewriting multiple original line numbers into sequential ranges (e.g., 1, 2, 3). Retrace uses the interval ranges in `mapping.txt` to reconstruct the exact original file line numbers. Ensure `proguard-rules.pro` includes `-keepattributes SourceFile,LineNumberTable` or line numbers cannot be recovered.\n\n"
            "2. **Long-Term Mapping File Archival**: Play Store apps remain active on user devices for years. If a user crashes on version 1.2.0 released 18 months ago, the matching `mapping.txt` must be retrievable. Configure CI release jobs to upload `mapping.txt` and unsigned AAB artifacts to immutable cloud cold storage (e.g., AWS S3 bucket with retention locks).\n\n"
            "3. **Google Play Console Deobfuscation**: When deploying AABs to Google Play, Google requires uploading `mapping.txt` (or bundles it automatically in the App Bundle metadata under `BUNDLE-METADATA/com.android.tools.build.obfuscation/proguard.map`) so Android Vitals can display deobfuscated traces natively."
        ),
        "follow_ups": [
            {
                "question": "What happens if LineNumberTable attribute is stripped in ProGuard rules?",
                "answer": "Stack traces will show Unknown Source or line number 1 for all frames, making it impossible to determine the exact failing line of code."
            },
            {
                "question": "Where is the mapping file embedded inside an Android App Bundle (AAB)?",
                "answer": "Inside BUNDLE-METADATA/com.android.tools.build.obfuscation/proguard.map within the root of the AAB archive."
            }
        ]
    },
    {
        "id": "BLD-11",
        "arabic_explanation": (
            "كيف تقوم بتحليل حجم الـ APK والـ AAB وفحص مكتبات الـ Native ABIs المضمنة لتفادي التضخم (App Bloat)؟\n\n"
            "1. أدوات تحليل حجم التطبيق:\n   - **APK Analyzer المدمج في Android Studio**: أسرع أداة لفحص تشريح الـ APK. يقسم الحجم إلى: `classes.dex`, `res/`, `resources.arsc`, `lib/` (Native Libraries), و `assets/`.\n   - **أداة `apkanalyzer` عبر السطر البرمجي**: تتيح فحص الحجم في الـ CI/CD ومقارنة الفروق بين إصدارين (`apkanalyzer apk compare old.apk new.apk`).\n\n"
            "2. تضخم مكتبات الـ Native (Native ABI Bloat):\n   - مجلد `lib/` يحتوي على ملفات الـ `.so`. إذا تضمن التطبيق معمارية غير مطلوبة، قد يتضاعف حجم التطبيق 3 مرات!\n   - المعماريات الشائعة: `arm64-v8a` (معظم الهواتف الحديثة 64-bit)، `armeabi-v7a` (الهواتف القديمة 32-bit)، `x86_64` (المحاكيات وChromebooks).\n\n"
            "3. تقنيات تقليص الحجم العملية:\n   - **استخدام Android App Bundle (AAB)**: يقسم التطبيق تلقائياً عبر `bundletool` ويرسل للمستخدم معمارية معالجه ولغته فقط.\n   - **ضغط الموارد وتنزيلها عند الطلب**: استخدام Play Feature Delivery للميزات الكبيرة، وتحويل الصور إلى صيغ WebP أو Vector Drawables.\n   - **حذف الـ ABIs غير الضرورية**: تقييد الـ ABIs في `build.gradle.kts` عبر `ndk.abiFilters`."
        ),
        "practical_walkthrough": (
            "تكوين فلاتر المعالجات (ABI Filters) واستخدام apkanalyzer لمقارنة الحجم في سطر الأوامر:\n"
            "```kotlin\n"
            "// في build.gradle.kts: تقييد حزم الـ Native على المعماريات المستهدفة فقط:\n"
            "android {\n"
            "    defaultConfig {\n"
            "        ndk {\n"
            "            // حصر المكتبات المجمعة على أجهزة الهواتف الحقيقية فقط واستبعاد x86 من الإنتاج:\n"
            "            abiFilters += listOf(\"arm64-v8a\", \"armeabi-v7a\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "```bash\n"
            "# 1. فحص ملخص حجم مكونات الـ APK عبر السطر البرمجي:\n"
            "apkanalyzer apk summary app-release.apk\n"
            "\n"
            "# 2. مقارنة حجم نسختين من الـ APK في CI لاكتشاف الزيادات غير المتوقعة (Size Regressions):\n"
            "apkanalyzer apk compare --different-only old-release.apk new-release.apk\n"
            "```"
        ),
        "quick_answer": "Analyze APK/AAB size using Android Studio's APK Analyzer or apkanalyzer CLI to inspect classes.dex, resources, and lib/ native folders. Eliminate bloat by publishing with AABs to deliver split ABIs, converting assets to WebP/Vectors, and configuring ndk.abiFilters to exclude unused architectures.",
        "best_answer": (
            "Auditing and optimizing binary footprint requires inspecting artifact composition across distinct asset categories:\n\n"
            "1. **Binary Composition Breakdown**:\n"
            "   - **`classes.dex`**: Compiled bytecode. Optimized via R8 shrinking, dead code elimination, and method inlining.\n   - **`lib/` (Native `.so` Binaries)**: Compiled C/C++ libraries. Often constitutes 50–70% of total download size if multiple ABIs are bundled.\n   - **`res/` & `resources.arsc`**: Images, XMLs, and indexed resource tables. Optimized via resource shrinking, WebP conversion, and vector drawables.\n   - **`assets/`**: Uncompressed arbitrary files (fonts, databases, ML models).\n\n"
            "2. **Native ABI Optimization**:\n"
            "   - When building fat APKs for direct distribution, restrict bundled ABIs using `ndk.abiFilters += listOf(\"arm64-v8a\", \"armeabi-v7a\")`, stripping unused `x86` and `x86_64` emulators.\n   - When distributing via Google Play, publish via **Android App Bundle (AAB)**. Google Play delivers a single architecture split matching the user's phone, slashing native download weight.\n\n"
            "3. **Automated CI Size Budgets**:\n"
            "   - Integrate `apkanalyzer` or GitHub size-diff actions into CI. Set an alert threshold (e.g., fail PR if download size increases by > 500KB) to prevent accidental bundling of massive third-party assets."
        ),
        "deep_answer": (
            "From an advanced mobile performance perspective, download size directly dictates user conversion and uninstall rates:\n\n"
            "1. **The Size-to-Install Dropoff Correlation**: Google Play telemetry demonstrates that every 6MB increase in APK download size correlates with a 1% drop in install conversion rates, particularly across emerging market cellular connections.\n\n"
            "2. **Uncompressed Native Libraries (android:extractNativeLibs)**: Setting `android:extractNativeLibs=\"false\"` in the manifest (default in modern AGP) stores `.so` files uncompressed and page-aligned inside the APK. The APK file size increases slightly, but the OS maps libraries directly into memory without extracting them to disk upon install, saving 50MB+ of device storage post-installation.\n\n"
            "3. **Font & Emoji Bundling Optimization**: Replace bundled TrueType/OpenType font files (which can add 15MB) with Google Play Services **Downloadable Fonts**, fetching shared system typography at runtime without bundling font files in the APK."
        ),
        "follow_ups": [
            {
                "question": "What is the benefit of android:extractNativeLibs=false?",
                "answer": "It page-aligns native libraries inside the APK so the OS executes them directly via mmap without extracting copies to disk, reducing device disk usage."
            },
            {
                "question": "How do Vector Drawables reduce APK size compared to PNGs?",
                "answer": "A single XML vector scales to all screen densities, replacing five separate rasterized PNG files (mdpi through xxxhdpi)."
            }
        ]
    },
    {
        "id": "BLD-12",
        "arabic_explanation": (
            "كيف تقوم بإعداد وتأمين مفاتيح التوقيع الرقمي (Signing Keys) واستخدام Google Play App Signing بأعلى معايير الأمان؟\n\n"
            "1. معمارية Google Play App Signing الحديثة:\n   - تفصل عملية التوقيع إلى مفتاحين مستقلين تماماً:\n     * **مفتاح الرفع (Upload Key)**: يملكه المطور ويستخدمه لتوقيع ملف الـ AAB قبل رفعه إلى Play Console.\n     * **مفتاح توقيع التطبيق (App Signing Key)**: يُخزن داخل بنية Google التحتية المشفرة والمحمية بنظام Google Cloud KMS. يقوم Google Play بحذف توقيع الـ Upload Key وتوقيع الـ Split APKs بمفتاح الـ App Signing Key الرسمي.\n\n"
            "2. الميزة الأمنية الكبرى:\n   - في الماضي: إذا فُقد مفتاح التوقيع أو غادر المطور المسؤول، كان التطبيق ينتهي للأبد ويجب تغيير الـ Package Name وخسارة جميع المستخدمين!\n   - مع Play App Signing: إذا فُقد الـ Upload Key، يمكن للمطور طلب إعادة تعيينه (Reset Upload Key) عبر Play Console بسهولة ودون أي تأثير على المستخدمين.\n\n"
            "3. أفضل الممارسات الأمنية لحماية المفاتيح:\n   - **ممنوع حفظ المفاتيح في Git**: استبعاد ملفات `.jks` و `.keystore` في `.gitignore`.\n   - **التخزين المشفر في CI/CD**: تشفير الـ Keystore كـ Base64 String وحفظه في GitHub Secrets أو Google Cloud Secret Manager، وقراءته أثناء وقت الـ Build فقط ثم مسحه فوراً."
        ),
        "practical_walkthrough": (
            "استخراج شهادة الـ Upload Key وتهيئتها في CI/CD بأمان:\n"
            "```bash\n"
            "# 1. إنشاء مفتاح Upload Key مشفر جديد باستخدام keytool:\n"
            "keytool -genkeypair -v -keystore upload-keystore.jks \\\n"
            "  -alias upload_key -keyalg RSA -keysize 2048 -validity 10000\n"
            "\n"
            "# 2. استخراج شهادة المفتاح العامة بصيغة PEM لتسجيلها في Google Play Console:\n"
            "keytool -export -rfc -keystore upload-keystore.jks \\\n"
            "  -alias upload_key -file upload_certificate.pem\n"
            "\n"
            "# 3. تحويل ملف الـ Keystore إلى Base64 لتخزينه كـ Secret في GitHub Actions:\n"
            "base64 -i upload-keystore.jks | pbcopy\n"
            "```"
        ),
        "quick_answer": "Configure signing safely by enrolling in Google Play App Signing, which isolates your developer Upload Key from the master App Signing Key secured in Google Cloud KMS. Manage the upload keystore securely in CI/CD using encrypted base64 environment variables, never committing credentials to Git.",
        "best_answer": (
            "Modern Android release signing delegates distribution authority to Google Play App Signing while protecting developer upload credentials:\n\n"
            "1. **The Dual-Key Security Model**:\n"
            "   - **Upload Key**: Held by the developer or CI pipeline. Used exclusively to sign the uploaded `.aab` bundle to prove developer authenticity to Google Play.\n   - **App Signing Key**: Stored securely in Google's enterprise Key Management Service (KMS). Google validates the upload bundle, strips the upload signature, and signs end-user split APKs using the master app signing key.\n\n"
            "2. **Disaster Recovery Benefit**:\n"
            "   - If a developer machine is lost or an upload key compromised, an account owner can request an upload key reset via the Google Play Console. Google registers the new upload certificate within 48 hours without breaking installed user upgrade lineages.\n\n"
            "3. **Automated CI/CD Key Injection**:\n"
            "   - Encode the upload keystore binary into a Base64 string and store it inside CI secrets (`ANDROID_KEYSTORE_BASE64`).\n   - During the release pipeline execution, the runner decodes the string to a transient temporary file, compiles and signs the bundle, and deterministically wipes the file before job termination."
        ),
        "deep_answer": (
            "From a cryptographic governance perspective, deploying Play App Signing requires managing certificate dependencies across ecosystems:\n\n"
            "1. **Third-Party API Certificate Binding**: APIs like Google Maps, SafetyNet/Play Integrity, Firebase Phone Auth, and OAuth2 clients validate requests by checking the app's signing certificate SHA-1/SHA-256 fingerprint. When enrolled in Play App Signing, you must register **Google's App Signing certificate fingerprint** in developer consoles, not your local upload key fingerprint, or production authentication will fail.\n\n"
            "2. **Dual-Distribution (Play Store + Alternative Stores)**: If an app is distributed on both Google Play and alternative app stores (e.g. Huawei AppGallery, Samsung Galaxy Store, or direct APK downloads), managing different keys is required unless you export the original signing key to both stores, which partially undermines the isolation benefit.\n\n"
            "3. **Hardware-Backed Key Generation**: For maximum enterprise security, generate upload keys within Hardware Security Modules (HSM) or YubiKeys supporting PKCS#11, preventing exportable private key bytes from touching local developer hard drives."
        ),
        "follow_ups": [
            {
                "question": "What happens if you accidentally publish an app with a debug signing key?",
                "answer": "Google Play Console rejects the upload immediately because debug keystores are well-known and insecure."
            },
            {
                "question": "Where do you find the official SHA-1 fingerprint of the App Signing Key?",
                "answer": "Inside Google Play Console under Setup -> App Signing -> App signing key certificate."
            }
        ]
    },
    {
        "id": "BLD-13",
        "arabic_explanation": (
            "كيف تدير الـ `versionCode` والـ `versionName` وسجلات الإصدار (Release Notes) آلياً وبشكل حتمي في مسارات الـ CI/CD؟\n\n"
            "1. ما هو `versionCode` وما هو `versionName`؟\n   - **`versionCode`**: رقم صحيح موجب متزايد دائماً (`Int` مثل `1024`). يستخدمه نظام Android و Google Play لتحديد تسلسل التحديثات. **ممنوع تكرار نفس الرقم أو رفعه برقم أقل في المتجر**!\n   - **`versionName`**: النص الذي يراه المستخدم (`String` مثل `\"2.4.1\"`). يتبع عادة قواعد الترقيم الدلالي (**Semantic Versioning - SemVer**: `MAJOR.MINOR.PATCH`).\n\n"
            "2. أتمتة حساب `versionCode` دون تعديل يدوي:\n   - **الاعتماد على عدد الـ Git Commits**: حساب عدد الـ Commits في الـ Main branch عبر `git rev-list --count HEAD`. رقم متزايد حتمياً دائماً.\n   - **الاعتماد على معرّف بناء الـ CI/CD**: استخدام متغير بيئة الـ CI (مثل `GITHUB_RUN_NUMBER`).\n\n"
            "3. أتمتة سجلات التغييرات (Release Notes / Changelogs):\n   - حفظ ملفات التغييرات في مجلد منظم باللغات (`metadata/android/ar-SA/changelogs/{versionCode}.txt`).\n   - استخدام أدوات مثل **Fastlane Supply** أو **Gradle Play Publisher (GPP)** لقراءة ملفات الـ Changelogs ورفعها تلقائياً مع الـ AAB."
        ),
        "practical_walkthrough": (
            "حساب versionCode تلقائياً من Git وإعداد versionName وسجلات الإصدار في build.gradle.kts:\n"
            "```kotlin\n"
            "fun generateVersionCode(): Int {\n"
            "    // حساب إجمالي عدد الـ Commits في مستودع Git للحصول على رقم متزايد حتمياً:\n"
            "    return try {\n"
            "        val process = ProcessBuilder(\"git\", \"rev-list\", \"--count\", \"HEAD\").start()\n"
            "        process.inputStream.bufferedReader().readText().trim().toInt()\n"
            "    } catch (e: Exception) {\n"
            "        1 // قيمة افتراضية إذا كان مجلد الـ Git غير متاح\n"
            "    }\n"
            "}\n"
            "\n"
            "android {\n"
            "    defaultConfig {\n"
            "        // 1. versionCode محسوب آلياً في كل Build:\n"
            "        versionCode = generateVersionCode()\n"
            "        \n"
            "        // 2. versionName يتبع Semantic Versioning:\n"
            "        versionName = \"2.5.0\"\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Manage versionCode monotonically via CI build numbers or git commit counts (git rev-list --count HEAD), format versionName using Semantic Versioning (MAJOR.MINOR.PATCH), and automate localized release notes using Gradle Play Publisher or Fastlane changelog files matching the versionCode.",
        "best_answer": (
            "Automating versioning and release notes eliminates human deployment errors and prevents rejected Play Console uploads:\n\n"
            "1. **Deterministic `versionCode` Management**:\n"
            "   - Must strictly be a positive monotonically increasing integer (max 2,100,000,000). Google Play rejects any upload with a `versionCode` less than or equal to previous active builds.\n   - Best automated via Git commit depth (`git rev-list --count HEAD`) or CI build run counters (`GITHUB_RUN_NUMBER + OFFSET`). This guarantees that every PR merge produces a unique, incremented code without manual commit modifications.\n\n"
            "2. **Semantic `versionName` Modeling**:\n"
            "   - Follow Semantic Versioning: `MAJOR.MINOR.PATCH`. Defined in a central `version.properties` file or extracted from Git release tags (`git describe --tags`).\n\n"
            "3. **Automated Release Notes Deployment**:\n"
            "   - Maintain localized changelog text files under source control: `distribution/whatsnew/whatsnew-en-US` and `whatsnew-ar-SA`.\n   - In CI/CD, tools like **Gradle Play Publisher (GPP)** or **Fastlane Supply** bundle these release notes alongside the compiled AAB directly to Play Store tracks."
        ),
        "deep_answer": (
            "From an advanced multi-architecture and release pipeline perspective, versioning involves ABI offsets and track management:\n\n"
            "1. **ABI Version Code Offsets (For Split APKs)**: When distributing multiple APKs partitioned by ABI, each APK must have a distinct `versionCode`. Standard industry convention uses structured offsets: `64-bit ARM (prefix 2) -> 2001024`, `32-bit ARM (prefix 1) -> 1001024`. The 64-bit build must always have the higher `versionCode` so 64-bit devices prefer the 64-bit APK.\n\n"
            "2. **Continuous Deployment with Internal Test Tracks**: Configure CI to publish every successful main branch commit to Google Play Internal Testing Track using automated release tags. This allows QA and beta testers to receive updates within 15 minutes of code merge.\n\n"
            "3. **Version Catalog Integration**: Centralize app versioning metadata within `gradle/libs.versions.toml` or `build-logic` convention plugins to keep multi-module sample apps and release flavors synchronized."
        ),
        "follow_ups": [
            {
                "question": "What is the maximum integer limit for Android versionCode?",
                "answer": "2,100,000,000 (2.1 billion), which fits within a standard 32-bit signed integer."
            },
            {
                "question": "Why must a 64-bit APK have a higher versionCode than a 32-bit APK for the same app version?",
                "answer": "Android installs the compatible APK with the highest versionCode; a higher code ensures 64-bit devices install the optimized 64-bit binary."
            }
        ]
    },
    {
        "id": "BLD-14",
        "arabic_explanation": (
            "كيف تستكشف وتصلح أخطاء غياب مكتبات الـ Native (UnsatisfiedLinkError) ومشاكل عدم توافق معمارية المعالج (ABI Incompatibility)؟\n\n"
            "1. خطأ الانهيار الشهير (UnsatisfiedLinkError: dlopen failed):\n   - يحدث عندما يحاول التطبيق استدعاء `System.loadLibrary(\"crypto\")` أو تشغيل كود C++ عبر JNI، ولكنه لا يجد ملف `libcrypto.so` المخصص لمعمارية الهاتف الحالية.\n\n"
            "2. الكارثة الشائعة: الـ 32-bit vs 64-bit Mismatch (مشكلة الـ ABI غير المتناسقة):\n   - إذا استخدم تطبيقك مكتبتين:\n     * مكتبة A توفر كود لكل من: `arm64-v8a` و `armeabi-v7a`.\n     * مكتبة B توفر كود لـ `armeabi-v7a` فقط (لا تملك كود 64-bit)!\n   - **ماذا يفعل أندرويد على هاتف حديث (64-bit)**؟\n     * يرى النظام أن التطبيق يحتوي على مجلد `lib/arm64-v8a/`، فيقوم بتشغيل التطبيق في وضع 64-bit ويبحث عن جميع المكتبات داخل هذا المجلد فقط!\n     * عندما يحاول التطبيق تشغيل مكتبة B، لا يجدها في مجلد 64-bit، فينهار التطبيق فوراً برمي `UnsatisfiedLinkError`!\n\n"
            "3. خطوات التشخيص والحل:\n   - فحص الـ APK عبر **APK Analyzer**: فتح مجلد `lib/` والتأكد من أن كل ملف `.so` موجود في **جميع** مجلدات المعماريات بالتساوي.\n   - **الحل**: إما الحصول على نسخة 64-bit من المكتبة الناقصة، أو إجبار التطبيق على العمل في وضع 32-bit عبر تقييد الـ `ndk.abiFilters` على `armeabi-v7a` فقط."
        ),
        "practical_walkthrough": (
            "تشخيص محتويات الـ ABIs داخل الـ APK وحل مشكلة عدم تناسق المكتبات:\n"
            "```bash\n"
            "# 1. فحص ملفات الـ .so المضمنة في كل معمارية باستخدام unzip:\n"
            "unzip -l app-release.apk \"lib/*\"\n"
            "\n"
            "# النتيجة توضح وجود عدم تناسق (libfoo موجود في المعماريتين، بينما libbar ناقص في 64-bit!):\n"
            "# lib/arm64-v8a/libfoo.so\n"
            "# lib/armeabi-v7a/libfoo.so\n"
            "# lib/armeabi-v7a/libbar.so   <-- غائب في arm64-v8a!\n"
            "```\n\n"
            "```kotlin\n"
            "// 2. الحل المؤقت في build.gradle.kts إذا لم تتوفر نسخة 64-bit للمكتبة:\n"
            "android {\n"
            "    defaultConfig {\n"
            "        ndk {\n"
            "            // إجبار التطبيق بالكامل على العمل في وضع 32-bit لحين ترقية المكتبة:\n"
            "            abiFilters.clear()\n"
            "            abiFilters.add(\"armeabi-v7a\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Diagnose UnsatisfiedLinkError by inspecting the APK's lib/ directory with APK Analyzer to detect ABI mismatches. If one library includes 64-bit (arm64-v8a) while another only provides 32-bit (armeabi-v7a), the 64-bit OS runs in 64-bit mode and crashes when looking for the missing library. Resolve by adding 64-bit binaries or filtering to 32-bit.",
        "best_answer": (
            "`java.lang.UnsatisfiedLinkError` occurs when the Android dynamic linker (`dlopen`) fails to locate or load a required native shared object (`.so`) for the current CPU architecture:\n\n"
            "1. **The 32-bit vs. 64-bit Asymmetry Trap**:\n"
            "   - If any third-party SDK includes a 64-bit binary in `lib/arm64-v8a/`, the Android OS launches the app inside a 64-bit Zygote process.\n   - Once running in 64-bit mode, the OS dynamic linker looks **strictly** inside `lib/arm64-v8a/` and will never fall back to 32-bit folders.\n   - If a second library in your project only supplied 32-bit `armeabi-v7a` binaries, calls to load that library crash immediately with `UnsatisfiedLinkError: dlopen failed: library not found`.\n\n"
            "2. **Inspection & Diagnosis**:\n"
            "   - Open the compiled APK in Android Studio's **APK Analyzer** or execute `unzip -l app.apk \"lib/*\"`.\n   - Verify that the exact same set of `.so` library names exists across all supported ABI folders.\n\n"
            "3. **Resolution Strategies**:\n"
            "   - **Preferred**: Procure or compile 64-bit `.so` binaries for the missing dependencies (mandatory for Google Play compliance).\n   - **Fallback**: Enforce uniform 32-bit packaging via `ndk.abiFilters.add(\"armeabi-v7a\")` until 64-bit dependencies are available."
        ),
        "deep_answer": (
            "From an OS loader and systems architecture perspective, native linking errors can also stem from missing transitive dependencies and text relocations:\n\n"
            "1. **Missing Transitive Dependencies (`NEEDED` ELF headers)**: A `.so` file often depends on secondary libraries (e.g. `libnative.so` depends on `libcrypto.so`). If `libcrypto.so` is missing from the APK or stripped by packaging excludes, `dlopen(\"libnative.so\")` fails with `library \"libcrypto.so\" not found`. Inspect ELF dependencies using `readelf -d libnative.so | grep NEEDED`.\n\n"
            "2. **Text Relocations (API 23+)**: Since Android 6.0, Android blocks libraries with text relocations (`W^X` memory protection). Libraries compiled with legacy NDK toolchains without `-fPIC` throw `dlopen failed: has text relocations` and crash on modern devices.\n\n"
            "3. **Automated ABI Verification in CI**: Add an automated assertion test in CI that unpacks the built APK and asserts that the file lists under `lib/arm64-v8a/` and `lib/armeabi-v7a/` are identical, failing the build on asymmetric native packaging."
        ),
        "follow_ups": [
            {
                "question": "What does readelf -d libfoo.so show?",
                "answer": "It displays the dynamic section of the ELF binary, including shared library dependencies listed in NEEDED tags."
            },
            {
                "question": "Does Google Play allow uploading 32-bit only APKs today?",
                "answer": "No; since August 2019, Google Play mandates 64-bit (arm64-v8a) support for all apps bundling native code."
            }
        ]
    }
]


def update_bld_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in BLD_08_14:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions BLD-08 to BLD-14. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_bld_data()
