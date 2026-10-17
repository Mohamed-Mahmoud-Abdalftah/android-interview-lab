---
id: "COM-02"
question: "What is a @Composable function? What is recomposition?"
topic: "Jetpack Compose"
code: "COM"
group: "A"
phase: 3
priority: "P1"
order: 231
editorial_status: "reviewed"
---

# COM-02

## Original interview question

What is a @Composable function? What is recomposition?

## What the interviewer evaluates

- Define composable invocation in a composition context.
- Relate recomposition to changed inputs or state reads.
- Separate recomposition from every layout or draw and reject side effects in rendering.

## Concept and technical explanation

A @Composable function is a Kotlin function annotated with @Composable that serves as a basic building unit in Jetpack Compose, emitting UI nodes into the composition graph rather than returning a value. The @Composable annotation alters the function's calling conventions at compile time, allowing it to read and write state, access composition locals, and participate in lifecycle management. Recomposition is the process whereby the Compose runtime re-executes composable functions in response to state changes to update the visual UI tree, intelligently skipping any functions whose input parameters have not changed.

## Practical walkthrough (English)

Demonstrating a Composable function, state observation, and recomposition execution:
```kotlin
// A pure Composable function that observes state and re-executes during recomposition
@Composable
fun CounterWidget(count: Int, onIncrement: () -> Unit) {
    // This function will re-execute (recompose) whenever 'count' changes
    Column(
        modifier = Modifier.padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Current Taps: $count",
            style = MaterialTheme.typography.headlineMedium
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onIncrement) {
            Text("Increment")
        }
    }
}

// Side-effects MUST NOT be placed directly in the composable body, as recomposition can happen frequently!
@Composable
fun BadAnalyticsComposable(screenName: String) {
    // ❌ ANTI-PATTERN: Side-effect executed directly in the body! Runs on EVERY recomposition!
    // analytics.track(screenName) 

    // ✅ BEST PRACTICE: Wrap side-effects inside dedicated effect handlers
    LaunchedEffect(screenName) {
        // Runs only when screenName changes, not on every random recomposition!
    }
}
```

## Explanation in Arabic

ما هي دالة `@Composable` وما هو مفهوم الـ Recomposition؟

1. طبيعة الـ `@Composable Annotation`:
   - الـ `@Composable` ليس مجرد وسم شكلي (Annotation)، بل هو **مغير نوع للغة كوتلن (Type modifier)** يفهمه الـ Compose Compiler Plugin.
   - تماماً كما أن كلمة `suspend` تغير توقيع الدالة وتمرر `Continuation`، فإن `@Composable` تجبر المترجم على حقن بارامتر خفي اسمه `$composer` داخل الدالة وتغيير نوعها لتصبح صالحة للاستدعاء فقط من داخل دوال `@Composable` أخرى.

2. ما هي الـ Recomposition (إعادة التركيب)؟
   - هي العملية التي يقوم فيها محرك Compose بإعادة تشغيل (Re-executing) دوال الـ Composable عندما تتغير البيانات أو الحالات (`State`) التي تقرأها تلك الدوال.
   - الهدف: تحديث شجرة العرض بما يتطابق مع الحالة الجديدة.

3. القواعد الذهبية للـ Recomposition التي يجب أن يعيها مهندس الـ Senior:
   - **Recomposition is Optimistic**: قد يبدأ Compose إعادة التركيب، وإذا تغيرت الحالة مجدداً قبل اكتمال الفريم، يلغي العملية ويعيدها بالحالة الأحدث.
   - **Executes in Any Order**: لا تضمن ترتيب تنفيذ دوال الـ Composable؛ قد تعمل بالتوازي.
   - **Side-Effect Free**: يجب ألا تحتوي دالة الـ Composable على أي Side Effects (مثل استدعاء شبكة، أو تعديل متغير عام، أو تشغيل صوت) خارج الـ Effect APIs المخصصة (`LaunchedEffect` / `SideEffect`).

## Practical walkthrough

كيف يؤدي كود يحتوي على Side-Effect داخل دالة Composable إلى كوارث أداء وكيفية علاجه:
```kotlin
// ❌ كود كارثي: تشغيل Side-Effect مباشرة داخل جسم الـ Composable:
@Composable
fun BadUserCounter(count: Int) {
    // 💥 كارثة: في كل مرة يعاد فيها رسم الشاشة (Recomposition)، يتم إرسال طلب تحليلات جديد!
    AnalyticsTracker.logEvent("screen_viewed")

    Text(text = "Count: $count")
}

// ✅ كود سليم: عزل الـ Side-Effects داخل Effect Handlers المخصصة:
@Composable
fun GoodUserCounter(count: Int) {
    // يتم استدعاؤه مرة واحدة فقط عند دخول الـ Composable لأول مرة:
    LaunchedEffect(Unit) {
        AnalyticsTracker.logEvent("screen_viewed")
    }

    Text(text = "Count: $count")
}
```

## Why it matters and how it works

The annotation enables compiler transformation and runtime composition bookkeeping. A composable call is meaningful in the composition context, where remembered values and nodes are associated with call positions and keys. State reads can invalidate scopes; recomposition reruns them to produce an updated UI description. Later layout or draw work has distinct triggers, so a recomposition count is not a frame-time metric by itself.

## Worked example

`Counter(value, onIncrement)` displays `value` and a button. A state owner increments from 4 to 5, causing the scope that reads `value` to recompose and display 5. The click callback changes state; the composable body does not increment it during rendering. An adjacent static logo may be skipped depending on its parameters and compiler/runtime behavior.

### Compose/Kotlin walkthrough

```kotlin
// A parent owns count; the composable stays safe to run again.
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Row {
        Text("Count: $count")
        Button(onClick = onIncrement) { Text("Add") }
    }
}
// Parent: var count by rememberSaveable { mutableIntStateOf(0) }
// Counter(count, onIncrement = { count++ })
```

## Trade-offs and decision criteria

Small composables can isolate readable state and simplify reuse, but splitting every `Text` into an abstraction adds indirection. Hoist only state needed by a wider owner; keep local decoration state near its consumer. Optimize based on traces and user-visible jank, not raw recomposition counts.

## Failure modes

Mutating state during composition can cause repeated invalidation or loops. Calling a composable from an ordinary callback is not valid without a composition context. A time-consuming calculation runs for every invalidated call. Treating a recomposition as proof of a redraw sends debugging in the wrong direction.

## Production perspective

Use state/event boundaries and effects for controlled work. Profile with Compose tooling and system traces in release mode when frames regress, and verify correctness under recomposition and lifecycle recreation.

## Interview answer — short

A @Composable function is a Kotlin function annotated with @Composable that describes UI layout and emits nodes into the composition hierarchy. Recomposition is the automatic re-execution of composable functions by the runtime whenever their observed state changes. During recomposition, Compose inspects function parameters and intelligently skips re-running any composables whose inputs remain identical, ensuring high rendering performance and smooth 60fps animations.

## Interview answer — structured

Understanding @Composable functions and recomposition mechanics is the cornerstone of writing performant Jetpack Compose applications.
The @Composable annotation is a compiler directive that fundamentally transforms a function's bytecode. Much like Kotlin's suspend keyword, @Composable alters the function type, enabling it to be invoked only from within another composable context. Instead of constructing and returning a View instance, a composable function accepts state parameters and emits declarative UI layout descriptions.
Recomposition is Compose's reactive update mechanism.
When a snapshot state variable read by a composable changes, the Compose runtime invalidates that specific function scope.
During the subsequent frame rendering phase, Compose re-executes the invalidated composables with the updated state values.
Because recomposition can occur on every single animation frame (up to 120 times per second), composable functions must remain idempotent, pure, and completely free of direct side-effects like database queries, network requests, or direct analytics tracking.
Compose ensures optimal performance through smart skipping: if a composable's arguments are stable and unchanged, the runtime skips its execution entirely, updating only the modified leaf nodes.

## Interview answer — deep senior

Under the hood, the @Composable annotation activates the Compose Compiler plugin, which rewrites the function signature by appending two synthetic parameters: a Composer instance and an integer bitmask (changed).
The Composer parameter acts as a low-level broker between your code and the SlotTable. It tracks code location keys, allocates slots for remember calculations, records state read dependencies, and manages the execution stack.
The changed integer parameter contains bit flags that communicate the stability and mutation status of every input argument across recompositions. Before executing the function body, the compiled bytecode evaluates a conditional check comparing current arguments with previous values stored in the SlotTable. If all arguments are unchanged and stable, the function branches immediately to the end of the method, achieving zero-allocation skipping.
Furthermore, the Compose runtime does not guarantee that recomposition runs in top-down sequential order, nor does it guarantee that recomposition executes on the main thread during speculative phases.
Recomposition can also be canceled mid-execution if state updates again before the frame completes, discarding the intermediate composition work.
Senior engineers design composables to be completely side-effect free, delegating asynchronous tasks and imperative mutations exclusively to lifecycle-aware effect primitives like LaunchedEffect or DisposableEffect. By keeping composables deterministic and referentially transparent, the runtime safely parallelizes composition across worker threads in future compiler optimizations without risking concurrency locks or corrupted UI state.

## How to answer in the interview

- **Why:** rendering can run again whenever its observed inputs change.
- **How:** trace count from event to owner update to invalidated reader.
- **Trade-off:** tiny composables improve boundaries only when they clarify ownership.
- **Failure case:** mutation or network work in the body repeats.
- **Production solution:** profile frame cost and keep effects outside rendering.

## Deep-dive talking points

Explain compiler transformation, call identity, observable reads, invalidation, skip eligibility, and effect discipline.

## Follow-up questions

- **Interviewer:** "Can a composable function run on a background thread during recomposition?"
  **Answer:** "Yes. While Compose dispatches UI node mutations on the main thread, the actual execution and calculation of composable function logic can be executed across thread pools, meaning composable bodies must never read or write non-thread-safe state."

- **Interviewer:** "What happens if a composable is recomposed 60 times per second during an animation?"
  **Answer:** "If the function is pure, it recalculates UI values smoothly. But if it performs allocations, IO, or side-effects, it triggers immediate memory churn, GC pauses, and dropped frames."

## Self-check rubric

Define composable context, trace state change to recomposition, distinguish render stages, and name an unsafe side effect.

## References and reviewed-on date

- [Compose phases](https://developer.android.com/develop/ui/compose/phases) — composition, layout and drawing.
- [Compose mental model](https://developer.android.com/develop/ui/compose/mental-model) — composable invocation and recomposition.

Technically reviewed against primary documentation on 2026-10-13.
