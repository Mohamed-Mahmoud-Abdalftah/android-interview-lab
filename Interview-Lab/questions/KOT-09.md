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

## Practical walkthrough

لو عندك `fun Animal.sound()` و`fun Dog.sound()`، المتغير المعلن `Animal` هيختار extension بتاعة Animal حتى لو runtime object نوعه Dog. ده لأن extensions static resolution، ومش بتغيّر class bytecode من جواها. لو class نفسها فيها member بنفس الاسم والتوقيع، member تكسب. استخدم extension لتحويلات صغيرة قريبة من feature، مش لإخفاء business behavior لازم يكون polymorphic. في multi-module project، import لامتداد بنفس الاسم ممكن يغيّر resolution أو يخلق ambiguity؛ خليه discoverable ومسمى بوضوح.

## Trade-offs and decision criteria

Use extension for focused stateless utilities; use member or interface dispatch when behavior must be polymorphic. An extension cannot access private members unless those are otherwise visible and cannot add stored properties. Excessive global extensions make APIs hard to navigate.

## Failure modes

A team adds `fun User.isAuthorized()` locally and assumes it overrides the model’s member or server policy. It does neither; authorization must be authoritative server-side. A future library member with the same signature can silently change which call resolves.

## Production perspective

A mapper extension converts a Room entity into a domain model within the data module, keeping persistence details out of the domain API. Security checks remain in the server/backend contract, and polymorphic behavior uses an interface.

## Interview answer — short

Extensions add convenient call syntax without changing the class. They resolve from the declared receiver type, so they do not override virtual members; a matching member takes precedence. I use them for local helpers, not polymorphic behavior.

## Interview answer — structured

An extension looks like a method call but compiles as a statically resolved function. If a variable is declared `Animal` and holds a `Dog`, `animal.sound()` selects the `Animal` extension. A real member with a matching signature wins over an extension. This makes extensions useful for formatting or mapping third-party types while keeping call sites readable. It also makes them a poor choice for subtype-specific behavior. In a large codebase I scope imports and names carefully, because extensions are discovered through imports and competing names can make an API hard to understand.

## Interview answer — deep senior

I review extensions as part of the module API surface. They should be discoverable, scoped, and named to avoid collisions. Static resolution means they cannot implement polymorphism, and extension properties have no backing field. If an upstream dependency later adds a same-named member, call resolution may change, so broad extensions on common types need extra caution. For Android data mapping, package-local extensions are useful; for security or lifecycle policy, they are not a substitute for explicit ownership.

In a payment or account policy, polymorphism must be expressed by a member, interface, or explicit `when`, because an extension selected from the declared receiver type cannot vary with the runtime subtype. A helper like `ApiUser.toDomain()` is a good extension if it stays near the mapping module and does not hide I/O. I would avoid a global `String.isValid()` extension whose meaning changes across features. A dependency adding a same-named member can also alter call resolution, so I keep extension names precise and test public library calls after upgrades.

## How to answer in the interview

- **Why:** Extend existing classes with domain-specific utility functions without inheriting or modifying source code.
- **How:** Define extension functions resolved statically at compile time based on the declared receiver type.
- **Trade-offs:** Extensions cannot access private/protected members and do not participate in virtual polymorphic dispatch.
- **Failure cases:** Defining an extension that shares a signature with a member function; the compiler always prioritizes the member function, silently ignoring the extension.
- **Production solution:** Use extensions for pure, stateless helper methods on Android framework or third-party classes, keeping them scoped to relevant modules.

## Deep-dive talking points

Explain compile-time receiver selection, member priority, nullable receivers, extension properties, and collisions across imports.

## Follow-up questions

- [KOT-23](../kot-23/): Can Java call an extension? **Answer:** yes, as a generated static function subject to JVM naming and imports.
- [KOT-20](../kot-20/): Why does an extension inside a DSL feel like a member? **Answer:** its lambda or extension receiver is implicit, though resolution remains static.

## Self-check rubric

Predict the output for a base-typed subtype, explain member priority, and name one inappropriate polymorphic use.

## References and reviewed-on date

- [Kotlin extensions](https://kotlinlang.org/docs/extensions.html) — static resolution and member precedence.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
