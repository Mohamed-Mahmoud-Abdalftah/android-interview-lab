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

Recomposition is triggered when a composable function reads a Snapshot State object whose underlying value changes during state mutation. However, Compose does not blindly re-execute the entire UI hierarchy; instead, it enforces fine-grained, localized recomposition. A composable function can be completely skipped if all of its input parameters are determined to be Stable or Immutable by the Compose compiler and their runtime values remain unchanged since the previous composition. Conversely, functions accepting unstable types (such as standard Java/Kotlin collections like List, or mutable data classes with var properties) cannot be proven unchanged, forcing Compose to re-execute them conservatively on every recomposition pass.

## Practical walkthrough (English)

Contrasting an unskippable composable with a fully skippable composable:
```kotlin
// ❌ FAILS TO SKIP: Standard Kotlin List is considered UNSTABLE by Compose Compiler!
// Even if the list content is identical, UserList will ALWAYS re-execute whenever parent recomposes!
@Composable
fun UnstableUserList(users: List<String>, onUserClick: (String) -> Unit) {
    LazyColumn {
        items(users) { user -> Text(user, modifier = Modifier.clickable { onUserClick(user) }) }
    }
}

// ✅ ARCHITECTURAL BEST PRACTICE: Fully skippable composable using Immutable wrapper or Kotlinx Immutable
@Immutable
data class UserListState(val users: List<String>) // Marked @Immutable promises compiler list will never mutate!

@Composable
fun StableUserList(
    state: UserListState, // Stable type!
    onUserClick: (String) -> Unit // Stable lambda reference!
) {
    // Compose compiler successfully SKIPS this function if state and lambda have not changed!
    LazyColumn {
        items(state.users) { user -> Text(user, modifier = Modifier.clickable { onUserClick(user) }) }
    }
}
```

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

Recomposition is triggered whenever a Snapshot State object read by a composable function is modified. A composable can be skipped if all its input arguments are stable and equal to their previous composition values. The Compose compiler marks primitive types, Strings, function lambdas, and classes annotated with @Immutable or @Stable as stable. However, standard collections like List or classes with mutable var properties are treated as unstable, forcing Compose to re-execute the composable even if the underlying data has not changed.

## Interview answer — structured

Achieving peak UI performance in Jetpack Compose depends on understanding the exact mechanics governing recomposition triggers and compiler skipping.
Recomposition is not triggered by arbitrary background variable modifications; it is triggered strictly when a function reads a Snapshot State object (such as mutableStateOf or StateFlow converted via collectAsState) whose value subsequently updates.
Compose analyzes function signatures to determine skippability.
A composable is deemed skippable if all its parameters are stable. Stable types guarantee that if two instances are equal via equals(), they will never silently mutate over time.
The Compose compiler automatically recognizes primitives, String, enums, and classes with only val properties of stable types as stable.
A major trap in Android development involves standard collections like List or Map. Because Kotlin's List is technically a read-only interface that could be backed by a mutable ArrayList at runtime, the Compose compiler flags it as unstable. Consequently, any composable accepting a raw List cannot be skipped during parent recompositions.
To enable skipping, developers wrap collections inside @Immutable data classes, use Kotlinx Immutable Collections, or leverage strong skipping mode in modern Compose compilers.

## Interview answer — deep senior

Under the hood, skipping behavior is governed by stability inference performed by the Compose Compiler plugin during compilation.
For each composable function, the compiler computes a stability summary for every parameter, assigning it $stable, $unstable, or $dynamic. In the generated bytecode, the compiler inserts change-tracking logic into the synthetic changed bitmask integer. Each parameter occupies 3 bits in the mask, representing states like SAME, DIFFERENT, UNCERTAIN, and STATIC.
When a parent composable recomposes, it evaluates the bitmask. If a parameter is marked unstable, the bitmask is forced to UNCERTAIN, forcing the child function body to execute.
If all parameters are stable and evaluate to SAME (or have STATIC references), the method executes an early return opcode, entirely skipping slot allocation and child tree reconciliation.
In modern Compose compilers (Compose Compiler 1.5.4+ and Kotlin 2.0+), Google introduced Strong Skipping Mode (enabled by default in Kotlin 2.0). Strong skipping relaxes classical stability rules: composables with unstable parameters become skippable if their runtime instances compare equal via instance equality (===) or structural equality (equals).
Furthermore, lambda memoization automatically wraps unstable lambda captures inside remember blocks, dramatically reducing unnecessary recompositions across enterprise Android codebases. Senior engineers inspect compiler metrics using the reportsDestination flag to audit unskippable composables and verify that critical screens achieve predictable, near-zero recomposition overhead.

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
