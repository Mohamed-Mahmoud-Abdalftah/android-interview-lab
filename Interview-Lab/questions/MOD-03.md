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

A dependency graph models modules as nodes and dependencies as directed edges. It must be a Directed Acyclic Graph (DAG) because Gradle relies on topological sorting to determine compilation order. A cycle (A depends on B, B depends on A) causes an unresolvable compiler deadlock, which is resolved by extracting shared interfaces into a separate API module.

## Interview answer — structured

In Gradle, the project architecture is modeled as a Directed Graph where modules are nodes and project dependencies (`implementation(projects.foo)`) form directed edges.

The graph **must strictly be acyclic (a DAG)** because the compiler requires a deterministic **Topological Sort** to establish the build order:
1. If module `B` depends on `A`, `A` must compile into bytecode, package its public ABI, and expose it on `B`'s compile classpath before `B` can even begin parsing code.
2. If a cycle exists (`A -> B -> A`), an impossible paradox occurs: neither module can compile before the other. Gradle terminates build graph evaluation immediately with a `CircularDependencyException`.

To resolve circular dependencies in production, never hack around it with reflection. Apply the **Dependency Inversion Principle**: extract the shared interfaces, routes, and data models into a lightweight `:feature:x-api` module. Both modules then depend downward on the API module, breaking the cycle.

## Interview answer — deep senior

Cycles do not only occur between Gradle modules; they frequently occur as **transitive classpath cycles and task dependency cycles**.

For example, if `:app` has a custom task that packages assets generated by a downstream module, and that downstream module has a task that reads resources from `:app`, Gradle's task execution engine deadlocks.

In enterprise Android repositories with dozens of engineers, teams use automated architectural enforcement plugins like **Graphite** or **Gradle Dependency Guard** in CI. These tools inspect the project DAG on every pull request, calculating graph metrics such as **Longest Critical Path (Depth)** and **Module Fan-in / Fan-out**. If an engineer attempts to introduce an unauthorized cross-feature edge or creates a dependency cycle, the CI pipeline blocks the PR before code ever merges to main.

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
