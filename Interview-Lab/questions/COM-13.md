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

## Concept and technical explanation

Implementing Snackbar messages, navigation transitions, and event callbacks in Jetpack Compose requires a disciplined separation between persistent UI state and transient UI effects. Rather than relying on fragile single-shot channels or passing ambient navigation controllers down the UI hierarchy, modern Compose architecture treats one-off events as consumable state or hoisted lambda callbacks. Snackbars are orchestrated via a hoisted SnackbarHostState inside Scaffold and launched in a coroutine scope. Navigation is decoupled by hoisting navigation callbacks to top-level navigation graphs, keeping screen composables completely agnostic of NavController instances.

## Practical walkthrough (English)

Architectural implementation of Snackbar, navigation, and callbacks:
```kotlin
// 1. Screen Composable: Completely stateless, receives lambdas, NO NavController passed!
@Composable
fun ProductDetailContent(
    productName: String,
    onBackClick: () -> Unit,
    onShowMessage: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.padding(16.dp)) {
        IconButton(onClick = onBackClick) { Icon(Icons.Default.ArrowBack, "Back") }
        Text("Product: $productName", style = MaterialTheme.typography.headlineMedium)
        Button(onClick = { onShowMessage("Item added to cart!") }) {
            Text("Add to Cart")
        }
    }
}

// 2. Route Composable: Orchestrates Scaffold, SnackbarHostState, and Navigation
@Composable
fun ProductDetailRoute(
    productId: String,
    onNavigateBack: () -> Unit,
    viewModel: ProductViewModel = hiltViewModel()
) {
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        ProductDetailContent(
            productName = "Pixel 9 Pro",
            onBackClick = onNavigateBack,
            onShowMessage = { msg ->
                scope.launch {
                    snackbarHostState.currentSnackbarData?.dismiss() // Dismiss previous!
                    snackbarHostState.showSnackbar(msg)
                }
            },
            modifier = Modifier.padding(padding)
        )
    }
}
```

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

We implement Snackbars using a hoisted SnackbarHostState inside a Scaffold, triggering showSnackbar() within a rememberCoroutineScope or LaunchedEffect. For navigation and callbacks, we hoist lambda events to the navigation graph level instead of passing NavController into screen composables. This keeps screens stateless, enables seamless Compose Previews, and makes unit and screenshot testing trivial without mocking Android navigation classes.

## Interview answer — structured

Managing transient UI events like Snackbars and navigation transitions is a frequent architectural testing ground in Android interviews.
In legacy architectures, developers relied on SingleLiveEvent or Channel anti-patterns that frequently leaked events or dropped them during configuration changes.
Modern Jetpack Compose adheres to clean architectural decoupling.
For Snackbars, the standard pattern utilizes Scaffold and its dedicated snackbarHost parameter.
The screen creates a remembered SnackbarHostState.
When a user action triggers a message, a coroutine launched via rememberCoroutineScope or a state-driven LaunchedEffect invokes snackbarHostState.showSnackbar().
Calling dismiss() on currentSnackbarData before showing a new snackbar prevents stacking delayed message queues.
For navigation, a major industry rule is never passing NavHostController down into presenter composables.
Passing NavController tightly couples the UI to a specific navigation library, destroys Android Studio Previews, and prevents isolated UI testing.
Instead, screens expose explicit callback lambdas like onNavigateToDetails or onBackClick.
The outer navigation graph or route composable implements these lambdas, invoking navController.navigate() at the top boundary.

## Interview answer — deep senior

Under the hood, SnackbarHostState acts as an asynchronous state coordinator powered by Kotlin Coroutines Mutex locks.
When showSnackbar() is called, SnackbarHostState acquires an internal Mutex. If another snackbar is currently visible, the calling coroutine suspends until the existing snackbar dismisses, times out, or is explicitly cancelled via currentSnackbarData?.dismiss().
This built-in suspension mechanism guarantees thread-safe, serialized message presentation without requiring custom queue data structures.
When integrating with architecture ViewModels, transient events should be modeled either as consumable state properties inside an immutable UiState data class (cleared via an onEventConsumed callback once displayed) or emitted through a state-driven UI message queue.
Regarding navigation, decoupling NavController from leaf composables is critical for compiler skipping and multiplatform modularization.
NavController is a complex, mutable Android platform class that is marked unstable by the Compose compiler. Passing it down as a parameter immediately renders the child composable unskippable.
By replacing NavController with stable lambda function types (such as () -> Unit), the Compose compiler marks the parameter as stable, enabling zero-overhead smart skipping across the entire presenter layer.
Furthermore, this separation allows the same presenter screen to be reused across standard phone screens, navigation drawer panels, and adaptive foldable split-panes without altering a single line of presentation code.

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
