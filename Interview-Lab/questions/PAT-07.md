---
id: "PAT-07"
question: "What does Dependency Injection as a pattern accomplish?"
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 198
editorial_status: "reviewed"
---

# PAT-07

## Original interview question

What does Dependency Injection as a pattern accomplish?

## What the interviewer evaluates

Explain external provisioning of dependencies, graph composition, test substitution and lifecycle scope.

## Explanation in Arabic

Dependency Injection pattern يعني object تستقبل dependencies من برّه بدل تعمل `Retrofit.Builder()` أو `Room.databaseBuilder()` جوا نفسها. Constructor injection تخلي الاحتياجات صريحة وسهلة الاختبار؛ Hilt/Dagger أو manual composition root يكوّنوا graph. ده يساعد تبديل implementation وscope ownership، لكن DI مش نفسها DIP: ممكن تحقن concrete SDK في business policy وتبقى لسه coupled. Android lifecycle مهمة: singleton ما يمسكش Activity context؛ ViewModel-scoped object ما ينفعش نفترض إنها durable بعد process death.

## Why it matters and how it works

DI separates construction from use. It makes dependencies visible, enables fakes and centralizes scope decisions. A container is optional; the pattern can be implemented manually. It does not select good abstraction boundaries automatically.

## Worked example

JVM illustration:
```kotlin
interface Clock { fun nowMillis(): Long }
class ExpiryPolicy(private val clock: Clock) {
    fun expired(deadline: Long) = clock.nowMillis() >= deadline
}
```
Production composition supplies a system clock; tests supply a fixed clock. No Android dependency is needed for policy tests.

## Trade-offs and decision criteria

Manual DI is transparent for small graphs; Hilt reduces repetitive wiring as a graph grows but adds build tooling and scope complexity. Service locator hides dependencies and makes tests order-dependent. Avoid interfaces for every pure helper.

## Failure modes

A singleton-scoped network service stores an Activity passed through a constructor, leaking it across recreation. Use application context only where appropriate and inject lifecycle-bound collaborators into matching scopes.

## Production perspective

An Android app wires repositories, API clients and ViewModels through Hilt, while domain unit tests construct policies directly with fake clocks/repositories. Scope tests verify no Activity leaks.

## Interview answer — short

DI supplies collaborators from outside an object, making dependencies explicit and replaceable. It can be manual or framework-driven. I use it to simplify testing and scope ownership, while reviewing DIP and lifecycle separately.

## Interview answer — structured

Without DI, a class may construct its own Retrofit client or read a global singleton, making tests and configuration difficult. Constructor injection exposes that dependency in the API, and an app composition root supplies the production implementation. Hilt can automate the graph, but manual DI is also valid. I choose scopes by lifecycle, not convenience: an application singleton cannot retain an Activity. DI helps substitution and tests; it does not by itself ensure the business code depends on the right abstraction.

## Interview answer — deep senior

Dependency injection is a construction pattern. The consumer states what it needs, and the composition root decides which implementation and lifetime to provide. That allows a domain policy to be tested with deterministic fakes and lets infrastructure change without editing every caller, provided the contracts are well designed. Hilt/Dagger are graph tools, not a substitute for deciding boundaries. I distinguish DI from DIP by inspecting types: a Hilt-injected Retrofit service inside a use case is still a transport dependency. I also audit scopes. A singleton containing Activity context can leak; a ViewModel-scoped object disappears with its owner and cannot hold durable transaction truth. In production I test graph wiring and lifecycle separately from pure policy behavior.

## Deep-dive talking points

Compare manual composition with Hilt, constructor visibility, service locator and scope ownership.

## Follow-up questions

- [SOL-07](../sol-07/): DI versus DIP? **Answer:** provisioning mechanism versus source dependency direction.
- [DI-02](../di-02/): Which injection style exposes required dependencies? **Answer:** constructor injection.

## Self-check rubric

Show one constructor-injected dependency, a fake test, and a scope mistake DI does not prevent.

## References and reviewed-on date

- [Android dependency injection](https://developer.android.com/training/dependency-injection) — DI on Android.
- [Kotlin classes](https://kotlinlang.org/docs/classes.html) — constructor mechanics.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
