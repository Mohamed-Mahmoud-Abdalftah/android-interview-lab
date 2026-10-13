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

كيف تتجنب التبعيات الدائرية (Circular Dependencies) وتمنع تضخم الموديولات العامة العملاقة (`:core:common` / `:core:base`)؟

1. أزمة موديول الـ Common العملاق (The 'God Module' Anti-pattern):
   - يبدأ المطورون بموديول `:core:common` لوضع دالة بسيطة لتنسيق التاريخ. بعد عام، يتحول إلى مستودع فوضوي يحتوي على: Retrofit DTOs، كلاسات Room، مكونات UI، ودوال تعامل مع الـ Bluetooth!
   - **الكارثة**: كل موديول في التطبيق يعتمد على `:core:common`. أي تعديل في سطر واحد فيه يعيد تجميع التطبيق بالكامل (High Build Fan-out)، وتضيع كل فوائد الـ Modularization.

2. استراتيجيات الوقاية وتفكيك الـ God Module:
   - **التفكيك إلى موديولات متخصصة عالية التماسك (High-Cohesion Slices)**: استبدال `:core:common` بـ:
     * `:core:model` (نماذج البيانات المشتركة النظيفة فقط).
     * `:core:network` (إعدادات الشبكة فقط).
     * `:core:designsystem` (مكونات الواجهة فقط).
   - **السماح بتكرار الكود البسيط (Accepting Benign Duplication)**: كتابة دالة مساعدة من سطرين (`fun String.isValidEmail()`) في موديولين مختلفين أفضل بمليون مرة من ربط الموديولين بموديول عام ضخم.

3. حل التبعيات الدائرية ومنعها آلياً:
   - فرض مسارات التبعيات باتجاه واحد (Unidirectional Flow) للأسفل دائماً.
   - استخدام أدوات التحقق التلقائي في الـ CI (مثل Dependency Analysis Plugin أو Lint Rules) لمنع أي موديول Core من الاعتماد على Feature، وحظر أي تبعية دائرية قبل الدمج.

## Practical walkthrough

تفكيك موديول :core:common الفوضوي إلى موديولات محددة المسؤولية:
```text
❌ قبل التفكيك (God Module :core:common): موديول ضخم يكسر الـ Build Cache ويعيد بناء كل شيء:
:feature:cart ──┐
:feature:feed ──┼──► ┌──────────────────────────────────────────────┐
:feature:auth ──┘    │               :core:common                   │
                     │ (DateUtils, DTOs, RoomDAOs, Compose Theme)   │
                     └──────────────────────────────────────────────┘

✅ بعد التفكيك إلى موديولات مركزة عالية التماسك:
:feature:cart ──────► :core:designsystem (Compose tokens only)
:feature:feed ──────► :core:model (Immutable data classes only)
:feature:auth ──────► :core:network (Network clients only)

كل موديول يعتمد فقط على ما يحتاجه بدقة! تعديل كود الشبكة لا يعيد تجميع Compose Theme أو :feature:cart إطلاقاً.
```

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

Avoid giant common modules by decomposing them into highly focused, single-responsibility modules (:core:model, :core:network, :core:ui). Prefer benign duplication of trivial 2-line helpers over introducing heavy shared dependencies. Enforce acyclic graphs using CI architecture lint rules and API contract extractions.

## Interview answer — structured

The emergence of a giant `:core:common` module and circular dependency loops are the two primary symptoms of an unmaintained multi-module architecture:

1. **Eradicating the `:core:common` God Module**:
   - A monolithic common module has near-infinite fan-out; every feature imports it, meaning any single edit invalidates the build cache for the entire application.
   - Dismantle it into focused, cohesive modules based on stability and responsibility: `:core:model` (pure data entities), `:core:designsystem` (UI tokens), `:core:network` (networking), and `:core:analytics`.
   - Tolerate **benign duplication**: It is far better to duplicate a 3-line string formatting extension across two feature modules than to create a shared build dependency between them.

2. **Eliminating Circular Dependencies**:
   - Cycles (`A -> B -> A`) occur when feature boundaries are blurred. Resolve them by extracting the shared data models or route contracts into an independent `:feature:x:api` module that both modules depend on downward.
   - Enforce unidirectional graph rules in CI using Gradle architecture validation plugins.

## Interview answer — deep senior

In large engineering organizations, preventing architectural entropy requires **Automated Guardrails rather than developer vigilance**.

Teams implement **Gradle Module Graph Rules** via custom Gradle tasks or plugins like `dependency-guard` or `ArchUnit`:

```kotlin
// Example Gradle constraint verification in build-logic:
tasks.register("assertModularizationRules") {
    doLast {
        project.subprojects.forEach { subproject ->
            if (subproject.path.startsWith(":core")) {
                subproject.configurations.all { config ->
                    config.dependencies.forEach { dep ->
                        if (dep.name.startsWith("feature")) {
                            throw GradleException("ILLEGAL DEPENDENCY: Core module ${subproject.path} cannot depend on feature ${dep.name}!")
                        }
                    }
                }
            }
        }
    }
}
```
Running this verification on pull request CI guarantees that forbidden edges (Core depending on Feature, or Feature-to-Feature direct implementation coupling) fail the build automatically.

## How to answer in the interview

- **Why:** cycles and giant core harm independence.
- **How:** extract narrow contract and compose at top.
- **Trade-off:** extra module versus central sprawl.
- **Failure case:** common contains business from every feature.
- **Production solution:** CI graph checks and API budgets.

## Deep-dive talking points

Explain topological order, API extraction, app shell, justified merge, common-module fan-out and CI enforcement.

## Follow-up questions

- **Interviewer:** "What is the 'Rule of Three' for extracting shared code into a module?"
  **Answer:** "Do not extract shared code when you see the second usage. Wait until a third distinct consumer requires it, ensuring the abstraction is genuinely stable and necessary."

- **Interviewer:** "Can Gradle enforce module boundary visibility automatically?"
  **Answer:** "Yes, by configuring dependency constraints or using Gradle's Experimental Isolated Projects feature to validate cross-module access."

## Self-check rubric

Resolve a feature cycle, explain a common-module smell, and name a preventive graph check.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — dependency graph and ownership.
- [Common modularization patterns](https://developer.android.com/topic/modularization/patterns) — API boundaries.

Technically reviewed against primary documentation on 2026-10-13.
