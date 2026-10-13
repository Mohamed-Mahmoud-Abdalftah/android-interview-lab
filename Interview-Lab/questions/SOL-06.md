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

DIP تقول high-level business policy ما تعتمدش على low-level detail زي Retrofit service أو Room DAO مباشرة؛ الاتنين يعتمدوا على abstraction مناسبة للpolicy. مثال `EligibilityUseCase` يحتاج `AccountStatusSource`، وdata implementation تستخدم API/DB. وقت التشغيل DI تربطهم، لكن DIP هي direction/types مش أداة حقن. لا تضع interface في data module ثم تخلي domain تستورد Retrofit DTO من signature؛ ده مش inversion حقيقي. في Android guidance domain اختيارية وقد تعتمد على repository في data؛ وضّح هل تتكلم عن Clean Architecture classic ولا توصيات Android العملية.

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

## Practical walkthrough

لو `CanTransfer` بتستورد `RetrofitTransferApi` وتفهم HTTP codes، business rule مربوط بتفاصيل الشبكة. خليها تسأل `AccountStatusSource` عن `AccountStatus` مفهومة في الدومين. الـdata adapter يترجم response وnetwork errors، والـcomposition root يربط adapter بالعقد. اختبر قرار التحويل بـfake من غير Android أو network. لازم تحدد معنى الحالة القديمة أو unknown: هل تمنع التحويل ولا تطلب refresh؟ مجرد interface حوالين Retrofit response مش DIP مفيد، لأن نوع النقل لسه متسرب جوه policy.

## Trade-offs and decision criteria

A contract adds indirection and DI wiring. In a tiny feature, depending on a concrete repository may be simpler if it exposes stable app data. Use DIP where volatile implementation would otherwise reach important policy.

## Failure modes

A use case constructor takes `RetrofitAccountService` and returns `Response<AccountDto>`; changing the API changes policy tests and signatures. Introduce a domain-facing contract and map transport details at the adapter.

## Production perspective

A credit-limit rule depends on `CreditStatusSource`; production adapter fetches and caches status, tests supply deterministic states. Server still authorizes the actual transaction.

## Interview answer — short

DIP means high-level policy depends on a stable abstraction rather than a specific low-level adapter. DI can supply the adapter at runtime, but the interface and dependency direction are the design choice.

## Interview answer — structured

I separate the business decision from the mechanism that fetches inputs. A transfer eligibility rule should know account status, not Retrofit response types or a particular database. It depends on a small `AccountStatusSource` contract, while a data adapter implements that contract. The app graph injects the implementation. This keeps policy tests fast and transport changes local. I add the abstraction when it protects a meaningful boundary, not for every pure helper. In a transfer feature, I would ask for an account eligibility fact, not an HTTP response object.

## Interview answer — deep senior

The key is source dependency direction. The high-level policy names the information it needs in domain terms; the low-level adapter knows how to get it from a server or database. Both can be wired at runtime through DI, but using Hilt alone does not guarantee DIP if the use case still imports a concrete SDK. I inspect module edges and signature types, especially DTO or Android framework leakage. In classic Clean Architecture, contracts often belong inward with policy. Android’s practical guidance may organize the optional domain layer above data repositories, so I state the chosen model explicitly. For a critical flow I also test substitution and server authority; swapping adapters should not alter the rule’s result meaning. Dependency inversion concerns the direction of source-level dependencies: high-level transfer policy should not import transport details. I would define a small status contract in the consumer's language and put the Retrofit mapping in a data adapter. Wiring can be manual or through Hilt; the mechanism of construction is a separate concern. The useful test replaces the source with an in-memory fake and checks blocked, active, and unknown states. The failure mode is an interface whose method still returns `Response<Dto>`: that merely renames the dependency while preserving the coupling. In production I would also specify stale-data behavior, cancellation, and how authorization is confirmed by the backend.

## How to answer in the interview

- **Why:** Show dependency direction.
- **How:** map HTTP data into domain status.
- **Trade-offs:** mention extra boundary cost.
- **Failure cases:** flag `Response<Dto>` leakage.
- **Production solutions:** end with fake tests and backend authority..

## Deep-dive talking points

Draw source arrows versus runtime calls; identify a leaking DTO signature and a consumer-owned contract.

## Follow-up questions

- [SOL-07](../sol-07/): DIP versus DI? **Answer:** DIP is design direction; DI is one way to supply dependencies.
- [ARC-03](../arc-03/): What is the Dependency Rule? **Answer:** classic Clean Architecture source dependencies point inward.

## Self-check rubric

Show an inverted account-status contract, locate its implementation, and explain why Hilt wiring alone is insufficient.

## References and reviewed-on date

- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — dependency inversion.
- [Android dependency injection](https://developer.android.com/training/dependency-injection) — DI mechanics.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
