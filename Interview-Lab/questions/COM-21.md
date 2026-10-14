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

`NavHost` coordinates navigation by rendering composables bound to a backstack of `NavBackStackEntry` instances, each possessing its own Lifecycle, ViewModelStore, and SavedStateRegistry. Following process death, `NavHost` restores the full backstack hierarchy from the Activity's saved instance state bundle, while ViewModels recover state via `SavedStateHandle`.

## Interview answer — structured

The `NavHost` manages the presentation of destinations defined in a navigation graph, mapping navigation backstack entries to active composables.

First, with BackStack Architecture, under the hood, the `NavHost` orchestrates a stack of `NavBackStackEntry` objects. Each entry is an isolated architectural scope with three distinct responsibilities. Next, its own **Lifecycle**: Transitions to `RESUMED` when on top, and `CREATED` when pushed into the backstack.
Its own **ViewModelStore**: Scoping destination-specific ViewModels that survive configuration changes and clear only when popped off the backstack. Its own **SavedStateRegistry**: Providing slot isolation for `rememberSaveable` calls.
Finally, with Process Death Restoration, when the OS terminates an application in the background, Android invokes Activity `onSaveInstanceState()`. The `NavController` serializes the destination backstack and typed route arguments into this Bundle.

Upon relaunch, `NavHost` rebuilds the backstack structure. Screen composables restore local UI state through `rememberSaveable`, while ViewModels restore saved inputs and queries via **`SavedStateHandle`**, making process recovery seamless to the user.


## Interview answer — deep senior

Testing process death restoration is mandatory for enterprise applications. We verify this via ADB: putting the app in the background (`pressHome()`) and executing `adb shell am kill <package_name>`, then relaunching the app from the recent apps switcher. If a screen crashes or resets to a blank state, it exposes un-hoisted memory state that wasn't backed by `SavedStateHandle` or `rememberSaveable`.

Inside `NavHost`, transitions between destinations are animated using Compose animations (`enterTransition`, `exitTransition`). When navigating forward, `SaveableStateHolder` saves the composition state of the leaving composable and unbinds its Slot Table nodes from memory to preserve RAM. When popping the backstack, `SaveableStateHolder` restores the saved composition state, instantly recovering scroll positions and local text fields without re-instantiating the screen.


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
