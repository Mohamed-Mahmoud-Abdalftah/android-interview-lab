---
id: "LEAD-09"
question: "How do you run an incident postmortem without blame?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "B"
phase: 5
priority: "P2"
order: 464
editorial_status: "reviewed"
---

# LEAD-09

## Original interview question

How do you run an incident postmortem without blame?

## What the interviewer evaluates

- Blameless incident analysis with factual timeline and corrective actions.
- Accountability without individual blame.

## Explanation in Arabic

Postmortem بدون لوم مش معناه مفيش مسؤولية؛ معناه نفهم system سمح إزاي بالخطأ ونصلح controls. نجمع timeline factual من logs وقرارات، impact، detection، mitigation، root/contributing factors، what worked، actions بowners/dates وverification. نتجنب “المهندس نسي” كسبب وحيد؛ نسأل ليه CI/review/rollout ما كشفوش.

## Practical walkthrough

بعد incident، ما تكتبش “فلان نسي check”. اعمل timeline بالأدلة: أول symptom، detection، mitigation، recovery، ومتى اتأكدنا إن المستخدمين رجعوا طبيعي. اسأل لماذا النظام سمح للخطأ بالمرور: gate ناقصة؟ metric متأخرة؟ ownership غامض؟ لكل action حدد owner وموعد واختبار أو alert يثبت الإصلاح. شارك impact بصدق ومن غير بيانات حساسة، وراجع action بعد فترة بدل إغلاق المستند فور الاجتماع.

## Why it matters and how it works

A blameless review encourages accurate reporting of near misses and context. Separate triggering event from systemic contributors. Corrective actions need measurable completion and validation; “be more careful” is weak.

## Worked example

After wrong flavor release, timeline shows artifact selection wildcard, missing package assertion and rollout detection delay. Actions: exact artifact path, pre-upload applicationId/host gate, canary wrong-flavor test and rollout metric. Owner verifies gate by deliberately swapping variant in test.

## Trade-offs and decision criteria

Open discussion improves learning but sensitive personnel or security details may require restricted handling. A short incident review may suffice for low impact; major financial impact needs deeper cross-team analysis.

## Failure modes

A postmortem lists “developer selected wrong flavor” and no system changes, so recurrence remains possible. Or creates 20 action items nobody owns. Prioritize a few controls with due dates and evidence.

## Production perspective

Share sanitized lessons across mobile/backend/QA/security, track action closure and rerun incident drill. Measure time to detect, mitigate and recover, plus recurrence.

## Interview answer — short

“I write a factual timeline and impact, identify system conditions, and assign verifiable corrective actions. Blameless means learning without hiding accountability.”

## Interview answer — structured

“During an incident I focus on customer mitigation first. Afterward I reconstruct a timeline from evidence, separate trigger from contributing conditions, and ask why detection and safeguards failed. For a wrong-flavor release, the fix is not just telling someone to be careful; it is an artifact assertion and canary test. Actions have owners, dates and verification, and I share lessons without naming or shaming individuals. Separate triggering event from systemic contributors. ”

## Interview answer — deep senior

“I run a postmortem to improve the system, not to assign personal blame. I start with an evidence-based timeline: first signal, customer impact, decisions, mitigation and confirmation of recovery. I separate facts from hypotheses and ask which conditions allowed the issue to reach users—perhaps a release manifest check was missing, a payment unknown-state metric was invisible, or responsibility for rollback was unclear. The action list has owners, deadlines and verification: a CI assertion, a chaos test for lost responses, or an alert with a measured threshold. I include what worked so the team preserves useful controls. Blameless does not mean no accountability; it means people can describe the truth without defensive editing while leaders own follow-through. I avoid exposing customer or payment data in the document. A weak postmortem ends with ‘be more careful’; a strong one changes a control and later confirms that it catches the same failure.”

## How to answer in the interview

- **Why:** incidents reveal system gaps.
- **How:** timeline facts, causes, actions and owners.
- **Trade-off:** open learning versus accountability.
- **Failure case:** action says only “be careful”.
- **Production solution:** verify a new gate or drill and review recurrence.

## Deep-dive talking points

Prompt for trigger versus contributors, factual timeline, action verification, customer mitigation and data minimization.

## Follow-up questions

- [CIC-19](../cic-19/): What systemic gate prevents wrong flavor? **Answer:** assert built artifact tuple before upload.
- [LEAD-08](../lead-08/): How measure improvement? **Answer:** recurrence, detection and recovery metrics.

## Self-check rubric

Build a timeline from evidence, separate contributing system conditions from individual blame, assign corrective actions with owners and dates, and verify recurrence signals.

## References and reviewed-on date

- [Google SRE postmortem culture](https://sre.google/workbook/postmortem-culture/) — primary blameless practice.
- [Android app quality](https://developer.android.com/quality) — reliability outcomes.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
