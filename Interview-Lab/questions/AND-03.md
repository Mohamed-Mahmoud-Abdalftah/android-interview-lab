---
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

A Fragment's instance lifecycle spans from creation to onDestroy(), while its view lifecycle spans only between onCreateView() and onDestroyView(). When placed on the backstack, the view hierarchy is destroyed while the Fragment instance remains alive, requiring observers and view bindings to bind to viewLifecycleOwner to prevent memory leaks.

## Interview answer — structured

The critical distinction is that a Fragment's object instance outlives its UI view hierarchy when using the backstack.

When Fragment A is replaced by Fragment B and added to the backstack (`addToBackStack()`):

1. Android destroys Fragment A's UI layout, calling `onDestroyView()`. However, the `Fragment` class instance remains alive in memory so that its scroll position and arguments are preserved.
2. When the user taps Back, the existing Fragment A instance creates a brand-new View hierarchy, calling `onCreateView()` and `onViewCreated()`.

Because of this asymmetry, observing LiveData or collecting Flows against the Fragment's own lifecycle (`this`) creates memory leaks and duplicate observers every time the user returns from the backstack.

In modern Android development, all View-related operations, ViewBindings, and Flow collections must strictly bind to **`viewLifecycleOwner`**, and ViewBindings must be nulled out in `onDestroyView()`.

## Interview answer — deep senior

Under the hood, `Fragment.getViewLifecycleOwner()` returns a dedicated `LifecycleOwner` that is created in `onCreateView()` and set to the `DESTROYED` state in `onDestroyView()`. If you attempt to call `viewLifecycleOwner` before `onCreateView()` or after `onDestroyView()`, it throws an `IllegalStateException: Can't access the Fragment View's LifecycleOwner when getView() is null`.

In memory profiling, failing to null out `_binding` in `onDestroyView()` is one of the most common causes of Out-Of-Memory (OOM) errors in large applications. A single ViewBinding reference holds pointers to the root View, all child Views, the WindowManager, and bitmap drawables, preventing the entire screen's graphic memory from being reclaimed by ART garbage collection while the fragment rests in the backstack.

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
