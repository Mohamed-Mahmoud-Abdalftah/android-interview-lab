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

ماذا يعني استقرار الأنواع والبارامترات (Type & Parameter Stability) في Jetpack Compose؟

1. العقد الأساسي للاستقرار (Stability Contract):
   - الـ Compose Compiler يفحص كل نوع (Class / Interface) ويصنفه ليحدد ما إذا كان يمكنه **تخطي (Skip)** الـ Composable أثناء إعادة التركيب أم لا.
   - الشروط الثلاثة للنوع المستقر (Stable):
     * نتيجة مقارنة `equals()` بين كائنين متماثلين تعطي دائماً نفس النتيجة لنفس الكائنات.
     * إذا تغيرت خاصية عامة في الكائن، يُشعر الكائن محرك Compose بالتغيير (عبر `SnapshotState`).
     * كل الحقول العامة للكائن من أنواع مستقرة أيضاً.

2. تصنيفات المترجم الثلاثة:
   - **`@Immutable`**: نوع ثابت لا يتغير أبداً بعد إنشائه؛ جميع حقوله `val` من أنواع بدائية أو Immutable. يقدم أعلى درجات التحسين والتخطي.
   - **`@Stable`**: نوع قد يحتوي على خصائص متغيرة، ولكنه يضمن إشعار Compose عند حدوث أي تعديل (مثل كائن يحمل `mutableStateOf`).
   - **`Unstable`**: أي كائن يحتوي على حقول `var` عادية، أو واجهات (Interfaces)، أو مجموعات كوتلن القياسية مثل `List<T>` (لأن الـ `List` قد تكون في الحقيقة `ArrayList` قابلة للتعديل خلف الستار!).

3. الحلول العملية لمشكلة الـ Unstable Types:
   - استخدام **Kotlinx Immutable Collections** (`ImmutableList<T>`, `PersistentList<T>`).
   - وسم الـ Data Classes الخارجية أو الـ Models بـ `@Immutable` صراحة.
   - الاعتماد على **Strong Skipping Mode** المتاح في المترجم الحديث لتخطي الكائنات بالمرجع.

## Practical walkthrough

جعل الكائنات مستقرة وإصلاح عدم الاستقرار في Data Models:
```kotlin
// ❌ كائن غير مستقر: المترجم يعتبره Unstable بسبب List و var:
data class BadUserModel(
    val id: String,
    val tags: List<String>, // List هي Interface غير مضمونة الثبات للمترجم!
    var score: Int // وجود var يجعل الكائن Unstable فوراً!
)

// ✅ كائن مستقر بنسبة 100% ويقبل التخطي الذكي (Skippable):
import androidx.compose.runtime.Immutable
import kotlinx.collections.immutable.ImmutableList

@Immutable
data class GoodUserModel(
    val id: String,
    val tags: ImmutableList<String>,
    val score: Int
)
```

## Why it matters and how it works

Stability information helps Compose determine whether a recomposed parent can skip a child call with unchanged parameters. Stable values use equality semantics under documented compiler modes; unstable values may be compared by identity with strong skipping. Compiler settings and versions matter, so an absolute claim that any unstable type always recomposes is unsafe. Skipping has comparison and bookkeeping cost; correctness requires that changes affecting UI be observable.

## Worked example

`UserCard(model: UserUiModel)` receives a data class with immutable `id` and `displayName`; equivalent updates may be skipped depending on compiler inference. A `MutableUser` class changes `displayName` in place without Compose state: annotating it `@Stable` can suppress an update while showing stale text. Instead emit a new immutable UI model or use observable state in a carefully owned state holder.

### Compose/Kotlin walkthrough

```kotlin
// Immutable UI input; a changed price creates a new instance.
data class ProductUi(val id: String, val title: String, val priceLabel: String)
@Composable
fun ProductRow(product: ProductUi) {
    Text("${product.title} · ${product.priceLabel}")
}
// Owner: ui.value = ui.value.copy(product = old.product.copy(priceLabel = "EGP 120"))
// Avoid: @Stable class ProductUi(var priceLabel: String) with an unobserved var.
```

## Trade-offs and decision criteria

Immutable models simplify reasoning and testing, but copying a large tree can cost allocations. Stable mutable objects can work if every public UI-affecting change is observable, a hard contract to maintain. Strong skipping may already handle an unstable parameter effectively when the same instance is passed; adding annotations blindly can trade cheap identity checks for expensive equality checks.

## Failure modes

A false stability annotation hides updates. A collection is mutated in place and no new state emission occurs. A team optimizes skip counts while the real frame cost is image loading or layout. Compiler reports are interpreted without checking active strong-skipping mode and version.

## Production perspective

Diagnose measured jank first, inspect compiler stability reports for the affected composable, and test that changed fields render correctly. Benchmark any model or annotation change on a release build before spreading it across the design system.

## Interview answer — short

In Compose, type stability determines whether a composable can be skipped during recomposition. An `@Immutable` type never mutates; a `@Stable` type notifies Compose if it mutates. Unstable types—such as classes with mutable `var` properties or standard Kotlin `List<T>`—force recomposition of the composables that accept them.

## Interview answer — structured

Type stability is the core contract that governs the Compose Compiler's smart skipping optimization.

When a parent composable recomposes, Compose evaluates child composables. If all parameters passed to a child are **Stable** and their values evaluate as equal via `equals()`, Compose skips re-executing that child composable entirely.

The compiler infers stability into three categories.

First, with Immutable (`@Immutable`), all public properties are `val` and their types are also immutable. The object's state is guaranteed never to change post-creation (e.g. Primitives, `String`, or annotated data classes). Next, stable (`@Stable`) is the object may be mutable, but it guarantees that any state mutations notify the composition (such as holding `mutableStateOf` properties).
Finally, with Unstable, any class containing public `var` properties, external multi-module classes uncompiled by the Compose compiler plugin, or standard Kotlin collection interfaces (`List`, `Set`, `Map`). Because `List<T>` is an interface that could hide a mutable `ArrayList`, Compose assumes it can change without notification, marking any composable accepting it as unskippable.


## Interview answer — deep senior

To resolve collection instability in production architectures, teams historically wrapped lists in `@Immutable data class ImmutableHolder<T>(val items: List<T>)` or adopted `kotlinx.collections.immutable` (`ImmutableList<T>`). Annotating domain entities with `@Immutable` promises the compiler that callers will treat the model as immutable, allowing full skipping.

In recent releases, Compose introduced **Strong Skipping Mode** (standard in Kotlin 2.0+). Under strong skipping, composables with unstable parameters *can* still be skipped if the instance reference has not changed (`===`), and lambdas with captures are automatically remembered. However, if a new instance of an unstable class is passed—even with identical data—it still forces recomposition.

We audit stability using Compose Compiler metrics (`./gradlew assembleRelease -PcomposeCompilerReports=true`), inspecting the generated `-classes.txt` and `-composables.txt` files to eliminate any accidental stability regressions.


## How to answer in the interview

- **Why:** skipping relies on knowing whether inputs changed.
- **How:** contrast immutable replacement with an unobserved mutable field.
- **Trade-off:** equality checks and annotations also have cost.
- **Failure case:** a false @Stable promise leaves stale UI.
- **Production solution:** inspect compiler reports under the project’s Compose version, then profile frames.

## Deep-dive talking points

Discuss inference, observability, strong skipping, identity versus equality, false annotations, and benchmark evidence.

## Follow-up questions

- **Interviewer:** "Why is standard `List<T>` considered unstable by the Compose Compiler?"
  **Answer:** "`List<T>` in Kotlin is a read-only interface, not an immutable one. At runtime, the backing implementation may be a mutable `ArrayList` whose contents could change without altering the list reference, so Compose cannot safely skip."

- **Interviewer:** "How do you enable Strong Skipping Mode in Kotlin 2.0+?"
  **Answer:** "In Kotlin 2.0+, Strong Skipping Mode is enabled by default in the new Jetpack Compose Compiler Gradle plugin, though explicit stability annotations remain best practice for cross-module boundary optimization."

## Self-check rubric

Define the contract, explain one stale-UI bug, account for strong skipping, and propose a measured fix.

## References and reviewed-on date

- [Stability in Compose](https://developer.android.com/develop/ui/compose/performance/stability) — type contract.
- [Strong skipping mode](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping) — version-sensitive skip rules.

Technically reviewed against primary documentation on 2026-10-13.
