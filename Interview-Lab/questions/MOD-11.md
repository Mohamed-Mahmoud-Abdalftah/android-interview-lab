---
id: "MOD-11"
question: "How do you manage dependency injection across modules?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 364
editorial_status: "reviewed"
---

# MOD-11

## Original interview question

How do you manage dependency injection across modules?

## What the interviewer evaluates

- Place binding ownership and contracts correctly.
- Explain Hilt aggregation, scopes and variant visibility.
- Note dynamic-feature exception and test graph assembly.

## Explanation in Arabic

في multi-module Hilt، module تملك implementation قد تعلن `@Binds` أو `@Provides` لها، والعقد يعيش في API مناسب يراه feature. `:app` يجب يرى modules/constructor-injected types اللازمة وقت component generation، فراجع Gradle dependencies وvariant. لا تجعل كل feature تقدم binding لنفس interface بلا qualifier، ولا ترفع screen state إلى Singleton. dynamic feature حالة خاصة لأن base لا ترى classes داخلها أثناء compilation؛ استخدم entry point/component dependency أو factory boundary كما توثق Hilt. اختبر assemble/app graph، لا تكتفِ باختبار isolated feature.

## Why it matters and how it works

Generated DI components collect reachable binding declarations for an app variant. Gradle compile visibility therefore shapes graph completeness. Scopes cache objects for component lifetimes, so a binding declared in one module can still be wrong if it owns a shorter-lived Android object. A contract module permits features to compile independently of the implementation chosen by the app.

## Worked example

Catalog feature depends on `CatalogRepository` API; `:data:catalog` binds `RealCatalogRepository` and app includes both. The binding is installed in a component matching its stateful lifetime, and tests replace it with an in-memory fake. A debug variant with a fake API client and release with real client each assemble successfully. An on-demand scanner uses a documented bridge instead of assuming base Hilt knows its classes.

## Trade-offs and decision criteria

Bindings near implementations make ownership clear; app-level selection supports multiple implementations but can grow a composition file. Too many broad modules/qualifiers make graph diagnostics hard. Hilt gives compile-time errors for many missing/duplicate bindings but cannot catch every semantic lifecycle leak.

## Failure modes

Implementation module absent from app variant produces a missing binding. Two unqualified bindings collide. A Singleton provider captures an Activity. Dynamic feature declares a Hilt binding that base compilation cannot aggregate. Tests use a fake binding that differs in qualifier from production.

## Production perspective

Maintain an injection graph inventory of contract, binding module, qualifier, scope and variants. Run app assembly, graph smoke tests and test binding replacement in CI; review module edge changes with DI owners.

## Interview answer — short

“I keep contracts feature-visible, bindings implementation-owned and app variants able to aggregate them; scopes and qualifiers stay explicit, with a bridge for dynamic features.”

## Interview answer — structured

“A feature depends on a repository interface; its data module supplies a Hilt binding and the app composition graph includes that implementation. I check compile visibility because generated Hilt components only know reachable modules. I match scope to lifetime, use qualifiers for genuine multiple implementations, and build each variant. Dynamic features need their documented entry-point/component-dependency path. An integrated graph test confirms wiring that a unit test cannot.”

## Interview answer — deep senior

“DI across modules is the intersection of the module DAG and object lifetime. I place the repository contract where the feature can compile without importing data internals, then keep the binding close to the implementation or at a deliberate app selection point. The final app variant must have compile visibility of the Hilt modules and injectable classes that generated components aggregate. That is why a feature compiling alone does not prove the app graph will resolve. I review qualifiers and scopes alongside edges: a Singleton binding cannot own an Activity callback just because the compiler can construct it, and two unqualified implementations should not be installed together. Tests keep direct constructor seams for logic, plus a small Hilt integration path that replaces the right qualified binding and proves actual Android injection. Dynamic features need special treatment because their dependency direction prevents the base app from seeing feature-only classes during its Hilt generation; a narrow entry point and feature Dagger component or explicit factory bridges it. CI assembles debug and release variants and reports missing bindings early. The result is explicit composition without feature-to-implementation coupling.”

## Deep-dive talking points

Discuss contracts, aggregation, variant graph, qualifiers, scope, dynamic feature bridge and smoke tests.

## Follow-up questions

- Why can isolated feature compilation pass while app assembly fails? **Answer:** the final graph may lack a visible binding or have duplicates.
- Does Hilt compile success prove no Activity leaks? **Answer:** no; transitive callbacks and manual providers can violate ownership.
- How does dynamic delivery alter DI? **Answer:** base-generated Hilt components cannot aggregate feature-only classes directly.

## Self-check rubric

Draw binding visibility, choose scope and qualifier, and test one normal and one dynamic feature path.

## References and reviewed-on date

- [Hilt in multi-module apps](https://developer.android.com/training/dependency-injection/hilt-multi-module) — visibility and dynamic features.
- [Hilt on Android](https://developer.android.com/training/dependency-injection/hilt-android) — scopes and modules.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Variant graph must be verified in the actual build.
How do you manage dependency injection across modules?
