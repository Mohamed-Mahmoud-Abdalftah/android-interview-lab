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

Compose stability is a contract about whether changes to a type can be observed, which helps the compiler decide whether an eligible child call can be skipped when its parent recomposes. Immutable values do not change after construction; stable mutable values must notify Compose about UI-affecting changes. Standard Kotlin collection interfaces are considered unstable because a read-only type does not guarantee an immutable backing object. In strong skipping mode, enabled by default from Kotlin 2.0.20, eligible composables may still be skipped with unstable parameters: stable values use equality and unstable values use instance identity. Stability does not mean that an entire screen recomposes on every frame, and a false @Stable or @Immutable promise can leave stale UI.

## Practical walkthrough (English)

A product row receives an immutable UI model. Updating the price produces a new model, so Compose can observe the state change. If code instead mutates an ordinary `var` on the same instance without Snapshot State, the UI may not update; adding `@Stable` does not fix that and may make the bug harder to notice. Inspect the compiler report for the project version and measure frames before changing collection types. This is a conceptual scenario, not an executable snippet.

## Explanation in Arabic

لما Parent Composable تعمل Recomposition، Compose بتقرر هل لازم تنفّذ Child تاني ولا تقدر تعمل Skip. Stability بتساعدها تعرف إذا كان الـ Parameter اتغير بطريقة ممكن تلاحظها. `Immutable` يعني القيمة اللي الـ UI بيشوفها مش هتتغير بعد الإنشاء؛ `Stable` ممكن يتغير، لكن أي تغيّر مؤثر لازم Compose تعرفه، زي `MutableState`. لو Compiler مش قادر يثق في العقد، النوع يبقى `Unstable`.

`List<T>` في Kotlin Read-only Interface، مش ضمان إن الـ Backing Collection مش هتتعدل؛ عشان كده Compose بتعامل الـ Collections القياسية كـ Unstable. وسم كلاس بـ `@Immutable` أو `@Stable` وعد منك للمترجم، مش تحويل سحري للبيانات. لو الوعد غلط، ممكن الـ UI تعرض قيمة قديمة.

في Strong Skipping، اللي بقى Default من Kotlin 2.0.20، Composable مؤهلة للتخطي ممكن تتخطى حتى مع Unstable Parameters: المستقرة بتتقارن بـ `equals`، وغير المستقرة بالـ Instance Identity (`===`). ده مش معناه إن كل Recomposition اتلغت أو إن كل Child لازم تتنفذ كل Frame؛ لازم تشوف نسخة Compiler والـ Reports والقياس.

## Practical walkthrough

شاشة منتجات بتعرض `ProductRow(product)`. لو `product` موديل Immutable وبعت نفس القيمة، Compose ممكن تعمل Skip لما الـ Parent تتنفذ تاني. لو عندك `MutableList` وغيرت عنصر فيها في مكانه من غير State Update، المشكلة مش مجرد Recomposition زيادة؛ ممكن الـ UI أصلًا ما تعرفش إن البيانات اتغيرت. الحل العملي: اعمل State Update بقيمة جديدة، أو استخدم State Holder واضح بيبلّغ Compose. بعد كده بص على Compiler Reports وقياس Frames قبل ما تضيف Annotations أو تغيّر Collection Library.

## Why it matters and how it works

Stability information helps Compose determine whether a recomposed parent can skip a child call with unchanged parameters. Stable values use equality semantics under documented compiler modes; unstable values may be compared by identity with strong skipping. Compiler settings and versions matter, so an absolute claim that any unstable type always recomposes is unsafe. Skipping has comparison and bookkeeping cost; correctness requires that changes affecting UI be observable.

## Worked example

`UserCard(model: UserUiModel)` receives a data class with immutable `id` and `displayName`; equivalent updates may be skipped depending on compiler inference. A `MutableUser` class changes `displayName` in place without Compose state: annotating it `@Stable` can suppress an update while showing stale text. Instead emit a new immutable UI model or use observable state in a carefully owned state holder.

### Compose/Kotlin walkthrough

Conceptual Compose sketch; imports and the surrounding app state are omitted.

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

Stability is Compose’s contract for whether changes to a parameter are observable. Immutable values do not change; stable mutable values notify Compose when UI-visible properties change. Standard Kotlin List is considered unstable because read-only does not guarantee immutable backing storage. Strong skipping can still skip eligible composables with unstable parameters by comparing instance identity. A false @Stable annotation can leave stale UI, so verify correctness before tuning skip rates.

## Interview answer — structured

Stability tells Compose whether it can trust that a parameter has not changed in a way that affects UI. An immutable model cannot change after construction; a stable mutable holder must make UI-affecting changes observable, for example through Snapshot State. Standard List is considered unstable because a read-only reference may point at a mutable collection.

When a parent recomposes, this information helps decide whether an eligible child call can be skipped. With strong skipping in current compiler versions, an unstable parameter can still allow skipping when the same instance is passed; the compiler compares stable values by equality and unstable values by identity.

A product price changed in place on an ordinary `var` may never notify Compose. Marking the class @Stable just to improve a report can hide that bug. Emit a new immutable UI model or use a state holder whose changes Compose observes. Then inspect compiler reports and measure actual frame cost before adding annotations or immutable collection dependencies.

## Interview answer — deep senior

Compose invalidation follows observed state reads; it does not rerun an entire screen on every frame by default. If a parent recomposes, an eligible child call may be skipped when the compiler sees unchanged parameters. Stability describes the observability contract behind that decision. Immutable models never change their public UI-visible values; stable mutable holders notify the runtime when those values change.

Standard Kotlin collections are inferred unstable because List, Set, and Map interfaces do not promise that the backing collection cannot mutate. This does not by itself mean every call is expensive. Strong skipping, enabled by default starting with Kotlin 2.0.20, allows eligible composables with unstable parameters to skip using instance identity. Stable parameters use equality. Exact behavior depends on compiler mode and the composable’s restartability, so claims that unstable parameters always rerun or that @Immutable guarantees performance are too broad.

Suppose a product model contains an ordinary mutable price field. Mutating it in place without Snapshot State may leave UI stale. A false @Stable annotation makes the contract even less reliable. Prefer a new immutable UI value or a carefully owned state holder with observable mutations. Immutable collections and stability configuration can help in some cases, but they add contracts the team must uphold. First test that changed values render, then inspect reports for the actual build and benchmark frames before and after the proposed change.

## How to answer in the interview

- **Why:** skipping relies on knowing whether inputs changed.
- **How:** contrast immutable replacement with an unobserved mutable field.
- **Trade-off:** equality checks and annotations also have cost.
- **Failure case:** a false @Stable promise leaves stale UI.
- **Production solution:** inspect compiler reports under the project’s Compose version, then profile frames.

## Deep-dive talking points

Discuss inference, observability, strong skipping, identity versus equality, false annotations, and benchmark evidence.

## Follow-up questions

- **Interviewer:** "Why is List<T> unstable?"
  **Answer:** "Kotlin List is a read-only interface, not proof that the backing collection is immutable. Compose cannot assume external code will not mutate it."

- **Interviewer:** "Does an unstable parameter always prevent skipping?"
  **Answer:** "No. With strong skipping enabled, an eligible composable can be skipped when the same unstable instance is passed. Check the compiler version and reports."

- **Interviewer:** "Should we annotate every model @Stable?"
  **Answer:** "No. The annotation is a contract. An unobserved mutable field can leave stale UI if that contract is false; test correctness and profile first."

## Self-check rubric

Define the contract, explain one stale-UI bug, account for strong skipping, and propose a measured fix.

## References and reviewed-on date

- [Stability in Compose](https://developer.android.com/develop/ui/compose/performance/stability) — observability contract.
- [Strong skipping mode](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping) — version and comparison rules.
- [Fix stability issues](https://developer.android.com/develop/ui/compose/performance/stability/fix) — collections and configuration.

Technically reviewed against primary documentation on 2026-10-19.
