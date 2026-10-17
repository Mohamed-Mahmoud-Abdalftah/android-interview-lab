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

## Concept and technical explanation

The Dependency Inversion Principle (DIP) states that high-level modules should not depend on low-level modules; both must depend on abstractions. Furthermore, abstractions should not depend on details; details must depend on abstractions. In software architecture, source code dependencies traditionally point in the direction of execution flow (UI depends on Business Logic, which depends on Database and Network drivers). DIP completely inverts this dependency direction: business domain policies reside at the architectural center, defining abstract interfaces that external infrastructure layers (such as Room, Retrofit, or DataStore) must implement, isolating application business rules from third-party frameworks.

## Practical walkthrough (English)

Inverting source code dependencies in Android Clean Architecture:
```kotlin
// DOMAIN LAYER (:domain module - Pure Kotlin, Zero Android Framework dependencies)
// High-level business entity and abstraction
data class User(val id: String, val name: String)

interface UserRepository { // Domain defines the contract!
    suspend fun getUser(id: String): Result<User>
}

class GetUserUseCase @Inject constructor(
    private val repository: UserRepository // Depends on Domain abstraction!
) {
    suspend operator fun invoke(id: String): Result<User> = repository.getUser(id)
}

// DATA LAYER (:data module - Low-level details depend on Domain abstraction)
class UserRepositoryImpl @Inject constructor(
    private val localDao: UserDao, // Detail: Room
    private val remoteApi: UserApi // Detail: Retrofit
) : UserRepository { // Implements Domain contract, inverting source dependency!
    override suspend fun getUser(id: String): Result<User> = runCatching {
        localDao.getUser(id)?.toDomain() ?: remoteApi.fetchUser(id).toDomain()
    }
}
```

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

The Dependency Inversion Principle dictates that high-level business modules should not depend on low-level infrastructure modules; both must depend on abstractions. In Android Clean Architecture, the Domain layer defines the abstract UserRepository interface, and the Data layer implements it using Room and Retrofit. This inverts source code dependencies inward toward pure Kotlin business rules, allowing developers to swap database or networking libraries without touching business or UI logic.

## Interview answer — structured

The Dependency Inversion Principle establishes architectural independence by decoupling business policies from volatile infrastructure details.
In traditional, un-inverted architectures, control flow and compile-time dependencies point in the same downward direction. A ViewModel instantiates a Repository, and the Repository directly constructs and invokes a Retrofit REST client and a Room SQLite DAO. Under this structure, high-level business rules are held hostage by low-level technology choices. If the backend switches from REST to gRPC or WebSockets, or if Room is upgraded, changes cascade upward into business and presentation layers.
Dependency Inversion resolves this by inserting an abstraction boundary.
The high-level Domain layer defines the data contract, such as the UserRepository interface. High-level UseCases depend strictly on this abstraction.
The low-level Data layer implements this interface in UserRepositoryImpl, mapping database tables and network responses into domain entities.
Source code dependencies now point in the exact opposite direction of execution flow. The Domain module remains pure Kotlin with zero external library dependencies, enabling lightning-fast unit tests and total freedom to evolve infrastructure without risking core business stability.

## Interview answer — deep senior

Under the hood, Dependency Inversion is enforced at compilation time through multi-module Gradle dependency graphs and dependency injection bindings.
In an enterprise multi-module Android application, Gradle project dependencies strictly enforce DIP: the :feature and :data modules depend on the :domain module (implementation(project(":domain"))), but the :domain module has zero dependencies on :data, :feature, or Android SDK libraries. If an engineer attempts to import android.content.Context, androidx.room.Room, or retrofit2.Retrofit inside the :domain module, the Gradle compiler halts with a compilation error, preserving the pure domain boundary automatically.
At runtime, Dependency Injection frameworks like Dagger or Hilt wire the concrete implementations back together at the application assembly root. Using @Binds inside a Hilt module, Dagger binds the Data layer's UserRepositoryImpl to the Domain layer's UserRepository interface seamlessly.
This inversion enables total testability through JVM test doubles. In unit tests for ViewModels or UseCases, developers pass a lightweight fake repository implemented in memory.
Tests execute entirely within standard JVM bytecode at thousands of tests per second, completely eliminating the need for slow Android instrumentation runners, Robolectric reflection overhead, or mock SQLite databases, accelerating continuous integration pipelines significantly. This decoupling allows engineers to substitute storage engines or upgrade network protocols without risking any disruption to domain business logic or presentation state machines.

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
