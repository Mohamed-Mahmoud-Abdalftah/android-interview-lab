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

## Practical walkthrough

السؤال شخصي: اختار حادثة حصلت فعلًا، ووضح دورك من غير ما تنسب لنفسك شغل الفريق. استخدم STAR مع timestamps وأثر معروف، ثم لماذا قررت halt rollout أو feature flag أو hotfix. لو مثال payment، فرّق وقف محاولات جديدة عن متابعة unknown/reversal الموجودة. اختم بإصلاح systemic له owner واختبار، واذكر ما لا تعرفه أو ما كان ممكن تعمله أفضل. لو ما عندكش incident حقيقي، قل ده واستخدم near miss بشفافية.

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

“I use a truthful STAR structure. First I state the incident and customer impact, then my responsibility. I explain the evidence I gathered, the mitigation decision, who I coordinated with, and how we confirmed recovery. Finally I describe a systemic follow-up—such as a new release gate or reconciliation alert—and how it was tested. I avoid blaming an individual or claiming I owned work I did not do. If I only participated, I say so clearly and focus on the decisions I actually made. A blameless postmortem focuses systemic fixes.”

## Interview answer — deep senior

“I would answer with a real incident I can substantiate, not an invented success story. I would state the user impact and my specific responsibility, then walk through detection, the evidence available at each decision point, containment, communication and confirmation of recovery. If the incident involved a payment path, I would explain how we stopped new attempts while keeping reconciliation for in-flight unknown outcomes, because turning off a screen is not financial recovery. I would distinguish my action from what backend, QA and operations owned, and use only measured numbers I can defend. Then I would describe a systemic follow-up—such as a release artifact check or lost-response test—with an owner and evidence that it now catches the failure. I would also say what I would change about my own response. If I have only supported an incident or a near miss, I would say that plainly and focus on my actual decisions. The interviewer is evaluating judgment and accountability, not the drama of the story.”

## How to answer in the interview

- **Why:** real ownership demonstrates judgment.
- **How:** tell truthful impact, decisions, result and learning.
- **Trade-off:** brevity versus enough evidence.
- **Failure case:** invented metrics or blaming one person.
- **Production solution:** verified prevention and honest personal role.

## Deep-dive talking points

Prompt for real event, personal role, evidence, mitigation, result and verified prevention.

## Follow-up questions

- [LEAD-09](../lead-09/): What makes follow-up credible? **Answer:** owner, test and recurrence metric in postmortem.
- [CIC-14](../cic-14/): What does stopping rollout achieve? **Answer:** limits new installs but not existing impact.

## Self-check rubric

Tell a real incident as timeline, impact, your decision, mitigation and prevention. Name one measurable result and clearly distinguish your contribution from the wider team.

## References and reviewed-on date

- [Google SRE postmortem culture](https://sre.google/workbook/postmortem-culture/) — incident learning.
- [Android app quality](https://developer.android.com/quality) — impact metrics.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
