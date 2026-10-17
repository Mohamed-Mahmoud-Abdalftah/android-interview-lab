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

## Concept and technical explanation

Hilt acts as a dependency injection framework that automates object graph creation and lifecycle scoping, but using Hilt does not inherently guarantee compliance with the Dependency Inversion Principle (DIP). DIP is an architectural principle mandating that high-level modules must depend on abstract contracts rather than concrete details. If an engineer uses Hilt's @Inject constructor to inject a concrete Room database entity or Retrofit API class directly into a ViewModel, Dependency Injection is operational, but Dependency Inversion is completely broken because the high-level presentation layer remains tightly coupled to infrastructure details.

## Practical walkthrough (English)

Contrasting Hilt wiring that violates DIP against Hilt wiring that fulfills DIP:
```kotlin
// SCENARIO 1: Hilt used, but Dependency Inversion Principle VIOLATED!
// ViewModel depends directly on concrete Room implementation detail
class BadUserViewModel @Inject constructor(
    private val localRoomDao: UserDaoImpl // Direct concrete class coupling! Violates DIP!
) : ViewModel()

// SCENARIO 2: Hilt used, and Dependency Inversion Principle FULFILLED!
// 1. High-level Domain module defines pure Kotlin contract
interface UserRepository {
    suspend fun fetchUserProfile(): Result<UserProfile>
}

// 2. Low-level Data module implements the contract
class UserRepositoryImpl @Inject constructor(
    private val localRoomDao: UserDaoImpl
) : UserRepository {
    override suspend fun fetchUserProfile() = runCatching { localRoomDao.getUser().toDomain() }
}

// 3. Hilt module binds the abstraction to implementation using @Binds
@Module
@InstallIn(SingletonComponent::class)
abstract class UserDomainModule {
    @Binds
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// 4. ViewModel depends strictly on the Domain abstraction! Fulfills DIP!
class CleanUserViewModel @Inject constructor(
    private val repository: UserRepository // Abstract interface dependency
) : ViewModel()
```

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

Hilt provides the plumbing for dependency injection by instantiating and passing dependencies via constructors, but it does not dictate architectural rules. If you use Hilt to inject concrete classes like RoomUserDao or OkHttpClient directly into a ViewModel, you are practicing dependency injection while completely violating the Dependency Inversion Principle. Fulfilling DIP requires defining abstract domain interfaces and using Hilt's @Binds or @Provides to deliver concrete implementations behind those abstractions.

## Interview answer — structured

Distinguishing Hilt's operational mechanics from the architectural goals of Dependency Inversion is a fundamental senior engineering skill.
Hilt is an automated tool implementing Inversion of Control. It eliminates manual object instantiation by generating factory boilerplate, managing component lifecycles, and injecting dependencies via @Inject constructors. However, Hilt is completely agnostic about whether the injected dependency is an interface or a concrete class.
When an engineer uses Hilt to inject a concrete Room database or Retrofit service directly into a ViewModel or UseCase, the system practices Dependency Injection, but it flatly violates the Dependency Inversion Principle.
In this flawed setup, high-level business logic is directly coupled to low-level SQLite annotations and HTTP networking drivers. Upgrading or swapping the database forces rewrites across the UI and presentation layer.
To achieve true DIP with Hilt, the dependency direction must be inverted.
The high-level Domain layer declares pure Kotlin repository interfaces.
The low-level Data layer implements those interfaces.
Finally, a Hilt @Module uses @Binds to map the interface to the concrete implementation. Hilt delivers the object, but the architecture satisfies DIP.

## Interview answer — deep senior

Under the hood, failing to enforce DIP while using Hilt dismantles the compilation firewalls of multi-module Android architectures.
In a multi-module enterprise project, Gradle modules should enforce architectural layers: :feature depends on :domain, and :data depends on :domain. The :domain module remains pure Kotlin with zero Android framework or database dependencies.
When engineers bypass DIP and inject concrete classes via Hilt, the :feature module must declare a direct Gradle dependency on the :data module (implementation(project(":data"))). This exposes Room database DAOs, SQLite drivers, and Retrofit network response DTOs directly to the UI presentation layer.
Any internal change to a database column or an OkHttp interceptor invalidates Gradle's build cache for the :data module, triggering an unnecessary recompilation cascade across all dependent :feature modules and inflating build times.
When DIP is enforced, Hilt bindings are declared in the root :app assembly module or dedicated binding submodules. The :feature module compiles solely against the abstract interfaces in :domain, allowing Gradle's Compilation Avoidance to completely skip feature recompilation during data layer changes.
Furthermore, testing harnesses benefit enormously. Testing a ViewModel that injects a DIP-compliant interface requires zero reflection, zero Hilt test runners, and zero Mockk agents; a 5-line pure Kotlin fake repository provides deterministic, millisecond-fast JVM test execution.

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
