---
id: "MEM-12"
question: "How can callbacks, Handler, observers, listeners, or static references cause leaks?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "B"
phase: 1
priority: "P1"
order: 67
editorial_status: "reviewed"
---

# MEM-12

## Original interview question

How can callbacks, Handler, observers, listeners, or static references cause leaks?

## What the interviewer evaluates

- Trace a concrete retaining chain from a long-lived owner to a short-lived screen.
- Choose symmetry, lifecycle-aware observation, or cancellation for each API.
- Separate leak prevention from mere exception suppression.

## Explanation in Arabic

أي source عمره أطول من الشاشة ممكن يمسك callback، والـcallback ماسك `Activity` أو `View` عن طريق lambda capture. `Handler.postDelayed` مثال: الـmessage queue تحتفظ بـRunnable لحد ما يتنفذ أو يتشال؛ لو Runnable ماسك binding، هتفضل view القديمة عايشة. `static` أو singleton field يحتفظ بمرجع طول عمر الـprocess، وobserver غير مفصول يحتفظ بالـowner. الحل مش بس `if (isDestroyed) return`، لأن reference ما زال موجود. لازم unregister، remove callbacks، أو استخدم lifecycle owner مناسب، مع عدم ضياع state مهمة عند إعادة الإنشاء.

## Why it matters and how it works

GC reclaims only unreachable graphs. A system or application event source can remain reachable after an Activity closes; its callback then retains the Activity through an implicit `this`, binding, or View reference. Handler queues retain scheduled Runnable objects until execution/removal. Lifecycle-aware observers can remove themselves with an owner, but choosing Fragment instead of Fragment view lifecycle can still retain an obsolete view. A static field is process-lived and should hold only appropriately scoped data.

## Worked example

A screen registers a network-status listener in `onStart()` and removes it in `onStop()`. It also posts a delayed UI hint and removes that Runnable with `handler.removeCallbacks(hintRunnable)` in `onStop()` or view teardown. On re-entry, fresh callbacks are registered for the new view. The pattern assumes a known Handler and listener; the exact API cleanup must match the registration source.

## Trade-offs and decision criteria

Lifecycle-aware Flow/LiveData collection reduces manual cleanup for UI rendering, but external SDK callbacks still require explicit unregister or adapter design. A weak reference can avoid retention but may yield missed callbacks and does not resolve stale operation ownership. A durable event should be stored in a repository rather than relying on a screen callback surviving backgrounding.

## Failure modes

A Handler Runnable references a destroyed binding and crashes later. A singleton callback list grows on each rotation, causing both leaks and duplicate events. A static Context is an Activity rather than application Context. Removing a callback with a different instance does nothing. Test repeated open/close cycles, count registrations, and inspect shortest heap paths from leaked views to roots.

## Production perspective

Wrap third-party listeners in a lifecycle-bound adapter that registers and unregisters the same object. Define whether the source is active while visible or resumed. Record active subscription counts in debug builds and add a leak regression test for the screen. Production telemetry can track OOM and memory trend but avoid logging event payloads.

## Interview answer — short

“Long-lived callback sources can retain a destroyed screen through captured references. I remove or cancel registrations at the matching lifecycle boundary and verify the retaining path disappears.”

## Interview answer — structured

“A listener, Handler message, observer, or static field can hold a strong reference to an Activity or View after its lifetime ends. For example, a delayed Runnable captures a binding and sits in a message queue. Checking `isDestroyed` before rendering prevents some crashes but does not release that reference. I pair registration with unregister using the same callback instance, scope UI observation to the view lifecycle, and remove pending delayed messages. I test repeated navigation for duplicate callbacks and use a heap dump to identify any remaining root path.”

## Interview answer — deep senior

“I diagnose these leaks as ownership chains, not as special behavior of one API. A process-wide singleton, SDK event bus, or Handler queue remains reachable; the stored callback captures a short-lived screen or binding; therefore GC cannot collect that UI graph. I identify the source and its intended lifetime, then make subscription ownership explicit. A visible-only listener can register at STARTED and unregister at STOPPED, a Fragment UI stream uses `viewLifecycleOwner`, and a delayed Runnable is removed when its view is destroyed. I retain the exact callback token needed for removal and avoid simply adding a destroyed-state guard, which still leaves the graph retained. Important events are persisted in model state so cleanup does not lose them. I verify with a repeatable rotation/back-stack loop, registration counts, and heap retaining paths.”

## Deep-dive talking points

Discuss callback capture, Handler queue retention, static root, exact removal token, Fragment view owner, and durable event state.

## Follow-up questions

- Does `if (activity.isDestroyed) return` fix the leak? **Answer:** no; it may avoid UI work but the callback still retains the Activity until removed.
- Why use the same listener instance for removal? **Answer:** many APIs remove by callback identity; a newly created lambda is not the registered object.
- Can lifecycle-aware observation still leak a Fragment view? **Answer:** yes if the wrong owner is used or another callback captures the old binding.

## Self-check rubric

Trace one root path, pair register/unregister, cancel a Handler callback, identify wrong Fragment owner, and prove release.

## References and reviewed-on date

- [Manage your app's memory](https://developer.android.com/topic/performance/memory) — reference and resource ownership.
- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — view lifetime.
- [Handler reference](https://developer.android.com/reference/android/os/Handler) — callback queue and removal APIs.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The cleanup sketch is illustrative.
