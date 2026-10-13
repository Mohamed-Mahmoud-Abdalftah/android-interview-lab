---
id: "ARC-23"
question: "You have a very small app. When is Clean Architecture overengineering?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "C"
phase: 2
priority: "P1"
order: 168
editorial_status: "reviewed"
---

# ARC-23

## Original interview question

You have a very small app. When is Clean Architecture overengineering?

## What the interviewer evaluates

Balance architecture benefit against complexity for a small app, preserving clear boundaries without ceremony.

## Explanation in Arabic

تطبيق صغير بشاشة أو اتنين وAPI واحدة ممكن يشتغل كويس بـViewModel + Repository واضحة من غير domain module، DTO/domain/UI copies متطابقة، أو interface لكل class. Clean Architecture تصبح overengineering لما وقت التنقل بين طبقات واختبارات forwarding أكبر من خطر التغيير الفعلي. لكن “صغير” مش مبرر تحط Retrofit في Compose أو تخبّي secret في APK؛ احتفظ بحدود data وUI وبـmain safety، واستخرج domain لما rules تتكرر أو workflow يعقد.

### Practical walkthrough in Egyptian Arabic

App صغيرة: لو screen واحدة وrepository بسيطة، 5 modules وinterface لكل class قد تضيف navigation cost أكبر من فائدتها. استخدم State owner واضح، repository إذا فيه data policy، واختبارات للrisks الفعلية. لما rules تتكرر أو SDK تتبدل، extract domain boundary تدريجيًا. Clean Architecture مبدأ dependency/ownership، مش عدد مجلدات ثابت.

## Why it matters and how it works

Architecture has maintenance cost. Android guidance calls the domain layer optional. The smallest structure that clearly owns state, data, and failure behavior may be best until independent change pressure appears.

## Worked example

Example: a two-screen conference schedule app has `ScheduleRepository` reading one API and `ScheduleViewModel` producing UI state. It does not need `GetScheduleUseCase` if that class only delegates. When offline saved sessions and cross-screen registration rules arrive, focused domain behavior may become valuable.

## Trade-offs and decision criteria

Less layering speeds initial work but can accumulate coupling if types and ownership are unclear. More layering aids isolated change when complexity is real, but costs boilerplate and build graph maintenance. Favor reversible decisions.

## Failure modes

A team creates five modules and 20 interfaces for a static brochure app, then spends more time wiring than shipping. The opposite failure is directly parsing HTTP responses in UI and having no place for error or cache policy. Keep a meaningful repository seam.

## Production perspective

A small internal tool starts with UI/data and tests. As features grow, team extracts reuse and policies into domain without changing the whole app at once. Decisions are revisited based on actual change patterns.

## Interview answer — short

Clean Architecture is overengineering when layers and interfaces add more maintenance than isolation for a small app. I keep a clear UI/data boundary and add domain abstractions only when business complexity or reuse appears.

## Interview answer — structured

For a tiny app, I would begin with a ViewModel and a repository with clear data and error contracts. Android itself treats the domain layer as optional. A use case that only forwards one repository call and duplicate models with identical semantics may not earn their cost. I still keep networking out of Compose, preserve main safety, and test real behavior. If multiple screens start duplicating eligibility or sync rules, I can extract focused domain policy then. I would still keep one repository contract so the UI does not parse HTTP in every screen, and use a ViewModel for screen state. That is a minimal design, not a violation of architecture. As the app grows, I extract rules only when multiple callers or complex transitions justify them.

## Interview answer — deep senior

I look for actual forces: independently changing data sources, shared rules, multiple teams, complex state transitions, or offline consistency. Without them, full Clean Architecture machinery can be more expensive than the problem. A small app can maintain a strong UI/data split and one repository, with domain logic inside a focused place until it deserves extraction. I avoid premature interfaces and one-to-one mappers that only rename fields. At the same time, simplicity is not permission to leak DTOs into every UI or ignore lifecycle and cancellation. I make decisions reversible, write a few behavior tests, and review the architecture when change starts scattering edits across unrelated screens. The measure is local, safe change, not adherence to a diagram. I would revisit the design using evidence: how many files change for one feature, how much business logic is duplicated, and whether tests require booting Android just to check policy. When those costs appear, a focused domain layer or module boundary can pay off. Before then, dozens of empty interfaces and one-line use cases can make the app harder to understand. Simplicity remains bounded by correctness: blocking work, secrets, lifecycle, and source-of-truth decisions still need proper owners even in a two-screen app.

## How to answer in the interview

- **Why:** small systems still need clear ownership.
- **How:** start minimal and extract on pressure.
- **Trade-off:** future flexibility versus present complexity.
- **Failure case:** boilerplate hides simple flow.
- **Production solution:** evolve boundaries from measured change pain.

## Deep-dive talking points

Compare a tiny read-only app with a growing offline workflow; identify measurable triggers for extraction.

## Follow-up questions

- [ARC-13](../arc-13/): When add domain? **Answer:** reused or complex business behavior justifies it.
- [ARC-15](../arc-15/): Must every class have an interface? **Answer:** no; create one at a meaningful variation or boundary.

## Self-check rubric

Describe a minimal two-layer design, two premature abstractions, and a signal that would justify adding domain.

## References and reviewed-on date

- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — optionality.
- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — flexible guidance.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
