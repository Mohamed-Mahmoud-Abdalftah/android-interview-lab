---
id: "SOL-06"
question: "Explain Dependency Inversion Principle with an Android example."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 177
editorial_status: "reviewed"
---

# SOL-06

## Original interview question

Explain Dependency Inversion Principle with an Android example.

## What the interviewer evaluates

Explain high-level policy versus low-level detail, source dependencies, and runtime injection.

## Explanation in Arabic

شرح مبدأ عكس التبعية (Dependency Inversion Principle - DIP) مع مثال عملي واقعي في Android:

1. تعريف مبدأ عكس التبعية (DIP):
   - ينص المبدأ على قاعدتين أساسيتين:
     * **القاعدة 1**: الوحدات عالية المستوى (High-level modules) يجب ألا تعتمد على الوحدات منخفضة المستوى (Low-level modules). كلاهما يجب أن يعتمد على التجريدات (Abstractions).
     * **القاعدة 2**: التجريدات يجب ألا تعتمد على التفاصيل (Details)؛ التفاصيل هي التي يجب أن تعتمد على التجريدات.

2. ما الذي ينتهك DIP في Android؟
   - عندما يقوم كلاس `CheckoutViewModel` (High-level) بإنشاء أو استدعاء كلاس `RetrofitOrderApi` أو `RoomOrderDatabase` (Low-level infrastructure) مباشرة!
   - أي تغيير في تفاصيل قاعدة البيانات أو السيرفر يجبرك على تغيير كود العرض والبيزنس عالي المستوى.

3. كيف نطبق DIP في Android؟
   - نقوم بإنشاء **Interface مجرد في طبقة الـ Domain** يسمى `OrderRepository`.
   - الـ `CheckoutViewModel` يعتمد على الـ `OrderRepository` interface فقط.
   - الـ `OrderRepositoryImpl` في طبقة الـ Data يعتمد على الـ `OrderRepository` interface وينفذه.
   - محرك الـ DI (Hilt) يقوم بحقن الـ Implementation في وقت التشغيل.

## Practical walkthrough

تطبيق مبدأ DIP في كود Kotlin في Android:
```kotlin
// ❌ انتهاك صارخ لـ DIP: High-level ViewModel يعتمد مباشرة على Low-level Retrofit Service:
class BadOrderViewModel {
    // ارتهان مباشر بتفاصيل البنية التحتية:
    private val api = Retrofit.Builder().baseUrl("https://api.com").build().create(OrderApi::class.java)
}

// ✅ تطبيق DIP السليم: كلاهما يعتمد على التجريد (Abstraction):
// 1. التجريد (Abstraction) يعيش في الـ Domain:
interface OrderRepository {
    suspend fun submitOrder(order: Order): Result<OrderConfirmation>
}

// 2. High-level module (ViewModel) يعتمد على التجريد فقط:
@HiltViewModel
class GoodOrderViewModel @Inject constructor(
    private val orderRepository: OrderRepository // اعتماد نقي على Interface
) : ViewModel() { ... }

// 3. Low-level module (Data layer) يعتمد على التجريد وينفذ تفاصيله:
class OrderRepositoryImpl @Inject constructor(
    private val api: OrderApi,
    private val dao: OrderDao
) : OrderRepository {
    override suspend fun submitOrder(order: Order): Result<OrderConfirmation> { ... }
}
```

## Why it matters and how it works

DIP limits change propagation by making stable policy depend on a stable contract. A composition root supplies an adapter at runtime. The abstraction should use domain concepts and live where the high-level consumer can depend on it without importing volatile details.

## Worked example

Conceptual Kotlin:
```kotlin
interface AccountStatusSource { suspend fun status(id: String): AccountStatus }
enum class AccountStatus { ACTIVE, BLOCKED }
class CanTransfer(private val source: AccountStatusSource) {
    suspend fun check(id: String) = source.status(id) == AccountStatus.ACTIVE
}
```
A Retrofit-backed class can implement the contract in data, while tests use a fake.

## Trade-offs and decision criteria

A contract adds indirection and DI wiring. In a tiny feature, depending on a concrete repository may be simpler if it exposes stable app data. Use DIP where volatile implementation would otherwise reach important policy.

## Failure modes

A use case constructor takes `RetrofitAccountService` and returns `Response<AccountDto>`; changing the API changes policy tests and signatures. Introduce a domain-facing contract and map transport details at the adapter.

## Production perspective

A credit-limit rule depends on `CreditStatusSource`; production adapter fetches and caches status, tests supply deterministic states. Server still authorizes the actual transaction.

## Interview answer — short

Dependency Inversion Principle dictates that high-level modules (business/UI) must not depend on low-level modules (networking/database); both must depend on abstractions. In Android, the Domain layer defines the `Repository` interface, and the Data layer implements it, inverting the source code dependency.

## Interview answer — structured

The Dependency Inversion Principle (DIP) establishes that **high-level policies should not depend on low-level details; both should depend on abstractions**.

In procedural or coupled architectures, control and dependencies flow in the same direction: a ViewModel (high-level) directly instantiates a Database or Retrofit client (low-level). Consequently, if the database schema or network library changes, the high-level business code is forced to change.

DIP inverts this relationship.

First, the high-level layer (Domain/Presentation) defines the abstraction: `interface UserRepository`. Next, the low-level infrastructure layer (Data) imports that interface and implements it: `class UserRepositoryImpl : UserRepository`.
Finally, at compile time, the source code dependency points inward toward the high-level abstraction. At runtime, the Dependency Injection container (Hilt) resolves and injects the implementation.

This insulates critical business rules: the network library can be swapped from Retrofit to Ktor without altering a single line of business logic.


## Interview answer — deep senior

DIP is the foundational mechanism that powers the **Dependency Rule in Clean Architecture**. Without DIP, Clean Architecture would be impossible because the core domain would be forced to depend on database drivers and network libraries to fetch data.

In Gradle multi-module architecture, DIP is enforced via Gradle configuration.

First, `:core:domain` defines `interface AuthRepository`. It has zero dependencies on network or database modules. Next, `:core:data` has `implementation(project(":core:domain"))` and provides `AuthRepositoryImpl`.
Finally, the compile graph physically forbids `:core:domain` from accessing `:core:data`.

This inversion enables 100% pure JVM unit testability: we can test `AuthUseCase` by passing an in-memory `FakeAuthRepository` without touching SQLite or mocking HTTP calls.


## How to answer in the interview

- **Why:** Show dependency direction.
- **How:** map HTTP data into domain status.
- **Trade-offs:** mention extra boundary cost.
- **Failure cases:** flag `Response<Dto>` leakage.
- **Production solutions:** end with fake tests and backend authority..

## Deep-dive talking points

Draw source arrows versus runtime calls; identify a leaking DTO signature and a consumer-owned contract.

## Follow-up questions

- **Interviewer:** "What is the difference between DIP and Dependency Injection (DI)?"
  **Answer:** "DIP is an architectural design principle about the direction of code dependencies. DI is a practical creational design pattern/technique (used by Hilt/Koin) to provide instances of dependencies to a class at runtime."

- **Interviewer:** "Where should the abstraction (interface) live according to DIP?"
  **Answer:** "In the higher-level module (Domain layer), alongside the client that consumes it, NOT in the low-level infrastructure module."

## Self-check rubric

Show an inverted account-status contract, locate its implementation, and explain why Hilt wiring alone is insufficient.

## References and reviewed-on date

- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — dependency inversion.
- [Android dependency injection](https://developer.android.com/training/dependency-injection) — DI mechanics.

Technically reviewed against primary documentation on 2026-10-13.
