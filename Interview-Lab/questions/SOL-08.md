---
id: "SOL-08"
question: "Compare SRP and ISP."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 179
editorial_status: "reviewed"
---

# SOL-08

## Original interview question

Compare SRP and ISP.

## What the interviewer evaluates

Contrast module cohesion/change actors with client-specific dependency surfaces.

## Explanation in Arabic

SRP تسأل: module دي بتتغير لأسباب مستقلة قد إيه؟ ISP تسأل: client دي مجبرة تعتمد على operations مش محتاجاها؟ `AccountManager` تجمع pricing وlogin وanalytics: SRP مشكلة لأن actors مختلفة. `AccountApi` فيها 30 method وكل screen تستخدم واحدة: ISP مشكلة لأن clients مقترنة بباقي interface. ممكن الاتنين يحصلوا معًا لكن العلاج مش نفسه دائمًا: SRP تفصل responsibilities حسب change، ISP تفصل contracts حسب consumers. ما تحولش كل method لـinterface منفصلة لو cohesive capability موجودة.

## Why it matters and how it works

SRP concerns the cohesion of a module and its reasons to change. ISP concerns the surface a client must depend on. One large service may violate both, but the diagnostic questions and boundaries differ.

## Worked example

Scenario: `AccountRepository` owns session refresh and profile storage, which may be cohesive or not depending on change. `CheckoutScreen` only needs `SessionReader`; giving it the full repository API creates ISP coupling even if repository itself is cohesive.

## Practical walkthrough

SRP تسأل: `AccountRepository` عنده كام سبب مستقل للتغيير؟ لو session refresh وprofile storage بيتغيروا بفرق ومتطلبات مختلفة، ممكن تفصلهم. ISP تسأل من زاوية المستهلك: `CheckoutScreen` محتاجة `currentUserId` فقط؛ ليه تعرف كل methods الـrepository؟ ممكن class واحدة تكون cohesive لكنها تقدم interfaces صغيرة لكل client. والعكس، تقسيم interface لا يصلح class بتخلط policy وdatabase وUI. اعمل change-history بسيط وجدول client-method قبل أي تعديل، واختبر أثر تعديل logout على الشاشة اللي بتقرأ session فقط.

## Trade-offs and decision criteria

Splitting implementation for SRP may reduce unrelated changes but adds composition. Segregating interfaces for ISP can keep one implementation behind several client views. Avoid class explosion when only the public dependency surface needs narrowing.

## Failure modes

A team responds to ISP by splitting a cohesive repository into dozens of tiny classes, increasing coordination. Another responds to SRP only by adding smaller interfaces while one God Class still contains unrelated policies. Diagnose before refactoring.

## Production perspective

A wallet team separates risk policy from session refresh (SRP) but exposes one session implementation through read-only and sign-out contracts for different features (ISP). Tests reflect both responsibilities and client surfaces.

## Interview answer — short

SRP asks whether a module has one coherent reason to change; ISP asks whether a client depends on operations it does not use. They can overlap, but splitting implementation and narrowing a contract are different remedies.

## Interview answer — structured

Suppose an account class changes for login policy, analytics format, and payment rules. That suggests SRP trouble because independent requirements hit one module. Suppose a checkout screen only reads session status but must depend on a huge account interface with export and sign-out methods. That suggests ISP trouble, even if the implementation is otherwise cohesive. I may split responsibilities for the first issue and expose smaller client-specific interfaces for the second. I do not assume every interface must have one method. For the fat interface, one implementation may remain cohesive while each client sees a small view of it.

## Interview answer — deep senior

I start with two separate questions. Who asks this module to change, and why? That is SRP and cohesion. Which methods or types must a particular client import to do its job? That is ISP. A God Class can violate SRP because unrelated business actors change it. A wide interface can violate ISP because clients recompile or fake methods they never use. I separate the questions. SRP asks whether one implementation has independent reasons to change; ISP asks whether a consumer is forced to depend on operations it does not use. A repository could be internally cohesive and still expose a broad interface to a tiny checkout client. Conversely, splitting its API into role interfaces does not repair an implementation that mixes session policy with UI rendering. I would inspect recent change requests and map consumers to methods, then refactor the pressure point. For example, checkout can take `SessionReader` while account settings takes `SignOut`, even if one repository implements both. The trade-off is extra types, so I would not split without a real caller boundary. Tests should show that a logout change leaves the reader consumer unaffected.

## How to answer in the interview

- **Why:** Contrast implementation cohesion with client dependence.
- **How:** use the repository/client example.
- **Trade-offs:** warn about extra types.
- **Failure cases:** cite broad mocks.
- **Production solutions:** propose change-history and client-method evidence..

## Deep-dive talking points

Diagnose a God Class and a fat interface separately; show a shared implementation behind narrow client contracts.

## Follow-up questions

- [SOL-02](../sol-02/): What is SRP’s question? **Answer:** independent reasons or actors causing a module to change.
- [SOL-05](../sol-05/): What is ISP’s question? **Answer:** which operations each client must depend on.

## Self-check rubric

Give one SRP-only smell and one ISP-only smell, then choose the right repair for each.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns in application modules.
- [Robert C. Martin on SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — cohesion/change actors.
- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — interface segregation.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
