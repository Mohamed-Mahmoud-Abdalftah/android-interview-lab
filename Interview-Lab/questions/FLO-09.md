---
id: "FLO-09"
question: "Compare SharingStarted.Eagerly, Lazily, and WhileSubscribed."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 122
editorial_status: "reviewed"
---

# FLO-09

## Original interview question

Compare SharingStarted.Eagerly, Lazily, and WhileSubscribed.

## What the interviewer evaluates

Compare eager, lazy and subscriber-driven sharing including restart and resource tradeoffs.

## Explanation in Arabic

`Eagerly` يبدأ upstream فور إنشاء shared stream حتى لو مفيش subscribers؛ `Lazily` يبدأ مع أول subscriber ويفضل شغال بعده طول عمر الـscope؛ `WhileSubscribed` يبدأ مع أول subscriber ويوقف بعد آخر واحد بtimeout قابل للضبط، وممكن يبدأ من جديد. الـtimeout القصير يوفر battery لكن rotation السريعة ممكن تعمل restart/network reconnect.

## Why it matters and how it works

`SharingStarted` controls the sharing coroutine, not whether a hot flow instance exists. With WhileSubscribed, stop timeout reduces churn; replay expiration can reset replay cache, and stateIn resets to its initial value when configured expiration elapses. Match policy to freshness, connection cost and security/session scope.

## Worked example

Android ViewModel example assumes `source` is a cold Flow of immutable UiState and initial value is truthful.

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*

class StatusViewModel(source: Flow<String>) : ViewModel() {
    val status = source.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000),
        "loading",
    )
}
```

## Trade-offs and decision criteria

Eagerly lowers first-subscriber wait but consumes battery/network before demand. Lazily avoids initial idle work but does not stop after subscribers leave. WhileSubscribed saves resources yet can restart a costly source. Use a small stop timeout to span transient lifecycle gaps when appropriate.

## Failure modes

Assuming Lazily stops on background can leave a socket active for the entire ViewModel lifetime. Setting WhileSubscribed stop timeout to zero can reconnect on every brief STOP/START. A long replay cache may show stale user data after session change.

## Production perspective

A live score screen uses WhileSubscribed with a short grace window to survive rotation without reconnect, while a session owner cancels sharing at logout. Metrics count reconnects and battery cost; tests simulate subscriber transitions.

## Interview answer — short

“Eagerly starts immediately; Lazily starts with the first subscriber and keeps running; WhileSubscribed starts and stops with subscribers, optionally after a grace period. I choose based on startup latency, battery and restart behavior.”

## Interview answer — structured

“The policy determines when the shared upstream runs. Eagerly pays resource cost right away, which can reduce first-view latency. Lazily waits for the first subscriber but does not stop merely because subscribers leave. WhileSubscribed can stop when there is no demand and restart later; a stop timeout smooths brief rotation or navigation gaps. I tune it according to whether upstream is a cheap Room query or an expensive socket, and I keep session data scoped so logout clears it. Eagerly lowers first-subscriber wait but consumes battery/network before demand. Lazily avoids initial idle work but does not stop after subscribers leave. WhileSubscribed saves resources yet can restart a costly source. Use a small stop timeout to span transient lifecycle gaps when appropriate.”

## Interview answer — deep senior

“I would measure source cost and correctness needs before picking a policy. A persistent in-memory derived state may justify eager collection. A cold expensive source that is only needed on visible screens usually favors WhileSubscribed, with a grace interval to avoid reconnecting on configuration changes. Lazy sharing avoids work before first use but can keep an upstream alive longer than expected. WhileSubscribed may restart the upstream and replay old data or reset state according to replay-expiration settings, so the UI must model freshness. I test two subscribers, last unsubscribe, quick resubscribe and session invalidation. Battery savings are meaningful only if the source actually stops when sharing stops. `SharingStarted` controls the sharing coroutine, not whether a hot flow instance exists. With WhileSubscribed, stop timeout reduces churn; replay expiration can reset replay cache, and stateIn resets to its initial value when configured expiration elapses. Match policy to freshness, connection cost and security/session scope. Assuming Lazily stops on background can leave a socket active for the entire ViewModel lifetime. Setting WhileSubscribed stop timeout to zero can reconnect on every brief STOP/START. A long replay cache may show stale user data after session change. A live score screen uses WhileSubscribed with a short grace window to survive rotation without reconnect, while a session owner cancels sharing at logout.”

## Deep-dive talking points

Explain subscription transitions, replay expiration, rotation grace and session logout.

## Follow-up questions

- [FLO-08](../flo-08/): What starts sharing? **Answer:** `stateIn` or `shareIn` launches the sharing coroutine under the chosen policy.
- [FLO-31](../flo-31/): How choose for battery? **Answer:** measure idle upstream cost and restart/churn tradeoffs.

## Self-check rubric

Can I predict start/stop for all three, explain timeout, and identify a correctness risk on restart?

## References and reviewed-on date

- [Kotlin SharingStarted API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-sharing-started/) — policy semantics.
- [Android StateFlow/SharedFlow guide](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — lifecycle use.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
