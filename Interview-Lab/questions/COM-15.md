---
id: "COM-15"
question: "What does stability mean for Compose types and parameters?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 244
editorial_status: "reviewed"
---

# COM-15

## Original interview question

What does stability mean for Compose types and parameters?

## What the interviewer evaluates

- State the change-observability contract behind stability.
- Explain skip comparison with version-sensitive strong skipping behavior.
- Avoid false `@Stable`/`@Immutable` annotations and premature tuning.

## Explanation in Arabic

Compose تعتبر type stable عندما يمكنها معرفة إذا value تغيرت بين recompositions؛ immutable value أو mutable properties ترسل إشعارًا مرصودًا. `@Immutable`/`@Stable` وعود من المطور، وليست أدوات سحرية لتسريع أي class. مثلًا `var name` عادية داخل class معلّم `@Stable` دون observable state قد تجعل UI قديمة. Kotlin `List` interface قد تعتبر غير مستقرة لأن محتواها قابل للتغير؛ وفي إصدارات compiler الحديثة strong skipping يغيّر شروط تجاوز calls وكيف تُقارن parameters. افحص compiler reports وقياس الأداء الفعلي قبل وضع annotations.

## Why it matters and how it works

Stability information helps Compose determine whether a recomposed parent can skip a child call with unchanged parameters. Stable values use equality semantics under documented compiler modes; unstable values may be compared by identity with strong skipping. Compiler settings and versions matter, so an absolute claim that any unstable type always recomposes is unsafe. Skipping has comparison and bookkeeping cost; correctness requires that changes affecting UI be observable.

## Worked example

`UserCard(model: UserUiModel)` receives a data class with immutable `id` and `displayName`; equivalent updates may be skipped depending on compiler inference. A `MutableUser` class changes `displayName` in place without Compose state: annotating it `@Stable` can suppress an update while showing stale text. Instead emit a new immutable UI model or use observable state in a carefully owned state holder.

## Trade-offs and decision criteria

Immutable models simplify reasoning and testing, but copying a large tree can cost allocations. Stable mutable objects can work if every public UI-affecting change is observable, a hard contract to maintain. Strong skipping may already handle an unstable parameter effectively when the same instance is passed; adding annotations blindly can trade cheap identity checks for expensive equality checks.

## Failure modes

A false stability annotation hides updates. A collection is mutated in place and no new state emission occurs. A team optimizes skip counts while the real frame cost is image loading or layout. Compiler reports are interpreted without checking active strong-skipping mode and version.

## Production perspective

Diagnose measured jank first, inspect compiler stability reports for the affected composable, and test that changed fields render correctly. Benchmark any model or annotation change on a release build before spreading it across the design system.

## Interview answer — short

“Stability is Compose's contract that parameter changes can be detected reliably. It influences skipping, but annotations must reflect observable behavior and current compiler rules.”

## Interview answer — structured

“I distinguish stable data from a type merely labeled stable. Immutable values are easy to reason about; mutable stable types must notify Compose whenever UI-relevant data changes. Stability affects whether Compose can skip a child with unchanged inputs, but strong skipping and comparison rules are compiler-version-sensitive. I use reports and traces to identify a real problem. I would never annotate a plain mutable object `@Stable` just to silence a warning, because that can produce stale UI.”

## Interview answer — deep senior

“Stability tells Compose whether it can trust parameter comparisons when deciding to skip a call during parent recomposition. A deeply immutable UI model has a straightforward contract. A mutable stable model is possible, but every property that affects rendering must change observably; a naked `var` modified in place breaks that promise. `@Stable` and `@Immutable` are therefore semantic assertions, not performance switches. In modern compiler configurations, strong skipping can make restartable functions with unstable parameters skippable, often comparing unstable values by instance identity. That makes blanket statements about unstable classes wrong, and adding a supposedly stable wrapper can even replace a cheap identity check with a costlier equality comparison. I begin with a user-visible frame issue, inspect recomposition and compiler reports for the specific call, then verify which state read or parameter causes work. If a model change is justified, I prefer immutable UI values or an explicitly observable mutable state holder and test that every field update renders. I compare release benchmarks before and after. Correctness wins over a prettier skip count, and the exact optimization advice must match the project's Compose compiler version.”

## Deep-dive talking points

Discuss inference, observability, strong skipping, identity versus equality, false annotations, and benchmark evidence.

## Follow-up questions

- Is `@Stable` enough to make a plain mutable field observable? **Answer:** no; the annotation promises behavior but does not implement notifications.
- Are unstable parameters always unskippable? **Answer:** no; strong skipping can permit skipping under version-specific comparison rules.
- Why not annotate every model? **Answer:** skipping and equality checks have costs, and false contracts can break UI correctness.

## Self-check rubric

Define the contract, explain one stale-UI bug, account for strong skipping, and propose a measured fix.

## References and reviewed-on date

- [Stability in Compose](https://developer.android.com/develop/ui/compose/performance/stability) — type contract.
- [Strong skipping mode](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping) — version-sensitive skip rules.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Compiler behavior should be checked against the actual project toolchain.
What does stability mean for Compose types and parameters?
