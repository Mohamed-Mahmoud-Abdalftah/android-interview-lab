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

## Concept and technical explanation

When integrating a single new payment provider forces changes across ten existing classes, the codebase is suffering from the 'Shotgun Surgery' architectural code smell, directly violating the Open/Closed Principle (OCP), the Single Responsibility Principle (SRP), and the Dependency Inversion Principle (DIP). In well-architected systems, adding a variant capability should be an additive change requiring zero edits to existing, tested orchestration code. By encapsulating payment execution behind a polymorphic PaymentStrategy interface, centralizing payment routing, and inverting dependencies, new payment rails can be introduced simply by writing a new strategy class.

## Practical walkthrough (English)

Refactoring Shotgun Surgery into an OCP/DIP-compliant strategy architecture:
```kotlin
// BAD ANTI-PATTERN: Shotgun Surgery (Adding ApplePay forces modifying 10 ViewModels, Services, and DAOs)
class CheckoutViewModel {
    fun pay(type: String) {
        when(type) {
            "Stripe" -> stripeService.pay()
            "PayPal" -> payPalService.pay()
            // Modified here, modified in Analytics, modified in ReceiptGenerator, modified in DB...
        }
    }
}

// ARCHITECTURAL BEST PRACTICE: Closed to modification, open to extension via Strategy and DIP
interface PaymentGateway {
    fun handles(type: PaymentMethod): Boolean
    suspend fun executePayment(amount: Long): Result<PaymentReceipt>
}

// New provider added as a standalone class: ZERO edits to existing classes!
class ApplePayGateway @Inject constructor(private val applePayClient: ApplePayClient) : PaymentGateway {
    override fun handles(type: PaymentMethod) = type is PaymentMethod.ApplePay
    override suspend fun executePayment(amount: Long) = runCatching { applePayClient.charge(amount) }
}

// Central PaymentProcessor is 100% CLOSED to modification
class PaymentProcessor @Inject constructor(
    private val gateways: Set<@JvmSuppressWildcards PaymentGateway>
) {
    suspend fun process(method: PaymentMethod, amount: Long): Result<PaymentReceipt> {
        val gateway = gateways.firstOrNull { it.handles(method) }
            ?: return Result.failure(IllegalStateException("No gateway for $method"))
        return gateway.executePayment(amount)
    }
}
```

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

The principles that resolve this issue are the Open/Closed Principle (OCP), Single Responsibility Principle (SRP), and Dependency Inversion Principle (DIP). Modifying ten classes to add one payment rail is the classic Shotgun Surgery code smell, caused by hardcoded conditional logic and leaking provider details across layers. By encapsulating payment logic inside a polymorphic PaymentStrategy interface and inverting dependencies, adding a new provider becomes a purely additive operation involving only a new class.

## Interview answer — structured

Having to modify ten existing classes to support a single new payment provider is the hallmark symptom of Shotgun Surgery, caused by violations across the SOLID spectrum.
This anti-pattern occurs when payment handling logic is fragmented across the application: ViewModels check string flags in when blocks, network repositories format provider-specific payloads, and analytics classes maintain hardcoded vendor mappings. When a new provider like Apple Pay is added, the developer must open and modify every single one of those files.
Three core SOLID principles resolve this architectural flaw.
First, the Open/Closed Principle (OCP) mandates that the system should be open for extension but closed for modification. We achieve this using the Strategy pattern, where all payment providers adhere to a unified PaymentGateway interface.
Second, the Single Responsibility Principle (SRP) isolates payment orchestration into a dedicated processor, removing payment branching from ViewModels and UI layers.
Third, the Dependency Inversion Principle (DIP) ensures that high-level checkout flows depend only on the abstract PaymentGateway contract.
By combining these principles with Dagger Multibindings, adding a new payment rail requires writing exactly one new class and registering it in the dependency graph, leaving all ten existing classes completely untouched.

## Interview answer — deep senior

Under the hood, Shotgun Surgery represents the inverse problem of the Divergent Change code smell, and its presence indicates severe architectural erosion across Gradle module boundaries.
When adding a payment provider touches ten classes, it proves that low-level infrastructure details have leaked upward into high-level presentation and domain state machines. In a multi-module enterprise Android application, this leak creates extensive build invalidation cascades. If ten classes across :feature:checkout, :core:analytics, and :data:repository contain explicit references to payment provider implementations, changing or adding a provider invalidates the Gradle build cache across all three modules, triggering massive recompilations.
By restructuring the system around OCP and DIP, the payment domain boundary becomes fortified. The :domain module defines the abstract PaymentGateway interface and PaymentMethod sealed class.
Each payment vendor lives inside its own isolated Gradle feature module (such as :payment:stripe and :payment:applepay).
These modules bind their gateway implementations into Dagger's dependency injection container using @Binds @IntoSet.
The orchestrating PaymentProcessor in the checkout module injects the Set<PaymentGateway>, routing transactions polymorphically at runtime.
Adding a new payment vendor touches zero existing files, generates zero merge conflicts in Git, and causes zero recompilation of existing modules, preserving long-term developer velocity and architectural purity. This decoupling ensures that enterprise applications scale frictionlessly without destabilizing previously certified core features.

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
