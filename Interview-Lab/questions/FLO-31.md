---
id: "FLO-31"
question: "How do you choose SharingStarted for battery, correctness, and subscription behavior?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 144
editorial_status: "reviewed"
---

# FLO-31

## Original interview question

How do you choose SharingStarted for battery, correctness, and subscription behavior?

## What the interviewer evaluates

Choose SharingStarted using battery cost, freshness and subscriber transitions.

## Explanation in Arabic

لو upstream sensor/socket غالية، `WhileSubscribed` توقفها بعد آخر UI subscriber وتوفر battery، مع grace قصيرة للrotation. لو لازم cache تبقى دافئة قبل أول شاشة، `Eagerly` قد يناسب مع cost واضح. `Lazily` يبدأ عند أول subscriber لكن يفضل شغال حتى نهاية scope. نختبر restart والفجوة في data، ونحدد replay expiration/session logout بدل إعداد ثابت لكل streams.

## Practical walkthrough

لو repository Flow بتفتح location updates، `Eagerly` قد تفضل شغالة من غير UI؛ `WhileSubscribed(5_000)` توفر battery بعد خروج الشاشة وتتفادى restart سريع أثناء rotation. لكن لو sync مهمة مالية لازم تكمل حتى UI مخفية، ما تربطش شغلها بعدد subscribers؛ انقلها worker/repository owner. راقب replay expiration لأن cache ممكن ترجع initial value.

## Why it matters and how it works

`WhileSubscribed(stopTimeoutMillis, replayExpirationMillis)` controls stop and cache reset; stateIn can reset to initial value after replay expiration. A source may need reconnection/authentication on restart. Correctness of a continuous audit feed cannot depend on UI subscribers; run such work in a durable owner instead.

## Worked example

Android ViewModel illustration assumes source is cold Flow and initial Loading is a truthful state.

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*

class SensorViewModel(source: Flow<String>) : ViewModel() {
    val reading = source.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000),
        "loading",
    )
}
```

## Trade-offs and decision criteria

WhileSubscribed saves resources but can miss source changes when disconnected; a state source must provide current snapshot on reconnect. Eagerly costs idle resources. Lazily avoids pre-use cost but does not stop after use. Tune grace from measured rotation/background patterns.

## Failure modes

A sensor shared Eagerly in application scope can drain battery all day. WhileSubscribed on a transaction audit process can stop required recording when UI leaves. Replay after logout can expose stale user data if scope is not reset.

## Production perspective

A live exercise screen uses WhileSubscribed and a 5-second grace to avoid Bluetooth reconnect on rotation; a separate service owns any legally required continuous measurement. Session logout cancels sharing, and metrics track active connection time/reconnects.

## Interview answer — short

“I choose SharingStarted by upstream cost and correctness. WhileSubscribed can save battery, Eagerly warms state at idle cost, and Lazily keeps running after first use. I tune stop grace and verify restart/freshness behavior.”

## Interview answer — structured

“For an expensive socket or sensor needed only while a screen is visible, I usually consider WhileSubscribed with a short stop timeout. It allows quick rotation without immediate reconnect and stops work in the background. Eagerly is useful if first-view latency matters enough to pay continuous cost; Lazily starts on first demand but remains active afterward. I also consider whether the source can provide a fresh snapshot after restart and whether replayed state is safe across logout. Tests count subscriptions and measure active resource time. Tune grace from measured rotation/background patterns.”

## Interview answer — deep senior

“The start policy is part of architecture, not a styling preference. I list the upstream cost, first-subscriber latency, data-loss tolerance and owner lifetime. `WhileSubscribed` can stop a sensor or socket for battery savings, but restart must recover current state or missed events; a required audit stream cannot be owned only by UI subscriptions. A grace period smooths transient STOP/START during rotation, and replay expiration controls how long old values remain. `Eagerly` is acceptable for cheap state that must be warm; `Lazily` delays first work but continues until scope cancellation. I measure reconnect count, battery cost and stale-data time, and cancel the session scope on logout. I would decide ownership before selecting a constant. A screen-bound sensor or expensive Room transformation usually benefits from `WhileSubscribed` with a measured stop timeout, so short navigation or rotation gaps do not thrash the producer while long background periods stop it. `Eagerly` is reasonable when an application-wide source must be warm regardless of observers. `Lazily` waits for the first observer but normally keeps the upstream running for the scope lifetime afterward. I distinguish upstream lifetime from cached value retention: `WhileSubscribed` can also expire replay, affecting what a returning UI first sees. Required business work, such as a payment reversal, must not depend on UI subscriptions at all. I verify collector counts, restart costs, battery use, and the first value after return.”

## How to answer in the interview

- **Why:** subscription policy affects resource use and first-value correctness.
- **How:** map sensor, warm app source, and durable task to owners.
- **Trade-off:** battery versus restart latency.
- **Failure case:** UI subscribers accidentally control required business work.
- **Production solution:** measure starts, replay expiry, and battery.

## Deep-dive talking points

Trace first subscriber, last subscriber, grace timeout, replay reset and logout.

## Follow-up questions

- [FLO-09](../flo-09/): Does Lazily stop after unsubscribe? **Answer:** no, not solely due to zero subscribers.
- [FLO-08](../flo-08/): Where does sharing live? **Answer:** in the scope supplied to stateIn/shareIn.

## Self-check rubric

Can I justify a policy from cost/correctness, predict restart and define session invalidation?

## References and reviewed-on date

- [Kotlin SharingStarted API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-sharing-started/) — start/stop and replay expiration.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
