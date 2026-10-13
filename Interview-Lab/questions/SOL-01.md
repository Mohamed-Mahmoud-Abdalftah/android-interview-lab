---
id: "SOL-01"
question: "What does SOLID stand for, and why does it matter?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 172
editorial_status: "reviewed"
---

# SOL-01

## Original interview question

What does SOLID stand for, and why does it matter?

## What the interviewer evaluates

Name all five principles and explain their shared goal as change control, not class-count rules.

## Explanation in Arabic

SOLID اختصار لـSingle Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. هي heuristics لتقليل ripple effect لما requirements تتغير، مش قوانين تفرض interface لكل class. SRP تجمع اللي يتغير لسبب واحد، OCP تحمي policy من تعديلات متكررة بإضافة behavior، LSP تمنع subtype يكسر وعود base، ISP تمنع clients تعتمد على methods مش محتاجاها، DIP تخلي high-level policy مستقلة عن low-level details. في Android ده يظهر في ViewModel صغيرة، repository boundary، provider strategies، وinterfaces ضيقة. لكن abstractions غير مبررة تزود التعقيد.

## Why it matters and how it works

The principles address cohesion, extension, substitutability, client-specific contracts and dependency direction. They work together when a codebase grows, but each has a cost and context. Their practical measure is whether changes remain local and behavior remains substitutable.

## Worked example

Conceptual Android example: checkout policy depends on `PaymentGateway` rather than a specific SDK (DIP), accepts new provider adapters without editing the policy (OCP), and every adapter must honor the same result/cancellation contract (LSP). UI does not depend on unrelated gateway methods (ISP), while rendering stays separate from provider I/O (SRP).

## Practical walkthrough

في مقابلة على تطبيق checkout، ابدأ من change request حقيقي: مزود دفع جديد. اسأل: هل هتعدل شاشة الدفع والـpolicy والـSDK mapping مع بعض؟ لو آه، عندك أكثر من سبب للتغيير وانتشار واسع. خلي قرار الأهلية في policy، والتعامل مع الـSDK في adapter، والعقد بينهما صغير وواضح. بعدها اختبر إن كل adapter يرجع نفس أنواع النتائج ويلتزم بالإلغاء والـretry. ما تحولش كل class إلى interface؛ احسب عدد أماكن التغيير قبل وبعد. وافتكر إن SOLID ما يضمنش نجاح المعاملة: تأكيد السيرفر وidempotency لازمين برضه.

## Trade-offs and decision criteria

Applying every principle mechanically can create needless layers and interface pairs. Start with concrete cohesive code, then introduce abstractions where change or variation is real. Duplication can be cheaper than a premature “universal” base class.

## Failure modes

A team says “we use Hilt, therefore SOLID is satisfied,” while business rules still import Retrofit DTOs and a base class forces unsupported methods. DI wiring alone does not establish proper contracts or substitution.

## Production perspective

A multi-provider payment app isolates provider SDKs behind a narrow contract and tests failure semantics; it does not claim exactly-once execution from an interface or local state. A one-screen prototype can remain simpler.

## Interview answer — short

SOLID is five design principles for keeping change local: single responsibility, open/closed, substitutability, interface segregation, and dependency inversion. I use them as review questions, not a mandate to add interfaces everywhere.

## Interview answer — structured

I explain SOLID by asking what happens when a requirement changes. SRP keeps unrelated reasons to change apart. OCP makes stable policy extensible through a suitable seam. LSP requires substitutes to honor the contract. ISP keeps clients from depending on unused operations. DIP makes high-level policy depend on a stable abstraction rather than a specific SDK. In Android, a checkout rule and provider adapter illustrate several of them together.

## Interview answer — deep senior

These principles are most useful as a diagnosis of change pain. If adding a provider edits ten unrelated classes, OCP and DIP suggest a strategy seam. If an SDK implementation throws for a method that the contract promises, LSP and ISP are being strained. If a ViewModel renders UI, parses JSON, and decides payment policy, SRP suggests multiple reasons to change. But a proliferation of one-to-one interfaces is not the goal; it can make a small feature less readable and harder to evolve. I test substitution behavior, inspect dependency direction, and measure whether new requirements stay local. For critical Android flows I also consider lifecycle, cancellation, process death, and server authority, which the acronym itself does not solve. For example, I would trace one new provider request through the checkout code and mark every changed file. The useful seams are the ones that keep eligibility rules stable while provider mapping changes. A contract test can run against every adapter to check rejected, pending, cancelled, and network-uncertain outcomes. A UI-only fake is insufficient if the real SDK has different cancellation behavior. I would keep server confirmation and idempotency outside the acronym because interface design cannot make a payment exactly once. If the feature has only one stable implementation, a concrete class may be clearer until variation appears.

## How to answer in the interview

- **Why:** Lead with the five meanings and one change request.
- **How:** show where changes propagate.
- **Trade-offs:** mention abstraction cost.
- **Failure cases:** cite contract violations or cancellation.
- **Production solutions:** finish with contract tests and server confirmation..

## Deep-dive talking points

Map each letter to one concrete Android failure and an appropriate refactor; distinguish principle from DI framework.

## Follow-up questions

- [SOL-07](../sol-07/): Is DI the same as DIP? **Answer:** no; DI is wiring, DIP is dependency direction and contract design.
- [SOL-13](../sol-13/): Must each class have an interface? **Answer:** no; introduce one for meaningful variation or boundary.

## Self-check rubric

Expand all five letters, give an Android example for two, and explain one overengineering risk.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of responsibilities and dependency boundaries.
- [Robert C. Martin on SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — reasons to change.
- [Robert C. Martin on OCP](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — extension and dependency direction.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
