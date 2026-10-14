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

The Dependency Rule states that source code dependencies must only point inward toward higher-level policies (the Domain layer). Inner layers must have zero awareness of outer layers. Outer layers (UI, Network, Database) depend on interfaces declared by the Domain layer, realized at runtime via Dependency Inversion.

## Interview answer — structured

The Dependency Rule is the foundational postulate of Clean Architecture: **source code dependencies must strictly point inward toward higher-level business policies**.

Under this rule, inner layers (Domain) must know absolutely nothing about outer layers (Data, UI, Frameworks). Nothing declared in an outer circle—such as a database class, a Retrofit API definition, an Android `Activity`, or a JSON parser—may be mentioned or imported by code in an inner circle.

The direction of dependencies is structured as follows.

First, `Presentation / UI` -> depends on -> `Domain` Next, `Data` -> depends on -> `Domain`
Finally, `Domain` -> depends on -> **Nothing (Pure Kotlin)**

This protects core business value from framework churn. If the team migrates from Retrofit to Ktor, or swaps Room for SQLDelight, not a single line of business rule logic in the Domain layer is touched, invalidated, or recompiled.


## Interview answer — deep senior

A frequent question arises: how can the Domain layer drive data operations if it cannot depend on the Data layer? This is resolved via the **Dependency Inversion Principle (DIP)**. The Domain layer defines an abstraction—a `Repository` interface—that specifies the queries and mutations it requires. The Data layer, residing in the outer circle, imports the Domain module and implements that interface (`RepositoryImpl`).

At application startup, the Dependency Injection container (Hilt/Koin) wires the concrete Data implementation to the Domain interface contract. Thus, at compile time, the source code dependency points inward, while at runtime, control flows outward through the interface abstraction.

In Gradle multi-module codebases, we enforce this rule via module dependencies: `:core:domain` has zero module dependencies, while `:core:data` has `implementation(project(":core:domain"))`.


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
