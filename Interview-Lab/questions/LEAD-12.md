---
id: "LEAD-12"
question: "Tell me about a production incident you owned and how you prevented recurrence."
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "C"
phase: 5
priority: "P2"
order: 467
editorial_status: "reviewed"
---

# LEAD-12

## Original interview question

Tell me about a production incident you owned and how you prevented recurrence.

## What the interviewer evaluates

- Honest STAR-style incident story with personal ownership and evidence.
- No invented experience presented as fact.

## Explanation in Arabic

السؤال behavioral؛ لازم المرشح يحكي حادثة حقيقية من خبرته، مش ينسب لنفسه قصة متخيلة. نرتب Situation، Task، Actions، Result، Learning: impact بالأرقام لو متاح، قرار تحت ضغط، التعاون، ما الذي تغير في system. لو ما حصلتش production incident، قول ده بوضوح واستخدم near miss أو incident شاركت فيه مع توضيح دورك.

## Why it matters and how it works

Interviewers evaluate judgment, accountability, communication and learning. A strong answer separates personal action from team action, quantifies what was observed and states unresolved limitations. A blameless postmortem focuses systemic fixes.

## Worked example

Illustrative scenario only: release flavor pointed to staging backend, detected in 1% rollout. Candidate might describe halting rollout, assessing installed users, coordinating backend mitigation, shipping corrected AAB and adding artifact checks. Replace this with a truthful personal incident and real metrics.

## Trade-offs and decision criteria

A dramatic story is less valuable than accurate ownership. Avoid claiming sole credit for a team response, or inventing numbers. If details are confidential, anonymize safely while retaining engineering decisions.

## Failure modes

“We fixed it” with no personal decision or prevention is weak. So is blaming one developer. Explain what evidence changed your decision and how corrective action was verified.

## Production perspective

Prepare one real incident timeline, artifacts/metrics you can discuss, and a short reflection on what you would do differently. Confirm no sensitive user/card data enters the interview story.

## Interview answer — short

“I would describe a real incident with impact, my specific role, mitigation, measured outcome and a verified prevention change. I would be explicit about team contributions and unknowns.”

## Interview answer — structured

“I use a truthful STAR structure. First I state the incident and customer impact, then my responsibility. I explain the evidence I gathered, the mitigation decision, who I coordinated with, and how we confirmed recovery. Finally I describe a systemic follow-up—such as a new release gate or reconciliation alert—and how it was tested. I avoid blaming an individual or claiming I owned work I did not do. If I only participated, I say so clearly and focus on the decisions I actually made. The mechanics matter. Interviewers evaluate judgment, accountability, communication and learning. A strong answer separates personal action from team action, quantifies what was observed and states unresolved limitations. A blameless postmortem focuses systemic fixes.”

## Interview answer — deep senior

“I would choose an incident I can substantiate with a timeline and results. A strong narrative covers detection signal, immediate risk assessment, safe containment, communication cadence, technical diagnosis and trade-offs under time pressure. For a payment issue, I would distinguish stopping new attempts from preserving status lookup and reversals, and I would not declare success until unknown transactions were reconciled. I would state which action I personally took versus what backend, QA and operations did, quantify impact only from recorded data, and close with a blameless postmortem action that was verified by a drill or test. If no production incident fits, I would transparently use a near miss rather than invent ownership. Consider a concrete case. Illustrative scenario only: release flavor pointed to staging backend, detected in 1% rollout. Candidate might describe halting rollout, assessing installed users, coordinating backend mitigation, shipping corrected AAB and adding artifact checks. Replace this with a truthful personal incident and real metrics. A failure case illustrates the risk. “We fixed it” with no personal decision or prevention is weak. So is blaming one developer. Explain what evidence changed your decision and how corrective action was verified.”

## Deep-dive talking points

Prompt for real event, personal role, evidence, mitigation, result and verified prevention.

## Follow-up questions

- [LEAD-09](../lead-09/): What makes follow-up credible? **Answer:** owner, test and recurrence metric in postmortem.
- [CIC-14](../cic-14/): What does stopping rollout achieve? **Answer:** limits new installs but not existing impact.

## Self-check rubric

Can you state the context, decision evidence, alternatives, affected people, measurable result and both follow-up answers?

## References and reviewed-on date

- [Google SRE postmortem culture](https://sre.google/workbook/postmortem-culture/) — incident learning.
- [Android app quality](https://developer.android.com/quality) — impact metrics.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
