---
id: "SOL-03"
question: "Explain Open/Closed Principle with an Android example."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 174
editorial_status: "reviewed"
---

# SOL-03

## Original interview question

Explain Open/Closed Principle with an Android example.

## What the interviewer evaluates

Explain extension of stable policy and the strategic nature of “closed,” without banning all edits.

## Explanation in Arabic

شرح مبدأ الفتح والإغلاق (Open/Closed Principle - OCP) مع مثال عملي واقعي في Android:

1. تعريف مبدأ الـ OCP:
   - ينص المبدأ على: **"يجب أن تكون الكيانات البرمجية مفتوحة للتوسيع (Open for Extension) ومغلقة للتعديل (Closed for Modification)"**.
   - **مفتوحة للتوسيع**: يمكنك إضافة ميزات وسلوكيات جديدة للتطبيق بسهولة.
   - **مغلقة للتعديل**: إضافة الميزة الجديدة لا تتطلب تعديل الأكواد القديمة المكتوبة والمختبرة مسبقاً في الإنتاج!

2. ما الذي ينتهك OCP في Android؟
   - استخدام كتل `when` أو `if-else` الضخمة المعتمدة على Enums أو String types لمعالجة أنواع مختلفة (مثل طرق الدفع: Visa, PayPal, ApplePay).
   - كلما طلبت الشركة إضافة طريقة دفع جديدة (مثل Google Pay أو Fawry)، يضطر المطور لفتح الكلاس القديم وتعديل الـ when block، مما قد يكسر طرق الدفع القديمة!

3. كيف نطبق OCP في Android؟
   - باستخدام **نمط الاستراتيجية (Strategy Pattern)** أو **Polymorphism** عبر Interface مجرد (`PaymentProcessor`).
   - إضافة طريقة دفع جديدة تعني ببساطة إنشاء كلاس جديد `GooglePayProcessor : PaymentProcessor` وحقنه في النظام دون لمس سطر واحد في كود الدفع الأصلي!

## Practical walkthrough

تطبيق نمط Strategy لتحقيق OCP في نظام معالجة المدفوعات:
```kotlin
// ❌ انتهاك صارخ لـ OCP: إضافة طريقة دفع جديدة تجبرنا على تعديل الكود القديم المعتمد:
class BadPaymentService {
    fun process(type: String, amount: Long) {
        if (type == "CREDIT_CARD") { /* كود قديم */ }
        else if (type == "PAYPAL") { /* كود قديم */ }
        else if (type == "APPLE_PAY") { /* كود جديد تم حشره هنا! */ }
        // 💥 أي خطأ هنا سيكسر الدفع بالبطاقات القديمة!
    }
}

// ✅ تطبيق OCP: مفتوح لإضافة طرق دفع جديدة دون تعديل الكود القائم إطلاقاً:
interface PaymentProcessor {
    val paymentMethod: PaymentMethod
    suspend fun pay(amountCents: Long): PaymentResult
}

class CreditCardProcessor : PaymentProcessor { ... }
class PayPalProcessor : PaymentProcessor { ... }
// إضافة طريقة دفع جديدة لا تتطلب سوى كلاس جديد مستقل:
class GooglePayProcessor : PaymentProcessor { ... }

// الكلاس المنسق مغلق للتعديل ويعتمد على خريطة الموزعين:
class PaymentRouter @Inject constructor(
    private val processors: Set<PaymentProcessor>
) {
    suspend fun executePayment(method: PaymentMethod, amount: Long): PaymentResult {
        val handler = processors.firstOrNull { it.paymentMethod == method } ?: error("Unsupported method")
        return handler.pay(amount)
    }
}
```

## Why it matters and how it works

A stable policy should be insulated from foreseeable extensions through a deliberate seam. The seam can be strategy, adapter or data-driven configuration. Closure is strategic: not every possible future change needs an abstraction.

## Worked example

Conceptual Kotlin:
```kotlin
interface PaymentRoute { val code: String; suspend fun charge(request: Charge): ChargeResult }
data class Charge(val minor: Long, val requestId: String)
sealed interface ChargeResult { data class Accepted(val id: String): ChargeResult; data class Rejected(val code: String): ChargeResult }
```
A router selects a registered route; each provider adapter implements the same contract. Server authorization remains authoritative.

## Trade-offs and decision criteria

Strategy indirection helps when providers vary often and behavior is stable. A simple `when` may be clearer for two fixed cases. New variations still require wiring, policy review and tests. Do not use reflection registries solely to avoid one explicit binding edit.

## Failure modes

A new provider requires changing UI, ViewModel, repository and retry logic because provider checks are scattered. Centralize the routing contract and shared policy. Conversely, a giant generic plugin API can become harder to evolve than a small conditional.

## Production perspective

A fintech checkout integrates card and wallet providers. A narrow route contract localizes SDK differences; tests verify declined, timeout and cancellation semantics. A backend holds provider credentials and validates payment state.

## Interview answer — short

Open/Closed Principle states that code should be open for extension but closed for modification. In Android, rather than using massive `when` statements checking payment or notification types, we use polymorphism and the Strategy pattern (`PaymentProcessor` interface), allowing new providers to be added without editing existing, tested classes.

## Interview answer — structured

The Open/Closed Principle (OCP) requires that software entities (classes, modules, functions) should be **open for extension, but closed for modification**.

- **Open for extension**: The system's behavior can be enhanced as business requirements evolve.
- **Closed for modification**: Adding new behaviors does not require modifying, recompiling, or risking regressions in existing, production-tested code.

The primary violator of OCP in Android is type branching via long `when (type)` or `if-else` chains. For instance, an analytics engine or payment router that inspects string types: adding 'Google Pay' requires opening `PaymentManager.kt`, editing the conditional statements, and re-testing every existing payment method.

We adhere to OCP using **Polymorphic Abstraction (The Strategy Pattern)**:
1. Declare a common interface: `PaymentStrategy`.
2. Implement distinct classes: `CreditCardStrategy`, `PayPalStrategy`, `GooglePayStrategy`.
3. Inject a set of strategies via Dagger/Hilt Multibindings (`@IntoSet`).
To introduce a new payment method, developers simply create a new class and bind it in a Dagger module; zero existing payment code is touched.

## Interview answer — deep senior

In modern Kotlin, **Sealed Hierarchies** offer an intentional balance with OCP. When using `sealed interface UiState`, the compiler enforces exhaustive `when` expressions, which intentionally requires modifying the UI when a new state is added. This is desirable when the set of states is closed and known at compile time.

However, for **domain extensibility** (plugins, analytics trackers, payment gateways, validation rules), open interfaces and DI multibindings are strictly preferred over sealed classes. This allows feature modules to register new plugins dynamically without touching core orchestration modules.

## How to answer in the interview

- **Why:** Name the stable policy and varying provider.
- **How:** show strategy selection.
- **Trade-offs:** acknowledge registration cost.
- **Failure cases:** mention inconsistent provider semantics.
- **Production solutions:** close with shared contract and adapter tests..

## Deep-dive talking points

Distinguish strategic closure from no-edit dogma; compare strategy seam with a small conditional.

## Follow-up questions

- **Interviewer:** "How do Dagger Multibindings (`@IntoSet`, `@IntoMap`) enable OCP?"
  **Answer:** "Multibindings allow feature modules to contribute implementations to a central collection without the consuming class knowing about concrete implementations at compile time."

- **Interviewer:** "Does OCP mean you should never modify existing code?"
  **Answer:** "No. Bug fixes, performance tuning, and refactoring inherently require modifying existing code. OCP specifically targets behavioral feature additions."

## Self-check rubric

Describe a likely variation, stable policy, extension seam and one reason not to abstract yet.

## References and reviewed-on date

- [Robert C. Martin, Open Closed Principle](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — strategic extension.
- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns.

Technically reviewed against primary documentation on 2026-10-13.
