#!/usr/bin/env python3
"""Generator for MOD-01 through MOD-07 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "mod.json"

MOD_01_07 = [
    {
        "id": "MOD-01",
        "arabic_explanation": (
            "ما هي النمطية (Modularization) في Android، وما هي المقايضات (Trade-offs) والتكاليف الحقيقية التي تفرضها على الفريق والمشروع؟\n\n"
            "1. المفهوم الحقيقي للـ Modularization:\n   - الـ Module ليس مجرد مجلد (Folder) عادي؛ بل هو **حد مادي مستقل للبناء (Physical Build & Ownership Boundary)** في Gradle.\n   - كل موديول يمتلك ملف `build.gradle.kts` خاصاً به، وإعدادات اعتماديات مستقلة، ومخرجات تجميع خاصة به (AAR أو JAR).\n\n"
            "2. الفوائد الحقيقية في المشاريع الكبيرة:\n   - **تسريع وقت البناء (Faster Build Times)**: الاستفادة القصوى من الـ Parallel Execution والـ Gradle Build Cache. إذا عدلت في موديول `:feature:profile`، فلن يعيد Gradle تجميع موديول `:feature:checkout`.\n   - **فرض العزل المعماري ومنع التسريب (Strict Encapsulation)**: موديول الـ Feature لا يستطيع استيراد كلاسات خاصة أو قواعد بيانات داخلية إلا إذا تم تصديرها كـ Public API.\n   - **استقلالية الفرق ووضوح الملكية (Team Ownership & CODEOWNERS)**: يمكن لفريق المدفوعات العمل في `:feature:payment` دون أي تعارضات Git Merge مع فريق الشحن.\n   - **إمكانية إعادة الاستخدام واختبار الميزات المعزولة (Isolated Sample Apps)**: تشغيل تطبيق تجريبي خفيف للميزة فقط في 3 ثوانٍ دون تجميع التطبيق الضخم بالكامل.\n\n"
            "3. المقايضات والتكاليف الحقيقية (Trade-offs):\n   - **تضخم تكلفة إعداد الـ Gradle (Build Configuration Overhead)**: الحاجة لإدارة عشرات ملفات `build.gradle.kts`، وتوحيد إصدارات المكتبات عبر Version Catalogs و Convention Plugins.\n   - **صعوبة التنقل والتواصل بين الشاشات (Navigation & Inter-Module Communication)**: الانتقال بين موديولين لا يعرف أحدهما الآخر يتطلب عقوداً مجردة (Contracts) أو Deep Links بدلاً من مجرد `startActivity(Intent(this, DetailActivity::class.java))`.\n   - **خطر التبعيات الدائرية (Circular Dependencies)** وتضخم الموديولات العامة العشوائية (`:core:common`)."
        ),
        "practical_walkthrough": (
            "مقارنة بين تطبيق متجانس (Monolith) وتطبيق نمطي (Modularized) وتأثيره على وقت البناء:\n"
            "```kotlin\n"
            "// ❌ التطبيق المتجانس (Monolith - :app module only):\n"
            "// أي تعديل في سطر واحد في CheckoutActivity يعيد تجميع الـ 500 كلاس في المشروع بالكامل!\n"
            "// وقت التجميع: 45 ثانية مع كل تعديل بسيط.\n"
            "\n"
            "// ✅ التطبيق النمطي الموزع (Modularized Gradle Architecture):\n"
            "// rootProject/\n"
            "// ├── app/                      // يجمع التطبيق النهائي ويوفر شجرة الـ DI\n"
            "// ├── feature/\n"
            "// │   ├── checkout/             // يعتمد على payment-api فقط\n"
            "// │   └── payment/              // يطبق payment-api داخلياً\n"
            "// └── core/\n"
            "//     ├── designsystem/         // Composables, Colors, Typography\n"
            "//     └── database/             // Room entities & DAOs\n"
            "\n"
            "// في build.gradle.kts الخاص بـ :feature:checkout:\n"
            "dependencies {\n"
            "    implementation(projects.feature.paymentApi) // يعتمد على الواجهة فقط!\n"
            "    implementation(projects.core.designsystem)\n"
            "}\n"
            "// عند تعديل كود الدفع، يعيد Gradle تجميع :feature:payment فقط في 4 ثوانٍ من الـ Build Cache!\n"
            "```"
        ),
        "quick_answer": "Modularization splits a codebase into separate Gradle build units, enforcing strict physical boundaries. It dramatically speeds up incremental builds via parallelism and caching, isolates team ownership, and enforces clean encapsulation. However, it introduces build script maintenance overhead, complicates inter-feature navigation, and risks circular dependencies if poorly designed.",
        "best_answer": (
            "Modularization is the practice of breaking a monolithic application into discrete Gradle subprojects, establishing physical compilation and ownership boundaries.\n\n"
            "Key engineering advantages:\n"
            "1. **Compilation Scalability**: Leverages Gradle parallel execution and build caching. Unmodified modules are fetched directly from the local or remote cache as compiled AARs/JARs, slashing developer feedback loops.\n"
            "2. **Strict Encapsulation & Guardrails**: Internal package details (`internal` visibility) cannot be accessed across Gradle module boundaries. It makes architectural erosion impossible at compile time.\n"
            "3. **Team Autonomy**: Feature teams own designated modules with distinct `CODEOWNERS` rules, eliminating merge contention and decoupling release cadences.\n\n"
            "However, modularization is not free. It introduces significant build logic maintenance overhead, demands centralized convention plugins, complicates inter-feature navigation and dependency injection, and can degrade build configuration times if over-fragmented into hundreds of micro-modules."
        ),
        "deep_answer": (
            "From a build system engineering perspective, modularization impacts the **Gradle Task Graph and Configuration Time**.\n\n"
            "While modularization shrinks execution time for incremental builds, it **increases configuration time**. Gradle must evaluate every `build.gradle.kts` during the configuration phase before tasks can execute. "
            "Without modern optimizations—such as the **Gradle Configuration Cache**, **Isolated Projects**, and avoiding imperative configuration loops (`subprojects { ... }`)—a project with 150+ modules can spend 20+ seconds just configuring before compiling a single file.\n\n"
            "Furthermore, module design directly determines ABI fan-out: if a foundational low-level module (`:core:model`) is declared with `api` instead of `implementation`, a one-line change to an entity forces Gradle to invalidate the cache and recompile every single downstream feature module in the dependency tree."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between a package boundary and a module boundary?",
                "answer": "Package boundaries rely on developer discipline and can be bypassed easily. Gradle module boundaries are enforced at the compiler level; unexported symbols cannot be linked or imported."
            },
            {
                "question": "How does Gradle Configuration Cache impact multi-module builds?",
                "answer": "It caches the result of Gradle's configuration phase, allowing subsequent builds to skip evaluating `build.gradle.kts` files entirely and jump straight to task execution."
            }
        ]
    },
    {
        "id": "MOD-02",
        "arabic_explanation": (
            "مقارنة معمارية شاملة بين أنواع موديولات أندرويد:\n`:app`، و `:feature`، و `:core`، و `:data`، و `:domain`، و `:designsystem`:\n\n"
            "1. `:app` (موديول التجميع النهائي والـ Composition):\n   - الموديول التطبيقي الرئيسي (`com.android.application`).\n   - **وظيفته**: تجميع كل موديولات الـ Features والـ Data، وبناء شجرة الـ Dependency Injection المركزية (Hilt Root)، وإعداد الـ Navigation Graph النهائي وتهيئة الـ Application class. لا يحتوي على أي منطق أعمال (Business Logic).\n\n"
            "2. `:feature:*` (موديولات الميزات والشاشات):\n   - موديولات مكتبية تمثل ميزة مستقلة من منظور المستخدم (مثل `:feature:cart`, `:feature:profile`).\n   - تحتوي على شاشات Compose أو Views، والـ ViewModels، والـ UI State، ومنطق العرض. لا تعتمد ميزات على ميزات أخرى مباشرة.\n\n"
            "3. `:domain:*` (موديول منطق الأعمال الصافي):\n   - موديول Kotlin نقي (Pure JVM Library بدون أي تبعيات Android SDK).\n   - يحتوي على الكيانات النقية (Entities)، ونماذج الأعمال، والـ UseCases، وواجهات الـ Repositories المجردة.\n\n"
            "4. `:data:*` (موديول إدارة البيانات وتطبيق العقود):\n   - يطبق واجهات الـ Repositories المعرفة في الـ Domain.\n   - يتعامل مع مصادر البيانات المحلية (Room) والشبكية (Retrofit) ويحول الـ DTOs إلى Domain Models.\n\n"
            "5. `:core:*` (موديولات البنية التحتية المشتركة):\n   - مكتبات عامة تقدم خدمات منخفضة المستوى مستقلة عن أي ميزة تجارية محددة (مثل `:core:network`, `:core:database`, `:core:datastore`, `:core:analytics`).\n\n"
            "6. `:designsystem` (نظام التصميم الموحد):\n   - موديول يحتوي على مكونات الـ UI المشتركة القابلة لإعادة الاستخدام: الألوان، والخطوط، والـ Buttons، والـ Cards، والـ Dialogs الموحدة للتطبيق، بدون أي منطق أعمال أو ارتباط بـ API."
        ),
        "practical_walkthrough": (
            "اتجاه التبعيات (Dependency Direction) المسموح به بين أنواع الموديولات:\n"
            "```text\n"
            "                     ┌───────────────┐\n"
            "                     │     :app      │ (Application Assembly)\n"
            "                     └───────┬───────┘\n"
            "             ┌───────────────┴───────────────┐\n"
            "             ▼                               ▼\n"
            "   ┌───────────────────┐           ┌───────────────────┐\n"
            "   │ :feature:checkout │           │  :feature:catalog │\n"
            "   └─────────┬─────────┘           └─────────┬─────────┘\n"
            "             │                               │\n"
            "             ├───────────────┬───────────────┤\n"
            "             ▼               ▼               ▼\n"
            "     ┌──────────────┐ ┌──────────────┐ ┌───────────────┐\n"
            "     │ :core:design │ │:domain:order │ │ :core:network │\n"
            "     └──────────────┘ └──────▲───────┘ └───────▲───────┘\n"
            "                             │                 │\n"
            "                      ┌──────┴───────┐         │\n"
            "                      │  :data:order ├─────────┘\n"
            "                      └──────────────┘\n"
            "```\n"
            "قاعدة ذهبية: اتجاه الأسهم دائماً للأسفل باتجاه الاستقرار. لا يمكن لـ :core أو :designsystem أن يعتمد على أي :feature أبداً!"
        ),
        "quick_answer": ":app aggregates modules, wires Hilt DI, and builds the final APK. :feature holds UI screens, ViewModels, and state. :domain contains pure JVM business logic and repository interfaces. :data implements repositories via Room and Retrofit. :core provides low-level infrastructure (network, analytics). :designsystem provides reusable design tokens, typography, and UI widgets without business logic.",
        "best_answer": (
            "A disciplined taxonomy assigns distinct responsibilities and strict dependency rules across module categories:\n\n"
            "1. **`:app`**: The composition root. It applies `com.android.application`, aggregates all feature and data modules, configures the Hilt root component, registers global navigation, and generates the final APK/AAB. It contains zero business logic.\n"
            "2. **`:feature:*`**: User-facing vertical slices (`:feature:login`, `:feature:feed`). Contains UI composables, ViewModels, navigation routes, and presentation state. Features must never depend directly on sibling feature implementation modules.\n"
            "3. **`:domain:*`**: Pure Kotlin/JVM modules without Android framework imports. Houses domain entities, Use Cases, and abstract repository interfaces. It represents the most stable layer of the architecture.\n"
            "4. **`:data:*`**: Implements domain repository contracts using local databases and remote network APIs, encapsulating caching and network resilience.\n"
            "5. **`:core:*`**: Horizontal infrastructure libraries (`:core:network`, `:core:analytics`, `:core:database`) reusable across any feature.\n"
            "6. **`:core:designsystem`**: Houses shared theme tokens (colors, typography, shapes) and stateless reusable UI components (buttons, headers, empty states). It must remain strictly agnostic of business domains."
        ),
        "deep_answer": (
            "When enforcing module boundaries in enterprise codebases, architects use **dependency analysis tools (like Dependency Analysis Gradle Plugin)** and custom lint checks to enforce directional contracts:\n\n"
            "- **Rule 1 (The Gravity Rule)**: Dependencies only flow downward toward higher stability. A low-level module like `:core:designsystem` or `:core:network` must **NEVER** import a `:feature` module. Doing so inverts the architecture and causes instant cyclic dependency locks.\n"
            "- **Rule 2 (Domain Purity)**: The `:domain` module should use the standard `kotlin(\"jvm\")` plugin rather than `com.android.library`. This guarantees that Android framework dependencies (like `android.content.Context` or `android.os.Bundle`) cannot compile inside domain logic, keeping business rules testable on local JVMs in single-digit milliseconds.\n"
            "- **Rule 3 (Data Encapsulation)**: DAOs, Retrofit interfaces, and Room entities are `internal` to the `:data` module. Features only see domain repository interfaces."
        ),
        "follow_ups": [
            {
                "question": "Why should `:core:designsystem` never contain business models?",
                "answer": "Because it turns the design system into a coupled monolith. A user profile card in designsystem should accept primitive properties (`name: String`, `avatarUrl: String`), not a domain `User` entity."
            },
            {
                "question": "Can a `:feature` module depend on multiple `:domain` modules?",
                "answer": "Yes. A feature (such as checkout) may need domain rules from `:domain:cart`, `:domain:payment`, and `:domain:user`."
            }
        ]
    },
    {
        "id": "MOD-03",
        "arabic_explanation": (
            "ما هو الـ Dependency Graph (الرسم البياني للتبعيات) في Gradle، ولماذا يجب أن يكون خاليًا تمامًا من الحلقات (Acyclic - DAG)؟\n\n"
            "1. المفهوم الرياضي:\n   - في Gradle، تمثل الموديولات **الرؤوس (Vertices / Nodes)**، وتمثل علاقات الاعتماد `implementation(projects.core.network)` **الحواف الموجهة (Directed Edges)**.\n   - الرسم البياني يجب أن يكون **Directed Acyclic Graph (DAG)**؛ أي رسم بياني موجه بدون أي دورات أو حلقات دائرية مغلقة.\n\n"
            "2. لماذا يمنع Gradle التبعيات الدائرية (Circular Dependencies) بشكل قاطع؟\n   - **استحالة الترتيب الطوبولوجي للتجميع (Topological Sort Failure)**: لكي يقوم المترجم (Kotlin Compiler / javac) بتجميع الموديول B، يجب أن ينتهي أولاً من تجميع الموديول A الذي يعتمد عليه B. إذا كان A يعتمد بدوره على B، يدخل نظام البناء في حلقة مغلقة مستحيلة (Deadlock): من الذي يُجمع أولاً؟!\n   - يرفض Gradle التجميع فوراً مع الخطأ الشهير: `Circular dependency between the following tasks: ...`.\n\n"
            "3. كيف تحل التبعية الدائرية الواقعية بين موديولين؟\n   - لنفترض أن `:feature:cart` يحتاج كلاس من `:feature:checkout`، وفي نفس الوقت `:feature:checkout` يحتاج كلاس من `:feature:cart`.\n   - **الحل المعماري الصحيح (Extract Shared Contract / API Module)**:\n     * استخراج الواجهات والبيانات المشتركة إلى موديول ثالث مستقل ومحايد (مثل `:feature:cart-api` أو `:core:model`).\n     * الآن، يعتمد كلا الموديولين على الموديول الثالث في اتجاه واحد للأسفل، وتختفي الدورة تماماً!"
        ),
        "practical_walkthrough": (
            "حل التبعية الدائرية باستخراج موديول وسيط للعقود المشتركة (API Extraction):\n"
            "```text\n"
            "❌ دورة دائرية مستحيلة تمنع البناء:\n"
            ":feature:cart ──────(depends on)─────► :feature:checkout\n"
            "     ▲                                       │\n"
            "     └──────────────(depends on)─────────────┘\n"
            "[Gradle Error: Circular dependency between :feature:cart and :feature:checkout!]\n"
            "\n"
            "✅ الحل المعماري باستخراج موديول عقد مستقل (:feature:cart-api):\n"
            "         :feature:cart                  :feature:checkout\n"
            "               │                                │\n"
            "               │ (implements)                   │ (consumes)\n"
            "               ▼                                ▼\n"
            "         ┌──────────────────────────────────────────────┐\n"
            "         │             :feature:cart-api                │\n"
            "         │ (Interfaces, Route contracts, Shared DTOs)   │\n"
            "         └──────────────────────────────────────────────┘\n"
            "الرسم البياني أصبح DAG نقي خالي من أي حلقات دائرية، ويتم تجميعه بنجاح وبسرعة!\n"
            "```"
        ),
        "quick_answer": "A dependency graph models modules as nodes and dependencies as directed edges. It must be a Directed Acyclic Graph (DAG) because Gradle relies on topological sorting to determine compilation order. A cycle (A depends on B, B depends on A) causes an unresolvable compiler deadlock, which is resolved by extracting shared interfaces into a separate API module.",
        "best_answer": (
            "In Gradle, the project architecture is modeled as a Directed Graph where modules are nodes and project dependencies (`implementation(projects.foo)`) form directed edges.\n\n"
            "The graph **must strictly be acyclic (a DAG)** because the compiler requires a deterministic **Topological Sort** to establish the build order:\n"
            "1. If module `B` depends on `A`, `A` must compile into bytecode, package its public ABI, and expose it on `B`'s compile classpath before `B` can even begin parsing code.\n"
            "2. If a cycle exists (`A -> B -> A`), an impossible paradox occurs: neither module can compile before the other. Gradle terminates build graph evaluation immediately with a `CircularDependencyException`.\n\n"
            "To resolve circular dependencies in production, never hack around it with reflection. Apply the **Dependency Inversion Principle**: extract the shared interfaces, routes, and data models into a lightweight `:feature:x-api` module. Both modules then depend downward on the API module, breaking the cycle."
        ),
        "deep_answer": (
            "Cycles do not only occur between Gradle modules; they frequently occur as **transitive classpath cycles and task dependency cycles**.\n\n"
            "For example, if `:app` has a custom task that packages assets generated by a downstream module, and that downstream module has a task that reads resources from `:app`, Gradle's task execution engine deadlocks.\n\n"
            "In enterprise Android repositories with dozens of engineers, teams use automated architectural enforcement plugins like **Graphite** or **Gradle Dependency Guard** in CI. "
            "These tools inspect the project DAG on every pull request, calculating graph metrics such as **Longest Critical Path (Depth)** and **Module Fan-in / Fan-out**. "
            "If an engineer attempts to introduce an unauthorized cross-feature edge or creates a dependency cycle, the CI pipeline blocks the PR before code ever merges to main."
        ),
        "follow_ups": [
            {
                "question": "How does graph depth affect build times?",
                "answer": "A deep linear graph (A -> B -> C -> D) forces sequential compilation, preventing Gradle from utilizing multiple CPU cores in parallel. A flatter, balanced tree allows massive parallel builds."
            },
            {
                "question": "Can two classes inside the same Gradle module depend cyclically on each other?",
                "answer": "Yes, the Kotlin/Java compiler compiles all files within a single module together in one batch. However, class-level cycles remain a serious code smell."
            }
        ]
    },
    {
        "id": "MOD-04",
        "arabic_explanation": (
            "ما هو التماسك العالي (High Cohesion) والاقتران المنخفض (Low Coupling) في سياق معمارية موديولات Android؟\n\n"
            "1. التماسك العالي (High Cohesion - الارتباط الوثيق داخلياً):\n   - يعني أن جميع الكلاسات والدوال داخل الموديول الواحد تعمل معاً لخدمة **مسؤولية واحدة واضحة ومحددة (Single Cohesive Responsibility)**.\n   - **مثال لموديول عالي التماسك**: `:core:network` يحتوي فقط على إعدادات الـ HttpClient، والـ Interceptors، والـ SSL Pinning، وإدارة الـ WebSockets. كل كود فيه يخدم الاتصال بالشبكة.\n   - **مثال لموديول منخفض التماسك (Low Cohesion - كارثي)**: موديول يسمى `:core:utils` أو `:common` يحتوي على كود لتحميل الصور، وكود لحساب الضرائب، وكود لتنسيق التواريخ، ودوال للتعامل مع البلوتوث! الكلاسات داخله لا رابط منطقي بينها.\n\n"
            "2. الاقتران المنخفض (Low Coupling - قلة الاعتمادية خارجياً):\n   - يعني أن الموديول مستقل بذاته قدر الإمكان، ويعتمد على أقل عدد ممكن من الموديولات الخارجية، ويفصل تعاملاته عبر واجهات مجردة (Abstract Contracts).\n   - إذا أردت تعديل أو إعادة كتابة كود موديول `:feature:auth`، يجب ألا يؤثر ذلك أو يتطلب أي تعديل في موديول `:feature:cart`.\n\n"
            "3. القاعدة الهندسية:\n   - **High Cohesion** يجعل الموديول سهل الفهم، والصيانة، والاختبار.\n   - **Low Coupling** يجعل النظام مرناً، ويقلل من تسرب الأخطاء عند التعديل، ويسرع أوقات التجميع عبر تقليل تشابك شجرة التبعيات."
        ),
        "practical_walkthrough": (
            "المقارنة بين تصميم منخفض التماسك ومقترن بشدة وتصميم متماسك عالي ومنخفض الاقتران:\n"
            "```kotlin\n"
            "// ❌ تصميم كارثي: Low Cohesion + High Coupling في موديول عشوائي (:core:common):\n"
            "// يحتوي على كود ضرائب، وشاشات، وشبكة مخلطة في مكان واحد:\n"
            "class CommonUtils {\n"
            "    fun formatPrice(amount: Double): String = \"$$amount\"\n"
            "    fun parseJwtToken(token: String): JwtClaims = ... // منطق أمان!\n"
            "    fun calculateShipping(weight: Double, distance: Int): Double = ... // منطق مالي للشحن!\n"
            "}\n"
            "// أي موديول يستورد CommonUtils يرتبط تلقائياً بكل هذه التبعيات غير الضرورية!\n"
            "\n"
            "// ✅ تصميم معماري راقٍ: High Cohesion + Low Coupling:\n"
            "// 📁 في موديول :domain:pricing (High Cohesion: متخصص في التسعير فقط):\n"
            "class PriceCalculator @Inject constructor(private val currencyFormatter: CurrencyFormatter) {\n"
            "    fun calculateFinalTotal(items: List<CartItem>, taxRate: Double): Money = ...\n"
            "}\n"
            "\n"
            "// 📁 في موديول :core:auth (High Cohesion: متخصص في التحقق فقط):\n"
            "class TokenParser @Inject constructor() {\n"
            "    fun parse(rawToken: String): Result<AuthSession> = ...\n"
            "}\n"
            "// الموديولات لا تعتمد على بعضها إطلاقاً (Low Coupling)! كلاهما قابل لإعادة الاستخدام والاختبار في معزل.\n"
            "```"
        ),
        "quick_answer": "High cohesion means elements inside a module belong together and serve a single, unified purpose. Low coupling means modules maintain minimal dependencies on each other, interacting through stable abstract contracts. Together, they isolate changes, prevent ripple effects across features, and optimize build caching.",
        "best_answer": (
            "Cohesion and coupling are the twin pillars of sustainable software architecture, applied directly at the Gradle module level:\n\n"
            "1. **High Cohesion (Inside the Module)**: All components within a module change for the same business reason and serve a tightly focused domain responsibility. For example, `:feature:search` contains only query processing, search results UI, and recent searches storage. If a module contains auth helpers, date formatters, and payment models, it suffers from low cohesion and becomes an unmaintainable junk drawer.\n\n"
            "2. **Low Coupling (Between Modules)**: Modules minimize their knowledge of and dependencies on other modules. Instead of depending on concrete implementations or peer feature modules, they interact across clean boundaries using dependency inversion and API contracts.\n\n"
            "Architecturally, high cohesion ensures that when a feature changes, developers only modify files within that single module. Low coupling ensures that changes made inside that module never trigger unexpected regressions or recompilations in other modules."
        ),
        "deep_answer": (
            "A common architectural trap in Android modularization is **False Cohesion through Over-sharing**.\n\n"
            "Teams often create a `:core:common` module containing utility extension functions, custom views, and network DTOs. Developers assume this is 'high reuse'. In reality, `:core:common` exhibits **extremely low cohesion and catastrophic high coupling**—every feature module imports it. When an engineer modifies a string utility in `:core:common`, the ABI change invalidates the build cache for 100% of the downstream feature modules.\n\n"
            "To achieve true high cohesion and low coupling:\n"
            "- Break `:core:common` into hyper-focused modules: `:core:model`, `:core:network`, `:core:ui`.\n"
            "- Tolerate minor duplication of trivial helper functions (e.g., 2 lines of string formatting) rather than introducing a global shared dependency that couples otherwise independent features."
        ),
        "follow_ups": [
            {
                "question": "Is zero coupling achievable between two features?",
                "answer": "Yes, at compile time! Feature A and Feature B can communicate via deep link navigation URLs or event buses registered in the :app module without any compile-time dependency between them."
            },
            {
                "question": "What is the danger of prioritizing DRY (Don't Repeat Yourself) over Low Coupling?",
                "answer": "Coupling unrelated modules to share a 3-line utility creates tight build and architectural coupling that costs far more in maintenance and build time than harmless code duplication."
            }
        ]
    },
    {
        "id": "MOD-05",
        "arabic_explanation": (
            "المقارنة الجوهرية بين `api` و `implementation` في Gradle وكيف تؤثران على وقت البناء والـ ABI:\n\n"
            "1. ما هو الفرق الأساسي؟\n   - **`implementation` (خاص بالداخل)**: التبعية متاحة فقط للموديول الحالي أثناء التجميع (Compile Classpath). الموديولات التي تعتمد على هذا الموديول **لا ترى** هذه التبعية ولا تستطيع استيرادها.\n   - **`api` (مكشوف للجميع - Transitive Exposure)**: التبعية مكشوفة في الواجهة العامة للـ Module (الـ Public ABI). أي موديول يعتمد على هذا الموديول يرث هذه التبعية تلقائياً في الـ Compile Classpath الخاص به.\n\n"
            "2. الأثر الكارثي لـ `api` على وقت البناء (Build Fan-out):\n   - لنفترض أن Module C يعتمد على B، و B يعتمد على A.\n   - إذا استخدم B كلمة `implementation(A)`: عند تغيير كود داخلي في A، يقوم Gradle بتجميع A ثم B فقط. الموديول C لا يعاد تجميعه لأن الـ ABI الخاص بـ B لم يتغير!\n   - إذا استخدم B كلمة `api(A)`: أي تغيير في A يكسر الـ ABI الخاص بـ B، مما يجبر Gradle على إعادة تجميع B و C وجميع الموديولات التابعة لهما في المشروع بالكامل!\n\n"
            "3. القاعدة الذهبية لمهندس البرمجيات الأول (Senior Rule of Thumb):\n   - **اجعل `implementation` هو الخيار الافتراضي دائماً في 99% من الحالات**.\n   - استخدم `api` فقط وفقط إذا كانت كلاسات ودوال الموديول الحالي تُرجع أو تقبل كائنات من التبعية في دوالها العامة (Public Functions or Return Types)."
        ),
        "practical_walkthrough": (
            "المقارنة العملية لتأثير `api` مقابل `implementation` على الـ Classpath ووقت البناء:\n"
            "```kotlin\n"
            "// 📁 في موديول ':data:user' build.gradle.kts:\n"
            "dependencies {\n"
            "    // ✅ استخدام implementation: Retrofit تفصيل داخلي لا يجب أن يراه الـ UI:\n"
            "    implementation(libs.retrofit)\n"
            "    \n"
            "    // لو استخدمنا api(libs.retrofit):\n"
            "    // أي موديول يعتمد على :data:user سيستورد Retrofit تلقائياً،\n"
            "    // ولو غيرنا نسخة Retrofit، سيعيد تجميع كل الـ Feature Modules في التطبيق!\n"
            "}\n"
            "\n"
            "// 📁 متى يكون استخدام api مبرراً وإلزامياً؟\n"
            "// في موديول ':core:designsystem' build.gradle.kts:\n"
            "dependencies {\n"
            "    // بما أن موديول الـ Design System يُصدر Composables تعتمد مباشرة على Compose UI:\n"
            "    api(libs.androidx.compose.ui)\n"
            "    api(libs.androidx.compose.material3)\n"
            "}\n"
            "// هنا مبرر لأن أي شاشة تستخدم DesignSystem تحتاج تلقائياً كائنات Compose UI في شاشاتها.\n"
            "```"
        ),
        "quick_answer": "implementation keeps a dependency private to the module's compile classpath, hiding internal transitive types and preventing downstream recompilations when internals change. api exposes the dependency transitively to all consumers, polluting their classpaths and forcing costly rebuild cascades across all downstream modules.",
        "best_answer": (
            "The difference between `api` and `implementation` in Gradle determines whether a dependency leaks into the consumer's compile classpath:\n\n"
            "1. **`implementation` (Default Choice)**: The dependency is present on the compile classpath of the current module and on the runtime classpath of consumers, but **hidden from the compile classpath of consumers**. If module `B` uses `implementation(A)`, module `C` depending on `B` cannot reference types from `A`. This enforces strict encapsulation and dramatically accelerates incremental compilation.\n\n"
            "2. **`api` (Public ABI Exposure)**: Transitively exposes the dependency to any module that depends on this module. If `B` declares `api(A)`, `C` can import symbols from `A` directly.\n\n"
            "The golden architectural rule: use `implementation` by default. Only promote a dependency to `api` if its types appear directly in the module's public function parameters, return types, or inherited interfaces (part of its public Application Binary Interface - ABI)."
        ),
        "deep_answer": (
            "Under the hood, Gradle distinguishes between a module's **Compile Classpath** and its **Runtime Classpath**, optimizing builds via **ABI (Application Binary Interface) hashing**.\n\n"
            "When Gradle compiles a module, it generates an ABI hash representing only public and protected method signatures, return types, and fields. Method implementation bodies (private logic inside a function) do not change the ABI hash.\n\n"
            "- When module `B` uses `implementation(A)`, Gradle excludes `A` from `C`'s compile classpath. If a developer changes private code inside `A`, `A` recompiles, but `B`'s ABI remains unchanged, and Gradle completely skips recompiling `C`.\n"
            "- When `B` uses `api(A)`, `A` is part of `B`'s public interface. Any ABI change in `A` invalidates the ABI of `B`, triggering a massive recompile cascade across the entire downstream dependency tree.\n\n"
            "Using `implementation` isolates compile boundaries, maximizes Gradle's `UP-TO-DATE` task checks, and keeps developer build loops lightning-fast."
        ),
        "follow_ups": [
            {
                "question": "What happens if you use a type from an `implementation` dependency in a public function?",
                "answer": "The Kotlin/Java compiler will throw an error or warning because downstream consumers cannot resolve the public signature on their compile classpath."
            },
            {
                "question": "Does `implementation` reduce APK final size compared to `api`?",
                "answer": "No. Both configurations bundle the library into the final APK's runtime classpath. The advantage of `implementation` is strictly compile-time isolation and build speed."
            }
        ]
    },
    {
        "id": "MOD-06",
        "arabic_explanation": (
            "ما هي موديولات الميزات الديناميكية (Dynamic Feature Modules - DFMs) و Play Feature Delivery في Android؟\n\n"
            "1. المفهوم والهدف الأساسي:\n   - في الوضع الطبيعي، يتم تنزيل التطبيق ككتلة واحدة بجميع شاشاته وميزاته عند تثبيته من Google Play.\n   - **Dynamic Feature Modules (DFMs)**: تتيح تجزئة التطبيق إلى أجزاء منفصلة يتم تنزيلها عند الطلب (On-Demand Delivery) أو تنزيلها بشروط معينة (Conditional Delivery بناءً على الدولة أو العتاد).\n   - **أمثلة واقعية**: ميزة الواقع المعزز (AR Mode) في تطبيق تجارة إلكترونية، أو ميزة مسح المستندات بـ OCR، أو ميزة دعم العملاء عبر الفيديو.\n\n"
            "2. أنواع تسليم الميزات في Play Feature Delivery:\n   - **Install-time**: يتم تنزيله تلقائياً مع التطبيق الأساسي ولكنه مقسم في APK Split مستقل.\n   - **On-demand**: لا يُنزل مع التطبيق! عند ضغط المستخدم على زر 'تجربة الواقع المعزز'، يقوم التطبيق بطلب التنزيل من Google Play عبر `SplitInstallManager` وعرض شريط تقدم للمستخدم.\n   - **Conditional**: يتم تنزيله فقط للأجهزة التي تدعم إمكانيات عتادية محددة (مثل توافر مستشعر معين أو في بلدان محددة).\n\n"
            "3. التحديات والمخاطر الهندسية:\n   - **انعكاس التبعية (Inverted Dependency)**: الـ DFM يعتمد على `:app`، بينما `:app` لا يعتمد عليه، مما يعقد الـ DI والـ Navigation.\n   - **فشل التنزيل في وضع عدم الاتصال (Offline & Network Failures)**: ماذا لو انقطع النت أثناء تنزيل الميزة؟ يجب تصميم تجربة مستخدم تعالج الفشل وإعادة المحاولة بأمان."
        ),
        "practical_walkthrough": (
            "كيفية طلب تنزيل ميزة ديناميكية عند الطلب باستخدام SplitInstallManager:\n"
            "```kotlin\n"
            "class DynamicFeatureLauncher(private val context: Context) {\n"
            "    private val splitInstallManager = SplitInstallManagerFactory.create(context)\n"
            "\n"
            "    fun launchAugmentedRealityFeature(onReady: () -> Unit, onError: (String) -> Unit) {\n"
            "        val moduleName = \"feature_augmented_reality\"\n"
            "\n"
            "        // 1. التحقق مما إذا كانت الميزة مثبتة مسبقاً:\n"
            "        if (splitInstallManager.installedModules.contains(moduleName)) {\n"
            "            onReady()\n"
            "            return\n"
            "        }\n"
            "\n"
            "        // 2. طلب التنزيل من Google Play عند الطلب (On-Demand Request):\n"
            "        val request = SplitInstallRequest.newBuilder()\n"
            "            .addModule(moduleName)\n"
            "            .build()\n"
            "\n"
            "        splitInstallManager.startInstall(request)\n"
            "            .addOnSuccessListener { sessionId ->\n"
            "                // الاستماع لحالة التنزيل والتثبيت عبر SplitInstallStateUpdatedListener\n"
            "            }\n"
            "            .addOnFailureListener { exception ->\n"
            "                onError(exception.localizedMessage ?: \"Download failed\")\n"
            "            }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Dynamic Feature Modules enable modular delivery via Android App Bundles, downloading non-critical features on-demand after initial app install. They reduce initial APK download size, support conditional delivery by country or hardware, but introduce inverted dependencies, runtime download failure handling, and classloader complexity.",
        "best_answer": (
            "Dynamic Feature Modules (DFMs) leverage Google Play Feature Delivery to modularize app distribution rather than just code compilation.\n\n"
            "Key mechanisms:\n"
            "1. **Delivery Modes**: Modules can be configured as **Install-time** (packaged as separate splits), **On-demand** (downloaded in the background only when the user triggers that specific flow), or **Conditional** (installed based on user country, minimum SDK, or hardware device features like camera sensors).\n"
            "2. **Initial Download Reduction**: Heavy, infrequently used features—such as KYC facial scanning, AR viewers, or complex PDF report generators—are removed from the base APK, significantly boosting Play Store install conversion rates by reducing initial download size.\n\n"
            "However, DFMs introduce serious engineering complexity: Gradle dependencies are inverted (`:dfm` depends on `:app`), feature access requires asynchronous download UI states via `SplitInstallManager`, and features cannot be accessed offline if they haven't been downloaded yet."
        ),
        "deep_answer": (
            "Under the hood, dynamic delivery relies on **Android APK Splits and SplitCompat**.\n\n"
            "When Google Play installs a base APK on Android 5.0+ (API 21+), the OS mounts additional split APKs directly into the application process. "
            "However, when a split is installed dynamically while the app process is **already running**, Android cannot automatically update the running app's classloader and asset path. "
            "Developers must call `SplitCompat.installActivity(context)` inside the Activity's `attachBaseContext()` to merge the newly downloaded split's Dex files and native `.so` libraries into the live ClassLoader.\n\n"
            "Furthermore, navigation to DFMs cannot use direct Kotlin class references (`Intent(this, DfmActivity::class.java)`), because `:app` does not have compile-time visibility of `:dfm`. Instead, you must navigate via explicit class reflection, string deep links, or Android Jetpack Navigation dynamic feature artifacts."
        ),
        "follow_ups": [
            {
                "question": "What happens if a user is offline when attempting to open an on-demand dynamic feature?",
                "answer": "The installation request will fail immediately; the UI must gracefully display an offline warning and prevent the flow from crashing."
            },
            {
                "question": "Can Dynamic Feature Modules contain native C/C++ libraries?",
                "answer": "Yes, native `.so` libraries in DFMs are packaged inside the split APK and dynamically linked when SplitCompat installs the module."
            }
        ]
    },
    {
        "id": "MOD-07",
        "arabic_explanation": (
            "كيف تصمم هيكل نمطي متكامل (Multi-Module Architecture) لتطبيق Android ضخم الحجم؟\n\n"
            "1. المخطط المعماري الهرمي الموصى به (The Recommended Layered Graph):\n   - **`:app` (Root Composition)**: موديول خفيف جداً يجمع شجرة الـ DI والـ Navigation والـ Application Class.\n   - **`:features` (Vertical Slices)**: مقسمة بنمط API/Impl لكل ميزة:\n     * `:feature:auth:api` (عقود، مسارات، واجهات فقط)\n     * `:feature:auth:impl` (الشاشات، الـ ViewModels، والتنفيذ الفعلي)\n     * `:feature:checkout:api` و `:feature:checkout:impl`\n   - **`:core` (Horizontal Slices)**: خدمات البنية التحتية المشتركة:\n     * `:core:designsystem` (الألوان، الخطوط، المكونات الرسومية)\n     * `:core:network` (Retrofit, OkHttp, SSL Pinning)\n     * `:core:database` (Room database, migrations)\n     * `:core:analytics` (تتبع الأحداث)\n     * `:core:model` (نماذج البيانات المشتركة النظيفة)\n\n"
            "2. قواعد التحكم في شجرة التبعيات:\n   - موديولات الـ Feature لا تعتمد على موديولات Feature أخرى إطلاقاً؛ بل تعتمد فقط على الـ `:api` موديول للميزة المطلوبة.\n   - موديولات الـ `:core` لا تعتمد على أي موديول Feature في أي حال من الأحوال.\n   - استخدام Version Catalogs (`libs.versions.toml`) و Convention Plugins لتوحيد إعدادات Gradle لجميع الموديولات."
        ),
        "practical_walkthrough": (
            "الهيكل التنظيمي للموديولات في مشروع حقيقي واسع النطاق:\n"
            "```text\n"
            "MyEnterpriseApp/\n"
            "├── app/                           // Final packaging, Hilt root, NavHost\n"
            "├── build-logic/                   // Custom Gradle Convention Plugins\n"
            "├── core/\n"
            "│   ├── designsystem/              // Material3 tokens, Custom Buttons, Theme\n"
            "│   ├── network/                   // OkHttp, Retrofit, Auth Interceptors\n"
            "│   ├── database/                  // Room Database, DAOs\n"
            "│   ├── model/                     // Immutable shared data classes (User, Money)\n"
            "│   └── testing/                   // Test rules, Fake repositories\n"
            "└── feature/\n"
            "    ├── feed/\n"
            "    │   ├── api/                   // FeedNavigationContract, FeedEntryRoute\n"
            "    │   └── impl/                  // FeedScreen, FeedViewModel, FeedPagingSource\n"
            "    └── cart/\n"
            "        ├── api/                   // CartBadgeContract, AddToCartUseCase\n"
            "        └── impl/                  // CartScreen, CartViewModel\n"
            "```\n"
            "كل ميزة مفصولة إلى API و Implementation، مما يضمن سرعة خرافية في الـ Incremental Compilation وعزل تام بين الفرق!"
        ),
        "quick_answer": "Design a large-scale app using a layered DAG: an assembly :app module, feature modules split into :feature:x:api (contracts) and :feature:x:impl (screens/logic), horizontal :core infrastructure (network, database, designsystem), and centralized build-logic convention plugins with a Version Catalog.",
        "best_answer": (
            "A production-grade multi-module architecture for an enterprise Android app balances compilation speed, encapsulation, and team velocity:\n\n"
            "1. **Layered Module Architecture**:\n   - **`:app`**: Thin composition root. Assembles the final APK, provisions Hilt graph roots, and attaches top-level navigation graphs.\n   - **`:feature:*:impl`**: Contains UI Composables, ViewModels, and internal presentation logic. Feature implementations never depend directly on sibling feature implementations.\n   - **`:feature:*:api`**: Lightweight contract modules containing only navigation routes, shared events, and public interfaces. Features interact exclusively through peer API modules.\n   - **`:core:*`**: Horizontal foundations (`:core:designsystem`, `:core:network`, `:core:database`, `:core:model`, `:core:analytics`).\n\n"
            "2. **Standardized Build Governance**:\n   - Centralized dependency coordinates via `libs.versions.toml`.\n   - Custom Gradle Convention Plugins in `build-logic` (`android.library`, `android.feature`, `android.compose`) to eliminate 95% of boilerplate from individual `build.gradle.kts` files."
        ),
        "deep_answer": (
            "A critical pitfall in large-scale modularization is **Uncontrolled Micro-Modularization** (creating 300+ tiny modules for single classes).\n\n"
            "Every Gradle module introduces overhead: configuration evaluation time, IDE indexing load, and task scheduling overhead. If modules are too granular, cold build times and Android Studio sync times explode.\n\n"
            "To maintain an optimal balance:\n"
            "- Extract a module only when there is a **real compile boundary** (independent team ownership, distinct release cycle, or high rebuild frequency).\n"
            "- Use the `:api` / `:impl` split primarily for high-traffic features that multiple teams interact with, rather than dogmatically splitting every trivial screen.\n"
            "- Implement continuous CI graph validation (enforcing no feature-to-feature direct implementation dependencies) to protect the DAG from accidental erosion."
        ),
        "follow_ups": [
            {
                "question": "What is the primary benefit of the `:api` vs `:impl` module split?",
                "answer": "It minimizes rebuild cascades: modifying code inside `:impl` does not recompile other modules that only depend on the stable `:api` contract."
            },
            {
                "question": "How do feature modules navigate to each other without depending on `:impl`?",
                "answer": "They navigate using route contracts or destinations defined in peer `:api` modules, resolved at runtime by the root navigation graph in `:app`."
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

    for item in MOD_01_07:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions MOD-01 to MOD-07. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
