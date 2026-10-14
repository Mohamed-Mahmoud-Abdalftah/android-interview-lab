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

ما الذي يطلق الـ Recomposition (Triggers) وما الذي يمكن للـ Runtime تخطيه (Skipping)؟

1. ما الذي يُطلق الـ Recomposition؟
   - **قراءة Snapshot State معدلة**: إذا قرأت دالة Composable قيمة `State<T>` (مثل `mutableStateOf` أو `StateFlow.collectAsStateWithLifecycle`) ثم تغيرت هذه القيمة.
   - **تغير البارامترات الممررة (Parameter Changes)**: إذا تم استدعاء الـ Composable بقيم بارامترات جديدة تختلف عن القيم السابقة.

2. ما هو التخطي الذكي (Smart Skipping)؟
   - عندما يُعاد تركيب دالة أب (Parent Composable)، يفحص Compose كل الدوال الفرعية (Children).
   - إذا كانت جميع بارامترات الدالة الفرعية **مستقرة (Stable)** ولم تتغير قيمتها (حسب مقارنة `equals()`)، ولم تقرأ الدالة أي State معدلة، يقوم محرك Compose بـ **تخطي (Skip)** استدعاء الدالة الفرعية تماماً!

3. لماذا تفشل بعض الدوال في التخطي وتُعاد بدون داعٍ؟
   - **أنواع غير مستقرة (Unstable Types)**: مثل مجموعات كوتلن القياسية `List<T>`, `Set<T>`, `Map<T>` (لأن المترجم لا يضمن أنها غير قابلة للتعديل `MutableList`).
   - **كائنات عادية بدون `@Immutable` أو `@Stable`**: إذا كان الكلاس يحتوي على `var` أو كان معرفاً في مكتبة خارجية غير مجمعة بواسطة Compose Compiler.
   - **Lambdas تلتقط متغيرات غير مستقرة**.

## Practical walkthrough

كود يوضح الفرق بين دالة يمكن تخطيها ودالة يُعاد تركيبها دائماً بسبب `List` غير مستقرة:
```kotlin
// ❌ دالة تفشل في الـ Skipping بسبب استخدام List<String> القياسية:
@Composable
fun UnskippableUserList(users: List<String>, onUserClick: (String) -> Unit) {
    // Compose Compiler يعتبر List نوعاً Unstable، لذا يُعاد تنفيذ هذه الدالة في كل recomposition للأب!
    LazyColumn {
        items(users) { user ->
            Text(text = user, modifier = Modifier.clickable { onUserClick(user) })
        }
    }
}

// ✅ دالة مستقرة تقبل التخطي (Skippable) باستخدام ImmutableList:
import kotlinx.collections.immutable.ImmutableList

@Composable
fun SkippableUserList(users: ImmutableList<String>, onUserClick: (String) -> Unit) {
    // هنا يعلم المترجم أن users مستقرة تماماً، فإذا لم تتغير القائمة، يتم تخطي الدالة 100%:
    LazyColumn {
        items(users) { user ->
            Text(text = user, modifier = Modifier.clickable { onUserClick(user) })
        }
    }
}
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

Recomposition is triggered when a composable reads a `State` object whose value changes, or when its parent recomposes with updated parameters. A composable can be skipped if all its arguments are `Stable` and structurally equal to their previous values, and no observed internal states have changed.

## Interview answer — structured

Recomposition triggers strictly through state reads and parameter mutations.

First, a The Trigger is the Compose snapshot system observes which `State<T>` objects are read within each `RecomposeScope`. When an assignment occurs on a state property, all scopes that registered a read for that property are scheduled for recomposition. Next, with Smart Skipping, during a recomposition pass of a parent composable, Compose inspects child composables. A child composable is **skipped** if and only if.
The composable is marked **restartable** and **skippable** by the Compose Compiler. All parameters passed to the function are **Stable**.
Finally, none of the parameter values have changed according to their `equals()` implementation.

If a single parameter is inferred as **Unstable** (such as standard Kotlin `List<T>`, collections, or classes containing `var` properties), Compose cannot guarantee that the object's contents haven't changed behind its back. Consequently, the compiler forces the child to recompose every single time the parent recomposes, degrading performance.


## Interview answer — deep senior

The Compose Compiler classifies types into three stability categories: **Immutable** (all public properties are `val` of primitive or immutable types; will never change), **Stable** (may mutate, but notifies the composition when mutations occur via snapshot state), and **Unstable** (may mutate without notifying Compose).

With the introduction of the **Strong Skipping Mode** in recent Compose compiler releases (enabled by default in Kotlin 2.0+), Compose became significantly smarter: composables with unstable parameters can now be skipped if the instance reference has not changed (`===`), and lambdas with captures are automatically memoized using `remember`.

To audit stability in production apps, we enable Compose Compiler Metrics (`reportsDestination`). The generated reports categorize every composable as `skippable` or `restartable only`, and pinpoint exact unstable parameters (e.g. `unstable users: List<User>`), guiding us to wrap them in Kotlinx `ImmutableList` or annotate models with `@Immutable`.


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
  **Answer:** "Before Strong Skipping, lambdas capturing variables were re-instantiated on every composition pass, causing child composables to receive a new instance and fail skipping. Strong Skipping wraps these lambdas in `remember`, stabilizing their references across recompositions."

## Self-check rubric

Trace one state read and write, explain a skip caveat, identify a correctness trap, and propose a measurement.

## References and reviewed-on date

- [Compose phases](https://developer.android.com/develop/ui/compose/phases) — phase-specific state reads.
- [Stability in Compose](https://developer.android.com/develop/ui/compose/performance/stability) — skipping and contracts.

Technically reviewed against primary documentation on 2026-10-13.
