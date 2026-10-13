---
id: "SEC-10"
question: "What is reverse engineering? What do root, hooking, and instrumentation change?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "A"
phase: 3
priority: "P1"
order: 307
editorial_status: "reviewed"
---

# SEC-10

## Original interview question

What is reverse engineering? What do root, hooking, and instrumentation change?

## What the interviewer evaluates

- Static reverse engineering versus dynamic hooking/instrumentation.
- How root changes attacker access without granting client authority.

## Explanation in Arabic

Reverse engineering يعني تحليل APK وcode/resources أو مراقبة التطبيق وهو شغال. Root يدي المهاجم سيطرة أكبر على جهازه، وFrida/غيره يقدروا يبدّلوا return values، يقرؤوا memory أو يعطّلوا certificate checks. مش كل هجوم يحتاج root، لكن root يضعف افتراضات عزل الجهاز. لذلك أي قرار مالي في client قابل للتلاعب.

## Practical walkthrough

مهاجم عدّل `isEligibleForRefund()` أو hook رجّع `true`. ده ممكن يفتح زر في UI، لكن backend لازم يراجع صاحب العملية، حالتها، ومبلغ الرد قبل ما يعمل refund. Root يسهّل قراءة memory وتغيير السلوك، بس binary والتحليل متاحين حتى من غير root. جرّب اختبار hostile client يرسل نفس request بعد تغيير كل client flags.

## Why it matters and how it works

Static analysis recovers structure and constants; dynamic instrumentation observes or changes runtime behavior. Root can bypass some OS controls and ease access to app processes, but ordinary repackaging and proxying also matter. Keystore may protect key extraction while the app can still be manipulated at the use site.

## Worked example

An attacker hooks `isEligibleForRefund()` to return true. The UI may display a refund button, but the backend must independently check transaction ownership, settlement state and limits before issuing the refund. Instrumentation tests should deliberately send forged client states.

## Trade-offs and decision criteria

Root checks and integrity signals raise attack cost and inform risk scoring; hard blocking can harm legitimate users and can be bypassed. Server-side policy is stronger because the attacker cannot edit it through their APK.

## Failure modes

Calling `isRooted()` once at startup and trusting all later requests creates a single bypass point. A locally signed “approved” flag can also be patched. Validate sensitive actions on the backend and treat device signals as probabilistic.

## Production perspective

A fintech threat model includes stolen/repackaged APKs, rooted devices, hooks and traffic replay. The service enforces authorization, nonce/idempotency policy and anomaly monitoring; the app avoids storing unnecessary secrets and provides clear recovery for false positives.

## Interview answer — short

“Reverse engineering inspects the app; hooking changes it while running. Root often makes those attacks easier. I use resilience checks as signals but keep payment and authorization decisions on a trusted server.”

## Interview answer — structured

“Reverse engineering analyzes the APK and runtime behavior; root often increases local access, while hooks can change return values or inspect data at use time. I assume an attacker can make a client refund check return true. The backend still verifies ownership, state, amount and limits before acting. Keystore, obfuscation and integrity signals may raise cost or inform risk tiers, but they do not turn a local Boolean into authority.”

## Interview answer — deep senior

“I model what the attacker can change, not just whether the phone is rooted. The APK can be inspected; hooks can replace return values and observe plaintext at Java or native boundaries. Root may broaden those capabilities, but client checks are never an authority for refunds or transfers. If `isEligibleForRefund()` is forced true, the backend must still verify ownership, settlement state, limits, and provider outcome. I use integrity and tamper signals to tune risk responses, with false-positive monitoring, while the server enforces transaction invariants. A hostile-client test is more convincing than a claim that the app cannot be modified. For verification I would change the client amount, refund eligibility flag and device-risk result independently, then check that the backend still enforces the same transaction rules. I would also test that a suspicious signal leads to the intended step-up or limit, rather than an unexplained permanent denial. This separates resilience, which raises attack cost, from authorization, which must hold even when every local check is bypassed.”

## How to answer in the interview

- **Why:** client execution is observable and mutable by its owner.
- **How:** model APK inspection, root access, and runtime hooks as distinct capabilities.
- **Trade-off:** anti-tamper adds friction without proving trust.
- **Failure case:** backend accepts a client-approved refund flag.
- **Production solution:** derive financial decisions from server records and reconcile provider outcomes.

## Deep-dive talking points

Model an attacker who controls the device: inspect root access, Frida-style hooks, repackaging and local state manipulation, then place trust on the server.

## Follow-up questions

- [SEC-27](../sec-27/): What rejects a patched “approved” flag? **Answer:** backend state and authorization checks.
- [SEC-21](../sec-21/): Is an integrity verdict sufficient? **Answer:** no; verify it server-side and combine with normal authorization.

## Self-check rubric

Can I describe static/dynamic analysis, root effects, Keystore limits and a server-side defense against a patched client?

## References and reviewed-on date

- [OWASP MASTG tools](https://mas.owasp.org/MASTG/tools/) — static and dynamic testing tools.
- [Play Integrity overview](https://developer.android.com/google/play/integrity/overview) — app/device signals and server response.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
