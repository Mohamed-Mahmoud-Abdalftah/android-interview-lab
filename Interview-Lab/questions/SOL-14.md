---
id: "SOL-14"
question: "How does Hilt support dependency wiring without automatically guaranteeing DIP?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 185
editorial_status: "reviewed"
---

# SOL-14

## Original interview question

How does Hilt support dependency wiring without automatically guaranteeing DIP?

## What the interviewer evaluates

Separate Hilt construction from dependency inversion and inspect actual injected types.

## Explanation in Arabic

كيف يدعم Hilt ربط التبعيات (Dependency Wiring) دون أن يضمن تلقائياً تطبيق مبدأ عكس التبعية (DIP)؟

1. ما الذي يفعله Hilt فعلياً؟
   - Hilt هو مكتبة لإدارة وتوليد **حقن التبعيات (Dependency Injection Container)** في وقت التجميع (Compile-time).
   - يحل مشكلة الـ Wiring: إنشاء الكائنات، إدارة دورات حياتها (Singleton, ActivityScoped, ViewModelScoped)، وتمريرها في الـ Constructors تلقائياً.

2. كيف يمكن استخدام Hilt مع انتهاك صارخ لمبدأ DIP؟
   - يمكنك استخدام Hilt لحقن كلاس ملموس مباشر منخفض المستوى في كلاس عالي المستوى:
     `class ProfileViewModel @Inject constructor(val api: RetrofitUserApi, val dao: UserDao)`.
   - في هذه الحالة: Hilt يعمل بنجاح 100% ويقوم بحقن الـ Api والـ Dao في الـ ViewModel.
   - **ولكن مبدأ DIP منتهك بالكامل!** الـ ViewModel عالي المستوى مرتبط بشكل وثيق بـ Retrofit و Room دون أي Interface أو تجريد وسيط!

3. كيف تستخدم Hilt لضمان DIP؟
   - باستخدام وسم **`@Binds`** داخل Hilt Module لربط الـ Interface المجرد في الـ Domain بالتنفيذ الحقيقي في الـ Data، وحقن الـ Interface فقط في الـ ViewModel.

## Practical walkthrough

المقارنة بين Hilt يكسر DIP و Hilt يحقق DIP عبر @Binds:
```kotlin
// ❌ Hilt مستخدم بنجاح لكنه ينتهك DIP (حقن كلاسات ملموسة منخفضة المستوى مباشرة):
@HiltViewModel
class BadViewModel @Inject constructor(
    private val remoteApi: RetrofitOrderApi, // 💥 كلاس شبكة ملموس!
    private val roomDb: AppDatabase          // 💥 كلاس قاعدة بيانات ملموس!
) : ViewModel() { ... }

// ✅ Hilt يفرض DIP بنجاح عبر ربط الـ Abstractions:
// 1. الـ ViewModel يعتمد فقط على Interface مجرد:
@HiltViewModel
class GoodViewModel @Inject constructor(
    private val orderRepository: OrderRepository // Abstraction نقي
) : ViewModel() { ... }

// 2. Hilt Module يربط الـ Interface بالتنفيذ في طبقة Data عبر @Binds:
@Module
@InstallIn(SingletonComponent::class)
abstract class OrderDataModule {
    @Binds
    abstract fun bindOrderRepository(
        impl: OrderRepositoryImpl
    ): OrderRepository // يضمن تطبيق DIP بشكل كامل!
}
```

## Why it matters and how it works

A DI container resolves constructors and lifetimes. Dependency inversion concerns direction and semantics of source dependencies. Hilt can implement a good graph or a tightly coupled graph equally well.

## Worked example

Conceptual binding: `@Binds abstract fun bindStatus(impl: NetworkStatusSource): TransferStatusSource`. The useful part is that `TransferStatusSource` exposes domain status, not Retrofit `Response`. A manual composition root could bind the same types.

## Trade-offs and decision criteria

Hilt reduces wiring cost and supports test replacement but adds annotation processing and lifecycle scopes. Manual DI may be enough for a small project. DIP may justify an interface even if Hilt can inject concrete classes.

## Failure modes

Use case is annotated with `@Inject` yet imports `RetrofitService`, parses HTTP status and handles JSON fields. Moving construction to Hilt changed wiring only. Extract a data adapter and domain contract, then test policy without Retrofit.

## Production perspective

A lending app uses Hilt to wire an eligibility rule to a repository abstraction. Production adapter fetches and caches status; JVM tests provide a fake contract. Server enforces final approval.

## Interview answer — short

Hilt is a Dependency Injection tool that automates object creation and graph wiring, but it does not enforce architectural direction. If a developer injects concrete classes like `RetrofitApi` or `RoomDao` directly into a ViewModel, Hilt successfully wires dependencies while completely violating the Dependency Inversion Principle (DIP).

## Interview answer — structured

Hilt is a creational wiring mechanism, not an architectural governor. It automates Dependency Injection (DI), but **DI is agnostic to the Dependency Inversion Principle (DIP)**.

A developer can build a 100% functional Hilt dependency graph that aggressively violates DIP:
```kotlin
@HiltViewModel
class CheckoutViewModel @Inject constructor(
 val retrofit: RetrofitOrderService, // Concrete detail
 val roomDao: OrderDao // Concrete detail
) : ViewModel()
```
Hilt compiles cleanly, injects instances, and resolves scopes. Yet, the high-level presentation layer is directly coupled to low-level network and database infrastructure details, destroying JVM unit testability and violating DIP.

To guarantee DIP within Hilt.

First, high-level consumers must declare dependencies as **abstract interfaces** (`OrderRepository`). Finally, Hilt Modules must use **`@Binds`** to map the abstract interface to its concrete data layer implementation (`OrderRepositoryImpl`).


## Interview answer — deep senior

Under the hood, Hilt generates factory classes (`CheckoutViewModel_Factory.java`) based strictly on what is declared in constructor signatures. Hilt has no built-in lint rules preventing ViewModels from injecting Retrofit services or SQLite databases.

To prevent Hilt from facilitating DIP violations in large enterprise teams, we enforce architectural constraints using **Gradle Module boundaries** and **Konsist tests**.

First, feature modules (`:feature:checkout`) do not have a Gradle dependency on network or database modules, making it impossible for Hilt constructors to reference `RetrofitOrderService`. Finally, konsist tests assert that all constructor parameters in `@HiltViewModel` classes are either interfaces or Use Cases residing in domain modules.


## How to answer in the interview

- **Why:** Separate wiring from dependency direction.
- **How:** show Hilt binding.
- **Trade-offs:** mention binding/scope cost.
- **Failure cases:** flag DTO leakage or stale singleton.
- **Production solutions:** close with fake policy and adapter integration tests..

## Deep-dive talking points

Review a Hilt graph for injected concrete SDKs, leaked DTOs, binding direction and scope errors.

## Follow-up questions

- **Interviewer:** "What is the difference between `@Provides` and `@Binds` in Hilt regarding DIP?"
  **Answer:** "`@Binds` is used specifically to bind an abstract interface to a concrete implementation, promoting DIP and generating zero bytecode boilerplate. `@Provides` is used for creating instances requiring builder or manual setup logic (like configuring Retrofit or Room)."

- **Interviewer:** "How can Gradle modularization prevent Hilt from violating DIP?"
  **Answer:** "By removing dependencies between the feature module and the data/network modules. If the feature module cannot see `RetrofitService`, Hilt cannot inject it into the feature's ViewModel."

## Self-check rubric

Show one Hilt-injected DIP violation and repair it with a domain-facing contract.

## References and reviewed-on date

- [Android Hilt guide](https://developer.android.com/training/dependency-injection/hilt-android) — graph and bindings.
- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — dependency inversion.

Technically reviewed against primary documentation on 2026-10-13.
