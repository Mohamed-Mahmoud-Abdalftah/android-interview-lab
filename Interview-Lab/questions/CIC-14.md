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

“I release to a small cohort, compare crash/ANR and business outcomes against baseline, then expand only when evidence is stable. For fintech I watch payment unknowns, approvals and reversal backlog as well as crashes. If a gate fails, halt expansion and use server feature flags or a compatible hotfix for users already updated. Database/backend contracts must support mixed app versions during rollout. The mechanics matter. Play rollout percentage controls distribution to eligible users. Monitoring must segment by version, device/ABI and cohort and compare against baseline. Server API compatibility and remote flags allow mitigation while app update propagates. The choice has a trade-off. Small cohorts limit exposure but produce noisy statistics and slower detection of rare issues. Aggressive automatic gates need robust baselines and false-positive handling. Human release judgment remains useful for high-risk migrations.”

## Interview answer — deep senior

“I define metric thresholds and observation windows before launch to avoid moving the goalposts. Cohort segmentation by API, ABI and vendor firmware catches release-only native defects that aggregate crash rate can hide. I stop new authorizations if needed but preserve status lookup/reversal recovery. A stopped Play rollout is not an uninstall; already affected clients require operational mitigation and a new app version. I document whether schema or backend changes are backward compatible so rollback/fix-forward is realistic. Consider a concrete case. New payment SDK v4 goes to 1% of terminals. Gate expansion on crash-free sessions, authorization success, unknown-to-resolved time and reversal queue age. If one ABI crashes, halt rollout and disable new authorization for that cohort while reconciliation continues. A failure case illustrates the risk. A team halts rollout and assumes issue is gone, but installed users still crash or hold pending payments. Keep backend mitigation, support path and compatible hotfix. Never disable reversal workers to stop new payments. In production, the response is concrete. Release runbook defines thresholds, observation windows, owner and escalation. Record artifact/version, decisions and cohort metrics for incident review. The decision has a trade-off. Small cohorts limit exposure but produce noisy statistics and slower detection of rare issues. Aggressive automatic gates need robust baselines and false-positive handling. Human release judgment remains useful for high-risk migrations.”

## Deep-dive talking points

Prompt for cohort segmentation, financial metrics, installed-user limit and mixed-version compatibility.

## Follow-up questions

- [CIC-03](../cic-03/): What artifact is monitored? **Answer:** the exact promoted AAB/version.
- [PAY-14](../pay-14/): How handle ABI crash? **Answer:** cohort halt while recovery paths stay active.

## Self-check rubric

Can you explain the mechanism, apply the example, justify a trade-off, identify a failure mode, and answer both follow-ups?

## References and reviewed-on date

- [Android staged releases](https://developer.android.com/studio/publish) — release workflow.
- [Android vitals](https://developer.android.com/topic/performance/vitals) — crash/ANR monitoring.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
