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

كيف يستبدل نمط آلة الحالة الصريحة (Explicit State Machine) المتغيرات المنطقية المتفرقة (Scattered Boolean Flags)؟

1. كارثة الـ Boolean Flags المتعددة:
   - عندما تحتوي شاشة الطلبات أو الدفع على: `var isLoading = false` و `var isSuccess = false` و `var hasError = false` و `var isRetrying = false`.
   - المشكلة الرياضية: مع 4 أعلام Boolean، لديك $2^4 = 16$ حالة ممكنة في الذاكرة!
   - حالات غير قانونية (Illegal States): يمكن أن يصبح `isLoading = true` و `isSuccess = true` و `hasError = true` في نفس اللحظة بسبب Race Condition أو خطأ استدعاء، مما يؤدي إلى شاشة تعرض مؤشر التحميل وزر الخطأ ونجاح الدفع معاً!

2. الحل بـ State Machine و Sealed Interfaces:
   - حصر الحالات الممكنة في حالات منطقية قانونية فقط (`Idle`, `Loading`, `Success`, `Error`).
   - من المستحيل فيزيائياً أن يكون التطبيق في أكثر من حالة واحدة في نفس اللحظة.
   - حصر الأحداث (Events) التي تحرك الانتقالات بين الحالات (Transitions)، بحيث لا يمكن الانتقال من `Success` إلى `Loading` دون حدث صريح ومسموح.
   - الاستفادة من ميزة الـ Exhaustive `when` في Kotlin التي تجبر المترجم على التحقق من تغطية جميع الحالات، مما يمنع الأخطاء في وقت التشغيل (Compile-time safety).

## Practical walkthrough

المقارنة بين المتغيرات المنطقية المتفرقة وآلة الحالة المحكمة:
```kotlin
// ❌ فوضى الـ Scattered Booleans: احتمالية ظهور حالات مستحيلة وغير قانونية:
class BadCheckoutViewModel : ViewModel() {
    var isLoading = false
    var isPaid = false
    var hasError = false
    
    fun pay() {
        isLoading = true
        // لو حصل Exception وسقط الكود، قد يظل isLoading = true مع hasError = true!
    }
}

// ✅ آلة حالة صريحة (Explicit State Machine) باستخدام Sealed Interfaces:
sealed interface CheckoutState {
    object Idle : CheckoutState
    data class Submitting(val orderId: String) : CheckoutState
    data class Confirmed(val transactionId: String, val receiptUrl: String) : CheckoutState
    data class Failed(val errorReason: String, val canRetry: Boolean) : CheckoutState
}

sealed interface CheckoutEvent {
    data class SubmitClicked(val orderId: String) : CheckoutEvent
    data class PaymentSucceeded(val txId: String, val receipt: String) : CheckoutEvent
    data class PaymentFailed(val reason: String, val canRetry: Boolean) : CheckoutEvent
    object RetryClicked : CheckoutEvent
}

// Reducer نقي يحسب الحالة التالية بناءً على الحالة الحالية والحدث:
fun checkoutReducer(current: CheckoutState, event: CheckoutEvent): CheckoutState = when (current) {
    is CheckoutState.Idle -> when (event) {
        is CheckoutEvent.SubmitClicked -> CheckoutState.Submitting(event.orderId)
        else -> current // تجاهل الأحداث غير القانونية في هذه الحالة
    }
    is CheckoutState.Submitting -> when (event) {
        is CheckoutEvent.PaymentSucceeded -> CheckoutState.Confirmed(event.txId, event.receipt)
        is CheckoutEvent.PaymentFailed -> CheckoutState.Failed(event.reason, event.canRetry)
        else -> current
    }
    is CheckoutState.Failed -> when (event) {
        CheckoutEvent.RetryClicked if current.canRetry -> CheckoutState.Submitting("retry_order")
        else -> current
    }
    is CheckoutState.Confirmed -> current // حالة نهائية، لا تقبل أي انتقالات
}
```

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

## Trade-offs and decision criteria

A sealed hierarchy/reducer adds code. For two simple flags that are genuinely orthogonal, a data class can be clearer. Model actual legal combinations rather than forcing mutually exclusive cases when cached content and refresh error can coexist.

## Failure modes

An HTTP timeout sets `isPaid=false` and `canRetry=true`, but server accepted payment. A second submit can duplicate the effect. Keep pending status and reconcile with server using request ID/idempotency rules.

## Production perspective

A subscription checkout persists pending request IDs and restores state after process death. Tests exhaust legal transitions, late confirmations, duplicate taps and callback order.

## Interview answer — short

Scattered booleans create $2^N$ combinatorial states, allowing impossible illegal states like showing a loading spinner and an error banner simultaneously. An explicit state machine uses Kotlin sealed interfaces to model only valid domain states, explicit input events, and deterministic state transitions via a pure reducer, making illegal states unrepresentable at compile time.

## Interview answer — structured

Scattered boolean flags are one of the biggest sources of UI glitches in Android apps. When a ViewModel tracks `isLoading`, `isError`, and `isPaid` independently, you create $2^N$ possible combinations. It becomes trivially easy for asynchronous race conditions to leave the app in an impossible state where the screen is loading, displaying an error, and showing a success modal simultaneously.

An explicit State Machine solves this by making illegal states unrepresentable:
1. **Sealed State Hierarchy**: We model states as a closed hierarchy (`Idle`, `Submitting`, `Confirmed`, `Failed`). The UI renders exactly one state at any point in time.
2. **Explicit Events & Transitions**: State changes can only happen in response to registered domain events through a state reducer or transition table. If a user double-taps 'Pay', the reducer receives a second click event while already in the `Submitting` state and cleanly ignores it.
3. **Exhaustive Verification**: Kotlin's compiler forces the UI layer (`when (state)`) to handle every legal state, ensuring zero overlooked edge cases.

## Interview answer — deep senior

From a formal systems perspective, migrating to a Finite State Machine (FSM) elevates your architecture from ad-hoc procedural code to a deterministic mathematical model.

In production Android, we enforce three architectural guardrails when designing state machines:
1. **Single Source of Truth & Pure Reducers**: The transition logic `(State, Event) -> State` should be a pure function free of side effects. Side effects (network calls, database writes, analytics tracking) are emitted as separate side-effect commands or effects, ensuring the state machine itself is testable in pure JVM unit tests without mocking coroutines.
2. **State Machines across Process Death**: A common trap is keeping the state machine purely in memory. For critical transactions like payments, the state must be backed by durable persistence (Room or DataStore) using an idempotency key. If Android OS kills the process during `Submitting`, upon recreation the state machine resumes from `PendingReconciliation`, checking the server status rather than resetting to `Idle` or charging the user twice.
3. **Hierarchical State Machines (Statecharts)**: For deeply nested flows (like a multi-step checkout with address selection, payment method, and 3DS verification), nested sealed interfaces represent composite states cleanly without inflating the top-level machine.

## How to answer in the interview

- **Why:** Boolean flags admit impossible UI combinations.
- **How:** Define payload-bearing states plus a reducer transition table.
- **Trade-off:** State machine adds structure but makes complex flows reviewable.
- **Failure case:** Timeout marked failed or late callback overwrites terminal state.
- **Production solution:** Persist attempt ID and test every transition/crash path.

## Deep-dive talking points

Enumerate Boolean combinations, legal state transitions, effect ownership and server reconciliation.

## Follow-up questions

- **Interviewer:** "How do you handle asynchronous side-effects inside a pure reducer?"
  **Answer:** "Reducers must remain pure. Side effects are triggered by emitting one-off SideEffect objects or launching dedicated effect handlers in response to state transitions outside the reducer."

- **Interviewer:** "What prevents double-clicks from causing race conditions in a state machine?"
  **Answer:** "In the Submitting state, incoming Click events are not mapped to any transition and are simply discarded by the reducer."

## Self-check rubric

List five legal states, reject two impossible Boolean combinations, and test timeout plus duplicate tap.

## References and reviewed-on date

- [Kotlin sealed hierarchies](https://kotlinlang.org/docs/sealed-classes.html) — exhaustive state modeling.
- [Android UI state guidance](https://developer.android.com/topic/architecture/ui-layer/stateholders) — state-holder role.

Technically reviewed against primary documentation on 2026-10-13.
