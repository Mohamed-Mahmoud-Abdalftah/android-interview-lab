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

الـFragment نفسه له lifecycle من `onAttach` لحد ما يتشال نهائيًا. الـview اللي أنشأها في `onCreateView` عمرها أقصر: ممكن `onDestroyView` يحصل والـFragment لسه محفوظ في back stack، وبعدها يتعمل view جديدة. لو خزّنت ViewBinding أو observer على lifecycle الـFragment، ممكن تفضل ماسك view قديمة وتعمل leak أو تحدث UI مش موجودة. اربط أي حاجة تمس الـview بـ`viewLifecycleOwner`، وصفّر binding في `onDestroyView`. أما state المهمة خليها في ViewModel أو repository حسب عمرها، مش في widgets نفسها.

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

“A Fragment object can survive after its view is destroyed, especially on the back stack. The view has its own shorter lifecycle. I collect and observe UI state with viewLifecycleOwner and clear bindings in onDestroyView, while logical state lives in a ViewModel or repository.”

## Interview answer — structured

“The Fragment lifecycle tracks the component in FragmentManager; the view lifecycle starts with a created view and ends around onDestroyView. Back-stack navigation can destroy the view without destroying the Fragment. Therefore, a Fragment-level observer that holds ViewBinding can leak the old hierarchy or render into a detached view. I use viewLifecycleOwner for view updates, repeatOnLifecycle for visible collection, and release binding and listeners when the view ends. The operational symptom is often a leak or duplicate observation after navigating away and back. `fragment.lifecycleScope` can outlive the current view, while `viewLifecycleOwner.lifecycleScope` is canceled with that view. I clear binding references and test repeated view creation rather than only a single launch.”
## Interview answer — deep senior

“I separate logical screen ownership from rendering ownership. FragmentManager may retain the Fragment instance while replacing its view tree, so a Fragment-scoped ViewModel can continue holding state but any view reference must have the shorter view lifetime. I acquire binding per onViewCreated, launch collectors through viewLifecycleOwner, and clear binding and listeners at onDestroyView. For a hot state stream, a new view receives the latest snapshot; for one-time navigation effects I define replay/acknowledgement instead of assuming collection timing. I test back-stack transitions and configuration recreation and inspect heap retention to catch old view trees. I trace the two lifetimes explicitly: Fragment instance lifecycle may continue on the back stack, but the rendered hierarchy ends at `onDestroyView`. A collector that captures binding and is launched in Fragment scope can keep a detached view reachable or crash on a null binding. I start collection with the view owner, repeat at STARTED when appropriate, and remove listeners/adapters tied to the old view. A Fragment-scoped ViewModel holds screen state but never a View reference. I verify by navigating back and forth many times, counting collectors and inspecting heap roots. This is a UI resource problem, not a reason to persist every render value.”
## Deep-dive talking points

Explain view owner availability, back-stack view destruction, ViewBinding cleanup, lifecycle-aware StateFlow collection, adapter/listener retention, and why one-shot effects differ from current state.

## Follow-up questions

- [AND-02](../and-02/): Can a Fragment be alive without its view? **Answer:** yes; FragmentManager may retain it on the back stack after onDestroyView.
- [MEM-11](../mem-11/): Why release ViewBinding? **Answer:** it otherwise retains the old view tree longer than its lifecycle.
- [FLO-20](../flo-20/): Does a restarted collector always receive every event? **Answer:** no; delivery depends on the stream's replay/buffer contract.

## Self-check rubric

Describe one case where Fragment outlives its view; choose the right LifecycleOwner for UI collection; release binding at the correct callback; explain a leak symptom; and design a back-stack recreation test.

## References and reviewed-on date

- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — Fragment and view owner transitions.
- [Lifecycle-aware coroutine collection](https://developer.android.com/topic/libraries/architecture/coroutines) — restartable collection guidance.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The snippet requires generated binding and app ViewModel declarations and was not Android-compiled here.
