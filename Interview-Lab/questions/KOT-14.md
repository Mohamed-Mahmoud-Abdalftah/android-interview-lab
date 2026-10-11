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

## Trade-offs and decision criteria

Declare variance on interfaces with stable producer/consumer roles. Use a projection at a method boundary when the role is temporary. Avoid casts to force subtype relationships; they can move a type error to runtime. Star projections are useful for introspection but sacrifice write precision.

## Failure modes

A mutable `Box<Cat>` treated as `Box<Animal>` would allow inserting a Dog, breaking the Cat reader. Kotlin invariance prevents this. Another mistake is assuming `List<*>` permits arbitrary additions; its element type is unknown.

## Production perspective

A repository returns `Flow<out DomainEvent>`-like producer contracts where consumers only read events; command handlers accept contravariant processors. Public APIs name producer/consumer roles rather than leaking mutable generic containers.

## Interview answer — short

`out` is covariance for producers, `in` is contravariance for consumers, and invariant types allow neither substitution. A star projection represents an unknown type under its bounds. These rules prevent unsafe writes.

## Interview answer — structured

If a generic API only produces `T`, `out T` can safely expose a producer of Cats where Animals are expected. If it only consumes `T`, `in T` works in the opposite direction. Mutable containers generally need invariance because they both read and write. Star projections say the type argument is unknown, so callers have limited operations. I use variance to express the API contract, not to silence compiler errors. A mutable container both accepts and returns elements, and invariance prevents inserting a Dog into storage meant for Cats. Star projection says the element type is unknown under its bounds; it does not license arbitrary writes. In a repository API, I would expose a read-only producer to callers and keep mutable storage private. That expresses which direction data travels without pretending it is deeply immutable.

## Interview answer — deep senior

I reason from positions: returning `T` is an output, accepting `T` is an input. Covariance and contravariance are safe only when the type appears in the permitted positions, subject to language rules. Declaration-site variance is ideal for a stable interface role; use-site projections express a role for one call. Star projection is bounded existential typing, not an untyped escape hatch. In Android APIs, exposing read-only producers helps avoid leaking mutable state, but it does not itself make the values immutable or thread-safe. I reason about variance from allowed operations, not from the class names. If an interface only returns `T`, `out T` is safe: callers asking for Animals can use a Cat source. If it only accepts `T`, `in T` is safe in the opposite direction: an Animal handler can process Cats. A mutable list must support both read and write, so making it covariant would permit type corruption. A star projection hides the precise argument but retains its bound, restricting what can be written. In Android I use this to keep repository producers flexible while keeping mutation private, and I remember that type-safe variance does not imply immutability or synchronization. The compiler checks variance positions but cannot guarantee that the produced object is immutable or safe to share across threads. I combine generic type safety with explicit ownership and concurrency contracts. That matters when a Flow or repository exposes collections to multiple UI collectors.

## Deep-dive talking points

Explain PECS-style producer/consumer reasoning, type erasure, use-site projections, and why mutable lists are invariant.

## Follow-up questions

- [KOT-16](../kot-16/): Why can `List<Cat>` be viewed as `List<Animal>`? **Answer:** read-only `List` is covariant in its element type.
- [KOT-21](../kot-21/): Does a value class change generic variance? **Answer:** no; it affects representation, not subtype rules.

## Self-check rubric

Predict safe assignment direction for producer and consumer, reject a mutable-container cast, and describe one star-projection limitation.

## References and reviewed-on date

- [Kotlin generics](https://kotlinlang.org/docs/generics.html) — variance and star projections.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
