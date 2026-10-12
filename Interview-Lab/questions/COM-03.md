---
id: "COM-03"
question: "What triggers recomposition, and what can be skipped?"
topic: "Jetpack Compose"
code: "COM"
group: "A"
phase: 3
priority: "P1"
order: 232
editorial_status: "reviewed"
---

# COM-03

## Original interview question

What triggers recomposition, and what can be skipped?

## What the interviewer evaluates

- Trace observable state reads and parameter changes to invalidation.
- Explain skipping with stability caveats rather than a blanket guarantee.
- Diagnose an actual expensive scope.

## Explanation in Arabic

Compose يعيد composition عندما state مقروءة في scope تتغير، أو parent يعيد الاستدعاء بمدخلات مختلفة، أو عوامل أخرى تتطلب تحديث الـcomposition. لكنه يستطيع تجاوز child calls إذا parameters ومعايير الـcompiler تسمح. `mutableStateOf` مرصود؛ تغيير property داخل plain mutable object دون observable wrapper قد لا يظهر. ونقل قراءة state إلى child ضيق يحدّ invalidation، لكن قراءة value في parent الكبير توسع العمل. عدد recompositions وحده ليس دليل بطء؛ قياس frame time مهم.

## Why it matters and how it works

Snapshot state records reads within composition scopes. A write that changes a value according to its mutation policy invalidates dependent readers. A parent recomposition may call children, but skipping depends on compiler-inferred stability and whether arguments changed; exact rules can evolve with Compose versions. Reads during layout or draw can defer work to those phases instead of restarting composition.

## Worked example

A shopping screen has a changing `searchText` and a large static promotion panel. If the root reads `searchText` and computes every result and panel decoration inline, each keystroke traverses a broad scope. Move the text-dependent query UI into a smaller composable, keep stable inputs for the panel, and measure the frame trace before and after. Do not hide the search change in a plain mutable list.

## Trade-offs and decision criteria

Narrow state reads can reduce composition work but over-fragmenting code hurts clarity. Immutable data and stable APIs support skipping, yet stability annotations should reflect actual contracts rather than silence tooling. Expensive calculation should be moved or memoized only when traces show cost and keys are correct.

## Failure modes

An in-place list mutation does not notify Compose. A broad parent reads rapidly changing state and restarts costly work. A developer adds `@Stable` to a mutable type whose properties do not notify, causing stale UI. An optimization focuses on recompositions while the actual jank is image decoding or layout.

## Production perspective

Use compiler metrics, Layout Inspector or trace tools appropriate to the installed Compose version, measure a release build and test correctness under mutations. Keep a before/after performance case tied to user-visible frames.

## Interview answer — short

“Changed observable state invalidates scopes that read it, and changed inputs can propagate through parents. Compose can skip eligible child calls when its parameter stability and change checks allow.”

## Interview answer — structured

“I locate where state is read. A write to snapshot state can invalidate those composition scopes; a parent may also re-execute because its inputs changed. Children with suitable unchanged parameters may be skipped, but I would not promise that for every composable or every compiler version. I isolate rapidly changing reads, keep data truly observable, and profile the frame. A high count alone is less useful than knowing whether composition, layout or draw is expensive.”

## Interview answer — deep senior

“Recomposition is driven by the dependency between observable state reads and composition scopes, plus input changes flowing through callers. When a snapshot value changes, Compose schedules readers that depend on it. It can avoid repeating eligible calls with unchanged inputs, subject to the compiler's stability model and the actual version. I do not treat it as a simple ‘the whole screen rerenders’ rule. If typing is slow, I first trace the state read: perhaps a root composable reads every character and performs filtering, formatting and expensive subtree construction. I can move the read closer to the search results, pass stable values to unrelated children, and shift heavy work to an appropriate layer. I confirm that the data is observable; mutating an ordinary collection in place is a correctness bug, not a clever way to avoid recomposition. I then measure composition, layout and draw separately on a release build. Stability annotations are contracts about change visibility, so falsely marking a mutable model stable to raise skip counts risks stale UI. My success measure is correct behavior with improved frame timing.”

## Deep-dive talking points

Discuss snapshot reads, mutation policy, parent invocation, skippability, compiler stability, and phase-specific measurement.

## Follow-up questions

- Does changing a normal mutable list trigger UI updates? **Answer:** not reliably unless changes are exposed through observable Compose state.
- Can a parent recompose while a child is skipped? **Answer:** yes, when the child satisfies the runtime/compiler skip conditions.
- What should performance work optimize? **Answer:** measured user-visible frame cost, not recomposition counts in isolation.

## Self-check rubric

Trace one state read and write, explain a skip caveat, identify a correctness trap, and propose a measurement.

## References and reviewed-on date

- [Compose phases](https://developer.android.com/develop/ui/compose/phases) — phase-specific state reads.
- [Stability in Compose](https://developer.android.com/develop/ui/compose/performance/stability) — skipping and contracts.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Compiler behavior is version-sensitive.
