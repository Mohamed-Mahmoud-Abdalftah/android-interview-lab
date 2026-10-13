---
id: "SYS-02"
question: "Design a scalable multi-feature Android application."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 331
editorial_status: "reviewed"
---

# SYS-02

## Original interview question

Design a scalable multi-feature Android application.

## What the interviewer evaluates

Design scalable multi-feature Android app with team boundaries, data ownership and build health.

## Explanation in Arabic

كيف تصمم تطبيق أندرويد ضخم متعدد الميزات (Scalable Multi-Feature Android Application) يعمل عليه عشرات الفرق؟

1. التحديات الهندسية للتطبيقات الضخمة (Multi-Team Scale):
   - بطء زمن التجميع والبناء (Build Times > 20 mins).
   - التبعيات الدائرية (Circular Dependencies) وتداخل الكود بين الفرق.
   - نزاعات الدمج المستمرة (Merge Conflicts) على ملفات الـ Navigation والـ DI.
   - صعوبة اختبار وتطوير ميزة معينة بشكل منعزل.

2. المعمارية المعيارية الموصى بها (Modular Architecture by Feature & Layer):
   - **قاعدة فصل الواجهة عن التنفيذ (API vs. Implementation Pattern)**: لكل ميزة (Feature) يتم تقسيمها إلى موديولين على الأقل:
     * `:feature:checkout:api`: يحتوي على الـ Interfaces, Data Transfer Objects, والـ Navigation Routes العامة فقط (كود خفيف جداً يترجم في ثوانٍ).
     * `:feature:checkout:impl`: يحتوي على الـ Internal Views, ViewModels, Repositories، ولا يعتمد عليه أي موديول آخر مباشرة.
   - **Core Layer (موديولات النواة)**:
     * `:core:designsystem`: مكونات Compose العامة والـ Themes.
     * `:core:network`: إعدادات OkHttp, Retrofit, Auth Interceptors.
     * `:core:database`: Room DB المشتركة والـ DAOs.
     * `:core:model`: الـ Shared Domain Entities.
   - **App Layer (`:app`)**: موديول تجميعي خفيف يربط كل الـ Implementations ببعضها عبر Dagger/Hilt دون أن تعرف الميزات كود بعضها الداخلي.

3. إدارة التنقل بين الشاشات دون اقتران (Decoupled Navigation):
   - استخدام Navigation Contracts أو Deep Links أو Service Locator لتوجيه المستخدمين بين الميزات دون أن يستورد موديول الشاشة أ موديول الشاشة ب.

## Practical walkthrough

تصميم نمط Feature API/Impl لعزل الميزات وتسريع التجميع ومنع التبعيات الدائرية:
```kotlin
// في موديول :feature:payment:api (لا يعتمد على أي موديول خارجي):
interface PaymentFeatureLauncher {
    fun launchPaymentFlow(orderId: String, amountCents: Long)
}

// في موديول :feature:cart:impl (يعتمد فقط على :feature:payment:api):
class CartViewModel @Inject constructor(
    private val paymentLauncher: PaymentFeatureLauncher // حقن عبر الـ Interface بدون معرفة تفاصيل PaymentActivity
) : ViewModel() {
    fun onCheckoutClicked(orderId: String, amount: Long) {
        paymentLauncher.launchPaymentFlow(orderId, amount)
    }
}

// في موديول :feature:payment:impl (ينفذ الـ API):
class PaymentFeatureLauncherImpl @Inject constructor(
    @ApplicationContext private val context: Context
) : PaymentFeatureLauncher {
    override fun launchPaymentFlow(orderId: String, amountCents: Long) {
        val intent = Intent(context, InternalPaymentActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
            putExtra("order_id", orderId)
            putExtra("amount", amountCents)
        }
        context.startActivity(intent)
    }
}
```

## Why it matters and how it works

Android architecture recommends UI/data layers and optional domain. Modularization can improve separation and parallel team work but adds configuration and API maintenance cost. Use stable public interfaces for cross-feature communication and navigation contracts. Local data source of truth and server APIs remain explicit.

## Worked example

Conceptual Gradle module graph, not executable code; arrows mean compile-time dependency.

```kotlin
// :app -> :feature:catalog, :feature:checkout
// :feature:checkout -> :core:payments-api, :core:ui
// :data:payments -> :core:payments-api, :core:network
// :app binds payments-api to data:payments in DI.
// No feature depends directly on another feature implementation.
```

## Trade-offs and decision criteria

A monolith is simpler for a small team; split when ownership, reuse or build isolation pays for added configuration. Avoid a giant core/common module that every change recompiles. Measure build time and coupling before/after split.

## Failure modes

Cross-feature concrete dependencies create cycles and block independent releases. Duplicated token/session ownership yields inconsistent logout. A feature owning server DTOs in UI makes backend version changes cascade through screens.

## Production perspective

A 20-team commerce app has team-owned feature APIs, central session/payment contracts, local Room data ownership and independent feature tests. CI measures dependency graph and incremental builds; release trains stage high-risk payment changes.

## Interview answer — short

Design a scalable multi-feature app by splitting features into separate :api and :impl modules, isolating shared functionality into low-level :core modules, enforcing unidirectional dependency rules, using dependency injection to bind interfaces at the root :app module, and decoupling navigation via contract interfaces or deep links.

## Interview answer — structured

Scaling an Android codebase across multiple autonomous engineering teams requires decoupling compilation and architectural boundaries:

1. **The Feature API / Implementation Separation**:
   - Split each business domain into two modules: `:feature:name:api` and `:feature:name:impl`.
   - The `:api` module exposes public interfaces, navigation arguments, and lightweight data contracts. Other features depend strictly on `:api`.
   - The `:impl` module contains internal composables, ViewModels, and data repositories. No other module depends directly on `:impl`.

2. **Layered Module Hierarchy**:
   - **App Layer (`:app`)**: Thin application orchestrator that includes all `:impl` modules and wires Dagger/Hilt dependency graphs.
   - **Feature Layer (`:feature:*`)**: Isolated vertical slices owning specific user journeys.
   - **Core Layer (`:core:*`)**: Horizontal building blocks (`:core:network`, `:core:database`, `:core:designsystem`, `:core:common`).

3. **Decoupled Navigation & Communication**:
   - Features navigate to other features via exposed entry-point interfaces or typed deep link contracts, eliminating direct cross-feature class imports.

4. **Build Performance Optimization**:
   - Decoupled modules leverage Gradle build caching, parallel execution, and configuration caching, preventing full-project recompilations when a single feature changes.

## Interview answer — deep senior

From an organizational and platform engineering perspective, modularization must be protected by governance tooling:

1. **Enforcing Dependency Direction via Tooling**: Architecture rules rot without automated guardrails. Use Gradle plugins like `dependency-analysis-android-plugin` or custom ArchUnit/Konsist tests to enforce that no feature module ever imports another feature's `:impl` module, and that `:core` modules never depend on `:feature` modules.

2. **Independent Standalone Sample Apps**: Each major feature module should maintain a lightweight `:feature:name:sample` runnable app module. Developers on the checkout team can run and iterate on their feature in isolation within 5 seconds without compiling the remaining 50 features of the monolithic app.

3. **Binary Dependency Substitution**: In mega-apps (100+ engineers), build times can be further reduced by substituting local module projects with pre-compiled AAR artifacts hosted on an internal Maven cache for modules outside the engineer's active feature domain.

## How to answer in the interview

- **Why:** runtime and team scaling both depend on boundaries.
- **How:** define feature owners, narrow APIs, acyclic dependencies, and data authority.
- **Trade-off:** modules add Gradle and contract maintenance costs.
- **Failure case:** a giant shared core or feature-to-feature implementation dependency.
- **Production solution:** measure change impact and build time, then split at stable ownership seams.

## Deep-dive talking points

Draw acyclic graph with owners; defend where shared domain code lives and how CI measures benefit.

## Follow-up questions

- **Interviewer:** "What happens if two feature modules have a circular dependency?"
  **Answer:** "Gradle refuses to build due to circular task graphs; the circular relationship must be broken by extracting the shared contract into an independent :api module or a shared :core module."

- **Interviewer:** "Why is it dangerous to put all shared models in a single :core:models module?"
  **Answer:** "It becomes a god-module; modifying any single entity triggers a complete project-wide recompilation across all dependent modules."

## Self-check rubric

Can I assign data/team ownership, draw acyclic dependencies and identify runtime/build metrics?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — UI/data layers and SSOT.
- [Android modularization guide](https://developer.android.com/topic/modularization) — module boundaries.

Technically reviewed against primary documentation on 2026-10-13.
