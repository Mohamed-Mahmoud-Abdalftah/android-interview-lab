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

## Concept and technical explanation

Stability in Jetpack Compose is a compile-time and runtime behavioral contract that defines whether a data type guarantees immutable or predictable equality over time. The Compose compiler analyzes all classes and categorizes them as Stable, Immutable, or Unstable. A type is Stable if two instances comparing equal via equals() are guaranteed to notify Compose whenever any internal state mutates, or if the type is completely immutable. Stability directly controls smart skipping: a composable function can be skipped during recomposition only if all of its input parameters are proven Stable. Unstable types force conservative, unconditional recompositions on every frame.

## Practical walkthrough (English)

Inspecting stability categories and fixing unstable data models:
```kotlin
// ❌ UNSTABLE: Contains a mutable 'var' and a raw standard Kotlin List!
// Any composable taking UserProfile will NEVER be skipped!
data class UserProfile(
    var name: String, // 'var' makes class unstable!
    val friends: List<String> // Standard List interface is considered unstable by compiler!
)

// ✅ STABLE / IMMUTABLE: Explicit contract promises compiler data never mutates silently
@Immutable
data class StableUserProfile(
    val name: String, // Immutable val
    val friends: ImmutableList<String> // Kotlinx Immutable Collections guarantee stability!
)

// ✅ Skippable Composable: Both parameters are stable!
@Composable
fun UserCard(
    user: StableUserProfile, // Stable type!
    onFollowClick: () -> Unit // Function types (lambdas) are stable!
) {
    // Compose compiler generates zero-overhead early return skipping for this function!
    Text("User: ${user.name}")
}
```

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

Stability in Compose is a contract indicating whether a type's equality remains predictable over time. Primitives, Strings, function types, and classes with only val properties of stable types are automatically stable. The compiler marks classes with var properties or standard collections like List as unstable because they can mutate silently. A composable can only be skipped if all its parameters are stable. We enforce stability using @Immutable, @Stable, Kotlinx Immutable Collections, or Strong Skipping Mode.

## Interview answer — structured

Stability is the central compiler mechanism determining whether Jetpack Compose can skip re-executing functions during recomposition.
The Compose compiler inspects every type passed as a composable parameter and assigns it a stability classification based on strict contracts.
An Immutable type guarantees that its public properties will never change after instantiation. Primitives, Strings, and data classes with val fields of other immutable types are automatically inferred as immutable.
A Stable type guarantees that if two instances are equal via equals(), they will remain equal unless Compose is explicitly notified of a mutation, such as through a MutableState field.
Any type that violates these guarantees is classified as Unstable.
The most frequent source of instability is Kotlin's standard collection interfaces, like List, Set, or Map. Because List is a read-only interface rather than an immutable collection, a caller could pass a mutable ArrayList behind the scenes.
The Compose compiler cannot verify that the list will not mutate without its knowledge, so it marks any composable receiving a raw List as unskippable.
To resolve this, engineers wrap lists in @Immutable classes, adopt Kotlinx Immutable Collections, or leverage Kotlin 2.0 Strong Skipping Mode.

## Interview answer — deep senior

Under the hood, stability inference is performed by the Compose Compiler plugin during the Kotlin frontend IR lowering phase.
The compiler analyzes class declarations and appends synthetic metadata markers, assigning a $stable bit flag to stable classes.
When a composable function is compiled, the compiler inspects every parameter's stability flag. If all parameters are stable, the compiler generates a change-tracking bitmask check at the beginning of the function body.
During recomposition, if the bitmask indicates that all stable parameters evaluate to SAME or have STATIC references, the method executes an early-return opcode, skipping function body execution and avoiding all SlotTable reads and allocations.
If even a single parameter is marked unstable, the compiler flags the parameter as UNCERTAIN. In standard skipping mode, this forces the composable to execute unconditionally, even if the underlying data has not changed.
In modern Compose compilers (Kotlin 2.0+), Google introduced Strong Skipping Mode, enabled by default.
Strong skipping transforms this behavior by allowing composables with unstable parameters to be skipped if their instances compare equal via structural equality (equals()).
Furthermore, developers can configure compiler stability configuration files (stability_config.conf) to mark external third-party classes (like java.time.Instant or external network DTOs) as stable without adding annotations to foreign libraries.

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
