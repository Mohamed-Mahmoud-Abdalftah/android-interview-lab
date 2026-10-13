---
id: "SOL-02"
question: "Explain Single Responsibility Principle with an Android example."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 173
editorial_status: "reviewed"
---

# SOL-02

## Original interview question

Explain Single Responsibility Principle with an Android example.

## What the interviewer evaluates

Use “one reason to change” correctly rather than one method or one task per class.

## Explanation in Arabic

SRP معناها module يكون له سبب تغيير متماسك من جهة requirement/actor واحدة، مش “class تعمل function واحدة”. `CheckoutViewModel` لو بتعرض UI state، بتعمل Retrofit parsing، بتحسب fees، وبتسجل analytics، كل جزء بيتغير لسبب مختلف. اترك state production في ViewModel، rules في domain/use case لما تستحق، network mapping في data، analytics خلف contract مناسب. لكن تقسيم class متماسكة لـعشر helpers صغيرة من غير حدود حقيقية مش SRP. راجع change history ومن يطلب التعديل لتعرف cohesion.

## Why it matters and how it works

Cohesion around one reason to change keeps unrelated changes from breaking each other. In Android, UI rendering, network schema and business policy commonly evolve on different timelines. SRP is about responsibility to a change actor, not a fixed line count.

## Worked example

Scenario: `ProfileViewModel` both converts JSON and produces `ProfileUiState`. When server renames `avatar_url`, the ViewModel must change even though the screen contract did not. Move DTO mapping to repository/data; keep `ProfileUiState` logic in ViewModel. Test both boundaries separately.

## Practical walkthrough

لو `ProfileViewModel` بتقرأ JSON، تخزن في Room، وتجهز نصوص الشاشة، أي تغيير في API schema أو قاعدة البيانات أو التصميم هيعدل نفس الملف. افصل DTO mapping في data layer، وقرارات عرض الحالة في ViewModel، وخلي repository ينسق مصدر البيانات. الاختبار العملي: غيّر `avatar_url` في fixture؛ المفروض test المابّر فقط يتغير، مش UI state tests. المسؤولية هنا سبب التغيير، مش عدد الدوال ولا شرط إن كل class صغيرة. لو استخراج class جديد بيمرر parameters بلا منطق، يمكن تكون بتفكك زيادة.

## Trade-offs and decision criteria

Extract only independently changing concerns. A small class may legitimately contain several methods supporting one responsibility. Too many microscopic classes can obscure the use case and increase DI/build overhead.

## Failure modes

A “God ViewModel” changes for API schema, tax policy and UI copy in one release, causing regression outside the requested area. Characterization tests and incremental extraction reduce risk. Naming a class `UseCase` without moving policy does not fix cohesion.

## Production perspective

An ecommerce team separates checkout price policy from localized UI strings and provider transport. Product managers can change discounts without touching screen lifecycle code; UI redesign does not rewrite server mapping.

## Interview answer — short

SRP says a module should have one coherent reason to change. In Android, I keep UI state production separate from transport mapping and business rules so a server change does not force a ViewModel rewrite.

## Interview answer — structured

I do not interpret SRP as “one method per class.” I look for independent change pressures. If a ViewModel parses Retrofit DTOs, calculates discounts and formats screen text, server, business and UI changes all hit one file. I would move transport mapping into data and reusable discount policy into a focused domain component, while leaving screen state in the ViewModel. A small cohesive class can have many methods. The goal is fewer unrelated regressions, not a maximum number of files. A useful review technique is to look at three recent pull requests. If a server field rename, discount change, and screen copy update all modified the same ViewModel, it probably has several independent change pressures.

## Interview answer — deep senior

I would examine recent changes and ask which stakeholder or requirement caused each one. SRP is violated when one module must respond to independent policies, such as a server schema, pricing rule and UI design. In a real app I would first capture behavior, then extract one boundary at a time so errors and cancellation do not change accidentally. Data maps DTOs to stable app values; a policy component computes discount eligibility; ViewModel maps those outcomes to UI state. I would not split every helper into a separate class if all of them change together for the same feature. The design is successful when a new pricing rule stays in pricing tests and a server rename stays in adapter tests, with no surprise edits in presentation. The actor framing prevents a common mistake: a repository with several methods can still be cohesive if all methods respond to one data-policy concern. I would identify the separate change actors before moving code: the backend can rename a field, design can change presentation, and product can change eligibility. Each deserves a test boundary when its change is independent. In a profile screen, the data layer maps the API DTO to an app model, while the ViewModel maps that model to UI state and handles user actions. I would use a repository for data access, consistent with Android architecture guidance. A failure sign is a ViewModel test that needs Retrofit or JSON fixtures just to check a loading label. But I would not split every helper into a use case if it adds no reusable rule or clarity.

## How to answer in the interview

- **Why:** Define reason to change.
- **How:** walk through the DTO/ViewModel split.
- **Trade-offs:** avoid class-count dogma.
- **Failure cases:** mention schema-coupled UI tests.
- **Production solutions:** end with narrow tests per boundary..

## Deep-dive talking points

Use change history to identify independent actors; compare line-count refactoring with actual cohesion.

## Follow-up questions

- [SOL-08](../sol-08/): How differs from ISP? **Answer:** SRP addresses a module’s reasons to change; ISP addresses what clients must depend on.
- [ARC-21](../arc-21/): How refactor a God ViewModel? **Answer:** characterize behavior and extract responsibilities incrementally.

## Self-check rubric

Identify three reasons to change in one ViewModel, propose owners, and explain why one-method classes are unnecessary.

## References and reviewed-on date

- [Robert C. Martin, Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — change actors and cohesion.
- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — ViewModel role.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
