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

## Concept and technical explanation

When a monolithic shared data model (such as a generic User or Account entity) changes, it acts as a compilation bottleneck that invalidates compile classpaths and forces cascading recompilations across dozens of dependent feature modules. Shrinking this blast radius requires applying structural decoupling techniques:
1. Bounded Context Domain Slicing: Decomposing the "God Model" into cohesive, feature-scoped value objects (e.g., splitting a 50-field User into UserIdentity for auth, UserShippingAddress for checkout, and UserFinancialProfile for billing).
2. Interface Segregation: Exposing focused, read-only interface contracts rather than concrete models, so adding private fields to an implementation does not alter the consumer's ABI.
3. Anti-Corruption Layers (ACL) & Local Mappers: Feature modules define their own internal UI/Domain representations, mapping the external shared model at their ingestion boundary. Internal feature logic never depends directly on the shared model.
4. ABI-Safe Default Parameters: In Kotlin, adding fields with default arguments preserves constructor compatibility, preventing downstream source breaking.

## Practical walkthrough (English)

Slicing a bloated shared model and using local mappers to protect compilation boundaries:
```kotlin
// ❌ MONOLITHIC SHARED MODEL (:core:model)
// Changing one field forces recompilation of 30 feature modules!
// data class User(val id: String, val name: String, val email: String, val creditScore: Int, val address: String, ...)

// ✅ BOUNDED CONTEXT SLICING & LOCAL MAPPING
// 1. :core:model exports minimal, stable identity contract
data class UserIdentifier(val id: String, val username: String)

// 2. :feature:checkout defines its OWN local model with only what it needs
internal data class CheckoutCustomer(val id: String, val shippingAddress: String)

// 3. Local Mapper converts at boundary; changes to financial fields NEVER recompile checkout!
internal fun UserProfileDto.toCheckoutCustomer() = CheckoutCustomer(
    id = this.id,
    shippingAddress = this.defaultAddress
)
```

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

To shrink the recompilation impact of a shared model change, decompose monolithic data models into focused, bounded-context domain slices. Have features depend on read-only interfaces or define local internal models mapped at the boundary through an Anti-Corruption Layer, isolating feature internals from changes to shared infrastructure models.

## Interview answer — structured

When a widely shared data model changes, it triggers cascading recompilations across the entire multi-module dependency graph.
To shrink this blast radius, we eliminate monolithic God Models by slicing them into focused, bounded-context entities.
Instead of a single User class with fifty fields consumed by every module, we create targeted models like UserIdentity for authentication and ShippingAddress for checkout.
Features only import the lightweight slice relevant to their business domain.
Furthermore, feature modules should establish an Anti-Corruption Layer by defining internal domain representations.
The feature maps the incoming shared model into its internal representation at the repository boundary.
If a field is added, modified, or removed in the shared model, edits are confined to that single boundary mapper.
The feature's ViewModels, Compose screens, and internal tests remain completely insulated from recompilation.

## Interview answer — deep senior

The 'God Model' is one of the most insidious architectural anti-patterns in multi-module Android systems.
When a shared entity like User, Order, or Transaction sits in a foundational core module and accumulates fields from multiple teams, it acts as a massive compilation dependency bottleneck.
Every time an engineer adds a field to support a profile screen experiment, Gradle's ABI hashing detects a change in the core module's bytecode signatures, invalidating the compile classpath for twenty downstream feature modules.
We resolve this systematically by applying Domain-Driven Design bounded contexts and interface segregation.
First, we slice the bloated entity into lean, role-specific value objects.
A checkout feature has no business knowing a user's credit score or notification preferences; it requires solely a ShippingContact and a PaymentBillingAddress.
Second, we enforce an Anti-Corruption Layer at feature module boundaries.
Feature modules maintain their own internal, immutable domain models.
The feature repository receives data from the shared network or database layer and maps it immediately into internal feature models using extension functions hidden behind internal visibility.
Consequently, when the shared backend DTO or core model changes, the blast radius is strictly confined to that single mapper function.
The feature's domain use cases, ViewModels, and UI layouts remain untouched, preserving the Gradle build cache and shielding engineering squads from cross-team recompilation cascades.

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
