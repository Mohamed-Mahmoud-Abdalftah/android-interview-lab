---
id: "FLO-10"
question: "What is the difference between state and transient events?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 123
editorial_status: "reviewed"
---

# FLO-10

## Original interview question

What is the difference between state and transient events?

## What the interviewer evaluates

Separate durable/current state from one-time UI effects and define delivery semantics.

## Explanation in Arabic

الـstate هي حقيقة حالية ينفع UI جديد يشوفها تاني، زي `isLoggedIn` أو `paymentStatus=Pending`. الـtransient event فعل لحظي زي إظهار snackbar أو navigation command، وإعادته بعد rotation ممكن تكرر الفعل. لكن لو الحدث مهم تجاريًا، ما نخزّنش بس في SharedFlow؛ نخزن outcome في مصدر durable ونخلي UI تشتق التأثير مع acknowledgment واضح.

## Practical walkthrough

`UiState.Success` بتوصف الشاشة وتستحق إعادة العرض بعد rotation؛ `NavigateToReceipt` أمر لحظي لا لازم يتكرر بنفس الطريقة. لو حطيت navigation كـBoolean في StateFlow، collector الجديدة تشوف true وتتنقل تاني. ولو SharedFlow بدون replay ومافيش subscriber وقت الإرسال، الحدث ممكن يضيع. قرر هل الحدث ephemeral فعلًا ولا نتيجة دائمة تستحق saved-state/acknowledgment.

## Why it matters and how it works

StateFlow replays latest state and conflates equal values; that is ideal for rendering, not counting occurrences. SharedFlow/Channel have delivery and replay caveats, especially when no collector is active. Model business results as durable state, then use UI effects only for best-effort presentation or explicit consumption protocols.

## Worked example

Conceptual Kotlin model; navigation effect is best-effort while payment status is persistent repository state.

```kotlin
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow

data class ScreenState(val paymentStatus: String, val receiptId: String? = null)
class PaymentPresenter {
    private val _state = MutableStateFlow(ScreenState("pending"))
    val state = _state.asStateFlow()
    private val _hints = MutableSharedFlow<String>(extraBufferCapacity = 1)
    val hints = _hints.asSharedFlow()
    fun markSaved(receiptId: String) { _state.value = ScreenState("saved", receiptId) }
    suspend fun showHint() { _hints.emit("Saved") }
}
// Receipt identity is recoverable state; UI handles navigation by ID with
// back-stack/acknowledgment rules. A decorative hint may be transient.
```

## Trade-offs and decision criteria

An event stream avoids storing a one-shot command as replayed state, but may lose events without subscribers. A consumed flag in state can coordinate UI acknowledgement but adds protocol complexity. Persist outcome first when loss is unacceptable.

## Failure modes

A `StateFlow<Boolean>` navigation flag stays true after rotation and navigates again. A replay-zero SharedFlow emitted while the UI is stopped can be missed. Treat neither as exactly-once durable delivery.

## Production perspective

A payment completion is recorded in Room/server status. UI observes Success and navigates only through a documented consumption or destination state; a snackbar may be best-effort. Tests rotate before/after completion and kill the process between persistence and display.

## Interview answer — short

“State is a current fact a new collector should render; a transient event is an occurrence whose replay may be wrong. StateFlow suits state. For effects I define whether loss or replay is acceptable, and I persist business outcomes that must survive process death.”

## Interview answer — structured

“I ask whether a new screen instance should see the value. Loading, account and payment status are state, so I expose a current snapshot. A snackbar or navigation command is an effect; replaying it can duplicate action. SharedFlow or Channel can carry best-effort effects, but neither silently guarantees delivery while no UI collector exists or after process death. For important outcomes I persist the status and design a consumption/acknowledgement rule if the UI action must occur once.”

## Interview answer — deep senior

“A common mistake is putting `navigate=true` in StateFlow: it survives rotation as the latest state and can trigger navigation twice, while a second identical event may be suppressed by equality. Swapping to a replay-zero SharedFlow avoids replay but may lose an emission when the UI is stopped. The right design starts from delivery requirements. For a cosmetic snackbar, loss may be acceptable. For order completion, the server and local database store an authoritative status; the UI derives the destination or exposes an acknowledged effect with a stable event ID. I test collectors joining late, rotation and process death. Exactly-once UI effects are a protocol problem, not a property automatically supplied by a Flow type. Treat neither as exactly-once durable delivery. I would ask whether the value describes the world now or asks the UI to do something once. Loading, data, and error belong to durable screen state, commonly StateFlow. Navigation and Snackbar are effects, but their delivery requirements differ: a decorative toast can be dropped, while a completed purchase destination may need a recoverable state or acknowledged command. StateFlow replays its latest value, so a Boolean `navigate=true` can fire again after rotation; a zero-replay SharedFlow can miss an emission while UI is stopped. The answer is an explicit contract: who owns the event, whether it must survive a lifecycle gap, and how it is consumed. I test rotation and background delivery, not just a single happy tap.”

## How to answer in the interview

- **Why:** persistent state and one-time commands have different replay needs.
- **How:** classify Success versus navigation.
- **Trade-off:** replay can duplicate; no replay can lose.
- **Failure case:** repeated destination after rotation.
- **Production solution:** acknowledgment or recoverable destination state where required.

## Deep-dive talking points

Define replay, acknowledgement and process-death requirements before selecting a primitive.

## Follow-up questions

- [FLO-20](../flo-20/): Can Channel guarantee a navigation event? **Answer:** not across process death and not without a consumption contract.
- [FLO-27](../flo-27/): Why duplicate after rotation? **Answer:** a replayed state/effect was not consumed or modeled correctly.

## Self-check rubric

Can I identify current facts versus occurrences, state acceptable loss, and design a durable business outcome?

## References and reviewed-on date

- [Kotlin StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — latest-state replay.
- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — event replay/buffer behavior.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
