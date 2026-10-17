---
id: "ARC-11"
question: "How do you expose loading, content, empty, and error state?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 156
editorial_status: "reviewed"
---

# ARC-11

## Original interview question

How do you expose loading, content, empty, and error state?

## What the interviewer evaluates

Model mutually exclusive loading/content/empty/error states and avoid losing cached content on refresh failure.

## Concept and technical explanation

In modern Android and Jetpack Compose, UI state must be exposed as a single, immutable, type-safe representation via StateFlow to guarantee predictable recomposition and compile-time exhaustiveness. The four fundamental UI states of a screen are Loading (initial data retrieval or background refresh), Content (populated data models ready for rendering), Empty (valid response containing zero items, prompting onboarding or alternative actions), and Error (failure conditions containing actionable retry metadata). Modeling these states as a sealed interface hierarchy (or an immutable data class with explicit state flags) prevents impossible intermediate states—such as showing both a progress spinner and an error banner simultaneously—and ensures that the UI remains a pure, passive reflection of state.

## Practical walkthrough (English)

Exposing exhaustive UI states with a sealed interface in Jetpack Compose:
```kotlin
// 1. Sealed interface models mutually exclusive screen states
sealed interface ProductsUiState {
    object Loading : ProductsUiState
    data class Content(val products: List<ProductItemUiModel>) : ProductsUiState
    object Empty : ProductsUiState
    data class Error(val errorMessage: String, val canRetry: Boolean) : ProductsUiState
}

// 2. ViewModel exposes single StateFlow
class ProductsViewModel(private val repository: ProductRepository) : ViewModel() {
    val uiState: StateFlow<ProductsUiState> = repository.observeProducts()
        .map { list ->
            if (list.isEmpty()) ProductsUiState.Empty
            else ProductsUiState.Content(list.map { it.toUiModel() })
        }
        .catch { emit(ProductsUiState.Error(it.localizedMessage ?: "Unknown error", canRetry = true)) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), ProductsUiState.Loading)
}

// 3. Compose UI renders exhaustively via when expression
@Composable
fun ProductsScreen(uiState: ProductsUiState, onRetry: () -> Unit) {
    when (uiState) {
        is ProductsUiState.Loading -> CircularProgressIndicator()
        is ProductsUiState.Empty -> Text("No products found")
        is ProductsUiState.Error -> Button(onClick = onRetry) { Text("Retry: ${uiState.errorMessage}") }
        is ProductsUiState.Content -> LazyColumn { items(uiState.products) { ProductRow(it) } }
    }
}
```

## Explanation in Arabic

كيف تعرض وتصمم حالات التحميل (Loading)، المحتوى (Content)، القائمة الفارغة (Empty)، والخطأ (Error) باحترافية؟

1. معضلة الحالات المتضاربة (The Multiple-Boolean Anti-Pattern):
   - الخطأ الكلاسيكي هو استخدام متغيرات منفصلة في الـ ViewModel:
     `val isLoading = MutableStateFlow(false)` و `val error = MutableStateFlow<String?>(null)` و `val items = MutableStateFlow<List<Item>>(emptyList())`.
   - النتيجة: قد يكون `isLoading = true` و `error != null` في نفس اللحظة! مما يربك الـ Composable ويجعله يعرض Spinner فوق رسالة خطأ!

2. الحل المعماري الأول: الـ Sealed Interface (للحالات الحصرية):
   - ممتاز للشاشات الكاملة التي تنتقل بين حالات واضحة متنافية:
     * `data object Loading : FeedUiState`
     * `data object Empty : FeedUiState`
     * `data class Success(val items: ImmutableList<FeedItem>) : FeedUiState`
     * `data class Error(val message: String) : FeedUiState`
   - الميزة: مستحيل تمثيل حالة غير منطقية (Illegal States are Unrepresentable).

3. الحل المعماري الثاني: الـ Combined Data Class (للتحديث الجزئي / Pull-to-Refresh):
   - عندما تحتاج الشاشة لعرض القائمة القديمة مع وجود مؤشر تحميل خفيف في الأعلى (Pull-to-refresh) أو Snackbar خطأ دون مسح المحتوى:
     * `data class FeedUiState(val items: ImmutableList<FeedItem>, val isRefreshing: Boolean, val error: String?)`.

## Practical walkthrough

تطبيق النمطين باحترافية في Jetpack Compose:
```kotlin
// النمط 1: Sealed Interface للشاشات الكاملة المتبادلة حصرياً:
sealed interface ProductListUiState {
    data object Loading : ProductListUiState
    data object Empty : ProductListUiState
    data class Success(val products: ImmutableList<Product>) : ProductListUiState
    data class Error(val message: String) : ProductListUiState
}

@Composable
fun ProductListScreen(uiState: ProductListUiState, onRetry: () -> Unit) {
    when (uiState) {
        is ProductListUiState.Loading -> FullScreenLoadingSpinner()
        is ProductListUiState.Empty -> EmptyStatePlaceholder("No products found")
        is ProductListUiState.Success -> ProductList(uiState.products)
        is ProductListUiState.Error -> ErrorBanner(uiState.message, onRetry = onRetry)
    }
}
```

## Why it matters and how it works

UI state should be a complete, renderable snapshot. Choose exclusive cases when states cannot coexist, or orthogonal fields when content and refresh status can coexist. Data source freshness and errors should remain distinguishable.

## Worked example

Illustrative Kotlin model:
```kotlin
data class FeedUiState(
    val items: List<Article> = emptyList(),
    val isInitialLoading: Boolean = true,
    val isRefreshing: Boolean = false,
    val refreshError: String? = null
)
data class Article(val id: String, val title: String)
```
For a no-cache screen, a sealed state can make Loading/Content/Empty/Error mutually exclusive.

## Trade-offs and decision criteria

Sealed cases prevent impossible combinations; a data class supports simultaneous cached content and refresh status. Do not create a giant Boolean matrix without invariants. Decide whether errors replace content or appear alongside it based on product requirements.

## Failure modes

A failed refresh sets `items = emptyList()` and UI shows Empty, losing valid cached content and hiding the outage. Preserve cached items, show a non-destructive refresh error, and test offline/retry paths.

## Production perspective

A news feed observes Room, refreshes in background, and displays stale articles with a visible timestamp when offline. Initial load failure and refresh failure have different UI treatment and retry behavior.

## Interview answer — short

Expose UI state as a single, immutable sealed hierarchy or data class through StateFlow. This guarantees compile-time exhaustiveness in Compose when statements, prevents contradictory intermediate states like simultaneous loading and error banners, and models loading, content, empty, and error conditions with explicit type safety.

## Interview answer — structured

Modeling UI states explicitly eliminates unpredictable visual glitches and simplifies screen rendering logic in Jetpack Compose.

The ViewModel exposes a single StateFlow rather than multiple disparate Boolean flags. We model states using a sealed interface with discrete variants: Loading for initial data retrieval, Content carrying immutable list models, Empty for zero-result states, and Error encapsulating actionable diagnostic messages.

In production, when the screen opens, the ViewModel initiates the Loading state. If the repository emits an empty list, the state transitions explicitly to Empty, rendering tailored user guidance rather than a blank canvas. If an exception occurs, the Error state supplies retry actions.
As for maintenance advantages, this pattern enforces compile-time exhaustiveness in UI Composables. When engineers add new state variants—such as an offline cached banner—the compiler forces every screen branch to handle the transition safely without silent runtime failures.


## Interview answer — deep senior

Under the hood, whether to model UI state as a sealed interface hierarchy or a single comprehensive data class depends on screen complexity and transition overlap. A sealed interface like sealed interface ScreenState containing Loading, Success, Empty, and Error provides mathematical exclusivity: the UI can never accidentally render both an error message and a loading spinner at the same time because only one type exists in the StateFlow at any given millisecond.
However, in production applications with partial screen refreshes—such as swipe-to-refresh or pagination—a sealed hierarchy can be restrictive because transitioning to Loading destroys the existing Success state, wiping content off the screen and causing jarring visual flickers.
In such scenarios, staff engineers prefer a unified immutable data class: data class ScreenUiState containing items, isRefreshing, and userErrorMessage. This approach preserves existing list data while toggling an overlaid isRefreshing spinner or non-blocking Snackbar message.
Furthermore, staff engineers enforce Compose stability by annotating UI state classes with Immutable or Stable and using kotlinx.collections.immutable structures like ImmutableList to avoid unnecessary recomposition passes when parent Composable trees evaluate parameters. This architectural rigor guarantees fluid sixty frames per second rendering across complex state transitions. By rigorously separating presentation states and maintaining exhaustive branch coverage, teams eliminate entire classes of visual regressions and deliver deterministic user experiences.

## How to answer in the interview

- **Why:** users need honest transition states.
- **How:** model exclusive and concurrent state explicitly.
- **Trade-off:** simple sealed type versus combinational needs.
- **Failure case:** error wipes usable cached content.
- **Production solution:** test loading-to-content/error sequences.

## Deep-dive talking points

Compare exclusive and coexisting states; show a cached-content refresh transition; explain why Empty requires successful load.

## Follow-up questions

- **Interviewer:** "Why shouldn't you clear the existing items list when a refresh fails?"
  **Answer:** "Clearing the list replaces visible content with a blank error screen. Keeping cached data and displaying a transient snackbar error ensures the user can continue reading offline content."

- **Interviewer:** "How do you handle pagination loading vs initial screen loading?"
  **Answer:** "Initial loading uses a full-screen state or skeleton loader. Pagination loading is modeled as a footer append state (`isAppendingPage = true`) at the end of the existing content list."

## Self-check rubric

Predict UI after initial failure, successful empty response, and failed refresh with cache. Each needs a different state and user action.

## References and reviewed-on date

- [Android UI state holders](https://developer.android.com/topic/architecture/ui-layer/stateholders) — screen UI state.
- [Android offline-first guide](https://developer.android.com/topic/architecture/data-layer/offline-first) — local data during network failure.

Technically reviewed against primary documentation on 2026-10-13.
