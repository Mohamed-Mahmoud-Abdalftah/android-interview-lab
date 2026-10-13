---
id: "PAT-14"
question: "How can an explicit state machine replace scattered boolean flags?"
topic: "Design Patterns"
code: "PAT"
group: "B"
phase: 2
priority: "P1"
order: 205
editorial_status: "reviewed"
---

# PAT-14

## Original interview question

How can an explicit state machine replace scattered boolean flags?

## What the interviewer evaluates

Replace combinatorial booleans with legal states and explicit transitions, including uncertain outcomes.

## Explanation in Arabic

لو عندك `isLoading`, `isPaid`, `hasError`, `canRetry` كـbooleans منفصلة، ممكن تظهر تركيبات مستحيلة مثل loading وpaid وerror معًا. State machine تحدد states قانونية (`Idle`, `Submitting(requestId)`, `PendingVerification(requestId)`, `Confirmed(receipt)`, `Rejected(code)`) وevents وانتقالات مسموحة. Kotlin sealed types تساعد `when` exhaustive، وpure reducer يسهل test كل transition. لكن UI state ما تصبحش مصدر truth للدفع؛ server status يحرك الانتقال النهائي، وrequest ID محفوظ لو process مات.

## Why it matters and how it works

Explicit states make invalid combinations harder to represent and transitions testable. They clarify which events are legal in each state and how uncertainty is recovered. They do not replace persistence or server authority.

## Worked example

Pure JVM reducer for a subset of transitions; the repository performs I/O and persists the attempt ID before submitting. The explicit duplicate-submit branch is intentional, while all other unsupported transitions are rejected for diagnosis.
```kotlin
sealed interface CheckoutState {
    data object Idle : CheckoutState
    data class Submitting(val attemptId: String) : CheckoutState
    data class PendingVerification(val attemptId: String) : CheckoutState
    data class Confirmed(val receiptId: String) : CheckoutState
}
sealed interface CheckoutEvent {
    data class Submit(val attemptId: String) : CheckoutEvent
    data object Timeout : CheckoutEvent
    data class ServerConfirmed(val receiptId: String) : CheckoutEvent
}
fun reduce(state: CheckoutState, event: CheckoutEvent): CheckoutState = when {
    state == CheckoutState.Idle && event is CheckoutEvent.Submit ->
        CheckoutState.Submitting(event.attemptId)
    state is CheckoutState.Submitting && event == CheckoutEvent.Timeout ->
        CheckoutState.PendingVerification(state.attemptId)
    state is CheckoutState.PendingVerification && event is CheckoutEvent.ServerConfirmed ->
        CheckoutState.Confirmed(event.receiptId)
    state is CheckoutState.Submitting && event is CheckoutEvent.Submit -> state
    else -> error("Illegal checkout transition: $state + $event")
}
```
Add provider rejection, cancellation and restored-state events according to the actual server contract. The sealed type constrains state shapes; this reducer defines transition legality.

## Practical walkthrough

checkout فيها `isLoading`, `hasFailed`, `isSuccess`, `needsCheck` booleans هتسمح بحالات مستحيلة زي success+loading. sealed state `Idle`, `Submitting(attemptId)`, `PendingVerification(attemptId)`, `Confirmed(receiptId)`, `Rejected(code)` يخلي payload مناسبة لكل حالة. reducer `reduce(state, event)` يرفض أو يتجاهل events غير legal بقرار صريح؛ sealed alone ما تفرضش transition. timeout بعد submit يروح PendingVerification مش Failed، ثم status query من server. state machine لازم تتسلسل مع persistence: attempt ID تنحفظ قبل side effect عشان process death تقدر تعيد البناء.

## Trade-offs and decision criteria

A sealed hierarchy/reducer adds code. For two simple flags that are genuinely orthogonal, a data class can be clearer. Model actual legal combinations rather than forcing mutually exclusive cases when cached content and refresh error can coexist.

## Failure modes

An HTTP timeout sets `isPaid=false` and `canRetry=true`, but server accepted payment. A second submit can duplicate the effect. Keep pending status and reconcile with server using request ID/idempotency rules.

## Production perspective

A subscription checkout persists pending request IDs and restores state after process death. Tests exhaust legal transitions, late confirmations, duplicate taps and callback order.

## Interview answer — short

An explicit state machine replaces scattered booleans with legal states and transitions, making impossible combinations and duplicate actions easier to prevent. For payments, uncertain outcomes stay pending until server confirmation.

## Interview answer — structured

I list the legal states first, then model each with required payloads. `Submitting` needs a request ID; `Confirmed` needs a receipt; `PendingVerification` represents timeout uncertainty. Events drive a reducer or explicit transition function, and invalid events such as a second Submit while Submitting do nothing or return a defined error. That is easier to test than several booleans with ambiguous combinations. The UI still derives final payment status from a server-backed repository, not from a local transition alone.

## Interview answer — deep senior

The problem with flags is combinatorial state space. Four Booleans allow sixteen combinations, many of which may be nonsensical. A sealed hierarchy makes the intended cases explicit, and a transition table says what each event means from each state. I keep the reducer pure, with effects executed by a repository, so tests can cover every legal and illegal transition. For an offline-first screen, some dimensions can coexist; I may use a data class inside a `Content` state rather than forcing false exclusivity. For payment, a timeout is not final failure. I persist the request identity, reconcile with the server, and restore pending state after process death. That preserves both UX and business correctness.

I replace multiple flags with a finite set of states and an explicit transition function. A checkout can be Idle, Submitting with an attempt ID, PendingVerification with the same ID, Confirmed with a receipt, or Rejected with a reason. That prevents combinations such as loading and success at once, but the sealed hierarchy alone does not validate history; the reducer must define what events are legal from each state. A lost response transitions to PendingVerification, not a definite failure. I persist the attempt identity before the external request, then reconstruct and query server status after process death. I test each transition and rejected event, including double-tap submit and a late callback after terminal state.

## How to answer in the interview

- **Why:** Boolean flags admit impossible UI combinations.
- **How:** Define payload-bearing states plus a reducer transition table.
- **Trade-off:** State machine adds structure but makes complex flows reviewable.
- **Failure case:** Timeout marked failed or late callback overwrites terminal state.
- **Production solution:** Persist attempt ID and test every transition/crash path.

## Deep-dive talking points

Enumerate Boolean combinations, legal state transitions, effect ownership and server reconciliation.

## Follow-up questions

- [PAT-09](../pat-09/): State versus Strategy? **Answer:** transitions depend on current state; provider algorithm choice is separate.
- [ARC-25](../arc-25/): When is reducer-style MVI valuable? **Answer:** many payment transitions need exhaustive tests.

## Self-check rubric

List five legal states, reject two impossible Boolean combinations, and test timeout plus duplicate tap.

## References and reviewed-on date

- [Kotlin sealed hierarchies](https://kotlinlang.org/docs/sealed-classes.html) — exhaustive state modeling.
- [Android UI state guidance](https://developer.android.com/topic/architecture/ui-layer/stateholders) — state-holder role.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
