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

Can the candidate predict safe subtype directions for generic producers and consumers, explain mutable invariance, and use star and use-site projections without claiming that an unknown element type accepts arbitrary writes?

## Concept and technical explanation

Variance describes how subtype relationships interact with generic types. An invariant `Box<T>` does not inherit a subtype relationship from `T`; this protects containers that both read and write. A producer declared `out T` is covariant, so `Source<Dog>` can be used as `Source<Animal>`. A consumer declared `in T` is contravariant, so `Sink<Animal>` can be used as `Sink<Dog>`. A star projection hides the argument: `List<*>` can be read as `Any?`, while `MutableList<*>` cannot accept an arbitrary new element. Kotlin supports declaration-site variance and use-site projections.

## Practical walkthrough (English)

Suppose an Android screen displays animals. A function taking `List<Animal>` can read a `List<Dog>` because Kotlin `List` is covariant. It cannot treat a `MutableList<Dog>` as `MutableList<Animal>`; otherwise it could insert a Cat. For command handling, an `ActionConsumer<Animal>` can accept Dog actions. These are compile-time API relationships, not a substitute for validating external data.

## Explanation in Arabic

الـ Variance بتحدد هل علاقة `Dog : Animal` تنعكس على نوع زي `Box<Dog>` و`Box<Animal>`. الـ Invariance هي الافتراضي: مفيش علاقة Subtyping تلقائية، وده مهم لو الـ Box بتقرأ وتكتب. `out T` معناها إن الواجهة بتنتج `T` في مواضع آمنة، فـ `Source<Dog>` ينفع يتعامل كـ `Source<Animal>`. `in T` لعكس الاتجاه: `Sink<Animal>` تقدر تستقبل أي Dog، فتنفع مكان `Sink<Dog>`. الـ Star Projection زي `List<*>` معناها إن نوع العنصر غير معروف؛ تقدر تقرأ كـ `Any?`، لكن ما تقدرش تفترض نوع أدق أو تضيف عنصر اعتباطي لـ `MutableList<*>`.

## Practical walkthrough

لو عندك `MutableList<Dog>` وسمحت لحد يشوفها كـ `MutableList<Animal>`، هيقدر يضيف `Cat`، وبعدين الكود اللي مستني Dog هيفشل. Kotlin تمنع الإسناد ده. في المقابل، دالة عرض بتقرأ بس من `List<Animal>` ينفع تاخد `List<Dog>` لأن `List` معلنة `out`. ولو عندك `Comparator<Animal>` تقدر تستخدمه لمقارنة Dogs لأنه بيقبل أي Animal.

## Why it matters and how it works

The type checker restricts parameter positions to preserve safe assignments. Declaration-site variance fits an interface with a stable role; a use-site projection limits one particular use of an invariant type. Generic arguments are commonly erased on the JVM, so compile-time variance is not a runtime guarantee that arbitrary casts are safe.

## Worked example

A compact JVM example of covariance:

```kotlin
open class Animal
class Dog : Animal()
interface Source<out T> { fun next(): T }
fun inspect(source: Source<Animal>): Animal = source.next()
val dogs: Source<Dog> = object : Source<Dog> {
    override fun next() = Dog()
}
val animal: Animal = inspect(dogs)
```

The assignment to `inspect` compiles because the interface only produces `T`.

## Trade-offs and decision criteria

Use `out` or `in` when the API has a stable producer or consumer role. Keep a read/write abstraction invariant. Use a projection for a narrower operation. Star projections permit safe inspection at the cost of write precision.

## Failure modes

Casting `MutableList<Dog>` to a wider mutable type can allow incompatible writes. Assuming `MutableList<*>` accepts any element mistakes an unknown type for a permissive type. Unchecked casts and `@UnsafeVariance` can move a design error into runtime.

## Production perspective

Expose read-only state through producer interfaces and actions through consumer interfaces when their actual signatures support variance. Test intended assignment direction with a short compiling example before publishing the API.

## Interview answer — short

Variance controls whether a subtype relationship carries through a generic type. Invariance is the default, which keeps a `MutableList<Dog>` from being used as `MutableList<Animal>` and receiving a Cat. `out` makes a producer covariant; `in` makes a consumer contravariant. A star projection means the type argument is unknown, so I can read safely from `List<*>` but cannot assume arbitrary writes are valid.

## Interview answer — structured

If Dog extends Animal, `Box<Dog>` is not automatically a subtype of `Box<Animal>`. A mutable box could otherwise accept a Cat through the wider reference and break the Dog reader, so the default is invariance.

For a type that produces values, `out T` allows covariance: a `Source<Dog>` can be passed where `Source<Animal>` is expected. For a type that consumes values, `in T` reverses the direction: a `Sink<Animal>` can handle Dogs and can be passed where `Sink<Dog>` is expected. Kotlin `List` is covariant for reading, while `MutableList` stays invariant because it also writes.

A star projection such as `List<*>` means I do not know the element type. I can read an `Any?`, but I cannot treat it as a Dog list or add arbitrary values to a `MutableList<*>`. I use declaration-site variance when the role is stable and a use-site projection for a limited operation.

## Interview answer — deep senior

I start with the mutable-container counterexample. If `MutableList<Dog>` were assignable to `MutableList<Animal>`, a caller could insert a Cat into the same list. A later Dog read would no longer be type-safe. Invariance blocks that assignment at compile time.

`out T` permits a subtype relation for a producer because callers only obtain T in safe positions. A `Source<Dog>` can be used as a `Source<Animal>`. `in T` permits the reverse relationship for a consumer: a `Sink<Animal>` can consume Dogs, so it can fulfill a `Sink<Dog>` contract. Producer-out and consumer-in is a useful shortcut, but I still check the actual signatures and permitted type positions.

Kotlin can declare variance on an interface, or apply a projection at a use site when a particular function only needs one role from an invariant type. With `List<*>`, the argument is unknown and a read gives `Any?`. With `MutableList<*>`, no arbitrary element can be written safely because the real element type is hidden. I do not assume even null is a valid insertion for every list.

On the JVM, generic arguments are generally erased, so variance is checked mainly by the compiler rather than by a complete runtime type descriptor. Calls may still contain casts according to their expected result. That makes unchecked casts or `@UnsafeVariance` narrow escape hatches that need a clear proof, not routine tools to silence a compiler error. I would test the assignment direction with a small compiling example before putting variance into a public API.

## How to answer in the interview

Lead with the Dog/Cat mutable-list counterexample, then state producer-out and consumer-in with assignment directions. Finish with what a star projection lets you read and prevents you from writing.

## Deep-dive talking points

Declaration-site versus use-site projection; `List` versus `MutableList`; unknown element type in `*`; type erasure and unsafe casts.

## Follow-up questions

- **Interviewer:** "Why can `List<Dog>` be passed as `List<Animal>`?" **Answer:** "Kotlin `List` declares `out E`; the caller reads Animals and cannot insert a Cat through that interface."
- **Interviewer:** "Can I add a value to `MutableList<*>`?" **Answer:** "No general element value is safe because the actual type argument is unknown."

## Self-check rubric

Can I predict each assignment direction, reject the mutable-list substitution, and explain the read/write limit of `*`?

## References and reviewed-on date

- [Kotlin generics](https://kotlinlang.org/docs/generics.html).

Technically reviewed against primary documentation on 2026-10-18.
