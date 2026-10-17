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

## Concept and technical explanation

The repeatOnLifecycle and collectAsStateWithLifecycle APIs represent modern Android's official, lifecycle-aware flow collection mechanisms designed to eliminate background execution waste and UI crashes.
repeatOnLifecycle is a suspending extension on LifecycleOwner (or Lifecycle) used primarily in imperative View-based architectures or coroutine launch blocks. It restarts a new coroutine executing the provided block whenever the lifecycle reaches a target state (typically Lifecycle.State.STARTED), and actively cancels that coroutine when the lifecycle drops below that state (e.g., entering STOPPED when the app is backgrounded).
collectAsStateWithLifecycle is a specialized Jetpack Compose Composable operator that wraps repeatOnLifecycle under the hood. It collects emissions from a Flow in a lifecycle-aware manner, converting the latest value into a Compose State<T> snapshot, and automatically halts collection when the hosting Composable's lifecycle drops below the specified minimum active state.

## Practical walkthrough (English)

Applying lifecycle-aware collection in Views and Jetpack Compose:
```kotlin
// 1. In Views (Fragments / Activities) using repeatOnLifecycle:
class UserProfileFragment : Fragment(R.layout.fragment_profile) {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            // Suspends when view is destroyed; restarts on STARTED, cancels on STOPPED:
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.profileState.collect { state ->
                    updateProfileViews(state)
                }
            }
        }
    }
}

// 2. In Jetpack Compose using collectAsStateWithLifecycle:
@Composable
fun UserProfileScreen(viewModel: ProfileViewModel) {
    // Automatically pauses collection when app is in background:
    val uiState by viewModel.profileState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is ProfileUiState.Loading -> FullScreenSpinner()
        is ProfileUiState.Success -> ProfileContent(state.user)
    }
}
```

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

repeatOnLifecycle executes and cancels a coroutine block as the lifecycle enters and leaves a target state, ideal for Views; collectAsStateWithLifecycle is its Compose equivalent, collecting a Flow into a Compose State while automatically pausing collection when the app backgrounds.

## Interview answer — structured

These APIs guarantee that UI components collect data streams strictly while the user is actively viewing the screen.

Standard coroutine collection using lifecycleScope.launch continues collecting even when the app is in the background, wasting CPU cycles and network data. repeatOnLifecycle solves this by launching collection at Lifecycle.State.STARTED and cancelling the coroutine when the UI enters STOPPED.

In production, Jetpack Compose applications originally used collectAsState(), which observes flows throughout composition existence without pausing when the screen is placed in the background. Google introduced collectAsStateWithLifecycle to bridge this gap, ensuring that Compose applications pause flow consumption during backgrounding.

Pairing WhileSubscribed(5000) on ViewModels with collectAsStateWithLifecycle or repeatOnLifecycle ensures that upstream subscription counts drop to zero in the background, shutting down hardware sensors and database queries cleanly.


## Interview answer — deep senior

Under the hood in androidx.lifecycle, repeatOnLifecycle creates a custom LifecycleObserver. When the target state (e.g., STARTED) is entered via onStart, the observer launches a new child coroutine in the parent scope, executing the user's suspended block. When the lifecycle drops to STOPPED via onStop, the observer explicitly cancels the launched child coroutine by throwing a CancellationException.
If the Activity returns to the foreground later, onStart fires again, and repeatOnLifecycle launches an entirely fresh coroutine, resubscribing to the Flow from scratch. This periodic restart is what decrements StateFlow's subscriptionCount to zero when combined with SharingStarted.WhileSubscribed(5000), cleanly terminating upstream database queries and network sockets after the five-second grace period.
The Compose extension collectAsStateWithLifecycle wraps this exact pattern: it integrates remember(flow, lifecycle, minActiveState) and produces a State<T> backed by produceState. Whenever the Composable transitions to the background, produceState stops flow collection, preventing redundant recompositions and memory retention.
A critical architectural pitfall in legacy code was using lifecycleScope.launchWhenStarted. Google officially deprecated launchWhenStarted because it merely suspended the coroutine instead of cancelling it; keeping collectors suspended in the background held resources open and prevented upstream flows from shutting down.
Staff engineers mandate collectAsStateWithLifecycle across all Compose screens to guarantee zero background CPU waste and maximum battery efficiency.

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
