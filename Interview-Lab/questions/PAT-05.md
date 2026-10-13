---
id: "PAT-05"
question: "Explain Observer, Strategy, State, Command, and Chain of Responsibility."
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 196
editorial_status: "reviewed"
---

# PAT-05

## Original interview question

Explain Observer, Strategy, State, Command, and Chain of Responsibility.

## What the interviewer evaluates

Contrast notification, interchangeable algorithm, state-dependent behavior, action object and handler pipeline.

## Explanation in Arabic

Observer ينشر changes لمتابعين (Flow/LiveData شبهه بس lifecycle/backpressure semantics مهمة). Strategy يبدّل algorithm مستقل زي payment provider. State يغيّر سلوك object حسب حالته الحالية، وغالبًا transitions جزء من التصميم. Command يحوّل action لobject/data يمكن queue أو log أو undo حسب النظام. Chain of Responsibility يمرّر request على handlers بترتيب محدد لحد ما واحد يعالجها. الأسماء ما تعنيش إن network effect هيبقى exactly-once؛ command queue تحتاج persistence/idempotency لو مهم.

## Why it matters and how it works

Behavioral patterns organize communication and decision-making. Strategy varies policy selection; State varies behavior based on current state; Observer delivers updates; Command represents requests; a chain composes ordered handlers.

## Worked example

Example: checkout observes order Flow, chooses provider Strategy, transitions through `Pending/Confirmed` State, represents `SubmitPayment(requestId)` as a Command for durable handling, and validates request through an ordered chain of handlers. Each layer has explicit ownership and error semantics.

## Practical walkthrough

Observer معناه subscribers بتشوف state changes؛ `StateFlow` مثال، لكن lifecycle-aware collection لازمة للUI. Strategy تبدّل algorithm/provider وراء interface ثابتة. State تمثل الحالة الحالية وتقيّد actions/transition؛ enum booleans مش كفاية لو كل حالة لها payload مختلف. Command يمثل intent قابل للتخزين/retry مثل `SubmitPayment(attemptId)`، لكن لازم idempotency. Chain of Responsibility تمرر request عبر handlers مثل validation→auth→policy، بس ترتيبها مهم وممكن يخفي مين رفض. في checkout، ما تستخدمش الخمس patterns في نفس call stack لمجرد استعراضها؛ كل واحد لازم يحل مشكلة محددة وله test.

## Trade-offs and decision criteria

Patterns can clarify complex flows but add objects and indirection. A simple lambda may be enough for one strategy; a `when` may be enough for a small state machine. A chain can hide ordering and early-exit behavior if overused.

## Failure modes

A one-shot payment Command sits only in memory and is lost on process death; use persisted work plus server reconciliation. A Flow observer without lifecycle-aware collection can leak or do unnecessary work.

## Production perspective

A bank transfer flow uses explicit state transitions and persistent request IDs; UI observes status via a repository stream. Provider selection and validation handlers are tested independently.

## Interview answer — short

Observer distributes updates; Strategy selects interchangeable behavior; State models behavior tied to current state; Command represents an action; Chain of Responsibility passes a request through handlers. I choose by the actual variation and delivery needs.

## Interview answer — structured

I distinguish these by the question they answer. Who needs updates? Observer. Which algorithm or provider should run? Strategy. How does behavior change after a transition? State. Should an action be represented and possibly queued? Command. Should several handlers get a chance in order? Chain of Responsibility. In Android, Flow can carry updates, but lifecycle and buffering matter. A queued payment command needs persistence and idempotency; the pattern name alone does not provide durable execution.

## Interview answer — deep senior

A checkout feature can combine several behavioral patterns without putting everything into one “manager.” Repository status is observed by the UI; a provider strategy selects one SDK adapter; a state machine decides which transitions are legal; a command records a user action; a validation chain applies ordered checks. I keep their contracts distinct. Strategy implementations should be substitutable, while State concerns history and current transition rules. Observers may miss or replay values depending on the chosen stream, so I classify data as current state or durable event. A command placed in an in-memory queue can vanish with the process, and a chain whose order is implicit can reject the wrong request. I test failure propagation, cancellation and server authority, not just the happy path.

I would separate event observation from decision and execution. Observer lets a screen react to repository state, for example through a lifecycle-collected StateFlow. Strategy chooses one provider behavior behind a stable contract. State models where checkout is now and which transitions are legal; a sealed state can carry different payloads. Command represents a durable intent such as SubmitPayment with an attempt ID, which can be queued but still needs server idempotency. Chain of Responsibility can pass a request through validation, authentication, and policy handlers, though ordering and short-circuit behavior must be explicit. For a simple flow I might need only one or two of these. The test is whether the pattern localizes variation or clarifies failure, not whether the diagram includes every name.

## How to answer in the interview

- **Why:** These patterns address observation, variation, transitions, intent and handler order.
- **How:** Walk one checkout request through only the roles it actually needs.
- **Trade-off:** Prefer direct code when a chain or command queue adds no value.
- **Failure case:** Hidden handler order or replayed non-idempotent command.
- **Production solution:** Test state transitions, observer lifecycle and queued-operation identity.

## Deep-dive talking points

Compare Strategy/State, observer delivery, command persistence and chain ordering.

## Follow-up questions

- [PAT-09](../pat-09/): Strategy versus State? **Answer:** algorithm variation versus current-state-dependent behavior and transitions.
- [PAT-13](../pat-13/): What does lifecycle add to Observer? **Answer:** collection/registration must stop with the UI owner.

## Self-check rubric

Match five scenarios to patterns and identify one durability or lifecycle limitation.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — behavioral patterns.
- [Android LiveData overview](https://developer.android.com/topic/libraries/architecture/livedata) — lifecycle-aware Observer example.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
