---
id: "SYS-15"
question: "Compare monolith and multi-module designs."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 344
editorial_status: "reviewed"
---

# SYS-15

## Original interview question

Compare monolith and multi-module designs.

## What the interviewer evaluates

Compare monolith and multi-module by team scale, build isolation and API cost.

## Explanation in Arabic

Monolith module واحدة أبسط في البداية: wiring أقل وrefactor سريع، لكن مع فرق كثيرة كل تغيير ممكن يعيد compile/test نطاق كبير وتبقى boundaries ضمنية. multi-module تقسم features/core/data حسب ownership وتعمل dependency graph acyclic، فتحسن العزل وإعادة الاستخدام إن الحدود صحيحة. لكنها تزود Gradle config, DI, API compatibility وتحتاج CI. القرار مبني على measurements مش عدد الملفات.

## Why it matters and how it works

Modules are compilation/dependency boundaries, not automatically clean architecture. A poorly split project with giant shared API can be slower than a monolith. Measure clean/incremental build, affected module count, test isolation, merge conflicts and ownership before/after. Start with a few high-cohesion boundaries.

## Worked example

Conceptual graph; no code change is justified until coupling and build hotspot are measured.

```kotlin
// Monolith: :app contains catalog, checkout, account.
// Targeted split:
// :app -> :feature:catalog, :feature:checkout
// :feature:* -> :core:ui, narrow domain APIs
// Avoid :feature:catalog -> :feature:checkout implementation.
```

## Trade-offs and decision criteria

Monolith maximizes local simplicity for small teams; modularity adds up-front API/DI maintenance but can scale ownership. Dynamic delivery is a separate runtime packaging decision. Avoid splitting by every class or every layer when it creates boilerplate without isolation.

## Failure modes

A module cycle or all-features-depend-on-common graph prevents independent builds. Public API churn across 20 modules can increase recompilation. Teams may duplicate business logic if ownership is unclear.

## Production perspective

A startup with three engineers keeps one app module plus small data boundaries. At 20 teams, it extracts team-owned features and stable shared APIs incrementally, then tracks incremental build time and cross-team PR dependency.

## Interview answer — short

“A monolith is simpler at small scale; multi-module can improve ownership and compilation isolation when boundaries are stable. It adds configuration and API cost, so I measure build and team friction before splitting.”

## Interview answer — structured

“I compare the actual problem, not the architecture fashion. One module lets a small team refactor quickly with little Gradle/DI overhead. As features and teams grow, an acyclic multi-module graph can make ownership explicit and limit compilation/test impact. But a giant core module or unstable public APIs can make builds worse. I would measure changed-file-to-affected-target patterns, clean/incremental builds and cross-team coordination, then extract high-cohesion features gradually.”

## Interview answer — deep senior

“Modularity is a trade-off across code, build and organization. A monolith is easy to navigate and refactor when one team owns it, but at scale it can accumulate implicit coupling and force broad recompilation. Modules create explicit dependency edges and team APIs, potentially allowing parallel work and targeted tests. They also add Gradle configuration, DI binding, version/ABI considerations and contract governance. I avoid one module per class and avoid treating dynamic feature delivery as identical to source modularity. I establish a baseline for build time, test execution and change lead time, then split one cohesive feature with a stable contract, measure results and repeat only when benefits are real. Start with a few high-cohesion boundaries.”

## Deep-dive talking points

Defend one incremental split using measured build and ownership evidence.

## Follow-up questions

- [MOD-01](../mod-01/): What is modularization? **Answer:** explicit compilation/dependency boundaries with costs.
- [SYS-19](../sys-19/): How address 25-minute build? **Answer:** measure hotspots before redesigning graph.

## Self-check rubric

Can I articulate both costs, draw acyclic target and specify metrics?

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — benefits and costs.
- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
