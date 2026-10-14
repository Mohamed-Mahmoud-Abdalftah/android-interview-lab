---
id: "MOD-18"
question: "A shared model change forces recompilation of many modules. How would you shrink the impact?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "C"
phase: 4
priority: "P1"
order: 371
editorial_status: "reviewed"
---

# MOD-18

## Original interview question

A shared model change forces recompilation of many modules. How would you shrink the impact?

## What the interviewer evaluates

- Diagnose high fan-out and public ABI rather than assume Gradle bug.
- Propose stable contracts or smaller ownership boundaries.
- Measure task graph and preserve semantic correctness.

## Explanation in Arabic

تغيير سطر واحد في نموذج بيانات مشترك (Shared Model) أدى إلى إعادة تجميع عشرات الموديولات في المشروع. كيف تشخص المشكلة وتحد من أثرها الكارثي؟

1. تشخيص السبب الجذري (Root Cause Diagnosis):
   - **تضخم الاعتمادية وانتشار الـ Fan-out (High Build Fan-out)**: موديول يسمى `:core:model` يحتوي على كلاس `User` أو `Order`. هناك 40 موديول Feature يعتمدون على هذا الموديول مباشرة.
   - **تسريب الـ ABI (ABI Invalidation)**: عند إضافة حقل جديد (مثل `val isVip: Boolean = false`) لكلاس الـ `User`، فإن الـ ABI Digest الخاص بـ `User` يتغير بالكامل.
   - لأن جميع الموديولات تستورد هذا الكلاس في دوالها العامة، يعتبر Gradle أن الـ Compile Classpath لجميع هذه الموديولات الـ 40 قد فُقدت صلاحيته، فيلغي الـ Build Cache ويعيد تجميعها جميعاً من الصفر!

2. الحلول المعمارية للحد من الأثر (Architectural Solutions):
   - **تجزئة الموديل العام إلى نماذج متخصصة ومستقلة (Model Segregation)**: بدلاً من كائن `User` عملاق يحتوي على 50 حقلاً، افصله إلى نماذج بيانات مركزة:
     * `UserAuthCredentials` في موديول التحقق.
     * `UserBillingProfile` في موديول المدفوعات.
     * `UserShippingAddress` في موديول التوصيل.
   - **استخدام Feature-Specific UI Models مع Mappers**: موديول الـ Feature يعرّف نموذج الـ UI الخاص به (`UserProfileUiState`)، ويقوم بعمل Mapping من الموديل العام، مما يعزل الشاشات عن التغييرات الخارجية.
   - **تجنب وضع دوال `inline` داخل الموديولات المشتركة**: الدوال الـ Inline تجبر المترجم على تتبع الكود في كل مكان تم استدعاؤها فيه.

## Practical walkthrough

تفكيك الموديل العملاق عالي التأثير إلى نماذج متخصصة ضيقة الأثر:
```kotlin
// ❌ الموديل المشترك الكارثي (God Model في :core:model): أي تغيير يعيد تجميع 40 موديولاً:
data class User(
    val id: String,
    val name: String,
    val email: String,
    val creditCardToken: String, // يخص الدفع فقط
    val loyaltyPoints: Int,      // يخص المكافآت فقط
    val shippingAddress: String  // يخص الشحن فقط
)

// ✅ الحل المعماري: تجزئة النماذج حسب النطاق (Scoped Domain Models):
// 📁 في :domain:auth:
data class AuthenticatedUser(val id: String, val email: String)

// 📁 في :domain:payment:
data class PaymentCustomer(val userId: String, val creditCardToken: String)

// 📁 في :domain:loyalty:
data class LoyaltyMember(val userId: String, val points: Int)

// الآن: تعديل نظام نقاط المكافآت (Loyalty) في :domain:loyalty
// يعيد تجميع موديول المكافآت فقط! موديول الدفع وموديول المصادقة يظلان UP-TO-DATE بنسبة 100%.
```

## Why it matters and how it works

Changing a type in a high-fan-out API can invalidate downstream compile inputs. `api` edges and public signatures propagate visibility. Breaking one giant shared model into stable domain primitives and local presentation models can localize feature changes, but only if the contracts truly differ. Gradle configuration, annotation processing and resources may still drive work beyond ABI effects.

## Worked example

A `User` model includes account ID, profile image, loyalty tier, payment eligibility and admin flags. Changing a profile field rebuilds checkout and admin modules. Keep account identity and authorization rules in stable owned contracts; let profile and checkout map only needed data into their feature models. Move a library used solely by profile from `api` to `implementation` after public ABI is cleaned.

## Trade-offs and decision criteria

More models and mapping add code but reduce shared API churn and feature coupling. Excessive fragmentation can obscure one authoritative rule. The decision needs both build task evidence and correctness tests; a copied payment eligibility calculation is worse than a slow build.

## Failure modes

`implementation` is used despite public type exposure and consumers fail. Multiple feature copies of authorization policy drift. The model is split by field rather than ownership, creating many unstable micro-APIs. A build-speed conclusion comes from one noisy clean build.

## Production perspective

Track ABI and public API churn of high-fan-out modules, compare representative incremental builds, and test mappings and shared invariants. Use dependency reports and compiler/build scans to locate the actual invalidation path.

## Interview answer — short

A shared model change triggers massive rebuilds due to high fan-out and ABI invalidation. Shrink the impact by decomposing the monolithic model into domain-scoped models (e.g. AuthUser, BillingUser), introducing feature-specific UI models with local mappers, and moving stable primitives into isolated contract modules.

## Interview answer — structured

When modifying a shared data model causes dozens of modules to recompile, the root cause is **Unconstrained Module Fan-Out combined with Public ABI Invalidation**.

First, a Root Cause is a foundational module (like `:core:model`) exports an oversized entity (e.g. `User` with 40 fields) consumed transitively by 30+ feature modules. Adding or modifying a single property alters the compiled bytecode signatures (the ABI digest). Gradle detects the ABI mismatch and invalidates the compile classpath for every downstream module. Next, **Architectural Remediation**.
Additionally, with Domain Model Segregation, split the monolithic entity into bounded-context models. The payment feature needs `BillingAccount`, the delivery feature needs `DeliveryRecipient`, and the auth feature needs `AuthIdentity`. Each lives in its respective domain module. With Feature-Level UI Models & Adapters, feature modules should map domain models into internal UI state data classes (`CheckoutUiState`). A change in backend metadata does not alter the feature's internal ABI.
Finally, with Eliminate `inline` Functions on Models, never declare inline utility functions on shared models; inline bytecode embedding guarantees full caller recompilation.


## Interview answer — deep senior

To diagnose and monitor fan-out rebuild cascades quantitatively.

First, with Run Gradle with Profiling, execute `./gradlew assembleDebug --profile --scan`. The Gradle Build Scan's 'Timeline' and 'Performance' tabs reveal exactly which task invalidated the cache and triggered the cascade. Next, with Inspect the ABI Diff, compare task inputs using Gradle's verbose log: `./gradlew assembleDebug --info | grep -i "ABI changed"`. This confirms whether a public signature or private method triggered downstream compilation.
Finally, with Graph Fan-Out Metrics, in CI, track the **Fan-In (afferent coupling)** of core modules. If a single module's fan-in exceeds 50% of the repository's modules, it is an architectural hazard and must be prioritized for decomposition into independent, stable API slices.


## How to answer in the interview

- **Why:** public model churn propagates.
- **How:** narrow API and implementation edges.
- **Trade-off:** duplication versus compile isolation.
- **Failure case:** DTO made public to all features.
- **Production solution:** profile affected modules after change.

## Deep-dive talking points

Discuss ABI fan-out, `api` leakage, domain versus UI models, mapping cost, build scans and invariant ownership.

## Follow-up questions

- **Interviewer:** "Why does adding a private property to a public Kotlin data class invalidate ABI?"
  **Answer:** "Because in Kotlin, data classes auto-generate public methods (`copy()`, `componentN()`, `equals()`, `hashCode()`) based on all constructor properties; changing any property alters those public signatures."

- **Interviewer:** "How does using interfaces instead of data classes mitigate ABI rebuilds?"
  **Answer:** "Consumers depend on the stable interface; the concrete implementation can add internal fields without altering the interface's ABI signature."

## Self-check rubric

Trace one rebuild chain, redesign a shared model boundary, and verify build and behavior.

## References and reviewed-on date

- [Gradle Java Library Plugin](https://docs.gradle.org/current/userguide/java_library_plugin.html) — compile classpath boundaries.
- [Android modularization guide](https://developer.android.com/topic/modularization) — API and graph design.

Technically reviewed against primary documentation on 2026-10-13.
