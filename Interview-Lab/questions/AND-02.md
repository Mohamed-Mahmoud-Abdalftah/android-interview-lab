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

The Activity and Fragment lifecycles form the core mechanism through which the Android operating system manages device memory, window visibility, and user interaction states.

1. Activity Lifecycle:
   - `onCreate()`: Invoked when the Activity instance is first created in memory. Dependencies are injected, ViewModels acquired, and layout hierarchies initialized via `setContentView()` or Jetpack Compose `setContent()`.
   - `onStart()`: The window becomes visible to the user, but may not yet possess interactive touch focus. This callback is the entry point for starting UI-bound data observers.
   - `onResume()`: The Activity transitions into the foreground and gains full interactive focus. This state is appropriate for initiating exclusive hardware resources, such as camera previews or fine-grained location sensors.
   - `onPause()`: The Activity loses interactive focus due to partial occlusion, such as when a system dialog, permission request, or multi-window divider appears. Exclusive hardware access should pause here.
   - `onStop()`: The window is completely hidden from view because the user transitioned to another task or returned home. Heavy rendering, location polling, and background UI updates must stop.
   - `onDestroy()`: Called before the Activity instance is cleared from memory, either because the user explicitly finished the screen (`finish()`) or because the OS initiated a configuration change recreation.
   - `onRestart()`: Dispatched when an Activity transitions from a stopped state back toward visibility, immediately preceding `onStart()`.

2. Fragment Lifecycle:
   - Fragments live within a host Activity and follow its lifecycle constraints, but introduce an essential separation between the Fragment class instance and its view hierarchy.
   - The Fragment instance lifecycle spans from initialization to final detachment. In contrast, the view lifecycle, accessed through `viewLifecycleOwner`, spans strictly between `onCreateView()` and `onDestroyView()`.

## Practical walkthrough (English)

State transitions under realistic runtime scenarios:
- Normal in-app Dialog:
  The Activity remains in the `RESUMED` state because standard dialogs belong to the same window hierarchy as the host Activity.
- OS Permission Dialog:
  The Activity moves to `onPause()` because a separate system-owned window captures interactive focus. Upon dismissal, the Activity transitions back to `onResume()`.
- Screen Rotation:
  The Activity executes: `onPause()` -> `onStop()` -> `onSaveInstanceState()` -> `onDestroy()`. It is then reconstructed in the new orientation through: `onCreate()` -> `onStart()` -> `onResume()`.
- Multi-Window Split Screen:
  Both adjacent activities are in the `STARTED` state and fully visible. Only the specific window the user is actively touching is in `RESUMED`.

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

The Activity lifecycle manages screen visibility and focus across six core callbacks: onCreate for setup, onStart and onStop for visibility boundaries, onResume and onPause for interactive focus, and onDestroy for final teardown. Fragments mirror these transitions under their host Activity, but introduce a separate view lifecycle where the view tree can be destroyed and recreated while the Fragment instance remains retained in memory.

## Interview answer — structured

The Android lifecycle is fundamentally a state machine that governs memory reclamation, window visibility, and user interaction. The framework organizes Activity execution into three nested lifetime loops. The entire lifespan runs between onCreate and onDestroy, where we bind dependencies and tear down process-level references.

The visible lifespan runs between onStart and onStop. When the screen becomes visible, we prepare the UI to render data, and when it is hidden, we stop active animations, location updates, and heavy UI rendering.

The foreground interactive lifespan is defined by onResume and onPause. When an Activity enters onResume, it gains exclusive touch focus, whereas onPause signals partial occlusion, such as when a system dialog or multi-window divider appears.

In production, Fragments introduce a critical architectural caveat because a Fragment instance frequently outlives its view hierarchy on the backstack. Consequently, modern Android development delegates all UI observation to viewLifecycleOwner and repeatOnLifecycle, preventing background processing and memory leaks when the screen is obscured.


## Interview answer — deep senior

At the OS runtime and Linux kernel boundary, lifecycle callbacks represent the primary heuristic for the Low Memory Killer daemon, or lmkd, to determine process priority. The ActivityManagerService dynamically updates the out-of-memory adjustment score, oom_adj, of each Linux process based on its top component state. A foreground Activity in onResume is assigned TOP_APP priority with an oom_adj score of zero, granting it maximum immunity against process reclamation. As the Activity transitions to onStop, its process priority drops to the CACHED_APP tier, where the kernel can terminate it via SIGKILL under memory pressure without executing onDestroy.

From an execution and threading perspective, all six lifecycle callbacks are posted as individual messages to the Main Thread Looper via ActivityThread and the ClientTransactionHandler. Because of this, blocking operations inside any callback will immediately delay message queue processing and trigger an Application Not Responding condition if dispatch exceeds five seconds.

At a staff architecture level, we strictly treat lifecycle callbacks as integration ports rather than repositories for business logic. In modern Jetpack architectures, state persistence is decoupled across three tiers: ephemeral UI state survives configuration changes via ViewModelStore, transient navigation state is serialized to the system server process via SavedStateHandle during onSaveInstanceState, and durable truth is committed asynchronously to a local database. Furthermore, by observing state with repeatOnLifecycle scoped to Lifecycle.State.STARTED, we leverage coroutine cancellation mechanics under the hood to ensure that cold StateFlow collectors automatically suspend execution upon onStop, eliminating resource contention and background thread leaks across complex multi-window or picture-in-picture transitions.

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
