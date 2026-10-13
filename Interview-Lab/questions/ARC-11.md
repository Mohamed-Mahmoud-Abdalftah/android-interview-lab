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

Expose loading, content, empty, and error states using either a Sealed Interface for mutually exclusive full-screen transitions (making illegal states unrepresentable) or an Immutable Data Class when retaining content during background refresh or transient error snackbars.

## Interview answer — structured

Modeling screen states requires choosing the correct abstraction between mutually exclusive transitions and persistent content overlays.

1. **The Sealed Interface Pattern (Mutually Exclusive)**:
   - Ideal for screen-level states where only one visual representation can exist at a time (e.g. initial load, fatal error, empty catalog, or success grid).
   - By defining `sealed interface UiState { Loading, Empty, Success(data), Error(msg) }`, the compiler enforces exhaustive `when` expressions in Compose.
   - It makes invalid states—such as showing a full-screen loading spinner and an error message simultaneously—structurally impossible to represent.

2. **The Consolidated Data Class Pattern (Overlay / Partial Updates)**:
   - Ideal for screens supporting pull-to-refresh, pagination, or non-fatal errors.
   - When a user pulls to refresh, wiping the screen to show a full-screen spinner is terrible UX. Instead, a data class retaining `items`, `isRefreshing = true`, and `transientError = null` keeps existing items visible while displaying a top progress bar.

Both patterns avoid the legacy anti-pattern of exposing multiple independent reactive booleans that easily desynchronize.

## Interview answer — deep senior

Under the hood, in Compose, transitioning between sealed interface branches requires smooth visual coordination. Using `AnimatedContent(targetState = uiState)` enables seamless crossfade or slide transitions between `Loading`, `Content`, and `Error` states without jarring screen flashes.

When dealing with `Empty` states specifically, senior architects differentiate between a **true empty list** (the query returned zero records) and an **uninitialized state** (the query has not started). Modeling `data object Empty : UiState` provides dedicated UI real estate (illustration, helper text, clear filter button) that encourages user engagement.

In unit testing, testing a sealed interface is remarkably expressive: asserting `assertThat(state).isInstanceOf<UiState.Success>()` provides instant, type-safe validation of state progression.

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
