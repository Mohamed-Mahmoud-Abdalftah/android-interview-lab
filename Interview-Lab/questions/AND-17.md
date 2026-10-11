---
id: "AND-17"
question: "How should you register/unregister lifecycle-dependent listeners?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "B"
phase: 1
priority: "P1"
order: 47
editorial_status: "reviewed"
---

# AND-17

## Original interview question

How should you register/unregister lifecycle-dependent listeners?

## What the interviewer evaluates

- Pair registration with the lifecycle boundary matching the resource and visibility requirement.
- Remove callbacks from their exact owner; distinguish Activity, Fragment, and Fragment view lifecycles.
- Avoid double registration, leaked Context references, and missed events after recreation.

## Explanation in Arabic

الـlistener غالبًا مصدر أحداث ماسك reference للـcallback. لو سجلته في `onStart()` مثلًا، افصله في `onStop()` لما التحديثات مطلوبة بس والشاشة مرئية. لو مربوط بـFragment view استخدم `viewLifecycleOwner`، لأن الـview ممكن تتدمر والـFragment لسه موجود. المهم تختار lifecycle مناسب لاستهلاك الأحداث، مش تحفظ قاعدة ثابتة لكل المصادر. الـFlow من UI يتجمع بـ`repeatOnLifecycle` عشان يوقف collection ويرجعه مع visibility؛ لكن لازم تفهم إن المصدر نفسه قد يستمر إذا كان hot/shared. سجل مرة لكل owner، وخلي unregister idempotent لو الـAPI يتطلب.

## Why it matters and how it works

An event source retains callbacks until removed or its own lifetime ends. A system sensor listener, broadcast receiver, or repository observer can therefore keep a destroyed Activity or view reachable. A lifecycle observer can own registration and disposal at the intended state. For a Fragment view, `viewLifecycleOwner` limits UI collection to the current view instance. Lifecycle-aware collection suspends or cancels the UI observer at a boundary; it does not automatically shut down upstream work with a longer scope.

## Worked example

For a visible-only sensor preview, register the sensor listener in `onStart()` and call `sensorManager.unregisterListener(listener)` in `onStop()`. For a Fragment's UI StateFlow, launch from `viewLifecycleOwner.lifecycleScope` and call `repeatOnLifecycle(Lifecycle.State.STARTED) { state.collect { render(it) } }`. This abbreviated Kotlin assumes the AndroidX lifecycle KTX extensions, an existing listener, and a main-safe `render`; it is not a standalone program.

## Trade-offs and decision criteria

`STARTED` is suitable for visible UI updates; a resource needed while resumed only may use `RESUMED`. A process-wide observer needs a process or application owner, not a transient screen. Automatic `repeatOnLifecycle` removes manual UI collection bookkeeping, but direct platform listeners still need explicit cleanup or a lifecycle wrapper. Missing interim events is acceptable for state streams but may be wrong for one-off operations that require persistence.

## Failure modes

Registration in `onCreate()` with no matching removal keeps receiving callbacks after the screen closes. Collecting against a Fragment lifecycle renders into a destroyed view. Calling register every `onResume()` without symmetric unregister duplicates callbacks. Stop/start races can drop transient events; represent durable state in a repository and reload it on return. Use a heap dump and registration counters to diagnose retention and duplication.

## Production perspective

In a barcode scanning screen, camera preview and sensor updates run only while visible. UI observation uses the view lifecycle; the scan result is persisted before navigation. Instrument active registrations and test rotation, back navigation, split-screen visibility, and app backgrounding. A stop path releases hardware promptly and a recreated screen reads the latest saved result.

## Interview answer — short

“Register listeners at the lifecycle state where their events are needed and remove them at the matching exit state. For Fragment UI, use the view lifecycle; for Flow, use lifecycle-aware collection.”

## Interview answer — structured

“I first decide whether a listener is screen-visible, resumed-only, or process-wide. A visible sensor listener can register in `onStart` and unregister in `onStop`. A Fragment view observer should use `viewLifecycleOwner` so it cannot update an obsolete view. For Flow I use `repeatOnLifecycle(STARTED)`, which restarts collection as the screen becomes visible. I still examine the upstream producer, because stopping a UI collector may not stop a shared source. I test repeated transitions to detect duplicate registrations and leaks. I pair registration and cleanup at the same lifecycle boundary: for visible UI I often use `onStart`/`onStop`, and for a Fragment view I use `viewLifecycleOwner`. A listener source may hold a strong callback reference, so an unbalanced registration can leak a screen or deliver duplicates. Durable events belong in a repository, not a transient callback.”
## Interview answer — deep senior

“The correct boundary follows ownership and resource cost. If an external API retains my callback, I make registration and cleanup symmetrical and idempotent, and choose STARTED or RESUMED according to whether partially visible UI needs updates. In a Fragment I bind view work to `viewLifecycleOwner`, not the Fragment instance, because the view has a shorter lifetime. For Flow, lifecycle-aware collection prevents rendering after stop, but a hot producer or a repository scope can continue; I manage that separately. I do not rely on transient callbacks as the only record of an important event. I persist durable state, then let a recreated screen resubscribe. Rotation, process recreation, split screen, and rapid background transitions are tests for both leaks and missed updates. The right boundary depends on what the listener does. A sensor preview may need to run only while the screen is visible; a process-wide connectivity monitor may be owned by an application-scoped component. I avoid storing an Activity callback in a singleton without an explicit unregister path. For Flow rendering, `repeatOnLifecycle(STARTED)` restarts collection around visibility, and in a Fragment it uses the view owner so a destroyed binding is not retained. Stop/start may miss transient emissions, so important business state is reloaded from an authoritative repository rather than trusting a one-shot event. Tests repeatedly navigate, rotate and background the app, checking callback counts and heap retention.”
## Deep-dive talking points

Discuss callback ownership, STARTED versus RESUMED, Fragment view lifecycle, hot Flow producer scope, and repeat-transition testing.

## Follow-up questions

- Why is `viewLifecycleOwner` needed in a Fragment? **Answer:** its view can be destroyed while the Fragment remains; view-bound callbacks must stop with the view.
- Does `repeatOnLifecycle` stop a repository's shared producer? **Answer:** it stops and restarts its collection block; producer behavior depends on the upstream scope and sharing policy.
- How do you catch duplicate listener registration? **Answer:** exercise repeated start/stop transitions, count active registrations, and assert a single callback per event.

## Self-check rubric

Choose a lifecycle boundary, pair registration and removal, explain Fragment view ownership, distinguish UI collection from producer lifetime, and test rapid transitions.

## References and reviewed-on date

- [Lifecycle-aware components](https://developer.android.com/topic/libraries/architecture/lifecycle) — observer ownership.
- [StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — lifecycle-aware collection.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The snippets are illustrative and were not Android-compiled.
