---
id: "PAT-01"
question: "What is a design pattern, and how is it different from architecture?"
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 192
editorial_status: "reviewed"
---

# PAT-01

## Original interview question

What is a design pattern, and how is it different from architecture?

## What the interviewer evaluates

Define pattern as reusable local design idea and distinguish it from system-level architecture and implementation recipe.

## Concept and technical explanation

A design pattern is a reusable, localized solution to a commonly occurring structural, creational, or behavioral problem within a specific software context, operating at the granularity of individual classes and localized object collaborations. In contrast, software architecture defines the macro-level organizational blueprint of an entire system, establishing structural boundaries, layer separation, dependency rules, data flow paradigms, and cross-cutting system characteristics. While architecture dictates high-level governance (such as Clean Architecture, Unidirectional Data Flow, or multi-module packaging), design patterns (such as Adapter, Strategy, or Factory) serve as tactical building blocks employed within those architectural layers to solve concrete engineering mechanics without impacting global system topology.

## Practical walkthrough (English)

Contrasting macro architecture with localized design patterns:
```kotlin
// ARCHITECTURE LEVEL: Clean Architecture Layer Separation (Domain Layer)
interface PaymentRepository { // Macro Boundary: Domain interface isolated from data details
    suspend fun processTransaction(orderId: String, amount: Long): Result<TransactionReceipt>
}

// PATTERN LEVEL: Strategy Pattern implemented inside the Data Layer
interface PaymentStrategy { // Tactical Pattern: Encapsulates specific payment calculation & API call
    suspend fun executePayment(amount: Long): TransactionReceipt
}

class StripePaymentStrategy @Inject constructor(private val stripeApi: StripeApi) : PaymentStrategy {
    override suspend fun executePayment(amount: Long) = stripeApi.charge(amount)
}

class PayPalPaymentStrategy @Inject constructor(private val payPalSdk: PayPalSdk) : PaymentStrategy {
    override suspend fun executePayment(amount: Long) = payPalSdk.authorize(amount)
}

// Data layer repository uses Strategy pattern to satisfy the macro architectural contract
class PaymentRepositoryImpl @Inject constructor(
    private val strategies: Map<PaymentMethod, @JvmSuppressWildcards Provider<PaymentStrategy>>
) : PaymentRepository {
    override suspend fun processTransaction(orderId: String, amount: Long): Result<TransactionReceipt> = runCatching {
        val strategy = strategies[PaymentMethod.STRIPE]?.get() ?: error("Unsupported gateway")
        strategy.executePayment(amount)
    }
}
```

## Explanation in Arabic

`Architecture` هي المخطط العام والنظرة الكلية للنظام (Macro-level): بتحدد تقسيم الـ Layers (UI، Domain، Data)، واتجاه الـ Dependencies، وتدفق البيانات زي Clean Architecture وUDF. قرارات المعمارية صعبة ومكلفة التغيير بعد اتخاذها. أما الـ `Design Pattern` فهو حل موضعي متكرر (Micro-level) لمشكلة محددة بين شوية Classes جوه نفس الطبقة، زي Adapter لتحويل Interface غير متوافقة أو Strategy لعزل خوارزمية. الأنماط بتعيش جوه المعمارية وتغييرها أسهل ومحصور محليًا.

## Practical walkthrough

في تطبيق دفع، القرار المعماري يحدد إن الـ UI يعتمد على Domain Contract اسمه `CheckoutRepository` معزول عن أي SDK خارجي. جوه الـ Data Layer، بنستخدم Strategy Pattern للتبديل بين Gateways مختلفة (Stripe وPayPal) من غير ما نغير الـ Domain أو الـ UI. الـ Pattern حل مشكلة موضعية جوه الـ Data Layer، بينما الـ Architecture حافظت على استقلالية الطبقات.

## Why it matters and how it works

Patterns provide shared vocabulary for object collaboration; architecture sets larger boundaries, data flow and quality attributes. A pattern is applied within a context and can be combined with other patterns. The implementation must still honor lifecycle, concurrency and failure contracts.

## Worked example

Example: a checkout app uses a repository boundary to coordinate Room/network, a Strategy for multiple payment providers, and Adapter wrappers for SDK callback differences. Its architecture also defines UI/data modules, server authority and process-death recovery. These are different scales of decision.

## Trade-offs and decision criteria

A named pattern can speed review when the team shares its meaning. Forcing pattern classes into a simple feature adds indirection. Kotlin language features such as `object`, lambdas and delegation can implement the intent with less boilerplate.

## Failure modes

A team calls a global `object ApiManager` “Singleton pattern” and stores Activity plus token state in it. The name hides lifecycle leak and process-death fragility. Review ownership and invariants, not labels.

## Production perspective

A finance app uses an SDK adapter at data boundary while the app architecture keeps payment policy and server verification separate. Contract tests show whether swapping SDKs preserves behavior.

## Interview answer — short

A design pattern is a tactical, reusable solution to a localized class-level problem, such as adapting an interface or encapsulating an algorithm. Software architecture is the strategic blueprint that governs global system boundaries, data flow rules, and layer separation across the entire application. Architecture dictates how modules and layers interact, while design patterns solve specific implementation mechanics within those layers.

## Interview answer — structured

Understanding the difference between a design pattern and software architecture requires analyzing scale, scope, and impact on system evolvability.
Software architecture represents the strategic macro-level blueprint of an application. It defines foundational system boundaries, dependency direction rules, cross-cutting concerns, and information flow. For example, adopting Clean Architecture and Unidirectional Data Flow establishes that UI components observe ViewModels, ViewModels interact with UseCases, and Domain logic remains completely isolated from database drivers and network frameworks. Modifying system architecture is exceptionally expensive because it restructures foundational boundaries across entire module graphs.
In contrast, design patterns represent localized tactical solutions applied to recurring structural or behavioral challenges within individual components. Patterns operate at the micro level, describing collaborations between a few interacting classes. Within a Clean Architecture data layer, an engineer might use the Adapter pattern to wrap an unruly vendor SDK, or the Strategy pattern to interchange discount algorithms.
Changing or refactoring a design pattern is localized and low-risk, affecting only a handful of files without destabilizing application-wide architectural boundaries.

## Interview answer — deep senior

Under the hood, architecture establishes invariant compilation boundaries and dependency flow rules enforced by Gradle dependency graphs and static linters, whereas design patterns establish object collaboration protocols within those boundaries.
In large-scale Android development, confusing patterns with architecture leads to severe architectural degradation. A notorious anti-pattern is treating the Singleton pattern as an architectural foundation by storing global application state in static singletons, which destroys Clean Architecture boundaries, introduces hidden concurrency coupling, and prevents parallel unit testing.
Staff engineers view architecture as the enforcement of high-level constraints: data flows inward toward domain abstractions, feature modules compile in parallel without lateral dependencies, and presentation components observe state streams reactively. Within those constraints, design patterns solve tactical impedance mismatches.
For instance, the Repository pattern mediates between domain entities and multiple data sources. The Adapter pattern bridges legacy Java callbacks to modern Kotlin Coroutines. The Factory pattern delegates complex object construction to dependency injection engines.
By keeping design patterns strictly subordinate to architectural boundaries, engineering organizations ensure that class-level refactoring remains isolated, predictable, and fully verifiable without causing system-wide regressions. Automated architectural testing tools like Konsist or ArchUnit can formally assert that tactical design patterns never violate module layer boundaries, leak database entities into domain models, or reverse architectural dependency flow rules across the enterprise codebase.

## How to answer in the interview

- **Why:** Pattern vocabulary helps only when it names a real local change point.
- **How:** Contrast Adapter/Strategy inside checkout with app-wide ownership and server authority.
- **Trade-off:** Avoid ceremonial classes for one stable implementation.
- **Failure case:** A named Singleton still leaks Activity or loses state on process death.
- **Production solution:** Show the boundary, tests, and expected variation before naming the pattern.

## Deep-dive talking points

Compare object collaboration with module boundaries, and identify Kotlin shorthand plus lifecycle caveats.

## Follow-up questions

- **Interviewer:** "Can a bad design pattern ruin good architecture?"
  **Answer:** "Yes. If an anti-pattern like a monolithic God-Singleton is introduced, it creates hidden shared mutable state across architectural boundaries, corrupting the Clean Architecture dependency rule."

- **Interviewer:** "Is the Repository pattern an architectural pattern or a design pattern?"
  **Answer:** "It functions at both levels: tactically as a mediator design pattern abstracting data access, and architecturally as the foundational boundary between Data and Domain layers."

## Self-check rubric

Define pattern and architecture at different scales and give one Android example of each.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — original pattern catalog and categories.
- [Android architecture guide](https://developer.android.com/topic/architecture) — app-level boundaries.

Technically reviewed against the cited primary documentation on 2026-10-19; agent editorial review, not human verification.
