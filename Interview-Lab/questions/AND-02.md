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

دورة حياة الـ Activity والـ Fragment هي صميم عمل نظام أندرويد لإدارة الذاكرة والـ UI:

1. دورة حياة الـ Activity (Activity Lifecycle):
   - `onCreate()`: يتم استدعاؤها عند إنشاء الكائن في الذاكرة لأول مرة. هنا نقوم بتهيئة الـ ViewModel، حقن الاعتماديات، وضبط الـ View (`setContentView` أو `setContent`).
   - `onStart()`: تصبح الشاشة **مرئية للمستخدم (Visible)** ولكنها قد لا تكون في بؤرة التركيز التفاعلي (مثل وجود Dialog نصف شفاف أمامها).
   - `onResume()`: تصبح الشاشة **في المقدمة وقابلة للتفاعل باللمس بالكامل (Foreground & Interactive)**.
   - `onPause()`: تفقد الشاشة بؤرة التركيز جزئياً (Partial occlusion)، مثل ظهور نافذة إذن النظام أو الدخول في Multi-window.
   - `onStop()`: تصبح الشاشة **غير مرئية بالكامل (Hidden)** لأن المستخدم فتح تطبيقا آخر أو ضغط زر Home. هنا يتم إيقاف التحديثات الثقيلة.
   - `onDestroy()`: يتم تدمير الـ Activity بالكامل إما بسبب إنهاء المستخدم لها (`finish()`) أو بسبب Configuration Change.

2. دورة حياة الـ Fragment:
   - تتبع نفس المراحل، ولكنها تضيف فصلاً حاسماً بين **دورة حياة كائن الـ Fragment نفسه** و **دورة حياة الـ View المعروضة (`viewLifecycleOwner`)**.

## Practical walkthrough

ماذا يحدث بالضبط عند فتح Dialog أو عند تدوير الشاشة؟
- **فتح Dialog عادي داخل التطبيق:**
  الـ Activity تظل في حالة `RESUMED` لأن الـ Dialog جزء من نفس نافذة الـ Activity!
- **فتح Permission Dialog الخاص بنظام أندرويد (OS Permission Dialog):**
  الـ Activity تنتقل إلى `onPause()` لأن نافذة تابعة لنظام التشغيل حازت على بؤرة التركيز، ثم تعود لـ `onResume()` عند إغلاق الإذن.
- **تدوير الشاشة (Screen Rotation):**
  تنتقل بالترتيب: `onPause()` -> `onStop()` -> `onSaveInstanceState()` -> `onDestroy()` -> ثم يعاد بناؤها: `onCreate()` -> `onStart()` -> `onResume()`.

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

Activity transitions through onCreate() (initialization), onStart() (visible), onResume() (interactive), onPause() (partially visible/lost focus), onStop() (hidden), and onDestroy() (destroyed). Fragments mirror these states but possess an independent view lifecycle via viewLifecycleOwner.

## Interview answer — structured

The Android lifecycle represents the operating system's mechanism for managing memory constraints, window visibility, and user interaction states:

The six core Activity callbacks form matched pairs:

1. **`onCreate()` / `onDestroy()`**: Represents the entire lifespan of the Activity instance in memory. In `onCreate`, we initialize dependencies, ViewModels, and UI layouts.
2. **`onStart()` / `onStop()`**: Represents the visible lifespan. In `onStart`, the UI is visible to the user. In `onStop`, the Activity is completely hidden from view (e.g., app backgrounded). This is where heavy rendering and sensor listeners should pause.
3. **`onResume()` / `onPause()`**: Represents the foreground, interactive lifespan. In `onResume`, the window has full touch focus. In `onPause`, the window has lost focus (e.g., covered by a multi-window app or a system permission dialog).

Fragments mirror these states, but critically decouple the Fragment object lifecycle from the view lifecycle (`viewLifecycleOwner`), which can be destroyed and recreated independently when placed on the Fragment backstack.

## Interview answer — deep senior

From an architectural standpoint, modern Android applications avoid placing business logic or direct resource registration inside these callbacks. Instead, we use `DefaultLifecycleObserver` and `repeatOnLifecycle`.

Consider state preservation across the transition to `onStop()`: Between `onPause()` and `onStop()`, the OS invokes `onSaveInstanceState(Bundle)`. Once `onStop()` is called, the app process enters the 'killable' pool: if system RAM runs low, the OS kernel can terminate the entire Linux process without ever calling `onDestroy()`.

In modern Jetpack architecture, `androidx.lifecycle.Lifecycle` abstracts these callbacks into states (`INITIALIZED`, `CREATED`, `STARTED`, `RESUMED`, `DESTROYED`) and events. Coroutines observe these states via `repeatOnLifecycle(Lifecycle.State.STARTED)`, which automatically cancels background collectors in `onStop()` and restarts them in `onStart()`.

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

- **Interviewer:** "What is the difference between pressing the 'Back' button and pressing the 'Home' button?"
  **Answer:** "Pressing Back finishes the Activity (transitioning through onPause -> onStop -> onDestroy), signalling intentional termination. Pressing Home simply backgrounds the Activity (onPause -> onStop), preserving it in the recent apps stack."

- **Interviewer:** "What is `onRestart()` and when is it invoked?"
  **Answer:** "`onRestart()` is called between `onStop()` and `onStart()` when an Activity that was previously hidden is brought back to the foreground by the user."

## Self-check rubric

Order the main Activity states; distinguish Fragment object and view lifecycle; choose STARTED versus RESUMED for a resource; explain cleanup symmetry; and describe a process-death limitation.

## References and reviewed-on date

- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — state transitions and process behavior.
- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — Fragment and view lifecycle distinction.

Technically reviewed against primary documentation on 2026-10-13.
