---
id: "AND-02"
question: "Explain the Activity and Fragment lifecycles."
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 32
editorial_status: "reviewed"
---

# AND-02

## Original interview question

Explain the Activity and Fragment lifecycles.

## What the interviewer evaluates

- Describe the major Activity and Fragment transitions as ownership boundaries, not a callback memorization contest.
- Use the Fragment view lifecycle for view-bound observers and release references at the right time.
- Account for configuration recreation and process death without relying on `onDestroy()` for persistence.

## Explanation in Arabic

الـActivity بتتحرك بين `onCreate` للتهيئة، `onStart` لما تبقى ظاهرة، `onResume` للتفاعل في المقدمة، وبعدها `onPause` و`onStop` لما تفقد التفاعل أو الظهور، و`onDestroy` لما instance تنتهي بشكل عادي. الـFragment مربوط بالـFragmentManager وعنده callbacks مشابهة، لكن الـview بتاعته ليها lifecycle مستقل يبدأ بعد `onCreateView` وينتهي في `onDestroyView`. عشان كده observer بيكتب في views يتربط بـ`viewLifecycleOwner`، مش عمر Fragment كله. بعد rotation ممكن instances تتبدل، وبعد process death كل memory تروح؛ ما تعتمدش على callback أخير عشان تحفظ بيانات مهمة.

## Why it matters and how it works

Lifecycle states tell a component when resources may be visible or interactive. An Activity can be paused yet visible in multi-window, so avoid equating `onPause` with complete invisibility. Fragment lifecycle is constrained by its host and FragmentManager state, while its view lifecycle can end and restart independently. `repeatOnLifecycle(STARTED)` starts a UI collector while the relevant owner is started and cancels it when stopped. This prevents hidden screens from continuing view updates and avoids retaining destroyed views.

## Worked example

In a View-based Fragment, the collection belongs to the **view** owner. The app supplies `OrderViewModel`, `OrderUiState`, and a `render` function; the snippet assumes AndroidX Fragment/Lifecycle KTX and `uiState: StateFlow<OrderUiState>`.
```kotlin
import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch

class OrderFragment : Fragment(R.layout.order) {
    private val viewModel: OrderViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect(::render)
            }
        }
    }

    private fun render(state: OrderUiState) { /* update this view only */ }
}
```
With ViewBinding, clear its field in `onDestroyView`; do not retain the view in the ViewModel.

## Practical walkthrough

في screen بتعرض live location، اسأل إمتى الواجهة visible وإمتى فعليًا محتاجة sensor. Activity `onStart/onStop` يحدّدوا visibility على نطاق واسع؛ `onResume/onPause` قد يناسبوا resource حصري محتاج foreground interaction. في Fragment فيه lifecycle للobject وواحد للـview؛ collector اللي بيرسم UI لازم يستخدم `viewLifecycleOwner` عشان view تتشال وتتعمل تاني من غير duplicate collectors. لا تعتمد على `onDestroy` لحفظ transaction مهمة؛ process kill ممكن يحصل من غيره. اختبر rotation وBack وتبديل app وsplit-screen على الأجهزة المستهدفة.

## Trade-offs and decision criteria

Start/stop is a practical boundary for visible UI updates, but a camera preview or exclusive hardware resource may require a tighter resumed/paused boundary. A repository can keep data current independently of the screen, while view rendering should follow the view lifecycle. Lifecycle-aware APIs reduce manual registration bugs, but they do not automatically persist business data or make work survive process death.

## Failure modes

Registering a listener in `onStart` but removing it only in `onDestroy` duplicates callbacks after stop/start. Observing with Fragment lifecycle can keep a destroyed view binding reachable. Writing a transaction to disk only in `onDestroy()` loses it if Android kills the process. Test rotation, navigation away/back, multi-window visibility, and actual background process restoration; inspect leaks and duplicate collectors.

## Production perspective

On a live order screen, a repository owns the order stream, a ViewModel maps it into display state, and the Fragment's view owner collects only while visible. A foreground-only scanner opens its camera at an appropriate interactive state and closes it when no longer eligible. Durable order changes are committed before leaving a critical action, not from a terminal lifecycle callback. Metrics capture duplicate listeners and long main-thread callbacks.

## Interview answer — short

“Activity lifecycle describes creation, visibility, interaction, and teardown. Fragment has a similar owner lifecycle plus a separate, shorter view lifecycle. I bind view updates to the viewLifecycleOwner, stop visible-only work when the UI stops, and never rely on `onDestroy()` to save critical data.”

## Interview answer — structured

An Activity moves through create, start, resume, pause, stop, and destruction as its visibility and interaction change. A Fragment follows its host and manager, but its view can be destroyed while the Fragment remains. In a Fragment I collect UI state with the viewLifecycleOwner, commonly using repeatOnLifecycle at STARTED, and release binding in onDestroyView. I choose resource boundaries by whether a screen is visible or interactive. Configuration recreation and process death require separate restoration strategies.

## Interview answer — deep senior

I use lifecycle states to define resource ownership instead of attaching everything to onCreate/onDestroy. An Activity can be visible but not resumed, especially in multi-window, so a visible data collector may follow STARTED while an exclusive camera follows a tighter interaction policy. A Fragment's object and view lifetimes differ; view-bound flows, adapters, and bindings belong to the view owner and end at onDestroyView. Repositories can outlive the UI for data consistency, but external side effects need deliberate persistence and idempotency. I test stop/start, back-stack view recreation, rotation, and process death separately and watch for duplicate observers or retained old views. I choose a lifecycle state based on the resource, not a memorized callback list.

I would then apply the callbacks to one real resource. A camera preview may need to stop when the UI is no longer interactive, while a list collector can often run while the screen is visible at STARTED. Multi-window can separate visibility from focus, so a rigid “everything in onResume” policy is fragile. Rotation recreates UI, but it does not imply a durable save; process death is another path. I test rapid navigation and background/foreground transitions, then verify that there is one active listener and no reference to the destroyed view.

## How to answer in the interview

- **Why:** Resource ownership must match the period when the screen can use it.
- **How:** Explain Activity creation, visible, interactive, stopped, and destroyed states plus the Fragment view owner.
- **Trade-offs:** Pick STARTED or RESUMED based on the resource, not habit.
- **Failure cases:** Describe stale view collectors and missing cleanup after rapid transitions.
- **Production solution:** Give the location screen’s registration, state restoration, and rotation test.

## Deep-dive talking points

Contrast visibility with focus, Fragment and view owners, `repeatOnLifecycle` cancellation/restart, cleanup symmetry, ViewModel retention, and why no lifecycle callback guarantees a final durable write before process death.

## Follow-up questions

- [AND-03](../and-03/): Which owner should observe a Fragment's view? **Answer:** `viewLifecycleOwner`, since the view may end before the Fragment object.
- [AND-17](../and-17/): Where do you unregister a visible listener? **Answer:** at the symmetric stop boundary used to register it, or use a lifecycle-aware API.
- [AND-07](../and-07/): Can `onDestroy()` be a process-death save hook? **Answer:** no; Android may terminate the process without that callback.

## Self-check rubric

Order the main Activity states; distinguish Fragment object and view lifecycle; choose STARTED versus RESUMED for a resource; explain cleanup symmetry; and describe a process-death limitation.

## References and reviewed-on date

- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — state transitions and process behavior.
- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — Fragment and view lifecycle distinction.

Technically reviewed against these primary sources on 2026-10-13 by editorial review. The Fragment collection flow is descriptive and not a compiled snippet.
