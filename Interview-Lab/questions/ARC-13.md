---
id: "ARC-13"
question: "When is a separate domain layer genuinely useful versus optional?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 158
editorial_status: "reviewed"
---

# ARC-13

## Original interview question

When is a separate domain layer genuinely useful versus optional?

## What the interviewer evaluates

Apply Android guidance that domain is optional and articulate evidence that justifies one.

## Explanation in Arabic

Domain layer مش واجب في كل Android app. لو عندك ViewModel بسيطة بتنادي repository لقراءة شاشة واحدة، UseCase `GetItemsUseCase` اللي تعمل `repo.getItems()` بس بتضيف indirection. لما logic بقى معقد أو reused بين شاشات—زي eligibility، combine accounts/orders، أو transaction workflow—use case تعطي اسم واضح، tests مستقلة، وتحمي ViewModel من التضخم. افتكر إن Android docs تسمي domain optional وبينها وبين تعريف Clean Architecture الكلاسيكي فرق طفيف؛ اختار boundary حسب المشكلة الحقيقية.

## Practical walkthrough

Domain layer منفصلة مفيدة لو rules مشتركة بين عدة screens أو فيها invariants واختبارات مستقلة عن Android. لو app صغيرة وrepository واحدة pass-through، layer إضافية قد تشتت الفهم. ابدأ direct VM->repository، ثم استخرج use case عندما يتكرر قرار أو يتطلب transaction/coordination. المعيار هو فصل policy الحقيقي، لا اتباع رسم ثابت.

## Why it matters and how it works

Android guidance recommends domain use cases for complex logic or reuse across ViewModels, but not as a mandatory layer. The cost is extra files, mapping and navigation. A use case should own one coherent behavior rather than merely pass through.

## Worked example

Decision example: a one-screen weather app calls `WeatherRepository.observeForecast()` from ViewModel. A multi-feature finance app introduces `CalculateTransferEligibilityUseCase` because the same rule drives review, transfer, and account screens and combines limits plus status.

## Trade-offs and decision criteria

Starting without domain is reversible if repository/UI boundaries are clear. Adding use cases too early creates boilerplate; adding them too late leaves duplicated rules and giant state holders. Measure by duplication, complexity, and team ownership.

## Failure modes

A team creates 80 one-line use cases, each forwarding to a repository, then hides the real multi-step transaction policy in a ViewModel. The diagram looks layered but responsibilities remain wrong. Move actual policy first.

## Production perspective

A retail app begins with UI/data layers. As discounts and eligibility span cart, checkout and profile, it extracts focused use cases with tests and domain outcomes while keeping simple product reads direct.

## Interview answer — short

A separate domain layer is useful for complex or reused business logic; Android treats it as optional. I add use cases when they reduce duplicated rules or large ViewModels, not as mandatory wrappers around every repository method.

## Interview answer — structured

I would ask whether the business behavior has its own tests, is reused by multiple screens, or coordinates several repositories. If yes, a use case can make that policy explicit and keep ViewModels focused on UI state. If a small screen just reads one repository stream, a pass-through use case adds files without reducing coupling. Android guidance explicitly calls the domain layer optional, so I would start with clear UI and data boundaries and extract domain behavior when evidence appears. A good extraction point is when two ViewModels duplicate the same eligibility rule or one screen coordinates multiple repositories with many branches. I would move that cohesive behavior into a use case and test it directly, while leaving simple data observation alone.

## Interview answer — deep senior

The decision should be incremental. A domain layer earns its place when policies change independently of rendering and storage, when multiple ViewModels duplicate logic, or when a workflow needs focused tests. It should not become a dumping ground for arbitrary helpers. I look for cohesive actions—calculate eligibility, submit a transfer, combine subscriptions—and keep each use case narrow. A direct ViewModel-to-repository dependency can be entirely reasonable for simple data presentation. I still maintain a data boundary so DTOs and persistence details do not leak into the screen. If complexity grows, extraction is possible without rewriting every UI call. The trade-off is real: more types, mappings, and build graph edges versus clearer ownership and testing. The optionality is a strength, not a compromise. A use case has a cost in navigation, DI wiring and API design. I want it to expose a meaningful action and stable result, not merely repeat the repository name. If the app later adds another feature, I can extract shared policy behind a clear contract. That is easier when the repository already hides DTOs and database entities. I review complexity periodically instead of committing to a permanent three-layer template on day one.

## How to answer in the interview

- **Why:** abstractions should protect real policy.
- **How:** extract when rules or reuse justify.
- **Trade-off:** test seam versus extra indirection.
- **Failure case:** many one-line use cases obscure flow.
- **Production solution:** evolve by concrete coupling signals.

## Deep-dive talking points

Contrast a one-screen read with a multi-feature eligibility rule; discuss extraction timing and Android optionality.

## Follow-up questions

- [ARC-04](../arc-04/): What distinguishes a useful use case? **Answer:** it owns meaningful business action or reuse, not a trivial forwarder.
- [ARC-23](../arc-23/): When is Clean Architecture overengineering? **Answer:** when layer cost exceeds change/test benefit in a small app.

## Self-check rubric

Give two concrete triggers for a domain layer and one case where you would omit it.

## References and reviewed-on date

- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — optionality and reasons to add use cases.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
