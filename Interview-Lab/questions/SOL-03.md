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

## Concept and technical explanation

The Open/Closed Principle (OCP) states that software entities (classes, modules, functions) should be open for extension, but closed for modification. This architectural rule mandates that systems must accommodate new functional behaviors, business rules, and third-party integrations without rewriting or mutating existing, fully tested, and verified source code. In Android development, OCP is implemented primarily through polymorphic interfaces, abstract base capabilities, and strategy registries. Rather than scattering monolithic when or switch branches across repositories and UI controllers, engineers define extensible contracts that allow new implementations to plug in seamlessly at compile time or runtime.

## Practical walkthrough (English)

Refactoring a rigid payment processor to adhere to Open/Closed Principle:
```kotlin
// BAD ANTI-PATTERN: Closed for extension, constantly modified when new gateways arrive
class FragilePaymentHandler(private val stripe: StripeSdk, private val paypal: PayPalSdk) {
    fun processPayment(type: String, amount: Long) {
        when (type) {
            "STRIPE" -> stripe.charge(amount)
            "PAYPAL" -> paypal.pay(amount)
            // Adding GooglePay or Klarna forces editing this tested class!
            else -> throw IllegalArgumentException("Unknown type")
        }
    }
}

// ARCHITECTURAL BEST PRACTICE: Open for extension, closed for modification
interface PaymentStrategy {
    fun supports(method: PaymentMethod): Boolean
    suspend fun execute(amount: Long): Result<TransactionReceipt>
}

class StripeStrategy @Inject constructor(private val client: StripeClient) : PaymentStrategy {
    override fun supports(method: PaymentMethod) = method == PaymentMethod.STRIPE
    override suspend fun execute(amount: Long) = client.charge(amount)
}

class PayPalStrategy @Inject constructor(private val client: PayPalClient) : PaymentStrategy {
    override fun supports(method: PaymentMethod) = method == PaymentMethod.PAYPAL
    override suspend fun execute(amount: Long) = client.authorize(amount)
}

// Extensible orchestrator: Never modified when new payment strategies are added!
class PaymentProcessor @Inject constructor(
    private val strategies: Set<@JvmSuppressWildcards PaymentStrategy>
) {
    suspend fun pay(method: PaymentMethod, amount: Long): Result<TransactionReceipt> {
        val strategy = strategies.find { it.supports(method) }
            ?: return Result.failure(UnsupportedOperationException("Unsupported gateway: $method"))
        return strategy.execute(amount)
    }
}
```

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

The Open/Closed Principle mandates that software should be open for extension but closed for modification. In Android, instead of using sprawling when or switch blocks that inspect type flags and require constant edits whenever new features arrive, we rely on polymorphism and the Strategy pattern. By defining an interface like PaymentStrategy and injecting a collection of implementations, adding a new payment gateway or analytics tracker involves creating a new class without touching existing, tested codebase files.

## Interview answer — structured

The Open/Closed Principle provides stability and scalability by enabling systems to grow through additive changes rather than destructive edits.
In typical Android applications, the most visible violation of OCP appears as massive conditional dispatchers. When implementing payment providers, push notification handlers, or analytics tracking, developers often write centralized when expressions that check string keys or enums. Whenever product managers introduce a new provider like Google Pay or Braze, developers must modify existing, production-tested classes. This introduces high regression risks, requires re-running entire test suites, and creates merge conflicts across feature branches.
Applying OCP decouples execution from concrete variants through polymorphism.
First, an interface establishes a contract for the capability, defining an execution signature and a predicate method to check support.
Second, concrete providers implement this interface in independent, self-contained classes.
Third, the orchestrating class injects a collection of these strategies, querying the appropriate provider polymorphically at runtime.
When a new requirement emerges, developers simply create a new class implementing the interface and bind it via dependency injection. Existing orchestrator classes remain completely closed to modification, eliminating regression risks and ensuring zero disruption to existing business flows.

## Interview answer — deep senior

Under the hood, the Open/Closed Principle transforms hardcoded control flow branches into dynamic polymorphic dispatch tables (v-tables) or hash-based dependency injection lookups.
In large-scale Android development, coupling systems to monolithic when expressions creates significant compilation bottlenecks. When a single central class references every payment provider SDK, changes to any provider dependency force Gradle to recompile the shared file and all downstream consumers.
By restructuring the system around OCP with Dagger Multibindings (@IntoSet or @IntoMap), each provider lives in an isolated Gradle feature module. Adding a new provider creates a new independent compilation unit that Gradle compiles in parallel, keeping build times constant regardless of application feature growth.
Furthermore, OCP is foundational to Android framework design and modern UI paradigms. In the Android OS, RecyclerView does not contain hardcoded if-statements checking whether to display a text row, an image grid, or a video card. Instead, RecyclerView.Adapter is open for extension via onCreateViewHolder and onBindViewHolder while remaining completely closed to internal framework modifications.
Similarly, Jetpack Compose utilizes slot-based APIs (slots pattern) where composable containers accept generic @Composable () -> Unit lambdas, allowing engineers to extend UI structures arbitrarily without modifying the parent layout mechanics or introducing runtime state regressions. This slot architecture provides effortless extensibility while completely shielding the core layout runtime from unexpected modifications.

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
