---
id: "FLO-23"
question: "What happens if a UI collects indefinitely without lifecycle awareness?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 136
editorial_status: "reviewed"
---

# FLO-23

## Original interview question

What happens if a UI collects indefinitely without lifecycle awareness?

## What the interviewer evaluates

Explain continued offscreen collection, view retention and cold-source cost.

## Explanation in Arabic

لو UI عملت `lifecycleScope.launch { flow.collect { ... } }` مرة واحدة، coroutine ممكن تفضل بتجمع وهي STOPPED لحد DESTROYED. ده يستهلك network/battery، ويحدث view مش ظاهرة، أو يحتفظ reference لview اتدمرت في Fragment لو استخدمنا owner غلط. نستخدم `repeatOnLifecycle` أو Compose lifecycle-aware collection، ونشوف هل المصدر cold هيبدأ من جديد.

### Practical walkthrough in Egyptian Arabic

لو Activity عملت `lifecycleScope.launch { flow.collect { render(it) } }` من غير repeat، Job ممكن يفضل شغال وهي STOPPED؛ تستهلك DB/network وتحدث view غير ظاهرة، وخصوصًا Fragment view ممكن تكون اتدمرت. الحل اربط collection بالـSTARTED وراجع upstream sharing، مش بس أضف `launchIn` في scope أطول.

## Why it matters and how it works

LifecycleScope cancellation happens at owner destruction, not at every STOP. `repeatOnLifecycle` cancels and relaunches the inner collection at configured states. `viewLifecycleOwner` matches Fragment view lifetime. Upstream sharing can prevent repeated expensive source setup on transient stops.

## Worked example

Android conceptual snippet; in a Fragment, `state` is StateFlow and `render` is app code.

```kotlin
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

// Call after Fragment.onViewCreated; stops collection below STARTED.
fun Fragment.collectVisible(flow: StateFlow<String>, render: (String) -> Unit) {
    viewLifecycleOwner.lifecycleScope.launch {
        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            flow.collect { render(it) }
        }
    }
}
// Avoid collecting against Fragment.lifecycle when render touches its View.
```

## Trade-offs and decision criteria

Stopping collection saves offscreen work but can miss ephemeral replay-zero events. StateFlow resumes with current value, which is appropriate for state. For required events, persist/acknowledge them rather than collecting forever to avoid loss.

## Failure modes

A collector tied to Fragment lifecycle can retain a destroyed view after onDestroyView. Even if no leak occurs, an offscreen collector can keep a socket or sensor active. A cold source may re-register on each START; sharing policy should be deliberate.

## Production perspective

A location screen collects a ViewModel StateFlow only while STARTED and unregisters callbackFlow listener when inactive. A worker maintains necessary background location only under Android’s supported background execution rules, separate from a hidden UI collector.

## Interview answer — short

“A raw collection in lifecycleScope lasts until destruction, so it can keep running while UI is stopped. I use repeatOnLifecycle or collectAsStateWithLifecycle, choose the Fragment view owner and design any required event persistence separately.”

## Interview answer — structured

“The common mistake is assuming `lifecycleScope` means visible-only work. It cancels at destruction, but the Activity can be stopped for a long time first. A collecting coroutine may continue rendering, consuming network or holding a Fragment view reference. For Views I use `viewLifecycleOwner.repeatOnLifecycle(STARTED)`; for Compose I use lifecycle-aware state collection. StateFlow gives the latest snapshot after restart. I then inspect cold upstream behavior because starting collection again may reopen a socket or repeat a network request.”

## Interview answer — deep senior

“I investigate both correctness and resource cost. An offscreen collector can maintain sensor registrations or expensive polling, and a Fragment collector bound to the Fragment rather than its view can reference a dead view between onDestroyView and destruction. `repeatOnLifecycle` cancels the inner job at STOP and restarts it at START, while `collectAsStateWithLifecycle` covers common Compose state rendering. That may lose replay-zero effects, which is a modeling problem, not a reason to collect forever. I use StateFlow for current UI state and persist required outcomes. Tests drive lifecycle transitions, count upstream subscriptions and check listener cleanup. `viewLifecycleOwner` matches Fragment view lifetime. I would describe the concrete lifecycle path. A coroutine launched in `lifecycleScope` is cancelled when the lifecycle is destroyed, not merely when the screen moves below STARTED. A long-lived Flow can therefore keep delivering while the Activity is offscreen. That wastes CPU, network, or sensor resources and can update views that should no longer be touched; in a Fragment, using the fragment lifecycle instead of the view lifecycle is especially risky after `onDestroyView`. I use `repeatOnLifecycle` for Views or lifecycle-aware Compose collection and keep UI rendering inside the active block. Then I inspect upstream sharing, because stopping a collector does not automatically stop a producer launched elsewhere. I test Home, navigation, return, and view recreation.”

## How to answer in the interview

- **Why:** DESTROYED is later than offscreen STOPPED.
- **How:** tie UI collection to STARTED and view owner.
- **Trade-off:** restart may re-run cold upstream.
- **Failure case:** hidden screen keeps sensor or render work active.
- **Production solution:** lifecycle tests and upstream audit.

## Deep-dive talking points

Trace STOP versus DESTROY, Fragment view lifecycle and no-subscriber event behavior.

## Follow-up questions

- [FLO-22](../flo-22/): Which API restarts collection? **Answer:** repeatOnLifecycle or collectAsStateWithLifecycle.
- [FLO-21](../flo-21/): What happens to callbackFlow on cancellation? **Answer:** awaitClose should unregister its listener.

## Self-check rubric

Can I explain offscreen cost, bind a Fragment view correctly and preserve required events independently?

## References and reviewed-on date

- [Android lifecycle coroutines](https://developer.android.com/topic/libraries/architecture/coroutines) — collection recommendations.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
