---
id: "MOD-07"
question: "Design a multi-module structure for a large app."
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 360
editorial_status: "reviewed"
---

# MOD-07

## Original interview question

Design a multi-module structure for a large app.

## What the interviewer evaluates

- Produce a plausible acyclic graph with ownership and app composition.
- Explain APIs, data implementation, navigation and DI.
- Specify build/test evidence and avoid module proliferation.

## Explanation in Arabic

لتطبيق كبير مثل commerce، ابدأ بـ`:app` كـcomposition root، ثم `:feature:catalog`, `:feature:checkout`, `:feature:orders` حول قدرات المستخدم. ضع عقود مستقرة في `:domain:*` أو `:feature:*:api` عند حاجة حقيقية، وimplementations في `:data:*`. `:core:network`, `:core:database`, `:designsystem` للبنية المشتركة ذات owner واضح. feature لا تستورد implementation feature أخرى؛ app يربط navigation/DI. حافظ على DAG، اختبر compile variants وintegration، وقِس build configuration/incremental time. لا تجعل الهيكل رسمًا جميلًا بلا حدود API.

## Practical walkthrough

في app كبيرة، ارسم feature ownership وdata contracts قبل رسم أسماء modules. `:app` composition، `:feature:catalog` و`:feature:checkout` بواجهات صغيرة، shared account contract في core/domain مناسب، adapters في data modules. امنع direct feature-to-feature import، واجعل navigation عند app. ابدأ بfeature واحدة واختبر build impact قبل نقل 100 module دفعة واحدة.

## Why it matters and how it works

Separate feature modules can encapsulate screen behavior and team work. Contracts direct dependencies toward stable abstractions; data implementations and app bindings complete the graph. Build performance depends on public ABI changes and Gradle configuration, so a new module must earn its maintenance cost. App-level navigation and DI composition prevent feature-to-feature cycles.

## Worked example

`:feature:checkout` depends on `:domain:checkout-api` and `:designsystem`; `:data:checkout` implements the repository using `:core:network` and `:core:database`. `:app` brings both in and maps a typed checkout destination to a feature entry point. Catalog exposes a product ID contract; checkout reloads needed price/availability from its own domain path, not catalog UI internals.

## Trade-offs and decision criteria

Vertical feature modules support ownership; horizontal core layers avoid infrastructure duplication. Too much separation creates configuration overhead, duplicate DTO mapping and difficult DI graph visibility. A small common capability can begin inside one owner and be extracted when multiple consumers need a stable contract.

## Failure modes

All features depend on one unstable `:core:common`. Feature modules import each other's screen classes. App contains most business logic while modules are only wrappers. Every dependency is `api`, broadening consumer classpaths. Independent feature tests pass while final variant assembly fails.

## Production perspective

Write allowed-edge rules, ownership documentation and a module graph check. Track clean/configuration and incremental build times, test feature-local logic and final app assembly, and review public APIs as carefully as external SDK APIs.

## Interview answer — short

“I use a thin app composition root, cohesive feature modules, narrow contracts, owned data implementations and stable core/design-system modules in an acyclic graph.”

## Interview answer — structured

“For a large commerce app I separate catalog, checkout and orders features, each owning UI and workflow. Shared contracts live in a small API/domain boundary; data modules implement repositories using core network/database, and app selects bindings and top-level navigation. Features do not import one another's internals. I enforce dependency direction and test final variants, then measure whether the split improves team independence and build fan-out instead of maximizing module count.”

## Interview answer — deep senior

“I would start with user capabilities and team ownership, then draw a DAG before creating Gradle files. The app packages variants and composes navigation and DI. Catalog, checkout and orders each own their screens and feature logic, exposing only a destination or domain contract required by consumers. Data modules implement repository interfaces using infrastructure from core network and database, while a design-system module supplies UI tokens and components without business models. For checkout I want a stable product identifier and authoritative price check, not a dependency on catalog's internal Composable or DTO. I define allowed edges and decide which types are public; an `api` leak can cause broad rebuilds even in a DAG. I add feature unit/UI tests plus an app assembly and injection smoke path for release variants. Then I measure configuration time, incremental builds and cross-team change history. If a proposed `:core:common` accumulates unrelated helpers, I give the code a real owner or accept small duplication. The architecture should let teams change internals locally while keeping integration explicit and operationally testable.”

## How to answer in the interview

- **Why:** large teams need independent boundaries.
- **How:** map owners and DAG before splitting.
- **Trade-off:** parallel work versus configuration overhead.
- **Failure case:** big-bang split blocks releases.
- **Production solution:** incremental extraction with build metrics.

## Deep-dive talking points

Draw feature/data/core/app edges, public API, navigation ownership, DI wiring and build measurement.

## Follow-up questions

- Where does top-level navigation composition live? **Answer:** usually in app or a dedicated shell that composes feature entry points.
- Should checkout import catalog's UI implementation? **Answer:** no; use a stable ID or narrow contract.
- How do you validate the design? **Answer:** graph rules, final variant assembly, integration tests and build metrics.

## Self-check rubric

Sketch an acyclic commerce graph, assign owners, and show integration and performance evidence.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — graph design.
- [Common modularization patterns](https://developer.android.com/topic/modularization/patterns) — feature and core examples.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The commerce structure is an illustrative design.
