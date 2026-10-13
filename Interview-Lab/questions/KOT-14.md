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

Generics افتراضيًا invariant: `Box<Cat>` مش `Box<Animal>` تلقائيًا. `out T` يعني API تنتج `T` للمستهلك ولا تقبل `T` في موضع غير آمن، فـ`Source<Cat>` ينفع يتشاف `Source<Animal>`. `in T` عكسها للـconsumer: معالج Animals يقدر يعالج Cats. `*` star projection معناه “النوع مجهول ضمن الحدود المعلنة”، مش `Any` مجاني؛ القراءة والكتابة المتاحة بتتحدد حسب variance والbound. قواعد `in/out` تمنع إدخال Animal في collection مفروض كلها Cats.

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

## Practical walkthrough

في repository API، `Source<out User>` ينفع يرجّع subtype من User لأن caller بيقرأ فقط. `Sink<in User>` ينفع يستقبل subtype لأن handler لـUser يقدر يتعامل مع AdminUser. `MutableList<User>` بتقرأ وتكتب، فلو سمحت بتبديل `MutableList<AdminUser>` مكانها هتقدر تضيف User عادي وتكسر reader. `List<*>` نافعة لما النوع مش معروف، لكن ما تقدرش تضيف عنصر arbitrary؛ القراءة بحدود الـupper bound. في code review ارسم سهم: T بيخرج ولا بيدخل؟ وبعدها اختار declaration-site variance، أو projection محلي لو الدور خاص بmethod واحدة.

## Trade-offs and decision criteria

Declare variance on interfaces with stable producer/consumer roles. Use a projection at a method boundary when the role is temporary. Avoid casts to force subtype relationships; they can move a type error to runtime. Star projections are useful for introspection but sacrifice write precision.

## Failure modes

A mutable `Box<Cat>` treated as `Box<Animal>` would allow inserting a Dog, breaking the Cat reader. Kotlin invariance prevents this. Another mistake is assuming `List<*>` permits arbitrary additions; its element type is unknown.

## Production perspective

A repository returns `Flow<out DomainEvent>`-like producer contracts where consumers only read events; command handlers accept contravariant processors. Public APIs name producer/consumer roles rather than leaking mutable generic containers.

## Interview answer — short

`out T` is safe for producers, `in T` for consumers, and a type that both reads and writes is usually invariant. A star projection represents an unknown type under its bounds. I choose variance from the operations an API permits.

## Interview answer — structured

I reason in terms of data direction. A `Source<out T>` only gives values, so a source of Cats can serve a caller expecting Animals. A `Sink<in T>` accepts values, so an Animal sink can process Cats. A mutable box does both; allowing covariance there would let someone insert a Dog into a Cat box. Kotlin therefore defaults generic parameters to invariance. A star projection says the exact argument is unknown and restricts writes; it is not an unchecked `Any`. In a repository API I expose read-only producer contracts and keep mutation behind an owner, while remembering that variance does not make objects immutable or thread-safe.

## Interview answer — deep senior

I reason from positions: returning `T` is an output, accepting `T` is an input. Covariance and contravariance are safe only when the type appears in the permitted positions, subject to language rules. Declaration-site variance is ideal for a stable interface role; use-site projections express a role for one call. Star projection is bounded existential typing, not an untyped escape hatch. In Android APIs, exposing read-only producers helps avoid leaking mutable state, but it does not itself make the values immutable or thread-safe.

I would demonstrate the safety proof with a mutable box. If `Box<Cat>` could become `Box<Animal>`, another caller could insert a Dog, and the original Cat reader would fail. A read-only `Source<out T>` avoids that write, while `Sink<in T>` accepts values in the opposite direction. In a repository I use declaration-site variance for an interface whose role is stable; I use a projected parameter for a single operation on an otherwise invariant type. Star projection lets inspection code read only to its bound and blocks arbitrary writes. It does not make the underlying values immutable.

## How to answer in the interview

- **Why:** Preserve type safety in generic collections and interfaces while enabling flexible subtyping.
- **How:** Use declaration-site variance: `out` for producers (covariance) and `in` for consumers (contravariance).
- **Trade-offs:** Covariant types (`out T`) cannot accept `T` as a method argument; contravariant types (`in T`) cannot return `T`.
- **Failure cases:** Bypassing variance rules via `@UnsafeVariance` incorrectly, causing `ClassCastException` at runtime when writing incompatible types to a collection.
- **Production solution:** Design read-only domain interfaces as covariant (`Producer<out T>`) and event/sink handlers as contravariant (`Consumer<in T>`), using star projections (`*`) when element type is irrelevant.

## Deep-dive talking points

Explain PECS-style producer/consumer reasoning, type erasure, use-site projections, and why mutable lists are invariant.

## Follow-up questions

- [KOT-16](../kot-16/): Why can `List<Cat>` be viewed as `List<Animal>`? **Answer:** read-only `List` is covariant in its element type.
- [KOT-21](../kot-21/): Does a value class change generic variance? **Answer:** no; it affects representation, not subtype rules.

## Self-check rubric

Predict safe assignment direction for producer and consumer, reject a mutable-container cast, and describe one star-projection limitation.

## References and reviewed-on date

- [Kotlin generics](https://kotlinlang.org/docs/generics.html) — variance and star projections.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
