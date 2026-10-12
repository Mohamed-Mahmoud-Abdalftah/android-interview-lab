---
id: "MOD-14"
question: "How do you avoid circular dependencies and giant core/common modules?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 367
editorial_status: "reviewed"
---

# MOD-14

## Original interview question

How do you avoid circular dependencies and giant core/common modules?

## What the interviewer evaluates

- Resolve cycles by ownership and directional contracts.
- Recognize common-module fan-out and unrelated code accumulation.
- Describe governance and graph checks.

## Explanation in Arabic

ارسم DAG مسموحة وامنع reverse imports في CI. إذا ميزتان تحتاجان بعضهما، افصل العقد المشترك الأصغر في owner مناسب أو اجعل app تنسق، وأحيانًا ادمجهما لو هما قدرة واحدة. لا ترمِ code داخل `:core:common` لمجرد إزالة cycle؛ common تصبح high-fan-out، وكل تعديل API يعيد بناء نصف التطبيق. ضع criteria لقبول code مشتركة: استخدام حقيقي متعدد، semantics مستقرة، owner واضح. راجع dependencies والشيفرة العامة دورياً.

## Why it matters and how it works

Cycles prevent a topological project build and obscure responsibility. A giant core module can remain acyclic but still create a central bottleneck and expose unrelated APIs to every feature. Contract extraction works when the extracted concept is stable and owned; otherwise app orchestration or merging cohesive pieces may better reflect reality.

## Worked example

Profile needs loyalty points; Rewards wants a user avatar. Instead of `:feature:profile` ↔ `:feature:rewards`, a small `UserSummary` contract is owned by a shared domain/data API, while app shell composes the profile and rewards entry points. A generic avatar formatting helper stays in the owning UI module until multiple consumers demonstrate shared semantics.

## Trade-offs and decision criteria

Extra API modules break compile edges but cost maintenance. App coordination is explicit yet can grow a shell. Some duplication is cheaper than unstable shared code. Merging two features can be correct if their release/ownership always coincide; keep a boundary only when it serves a real purpose.

## Failure modes

A new `common` module becomes a dumping ground. Interfaces are extracted but still expose each feature's internal DTO. A static registry hides runtime coupling. CI checks only direct cycles but not high fan-out or forbidden feature-to-feature edges.

## Production perspective

Automate graph and allowed-edge checks, track core public API churn and incremental rebuild fan-out, and assign codeowners to shared modules. Review proposed cross-feature imports as architectural changes.

## Interview answer — short

“I enforce an acyclic dependency direction, extract only genuinely stable contracts or coordinate in app, and keep core modules narrow with explicit ownership.”

## Interview answer — structured

“A cycle tells me two modules are crossing responsibility lines. I examine the relationship, move a small shared contract to the right owner, coordinate at app level, or merge pieces that truly form one feature. I do not dump code into common just to silence Gradle: a huge core creates high fan-out and rebuilds. CI checks allowed edges and I review shared API growth and change history.”

## Interview answer — deep senior

“I want a graph whose arrows explain ownership. When Profile and Rewards depend on each other, I look at the actual information exchanged. A stable `UserSummary` might belong in a lower-level contract, while the app shell can compose navigation between the two. If both modules always change together, the original split may be artificial and merging may be simpler. I resist the familiar shortcut of moving whatever causes a cycle to `:core:common`. That can produce an acyclic graph on paper while creating a high-fan-out module that every team edits, every feature sees and every build recompiles after an API change. Shared code should have clear semantics, more than one genuine consumer and an owner responsible for compatibility. A tiny duplicate helper may be acceptable until that is true. I enforce direct and transitive graph rules in CI, inspect public API and rebuild impact of core changes, and review new cross-feature edges. A static service locator does not solve the design; it only hides the dependency from Gradle.”

## Deep-dive talking points

Explain topological order, API extraction, app shell, justified merge, common-module fan-out and CI enforcement.

## Follow-up questions

- Is an acyclic graph always well designed? **Answer:** no; a giant core can be acyclic and still tightly couple all features.
- When might duplication be better? **Answer:** when a tiny helper has no stable shared semantics and extraction adds coordination cost.
- What is an alternative to contract extraction? **Answer:** app orchestration or merging code with one cohesive owner.

## Self-check rubric

Resolve a feature cycle, explain a common-module smell, and name a preventive graph check.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — dependency graph and ownership.
- [Common modularization patterns](https://developer.android.com/topic/modularization/patterns) — API boundaries.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Boundary selection remains context-specific.
