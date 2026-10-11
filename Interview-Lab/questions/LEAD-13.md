---
id: "LEAD-13"
question: "You discover a critical vulnerability days before launch. What is your release decision process?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "C"
phase: 5
priority: "P2"
order: 468
editorial_status: "reviewed"
---

# LEAD-13

## Original interview question

You discover a critical vulnerability days before launch. What is your release decision process?

## What the interviewer evaluates

- Critical vulnerability release decision with severity, exploitability and exposure.
- Safe alternatives, escalation and evidence.

## Explanation in Arabic

ثغرة critical قبل launch لا تتخبّى ولا تتسيب عشان التاريخ. نوقف الجزء المعرّض أو نأجل release حسب exposure، نتحقق من exploit path ونطاق النسخ، نبلغ security/product/leadership بقرار مكتوب وخيارات: fix، feature gate، scope reduction أو delay. لو فيه مستخدمين بالفعل، incident response وربما تدوير secrets ومراقبة. نرجع launch بعد retest مستقل وخطة rollout.

## Why it matters and how it works

Risk assessment considers affected asset, exploitability, blast radius and compensating controls. A local UI guard cannot repair server authorization flaw. Release authority and regulatory requirements may vary; technical recommendation should make residual risk explicit.

## Worked example

Prelaunch review finds client-only refund eligibility. Demonstrate forged request against staging backend, block refund feature server-side, fix backend ownership/state validation, add regression and tampered-client tests, then stage release. An app-only patch is insufficient.

## Trade-offs and decision criteria

Delay has business cost; shipping an exploitable money-movement flaw has larger potential harm. Feature gate can preserve unaffected scope only if it truly blocks the vulnerable path on the trusted side. A narrow fix may be safer than a broad rushed rewrite.

## Failure modes

Team labels finding “theoretical” without reproducing trust boundary or says R8 will hide it. Document evidence, threat, workaround limits and decision owner. Do not claim patched app protects already-installed versions.

## Production perspective

Run a focused security review and release candidate test on actual artifact, verify server mitigation, monitor exploit indicators and prepare communication/incident plan.

## Interview answer — short

“I would stop or scope the release until the critical path is mitigated at the right trust boundary, escalate with evidence and options, then retest and stage rollout.”

## Interview answer — structured

“I verify the vulnerability and affected versions, assess exploitability and impact, and immediately contain any live exposure. I present security, product and leadership with concrete options: server-side feature disablement, a narrow fix, scope reduction or launch delay. For a client-only payment check, only backend authorization can close the hole; an app obfuscation patch cannot. I document residual risk and release criteria, add a regression test, get independent review and monitor a staged rollout. The mechanics matter. Risk assessment considers affected asset, exploitability, blast radius and compensating controls. A local UI guard cannot repair server authorization flaw. Release authority and regulatory requirements may vary; technical recommendation should make residual risk explicit. The choice has a trade-off. Delay has business cost; shipping an exploitable money-movement flaw has larger potential harm. Feature gate can preserve unaffected scope only if it truly blocks the vulnerable path on the trusted side. A narrow fix may be safer than a broad rushed rewrite.”

## Interview answer — deep senior

“I separate discovery, containment, remediation and release decision. First I reproduce safely, preserve evidence and map the trust boundary: can a tampered client move money or expose secrets? If yes, I recommend blocking the affected launch path and applying a server-controlled mitigation that covers old clients. I engage security, backend, product and incident owners promptly, quantify affected cohorts and evaluate whether unaffected features can ship safely. The fix includes negative tests for forged requests, logging/secret review and rollback compatibility. I do not trade away a critical control for a date; the decision record states risks, owner, retest evidence and monitored rollout plan. Consider a concrete case. Prelaunch review finds client-only refund eligibility. Demonstrate forged request against staging backend, block refund feature server-side, fix backend ownership/state validation, add regression and tampered-client tests, then stage release. An app-only patch is insufficient. A failure case illustrates the risk. Team labels finding “theoretical” without reproducing trust boundary or says R8 will hide it. Document evidence, threat, workaround limits and decision owner. Do not claim patched app protects already-installed versions. In production, the response is concrete. Run a focused security review and release candidate test on actual artifact, verify server mitigation, monitor exploit indicators and prepare communication/incident plan.”

## Deep-dive talking points

Prompt for exploit proof, server-side containment, old-client impact, decision owner and retest.

## Follow-up questions

- [SEC-27](../sec-27/): Why can’t app patch alone fix client-only auth? **Answer:** modified APK can bypass it.
- [TST-23](../tst-23/): What tests gate release? **Answer:** threat-specific evidence at the true boundary.

## Self-check rubric

Can you state the context, decision evidence, alternatives, affected people, measurable result and both follow-up answers?

## References and reviewed-on date

- [Android security best practices](https://developer.android.com/privacy-and-security/security-best-practices) — platform security guidance.
- [OWASP MASVS](https://mas.owasp.org/MASVS/) — control assessment.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
