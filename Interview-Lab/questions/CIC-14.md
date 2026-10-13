---
id: "CIC-14"
question: "How do you use staged rollout, crash-rate gates, and rollback plans?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 433
editorial_status: "reviewed"
---

# CIC-14

## Original interview question

How do you use staged rollout, crash-rate gates, and rollback plans?

## What the interviewer evaluates

- Staged rollout as blast-radius control, not true uninstall rollback.
- Crash/ANR and business metric gates.

## Explanation in Arabic

Staged rollout ينزل النسخة لنسبة صغيرة ثم يزيدها حسب crashes/ANRs وbusiness metrics مثل payment unknown rate، login failure وreversal backlog. لو metric تعدّت threshold نوقف توزيع جديد، لكن الأجهزة اللي ثبتت النسخة تظل عليها؛ rollback الحقيقي غالبًا feature gate أو fix-forward compatible. Database migration لازم تشتغل مع النسخ القديمة والجديدة أثناء rollout.

## Practical walkthrough

Staged rollout يعرّض نسبة صغيرة أولًا، لكن نسبة قليلة مش معناها risk قليل لو payments أو login مكسورين. حدد قبل النشر gates مثل crash/ANR، auth failure، payment unknown rate، support tickets، مع baseline وthreshold ووقت مراقبة. لو gate فشل، أوقف توسيع النسبة، عطّل feature من server إن كان آمنًا، وجهّز build جديد بـversionCode أعلى؛ Android المستخدم الذي حدّث لا يرجع تلقائيًا للقديم. راقب pending operations عند rollback حتى ما تضيعش reconciliation.

## Why it matters and how it works

Play rollout percentage controls distribution to eligible users. Monitoring must segment by version, device/ABI and cohort and compare against baseline. Server API compatibility and remote flags allow mitigation while app update propagates.

## Worked example

New payment SDK v4 goes to 1% of terminals. Gate expansion on crash-free sessions, authorization success, unknown-to-resolved time and reversal queue age. If one ABI crashes, halt rollout and disable new authorization for that cohort while reconciliation continues.

## Trade-offs and decision criteria

Small cohorts limit exposure but produce noisy statistics and slower detection of rare issues. Aggressive automatic gates need robust baselines and false-positive handling. Human release judgment remains useful for high-risk migrations.

## Failure modes

A team halts rollout and assumes issue is gone, but installed users still crash or hold pending payments. Keep backend mitigation, support path and compatible hotfix. Never disable reversal workers to stop new payments.

## Production perspective

Release runbook defines thresholds, observation windows, owner and escalation. Record artifact/version, decisions and cohort metrics for incident review.

## Interview answer — short

“I stage rollout with crash, ANR and payment-health gates. Halting stops new distribution, not existing installs, so I prepare server mitigation and compatible fix-forward.”

## Interview answer — structured

“I release to a small cohort, compare crash/ANR and business outcomes against baseline, then expand only when evidence is stable. For fintech I watch payment unknowns, approvals and reversal backlog as well as crashes. If a gate fails, halt expansion and use server feature flags or a compatible hotfix for users already updated. Database/backend contracts must support mixed app versions during rollout.”

## Interview answer — deep senior

“I define rollout and containment before pressing publish. A staged rollout limits exposure while I compare crash, ANR, startup and business transaction metrics against the prior release and explicit thresholds. I segment by app version, device, API level and network where useful; aggregate averages can hide an ABI-specific failure. A low crash rate does not excuse a payment flow that records unknown outcomes without reconciliation. If a gate fires, I halt expansion, use a tested server-side feature control where safe, and prepare a fixed higher-version release. I do not promise that Play can instantly downgrade devices already updated. A rollback plan also covers data compatibility and in-flight operations: disabling new payments must not stop workers from reconciling old attempts. The trade-off is slower reach versus time to detect issues. I keep an incident owner and decision log so the team can act on thresholds rather than debate during an outage.”

## How to answer in the interview

- **Why:** staging buys detection time.
- **How:** watch technical and business gates by version/device.
- **Trade-off:** release reach versus exposure.
- **Failure case:** crash aggregate hides one ABI failure.
- **Production solution:** halt, contain and ship corrected version.

## Deep-dive talking points

Prompt for cohort segmentation, financial metrics, installed-user limit and mixed-version compatibility.

## Follow-up questions

- [CIC-03](../cic-03/): What artifact is monitored? **Answer:** the exact promoted AAB/version.
- [PAY-14](../pay-14/): How handle ABI crash? **Answer:** cohort halt while recovery paths stay active.

## Self-check rubric

Declare staged rollout percentage, cohort metrics and stop thresholds before release; halt distribution on regression and describe the higher-version fix path for already installed users.

## References and reviewed-on date

- [Android staged releases](https://developer.android.com/studio/publish) — release workflow.
- [Android vitals](https://developer.android.com/topic/performance/vitals) — crash/ANR monitoring.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
