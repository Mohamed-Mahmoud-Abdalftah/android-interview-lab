---
id: "SOL-18"
question: "A new payment provider requires editing 10 existing classes. Which principles would help?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "C"
phase: 2
priority: "P1"
order: 189
editorial_status: "reviewed"
---

# SOL-18

## Original interview question

A new payment provider requires editing 10 existing classes. Which principles would help?

## What the interviewer evaluates

Use OCP/DIP/SRP/ISP/LSP together for a provider change that touches too much code.

## Explanation in Arabic

عندما يتطلب إضافة مزود دفع جديد (New Payment Provider) تعديل 10 كلاسات موجودة مسبقاً في التطبيق: ما هي المبادئ الهندسية التي تعالج ذلك؟

1. المبادئ الهندسية المنتهكة والتي يجب تطبيقها:
   - **المبدأ الأول: مبدأ الفتح والإغلاق (OCP - Open/Closed Principle)**:
     * وجود الحاجة لتعديل 10 كلاسات يعني أن الكود **مغلق للتوسيع ومفتوح للتعديل** (عكس OCP تماماً!).
     * الحل: تحويل نظام الدفع إلى **Strategy Pattern** حيث يتم تعريف واجهة `PaymentProvider`، وإضافة أي مزود جديد تعني فقط إنشاء كلاس جديد دون لمس الكلاسات القديمة.
   - **المبدأ الثاني: مبدأ المسؤولية الواحدة (SRP - Single Responsibility Principle)**:
     * تشتت منطق الدفع عبر 10 كلاسات يعني غياب التماسك وتشتت المسؤوليات؛ كلاسات الـ UI والـ Navigation وقواعد البيانات تفحص نوع الدفع بنفسها!
     * الحل: تركيز كل ما يخص الدفع داخل `PaymentRepository` و `PaymentRouter` واحد.
   - **المبدأ الثالث: مبدأ عكس التبعية (DIP - Dependency Inversion Principle)**:
     * الكلاسات الـ 10 تعتمد على كلاسات ملموسة لمزودي الدفع السابقين بدلاً من الاعتماد على تجريد موحد.

2. النتيجة بعد تطبيق المبادئ:
   - إضافة المزود رقم 11 ستتطلب إنشاء **ملف واحد جديد فقط** وتسجيله في الـ DI دون المساس بأي من الكلاسات الـ 10!

## Practical walkthrough

إعادة هندسة تدفق الدفع ليكون محكوماً بـ OCP و Strategy Pattern:
```kotlin
// ❌ الكود المكسور القديم: إضافة مزود جديد تجبرك على فتح 10 كلاسات وتعديل when(type):
// 1. CheckoutViewModel.kt -> when(type)
// 2. PaymentValidator.kt -> when(type)
// 3. ReceiptFormatter.kt -> when(type)
// 4. AnalyticsTracker.kt -> when(type)...

// ✅ الحل المعماري المحكم: دمج المسؤوليات في Strategy Component متكاملة:
interface PaymentGateway {
    val methodId: PaymentMethodId
    fun validate(details: PaymentDetails): Boolean
    suspend fun executePayment(amount: Long, details: PaymentDetails): PaymentResult
    fun formatReceipt(result: PaymentResult): ReceiptUiModel
}

// إضافة مزود جديد (مثل Fawry أو ApplePay) يتطلب ملفاً واحداً فقط يجمع كل تفاصيله:
class FawryPaymentGateway @Inject constructor(...) : PaymentGateway {
    override val methodId = PaymentMethodId.FAWRY
    override fun validate(details: PaymentDetails) = ...
    override suspend fun executePayment(amount: Long, details: PaymentDetails) = ...
    override fun formatReceipt(result: PaymentResult) = ...
}

// الـ Router يستقبل Set<PaymentGateway> عبر Hilt؛ لا تعديل في أي كلاس قديم!
class PaymentRouter @Inject constructor(private val gateways: Set<PaymentGateway>) { ... }
```

## Why it matters and how it works

Scattered provider conditionals indicate a missing variation boundary. A narrow strategy adapter localizes SDK differences; stable policy remains shared. Substitution and error semantics are critical to safe replacement.

## Worked example

Migration sketch: extract one `PaymentGateway` contract from existing provider path, write contract tests, route current provider through adapter, then add second provider adapter and composition binding. Keep server-side provider credentials and final transaction verification.

## Trade-offs and decision criteria

A strategy layer is worth the cost if providers change or SDKs differ materially. For one stable provider, a concrete repository may be simpler. Avoid a god-factory that knows every SDK and business rule.

## Failure modes

One provider reports a timeout as confirmed failure and the UI retries, risking duplicate charge. Contract tests must require `PendingVerification` for uncertainty and reconciliation with the backend.

## Production perspective

A commerce app adds wallet provider by writing an adapter, binding it, and testing shared checkout policy plus provider-specific error mapping. Metrics compare outcomes across providers without leaking payment data.

## Interview answer — short

The primary principle to apply is Open/Closed Principle (OCP) using the Strategy Pattern and Polymorphism, supported by Single Responsibility Principle (SRP) to stop spreading payment logic across disparate classes, and Dependency Inversion Principle (DIP) to decouple orchestrators from concrete provider SDKs.

## Interview answer — structured

If integrating a single new payment provider requires editing 10 existing classes across your application, the codebase is suffering from severe **shotgun surgery** caused by violating core SOLID principles.

1. **Open/Closed Principle (OCP) - The Primary Cure**:
   - The 10 classes are littered with type checks (`when (paymentType)` or `if (type == "STRIPE")`).
   - **The Fix**: Abstract provider behavior behind a cohesive `PaymentGateway` interface (The Strategy Pattern). The payment orchestrator dynamically delegates to an injected collection (`Set<PaymentGateway>`), closing existing classes to modification.

2. **Single Responsibility Principle (SRP)**:
   - Payment details (validation, fee calculation, API invocation, receipt rendering) are smeared across 10 unrelated classes (Activities, ViewModels, Analytics, Storage).
   - **The Fix**: Encapsulate all provider-specific behaviors inside the concrete `PaymentGateway` implementation. A new provider now requires authoring **exactly one new class**.

3. **Dependency Inversion Principle (DIP)**:
   - Consumers depend directly on concrete third-party payment SDKs (Stripe SDK, PayPal SDK) rather than an internal domain abstraction.
   - **The Fix**: The domain layer defines the payment abstraction, and adapters in the data layer isolate third-party SDK dependencies.

## Interview answer — deep senior

In software metrics, this code smell is called **Shotgun Surgery** (a single conceptual change requires making lots of little edits to many different classes), which is the exact polar opposite of **Divergent Change** (one class is commonly changed in different ways for different reasons).

Shotgun surgery introduces high regression risk: if an engineer forgets to update class #9 or #10, the bug only surfaces in production under specific edge cases.

By encapsulating the provider behind a Strategy interface and leveraging Dagger Multibindings (`@IntoSet`), adding a new provider becomes an **additive-only change**: create `GooglePayGateway.kt`, bind it in Hilt, and create its dedicated unit test. Zero existing classes are touched, zero merge conflicts occur, and existing payment flows remain completely safe.

## How to answer in the interview

- **Why:** Trace the ten edits.
- **How:** propose one variation seam.
- **Trade-offs:** note legitimate registration edits.
- **Failure cases:** flag false uniformity.
- **Production solutions:** finish with adapter contracts and backend verification..

## Deep-dive talking points

Trace ten edits to one variation axis, propose migration steps, and verify provider contract semantics.

## Follow-up questions

- **Interviewer:** "What is 'Shotgun Surgery' in code smell taxonomy?"
  **Answer:** "A code smell where a single conceptual modification requires making many small changes to multiple classes across the codebase, indicating poor encapsulation and OCP violations."

- **Interviewer:** "How do you verify in CI that OCP is respected for new payment providers?"
  **Answer:** "By inspecting Git diffs in pull requests: adding a new payment feature should only add new files (additions) without modifying existing payment routing files (zero modifications to existing lines)."

## Self-check rubric

Name three principles relevant to provider churn, show one contract, and include timeout reconciliation.

## References and reviewed-on date

- [Robert C. Martin, OCP](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — extension boundaries.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — adapter ownership.

Technically reviewed against primary documentation on 2026-10-13.
