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

A `@Composable` function participates in a composition: it describes UI by calling other composables and may read observable state and composition locals. Many UI-emitting composables return `Unit`, but composables can return values too. The Compose compiler transforms calls so the runtime can retain identity and schedule updates. Initial composition builds the UI description; recomposition re-executes invalidated scopes when observed state changes or a caller supplies changed inputs. The runtime may skip eligible calls with unchanged inputs, depending on compiler version, stability and restartability. Composition, layout and drawing are separate phases; a recomposition is neither a guaranteed redraw nor a frame-rate result.

## Practical walkthrough (English)

Demonstrating a Composable function, state observation, and recomposition execution:
```kotlin
// A pure Composable function that observes state and re-executes during recomposition
@Composable
fun CounterWidget(count: Int, onIncrement: () -> Unit) {
    // A caller changing count can cause this call to recompose.
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
    // An incidental side effect here might run repeatedly or be skipped.
    // analytics.track(screenName)

    // ✅ BEST PRACTICE: Wrap side-effects inside dedicated effect handlers
    LaunchedEffect(screenName) {
        // Runs on entry and restarts when screenName changes.
    }
}
```

## Explanation in Arabic

دالة `@Composable` بتوصف جزء من الواجهة عن طريق استدعاء دوال Compose تانية داخل سياق الـ Composition. أغلب دوال الواجهة بترجع `Unit`، لكن الـ annotation نفسها مش معناها إن الدالة ممنوع ترجع قيمة. الـ Compose Compiler بيحوّل الاستدعاءات عشان الـ Runtime يقدر يتابع موضعها ويحفظ قيم `remember` ويرصد قراءات الـ State.

أول تشغيل اسمه **Composition**. لما قيمة observable اتقرت أثناء الـ Composition تتغير، Compose بيعلّم النطاق القارئ إنه محتاج تحديث، وبعدها ممكن يعيد تنفيذ النطاق ده؛ دي **Recomposition**. كمان استدعاء الأب للابن بمدخلات مختلفة ممكن يعيد تنفيذ الابن. الدوال المؤهلة للـ Skipping ومدخلاتها ما اتغيرتش ممكن تتخطى، لكن القرار متعلق بالـ Stability والـ compiler version والـ restartability، مش وعد لكل دالة.

فرّق بين **Composition** اللي بتوصف العناصر، و**Layout** اللي بيقيس ويحطها، و**Draw** اللي بيرسمها. عدد مرات الـ Recomposition لوحده مش مقياس عدد الـ frames ولا دليل على الـ jank. اكتب جسم الدالة سريع ومن غير آثار جانبية مباشرة؛ لأن التنفيذ ممكن يتكرر، يتخطى أو يتلغى. استخدم `LaunchedEffect` للعمل المرتبط بدخول العنصر أو تغيّر مفتاح، و`DisposableEffect` للاشتراك اللي محتاج تنظيف. اختبر أثر التغيير بأدوات الـ profiler وframe traces على نسخة مناسبة للأداء.

## Practical walkthrough

مثال يفرّق بين وصف الواجهة والعمل اللي يحصل عند دخولها:
```kotlin
@Composable
fun CounterRoute(count: Int, analytics: AnalyticsTracker) {
    // الأثر مرتبط بدخول الـ Composition؛ تغيير count وحده لا يعيده.
    LaunchedEffect(Unit) {
        analytics.logEvent("screen_viewed")
    }
    Text(text = "Count: $count") // قراءة count هنا تصف المحتوى فقط.
}
```

لو المطلوب تسجيل كل نقرة، سجلها داخل callback النقرة نفسه؛ `LaunchedEffect(Unit)` مش بديل عن حدث المستخدم.

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

A `@Composable` function describes UI within a composition. Recomposition re-executes affected scopes after observable state changes or changed inputs; eligible unchanged children may be skipped. Composition, layout and draw are distinct, so neither skipping nor recomposition guarantees a frame rate. Keep rendering fast and move side effects to events or effect APIs.

## Interview answer — structured

The annotation marks a Kotlin function for Compose compiler transformation and lets it be called in a composable context. A UI-emitting function usually calls other composables to describe the desired hierarchy; it does not directly paint pixels. Initial composition establishes that hierarchy and records relevant state reads. A changed snapshot value can invalidate the scope that read it, and changed arguments supplied by a parent can also require work. The runtime then recomposes affected scopes. Calls that meet the current compiler's skipping rules may be omitted when inputs compare unchanged. These rules are version dependent and do not imply that every stable-looking function will skip. Layout and draw have their own invalidation paths, so a recomposition count should not be treated as a frame count. Since bodies may run again or be skipped, do not perform network calls, analytics or state mutations as incidental composition work. Use event handlers and the relevant Compose effect API with deliberate keys; profile frame time to evaluate performance.

## Interview answer — deep senior

At compilation, Compose changes composable calls to carry bookkeeping needed for identity, remembered values and change tracking. The exact generated signature and mask layout are compiler implementation details, not an API contract to memorize. The runtime associates a call with its position and keys, and snapshot state reads can identify scopes to invalidate. On a change, the runtime may restart those scopes and may skip child calls whose parameters compare unchanged under the installed compiler rules. A child that reads invalidated state itself still needs its own update even if a parent would otherwise be skipped. Strong skipping changes eligibility and uses different comparisons for stable and unstable parameters, so inspect the compiler report for the project's version rather than promising a universal rule.

Compose's documented mental model allows recomposition to be canceled, skipped, reordered or potentially parallelized. That is a reason to make the body idempotent and free of incidental work, not a claim that current Android rendering runs every body on background threads. `LaunchedEffect(key)` starts work when that effect enters composition and restarts when its key changes; `DisposableEffect` pairs setup and teardown. An event callback is the right place for work caused by a specific user action. None of these primitives automatically makes blocking work safe on the main thread.

For a performance investigation, capture a user-visible slow interaction in a release-like build, inspect traces and separate composition cost from measure/layout and draw. Reducing a recomposition counter without improving frame time may not solve the problem. Correctness comes first: state updates must remain observable and effect keys must match the lifetime of the operation.

## How to answer in the interview

- **Why:** rendering can run again whenever its observed inputs change.
- **How:** trace count from event to owner update to invalidated reader.
- **Trade-off:** tiny composables improve boundaries only when they clarify ownership.
- **Failure case:** mutation or network work in the body repeats.
- **Production solution:** profile frame cost and keep effects outside rendering.

## Deep-dive talking points

Explain compiler transformation, call identity, observable reads, invalidation, skip eligibility, and effect discipline.

## Follow-up questions

- **Interviewer:** "Should I assume composable bodies always run on a background thread?"
  **Answer:** "No. Compose's mental model allows different execution order and possible parallel execution, so I keep bodies free of unsafe side effects. I do not rely on a particular thread for composition work or claim that the current runtime parallelizes every call."

- **Interviewer:** "Does a high recomposition count prove dropped frames?"
  **Answer:** "No. Some animations update every frame by design. I measure actual frame timing, then trace whether composition, layout, draw or other work is expensive. I keep blocking IO and incidental effects out of the composable body."

## Self-check rubric

Define composable context, trace state change to recomposition, distinguish render stages, and name an unsafe side effect.

## References and reviewed-on date

- [Compose phases](https://developer.android.com/develop/ui/compose/phases) — composition, layout and drawing.
- [Compose mental model](https://developer.android.com/develop/ui/compose/mental-model) — composable invocation and recomposition.

Technically reviewed against primary documentation on 2026-10-19.
