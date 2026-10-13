---
id: "COM-10"
question: "What are LaunchedEffect, DisposableEffect, SideEffect, and rememberCoroutineScope?"
topic: "Jetpack Compose"
code: "COM"
group: "A"
phase: 3
priority: "P1"
order: 239
editorial_status: "reviewed"
---

# COM-10

## Original interview question

What are LaunchedEffect, DisposableEffect, SideEffect, and rememberCoroutineScope?

## What the interviewer evaluates

- Match each API to coroutine lifetime, cleanup, publication, or event-triggered launch.
- Explain key changes and composition exit.
- Avoid effects that duplicate work on recomposition.

## Explanation in Arabic

ما هي تأثيرات الجوانب (Side Effects) في Compose؟ والمقارنة بين `LaunchedEffect` و `DisposableEffect` و `SideEffect` و `rememberCoroutineScope`:

1. ما هو الـ Side Effect في Compose؟
   - هو أي عملية تغير حالة خارج نطاق دالة الـ Composable، أو تتفاعل مع العالم الخارجي (مثل استدعاء كود غير Composable، أو تسجيل أحداث، أو بدء Coroutine، أو الاشتراك في BroadcastReceiver).
   - يجب ألا تعمل هذه العمليات أبداً داخل جسم الـ Composable مباشرة لأن Recomposition قد يحدث 60 مرة في الثانية أو يُلغى فجأة.

2. متى تستخدم كل أداة؟
   - **`LaunchedEffect(key)`**: لتشغيل كود غير متزامن (`suspend` function) مرتبط بدورة حياة الـ Composable. يبدأ عند دخول الـ Composition، ويُلغى تلقائياً عند مغادرتها أو عند تغير الـ `key`.
   - **`DisposableEffect(key)`**: للعمليات التي تتطلب تنظيفاً متماثلاً (Cleanup / Unregister) مثل تسجيل Listeners أو مراقبة Sensor أو مشغل فيديو. يفرض توفير دالة `onDispose { ... }` تُستدعى عند مغادرة الشاشة.
   - **`SideEffect { ... }`**: لنشر حالة من Compose إلى كود خارجي غير مرتبط بـ Compose بعد **كل نجاح Recomposition كامل** (مثل إبلاغ مكتبة تحليلات خارجية أو تحديث شريط حالة النظام).
   - **`rememberCoroutineScope()`**: للحصول على `CoroutineScope` مرتبط بـ Composition لإطلاق مهام معلقة استجابةً **لأحداث المستخدم (User Events)** مثل النقر على زر (`onClick { scope.launch { ... } }`).

## Practical walkthrough

أمثلة توضح متى وأين تستخدم كل أداة من أدوات الـ Side Effects الأربعة:
```kotlin
@Composable
fun MediaScreen(
    mediaId: String,
    onCompleted: () -> Unit
) {
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()

    // 1. LaunchedEffect: جلب بيانات أو مهمة suspend مرتبطة بالـ mediaId:
    LaunchedEffect(mediaId) {
        analytics.trackMediaOpened(mediaId)
    }

    // 2. DisposableEffect: اشتراك في خدمة خارجية يحتاج تنظيفاً إلزامياً:
    DisposableEffect(Unit) {
        val listener = ScreenWakeLock.acquire()
        onDispose {
            listener.release() // تنظيف فوري عند مغادرة الـ Composable
        }
    }

    // 3. SideEffect: مزامنة حالة داخلية مع كائن خارجي بعد كل Recomposition ناجح:
    SideEffect {
        externalTracker.lastRenderTimestamp = System.currentTimeMillis()
    }

    // 4. rememberCoroutineScope: إطلاق كوروتين في استجابة لحدث نقر المستخدم:
    Button(onClick = {
        coroutineScope.launch {
            snackbarHostState.showSnackbar("Media saved!")
            onCompleted()
        }
    }) {
        Text("Save")
    }
}
```

## Why it matters and how it works

Compose rendering can run repeatedly. Effects provide managed points to coordinate external work with composition lifecycle. A keyed LaunchedEffect coroutine is canceled and relaunched on key change; DisposableEffect pairs setup with cleanup; SideEffect runs after a successful composition application. A remembered scope is useful for work initiated by an event handler while its call site exists.

## Worked example

A screen loads details for `userId` with `LaunchedEffect(userId)` if the work truly belongs to composition; a ViewModel may own the fetch instead. An analytics listener uses `DisposableEffect(lifecycleOwner)` to add and remove its observer. `SideEffect` publishes the latest selected category to an analytics adapter, and a button click uses a remembered scope to show a Snackbar through its host state.

### Compose/Kotlin walkthrough

```kotlin
// Assumes a screen-owned SnackbarHostState and Material3 Scaffold.
@Composable
fun MessageScreen(host: SnackbarHostState = remember { SnackbarHostState() }) {
    val scope = rememberCoroutineScope()
    Scaffold(snackbarHost = { SnackbarHost(host) }) { padding ->
        Button(
            modifier = Modifier.padding(padding),
            onClick = { scope.launch { host.showSnackbar("Saved") } }
        ) { Text("Save") }
    }
}
// Imports: runtime.remember/rememberCoroutineScope, material3.*, layout.padding,
// kotlinx.coroutines.launch.
```

## Trade-offs and decision criteria

Effect APIs make lifecycle explicit but overuse scatters business logic into UI. ViewModel-owned requests survive the composition boundary when appropriate. An event callback is preferable to a composition-triggered effect for direct user actions. Correct keys are as important as choosing the API; too broad restarts work, too narrow retains stale captures.

## Failure modes

A listener is registered on every recomposition and leaks. `LaunchedEffect(Unit)` retains an old ID. `SideEffect` performs a network request after each recomposition. A remembered scope is stored in a Singleton and launched after its composition has ended.

## Production perspective

Review every effect for its start trigger, keys, cancellation/cleanup, and owner. Test key changes, screen departure, and callback replacement. Use lifecycle-aware producers outside Compose for durable work.

## Interview answer — short

`LaunchedEffect` runs suspending tasks scoped to composition lifecycles and cancels them on departure or key change. `DisposableEffect` is for non-suspending setup that requires cleanup via `onDispose`. `SideEffect` runs non-suspending code after every successful recomposition. `rememberCoroutineScope` provides a scope to launch coroutines from user callbacks like `onClick`.

## Interview answer — structured

Side-effect handlers bridge Compose's declarative, restartable runtime with imperative external systems.

1. **`LaunchedEffect(key1, ...)`**: Launches a coroutine in the composition scope upon entering the composition. If any key changes, the running coroutine is cancelled cooperatively and restarted. When leaving the composition, it is cancelled automatically. Used for async operations like fetching data or triggering animations.

2. **`DisposableEffect(key1, ...)`**: Designed for non-suspending side-effects that require **mandatory cleanup**. It executes when entering composition and mandates an `onDispose { ... }` block that runs when leaving composition or before re-running due to key changes. Used for registering broadcast receivers, sensor listeners, or lifecycle observers.

3. **`SideEffect`**: Executes its lambda after **every successful recomposition**. It is non-suspending and cannot be cancelled. Used to publish Compose state mutations to non-Compose external objects (such as updating an external tracking SDK or system properties).

4. **`rememberCoroutineScope()`**: Creates a `CoroutineScope` bound to the calling composable's lifecycle. It is used to launch coroutines outside the composition phase—specifically inside **user callbacks and event listeners** like `Button(onClick = { scope.launch { ... } })`.

## Interview answer — deep senior

A critical pitfall in Compose architecture is calling `rememberCoroutineScope().launch { ... }` directly within the body of a Composable function. Because composables can recompose many times per second, doing this launches dozens of duplicate unmanaged coroutines, thrashing the CPU and creating race conditions. Coroutines executed directly within the composition body must strictly use `LaunchedEffect`.

Under the hood, `LaunchedEffect` is implemented as a `DisposableEffect` that creates a `StandaloneCoroutine` under the hood. When the effect is disposed, its `Job.cancel()` is called immediately.

`rememberCoroutineScope()` retrieves the `compositionContinuation`'s CoroutineContext, attaching a `SupervisorJob`. When the composable leaves the Slot Table, the `SupervisorJob` cancels, ensuring no child coroutine leaks into the application background.

## How to answer in the interview

- **Why:** recomposition makes unmanaged side effects unsafe.
- **How:** map coroutine, listener, post-commit publication, and click to their effect APIs.
- **Trade-off:** UI lifetime may be shorter than business work.
- **Failure case:** missing cleanup or wrong key.
- **Production solution:** test entry, key change, exit, and repeated taps.

## Deep-dive talking points

Compare keyed cancellation, disposal, post-composition publication, event scopes, and ViewModel ownership.

## Follow-up questions

- **Interviewer:** "Can you use `LaunchedEffect` inside an `onClick` lambda?"
  **Answer:** "No. `LaunchedEffect` is a `@Composable` function and can only be invoked within a Composable scope. For callbacks like `onClick`, you use a scope obtained via `rememberCoroutineScope()`."

- **Interviewer:** "What happens if an exception is thrown inside a `SideEffect` block?"
  **Answer:** "Because `SideEffect` executes synchronously during the commit phase of the composition pass, an unhandled exception will crash the composition process and propagate as an unhandled runtime exception."

## Self-check rubric

Map four use cases to APIs and name keys, cleanup, and duplicate-work risks.

## References and reviewed-on date

- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — effect contracts and keys.
- [Compose mental model](https://developer.android.com/develop/ui/compose/mental-model) — repeatable rendering.

Technically reviewed against primary documentation on 2026-10-13.
