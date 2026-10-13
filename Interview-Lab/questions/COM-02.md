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

`@Composable` يعلّم function تشارك في Composition؛ compiler/runtime يتتبع مكان استدعائها والـstate التي تقرأها. عندما تتغير observable state، Compose يحدد scopes تحتاج إعادة تنفيذ؛ هذه recomposition وليست بالضرورة إعادة بناء الشاشة كلها. ممكن يستدعي function ثانية أو يتجاوزها إذا inputs مناسبة للـskip. لذلك composable يجب يكون تقريبًا وصفًا للـUI، وليس مكانًا لإرسال API request أو تعديل repository في كل استدعاء.

## Practical walkthrough

خد counter بسيط: الـcomposable تقرأ `count` وتعرضه، والضغط يبعت event. تغيير الرقم يخلي الجزء اللي قرأه محتاج recomposition؛ ده مش معناه إن Android View hierarchy كلها اتبنت تاني ولا إن كل frame اتعمل لها draw. لو عندك حساب مكلف، قِس تكلفته بدل ما تحكم من عدد الاستدعاءات. المثال ده يبان تافه، لكنه يكشف bug شائع: تعديل state أثناء الرسم ممكن يعمل loop. اختبر نفس الشاشة مع تغيير سريع للقيمة وتأكد مفيش request أو listener بيتكرر.

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

“A `@Composable` function describes UI inside a composition. Recomposition re-executes affected scopes when their observed state or inputs change. A counter click changes owner state; rendering itself does not increment it.”

## Interview answer — structured

“The annotation lets the Compose compiler and runtime track a UI call, its place in the tree, and remembered state. If the scope reads a state value that changes, Compose can schedule that scope for recomposition. It may skip child calls when inputs permit; it does not automatically rerun the whole screen or equate to a redraw. I keep the function safe to call again and move one-time or lifecycle work into the appropriate effect or owner. I use a counter to show that the callback changes state and a state read triggers the next UI description.”

## Interview answer — deep senior

“A composable is a function participating in Compose's managed UI description, not just a function that returns a View. The compiler adds machinery that lets the runtime identify call sites and preserve remembered values in a composition. When a scope reads snapshot state, a later change can invalidate that scope and schedule recomposition. The runtime runs the necessary calls to describe the new UI and may skip eligible descendants; subsequent measure and draw work are separate concerns. That distinction matters when diagnosing performance: many harmless recompositions can coexist with smooth frames, while one expensive layout or draw can cause jank. I design the composable to tolerate re-execution, with immutable inputs and event callbacks. I avoid performing network requests, registering listeners, or mutating state unguarded in its body. For a counter, the button sends an event; the owner changes the value; rendering then reflects it. I use effect APIs when composition must coordinate external work and test that repeated recomposition does not duplicate it. I would check a frame trace before treating the number of recompositions as a performance problem.”

## How to answer in the interview

- **Why:** rendering can run again whenever its observed inputs change.
- **How:** trace count from event to owner update to invalidated reader.
- **Trade-off:** tiny composables improve boundaries only when they clarify ownership.
- **Failure case:** mutation or network work in the body repeats.
- **Production solution:** profile frame cost and keep effects outside rendering.

## Deep-dive talking points

Explain compiler transformation, call identity, observable reads, invalidation, skip eligibility, and effect discipline.

## Follow-up questions

- Is every recomposition a redraw? **Answer:** no; composition, layout and drawing have distinct work and triggers.
- Can a child composable be skipped? **Answer:** under eligible parameter and compiler/runtime conditions, yes.
- Why avoid a network call in the body? **Answer:** the body may execute again whenever the scope recomposes.

## Self-check rubric

Define composable context, trace state change to recomposition, distinguish render stages, and name an unsafe side effect.

## References and reviewed-on date

- [Compose phases](https://developer.android.com/develop/ui/compose/phases) — composition, layout and drawing.
- [Compose mental model](https://developer.android.com/develop/ui/compose/mental-model) — composable invocation and recomposition.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The counter is illustrative.
