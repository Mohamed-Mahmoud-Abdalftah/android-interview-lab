#!/usr/bin/env python3
"""Elevate AND-02, AND-03, AND-04, AND-05 for bilingual parity and senior spoken answers."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
METADATA_PATH = ROOT / "scripts/elevations/data/arabic_lab_metadata.json"
QUESTIONS_DIR = ROOT / "Interview-Lab/questions"

# ==============================================================================
# CANONICAL MARKDOWN DEFINITIONS
# ==============================================================================

AND_02_MD = """---
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

To begin with, the Android lifecycle is fundamentally a state machine that governs memory reclamation, window visibility, and user interaction. The framework organizes Activity execution into three nested lifetime loops. The entire lifespan runs between onCreate and onDestroy, where we bind dependencies and tear down process-level references. From an architectural standpoint, the visible lifespan runs between onStart and onStop. When the screen becomes visible, we prepare the UI to render data, and when it is hidden, we stop active animations, location updates, and heavy UI rendering. As for boundary management, the foreground interactive lifespan is defined by onResume and onPause. When an Activity enters onResume, it gains exclusive touch focus, whereas onPause signals partial occlusion, such as when a system dialog or multi-window divider appears. In production scenarios, Fragments introduce a critical architectural caveat because a Fragment instance frequently outlives its view hierarchy on the backstack. Consequently, modern Android development delegates all UI observation to viewLifecycleOwner and repeatOnLifecycle, preventing background processing and memory leaks when the screen is obscured.

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
"""


AND_03_MD = """---
id: "AND-03"
question: "Compare Fragment lifecycle and Fragment view lifecycle."
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 33
editorial_status: "reviewed"
---

# AND-03

## Original interview question

Compare Fragment lifecycle and Fragment view lifecycle.

## What the interviewer evaluates

- Explain how a Fragment instance can outlive one of its view trees.
- Scope binding, observers, and UI coroutines to the view owner rather than the Fragment object.
- Diagnose a retained binding or duplicate collector after back-stack navigation.

## Concept and technical explanation

The structural difference between a Fragment instance lifecycle and its view hierarchy lifecycle (`viewLifecycleOwner`) accounts for the vast majority of memory leaks in Fragment-based Android architectures.

1. Fundamental Distinction:
   - **Fragment Instance Lifecycle:** Extends from instantiation and `onAttach()` through `onCreate()` until final destruction in `onDestroy()` and `onDetach()`. It represents the Java/Kotlin object residing on the heap.
   - **Fragment View Lifecycle (`viewLifecycleOwner`):** Exists strictly between `onCreateView()` / `onViewCreated()` and `onDestroyView()`. It represents the rendered Android View hierarchy inflated onto the screen.

2. Backstack Asymmetry:
   - When Fragment A is replaced by Fragment B with `addToBackStack()`, FragmentManager keeps the Fragment A object alive in memory so its arguments, scroll position, and state holders are preserved.
   - However, the framework destroys Fragment A's rendered View hierarchy by calling `onDestroyView()` to reclaim graphics memory.
   - When the user presses the back button, Fragment A is not re-instantiated; instead, it executes `onCreateView()` and `onViewCreated()` to build a brand new View hierarchy.

3. The Classic ViewBinding and Coroutine Leaks:
   - If an engineer stores a `ViewBinding` in a non-null property without setting it to null in `onDestroyView()`, the retained Fragment holds the destroyed View hierarchy in memory, leaking root layouts and context references.
   - If an engineer collects a `Flow` or observes LiveData using `this` (the Fragment instance) inside `onViewCreated()`, every navigation back and forth attaches another observer, producing duplicated collectors and potential crashes.

## Practical walkthrough (English)

The standard architecture to avoid Fragment memory leaks:
```kotlin
class ProfileFragment : Fragment(R.layout.fragment_profile) {
    // 1. Backing property nullable for onDestroyView clearance:
    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentProfileBinding.bind(view)

        // 2. Bind coroutine collection to viewLifecycleOwner:
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { render(it) }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // 3. Mandatory nullification to release view hierarchy:
        _binding = null
    }
}
```

## Explanation in Arabic

المقارنة بين دورة حياة كائن الـ Fragment ودورة حياة الـ View المعروضة (`viewLifecycleOwner`) هي سبب وقوع 80% من أخطاء الـ Memory Leaks في الـ Fragments:

1. ما هو الفرق الجوهري؟
   - **كائن الـ Fragment (Instance Lifecycle):** يعيش من لحظة إنشاء الكلاس في الذاكرة حتى تدميره نهائياً (`onDestroy()`).
   - **كائن الـ View (`viewLifecycleOwner`):** يعيش **فقط** بين `onCreateView()` / `onViewCreated()` وبين `onDestroyView()`.

2. متى يتم تدمير الـ View مع بقاء الـ Fragment حياً في الذاكرة؟
   - عندما تستخدم **Fragment Backstack** (مثل: استبدال Fragment A بـ Fragment B مع مناداة `addToBackStack()`):
   - كائن Fragment A يظل حياً في الذاكرة بالكامل حتى يتمكن المستخدم من الرجوع إليه.
   - ولكن نظام أندرويد يقوم بـ **تدمير الـ Views الخاصة بـ Fragment A (`onDestroyView`)** لتوفير الذاكرة!

3. الكارثة البرمجية الشائعة (The Classic Memory Leak):
   - لو احتفظت بـ View Binding في متغير عادي ولم تصفره في `onDestroyView()`:
     `private var binding: FragmentProfileBinding? = null`
     فإن كائن الـ Fragment سيظل ممسكاً بالـ Views المدمرة، مما يسرب شجرة الـ Views بالكامل في الذاكرة!
   - ولو استمعت لـ Flow باستخدام `viewLifecycleOwner.lifecycleScope`، ستتوقف المراقبة عند تدمير الـ View بنظافة تامة.

## Practical walkthrough

النمط الصحيح لتجنب تسريب الذاكرة في الـ Fragments:
```kotlin
class ProfileFragment : Fragment(R.layout.fragment_profile) {
    // 1. المتغير nullable لتصفيره:
    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentProfileBinding.bind(view)

        // 2. استخدام viewLifecycleOwner للاستماع للـ Flow لمنع التسريب:
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { render(it) }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // 3. تصفير الـ binding إلزامي لتحرير الـ Views من الذاكرة:
        _binding = null
    }
}
```

## Why it matters and how it works

FragmentManager can keep a Fragment instance while destroying its rendered view, for example when a navigation transaction places it on the back stack. Its `viewLifecycleOwner` is available only after the view is created and reaches DESTROYED around `onDestroyView`. Lifecycle-aware observation with that owner terminates before a new view is attached. A Fragment-scoped ViewModel can keep logical screen state across view recreation, while a view reference must be reacquired each time.

## Worked example

Illustrative Fragment code using ViewBinding and Lifecycle KTX; `ScreenBinding` is the generated binding type, and `viewModel.uiState` is a `StateFlow` supplied by the app.

```kotlin
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch

class ScreenFragment : Fragment(R.layout.screen) {
    private var binding: ScreenBinding? = null

    override fun onViewCreated(view: android.view.View, savedInstanceState: android.os.Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding = ScreenBinding.bind(view)
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state -> binding?.title?.text = state.title }
            }
        }
    }

    override fun onDestroyView() {
        binding = null
        super.onDestroyView()
    }
}
```

The surrounding app must supply `viewModel` and `ScreenBinding`; this is not a stand-alone compiled program. Keep collectors free of references to a captured old binding across view recreation.

## Trade-offs and decision criteria

View-scoped collection restarts when a new view appears, which is appropriate for rendering current state. A Fragment-level scope can own work genuinely independent of the view, but never a view-bound adapter or binding. `StateFlow` replaying current state is suitable for restart; a one-shot event needs an explicit delivery policy. Compose hosted inside a Fragment still requires an appropriate composition disposal strategy tied to the view.

## Failure modes

Using `fragment.lifecycleScope` to collect into a binding can keep the collector after `onDestroyView`; it may update a detached view or crash when binding is null. Failing to clear an adapter/listener can retain the old hierarchy. Re-registering on every `onViewCreated` without view-owner cancellation duplicates work. Investigate with LeakCanary, collector counters, and navigation away/back tests.

## Production perspective

In a product-detail Fragment, a ViewModel holds the product ID and UI state; each new view renders the latest state using a view-bound collector. On navigating away, the binding and listeners are released even if the Fragment remains on the back stack. Tests move the Fragment through view destruction and recreation, then assert one active collector and no retained old root view.

## Interview answer — short

A Fragment instance lifecycle extends from creation through onDestroy and detachment, whereas its view lifecycle exists strictly between onCreateView and onDestroyView. When a Fragment is placed on the backstack, its view tree is destroyed to release graphics memory while the Fragment instance remains retained in memory. Consequently, view bindings and UI coroutine collections must strictly bind to viewLifecycleOwner to avoid memory leaks.

## Interview answer — structured

To begin with, the fundamental distinction between a Fragment and its view lifecycle lies in their asynchronous lifetimes during backstack navigation. When a Fragment is pushed onto the backstack, the operating system destroys its entire layout to reclaim RAM, yet retains the Fragment object instance in memory so that navigation arguments and scroll positions remain intact.

From an architectural standpoint, this asymmetry means that a single Fragment instance can generate multiple sequential view hierarchies across its lifetime. The Fragment instance lifecycle spans from initialization to final destruction, whereas the view lifecycle, exposed via viewLifecycleOwner, begins in onCreateView and terminates in onDestroyView.

As for boundary management, tying view-bound observers or coroutine collectors to the Fragment instance lifecycle rather than its view lifecycle causes severe memory leaks and duplicate execution. Every time the user returns from the backstack, a new observer is registered while the previous one continues referencing a detached view.

In production scenarios, we safeguard against this by strictly binding all UI flows, adapters, and ViewBinding references to viewLifecycleOwner, while ensuring that ViewBinding backing fields are explicitly reset to null inside onDestroyView.

## Interview answer — deep senior

Under the hood in the AndroidX FragmentManager, when a FragmentTransaction executes a replace operation with addToBackStack, the Fragment state machine drives the outgoing Fragment down from RESUMED to CREATED. During this transition, FragmentManager dispatches onDestroyView, which disposes of the underlying View hierarchy and transitions viewLifecycleOwner to the DESTROYED state, while keeping the Fragment instance in the CREATED state on the backstack record.

From an ART garbage collection and memory profiling standpoint, failure to null out the generated ViewBinding backing property inside onDestroyView constitutes a catastrophic memory leak. The retained Fragment instance holds a strong reference to the binding object, which directly references the root ViewGroup. This retains the entire child view tree, custom drawables, hardware acceleration rendering pipelines, and the host Activity context through the View.mContext field. In a production application with high-resolution image assets or complex layout hierarchies, keeping two or three such dead view trees on the backstack can easily consume over one hundred megabytes of native graphics and Java heap memory, triggering an OutOfMemoryError.

From a reactive coroutine architecture perspective, invoking lifecycleScope instead of viewLifecycleOwner.lifecycleScope inside onViewCreated registers a Job attached to the Fragment instance. When the user navigates forward and returns five times, five concurrent coroutine collectors remain active simultaneously, dispatching redundant state updates and potentially crashing the app with NullPointerExceptions when attempting to mutate views that have already been detached from the window. In staff-level codebases, we enforce this boundary via custom Lint rules or auto-clearing property delegates, or eliminate View hierarchies entirely by adopting Jetpack Compose with proper disposable effect boundaries.

## How to answer in the interview

- **Why:** The Fragment object may outlive its rendered view.
- **How:** Contrast Fragment lifecycle with `viewLifecycleOwner` and point to `onDestroyView`.
- **Trade-offs:** Keep screen state in a scoped ViewModel, view references in the view lifetime.
- **Failure cases:** Explain duplicate collection, stale binding, and leaked views.
- **Production solution:** Show view-scoped Flow collection and a navigate-away/back test.

## Deep-dive talking points

Explain view owner availability, back-stack view destruction, ViewBinding cleanup, lifecycle-aware StateFlow collection, adapter/listener retention, and why one-shot effects differ from current state.

## Follow-up questions

- **Interviewer:** "What happens if you observe a Flow with `this.lifecycleScope` inside `onViewCreated`?"
  **Answer:** "Every time the user navigates back to this Fragment from the backstack, `onViewCreated` runs again and attaches another active observer. If the user navigates back and forth 5 times, there will be 5 duplicate concurrent collectors executing UI updates!"

- **Interviewer:** "Can you avoid nulling out ViewBinding in `onDestroyView()` with auto-clearing delegates?"
  **Answer:** "Yes. Libraries often provide an `AutoClearedValue` delegate or lifecycle-observer delegate that automatically listens to `viewLifecycleOwner`'s `onDestroyView` event and sets the binding property to null automatically."

- **Interviewer:** "How does Jetpack Compose change this pattern?"
  **Answer:** "Jetpack Compose eliminates Fragment ViewBinding leaks entirely because Composables do not use persistent view hierarchy references. Compose state automatically cleans up when leaving composition."

## Self-check rubric

Describe one case where Fragment outlives its view; choose the right LifecycleOwner for UI collection; release binding at the correct callback; explain a leak symptom; and design a back-stack recreation test.

## References and reviewed-on date

- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — Fragment and view owner transitions.
- [Lifecycle-aware coroutine collection](https://developer.android.com/topic/libraries/architecture/coroutines) — restartable collection guidance.

Technically reviewed against primary documentation on 2026-10-13.
"""


AND_04_MD = """---
id: "AND-04"
question: "What is Context? Compare Activity Context and Application Context."
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 34
editorial_status: "reviewed"
---

# AND-04

## Original interview question

What is Context? Compare Activity Context and Application Context.

## What the interviewer evaluates

- Describe Context as access to app/system services, resources, and component operations.
- Match Context lifetime and visual configuration to the consumer.
- Spot a singleton retaining an Activity and a UI operation attempted with non-visual Application Context.

## Concept and technical explanation

Context is the central handle and abstract interface connecting application code to the Android operating system runtime. It provides access to application-specific resources, system services, local file sandboxes, and component launchers.

1. Role of Context:
   - Resource access: strings, drawables, assets, and display metrics.
   - System services: `LayoutInflater`, `WindowManager`, `LocationManager`, `NotificationManager`.
   - Inter-component communication: `startActivity()`, `startService()`, `sendBroadcast()`.

2. Application Context:
   - Tied directly to the lifecycle of the Linux application process via `getApplicationContext()`.
   - Outlives any individual screen and is destroyed only when the process is killed.
   - Safe to store in process-wide Singletons, Room database instances, and network repositories.
   - Limitations: Has no associated Window Token and does not carry Activity-specific theme styling; cannot host Dialogs or Window attachments.

3. Activity Context:
   - Tied directly to a single Activity screen's lifespan, destroyed upon screen finish or configuration recreation.
   - Subclasses `ContextThemeWrapper`, carrying explicit theme attributes, window tokens, and display configurations.
   - Mandatory for UI operations: displaying `AlertDialog`s, inflating themed layouts, and attaching window popups.
   - Leak hazard: Retaining an Activity Context in a singleton or background thread leaks the entire Activity and view hierarchy.

## Practical walkthrough (English)

Appropriate usage rules across layers:
1. Initialize Room Database or DataStore within a Singleton Repository:
   - Supply `context.applicationContext` to guarantee no transient Activity reference is leaked.
2. Display AlertDialog, Toast, or Inflate Themed Views:
   - Supply the Activity Context (`this` in Activity) to apply custom theme attributes and attach the dialog to the active Window Token.
3. Call `startActivity()`:
   - From an Activity Context: Seamlessly opens within the current task backstack.
   - From an Application Context: Requires `Intent.FLAG_ACTIVITY_NEW_TASK` because the Application lacks its own task stack.

## Explanation in Arabic

الـ `Context` هو أهم كائن في بيئة Android، وفهم الفرق بين `Activity Context` و `Application Context` يمنع حدوث أكبر كوارث الـ Memory Leaks والـ UI Glitches:

1. ما هو الـ Context بصفة عامة؟
   - هو الواجهة التي تربط كود تطبيقك **بنظام التشغيل Android (Handle to the System)**.
   - يسمح لك بالوصول للموارد (Resources, Strings, Drawables)، قواعد البيانات، خدمات النظام (LayoutInflater, WindowManager, LocationManager)، وتشغيل المكونات (startActivity).

2. الـ `Application Context` (مربوط بـ Process التطبيق):
   - يعيش طوال فترة حياة **التطبيق ككل (Singleton Lifecycle)** حتى يتم إنهاء الـ Linux Process.
   - **مستحيل تسريبه:** آمن تماماً للاحتفاظ به داخل Singletons، Repositories، أو كلاسات الـ Data Layer.
   - **حدوده:** ليس لديه Theme محدد، ولا يمكنه فتح Dialogs أو إنشاء نوافذ، واستخدامه مع `LayoutInflater` يؤدي لتجاهل ثيم الشاشة.

3. الـ `Activity Context` (مربوط بالشاشة الحالية):
   - يعيش فقط طالما الـ **Activity الحالية حية**، ويموت معها عند تدميرها أو تدوير الشاشة.
   - **مربوط بالـ Theme والـ Window:** قادر على رسم الـ UI، عرض الـ Dialogs، وتطبيق ثيمات التطبيق والألوان بدقة.
   - **خطر التسريب (Memory Leak Risk):** لو قمت بتمرير Activity Context لكائن Singleton أو Background Thread وظل ممسكاً به، فإنه سيسرب الـ Activity وشجرة الـ Views بالكامل في الـ Heap!

## Practical walkthrough

متى تستخدم أياً منهما؟
1. **تهيئة مكتبة Room أو DataStore داخل Singleton Repository:**
   - نستخدم **`context.applicationContext`** حتى نضمن عدم تسريب أي Activity.
2. **عرض AlertDialog أو Toast أو Inflating Layout:**
   - نستخدم **Activity Context** (`this` في Activity) لتطبيق الـ Theme وإرفاق النافذة بالـ Window Token الشرعي.
3. **استدعاء `startActivity`:**
   - لو استدعيتها من Activity Context: تفتح بسلاسة.
   - لو استدعيتها من Application Context: النظام يجبرك على إضافة `Intent.FLAG_ACTIVITY_NEW_TASK` لأن Application ليس لديه Task Stack خاص به!

## Why it matters and how it works

Context is an abstract handle through which Android exposes resources, services, package information, and component launches. Different Context implementations carry different configuration, theme, display, window, and lifecycle associations. An Activity Context reflects that Activity's current visual environment; Application Context outlives individual screens but may not represent a visual container's current configuration, especially with multi-window or foldables. The choice is therefore about capabilities and ownership, not merely replacing one object with a safer-looking global one.

## Worked example

An image-disk-cache singleton needs `context.applicationContext` to find an app-private cache directory; it should never retain the Activity passed during construction. A theme-aware Dialog belongs to a currently valid Activity or DialogFragment. A repository that needs neither files nor Android services should receive a narrower dependency instead of any Context. This is an architectural example; exact Context requirements of a system service must be checked against its API documentation.

## Trade-offs and decision criteria

Application Context reduces accidental Activity retention in process-level objects, but it cannot substitute for a visual Context when theme, display, or window token matters. Passing an Activity to a screen-scoped presenter can be valid if the presenter ends with that screen. Injecting Context everywhere couples domain code to Android and makes JVM tests harder; prefer supplying a file path, clock, or interface if that is the actual need.

## Failure modes

A process singleton stores `Activity` in a field and leaks every rotated screen. A Dialog constructed from Application Context can fail to attach to the expected window or render with an unsuitable theme. Using Application resources for a window-specific layout can be wrong on a foldable or multi-window display. Conversely, caching an Activity-specific resource object indefinitely can leave stale locale/night-mode values. Inspect retention paths and verify configuration-sensitive UI after changes.

## Production perspective

In a multi-window app, create visual resources from the current Activity/window Context. Inject an Application Context only into components with matching process lifetime, such as an app-private file store. Keep ViewModel and repositories free of Activity and View references. Leak tests rotate and close screens; UI tests change locale, night mode, and window size to catch stale resource assumptions.

## Interview answer — short

Context is an application's handle to the Android system environment, mediating access to resources, system services, and component launching. Activity Context is scoped to a single screen's lifecycle, contains window and theme metadata, and is mandatory for rendering UI and dialogs. Conversely, Application Context is a process-level singleton, safe for persistent storage and background repositories, but incapable of anchoring visual windows.

## Interview answer — structured

To begin with, Context acts as the primary gateway between an Android application's code and the underlying operating system, providing unified access to resource resolution, sandboxed file storage, system services, and inter-component communication.

From an architectural standpoint, the choice between Activity Context and Application Context hinges entirely on lifecycle duration and visual capabilities. An Activity Context is tied directly to a single screen. Because it inherits from ContextThemeWrapper and maintains an active Window Token, it is strictly required whenever we inflate UI layouts, display dialogs, or resolve custom theme attributes. However, retaining an Activity Context beyond the screen's lifecycle creates a classic memory leak by pinning the entire Activity and view tree in heap memory.

As for boundary management, Application Context is a process-wide singleton whose lifetime mirrors the entire application process. It is completely safe to inject into long-lived components such as Room databases, HTTP clients, and background repositories.

In production scenarios, we establish clear architectural guardrails by injecting Application Context into our data layer singletons while passing Activity Context exclusively to short-lived UI components, preventing both memory leaks and runtime window crashes.

## Interview answer — deep senior

At the Android platform architecture level, both Activity and Application inherit from ContextWrapper, which delegates all operations to an internal ContextImpl instance. However, their internal wiring to Android system services differs fundamentally. An Activity holds a WindowManagerImpl instance that is configured with an active IBinder Window Token assigned by the WindowManagerService during window creation.

When an application invokes AlertDialog.Builder(context).show() with an Application Context, the system delegates to WindowManagerGlobal.addView(). Because Application Context has no Window Token registered with WindowManagerService, the IPC call fails validation in the system server, immediately terminating the application with a fatal BadTokenException. Furthermore, starting an Activity from Application Context fails unless Intent.FLAG_ACTIVITY_NEW_TASK is explicitly supplied, because an Application Context has no affinity with any task backstack in ActivityTaskManagerService.

From a configuration and theming perspective, modern Android versions introduce localized configuration overrides, per-app language settings, and dynamic Material You color palettes. An Activity Context resolves these attributes accurately through its local Configuration and ResourcesImpl hierarchy. In contrast, Application Context evaluates resources against global device defaults, meaning layout inflation using Application Context silently produces broken dark mode styling, incorrect font scaling, and mismatched dimension metrics.

In enterprise codebases, we enforce clean boundary hygiene using dependency injection qualifiers such as Hilt's ApplicationContext and ActivityContext. Furthermore, we decouple pure business logic and repositories from Android framework dependencies altogether by injecting narrow, domain-specific primitives like filesystem paths or custom state interfaces rather than broad Context references.

## How to answer in the interview

- **Why:** A Context carries capabilities and a lifetime that can affect leaks and UI behavior.
- **How:** Contrast the Activity’s window/theme with the Application’s process lifetime.
- **Trade-offs:** Inject a narrower dependency such as `cacheDir` when possible.
- **Failure cases:** Name singleton-held Activity references and a Dialog built with the wrong owner.
- **Production solution:** Pair an application-scoped disk cache with an Activity-owned dialog.

## Deep-dive talking points

Explain Context capabilities, lifecycle and visual configuration, Activity retention leaks, theme/window token needs, multi-window resource behavior, and when to replace a broad Context dependency with a narrow interface.

## Follow-up questions

- **Interviewer:** "Why does calling `startActivity()` with an Application Context require `FLAG_ACTIVITY_NEW_TASK`?"
  **Answer:** "Because an Application Context is not part of an existing Activity task stack. Without `FLAG_ACTIVITY_NEW_TASK`, Android doesn't know which task to place the new Activity in, throwing an `AndroidRuntimeException` on older API levels."

- **Interviewer:** "Can a BroadcastReceiver receive an Activity Context?"
  **Answer:** "No. The Context passed to `BroadcastReceiver.onReceive()` is a receiver-restricted context that cannot be used to bind services or register nested receivers."

- **Interviewer:** "How do you safely extract an Application Context from any given Context?"
  **Answer:** "By calling `context.applicationContext`. This extracts the root application singleton regardless of whether the incoming reference was an Activity, Service, or Wrapper."

## Self-check rubric

Define Context without calling it a global variable; compare lifetimes; choose a Context for a cache and a Dialog; explain one foldable/multi-window caveat; and identify an Activity leak path.

## References and reviewed-on date

- [Context API reference](https://developer.android.com/reference/android/content/Context) — capabilities and visual Context distinctions.
- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — recreation and lifetime.

Technically reviewed against primary documentation on 2026-10-13.
"""


AND_05_MD = """---
id: "AND-05"
question: "When must you use an Activity Context rather than Application Context?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 35
editorial_status: "reviewed"
---

# AND-05

## Original interview question

When must you use an Activity Context rather than Application Context?

## What the interviewer evaluates

- Tie the need for Activity Context to a current visual owner, window, theme, or Activity-scoped API.
- Avoid blanket claims that every UI-related API or `startActivity` categorically requires Activity Context.
- Handle Activity lifetime safely rather than storing the Context in process-scoped objects.

## Concept and technical explanation

An Activity Context is strictly mandatory whenever an operation directly interfaces with the operating system's window management, display configuration, or UI theming pipeline.

1. Mandatory Scenarios for Activity Context:
   - **Displaying Dialogs and Popups (`AlertDialog`, `BottomSheetDialog`, `PopupWindow`):**
     * Requires an active **IBinder Window Token** registered with Android's `WindowManagerService`. Passing an Application Context results in an immediate fatal crash: `WindowManager.BadTokenException`.
   - **Layout Inflation and Themed View Creation:**
     * `LayoutInflater` depends on an Activity Context to resolve theme styling, attributes (`?attr/colorPrimary`), styles declared in the manifest, and dynamic Material You palettes. Using an Application Context causes views to be inflated with raw system defaults, ignoring custom app themes.
   - **In-Task Activity Navigation:**
     * Transitioning between screens using an Activity Context preserves the natural backstack within the existing task. Using an Application Context requires `FLAG_ACTIVITY_NEW_TASK`, creating disjointed tasks.
   - **Multi-Window and Foldable Display Adaptations:**
     * An Activity Context reflects window-specific bounds, display density, and per-app language settings, whereas Application Context reflects global device settings.

2. The Architecture Rule:
   - Any operation that performs window attachment, pixel rendering, or theme attribute resolution strictly demands an Activity Context.

## Practical walkthrough (English)

Runtime contrast between valid and invalid Context usage:
```kotlin
// Will crash with BadTokenException:
fun showConfirmationBad(appContext: Context) {
    AlertDialog.Builder(appContext) // BadTokenException!
        .setTitle("Confirm")
        .show()
}

// Mandatory Activity Context for Dialogs:
fun showConfirmationGood(activityContext: Context) {
    AlertDialog.Builder(activityContext)
        .setTitle("Confirm")
        .show() // Succeeds because activityContext carries an active Window Token
}
```

## Explanation in Arabic

متى يجب عليك استخدام `Activity Context` تحديداً ولا يمكن استبداله بـ `Application Context` إطلاقاً؟

1. الحالات الإلزامية التي تتطلب Activity Context:
   - **عرض الـ Dialogs (AlertDialog, BottomSheetDialog, DatePickerDialog):**
     * تتطلب **Window Token** حقيقي مسجل في نظام تشغيل أندرويد. محاولة استخدام Application Context سترمي فوراً استثناء: `WindowManager.BadTokenException` وتغلق التطبيق بكراش حتمي!
   - **إنشاء وتضخيم الـ Views (Layout Inflation):**
     * الـ `LayoutInflater` يحتاج للـ Activity Context لقراءة الـ Theme والألوان والـ Styles المحددة في الـ `AndroidManifest` للـ Activity الحالية. استخدام Application Context سينتج عناصر بتصميم افتراضي قبيح أو غير متناسق.
   - **بدء Activity جديدة داخل نفس الـ Task:**
     * الانتقال الطبيعي بين الشاشات يتطلب Activity Context للحفاظ على الـ Backstack وتسلسل النوافذ بدون فرض `FLAG_ACTIVITY_NEW_TASK`.

2. القاعدة الذهبية:
   - أي شيء له علاقة بـ **الرسم على الشاشة، النوافذ، أو الـ Themes** يتطلب حتماً Activity Context.

## Practical walkthrough

أمثلة كود توضح متى يكون Activity Context إلزامياً:
```kotlin
// ❌ سيفشل بكراش فوري BadTokenException:
fun showConfirmationBad(appContext: Context) {
    AlertDialog.Builder(appContext) // BadTokenException!
        .setTitle("Confirm")
        .show()
}

// ✅ استخدام Activity Context الإلزامي للـ Dialogs:
fun showConfirmationGood(activityContext: Context) {
    AlertDialog.Builder(activityContext)
        .setTitle("Confirm")
        .show() // ينجح لأن activityContext يحمل Window Token شرعي
}
```

## Why it matters and how it works

An Activity is a Context associated with a window, display, configuration, and theme. Dialogs and other attached UI need an appropriate visual owner and token. Resource inflation for a visual container should use a Context reflecting that container, particularly on resizable devices. Activity Result APIs require registration with a lifecycle owner, not simply a random Context. A non-visual Application Context can access many app services and can launch an Activity only under its own documented task/flag rules; it is not a drop-in substitute for an active screen.

## Worked example

For a confirmation Dialog, use the current Activity or a lifecycle-aware `DialogFragment`, then dismiss it when that owner ends. For a global image cache, use Application Context to locate cache files and pass the loaded image data to the screen without retaining the Activity. For a system picker result, register the launcher with the Activity/Fragment lifecycle owner. These three needs have different owners even though all participate in one user flow.

## Trade-offs and decision criteria

Activity Context provides correct visual environment but risks a leak if held beyond the screen lifetime. Application Context is safe for process-lifetime, non-visual operations but can miss window-specific configuration. A `DialogFragment` manages a dialog with Fragment lifecycle, reducing manual cleanup, but does not erase the need to reason about state restoration. Prefer APIs that take a LifecycleOwner or Activity explicitly when they need one; do not cast arbitrary Context to Activity.

## Failure modes

Creating a Dialog with Application Context can fail to attach to the expected Activity window or use the wrong theme. A singleton that holds a Dialog's Activity leaks the old window after rotation. Conversely, forcing `context as Activity` in a library crashes when called from a Service. Check the API contract, validate the owner is active before showing UI, and cancel/dismiss the operation when the screen ends.

## Production perspective

A checkout confirmation belongs to the visible checkout Activity or its DialogFragment. The payment repository should receive a request model and authenticated client, not Activity Context. If a browser or payment SDK explicitly requires an Activity for a launch, pass the current Activity for that call only and let its result return through the lifecycle-aware launcher. Test rotation while the dialog is visible and a late SDK callback after the user exits.

## Interview answer — short

An Activity Context is strictly mandatory when displaying windowed UI such as AlertDialogs and BottomSheetDialogs, which require a valid Window Token to prevent BadTokenException. It is also required when inflating views via LayoutInflater to accurately resolve Activity theme attributes and dynamic styling, and when navigating between screens to preserve the natural task backstack without forcing FLAG_ACTIVITY_NEW_TASK.

## Interview answer — structured

To begin with, an Activity Context is strictly mandatory whenever an operation directly interfaces with the operating system's window management, display configuration, or UI theming pipeline.

From an architectural standpoint, the most prominent requirement is displaying dialogs and popups. Presenting an AlertDialog, BottomSheetDialog, or PopupWindow requires an active IBinder Window Token registered with the system WindowManagerService. Because only an active Activity window holds this token, passing an Application Context causes the system server to reject the window addition and throw an immediate BadTokenException.

As for boundary management, layout inflation and programmatic View instantiation strictly rely on an Activity Context to resolve theme styling. An Activity Context inherits from ContextThemeWrapper, allowing the LayoutInflater to resolve theme attributes, night mode overrides, and Material You dynamic colors. Using an Application Context causes views to be inflated against default platform themes, producing visual inconsistencies.

In production scenarios, we also depend on Activity Context for in-task navigation. Launching a new screen with an Activity Context places it smoothly on the existing task backstack, whereas using an Application Context forces the addition of FLAG_ACTIVITY_NEW_TASK, creating disjointed navigation stacks for the user.

## Interview answer — deep senior

At the Android operating system and WindowManagerService level, every visible window surface is secured by an IBinder window token generated by the system server during Activity launch. When an Activity enters the resumed state, ViewRootImpl attaches this token to the Activity's WindowManagerImpl. When a developer attempts to display a dialog, Dialog.show invokes WindowManager.addView, which performs an IPC transaction across Binder to WindowManagerService. The system server inspects the layout parameters and verifies whether the token corresponds to an existing, non-destroyed window session. Because an Application Context possesses a null window token, the system server immediately rejects the transaction and the local process crashes with WindowManager.BadTokenException.

Furthermore, in modern multi-window, picture-in-picture, and foldable display architectures, an Android device frequently runs multiple Activities with completely different Configuration objects. One window may be in dark mode with a narrow split-screen width, while another operates in light mode. An Activity Context carries a Display and Configuration tailored specifically to its partitioned window bounds. In contrast, Application Context evaluates resources against global device metrics. Inflating layouts with an Application Context on a foldable device yields incorrect dimension calculations, broken responsive breakpoints, and unstyled widgets.

In enterprise production architectures, we maintain strict lifecycle contracts. For user interactions like confirmation dialogs or payment bottom sheets, we host UI exclusively within DialogFragment instances bound to the screen's viewLifecycleOwner. If an external SDK requires an Activity reference to launch a web checkout or biometric prompt, we pass the current Activity as a transient method parameter or leverage the Activity Result API, strictly avoiding storing Activity references in long-lived services or singleton classes.

## How to answer in the interview

- **Why:** Window-attached UI needs the current screen owner and theme.
- **How:** Compare Dialog and application-scoped cache needs.
- **Trade-offs:** Keep Activity context for short screen work; pass only file/service dependencies to long-lived objects.
- **Failure cases:** Describe invalid window tokens and leaking an old Activity.
- **Production solution:** Use a lifecycle-owned dialog and an application-scoped image cache.

## Deep-dive talking points

Discuss window token, visual resource configuration, lifecycle registration, Service versus Activity callers, late callbacks, and why a Context cast is not an ownership design.

## Follow-up questions

- **Interviewer:** "Can you show a Toast using an Application Context?"
  **Answer:** "Yes! A Toast is rendered by the system's `NotificationManagerService` in a system-managed overlay window, so it works completely fine with an Application Context."

- **Interviewer:** "What is `ContextThemeWrapper` and how does it relate to this?"
  **Answer:** "`ContextThemeWrapper` is a class that allows wrapping an existing Context with a custom theme resource (e.g., `ContextThemeWrapper(baseContext, R.style.MyCustomTheme)`), which Activities inherit from by default."

- **Interviewer:** "Why does Jetpack Compose still need an Activity Context for dialogs?"
  **Answer:** "Even in Compose, the `Dialog()` composable creates an underlying Android `DialogWindowProvider` which requires an Activity Context to anchor the dialog window to the host Activity surface."

## Self-check rubric

Give two cases requiring a visual Activity owner, one valid Application Context use, a caveat about starting Activities, and a way to avoid retaining a screen through an SDK call.

## References and reviewed-on date

- [Context API reference](https://developer.android.com/reference/android/content/Context) — visual Context and resource configuration.
- [Activity Result APIs](https://developer.android.com/training/basics/intents/result) — lifecycle-bound result handling.

Technically reviewed against primary documentation on 2026-10-13.
"""


# ==============================================================================
# ARABIC METADATA DEFINITIONS
# ==============================================================================

AND_02_META = {
    "id": "AND-02",
    "questionAr": "اشرح دورة حياة الـ Activity والـ Fragment في أندرويد.",
    "topicAr": "أساسيات أندرويد ودورة الحياة والسياق (Context)",
    "evaluates_ar": "- التمييز بين دورة حياة الشاشة ودورة حياة واجهتها الرسومية، وفهم حدود ملكية الموارد بدلاً من مجرد سرد الـ callbacks.\n- ربط مراقبة البيانات وحقن الـ ViewBinding بدورة حياة الـ View (`viewLifecycleOwner`) لتفادي تسريب الذاكرة.\n- التعامل السليم مع إعادة بناء الشاشة (Configuration Changes) وموت العملية في الخلفية (Process Death) دون الاعتماد على `onDestroy` لحفظ البيانات.",
    "concept_ar": "",
    "walkthrough_ar": "",
    "why_it_matters_ar": "دورة الحياة بتحدد للنظام متى تكون الموارد مرئية أو قابلة للتفاعل. الـ Activity ممكن تكون في حالة Pause لكنها لا تزال مرئية جزئياً في وضع الشاشات المتعددة (Multi-window)، وبالتالي مينفعش نساوي بين onPause والاختفاء الكامل. دورة حياة الـ Fragment مقيدة بالـ Activity الحاضنة، بينما دورة حياة الـ View بتاعه بتبدأ وتنتهي بشكل مستقل تماماً. استخدام `repeatOnLifecycle(STARTED)` بيضمن تشغيل جمع تدفقات البيانات (Flows) فقط أثناء ظهور الشاشة، وإلغاء الكوروتين فور اختفائها، وده بيمنع استهلاك موارد المعالج في الخلفية وبيحمي التطبيق من تحديث واجهات مدمرة.",
    "worked_example_ar": "في شاشة تفاصيل الطلب، المراقبة لازم ترتبط بـ `viewLifecycleOwner`:\n```kotlin\nclass OrderFragment : Fragment(R.layout.order) {\n    private val viewModel: OrderViewModel by viewModels()\n\n    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n        super.onViewCreated(view, savedInstanceState)\n        viewLifecycleOwner.lifecycleScope.launch {\n            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n                viewModel.uiState.collect(::render)\n            }\n        }\n    }\n\n    private fun render(state: OrderUiState) { /* تحديث عناصر الواجهة الحالية فقط */ }\n}\n```\nوعند استخدام ViewBinding، يجب تصفير المتغير في `onDestroyView` لتجنب حبس الـ View القديم في الذاكرة.",
    "trade_offs_ar": "استخدام حدود Start/Stop هو الأنسب لمعظم تحديثات واجهة المستخدم، بينما الموارد الحصرية زي الكاميرا أو حساسات الحركة قد تتطلب التقييد بحدود Resume/Pause لتحرير العتاد بمجرد فقدان التركيز التفاعلي. الـ Repository بيحتفظ بتدفق البيانات مستقلاً عن الشاشة، بينما رندرة الواجهة لازم تتبع `viewLifecycleOwner`. مكتبات دورة الحياة الحديثة بتقلل الأخطاء اليدوية، لكنها مش بديل عن الحفظ الدائم للبيانات في قاعدة بيانات محلية قبل إغلاق الشاشة.",
    "failure_modes_ar": "تسجيل مستمع (Listener) في `onStart` وإلغاؤه في `onDestroy` بيؤدي لتكرار الاستدعاءات ومضاعفة الاستهلاك مع كل إخفاء وإظهار للشاشة. مراقبة الـ Flow باستخدام دورة حياة الـ Fragment بدلاً من الـ View بتسرب شجرة الـ Views بالكامل في الـ Backstack. الاعتماد على `onDestroy()` لحفظ البيانات في قاعدة البيانات بيعرض التطبيق لفقدان البيانات لو قرر النظام إنهاء العملية (Process Kill). الاختبار الحقيقي بيتطلب محاكاة التدوير، والانتقال للـ Backstack، ومحاكاة موت العملية من الـ adb.",
    "production_perspective_ar": "في تطبيقات الإنتاج الكبيرة، الـ Repository بيمتلك مصدر الحقيقة، والـ ViewModel بيحول البيانات لـ UiState غير قابلة للتعديل، والـ Fragment بيجمع البيانات فقط أثناء حالة STARTED. الكاميرا أو حساسات الباركود بتشتغل في الحالة التفاعلية وتقفل أول ما تخرج الشاشة من الواجهة. التغييرات المالية ومعاملات الشراء بتتحفظ في قاعدة بيانات محلية بمجرد اتخاذ الإجراء، مش في callbacks دورة الحياة المتأخرة، مع تتبع معدلات الـ ANRs وطول وقت تنفيذ دوال الـ Main Thread.",
    "how_to_answer_ar": "- **السبب الهندسي:** اربط ملكية الموارد بالفترة الزمنية اللي بتكون فيها الشاشة قادرة تستفيد منها فعلياً.\n- **طريقة الشرح:** ابدأ بشرح الحلقات الثلاث لدورة حياة الـ Activity (الوجود، الرؤية، التفاعل)، ثم وضح استقلالية `viewLifecycleOwner` في الـ Fragment.\n- **المفاضلات:** وضح ليه بنختار STARTED للبيانات العادية وRESUMED للموارد الحصرية زي الكاميرا.\n- **أنماط الفشل:** اشرح تسريب الـ Views عبر الـ Backstack وخطر الاعتماد على `onDestroy`.\n- **الحل العملي:** استشهد بكود `repeatOnLifecycle` ومسح الـ ViewBinding وتأمين البيانات في قاعدة بيانات محلية.",
    "talking_points_ar": "ناقش الفرق الجوهري بين الرؤية (Visibility) وبؤرة التركيز (Focus)، وفصل دورة حياة كائن الـ Fragment عن واجهته، وآلية عمل `repeatOnLifecycle` في إلغاء وإعادة تشغيل الكوروتينات، وسيمترية التسجيل والإلغاء (Start/Stop و Resume/Pause)، ولماذا لا يعتبر أي callback في دورة الحياة ضماناً كافياً لنجاة البيانات عند إنهاء العملية من قِبل الـ LMK.",
    "follow_ups_ar": "- **المحاور:** \"هل استدعاء `onDestroy()` مضمون دائماً لما المستخدم يخرج من التطبيق؟\"\n  **المرشح:** \"لأ، مش مضمون نهائياً. لو المستخدم داس Home والتطبيق دخل في الـ Background والنظام احتاج ذاكرة، الـ Low Memory Killer بيقتل الـ Process فوراً عبر SIGKILL من غير ما يستدعي `onDestroy()`. علشان كده أي بيانات هامة لازم تتحفظ فوراً في Room أو DataStore.\"\n\n- **المحاور:** \"ما الفرق في دورة الحياة بين الضغط على زر Back والضغط على زر Home؟\"\n  **المرشح:** \"الضغط على Back بيمثل رغبة صريحة في إنهاء الشاشة، فـ Activity بتمر بـ onPause ثم onStop ثم onDestroy وبتتشال من الـ Task. أما الضغط على Home فبينقل التطبيق للخلفية فبيمر بـ onPause ثم onStop فقط، وبيفضل كائن الشاشة محتفظاً بحالته في الـ Recent Apps.\"\n\n- **المحاور:** \"متى يتم استدعاء `onRestart()` تحديداً؟\"\n  **المرشح:** \"بيتم استدعاؤها لما الشاشة تكون وقفت بالكامل وراحت لـ onStop، وبعدين المستخدم يرجع يفتحها تاني، فـ onRestart بتتنفذ بين onStop و onStart قبل ما الشاشة ترجع تظهر للمستخدم.\"",
    "self_check_ar": "رتب حالات الـ Activity الأساسية؛ فرّق بين كائن الـ Fragment وواجهته الرسومية؛ حدد معيار الاختيار بين STARTED و RESUMED للموارد؛ اشرح سيمترية التنظيف؛ ووضح حدود نجاة البيانات عند موت العملية.",
    "references_ar": "- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — التنقل بين حالات الشاشة وسلوك العملية.\n- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — التمييز بين دورة حياة الـ Fragment ودورة حياة واجهته.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
    "quick_answer_ar": "دورة حياة الـ Activity بتدير ظهور الشاشة وتفاعلها مع المستخدم عبر مراحل أساسية: onCreate للتهيئة، و onStart مع onStop لحدود الرؤية، و onResume مع onPause لبؤرة التركيز والتفاعل، و onDestroy للهدم النهائي. وفي الـ Fragment بنمشي على نفس الترتيب، بس بيفصل بشكل جوهري بين دورة حياة كائن الـ Fragment نفسه ودورة حياة الـ View بتاعته عبر viewLifecycleOwner.",
    "best_answer_ar": "في أندرويد بنتعامل مع دورة الحياة كـ State Machine بتتحكم في الرؤية واستهلاك الذاكرة والتركيز التفاعلي.\n\nالـ Activity بتتحرك في تلات حلقات متداخلة: الحلقة الأولى هي دورة الحياة الكاملة بين onCreate و onDestroy، ودي اللي بنعمل فيها الـ Setup وحقن الـ ViewModel وتجهيز الشاشة.\n\nالحلقة التانية بتمثل حدود الرؤية بين onStart و onStop، وأول ما الشاشة تظهر للمستخدم بنجهز عرض البيانات، ولما تختفي ونروح لـ onStop بنوقف الـ Animations والـ Listeners الثقيلة لتوفير البطارية.\n\nالحلقة التالتة هي بؤرة التركيز والتفاعل التام بين onResume و onPause، وهنا بناخد الـ Touch Focus، ولو ظهر Dialog تابع للنظام بنروح لـ onPause لأن التركيز اتسحب مننا جزئياً.\n\nالمهم جداً كمهندسين إننا ناخد بالنا من الـ Fragment، لأن كائن الـ Fragment في الـ Backstack بيفضل عايش في الذاكرة حتى بعد ما الـ View بتاعه يتدمر بالكامل في onDestroyView. علشان كده في شغل الـ Production لازم نربط أي Flow collection أو ViewBinding بـ viewLifecycleOwner مع repeatOnLifecycle علشان نضمن إن مفيش أي تسريب للذاكرة أو استهلاك غير مبرر للـ CPU في الخلفية.",
    "deep_answer_ar": "على مستوى الـ Linux Kernel والـ Android OS Runtime، دورات الحياة دي هي المعيار الأساسي اللي بيعتمد عليه الـ Low Memory Killer daemon أو lmkd علشان يحدد الـ oom_adj score لكل عملية في النظام. لما الشاشة تكون في onResume، الـ ActivityManagerService بيدي العملية أولوية TOP_APP بقيمة oom_adj تساوي صفر، وده بيمنحها أعلى حماية ضد القتل. لكن بمجرد ما المستخدم يخرج والتطبيق يدخل onStop، أولوية العملية بتنزل لـ CACHED_APP، وساعتها نواة لينكس ممكن تبعت SIGKILL للعملية في أي لحظة تحت ضغط الذاكرة من غير ما تستدعي onDestroy نهائياً.\n\nمن ناحية الـ Threading، كل دوال دورة الحياة دي بتتبعت كرسائل للـ Looper بتاع الـ Main Thread عن طريق الـ ActivityThread والـ ClientTransactionHandler، وده معناه إن أي عملية حابسة (Blocking) جوه الـ callbacks دي هتعطل الـ Message Queue وتطلع للمستخدم خطأ ANR لو استمرت أكتر من خمس ثوانٍ.\n\nمعمارياً، إحنا مبنحطش كود الأعمال جوه الـ Callbacks دي؛ إحنا بنقسم إدارة الحالة لتلات مستويات منفصلة تماماً: الحالة المؤقتة للواجهة بتنجو من الـ Rotation عن طريق الـ ViewModelStore، وحالة التنقل بتتسجل في عملية النظام عبر SavedStateHandle أثناء onSaveInstanceState، والبيانات الحقيقية المستقرة بتتحفظ فوراً في قاعدة بيانات Room. وبفضل repeatOnLifecycle مع حالة STARTED، الكوروتينات بتلغي الـ Collectors تلقائياً في onStop وترجع تشغلها في onStart، وده بيوفر معالجة آمنة تماماً للموارد في حالات Multi-window والـ Foldables."
}

AND_03_META = {
    "id": "AND-03",
    "questionAr": "قارن بين دورة حياة كائن الـ Fragment ودورة حياة الـ View الخاصة به.",
    "topicAr": "أساسيات أندرويد ودورة الحياة والسياق (Context)",
    "evaluates_ar": "- فهم كيف يمكن لكائن الـ Fragment أن يعيش في الذاكرة لفترة أطول من شجرة الـ Views الخاصة به.\n- ربط الـ ViewBinding والـ Observers والكوروتينات بـ `viewLifecycleOwner` بدلاً من كائن الـ Fragment.\n- تشخيص تسريبات الـ ViewBinding وتكرار الـ Collectors بعد الرجوع من الـ Backstack.",
    "concept_ar": "",
    "walkthrough_ar": "",
    "why_it_matters_ar": "يقوم الـ FragmentManager بالاحتفاظ بكائن الـ Fragment في الذاكرة مع تدمير شجرة واجهته المعروضة عند وضعه في الـ Backstack لتوفير مساحة الرام. كائن `viewLifecycleOwner` بيكون متاح فقط بعد بناء الواجهة في `onViewCreated` وينتهي ويصل لحالة DESTROYED فور استدعاء `onDestroyView`. مراقبة البيانات المرتبطة بهذا الـ Owner بتضمن توقف التحديثات قبل انفصال الـ View عن الشاشة. الـ ViewModel المرتبط بنطاق الـ Fragment بيقدر يحتفظ بالحالة المنطقية عبر مرات إعادة بناء الواجهة، بينما مراجع الـ Views لازم يعاد ربطها في كل مرة.",
    "worked_example_ar": "النمط القياسي لتفادي تسريب الواجهة في الـ Fragment:\n```kotlin\nclass ScreenFragment : Fragment(R.layout.screen) {\n    private var _binding: ScreenBinding? = null\n    private val binding get() = _binding!!\n\n    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n        super.onViewCreated(view, savedInstanceState)\n        _binding = ScreenBinding.bind(view)\n        viewLifecycleOwner.lifecycleScope.launch {\n            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n                viewModel.uiState.collect { state ->\n                    binding.title.text = state.title\n                }\n            }\n        }\n    }\n\n    override fun onDestroyView() {\n        _binding = null\n        super.onDestroyView()\n    }\n}\n```\nتصفير المتغير `_binding` في `onDestroyView` يضمن تحرير شجرة الـ Views من الذاكرة أثناء بقاء الـ Fragment في الـ Backstack.",
    "trade_offs_ar": "جمع البيانات المرتبط بـ View-scope بيعيد تشغيل نفسه بمجرد ظهور واجهة جديدة، وده السلوك الطبيعي لعرض أحدث حالة. في المقابل، العمليات الحسابية أو المهام غير المرتبطة بالرسم ممكن ترتبط بنطاق الـ Fragment أو الـ ViewModel، لكن مينفعش بأي حال من الأحوال ربط كائن View أو Adapter طويل الأمد بهذا النطاق. استخدام StateFlow مناسب جداً لإعادة بث آخر حالة، بينما الأحداث الفردية (One-shot events) بتحتاج استراتيجية تسليم صريحة لتفادي تكرار تنفيذها عند إعادة بناء الواجهة.",
    "failure_modes_ar": "استخدام `fragment.lifecycleScope` لجمع البيانات داخل الواجهة بيخلي الـ Collector شغال حتى بعد `onDestroyView`، وده بيؤدي لتحديث واجهة منفصلة أو حدوث Crash فوري نتيجة محاولة الوصول لـ binding بقيمة null. عدم تصفير الـ ViewBinding بيحبس شجرة الواجهات والـ Drawables والـ Context في الذاكرة. تكرار التسجيل في `onViewCreated` بدون إلغاء يضاعف العمليات مع كل رجوع من الـ Backstack. يتم فحص المشكلة عبر أداة LeakCanary ومراقبة عداد الـ Collectors عند التنقل ذهاباً وإياباً.",
    "production_perspective_ar": "في شاشة تفاصيل المنتج، الـ ViewModel بيحتفظ بمعرف المنتج وحالة الشاشة، وكل View جديدة بتترسم بأحدث حالة عبر Collector مرتبط بـ `viewLifecycleOwner`. عند الانتقال لشاشة تانية وإضافة الشاشة للـ Backstack، بيتم تصفير الـ ViewBinding وإلغاء مستمعي الأحداث فوراً. اختبارات الوحدة والـ UI بتختبر انتقال الـ Fragment لدورة تدمير الواجهة وإعادة بنائها، مع التأكد من وجود Collector واحد نشط وعدم بقاء أي مرجع للـ Root View القديم في الذاكرة.",
    "how_to_answer_ar": "- **السبب الهندسي:** وضح أن كائن الـ Fragment مصمم ليعيش أطول من واجهته الرسومية في حالات الـ Backstack.\n- **طريقة الشرح:** قارن بين دورة حياة الكائن و `viewLifecycleOwner` وحدد نقطة الفصل عند `onDestroyView`.\n- **المفاضلات:** وضح مكان حفظ الحالة في الـ ViewModel ومكان ربط الواجهة عبر `viewLifecycleOwner`.\n- **أنماط الفشل:** اشرح مشكلة الـ Memory Leak وتكرار الـ Observers عند الرجوع للشاشة.\n- **الحل العملي:** استعرض كود ViewBinding مع المتغير الـ nullable وتصفيره في `onDestroyView` واستخدام `repeatOnLifecycle`.",
    "talking_points_ar": "ناقش توقيت إتاحة `viewLifecycleOwner` بين `onCreateView` و `onDestroyView`، وكيف يدير FragmentManager ذاكرة الشاشات في الـ Backstack، وتفاصيل تسريب الـ ViewBinding وتأثيره على Garbage Collection في الـ Heap، والفرق بين جمع StateFlow وبين معالجة الأحداث الفردية، ومتى يحل Jetpack Compose هذه المعضلة بالكامل.",
    "follow_ups_ar": "- **المحاور:** \"إيه اللي هيحصل لو عملت collect لـ Flow باستخدام `this.lifecycleScope` جوه `onViewCreated`؟\"\n  **المرشح:** \"في كل مرة المستخدم يروح شاشة تانية ويرجع للـ Fragment من الـ Backstack، دالة onViewCreated هتتنفذ من جديد وهتضيف Collector جديد شغال بالتوازي مع القديم. لو المستخدم راح ورجع 5 مرات، هيكون عندك 5 كوليكتورز بيحدثوا الـ UI في نفس الوقت وبيستهلكوا الموارد وممكن يعملوا كراش لو الـ ViewBinding بقى null.\"\n\n- **المحاور:** \"هل ممكن نتجنب تصفير الـ ViewBinding يدوياً في `onDestroyView`؟\"\n  **المرشح:** \"أيوة، نقدر نستخدم Custom Property Delegate زي AutoClearedValue، أو كلاس بيشترك في دورة حياة viewLifecycleOwner ويصفر الـ backing property تلقائياً أول ما يوصل لحدث onDestroyView، وده بيمنع خطأ النسيان اليدوي في الفرق الكبيرة.\"\n\n- **المحاور:** \"إزاي الانتقال لـ Jetpack Compose بيعالج المشكلة دي جذرياً؟\"\n  **المرشح:** \"في Jetpack Compose مفيش مفهوم شجرة الـ Views التقليدية ولا ViewBinding، وبالتالي مفيش خطر احتجاز مراجع الـ Views في الذاكرة. الـ Composable functions بتعتمد على State وإعادة التركيب (Recomposition)، وحالة الـ UI بتتخلص من الذاكرة بنظافة عند الخروج من الـ Composition.\"",
    "self_check_ar": "اشرح حالة يعيش فيها الـ Fragment أطول من واجهته؛ اختر الـ LifecycleOwner الصحيح لمراقبة الواجهة؛ حدد الدالة الصحيحة لتحرير الـ Binding؛ اشرح أعراض تسريب الذاكرة؛ وصمم اختباراً للتحقق من سلامة الرجوع من الـ Backstack.",
    "references_ar": "- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — الفروق بين حالات كائن الـ Fragment والواجهة.\n- [Lifecycle-aware coroutine collection](https://developer.android.com/topic/libraries/architecture/coroutines) — التجميع الآمن للكوروتينات.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
    "quick_answer_ar": "الفرق الجوهري إن كائن الـ Fragment بيعيش من لحظة إنشائه لحد onDestroy و onDetach، لكن الـ View بتاعته بتعيش فقط بين onCreateView و onDestroyView. لما بنحط الـ Fragment في الـ Backstack، النظام بيدمر شجرة الـ Views لتوفير الرام مع بقاء كائن الـ Fragment حياً في الذاكرة، وعلشان كده كل مراجع الـ ViewBinding والـ Flows لازم تتربط حصراً بـ viewLifecycleOwner لتفادي تسريب الذاكرة.",
    "best_answer_ar": "الفرق الحاسم بين الاتنين بيبان بوضوح أول ما نستخدم الـ Backstack في التطبيق.\n\nلما بننقل من Fragment A لـ Fragment B ونعمل addToBackStack، نظام أندرويد علشان يوفر الرام بيدمر الواجهة الرسومية للـ Fragment الأولاني وبيستدعي onDestroyView، لكن كائن الـ Fragment نفسه بيفضل عايش في الذاكرة ومحتفظ ببياناته والـ Arguments بتاعته.\n\nوده معناه هندسياً إن كائن الـ Fragment الواحد ممكن يرسم كذا View مختلفة على مدار فترة حياته. دورة حياة الكائن بتبدأ من أول الإنشاء لحد ما التطبيق يمسحه تماماً، أما دورة حياة الـ View فبتبدأ في onCreateView وبتموت في onDestroyView.\n\nالخطأ القاتل اللي بيوقع ناس كتير هو ربط مراقبة البيانات أو تخزين الـ ViewBinding في كائن الـ Fragment نفسه؛ لأنك لو مرجعتش صفرت الـ Binding في onDestroyView، كائن الـ Fragment هيفضل ممسك بالـ Views المدمرة ويسرب الـ Context بالكامل في الذاكرة.\n\nعلشان كده في الإنتاج بنربط دايماً جمع تدفقات الـ Flow بـ viewLifecycleOwner مع repeatOnLifecycle، وبنخلي متغير الـ ViewBinding يقبل الـ null وبنصفره صراحة أول ما الـ View تتدمر.",
    "deep_answer_ar": "تحت الكابوت في الـ AndroidX FragmentManager، لما بنعمل عملية استبدال مع addToBackStack، الـ Fragment Manager بينزل حالة الـ Fragment من RESUMED لـ CREATED فقط، فبيستدعي onDestroyView وينقل viewLifecycleOwner لحالة DESTROYED، لكن بيفضل الـ Fragment instance متخزن في سجل الـ Backstack بحالته.\n\nمن منظور إدارة الـ ART Garbage Collection والذاكرة، الاحتفاظ بمرجع الـ ViewBinding كمتغير عادي من غير ما تصفره في onDestroyView بيعمل كارثة تسريب ذاكرة حقيقية. مرجع الـ Binding بيفضل ماسك الـ Root View، والـ Root View ماسك كل الـ Child Views، وشجرة الـ Layout، والصور والـ Drawables، وكمان واصل لـ Activity Context عن طريق View.mContext. في تطبيق شغال في الـ Production وفيه صور بجودة عالية، احتجاز شاشتين تلاتة بالشكل ده في الـ Backstack ممكن يحجز أكتر من مية ميجابايت في الـ Java Heap والـ Native Memory، ويجيب OutOfMemoryError للمستخدم.\n\nأما من ناحية الـ Coroutines والتدفقات، فاستخدام lifecycleScope الخاص بالـ Fragment جوه onViewCreated بدل viewLifecycleOwner.lifecycleScope بيربط الـ Job بكائن الـ Fragment نفسه. فلو المستخدم راح ورجع بين الشاشات خمس مرات، هيكون عندك خمسة Collectors شغالين في نفس الوقت بيعملوا معالجة متكررة لنفس البيانات، وممكن يرموا NullPointerException أول ما يحاولوا يوصلوا لواجهة تم تدميرها بالفعل. علشان كده في الفرق الكبيرة بنعتمد على AutoClearedValue أو بننقل الشاشات بالكامل لـ Jetpack Compose اللي مفيهاش مراجع Views أصلاً."
}

AND_04_META = {
    "id": "AND-04",
    "questionAr": "ما هو الـ Context في أندرويد؟ وقارن بين Activity Context و Application Context.",
    "topicAr": "أساسيات أندرويد ودورة الحياة والسياق (Context)",
    "evaluates_ar": "- تعريف الـ Context كبوابة للوصول إلى موارد التطبيق، وخدمات النظام، وتشغيل المكونات.\n- مطابقة دورة حياة الـ Context والتكوين البصري مع المكون المستهلك له.\n- اكتشاف تسريب الـ Activity داخل كائنات الـ Singleton، ومحاولات عرض واجهات بنسخة Application Context غير بصرية.",
    "concept_ar": "",
    "walkthrough_ar": "",
    "why_it_matters_ar": "الـ Context هو المقبض التجريدي اللي بيتيح للتطبيق الوصول للموارد، وخدمات النظام، ومعلومات الحزم، وبدء المكونات البرمجية. التطبيقات المختلفة للـ Context بتحمل إعدادات وثيمات ونوافذ ودورات حياة متباينة تماماً. الـ Activity Context بيعكس البيئة البصرية الحالية للشاشة؛ بينما الـ Application Context بيعيش طوال عمر العملية، لكنه مش مهيأ لتمثيل واجهة المستخدم خصوصاً في وضع الشاشات المتعددة أو الهواتف القابلة للطي. الاختيار بينهم بيعتمد على القدرات والملكية الهندسية، مش مجرد استبدال كائن بآخر للهروب السطحي من أخطاء الـ Leaks.",
    "worked_example_ar": "في تطبيقات الإنتاج، بنحدد نوع الـ Context بناءً على طبيعة الاستخدام:\n```kotlin\n// 1. آمن للـ Singletons ومستودعات البيانات:\nclass ImageCacheManager(\n    @ApplicationContext private val context: Context\n) {\n    private val cacheDir = context.cacheDir\n}\n\n// 2. إلزامي لعرض الحوارات وقراءة الثيمات:\nfun showLogoutDialog(activityContext: Context) {\n    MaterialAlertDialogBuilder(activityContext)\n        .setTitle(\"تأكيد الخروج\")\n        .setMessage(\"هل تريد تسجيل الخروج؟\")\n        .setPositiveButton(\"نعم\") { _, _ -> /* تنفيذ */ }\n        .show()\n}\n```\nاستخدام Application Context مع الـ Dialog كان هيرمي فوراً خطأ `BadTokenException` بسبب غياب الـ Window Token.",
    "trade_offs_ar": "استخدام Application Context بيمنع تسريب الـ Activities داخل الكائنات التي تعيش طوال عمر العملية، لكنه لا يمكن أن يحل محل الـ Visual Context لما يكون الثيم أو الـ Window Token مطلوباً. تمرير Activity Context لـ Presenter مرتبط بدورة حياة الشاشة مقبول طالما بينتهي معاها. حقن الـ Context في كل مكان بيعمل اقتران غير ضروري بين كود النطاق (Domain) ونظام أندرويد وبيصعب اختبارات الـ JVM؛ الأفضل تمرير مسار ملف أو واجهة برمجية محددة بدلاً من كائن Context كامل.",
    "failure_modes_ar": "تخزين الـ Activity كمتغير داخل كائن Singleton بيسرب كل شاشة تم تدويرها في الذاكرة. إنشاء Dialog باستخدام Application Context بيفشل في الارتباط بنافذة الـ Activity ويرمي `BadTokenException`. استخدام موارد الـ Application لتضخيم واجهة معينة بيؤدي لتجاهل الثيم والوضع الليلي في الشاشات القابلة للطي. والاحتفاظ بكائن موارد خاص بـ Activity لفترة غير محددة بيترك قيماً قديمة للغة وثيم الشاشة. يتم الفحص عبر مراجعة مسارات المراجع واختبارات تغيير الإعدادات.",
    "production_perspective_ar": "في التطبيقات الكبيرة متعددة النوافذ، بننشئ الموارد البصرية حصراً من الـ Activity Context للشاشة الحالية. بنحقن الـ Application Context فقط في المكونات ذات العمر المطابق للعملية، زي مستودعات التخزين المحلي وقواعد البيانات. بنحافظ على الـ ViewModel والـ Repositories خالية تماماً من أي مراجع للـ Activity أو الـ View. اختبارات الـ LeakCanary بتتحقق من إغلاق الشاشات وتدويرها، واختبارات الـ UI بتغير الوضع الليلي وحجم الشاشة لكشف أي افتراضات غير دقيقة.",
    "how_to_answer_ar": "- **السبب الهندسي:** وضح أن الـ Context يحمل قدرات وظيفية ودورة حياة تحدد إمكانية استخدامه في الواجهة أو التخزين.\n- **طريقة الشرح:** ابدأ بتعريف الـ Context كبوابة للنظام، ثم قارن بين Activity Context المرتبط بالنافذة والثيم، و Application Context المرتبط بالعملية ككل.\n- **المفاضلات:** بين متى يفضل حقن مسار محدد بدلاً من كائن Context كامل في طبقة الـ Domain.\n- **أنماط الفشل:** استشهد بـ `BadTokenException` وتسريب الذاكرة عند الاحتفاظ بالـ Activity في Singleton.\n- **الحل العملي:** وضح استخدام Hilt Qualifiers لفصل `@ApplicationContext` عن `@ActivityContext`.",
    "talking_points_ar": "ناقش معمارية ContextWrapper و ContextImpl في الكود المصدري لنظام أندرويد، ودور الـ Window Token المسجل لدى WindowManagerService، ومشاكل قراءة موارد الثيم والوضع الليلي عند استخدام Application Context، وسبب فرض `FLAG_ACTIVITY_NEW_TASK` عند تشغيل شاشة من سياق التطبيق العام، وكيفية تجريد طبقة الـ Domain تماماً من أي تبعية للـ Context.",
    "follow_ups_ar": "- **المحاور:** \"ليه استدعاء `startActivity()` باستخدام Application Context بيتطلب إضافة `FLAG_ACTIVITY_NEW_TASK`؟\"\n  **المرشح:** \"لأن Application Context مش جزء من Task Stack خاص بشاشة معينة. من غير الراية دي، أندرويد مبيكونش عارف يفتح الـ Activity الجديدة في أي Task، فبيرمي خطأ AndroidRuntimeException في الإصدارات القديمة أو يفرض إنشاء مهمة منفصلة.\"\n\n- **المحاور:** \"هل الـ BroadcastReceiver بيستلم Activity Context في دالة onReceive؟\"\n  **المرشح:** \"لأ، الـ Context اللي بيوصل لـ onReceive هو ReceiverRestrictedContext، وده سياق محدود جداً وممنوع استخدامه لربط Services أو تسجيل Receivers تانية.\"\n\n- **المحاور:** \"إزاي تستخرج الـ Application Context بأمان من أي كائن Context يجيلك؟\"\n  **المرشح:** \"عن طريق استدعاء `context.applicationContext`. وده بيستخرج كائن التطبيق الجذري الآمن بغض النظر عن كون المرجع الأصلي Activity أو Service أو ContextWrapper.\"",
    "self_check_ar": "عرّف الـ Context بدون وصفه كمتغير عام؛ قارن بين فترات الحياة؛ حدد السياق المناسب للكاش والحوارات؛ وضح قيود الشاشات القابلة للطي؛ وحدد مسار تسريب الـ Activity.",
    "references_ar": "- [Context API reference](https://developer.android.com/reference/android/content/Context) — قدرات الـ Context والفروق البصرية.\n- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — دورة حياة المكونات وإعادة البناء.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
    "quick_answer_ar": "الـ Context هو بوابة التطبيق للتعامل مع نظام أندرويد والوصول للموارد وخدمات النظام وتشغيل الشاشات. الـ Activity Context مرتبط بدورة حياة شاشة معينة، وبيحمل الثيم والـ Window Token، وده بيخليه إلزامي لرسم الواجهات والـ Dialogs. أما الـ Application Context فمرتبط بالعملية ككل، وآمن تماماً للتخزين في كائنات الـ Singleton وقواعد البيانات، بس مينفعش يعرض نوافذ على الشاشة.",
    "best_answer_ar": "الـ Context هو المقبض الأساسي اللي بيربط كود تطبيقنا بنظام التشغيل، وهو المسؤول عن الوصول للموارد زي النصوص والألوان، وخدمات النظام زي الـ LayoutInflater ومستشعرات الجهاز، وبدء الشاشات والعمليات.\n\nالفارق الجوهري بين Activity Context و Application Context بيعتمد على حاجتين: دورة الحياة والقدرات البصرية.\n\nالـ Activity Context مرتبط بدورة حياة شاشة معينة، وبيرث من ContextThemeWrapper، وده معناه إنه مجهز بثيم الشاشة وبيحمل Window Token شرعي من النظام. وجود التوكن ده بيخليه إلزامي لعرض أي Dialog، أو تضخيم Views، أو التنقل الطبيعي جوه الـ Backstack. لكن خطورته الكبيرة بتظهر لو احتفظت بيه جوه Singleton أو Background thread، لأنك كده بتسرب الشاشة بالكامل في الذاكرة.\n\nأما الـ Application Context فهو Singleton مرتبط بعمر الـ Linux Process ككل، وعايش من لحظة تشغيل التطبيق لحد ما النظام ينهيه. وده بيخليه آمن تماماً للحقن في طبقة البيانات، زي قواعد بيانات Room ومستودعات الشبكة والـ Repositories، لكنه ميعرفش يرسم نوافذ ومفيهوش ثيم الشاشة.\n\nالقاعدة الهندسية عندنا: بنحقن Application Context في طبقة الـ Data، وبنستخدم Activity Context حصراً في طبقة الـ UI.",
    "deep_answer_ar": "على مستوى الـ Framework Architecture، الـ Activity والـ Application الاتنين بيرثوا من ContextWrapper اللي بيفوض العمليات لكائن داخلي هو ContextImpl. لكن الفرق الجوهري في الربط بنظام إدارة النوافذ؛ الـ Activity بتحتوي على WindowManagerImpl مربوط بـ IBinder Window Token بيمنحه الـ WindowManagerService للشاشة أول ما تفتح.\n\nلو حاولت تعمل AlertDialog باستخدام Application Context، الـ WindowManagerGlobal هيحاول يضيف النافذة، ونظام الـ System Server هيكتشف إن التوكن فارغ، فهيرمي فوراً BadTokenException ويقفل التطبيق. ونفس الشيء بيحصل لما تشغل Activity من Application Context؛ النظام بيجبرك تضيف FLAG_ACTIVITY_NEW_TASK لأن سياق التطبيق العام ملوش Task Stack مسجل في ActivityTaskManagerService.\n\nكمان من ناحية الثيم والـ Material You في أندرويد الحديث، الـ Activity Context بيحمل Configuration و ResourcesImpl محليين بيعكسوا الوضع الليلي وحجم الخطوط الخاص بالشاشة بدقة، بينما الـ Application Context بيقيس الموارد على مستوى النظام ككل، واستخدامه في تضخيم الواجهات بيطلع عناصر بتصميم مشوه أو بألوان باهتة متجاهلة ثيم التطبيق.\n\nمعمارياً، بنفصل بينهم تماماً باستخدام الـ Dependency Injection عن طريق Hilt Qualifiers زي ApplicationContext للـ Repositories و ActivityContext للـ Adapters، ومع الكود النظيف بنفضل إن طبقة الـ Domain متشوفش كائن الـ Context أصلاً وتعتمد على Interfaces مجردة لتسهيل اختبارات الـ Unit Tests على الـ JVM."
}

AND_05_META = {
    "id": "AND-05",
    "questionAr": "متى يكون استخدام Activity Context إلزامياً ولا يمكن استبداله بـ Application Context؟",
    "topicAr": "أساسيات أندرويد ودورة الحياة والسياق (Context)",
    "evaluates_ar": "- ربط الحاجة لـ Activity Context بوجود مالك بصري نشط، أو نافذة، أو ثيم، أو واجهة تعتمد على دورة حياة الشاشة.\n- تجنب التعميم الخاطئ بأن كل عمليات الواجهة أو تشغيل الشاشات تتطلب حصراً Activity Context.\n- التعامل الآمن مع دورة حياة الـ Activity بدلاً من تخزين الـ Context في كائنات تعيش على مستوى العملية.",
    "concept_ar": "",
    "walkthrough_ar": "",
    "why_it_matters_ar": "الـ Activity هي Context مرتبط بنافذة وشاشة وعرض وإعدادات وثيم محدد. الـ Dialogs وعناصر الواجهة المرتبطة بالشاشة بتحتاج مالكاً بصرياً وتوكن نافذة شرعي مسجل في النظام. تضخيم الموارد للواجهة لازم يستخدم Context بيعكس تكوين الحاوية الرسومية الحالية، خاصة على الأجهزة القابلة للطي وتعدد النوافذ. واجهات الـ Activity Result بتتطلب التسجيل مع LifecycleOwner محدد، مش مجرد أي سياق عشوائي. بينما الـ Application Context غير البصري بيقدر يوصل للخدمات ويبدأ شاشات تحت قواعد رايات محددة، لكنه مش بديل مناسب لشاشة تفاعلية نشطة.",
    "worked_example_ar": "كود عملي يوضح الفارق بين الاستخدامين:\n```kotlin\n// ❌ سيفشل فوراً بكراش BadTokenException:\nfun showConfirmationBad(appContext: Context) {\n    AlertDialog.Builder(appContext)\n        .setTitle(\"تأكيد العملية\")\n        .setMessage(\"هل أنت متأكد؟\")\n        .show() // كراش لأن appContext لا يحمل Window Token\n}\n\n// ✅ استخدام Activity Context الإلزامي للـ Dialogs:\nfun showConfirmationGood(activityContext: Context) {\n    AlertDialog.Builder(activityContext)\n        .setTitle(\"تأكيد العملية\")\n        .setMessage(\"هل أنت متأكد؟\")\n        .show() // ينجح لأن activityContext يحمل Window Token شرعي\n}\n```\nفي المقابل، تخزين الملفات المؤقتة في الـ Cache بيتم عبر `applicationContext` بأمان تام.",
    "trade_offs_ar": "استخدام Activity Context بيوفر بيئة بصرية وثيمات صحيحة لكنه بيحمل مخاطرة تسريب الذاكرة لو تم الاحتفاظ بيه بعد انتهاء الشاشة. الـ Application Context آمن للمهام الخلفية المستمرة لكنه يفتقد معلومات النافذة والثيم. استخدام `DialogFragment` بيدير الـ Dialog وفق دورة حياة الـ Fragment ويقلل مشاكل التنظيف اليدوي، لكنه مش بيلغي ضرورة التعامل مع استعادة الحالة (State Restoration). الأفضل دائماً اعتماد الدوال اللي بتطلب صراحة Activity أو LifecycleOwner وتجنب عمل Casting عشوائي لـ Context إلى Activity.",
    "failure_modes_ar": "إنشاء Dialog باستخدام Application Context بيؤدي لـ `WindowManager.BadTokenException` وانهيار التطبيق فوراً. احتفاظ Singleton بمرجع Activity لفتح Dialog بيسرب نافذة الشاشة القديمة بعد التدوير. في المقابل، إجبار الكود على عمل `context as Activity` في مكتبة عامة بيعمل كراش لو تم استدعاؤها من Service أو Application. يتم فحص العقد البرمجي والتأكد من أن المالك البصري نشط قبل إظهار الواجهة وإلغاء أو إغلاق الحوارات عند انتهاء الشاشة.",
    "production_perspective_ar": "حوار تأكيد الدفع لازم يتبع الـ Activity النشطة أو DialogFragment الخاص بها. مستودع المدفوعات (Payment Repository) لازم يستلم نموذج الطلب والـ Client الموثق، مش كائن Activity Context. لو مكتبة خارجية للدفع أو متصفح ويب طلبت Activity لتشغيل واجهتها، بنمرر الـ Activity الحالية كـ Parameter للدالة فقط، ونستقبل النتيجة عبر Activity Result API المرتبط بدورة الحياة. بنختبر تدوير الشاشة أثناء ظهور الـ Dialog، ومعالجة استجابات الـ SDK المتأخرة بعد خروج المستخدم.",
    "how_to_answer_ar": "- **السبب الهندسي:** وضح أن النوافذ المرئية تتطلب مالكاً بصرياً حقيقياً وتوكن نافذة مسجل في نظام التشغيل.\n- **طريقة الشرح:** قارن بين احتياج الـ Dialog لتوكن النافذة واحتياج الكاش لسياق التطبيق العام.\n- **المفاضلات:** احتفظ بـ Activity Context للمهام اللحظية، ومرر فقط مسارات الملفات والتبعيات المحددة للكائنات طويلة الأمد.\n- **أنماط الفشل:** اشرح حدوث `BadTokenException` ومخاطر تسريب الشاشات القديمة عند تدوير الجهاز.\n- **الحل العملي:** استعرض استخدام DialogFragment وتمرير الـ Activity كمعامل لحظي للـ SDKs بدلاً من تخزينها.",
    "talking_points_ar": "ناقش آلية عمل الـ Window Token في نظام WindowManagerService، وتأثير وضع النوافذ المتعددة والأجهزة القابلة للطي على قراءة الموارد، وتسجيل نتائج الـ Activity Result API، والفروق الدقيقة بين طلبات الخدمة والشاشة، ولماذا لا يعد الـ Casting حلاً معمارياً مناسباً لإدارة السياق.",
    "follow_ups_ar": "- **المحاور:** \"هل نقدر نعرض Toast باستخدام Application Context من غير مشاكل؟\"\n  **المرشح:** \"أيوة، الـ Toast بيتعرض من خلال NotificationManagerService في نافذة نظام مستقلة تماماً، وبالتالي مش بيحتاج Window Token خاص بالشاشة وشغال تماماً مع Application Context.\"\n\n- **المحاور:** \"إيه هو الـ ContextThemeWrapper وإيه علاقته بالموضوع ده؟\"\n  **المرشح:** \"الـ ContextThemeWrapper هو كلاس بيغلف أي Context موجود ويطبق عليه Theme محدد برمجياً، والـ Activity في الأساس بترث منه، وده اللي بيمكنها من قراءة ألوان وثيمات التطبيق بدقة.\"\n\n- **المحاور:** \"ليه Jetpack Compose لسه بيحتاج Activity Context في الـ Dialogs رغم إنه مش بيعتمد على الـ Views التقليدية؟\"\n  **المرشح:** \"لأن دالة Dialog في Compose بتنشئ تحت الكابوت نافذة حقيقية عبر DialogWindowProvider، والنافذة دي بتحتاج ترتبط بـ Window Token الخاص بالـ Activity الحاضنة لعرض السطح الرسومي فوق الشاشة.\"",
    "self_check_ar": "اذكر حالتين تتطلبان مالكاً بصرياً؛ حالة استخدام صحيحة للـ Application Context؛ ملاحظة هامة حول تشغيل الـ Activities؛ وطريقة لتجنب احتجاز الشاشة عبر استدعاءات الـ SDKs.",
    "references_ar": "- [Context API reference](https://developer.android.com/reference/android/content/Context) — السياق البصري وإعدادات الموارد.\n- [Activity Result APIs](https://developer.android.com/training/basics/intents/result) — إدارة النتائج المرتبطة بدورة الحياة.\n\nتمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.",
    "quick_answer_ar": "استخدام Activity Context إلزامي عند عرض الـ Dialogs والـ Popups علشان محتاجة Window Token حقيقي من النظام لمنع خطأ BadTokenException. وإلزامي كمان عند تضخيم الواجهات بالـ LayoutInflater لقراءة ثيم وألوان الشاشة بدقة، وعند التنقل بين الشاشات للحفاظ على الـ Backstack الطبيعي من غير ما نضطر نستخدم FLAG_ACTIVITY_NEW_TASK.",
    "best_answer_ar": "استخدام Activity Context بيكون إلزامي في أي عملية بتتعامل مباشرة مع نظام إدارة النوافذ، أو بتعتمد على رسم الواجهات، أو محتاجة ثيم محدد للشاشة.\n\nالحالة الأولى والأشهر هي عرض الـ Dialogs زي AlertDialog و BottomSheetDialog؛ لأنها بتتطلب Window Token حقيقي مسجل في نظام WindowManagerService ومربوط بنافذة الشاشة الحالية. لو حاولت تستخدم Application Context، النظام هيرفض إضافة النافذة ويرمي فوراً BadTokenException ويقفل التطبيق.\n\nالحالة التانية هي تضخيم الواجهات بالـ LayoutInflater أو إنشاء Views برمجياً؛ لأن الـ Activity Context وارث من ContextThemeWrapper، وده بيمكنه من قراءة ألوان وثيمات الشاشة والوضع الليلي بدقة، بينما سياق التطبيق العام بيعتمد على ثيمات النظام الافتراضية وهيطلع واجهات مشوهة.\n\nالحالة التالتة هي التنقل الطبيعي بين الشاشات؛ فتح شاشة جديدة بـ Activity Context بيحافظ على تسلسل الـ Backstack داخل نفس المهمة، في حين إن استخدام سياق التطبيق بيجبرك تستخدم FLAG_ACTIVITY_NEW_TASK وده بيفصل المهام عن بعضها.\n\nالقاعدة عندنا واضحة: كل ما هو رسم ونوافذ وثيم بيحتاج Activity Context، وكل ما هو كاش ومستودعات بيانات بيحتاج Application Context.",
    "deep_answer_ar": "على مستوى الـ WindowManagerService في نظام أندرويد، كل نافذة بتترسم على الشاشة بيكون ليها IBinder Window Token فريد بيولده الـ System Server أول ما الـ Activity تفتح وتوصل لحالة onResume. لما المطور يستدعي Dialog.show، الكود بيطلب من الـ WindowManager إضافة السطح الرسومي، فـ WMS بيفحص التوكن للتأكد من إنه تابع لنافذة نشطة وغير مدمرة. وبما إن Application Context ملوش أي توكن مسجل في الـ Window Manager، عملية التحقق بتفشل فوراً والنظام بيرمي BadTokenException.\n\nبالإضافة لكده، في أجهزة الشاشات القابلة للطي ووضع تقسيم الشاشة (Multi-window)، بيكون عندك شاشتين شغالين في نفس الوقت وكل شاشة ليها Configuration خاص بيها؛ شاشة في الوضع الليلي وشاشة تانية في الوضع النهاري، أو شاشة عريضة والتانية مضغوطة. الـ Activity Context بيحمل مقاييس الـ Window المنفصلة دي، بينما الـ Application Context بيقيس الموارد على مستوى الجهاز ككل، واستخدامه في رسم الواجهات على الأجهزة دي بيطلع مقاسات مشوهة واستجابة مكسورة تماماً.\n\nفي معمارية التطبيقات الكبيرة، بنتعامل مع الحدود دي بانضباط صارم: حوارات التأكيد وبوابات الدفع بتتحط حصراً جوه DialogFragment مرتبط بـ viewLifecycleOwner علشان نضمن قفله تلقائياً مع انتهاء الشاشة. ولو عندنا SDK خارجي للدفع أو البصمة بيطلب Activity، بنمررله الـ Activity الحالية كـ Parameter وقت الاستدعاء فقط أو بنستخدم Activity Result API، وبنمنع تماماً تخزين أي مرجع للشاشة جوه Services أو كائنات Singleton ممتدة."
}


def main():
    # 1. Update Markdown files
    (QUESTIONS_DIR / "AND-02.md").write_text(AND_02_MD, encoding="utf-8")
    print("Updated AND-02.md")

    (QUESTIONS_DIR / "AND-03.md").write_text(AND_03_MD, encoding="utf-8")
    print("Updated AND-03.md")

    (QUESTIONS_DIR / "AND-04.md").write_text(AND_04_MD, encoding="utf-8")
    print("Updated AND-04.md")

    (QUESTIONS_DIR / "AND-05.md").write_text(AND_05_MD, encoding="utf-8")
    print("Updated AND-05.md")

    # 2. Update JSON metadata
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    metadata["AND-02"] = AND_02_META
    metadata["AND-03"] = AND_03_META
    metadata["AND-04"] = AND_04_META
    metadata["AND-05"] = AND_05_META

    METADATA_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Updated arabic_lab_metadata.json for AND-02, AND-03, AND-04, AND-05.")


if __name__ == "__main__":
    main()
