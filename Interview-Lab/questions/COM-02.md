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

A `@Composable` function is a Kotlin function transformed by the Compose compiler to emit UI nodes into the composition tree. Recomposition is the process where Compose re-executes composables whose observed `State` has changed to produce updated UI, skipping unchanged composables intelligently.

## Interview answer — structured

A `@Composable` annotation transforms a Kotlin function at compile time. Much like the `suspend` keyword modifies a function's calling convention to inject a `Continuation`, `@Composable` modifies the function type to inject a `$composer` parameter and runtime control structures.

**Recomposition** is the core reactive mechanism of Jetpack Compose. When a snapshot `State` object read within a composable changes its value, the Compose runtime invalidates that specific scope in the **Slot Table** and re-executes the composable function to produce updated UI nodes.

Three critical operational rules govern recomposition.

First, with Idempotency & Purity, composables must be free of side-effects because recomposition can execute on every single frame during animations. Next, with Parallel & Arbitrary Order, composables may run concurrently on background thread pools or in arbitrary order.
Finally, with Optimistic Cancellation, if state updates again while recomposition is underway, Compose discards the pending pass and restarts with the fresh state.


## Interview answer — deep senior

Under the hood, the Compose Compiler generates synthetic bytecode called **Restartable and Replaceable Groups**. A composable marked with `@Composable` is wrapped in `$composer.startRestartGroup()` and `$composer.endRestartGroup()`. The returned scope implements `RecomposeScopeImpl`, which registers itself as an observer of snapshot state reads.

When you read `state.value` inside a composable, the `Snapshot` system records that read against the active `RecomposeScope`. When `state.value = newValue` is assigned, the snapshot system marks that `RecomposeScope` as dirty and dispatches an invalidation to the Choreographer frame loop.

If all parameters passed to a composable are known to be **Stable** and have not changed by `equals()` comparison, Compose skips executing the function body entirely (`Skipping`), which is why understanding Compose compiler stability is fundamental to fluid 120fps performance.


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
