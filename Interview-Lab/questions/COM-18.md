---
id: "COM-18"
question: "What are Route Composable and Screen Composable?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 247
editorial_status: "reviewed"
---

# COM-18

## Original interview question

What are Route Composable and Screen Composable?

## What the interviewer evaluates

- Separate app wiring/navigation from reusable rendering.
- Explain state collection, ViewModel ownership and callbacks.
- Avoid treating the split as a framework requirement.

## Explanation in Arabic

الفرق المعماري بين الـ Route Composable والـ Screen Composable وكيف يعزز هذا الفصل جودة واختبار التطبيق:

1. ما هو الـ Route Composable (المكون الموجّه)؟
   - هو المكون المرتبط مباشرة بنظام التنقل (`NavGraphBuilder.composable("route")`).
   - **مسؤولياته**:
     * حقن الـ `ViewModel` (عبر `hiltViewModel()` أو `viewModel()`).
     * جمع الـ UI State عبر `collectAsStateWithLifecycle()`.
     * تمرير الأحداث والتنقل (`onNavigateBack`, `onNavigateToDetails`).
     * لا يحتوي على أي عناصر تصميم أو كود Layout مباشر!

2. ما هو الـ Screen Composable (المكون البصري للشاشة)؟
   - هو المكون البصري النقي الذي يرسم عناصر الشاشة الفعلية (Scaffold, Column, Cards).
   - **مسؤولياته**:
     * استقبال الـ `UiState` المكتمل كـ Parameter.
     * استقبال أحداث المستخدم كـ Lambdas مستقلة (`onItemClicked: (Id) -> Unit`).
     * **عديم الحالة تماماً (Stateless)** ولا يعلم أي شيء عن وجود `ViewModel` أو `NavController`!

3. لماذا يُعتبر هذا الفصل معياراً إجبارياً في الشركات الكبرى؟
   - **إمكانية عمل Previews فورية في Android Studio**: الـ Screen Composable لا يعتمد على ViewModel أو DI، لذا يعمل الـ `@Preview` ببيانات وهمية فوراً!
   - **سهولة كتابة اختبارات Screenshot و UI Tests**: يمكنك اختبار رسم حالات الخطأ والنجاح دون الحاجة لـ Mocking لمكتبات Hilt و Navigation.

## Practical walkthrough

الفصل المعماري القياسي بين Route Composable و Screen Composable:
```kotlin
// 1. Route Composable: يربط التنقل والـ ViewModel بالواجهة (Stateful Coordinator):
@Composable
fun OrderDetailsRoute(
    onNavigateBack: () -> Unit,
    viewModel: OrderDetailsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    OrderDetailsScreen(
        uiState = uiState,
        onBackClicked = onNavigateBack,
        onCancelOrder = viewModel::cancelOrder
    )
}

// 2. Screen Composable: كود بصري نقي بدون أي ارتباط بـ ViewModel أو Navigation (Stateless UI):
@Composable
fun OrderDetailsScreen(
    uiState: OrderDetailsUiState,
    onBackClicked: () -> Unit,
    onCancelOrder: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(modifier = modifier) {
        when (uiState) {
            is OrderDetailsUiState.Loading -> LoadingView()
            is OrderDetailsUiState.Success -> {
                OrderContent(order = uiState.order, onCancel = onCancelOrder)
            }
            is OrderDetailsUiState.Error -> ErrorView(uiState.message)
        }
    }
}
```

## Why it matters and how it works

The route couples the screen to application concerns such as a back stack entry, dependency creation, and lifecycle collection. The screen is a rendering function over explicit inputs, so preview and Compose tests can supply states directly. Event callbacks flow to the route or ViewModel. The navigation owner matters because a ViewModel scoped to the wrong graph or destination can retain or lose state unexpectedly.

## Worked example

`ProductRoute(productId, onBack)` retrieves its ViewModel and `uiState`, then calls `ProductScreen(state, onRetry, onAddToCart, modifier)`. The Screen renders loading/error/product content in preview without Hilt or NavController. The Route handles Add-to-Cart result navigation and parses a small ID, while repository loading remains in the ViewModel.

### Compose/Kotlin walkthrough

```kotlin
@Composable
fun ProductRoute(viewModel: ProductViewModel = viewModel(), onBack: () -> Unit) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    ProductScreen(state, onRetry = viewModel::retry, onBack = onBack)
}
@Composable
fun ProductScreen(state: ProductState, onRetry: () -> Unit, onBack: () -> Unit) {
    Column {
        TextButton(onClick = onBack) { Text("Back") }
        when (state) {
            ProductState.Loading -> CircularProgressIndicator()
            is ProductState.Error -> Button(onClick = onRetry) { Text("Retry") }
            is ProductState.Ready -> Text(state.title)
        }
    }
}
// Requires lifecycle-runtime-compose and lifecycle-viewmodel-compose.
```

## Trade-offs and decision criteria

The split improves testability and keeps UI dependencies narrow, but adds function parameters and can become ceremony for a tiny static screen. Passing a single state object and focused callbacks balances readability. Avoid an excessively generic `onEvent(Any)` API that hides contracts.

## Failure modes

The Screen reaches into NavController, breaking previews and reuse. The Route holds long-lived mutable form data only in a local variable. The ViewModel is obtained under the Activity owner when it should be destination-scoped, causing stale data on back-stack changes. A route serializes a large object in navigation arguments.

## Production perspective

Adopt consistent ownership in feature modules, provide previews for key states, and test Route integration separately from Screen rendering. Verify back-stack recreation and deep-link arguments for screens that navigate independently.

## Interview answer — short

A Route Composable is stateful and navigation-aware: it injects the ViewModel, collects `StateFlow` via `collectAsStateWithLifecycle()`, and binds navigation lambdas. A Screen Composable is stateless and pure: it accepts plain `UiState` and event lambdas, enabling instant Android Studio Previews and isolated UI testing.

## Interview answer — structured

Separating a feature screen into a **Route Composable** and a **Screen Composable** is the industry standard for scalable Jetpack Compose architecture.

First, with The Route Composable (`...Route`), acts as the orchestration boundary registered inside the `NavHost`. Its sole purpose is dependency resolution and lifecycle coordination: it retrieves the ViewModel (e.g. `hiltViewModel()`), collects UI state using `collectAsStateWithLifecycle()`, and bridges navigation callbacks (`onNavigateToDetail`). It contains zero layout logic. Finally, with The Screen Composable (`...Screen`), acts as the pure declarative presentation layer. It takes only the resolved, immutable `UiState` and hoisted event callbacks (`onAction: (Action) -> Unit`). It knows nothing about `ViewModel`, Hilt, or `NavController`.

This architectural separation delivers enormous benefits.

First, frictionless Previews is the Screen composable can be rendered in Android Studio `@Preview` instantly with fake data without mocking complex ViewModel dependencies. Finally, with Screenshot & UI Testing, screenshot tests (using Paparazzi or Roborazzi) and Compose UI tests can assert every visual permutation (`Loading`, `Error`, `Empty`) purely by passing fake states.


## Interview answer — deep senior

Under the hood, passing a `ViewModel` directly into a leaf UI Composable creates tight architectural coupling. If a composable references `viewModel.someProperty` or `navController.navigate()`, testing that composable requires a simulated `ViewModelStoreOwner`, instantiated coroutine dispatchers, and mocked navigation graphs.

Furthermore, passing `NavController` deep into composable trees violates encapsulation and modularization. In multi-module Android apps, feature modules should not depend on the global app navigation graph. By hoisting navigation callbacks out of the Screen composable up to the Route composable, each feature module remains completely isolated and independently compilable.

In our enterprise design pattern, every screen file has the canonical structure: `OrderDetailsRoute` at the top, `OrderDetailsScreen` below it, and multiple preview functions demonstrating distinct UI states.


## How to answer in the interview

- **Why:** separating integration from rendering makes states testable.
- **How:** route collects and delegates; screen renders explicit inputs.
- **Trade-off:** tiny screens may not need two files.
- **Failure case:** wrong back-stack owner changes ViewModel lifetime.
- **Production solution:** preview Screen and integration-test Route navigation.

## Deep-dive talking points

Explain app boundary, UI inputs, ViewModelStoreOwner, previews, typed events, and test layers.

## Follow-up questions

- **Interviewer:** "Why shouldn't you pass `NavController` directly into a Screen Composable?"
  **Answer:** "Passing `NavController` couples your UI to navigation implementation details, prevents previews in Android Studio, complicates UI unit testing, and breaks multi-module encapsulation boundaries."

- **Interviewer:** "Can a Route Composable be previewed in Android Studio?"
  **Answer:** "Typically no, because it requires active Hilt injection and navigation backstacks. We preview the pure Screen Composable instead."

## Self-check rubric

Assign wiring and rendering tasks, name the owner, and propose one Screen test and one Route test.

## References and reviewed-on date

- [Compose architecture](https://developer.android.com/develop/ui/compose/architecture) — state/event separation.
- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — destination boundaries.

Technically reviewed against primary documentation on 2026-10-13.
