---
id: "PAT-03"
question: "Explain Singleton, Factory, Abstract Factory, and Builder."
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 194
editorial_status: "reviewed"
---

# PAT-03

## Original interview question

Explain Singleton, Factory, Abstract Factory, and Builder.

## What the interviewer evaluates

Contrast one shared instance, object selection, related-family construction, and staged configuration.

## Explanation in Arabic

Singleton تتحكم في instance واحدة (في Kotlin `object` per process/classloader)، لكنها مش durable storage ولا تلقائيًا thread-safe لmutable fields. Factory تنشئ/تختار implementation واحد حسب inputs، Abstract Factory تنشئ عائلة related objects متوافقة مثل network + serializer variants، وBuilder تبني object مع options وخطوات validation قبل `build()`. Android/Hilt ممكن تتولى construction من غير GoF classes صريحة. فرق مهم: `@Singleton` في Hilt scope لعمر graph/application component، مش وعد global عبر process death. اختار أبسط حاجة تكفي، ولا تخبّي Activity في singleton.

## Why it matters and how it works

Each creational pattern addresses a different construction problem. Singleton controls instance count within an owner; factory selects type; abstract factory maintains consistency across a family; builder manages complex configuration. None guarantees business correctness or durable state.

## Worked example

Example: `object CurrencyCodes` holds stateless constants; `PaymentRouteFactory` selects a provider adapter; an `EnvironmentFactory` could create matching API and serializer for sandbox/production; an OkHttp-style builder configures timeouts/interceptors before creation. These are conceptual roles, not an instruction to implement all four.

## Practical walkthrough

`object CurrencyCodes` لو stateless utility ممكن، لكن `object CurrentSession` اللي فيه user/token state خطر: process death يمسحه وaccount switch يعمل stale state. Factory function تنشئ provider adapter من config/runtime choice؛ Abstract Factory تنشئ مجموعة متوافقة مثل sandbox API + signer معًا، مش مجرد factory لكل class. Builder مفيدة لو options كتير وبعض combinations invalid وتحتاج `build()` يعمل validation؛ لconstructor صغير بتخفي المطلوب. في Android DI scope تحدد lifetime فعليًا، و`@Singleton` معناها one instance في graph/process تقريبًا، مش persistent data ولا مناسب لكل dependency. اشرح متى تختار كل واحدة وحالة فشلها.

## Trade-offs and decision criteria

A constructor is best when creation is simple. Factories and builders add names and indirection but can enforce invariants. A global singleton is convenient but hard to reset in tests and risky for mutable state. Hilt scopes may replace manual singleton wiring.

## Failure modes

A process-wide `object Session` stores `isLoggedIn = true` and is treated as source of truth. Process death resets it; token expiry can make it stale. Use repository/persistence and server validation. Another failure is a Builder that allows `build()` with missing required endpoint.

## Production perspective

A networking module uses DI-managed client construction with validated config, while session status remains repository-backed. Integration tests verify correct environment family and timeouts.

## Interview answer — short

Singleton manages one instance within its scope; Factory creates or selects an implementation; Abstract Factory creates a compatible family; Builder assembles a configurable object. I choose by construction complexity and avoid global mutable state.

## Interview answer — structured

I would use a constructor for a simple object. A factory becomes useful when selection or creation logic is nontrivial; an abstract factory when several related objects must be created consistently; a builder when there are many optional settings and validation before creation. A Kotlin `object` is a singleton-like instance in the process, but not durable storage. Hilt can manage instance scopes instead of a hand-written singleton. I test construction invariants and lifecycle ownership.

## Interview answer — deep senior

These four patterns are often confused because they all involve creation. A singleton is about instance cardinality and access, not complex configuration; Kotlin `object` makes it concise but mutable state inside it still needs synchronization and process-death recovery. A factory method or factory object chooses a product without forcing callers to know constructor details. An abstract factory coordinates a family—such as matching API and serializer implementations for an environment—so mismatched combinations are harder to create. A builder collects options, validates required fields, then creates an immutable client. DI can wire these constructions and scopes, but I still design the contract. In Android I never let an application-scoped instance retain Activity context, and I do not mistake a Hilt scope for server-authoritative session truth.

I distinguish lifetime, variation, families, and construction complexity. A stateless Kotlin `object` can be a simple singleton, but a global current-session object is a bad source of truth because it can leak screen references and is lost after process death. A Factory chooses or creates one product under a rule; an Abstract Factory produces a compatible family, such as sandbox API and signer, so callers cannot mix environments. A Builder handles a configuration with many optional choices and a validated final object. In Android I do not apply an application-wide singleton scope by default: ownership follows the feature or session. I test invalid environment combinations and account switching, and I prefer a constructor when the object has only a few required inputs.

## How to answer in the interview

- **Why:** Each creational pattern solves a different construction or lifetime constraint.
- **How:** Contrast `object`, one-product factory, compatible-family factory and validated builder.
- **Trade-off:** Direct constructor beats Builder for a small fixed input set.
- **Failure case:** Global session Singleton leaks state or outlives the account.
- **Production solution:** Scope providers correctly and test environment/account transitions.

## Deep-dive talking points

Compare construction intent, instance lifetime, related product families, validation and Hilt scope.

## Follow-up questions

- [PAT-10](../pat-10/): Factory versus Abstract Factory? **Answer:** one product selection versus a family of compatible products.
- [DI-07](../di-07/): Does `@Singleton` survive process death? **Answer:** no; it scopes within the running component graph.

## Self-check rubric

Choose among constructor, factory, abstract factory and builder for four cases; identify a singleton lifecycle risk.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — creational patterns.
- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — Kotlin singleton syntax.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
