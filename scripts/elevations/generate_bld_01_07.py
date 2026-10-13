#!/usr/bin/env python3
"""Generator for BLD-01 through BLD-07 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "bld.json"

BLD_01_07 = [
    {
        "id": "BLD-01",
        "arabic_explanation": (
            "ما هي الأدوار المحددة والمفصولة لكل من Gradle، و Android Gradle Plugin (AGP)، و Kotlin Compiler (K2/kotlinc) في عملية بناء التطبيق؟\n\n"
            "1. محرك البناء العام (Gradle Core Engine):\n   - هو **General-Purpose Build Automation Tool**. لا يعرف أي شيء عن هواتف أندرويد أو ملفات APK أو DEX!\n   - مسؤوليته: إدارة دورة حياة البناء (Configuration, Execution, Initialization)، حل شجرة التبعيات (Dependency Resolution)، وإدارة الـ Task Graph والـ Caching والـ Parallel Execution.\n\n"
            "2. إضافة أندرويد الرسمية (Android Gradle Plugin - AGP):\n   - هو **Plugin** يتم تطبيقه فوق Gradle (`com.android.application` أو `com.android.library`).\n   - يعلم Gradle كيف يبني تطبيقات أندرويد: يضيف Android DSL (`android { compileSdk, defaultConfig, ... }`)، يدمج الموارد عبر AAPT2، يدمج ملفات الـ AndroidManifest.xml، يحول كود الـ Java/Kotlin بايت كود إلى DEX bytecode عبر D8/R8، ويوقع ويحزم ملفات APK و AAB.\n\n"
            "3. مترجم لغة كوتلن (Kotlin Compiler - kotlinc / K2):\n   - يترجم كود Kotlin المصدري (`.kt`) إلى Java Bytecode (`.class`).\n   - في الإصدارات الحديثة، يدعم مترجم K2 Frontend السريع ومكونات Kotlin Symbol Processing (KSP) لمعالجة الـ Annotations دون المرور بـ Java Stubs البطيئة."
        ),
        "practical_walkthrough": (
            "فهم كيفية تكوين AGP و Kotlin Compiler والتحكم في مهام البناء في build.gradle.kts:\n"
            "```kotlin\n"
            "// 1. ربط الـ Plugins في root أو module build.gradle.kts:\n"
            "plugins {\n"
            "    alias(libs.plugins.android.application) // يضيف AGP ومهام تجميع أندرويد\n"
            "    alias(libs.plugins.kotlin.android)     // يربط kotlinc لتحويل .kt إلى .class bytecode\n"
            "}\n"
            "\n"
            "// 2. إعدادات AGP التي تتحكم في دمج الموارد وإصدارات النظام المستهدفة:\n"
            "android {\n"
            "    namespace = \"com.example.enterprise\"\n"
            "    compileSdk = 35\n"
            "\n"
            "    defaultConfig {\n"
            "        applicationId = \"com.example.enterprise\"\n"
            "        minSdk = 26\n"
            "        targetSdk = 35\n"
            "        versionCode = 100\n"
            "        versionName = \"1.0.0\"\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. إعدادات Kotlin Compiler لتفعيل تحسينات الأداء واللغة:\n"
            "kotlin {\n"
            "    jvmToolchain(17) // يضبط إصدار JDK الموحد لجميع المترجمين\n"
            "    compilerOptions {\n"
            "        freeCompilerArgs.addAll(\"-opt-in=kotlinx.coroutines.ExperimentalCoroutinesApi\")\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Gradle is the generic build automation engine managing task graphs and dependencies. AGP extends Gradle with Android-specific tasks like AAPT2 resource merging, manifest blending, and DEX compilation. The Kotlin compiler (kotlinc) compiles Kotlin source files into JVM bytecode before AGP's D8/R8 converts them into Android DEX format.",
        "best_answer": (
            "The Android build pipeline is an orchestrated pipeline dividing responsibilities across three distinct tools:\n\n"
            "1. **Gradle (Build Orchestrator)**:\n"
            "   - A general-purpose build automation engine. It knows nothing about Android APIs. It evaluates settings and build scripts, resolves remote Maven dependencies, constructs the Directed Acyclic Graph (DAG) of tasks, and enforces execution caching and parallelization.\n\n"
            "2. **Android Gradle Plugin / AGP (Android Domain Engine)**:\n"
            "   - Developed by Google to extend Gradle for Android. It registers custom tasks: running AAPT2 to compile XML layouts and resources into `resources.ap_`, executing Manifest Merger, running D8/R8 to transform JVM `.class` bytecode into Dalvik Executable (`.dex`) files, and packaging native `.so` libraries into signed APK/AAB artifacts.\n\n"
            "3. **Kotlin Compiler / kotlinc (Language Frontend)**:\n"
            "   - Compiles Kotlin `.kt` source files into standard JVM `.class` bytecode. In modern AGP builds with K2 and KSP, it runs concurrently with Java compilation, emitting intermediate bytecodes ready for AGP's desugaring and R8 shrinking pipeline."
        ),
        "deep_answer": (
            "From a low-level build systems perspective, tracing the precise task boundary pipeline illuminates optimization opportunities:\n\n"
            "1. **Task Execution Pipeline Sequence**: Source generation -> `compileDebugKotlin` (kotlinc emits `.class`) -> `compileDebugJavaWithJavac` -> Class merging -> `mergeDebugResources` (AAPT2) -> `processDebugManifest` -> `minifyDebugWithR8` (shrinks, optimizes, and dexes into `classes.dex`) -> `packageDebug` (assembles unsigned ZIP) -> `signDebugBundle`.\n\n"
            "2. **Desugaring in D8/R8**: Modern Java 8/11/17 language APIs (e.g. `java.time`, streams) used in Kotlin or Java source are rewritten by AGP's D8 desugaring engine into backward-compatible synthetic bytecode that runs safely on older Android devices down to API 21.\n\n"
            "3. **K2 Compiler Upgrades**: Kotlin 2.0 (K2) completely replaces the compiler frontend with a unified semantic analyzer. It optimizes build compilation time by up to 2x and standardizes type inference across multiplatform targets."
        ),
        "follow_ups": [
            {
                "question": "What is AAPT2 and what is its role in AGP?",
                "answer": "Android Asset Packaging Tool 2; it compiles XML and resource files into binary formats (.arsc) and packages them into the final Android archive."
            },
            {
                "question": "What is D8 compared to R8?",
                "answer": "D8 is AGP's standalone DEX compiler converting .class files to .dex; R8 is a combined shrinking, optimizing, obfuscating, and dexing engine."
            }
        ]
    },
    {
        "id": "BLD-02",
        "arabic_explanation": (
            "ما هي الـ Build Types، والـ Product Flavors، والـ Build Variants، والـ Source Sets في أندرويد وكيف تتكامل معاً؟\n\n"
            "1. أنواع البناء (Build Types):\n   - تحدد **كيفية بناء التطبيق وتجهيزه تقنياً** (Build & Packaging Characteristics).\n   - أشهر نوعين هما: `debug` (مفتوح للـ Debugging، غير مشوش، موقع بمفتاح تجريبي) و `release` (مغلق، مشوش عبر R8، مصغر الحجم، موقع بمفتاح إنتاج رسمي).\n\n"
            "2. نكهات المنتج (Product Flavors):\n   - تحدد **الميزات والخصائص التجارية الموجهة للمستخدم أو البيئة** (Product Features & Branding).\n   - أمثلة: `free` مقابل `paid`، أو البيئات: `dev`, `staging`, `prod` (مع تغيير الـ Base URL والـ Application ID).\n   - تُجمع النكهات تحت أبعاد صريحة (`flavorDimensions = listOf(\"environment\", \"tier\")`).\n\n"
            "3. متغيرات البناء (Build Variants):\n   - هي **حاصل الضرب الديكارتي (Cartesian Product)** لكل Flavor مع كل Build Type.\n   - مثال: نكهتان (`free`, `paid`) × نوعان (`debug`, `release`) = 4 Variants:\n     `freeDebug`, `freeRelease`, `paidDebug`, `paidRelease`.\n\n"
            "4. مجموعات المصادر (Source Sets):\n   - مجلدات الكود والموارد المخصصة لكل Variant.\n   - الأولوية في دمج الموارد والكود: `src/freeDebug/` تتفوق على `src/free/` التي تتفوق على `src/debug/` التي تتفوق على الكود المشترك في `src/main/`."
        ),
        "practical_walkthrough": (
            "تكوين Flavors و Build Types وأبعاد النكهات وتخصيص الـ Source Sets في build.gradle.kts:\n"
            "```kotlin\n"
            "android {\n"
            "    flavorDimensions += listOf(\"environment\", \"monetization\")\n"
            "\n"
            "    productFlavors {\n"
            "        create(\"dev\") {\n"
            "            dimension = \"environment\"\n"
            "            applicationIdSuffix = \".dev\"\n"
            "            buildConfigField(\"String\", \"BASE_URL\", \"\\\"https://dev.api.example.com\\\"\")\n"
            "        }\n"
            "        create(\"prod\") {\n"
            "            dimension = \"environment\"\n"
            "            buildConfigField(\"String\", \"BASE_URL\", \"\\\"https://api.example.com\\\"\")\n"
            "        }\n"
            "        create(\"free\") {\n"
            "            dimension = \"monetization\"\n"
            "        }\n"
            "        create(\"pro\") {\n"
            "            dimension = \"monetization\"\n"
            "            applicationIdSuffix = \".pro\"\n"
            "        }\n"
            "    }\n"
            "\n"
            "    buildTypes {\n"
            "        debug {\n"
            "            isDebuggable = true\n"
            "            applicationIdSuffix = \".debug\"\n"
            "        }\n"
            "        release {\n"
            "            isMinifyEnabled = true\n"
            "            isShrinkResources = true\n"
            "            proguardFiles(getDefaultProguardFile(\"proguard-android-optimize.txt\"), \"proguard-rules.pro\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Build types configure packaging and debugging attributes (debug vs release), product flavors configure feature sets and branding (free vs paid), build variants are the Cartesian product of both (e.g. freeRelease), and source sets provide variant-specific code and resource overlays resolved hierarchically over src/main.",
        "best_answer": (
            "The Android build variant matrix organizes compilation targets into distinct operational axes:\n\n"
            "1. **Build Types (How it is built)**:\n"
            "   - Dictate technical packaging configurations: debuggability (`isDebuggable`), code optimization and obfuscation (`isMinifyEnabled`), resource shrinking, signing configurations, and symbols stripping.\n\n"
            "2. **Product Flavors (What is built)**:\n"
            "   - Dictate business and environment differentiation. Grouped by `flavorDimensions` (e.g., `environment` for dev/staging/prod; `distribution` for gms/hms). They configure `applicationIdSuffix`, specific `buildConfigField` parameters, and feature toggles.\n\n"
            "3. **Build Variants (The Output Permutations)**:\n"
            "   - The Cartesian product of every dimension flavor multiplied by build types. For example, 2 environments (`dev`, `prod`) × 2 types (`debug`, `release`) yields 4 runnable variants: `devDebug`, `devRelease`, `prodDebug`, `prodRelease`.\n\n"
            "4. **Source Sets (Resource & Code Overlays)**:\n"
            "   - Dedicated directory structures (e.g., `src/devDebug/`, `src/dev/`, `src/main/`). The Gradle resource merger merges files hierarchically: variant-specific assets override flavor-specific assets, which in turn override `src/main/` defaults."
        ),
        "deep_answer": (
            "From an enterprise release and build-velocity viewpoint, managing the variant matrix requires defensive configuration:\n\n"
            "1. **Variant Filter Optimization**: Creating 3 flavor dimensions with 3 flavors each generates $3 \\times 3 \\times 2 = 18$ variants. Gradle evaluates tasks for every variant, blowing up configuration time. Filter out useless permutations using `variantFilter { if (name == \"demoStagingRelease\") setIgnore(true) }` to drastically reduce sync and build times.\n\n"
            "2. **Code Discrepancies Across Source Sets**: While resources merge automatically, Kotlin/Java source files in source sets do not merge; they conflict. If a class `Logger.kt` is placed in `src/debug/`, it cannot exist in `src/main/` or a duplicate class compilation error occurs. Keep `src/main/` clean and use interfaces with dependency injection rather than duplicating classes across variant source sets.\n\n"
            "3. **Dynamic Manifest Placeholders**: Inject variant-specific deep link schemes, authorities, and API keys using `manifestPlaceholders = mapOf(\"authDomain\" to \"dev.auth.com\")` rather than maintaining separate `AndroidManifest.xml` files per flavor."
        ),
        "follow_ups": [
            {
                "question": "Can two different flavors define different applicationId values?",
                "answer": "Yes, either by setting distinct applicationId values or using applicationIdSuffix (e.g., .dev) to allow installing both side-by-side on one device."
            },
            {
                "question": "What happens if a string resource with the same key exists in both src/main and src/flavor/res?",
                "answer": "The flavor-specific resource overrides the main resource during the AAPT2 resource merging phase."
            }
        ]
    },
    {
        "id": "BLD-03",
        "arabic_explanation": (
            "قارن بين ملف الـ APK وملف الـ Android App Bundle (AAB)، ولماذا أصبح الـ AAB إلزامياً للنشر في Google Play؟\n\n"
            "1. ما هو ملف الـ APK (Android Package)؟\n   - هو الأرشيف التقليدي القابل للتثبيت مباشرة على أجهزة أندرويد (`.apk`).\n   - **مشكلته التاريخية (Fat APK)**: يحتوي على كل لغات العالم (ar, en, fr, zh)، وكل كثافات الشاشات (mdpi, hdpi, xhdpi, xxxhdpi)، وكل مكتبات الـ Native ABIs (arm64-v8a, armeabi-v7a, x86_64).\n   - المستخدم الذي يملك هاتف ARM64 بشاشة xhdpi يُجبر على تنزيل حجم هائل من الملفات والصور التي لن يستخدمها جهازه أبداً!\n\n"
            "2. ما هو ملف الـ AAB (Android App Bundle)؟\n   - هو صيغة نشر مضغوطة (`.aab`) تُرفع إلى Google Play Console وتتضمن كود وموارد التطبيق بالكامل مقسمة إلى موديولات.\n   - **لا يُثبت مباشرة على الهاتف**؛ بل يستخدم Google Play أداة `bundletool` لإنشاء **Split APKs** مخصصة لكل هاتف على حدة:\n     * **Base APK**: يحتوي على الكود المشترك والموارد الأساسية.\n     * **Configuration APKs**: يحتوي فقط على لغة جهاز المستخدم، كثافة شاشته، ومعمارية معالجه (CPU ABI).\n   - النتيجة: تقليص حجم التحميل بنسبة تصل إلى 35%!\n\n"
            "3. الميزات المتقدمة للـ AAB:\n   - **Dynamic Feature Delivery (Play Feature Delivery)**: إمكانية تنزيل ميزات التطبيق عند الطلب (On-Demand) دون تضمينها في التثبيت الأولي.\n   - **Play Asset Delivery**: لألعاب وتطبيقات الوسائط لتحميل الملفات الضخمة تلقائياً."
        ),
        "practical_walkthrough": (
            "توليد واختبار Split APKs محلياً من ملف AAB باستخدام أداة bundletool قبل النشر:\n"
            "```bash\n"
            "# 1. بناء ملف AAB في بيئة Release عبر Gradle:\n"
            "./gradlew :app:bundleRelease\n"
            "\n"
            "# 2. استخدام أداة bundletool الرسمية من Google لتوليد Split APKs مخصصة للهاتف المتصل حالياً:\n"
            "bundletool build-apks \\\n"
            "  --bundle=app/build/outputs/bundle/release/app-release.aab \\\n"
            "  --output=app-release.apks \\\n"
            "  --connected-device \\\n"
            "  --ks=release.keystore \\\n"
            "  --ks-key-alias=release_key\n"
            "\n"
            "# 3. تثبيت الـ Split APKs الناتجة على الهاتف المتصل للتأكد من خلوها من أي مشاكل:\n"
            "bundletool install-apks --apks=app-release.apks\n"
            "```"
        ),
        "quick_answer": "An APK is a monolithic, directly installable package containing all languages, screen densities, and CPU ABIs. An AAB is an upload format containing modular app components from which Google Play dynamically generates optimized Split APKs tailored to each user's device specs, reducing download size by up to 35%.",
        "best_answer": (
            "Comparing APK and Android App Bundle (AAB) highlights a shift from fat client binaries to dynamic server-side artifact delivery:\n\n"
            "1. **Monolithic APK (Android Package)**:\n"
            "   - Directly installable via `adb install`. Traditionally packages all density assets (hdpi to xxxhdpi), localized string tables, and native CPU architectures (`armeabi-v7a`, `arm64-v8a`, `x86_64`). This bloats download sizes and wastes user bandwidth.\n\n"
            "2. **Android App Bundle (AAB)**:\n"
            "   - Google Play's mandatory publishing format (since August 2021). Developers upload a single `.aab` file containing compiled DEX, compiled resources, and modular splits.\n   - Google Play uses `bundletool` server-side to generate optimized **Split APKs**: a small Base APK accompanied by targeted configuration splits matching only the user's specific ABI, screen density, and device language.\n\n"
            "3. **Dynamic Delivery Capabilities**:\n"
            "   - AAB enables **Play Feature Delivery** (downloading optional modules on-demand or based on conditional hardware capabilities) and **Play Asset Delivery** for multi-gigabyte media packages, avoiding external downloader architectures."
        ),
        "deep_answer": (
            "From a release engineering perspective, adopting AAB introduces cryptographic and QA testing considerations:\n\n"
            "1. **Play App Signing Prerequisite**: Publishing with AAB mandates Google Play App Signing. Developers sign the AAB using an Upload Key, while Google manages the master App Signing Key inside Google's secure infrastructure to sign generated Split APKs. If the upload key is lost, Google can reset it without abandoning the application ID.\n\n"
            "2. **Local QA Verification with bundletool**: Because `.aab` files cannot be installed via `adb install` directly, QA teams must use Google's `bundletool` CLI. Generate device-spec JSON files (`bundletool get-device-spec --output=device.json`), produce the APKS set, and test split APK installation across local test devices.\n\n"
            "3. **Language Switching In-App Pitfall**: On older Android versions, Split APKs only bundle the system language selected at install. If an app provides an in-app language picker to switch to French, but French strings were stripped out by dynamic delivery, the app crashes or shows missing strings. Apps must use AndroidX `PlayCore` / `SplitInstallManager` to request deferred language splits."
        ),
        "follow_ups": [
            {
                "question": "Can an AAB be installed directly on a device without bundletool or Google Play?",
                "answer": "No; Android OS package managers understand only APK files; AAB must be transformed into APKs by bundletool or an app store."
            },
            {
                "question": "What is the maximum download size for the base APK generated from an AAB on Google Play?",
                "answer": "Google Play allows up to 200MB compressed download size for generated base APKs; larger assets must use Play Asset Delivery."
            }
        ]
    },
    {
        "id": "BLD-04",
        "arabic_explanation": (
            "ما هو الفرق الجوهري بين التوقيع التجريبي (Debug Signing) والتوقيع الرسمي (Release Signing) في أندرويد، وكيف تحمي مفاتيح الإنتاج؟\n\n"
            "1. ما هو التوقيع الرقمي للـ APK/AAB؟\n   - نظام أندرويد لا يقبل تثبيت أي تطبيق غير موقع رقمياً (Cryptographically Signed).\n   - التوقيع يضمن أمرين: **هوية المطور (Author Identity)** و**سلامة الكود من التعديل (Integrity)**. لا يمكن لأي تطبيق آخر تحديث تطبيقك إلا إذا كان موقعاً بنفس الشهادة الرقمية تماماً.\n\n"
            "2. التوقيع التجريبي (Debug Signing):\n   - يتم تلقائياً باستخدام ملف `debug.keystore` الافتراضي الذي ينشئه أندرويد ستوديو في مجلد المستخدم (`~/.android/debug.keystore`).\n   - كلمة المرور والمفتاح معروفان وثابتان عالمياً (`android` / `androiddebugkey`).\n   - **غير آمن ومكشوف للجميع**؛ يُستخدم فقط للتطوير والاختبار المحلي.\n\n"
            "3. التوقيع الرسمي (Release Signing):\n   - يعتمد على Keystore خاص مشفر بمفتاح تشفير قوي (2048-bit RSA أو 256-bit EC) تم إنشاؤه بواسطة فريق الأمان.\n   - **قاعدة أمنية صارمة**: **ممنوع كتابة كلمات مرور الـ Keystore أو مسار المفتاح كنص صريح في ملف build.gradle.kts** أو رفعه إلى Git Repository!\n   - يجب تمرير كلمات المرور والمسارات عبر Environment Variables مشفرة في خوادم الـ CI/CD (GitHub Secrets) أو قراءتها من أداة إدارة أسرار موثوقة (HashiCorp Vault / Google Secret Manager)."
        ),
        "practical_walkthrough": (
            "تكوين Release Signing في Gradle باستخدام Environment Variables وتجنب كتابة الأسرار في الكود:\n"
            "```kotlin\n"
            "android {\n"
            "    signingConfigs {\n"
            "        create(\"release\") {\n"
            "            // قراءة مسار المفتاح وكلمات المرور من متغيرات البيئة المشفرة في CI/CD\n"
            "            storeFile = file(System.getenv(\"KEYSTORE_FILE_PATH\") ?: \"keystore/dummy.jks\")\n"
            "            storePassword = System.getenv(\"KEYSTORE_PASSWORD\")\n"
            "            keyAlias = System.getenv(\"KEY_ALIAS\")\n"
            "            keyPassword = System.getenv(\"KEY_PASSWORD\")\n"
            "            \n"
            "            // تفعيل أحدث إصدارات التوقيع الرقمي المدعومة عتادياً:\n"
            "            enableV1Signing = true // JAR Signature للأجهزة القديمة\n"
            "            enableV2Signing = true // APK Signature Scheme v2 (كامل الأرشيف)\n"
            "            enableV3Signing = true // APK Signature Scheme v3 (يدعم تدوير المفاتيح)\n"
            "            enableV4Signing = true // APK Signature Scheme v4 (تدفق التثبيت السريع عبر ADB)\n"
            "        }\n"
            "    }\n"
            "\n"
            "    buildTypes {\n"
            "        release {\n"
            "            signingConfig = signingConfigs.getByName(\"release\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Debug signing uses a standard insecure local keystore with public credentials (android/androiddebugkey) for local development. Release signing uses a secure private cryptographic key that must never be committed to source control, managed via CI/CD environment variables or Play App Signing.",
        "best_answer": (
            "Cryptographic code signing establishes developer identity and artifact immutability on Android:\n\n"
            "1. **Debug Signing**:\n"
            "   - Uses a default auto-generated keystore (`~/.android/debug.keystore`) with well-known public credentials (`android` password and `androiddebugkey` alias). Intended strictly for local development and USB debugging.\n   - Debug signatures are non-unique and must never be permitted in production, as third parties could mimic the identity or claim debug-level permissions.\n\n"
            "2. **Release Signing**:\n"
            "   - Uses an enterprise cryptographic keystore. Guarantees that app updates come authentically from the original developer. Upgrading an app fails with `INSTALL_FAILED_UPDATE_INCOMPATIBLE` if the signing certificate does not match the installed version.\n\n"
            "3. **Secrets Hygiene in CI/CD**:\n"
            "   - Never commit `.keystore` / `.jks` files or passwords into Git repositories. Inject keystores as Base64-encoded strings and passwords via encrypted environment variables inside secure CI/CD runners (GitHub Actions Secrets).\n\n"
            "4. **APK Signature Schemes (v1 through v4)**:\n"
            "   - Enable modern signing schemes: v1 (JAR signing), v2 (whole-file hash verification), v3 (cryptographic key rotation support), and v4 (supporting streaming installations over ADB on Android 11+)."
        ),
        "deep_answer": (
            "From an operational security perspective, Google Play App Signing decouples development risk from master distribution keys:\n\n"
            "1. **The Play App Signing Architecture**: Traditionally, losing an app's private release key meant the developer could never update the application again—abandoning millions of active users. With Play App Signing, developers sign artifacts using a distinct **Upload Key**. Google strips the upload signature, validates it, and re-signs the APKs using the master **App Signing Key** locked in Google Cloud KMS. If an upload key is compromised or lost, Google resets it via developer console support without disrupting existing users.\n\n"
            "2. **Third-Party API Binding (SHA-1 / SHA-256 Fingerprints)**: APIs like Google Sign-In, Firebase Auth, and Google Maps validate requests using the signing certificate's SHA-1 fingerprint. When using Play App Signing, developers must register the **Play App Signing Key's SHA-1** in Google Cloud Console, not just their local upload key SHA-1, or third-party authentication will fail in production releases.\n\n"
            "3. **Key Rotation via Scheme v3**: APK Signature Scheme v3 enables key rotation by embedding a cryptographic proof-of-rotation lineage attribute in the signing block, allowing applications to migrate to stronger keys over time."
        ),
        "follow_ups": [
            {
                "question": "What happens if a user tries to install an update signed with a different key than the installed app?",
                "answer": "Android OS package manager rejects the update immediately with INSTALL_FAILED_UPDATE_INCOMPATIBLE, protecting users from malicious hijacking."
            },
            {
                "question": "Why is APK Signature Scheme v2 faster to verify than v1?",
                "answer": "v1 verifies every individual zip entry individually; v2 verifies a single cryptographic hash across the entire binary file structure, accelerating install times."
            }
        ]
    },
    {
        "id": "BLD-05",
        "arabic_explanation": (
            "ما هي الـ Build Cache، والـ Configuration Cache، والـ Incremental Compilation في Gradle، وكيف تضاعف سرعة البناء؟\n\n"
            "1. الـ Incremental Compilation (التجميع التزايدي):\n   - عند تعديل سطر واحد في كلاس، لا داعي لإعادة تجميع المشروع بأكمله!\n   - المترجم يفحص ملفات الإدخال (Inputs)، ويعيد تجميع الكلاسات المعدلة والكلاسات التي تعتمد عليها مباشرة فقط (ABI changes)، متخطياً باقي الكلاسات.\n\n"
            "2. الـ Build Cache (ذاكرة تخزين مخرجات المهام):\n   - يقوم بحفظ مخرجات الـ Tasks في كاش محلي أو عن بُعد (Remote Cache) بناءً على بصمة تشفيرية (Hash) لمدخلات المهمة.\n   - إذا طلبت من Gradle تشغيل مهمة (مثل `compileReleaseKotlin`) وكانت نفس المدخلات قد تم تجميعها سابقاً (على جهازك أو على سيرفر الـ CI)، يقوم Gradle بتخطي التنفيذ فوراً واستعادة المخرجات (`FROM-CACHE`) في أجزاء من الثانية!\n\n"
            "3. الـ Configuration Cache (كاش مرحلة الإعداد):\n   - مرحلة الـ Configuration في Gradle تقوم بقراءة كل ملفات `build.gradle.kts` وبناء الـ Task Graph، وهذا يستغرق 10-30 ثانية في المشاريع الضخمة حتى قبل بدء البناء!\n   - الـ Configuration Cache يقوم بحفظ الـ Task Graph بالكامل على القرص؛ في المرات التالية، يتخطى Gradle مرحلة الـ Configuration ويبدأ تنفيذ المهام فوراً (`Configuration cache entry reused`)."
        ),
        "practical_walkthrough": (
            "تفعيل الـ Configuration Cache والـ Build Cache وتحسين أداء Gradle في gradle.properties:\n"
            "```properties\n"
            "# 1. تفعيل الـ Configuration Cache لتخطي مرحلة تقييم ملفات Gradle:\n"
            "org.gradle.configuration-cache=true\n"
            "\n"
            "# 2. تفعيل الـ Build Cache المحلي والمشترك:\n"
            "org.gradle.caching=true\n"
            "\n"
            "# 3. تفعيل المعالجة المتوازية للمشاريع المستقلة في وقت واحد:\n"
            "org.gradle.parallel=true\n"
            "\n"
            "# 4. زيادة حجم ذاكرة الـ JVM المخصصة لـ Gradle Daemon وتسريع جمع المهملات:\n"
            "org.gradle.jvmargs=-Xmx6g -XX:+UseParallelGC -Dfile.encoding=UTF-8\n"
            "\n"
            "# 5. تفعيل مراقبة نظام الملفات لتجنب إعادة فحص الملفات غير المعدلة:\n"
            "org.gradle.vfs.watch=true\n"
            "```"
        ),
        "quick_answer": "Incremental compilation recompiles only modified source files and their dependents. Build cache stores and reuses task outputs locally or across CI based on input hashes. Configuration cache serializes the Gradle task graph to disk, skipping the entire project configuration phase on subsequent builds.",
        "best_answer": (
            "Optimizing Gradle performance relies on understanding the distinct layers of build caching:\n\n"
            "1. **Incremental Compilation**:\n"
            "   - Operates within a single compiler task (e.g. `compileKotlin`). Analyzes source file change sets (diffs). If a private method body is modified without changing public ABI signatures, only that file recompiles, sparing dependent modules from recompilation.\n\n"
            "2. **Build Cache (`org.gradle.caching=true`)**:\n"
            "   - Caches the physical output artifacts of entire Gradle tasks. Generates a composite SHA-256 hash across task inputs (source files, compiler arguments, dependencies). If an identical hash is found in the local cache or remote CI cache, Gradle skips task execution entirely and displays `FROM-CACHE`.\n\n"
            "3. **Configuration Cache (`org.gradle.configuration-cache=true`)**:\n"
            "   - Caches the output of Gradle's Configuration phase. Evaluating dozens of `build.gradle.kts` files to construct the task execution graph often takes 15–30 seconds. Configuration caching serializes this execution graph to disk, executing directly on subsequent runs."
        ),
        "deep_answer": (
            "From an advanced build infrastructure engineering viewpoint, caching requires strict hygiene to avoid cache invalidation:\n\n"
            "1. **Configuration Cache Invalidation Hazards**: Custom tasks or plugins that access the `Project` instance during the execution phase, read environment variables dynamically without `providers.environmentVariable()`, or inspect system timestamps break Configuration Caching. Audit builds with `./gradlew build --configuration-cache-problems=warn`.\n\n"
            "2. **Cache Key Determinism & Non-Hermetic Builds**: Build caching fails if task inputs contain non-deterministic data. A common mistake is injecting current timestamps (`System.currentTimeMillis()`) into `BuildConfig.BUILD_TIME`. This changes input hashes on every execution, completely blowing up remote and local build caching.\n\n"
            "3. **Remote Build Cache Strategy in CI**: Configure CI pipelines to populate a centralized HTTP build cache (e.g., Gradle Enterprise or self-hosted Docker cache) on every merged PR. Developers pulling the latest main branch download precompiled binaries, turning 15-minute builds into 45-second cache fetches."
        ),
        "follow_ups": [
            {
                "question": "What is UP-TO-DATE vs FROM-CACHE in Gradle task execution?",
                "answer": "UP-TO-DATE means task inputs did not change since the last local run in the current workspace; FROM-CACHE means outputs were loaded from the local or remote build cache."
            },
            {
                "question": "Why does injecting dynamic timestamps in BuildConfig break build caching?",
                "answer": "Because the timestamp alters the compiler input arguments on every run, changing the task input hash and forcing a full recompilation."
            }
        ]
    },
    {
        "id": "BLD-06",
        "arabic_explanation": (
            "ما هو R8، وما هي الفروق المحددة بين الـ Shrinking، والـ Optimization، والـ Obfuscation، والـ Dexing؟\n\n"
            "1. ما هو R8؟\n   - هو محرك تحسين وتحويل الكود المدمج في AGP والذي حل محل ProGuard و D8.\n   - يدمج أربع عمليات رئيسية في خطوة معالجة واحدة فائقة السرعة لتحويل الـ Java Bytecode إلى Dalvik Bytecode (`classes.dex`).\n\n"
            "2. العمليات الأربع الرئيسية في R8:\n   - **1. تقليص الكود والموارد (Code & Resource Shrinking)**: يفحص الكود انطلاقاً من نقاط الدخول (Entry Points) ويحذف أي كلاسات أو دوال أو موارد (`res/`) غير مستخدمة (Dead Code Elimination)، مما يقلص حجم الـ APK بشكل ملحوظ.\n   - **2. تحسين الكود (Code Optimization)**: يعيد هيكلة الكود لتسريع تنفيذه: دمج الدوال الصغيرة (Method Inlining)، إزالة الفئات المغلفة غير الضرورية (Class Inlining)، حذف الفحوصات المنطقية الميتة (Dead Branches)، وتبسيط استدعاءات الـ Enums.\n   - **3. التشويش البرمجي (Obfuscation)**: يعيد تسمية الكلاسات والدوال والمتغيرات إلى أسماء مبهمة وقصيرة (`a`, `b.c()`) لتقليص حجم ملفات الـ DEX وتصعيب الهندسة العكسية.\n   - **4. التحويل إلى DEX (Dexing)**: تحويل كود JVM Bytecode النهائي إلى Dalvik Executable Bytecode المتوافق مع بيئة تشغيل أندرويد (ART).\n\n"
            "3. ملف التعيين (mapping.txt):\n   - ينتجه R8 أثناء التشويش ويحتوي على خريطة مطابقة الأسماء الأصلية بالأسماء المشوشة. **بدونه يستحيل فك تشفير وفهم تقارير الانهيارات (Stack Traces) في الإنتاج**!"
        ),
        "practical_walkthrough": (
            "تفعيل وتحسين R8 في build.gradle.kts مع الاحتفاظ بنماذج البيانات وحذف السجلات:\n"
            "```kotlin\n"
            "android {\n"
            "    buildTypes {\n"
            "        release {\n"
            "            // 1. تفعيل تقليص الكود والتشويش والتحسين عبر R8:\n"
            "            isMinifyEnabled = true\n"
            "            \n"
            "            // 2. تفعيل حذف الموارد والملفات غير المستخدمة في res/:\n"
            "            isShrinkResources = true\n"
            "            \n"
            "            // 3. تطبيق القواعد الافتراضية مع قواعد المشروع الخاصة:\n"
            "            proguardFiles(\n"
            "                getDefaultProguardFile(\"proguard-android-optimize.txt\"), // قواعد التحسين الصارمة\n"
            "                \"proguard-rules.pro\"\n"
            "            )\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "R8 is AGP's unified code processing engine that performs tree shaking to delete unused code (shrinking), rewrites bytecode for performance like method inlining (optimization), renames identifiers to short symbols (obfuscation), and converts JVM bytecode to Dalvik dex format (dexing) in a single pass.",
        "best_answer": (
            "R8 is Google's all-in-one replacement for ProGuard and D8, unifying four distinct bytecode transformation phases:\n\n"
            "1. **Tree Shaking / Shrinking**:\n"
            "   - Starting from declared entry points (Activities, Services, annotated roots), R8 traces the reachability call graph. Unreferenced classes, methods, and fields are permanently stripped from the binary.\n\n"
            "2. **Bytecode Optimization**:\n"
            "   - Rewrites control flow and instructions for performance: aggressive method inlining, class inlining, horizontal class merging (combining classes with identical shapes), dead branch pruning, and scalar replacement of aggregates.\n\n"
            "3. **Identifier Obfuscation**:\n"
            "   - Renames surviving classes, methods, and fields to short non-descriptive names (`a.b.c()`). This shrinks DEX string table footprints and increases the cognitive barrier against reverse engineering.\n\n"
            "4. **Direct Dexing**:\n"
            "   - Converts the optimized JVM bytecode directly into Android's Dalvik Executable (`classes.dex`) format in a single integrated pipeline phase, emitting the cryptographic `mapping.txt` file."
        ),
        "deep_answer": (
            "From an advanced compiler optimization perspective, understanding R8 optimizations prevents catastrophic runtime bugs:\n\n"
            "1. **proguard-android.txt vs. proguard-android-optimize.txt**: The standard default file disables optimization passes to avoid edge-case bytecode bugs. Senior architects use `proguard-android-optimize.txt`, enabling multi-pass optimizations and class inlining, delivering an extra 10–20% APK size reduction.\n\n"
            "2. **Reflection Hazards with Inlining**: R8 optimization inlines single-use classes or methods. If code invokes a method dynamically via reflection, but R8 inlined or pruned it thinking it was uncalled, runtime crashes (`NoSuchMethodException`) occur in release builds. Annotate reflected targets with `@Keep`.\n\n"
            "3. **Resource Shrinking Integration**: Setting `isShrinkResources = true` requires `isMinifyEnabled = true`. The resource shrinker inspects R8's surviving code reachability graph, identifies unused drawables or layouts, and replaces them with tiny dummy 1-byte files in the packaged APK."
        ),
        "follow_ups": [
            {
                "question": "Can resource shrinking work without code shrinking?",
                "answer": "No; resource shrinking relies on R8's code reachability analysis to determine which R.drawable/layout IDs are unused."
            },
            {
                "question": "What is the purpose of the mapping.txt file generated by R8?",
                "answer": "It provides the bidirectional mapping table translating obfuscated stack traces back into original class, method, and line numbers."
            }
        ]
    },
    {
        "id": "BLD-07",
        "arabic_explanation": (
            "ما هي خاصية `consumerProguardFiles` في موديولات المكتبات (Android Libraries)، ولماذا هي حاسمة في المشاريع متعددة الموديولات؟\n\n"
            "1. مشكلة قواعد الـ ProGuard في الـ Libraries:\n   - عندما تنشئ موديول مكتبة (Android Library Module `:feature:auth` أو مكتبة AAR منشورة)، قد يستخدم هذا الموديول مكتبات سيريالايزيشن أو Reflection أو JNI.\n   - إذا اعتمد التطبيق الرئيسي (`:app`) على هذه المكتبة، وقام بتفعيل R8، سينهار التطبيق في بيئة الـ Release لأن R8 سيحذف كلاسات المكتبة الداخلية أو يشوش أسماء حقولها!\n\n"
            "2. دور `consumerProguardFiles`:\n   - تتيح لموديول المكتبة **تضمين قواعد ProGuard خاصة به داخل ملف الـ AAR الناتج**.\n   - عندما يقوم موديول التطبيق الرئيسي (`:app`) ببناء نسخة الـ Release، يقوم AGP تلقائياً بدمج قواعد الـ `consumerProguardFiles` الواردة من جميع المكتبات التابعة ضمن ملف قواعد R8 النهائي!\n\n"
            "3. الفرق بين `proguardFiles` و `consumerProguardFiles`:\n   - `proguardFiles`: تُطبق على موديول المكتبة نفسه عندما يقوم بعمل Minify لكوده الخاص.\n   - `consumerProguardFiles`: **تُحزم داخل المكتبة وتُطبق على التطبيق المستهلك (The Consuming App)** عندما يقوم ببناء الـ Release."
        ),
        "practical_walkthrough": (
            "تكوين consumerProguardFiles في موديول مكتبة لحماية نماذج البيانات تلقائياً في التطبيق المستهلك:\n"
            "```kotlin\n"
            "// في ملف build.gradle.kts الخاص بموديول المكتبة (:core:network أو :feature:payment):\n"
            "plugins {\n"
            "    alias(libs.plugins.android.library)\n"
            "}\n"
            "\n"
            "android {\n"
            "    defaultConfig {\n"
            "        // 1. تحديد ملف القواعد الذي سيتم تجميعه وتمريره للتطبيق المستهلك:\n"
            "        consumerProguardFiles(\"consumer-rules.pro\")\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "```text\n"
            "# محتوى consumer-rules.pro في موديول المكتبة:\n"
            "# 2. حماية الـ DTOs الخاصة بالمكتبة تلقائياً دون أن يضطر مطور التطبيق لكتابتها يدوياً:\n"
            "-keepclassmembers class com.example.network.dto.** {\n"
            "    <fields>;\n"
            "}\n"
            "```"
        ),
        "quick_answer": "consumerProguardFiles embeds ProGuard rules directly into compiled AAR library packages. When the consuming app builds with R8, AGP automatically merges these rules into the app's master ProGuard configuration, ensuring library-specific reflection and serialization rules apply without manual host app setup.",
        "best_answer": (
            "In modular architectures and third-party SDK development, `consumerProguardFiles` ensures encapsulated R8 configuration:\n\n"
            "1. **The Packaging Mechanism**:\n"
            "   - When configured in an Android library module (`com.android.library`), the specified rules file is bundled directly into the root of the resulting AAR as `proguard.txt`.\n\n"
            "2. **Automatic Rule Merging**:\n"
            "   - When an application module (`:app`) compiles a release build, AGP extracts and merges all `proguard.txt` files from every upstream dependency into its master R8 configuration.\n\n"
            "3. **Zero Configuration for Consumers**:\n"
            "   - If your library uses reflection, JNI, or Moshi/Kotlinx Serialization, consuming developers do not need to manually discover and copy keep rules into the app's `proguard-rules.pro`. The library encapsulates its own preservation requirements.\n\n"
            "4. **Difference from proguardFiles**:\n"
            "   - `proguardFiles` applies only when building and shrinking the library itself; `consumerProguardFiles` applies to downstream consumers of the library."
        ),
        "deep_answer": (
            "From an architectural governance perspective, careless use of consumerProguardFiles can degrade application performance:\n\n"
            "1. **The Poisonous Keep Rule Hazard**: Rules defined in `consumerProguardFiles` apply globally across the entire consuming application's build. If a library author carelessly writes `-keep class ** { *; }` or broad wildcard keep rules, they accidentally disable R8 shrinking and obfuscation across the whole app, ballooning APK size.\n\n"
            "2. **Namespace Scoping**: Always strictly scope consumer keep rules to the exact package namespace owned by the library (e.g. `-keep class com.mycompany.library.internal.**`). Never define global compiler flag directives (`-dontobfuscate` or `-dontoptimize`) in consumer rules.\n\n"
            "3. **Multi-Module Monorepos**: In large enterprise codebases, use `consumerProguardFiles` in internal feature and core modules. This decouples library refactoring: when the payment team updates their DTO reflection patterns, their keep rules update within their own module without touching the root application build file."
        ),
        "follow_ups": [
            {
                "question": "Can consumerProguardFiles be used in an application module (com.android.application)?",
                "answer": "No; consumerProguardFiles is valid only in Android Library modules, as applications do not produce consumable AAR packages."
            },
            {
                "question": "What happens if two libraries declare conflicting ProGuard rules in consumerProguardFiles?",
                "answer": "ProGuard rules are additive; if one library asks to keep a class and another doesn't, the class is kept, as keep rules always take precedence."
            }
        ]
    }
]


def update_bld_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in BLD_01_07:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions BLD-01 to BLD-07. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_bld_data()
