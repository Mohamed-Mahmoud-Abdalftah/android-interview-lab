---
id: "FLO-22"
question: "Compare repeatOnLifecycle and collectAsStateWithLifecycle."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 135
editorial_status: "reviewed"
---

# FLO-22

## Original interview question

Compare repeatOnLifecycle and collectAsStateWithLifecycle.

## What the interviewer evaluates

Compare lifecycle-aware View collection with Compose state collection and restart semantics.

## Explanation in Arabic

في Views، `repeatOnLifecycle(STARTED)` يشغّل block لما LifecycleOwner يوصل STARTED ويلغيه لما ينزل STOPPED، وبيرجع يشغّله عند الرجوع. في Compose، `collectAsStateWithLifecycle()` يحوّل Flow/StateFlow إلى Compose State ويراعي lifecycle تحت الغطاء. لازم نستخدم `viewLifecycleOwner` في Fragment view، ونفهم إن restart ممكن يعيد cold upstream أو replay آخر StateFlow value.

## Practical walkthrough

في Fragment View، `repeatOnLifecycle(STARTED)` تشغّل collection لما view owner يبدأ وتلغيها لما يقف، ثم ترجعها. في Compose Android، `collectAsStateWithLifecycle()` تختصر Flow→Compose State بنفس lifecycle owner المناسب. لو collect من Activity lifecycle بدل `viewLifecycleOwner` في Fragment، ممكن تحدث View مدمرة؛ ولو جمعت hot flow خارج lifecycle، شغلها يستمر وهي مخفية.

## Why it matters and how it works

`repeatOnLifecycle` is a suspending API whose child block restarts serially as lifecycle state changes. `collectAsStateWithLifecycle` is a convenience for rendering a stream as Compose state. For multiple flows in Views, collect them in separate child launches inside the repeat block so one endless collect does not block the next.

## Worked example

Android Fragment conceptual snippet; `state` is `StateFlow<UiState>`, `render` and UiState are app types, and lifecycle runtime KTX is required.

```kotlin
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.material3.Text
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

// Call after Fragment.onViewCreated; use the shorter view lifecycle.
fun Fragment.collectStatus(flow: StateFlow<String>, render: (String) -> Unit) {
    viewLifecycleOwner.lifecycleScope.launch {
        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            flow.collect { render(it) }
        }
    }
}

@Composable
fun StatusScreen(flow: StateFlow<String>) {
    val status by flow.collectAsStateWithLifecycle()
    Text(status)
}
// Requires lifecycle-runtime-ktx, lifecycle-runtime-compose, Fragment, Compose.
```

## Trade-offs and decision criteria

View API offers explicit block control; Compose API is concise for renderable state. Use an effect collector only after deciding replay/loss behavior. Lifecycle-aware collection reduces offscreen work but is not a process-death persistence mechanism.

## Failure modes

Using Fragment.lifecycleScope instead of viewLifecycleOwner can collect after view destruction. Launching a raw collect once in lifecycleScope does not stop at STOP. A cold source may restart and duplicate network calls on every START unless shared upstream.

## Production perspective

A Fragment collects screen StateFlow under repeatOnLifecycle, while a Compose screen uses collectAsStateWithLifecycle. ViewModel shares expensive upstream with stateIn and a grace period; rotation tests verify current state and no duplicate effects.

## Interview answer — short

“repeatOnLifecycle is an explicit Views collection block that starts and stops with lifecycle state. collectAsStateWithLifecycle is a Compose helper that converts a stream to lifecycle-aware State. I use viewLifecycleOwner in Fragments and expect cold upstream to restart unless shared.”

## Interview answer — structured

“For Views I launch from the view lifecycle and call `repeatOnLifecycle(STARTED)`, which cancels the inner collection at STOP and restarts it at START. In Compose, `collectAsStateWithLifecycle` gives a State value for rendering while respecting lifecycle. Both avoid collecting UI state continuously while the screen is invisible. A StateFlow replays its current value on restart, while a cold Flow may rerun source work, so I share expensive upstream in the ViewModel when appropriate. I test rotation and STOP/START separately.”

## Interview answer — deep senior

“Lifecycle-aware collection is a consumer policy, not the source-of-truth design. `repeatOnLifecycle` relaunches its block as the owner crosses the chosen state; if I have multiple endless flows, I launch each as a child within that block. In a Fragment I use `viewLifecycleOwner` so destroyed views do not retain collectors. Compose’s `collectAsStateWithLifecycle` is well suited to renderable state, but one-shot effects still need an explicit delivery contract. Re-collection of a cold Flow can repeat HTTP or listener registration, while a StateFlow gives the latest snapshot. I verify startup, STOP, restart and process recreation, and keep durable business state outside the UI stream. I would choose based on UI framework and required operation. In Views, `repeatOnLifecycle` runs a block while the chosen LifecycleOwner is at least STARTED and cancels/restarts the block around visibility; in a Fragment I use the view lifecycle owner for view-bound work. In Android Compose, `collectAsStateWithLifecycle` converts a Flow or StateFlow into Compose State under a lifecycle minimum, usually STARTED, so recomposition sees the current value while active. Both manage collection, not necessarily the upstream producer: a ViewModel job or eagerly shared source may continue. I test stop/start and rotation, then check the repository sharing policy if background work persists. For multiple flows in a repeat block I launch child collectors so one infinite collection does not block another.”

## How to answer in the interview

- **Why:** UI collection should follow its visible owner.
- **How:** Views repeatOnLifecycle versus Compose collector.
- **Trade-off:** upstream may continue despite stopped UI collection.
- **Failure case:** Fragment collects after its view is destroyed.
- **Production solution:** test stop/start and correct owner selection.

## Deep-dive talking points

Trace START/STOP cycles, cold restart, StateFlow replay and Fragment view destruction.

## Follow-up questions

- [FLO-23](../flo-23/): What if collection never stops? **Answer:** offscreen work continues and may retain a destroyed view.
- [FLO-08](../flo-08/): How avoid repeated upstream work? **Answer:** share in a ViewModel/session scope with deliberate start policy.

## Self-check rubric

Can I use both APIs correctly, choose Fragment view owner and predict restart behavior?

## References and reviewed-on date

- [Android lifecycle coroutines](https://developer.android.com/topic/libraries/architecture/coroutines) — repeatOnLifecycle.
- [Android Compose lifecycle state](https://developer.android.com/reference/kotlin/androidx/lifecycle/compose/package-summary) — collectAsStateWithLifecycle.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
