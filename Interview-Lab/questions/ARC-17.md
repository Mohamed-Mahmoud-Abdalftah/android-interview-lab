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

كيف تدير أحداث المرة الواحدة (One-Time Effects) مثل الـ Snackbars، الـ Toasts، وأحداث التنقل في معمارية UDF؟

1. معضلة أحداث المرة الواحدة في UDF:
   - في المعمارية أحادية الاتجاه (UDF)، الواجهة عبارة عن مراقب لحالة مستمرة (`StateFlow<UiState>`).
   - الأحداث العابرة (مثل إظهار رسالة خطأ سريعة Snackbar أو التنقل لشاشة أخرى عند نجاح الدفع) ليست حالات مستمرة؛ بل هي أحداث يجب أن تستهلك **مرة واحدة فقط (Fire-and-Forget)**.
   - إذا وضعت حدثاً كـ Boolean في الـ State (مثل `showError = true`) دون تصفيره، فعند تدوير الشاشة (Configuration Change) يعاد استهلاك الحدث ويظهر الـ Snackbar مرة أخرى للمستخدم بدون داعٍ!

2. الطريقة الحديثة الرسمية الموصى بها (State-Based Event Consumption):
   - تمثيل الحدث ككائن قابل للاستهلاك في الـ State: `val userMessage: UserMessage? = null`.
   - عندما تقرأه الواجهة، تعرض الـ Snackbar فوراً، ثم ترسل حدثاً للـ ViewModel: `onMessageDismissed(messageId)` لتصفيره إلى `null`.
   - الميزة: استعادة تامة وموثوقة للحالة حتى مع موت العملية (Process Death).

3. بديل الـ Channels الموجهة للـ UI:
   - استخدام `Channel<UiEffect>(Channel.BUFFERED)` والتحويل إلى `receiveAsFlow()`.
   - يتم استقبالها في Compose عبر `LaunchedEffect`.
   - تنبيه: يجب جمع الـ Channel عبر دورة حياة آمنة (`repeatOnLifecycle`) لمنع فقدان الأحداث أثناء وجود التطبيق في الخلفية.

## Practical walkthrough

تنفيذ أحداث المرة الواحدة باستخدام نمط الرسائل القابلة للاستهلاك ونمط الـ Channel:
```kotlin
// النمط الرسمي الموصى به: State-Based مع تصفير الحدث بعد استهلاكه:
data class PaymentUiState(
    val isProcessing: Boolean = false,
    val pendingMessage: String? = null // يمثل حدث المرة الواحدة كـ State
)

@Composable
fun PaymentScreen(
    viewModel: PaymentViewModel,
    snackbarHostState: SnackbarHostState = remember { SnackbarHostState() }
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    // مراقبة الرسالة؛ عرضها ثم إبلاغ الـ ViewModel بتصفيرها فوراً:
    LaunchedEffect(state.pendingMessage) {
        state.pendingMessage?.let { msg ->
            snackbarHostState.showSnackbar(msg)
            viewModel.onMessageShown() // تصفير لمنع تكرار العرض عند تدوير الشاشة!
        }
    }

    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) {
        PaymentContent(state)
    }
}
```

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

Manage one-time effects either by modeling them as consumable state in `UiState` and clearing them via an `onDismissed()` callback immediately after display (Google's official recommendation), or via a buffered `Channel<UiEffect>` collected with `LaunchedEffect` and `repeatOnLifecycle`.

## Interview answer — structured

Managing one-time transient events (Snackbars, toasts, navigation triggers) in Unidirectional Data Flow requires balancing state immutability with single-consumption guarantees.

First, **The Consumable State Pattern (Official Google Recommendation)**. Next, model the one-off event directly inside the `UiState`: `userMessage: UserMessage?`.
In Compose, a `LaunchedEffect(state.userMessage)` triggers when non-null, displays the Snackbar via `snackbarHostState.showSnackbar(message)`, and immediately invokes a callback `viewModel.onMessageShown(id)` to clear the state back to `null`. *Advantage*: Guarantees state restoration across process death via `SavedStateHandle` without event dropping or phantom repeats.
**The Buffered Channel Pattern (Side-Effect Stream)**. In the ViewModel, declare `private val _effectChannel = Channel<UiEffect>(Channel.BUFFERED)` exposed as `val effects = _effectChannel.receiveAsFlow()`.
In Compose, collect effects inside `LaunchedEffect(Unit)`. *Advantage*: Zero boilerplate callback required to clear state; strictly delivers events sequentially.
Finally, *Caution*: Must be collected with lifecycle awareness (`flowWithLifecycle` or `repeatOnLifecycle`) so events emitted while in the background are buffered rather than dropped.


## Interview answer — deep senior

Why did the classic `SharedFlow(replay = 0)` fail for single-shot events? `SharedFlow` with zero replay acts as a hot broadcast. If an event is emitted while the UI is executing an orientation change or navigation transition, no collector is actively subscribed. The event is silently dropped into the void, and the user never sees the Snackbar or confirmation alert!

A `Channel(Channel.BUFFERED)` solves this by maintaining an internal queue. If the UI is temporarily unsubscribed during screen rotation, the channel buffers the event until the new Activity/Composable subscribes, delivering it reliably without loss.

For user-driven navigation, remember that not all navigation is a ViewModel effect: clicking an item to open details should directly invoke `navController.navigate()` from the UI callback, avoiding roundtrips through the ViewModel.


## How to answer in the interview

- **Why:** effects need delivery semantics.
- **How:** separate durable state from transient command.
- **Trade-off:** replay safety versus missed event.
- **Failure case:** payment success event lost on recreation.
- **Production solution:** model domain outcome durably and acknowledge UI effects.

## Deep-dive talking points

Compare state acknowledgement with Channel and SharedFlow semantics during stop, rotation and process death.

## Follow-up questions

- **Interviewer:** "Why is `SharedFlow(replay = 0)` problematic for one-time events?"
  **Answer:** "It drops emissions if there are no active subscribers at the exact millisecond of emission, causing lost navigation or toast events during configuration changes or background transitions."

- **Interviewer:** "Can `Channel.receiveAsFlow()` be collected by multiple collectors?"
  **Answer:** "No. Channels are unicast by default; emissions are consumed by whichever collector retrieves them first, which is ideal for single-screen UI effects."

## Self-check rubric

Describe how navigation occurs once after signup across rotation and why an in-memory effect is not a durable queue.

## References and reviewed-on date

- [Android UI events](https://developer.android.com/topic/architecture/ui-layer/events) — state-driven ViewModel events.
- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — UDF.

Technically reviewed against primary documentation on 2026-10-13.
