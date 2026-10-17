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

## Concept and technical explanation

Scalable multi-module architectures actively prevent two widespread architectural anti-patterns:
- Circular Dependencies: Where two or more modules depend on each other directly or transitively (A -> B -> C -> A), breaking Gradle's topological sort and halting builds. Prevention requires strictly unidirectional dependency flow, extracting shared API contracts into independent submodules, applying dependency inversion via Hilt, and enforcing architectural linters.
- Giant Core/Common Module: Where teams treat :core:common as an undisciplined dumping ground for unrelated utilities (auth, analytics, string formatters, image loaders). Because nearly all feature modules import common, any change invalidates the build cache project-wide, creating a disguised monolith. Prevention requires decomposing :core into highly cohesive, single-responsibility leaf modules (e.g., :core:dispatchers, :core:crypto, :core:designsystem) and strictly localizing feature-specific helpers within their respective domains.

## Practical walkthrough (English)

Decomposing a bloated core module and breaking circular loops via contract extraction:
```text
// ❌ ANTI-PATTERN: Giant core module that breaks build cache for all features
:core:common (contains: DateUtils, AuthTokenManager, PaymentModels, BarcodeScanner)

// ✅ PRODUCTION TOPOLOGY: Decomposed into single-responsibility leaf modules
:core/
  ├── dispatchers/       (CoroutineDispatchers, test dispatchers)
  ├── crypto/            (Keystore wrappers, encryption engines)
  ├── formatting/        (Currency and date formatters)
  └── designsystem/      (Compose theme, atomic UI components)

// Breaking a circular loop between :feature:profile and :feature:auth:
// :feature:profile depends on :feature:auth:api ONLY (Unidirectional flow)
// Neither module imports the other's internal implementation!
```

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

To avoid circular dependencies, enforce strictly unidirectional dependency flows and decouple cross-feature interactions using independent api contract modules and Hilt. To prevent giant core:common modules, dismantle monolithic utilities into focused, single-responsibility leaf modules like core:crypto and core:dispatchers, keeping feature-specific helpers strictly inside their owning domains.

## Interview answer — structured

Preventing circular dependencies and monolithic core modules requires deliberate architectural boundaries and automated governance.
Circular dependencies occur when modules import each other either directly or transitively, creating an impossible loop that halts Gradle compilation.
We resolve cycles by extracting shared models and interfaces into an independent, leaf-level api module, allowing both original modules to depend downward without cyclic coupling.
The giant core:common module is another common architectural pitfall where unrelated utilities are aggregated together.
Because every feature depends on common, a minor edit triggers application-wide recompilation and invalidates the remote build cache.
To eliminate this problem, we enforce a strict single-responsibility rule, decomposing common into focused leaf modules such as core:dispatchers, core:network, and core:designsystem.
Utilities that are not genuinely domain-agnostic are rejected from core and localized within their respective feature modules.

## Interview answer — deep senior

In enterprise Android development, unmonitored modular architectures naturally decay into circular loops and giant shared garbage modules unless actively governed.
The giant core:common anti-pattern is particularly destructive because it recreates monolith bottlenecks under the illusion of modularity.
When a single module holds database helpers, authentication tokens, image loading bindings, and string extensions, it sits at the foundation of the dependency tree.
Any trivial update to a string formatter invalidates the Gradle build cache for every downstream feature, destroying build performance across the company.
Our architectural policy decomposes shared infrastructure into highly cohesive, domain-agnostic leaf subprojects: :core:dispatchers, :core:database, :core:crypto, and :core:designsystem.
If a utility does not qualify as platform-level infrastructure—such as a formatOrderReference function—it is strictly confined inside its owning feature module.
To eradicate circular dependencies, we enforce unidirectional dependency layering: presentation depends on domain, data implements domain, and features communicate solely through isolated :api contracts wired via Hilt at the app level.
We enforce these structural invariants in our CI pipeline using automated Konsist tests that scan imports across all modules, immediately failing pull requests that attempt to introduce reverse dependency edges or instantiate monolithic shared modules. We also generate automated architectural diagrams during pull request builds, giving code reviewers instant visual feedback on any suspicious dependency edge additions before merging.

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
