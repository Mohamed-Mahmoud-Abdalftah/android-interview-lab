---
id: "COM-13"
question: "How do you correctly implement Snackbar, navigation, and callbacks?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 242
editorial_status: "reviewed"
---

# COM-13

## Original interview question

How do you correctly implement Snackbar, navigation, and callbacks?

## What the interviewer evaluates

- Separate user actions, UI effects, and destination state.
- Explain Snackbar coroutine ownership and navigation idempotence.
- Handle lifecycle gaps and current callbacks.

## Explanation in Arabic

كيفية التعامل الصحيح مع أحداث المرة الواحدة (One-off Events) مثل الـ Snackbar والتنقل (Navigation) والـ Callbacks في Jetpack Compose:

1. معضلة أحداث المرة الواحدة (Single-Event Anti-Pattern):
   - في السابق، كان المطورون يضعون `SharedFlow` أو `Channel` أو `SingleLiveEvent` لإرسال حدث مثل `ShowToast` أو `NavigateToHome`.
   - المشكلة: الـ Channels قد تفقد الأحداث إذا حدث Configuration Change أثناء الإرسال، أو قد تعيد تنفيذ الحدث مرتين عند إعادة التدوير (Double Navigation)!

2. التوجيه الرسمي الحديث من Google (State-Based Events):
   - يجب تمثيل رسائل التنبيه والـ Snackbars **كجزء من الـ UI State نفسها**!
   - يتم وضع كائن مثل `userMessage: UserMessage?` داخل الـ `UiState`.
   - عندما يقرأ الـ Composable هذه الرسالة، يعرض الـ Snackbar، ثم يُرسل فورياً حدثاً للـ ViewModel يقول: `onMessageShown(messageId)` لتصفير القيمة إلى `null`.
   - هذا يضمن الحتمية التامة؛ فحتى لو تدوّرت الشاشة أو ماتت العملية، يُعرف بالضبط هل عُرضت الرسالة أم لا.

3. أحداث التنقل (Navigation Events):
   - التنقل استجابةً لضغط المستخدم المباشر يجب أن يتم في الـ UI Layer فوراً عبر Lambdas (`onClick = { onNavigateToDetails(itemId) }`).
   - إذا كان التنقل مشروطاً بنتيجة عملية في السيرفر (مثل تسجيل دخول ناجح)، يتم تمثيل حالة الوجهة في الـ ViewModel وعند الوصول لحالة النجاح يُستدعى التنقل ويُفرغ الحدث.

## Practical walkthrough

النمط القياسي لعرض الـ Snackbar كجزء من الحالة وتصفيره بعد العرض:
```kotlin
// 1. تمثيل الرسالة في الـ UiState:
data class EditProfileUiState(
    val isLoading: Boolean = false,
    val userMessage: String? = null // رسالة المرة الواحدة كـ State قابلة للإلغاء
)

// 2. معالجة الرسالة في Compose باستخدام LaunchedEffect وتصفيرها فوراً:
@Composable
fun EditProfileScreen(
    viewModel: EditProfileViewModel,
    snackbarHostState: SnackbarHostState = remember { SnackbarHostState() }
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // مراقبة userMessage؛ عند توفره يتم عرضه ثم إبلاغ الـ ViewModel بتصفيره:
    LaunchedEffect(uiState.userMessage) {
        uiState.userMessage?.let { message ->
            snackbarHostState.showSnackbar(message)
            viewModel.onUserMessageShown() // تصفير الرسالة لمنع تكرارها عند التدوير!
        }
    }

    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) {
        ProfileContent(uiState)
    }
}
```

## Why it matters and how it works

Recomposition can re-enter render code, so an imperative UI command must have a clear event trigger and owner. `SnackbarHostState` serializes visual messages through a suspending call. Navigation changes back stack state and should occur once for a particular transition, with `launchSingleTop` or state consumption as appropriate but not as a substitute for a correct event contract. Callback capture depends on effect keys and composition updates.

## Worked example

The user taps Save. The screen invokes `onSave`, the ViewModel submits once, and exposes `Saved(receiptId)` or a consumed navigation action. The route navigates to a receipt ID after observing the transition and marks it handled; if the save fails, it shows a Snackbar using the screen-owned host state. A repeated tap while saving is rejected in both UI and domain layers.

### Compose/Kotlin walkthrough

```kotlin
// Route-level example; ViewModel emits a unique, consumable UiEffect.
LaunchedEffect(viewModel, navController) {
    viewModel.effects.collect { effect ->
        when (effect) {
            is UiEffect.Saved -> navController.navigate("receipt/${Uri.encode(effect.id)}")
            is UiEffect.Error -> snackbarHostState.showSnackbar(effect.message)
        }
    }
}
// Screen: Button(onClick = onSave) { Text("Save") }
// UiEffect/effects are app contracts; import android.net.Uri.
// Define event delivery/acknowledgment for stopped lifecycle and restoration.
```

## Trade-offs and decision criteria

Keeping NavController at route level makes a reusable screen easier to preview and test. A one-off event stream is concise but needs buffering/lifecycle policy; destination state can survive recreation but needs consumption semantics. Snackbars are transient feedback, while durable errors should remain visible in UI state.

## Failure modes

`if (state.saved) nav.navigate(...)` in a composable body navigates repeatedly. A Channel event emitted while stopped is lost. A Snackbar callback uses a scope after the screen leaves. A lambda captured by a Unit-keyed effect points to an old owner.

## Production perspective

Test duplicate taps, rotation during saving, STOP/START delivery, and back navigation. Keep navigation routes typed or validated, and do not pass large sensitive payloads through route arguments.

## Interview answer — short

Model one-off UI events (like Snackbars) as consumable state properties inside the UI state, displaying them via `LaunchedEffect(userMessage)` and immediately calling an `onMessageDismissed()` event to clear the state. Navigation triggered by user input should be handled directly in the UI via callbacks, while business-driven navigation is driven by explicit state transitions.

## Interview answer — structured

Handling one-off events in Jetpack Compose requires transitioning away from legacy event-bus and channel antipatterns toward state-driven architectures.

First, with Snackbar and Transient Messages as State, rather than pushing side-effect events through `Channel` or `SharedFlow`, the modern official pattern models messages as state: `userMessage: UserMessage?` inside `ScreenUiState`. In Compose, a `LaunchedEffect(uiState.userMessage)` observes this field. When non-null, it invokes `snackbarHostState.showSnackbar(message)`, and immediately fires a callback `viewModel.onMessageShown(id)` to reset the state to `null`. This prevents missed messages or duplicate displays upon screen rotation. Next, with User-Driven Navigation, clicks and direct user navigation (e.g. Tapping an item) should be handled immediately in the UI layer through hoisted lambda callbacks (`onItemClick: (Id) -> Unit`), directly invoking the `NavController`.
Finally, with Business-Driven Navigation, when navigation depends on business outcomes (e.g. Successful authentication), the ViewModel emits a distinct terminal state (e.g. `AuthState.Authenticated`), which the UI observes to execute navigation.


## Interview answer — deep senior

Why did Google advise against using `Channel` or `SharedFlow` for one-off UI events in Compose? Channels buffer events imperatively. If an event is posted while the UI is transitioning lifecycles (e.g. During an Activity recreation or rotation), the collector may either drop the event or consume it before the new composition is ready, resulting in dropped Snackbars or phantom double navigations.

By embedding events in the immutable `UiState`, state restoration is guaranteed: if the screen dies and is recreated via `SavedStateHandle`, the pending message is preserved and displayed reliably.

For navigation specifically, to prevent rapid double-clicks from pushing two duplicate screens onto the backstack, we either guard navigations with a boolean gate or debounce click modifiers, and verify that the destination is not already the top destination on the NavController backstack.


## How to answer in the interview

- **Why:** imperative UI commands need a single trigger.
- **How:** separate button intent, authoritative result, and route action.
- **Trade-off:** a transient stream may miss events while stopped.
- **Failure case:** success state causes repeat navigation after recreation.
- **Production solution:** define consumption and restore-safe destination state.

## Deep-dive talking points

Discuss route/screen split, Snackbar suspension, event delivery, navigation replay, callback capture, and idempotency.

## Follow-up questions

- **Interviewer:** "What happens if a user rotates the screen while a Snackbar is currently being displayed?"
  **Answer:** "If modeled as state cleared only upon `showSnackbar()` completion, the recreated screen will simply re-display the active message. If cleared immediately before display, the rotation drops it gracefully without crashing."

- **Interviewer:** "How do you prevent rapid double-taps on navigation buttons in Compose?"
  **Answer:** "By using a single-click modifier that checks `SystemClock.elapsedRealtime()`, or checking that `navController.currentBackStackEntry?.destination?.route` matches the expected source route before navigating."

## Self-check rubric

Trace Save through callback, state, Snackbar or navigation; cover rotation and duplicate delivery.

## References and reviewed-on date

- [Compose Snackbar](https://developer.android.com/develop/ui/compose/components/snackbar) — host and suspending API.
- [Navigation in Compose](https://developer.android.com/develop/ui/compose/navigation) — route navigation practices.
- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — callbacks and effects.

Technically reviewed against primary documentation on 2026-10-13.
