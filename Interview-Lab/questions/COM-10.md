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

## Concept and technical explanation

Jetpack Compose provides four foundational effect handlers to execute imperative side-effects safely across the composition lifecycle. LaunchedEffect launches a lifecycle-aware coroutine scope bound to composition keys, canceling and restarting whenever keys change. DisposableEffect executes cleanup logic via onDispose when its keys change or when the composable leaves the composition, ideal for registering and unregistering external system observers or listeners. SideEffect executes a non-suspending side-effect on every successful recomposition pass, synchronizing Compose state with external objects not managed by Compose. rememberCoroutineScope creates a long-lived coroutine scope bound to the composition call site, enabling user-initiated event handlers (like button clicks) to launch coroutines outside composition phases.

## Practical walkthrough (English)

Applying the four effect handlers in an Android multimedia screen:
```kotlin
@Composable
fun VideoPlayerScreen(
    videoId: String,
    analytics: AnalyticsTracker,
    scaffoldState: SnackbarHostState
) {
    // 1. rememberCoroutineScope: Launch coroutine from user event callbacks (e.g. Button click)
    val coroutineScope = rememberCoroutineScope()

    // 2. LaunchedEffect: Suspending coroutine tied to a key; restarts if videoId changes
    LaunchedEffect(videoId) {
        analytics.trackScreenView("Video_$videoId")
        // Load initial video buffers asynchronously...
    }

    // 3. DisposableEffect: Lifecycle-bound side-effect with cleanup logic
    DisposableEffect(videoId) {
        val listener = VideoPlaybackListener { /* handle playback */ }
        registerVideoListener(listener)

        onDispose {
            // Cleanup executed when videoId changes or composable leaves the composition!
            unregisterVideoListener(listener)
        }
    }

    // 4. SideEffect: Runs on EVERY successful recomposition pass; syncs state with external non-Compose world
    SideEffect {
        analytics.setGlobalUserProperty("last_rendered_video", videoId)
    }

    Button(onClick = {
        // Must use rememberCoroutineScope because onClick is NOT a composable scope!
        coroutineScope.launch { scaffoldState.showSnackbar("Video bookmarked!") }
    }) {
        Text("Bookmark")
    }
}
```

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

These four primitives manage side-effects safely in Compose. LaunchedEffect runs suspending coroutines tied to a key, canceling and restarting when the key changes. DisposableEffect manages operations requiring cleanup, executing onDispose when leaving the composition. SideEffect runs on every successful recomposition to sync Compose state with external non-Compose objects. rememberCoroutineScope provides a coroutine scope for user-triggered callbacks like button clicks that execute outside of the composition phase.

## Interview answer — structured

Side-effect handlers are the official gateway connecting Compose's pure declarative world to the imperative Android platform.
Because composables can recompose unpredictably and frequently, executing side-effects directly inside the function body causes duplicate network requests, memory leaks, and state bugs.
Compose provides four specialized tools tailored to specific operational contexts.
LaunchedEffect is designed for suspending operations tied to state. It launches a coroutine upon entering composition and automatically cancels and restarts if its key parameter changes. It is ideal for loading screen data or triggering single-shot animations.
DisposableEffect is designed for non-suspending operations that require explicit teardown. It provides an onDispose clause that executes when its key changes or when the composable leaves the composition tree, making it the perfect tool for registering broadcast receivers, sensor managers, or third-party SDK listeners.
SideEffect executes a non-suspending block after every successful recomposition. It is used to push updated Compose state to external objects that are not managed by Compose, such as updating an external analytics tracker or system notification manager.
rememberCoroutineScope provides a CoroutineScope bound to the composition point. It is strictly used in event callbacks (like onClick or onSwipe) where code runs outside the composable body and cannot call composable effect APIs directly.

## Interview answer — deep senior

Under the hood, these four effect handlers interface directly with the Composer's RecomposeScope and SlotTable management routines.
LaunchedEffect stores an internal CoroutineScope instance inside a slot. When its key changes during recomposition, the Composer invokes Job.cancel() on the existing coroutine job and launches a new child job on the Apply-dispatcher. If the composable leaves composition, the Composer cancels the scope entirely.
DisposableEffect registers a DisposableEffectScope inside the SlotTable. Crucially, the Compose runtime guarantees that onDispose() will be invoked in two exact scenarios: either before re-running the effect with new keys, or when the layout node is unmounted from the composition tree. Failing to provide onDispose() results in a compile-time error.
SideEffect operates differently: it does not create a coroutine. Instead, the Composer records the lambda into a pending side-effects queue. This queue is executed strictly after the current composition transaction successfully applies to the layout tree. If the composition pass is canceled, interrupted, or discarded due to mid-flight state invalidation, the queued SideEffect lambdas are purged without executing, preventing inconsistent external state updates.
rememberCoroutineScope allocates a CoroutineScope bound to the CompositionContext. When the host composable is unmounted, the runtime calls cancel() on the scope's Job, ensuring that background jobs launched from button clicks do not outlive their UI context.

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
