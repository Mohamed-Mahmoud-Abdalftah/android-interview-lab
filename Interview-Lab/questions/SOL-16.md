---
id: "SOL-16"
question: "How do you identify cohesive responsibilities within a God Class?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 187
editorial_status: "reviewed"
---

# SOL-16

## Original interview question

How do you identify cohesive responsibilities within a God Class?

## What the interviewer evaluates

Diagnose God Class responsibilities using change history, clients, data flow and safe extraction.

## Explanation in Arabic

God Class غالبًا بقت مسؤولة عن UI events، API، cache، pricing، analytics. ما تقسّمهاش حسب عدد الأسطر بس؛ اعمل change-history وcall-site map: أي أجزاء بتتغير مع بعض ولأي سبب؟ شوف dependencies وstate ownership: networking وRoom للdata، policy مشتركة للدومين، UI projection للViewModel. اكتب characterization tests للحالات المهمة، ثم استخرج coherent slice واحدة كل مرة، وحافظ على cancellation/error semantics. لو helper يستخدم mutable shared state، افصل ownership قبل نقله.

## Why it matters and how it works

Cohesion is about related change pressure and invariants. A large class can be coherent; a small class can still mix unrelated reasons. Safe extraction requires understanding state, side effects and caller contracts.

## Worked example

Refactor plan for `CheckoutManager`: (1) test submit/timeout/duplicate tap; (2) move provider SDK mapping to adapter; (3) move eligibility into a policy component; (4) keep UI state transition in ViewModel; (5) move durable request tracking to repository. Measure changed-file locality afterward.

## Practical walkthrough

افتح `CheckoutManager` وشوف change history بدل عدّ الأسطر. لو تعديل provider SDK، eligibility policy، UI loading، وتخزين request ID كلهم بيعدّلوا نفس class، دي أسباب تغيير مختلفة. حدد invariants قبل النقل: no duplicate submission، timeout نتيجته unknown، وserver status هو النهائي. انقل SDK mapping إلى adapter، policy إلى component قابل للاختبار، UI state إلى ViewModel، وtracking durable إلى repository. بعد كل خطوة شغّل behavior tests عشان ما تضيعش ترتيب الأحداث. لو فُصلت functions بس ولسه كل class عارفة تفاصيل التانية، المشكلة ما اتحلتش.

## Trade-offs and decision criteria

Incremental extraction temporarily leaves adapters and duplicate paths but lowers risk. A big-bang rewrite may be faster on paper yet miss hidden behavior. Avoid microscopic classes that split one invariant across too many owners.

## Failure modes

A team moves `calculateFee()` to `FeeUseCase` but leaves mutable cart state in God Class, so the new method still reaches back into shared fields. Pass explicit inputs and define ownership. Test concurrent/timeout behavior before changing flow.

## Production perspective

A commerce team uses production incident history to prioritize extracting payment SDK code from a 1,200-line coordinator. They monitor decline/timeout metrics during rollout and keep rollback available.

## Interview answer — short

I identify responsibilities by reasons to change and shared invariants, not line count. I capture behavior, extract one coherent slice at a time, and preserve state ownership, cancellation and error semantics.

## Interview answer — structured

I inspect recent edits, callers and mutable fields to see which responsibilities actually move together. A God Class might contain UI state, provider SDK mapping, business eligibility and cache policy, each with a different owner. I add characterization tests for important flows, then extract one seam at a time, starting with the most volatile or risky. I avoid merely moving helper methods that still depend on the old class’s mutable state. The goal is independent change and reliable behavior, not a cosmetic reduction in line count. For example, if network mapping moves out but still reads a mutable field inside the old manager, the responsibility has not really moved. I would pass explicit inputs and create one owner for shared state before calling the refactor complete.

## Interview answer — deep senior

A useful decomposition starts with data flow and invariants. I draw how a user action reaches network, persistence and UI state, and identify which fields are shared across those paths. Change history reveals separate actors: design, server schema, pricing and compliance. I put SDK translation in data, reusable policy in a focused component, and screen state in a ViewModel, but I do not scatter a cohesive transaction invariant across many classes. Before each move I write behavior tests for success, failure, cancellation, duplicate taps and process death where applicable. Afterward I inspect module dependencies and whether a new requirement changes fewer unrelated files. I use staged rollout and telemetry for high-risk payment changes. I look for clusters of changes and invariants rather than simply labeling a long class bad. In a checkout manager, provider mapping, eligibility, UI state transitions, and durable request tracking have different change actors. I would capture behavior tests for duplicate taps, timeout, and recovery, then extract one cluster at a time. The adapter handles SDK translation, the policy owns eligibility, the ViewModel exposes screen state, and a repository tracks durable request IDs. The risk is a cosmetic split where the new classes call each other in a cycle and still change together. I would review dependency direction and future changed-file locality, not just class length.

## How to answer in the interview

- **Why:** Use change history and invariants.
- **How:** describe extraction order.
- **Trade-offs:** mention temporary migration cost.
- **Failure cases:** flag cyclic cosmetic split.
- **Production solutions:** close with behavior tests and change-locality evidence..

## Deep-dive talking points

Use change history, state-field map, call graph and characterization tests to find cohesive slices.

## Follow-up questions

- [SOL-02](../sol-02/): What defines responsibility? **Answer:** a coherent reason/actor for change, not one method.
- [ARC-21](../arc-21/): How refactor a 1,000-line ViewModel? **Answer:** characterize behavior and extract data/policy seams incrementally.

## Self-check rubric

Identify three change actors and one shared invariant in a God Class; propose a first safe extraction.

## References and reviewed-on date

- [Robert C. Martin, SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — reasons to change.
- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
