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

## Concept and technical explanation

Compose recomposes scopes after observable state they read changes, or when a parent calls them with changed inputs. A write that compares equal under its snapshot mutation policy may not invalidate readers. Reading state in layout or draw can instead invalidate those later phases. A called child can be skipped when it is eligible and its parameters compare unchanged; the exact eligibility depends on compiler settings and restartability. With strong skipping enabled by default in Kotlin 2.0.20, restartable composables with unstable parameters may also be skipped: unstable arguments use instance equality (`===`), while stable arguments use object equality. A plain `List` is normally inferred unstable, but it does not force every invocation under strong skipping.

## Practical walkthrough (English)

Compare a new list instance with a reused immutable collection; neither example promises a frame rate:
```kotlin
@Composable
fun UserList(users: List<String>, onUserClick: (String) -> Unit) {
    LazyColumn {
        items(users) { user -> Text(user, modifier = Modifier.clickable { onUserClick(user) }) }
    }
}
// In strong skipping, reusing the same unstable List instance can allow a skip.
// A newly allocated equal List is a different instance and may not skip.
// Never mutate the backing list in place: Compose may not observe that change.
```

## Explanation in Arabic

لما Composable يقرأ `mutableStateOf` أثناء الـ Composition، القراءة بتحدد نطاق ممكن يتأثر لو القيمة اتغيرت حسب mutation policy. لو القراءة حصلت في مرحلة الـ Layout أو Draw، التحديث ممكن يقتصر على المرحلة دي. كمان الأب لما يستدعي ابن بمدخلات جديدة قد يحتاج الابن يتنفذ. متغير Kotlin عادي بيتغير من غير حالة observable مش بيشغّل Recomposition تلقائياً.

الـ Skipping يعني إن استدعاء ابن مؤهل اتعمل وقت إعادة تركيب الأب لكن جسم الابن ما اتنفذش لأن المدخلات اتقارنت وطلعت كما هي. في الإعدادات القديمة، الأنواع غير المستقرة زي `List<T>` تمنع أهلية التخطي غالباً. مع **Strong Skipping**، الافتراضي من Kotlin 2.0.20، الدوال الـ restartable بقت مؤهلة حتى مع باراميترات unstable؛ المقارنة للـ unstable بالهوية `===` وللـ stable بالمساواة `equals()`. ده معناه إن `List` جديدة بنفس العناصر ممكن تؤدي لإعادة التنفيذ، بينما نفس الكائن قد يُتخطى؛ لكنه لو اتعدل في مكانه من غير إشارة observable ممكن الواجهة تبقى قديمة.

استخدم immutable model حقيقي أو persistent collection لما ده مناسب، ومتضيفش `@Immutable` على غلاف فيه `List` قابلة للتعديل لمجرد إسكات التقرير؛ الـ annotation وعد بصحة سلوك النوع. افحص compiler metrics للنسخة اللي عندك وقِس frame time. عدد مرات إعادة التركيب مش حكم نهائي على أداء الشاشة.

## Practical walkthrough

تجربة بسيطة تقارن هوية القائمة بدل إطلاق حكم مطلق على `List`:
```kotlin
@Composable
fun NamesPanel(names: List<String>) {
    Column { names.forEach { name -> Text(name) } }
}
// الأب يحتفظ بنفس instance لو البيانات لم تتغير، ويصدر قائمة جديدة عند التعديل.
// نجاح التخطي يعتمد أيضاً على نسخة Compose Compiler وإعداداته.
```

## Why it matters and how it works

Snapshot state records reads within composition scopes. A write that changes a value according to its mutation policy invalidates dependent readers. A parent recomposition may call children, but skipping depends on compiler-inferred stability and whether arguments changed; exact rules can evolve with Compose versions. Reads during layout or draw can defer work to those phases instead of restarting composition.

## Worked example

A shopping screen has a changing `searchText` and a large static promotion panel. If the root reads `searchText` and computes every result and panel decoration inline, each keystroke traverses a broad scope. Move the text-dependent query UI into a smaller composable, keep stable inputs for the panel, and measure the frame trace before and after. Do not hide the search change in a plain mutable list.

### Compose/Kotlin walkthrough

```kotlin
// Keep the frequently changing read inside the small search region.
@Composable
fun Catalog(query: State<String>, onQuery: (String) -> Unit) {
    Column {
        Text("Featured")
        SearchBox(query, onQuery) // Catalog does not read query.value.
    }
}
@Composable
private fun SearchBox(query: State<String>, onQuery: (String) -> Unit) {
    OutlinedTextField(query.value, onValueChange = onQuery, label = { Text("Search") })
}
// Import androidx.compose.runtime.State; owner passes observable State.
```

## Trade-offs and decision criteria

Narrow state reads can reduce composition work but over-fragmenting code hurts clarity. Immutable data and stable APIs support skipping, yet stability annotations should reflect actual contracts rather than silence tooling. Expensive calculation should be moved or memoized only when traces show cost and keys are correct.

## Failure modes

An in-place list mutation does not notify Compose. A broad parent reads rapidly changing state and restarts costly work. A developer adds `@Stable` to a mutable type whose properties do not notify, causing stale UI. An optimization focuses on recompositions while the actual jank is image decoding or layout.

## Production perspective

Use compiler metrics, Layout Inspector or trace tools appropriate to the installed Compose version, measure a release build and test correctness under mutations. Keep a before/after performance case tied to user-visible frames.

## Interview answer — short

Observable state changes can invalidate scopes that read it in composition, and changed parameters from a parent can require recomposition. Skipping applies to eligible calls with unchanged inputs. In strong skipping, restartable composables with unstable parameters can skip too: stable arguments use equality and unstable arguments use identity. Check the project's compiler settings and measure before optimizing.

## Interview answer — structured

First identify where the state is read. A change to snapshot state can invalidate a composition scope that read it; a state read deferred to layout or draw can invalidate only that phase. A parent with changed inputs may call a child again. A normal mutable property does not notify Compose by itself. The compiler then decides whether a called child can skip. In older configurations, a stable parameter contract is central to skippability. Kotlin's read-only `List` interface is not proof of immutability, so the compiler commonly classifies it unstable. Strong skipping, enabled by default from Kotlin 2.0.20, broadens eligibility to restartable composables with unstable parameters. Its comparison for unstable values is identity, not structural equality; stable values use object equality. A fresh list may therefore recompose where a reused instance would skip. Do not turn this into a reason to mutate a list in place: that can leave UI stale. Use observable immutable updates and inspect compiler reports and traces before changing APIs.

## Interview answer — deep senior

Compose Compiler infers parameter stability and generates change tracking for composable calls. The generated bit layout is an implementation detail; the interview-level contract is observable inputs, eligibility and comparison behavior. With strong skipping enabled, every restartable composable becomes skippable even when some parameters are unstable; non-restartable composables remain outside that rule. Stable arguments compare using object equality, unstable arguments using instance identity. Compiler memoization of lambdas under strong skipping can preserve a callback reference when its captures compare unchanged, but the exact capture comparison also follows stability rules.

Consider a parent building `names = source.toList()` on each recomposition. Even if names look the same, a new unstable list instance may fail identity comparison. `remember(source)` may help when the source itself has a valid immutable change contract, but remembering a mutable list that is edited in place breaks correctness. A persistent immutable collection can express the model more clearly. Applying `@Immutable` is a promise that all publicly exposed values obey immutability, not a performance switch to paste onto a mutable wrapper. Inspect the generated compiler report and a release-like trace before claiming a bottleneck.

Also distinguish phases. If rapidly changing state is only needed in draw, moving the read to a drawing modifier may avoid recomposing the tree. If composition is actually expensive, narrow its read scope or move the expensive calculation behind correctly keyed memoization. If the slow frame is caused by image decode or layout, making a child skippable will not fix it. Explain a concrete state change and measure the result rather than aiming for zero recompositions.

## How to answer in the interview

- **Why:** a broad state read can increase work per edit.
- **How:** name the snapshot read, its invalidated scope, and possible child skipping.
- **Trade-off:** extra boundaries cost readability if no measured issue.
- **Failure case:** plain mutable fields do not notify Compose.
- **Production solution:** inspect traces and compiler reports before changing the model.

## Deep-dive talking points

Discuss snapshot reads, mutation policy, parent invocation, skippability, compiler stability, and phase-specific measurement.

## Follow-up questions

- **Interviewer:** "What is the difference between restartable and skippable in Compose Compiler metrics?"
  **Answer:** "A restartable composable can act as a RecomposeScope boundary to re-execute when its internal states change. A skippable composable can be completely bypassed when called by a recomposing parent if its parameters haven't changed."

- **Interviewer:** "How did Strong Skipping Mode change Compose behavior for lambdas?"
  **Answer:** "With strong skipping, the compiler memoizes lambdas inside composables using their captured values as keys. Stable captures use equality and unstable captures use identity, which may keep a callback reference unchanged. I still check compiler version and actual metrics."

## Self-check rubric

Trace one state read and write, explain a skip caveat, identify a correctness trap, and propose a measurement.

## References and reviewed-on date

- [Compose phases](https://developer.android.com/develop/ui/compose/phases) — phase-specific state reads.
- [Stability in Compose](https://developer.android.com/develop/ui/compose/performance/stability) — skipping and contracts.
- [Strong skipping mode](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping) — default version and stable/unstable comparison.

Technically reviewed against primary documentation on 2026-10-19.
