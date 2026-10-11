---
id: "SOL-20"
question: "How would you explain SOLID trade-offs to a team overengineering a small feature?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "C"
phase: 2
priority: "P1"
order: 191
editorial_status: "reviewed"
---

# SOL-20

## Original interview question

How would you explain SOLID trade-offs to a team overengineering a small feature?

## What the interviewer evaluates

Communicate practical trade-offs to a team and propose a small, evidence-based design.

## Explanation in Arabic

لما فريق صغير feature بيعمل خمس interfaces، ثلاث layers، وfactory لكل button، اشرح تكلفة التنقل والـwiring والاختبارات الوهمية. SOLID أسئلة مراجعة: إيه سبب التغيير؟ مين client؟ هل في implementation تانية؟ هل substitution contract واضح؟ اقترح minimal design: ViewModel للحالة، Repository للداتا، domain/use case فقط لو rule معقدة أو reused. احتفظ بتجربة صغيرة واختبر behavior. لو requirement جديد بدأ يلمس 10 ملفات أو fakes فيها unimplemented throwing stubs, استخرج abstraction وقتها. ما تستخدمش “clean” كحجة ضد تسليم feature صحيح.

## Why it matters and how it works

Principles help when they lower change and defect cost. Overengineering spends complexity before variation exists. A team can choose simple concrete code while preserving safe data/UI boundaries and a clear path to extract later.

## Worked example

Team discussion: show two diagrams for a small settings screen. Option A has `SettingsViewModel -> SettingsRepository` with a concrete formatter; option B adds one use case and interface per getter. Ask which independent change B protects. Keep A if no answer, and add a test for save/error behavior.

## Trade-offs and decision criteria

A lean design can defer useful abstraction until a second implementation or duplicated rule appears. Excessive simplicity can become direct SDK calls in UI, so keep core lifecycle, data and error ownership even in small work.

## Failure modes

A feature takes longer to wire than implement, and a tiny API rename forces changes across three model layers with no semantic difference. Reduce ceremonial types. Conversely, if a new payment provider touches every screen, add a real strategy boundary.

## Production perspective

A team agrees on a review checklist and revisits architecture after two iterations. They measure changed files, build time and test pain, while preserving server-side payment authority and Android lifecycle correctness.

## Interview answer — short

I present SOLID as change-control heuristics, then ask which real variation each abstraction protects. For a small feature I keep clear UI/data ownership and concrete helpers; I add contracts when change or test evidence justifies them.

## Interview answer — structured

I would avoid framing the discussion as “clean versus messy.” I would show the actual cost: files, DI bindings, navigation and test fakes for a small settings screen. Then ask what changes independently and whether an interface protects a consumer from that change. A ViewModel plus repository may be enough. I would still keep network details out of UI and handle lifecycle correctly. If duplicated business rules or provider variation appear, we can extract a focused use case or strategy with tests. I would propose a concrete review question for each new interface: which caller needs to stay independent of which implementation? If nobody can answer, keep the helper concrete for now. I would also set a trigger to revisit, such as a second provider or duplicated rule across screens.

## Interview answer — deep senior

I explain each principle as a way to reduce a specific cost, not a checklist that every class must satisfy visibly. SRP helps when different stakeholders change one module; ISP helps when clients depend on unused methods; DIP/OCP help when volatile adapters repeatedly force policy edits; LSP protects substitutions. For a small feature, adding all possible interfaces can increase the very coupling we hoped to avoid. I propose the smallest clear architecture, document the likely extension point, and add behavior tests. Then I revisit with evidence from real changes: how many unrelated files are touched, how many mocks have empty methods, how difficult is it to replace a provider? I also keep non-negotiable correctness boundaries—main safety, lifecycle, source of truth and server authority—regardless of abstraction count. The discussion should be about cost and risk, not taste. I would show how many files, bindings and mocks Option B adds, and what class of change it actually isolates. I would keep the safeguards that matter regardless of architecture style: network work off Main where necessary, lifecycle ownership, typed errors, source of truth, and backend authority for sensitive actions. Then I would use pull-request history and tests to reassess. If an apparently simple repository grows several independent responsibilities, extraction becomes justified. If the small feature remains stable, the lean design was the better choice.

## Deep-dive talking points

Present a concrete two-option design review, count protected change axes and identify a future extraction trigger.

## Follow-up questions

- [SOL-13](../sol-13/): Why not an interface for every class? **Answer:** it adds cost without necessarily protecting a consumer.
- [ARC-23](../arc-23/): When is layered architecture too much? **Answer:** when added ceremony exceeds isolation benefit for the actual app.

## Self-check rubric

Explain a minimal settings design, one risk of overengineering, one risk of underengineering, and a revisit trigger.

## References and reviewed-on date

- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — adaptable guidance.
- [Robert C. Martin, SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — change ownership.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
