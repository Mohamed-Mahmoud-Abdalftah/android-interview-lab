---
id: "LEAD-04"
question: "How do you estimate an unfamiliar feature and communicate risk?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "A"
phase: 5
priority: "P2"
order: 459
editorial_status: "reviewed"
---

# LEAD-04

## Original interview question

How do you estimate an unfamiliar feature and communicate risk?

## What the interviewer evaluates

- Estimates as ranges with assumptions and risk.
- Spike, decomposition and communication of uncertainty.

## Explanation in Arabic

ميزة غير مألوفة ما تتقدرش برقم دقيق من أول دقيقة. نفصل discovery، API/backend contract، Android UI/state، security، tests، rollout. نحدد assumptions والمجهول الكبير ونقترح spike قصير لخفض uncertainty. نعطي range وثقة وتواريخ checkpoints، ونحدّث estimate لما نتعلم. ما نخلطش estimate بالتزام ثابت من غير scope.

### Practical walkthrough in Egyptian Arabic

لو feature مجهولة مثل offline checkout، لا تقول “أسبوعين” من UI mockup. فكّك unknowns: backend contract، payment status، Room migration، SDK device، auth، QA matrix وPlay release. اعمل spike قصير للجزء الأعلى مخاطرة، وقدم range مع assumptions ومراحل evidence. عرف ما الذي يمكن قصّه من scope وما الذي لا يمكن قصّه مثل idempotency. بلّغ المخاطر بدري وحدث التقدير عند ظهور نتيجة الـspike بدل الدفاع عن رقم أولي.

## Why it matters and how it works

Estimation is a forecast conditional on scope, dependencies and team capacity. Separate known work from unknown integration risk. A spike should answer a specific technical question and produce evidence, not become hidden feature implementation.

## Worked example

New EMV reader integration: estimate vendor SDK evaluation, firmware matrix, backend intent/reversal contract, UI, certification and test devices separately. State that provider sandbox access and hardware availability are critical path assumptions.

## Trade-offs and decision criteria

Wide range is honest but less useful for planning; narrowing it requires discovery. A fixed-date release may require reducing scope while keeping financial safety gates. Share options and consequences.

## Failure modes

Promising two weeks based only on UI screens ignores device certification and unknown timeout recovery. Track risk register and revise forecast after first hardware proof.

## Production perspective

Weekly update shows completed evidence, remaining uncertainties, current range and decisions needed from backend/vendor. Escalate dependency slips early with impact on critical path.

## Interview answer — short

“I decompose the work, state assumptions and unknowns, run a focused spike for the riskiest dependency, and communicate a range with checkpoints rather than false precision.”

## Interview answer — structured

“For an unfamiliar feature I identify outcome and constraints, split mobile, backend, security, testing and rollout tasks, then estimate known pieces separately from uncertain integrations. I give a range and confidence level tied to assumptions such as SDK access or API readiness. A short spike answers the highest-risk question; after it, I update the range and show what changed. If the deadline is fixed, I discuss scope options while preserving safety requirements. Share options and consequences.”

## Interview answer — deep senior

“For unfamiliar work I estimate the uncertainty, not only the visible UI. I break the feature into contracts, Android state ownership, persistence, external SDK behavior, tests and release verification. An offline checkout estimate, for example, depends on whether the backend already supports durable idempotent operation IDs and status lookup; if that is unknown, I time-box a spike with backend and QA before promising a fixed date. I provide a range, the assumptions behind it, a likely critical path and a checkpoint when I will re-estimate. I distinguish scope that can be deferred, such as polish, from safety requirements that cannot, such as preventing duplicate charges. I communicate evidence and choices to product in plain language: what can ship, what risk remains and what additional work changes confidence. The trade-off is spending early time reducing uncertainty versus moving immediately. False precision creates a larger schedule surprise than an honest range with a validation plan.”

## How to answer in the interview

- **Why:** unknown dependencies make point estimates misleading.
- **How:** decompose work, spike risk, give range.
- **Trade-off:** early discovery time versus schedule confidence.
- **Failure case:** backend idempotency assumed but absent.
- **Production solution:** re-estimate at evidence checkpoints.

## Deep-dive talking points

Prompt for conditional range, dependency map, focused spike, safety floor and update cadence.

## Follow-up questions

- [LEAD-07](../lead-07/): Who owns API uncertainty? **Answer:** mobile/backend/QA agree a contract and test it.
- [LEAD-13](../lead-13/): What if launch date conflicts with security? **Answer:** escalate risk and choose safe scope or delay.

## Self-check rubric

Break the unknown feature into discovery, dependencies and implementation slices; give a range with assumptions, name the top risk and report what evidence would narrow the estimate.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — layer/task decomposition.
- [Android testing overview](https://developer.android.com/training/testing) — verification scope.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
