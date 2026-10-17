---
id: "MOD-03"
question: "What is a dependency graph? Why must it be acyclic?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "A"
phase: 4
priority: "P1"
order: 356
editorial_status: "reviewed"
---

# MOD-03

## Original interview question

What is a dependency graph? Why must it be acyclic?

## What the interviewer evaluates

- Define vertices and directed compile edges.
- Explain topological build/composition order and cycle consequences.
- Resolve a realistic feature cycle by extracting a smaller contract.

## Concept and technical explanation

A dependency graph in a multi-module Gradle project is a formal directed graph where vertices represent independent modules (subprojects) and directed edges represent compile-time or runtime dependencies between them. The graph MUST be acyclic—meaning it forms a Directed Acyclic Graph (DAG)—because build systems depend on topological sorting to compute a deterministic compilation order. If Module A depends on Module B, Module B must finish compilation and produce its symbols and AAR artifact before Module A can begin compilation. If a cycle exists (e.g., A depends on B, and B depends on A), topological sorting is mathematically impossible: neither module can compile first, resulting in infinite recursion or an immediate Gradle build failure with a circular dependency error. Resolving cycles requires inverting dependencies (DIP), extracting shared interface contracts into a third module, or mediating interactions via dependency injection.

## Practical walkthrough (English)

Resolving circular dependencies by extracting a shared API contract module:
```kotlin
// ❌ CIRCULAR DEPENDENCY TRAP:
// :feature:cart depends on :feature:checkout
// :feature:checkout depends on :feature:cart
// FAILS: Circular dependency between project ':feature:cart' and project ':feature:checkout'

// ✅ RESOLUTION VIA API EXTRACTION:
// 1. Create :feature:checkout:api containing only the interface
// feature/checkout/api/src/main/kotlin/CheckoutContract.kt
interface CheckoutNavigator {
    fun openCheckout(context: Context, cartId: String)
}

// 2. :feature:cart depends ONLY on :feature:checkout:api (DAG is preserved)
// 3. :feature:checkout:impl implements CheckoutNavigator
// 4. :app binds CheckoutNavigator implementation via Hilt
```

## Explanation in Arabic

ما هو الـ Dependency Graph (الرسم البياني للتبعيات) في Gradle، ولماذا يجب أن يكون خاليًا تمامًا من الحلقات (Acyclic - DAG)؟

1. المفهوم الرياضي:
   - في Gradle، تمثل الموديولات **الرؤوس (Vertices / Nodes)**، وتمثل علاقات الاعتماد `implementation(projects.core.network)` **الحواف الموجهة (Directed Edges)**.
   - الرسم البياني يجب أن يكون **Directed Acyclic Graph (DAG)**؛ أي رسم بياني موجه بدون أي دورات أو حلقات دائرية مغلقة.

2. لماذا يمنع Gradle التبعيات الدائرية (Circular Dependencies) بشكل قاطع؟
   - **استحالة الترتيب الطوبولوجي للتجميع (Topological Sort Failure)**: لكي يقوم المترجم (Kotlin Compiler / javac) بتجميع الموديول B، يجب أن ينتهي أولاً من تجميع الموديول A الذي يعتمد عليه B. إذا كان A يعتمد بدوره على B، يدخل نظام البناء في حلقة مغلقة مستحيلة (Deadlock): من الذي يُجمع أولاً؟!
   - يرفض Gradle التجميع فوراً مع الخطأ الشهير: `Circular dependency between the following tasks: ...`.

3. كيف تحل التبعية الدائرية الواقعية بين موديولين؟
   - لنفترض أن `:feature:cart` يحتاج كلاس من `:feature:checkout`، وفي نفس الوقت `:feature:checkout` يحتاج كلاس من `:feature:cart`.
   - **الحل المعماري الصحيح (Extract Shared Contract / API Module)**:
     * استخراج الواجهات والبيانات المشتركة إلى موديول ثالث مستقل ومحايد (مثل `:feature:cart-api` أو `:core:model`).
     * الآن، يعتمد كلا الموديولين على الموديول الثالث في اتجاه واحد للأسفل، وتختفي الدورة تماماً!

## Practical walkthrough

حل التبعية الدائرية باستخراج موديول وسيط للعقود المشتركة (API Extraction):
```text
❌ دورة دائرية مستحيلة تمنع البناء:
:feature:cart ──────(depends on)─────► :feature:checkout
     ▲                                       │
     └──────────────(depends on)─────────────┘
[Gradle Error: Circular dependency between :feature:cart and :feature:checkout!]

✅ الحل المعماري باستخراج موديول عقد مستقل (:feature:cart-api):
         :feature:cart                  :feature:checkout
               │                                │
               │ (implements)                   │ (consumes)
               ▼                                ▼
         ┌──────────────────────────────────────────────┐
         │             :feature:cart-api                │
         │ (Interfaces, Route contracts, Shared DTOs)   │
         └──────────────────────────────────────────────┘
الرسم البياني أصبح DAG نقي خالي من أي حلقات دائرية، ويتم تجميعه بنجاح وبسرعة!
```

## Why it matters and how it works

A directed edge imports another module's API and potentially its transitive dependencies. Acyclic graphs permit compilation in dependency order and make layering understandable. A cycle signals that two boundaries are not independent as designed; merely hiding it behind reflection or a global service locator leaves architectural coupling unresolved.

## Worked example

Orders needs `AuthStatus` to gate checkout, while Auth wants to show a pending-order count. Put an authentication status contract in `:core:auth-api` or an appropriate domain API that Orders consumes; have app coordinate an order-count contribution to a top-level shell. Auth implementation does not import Orders implementation. A graph check rejects reverse edges in CI.

## Trade-offs and decision criteria

An extracted interface module can break a genuine shared contract but adds API maintenance. App-level orchestration keeps features independent but can enlarge app wiring. If two features always change together, merging them may be clearer than artificial abstractions. Choose based on cohesive ownership, not just compiler appeasement.

## Failure modes

A shared module imports a feature, reversing the intended layer. A dependency is added as `api` and leaks internals through consumers. Two modules communicate via static globals to conceal a conceptual cycle. A giant common module accumulates unrelated policies as a cycle escape hatch.

## Production perspective

Visualize and enforce allowed edges in CI, review new dependency changes, and periodically inspect high-fan-out nodes. Include full app assembly so technically acyclic modules still compose correctly.

## Interview answer — short

A dependency graph represents modules as nodes and their dependencies as directed edges. It must be strictly acyclic because Gradle uses topological sorting to determine task execution order. A circular dependency creates an impossible chicken-and-egg compilation loop where neither module can build first, breaking builds and paralyzing incremental caching.

## Interview answer — structured

In multi-module Gradle engineering, the dependency graph models how modules connect across the codebase.
Each module serves as a vertex, while implementation and api declarations define directed edges pointing toward dependencies.
This graph must strictly form a Directed Acyclic Graph, meaning following the arrows never leads back to the originating module.
Gradle relies on topological sorting to calculate the exact execution order of compilation tasks.
When Module A depends on Module B, Gradle compiles Module B first, producing the necessary class files and symbol tables before starting compilation on Module A.
If a cycle occurs, such as Module A depending on Module B while Module B simultaneously depends on Module A, Gradle encounters an unresolvable circular dependency error.
To resolve cyclical dependencies in production, engineers apply the Dependency Inversion Principle.
By extracting shared data models or contract interfaces into an independent API module, both features depend downward on the contract without depending directly on each other.

## Interview answer — deep senior

The dependency graph is the foundational blueprint of your Android build performance and architectural health.
From a graph theory perspective, Gradle treats tasks as nodes within an execution DAG, resolving task dependencies such as compileKotlin and packageDebug through topological sorting.
If an edge introduces a cycle, the graph loses its partial ordering property, making it mathematically impossible for the compiler to schedule tasks without deadlock.
Beyond direct two-module loops, large codebases frequently suffer from insidious multi-hop cycles, where module A depends on B, B on C, and C imports an internal helper from A.
These transitive loops instantly crash project synchronization and break build caching.
In enterprise architectures, we enforce acyclic dependency rules using continuous integration linters such as Gradle Dependency Analysis Plugin or custom Konsist unit tests that assert forbidden dependency paths.
When an apparent cycle arises between two domain features—such as user profile needing payment data while payment requires user address details—we refuse to merge the modules.
Instead, we extract an explicit interface contract into a lightweight API module or invert the dependency using Hilt.
Feature A consumes the interface, Feature B implements it, and the root app module wires the binding at runtime.
This maintains a clean, single-direction DAG that maximizes Gradle parallel compilation lanes across developer workstations.

## How to answer in the interview

- **Why:** cycles block independent build and change.
- **How:** orient edges toward stable contracts.
- **Trade-off:** new interface versus direct convenience.
- **Failure case:** hidden runtime cycle via global registry.
- **Production solution:** enforce DAG and ownership.

## Deep-dive talking points

Discuss directed edges, topological order, contract extraction, app orchestration, merging, and graph enforcement.

## Follow-up questions

- **Interviewer:** "How does graph depth affect build times?"
  **Answer:** "A deep linear graph (A -> B -> C -> D) forces sequential compilation, preventing Gradle from utilizing multiple CPU cores in parallel. A flatter, balanced tree allows massive parallel builds."

- **Interviewer:** "Can two classes inside the same Gradle module depend cyclically on each other?"
  **Answer:** "Yes, the Kotlin/Java compiler compiles all files within a single module together in one batch. However, class-level cycles remain a serious code smell."

## Self-check rubric

Draw a three-module cycle, explain why it fails, and resolve it with an owned contract or composition root.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — dependency graph principles.
- [Gradle multi-project builds](https://docs.gradle.org/current/userguide/multi_project_builds.html) — project graph.

Technically reviewed against primary documentation on 2026-10-13.
