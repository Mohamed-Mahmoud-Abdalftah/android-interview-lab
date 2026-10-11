---
id: "FLO-27"
question: "A navigation event fires twice after rotation. How do you investigate event modeling and consumption?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 140
editorial_status: "reviewed"
---

# FLO-27

## Original interview question

A navigation event fires twice after rotation. How do you investigate event modeling and consumption?

## What the interviewer evaluates

Investigate duplicate navigation through replay, collector duplication and consumption race.

## Explanation in Arabic

لو navigation حصلت مرتين بعد rotation، نفتش: هل `StateFlow<Boolean>` لسه true فـcollector جديد أعاد الفعل؟ هل `SharedFlow(replay=1)` رجّعت command؟ هل عندنا collectors اتنين أو lifecycle restart؟ الحل يعتمد على العقد: نخزن destination/current screen كـstate، أو effect بمعرّف مع acknowledgment، ونخلي business completion durable. ما نعتبرش Channel حل سحري لكل race.

## Why it matters and how it works

Replayed state is correct for facts but can be wrong for imperative effects. A new collector may observe the last value, and duplicate collectors may both act. Channel receive can race with view destruction between dequeue and navigation. Instrument event IDs, producer calls and consumer lifecycle to locate duplication before changing primitive.

## Worked example

Conceptual Kotlin model uses a unique effect ID; UI must acknowledge after handling according to app navigation contract.

```kotlin
data class NavEffect(val id: Long, val route: String)
interface NavEffectStore {
    suspend fun pending(): NavEffect?
    suspend fun acknowledge(id: Long)
}
// UI reads pending, navigates under its lifecycle, then acknowledges;
// exact acknowledgement timing must be tested against rotation/process death.
```

## Trade-offs and decision criteria

For simple destination state, deriving navigation graph from authenticated state may be more robust than one-shot commands. An ID/ack protocol is more complex and must define when navigation counts as handled. SharedFlow replay zero avoids some duplicates but can lose offscreen emissions.

## Failure modes

Clearing a Boolean immediately after emission can race with collection and lose the effect; leaving it true replays it. A Channel may dequeue before the UI navigates and lose the action on rotation. Duplicated producer calls also need root-cause analysis.

## Production perspective

For sign-in, the authoritative session state drives the destination so a recreated UI lands correctly without issuing a repeated push. For a non-critical snackbar, best-effort loss is acceptable. Tests rotate before, during and after event consumption and record IDs in logs.

## Interview answer — short

“I check whether navigation was modeled as replayed state or event, whether multiple collectors exist, and whether the producer emitted twice. I prefer destination derived from durable session state or an explicit ID/ack protocol when once-only handling matters.”

## Interview answer — structured

“A StateFlow Boolean remains true after rotation and can trigger the new collector again; a SharedFlow with replay can do the same. But duplication can also come from two collectors or two producer calls, so I trace event IDs and lifecycle. If navigation represents authenticated destination, I derive it from session state rather than fire a command. For a true one-shot effect I define replay and acknowledgement, accepting its race complexity. A Channel changes delivery semantics but does not guarantee process-durable exactly-once navigation. For simple destination state, deriving navigation graph from authenticated state may be more robust than one-shot commands. An ID/ack protocol is more complex and must define when navigation counts as handled. SharedFlow replay zero avoids some duplicates but can lose offscreen emissions.”

## Interview answer — deep senior

“I would reproduce the exact rotation window and instrument producer emission, collector start/stop and navigation with stable effect IDs. If the producer emits once but two collectors navigate, I fix ownership/lifecycle. If StateFlow stores `navigate=true`, replay is working as designed for state but the model is wrong for an imperative action. A replayed SharedFlow can also repeat; replay zero can lose an event while stopped. Channel one-consumer receive can lose an effect after dequeue but before action. For session-driven destinations I use durable session state and declarative routing. For effects requiring one-time handling I implement a persisted ID and acknowledgement protocol, then test crash windows and accept that UI navigation itself is not an atomic database transaction. Replayed state is correct for facts but can be wrong for imperative effects. A new collector may observe the last value, and duplicate collectors may both act. Channel receive can race with view destruction between dequeue and navigation. Instrument event IDs, producer calls and consumer lifecycle to locate duplication before changing primitive. Clearing a Boolean immediately after emission can race with collection and lose the effect; leaving it true replays it. A Channel may dequeue before the UI navigates and lose the action on rotation. Duplicated producer calls also need root-cause analysis.”

## Deep-dive talking points

Trace producer count, replay, two collectors and acknowledge-before/after-action windows.

## Follow-up questions

- [FLO-10](../flo-10/): Is navigation state or event? **Answer:** a destination can be state; an imperative push needs explicit delivery semantics.
- [FLO-20](../flo-20/): Does Channel guarantee once? **Answer:** no, dequeue and UI action can race.

## Self-check rubric

Can I diagnose root cause before changing type, define consumption and test rotation windows?

## References and reviewed-on date

- [Kotlin StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — replayed latest value.
- [Kotlin SharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — replay behavior.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
