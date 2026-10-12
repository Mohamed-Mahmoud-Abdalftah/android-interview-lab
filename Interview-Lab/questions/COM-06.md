---
id: "COM-06"
question: "What is Unidirectional Data Flow in Compose?"
topic: "Jetpack Compose"
code: "COM"
group: "A"
phase: 3
priority: "P1"
order: 235
editorial_status: "reviewed"
---

# COM-06

## Original interview question

What is Unidirectional Data Flow in Compose?

## What the interviewer evaluates

- Show state down and events up with one owner.
- Separate UI rendering from business decisions and asynchronous effects.
- Account for transient events without silently dropping or replaying them.

## Explanation in Arabic

في UDF، الـowner مثل ViewModel يخرج `UiState` للـscreen، والـcomposable ترسمه وتُرجع actions عبر callbacks مثل `onRetry`. الـViewModel يعالج الحدث، يحدث state، وقد يطلب من repository عملًا؛ ثم state الجديدة تنزل للواجهة. بهذه الطريقة سبب التغيير واضح واختباره أسهل. لا تعمل screen نسخة mutable موازية لنفس البيانات. أحداث مثل navigation أو Snackbar تحتاج contract واضح: state مستهلكة مرة مع acknowledgment أو event stream بخصائص delivery معلومة، لا مجرد Boolean يعاد تشغيله بعد rotation.

## Why it matters and how it works

UDF makes the rendering function a consumer of state and producer of user intents. A state holder serializes or coordinates changes and exposes a coherent snapshot, commonly as `StateFlow`. Side effects occur in the owner or a composition-aware effect rather than during rendering. This helps distinguish durable screen state from one-time UI actions whose delivery needs lifecycle consideration.

## Worked example

`CheckoutScreen(uiState, onAction)` renders `Loading`, `Ready`, or `Error`; tapping Pay sends `CheckoutAction.Pay`. The ViewModel disables payment while an idempotent request is in flight, records the result, and emits a new state. Navigation to a receipt occurs after authoritative result, with a consumed action or destination state designed to avoid double navigation.

## Trade-offs and decision criteria

A single large state model gives coherent updates but may widen observation and copy cost. Smaller state holders can be appropriate if ownership remains explicit. A channel for ephemeral events is simple but can lose events while no collector exists; representing a destination as state can replay unless it is acknowledged. Match delivery semantics to the event.

## Failure modes

The composable directly calls a repository and repeats work on recomposition. Two sources of truth disagree about whether Pay is enabled. A navigation event replays after rotation, or a Snackbar is dropped while the screen is stopped. A mutable collection changes without emitting new observable state.

## Production perspective

Define a typed action contract, model loading/error/success explicitly, and test event-to-state transitions and lifecycle collection. Record duplicate-tap and restoration behavior for high-value flows; server idempotency remains necessary beyond UI disabling.

## Interview answer — short

“UDF sends immutable state from an owner into composables and user events back to that owner. The owner changes state and handles effects; the UI renders the result.”

## Interview answer — structured

“I give the screen a state value and callbacks rather than letting it mutate repositories during composition. A Pay tap becomes an action; the ViewModel checks whether payment is already running, calls the use case, and emits loading or result state. Compose renders each state. I separately define transient navigation or Snackbar delivery so lifecycle changes do not replay or lose it accidentally. The important invariant is one owner for each fact.”

## Interview answer — deep senior

“Unidirectional flow is an ownership and causality model. The ViewModel or other screen state holder exposes an immutable state snapshot; composables read it and send typed user intents upward. The owner validates the intent, runs business work, and produces a new state. That lets me test a transition without needing a full UI: given Ready and Pay, expect Loading and then a result. It also keeps recomposition safe because rendering does not initiate requests. I pay special attention to one-time actions. A navigation command is not interchangeable with persistent screen state: a replayed flow event may navigate twice, while an unbuffered event may be missed while stopped. I choose an explicit delivery and acknowledgment policy or model the destination state so it can be consumed deterministically. For payment I disable duplicate taps but also use a backend idempotency key because UI controls alone cannot stop retries or process restarts. I avoid two mutable copies of the same form state and make lifecycle-aware collection part of the screen boundary. UDF is useful when the state and event contracts clarify behavior, not because every click needs an elaborate reducer framework.”

## Deep-dive talking points

Discuss state ownership, typed actions, reducer-like transitions, effects, lifecycle event delivery, and idempotency.

## Follow-up questions

- Can the composable call a repository in its body? **Answer:** it should not; rendering may repeat and duplicate work.
- Is a one-shot navigation event ordinary persistent state? **Answer:** it needs a separate delivery or consumption contract to avoid replay or loss.
- Does disabling Pay prevent duplicate charges by itself? **Answer:** no; server-side idempotency is also required.

## Self-check rubric

Trace one event to a state transition, name the owner, and explain one-shot delivery and duplicate protection.

## References and reviewed-on date

- [Compose UI architecture](https://developer.android.com/develop/ui/compose/architecture) — UDF and state/events.
- [UI layer guidance](https://developer.android.com/topic/architecture/ui-layer) — state holders and UI events.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Payment flow is illustrative.
