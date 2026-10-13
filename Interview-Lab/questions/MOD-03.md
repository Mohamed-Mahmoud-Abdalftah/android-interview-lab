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

Dependency graph تمثل modules كعُقد والأسهم “A يحتاج B ليُترجم/يعمل”. في Gradle project dependencies لازم تكون DAG حتى توجد topological order للبناء؛ لو A يعتمد على B وB على A لا يوجد ترتيب، كما أن ownership تختلط. مثال `:feature:orders` يحتاج شاشة login و`:feature:auth` يحتاج order badge: لا تربطهما مباشرة ذهابًا وإيابًا؛ استخرج contract أو navigation destination صغير في module أدنى، أو app ينسق التفاعل. لا تعالج cycle بنقل كل شيء إلى `:core:common` بلا تصميم.

### Practical walkthrough in Egyptian Arabic

Dependency graph فيها module nodes وأسهم import. لو `:feature:pay` يعتمد `:feature:account` والعكس، Gradle قد يرفض cycle أو architectural coupling يصبح صعب الاختبار. استخرج contract مشترك صغير باتجاه واحد أو composition في app module. احذر cycle منطقي عبر service locator حتى لو Gradle graph acyclic. CI ترسم/تفحص graph عند تغيير dependencies.

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

“A module dependency graph is a directed map of compile relationships. It must be acyclic to permit a build order and maintain clear ownership.”

## Interview answer — structured

“I draw modules as nodes and dependencies as arrows toward what they need. A cycle means no topological build order and usually reveals mixed responsibilities. If Orders and Auth import each other, I identify the narrow shared contract or let the app coordinate rather than introduce a global service locator. I then enforce the allowed DAG in CI so a future convenience import cannot recreate the cycle.”

## Interview answer — deep senior

“A dependency graph describes compile-time and packaging relationships between modules, with a directed edge from a consumer to the API it uses. Gradle needs an acyclic project graph to order work. Architecturally, a cycle also means neither boundary can evolve independently: changing one may require the other's internals, and ownership becomes ambiguous. I diagnose what crossed the boundary. If Orders needs authentication status, that can be a small stable contract below both features; if Auth wants an order badge in the app shell, the app can compose those contributions rather than Auth importing Orders. Sometimes the features were artificially split and should merge. I avoid a giant common module that merely hides the cycle or a static service locator that moves it to runtime. The extracted API must remain narrow and have an owner; its consumers should not see implementation types. I add a dependency-graph rule in CI and review high-fan-out modules because an acyclic graph can still be badly coupled. Full app assembly then checks that the acyclic pieces actually wire together.”

## How to answer in the interview

- **Why:** cycles block independent build and change.
- **How:** orient edges toward stable contracts.
- **Trade-off:** new interface versus direct convenience.
- **Failure case:** hidden runtime cycle via global registry.
- **Production solution:** enforce DAG and ownership.

## Deep-dive talking points

Discuss directed edges, topological order, contract extraction, app orchestration, merging, and graph enforcement.

## Follow-up questions

- Can reflection make an architectural cycle healthy? **Answer:** no; it can hide compile edges while retaining runtime coupling.
- Is every shared interface worth a new module? **Answer:** no; weigh API cost and whether the boundary is genuinely stable.
- What does CI enforce? **Answer:** allowed module dependencies and absence of cycles.

## Self-check rubric

Draw a three-module cycle, explain why it fails, and resolve it with an owned contract or composition root.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — dependency graph principles.
- [Gradle multi-project builds](https://docs.gradle.org/current/userguide/multi_project_builds.html) — project graph.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The Auth/Orders graph is illustrative.
