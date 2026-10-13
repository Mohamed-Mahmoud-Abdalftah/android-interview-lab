---
id: "ARC-25"
question: "Compare MVVM and MVI for a payment state machine with many transitions."
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "C"
phase: 2
priority: "P1"
order: 170
editorial_status: "reviewed"
---

# ARC-25

## Original interview question

Compare MVVM and MVI for a payment state machine with many transitions.

## What the interviewer evaluates

Choose MVVM versus reducer-style MVI using transition complexity and distributed payment uncertainty.

## Explanation in Arabic

Payment flow حالات كتير: idle، validating، submitting، pending verification، confirmed، declined، recoverable error. MVVM ممكن تنجح لو ViewModel بتصدر immutable state وevents واضحة؛ مش لازم MVI framework. لما transitions كثيرة ومتشابكة، reducer pure `state + action -> new state/effect request` يساعد تعمل table واختبارات exhaustive ويمنع `isPaid && isLoading`. لكن reducer وحده ما ينفّذش network ولا يضمن exactly-once: effects تروح repository، status authoritative من server، وrequest ID محفوظ لاسترجاع process death.

## Practical walkthrough

Payment state machine كثيرة transitions: MVVM يمكنها immutable state وأحداث واضحة، وMVI reducer يجعل transition table صريحة؛ الاسم لا يضمن safety. Decision يعتمد على complexity/testability/team familiarity. مهما اخترت، operation ID وUnknown وreconciliation durable في repository/backend، وليس داخل ViewModel فقط. اختبر duplicate tap، late callback، process death، وinvalid transition.

## Why it matters and how it works

MVVM is a state-holder arrangement; MVI often adds explicit intents and reducers. Both can follow UDF. A complex state machine benefits from explicit transitions, but implementation ceremony must be justified.

## Worked example

Transition sketch: `Idle + Submit -> Validating`; valid input -> `Submitting(requestId)`; timeout -> `PendingVerification(requestId)`; server status -> `Confirmed(receipt)` or `Declined(code)`. Reducer can be a pure function for local transitions; repository performs I/O and emits authoritative result.

This pure Kotlin reducer makes one critical rule visible: an ambiguous timeout remains `Unknown`, and a repeated tap does not create a fresh attempt. A real app persists the operation ID before send and reconciles against the backend.

```kotlin
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

sealed interface PaymentState {
    data class Processing(val operationId: String) : PaymentState
    data class Unknown(val operationId: String) : PaymentState
    data class Approved(val operationId: String) : PaymentState
}
sealed interface PaymentEvent {
    data object TimedOut : PaymentEvent
    data object PayTapped : PaymentEvent
    data object Confirmed : PaymentEvent
}

private fun reduce(state: PaymentState, event: PaymentEvent): PaymentState =
    when (state) {
        is PaymentState.Processing -> when (event) {
            PaymentEvent.TimedOut -> PaymentState.Unknown(state.operationId)
            PaymentEvent.Confirmed -> PaymentState.Approved(state.operationId)
            PaymentEvent.PayTapped -> state
        }
        is PaymentState.Unknown -> when (event) {
            PaymentEvent.Confirmed -> PaymentState.Approved(state.operationId)
            else -> state
        }
        is PaymentState.Approved -> state
    }

class PaymentReducerExampleTest {
    @Test fun timeoutKeepsIdentityAndBlocksNewTap() {
        val unknown = reduce(PaymentState.Processing("op-1"), PaymentEvent.TimedOut)
        assertEquals(PaymentState.Unknown("op-1"), unknown)
        assertEquals(unknown, reduce(unknown, PaymentEvent.PayTapped))
        assertEquals(PaymentState.Approved("op-1"), reduce(unknown, PaymentEvent.Confirmed))
    }
}
```

## Trade-offs and decision criteria

MVVM with a small set of immutable states is simpler. MVI/reducer approach improves auditability for many transitions but adds actions, effect handling and boilerplate. Hybrid MVVM plus an explicit reducer can be pragmatic.

## Failure modes

A ViewModel sets `success=true` after timeout and enables another payment request. Server may have accepted the first. Persist request key and reconcile before retry. Another failure is reducer emitting a network effect twice after replay; effect execution needs idempotency policy.

## Production perspective

A checkout team keeps ViewModel as Android owner, reducer for pure transition logic, and repository for durable request/status. Tests cover duplicate taps, timeout, rotation, process death, and late server confirmation.

## Interview answer — short

For simple payment UI, MVVM with immutable state can suffice. For many transitions, a reducer-style MVI approach makes state changes explicit and testable. Neither replaces server authority or durable reconciliation.

## Interview answer — structured

I would map the states and transitions before choosing a label. If there are a few clear states, a ViewModel that exposes one immutable state is enough. If many actions can arrive during submitting, retrying and verification, a reducer can make legal transitions explicit and unit-testable. MVVM and MVI can both follow UDF. The payment result must still come from a repository and server, with request IDs persisted for uncertain outcomes and process-death recovery. A reducer can make a transition table visible: `Submitting + Timeout -> PendingVerification`, never immediately `Failed`. I would use that rigor where the number of events makes ad hoc ViewModel branches hard to audit. For a small flow, immutable MVVM state may be simpler.

## Interview answer — deep senior

The senior trade-off is complexity versus auditability. A giant ViewModel with several booleans invites invalid combinations and unclear transition ordering; a pure reducer can make `state + action` behavior explicit and test every edge. But a full MVI framework may add unnecessary action/effect plumbing to a simple flow. I might use a ViewModel as lifecycle owner and a small reducer as an internal state machine. Effects are executed by a repository, not by the reducer, and duplicate effect execution needs an idempotency and acknowledgement strategy. A timeout is `PendingVerification`, not confirmed failure, because server commit may have happened. Persist request identifiers and restore from server-backed state after process death. Tests exercise rapid taps, cancellation, retry, and late confirmation. I also separate pure transition calculation from effects. The reducer should not secretly call a provider SDK; it can describe a request while a repository performs it with a persisted ID. If an effect is replayed after rotation or process death, server-side idempotency and reconciliation must prevent duplicate business effects. I test rapid double taps, late responses, cancellation and restored pending state. The choice between MVVM and MVI is secondary to a correct state machine and server authority.

## How to answer in the interview

- **Why:** financial transitions require explicit rules.
- **How:** compare reducer and VM by state semantics.
- **Trade-off:** ceremony versus auditability.
- **Failure case:** UI pattern mistaken for ledger.
- **Production solution:** durable state machine and transition tests.

## Deep-dive talking points

Compare state complexity, reducer purity, effect execution, duplicate taps, timeout uncertainty and server reconciliation.

## Follow-up questions

- [ARC-08](../arc-08/): Can MVVM follow UDF? **Answer:** yes; MVI is not the only way to route events and state one way.
- [ARC-17](../arc-17/): What about one-time effects? **Answer:** define delivery/acknowledgement and derive durable outcomes from state.

## Self-check rubric

Draw four payment states and two invalid transitions; justify either MVVM or reducer-style MVI with recovery tests.

## References and reviewed-on date

- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — UDF and state holders.
- [Android UI events](https://developer.android.com/topic/architecture/ui-layer/events) — state-driven event handling.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
