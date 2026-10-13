---
id: "SOL-03"
question: "Explain Open/Closed Principle with an Android example."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 174
editorial_status: "reviewed"
---

# SOL-03

## Original interview question

Explain Open/Closed Principle with an Android example.

## What the interviewer evaluates

Explain extension of stable policy and the strategic nature of “closed,” without banning all edits.

## Explanation in Arabic

OCP تقول stable module يكون قابل لإضافة variation من غير ما تعدّل كل core policy في كل مرة. في Android لو payment routing عندك `when(provider)` متكرر في 10 أماكن، Strategy contract أو registry يخلي provider جديد implementation جديدة مع wiring واختبارات، مش edits موزعة. بس لازم تفضل تعدّل composition root/config عند إضافة provider؛ OCP مش “ممنوع تلمس أي ملف”. وما تعملش plugin interface قبل وجود variation حقيقي. الحماية تكون حول محور تغيير متوقع ومهم.

## Why it matters and how it works

A stable policy should be insulated from foreseeable extensions through a deliberate seam. The seam can be strategy, adapter or data-driven configuration. Closure is strategic: not every possible future change needs an abstraction.

## Worked example

Conceptual Kotlin:
```kotlin
interface PaymentRoute { val code: String; suspend fun charge(request: Charge): ChargeResult }
data class Charge(val minor: Long, val requestId: String)
sealed interface ChargeResult { data class Accepted(val id: String): ChargeResult; data class Rejected(val code: String): ChargeResult }
```
A router selects a registered route; each provider adapter implements the same contract. Server authorization remains authoritative.

## Practical walkthrough

في checkout عندك provider واحد وبعدين دخل provider تاني. لو كل إضافة بتحتاج `when` جديد في ViewModel وrepository والanalytics، يبقى نقطة الاختلاف مش معزولة. اعمل `PaymentRoute` بعقد واحد، وخلي registry أو composition root يختار implementation. اختبر كل route بنفس contract suite: pending، rejection، cancellation، ونتيجة غير مؤكدة. OCP مش معناها إن مفيش أي ملف بيتعدل؛ غالبًا registration هيتغير. ولا تخلي extension seam تخفي قواعد قانونية أو أمنية مختلفة بين providers. لو التباين غير ثابت، branch واضح قد يكون أسهل من hierarchy مبكر.

## Trade-offs and decision criteria

Strategy indirection helps when providers vary often and behavior is stable. A simple `when` may be clearer for two fixed cases. New variations still require wiring, policy review and tests. Do not use reflection registries solely to avoid one explicit binding edit.

## Failure modes

A new provider requires changing UI, ViewModel, repository and retry logic because provider checks are scattered. Centralize the routing contract and shared policy. Conversely, a giant generic plugin API can become harder to evolve than a small conditional.

## Production perspective

A fintech checkout integrates card and wallet providers. A narrow route contract localizes SDK differences; tests verify declined, timeout and cancellation semantics. A backend holds provider credentials and validates payment state.

## Interview answer — short

OCP means a stable policy can gain a new variation through an extension seam rather than repeated edits throughout existing code. For Android payment providers, a strategy adapter can localize each integration.

## Interview answer — structured

I look for a change axis that is both likely and costly. If adding a payment provider means editing many branches across the app, I define a narrow provider contract and let each adapter implement it. The core checkout policy depends on that contract, while app wiring chooses implementations. This does not mean no file is ever edited; registration and tests still change. For a fixed two-case feature, an explicit `when` can be simpler than a plugin architecture. When adding a provider, I still expect to edit the DI binding or registry and add tests. OCP aims to avoid changing the stable checkout rule and every screen, not to make integration invisible.

## Interview answer — deep senior

OCP is about strategic closure against a class of change, not universal immutability of source code. I first identify what varies—provider SDK calls, notification channel, or pricing strategy—and what should remain stable—business validation and UI state contract. A narrow abstraction makes new implementations possible without modifying the stable policy. But it has costs: a contract can be too broad, and adding a provider still requires DI wiring, compatibility tests, and sometimes a new business rule. In a payment flow I test that each provider honors timeout and cancellation semantics; a new adapter cannot claim success on an uncertain network result. I avoid introducing a registry before variation exists, and I prefer one clear conditional when it is easier to understand and unlikely to change. I would first prove that provider variation is a real axis by examining past changes. The stable part is the checkout policy, not the list of providers. I would move provider SDK calls behind a strategy contract and select the implementation at an edge of the system. Adding a provider should add an adapter and a binding, while core eligibility and UI state rules remain unchanged. I would test the shared contract against all adapters, then test each adapter's SDK mapping separately. The trade-off is that a registry and interface make navigation harder when there is only one provider. I would introduce that seam after evidence of variation, and I would still review new provider security and business semantics explicitly rather than assuming extension is automatically safe.

## How to answer in the interview

- **Why:** Name the stable policy and varying provider.
- **How:** show strategy selection.
- **Trade-offs:** acknowledge registration cost.
- **Failure cases:** mention inconsistent provider semantics.
- **Production solutions:** close with shared contract and adapter tests..

## Deep-dive talking points

Distinguish strategic closure from no-edit dogma; compare strategy seam with a small conditional.

## Follow-up questions

- [SOL-18](../sol-18/): What if a provider changes ten classes? **Answer:** centralize variation behind a narrow route/adapter contract.
- [PAT-09](../pat-09/): Strategy versus State? **Answer:** strategy selects an algorithm; state models behavior based on current lifecycle state.

## Self-check rubric

Describe a likely variation, stable policy, extension seam and one reason not to abstract yet.

## References and reviewed-on date

- [Robert C. Martin, Open Closed Principle](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — strategic extension.
- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
