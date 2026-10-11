---
id: "KOT-09"
question: "What are extension functions? Can they override member functions?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "A"
phase: 1
priority: "P1"
order: 9
editorial_status: "reviewed"
---

# KOT-09

## Original interview question

What are extension functions? Can they override member functions?

## What the interviewer evaluates

Explain static resolution of extensions, member precedence, and their limits as API design tools.

## Explanation in Arabic

Extension function بتدي syntax كأن function عضو في type موجود، من غير تعديل class أو inheritance. الـdispatch بتاعها static حسب declared receiver type، مش runtime subtype. لو class عندها member بنفس الاسم ونفس signature، الـmember يكسب. ده يخلي extensions ممتازة لـpure helpers أو mapping قريبة من type، لكن مش طريقة override لسلوك class أو إضافة state مخفي. nullable receiver extension ممكن تتعامل مع null صراحة.

## Why it matters and how it works

Extensions improve discoverability and keep adapters near a type, but static resolution affects polymorphic expectations. They compile to functions with a receiver parameter on the JVM. Public extensions should have clear names and avoid collisions with future members.

## Worked example

JVM example shows declared-type dispatch.
```kotlin
open class Animal
class Dog : Animal()
fun Animal.sound() = "animal"
fun Dog.sound() = "dog"
fun main() {
    val pet: Animal = Dog()
    println(pet.sound()) // animal: static receiver type
}
```

## Trade-offs and decision criteria

Use extension for focused stateless utilities; use member or interface dispatch when behavior must be polymorphic. An extension cannot access private members unless those are otherwise visible and cannot add stored properties. Excessive global extensions make APIs hard to navigate.

## Failure modes

A team adds `fun User.isAuthorized()` locally and assumes it overrides the model’s member or server policy. It does neither; authorization must be authoritative server-side. A future library member with the same signature can silently change which call resolves.

## Production perspective

A mapper extension converts a Room entity into a domain model within the data module, keeping persistence details out of the domain API. Security checks remain in the server/backend contract, and polymorphic behavior uses an interface.

## Interview answer — short

An extension is statically resolved helper syntax; it does not change a class or override a member. A matching member wins, and overload selection uses the declared receiver type. I use extensions for small stateless adapters.

## Interview answer — structured

`fun User.toUiModel()` looks like a method call but is resolved like a function whose first argument is the receiver. That makes it handy for mappings and formatting without changing a third-party type. It is not virtual dispatch: an extension for a subtype will not be selected through a base-typed reference, and an existing matching member takes precedence. If I need overrideable behavior, I use a member/interface contract. For example, a Room entity mapper is a good extension because it is a stateless conversion near the data layer. If I need a subtype to choose different behavior at runtime, an extension is the wrong tool: a base-typed variable resolves the base extension. I keep extensions scoped and named carefully, especially on broad types such as `String` or `Context`.

## Interview answer — deep senior

I review extensions as part of the module API surface. They should be discoverable, scoped, and named to avoid collisions. Static resolution means they cannot implement polymorphism, and extension properties have no backing field. If an upstream dependency later adds a same-named member, call resolution may change, so broad extensions on common types need extra caution. For Android data mapping, package-local extensions are useful; for security or lifecycle policy, they are not a substitute for explicit ownership. The call syntax looks like a member call, but the compiler resolves an extension against the declared receiver type. That is why `val animal: Animal = Dog()` calls an `Animal` extension even when a `Dog` extension exists. Extensions cannot store per-instance state or bypass private visibility. I use them for small pure adapters, formatting, and mapping, where static dispatch is expected. If I need polymorphism, I define an interface or member method. In Android I also consider package scope and imports: too many generic extensions make it difficult to know which helper is in play. Security policy belongs in an explicit trusted component, not an extension that merely reads nicely.

## Deep-dive talking points

Explain compile-time receiver selection, member priority, nullable receivers, extension properties, and collisions across imports.

## Follow-up questions

- [KOT-23](../kot-23/): Can Java call an extension? **Answer:** yes, as a generated static function subject to JVM naming and imports.
- [KOT-20](../kot-20/): Why does an extension inside a DSL feel like a member? **Answer:** its lambda or extension receiver is implicit, though resolution remains static.

## Self-check rubric

Predict the output for a base-typed subtype, explain member priority, and name one inappropriate polymorphic use.

## References and reviewed-on date

- [Kotlin extensions](https://kotlinlang.org/docs/extensions.html) — static resolution and member precedence.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
