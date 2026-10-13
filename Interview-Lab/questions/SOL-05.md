---
id: "SOL-05"
question: "Explain Interface Segregation Principle with an Android example."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 176
editorial_status: "reviewed"
---

# SOL-05

## Original interview question

Explain Interface Segregation Principle with an Android example.

## What the interviewer evaluates

Explain client-specific interfaces rather than merely “small interfaces” or SRP.

## Explanation in Arabic

ISP بتقول client ما يعتمدش على methods مش بيستخدمها. لو `AccountService` فيها login، analytics، export، payment، وكل screen لازم inject نفس giant contract، أي تغيير فيه يعمل ripple ويجبر fake implementations على methods فارغة. اقسمها حسب client needs: `SessionReader`, `SignOut`, `PaymentStatusSource` مثلًا. الهدف مش interface واحدة لكل method؛ خلي interface متماسكة لخدمة client واضح. في Android modules، العقود الضيقة تقلل imports وbuild/test coupling.

## Why it matters and how it works

A wide interface couples clients to unrelated changes and forces implementations to provide irrelevant behavior. Segregated contracts let each consumer depend on exactly the capabilities it needs, improving substitution and test fakes.

## Worked example

Conceptual Kotlin:
```kotlin
interface SessionReader { fun currentUserId(): String? }
interface SignOut { suspend fun signOut() }
class AccountMenu(private val signOut: SignOut)
```
A read-only widget does not need to depend on sign-out or payment methods. Shared implementation may implement both interfaces.

## Practical walkthrough

لو widget عايز يعرض اسم المستخدم فقط، متدّيلوش `AccountService` فيها logout وtoken refresh وحذف الحساب. خليه يعتمد على `SessionReader` صغيرة، وشاشة الإعدادات على `SignOut`. نفس implementation ممكن ينفذ الاتنين. لما يتغير logout flow، widget مش محتاج إعادة بناء معرفي أو fake ضخم في اختباره. لكن متقسّمش interface إلى getter لكل field؛ دور على مجموعات calls اللي clients فعلاً بتستخدمها. اعمل جدول client مقابل methods، واتبع dependencies الحقيقية قبل الrefactor.

## Trade-offs and decision criteria

Over-splitting creates interface clutter and wiring. Group operations that change together for one client. A cohesive repository API can have several methods without violating ISP; size alone is not the criterion.

## Failure modes

A fake for a settings screen implements 20 unrelated payment methods as `error("unused")`; tests become brittle and production substitutes may throw. Split contracts around consuming features and run contract tests.

## Production perspective

A wallet app exposes a narrow session reader to UI, a token refresher to networking, and sign-out capability to account settings. The implementation can share state while feature dependencies stay focused.

## Interview answer — short

ISP says a client should not depend on operations it does not use. I split a broad service into cohesive capabilities aligned with consumers, without creating one interface per method.

## Interview answer — structured

If a profile screen only needs to observe session status, it should not depend on a giant account interface that also exposes payment or export commands. Wide contracts make unrelated changes rebuild clients and force fakes to implement unused methods. I define narrow capability interfaces for groups of related operations, and one implementation may implement several. The rule is about client dependency, not an arbitrary maximum method count. For example, a payment status widget should not receive an interface that can initiate a charge or delete an account. Narrowing its dependency reduces both accidental calls and the surface that tests must fake. One implementation can still own the shared state.

## Interview answer — deep senior

I would inspect which methods each consumer actually calls and which changes cause cascading edits. A broad `AccountService` can tie settings, checkout and analytics to one signature set; even a fake for one screen must stub unrelated operations. Splitting into `SessionReader`, `SignOut`, and `PaymentStatusSource` lets each feature depend on its own capability and makes contract tests precise. But I do not split every method into a separate interface if several operations form one cohesive client use case. On Android, narrower contracts also help modularization and prevent accidental imports of provider-specific or security-sensitive methods. The implementation can still share a repository internally; ISP is about what clients see. I would build a client-method matrix before splitting anything. ISP is about the consumer's contract rather than the implementation's class size. I would map which operations each caller actually uses; a read-only UI component should not import token rotation or account deletion capabilities. Small role interfaces let one implementation serve several consumers while tests provide focused fakes. A sign-out change should not force a read-only widget to update its mock. The risk is splitting too far into dozens of one-method interfaces that obscure the workflow. I would group methods by stable client role and migrate one caller at a time, checking dependency graphs and tests for accidental access to unrelated operations.

## How to answer in the interview

- **Why:** Describe the client's unused methods.
- **How:** draw client-method matrix.
- **Trade-offs:** note interface proliferation.
- **Failure cases:** cite giant mocks as a symptom.
- **Production solutions:** propose role interfaces and focused fakes..

## Deep-dive talking points

Compare one giant account API to client-facing capabilities; discuss fake tests and module rebuild coupling.

## Follow-up questions

- [SOL-08](../sol-08/): How differs from SRP? **Answer:** ISP focuses on a client’s dependency surface; SRP on reasons a module changes.
- [SOL-15](../sol-15/): How split a wide interface? **Answer:** cluster methods by consumer capability, then migrate callers.

## Self-check rubric

Identify two clients using different method subsets, propose capability interfaces, and avoid one-method-interface dogma.

## References and reviewed-on date

- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — interface segregation and dependency direction.
- [Android modularization guide](https://developer.android.com/topic/modularization) — module boundaries.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
