---
id: "LEAD-15"
question: "How would you push back on a requirement that conflicts with mobile OS/security constraints?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "C"
phase: 5
priority: "P2"
order: 470
editorial_status: "reviewed"
---

# LEAD-15

## Original interview question

How would you push back on a requirement that conflicts with mobile OS/security constraints?

## What the interviewer evaluates

- Constructive pushback grounded in OS/security facts and user outcome.
- Viable alternatives, decision ownership and documentation.

## Explanation in Arabic

لو requirement يخالف Android/security، ما نقولش “مستحيل” وخلاص. نفهم user outcome، نشرح constraint بدليل: background work limits، permission policy، process death، أو إن client secret مش سري. نقترح بدائل تحقق الغرض: WorkManager لdeferrable sync، server-issued scoped token بدل private key في APK، أو UX يوضح pending. نسجل trade-off ونجرب prototype صغير لو فيه شك.

## Why it matters and how it works

Platform constraints change by OS/API and app target, so verify current official docs. Security boundaries are design constraints, not optional polish. Pushback should separate fixed constraints from negotiable UX/scope and quantify impact.

## Worked example

Product asks “charge again immediately when spinner times out.” Explain that timeout may hide approved charge; propose pending UI with status lookup and safe retry using original operation ID. Show a test where server commits then drops response, making the risk concrete.

## Trade-offs and decision criteria

Alternative design may add latency or UX friction; share metrics and support plan. A hard no without options blocks product value, while agreeing to unsafe shortcut creates financial harm.

## Failure modes

If team adds a private API key to BuildConfig to meet deadline, it ships in APK. Escalate with proof of extraction and propose backend proxy. Document residual risk if leadership chooses a scoped temporary mitigation.

## Production perspective

Bring product, backend, security and QA into decision early. Prototype the constraint, write ADR, test critical failure and monitor post-release user friction and risk.

## Interview answer — short

“I clarify the desired user outcome, verify the Android/security constraint, show the concrete failure, and offer a safe alternative with cost and timeline.”

## Interview answer — structured

“I avoid saying only ‘Android won’t allow it.’ I identify the user need, check current platform guidance, and demonstrate the risk. If the request is to retry a timed-out payment, I explain that the first charge may have succeeded and propose a pending state plus status lookup and same-ID retry. I compare UX cost with duplicate-charge risk, invite backend/security input and document the decision. For version-dependent OS behavior I test the supported API matrix before drawing a hard line.”

## Interview answer — deep senior

“I separate the non-negotiable invariant from the product implementation. A requirement to store a private provider key in BuildConfig cannot satisfy secrecy because every APK is inspectable; I show extraction risk and offer a backend endpoint with scoped authorization. A requirement for instant completion after network timeout conflicts with distributed uncertainty; I propose a truthful Unknown UI, reconciliation and clear support reference. I quantify latency and adoption costs, prototype the alternative and align mobile, backend, QA and security on tests. If leadership accepts residual risk for a noncritical area, I document owner, expiry and mitigation; for financial authorization I recommend blocking unsafe release rather than disguising the boundary.”

## Deep-dive talking points

Prompt for user outcome, verified constraint, demonstration, alternative, cost and decision record.

## Follow-up questions

- [PAY-08](../pay-08/): Why not immediate second charge? **Answer:** timeout is unknown, requiring same-ID lookup.
- [SEC-31](../sec-31/): Why not BuildConfig secret? **Answer:** APK extraction defeats confidentiality.

## Self-check rubric

Can you state the context, decision evidence, alternatives, affected people, measurable result and both follow-up answers?

## References and reviewed-on date

- [Android background work guide](https://developer.android.com/develop/background-work/background-tasks) — platform limits.
- [Android security best practices](https://developer.android.com/privacy-and-security/security-best-practices) — trust boundaries.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
