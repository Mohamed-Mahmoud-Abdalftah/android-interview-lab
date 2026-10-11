---
id: "SEC-32"
question: "A security SDK falsely flags legitimate devices. How would you handle risk and availability?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "C"
phase: 3
priority: "P1"
order: 329
editorial_status: "reviewed"
---

# SEC-32

## Original interview question

A security SDK falsely flags legitimate devices. How would you handle risk and availability?

## What the interviewer evaluates

- False-positive risk/availability trade-off for security SDK signals.
- Tiered enforcement, shadow mode, appeals and rollback.

## Explanation in Arabic

Security SDK لو false-flagged أجهزة سليمة، hard block للدفع ممكن يضر مستخدمين كتير. نتعامل مع signal كاحتمال: نجمع metrics بدون بيانات حساسة، نتحقق من SDK version/device cohorts، نجرب shadow mode أو step-up/limits بدل منع شامل، ونجهز rollback server-side. لا نلغي كل الحماية بسبب false positives؛ نحافظ على backend authorization.

## Why it matters and how it works

A third-party verdict has sensitivity/specificity that changes by OS, device, SDK and attack patterns. Server policy can score it alongside session, transaction and behavioral signals. Rules should be versioned and reversible, with documented error budget and appeals path.

## Worked example

After an SDK update flags a new OEM model, the risk service compares decline rate and confirmed fraud by cohort. It moves that verdict from block to step-up for the affected cohort, canaries a fixed SDK, and records policy changes. Payment authorization still checks account, amount and provider status.

## Trade-offs and decision criteria

Hard blocks reduce some fraud but cause lost access and support load. Soft decisions preserve availability but may admit abuse; control exposure with transaction limits and extra verification. Shadow mode supplies baseline evidence before enforcement.

## Failure modes

If the app directly exits on `isCompromised=true`, remote policy cannot rescue users and a hook can bypass it. Keep the SDK output as one server-verified input, define timeout/unavailable behavior and monitor both fraud and legitimate decline.

## Production perspective

Run canary rollout, cohort dashboards, support escalation and rollback drills. Do not log device fingerprints unnecessarily; store minimal verdict category, app/SDK version and opaque operation ID.

## Interview answer — short

“I measure false positives, use the SDK as one risk signal, and apply reversible server-side tiers such as step-up or limits. Backend transaction rules remain enforced while availability is restored.”

## Interview answer — structured

“A security SDK is not ground truth. I would quantify impact by app version and device cohort, compare it with fraud outcomes, and use shadow mode before hard enforcement. If legitimate users are blocked, a server-controlled policy can move the affected signal to step-up authentication or lower limits while the SDK issue is fixed. I monitor abuse, provide a support path and preserve ordinary authorization, idempotency and provider confirmation. The mechanics matter. A third-party verdict has sensitivity/specificity that changes by OS, device, SDK and attack patterns. Server policy can score it alongside session, transaction and behavioral signals. Rules should be versioned and reversible, with documented error budget and appeals path. The choice has a trade-off. Hard blocks reduce some fraud but cause lost access and support load. Soft decisions preserve availability but may admit abuse; control exposure with transaction limits and extra verification. Shadow mode supplies baseline evidence before enforcement.”

## Interview answer — deep senior

“I would define a risk-policy state machine with monitor, challenge, limit and deny tiers. Each rule has evidence, owner, version and rollback. A sudden OEM-specific false-positive spike triggers a cohort-specific mitigation rather than disabling all detection; we retain server-side transaction invariants and may lower high-risk limits. I validate SDK error and timeout behavior, canary updates, and compare fraud loss against legitimate conversion. Client-side exit logic is avoided because it is both bypassable and operationally brittle. Users get a safe appeal or alternate verification path without exposing internal detection details. Consider a concrete case. After an SDK update flags a new OEM model, the risk service compares decline rate and confirmed fraud by cohort. It moves that verdict from block to step-up for the affected cohort, canaries a fixed SDK, and records policy changes. Payment authorization still checks account, amount and provider status. A failure case illustrates the risk. If the app directly exits on `isCompromised=true`, remote policy cannot rescue users and a hook can bypass it. Keep the SDK output as one server-verified input, define timeout/unavailable behavior and monitor both fraud and legitimate decline. In production, the response is concrete. Run canary rollout, cohort dashboards, support escalation and rollback drills. Do not log device fingerprints unnecessarily; store minimal verdict category, app/SDK version and opaque operation ID.”

## Deep-dive talking points

Prompt for measured cohorts, shadow mode, reversible rules, SDK outages, user recovery and fraud/availability balance.

## Follow-up questions

- [SEC-21](../sec-21/): Why verify SDK signal server-side? **Answer:** client output is patchable.
- [SEC-29](../sec-29/): Can root detection guarantee security? **Answer:** no; preserve backend invariants.

## Self-check rubric

Can I propose a measured, reversible response to false positives without abandoning payment safeguards?

## References and reviewed-on date

- [Play Integrity overview](https://developer.android.com/google/play/integrity/overview) — tiered enforcement guidance.
- [OWASP MASVS resilience](https://mas.owasp.org/MASVS/controls/MASVS-RESILIENCE-1/) — resilience as defense in depth.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
