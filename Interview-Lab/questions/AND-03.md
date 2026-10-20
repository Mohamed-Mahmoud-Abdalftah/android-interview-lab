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

## Concept and technical explanation

A Fragment has its own lifecycle, and a non-null Fragment view gets a separate `viewLifecycleOwner` lifecycle. The Fragment may remain managed while its current view is destroyed, as can happen with a back-stack transaction. A later view is a new tree with a new view lifecycle owner. ViewBinding, adapters, listeners and UI collectors therefore belong to that view lifetime. Clear a Fragment field holding the binding in `onDestroyView`; collect UI `Flow` with `viewLifecycleOwner.lifecycleScope` and `repeatOnLifecycle(STARTED)`. A Fragment-scoped ViewModel may retain logical screen state while the view is recreated. A binding leak is possible when a retained Fragment holds an old root view, but no fixed percentage, memory size or duplicate-collector count follows from this pattern. A `ComposeView` hosted in a Fragment is still an Android View and needs composition disposal tied to the view lifecycle.

## Practical walkthrough (English)

Use the view owner for rendering, and release the binding when that view is destroyed:
```kotlin
class ProfileFragment : Fragment(R.layout.fragment_profile) {
    private var _binding: FragmentProfileBinding? = null
    private val binding get() = requireNotNull(_binding)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentProfileBinding.bind(view)
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state -> binding.title.text = state.title }
            }
        }
    }

    override fun onDestroyView() {
        _binding = null
        super.onDestroyView()
    }
}
```
`FragmentProfileBinding` and `viewModel` are app-provided. Navigation away and back should leave one view-bound collector for the current view; count it in a test rather than assuming an exact duplication rate.

## Explanation in Arabic

الـ Fragment نفسه له Lifecycle، ولو رجّع View غير `null` فالـ View دي ليها Lifecycle تانية عبر `viewLifecycleOwner`. في عملية Back Stack شائعة، FragmentManager ممكن يفضل محتفظ بكائن الـ Fragment بعد `onDestroyView`؛ ولما ترجع الشاشة، تتبني View جديدة و`viewLifecycleOwner` جديد. مش لازم كل تنقل يحصل بنفس التسلسل، فراقب حالة الـ transaction اللي عندك.

أي مرجع مربوط بالـ View، زي `ViewBinding` أو adapter أو listener، عمره ينتهي مع الـ View. لو binding مخزنة في property داخل Fragment وما اتصفرتش في `onDestroyView`، الكائن المحتفَظ به ممكن يمسك شجرة View قديمة وContext. مفيش رقم موثّق يقول إن النمط ده سبب 80% من التسريبات أو إنه يحجز كمية RAM ثابتة.

لجمع `StateFlow` اللي بيحدّث الواجهة، استخدم `viewLifecycleOwner.lifecycleScope` مع `repeatOnLifecycle(STARTED)`. الجمع يقف لما الـ View owner ينزل عن STARTED، وينتهي مع DESTROYED. حالة العمل المنطقية ممكن تفضل في ViewModel مرتبط بالـ Fragment. ولو حاطط `ComposeView` داخل Fragment، لسه عندك View حقيقية؛ استخدم `ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed` عشان تخلص الـ Composition مع دورة حياة الـ View.

## Practical walkthrough

في شاشة ملف شخصي، اربط كل render بالـ View الحالية:
```kotlin
class AccountFragment : Fragment(R.layout.fragment_account) {
    private var _binding: FragmentAccountBinding? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentAccountBinding.bind(view)
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.name.collect { name -> _binding?.name?.text = name }
            }
        }
    }

    override fun onDestroyView() {
        _binding = null
        super.onDestroyView()
    }
}
```
المثال يفترض وجود `FragmentAccountBinding` و`viewModel` من التطبيق؛ اختبار AndroidX Fragment والتنقل هو اللي يثبت إن الـ collector القديم انتهى وإن الـ View القديمة اتحررت.

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

A Fragment instance can outlive one of its view trees. A non-null view has its own `viewLifecycleOwner`, which reaches destruction around `onDestroyView`; a later view gets a new owner. Scope UI collectors to the view owner and clear Fragment-held binding references in `onDestroyView`. A Fragment-scoped ViewModel may preserve logical state across view recreation.

## Interview answer — structured

A Fragment and its view have different lifetimes. The Fragment object may stay managed on a back stack while `onDestroyView` ends the current view lifecycle. Returning to it creates a fresh view tree and a new `viewLifecycleOwner`. That distinction tells me where to put dependencies: the ViewModel or arguments can hold screen logic, while ViewBinding, adapters and UI listeners belong to the current view. I use `viewLifecycleOwner.lifecycleScope` with `repeatOnLifecycle(STARTED)` to collect a state stream only while the view can render it. I clear a Fragment property holding ViewBinding in `onDestroyView` so an old root view is not retained. This prevents a plausible leak path; it does not imply a universal leak percentage or a fixed number of duplicate collectors. If I embed Compose in a Fragment, its `ComposeView` still needs a disposal strategy tied to the view tree. I test navigate away/back and inspect active collectors and retained views rather than assuming every transaction follows an identical path.

## Interview answer — deep senior

AndroidX Fragment exposes two lifecycle owners because a Fragment object and one rendered View tree are not the same resource. When the Fragment provides a non-null View, `viewLifecycleOwner` becomes available around `onViewCreated`. On a downward transition that destroys that view, its lifecycle reaches `DESTROYED` and `onDestroyView` is called; the Fragment instance may still be managed. A subsequent view is a new tree with a new owner. Back-stack `replace` is a common example, but the exact state path depends on the transaction and parent lifecycle.

The risk is ownership mismatch. A Fragment field holding a generated binding holds its root View, which can in turn retain descendants and a Context. If the Fragment remains reachable after its view is destroyed, that old tree can be retained until the field is cleared. The impact depends on the actual tree and reachability; an invented 80% statistic or a fixed RAM cost is not defensible. UI observers registered against the Fragment lifecycle from each `onViewCreated` can also outlive their associated view. Depending on collection structure and cancellation, this may cause stale updates or duplicate work, so I verify with a navigation test and a memory inspection rather than promise an exact count.

For state rendering, I launch in `viewLifecycleOwner.lifecycleScope` and use `repeatOnLifecycle(STARTED)`. The block restarts while that owner is active, then is canceled when it stops and ends when the view is destroyed. A Fragment-scoped ViewModel can hold the logical state and re-emit it to the new view. For one-shot navigation events, I define a separate delivery policy so replay does not trigger duplicate navigation. Compose interop does not remove the view lifetime: a `ComposeView` is a View, and the documented strategy in a Fragment is `DisposeOnViewTreeLifecycleDestroyed`. I also clear adapters or listeners that retain the root view. The proof is one live collector for the current view and no retained old root after repeated back-stack transitions.

## How to answer in the interview

- **Why:** The Fragment object may outlive its rendered view.
- **How:** Contrast Fragment lifecycle with `viewLifecycleOwner` and point to `onDestroyView`.
- **Trade-offs:** Keep screen state in a scoped ViewModel, view references in the view lifetime.
- **Failure cases:** Explain duplicate collection, stale binding, and leaked views.
- **Production solution:** Show view-scoped Flow collection and a navigate-away/back test.

## Deep-dive talking points

Explain view owner availability, back-stack view destruction, ViewBinding cleanup, lifecycle-aware StateFlow collection, adapter/listener retention, and why one-shot effects differ from current state.

## Follow-up questions

- **Interviewer:** "What if I collect a Flow in `fragment.lifecycleScope` from every `onViewCreated`?"
  **Answer:** "Those jobs may outlive the view and accumulate or try to render into stale references. I scope UI collection to `viewLifecycleOwner` and verify the actual collector count after back-stack navigation."
- **Interviewer:** "Does switching to Compose eliminate Fragment view leaks?"
  **Answer:** "No. `ComposeView` is still a View in the Fragment hierarchy. I tie its composition disposal to the view-tree lifecycle and avoid retaining old view references."

## Self-check rubric

Describe one case where Fragment outlives its view; choose the right LifecycleOwner for UI collection; release binding at the correct callback; explain a leak symptom; and design a back-stack recreation test.

## References and reviewed-on date

- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — separate Fragment and view owners.
- [Lifecycle-aware coroutine collection](https://developer.android.com/topic/libraries/architecture/coroutines) — `repeatOnLifecycle` for UI collection.
- [Using Compose in Views](https://developer.android.com/develop/ui/compose/migrate/interoperability-apis/compose-in-views) — `ComposeView` disposal in a Fragment.

Technically reviewed against primary documentation on 2026-10-19.
