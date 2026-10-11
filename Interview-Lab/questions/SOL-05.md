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

I would inspect which methods each consumer actually calls and which changes cause cascading edits. A broad `AccountService` can tie settings, checkout and analytics to one signature set; even a fake for one screen must stub unrelated operations. Splitting into `SessionReader`, `SignOut`, and `PaymentStatusSource` lets each feature depend on its own capability and makes contract tests precise. But I do not split every method into a separate interface if several operations form one cohesive client use case. On Android, narrower contracts also help modularization and prevent accidental imports of provider-specific or security-sensitive methods. The implementation can still share a repository internally; ISP is about what clients see. I would build a client-method matrix before splitting anything. If two screens use disjoint subsets and unrelated additions keep forcing both to recompile, a capability boundary is justified. I would also review security and permissions: a broad interface can expose sensitive operations to modules that have no reason to see them. Yet a single cohesive `ProfileEditor` may have several operations; creating one interface per method just moves complexity into DI wiring. ISP is about client relevance and substitutability, not an arbitrary size target.

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

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
