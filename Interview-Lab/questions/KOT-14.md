---
id: "KOT-14"
question: "Explain Kotlin variance: in, out, invariance, and star projections."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 14
editorial_status: "reviewed"
---

# KOT-14

## Original interview question

Explain Kotlin variance: in, out, invariance, and star projections.

## What the interviewer evaluates

Apply producer/consumer variance safely, distinguish declaration/use-site variance and star projections.

## Explanation in Arabic

الـ Generics والـ Variance في Kotlin بتحدد إزاي الأنواع الفرعية (Subtypes) بتتعامل لما تتغلف جوه Generics:

1. الـ Invariance (الوضع الافتراضي):
   لو `Dog` بترث من `Animal`، فـ `List<Dog>` **مش** Subtype من `List<Animal>`. ده لمنع كوارث زي كتابة `Cat` جوه قائمة `Dogs`!

2. الـ Covariance (`out`):
   - الكلاس بيعمل **إنتاج للبيانات فقط (Producer Only)**.
   - الـ `out T` بتسمح إن `List<Dog>` تكون Subtype من `List<Animal>`.
   - القاعدة: تقدر تقرأ `T` (Return Type)، لكن مستحيل تدخله كـ Parameter (ممنوع في الـ `in` position). مثال: `List<out E>` في Kotlin هي Read-Only.

3. الـ Contravariance (`in`):
   - الكلاس بيعمل **استهلاك للبيانات فقط (Consumer Only)**.
   - الـ `in T` بتعكس العلاقة: `Comparable<Animal>` بتعتبر Subtype من `Comparable<Dog>` (لأن اللي يقدر يقارن أي حيوان يقدر يقارن الكلاب بالتأكيد).
   - القاعدة: تقدر تمرر `T` كـ Parameter، لكن مينفعش ترجعه.

4. الـ Star Projection (`*`):
   بتستخدمها لما متعرفش أو ميهمكش النوع الدقيق للـ Generic (زي `List<*>`)؛ ده بيعادل `List<out Any?>`، يعني تقدر تقرأ منها بأمان كـ `Any?` لكن مستحيل تكتب فيها.

## Practical walkthrough

في معمارية أندرويد:
- الـ StateFlow والـ LiveData هي Covariant (`StateFlow<out T>`): ده بيسمح إن `StateFlow<UserUiState.Success>` تتمرر لدالة مستنية `StateFlow<UserUiState>` بدون أي مشاكل.
- في الـ Repository، واجهة القراءة فقط بنعمل لها Covariant:
  `interface ReadOnlyRepository<out T> { fun getById(id: String): T }`
- بينما الـ Serializer أو الـ Consumer بنعمل له Contravariant:
  `interface JsonWriter<in T> { fun write(item: T): String }`
- الخطأ الشائع: محاولة وضع دالة `fun update(item: T)` داخل واجهة متعلمة بـ `out T`؛ المترجم هيرفض البناء فوراً: "Type parameter T is declared as 'out' but occurs in 'in' position".

## Why it matters and how it works

Variance lets an API expose flexible subtyping without runtime corruption. Read-only producers and write-only consumers have different safe directions. Use-site projections help when the generic type itself is invariant but one operation has a limited role.

## Worked example

Runnable JVM illustration: a source of cats can be consumed as a source of animals.
```kotlin
open class Animal
class Cat : Animal()
interface Source<out T> { fun get(): T }
class CatSource : Source<Cat> { override fun get() = Cat() }
fun inspect(source: Source<Animal>) = println(source.get() is Cat)
fun main() = inspect(CatSource())
```

## Trade-offs and decision criteria

Declare variance on interfaces with stable producer/consumer roles. Use a projection at a method boundary when the role is temporary. Avoid casts to force subtype relationships; they can move a type error to runtime. Star projections are useful for introspection but sacrifice write precision.

## Failure modes

A mutable `Box<Cat>` treated as `Box<Animal>` would allow inserting a Dog, breaking the Cat reader. Kotlin invariance prevents this. Another mistake is assuming `List<*>` permits arbitrary additions; its element type is unknown.

## Production perspective

A repository returns `Flow<out DomainEvent>`-like producer contracts where consumers only read events; command handlers accept contravariant processors. Public APIs name producer/consumer roles rather than leaking mutable generic containers.

## Interview answer — short

Variance governs subtyping of generic types. Invariant types require exact type matches. Covariant (out) types are producers that allow subtypes (List<Dog> is a subtype of List<Animal>) but restrict T from input positions. Contravariant (in) types are consumers that reverse subtyping (Comparable<Animal> is a subtype of Comparable<Dog>) and restrict T from return positions. Star projection represents unknown types safely.

## Interview answer — structured

Variance defines how subtyping between base types relates to subtyping between generic types parameterized by them.

By default, generics in Kotlin are invariant: a MutableList of Dog is not a subtype of MutableList of Animal, which prevents adding a Cat to a list of Dogs.

When a class only produces data, we mark it covariant using out. For example, Kotlin's read-only List is declared as List<out E>. This allows a List of Dog to be passed wherever a List of Animal is expected, but the compiler forbids E in parameter input positions.

Conversely, when a class only consumes data, we mark it contravariant using in, like Comparable<in T>. This inverts subtyping: a comparator that handles all Animals can safely be used to compare Dogs.

Star projection (*) is used when the type argument is unknown, safely allowing reads as Any? while preventing writes.


## Interview answer — deep senior

Kotlin's variance system improves on Java's wildcard generics (? extends T and ? super T) by supporting declaration-site variance. In Java, variance must be repeated at every call site (e.g., List<? extends Animal>). In Kotlin, we declare variance on the interface definition itself (e.g., interface Source<out T>), and all call sites automatically inherit covariant subtyping without wildcard annotations.

Kotlin still supports use-site variance (type projections) for invariant classes like Array or MutableList. Writing copy(from: Array<out Any>, to: Array<in Any>) applies Java-style PECS (Producer Extends, Consumer Super) at specific call sites.

Under the hood, declaration-site variance is enforced strictly by the compiler's position checker. If a type parameter is marked out, it can only appear in output positions (return types, read-only property types). If marked in, it can only appear in input positions (method parameters). If an out type parameter genuinely needs to be accepted in an internal private method or constructor, it must be annotated with @UnsafeVariance to bypass compiler checks, a technique used carefully inside Kotlin's standard library collections.


## How to answer in the interview

- **Why:** Preserve type safety in generic collections and interfaces while enabling flexible subtyping.
- **How:** Use declaration-site variance: `out` for producers (covariance) and `in` for consumers (contravariance).
- **Trade-offs:** Covariant types (`out T`) cannot accept `T` as a method argument; contravariant types (`in T`) cannot return `T`.
- **Failure cases:** Bypassing variance rules via `@UnsafeVariance` incorrectly, causing `ClassCastException` at runtime when writing incompatible types to a collection.
- **Production solution:** Design read-only domain interfaces as covariant (`Producer<out T>`) and event/sink handlers as contravariant (`Consumer<in T>`), using star projections (`*`) when element type is irrelevant.

## Deep-dive talking points

Explain PECS-style producer/consumer reasoning, type erasure, use-site projections, and why mutable lists are invariant.

## Follow-up questions

- **Interviewer:** "Why is Kotlin's `List<T>` covariant (`out T`), while `MutableList<T>` is invariant?"
  **Answer:** "`List<T>` is read-only, meaning it only produces items. Passing `List<Dog>` to a function expecting `List<Animal>` is completely type-safe because callers can only read `Animal` instances. `MutableList<T>` allows writing: if `MutableList<Dog>` could be passed as `MutableList<Animal>`, a caller could add a `Cat` to it, crashing the app when retrieving a `Dog` later."

- **Interviewer:** "What is the difference between `List<*>` and `List<Any>`?"
  **Answer:** "`List<Any>` requires a list parameterized specifically with `Any` (or subtypes if covariant). `List<*>` represents a list of an unknown type. You can read from `List<*>` safely as `Any?`, but you cannot add anything into it (except null, if permitted). It acts as an abstraction over any list type regardless of its generic argument."

- **Interviewer:** "What is `@UnsafeVariance`, and why is it used in `Collection.contains(element: @UnsafeVariance E)`?"
  **Answer:** "In `Collection<out E>`, `E` is covariant. However, `contains(element: E)` takes `E` in an input position, which violates covariance rules. In reality, `contains` only reads the element to call `.equals()` and never mutates the collection. `@UnsafeVariance` suppresses the compiler error where the author mathematically proves that the operation is safe."

## Self-check rubric

Predict safe assignment direction for producer and consumer, reject a mutable-container cast, and describe one star-projection limitation.

## References and reviewed-on date

- [Kotlin generics](https://kotlinlang.org/docs/generics.html) — variance and star projections.

Technically reviewed against primary documentation on 2026-10-13.
