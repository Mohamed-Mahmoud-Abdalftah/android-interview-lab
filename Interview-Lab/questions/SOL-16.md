---
id: "SOL-16"
question: "How do you identify cohesive responsibilities within a God Class?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 187
editorial_status: "reviewed"
---

# SOL-16

## Original interview question

How do you identify cohesive responsibilities within a God Class?

## What the interviewer evaluates

Diagnose God Class responsibilities using change history, clients, data flow and safe extraction.

## Explanation in Arabic

كيف تحدد وتكتشف المسؤوليات المتماسكة (Cohesive Responsibilities) داخل كلاس متضخم (God Class)؟

1. ما هو الـ God Class في Android؟
   - كلاس ضخم (1,500 إلى 3,000 سطر) يسيطر على كل شيء؛ يقرأ الحساسات، ويطلب الشبكة، ويعدل قاعدة البيانات، وينسق الرسوم، ويتعامل مع الأذونات (مثل كلاس `OrderManager` أو `MainActivity`).

2. المنهجية العلمية لتحديد المسؤوليات المتماسكة داخل الكلاس:
   - **فحص استخدام المتغيرات المشتركة (LCOM - Lack of Cohesion of Methods)**:
     * انظر إلى خصائص الكلاس (Fields): ستجد مجموعة دوال (A, B, C) تستخدم فقط `LocationManager` و `gpsCoordinates`.
     * ومجموعة أخرى (D, E, F) تستخدم فقط `RetrofitOrderApi` و `authToken`.
     * ومجموعة ثالثة تستخدم فقط `Dialog` و `Toast`.
     * هذه المجموعات المنفصلة هي كلاسات جديدة تنادي عليك لاستخراجها فوراً!
   - **فحص أصحاب المصلحة (Stakeholders / Business Actors)**:
     * اسأل نفسك: من يطلب تعديل هذا الجزء؟ هل هو فريق الـ UI؟ أم فريق الـ Backend؟ أم فريق الأمان؟
   - **فحص التسميات (Naming Smells)**: الدوال التي تبدأ بـ `calculate...`, `validate...`, `format...` غالباً ما تكون وظائف Domain يجب فصلها عن وظائف التخزين `save...` و `fetch...`.

## Practical walkthrough

تحليل وتفكيك God Class إلى مكونات متماسكة:
```kotlin
// ❌ God Class يجمع حقولاً غير متجانسة إطلاقاً:
class MonolithicCartManager {
    // Cluster 1: موقع جغرافي لحساب التوصيل
    var userLat: Double = 0.0
    var userLng: Double = 0.0
    fun updateGpsLocation() { ... }

    // Cluster 2: حسابات الضرائب والخصومات (Domain Rules)
    fun applyDiscountCoupon(code: String) { ... }
    fun calculateVatTax(subtotal: Long): Long { ... }

    // Cluster 3: التخزين وقاعدة البيانات (Data Storage)
    fun persistCartToDatabase() { ... }
    fun syncWithBackendApi() { ... }
}

// ✅ التفكيك إلى كلاسات عالية التماسك (High Cohesion):
// 1. DeliveryLocationProvider (مسؤول عن الموقع فقط)
class DeliveryLocationProvider { ... }

// 2. CartPricingEngine (مسؤول عن حسابات الضرائب والخصومات في Domain)
class CartPricingEngine { ... }

// 3. CartRepository (مسؤول عن حفظ البيانات ومزامنة السيرفر في Data)
class CartRepository { ... }
```

## Why it matters and how it works

Cohesion is about related change pressure and invariants. A large class can be coherent; a small class can still mix unrelated reasons. Safe extraction requires understanding state, side effects and caller contracts.

## Worked example

Refactor plan for `CheckoutManager`: (1) test submit/timeout/duplicate tap; (2) move provider SDK mapping to adapter; (3) move eligibility into a policy component; (4) keep UI state transition in ViewModel; (5) move durable request tracking to repository. Measure changed-file locality afterward.

## Trade-offs and decision criteria

Incremental extraction temporarily leaves adapters and duplicate paths but lowers risk. A big-bang rewrite may be faster on paper yet miss hidden behavior. Avoid microscopic classes that split one invariant across too many owners.

## Failure modes

A team moves `calculateFee()` to `FeeUseCase` but leaves mutable cart state in God Class, so the new method still reaches back into shared fields. Pass explicit inputs and define ownership. Test concurrent/timeout behavior before changing flow.

## Production perspective

A commerce team uses production incident history to prioritize extracting payment SDK code from a 1,200-line coordinator. They monitor decline/timeout metrics during rollout and keep rollback available.

## Interview answer — short

Identify cohesive responsibilities in a God Class by analyzing field-method clustering (identifying groups of methods that operate on isolated subsets of class variables), grouping methods by the business actors requesting changes, and isolating orthogonal concerns like validation, storage, and UI into dedicated classes.

## Interview answer — structured

Dismantling a God Class requires an objective, metric-driven analysis of internal cohesion rather than subjective guesswork.

1. **Variable-Method Clustering (LCOM - Lack of Cohesion of Methods)**:
   - Map out the class fields and observe which methods access which properties.
   - In a God Class, methods naturally form isolated clusters: Methods A, B, and C only read and write location coordinates; Methods D and E only touch the network client; Methods F and G only manipulate formatting and UI dialogs.
   - Each distinct cluster represents a distinct cohesive class waiting to be extracted.

2. **Actor Alignment (Single Reason to Change)**:
   - Group methods by the business stakeholder who commands their changes:
     * Methods requested by UI designers belong in the Presentation/UI layer.
     * Methods requested by accountants or product rules (tax rules, loyalty points) belong in Domain Use Cases.
     * Methods requested by infrastructure or backend changes belong in the Data Repository.

3. **Linguistic Clustering (Naming & Verb Analysis)**:
   - Look for method prefixes: `validate*()` indicates a Validator, `format*()` indicates a Mapper/Formatter, `sync*()` or `save*()` indicates a Repository.

## Interview answer — deep senior

Static analysis tools (like SonarQube, Detekt, or Konsist) formalize this process. Detekt flags classes violating `ComplexInterface`, `LargeClass` (e.g. >600 LOC), or `TooManyFunctions` (>15 methods). When these metrics trigger, we run an automated dependency structure matrix (DSM) in IntelliJ/Android Studio to visualize coupling blocks.

Once clusters are identified, refactor using the **Extract Class refactoring technique**:
- Step 1: Create the new focused class (`DeliveryCalculator`).
- Step 2: Delegate the God Class's methods to an instance of the new class.
- Step 3: Update client callers to inject the new class directly, gradually strangling the legacy God Class.

## How to answer in the interview

- **Why:** Use change history and invariants.
- **How:** describe extraction order.
- **Trade-offs:** mention temporary migration cost.
- **Failure cases:** flag cyclic cosmetic split.
- **Production solutions:** close with behavior tests and change-locality evidence..

## Deep-dive talking points

Use change history, state-field map, call graph and characterization tests to find cohesive slices.

## Follow-up questions

- **Interviewer:** "What is LCOM (Lack of Cohesion of Methods)?"
  **Answer:** "A software metric that measures the disparity between methods and fields in a class. High LCOM indicates low cohesion, proving that a class is doing too many unrelated things and should be split."

- **Interviewer:** "How do God Classes negatively affect team velocity and Git workflows?"
  **Answer:** "Multiple developers working on different features simultaneously edit the same massive file, creating frequent and painful merge conflicts, broken builds, and duplicated regression testing."

## Self-check rubric

Identify three change actors and one shared invariant in a God Class; propose a first safe extraction.

## References and reviewed-on date

- [Robert C. Martin, SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — reasons to change.
- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns.

Technically reviewed against primary documentation on 2026-10-13.
