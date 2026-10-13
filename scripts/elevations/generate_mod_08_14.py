#!/usr/bin/env python3
"""Generator for MOD-08 through MOD-14 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "mod.json"

MOD_08_14 = [
    {
        "id": "MOD-08",
        "arabic_explanation": (
            "ما هي المسؤوليات الدقيقة التي تنتمي لكل من: `:core:network`، و `:core:database`، و `:core:ui`، و `:feature`؟ وكيف تمنع تسرب المنطق؟\n\n"
            "1. `:core:network` (البنية التحتية للاتصال بالشبكة):\n   - **ما ينتمي إليه**: إعدادات `OkHttpClient`, محولات `Retrofit`, إدارة شهادات الأمان و SSL Pinning, الـ Auth Interceptors لإرفاق الـ Bearer Tokens, ومتابعة جودة الاتصال وتحديث الـ Base URL.\n   - **ما لا ينتمي إليه (خطر التسريب)**: نماذج بيانات خاصة بميزة تجارية معينة (مثل `CartResponse` أو `OrderDto`). هذه النماذج تنتمي لموديول بيانات الميزة نفسها (`:data:cart` أو `:data:order`).\n\n"
            "2. `:core:database` (البنية التحتية لقاعدة البيانات المحلية):\n   - **ما ينتمي إليه**: بناء كائن `RoomDatabase` الرئيسي، وإدارة الـ TypeConverters العامة، واستراتيجيات التشفير (SQLCipher)، وتنفيذ قواعد الترقية (Database Migrations).\n   - **ما لا ينتمي إليه**: استعلامات الـ SQL الخاصة بشاشات معينة أو الـ DAOs المحددة للميزات.\n\n"
            "3. `:core:ui` / `:core:designsystem` (مكونات الواجهة المشتركة):\n   - **ما ينتمي إليه**: ألوان التطبيق (Color Palette), الخطوط (Typography), الأشكال (Shapes), وأزرار عامة وحقول إدخال ومكونات عرض خالية من المنطق التجاري.\n   - **ما لا ينتمي إليه**: بطاقات عرض تعتمد على موديل تجاري (مثل بطاقة عرض المنتج `ProductCard` التي تعتمد على `ProductEntity`). يجب أن تأخذ المكونات بيانات بدائية (Primitives).\n\n"
            "4. `:feature:*` (موديولات الميزات المستقلة):\n   - **ما ينتمي إليه**: واجهات العرض (Composables/Screens), الـ ViewModels, الـ UI State, والـ Navigation Routes الخاصة بالميزة فقط."
        ),
        "practical_walkthrough": (
            "تنظيم المسؤوليات ومنع تسريب منطق الميزات إلى موديولات الـ Core:\n"
            "```kotlin\n"
            "// ❌ تسريب خاطئ: وضع كود منتج تجاري داخل :core:ui:\n"
            "// في موديول :core:ui:\n"
            "@Composable\n"
            "fun ProductCard(product: ProductDomainModel) { /* ... */ }\n"
            "// خطأ! جعلت :core:ui يعتمد على موديل تجاري في :domain:product!\n"
            "\n"
            "// ✅ التصميم النظيف: :core:ui يعتمد فقط على عناصر بدائية (Stateless Primitives):\n"
            "// في موديول :core:ui:\n"
            "@Composable\n"
            "fun StandardMediaCard(\n"
            "    title: String,\n"
            "    subtitle: String,\n"
            "    imageUrl: String,\n"
            "    onClick: () -> Unit\n"
            ") {\n"
            "    Card(...) { /* رسم عام بدون أي اعتماد على أي موديل تجاري */ }\n"
            "}\n"
            "\n"
            "// 📁 في موديول :feature:catalog:\n"
            "@Composable\n"
            "fun CatalogProductItem(product: Product, onSelect: () -> Unit) {\n"
            "    // الميزة هي التي تمرر البيانات للمكون العام في :core:ui:\n"
            "    StandardMediaCard(\n"
            "        title = product.name,\n"
            "        subtitle = product.formattedPrice,\n"
            "        imageUrl = product.imageUrl,\n"
            "        onClick = onSelect\n"
            "    )\n"
            "}\n"
            "```"
        ),
        "quick_answer": ":core:network owns network infrastructure (OkHttp, SSL, Retrofit engine, auth interceptors). :core:database owns the Room database container and migrations. :core:ui owns stateless design tokens and generic widgets. Feature modules own user-facing screens, ViewModels, and presentation state, ensuring zero business domain models leak into core foundations.",
        "best_answer": (
            "Clear architectural separation between infrastructure core modules and domain feature modules prevents the core from degrading into an unmaintainable monolith:\n\n"
            "1. **`:core:network`**: Houses HTTP client engines (`OkHttpClient`), token refresh interceptors, SSL pinning configurations, and connectivity observers. It must **not** host feature-specific API endpoints (like `OrderApiService`); feature APIs belong in their respective `:data:*` modules.\n"
            "2. **`:core:database`**: Manages the underlying database engine (`RoomDatabase`), encryption keys, and schema migration coordinators. Feature-specific DAOs and entities should be provided by data modules and aggregated by the database.\n"
            "3. **`:core:ui` (Design System)**: Contains design tokens (theme colors, typography, elevations) and generic, stateless UI primitives (`AppButton`, `EmptyStateView`, `AppDialog`). It must remain strictly agnostic of business models, accepting only primitive parameters.\n"
            "4. **`:feature:*`**: Contains end-to-end presentation logic for a user journey: composable screens, ViewModels, UI state machines, and local navigation routes."
        ),
        "deep_answer": (
            "A critical design challenge in multi-module database architecture is **Room Database Aggregation**.\n\n"
            "Room requires its `@Database(entities = [...], version = ...)` annotation to enumerate all entity classes at compile time. "
            "If entities live inside feature modules, having `:core:database` declare the database directly creates an illegal circular dependency (core depending on features).\n\n"
            "Senior engineers resolve this in one of two ways:\n"
            "1. **Entity Delegation in `:core:database`**: Entities live in `:core:model` or dedicated `:data:*:model` modules that `:core:database` imports, keeping DAOs internal to their data modules.\n"
            "2. **Single Database in `:app`**: The concrete `@Database` class is declared inside the `:app` module (where all feature data modules are already aggregated), while `:core:database` provides only the database builder infrastructure and migrations."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't an Auth Token interceptor live in a feature module?",
                "answer": "Because all network requests across all feature modules need authentication; centralizing token refresh in `:core:network` avoids duplicate or conflicting token states."
            },
            {
                "question": "Can a feature module have its own separate Room Database?",
                "answer": "Yes, if the feature's data is completely independent and offline-contained, a separate SQLite file is often cleaner than a single shared database."
            }
        ]
    },
    {
        "id": "MOD-09",
        "arabic_explanation": (
            "كيف تتواصل موديولات الميزات (Feature Modules) مع بعضها البعض دون وجود اقتران مباشر (Direct Coupling) بينها؟\n\n"
            "1. التحدي الأساسي:\n   - في بنية الـ Multi-Module النظيفة، موديول `:feature:feed` لا يستطيع استيراد أي كلاس من `:feature:profile` أو `:feature:cart` (لا توجد تبعية `implementation(projects.feature.cart)`).\n   - ومع ذلك، يحتاج المستخدم في شاشة الـ Feed إلى الضغط على صورة الناشر لفتح ملفه الشخصي في شاشة الـ Profile، أو الضغط على زر إضافة إلى السلة.\n\n"
            "2. الأنماط المعمارية الثلاثة للتواصل غير المقترن:\n   - **نمط الـ API/Impl (Contract Extraction)**: لكل ميزة موديولان: `:feature:cart-api` و `:feature:cart-impl`. موديول `:feature:feed` يعتمد فقط على `:feature:cart-api` الذي يحتوي على واجهات مجردة ومسارات بدون أي كود UI.\n   - **التنقل عبر Deep Links أو مسارات مجردة (Navigation Routes)**: فتح الشاشات عبر مسار نصي أو نوعي (`NavigationContract` أو URIs مثل `app://profile/{userId}`) يتولى موديول الـ `:app` ربطه بالشاشة الفعلية.\n   - **التواصل عبر حالة مشتركة في الـ Data Layer (Shared State via Repositories)**: إذا أضاف المستخدم عنصراً إلى السلة من شاشة الـ Feed، لا تتحدث الـ Feed مباشرة مع الـ Cart Screen؛ بل تقوم باستدعاء `CartRepository.addToCart(id)`. تقوم شاشة الـ Cart بمراقبة `CartRepository.cartFlow` وتحديث واجهتها تلقائياً عبر تدفق البيانات التفاعلي (Reactive Single Source of Truth)."
        ),
        "practical_walkthrough": (
            "التواصل بين موديولين عبر Shared State Repository وعقد التنقل المجرد:\n"
            "```kotlin\n"
            "// 1. التواصل لحفظ وتحديث البيانات: عبر طبقة الـ Data المشتركة وليس بين الـ ViewModels:\n"
            "// في :feature:catalog:\n"
            "@HiltViewModel\n"
            "class CatalogViewModel @Inject constructor(\n"
            "    private val cartRepository: CartRepository // واجهة من :domain:cart\n"
            ") : ViewModel() {\n"
            "    fun addItemToCart(item: Product) {\n"
            "        viewModelScope.launch { cartRepository.addItem(item.id) }\n"
            "        // لا نكلم شاشة الـ Cart مباشرة! مجرد كتابة في الـ Single Source of Truth\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. التواصل للتنقل (Navigation Decoupling) عبر عقد مجرد:\n"
            "// في :feature:profile-api (موديول عقد خفيف جداً):\n"
            "interface ProfileNavigationContract {\n"
            "    fun openUserProfile(context: Context, userId: String)\n"
            "}\n"
            "\n"
            "// في :feature:feed:\n"
            "class FeedNavigator @Inject constructor(\n"
            "    private val profileNav: ProfileNavigationContract // محقونة من الخارج!\n"
            ") {\n"
            "    fun onAvatarClicked(context: Context, authorId: String) {\n"
            "        profileNav.openUserProfile(context, authorId)\n"
            "    }\n"
            "}\n"
            "// موديول الـ Feed لا يعلم أي شيء عن كلاسات شاشة الـ Profile أو تطبيقها الفعلي!\n"
            "```"
        ),
        "quick_answer": "Feature modules communicate without direct coupling through three patterns: shared reactive state in lower data/domain layers, API contract modules (:feature:x-api) exposing abstract interfaces, and decoupled navigation using URL deep links or navigation delegates wired centrally in the :app module.",
        "best_answer": (
            "Enforcing zero direct compile-time coupling between peer feature modules requires three complementary architectural patterns:\n\n"
            "1. **Shared Reactive Data Layer**: When features need to exchange information (e.g. adding an item in `:feature:catalog` that updates a badge in `:feature:cart`), they never communicate ViewModel-to-ViewModel. Instead, both depend downward on `:data:cart`. The catalog ViewModel mutates the repository, and the cart badge reacts to the resulting `StateFlow` emitted by the single source of truth.\n\n"
            "2. **API/Implementation Module Splitting**: When feature `A` must explicitly invoke a capability in feature `B`, split feature `B` into `:feature:b:api` (containing interfaces and models) and `:feature:b:impl`. Feature `A` depends only on `:api`. The concrete implementation is bound via Hilt in `:app`.\n\n"
            "3. **Decoupled Navigation**: Navigation between features is delegated to type-safe route contracts, deep link URIs, or navigation interfaces implemented in `:app`. Feature `A` requests navigation to an abstract route without importing Feature `B`'s Composable or Activity."
        ),
        "deep_answer": (
            "A frequent anti-pattern when communicating between features is **Global In-Memory Event Buses** (e.g. broadcasting untyped JSON strings or arbitrary event classes across an application-wide SharedFlow).\n\n"
            "Event buses create invisible, untraceable data dependencies: if an event payload changes, nothing fails at compile time, leading to silent runtime bugs. Furthermore, event buses fail across Android process recreation—if the app process dies while an event was fired, the listener in another screen will never receive it.\n\n"
            "By channeling inter-feature communication through **durable domain repositories backed by Room or DataStore**, data persistence and reactive UI synchronization are guaranteed across process death, background updates, and screen lifecycles."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't one ViewModel inject another ViewModel directly?",
                "answer": "ViewModels are tied to specific lifecycle owners (Activity/Fragment/NavBackStackEntry). Cross-injecting ViewModels leads to severe lifecycle leaks and crashes."
            },
            {
                "question": "How does Deep Link navigation benefit multi-module apps?",
                "answer": "It provides uniform navigation that works identically for in-app screen transitions, push notifications, and external web URLs without compile-time module coupling."
            }
        ]
    },
    {
        "id": "MOD-10",
        "arabic_explanation": (
            "كيف تعمل عقود التنقل (Navigation Contracts) عبر موديولات أندرويد المتعددة؟\n\n"
            "1. طبيعة المشكلة:\n   - في Jetpack Navigation أو Compose Navigation العادي، تقوم بكتابة: `navController.navigate(ProfileRoute(userId))`.\n   - في مشروع نمطي، إذا كان كلاس `ProfileRoute` وشاشة `ProfileScreen` موجودين في موديول `:feature:profile`، فإن موديول `:feature:feed` لا يستطيع كتابة هذا السطر لأن `:feature:feed` لا يرى `:feature:profile` في وقت التجميع!\n\n"
            "2. الحلول المعمارية لعقود التنقل عبر الموديولات:\n   - **الحل الأول: نمط `:api` الموديول (API Route Contracts)**:\n     * يتم وضع كلاس المسار (`@Serializable data class ProfileRoute(val id: String)`) داخل موديول خفيف `:feature:profile-api`.\n     * يستطيع `:feature:feed` استيراد `ProfileRoute` والتنقل إليه بأمان نوعي كامل (Type-Safe Navigation).\n     * موديول `:app` فقط هو من يجمع `:feature:profile-impl` ويربط الشاشة بالمسار داخل `NavHost`.\n   - **الحل الثاني: واجهة موجه التنقل المجردة (Navigation Interface Delegate)**:\n     * واجهة `interface FeedNavigator { fun navigateToProfile(userId: String) }` يتم حقنها في `FeedViewModel`.\n     * يتم تنفيذ الواجهة داخل موديول `:app` واستدعاء `navController.navigate(...)` هناك."
        ),
        "practical_walkthrough": (
            "تطبيق Navigation Contracts في Compose Multi-Module باستخدام الـ API Module:\n"
            "```kotlin\n"
            "// 📁 في موديول ':feature:profile-api' (موديول عقود خفيف جداً):\n"
            "@Serializable\n"
            "data class ProfileDestination(val userId: String)\n"
            "\n"
            "// 📁 في موديول ':feature:feed' (يستورد فقط profile-api):\n"
            "@Composable\n"
            "fun FeedScreen(onNavigateToProfile: (String) -> Unit) {\n"
            "    Button(onClick = { onNavigateToProfile(\"user_42\") }) { Text(\"View Profile\") }\n"
            "}\n"
            "\n"
            "// 📁 في موديول ':feature:profile-impl' (يحتوي على الشاشة الفعلية):\n"
            "fun NavGraphBuilder.profileScreen() {\n"
            "    composable<ProfileDestination> {\n"
            "        ProfileRoute() // الشاشة الفعلية\n"
            "    }\n"
            "}\n"
            "\n"
            "// 📁 في موديول ':app' (يجمع كل الميزات ويربط مسارات الـ NavHost):\n"
            "@Composable\n"
            "fun AppNavHost(navController: NavHostController) {\n"
            "    NavHost(navController, startDestination = FeedDestination) {\n"
            "        composable<FeedDestination> {\n"
            "            FeedScreen(onNavigateToProfile = { userId ->\n"
            "                navController.navigate(ProfileDestination(userId)) // آمن نوعياً 100%!\n"
            "            })\n"
            "        }\n"
            "        profileScreen() // تسجيل شاشة البروفايل من الموديول الفعلي\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Navigation contracts decouple screen transitions in multi-module apps. Route destinations are placed in lightweight :api modules using Kotlin Serialization types, allowing callers to navigate with full type-safety. The :app module hosts the NavHost, registering destinations and linking screen composables from feature implementation modules.",
        "best_answer": (
            "In multi-module applications, features cannot reference peer screen classes directly. Navigation contracts solve this by decoupling the destination definition from the screen implementation:\n\n"
            "1. **Contract in `:feature:*:api`**: We define the navigation target as a serializable route type (`@Serializable data class UserProfileRoute(val id: String)`) inside a lightweight API module. Any feature needing to navigate to the profile imports only this tiny API contract.\n\n"
            "2. **Implementation in `:feature:*:impl`**: The feature implementation module exposes an extension function on `NavGraphBuilder` (e.g. `fun NavGraphBuilder.userProfileScreen(...)`) registering the composable entry.\n\n"
            "3. **Assembly in `:app`**: The `:app` module imports both modules and configures the top-level `NavHost`. When feature `A` triggers navigation, it passes the typed contract from `feature-b-api` to the controller. The destination matches without feature `A` ever knowing how the destination screen is implemented or tested."
        ),
        "deep_answer": (
            "With modern **Type-Safe Compose Navigation (Navigation 2.8+)**, navigation contracts achieve compile-time safety without raw string URLs.\n\n"
            "Under the hood, routes are typed Kotlin classes serialized via `kotlinx.serialization`. "
            "However, when architecting navigation contracts across modules, two runtime constraints must be respected:\n\n"
            "1. **Serializable Model Independence**: Never include complex domain models inside navigation route arguments (e.g. `data class CheckoutRoute(val cart: CartDomainModel)`). Large objects violate Android's `Bundle` size limits (risking `TransactionTooLargeException`) and violate encapsulation. Route arguments must strictly be lightweight primitives (IDs, keys, or query tokens). The destination screen fetches full data from its own repository.\n\n"
            "2. **State Restoration Across Process Death**: Type-safe navigation routes automatically serialize into the `SavedStateHandle`. When Android OS terminates the process in the background and restores it, Compose Navigation deserializes the route arguments flawlessly without manual bundle parsing."
        ),
        "follow_ups": [
            {
                "question": "What is the consequence of passing large objects via Navigation route arguments?",
                "answer": "It risks crashing the app with `TransactionTooLargeException` during state saving and couples the two screens to an identical data model."
            },
            {
                "question": "Can you navigate between features using Android Deep Links?",
                "answer": "Yes. Deep links decouple modules via URI strings (`app://user/{id}`), but sacrifice compile-time type checking compared to serialization contracts."
            }
        ]
    },
    {
        "id": "MOD-11",
        "arabic_explanation": (
            "كيف تدير حقن التبعيات (Dependency Injection) عبر موديولات Gradle المتعددة؟\n\n"
            "1. القاعدة المعمارية للـ DI في الـ Multi-Module:\n   - **فصل العقد عن التنفيذ (Contract vs. Implementation Separation)**:\n     * موديول الـ API أو الـ Domain يعرف الواجهة (`interface CartRepository`).\n     * موديول الـ Data أو الـ Feature Impl يحتوي على الكلاس الملموس (`class CartRepositoryImpl @Inject constructor(...)`).\n     * يوفر موديول الـ Data موديول Hilt معلّم بـ `@InstallIn(SingletonComponent::class)` يحتوي على `@Binds` يربط الواجهة بالتنفيذ.\n\n"
            "2. التجميع المركزي في Hilt (Decentralized Aggregation in `:app`):\n   - موديول `:app` يعتمد على جميع موديولات التطبيق.\n   - يقوم Hilt في وقت التجميع بجمع (Aggregate) جميع الـ Modules المعلمة بـ `@InstallIn` عبر جميع موديولات Gradle ودمجها في شجرة Dagger Graph واحدة متكاملة ومتحقق منها.\n\n"
            "3. إدارة الـ Scopes عبر الموديولات:\n   - تجنب وضع `@Singleton` عشوائياً في موديولات الـ Features.\n   - استخدم `@ViewModelScoped` لمنطق الشاشات في موديولات الـ Feature Impl، واحتفظ بـ `@Singleton` فقط للموارد المشتركة في موديولات الـ Core والـ Data."
        ),
        "practical_walkthrough": (
            "هيكل تنظيم الـ Hilt Modules عبر الموديولات المختلفة:\n"
            "```kotlin\n"
            "// 📁 في موديول ':domain:payment' (موديول Kotlin نقي):\n"
            "interface PaymentGateway {\n"
            "    suspend fun pay(orderId: String, amount: Double): Result<TransactionReceipt>\n"
            "}\n"
            "\n"
            "// 📁 في موديول ':data:payment' (يحتوي على التنفيذ الفعلي وموديول Hilt):\n"
            "class StripePaymentGateway @Inject constructor(\n"
            "    private val stripeClient: StripeClient\n"
            ") : PaymentGateway { /* ... */ }\n"
            "\n"
            "@Module\n"
            "@InstallIn(SingletonComponent::class)\n"
            "abstract class PaymentDataModule {\n"
            "    @Binds @Singleton\n"
            "    abstract fun bindPaymentGateway(impl: StripePaymentGateway): PaymentGateway\n"
            "}\n"
            "\n"
            "// 📁 في موديول ':feature:checkout':\n"
            "@HiltViewModel\n"
            "class CheckoutViewModel @Inject constructor(\n"
            "    private val paymentGateway: PaymentGateway // يعتمد على الواجهة فقط من :domain:payment!\n"
            ") : ViewModel()\n"
            "// موديول :app يقوم بتجميع PaymentDataModule وحقنه تلقائياً في CheckoutViewModel!\n"
            "```"
        ),
        "quick_answer": "Manage multi-module DI by keeping interfaces in domain/api modules, implementations and @InstallIn Hilt binding modules in data/impl modules, and letting the :app module aggregate the graph at compile time. Feature modules inject interfaces without depending on implementation modules.",
        "best_answer": (
            "Managing dependency injection cleanly in a multi-module architecture relies on Hilt's decentralized compilation model:\n\n"
            "1. **Contract Definition**: Domain and API modules define pure interfaces (e.g. `AuthRepository`) without depending on Hilt or Android frameworks.\n\n"
            "2. **Implementation & Module Packaging**: Data and implementation modules contain the concrete class with an `@Inject constructor`. Alongside the implementation, the module includes a Hilt `@Module` annotated with `@InstallIn(SingletonComponent::class)` using `@Binds` to bind the interface to the concrete class.\n\n"
            "3. **Consumer Decoupling**: Feature modules inject the interface into their `@HiltViewModel` constructors, depending only on the interface module. They have zero compile-time dependencies on the implementation module.\n\n"
            "4. **Root Aggregation**: The `:app` module aggregates all implementation modules at compile time, resolving the full Dagger graph with zero manual component wiring."
        ),
        "deep_answer": (
            "A critical pitfall in multi-module DI is **Accidental Dependency Leakage via Hilt Aggregation**.\n\n"
            "Because Hilt aggregates modules across the entire classpath of `:app`, if two feature modules accidentally bind the same interface without qualifiers, Dagger fails at the root `:app` compilation level with a `DuplicateBindingException`, even though both feature modules compiled individually without errors!\n\n"
            "Furthermore, for **Dynamic Feature Modules (Play Feature Delivery)**, standard Hilt `@InstallIn` cannot be resolved because `:app` does not depend on dynamic feature modules. "
            "To provide dependencies into dynamic features, developers must use `@EntryPoint` to explicitly retrieve base graph dependencies from the `applicationContext`."
        ),
        "follow_ups": [
            {
                "question": "Can a Hilt module in a library module be installed in `ActivityComponent`?",
                "answer": "Yes. `@InstallIn(ActivityComponent::class)` works in any library module, scoping those dependencies to Activities in the consuming application."
            },
            {
                "question": "How do you test a feature module's ViewModel in isolation without compiling the whole Hilt graph?",
                "answer": "In JVM unit tests, bypass Hilt completely. Instantiate the ViewModel directly using its constructor and pass a Fake implementation of the interface."
            }
        ]
    },
    {
        "id": "MOD-12",
        "arabic_explanation": (
            "كيف تقلل ملفات كتالوج الإصدارات (Version Catalogs) و Convention Plugins تكرار إعدادات Gradle في المشاريع النمطية؟\n\n"
            "1. المشكلة في المشاريع الكبيرة بدون هذه الأدوات:\n   - تطبيق يحتوي على 60 موديولاً: كل ملف `build.gradle.kts` يكرر 40 سطراً من الإعدادات: `compileSdk = 35`, `minSdk = 26`, إعدادات `kotlinCompilerExtensionVersion`, إعدادات `JavaVersion.VERSION_17`, وتكرار نسخ المكتبات.\n   - إذا أردت ترقية نسخة Compose أو Kotlin، تضطر لتعديل 60 ملفاً يدوياً، مع خطر عدم توافق النسخ في بعض الموديولات.\n\n"
            "2. دور الـ Version Catalog (`gradle/libs.versions.toml`):\n   - **مصدر موحد للحقيقة (Single Source of Truth)** لجميع إصدارات المكتبات والـ Plugins.\n   - يوفر Type-Safe Accessors تلقائياً في Gradle: بدلاً من نصوص سحرية `implementation(\"androidx.compose.ui:ui:1.7.0\")`، تكتب `implementation(libs.androidx.compose.ui)` مع إكمال تلقائي في الـ IDE.\n\n"
            "3. دور الـ Convention Plugins (في مجلد `build-logic`):\n   - تحويل كود إعدادات Gradle المتكرر إلى Plugins مخصصة وقابلة لإعادة الاستخدام:\n     * `com.example.android.feature`: يطبق تلقائياً مكتبة أندرويد، و Compose، و Hilt، ونسخ الـ SDK.\n     * `com.example.jvm.library`: يطبق إعدادات Kotlin النقي لموديولات الـ Domain.\n   - يتقلص ملف `build.gradle.kts` الخاص بكل موديول من 50 سطراً إلى 5 أسطر فقط!"
        ),
        "practical_walkthrough": (
            "المقارنة بين ملف build.gradle.kts التقليدي وملف نظيف مدعوم بـ Convention Plugins:\n"
            "```kotlin\n"
            "// ❌ في السابق: 40 سطراً مكررة في كل موديول من الـ 60 موديولاً:\n"
            "plugins {\n"
            "    id(\"com.android.library\")\n"
            "    id(\"org.jetbrains.kotlin.android\")\n"
            "    id(\"com.google.dagger.hilt.android\")\n"
            "    id(\"kotlin-kapt\")\n"
            "}\n"
            "android {\n"
            "    compileSdk = 35\n"
            "    defaultConfig { minSdk = 26 }\n"
            "    compileOptions { sourceCompatibility = JavaVersion.VERSION_17 }\n"
            "    buildFeatures { compose = true }\n"
            "    // ... 30 سطراً أخرى مكررة!\n"
            "}\n"
            "\n"
            "// ✅ مع Convention Plugins و Version Catalog: ملف build.gradle.kts في 5 أسطر فقط!\n"
            "plugins {\n"
            "    alias(libs.plugins.example.android.feature) // يطبق كل ما سبق تلقائياً!\n"
            "}\n"
            "\n"
            "dependencies {\n"
            "    implementation(projects.core.designsystem)\n"
            "    implementation(projects.domain.order)\n"
            "}\n"
            "// ترقية إصدار الـ SDK أو المكتبات تتم الآن بتعديل رقم واحد فقط في libs.versions.toml!\n"
            "```"
        ),
        "quick_answer": "Version Catalogs (libs.versions.toml) centralize all dependency coordinates and versions in a single type-safe source of truth. Convention plugins (in build-logic) encapsulate repeated Gradle configuration (SDK versions, compiler options, Compose/Hilt setups) into reusable plugins, reducing individual module build scripts to a few declarative lines.",
        "best_answer": (
            "Managing dozens of Gradle subprojects requires centralizing both dependency versions and build logic:\n\n"
            "1. **Version Catalogs (`libs.versions.toml`)**: Centralizes third-party dependency coordinates, plugin identifiers, and version numbers. Gradle automatically generates type-safe DSL accessors (`libs.androidx.core.ktx`). Upgrading a library version across 80 modules requires editing a single line in the catalog, preventing version drift.\n\n"
            "2. **Convention Plugins (via `build-logic`)**: Encapsulates repeated Gradle configuration patterns into custom composite build plugins written in Kotlin (`AndroidFeatureConventionPlugin`, `AndroidLibraryConventionPlugin`, `JvmLibraryConventionPlugin`).\n\n"
            "Instead of copying 50 lines of `android { ... }` blocks, JVM target options, and Compose compiler configurations into every module, a feature module simply applies `plugins { alias(libs.plugins.myapp.android.feature) }`, keeping build scripts minimal, consistent, and maintainable."
        ),
        "deep_answer": (
            "Architecturally, custom Convention Plugins are implemented inside an included composite build (typically named `build-logic`) in the project root.\n\n"
            "Because `build-logic` is an included build, Gradle compiles it first with full Kotlin DSL type safety and autocompletion before evaluating the main project's task graph. "
            "Inside convention plugins, we write clean extension functions that configure common Android blocks:\n\n"
            "```kotlin\n"
            "internal fun Project.configureKotlinAndroid(commonExtension: CommonExtension<*, *, *, *, *, *>) {\n"
            "    commonExtension.apply {\n"
            "        compileSdk = 35\n"
            "        defaultConfig { minSdk = 26 }\n"
            "        compileOptions {\n"
            "            sourceCompatibility = JavaVersion.VERSION_17\n"
            "            targetCompatibility = JavaVersion.VERSION_17\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "This eliminates legacy, fragile Groovy scripts and avoids the dreaded `subprojects { ... }` block in `rootProject/build.gradle`, which breaks Gradle Configuration Caching and parallel execution."
        ),
        "follow_ups": [
            {
                "question": "Why is `subprojects { ... }` considered an anti-pattern in modern Gradle?",
                "answer": "It couples projects together imperatively, breaking Gradle Configuration Cache, Isolated Projects, and parallel configuration."
            },
            {
                "question": "Can convention plugins configure dependencies as well as build options?",
                "answer": "Yes. An `AndroidFeatureConventionPlugin` can automatically add common dependencies like Hilt, Compose, and core testing libraries to all feature modules."
            }
        ]
    },
    {
        "id": "MOD-13",
        "arabic_explanation": (
            "متى يجب أن يعتمد الموديول على واجهة مجردة (Interface) ومتى يكون اعتماده على كلاس ملموس (Concrete Type) أفضل وأكثر عملية؟\n\n"
            "1. متى يجب الاعتماد على واجهة مجردة (Interface):\n   - **عبر حدود الموديولات (Cross-Module Boundaries)**: عندما يعتمد موديول Presentation على موديول Data، الاعتماد على `UserRepository` كـ Interface يسمح بتطوير واختبار الـ UI بشكل مستقل تماماً.\n   - **تعدد التطبيقات الحقيقية (Multiple Implementations)**: عندما يكون هناك تطبيقان فعليان للكلاس (مثل `StripePaymentGateway` و `PayPalPaymentGateway`).\n   - **عزل المكتبات الخارجية المتقلبة (Volatile 3rd Party SDKs)**: عزل كود التحقق من الهوية أو التتبع بواجهة نقية.\n   - **فصل وقت التجميع (Decoupling Compile Classpaths)**: التغيير في تنفيذ الـ Class لا يجبر الموديول المستهلك على إعادة التجميع طالما أن الـ Interface لم تتغير.\n\n"
            "2. متى يكون الاعتماد على كلاس ملموس (Concrete Type) أفضل وأكثر واقعية:\n   - **نماذج البيانات غير القابلة للتغيير (Immutable Data Classes / Value Objects)**: كلاسات مثل `User`, `Money`, `Address` يجب أن تكون Concrete Data Classes، ولا داعي لعمل `interface IUser` إطلاقاً!\n   - **الكلاسات المساعدة النقية الخالية من الحالة (Stateless Utility Classes)**: دوال الرياضيات وتنسيق النصوص.\n   - **الاستخدام الداخلي المحصور داخل الموديول الواحد (Same Module Internals)**: إذا كان الكلاس خاصاً بالـ Feature ولا يتم استخدامه خارجها، فالاعتماد المباشر يوفر طبقات وهمية غير مفيدة."
        ),
        "practical_walkthrough": (
            "المقارنة بين التجريد الصحيح والتجريد المتكلف غير المبرر:\n"
            "```kotlin\n"
            "// ❌ تجريد متكلف لا داعي له (Over-abstraction on Data Models):\n"
            "interface IUser { val id: String; val name: String }\n"
            "class UserImpl(override val id: String, override val name: String) : IUser\n"
            "// هذا هراء معماري يضاعف حجم الكود بدون أي فائدة حقيقية!\n"
            "\n"
            "// ✅ استخدام Concrete Data Class لنماذج البيانات النظيفة:\n"
            "data class User(val id: String, val name: String, val email: String)\n"
            "\n"
            "// ✅ استخدام Interface فقط للحدود المعمارية ومصادر البيانات:\n"
            "interface UserRepository {\n"
            "    val currentUser: Flow<User>\n"
            "    suspend fun updateProfile(name: String): Result<Unit>\n"
            "}\n"
            "\n"
            "// في الـ Feature ViewModel: الاعتماد على Interface يتيح اختبار الـ ViewModel بـ Fake في ثوانٍ:\n"
            "@HiltViewModel\n"
            "class ProfileViewModel @Inject constructor(\n"
            "    private val repository: UserRepository // Interface: سهولة خارقة في الاختبار والعزل\n"
            ") : ViewModel()\n"
            "```"
        ),
        "quick_answer": "Depend on interfaces across module boundaries where independent substitution, test seams, and compile-time decoupling are required (e.g. repositories, payment gateways). Depend on concrete types for immutable data models, value objects, and internal same-module utilities where multiple implementations will never exist.",
        "best_answer": (
            "The decision to depend on an interface versus a concrete type is an architectural choice balancing flexibility against ceremony:\n\n"
            "1. **Depend on an Interface**:\n   - **Architectural Seams**: Between domain layers and data layers (Repositories, Gateways). This allows UI and Domain logic to be tested on the JVM with fast Fakes without compiling Room or Retrofit.\n   - **Cross-Module API Contracts**: When splitting modules into `:feature:api` and `:feature:impl` to break rebuild cascades and circular dependencies.\n   - **Polymorphism**: When multiple implementations exist (e.g., debug mock data source vs. production network data source).\n\n"
            "2. **Depend on a Concrete Type**:\n   - **Data Models and Value Objects**: Immutable data classes (`User`, `TransactionDetails`) should never be wrapped in interfaces. They carry data, not behavior.\n   - **Same-Module Collaborators**: Internal helpers within a single feature module that will never need polymorphic variation or independent substitution."
        ),
        "deep_answer": (
            "From a build system perspective, an interface serves as an **ABI firewall**.\n\n"
            "If module `A` depends on concrete class `DatabaseUserRepository` in module `B`, any private change inside `DatabaseUserRepository` (even changing a private helper method or adding a local variable) alters `B`'s bytecode. Depending on Gradle caching granularity, this can trigger recompilations.\n\n"
            "If module `A` instead depends on `interface UserRepository` in `:domain:user-api`, module `A`'s compile classpath references **only the interface's ABI**. "
            "You can rewrite the entire SQL query, add caching, or refactor private methods inside `DatabaseUserRepository` in `:data:user`, and Gradle will **never recompile module `A`**. "
            "This compile-time insulation is one of the primary drivers of developer velocity in 100+ module repositories."
        ),
        "follow_ups": [
            {
                "question": "What is the 'Interface per Class' anti-pattern?",
                "answer": "Blindly creating an interface for every single class in a project, even when there is only one implementation and no architectural boundary, creating unnecessary indirection."
            },
            {
                "question": "Can a Kotlin `interface` contain concrete method implementations?",
                "answer": "Yes, default interface methods allow providing default behavior without forcing consumers to override them."
            }
        ]
    },
    {
        "id": "MOD-14",
        "arabic_explanation": (
            "كيف تتجنب التبعيات الدائرية (Circular Dependencies) وتمنع تضخم الموديولات العامة العملاقة (`:core:common` / `:core:base`)؟\n\n"
            "1. أزمة موديول الـ Common العملاق (The 'God Module' Anti-pattern):\n   - يبدأ المطورون بموديول `:core:common` لوضع دالة بسيطة لتنسيق التاريخ. بعد عام، يتحول إلى مستودع فوضوي يحتوي على: Retrofit DTOs، كلاسات Room، مكونات UI، ودوال تعامل مع الـ Bluetooth!\n   - **الكارثة**: كل موديول في التطبيق يعتمد على `:core:common`. أي تعديل في سطر واحد فيه يعيد تجميع التطبيق بالكامل (High Build Fan-out)، وتضيع كل فوائد الـ Modularization.\n\n"
            "2. استراتيجيات الوقاية وتفكيك الـ God Module:\n   - **التفكيك إلى موديولات متخصصة عالية التماسك (High-Cohesion Slices)**: استبدال `:core:common` بـ:\n     * `:core:model` (نماذج البيانات المشتركة النظيفة فقط).\n     * `:core:network` (إعدادات الشبكة فقط).\n     * `:core:designsystem` (مكونات الواجهة فقط).\n   - **السماح بتكرار الكود البسيط (Accepting Benign Duplication)**: كتابة دالة مساعدة من سطرين (`fun String.isValidEmail()`) في موديولين مختلفين أفضل بمليون مرة من ربط الموديولين بموديول عام ضخم.\n\n"
            "3. حل التبعيات الدائرية ومنعها آلياً:\n   - فرض مسارات التبعيات باتجاه واحد (Unidirectional Flow) للأسفل دائماً.\n   - استخدام أدوات التحقق التلقائي في الـ CI (مثل Dependency Analysis Plugin أو Lint Rules) لمنع أي موديول Core من الاعتماد على Feature، وحظر أي تبعية دائرية قبل الدمج."
        ),
        "practical_walkthrough": (
            "تفكيك موديول :core:common الفوضوي إلى موديولات محددة المسؤولية:\n"
            "```text\n"
            "❌ قبل التفكيك (God Module :core:common): موديول ضخم يكسر الـ Build Cache ويعيد بناء كل شيء:\n"
            ":feature:cart ──┐\n"
            ":feature:feed ──┼──► ┌──────────────────────────────────────────────┐\n"
            ":feature:auth ──┘    │               :core:common                   │\n"
            "                     │ (DateUtils, DTOs, RoomDAOs, Compose Theme)   │\n"
            "                     └──────────────────────────────────────────────┘\n"
            "\n"
            "✅ بعد التفكيك إلى موديولات مركزة عالية التماسك:\n"
            ":feature:cart ──────► :core:designsystem (Compose tokens only)\n"
            ":feature:feed ──────► :core:model (Immutable data classes only)\n"
            ":feature:auth ──────► :core:network (Network clients only)\n"
            "\n"
            "كل موديول يعتمد فقط على ما يحتاجه بدقة! تعديل كود الشبكة لا يعيد تجميع Compose Theme أو :feature:cart إطلاقاً.\n"
            "```"
        ),
        "quick_answer": "Avoid giant common modules by decomposing them into highly focused, single-responsibility modules (:core:model, :core:network, :core:ui). Prefer benign duplication of trivial 2-line helpers over introducing heavy shared dependencies. Enforce acyclic graphs using CI architecture lint rules and API contract extractions.",
        "best_answer": (
            "The emergence of a giant `:core:common` module and circular dependency loops are the two primary symptoms of an unmaintained multi-module architecture:\n\n"
            "1. **Eradicating the `:core:common` God Module**:\n   - A monolithic common module has near-infinite fan-out; every feature imports it, meaning any single edit invalidates the build cache for the entire application.\n   - Dismantle it into focused, cohesive modules based on stability and responsibility: `:core:model` (pure data entities), `:core:designsystem` (UI tokens), `:core:network` (networking), and `:core:analytics`.\n   - Tolerate **benign duplication**: It is far better to duplicate a 3-line string formatting extension across two feature modules than to create a shared build dependency between them.\n\n"
            "2. **Eliminating Circular Dependencies**:\n   - Cycles (`A -> B -> A`) occur when feature boundaries are blurred. Resolve them by extracting the shared data models or route contracts into an independent `:feature:x:api` module that both modules depend on downward.\n   - Enforce unidirectional graph rules in CI using Gradle architecture validation plugins."
        ),
        "deep_answer": (
            "In large engineering organizations, preventing architectural entropy requires **Automated Guardrails rather than developer vigilance**.\n\n"
            "Teams implement **Gradle Module Graph Rules** via custom Gradle tasks or plugins like `dependency-guard` or `ArchUnit`:\n\n"
            "```kotlin\n"
            "// Example Gradle constraint verification in build-logic:\n"
            "tasks.register(\"assertModularizationRules\") {\n"
            "    doLast {\n"
            "        project.subprojects.forEach { subproject ->\n"
            "            if (subproject.path.startsWith(\":core\")) {\n"
            "                subproject.configurations.all { config ->\n"
            "                    config.dependencies.forEach { dep ->\n"
            "                        if (dep.name.startsWith(\"feature\")) {\n"
            "                            throw GradleException(\"ILLEGAL DEPENDENCY: Core module ${subproject.path} cannot depend on feature ${dep.name}!\")\n"
            "                        }\n"
            "                    }\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "Running this verification on pull request CI guarantees that forbidden edges (Core depending on Feature, or Feature-to-Feature direct implementation coupling) fail the build automatically."
        ),
        "follow_ups": [
            {
                "question": "What is the 'Rule of Three' for extracting shared code into a module?",
                "answer": "Do not extract shared code when you see the second usage. Wait until a third distinct consumer requires it, ensuring the abstraction is genuinely stable and necessary."
            },
            {
                "question": "Can Gradle enforce module boundary visibility automatically?",
                "answer": "Yes, by configuring dependency constraints or using Gradle's Experimental Isolated Projects feature to validate cross-module access."
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

    for item in MOD_08_14:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions MOD-08 to MOD-14. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
