---
id: "ARC-03"
question: "What is the Dependency Rule, and in which direction should dependencies point?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 148
editorial_status: "reviewed"
---

# ARC-03

## Original interview question

What is the Dependency Rule, and in which direction should dependencies point?

## What the interviewer evaluates

Explain compile-time source dependencies versus runtime control flow and where interfaces are placed.

## Concept and technical explanation

The Dependency Rule is the central governance constraint of Clean Architecture: source code dependencies must point exclusively inward, toward higher-level policies and business entities. Inner layers (Domain) must have zero knowledge of outer layers (Presentation, Data, Frameworks, Database, Network), meaning no name, interface, function, or data type declared in an outer circle can be mentioned or imported by an inner circle. To enable inner business logic to communicate with external data sources or dispatch UI callbacks without violating this rule, architects apply the Dependency Inversion Principle (DIP). The inner domain layer declares abstract repository interfaces representing its requirements, while the outer data layer implements those contracts and converts external payloads into domain models. Inversion of control is resolved at application startup using dependency injection frameworks like Hilt or Dagger.

## Practical walkthrough (English)

Enforcing inward dependencies via Dependency Inversion in Kotlin:
```kotlin
// ==========================================
// INNER CIRCLE: :core:domain (Pure Kotlin)
// ==========================================
data class PaymentTransaction(val id: String, val amount: Double, val status: String)

// Domain declares the contract it needs; knows NOTHING about Retrofit or Room
interface PaymentGateway {
    suspend fun executePayment(amount: Double): Result<PaymentTransaction>
}

class ProcessPaymentUseCase(private val gateway: PaymentGateway) {
    suspend operator fun invoke(amount: Double): Result<PaymentTransaction> {
        if (amount <= 0.0) return Result.failure(IllegalArgumentException("Amount must be positive"))
        return gateway.executePayment(amount)
    }
}

// ==========================================
// OUTER CIRCLE: :core:data (Depends on :core:domain)
// ==========================================
class StripePaymentGateway(
    private val stripeApi: StripeApi // Retrofit dependency lives OUTSIDE
) : PaymentGateway { // Implements inward domain interface!
    override suspend fun executePayment(amount: Double): Result<PaymentTransaction> = runCatching {
        val response = stripeApi.charge(StripeChargeRequest(amount))
        response.toDomainTransaction()
    }
}
```

## Explanation in Arabic

ما هي قاعدة التبعية (The Dependency Rule)، وفي أي اتجاه يجب أن تشير التبعيات دائماً؟

1. نص قاعدة التبعية الأساسية:
   - **قاعدة التبعية تنص على**: "لا يمكن لأي اسم أو كود أو كلاس في طبقة داخلية أن يذكر أو يعتمد على أي شيء موجود في طبقة خارجية".
   - التبعيات البرمجية في الكود (Source Code Dependencies) يجب أن تشير **دائماً إلى الداخل فقط (Inward towards the Domain)**.

2. لماذا يجب أن تشير التبعيات للداخل؟
   - لحماية منطق العمل الحساس (Core Business Rules) من التقلبات والتغييرات الخارجية (Framework Churn).
   - أطر العمل ومكتبات واجهات المستخدم تتغير وتتطور باستمرار (من XML إلى Compose، من RxJava إلى Coroutines، من SQLite المباشر إلى Room).
   - بفضل قاعدة التبعية، تستطيع تغيير مكتبة الشبكة بالكامل من Retrofit إلى Ktor دون المساس بسطر واحد من كود الـ Domain أو الـ UseCases!

3. كيف نحقق ذلك عملياً (Dependency Inversion)؟
   - كيف تقرأ طبقة الـ Domain بيانات من السيرفر إذا كانت لا تستطيع الاعتماد على طبقة الـ Data؟
   - الحل هو **عكس التبعية (DIP)**: الـ Domain يُعرّف Interface (`UserRepository`)، وطبقة الـ Data تعتمد على الـ Domain وتقوم بـ `implements UserRepository`. في وقت التشغيل، يقوم محرك الـ DI (Hilt) بحقن الـ Implementation.

## Practical walkthrough

توضيح انتهاك قاعدة التبعية وكيفية تصحيحه عبر Dependency Inversion:
```kotlin
// ❌ انتهاك صارخ: Domain يعتمد على تفاصيل طبقة Data (Retrofit DTO و Room Entity):
// في module:domain:
class AuthenticateUserUseCase(
    private val api: RetrofitAuthApi // 💥 خطأ كارثي! Domain أصبح يعرف تفاصيل الشبكة الخارجية!
) {
    suspend fun execute(dto: LoginRequestDto): UserEntity { ... }
}

// ✅ تطبيق قاعدة التبعية السليمة: التبعية تشير للداخل والـ Data تعتمد على الـ Domain:
// في module:domain:
interface AuthRepository { // عقد مجرد في قلب الـ Domain
    suspend fun authenticate(credentials: Credentials): Result<User>
}
class AuthenticateUserUseCase(private val authRepository: AuthRepository) {
    suspend fun execute(credentials: Credentials): Result<User> = authRepository.authenticate(credentials)
}

// في module:data (الطبقة الخارجية تعتمد على الـ Domain):
class AuthRepositoryImpl(private val api: RetrofitAuthApi) : AuthRepository {
    override suspend fun authenticate(credentials: Credentials): Result<User> {
        val dto = api.login(credentials.toDto())
        return Result.success(dto.toDomain())
    }
}
```

## Why it matters and how it works

Compile-time dependencies determine what must change/rebuild when a component changes. Dependency inversion lets a stable policy depend on an abstraction rather than a volatile adapter. The adapter depends on the policy contract and is supplied at runtime.

## Worked example

Conceptual Kotlin contract: `interface AccountRepository { suspend fun balance(id: AccountId): Balance }` in a stable module; `RoomAccountRepository` in data implements it. `GetBalanceUseCase` depends only on the interface. The app DI composition root binds the implementation. `Balance` is a domain value, not a Room entity.

## Trade-offs and decision criteria

Inversion has a cost: interface placement and wiring. For a small internal feature, a UI state holder depending on a concrete repository can still be acceptable if the dependency does not leak volatile types. Use interfaces where they isolate meaningful variation, not for every class.

## Failure modes

A domain contract returns `Response<AccountDto>`; although the interface lives in domain, the boundary still depends on Retrofit and server schema. Define domain-friendly inputs/outputs and map in the adapter. Avoid circular Gradle module dependencies created by placing contracts in the wrong module.

## Production perspective

A payment eligibility rule depends on a `PaymentStatusSource` contract. One adapter reads a backend API; tests use a deterministic fake. The server remains authoritative, and a new provider adapter does not force rule rewrites.

## Interview answer — short

Dependencies must point strictly inward toward pure business logic. Domain depends on nothing; Data and Presentation depend on Domain. We invert control using interfaces declared in Domain and implemented in Data, keeping core business policies completely insulated from framework volatility and third-party libraries.

## Interview answer — structured

The Dependency Rule is the foundational governance principle of Clean Architecture dictating that source code dependencies must point exclusively inward.

Inner layers represent high-level business policies and domain models, while outer layers represent volatile implementation mechanisms like UI frameworks, Room databases, and Retrofit network clients. The inner domain layer must know nothing about the outer layers, meaning no class in domain can import classes from data or presentation.

In production, when the domain layer requires information from an external database or network endpoint, it enforces the Dependency Inversion Principle. The domain layer declares an abstract repository interface representing the required business contract, and the outer data layer implements that interface.
As for dependency injection, frameworks like Dagger and Hilt wire the concrete data implementation into the domain consumer at runtime, keeping compile-time dependencies strictly pointed inward while runtime execution flows outward to external drivers.


## Interview answer — deep senior

Under the hood, the Dependency Rule decouples the lifespan of core business rules from external technology stacks. In traditional layered architectures, business logic frequently imported database DAOs or network models directly, creating a downstream dependency on third-party libraries and database schema definitions. When libraries change or APIs deprecate, business logic breaks.
By enforcing an inward dependency direction, the domain layer defines its own stable contracts and models. The outer data layer references the domain module and maps external DTOs into domain entities before returning them. This inversion ensures that updating from Retrofit to Ktor or switching from Room to SQLDelight requires zero changes inside domain use cases or business validation rules.
In modular Android architectures, this rule is strictly enforced by Gradle dependency graphs. The core domain module has no implementation dependency on data or presentation. Instead, app and data modules depend on domain, making accidental cyclic dependencies or illegal framework imports fail at compile time.
Staff engineers pay close attention to boundary leaks where developers define domain repository interfaces that inadvertently leak external types—such as Retrofit Response objects or Room exceptions—into domain method signatures. True inward dependency requires all exceptions and responses to be mapped into domain-safe results before crossing the architectural boundary. This ensures complete isolation and allows enterprise applications to swap infrastructure layers with zero regression risk.

## How to answer in the interview

- **Why:** business rules should survive framework change.
- **How:** use inward interfaces with outward implementations.
- **Trade-off:** abstraction cost versus stable core.
- **Failure case:** domain imports Room/Android types.
- **Production solution:** enforce module dependency direction.

## Deep-dive talking points

Draw compile-time module arrows separately from runtime calls. Inspect a repository contract for leaked `Response<Dto>` and show how DI binds an adapter.

## Follow-up questions

- **Interviewer:** "What happens if a Domain entity imports a Room `@Entity` annotation?"
  **Answer:** "It violates the Dependency Rule. The Domain becomes coupled to SQLite storage schemas, Room library versions, and Android packaging, breaking purity and JVM test isolation."

- **Interviewer:** "How does Gradle prevent accidental violations of the Dependency Rule?"
  **Answer:** "By making `:domain` an independent module without a dependency on `:data` or `:app`. If an engineer tries to import a Data class into Domain, the project fails to compile."

## Self-check rubric

State the source dependency direction, show a domain-facing contract, explain runtime calls, and detect one transport type leaked through the boundary.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — layer dependency guidance.
- [Robert C. Martin, The Dependency Rule](https://www.informit.com/articles/article.aspx?p=2832399) — original inward source-dependency rule.
- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — optional intermediate layer.

Technically reviewed against primary documentation on 2026-10-13.
