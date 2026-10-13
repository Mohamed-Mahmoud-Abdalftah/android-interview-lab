---
id: "MOD-08"
question: "What belongs in :core:network, :core:database, :core:ui, and feature modules?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 361
editorial_status: "reviewed"
---

# MOD-08

## Original interview question

What belongs in :core:network, :core:database, :core:ui, and feature modules?

## What the interviewer evaluates

- Distinguish infrastructure from feature policy and UI.
- Prevent giant core modules and domain leakage.
- Specify ownership of migrations, API clients and reusable UI.

## Explanation in Arabic

`:core:network` قد يملك HTTP client configuration، auth interceptor العام وserialization infrastructure؛ ليس checkout endpoint policy كلها. `:core:database` يملك Room setup، migration infrastructure وshared transaction primitives، لكن feature-owned tables/DAOs قد تبقى في data feature حسب graph. `:core:ui` أو design system يملك theme، tokens ومكونات عامة لا تعرف business entities. feature module يملك screen, state, events, navigation entry، وقواعد العمل الخاصة به أو تنسيق use case. السؤال الحاسم: لو feature واحدة تغيرت، هل يجب تعديل core؟ لو نعم دائمًا، core صارت مكبًا للتفاصيل.

### Practical walkthrough in Egyptian Arabic

`:core:network` يوفر HTTP client/config وليس product API DTO لكل feature؛ `:core:database` يوفر DB infrastructure/shared tables؛ `:core:ui` tokens/components لا feature business. Feature تملك screen, state, policy خاص بها. لو core يستورد feature model فهذا عكس الاتجاه. افصل shared contract فقط عندما يوجد أكثر من مستهلك وسلوك ثابت.

## Why it matters and how it works

Core modules often have high fan-out, so changing their public API recompiles many consumers. Keeping infrastructure interfaces narrow protects that boundary. Feature modules remain cohesive when their UI and workflow policy live together. Database schema can be centralized physically yet ownership of feature migrations and tables should be explicit so teams do not edit one opaque shared module blindly.

## Worked example

Orders data uses a `NetworkClient` configured in core network but owns `OrdersApi` request/response mapping. Core database configures Room and the migration test harness; Orders data owns its `OrderEntity` schema and migration change review. Core UI provides an `AppButton` that accepts text/loading/click, while Orders feature formats the order-status message and decides when the button is enabled.

## Trade-offs and decision criteria

Central infrastructure reduces duplication but becomes a coordination hotspot. Feature-owned endpoint/DAO code keeps policy local, though cross-feature transactions require deliberate shared ownership. A separate UI core simplifies consistency but can over-generalize components. Choose a boundary that minimizes unstable public API and has a clear maintainer.

## Failure modes

Every feature-specific Retrofit interface is placed in core network, forcing core changes for all releases. Core UI accepts an `Order` domain object. Database migrations are added without the feature owner and break another variant. Multiple feature data modules configure incompatible HTTP clients accidentally.

## Production perspective

Publish module responsibilities and codeowners, track public API churn and affected builds, and test migrations and cross-feature integration. Review proposed core additions for genuine multi-feature reuse and stable semantics.

## Interview answer — short

“Core modules own stable cross-cutting infrastructure and UI primitives; features own their workflows, endpoints, state and business-specific presentation.”

## Interview answer — structured

“I put shared HTTP configuration in core network, database setup and migration tooling in core database, and neutral theme/components in core UI. The orders feature or its data module still owns orders endpoint mapping, schema policy and screen state. That prevents every product change from touching a high-fan-out core module. I make ownership of shared transactions and migrations explicit and keep core APIs narrow.”

## Interview answer — deep senior

“The labels are useful only if they express change ownership. `:core:network` should hold stable transport configuration—client setup, common interceptors and serialization facilities—not every feature's endpoint policy. `:core:database` can own a Room database shell and migration test infrastructure, while each feature's data owner remains accountable for its schema and queries even if they compile into a shared database artifact. `:core:ui` or design system provides tokens and generic components such as an accessible button; it should not import Orders entities to decide button text. Feature modules own screen state, events, navigation entry and workflow-specific rules, with feature data mapping its API and persistence models. I watch the public API of core because a small unstable change fans out to many builds and teams. There are exceptions: a cross-feature transaction or shared authenticated transport needs central coordination. I write those owners down, test migrations and app assembly, and look at change history. If every orders change modifies core, I likely placed policy at the wrong level.”

## How to answer in the interview

- **Why:** core should not absorb feature logic.
- **How:** define narrow infrastructure and feature ownership.
- **Trade-off:** reuse versus central bottleneck.
- **Failure case:** core imports feature DTO.
- **Production solution:** dependency direction and API audit.

## Deep-dive talking points

Discuss transport versus endpoint policy, physical database versus schema ownership, design-system neutrality and fan-out.

## Follow-up questions

- Where should an OrdersApi interface live? **Answer:** usually in orders data ownership, using shared transport infrastructure.
- Can a database be physically shared? **Answer:** yes, while schema/migration ownership remains explicit.
- Why avoid domain entities in core UI? **Answer:** it couples reusable components to one feature's business model.

## Self-check rubric

Place four concrete classes in modules, explain one shared exception, and identify a giant-core smell.

## References and reviewed-on date

- [Android modularization patterns](https://developer.android.com/topic/modularization/patterns) — feature and core roles.
- [Data layer guidance](https://developer.android.com/topic/architecture/data-layer) — repository ownership.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Physical schema split depends on project architecture.
