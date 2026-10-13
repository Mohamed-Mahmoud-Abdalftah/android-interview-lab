#!/usr/bin/env python3
"""Generator for ARC-08 through ARC-13 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "arc.json"

ARC_08_13 = [
    {
        "id": "ARC-08",
        "arabic_explanation": (
            "المقارنة التاريخية والمعمارية بين أنماط العرض: MVC و MVP و MVVM و MVI وتدفق البيانات أحادي الاتجاه (UDF):\n\n"
            "1. نمط MVC (Model-View-Controller - البدايات القديمة):\n"
            "   - في بدايات أندرويد، كان كلاس `Activity` يلعب دور الـ View والـ Controller معاً!\n   - نتج عن ذلك ظاهرة God Activity (آلاف الأسطر تجمع بين الرسم، والشبكة، وقواعد البيانات)، مع ارتباط مباشر بين الـ View والـ Model مما جعل الـ Unit Testing مستحيلاً تقريباً.\n\n"
            "2. نمط MVP (Model-View-Presenter):\n"
            "   - فصل الـ Presenter عن الـ Activity عبر `Interface` مخصص للـ View (`interface MainView`).\n   - الاتصال كان ثنائي الاتجاه (Bi-directional) ومتزامناً: الـ View ينادي الـ Presenter، والـ Presenter ينادي دوال الـ View (`view.showLoading()`).\n   - المشكلة: تسريب الذاكرة عند تدوير الشاشة إذا لم يتم تصفير مرجع الـ View يدوياً في `onDestroy`، وكثرة الـ Interfaces.\n\n"
            "3. نمط MVVM (Model-View-ViewModel):\n"
            "   - كسر الارتباط الثنائي! الـ ViewModel لا يعرف أي شيء عن الـ View ولا يمتلك أي مرجع له.\n   - يعتمد على الـ Data Binding أو المراقبة التفاعلية (`LiveData` / `StateFlow`).\n   - الـ ViewModel ينشر البيانات، والـ View يراقبها بنفسه.\n   - ينجو تلقائياً من تغييرات اتجاه الشاشة (Configuration Changes).\n\n"
            "4. نمط MVI (Model-View-Intent) و UDF:\n"
            "   - التطور الأحدث والأنسب لـ Jetpack Compose.\n   - حلقة أحادية الاتجاه صارمة: **Intent / User Action** يرسل للـ ViewModel، والـ ViewModel ينتج كائن **Single Immutable State** واحد يصف الشاشة بالكامل، وتأثيرات جانبية وحيدة الاتجاه (**Single-shot Effects**).\n   - يمنع تماماً تناقض وتضارب الحالات (State Desync)."
        ),
        "practical_walkthrough": (
            "مقارنة عملية بين أسلوب MVP الثنائي وأسلوب MVI التفاعلي أحادي الاتجاه:\n"
            "```kotlin\n"
            "// ❌ نمط MVP القديم: ارتباط ثنائي بالواجهة عبر Interface وكولباكس متزامنة:\n"
            "class LoginPresenter(private var view: LoginView?) {\n"
            "    fun onLoginClicked(user: String, pass: String) {\n"
            "        view?.showLoading() // الـ Presenter يوجه الـ View أمرياً\n"
            "        authApi.login(user, pass) { success ->\n"
            "            if (success) view?.navigateToHome() else view?.showError()\n"
            "        }\n"
            "    }\n"
            "    fun detachView() { view = null } // ضروري لتجنب تسريب الذاكرة!\n"
            "}\n"
            "\n"
            "// ✅ نمط MVI الحديث: تدفق أحادي الاتجاه وحالة غير قابلة للتعديل (Compose-Friendly):\n"
            "sealed interface LoginIntent {\n"
            "    data class Submit(val user: String, val pass: String) : LoginIntent\n"
            "}\n"
            "data class LoginUiState(val isLoading: Boolean = false, val error: String? = null)\n"
            "\n"
            "class LoginViewModel : ViewModel() {\n"
            "    private val _state = MutableStateFlow(LoginUiState())\n"
            "    val state: StateFlow<LoginUiState> = _state.asStateFlow()\n"
            "\n"
            "    fun processIntent(intent: LoginIntent) {\n"
            "        when (intent) {\n"
            "            is LoginIntent.Submit -> executeLogin(intent.user, intent.pass)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "MVC coupled Views and Controllers inside Activities. MVP separated Presenters via interfaces but required manual lifecycle cleanup. MVVM decoupled View from ViewModel using observable state. MVI formalizes strict Unidirectional Data Flow (UDF) with immutable single-state containers and explicit User Intents, making it the ideal partner for Jetpack Compose.",
        "best_answer": (
            "The evolution of Android presentation patterns reflects the industry's shift toward lifecycle safety, testability, and reactive declarative UI.\n\n"
            "1. **MVC**: In early Android, `Activity` served as both View and Controller. This produced tight coupling, bloated 'God Activities', and near-zero unit testability because UI and lifecycle were inseparable.\n\n"
            "2. **MVP**: Introduced a `Presenter` communicating with the Activity via a `View` interface. While testable, it was tightly coupled bi-directionally: the Presenter held a direct reference to the View, requiring meticulous manual lifecycle nullification (`detachView()`) to prevent memory leaks during configuration changes.\n\n"
            "3. **MVVM**: Broke bi-directional coupling. The `ViewModel` has zero references to the UI. Instead, it exposes observable streams (`LiveData` or `StateFlow`). The View observes the ViewModel; when data changes, the View updates. ViewModels natively survive configuration changes via `ViewModelStore`.\n\n"
            "4. **MVI / UDF**: The modern standard tailored for declarative UI (Compose). It enforces a closed reactive loop: User interactions emit typed **Intents**, processed by a state machine that outputs a single **Immutable UiState** snapshot. This guarantees deterministic state transitions and eradicates state desynchronization bugs."
        ),
        "deep_answer": (
            "The philosophical difference between MVVM and MVI in modern Android is state modeling discipline. "
            "In classic MVVM, a ViewModel often exposes multiple independent streams: `val isLoading: LiveData<Boolean>`, `val data: LiveData<List<T>>`, `val error: LiveData<String?>`. "
            "This creates an *inconsistent state vulnerability*: a race condition can cause `isLoading` to emit `true` while an old `error` is still active, causing the UI to briefly show both a spinner and an error banner simultaneously.\n\n"
            "MVI resolves this through **Single Source of Truth state modeling**: the entire screen is governed by a single `sealed interface ScreenState` or consolidated `data class ScreenUiState`. "
            "Invalid combinations are made structurally unrepresentable at compile time.\n\n"
            "In production testing, MVI makes ViewModels trivially verifiable via turbine or `runTest`: tests dispatch an Intent and assert the exact deterministic sequence of resulting state emissions."
        ),
        "follow_ups": [
            {
                "question": "What is the primary drawback of classic MVI?",
                "answer": "Boilerplate overhead: defining distinct Intents, Reducers, and single-shot Effect channels for simple CRUD screens can be overkill compared to pragmatic MVVM."
            },
            {
                "question": "Why is MVI particularly suited for Jetpack Compose?",
                "answer": "Compose is a declarative function of state (`UI = f(State)`). MVI provides exactly what Compose expects: a single immutable state object that drives recomposition deterministically."
            }
        ]
    },
    {
        "id": "ARC-09",
        "arabic_explanation": (
            "كيف تختلف حالة الواجهة (UI State) عن حالة الأعمال/النطاق (Business / Domain State)؟\n\n"
            "1. ما هي حالة الأعمال (Business / Domain State)؟\n"
            "   - تمثل الحقيقة الأساسية للبيانات والمنتج (Source of Truth) بصرف النظر عن كيفية أو مكان عرضها.\n   - أمثلة: رصيد الحساب البنكي، عناصر سلة التسوق الفعلية في قاعدة البيانات، وحالة اشتراك المستخدم (Active / Expired).\n   - تتميز بأنها: طويلة الأجل (Long-lived)، مستقلة عن أجهزة العرض وشاشات الهواتف، ولا تتغير بمجرد تفاعل بصري.\n\n"
            "2. ما هي حالة الواجهة (UI State)؟\n"
            "   - تمثل ما يراه المستخدم ويتفاعل معه على الشاشة في اللحظة الراهنة.\n   - أمثلة: هل مؤشر التحميل (Spinner) ظاهر؟ ما هو نص رسالة الخطأ المترجمة المعروضة؟ أي تبويب محدد حالياً؟ هل القائمة منسدلة (Expanded)؟ وما هو النص المكتوب في حقل البحث؟\n   - تتميز بأنها: مؤقتة (Ephemeral)، تعيش مع الشاشة، وتتأثر بالحجم والدوران ونوع الجهاز.\n\n"
            "3. لماذا يُعتبر الخلط بينهما خطأ معمارياً فادحاً؟\n   - إذا قمت بحفظ متغير مثل `isDropdownExpanded: Boolean` داخل الـ Domain Entity، فإنك لوثت بيانات البزنس بتفاصيل واجهة مستخدم مؤقتة لا معنى لها في قاعدة البيانات أو على السيرفر!"
        ),
        "practical_walkthrough": (
            "توضيح الفرق العملي بين Domain State و UI State وكيف يحول الـ ViewModel بينهما:\n"
            "```kotlin\n"
            "// 1. DOMAIN STATE (حالة البزنس النقية - تعيش في Domain/Database):\n"
            "data class BankAccount(\n"
            "    val accountNumber: String,\n"
            "    val balanceCents: Long,\n"
            "    val currency: String,\n"
            "    val isOverdrawn: Boolean\n"
            ")\n"
            "\n"
            "// 2. UI STATE (حالة العرض المخصصة للشاشة - تعيش في Presentation):\n"
            "@Immutable\n"
            "data class AccountDetailsUiState(\n"
            "    val isLoading: Boolean = false,\n"
            "    val formattedBalance: String = \"\", // مجهزة للعرض المباشر: \"-$150.00\"\n"
            "    val balanceColor: Color = Color.Black, // أحمر إذا كان مكشوفاً\n"
            "    val isDepositButtonEnabled: Boolean = true,\n"
            "    val errorMessage: String? = null\n"
            ")\n"
            "\n"
            "// 3. التحويل في الـ ViewModel:\n"
            "fun BankAccount.toUiState(): AccountDetailsUiState {\n"
            "    return AccountDetailsUiState(\n"
            "        isLoading = false,\n"
            "        formattedBalance = CurrencyFormatter.format(balanceCents, currency),\n"
            "        balanceColor = if (isOverdrawn) Color.Red else Color.Green,\n"
            "        isDepositButtonEnabled = !isOverdrawn\n"
            "    )\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Business/domain state represents persistent, presentation-independent business facts (e.g. account balance, cart items in DB). UI state represents transient, presentation-specific rendering requirements (e.g. loading spinners, active tab indexes, formatted strings, and error banners).",
        "best_answer": (
            "Distinguishing between UI state and Business/Domain state is a cornerstone of clean separation of concerns.\n\n"
            "1. **Business / Domain State**:\n"
            "   - Represents core domain truth and invariants independently of how or whether data is displayed.\n"
            "   - Examples: A user's remaining credit balance, an authentication token, or an order's fulfillment status.\n"
            "   - Maintained in data/domain layers, often backed by local databases (Room) or remote servers. It survives Activity destructions and app process restarts.\n\n"
            "2. **UI State (Presentation State)**:\n"
            "   - Represents the visual rendering of the screen at a specific instant.\n"
            "   - Examples: Whether a loading indicator is spinning, active text field inputs, whether an accordion item is expanded, or localized error strings.\n"
            "   - Scoped to the UI lifecycle (ViewModel or Composable) and ephemeral in nature.\n\n"
            "The ViewModel acts as the transformer: it observes long-lived domain state, applies presentation logic, and projects it into formatted, immutable `UiState` snapshots."
        ),
        "deep_answer": (
            "A frequent architectural defect is leaking UI state down into domain repositories or databases. "
            "For example, adding `var isSelected: Boolean` or `var isExpanded: Boolean` directly onto a database entity or domain model corrupts pure business definitions with transient UI concerns. "
            "If that entity is reused across a notification service, widget, or background sync worker, those UI properties are completely meaningless and cause data corruption bugs.\n\n"
            "Conversely, storing domain business rules inside UI state creates duplicate logic across screens. "
            "For instance, checking if an account is eligible for a loan must be evaluated in a domain Use Case, not computed ad-hoc within a composable's `UiState` mapping lambda.\n\n"
            "In testing, domain state is tested via assertions on repository updates, whereas UI state is tested by asserting that domain events produce expected visual states in `StateFlow`."
        ),
        "follow_ups": [
            {
                "question": "Can UI state exist without domain state?",
                "answer": "Yes. Purely transient UI states—like an accordion expansion toggle, a dialog visibility flag, or animation progress—are UI states that have zero backing domain state."
            },
            {
                "question": "Where should the formatting of a date timestamp (Long to String) occur?",
                "answer": "In the Presentation layer (ViewModel or Presentation Mapper). Formatting depends on device locale and UI display rules, which have no place in the pure domain layer."
            }
        ]
    },
    {
        "id": "ARC-10",
        "arabic_explanation": (
            "ما هو مبدأ المصدر الوحيد للحقيقة (Single Source of Truth - SSOT) وكيف نطبقه في أندرويد؟\n\n"
            "1. تعريف مبدأ الـ SSOT:\n"
            "   - ينص المبدأ على أن **كل معلومة أو بيان في التطبيق يجب أن يمتلك مالكاً ومصدراً وحيداً مسؤولاً عن حفظه وتعديله ونشره**.\n   - لا يجوز أبداً الاحتفاظ بنسخ متعددة قابلة للتعديل من نفس البيانات في أماكن متفرقة (مثل وجود نسخة في ViewModel ونسخة في Activity ونسخة في قاعدة البيانات).\n\n"
            "2. كيف نطبقه عملياً في Android (Offline-First Pattern)؟\n"
            "   - **قاعدة البيانات المحلية (Room) هي الـ SSOT لبيانات التطبيق**:\n   - الـ UI يراقب فقط قاعدة البيانات المحلية عبر `Flow<List<Item>>`.\n   - عندما يطلب التطبيق بيانات من السيرفر عبر Network API:\n     * لا يتم إرسال استجابة الشبكة مباشرة إلى الشاشة!\n     * يتم حفظ استجابة الشبكة داخل قاعدة بيانات Room أولاً.\n     * تقوم Room تلقائياً بإطلاق انبعاث (Emit) جديد للبيانات المحدثة إلى الشاشة.\n\n"
            "3. الفوائد الحقيقية للـ SSOT:\n   - **منع تضارب البيانات (No Inconsistencies)**: مستحيل أن تظهر الشاشة بيانات تختلف عن البيانات المحفوظة.\n   - **دعم Offline كامل تلقائياً**: التطبيق يعرض البيانات فوراً من الـ DB حتى لو انقطع الإنترنت، ثم يحدثها بصمت عند عودته."
        ),
        "practical_walkthrough": (
            "تطبيق نمط Offline-First بجعل Room هي المصدر الوحيد للحقيقة (SSOT):\n"
            "```kotlin\n"
            "class UserRepositoryImpl(\n"
            "    private val userDao: UserDao,\n"
            "    private val userApi: UserApi\n"
            ") : UserRepository {\n"
            "\n"
            "    // 1. القراءة تتدفق دائماً وحصرياً من الـ SSOT (قاعدة بيانات Room):\n"
            "    override fun observeUserProfile(userId: String): Flow<User> {\n"
            "        return userDao.observeUser(userId)\n"
            "            .map { it.toDomain() }\n"
            "    }\n"
            "\n"
            "    // 2. طلب الشبكة يحدث الـ SSOT فقط، والـ SSOT هي التي تخطر الواجهة تلقائياً:\n"
            "    override suspend fun refreshUserProfile(userId: String): Result<Unit> = runCatching {\n"
            "        val remoteDto = userApi.fetchUser(userId)\n"
            "        // كتابة البيانات في Room هي الخطوة الوحيدة؛ انبعاث الـ Flow سيحدث تلقائياً:\n"
            "        userDao.insertUser(remoteDto.toEntity())\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Single Source of Truth (SSOT) means every piece of data has a single owner that acts as the authoritative source. In Android, the local database (Room) is typically the SSOT: network responses write directly to Room, and the UI exclusively observes Room flows, preventing data inconsistency and providing offline support.",
        "best_answer": (
            "Single Source of Truth (SSOT) is an architectural discipline ensuring that every piece of state has exactly one authoritative owner responsible for its storage, mutation, and distribution.\n\n"
            "In modern Android architectures, we implement SSOT via the **Offline-First Reactive Repository pattern**:\n"
            "1. **Authoritative Storage**: The local database (Room) serves as the definitive SSOT for app data.\n"
            "2. **Unidirectional Observation**: The UI layer and ViewModels observe data strictly through reactive streams (`Flow<T>`) emitted by the local database DAO. The UI never queries the network directly.\n"
            "3. **Write-Through Ingestion**: When network requests complete, the repository does not return network models to the UI. Instead, it writes the payload directly into Room inside a database transaction. Room's internal invalidation tracker automatically triggers a new emission on the active Flow, notifying all listening ViewModels.\n\n"
            "This eliminates state desynchronization: if five different screens or background workers observe the same user profile, modifying that profile in one place instantly updates all five screens automatically."
        ),
        "deep_answer": (
            "Contrast this with the flawed **Dual-Source Anti-Pattern**: a screen fetches data from Retrofit, displays it, and separately writes a copy to SharedPreferences or Room. "
            "If the network request succeeds but database persistence fails, or if an in-memory cache differs from disk, the user encounters jarring contradictions—such as navigating back and seeing an outdated item count.\n\n"
            "SSOT applies to the Presentation layer as well. "
            "Inside the ViewModel, a single `MutableStateFlow<ScreenUiState>` acts as the SSOT for the entire screen. "
            "Mutating UI state requires calling `_uiState.update { ... }`, preventing multiple independent LiveData streams from racing each other.\n\n"
            "In testing, SSOT drastically simplifies verification: repository tests simply verify that executing a network sync populates the local Fake DAO, and UI tests verify reactions to simulated DAO emissions."
        ),
        "follow_ups": [
            {
                "question": "Can an in-memory cache serve as an SSOT?",
                "answer": "Yes, for volatile session data that must not persist across app process death (like an active in-memory shopping cart or socket stream), a thread-safe in-memory cache (like `MutableStateFlow`) acts as the SSOT."
            },
            {
                "question": "How does Room notify observers when data changes in the table?",
                "answer": "Room installs an internal SQLite `InvalidationTracker` that hooks into database table updates. When a write occurs on an observed table, it triggers a query re-evaluation and emits the updated result on the Flow."
            }
        ]
    },
    {
        "id": "ARC-11",
        "arabic_explanation": (
            "كيف تعرض وتصمم حالات التحميل (Loading)، المحتوى (Content)، القائمة الفارغة (Empty)، والخطأ (Error) باحترافية؟\n\n"
            "1. معضلة الحالات المتضاربة (The Multiple-Boolean Anti-Pattern):\n"
            "   - الخطأ الكلاسيكي هو استخدام متغيرات منفصلة في الـ ViewModel:\n     `val isLoading = MutableStateFlow(false)` و `val error = MutableStateFlow<String?>(null)` و `val items = MutableStateFlow<List<Item>>(emptyList())`.\n   - النتيجة: قد يكون `isLoading = true` و `error != null` في نفس اللحظة! مما يربك الـ Composable ويجعله يعرض Spinner فوق رسالة خطأ!\n\n"
            "2. الحل المعماري الأول: الـ Sealed Interface (للحالات الحصرية):\n   - ممتاز للشاشات الكاملة التي تنتقل بين حالات واضحة متنافية:\n     * `data object Loading : FeedUiState`\n     * `data object Empty : FeedUiState`\n     * `data class Success(val items: ImmutableList<FeedItem>) : FeedUiState`\n     * `data class Error(val message: String) : FeedUiState`\n   - الميزة: مستحيل تمثيل حالة غير منطقية (Illegal States are Unrepresentable).\n\n"
            "3. الحل المعماري الثاني: الـ Combined Data Class (للتحديث الجزئي / Pull-to-Refresh):\n   - عندما تحتاج الشاشة لعرض القائمة القديمة مع وجود مؤشر تحميل خفيف في الأعلى (Pull-to-refresh) أو Snackbar خطأ دون مسح المحتوى:\n     * `data class FeedUiState(val items: ImmutableList<FeedItem>, val isRefreshing: Boolean, val error: String?)`."
        ),
        "practical_walkthrough": (
            "تطبيق النمطين باحترافية في Jetpack Compose:\n"
            "```kotlin\n"
            "// النمط 1: Sealed Interface للشاشات الكاملة المتبادلة حصرياً:\n"
            "sealed interface ProductListUiState {\n"
            "    data object Loading : ProductListUiState\n"
            "    data object Empty : ProductListUiState\n"
            "    data class Success(val products: ImmutableList<Product>) : ProductListUiState\n"
            "    data class Error(val message: String) : ProductListUiState\n"
            "}\n"
            "\n"
            "@Composable\n"
            "fun ProductListScreen(uiState: ProductListUiState, onRetry: () -> Unit) {\n"
            "    when (uiState) {\n"
            "        is ProductListUiState.Loading -> FullScreenLoadingSpinner()\n"
            "        is ProductListUiState.Empty -> EmptyStatePlaceholder(\"No products found\")\n"
            "        is ProductListUiState.Success -> ProductList(uiState.products)\n"
            "        is ProductListUiState.Error -> ErrorBanner(uiState.message, onRetry = onRetry)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Expose loading, content, empty, and error states using either a Sealed Interface for mutually exclusive full-screen transitions (making illegal states unrepresentable) or an Immutable Data Class when retaining content during background refresh or transient error snackbars.",
        "best_answer": (
            "Modeling screen states requires choosing the correct abstraction between mutually exclusive transitions and persistent content overlays.\n\n"
            "1. **The Sealed Interface Pattern (Mutually Exclusive)**:\n"
            "   - Ideal for screen-level states where only one visual representation can exist at a time (e.g. initial load, fatal error, empty catalog, or success grid).\n"
            "   - By defining `sealed interface UiState { Loading, Empty, Success(data), Error(msg) }`, the compiler enforces exhaustive `when` expressions in Compose.\n"
            "   - It makes invalid states—such as showing a full-screen loading spinner and an error message simultaneously—structurally impossible to represent.\n\n"
            "2. **The Consolidated Data Class Pattern (Overlay / Partial Updates)**:\n"
            "   - Ideal for screens supporting pull-to-refresh, pagination, or non-fatal errors.\n"
            "   - When a user pulls to refresh, wiping the screen to show a full-screen spinner is terrible UX. Instead, a data class retaining `items`, `isRefreshing = true`, and `transientError = null` keeps existing items visible while displaying a top progress bar.\n\n"
            "Both patterns avoid the legacy anti-pattern of exposing multiple independent reactive booleans that easily desynchronize."
        ),
        "deep_answer": (
            "Under the hood, in Compose, transitioning between sealed interface branches requires smooth visual coordination. "
            "Using `AnimatedContent(targetState = uiState)` enables seamless crossfade or slide transitions between `Loading`, `Content`, and `Error` states without jarring screen flashes.\n\n"
            "When dealing with `Empty` states specifically, senior architects differentiate between a **true empty list** (the query returned zero records) and an **uninitialized state** (the query has not started). "
            "Modeling `data object Empty : UiState` provides dedicated UI real estate (illustration, helper text, clear filter button) that encourages user engagement.\n\n"
            "In unit testing, testing a sealed interface is remarkably expressive: asserting `assertThat(state).isInstanceOf<UiState.Success>()` provides instant, type-safe validation of state progression."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't you clear the existing items list when a refresh fails?",
                "answer": "Clearing the list replaces visible content with a blank error screen. Keeping cached data and displaying a transient snackbar error ensures the user can continue reading offline content."
            },
            {
                "question": "How do you handle pagination loading vs initial screen loading?",
                "answer": "Initial loading uses a full-screen state or skeleton loader. Pagination loading is modeled as a footer append state (`isAppendingPage = true`) at the end of the existing content list."
            }
        ]
    },
    {
        "id": "ARC-12",
        "arabic_explanation": (
            "كيف يتم تحويل أخطاء طبقتي النطاق والبيانات (Domain / Data Errors) إلى أخطاء واجهة مستخدم مفهومة وقابلة للتنفيذ (Actionable UI Errors)؟\n\n"
            "1. المشكلة في تسريب استثناءات الطبقات الخارجية (Leaking Raw Exceptions):\n"
            "   - عرض نصوص مثل `java.net.SocketTimeoutException` أو `HTTP 502 Bad Gateway` للمستخدم هو تجربة مستخدم كارثية وغير مفهومة، وتسريب لمعلومات النظام التقنية.\n   - كما أن طبقة الـ UI لا يجب أن تفحص كود أخطاء HTTP (مثل فحص `code == 401`).\n\n"
            "2. رحلة تحويل الأخطاء عبر الطبقات الثلاث:\n   - **في طبقة الـ Data**: التقاط `HttpException` أو `IOException` وتحويلها إلى **Typed Domain Errors** (مثل `AppError.NetworkTimeout`, `AppError.Unauthorized`).\n   - **في طبقة الـ Domain**: اتخاذ قرارات الأعمال (مثل محاولة إعادة الطلب Retry أو توجيه المستخدم لتسجيل الدخول).\n   - **في طبقة الـ Presentation**: تحويل الـ Domain Error إلى **Actionable UI Error** يحمل:\n     * رسالة مترجمة واضحة (`UiText.StringResource(R.string.network_timeout_msg)`).\n     * زر تصحيحي قابل للتنفيذ (Actionable button: مثل زر \"إعادة المحاولة Retry\" أو \"تسجيل الدخول\").\n\n"
            "3. نمط `UiText` لمنع تسريب الـ Android Context إلى الـ ViewModel:\n   - استخدام Sealed Class يسمى `UiText` يمثل إما نصاً ثابتاً (`UiText.DynamicString`) أو معرف مورد (`UiText.StringResource(R.string.xyz)`).\n   - يتيح للـ ViewModel تحديد المورد دون الحاجة لـ Context، وتقوم دالة الـ Composable بقراءته عبر `uiText.asString()`."
        ),
        "practical_walkthrough": (
            "نمط UiText وتحويل الأخطاء التقنية إلى أخطاء واجهة قابلة للإصلاح:\n"
            "```kotlin\n"
            "// 1. DOMAIN LAYER: تصنيف الأخطاء كـ Domain Errors نقية:\n"
            "sealed interface DomainError {\n"
            "    data object NetworkOffline : DomainError\n"
            "    data object SessionExpired : DomainError\n"
            "    data class ServerError(val code: Int) : DomainError\n"
            "}\n"
            "\n"
            "// 2. PRESENTATION HELPER: تمثيل النصوص المترجمة دون الحاجة لـ Context في ViewModel:\n"
            "sealed interface UiText {\n"
            "    data class Dynamic(val value: String) : UiText\n"
            "    data class Resource(@StringRes val resId: Int, val args: List<Any> = emptyList()) : UiText\n"
            "\n"
            "    @Composable\n"
            "    fun asString(): String = when (this) {\n"
            "        is Dynamic -> value\n"
            "        is Resource -> stringResource(resId, *args.toTypedArray())\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. PRESENTATION LAYER: نموذج خطأ تفاعلي قابل للتنفيذ:\n"
            "data class ActionableUiError(\n"
            "    val message: UiText,\n"
            "    val actionLabel: UiText,\n"
            "    val onAction: () -> Unit\n"
            ")\n"
            "\n"
            "// في الـ ViewModel: التحويل من DomainError إلى ActionableUiError:\n"
            "fun mapError(error: DomainError): ActionableUiError = when (error) {\n"
            "    is DomainError.NetworkOffline -> ActionableUiError(\n"
            "        message = UiText.Resource(R.string.error_no_internet),\n"
            "        actionLabel = UiText.Resource(R.string.retry),\n"
            "        onAction = { retryLastAction() }\n"
            "    )\n"
            "    is DomainError.SessionExpired -> ActionableUiError(\n"
            "        message = UiText.Resource(R.string.error_session_expired),\n"
            "        actionLabel = UiText.Resource(R.string.login_again),\n"
            "        onAction = { navigateToLogin() }\n"
            "    )\n"
            "    is DomainError.ServerError -> ActionableUiError(\n"
            "        message = UiText.Resource(R.string.error_server_generic),\n"
            "        actionLabel = UiText.Resource(R.string.dismiss),\n"
            "        onAction = { clearError() }\n"
            "    )\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Map technical errors into actionable UI errors through layer boundaries: Data maps raw IO/HTTP exceptions into typed Domain errors (e.g. `NetworkOffline`, `SessionExpired`). The ViewModel maps Domain errors into `ActionableUiError` containing localized `UiText` resource references and executable recovery callbacks (e.g. Retry, Login).",
        "best_answer": (
            "Transforming raw technical failures into actionable user experiences is a benchmark of enterprise architecture.\n\n"
            "1. **Data Layer Translation**: Data sources catch raw platform exceptions (`HttpException`, `SocketTimeoutException`, `SQLiteConstraintException`) and convert them into strongly typed **Domain Errors** (e.g. `DataError.Network.Timeout`, `DataError.Auth.Unauthorized`). Raw stack traces and HTTP status codes must never cross into presentation.\n\n"
            "2. **Presentation Layer Mapping**: The ViewModel maps domain errors into a presentation-centric model: the **Actionable UI Error**:\n"
            "   - **Localized Message**: Encapsulated using a `UiText` wrapper (`UiText.StringResource(R.string.error_no_internet)`), allowing the ViewModel to stay pure and Context-free while supporting instant language changes.\n"
            "   - **Recovery Action**: Every error must empower the user with an actionable recourse—such as a 'Retry' button, 'Re-authenticate' redirect, or 'Check Settings' link.\n\n"
            "This ensures users are never greeted with incomprehensible raw exceptions while decoupling the UI from backend status codes."
        ),
        "deep_answer": (
            "The `UiText` pattern is vital for ViewModel testability. "
            "If a ViewModel injects Android `Context` or `Resources` merely to call `getString(R.string.error)`, it breaks pure JVM unit test isolation and requires mocking Android framework objects. "
            "With `UiText.Resource(R.string.error_id)`, the ViewModel returns a lightweight data class holding the integer resource ID. "
            "Unit tests simply assert `assertThat(state.error.message.resId).isEqualTo(R.string.error_id)` in sub-millisecond JVM tests.\n\n"
            "In Compose, extracting the string is seamless: composables call `error.message.asString()` which internally invokes `stringResource()`, reacting to configuration changes automatically.\n\n"
            "For production telemetry, the raw technical exception is logged to Crashlytics or Datadog in the Data layer before being sanitized, ensuring engineers have stack traces while users receive friendly, actionable prompts."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't ViewModels call `context.getString(resId)` directly?",
                "answer": "Holding `Context` in ViewModels risks memory leaks and destroys pure JVM unit testability. Using the `UiText` abstraction defers string resolution to the Composable rendering phase."
            },
            {
                "question": "What is an 'actionable' error versus a passive error?",
                "answer": "A passive error simply displays 'An error occurred'. An actionable error explains what happened and provides a concrete recovery mechanism, such as 'Connection lost. [Retry]' or 'Card expired. [Update Payment]'."
            }
        ]
    },
    {
        "id": "ARC-13",
        "arabic_explanation": (
            "متى تكون طبقة النطاق (Domain Layer) مفيدة وضرورية حقاً، ومتى تكون اختيارية أو زيادة غير مبررة (Overengineering)؟\n\n"
            "1. متى تكون طبقة الـ Domain مفيدة وضرورية حتماً؟\n   - **تعدد الشاشات ومصادر الدخول (Multiple Callers / Shared Logic)**: إذا كانت نفس عملية البيزنس (مثل `AddToCartUseCase` أو `ValidatePromoCodeUseCase`) تُستدعى من شاشة الكتالوج، وشاشة البحث، وشاشة الـ DeepLink، والـ Widget.\n   - **قواعد عمل معقدة وحسابات مالية (Complex Invariants)**: شاشات البنوك، حساب الضرائب، التأمين، والتطبيقات الطبية التي تتطلب عشرات الشروط والتحققات التي يجب عزلها واختبارها في بيئة JVM سريعة.\n   - **تنسيق عمليات بين Repositories متعددة**: عندما تتطلب العملية الواحدة التنسيق بين 3 مستودعات مختلفة.\n\n"
            "2. متى تكون طبقة الـ Domain اختيارية وتعتبر Overengineering؟\n   - **شاشات العرض والتصفح البسيطة (Simple CRUD / Pass-through)**: شاشة تقرأ قائمة مقالات وتعرضها؛ إنشاء `GetArticlesUseCase` يقوم فقط بـ `return repo.getArticles()` دون أي معالجة أو فحص هو إهدار للوقت وتضخيم للكود (Code Bloat).\n   - **تطبيقات الـ MVP الصغيرة والتجريبية**: حيث تكون متطلبات المنتج سريعة التغير والبيزنس شبه منعدم.\n\n"
            "3. التوجيه الرسمي من Google (Architecture Guidance):\n   - أعلنت Google رسمياً أن **طبقة الـ Domain هي طبقة اختيارية (Optional Layer)** في أندرويد؛ يُنصح بإضافتها فقط عند وجود تعقيد حقيقي في قواعد العمل أو حاجة لإعادة الاستخدام."
        ),
        "practical_walkthrough": (
            "المقارنة بين استخدام مبرر لـ UseCase واستخدام يعتبر Overengineering:\n"
            "```kotlin\n"
            "// ❌ OVERENGINEERING: Passthrough UseCase لا يضيف أي قيمة، مجرد وسيط بلا فائدة:\n"
            "class GetNewsListUseCase(private val repository: NewsRepository) {\n"
            "    // مجرد سطر يمرر الاستدعاء؛ تعقيد إضافي لـ DI والـ Navigation دون فائدة!\n"
            "    operator fun invoke(): Flow<List<Article>> = repository.getArticles()\n"
            "}\n"
            "\n"
            "// ✅ استخدام مبرر وضروري للـ Domain Layer: منطق بيزنس معقد وتنسيق مستودعات:\n"
            "class CheckoutCartUseCase @Inject constructor(\n"
            "    private val cartRepo: CartRepository,\n"
            "    private val paymentRepo: PaymentRepository,\n"
            "    private val couponValidator: CouponValidator\n"
            ") {\n"
            "    suspend operator fun invoke(cartId: String, couponCode: String?): CheckoutResult {\n"
            "        val items = cartRepo.getCartItems(cartId)\n"
            "        if (items.isEmpty()) return CheckoutResult.EmptyCart\n"
            "\n"
            "        val discount = couponCode?.let { couponValidator.calculateDiscount(it, items) } ?: 0L\n"
            "        val finalTotal = items.sumOf { it.price } - discount\n"
            "\n"
            "        return paymentRepo.processPayment(finalTotal)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A separate Domain layer is genuinely useful when business logic is complex, requires strict JVM test isolation, orchestrates multiple repositories, or is shared across multiple ViewModels. It is optional and overengineered for simple CRUD screens where Use Cases would merely act as pass-through wrappers around repository calls.",
        "best_answer": (
            "The Domain layer is an architectural investment that pays dividends under specific complexity thresholds, but introduces counterproductive boilerplate when applied dogmatically.\n\n"
            "1. **When Domain Layer is Genuinely Useful**:\n"
            "   - **Multi-Entry Business Logic**: When the same business flow (e.g. `AddToCartUseCase`, `LogOutUseCase`) is triggered from multiple ViewModels, Push Notification receivers, or Widgets.\n"
            "   - **Complex Business Rules & Invariants**: Financial, healthcare, or security domains requiring mathematical calculations, threshold evaluations, or conditional validations independent of UI.\n"
            "   - **Cross-Repository Orchestration**: When a single operation coordinates multiple repositories (e.g. updating local database, calling third-party payment, and flushing cache).\n"
            "   - **Kotlin Multiplatform (KMP)**: When business logic is shared verbatim across Android, iOS, and Desktop platforms.\n\n"
            "2. **When it is Overengineering**:\n"
            "   - **Simple CRUD Applications**: In news readers, blogs, or basic display lists where the UI merely queries and displays data. Creating a `GetArticlesUseCase` that contains only `invoke() = repo.getArticles()` is pure pass-through noise.\n\n"
            "Google's official Android Architecture Guidelines explicitly classify the Domain layer as **optional**, encouraging ViewModels to directly consume Repositories when business transformation is absent."
        ),
        "deep_answer": (
            "A pragmatic Senior Architect evaluates the ROI of an explicit Domain module based on team scale and product lifecycle. "
            "In an early-stage startup building an MVP, enforcing a mandatory Use Case for every database read slows down delivery velocity by 30% due to redundant interfaces, DTO mappers, and DI bindings.\n\n"
            "However, in large enterprise teams with 20+ Android engineers, establishing a distinct `:domain` module enforces code ownership boundaries. "
            "Feature teams cannot accidentally introduce database migrations or UI widgets into business policy files. "
            "Furthermore, JVM unit tests for the `:domain` module run in under 2 seconds across thousands of tests because there is zero Android Gradle plugin overhead.\n\n"
            "The recommended approach is **Pragmatic Layering**: allow ViewModels to call Repositories directly by default, and extract a Use Case only when business logic emerges, becomes complex, or requires reuse."
        ),
        "follow_ups": [
            {
                "question": "What is the official Google recommendation regarding the Domain layer?",
                "answer": "Google classifies the Domain layer as optional. It should be introduced only to encapsulate complex business logic or reuse rules across multiple ViewModels."
            },
            {
                "question": "How do passthrough Use Cases harm large projects?",
                "answer": "They double the number of classes, require boilerplate Dagger/Hilt bindings, lengthen compilation times, and force developers to navigate through multiple meaningless abstraction layers during debugging."
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

    for item in ARC_08_13:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions ARC-08 to ARC-13. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
