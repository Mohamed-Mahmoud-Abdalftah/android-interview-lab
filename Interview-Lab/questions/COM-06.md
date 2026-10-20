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

## Concept and technical explanation

Unidirectional Data Flow (UDF) gives a UI feature a clear owner: current state flows from that owner to consumers, and user actions flow back as events. The owner applies business rules or starts work, then emits updated state. A child may still own isolated visual state when appropriate; UDF does not require one global ViewModel or a sealed event for every click. It makes transitions easier to trace but does not guarantee zero races, no duplicate requests or automatic skip performance. One-time effects such as navigation require an explicit delivery or acknowledgment policy.

## Practical walkthrough (English)

Implementing pure Unidirectional Data Flow (UDF) in a Jetpack Compose screen:
```kotlin
// 1. Immutable State representation (Flows DOWN)
data class TaskUiState(
    val title: String = "",
    val isCompleted: Boolean = false,
    val isSubmitting: Boolean = false
)

// 2. Sealed Interface for Events (Flows UP)
sealed interface TaskUiEvent {
    data class TitleChanged(val newTitle: String) : TaskUiEvent
    data object ToggleCompletion : TaskUiEvent
    data object SubmitTask : TaskUiEvent
}

// 3. Stateless Composable adhering to UDF: State DOWN, Events UP
@Composable
fun TaskScreenContent(
    state: TaskUiState, // State flows DOWN
    onEvent: (TaskUiEvent) -> Unit, // Events flow UP
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.padding(16.dp)) {
        TextField(
            value = state.title,
            onValueChange = { onEvent(TaskUiEvent.TitleChanged(it)) }
        )
        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(
                checked = state.isCompleted,
                onCheckedChange = { onEvent(TaskUiEvent.ToggleCompletion) }
            )
            Text("Mark as completed")
        }
        Button(
            onClick = { onEvent(TaskUiEvent.SubmitTask) },
            enabled = !state.isSubmitting
        ) {
            Text("Save Task")
        }
    }
}
```

## Explanation in Arabic

UDF معناها إنك تقدر تتبع رحلة التغيير: المالك يبعث **State** للمكوّنات، والمكوّن يبعت **Event** لما المستخدم يعمل حاجة، والمالك يقرر التغيير ويرجع State جديدة. مثلاً زرار الدفع يبعت `PayClicked`، الـ ViewModel يمنع الطلب المكرر ويتعامل مع الـ repository، وبعدها يبعت `Submitting` أو `Success` أو `Error`.

النمط ده يساعدك تعرف مين صاحب القرار ومين بيعرض النتيجة، بس مش سحر: ممكن يبقى عندك race في طلبين شبكة، أو Snackbar تضيع لو مفيش collector، أو Navigation تتكرر لو event اتبعتت تاني بعد التدوير. لازم تحدد سياسة التسليم، والأفعال المهمة زي الدفع تحتاج idempotency على السيرفر كمان. الـ UDF لا يضمن إن كل composable تتخطى ولا إن كل Bug يختفي.

مش لازم كل click يبقى `sealed interface`؛ callback واضح ممكن يبقى أبسط لشاشة صغيرة. وممكن عنصر يحتفظ بحالة UI محلية، زي فتح tooltip، طالما مفيش مصدر تاني بيملك نفس القيمة. اختبر انتقال `Event → state` باختبار وحدة للـ state holder، واختبر تفاعل Compose نفسه باستخدام Compose UI tests لما يكون السلوك البصري هو محل الاختبار.

## Practical walkthrough

مثال على حدث الدفع مع منع ضغطتين متتاليتين في طبقة المالك:
```kotlin
data class PayUiState(val submitting: Boolean = false, val error: String? = null)

@Composable
fun PayContent(state: PayUiState, onPay: () -> Unit) {
    Column {
        Button(onClick = onPay, enabled = !state.submitting) { Text("Pay") }
        state.error?.let { Text(it) }
    }
}
// ViewModel.onPay(): لو فيه طلب جارٍ ارفض الحدث المكرر، ثم حدّث State.
// الطلب نفسه يحتاج idempotency key على السيرفر لو الدفع حساس.
```

اختبر انتقالات `Ready → Submitting → Success/Error`، وحدد إزاي هتتعامل مع Navigation وSnackbar عند توقف الشاشة أو إعادة إنشائها.

## Why it matters and how it works

UDF makes the rendering function a consumer of state and producer of user intents. A state holder serializes or coordinates changes and exposes a coherent snapshot, commonly as `StateFlow`. Side effects occur in the owner or a composition-aware effect rather than during rendering. This helps distinguish durable screen state from one-time UI actions whose delivery needs lifecycle consideration.

## Worked example

`CheckoutScreen(uiState, onAction)` renders `Loading`, `Ready`, or `Error`; tapping Pay sends `CheckoutAction.Pay`. The ViewModel disables payment while an idempotent request is in flight, records the result, and emits a new state. Navigation to a receipt occurs after authoritative result, with a consumed action or destination state designed to avoid double navigation.

### Compose/Kotlin walkthrough

```kotlin
sealed interface CheckoutUiState {
    data object Ready : CheckoutUiState
    data object Submitting : CheckoutUiState
    data class Failed(val message: String) : CheckoutUiState
}
@Composable
fun CheckoutScreen(state: CheckoutUiState, onPay: () -> Unit) {
    when (state) {
        CheckoutUiState.Ready -> Button(onClick = onPay) { Text("Pay") }
        CheckoutUiState.Submitting -> CircularProgressIndicator()
        is CheckoutUiState.Failed -> Text(state.message)
    }
}
```

## Trade-offs and decision criteria

A single large state model gives coherent updates but may widen observation and copy cost. Smaller state holders can be appropriate if ownership remains explicit. A channel for ephemeral events is simple but can lose events while no collector exists; representing a destination as state can replay unless it is acknowledged. Match delivery semantics to the event.

## Failure modes

The composable directly calls a repository and repeats work on recomposition. Two sources of truth disagree about whether Pay is enabled. A navigation event replays after rotation, or a Snackbar is dropped while the screen is stopped. A mutable collection changes without emitting new observable state.

## Production perspective

Define a typed action contract, model loading/error/success explicitly, and test event-to-state transitions and lifecycle collection. Record duplicate-tap and restoration behavior for high-value flows; server idempotency remains necessary beyond UI disabling.

## Interview answer — short

UDF sends state from an owner down to UI and sends user actions back as events. The owner processes an action and emits new state. This makes ownership and transitions easier to test, but delivery of navigation or Snackbar effects and duplicate requests still need explicit handling.

## Interview answer — structured

In a Compose feature, UDF means the UI consumes a state value and reports user intent through callbacks. A screen state holder owns decisions and exposes a new value after handling an event. For a payment button, the UI renders `Ready`, sends `Pay`, shows `Submitting`, then renders the result. The callback is an event boundary; a repository call does not belong in the composable body. A small local visual state can remain local if no other consumer needs it. A single screen model can simplify coherence, but a large model can widen the work needed per update. UDF is an ownership pattern, not a guarantee of no races, no loops or automatic skipping. Navigation and Snackbar delivery require a policy for stopped collectors and recreation; a payment request additionally needs duplicate protection and server idempotency. Test the state holder's event-to-state transition separately from the actual UI click behavior.

## Interview answer — deep senior

The useful invariant in UDF is that each piece of meaningful state has an owner. Children display an immutable view of it and emit intents. The owner validates an intent, coordinates asynchronous work and publishes a coherent state update. For a checkout flow, `PayClicked` should first move the screen into a submitting state, reject duplicate UI actions and use a server idempotency key because disabling a button cannot protect against retries or network races. On success, the owner can represent a receipt destination in durable screen state or deliver a navigation effect with explicit acknowledgment semantics.

One-time effects are where simplistic UDF examples fail. A hot event stream with no active collector can drop a Snackbar while the screen is stopped; a replaying stream can navigate twice after rotation. The delivery choice depends on whether the event must survive recreation and whether it can safely repeat. Treat navigation to a completed purchase differently from a decorative toast. Similarly, UDF does not imply that every child is stateless. A local expansion flag can be private to a component, while a cart total used by several consumers belongs at their common owner.

Compose can use observable state and compiler skipping to avoid some work, but UDF itself does not guarantee a skip: stability, current compiler configuration and where state is read still matter. A large `UiState` passed everywhere may increase invalidated work. Profile the actual interaction before splitting the state. Unit tests can verify a plain state holder or ViewModel reducer on the JVM; verifying Compose rendering and click callbacks generally needs Compose UI test infrastructure. The architecture improves traceability when the contracts are explicit, while concurrency and lifecycle correctness still require separate tests.

## How to answer in the interview

- **Why:** state and intents make transitions auditable.
- **How:** walk through Pay, repository result, and a new immutable state.
- **Trade-off:** one-time navigation needs an explicit delivery contract.
- **Failure case:** duplicate mutable state in UI and owner.
- **Production solution:** test transitions and acknowledge consumed actions.

## Deep-dive talking points

Discuss state ownership, typed actions, reducer-like transitions, effects, lifecycle event delivery, and idempotency.

## Follow-up questions

- **Interviewer:** "Does UDF prevent every recomposition loop?"
  **Answer:** "No. Clear ownership reduces accidental feedback, but an owner can still emit a new state in response to every render-triggered effect. I keep events tied to user actions or correctly keyed effects and test transitions."
- **Interviewer:** "Can a screen have local state too?"
  **Answer:** "Yes. Isolated visual state may stay in a composable. Shared business state goes to a suitable common owner, with explicit event and restoration contracts."

## Self-check rubric

Trace one event to a state transition, name the owner, and explain one-shot delivery and duplicate protection.

## References and reviewed-on date

- [Compose UI architecture](https://developer.android.com/develop/ui/compose/architecture) — UDF and state/events.
- [UI layer guidance](https://developer.android.com/topic/architecture/ui-layer) — state holders and UI events.

Technically reviewed against primary documentation on 2026-10-19.
