---
id: "SOL-07"
question: "Compare DIP and Dependency Injection (DI)."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 178
editorial_status: "reviewed"
---

# SOL-07

## Original interview question

Compare DIP and Dependency Injection (DI).

## What the interviewer evaluates

Separate a design principle from object construction/wiring, with a counterexample using Hilt.

## Explanation in Arabic

المقارنة الجوهرية بين مبدأ عكس التبعية (DIP) وحقن التبعيات (Dependency Injection - DI):

1. ما هو مبدأ عكس التبعية (DIP - Dependency Inversion Principle)؟
   - هو **مبدأ تصميم معماري عالي المستوى (High-level Architectural Principle)**.
   - يركز على: **اتجاه التبعيات (Direction of Dependencies)** وهيكلة العلاقات بين الطبقات.
   - يقول: "لا تجعل الكود العالي يعتمد على التفاصيل، بل اجعل كلاهما يعتمد على واجهات مجردة (Abstractions)".

2. ما هو حقن التبعيات (DI - Dependency Injection)؟
   - هو **نمط تصميم عملي / أسلوب تنفيذي (Creational Design Pattern / Technique)**.
   - يركز على: **كيفية تزويد الكائنات بالاعتماديات التي تحتاجها من الخارج بدلاً من إنشائها بنفسها بالداخل** (`new` أو instantiation).
   - يتم تنفيذه برمجياً عبر Constructor Injection أو عبر أطر عمل مثل Hilt و Koin و Dagger.

3. هل يمكن استخدام أحدهما دون الآخر؟
   - **نعم!**:
     * يمكنك استخدام DI بدون DIP: إذا قمت بحقن كلاس ملموس مباشر `class ViewModel(val api: RetrofitApi)`، فأنت استخدمت Dependency Injection، ولكنك انتهكت مبدأ DIP لأنك ارتهنت بكلاس منخفض المستوى دون أي تجريد!
     * الـ DI هو الأداة التقنية التي تجعل تطبيق مبدأ DIP سهلاً وعملياً في أندرويد.

## Practical walkthrough

توضيح الفرق بين DI بدون DIP و DI مع DIP:
```kotlin
// ❌ حقن تبعيات (DI) لكن بدون عكس التبعية (Violates DIP):
// هنا استخدمنا Constructor Injection (DI)، لكن الـ ViewModel يعتمد على كلاس ملموس مباشر من طبقة الشبكة:
class LoginViewModel @Inject constructor(
    private val retrofitService: RetrofitLoginService // 💥 DI مطبق لكن DIP منتهك!
) : ViewModel() { ... }

// ✅ DI متناغم مع DIP بنسبة 100%:
// 1. DIP: اعتماد على abstraction نقي في Domain:
interface AuthRepository {
    suspend fun login(creds: Credentials): Result<User>
}

// 2. DI + DIP: حقن الـ Abstraction في ViewModel وربط الـ Implementation عبر Hilt Module:
@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository // DIP مطبق بامتياز!
) : ViewModel() { ... }

@Module
@InstallIn(SingletonComponent::class)
abstract class AuthModule {
    @Binds
    abstract fun bindAuthRepository(impl: AuthRepositoryImpl): AuthRepository // DI يقوم بتوصيل الأسلاك
}
```

## Why it matters and how it works

DI is a construction mechanism; DIP is source-level dependency design. They often work together but are logically independent. Constructor injection makes dependencies visible and replaceable, yet the injected type may still be an unwanted detail.

## Worked example

Counterexample: `class TransferRule @Inject constructor(private val api: RetrofitTransferApi)` uses DI but policy imports transport. Better: `TransferRule(private val status: TransferStatusSource)` with a data adapter bound in Hilt or a manual composition root.

## Trade-offs and decision criteria

Hilt reduces manual graph wiring but adds generated code and Android setup. Manual DI can be enough for a small app. Neither approach excuses a poorly chosen abstraction or hidden service locator.

## Failure modes

A team celebrates replacing `Retrofit.create()` with Hilt constructor injection, yet the use case still handles HTTP codes and DTOs. The change improves construction but not policy isolation. Move mapping to data and inject a domain-facing contract.

## Production perspective

A marketplace uses Hilt to bind a pricing repository contract to an API-backed adapter, while domain tests manually pass a fake. The design can survive an adapter change and still be tested without Hilt.

## Interview answer — short

DIP is an architectural principle stating that high-level modules should depend on abstractions rather than low-level details. DI is a creational pattern/technique of supplying dependencies from the outside (via constructor injection or Hilt). You can use DI without DIP by injecting concrete classes directly.

## Interview answer — structured

While frequently conflated, Dependency Inversion Principle (DIP) and Dependency Injection (DI) operate at fundamentally different architectural levels.

1. **DIP (The Architectural Principle)**:
   - Formulated as the 'D' in SOLID.
   - Dictates **coupling direction**: high-level business policies must depend on abstractions (interfaces), and low-level detail implementations must depend on those same abstractions.
   - It answers: *'How should my software layers be decoupled structurally?'*

2. **DI (The Creational Technique / Pattern)**:
   - A concrete implementation pattern (typically powered by frameworks like Hilt, Dagger, or Koin).
   - Dictates **how dependencies are instantiated**: instead of a class instantiating its collaborators (`val repo = UserRepository()`), they are passed into its constructor from an external assembler.
   - It answers: *'How does a class obtain references to its collaborators at runtime?'*

Crucially, **using DI does not automatically satisfy DIP**. Injecting a concrete `RetrofitApi` into a `ViewModel` uses Dependency Injection, but severely violates the Dependency Inversion Principle because the high-level ViewModel remains tightly coupled to low-level networking details.

## Interview answer — deep senior

Under the hood, DI acts as the practical enabler of DIP. When you apply DIP, a class depends on an abstract interface (`UserRepository`). However, at runtime, a concrete instance (`UserRepositoryImpl`) must actually be created and passed to that class. Without DI, the class or its caller would have to manually call `UserRepositoryImpl()`, resurrecting the compile-time coupling DIP was designed to eliminate.

Dagger/Hilt resolves this using **`@Binds`**: it maintains a compile-time dependency graph that maps the Domain abstraction `UserRepository` to the Data implementation `UserRepositoryImpl`, injecting it seamlessly.

In unit testing, DI allows passing an in-memory `FakeUserRepository` without any DI framework, making tests fast and deterministic.

## How to answer in the interview

- **Why:** Define DI versus DIP.
- **How:** show injected Retrofit counterexample.
- **Trade-offs:** mention interface overhead.
- **Failure cases:** explain DTO leakage.
- **Production solutions:** finish with domain contract and composition binding..

## Deep-dive talking points

Construct a Hilt-but-not-DIP example and a manual-DI-with-DIP example; inspect public types.

## Follow-up questions

- **Interviewer:** "Can you have DIP without a DI framework like Hilt?"
  **Answer:** "Yes. You can invert dependencies using pure interfaces and wire them up manually using manual dependency injection (pure Constructor Injection in Application class) without any third-party framework."

- **Interviewer:** "What is the `@Binds` annotation in Hilt/Dagger, and how does it relate to DIP?"
  **Answer:** "`@Binds` tells Hilt which concrete implementation class to provide when an abstract interface is requested, directly wiring DIP abstractions at compile time without generating extra factory code."

## Self-check rubric

Give one counterexample proving DI and DIP are independent, then repair the boundary.

## References and reviewed-on date

- [Android dependency injection](https://developer.android.com/training/dependency-injection) — injection mechanisms.
- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — inversion.

Technically reviewed against primary documentation on 2026-10-13.
