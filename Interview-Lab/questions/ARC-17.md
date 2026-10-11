---
id: "ARC-17"
question: "How do you manage one-time effects in a UDF architecture?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 162
editorial_status: "reviewed"
---

# ARC-17

## Original interview question

How do you manage one-time effects in a UDF architecture?

## What the interviewer evaluates

Handle transient UI actions without event loss or repetition across lifecycle and process death.

## Explanation in Arabic

في UDF، user events تدخل state holder ونتيجتها state جديدة. Snackbar أو navigation غالبًا “one-time effect”، لكن channel/SharedFlow بس ممكن تضيع event لو UI مش بتجمع، وreplay ممكن تعيدها بعد rotation. Android guidance تفضّل تمثّل ViewModel event كـUI state قابل للملاحظة؛ مثل `showLoginRequired` ومعاه acknowledgement لما UI تنفذ action. Navigation trigger لازم مرتبط بbusiness state أو state flag واضح، مش payment effect يتنفّذ اعتمادًا على emission عابر. لو العملية لازم تنجو من process death، persist الحالة أو request ID؛ effect stream في الذاكرة لا يكفي.

## Why it matters and how it works

UDF makes events flow to the state holder and state flow back. Delivery semantics for effects need explicit acknowledgement/replay policy. Lifecycle-aware collection can pause, so ephemeral channels are not durable business queues.

## Worked example

Conceptual flow: `onSave()` updates state to `Saved(pendingNavigation = true)` after repository confirmation; UI observes it, navigates, then calls `onNavigationHandled()`. If process death can occur before handling, persist the underlying saved record and derive destination from restored state.

## Trade-offs and decision criteria

A state flag with acknowledgement is more verbose but observable and testable. An ephemeral effect stream can suit harmless transient feedback when loss is acceptable. Avoid treating any in-memory stream as exactly-once across process death.

## Failure modes

A `Channel` sends navigation while the Activity is stopped; no collector receives it or it gets consumed by an old collector. A replayed `SharedFlow` can navigate twice after rotation. Specify delivery guarantees and test lifecycle transitions.

## Production perspective

A signup flow persists account creation, exposes `AccountCreated(id)` state, navigates after UI acknowledgement, and can recover from recreation. A cosmetic toast can be best-effort; financial confirmation must derive from durable status.

## Interview answer — short

In UDF, I turn events into state and define acknowledgement for one-time UI actions. An in-memory effect stream may lose or replay events across lifecycle changes, so durable business outcomes must come from persisted state.

## Interview answer — structured

I first classify the effect: a cosmetic toast may be best-effort, while navigation after account creation should be reproducible. Android guidance recommends ViewModel events produce UI state. I can expose a pending navigation state, let the UI act, then acknowledge it. A Channel or SharedFlow is possible if I define buffering and replay behavior, but it is not durable across process death. For payments I derive the UI from server-backed status rather than an ephemeral success event. For navigation after signup, I prefer a state that says account creation succeeded and a pending navigation action, then an acknowledgement after the UI handles it. I test rotation between those steps. A best-effort toast has a weaker requirement and may use an ephemeral effect.

## Interview answer — deep senior

The hard part is delivery semantics. Compose and Activity lifecycles can stop collection; a channel may deliver to an unexpected collector, while replay may duplicate a command. I prefer modeling the result as state when the action matters: the ViewModel exposes a pending outcome, UI consumes it in a lifecycle-aware way, and calls back to acknowledge completion. The underlying business record is persisted if it must survive process death. I test rotation between state update and acknowledgement, repeat collectors, back stack recreation, and duplicate taps. For purely decorative feedback, a best-effort effect stream may be acceptable and simpler. I never equate one emission with exactly-once payment execution or server confirmation. The effect contract must say what happens with zero collectors, a recreated collector, and process death. A Channel can lose an item or deliver it to the wrong consumer depending on setup; replay can repeat navigation. State with acknowledgement makes the pending action visible and testable, but only persisted or reconstructible business state survives process death. If server confirmation matters, the app should derive it from repository status, not from whether an effect was emitted. This is a delivery design problem, not simply a choice of Flow type.

## Deep-dive talking points

Compare state acknowledgement with Channel and SharedFlow semantics during stop, rotation and process death.

## Follow-up questions

- [ARC-09](../arc-09/): Is a navigation command a domain fact? **Answer:** no; derive it from UI state or confirmed domain outcome.
- [FLO-20](../flo-20/): Does SharedFlow guarantee process-death delivery? **Answer:** no; it is in-memory.

## Self-check rubric

Describe how navigation occurs once after signup across rotation and why an in-memory effect is not a durable queue.

## References and reviewed-on date

- [Android UI events](https://developer.android.com/topic/architecture/ui-layer/events) — state-driven ViewModel events.
- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — UDF.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
