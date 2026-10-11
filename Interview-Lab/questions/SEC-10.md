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

“An attacker with the APK can inspect bytecode and resources, and with instrumentation can intercept method calls and alter results. Root broadens local access but is not the only threat. Keystore can make key extraction harder, yet the caller can still be hooked around the cryptographic operation. I put sensitive business rules on the backend, bind requests to sessions and transaction identity, and use integrity checks as one risk input. A practical defense is to ask which client result would be dangerous if forced to true. A patched refund-eligibility method may alter a screen, but the backend must independently check ownership, state and limits. Root or integrity checks can inform risk policy, but they should not be the only gate.”
## Interview answer — deep senior

“My first question is what an attacker gains by changing one Boolean or API request. If the backend accepts a client-approved payment or refund, obfuscation and root detection cannot repair the trust boundary. I reproduce bypasses with a test harness, instrument the network/client decision path, and make the server reconstruct authoritative price, ownership and state. I may add Play Integrity and anti-tamper signals with tiered responses, but I monitor false positives and never claim these controls make a rooted endpoint trustworthy. I also minimize tokens and sensitive memory because hooks can observe plaintext at use time. I assume an attacker can both read and modify their app copy. Static tools expose code and constants; dynamic hooks can replace return values, capture token plaintext or bypass certificate checks. Root makes some of that easier, though repackaging does not require it. I would test a forged refund request from a modified client and ensure the service rejects it using trusted transaction records. Keystore can resist raw key extraction on some hardware but does not prevent observation around a key operation. Play Integrity may increase confidence if verified and bound to a request on the backend; I would monitor false positives and avoid claiming a verdict proves the endpoint is clean. Financial effects remain protected by server authorization, idempotency and reconciliation.”
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

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
