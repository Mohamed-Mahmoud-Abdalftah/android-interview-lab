---
id: "FLO-22"
question: "Compare repeatOnLifecycle and collectAsStateWithLifecycle."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 135
editorial_status: "reviewed"
---

# FLO-22

## Original interview question

Compare repeatOnLifecycle and collectAsStateWithLifecycle.

## What the interviewer evaluates

Compare lifecycle-aware View collection with Compose state collection and restart semantics.

## Explanation in Arabic

المقارنة بين `repeatOnLifecycle` و `collectAsStateWithLifecycle` هي جوهر استهلاك البيانات الآمن دورياً (Lifecycle-Safe Collection) في أندرويد:

1. المشكلة في الجمع التقليدي (`collect` العادي في `lifecycleScope`):
   - لو كتبت `lifecycleScope.launch { flow.collect { } }`، الـ Coroutine ستظل تجمع وتستقبل بيانات حتى لو التطبيق في الخلفية (Background) والشاشة غير مرئية!
   - هذا يستهلك المعالج والبطارية ويرسل طلبات شبكة ويحدث Views غير مرئية في الخلفية.

2. دالة `repeatOnLifecycle(Lifecycle.State)` (في XML / Views):
   - دالة Suspending تعيد تشغيل الـ Coroutine عندما يصل الـ Lifecycle لحالة معينة (عادة `STARTED`).
   - **وتلغي الـ Coroutine تلقائياً فوراً** عندما ينزل الـ Lifecycle تحت تلك الحالة (مثل `STOPPED` عند وضع التطبيق في الخلفية)!
   - عند عودة المستخدم للتطبيق، يعاد تشغيل الـ Collection من جديد بنظافة.

3. دالة `collectAsStateWithLifecycle()` (في Jetpack Compose):
   - هي التوأم المخصص لـ Jetpack Compose.
   - تستمع للـ Flow بطريقة Lifecycle-aware وتنتج Compose `State<T>`.
   - تتوقف عن جمع البيانات تلقائياً عندما تكون الشاشة في الخلفية، وتستأنف عند العودة.

## Practical walkthrough

مقارنة عملية في الكود:
```kotlin
// 1. في XML Activity / Fragment:
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)
    viewLifecycleOwner.lifecycleScope.launch {
        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            viewModel.uiState.collect { state ->
                renderUi(state)
            }
        }
    }
}

// 2. في Jetpack Compose Composable:
@Composable
fun ProfileScreen(viewModel: ProfileViewModel) {
    // توأم repeatOnLifecycle المخصص لـ Compose:
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    ProfileContent(state)
}
```

## Why it matters and how it works

`repeatOnLifecycle` is a suspending API whose child block restarts serially as lifecycle state changes. `collectAsStateWithLifecycle` is a convenience for rendering a stream as Compose state. For multiple flows in Views, collect them in separate child launches inside the repeat block so one endless collect does not block the next.

## Worked example

Android Fragment conceptual snippet; `state` is `StateFlow<UiState>`, `render` and UiState are app types, and lifecycle runtime KTX is required.

```kotlin
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.material3.Text
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

// Call after Fragment.onViewCreated; use the shorter view lifecycle.
fun Fragment.collectStatus(flow: StateFlow<String>, render: (String) -> Unit) {
    viewLifecycleOwner.lifecycleScope.launch {
        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            flow.collect { render(it) }
        }
    }
}

@Composable
fun StatusScreen(flow: StateFlow<String>) {
    val status by flow.collectAsStateWithLifecycle()
    Text(status)
}
// Requires lifecycle-runtime-ktx, lifecycle-runtime-compose, Fragment, Compose.
```

## Trade-offs and decision criteria

View API offers explicit block control; Compose API is concise for renderable state. Use an effect collector only after deciding replay/loss behavior. Lifecycle-aware collection reduces offscreen work but is not a process-death persistence mechanism.

## Failure modes

Using Fragment.lifecycleScope instead of viewLifecycleOwner can collect after view destruction. Launching a raw collect once in lifecycleScope does not stop at STOP. A cold source may restart and duplicate network calls on every START unless shared upstream.

## Production perspective

A Fragment collects screen StateFlow under repeatOnLifecycle, while a Compose screen uses collectAsStateWithLifecycle. ViewModel shares expensive upstream with stateIn and a grace period; rotation tests verify current state and no duplicate effects.

## Interview answer — short

repeatOnLifecycle pauses and restarts coroutine collection when an Android Lifecycle enters and exits a specified target state (e.g. STARTED) in View-based code; collectAsStateWithLifecycle is its Jetpack Compose equivalent, converting a Flow into Compose State with automatic background collection pausing.

## Interview answer — structured

Both APIs solve the critical problem of **Lifecycle-Safe Flow Collection**, ensuring that backgrounded Android screens stop observing data streams to conserve battery and CPU.

**`repeatOnLifecycle(Lifecycle.State.STARTED)`** is designed for the View/XML layer (Activities and Fragments). It is a suspending function that launches a collection block when the lifecycle enters `STARTED`. When the user minimizes the app and the lifecycle drops to `STOPPED`, it **cancels the coroutine immediately**. When the user returns to the app, it relaunches the block fresh.

**`collectAsStateWithLifecycle()`** is the specialized Jetpack Compose equivalent from `androidx.lifecycle.compose`. It collects a Flow in a lifecycle-aware manner (defaulting to `Lifecycle.State.STARTED`) and emits a Compose `State<T>`. When the app goes into the background, it suspends collection, preventing recompositions and stopping upstream cold flows until the screen is visible again.

## Interview answer — deep senior

Historically, developers used `flowWithLifecycle()`. However, `repeatOnLifecycle` is vastly superior because it can host multiple parallel flow collections inside a single block, avoiding multiple observer allocations:

```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        launch { viewModel.feed.collect { ... } }
        launch { viewModel.notifications.collect { ... } }
    }
}
```

In Jetpack Compose, using plain `collectAsState()` is an antipattern because it keeps the flow collection active as long as the composable is part of the composition tree, even when the Activity is paused or stopped in the background. `collectAsStateWithLifecycle()` internally uses `repeatOnLifecycle` under the hood to unsubscribe from the Flow during backgrounding, which in turn triggers `WhileSubscribed(5000)` in the ViewModel to shut down upstream network and database sensors.

## How to answer in the interview

- **Why:** UI collection should follow its visible owner.
- **How:** Views repeatOnLifecycle versus Compose collector.
- **Trade-off:** upstream may continue despite stopped UI collection.
- **Failure case:** Fragment collects after its view is destroyed.
- **Production solution:** test stop/start and correct owner selection.

## Deep-dive talking points

Trace START/STOP cycles, cold restart, StateFlow replay and Fragment view destruction.

## Follow-up questions

- **Interviewer:** "Why must you use `viewLifecycleOwner` instead of `this` in Fragments?"
  **Answer:** "Because a Fragment's view lifecycle is destroyed and recreated separately from the Fragment instance itself (e.g., when placed on the backstack). Using `viewLifecycleOwner` ensures flow collection cancels when the view is destroyed, preventing view memory leaks."

- **Interviewer:** "Why is `Lifecycle.State.STARTED` the recommended state instead of `RESUMED`?"
  **Answer:** "`STARTED` ensures that the UI updates even when partially visible in multi-window or picture-in-picture mode. `RESUMED` only runs when the window has full user touch focus, which pauses updates in split-screen mode."

- **Interviewer:** "What dependency is required for `collectAsStateWithLifecycle`?"
  **Answer:** "It requires the `androidx.lifecycle:lifecycle-runtime-compose` dependency."

## Self-check rubric

Can I use both APIs correctly, choose Fragment view owner and predict restart behavior?

## References and reviewed-on date

- [Android lifecycle coroutines](https://developer.android.com/topic/libraries/architecture/coroutines) — repeatOnLifecycle.
- [Android Compose lifecycle state](https://developer.android.com/reference/kotlin/androidx/lifecycle/compose/package-summary) — collectAsStateWithLifecycle.

Technically reviewed against primary documentation on 2026-10-13.
