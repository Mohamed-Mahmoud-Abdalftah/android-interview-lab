---
id: "ARC-04"
question: "What is the Repository pattern? What is a UseCase?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 149
editorial_status: "reviewed"
---

# ARC-04

## Original interview question

What is the Repository pattern? What is a UseCase?

## What the interviewer evaluates

Define repository as data abstraction/source coordination and use case as business action, without mandatory pass-through classes.

## Concept and technical explanation

The Repository pattern and Use Cases (Interactors) represent two complementary architectural abstractions with clearly separated concerns. A Repository belongs to the Data layer and acts as an in-memory collection of domain entities, abstracting underlying data sources (remote network, local database, in-memory caches, datastores) behind clean interfaces. Its responsibility is data access, data synchronization, offline caching policies, and mapping raw storage payloads into domain models. A Use Case resides in the Domain layer and encapsulates a single, granular, reusable unit of business logic or orchestration across repositories. Representing a specific user or system action, a Use Case enforces domain validation rules, coordinates multi-step transactions, and executes domain algorithms without knowledge of UI lifecycles or transport protocols.

## Practical walkthrough (English)

Contrasting a Repository and an orchestrating Use Case in Kotlin:
```kotlin
// 1. Repository: Manages data access, caching, and synchronization
interface CartRepository {
    fun observeCart(): Flow<Cart>
    suspend fun clearCart()
}

interface PaymentRepository {
    suspend fun processPayment(orderId: String, amount: Double): Result<TransactionReceipt>
}

// 2. Use Case: Coordinates business workflow across both repositories
class CheckoutUseCase(
    private val cartRepository: CartRepository,
    private val paymentRepository: PaymentRepository
) {
    suspend operator fun invoke(orderId: String): Result<TransactionReceipt> {
        val currentCart = cartRepository.observeCart().first()
        if (currentCart.items.isEmpty()) {
            return Result.failure(IllegalStateException("Cannot checkout with an empty cart"))
        }
        val totalAmount = currentCart.calculateTotalWithTax()
        val paymentResult = paymentRepository.processPayment(orderId, totalAmount)

        if (paymentResult.isSuccess) {
            cartRepository.clearCart() // State transition upon successful business transaction
        }
        return paymentResult
    }
}
```

## Explanation in Arabic

ما هو نمط الـ Repository وما هو الـ UseCase؟ وما هي الفروق الجوهرية بينهما؟

1. ما هو نمط المستودع (Repository Pattern)؟
   - الـ Repository هو **وسيط مجرد (Mediator)** بين مصادر البيانات المختلفة وباقي أجزاء التطبيق.
   - مهمته الأساسية: توفير واجهة نظيفة وكأن البيانات مقروءة من مجموعة كائنات في الذاكرة (`In-memory collection`).
   - يخفي تفاصيل من أين أتت البيانات: هل أتت من الـ Cache؟ أم من قاعدة بيانات Room؟ أم من الـ Network عبر Retrofit؟
   - هو المسؤول الوحيد عن إدارة استراتيجية الـ Caching وقواعد مزامنة البيانات (Offline-first sync).

2. ما هو كائن حالة الاستخدام (UseCase / Interactor)؟
   - الـ UseCase هو كائن يمثل **عملية بيزنس محددة لمرة واحدة (Single Business Action)** تعبر عن رغبة المستخدم أو النظام (مثل `SubmitTransferUseCase`, `GetAccountSummaryUseCase`).
   - يركز على: قواعد التحقق (Validation)، دمج نتائج أكثر من Repository، وتطبيق الشروط الحسابية.
   - يتبع مبدأ Single Responsibility: له دالة تنفيذ واحدة (غالباً `operator fun invoke`).

3. المقارنة الجوهرية:
   - **الـ Repository**: يتحدث بلغة البيانات والتخزين (`saveUser`, `getUserById`, `syncCart`).
   - **الـ UseCase**: يتحدث بلغة المنتج وقواعد العمل (`PlaceOrderUseCase`, `VerifyEligibilityUseCase`).

## Practical walkthrough

تطبيق عملي يوضح الفرق بين UseCase يدمج مستودعين و Repository يدير الـ Cache:
```kotlin
// 1. REPOSITORY: يركز على مصادر البيانات والـ Cache:
class UserRepositoryImpl(
    private val localDao: UserDao,
    private val remoteApi: UserApi
) : UserRepository {
    override fun getUser(id: String): Flow<User> = localDao.getUser(id).onStart {
        // استراتيجية مزامنة البيانات والـ Cache:
        refreshUser(id)
    }
    private suspend fun refreshUser(id: String) {
        val networkUser = remoteApi.fetchUser(id)
        localDao.insertUser(networkUser.toEntity())
    }
}

// 2. USE CASE: يركز على سيناريو البيزنس وينسق بين Repositories متعددة:
class UpgradeToPremiumUseCase @Inject constructor(
    private val userRepository: UserRepository,
    private val paymentRepository: PaymentRepository
) {
    suspend operator fun invoke(userId: String, paymentMethodId: String): Result<Subscription> {
        val user = userRepository.getUserSync(userId) ?: return Result.failure(UserNotFoundException())
        if (user.isSuspended) return Result.failure(AccountSuspendedException())

        val chargeResult = paymentRepository.charge(paymentMethodId, PREMIUM_COST_CENTS)
        if (chargeResult.isSuccess) {
            userRepository.markAsPremium(userId)
        }
        return chargeResult
    }
}
```

## Why it matters and how it works

Data repositories are entry points to data and may coordinate multiple sources. Use cases are optional units of domain behavior in Android guidance, useful for reuse and complex logic. Boundaries should expose domain results and clearly state freshness, errors, and cancellation.

## Worked example

Conceptual design: `OrdersRepository.observeOrder(id): Flow<Order>` reads Room as source of truth while refresh writes server updates. `PlaceOrderUseCase(repo, limits)` validates amount, sends a request key, and returns `Accepted`, `Rejected`, or `PendingVerification`. The ViewModel maps those outcomes into screen state.

A small JVM contract shows the split: the use case owns input policy; the repository owns persistence/transport behind its interface. This does not prove the actual HTTP or Room adapter, which needs integration tests.

```kotlin
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

data class OrderDraft(val sku: String, val quantity: Int)
data class Receipt(val id: String)
interface OrderRepository { fun submit(draft: OrderDraft): Receipt }

class SubmitOrder(private val repository: OrderRepository) {
    fun invoke(draft: OrderDraft): Receipt {
        require(draft.sku.isNotBlank() && draft.quantity > 0)
        return repository.submit(draft)
    }
}

class SubmitOrderExampleTest {
    @Test fun validatesBeforeRepositoryCall() {
        var calls = 0
        val repository = object : OrderRepository {
            override fun submit(draft: OrderDraft): Receipt {
                calls++
                return Receipt("order-1")
            }
        }
        val submit = SubmitOrder(repository)
        assertThrows(IllegalArgumentException::class.java) {
            submit.invoke(OrderDraft("sku", 0))
        }
        assertEquals(0, calls)
        assertEquals(Receipt("order-1"), submit.invoke(OrderDraft("sku", 1)))
        assertEquals(1, calls)
    }
}
```

## Trade-offs and decision criteria

A repository can contain data-centric business rules such as merge policy. A use case adds value when it coordinates or centralizes application behavior. Avoid many one-line use cases in a small app; conversely avoid a huge repository that owns unrelated workflows.

## Failure modes

A repository exposing `Call<OrderDto>` forces UI to know Retrofit, dispatching, and server schema. Another failure is treating a use case as a durable job owner; process-death recovery requires persisted state and scheduling, not just a class name.

## Production perspective

An offline-first feed repository exposes database-backed Flow and refreshes from network. A “bookmark article” use case is worthwhile if the same rule spans feed, details, and notifications. Tests separate data merge behavior from policy.

## Interview answer — short

A Repository abstracts data sources and caching, presenting a unified collection of domain entities to the application. A UseCase encapsulates a single, focused piece of business logic or orchestration across repositories, representing an actionable user intent.

## Interview answer — structured

Repositories and UseCases serve distinct responsibilities within Clean Architecture, separating data management from business execution.

The Repository pattern mediates between domain logic and disparate data sources like network endpoints, local databases, and memory caches. It exposes clean domain models, implements caching strategies, and acts as the application's single source of truth without exposing SQL queries or HTTP endpoints.

In production, a UseCase—often called an Interactor—encapsulates a single business task or transaction, such as transferring funds, validating a promo code, or syncing offline edits. It typically exposes an operator invoke function, orchestrating one or more repositories while executing pure business rules.
As for ownership, UseCases prevent ViewModels from becoming bloated coordination centers, allowing critical business workflows to be reused consistently across multiple screens, background workers, or app shortcuts without duplicating validation logic.


## Interview answer — deep senior

Under the hood, the combination of Repositories and UseCases creates a robust separation between data orchestration and business decision-making. A well-designed Repository manages data synchronization mechanics: it decides whether to emit cached records from Room immediately while triggering a background Retrofit fetch, handles token refreshes, and resolves optimistic write conflicts. By exposing reactive streams via Flow, it keeps the rest of the application synchronized with data mutations.
UseCases, on the other hand, sit above Repositories and should never contain data-caching or transport logic. A UseCase receives domain parameters, validates business constraints, coordinates calls to multiple repositories, and applies domain calculations. For instance, a CheckoutUseCase might call CartRepository to retrieve items, PaymentRepository to execute a transaction, and AnalyticsRepository to record telemetry, wrapping the entire multi-step operation in a transactional domain Result.
Staff engineers adhere to strict naming conventions and architectural discipline: UseCases are named as verbs in present tense and contain a single public operator invoke function. If a UseCase merely forwards a call to a repository without applying business logic, formatting, or coordination, it is an architectural anti-pattern known as a pass-through UseCase. In such scenarios, senior engineers allow ViewModels to observe the Repository directly to eliminate pointless indirection while maintaining complete testability. This pragmatic approach preserves productivity without compromising architectural cleanlines.

## How to answer in the interview

- **Why:** data access and business decision differ.
- **How:** define repository contract and use case policy.
- **Trade-off:** extra layers versus meaningful separation.
- **Failure case:** pass-through classes hide responsibility.
- **Production solution:** test policy and real adapter separately.

## Deep-dive talking points

Compare repository data ownership with use-case action semantics; explain offline source of truth, multi-repository coordination, cancellation and process-death limits.

## Follow-up questions

- **Interviewer:** "When is a Use Case genuinely necessary versus overengineering?"
  **Answer:** "It is necessary when business rules require validation, orchestrate multiple repositories, or must be reused across multiple ViewModels. It is overengineering when it simply passes a call directly to a single repository method without added value."

- **Interviewer:** "Why should a UseCase have only one public method (`invoke`)?"
  **Answer:** "To uphold the Single Responsibility Principle. A UseCase represents a single business action; having multiple disparate public functions turns it into a god class."

## Self-check rubric

Describe a repository that actually coordinates sources, one use case that adds business value, and one pass-through use case you would omit.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository responsibilities.
- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — use cases and optionality.

Technically reviewed against primary documentation on 2026-10-13.
