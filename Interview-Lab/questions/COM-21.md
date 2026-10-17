---
id: "COM-21"
question: "What is NavHost, and how is state restored after process death?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 250
editorial_status: "reviewed"
---

# COM-21

## Original interview question

What is NavHost, and how is state restored after process death?

## What the interviewer evaluates

- Explain navigation graph/back-stack ownership in Navigation Compose.
- Separate saved navigation/UI state from ViewModel and durable data.
- Test deep link and process recreation without overclaiming restoration.

## Concept and technical explanation

NavHost is the foundational container composable in Jetpack Compose Navigation that hosts a self-contained navigation graph and swaps screen destinations based on NavHostController state. State restoration across Android process death operates on two architectural levels: UI presentation state and business domain state. UI widget state (such as scroll positions and uncommitted text input) is preserved using rememberSaveable backed by SaveableStateRegistry, which serializes data into the platform saved instance state Bundle. Business state inside architecture ViewModels is restored via SavedStateHandle, which automatically retains navigation arguments and query states across process recreation.

## Practical walkthrough (English)

Restoring UI and ViewModel state after process death in a Compose NavHost:
```kotlin
// 1. Business state surviving process death via ViewModel SavedStateHandle
@HiltViewModel
class SearchViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Survives process termination and system RAM reclamation!
    var query: String
        get() = savedStateHandle["search_query"] ?: ""
        set(value) { savedStateHandle["search_query"] = value }
}

// 2. UI presentation state surviving process death via rememberSaveable
@Composable
fun FilterableSearchScreen(viewModel: SearchViewModel) {
    // Survives process death and config changes via Bundle serialization!
    var isFilterExpanded by rememberSaveable { mutableStateOf(false) }

    Column(modifier = Modifier.padding(16.dp)) {
        TextField(
            value = viewModel.query,
            onValueChange = { viewModel.query = it },
            placeholder = { Text("Search...") }
        )
        FilterToggle(
            isExpanded = isFilterExpanded,
            onToggle = { isFilterExpanded = !isFilterExpanded }
        )
    }
}

// 3. NavHost container managing destinations and backstack state
@Composable
fun AppNavHost(navController: NavHostController) {
    NavHost(navController = navController, startDestination = "home") {
        composable("home") { HomeScreen(onOpenSearch = { navController.navigate("search") }) }
        composable("search") {
            val searchVm: SearchViewModel = hiltViewModel()
            FilterableSearchScreen(viewModel = searchVm)
        }
    }
}
```

## Explanation in Arabic

كيف يعمل الـ `NavHost` وكيف يتم استعادة حالة التطبيق بعد موت العملية (Process Death) في Jetpack Compose:

1. كيف يعمل الـ NavHost داخلياً؟
   - الـ `NavHost` هو حاوية Composable ترتبط بكائن الـ `NavHostController`.
   - يحتفظ بـ **BackStack** مكوّن من كائنات `NavBackStackEntry`.
   - كل `NavBackStackEntry` يمتلك دورة حياة خاصة به (`Lifecycle`), و `ViewModelStore` خاص به (لحفظ ViewModels خاصة بالوجهة), و `SavedStateRegistry` خاص به لاستعادة الحالة.

2. ما هو موت العملية (System-Initiated Process Death)؟
   - عندما يضع المستخدم التطبيق في الخلفية لعدة ساعات أو يفتح لعبة ثقيلة، يقوم نظام التشغيل بإنهاء عملية التطبيق (Kill Process) لتحرير الذاكرة.
   - عندما يعود المستخدم للتطبيق، يحاول النظام استعادة الشاشة التي كان يقف عليها بالضبط.

3. كيف تُستعاد الحالة عبر الـ NavHost و SavedStateHandle؟
   - يحتفظ الـ `NavHost` تلقائياً بمسار الـ BackStack بالكامل داخل الـ `Bundle` الخاص بالنشاط (`onSaveInstanceState`).
   - عند إعادة التشغيل، يعيد الـ `NavHost` بناء شجرة الشاشات السابقة بنفس الترتيب.
   - كائنات `rememberSaveable` في الشاشات السابقة تُستعاد فورياً من الـ `SaveableStateRegistry`.
   - الـ ViewModels المرتبطة بالوجهات تستعيد متغيراتها المحفوظة تلقائياً عبر **`SavedStateHandle`**.

## Practical walkthrough

استعادة حالة البحث وتفاصيل الشاشة عبر SavedStateHandle بعد موت العملية:
```kotlin
// في ViewModel: قراءة وحفظ الحالة داخل SavedStateHandle لضمان بقائها بعد موت العملية:
class SearchViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    // getStateFlow تحفظ القيمة تلقائياً في SavedStateHandle وتستعيدها فور موت العملية:
    val searchQuery: StateFlow<String> = savedStateHandle.getStateFlow("QUERY_KEY", "")

    fun onQueryChanged(newQuery: String) {
        savedStateHandle["QUERY_KEY"] = newQuery
    }
}

// في الـ NavHost: التنقل واستعادة الوجهة والحالة تلقائياً:
@Composable
fun AppNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController = navController, startDestination = "home") {
        composable("home") { HomeScreen(...) }
        composable("search") {
            // ViewModel مرتبط بالـ NavBackStackEntry ويستعيد SavedStateHandle تلقائياً:
            val searchVm: SearchViewModel = hiltViewModel()
            SearchRoute(viewModel = searchVm)
        }
    }
}
```

## Why it matters and how it works

The navigation host renders the current destination from a back stack. Back-stack entries provide owners for lifecycle, ViewModel and saved state, so scope choice affects retention and restoration. Android saved-state mechanisms can restore small navigation/UI information after eligible system recreation; they do not persist arbitrary process memory or unfinished external work. Durable business data belongs in a repository or persistent store.

## Worked example

An article route passes `articleId`, not an `Article` object. The destination ViewModel reads that ID from its saved-state handle and loads the article. A local selected tab uses saveable state. After system process recreation, NavHost returns to the article destination if the platform restores the task, the ViewModel is new, and it reloads by ID; a deleted article shows a valid error state.

### Compose/Kotlin walkthrough

```kotlin
// Navigation graph; article destination reads only a small stable ID.
@Composable
fun ArticleGraph(navController: NavHostController) {
NavHost(navController, startDestination = "feed") {
    composable("feed") { FeedScreen(onOpen = { id ->
        navController.navigate("article/$id")
    }) }
    composable("article/{articleId}") { entry ->
        val id = requireNotNull(entry.arguments?.getString("articleId"))
        ArticleRoute(articleId = id)
    }
}
}
// Imports: androidx.navigation.NavHostController, navigation.compose.NavHost/composable;
// encode arbitrary IDs
// before route interpolation, or use supported typed routes.
```

## Trade-offs and decision criteria

Small route arguments are robust and deep-linkable but require reloading. Saving large objects avoids a fetch only superficially and risks Bundle size/version problems. Graph-scoped ViewModels can share state across destinations, but overly broad ownership may leak stale flows. Navigation library generations differ; describe behavior for the installed version.

## Failure modes

The app assumes a ViewModel survives process death. A route serializes a large mutable entity. A destination depends on an in-memory Singleton cache and opens blank after restoration. A back-stack entry is scoped incorrectly, causing a prior account's state to reappear. A user-dismissed task is treated as guaranteed to restore.

## Production perspective

Test rotation, background system process death, deep links, and missing/stale IDs separately. Inspect saved-state size, use durable storage for user work, and add a loading/recovery path while data reloads.

## Interview answer — short

NavHost is the container composable that links a NavHostController to a navigation graph, displaying destinations based on backstack state. State restoration after system process death occurs at two levels. Local UI state like toggles or draft text uses rememberSaveable, which serializes into the Activity saved instance Bundle via SaveableStateHolder. Business state and arguments are restored inside ViewModels using SavedStateHandle, ensuring seamless recovery when the operating system kills the background process.

## Interview answer — structured

Managing screen destinations and surviving system-initiated process death is a critical benchmark for enterprise-grade Android applications.
NavHost serves as the primary composition viewport for Jetpack Navigation.
It observes the destination backstack emitted by NavHostController, mapping route strings or type-safe serializable destinations to their corresponding composable contents.
When Android reclaims application memory in the background due to RAM pressure, the operating system executes process death.
Restoring application state upon return requires two coordinated mechanisms.
For presentation state within the composable tree, developers replace remember with rememberSaveable.
While remember only survives recomposition, rememberSaveable serializes data into the Android platform saved instance state Bundle using built-in Savers for primitives or custom Savers for complex objects.
For business state inside ViewModels, we rely on SavedStateHandle.
Hilt automatically injects SavedStateHandle into ViewModels, providing a persistent key-value store that survives process destruction.
Furthermore, NavHost internally wraps backstack entries with SaveableStateHolder, guaranteeing that each destination's scroll offset and input state are saved and restored automatically when popping and pushing backstack destinations.

## Interview answer — deep senior

Under the hood, NavHost and process death state restoration rely on SaveableStateHolder and the AndroidX SavedStateRegistryOwner pipeline.
When NavHost navigates between composables, it utilizes SaveableStateHolder.SaveableStateProvider.
This component assigns a unique key to each backstack entry.
When a destination is covered by a new screen or temporarily unmounted, SaveableStateHolder invokes its internal saveState() logic, serializing that subcomposition's rememberSaveable slot values into a detached bundle dictionary rather than discarding them.
When the user pops the backstack to return, the runtime matches the entry key and restores the exact SlotTable interval values.
During system process death, the host Activity's onSaveInstanceState(outState: Bundle) triggers the root SaveableStateRegistry.
The registry serializes all active SaveableStateHolder dictionaries and ViewModel SavedStateHandles into the system-managed persistent Parcelable Bundle.
Upon process resurrection, the operating system launches a new Linux process, re-creates the Activity, and passes the saved Bundle into onCreate().
Compose's root RecomposeScope reads the registry, and SavedStateHandle restores its key-value map.
Because the operating system imposes a strict transaction buffer limit of roughly one megabyte across Binder IPC transactions, senior engineers ensure that only primitive identifiers, scroll indices, and query tokens are serialized, completely avoiding heavy domain payloads to prevent fatal TransactionTooLargeException crashes during process recreation.
Senior engineers test this resilience by enabling 'Don't keep activities' in Developer Options or executing 'adb shell am kill <package>' to verify that screens rehydrate flawlessly without throwing NullPointerExceptions or dropping user form drafts.

## How to answer in the interview

- **Why:** a back stack restores destination identity, not process memory.
- **How:** pass ID, recreate owner, reload authoritative data.
- **Trade-off:** saved state is small and restoration is platform-conditional.
- **Failure case:** in-memory singleton or large argument disappears.
- **Production solution:** test eligible process recreation and deleted-content errors.

## Deep-dive talking points

Discuss back-stack owners, saved arguments, ViewModel recreation, durable reload, deep links, and test conditions.

## Follow-up questions

- **Interviewer:** "What is `SaveableStateHolder` and how does NavHost use it?"
  **Answer:** "`SaveableStateHolder` allows saving and restoring the composition state of composable subtrees by key. `NavHost` uses it to preserve the UI state of backstack entries that are not currently displayed on screen."

- **Interviewer:** "How do you test process death locally without waiting for OS low-memory events?"
  **Answer:** "Enable 'Don't keep activities' in Developer Options to test configuration death, or send the app to background and run `adb shell am kill <package-name>` to simulate true OS process death."

## Self-check rubric

Trace one route through process recreation, assign owners, and handle stale data and non-restoration cases.

## References and reviewed-on date

- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — NavHost and destination practices.
- [Save UI state in Compose](https://developer.android.com/develop/ui/compose/state-saving) — process recreation limits.

Technically reviewed against primary documentation on 2026-10-13.
