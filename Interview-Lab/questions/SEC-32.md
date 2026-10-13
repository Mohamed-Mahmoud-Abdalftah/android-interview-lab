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

## Practical walkthrough

بعد تحديث SDK، جهاز OEM معيّن بقى يحصل له `tampered=true` رغم إن معدل fraud ما اتغيرش. قارن false positives حسب app version/device cohort، حوّل cohort دي مؤقتًا من deny إلى step-up/limit بسياسة server-side، وراقب النتائج. ما توقفش backend authorization أو AML limits علشان availability؛ غيّر وزن signal المعيوبة واعمل canary للإصلاح.

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

“A security SDK is not ground truth. I would quantify impact by app version and device cohort, compare it with fraud outcomes, and use shadow mode before hard enforcement. If legitimate users are blocked, a server-controlled policy can move the affected signal to step-up authentication or lower limits while the SDK issue is fixed. I monitor abuse, provide a support path and preserve ordinary authorization, idempotency and provider confirmation.”

## Interview answer — deep senior

“I would define a risk-policy state machine with monitor, challenge, limit and deny tiers. Each rule has evidence, owner, version and rollback. A sudden OEM-specific false-positive spike triggers a cohort-specific mitigation rather than disabling all detection; we retain server-side transaction invariants and may lower high-risk limits. I validate SDK error and timeout behavior, canary updates, and compare fraud loss against legitimate conversion. Client-side exit logic is avoided because it is both bypassable and operationally brittle. Users get a safe appeal or alternate verification path without exposing internal detection details. I would define measured thresholds for false-positive rate, fraud loss and abandonment before turning an SDK verdict into a hard block. A versioned server policy can move one affected cohort to step-up while leaving transaction ownership and limits untouched. I would canary a fixed SDK, compare outcomes, and record who approved the temporary policy. The rollback plan must be as fast as the rollout, because availability harm can exceed the benefit of a weak signal.”

## How to answer in the interview

- **Why:** a false-positive security signal can deny legitimate payments.
- **How:** measure verdicts by cohort against fraud outcomes and apply reversible risk tiers.
- **Trade-off:** step-up restores access with added friction and monitored residual risk.
- **Failure case:** global hard block or blanket disablement.
- **Production solution:** server-controlled policy version, canary, rollback, and audit trail.

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

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
