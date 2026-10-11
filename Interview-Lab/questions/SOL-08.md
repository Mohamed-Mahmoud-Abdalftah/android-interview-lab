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

## Trade-offs and decision criteria

Splitting implementation for SRP may reduce unrelated changes but adds composition. Segregating interfaces for ISP can keep one implementation behind several client views. Avoid class explosion when only the public dependency surface needs narrowing.

## Failure modes

A team responds to ISP by splitting a cohesive repository into dozens of tiny classes, increasing coordination. Another responds to SRP only by adding smaller interfaces while one God Class still contains unrelated policies. Diagnose before refactoring.

## Production perspective

A wallet team separates risk policy from session refresh (SRP) but exposes one session implementation through read-only and sign-out contracts for different features (ISP). Tests reflect both responsibilities and client surfaces.

## Interview answer — short

SRP asks whether a module has one coherent reason to change; ISP asks whether a client depends on operations it does not use. They can overlap, but splitting implementation and narrowing a contract are different remedies.

## Interview answer — structured

Suppose an account class changes for login policy, analytics format, and payment rules. That suggests SRP trouble because independent requirements hit one module. Suppose a checkout screen only reads session status but must depend on a huge account interface with export and sign-out methods. That suggests ISP trouble, even if the implementation is otherwise cohesive. I may split responsibilities for the first issue and expose smaller client-specific interfaces for the second. I do not assume every interface must have one method. For the fat interface, one implementation may remain cohesive while each client sees a small view of it. For the God Class, the implementation itself needs responsibility separation. Confusing the two can add interfaces without removing tangled logic or split classes without reducing client coupling.

## Interview answer — deep senior

I start with two separate questions. Who asks this module to change, and why? That is SRP and cohesion. Which methods or types must a particular client import to do its job? That is ISP. A God Class can violate SRP because unrelated business actors change it. A wide interface can violate ISP because clients recompile or fake methods they never use. One implementation may legitimately implement several narrow client contracts; I need not split it into one class per method. Conversely, splitting interfaces alone may leave a tangled implementation with multiple change reasons. I use change history, call sites and test pain to choose a refactor, then verify that changes become more local and that substitution behavior remains sound. I would run two small experiments. First, change a pricing rule: which modules need edits? If account session code changes too, SRP may be poor. Second, add an export method to an interface: which clients must rebuild or update fakes? If checkout is affected despite never exporting, ISP is poor. The remedies can be combined but should be chosen separately. The goal is not a graph with maximum nodes; it is a codebase where independent product changes stay independent and clients see only relevant operations.

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

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
