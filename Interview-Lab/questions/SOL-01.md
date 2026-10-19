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

Name all five principles, explain one or two with a meaningful Android example, and treat them as change and contract guidance rather than class-count or testability guarantees.

## Concept and technical explanation

SOLID names five object-oriented design principles: Single Responsibility (one reason to change for a cohesive unit), Open/Closed (extend behavior without repeatedly editing stable policy), Liskov Substitution (an implementation honors the behavior clients expect), Interface Segregation (clients depend on operations they use), and Dependency Inversion (high-level policy and low-level detail depend on suitable abstractions). The slogans need context. OCP does not forbid editing existing code; SRP does not mean one method per class; DIP does not require an interface for every class.

In Android, they can help separate UI state from product decisions, keep SDK adapters behind stable contracts, and prevent clients from depending on methods they never use. They do not guarantee simple maintenance, JVM-only tests, or freedom from regressions. Design for actual variation and test behavioral contracts.

## Practical walkthrough (English)

Suppose checkout can use two payment provider adapters. A narrow `PaymentGateway` contract lets the checkout policy depend on the result semantics rather than a provider SDK (DIP/ISP). Adding an adapter can extend the system without rewriting that policy (OCP), provided the contract remains suitable. Both adapters must distinguish approved, declined, and unknown outcomes consistently (LSP); treating timeout as decline would break substitution. UI rendering and provider communication have different reasons to change (SRP). This is a conceptual example, not a claim that an interface makes financial processing safe or exactly once.

## Explanation in Arabic

`SOLID` خمس Design Principles تساعدني أفكر في حدود التغيير والعقود، مش Checklist أزود عشانها Classes. `S — Single Responsibility`: الجزء المتماسك له سبب واضح للتغيير، مش شرط كلاس فيها Method واحدة. `O — Open/Closed`: أقدر أضيف Variation حقيقية من غير ما أعيد تعديل Policy مستقرة في كل مرة، لكن ده مش حظر لتعديل الكود. `L — Liskov Substitution`: أي Implementation تنفع مكان التانية من غير ما تكسر Behavior المتفق عليه. `I — Interface Segregation`: Client تعتمد على Methods اللي محتاجاها فقط. `D — Dependency Inversion`: Policy مهمة ما تبقاش مربوطة بتفاصيل SDK؛ الطرفين يعتمدوا على Contract مناسب.

في Android ممكن أفصل UI State عن Business Rule وأخلي Provider SDK وراء Adapter، بس المبادئ دي ما تضمنش Testability أو عدم وجود Bugs لوحدها. أضيف Abstraction لما Variation أو Boundary فعلًا تستحقها.

## Practical walkthrough

في Checkout افتراضي عندي Providerين للدفع. `PaymentGateway` Contract ضيقة تخلي Policy تعتمد على Result Semantics بدل SDK محددة: ده DIP وISP. Provider جديدة قد تضيف Behavior من غير تعديل Policy كل مرة: ده OCP لما الاختلاف حقيقي. لازم الاتنين يميزوا Approved وDeclined وUnknown بنفس المعنى: ده LSP؛ لو Timeout اتترجمت Declined في واحدة، الاستبدال ممكن يخلي العميل يعمل Retry غلط. UI Rendering وProvider I/O أسباب تغيير مختلفة: ده SRP. وجود Interface وحده ما يضمنش إن الدفع آمن أو Exactly-once.

## Why it matters and how it works

The principles address cohesion, extension, substitutability, client-specific contracts and dependency direction. They work together when a codebase grows, but each has a cost and context. Their practical measure is whether changes remain local and behavior remains substitutable.

## Worked example

Conceptual Android example: checkout policy depends on `PaymentGateway` rather than a specific SDK (DIP), accepts new provider adapters without editing the policy (OCP), and every adapter must honor the same result/cancellation contract (LSP). UI does not depend on unrelated gateway methods (ISP), while rendering stays separate from provider I/O (SRP).

## Trade-offs and decision criteria

Applying every principle mechanically can create needless layers and interface pairs. Start with concrete cohesive code, then introduce abstractions where change or variation is real. Duplication can be cheaper than a premature “universal” base class.

## Failure modes

A team says “we use Hilt, therefore SOLID is satisfied,” while business rules still import Retrofit DTOs and a base class forces unsupported methods. DI wiring alone does not establish proper contracts or substitution.

## Production perspective

A multi-provider payment app isolates provider SDKs behind a narrow contract and tests failure semantics; it does not claim exactly-once execution from an interface or local state. A one-screen prototype can remain simpler.

## Interview answer — short

SOLID stands for Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion. I use those ideas to make changes safer: keep a class focused, let implementations honor their contracts, and keep business rules away from concrete framework details. They are useful checks when a design is hard to change or test, not a reason to add an interface to every class.

## Interview answer — structured

SOLID is a set of five design principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion. In an interview I would name them, then explain the common purpose: make a change in one part of the app without surprising unrelated parts.

In Android, a large Activity that draws the screen, calls Retrofit, validates input, and writes to Room is a useful warning sign. I would move the decision logic out of the UI and give it a clear dependency on the data it needs. That makes the behavior easier to test. If I have several payment providers, I might put their differing behavior behind a narrow contract; each implementation must still honor the same failure semantics.

I would not apply the acronym mechanically. A one-off class does not need an interface just because Dependency Inversion exists, and forcing every variation into a shared base class can make things worse. I use the principles when they answer a real change or testing problem, then keep the simplest design that does that.

## Interview answer — deep senior

The interesting part is how the principles interact when requirements change. Single Responsibility is about reasons to change, not about making every class tiny. If a ViewModel owns UI state and delegates payment authorization rules, a policy change can be tested without booting an Activity. Open/Closed can help when new providers arrive, but only if the variation is real; an elaborate plugin system for one provider adds cost without benefit.

Liskov Substitution is the contract check. A provider implementation that silently treats a timeout as a decline cannot safely replace one that reports an unknown outcome. That is a correctness issue, even if both satisfy the same Kotlin interface. Interface Segregation helps keep consumers from depending on operations they cannot use, such as a read-only screen receiving a repository with mutation methods. Dependency Inversion puts important policy behind an abstraction that can be supplied by a data implementation, but using Hilt alone does not prove that the dependency direction is healthy.

I would test these boundaries with behavior-focused tests: the same contract cases for each provider, plus tests for failures and cancellation. I would also review whether the new abstraction made the code easier to change. If the change still touches ten unrelated classes, the boundary is probably in the wrong place. If a tiny feature now has five pass-through layers, I would simplify it. SOLID is most useful as a way to reason about change and substitutability, not as a scoring checklist.

## How to answer in the interview

Name the five principles, connect them to one real change or contract problem, and explain the cost of adding an abstraction. Avoid claiming that a DI framework proves SOLID or that an interface alone makes a payment safe.

## Deep-dive talking points

Map each letter to one concrete Android failure and an appropriate refactor; distinguish principle from DI framework.

## Follow-up questions

- **Interviewer:** "Does using Hilt mean the app follows Dependency Inversion?"
  **Answer:** "No. Hilt wires objects. If the business rule still imports a Retrofit DTO or depends directly on an Android component, its policy is coupled to that detail. I would look at the dependency direction, not just the constructor annotation."

- **Interviewer:** "Would you create an interface for every repository and use case?"
  **Answer:** "Only where the contract gives us a useful boundary or real variation. For one simple implementation, an extra interface can hide the flow without making change easier."

- **Interviewer:** "How can an implementation satisfy an interface and still violate Liskov Substitution?"
  **Answer:** "The method signatures can match while behavior differs. If one payment provider reports a timeout as a decline, callers may retry and charge twice. The behavioral contract has to cover those outcomes."

## Self-check rubric

Expand all five letters, give an Android example for two, and explain one overengineering risk.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns and dependency boundaries.
- [Robert C. Martin on SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — reasons to change.
- [Robert C. Martin on OCP](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — extension and dependency direction.

Technically reviewed against the cited primary documentation on 2026-10-19; agent editorial review, not human verification.

