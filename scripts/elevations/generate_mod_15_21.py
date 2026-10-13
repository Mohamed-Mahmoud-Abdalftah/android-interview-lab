#!/usr/bin/env python3
"""Generator for MOD-15 through MOD-21 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "mod.json"

MOD_15_21 = [
    {
        "id": "MOD-15",
        "arabic_explanation": (
            "كيف يؤثر اختيار `api` مقابل `implementation` في Gradle على حدود التجميع (Compilation Boundaries) وإعادة البناء التزايدي (Incremental Rebuilds)؟\n\n"
            "1. المفهوم التقني لـ ABI (Application Binary Interface):\n   - الـ ABI يمثل الهيكل العام الخارجي للكلاسات: أسماء الدوال العامة (Public Methods)، أنواع المعاملات (Parameter Types)، قيم الإرجاع (Return Types)، والحقول العامة.\n   - لا يشمل الـ ABI الكود التنفيذي الداخلي داخل جسم الدوال الخاصة (Private method bodies).\n\n"
            "2. ما الذي يحدث عند استخدام `implementation`؟\n   - التبعية تكون محصورة داخل الموديول فقط.\n   - إذا قمت بتعديل كود داخلي (Private Implementation) في الموديول الأدنى A، يقوم Gradle بإعادة تجميع A فقط.\n   - يكتشف Gradle أن الـ ABI الخاص بـ A لم يتغير، فيقوم بعمل **Skip** لتجميع الموديولات B و C المستهلكة (يضع عليها علامة `UP-TO-DATE` أو `FROM-CACHE`).\n\n"
            "3. ما الذي يحدث عند استخدام `api` (خطر الـ Rebuild Cascade)؟\n   - التبعية تُكشف في الـ Compile Classpath لجميع الموديولات التابعة.\n   - أي تغيير في الموديول A يُبطل صلاحية الـ ABI لجميع الموديولات التي تعتمد عليه عبر `api`، مما يجبر Gradle على إعادة تجميع سلسلة الموديولات بالكامل، وهو ما يقتل سرعة التطوير اليومي."
        ),
        "practical_walkthrough": (
            "تجربة عملية توضح سلوك Gradle مع التعديلات في implementation مقابل api:\n"
            "```kotlin\n"
            "// السيناريو: لدينا 3 موديولات: :core:network <- :data:auth <- :feature:login\n"
            "\n"
            "// الحالة 1: استخدام implementation في :data:auth build.gradle.kts:\n"
            "dependencies {\n"
            "    implementation(projects.core.network)\n"
            "}\n"
            "// إذا قمنا بتعديل دالة خاصة داخل :core:network (مثلاً تحسين لوج الاتصال):\n"
            "// نتيجة تشغيل ./gradlew :feature:login:assembleDebug:\n"
            "// > Task :core:network:compileKotlin SUCCESS\n"
            "// > Task :data:auth:compileKotlin UP-TO-DATE  (لم يُعد تجميعه لأن ABI لم يتغير!)\n"
            "// > Task :feature:login:compileKotlin UP-TO-DATE (تم التخطي تماماً!)\n"
            "\n"
            "// الحالة 2: استخدام api في :data:auth build.gradle.kts:\n"
            "dependencies {\n"
            "    api(projects.core.network)\n"
            "}\n"
            "// أي تعديل في :core:network يُسقط الـ ABI Cache:\n"
            "// > Task :core:network:compileKotlin SUCCESS\n"
            "// > Task :data:auth:compileKotlin SUCCESS     (إعادة تجميع إجبارية!)\n"
            "// > Task :feature:login:compileKotlin SUCCESS (إعادة تجميع إجبارية!)\n"
            "// الفرق في وقت البناء: من ثانية واحدة إلى 25 ثانية مع كل تعديل بسيط!\n"
            "```"
        ),
        "quick_answer": "implementation hides dependencies from the consumer's compile classpath, allowing Gradle to skip downstream recompilations if the dependency's public ABI hasn't changed. api leaks dependencies into downstream classpaths, invalidating ABI caches and triggering expensive rebuild cascades across all transitive consumers whenever any upstream change occurs.",
        "best_answer": (
            "The difference between `api` and `implementation` directly dictates how Gradle performs incremental compilation and task avoidance:\n\n"
            "1. **Compilation Boundaries (`implementation`)**: A dependency declared with `implementation` is available to the declaring module's compiler, but is strictly stripped from the compile classpath of downstream consumers. If module `A` changes an internal implementation detail, Gradle recompiles `A`, verifies its public ABI hash is intact, and skips compiling downstream modules (`UP-TO-DATE`).\n\n"
            "2. **ABI Leakage (`api`)**: Declaring a dependency with `api` publishes it onto the compile classpath of every transitive consumer. Any change to the upstream dependency invalidates the ABI hash of intermediate modules, causing a massive rebuild cascade that recompiles the entire downstream subtree.\n\n"
            "To maximize build speeds in large modularized codebases, enforce `implementation` universally. Reserve `api` exclusively for types that are formally part of the module's public function signatures or return types."
        ),
        "deep_answer": (
            "Under the hood, Gradle's Kotlin compile task (`compileKotlin`) computes an **ABI (Application Binary Interface) digest** based on public classes, method signatures, return types, and annotations.\n\n"
            "When module `A` compiles, Gradle compares its new ABI digest against the cached digest from the previous run:\n"
            "- If the digest matches (meaning only private method bodies, local variables, or comments changed), Gradle halts recompilation for all modules connected via `implementation`.\n"
            "- However, if `B` exposes `A` via `api`, Gradle cannot guarantee that `C` didn't transitively rely on inline functions, constants, or bytecode metadata from `A`. It is forced to re-evaluate and recompile `C`.\n\n"
            "In modern Android architectures, using `implementation` alongside the **Gradle Build Cache** and **Configuration Avoidance APIs** transforms what would be a 40-second build into a sub-second cached fetch."
        ),
        "follow_ups": [
            {
                "question": "Do Kotlin `inline fun` declarations affect ABI stability?",
                "answer": "Yes! Inline functions are inlined directly at the call site in bytecode. Changing the body of an inline function changes the ABI and forces all callers to recompile."
            },
            {
                "question": "Can Gradle lint detect unnecessary `api` dependencies?",
                "answer": "Yes. The Dependency Analysis Gradle Plugin analyzes class usage and flags dependencies that can be safely demoted from `api` to `implementation`."
            }
        ]
    },
    {
        "id": "MOD-16",
        "arabic_explanation": (
            "كيف تختبر وتنشر مكتبة أو SDK أندرويد قابلة لإعادة الاستخدام (Reusable Android Library/SDK Module)؟\n\n"
            "1. عقود ومسؤوليات بناء الـ SDK:\n   - عندما تبني مكتبة مستقلة (تُوزع كـ AAR أو JAR عبر Maven/Nexus/Artifactory)، فإنك تبني منتجاً عاماً يجب أن يراعي:\n     * **الاستقرار الثنائي والتوافق (Binary Compatibility & Semantic Versioning)**: تجنب كسر التوافق مع الإصدارات السابقة (Backward Compatibility).\n     * **تقليل الاعتماديات الخارجية (Minimizing Dependencies)**: إذا استخدم الـ SDK مكتبات مثل OkHttp أو Coroutines بنسخ قديمة، فقد يتعارض مع نسخ التطبيق المستضيف (Dependency Hell / NoSuchMethodError).\n     * **قواعد الحماية والـ Consumer Proguard Rules**: تضمين ملف `consumer-rules.pro` لحماية الكلاسات العامة من الحذف عند قيام التطبيق المستضيف بتفعيل R8/ProGuard.\n\n"
            "2. استراتيجية الاختبار المتكاملة للـ SDK:\n   - **Unit Tests على الـ JVM**: اختبار منطق الأعمال الداخلي بشكل معزول وسريع.\n   - **Instrumented Tests**: اختبار التفاعل مع عتاد ونظام أندرويد الحقيقي.\n   - **Sample Consumer App**: تطبيق أندرويد تجريبي حقيقي داخل نفس الـ Repository يستورد المكتبة ويختبر تجربة المطور (DX) والتكامل الواقعي.\n   - **Binary Compatibility Validator (BCV)**: أداة رسمية من JetBrains تفحص الـ Public API للمكتبة وتفشل الـ Build إذا قام مطور بتغيير كسر التوافق دون تغيير رقم الإصدار الأساسي (Major Version).\n\n"
            "3. النشر الآلي (Publishing Pipeline):\n   - استخدام `maven-publish` plugin لنشر الـ AAR والـ POM و Gradle Module Metadata و Javadoc."
        ),
        "practical_walkthrough": (
            "إعداد نشر مكتبة Android باستخدام maven-publish و consumer-rules:\n"
            "```kotlin\n"
            "// 📁 في build.gradle.kts الخاص بموديول المكتبة (:mylibrary):\n"
            "plugins {\n"
            "    id(\"com.android.library\")\n"
            "    id(\"maven-publish\")\n"
            "    id(\"org.jetbrains.kotlinx.binary-compatibility-validator\") // فحص كسر الـ API في CI\n"
            "}\n"
            "\n"
            "android {\n"
            "    namespace = \"com.company.sdk\"\n"
            "    compileSdk = 35\n"
            "    \n"
            "    defaultConfig {\n"
            "        minSdk = 21\n"
            "        // تضمين قواعد الحماية التي سيطبقها التطبيق المستهلك تلقائياً:\n"
            "        consumerProguardFiles(\"consumer-rules.pro\")\n"
            "    }\n"
            "    \n"
            "    publishing {\n"
            "        singleVariant(\"release\") { withSourcesJar(); withJavadocJar() }\n"
            "    }\n"
            "}\n"
            "\n"
            "publishing {\n"
            "    publications {\n"
            "        register<MavenPublication>(\"release\") {\n"
            "            afterEvaluate { from(components[\"release\"]) }\n"
            "            groupId = \"com.company.sdk\"\n"
            "            artifactId = \"core-sdk\"\n"
            "            version = \"2.1.0\"\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "To build and publish a reusable Android SDK, enforce strict semantic versioning and binary compatibility via JetBrains Binary Compatibility Validator. Bundle consumer ProGuard rules via consumer-rules.pro, test against a sample consumer app in the repo, and publish release AARs with POM metadata and sources via the maven-publish Gradle plugin.",
        "best_answer": (
            "Building an enterprise-grade reusable Android SDK requires treating the library as a self-contained product with strict stability contracts:\n\n"
            "1. **Consumer ProGuard Rules (`consumer-rules.pro`)**: Libraries must ship ProGuard rules that are automatically applied to consuming applications. This ensures that the SDK's public interfaces, JNI native bindings, and serialization models are not stripped or mangled when client apps run R8.\n\n"
            "2. **Binary Compatibility Governance**: Use JetBrains' **Binary Compatibility Validator (BCV)** plugin in CI. It maintains an API dump file (`.api`) in Git. If a pull request modifies a public method signature or removes an overload, BCV fails the build unless the change is explicitly approved and versioned under SemVer rules.\n\n"
            "3. **Testing Pyramid**: Comprehensive JVM unit tests, instrumented tests on Firebase Test Lab, and an included **Sample App** module that consumes the library exactly like a third-party developer.\n\n"
            "4. **Publishing Pipeline**: Configure the `maven-publish` plugin to emit release AARs, Javadoc JARs, Sources JARs, and Gradle Module Metadata (`.module`) to a secure Maven repository (Nexus/Artifactory/MavenCentral)."
        ),
        "deep_answer": (
            "When engineering production SDKs, the greatest technical pitfall is **Transitive Dependency Pollution**.\n\n"
            "If your SDK depends on `OkHttp 4.9.0` and a host application depends on `OkHttp 5.0.0-alpha`, Gradle's conflict resolution selects the higher version, which may contain breaking binary changes that crash your SDK. Conversely, if your SDK bundles an internal library via `implementation`, the host app might experience duplicate class conflicts.\n\n"
            "To safeguard a commercial SDK:\n"
            "- Minimize external dependencies; prefer pure Kotlin standard library and platform Android APIs wherever possible.\n"
            "- If heavy third-party libraries (like Protocol Buffers or JSON parsers) are mandatory, use **Bytecode Shading / Relocation (via Shadow plugin or Jarjar)** to rename packages (e.g. `com.google.protobuf` -> `com.company.sdk.internal.protobuf`), insulating your SDK from host app version conflicts."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between `proguardFiles` and `consumerProguardFiles` in an Android library?",
                "answer": "`proguardFiles` configures obfuscation for the library itself during its build; `consumerProguardFiles` bundles rules packaged inside the AAR for the client app to apply during its build."
            },
            {
                "question": "Why should SDK public APIs use explicit visibility modifiers (`explicitApi()`)?",
                "answer": "Kotlin's `explicitApi()` compiler mode forces developers to explicitly declare `public` or `internal` and return types on all declarations, preventing accidental leakage of internal implementation details."
            }
        ]
    },
    {
        "id": "MOD-17",
        "arabic_explanation": (
            "متى يكون إنشاء موديول ميزة جديد (New Feature Module) مبرراً، ومتى يتحول إلى تعقيد زائد غير مبرر (Unnecessary Complexity)؟\n\n"
            "1. متى يكون إنشاء موديول جديد مبرراً وضرورياً (Justified Reasons):\n   - **استقلالية الفريق والملكية (Distinct Team Ownership)**: ميزة جديدة يديرها فريق مستقل تماماً (مثل فريق التوصيل أو فريق الدفع) لمنع تعارضات الـ Git والاندماج.\n   - **عزل الميزات الثقيلة المتغيرة باستمرار (High-Velocity / High-Churn Feature)**: ميزة يتم التعديل عليها مئات المرات أسبوعياً؛ فصلها في موديول يمنع إعادة تجميع باقي أجزاء التطبيق المستقرة.\n   - **التسليم عند الطلب (Dynamic Feature Delivery)**: ميزة يراد تنزيلها لاحقاً عبر Play Feature Delivery لتقليل حجم التطبيق الأولي.\n   - **تطبيقات تجريبية معزولة (Sample / Demo App Need)**: الحاجة لتشغيل الميزة وتجربتها في تطبيق تجريبي معزول في 3 ثوانٍ.\n\n"
            "2. متى يكون إنشاء موديول تعقيداً هندسياً زائداً (Unnecessary Over-Modularization):\n   - **شاشة واحدة بسيطة (Single-Screen Trivial Features)**: إنشاء موديول كامل لشاشة شروط الاستخدام (Terms of Service) أو شاشة 'من نحن' التي تحتوي على نص ثابت فقط!\n   - **شاشات شديدة الترابط (Tightly Coupled Sub-flows)**: تقسيم شاشة سلة المشتريات (Cart) وشاشة الدفع (Checkout) إلى موديولين منفصلين مع أنهما يتشاركان نفس الحالة ونفس نماذج البيانات خطوة بخطوة.\n   - **التقسيم لمجرد التنظيم الشكلي**: تفتيت التطبيق إلى 200 موديول ميكروسكوبي، مما يؤدي إلى بطء رهيب في تزامن Android Studio (Gradle Sync Time) وزيادة وقت التجميع الكلي للـ Clean Build."
        ),
        "practical_walkthrough": (
            "مصفوفة اتخاذ القرار الهندسي: هل نحتاج إلى إنشاء موديول جديد أم مجرد Package؟\n"
            "```text\n"
            "┌──────────────────────────────────────────────┬──────────────────────────────────┐\n"
            "│ معيار القرار                                │ القرار الهندسي الموصى به          │\n"
            "├──────────────────────────────────────────────┼──────────────────────────────────┤\n"
            "│ شاشة بسيطة (About, FAQ, Settings item)       │ ❌ Package داخل موديول قائم      │\n"
            "│ ميزة متصلة بشدة وتشارك الـ ViewModel         │ ❌ نفس الموديول                  │\n"
            "│ تدفق كامل يديره فريق منفصل (Payment, KYC)    │ ✅ موديول مستقل (:feature:kyc)   │\n"
            "│ ميزة تتطلب تسليم ديناميكي (On-demand AR)     │ ✅ Dynamic Feature Module        │\n"
            "│ ميزة تحتاج لتطبيق تجريبي مستقل للتطوير السريع│ ✅ موديول مستقل                  │\n"
            "└──────────────────────────────────────────────┴──────────────────────────────────┘\n"
            "\n"
            "// إذا كان الموديول سيحتوي على أقل من 3 ملفات، فغالباً هو تعقيد غير مبرر (Premature Modularization)!\n"
            "```"
        ),
        "quick_answer": "A new feature module is justified when driven by independent team ownership, high-velocity code changes requiring isolated build caching, dynamic feature delivery, or the need for an isolated sample app. It is unnecessary complexity for trivial single screens, tightly coupled sub-flows, or speculative modularization that inflates Gradle sync times.",
        "best_answer": (
            "Creating a new Gradle module carries a permanent maintenance and build cost. A senior engineer evaluates module extraction against four concrete criteria:\n\n"
            "1. **When It Is Justified**:\n   - **Team Ownership Boundaries**: A dedicated team owns the feature (e.g., `:feature:checkout` owned by the Payments team), supported by explicit GitHub `CODEOWNERS` rules.\n   - **Compilation Velocity & Caching**: The feature experiences high code churn. Isolating it ensures that hundreds of daily commits do not trigger recompilations of stable sibling modules.\n   - **Dynamic Feature Delivery**: The feature is delivered conditionally or on-demand via Android App Bundles (e.g. heavy ML or AR features).\n   - **Fast Isolated Feedback**: The team requires an isolated sample app (`:feature:x:sample`) that compiles in 4 seconds to test UI flows without launching the monolithic app.\n\n"
            "2. **When It Is Accidental Complexity**:\n   - **Trivial Read-Only Screens**: Creating dedicated modules for 'About Us' or 'Legal Terms'.\n   - **Tightly Coupled Sub-flows**: Splitting screens that inherently share view models, state machines, and atomic transactions.\n   - **Premature Granularity**: Splitting code into hundreds of micro-modules, degrading Android Studio IDE sync times and increasing Gradle configuration overhead."
        ),
        "deep_answer": (
            "The performance trade-off of modularization is governed by the ratio between **Gradle Configuration Time and Execution Time**.\n\n"
            "In a project with 300 micro-modules, Gradle must evaluate 300 `build.gradle.kts` files, configure 300 compile tasks, and Android Studio must index 300 module source sets. "
            "If modules are too small, the configuration phase takes 15 seconds, while the actual compilation takes 2 seconds—making the developer experience painfully sluggish.\n\n"
            "A pragmatic rule of thumb: **Start with cohesive package structures inside a single module**. "
            "Only extract a package into a discrete Gradle module when package-level boundaries are established, compilation frequency is high, or cross-team collaboration friction demands physical enforcement."
        ),
        "follow_ups": [
            {
                "question": "How does Android Studio IDE memory consumption scale with module count?",
                "answer": "Each Gradle module creates distinct project models and facet caches in IDE memory; having hundreds of modules dramatically increases RAM usage and indexing latency."
            },
            {
                "question": "What is an isolated sample app module?",
                "answer": "A lightweight application module (`com.android.application`) that depends only on a single feature module and fake repositories, allowing rapid UI iteration without running the full app."
            }
        ]
    },
    {
        "id": "MOD-18",
        "arabic_explanation": (
            "تغيير سطر واحد في نموذج بيانات مشترك (Shared Model) أدى إلى إعادة تجميع عشرات الموديولات في المشروع. كيف تشخص المشكلة وتحد من أثرها الكارثي؟\n\n"
            "1. تشخيص السبب الجذري (Root Cause Diagnosis):\n   - **تضخم الاعتمادية وانتشار الـ Fan-out (High Build Fan-out)**: موديول يسمى `:core:model` يحتوي على كلاس `User` أو `Order`. هناك 40 موديول Feature يعتمدون على هذا الموديول مباشرة.\n   - **تسريب الـ ABI (ABI Invalidation)**: عند إضافة حقل جديد (مثل `val isVip: Boolean = false`) لكلاس الـ `User`، فإن الـ ABI Digest الخاص بـ `User` يتغير بالكامل.\n   - لأن جميع الموديولات تستورد هذا الكلاس في دوالها العامة، يعتبر Gradle أن الـ Compile Classpath لجميع هذه الموديولات الـ 40 قد فُقدت صلاحيته، فيلغي الـ Build Cache ويعيد تجميعها جميعاً من الصفر!\n\n"
            "2. الحلول المعمارية للحد من الأثر (Architectural Solutions):\n   - **تجزئة الموديل العام إلى نماذج متخصصة ومستقلة (Model Segregation)**: بدلاً من كائن `User` عملاق يحتوي على 50 حقلاً، افصله إلى نماذج بيانات مركزة:\n     * `UserAuthCredentials` في موديول التحقق.\n     * `UserBillingProfile` في موديول المدفوعات.\n     * `UserShippingAddress` في موديول التوصيل.\n   - **استخدام Feature-Specific UI Models مع Mappers**: موديول الـ Feature يعرّف نموذج الـ UI الخاص به (`UserProfileUiState`)، ويقوم بعمل Mapping من الموديل العام، مما يعزل الشاشات عن التغييرات الخارجية.\n   - **تجنب وضع دوال `inline` داخل الموديولات المشتركة**: الدوال الـ Inline تجبر المترجم على تتبع الكود في كل مكان تم استدعاؤها فيه."
        ),
        "practical_walkthrough": (
            "تفكيك الموديل العملاق عالي التأثير إلى نماذج متخصصة ضيقة الأثر:\n"
            "```kotlin\n"
            "// ❌ الموديل المشترك الكارثي (God Model في :core:model): أي تغيير يعيد تجميع 40 موديولاً:\n"
            "data class User(\n"
            "    val id: String,\n"
            "    val name: String,\n"
            "    val email: String,\n"
            "    val creditCardToken: String, // يخص الدفع فقط\n"
            "    val loyaltyPoints: Int,      // يخص المكافآت فقط\n"
            "    val shippingAddress: String  // يخص الشحن فقط\n"
            ")\n"
            "\n"
            "// ✅ الحل المعماري: تجزئة النماذج حسب النطاق (Scoped Domain Models):\n"
            "// 📁 في :domain:auth:\n"
            "data class AuthenticatedUser(val id: String, val email: String)\n"
            "\n"
            "// 📁 في :domain:payment:\n"
            "data class PaymentCustomer(val userId: String, val creditCardToken: String)\n"
            "\n"
            "// 📁 في :domain:loyalty:\n"
            "data class LoyaltyMember(val userId: String, val points: Int)\n"
            "\n"
            "// الآن: تعديل نظام نقاط المكافآت (Loyalty) في :domain:loyalty\n"
            "// يعيد تجميع موديول المكافآت فقط! موديول الدفع وموديول المصادقة يظلان UP-TO-DATE بنسبة 100%.\n"
            "```"
        ),
        "quick_answer": "A shared model change triggers massive rebuilds due to high fan-out and ABI invalidation. Shrink the impact by decomposing the monolithic model into domain-scoped models (e.g. AuthUser, BillingUser), introducing feature-specific UI models with local mappers, and moving stable primitives into isolated contract modules.",
        "best_answer": (
            "When modifying a shared data model causes dozens of modules to recompile, the root cause is **Unconstrained Module Fan-Out combined with Public ABI Invalidation**:\n\n"
            "1. **Root Cause**: A foundational module (like `:core:model`) exports an oversized entity (e.g. `User` with 40 fields) consumed transitively by 30+ feature modules. Adding or modifying a single property alters the compiled bytecode signatures (the ABI digest). Gradle detects the ABI mismatch and invalidates the compile classpath for every downstream module.\n\n"
            "2. **Architectural Remediation**:\n   - **Domain Model Segregation**: Split the monolithic entity into bounded-context models. The payment feature needs `BillingAccount`, the delivery feature needs `DeliveryRecipient`, and the auth feature needs `AuthIdentity`. Each lives in its respective domain module.\n   - **Feature-Level UI Models & Adapters**: Feature modules should map domain models into internal UI state data classes (`CheckoutUiState`). A change in backend metadata does not alter the feature's internal ABI.\n   - **Eliminate `inline` Functions on Models**: Never declare inline utility functions on shared models; inline bytecode embedding guarantees full caller recompilation."
        ),
        "deep_answer": (
            "To diagnose and monitor fan-out rebuild cascades quantitatively:\n\n"
            "1. **Run Gradle with Profiling**: Execute `./gradlew assembleDebug --profile --scan`. The Gradle Build Scan's 'Timeline' and 'Performance' tabs reveal exactly which task invalidated the cache and triggered the cascade.\n\n"
            "2. **Inspect the ABI Diff**: Compare task inputs using Gradle's verbose log: `./gradlew assembleDebug --info | grep -i \"ABI changed\"`. This confirms whether a public signature or private method triggered downstream compilation.\n\n"
            "3. **Graph Fan-Out Metrics**: In CI, track the **Fan-In (afferent coupling)** of core modules. If a single module's fan-in exceeds 50% of the repository's modules, it is an architectural hazard and must be prioritized for decomposition into independent, stable API slices."
        ),
        "follow_ups": [
            {
                "question": "Why does adding a private property to a public Kotlin data class invalidate ABI?",
                "answer": "Because in Kotlin, data classes auto-generate public methods (`copy()`, `componentN()`, `equals()`, `hashCode()`) based on all constructor properties; changing any property alters those public signatures."
            },
            {
                "question": "How does using interfaces instead of data classes mitigate ABI rebuilds?",
                "answer": "Consumers depend on the stable interface; the concrete implementation can add internal fields without altering the interface's ABI signature."
            }
        ]
    },
    {
        "id": "MOD-19",
        "arabic_explanation": (
            "فريقان لميزتين مختلفتين (Feature Teams) يحتاجان إلى نفس منطق الأعمال (Same Business Logic). أين يجب أن يعيش هذا المنطق معمارياً؟\n\n"
            "1. الحلول الخاطئة الشائعة:\n   - **الخطأ الأول**: جعل موديول Feature A يعتمد على موديول Feature B (`:feature:cart -> :feature:catalog`). هذا يكسر العزل، ويخلق اقتراناً شديداً، وقد يسبب تبعية دائرية مستحيلة.\n   - **الخطأ الثاني**: رمي الكود في موديول عشوائي `:core:common` أو `:core:utils`، مما يجعله مزبلة للمنطق التجاري غير المترابط.\n\n"
            "2. الحل المعماري النظيف (Single Authoritative Owner in Domain Layer):\n   - **إنشاء موديول Domain مخصص**: استخراج منطق الأعمال إلى موديول نقي في طبقة الـ Domain، مثل `:domain:pricing` أو `:domain:tax`.\n   - يحتوي هذا الموديول على الكيان النقي (Entity)، وقواعد الحساب، و UseCase محدد (مثل `CalculateOrderDiscountUseCase`).\n   - **يعتمد كلا الفريقين على موديول الـ Domain للأسفل**: يعتمد كل من `:feature:cart` و `:feature:checkout` على `:domain:pricing`.\n   - **وضوح الملكية (Code Ownership)**: يتم تعيين فريق محدد كمالك للموديول في ملف `CODEOWNERS` لضمان عدم إجراء أي تعديل دون مراجعة وتدقيق معتمدين."
        ),
        "practical_walkthrough": (
            "استخراج منطق أعمال مشترك إلى موديول Domain مستقل:\n"
            "```text\n"
            "❌ قبل: اقتران غير مسموح بين موديولين ميزات:\n"
            ":feature:cart ─────(illegal direct dependency)─────► :feature:catalog\n"
            "\n"
            "✅ بعد: استخراج المنطق المشترك إلى موديول Domain مستقل يملكه مالك محدد:\n"
            "      :feature:cart                   :feature:checkout\n"
            "            │                                │\n"
            "            │ (depends on)                   │ (depends on)\n"
            "            ▼                                ▼\n"
            "      ┌──────────────────────────────────────────────┐\n"
            "      │             :domain:pricing                  │\n"
            "      │ (DiscountCalculator, TaxPolicy, PricingRules)│\n"
            "      └──────────────────────────────────────────────┘\n"
            "\n"
            "// في :domain:pricing (Pure Kotlin JVM):\n"
            "class CalculatePromotionalDiscountUseCase @Inject constructor() {\n"
            "    fun execute(items: List<CartItem>, promoCode: String?): DiscountResult = ...\n"
            "}\n"
            "// كلا الفريقين يستوردان هذا الـ UseCase بأمان واستقرار تام!\n"
            "```"
        ),
        "quick_answer": "When two feature teams share business logic, never couple the features directly or dump code into :core:common. Extract the logic into a focused, single-responsibility domain module (e.g. :domain:pricing) containing pure Use Cases and business rules, with clear CODEOWNERS governance.",
        "best_answer": (
            "When two feature teams require identical business logic, resolving placement demands strict architectural governance:\n\n"
            "1. **Never Create Feature-to-Feature Dependencies**: Permitting `:feature:cart` to depend on `:feature:checkout` violates the fundamental acyclic boundary rule and entangles two distinct user journeys.\n\n"
            "2. **Extract to a Focused Domain Module**: Create a dedicated JVM module representing the specific business capability: e.g. `:domain:pricing` or `:domain:identity`. This module houses pure Kotlin business entities, invariants, and Use Cases (`CalculateTaxUseCase`). Both feature modules depend downward on this domain module.\n\n"
            "3. **Establish Clear Code Ownership**: Designate a single team as the primary owner in `CODEOWNERS` (e.g. Payments team owns `:domain:pricing`). If the other team needs enhancements, they submit pull requests subject to the owning team's review and automated test suites."
        ),
        "deep_answer": (
            "Before extracting shared business logic into a common module, senior engineers evaluate **Semantic Equivalence vs. Accidental Coincidence**.\n\n"
            "Often, two features appear to need the 'same' logic, but their underlying domain invariants are actually diverging. For example, calculating price in a product catalog may tolerate cached approximate tax estimations, whereas calculating price in final checkout requires strict real-time fiscal compliance.\n\n"
            "If you force divergent requirements into a single shared function with boolean flags (`calculatePrice(isCheckout: Boolean)`), you introduce toxic coupling. "
            "If the business rules have fundamentally different lifecycles or reasons to change, it is better to maintain separate use cases. Only extract shared code when the underlying business invariant is mathematically or legally identical."
        ),
        "follow_ups": [
            {
                "question": "What happens if a shared domain module requires network data?",
                "answer": "The domain module declares an abstract repository interface; the corresponding `:data:*` module implements it and handles networking."
            },
            {
                "question": "Should shared business logic include UI formatting strings?",
                "answer": "No. Business logic returns raw domain types (e.g. `Money(amount = 12.50, currency = USD)`); UI formatting belongs in presentation layers."
            }
        ]
    },
    {
        "id": "MOD-20",
        "arabic_explanation": (
            "كيف تهاجر تطبيقاً متجانساً ضخماً (Monolith) إلى هيكل نمطي (Modularized Architecture) دون تعطيل تسليم الميزات الجديدة للفريق؟\n\n"
            "1. الاستراتيجية المعمارية الأساسية: نمط شجرة التين الخانقة (Strangler Fig Pattern):\n   - لا تقم أبداً بإيقاف تطوير الميزات لمدة 3 أشهر لإعادة كتابة التطبيق (وصفة للفشل المؤكد).\n   - تتم الهجرة بشكل تزايدي وتدريجي شريحة بشريحة (Vertical Slices)، مع بقاء التطبيق القديم والجديد يعملان معاً في كل Release.\n\n"
            "2. مراحل خطة الهجرة خطوة بخطوة:\n   - **المرحلة 1: بناء الأساسات (Foundations & Build Infrastructure)**: إعداد Version Catalog و Convention Plugins في مجلد `build-logic` لتوحيد إعدادات Gradle.\n   - **المرحلة 2: استخراج موديولات الـ Core من القاع (Bottom-Up Infrastructure Extraction)**:\n     * استخراج `:core:designsystem` (الألوان والخطوط والمكونات العامة).\n     * استخراج `:core:network` و `:core:database`.\n   - **المرحلة 3: استخراج شريحة ميزة رأسية كاملة كـ Pilot Feature (Vertical Slice)**:\n     * اختيار ميزة صغيرة ومحددة (مثل شاشة الإعدادات أو الملف الشخصي).\n     * استخراجها في `:feature:profile` مع تطبيق نمط الـ DI و Navigation Contracts.\n   - **المرحلة 4: تدريب الفريق وتوثيق المعايير (Documentation & Playbook)**: تحويل التجربة إلى دليل عمل للفريق لهجرة باقي الشاشات بالتوازي مع مهام السبرنت العادية.\n   - **المرحلة 5: ضمور الموديول القديم**: يستمر موديول `:app` في فقدان الكلاسات تدريجياً حتى يتحول إلى مجرد موديول تجميع فارغ (Thin Composition Root)."
        ),
        "practical_walkthrough": (
            "خطة الهجرة التدريجية لشريحة رأسية (Vertical Slice Extraction):\n"
            "```text\n"
            "المرحلة 1: Monolith مع موديولات أساسية مستخرجة:\n"
            "┌────────────────────────────────────────────────────────┐\n"
            "│                         :app                           │\n"
            "│ (Cart, Feed, Profile, Checkout, Auth كود مختلط بالداخل)│\n"
            "└───────────┬────────────────────────────────┬───────────┘\n"
            "            ▼                                ▼\n"
            "    ┌───────────────┐                ┌───────────────┐\n"
            "    │ :core:design  │                │ :core:network │\n"
            "    └───────────────┘                └───────────────┘\n"
            "\n"
            "المرحلة 2: استخراج أول ميزة مستقلة بنجاح (:feature:profile):\n"
            "┌────────────────────────────────────────────────────────┐\n"
            "│                         :app                           │\n"
            "│        (فقط يجمع ويشغل Navigation و Hilt)             │\n"
            "└───────┬────────────────────────────────────────┬───────┘\n"
            "        ▼                                        ▼\n"
            "┌─────────────────┐                     ┌─────────────────┐\n"
            "│ :feature:profile│ (كود معزول جديد)    │ Monolith Legacy │ (القديم ينكمش)\n"
            "└───────┬─────────┘                     └────────┬────────┘\n"
            "        └────────────────┬───────────────────────┘\n"
            "                         ▼\n"
            "                 ┌───────────────┐\n"
            "                 │ :core:*       │\n"
            "                 └───────────────┘\n"
            "```"
        ),
        "quick_answer": "Migrate a monolith incrementally using the Strangler Fig pattern. Establish Gradle convention plugins first, extract core horizontal foundations (:core:designsystem, :core:network) bottom-up, migrate one vertical feature slice as a pilot to validate the pattern, and gradually extract remaining features during regular sprints until :app becomes a thin assembly root.",
        "best_answer": (
            "Migrating an enterprise Android monolith to a multi-module architecture without halting feature velocity relies on the **Strangler Fig Pattern** executed in four controlled phases:\n\n"
            "1. **Phase 1: Build Governance & Tooling**:\n   - Introduce `libs.versions.toml` and custom Gradle convention plugins in `build-logic`.\n   - Establish CI performance baselines for Gradle build times and memory consumption.\n\n"
            "2. **Phase 2: Bottom-Up Foundation Extraction**:\n   - Extract horizontal infrastructure that has zero feature dependencies: `:core:designsystem`, `:core:network`, and `:core:model`.\n   - The legacy monolith consumes these modules immediately, proving they work in production.\n\n"
            "3. **Phase 3: The Pilot Vertical Slice**:\n   - Select an isolated, low-risk feature (e.g. `:feature:settings`).\n   - Extract its UI, ViewModel, Domain logic, and Data layer into dedicated modules, establishing the navigation and DI patterns for the entire organization.\n\n"
            "4. **Phase 4: Opportunistic Feature Migration**:\n   - Create a 'Modularization Playbook'. Feature teams extract their own modules incrementally whenever embarking on a major feature redesign, until `:app` shrinks to a thin composition shell."
        ),
        "deep_answer": (
            "The greatest danger during a monolith migration is **The Entangled Dependency Knot** (where Class A in the feature imports 25 random utility and helper classes from the monolith).\n\n"
            "If you try to extract everything Class A touches, you end up moving half the monolith into the new module. To break this knot in production:\n\n"
            "1. **Invert the Seam with an Interface**: If the feature needs a monolith service (`LegacySessionManager`), define an interface inside the new feature module (`interface SessionProvider`). Have the legacy monolith implement this interface and inject it into the feature.\n\n"
            "2. **Temporary Bidirectional Bridge**: The feature compiles against its own interface, completely isolated from monolith internals. Once the session logic itself is migrated to a core module later, you simply delete the bridge implementation in the monolith."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't you freeze feature development during modularization?",
                "answer": "Freezing feature development stalls business value for months, and merging back a massive refactoring branch inevitably causes catastrophic merge conflicts and regressions."
            },
            {
                "question": "What defines a 'Thin Composition Root' in `:app`?",
                "answer": "An `:app` module that contains almost no Kotlin code except the `Application` class, top-level `NavHost` wiring, and root Hilt entry points."
            }
        ]
    },
    {
        "id": "MOD-21",
        "arabic_explanation": (
            "متى تكون موديولات الميزات الديناميكية (Dynamic Feature Modules - DFMs) غير مناسبة وخياراً معمارياً سيئاً بسبب قيود وضع عدم الاتصال وأوقات التشغيل؟\n\n"
            "1. الحالات التي يُحظر فيها استخدام Dynamic Feature Modules:\n   - **الميزات الأساسية في المسار الحرج (Critical User Journey)**: شاشات تسجيل الدخول (Login), سلة المشتريات (Cart), أو إتمام الدفع (Checkout). لا يجوز أبداً أن يفتح المستخدم التطبيق ليشتري منتجاً فيفاجأ بشاشة 'جارِ تنزيل شاشة الدفع بنسبة 12%'!\n   - **التطبيقات التي تتطلب العمل دون اتصال (Offline-First Apps)**: تطبيقات الطوارئ، تطبيقات الميدان والمستودعات، أو تطبيقات السفر والملاحة. إذا كان المستخدم في منطقة بدون شبكة، فلن يستطيع تنزيل الميزة وستتعطل وظيفته بالكامل.\n   - **الميزات ذات زمن الانتقال الحرج (Low-Latency SLA)**: إذا كانت الميزة تتطلب استجابة فورية (مثل كاميرا فحص الباركود في السوبرماركت)، فإن انتظار تنزيل 15MB عبر شبكة الجوال يقتل تجربة المستخدم.\n   - **التطبيقات الموزعة خارج متجر Google Play**: الـ Dynamic Delivery يعتمد حصرياً على Google Play Core Services. إذا كان تطبيقك يُوزع عبر Huawei AppGallery أو Samsung Galaxy Store أو تثبيت مباشر (Sideloading/Enterprise APKs)، فلن تعمل الـ DFMs على الإطلاق!\n\n"
            "2. البديل المعماري الموصى به:\n   - استخدم النمطية العادية (Standard Library Modules `com.android.library`) المجمعة في الـ Base APK، واستفد من تقنيات تصغير الحجم مثل R8، وتحويل الصور إلى WebP، وضغط الموارد لتحقيق حجم خفيف دون التضحية بالموثوقية."
        ),
        "practical_walkthrough": (
            "مقارنة متى تستخدم Dynamic Delivery ومتى تعتمد على Standard Modularization:\n"
            "```text\n"
            "┌──────────────────────────────────────────────┬──────────────────────────────────┐\n"
            "│ سيناريو الميزة                              │ الاختيار المعماري الصحيح         │\n"
            "├──────────────────────────────────────────────┼──────────────────────────────────┤\n"
            "│ تسجيل الدخول وشاشات المصادقة (Auth)          │ ❌ Base APK (Standard Module)    │\n"
            "│ إتمام الشراء والدفع (Checkout/Payment)       │ ❌ Base APK (مسار حرج لا يحتمل)  │\n"
            "│ تطبيق ملاحة ومستودعات يعمل Offline           │ ❌ Base APK (غير متصل بالإنترنت) │\n"
            "│ توزيع خارج Google Play (Huawei, Enterprise)   │ ❌ Base APK (Google Play غير متاح│\n"
            "│ وضع واقع معزز ثقيل (50MB AR Viewer)          │ ✅ Dynamic Feature Module (DFM)  │\n"
            "│ فحص وثائق الهوية نادراً ما يُستخدم (KYC Scan) │ ✅ Dynamic Feature Module (DFM)  │\n"
            "└──────────────────────────────────────────────┴──────────────────────────────────┘\n"
            "```"
        ),
        "quick_answer": "Dynamic Feature Modules are inappropriate for critical paths (login, checkout), offline-first apps, latency-sensitive workflows, and apps distributed outside Google Play. Downloading on-demand introduces network failure points, loading spinners, and dependency on Google Play Services that ruin core app experiences.",
        "best_answer": (
            "Dynamic Feature Modules (DFMs) solve APK download size constraints, but they introduce severe runtime failure vectors that make them inappropriate for core application functionality:\n\n"
            "1. **Critical Path User Journeys**: Onboarding, Authentication, Catalog browsing, and Checkout must **never** be dynamic features. Requiring a user to wait for a 15MB download before they can log in or swipe their credit card causes catastrophic conversion drops.\n\n"
            "2. **Offline-First Architectural Constraints**: If an application must operate without active cellular connectivity (e.g., warehouse inventory scanning, field inspections, emergency response), an uninstalled on-demand module is completely unreachable, turning core features into dead buttons.\n\n"
            "3. **Store Vendor Lock-in**: Google Play Feature Delivery relies strictly on the Google Play Core library and Play Store client infrastructure. If the app is distributed via sideloading, enterprise MDM, Amazon Appstore, or Huawei AppGallery, dynamic split downloading is unsupported.\n\n"
            "Reserve DFMs strictly for non-critical, heavy, infrequently used capabilities (e.g. a 40MB AR furniture previewer or an annual tax calculator). Core capabilities should always be bundled into the base APK using standard Gradle library modules."
        ),
        "deep_answer": (
            "When analyzing failure modes for on-demand DFMs in production telemetry:\n\n"
            "1. **High Download Drop-off**: Network metrics reveal that 10% to 25% of on-demand download requests fail due to mobile network handoffs, slow roaming data, or insufficient device disk storage (`ERROR_INSUFFICIENT_STORAGE`).\n\n"
            "2. **User Drop-off During Progress Spinners**: Even when the download succeeds, placing a 10-second download progress bar between a user's tap and screen presentation causes over 30% of users to abandon the funnel.\n\n"
            "3. **The Architectural Sweet Spot**: If module size reduction is the primary goal, senior teams evaluate asset streaming (downloading heavy 3D assets or ML models from a standard CDN to local disk) rather than dynamic code splits. Streaming assets keeps code paths in the base APK with full compile-time type safety while keeping initial download sizes minimal."
        ),
        "follow_ups": [
            {
                "question": "Can Dynamic Feature Modules be pre-installed conditionally based on device capabilities?",
                "answer": "Yes. Conditional Delivery can install modules during initial app install if the device meets hardware criteria (e.g. has ARCore support), avoiding runtime download friction."
            },
            {
                "question": "What error code indicates insufficient storage during dynamic install?",
                "answer": "`SplitInstallErrorCode.INSUFFICIENT_STORAGE` (-10), which must be caught to notify the user to free up device space."
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

    for item in MOD_15_21:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions MOD-15 to MOD-21. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
