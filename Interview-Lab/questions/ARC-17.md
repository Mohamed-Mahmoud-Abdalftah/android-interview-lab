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

## Concept and technical explanation

In Unidirectional Data Flow (UDF), UI state is continuous and persistent, representing what is currently rendered on screen. However, applications constantly produce transient, one-time side effects—such as displaying a Snackbar, showing a Toast, triggering haptic feedback, or executing navigation events. If one-time effects are improperly modeled as raw properties inside persistent StateFlow state, configuration changes (such as device rotation) cause the newly created UI subscriber to re-observe the state and replay the effect (triggering duplicate Snackbars or navigating twice). Architectural solutions include: (1) single-event buffered Kotlin Channels exposed as Flows and collected via LaunchedEffect with repeatOnLifecycle, or (2) modeling effects as consumable message objects inside the UI state with unique IDs, where the UI dispatches a consumption event back to the ViewModel immediately upon rendering.

## Practical walkthrough (English)

Managing one-time effects using a buffered Channel in Jetpack Compose:
```kotlin
// 1. Define transient side effects as a sealed interface
sealed interface CheckoutEffect {
    data class ShowToast(val message: String) : CheckoutEffect
    data class NavigateToReceipt(val orderId: String) : CheckoutEffect
}

// 2. ViewModel exposes buffered Channel as Flow
class CheckoutViewModel : ViewModel() {
    private val _effectChannel = Channel<CheckoutEffect>(Channel.BUFFERED)
    val effects: Flow<CheckoutEffect> = _effectChannel.receiveAsFlow()

    fun onPayClicked(orderId: String) {
        viewModelScope.launch {
            _effectChannel.send(CheckoutEffect.ShowToast("Payment successful!"))
            _effectChannel.send(CheckoutEffect.NavigateToReceipt(orderId))
        }
    }
}

// 3. Compose UI collects effect safely via LaunchedEffect
@Composable
fun CheckoutScreen(viewModel: CheckoutViewModel, onNavigate: (String) -> Unit) {
    val context = LocalContext.current
    LaunchedEffect(Unit) {
        viewModel.effects.collect { effect ->
            when (effect) {
                is CheckoutEffect.ShowToast -> Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
                is CheckoutEffect.NavigateToReceipt -> onNavigate(effect.orderId)
            }
        }
    }
}
```

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

Manage one-time effects using either a buffered Kotlin Channel exposed as a Flow for fire-and-forget events, or by modeling effects inside the UI state with unique identifiers that the UI marks as consumed. This prevents accidental event replay upon screen rotation or configuration changes.

## Interview answer — structured

Handling transient side effects like navigation or Snackbars requires preventing event replay during configuration changes.

Persistent UI state models what is currently visible, whereas one-time effects represent discrete, non-persistent events. If an effect is stored as a raw property in StateFlow, rotating the device will cause the newly attached Composable to re-read the state and re-trigger the navigation or Toast.

In production, we use a buffered Kotlin Channel exposed as a Flow via receiveAsFlow. The UI observes this stream inside a LaunchedEffect scoped to the screen lifecycle, ensuring each event is delivered and consumed exactly once.
As for alternative architectures, teams can model effects directly inside the UI state as a list of consumable message objects with unique IDs. Once the Composable renders the Snackbar, it dispatches an onMessageShown event back to the ViewModel to remove the consumed item from state.


## Interview answer — deep senior

Under the hood, the handling of one-time events has sparked significant debate in the Android community. Historically, developers used SingleLiveEvent or Event wrappers to prevent event replay on configuration changes. However, when migrating to coroutines and Flow, naive usage of SharedFlow can silently drop events if no collector is currently active—for example, if an event is emitted while the Activity is in the background or navigating between destinations.
Using a buffered Channel—configured as Channel(Channel.BUFFERED) and exposed via channel.receiveAsFlow—guarantees that events are buffered until an active collector subscribes. When the UI collects the flow using LaunchedEffect combined with repeatOnLifecycle(Lifecycle.State.STARTED), events emitted during background transitions remain in the buffer and are processed immediately when the UI resumes.
Conversely, Google's modern architectural guidance leans toward modeling events as part of UI state rather than separate side channels. In this approach, the UI state contains an optional property: data class CheckoutUiState containing userMessage. When the Composable displays the Snackbar, it invokes a callback like viewModel.onMessageDismissed, which resets userMessage to null.
Staff engineers choose the strategy based on team conventions: buffered Channels work exceptionally well for fire-and-forget imperative side effects like navigation actions and haptic triggers, while state-based message objects excel for user-visible notifications where state restoration and synchronization must remain completely predictable across process death.

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
