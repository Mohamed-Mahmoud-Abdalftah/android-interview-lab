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

## Concept and technical explanation

Lifecycle callbacks describe the state of a particular Activity or Fragment instance; they are not a persistence or process-survival contract. `onCreate()` sets up a new Activity instance, `onStart()` makes it visible, and `onResume()` marks it resumed. `onPause()` and `onStop()` move it out of those states; `onRestart()` precedes `onStart()` when a stopped instance returns. `onDestroy()` runs for a normal finish or framework recreation, but is not guaranteed when Android kills a cached process. Visibility, focus, and resumed state should not be treated as identical, especially in multi-window and on newer Android versions that allow multiple resumed activities.

A Fragment has its own lifecycle, constrained by its host and FragmentManager. A Fragment with a view has a *separate* view lifecycle. Its view can be destroyed on the back stack while the Fragment object remains; it can then receive a new view. Use `viewLifecycleOwner` for collectors and observers that touch views, and release ViewBinding references in `onDestroyView()`. A Fragment-scoped ViewModel can outlive the view; an Activity-scoped ViewModel may also be shared with other Fragments. Both survive eligible configuration recreation through their owner's `ViewModelStore`, but neither survives process death as the same object.

## Practical walkthrough (English)

Consider an order screen in a View-based Fragment. The repository can own the order stream, the ViewModel can map it into UI state, and the Fragment collects it only while its *view* is `STARTED`. Navigation may destroy that view while keeping the Fragment instance on the back stack. On return, a new view and a new view-lifecycle collector are created. Rotation usually recreates the Activity and Fragment instances; the appropriate ViewModel can be retained through their owner's store, while the view is rebuilt. After system process death, even the ViewModel object is new: recover a lightweight order ID from saved state and reload durable data from storage. Save a confirmed order when the operation happens, never only in `onDestroy()`.

Do not memorize a universal callback trace for every dialog, permission UI, or rotation. `onSaveInstanceState()` timing relative to `onStop()` differs across platform versions, and callbacks depend on the actual window and configuration behavior. Instrument the Activity and Fragment lifecycles when the precise ordering matters. In multi-window, visible activities need not share the same focus or lifecycle state; Android 10 and later can have multiple resumed activities.

## Explanation in Arabic

فكّر في الـ Lifecycle كحدود ملكية: إمتى الشاشة موجودة، إمتى ظاهرة، وإمتى ينفع تستخدم مورد محتاج تفاعل. `onCreate()` بيجهّز نسخة الـ Activity، و`onStart()` يدخلها حالة الظهور، و`onResume()` يدخلها حالة Resumed. لما الحالة تتغير، `onPause()` و`onStop()` بيحددوا وقت إيقاف الشغل المرتبط بالشاشة. `onRestart()` بييجي قبل `onStart()` لو نفس النسخة راجعة من Stopped. `onDestroy()` ممكن يحصل عند إنهاء الشاشة أو إعادة إنشائها، لكنه مش Callback مضمون قبل قتل الـ Process.

الـ Fragment له Lifecycle تحت تحكم الـHost والـFragmentManager، والـView بتاعته لها Lifecycle تانية. ممكن تسيب Fragment على الـBack Stack فتتدمر الـView وتفضل نسخة الـFragment، وبعد الرجوع تتبني View جديدة. أي Collector أو Observer بيحدّث الـUI اربطه بـ`viewLifecycleOwner`، وصفّر مرجع الـViewBinding في `onDestroyView()`. الـViewModel ممكن يفضل عبر Configuration Change بحسب الـOwner بتاعه، لكن بعد Process Death بيتعمل Object جديد؛ استرجع مفتاح صغير من Saved State، وحمّل البيانات الحقيقية من مصدر دائم.

## Practical walkthrough

في شاشة طلبات معمولة بـFragment وViews، اربط جمع `uiState` بـ`viewLifecycleOwner.repeatOnLifecycle(STARTED)`. لو فتحت شاشة تانية والـView الأولى اتدمرت، الـCollector يتلغى والـViewBinding يتصفّر. لما ترجع، الـView الجديدة تبدأ Collector جديد من أحدث State. عند Rotation غالبًا الـActivity والـViews بيتبنوا من جديد؛ الـViewModel المناسب للـOwner ممكن يفضل. بعد Process Death مفيش نفس ViewModel في الذاكرة: احفظ `orderId` صغير في Saved State وحمّل الطلب من Repository. متعتمدش على `onDestroy()` لتأكيد طلب أو كتابة مالية.

ولو حد سألك عن ترتيب `onSaveInstanceState()` مع `onStop()` أو تأثير Dialog وMulti-window، متديش تسلسل ثابت لكل الإصدارات. ترتيب الحفظ اتغير عبر إصدارات Android، وMulti-resume ممكن يخلي أكتر من Activity في `RESUMED`. اختبر الحالة الفعلية وسجّل الـCallbacks عند الحاجة.

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

## Trade-offs and decision criteria

Start/stop is a practical boundary for visible UI updates, but a camera preview or exclusive hardware resource may require a tighter resumed/paused boundary. A repository can keep data current independently of the screen, while view rendering should follow the view lifecycle. Lifecycle-aware APIs reduce manual registration bugs, but they do not automatically persist business data or make work survive process death.

## Failure modes

Registering a listener in `onStart` but removing it only in `onDestroy` duplicates callbacks after stop/start. Observing with Fragment lifecycle can keep a destroyed view binding reachable. Writing a transaction to disk only in `onDestroy()` loses it if Android kills the process. Test rotation, navigation away/back, multi-window visibility, and actual background process restoration; inspect leaks and duplicate collectors.

## Production perspective

On a live order screen, a repository owns the order stream, a ViewModel maps it into display state, and the Fragment's view owner collects only while visible. A foreground-only scanner opens its camera at an appropriate interactive state and closes it when no longer eligible. Durable order changes are committed before leaving a critical action, not from a terminal lifecycle callback. Metrics capture duplicate listeners and long main-thread callbacks.

## Interview answer — short

An Activity moves through created, started, resumed, paused, stopped, and destroyed states as its screen changes visibility and interaction. A Fragment has its own host-constrained lifecycle plus a separate view lifecycle: its view can be destroyed while the Fragment object remains. I use the view owner for UI collectors and never rely on `onDestroy()` for a final save.

## Interview answer — structured

I use the Activity lifecycle to decide who owns work. `onStart()` and `onStop()` bound visibility; `onResume()` and `onPause()` describe a tighter resumed period, but I do not equate those callbacks with exclusive focus on every Android version. A View-based Fragment adds another boundary: its view can be destroyed on the back stack while the Fragment instance remains. I collect UI state with `viewLifecycleOwner.repeatOnLifecycle(STARTED)` and clear ViewBinding in `onDestroyView()`. For example, returning to an order screen creates a new view collector that renders current ViewModel state. Rotation usually recreates the screen instance while an appropriately scoped ViewModel can survive; process death creates a new ViewModel, so I restore a small order ID from saved state and reload durable order data. I commit important writes when the action succeeds, not from `onDestroy()`.


## Interview answer — deep senior

The ownership decision is more useful than a memorized callback chart. An Activity may be visible but not resumed; multi-window behavior depends on platform version, and multiple Activities can be resumed on Android 10 and later. Choose `STARTED` for visible UI rendering and a tighter `RESUMED` boundary only when the resource requires it. Register and unregister listeners symmetrically. Lifecycle callbacks normally run on the main thread, so blocking them can delay frames or contribute to an ANR; no universal five-second rule applies to every callback and input path.

For a View-based Fragment, collect from `viewLifecycleOwner.lifecycleScope` with `repeatOnLifecycle`. Leaving `STARTED` cancels the inner block; returning launches it again. If the upstream is cold, restarting collection can repeat upstream work, so put sharing or caching at the right owner rather than assuming lifecycle awareness makes network work free. A `StateFlow` collector gets current state when it restarts, not every intermediate value it missed. Clear binding in `onDestroyView()` and avoid passing a View or Activity Context into a longer-lived ViewModel.

Configuration recreation can retain a ViewModel through the owner's `ViewModelStore`, not the Activity or Fragment object itself. Process death destroys that in-memory ViewModel. A `SavedStateHandle` is appropriate for small restorable UI keys while the task's saved state is available; it is not durable storage for completed orders or payments. Keep durable data in an appropriate local/server store and reconstruct UI from it. `onSaveInstanceState()` is a state-saving hook, but its ordering versus `onStop()` has differed by API level, and `onDestroy()` is not a final-write guarantee. I would test rotation, back-stack view recreation, process restoration, and multi-window on supported devices instead of promising one exact callback trace.

## How to answer in the interview

- **Why:** Resource ownership must match the period when the screen can use it.
- **How:** Explain Activity creation, visible, interactive, stopped, and destroyed states plus the Fragment view owner.
- **Trade-offs:** Pick STARTED or RESUMED based on the resource, not habit.
- **Failure cases:** Describe stale view collectors and missing cleanup after rapid transitions.
- **Production solution:** Give the location screen’s registration, state restoration, and rotation test.

## Deep-dive talking points

Contrast visibility with focus, Fragment and view owners, `repeatOnLifecycle` cancellation/restart, cleanup symmetry, ViewModel retention, and why no lifecycle callback guarantees a final durable write before process death.

## Follow-up questions

- **Interviewer:** "Is `onDestroy()` guaranteed to be called when the user exits the app?"
  **Answer:** "No! If the user presses the home button and the OS kills the process in the background due to low memory, `onDestroy()` is never called. Never place critical data persistence solely inside `onDestroy()`."

- **Interviewer:** "Does Back always destroy the Activity and Home always preserve it?"
  **Answer:** "No. Navigation behavior depends on the task, back stack, and predictive-back integration. Home normally moves the task away, but Android may later kill its process without `onDestroy()`. I test the actual task and restoration path instead of promising a callback trace."

- **Interviewer:** "What is `onRestart()` and when is it invoked?"
  **Answer:** "`onRestart()` is called between `onStop()` and `onStart()` when an Activity that was previously hidden is brought back to the foreground by the user."

## Self-check rubric

Order the main Activity states; distinguish Fragment object and view lifecycle; choose STARTED versus RESUMED for a resource; explain cleanup symmetry; and describe a process-death limitation.

## References and reviewed-on date

- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — state transitions and process behavior.
- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — Fragment and view lifecycle distinction.
- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — configuration recreation, process death, and state ownership.
- [Multi-window lifecycle](https://developer.android.com/guide/topics/large-screens/multi-window-support) — multi-resume and visibility behavior.

Technically reviewed against primary documentation on 2026-10-19. The AndroidX example is illustrative here; no Android compilation was run for this question.
