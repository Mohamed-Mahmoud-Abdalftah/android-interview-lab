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

“A useful postmortem explains how a reasonable person operating the system reached the outcome. I document impact, timeline, detection gap, decisions and uncertainty, then map contributing technical and organizational factors. For a payment incident I include unknown transactions and reconciliation impact, while protecting card/customer data in the record. I prioritize actions by risk reduction: an automated pre-upload gate, a staged rollout signal, an on-call runbook and a drill. Each action has an owner and test that proves it works; we review closure and recurrence. Blameless language increases reporting honesty but does not excuse failing to deliver the agreed corrective work.”

## Deep-dive talking points

Prompt for trigger versus contributors, factual timeline, action verification, customer mitigation and data minimization.

## Follow-up questions

- [CIC-19](../cic-19/): What systemic gate prevents wrong flavor? **Answer:** assert built artifact tuple before upload.
- [LEAD-08](../lead-08/): How measure improvement? **Answer:** recurrence, detection and recovery metrics.

## Self-check rubric

Can you state the context, decision evidence, alternatives, affected people, measurable result and both follow-up answers?

## References and reviewed-on date

- [Google SRE postmortem culture](https://sre.google/workbook/postmortem-culture/) — primary blameless practice.
- [Android app quality](https://developer.android.com/quality) — reliability outcomes.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
