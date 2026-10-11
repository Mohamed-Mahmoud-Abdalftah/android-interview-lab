---
id: "LEAD-14"
question: "You inherit a legacy app with low test coverage and frequent bugs. What is your first 90-day plan?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "C"
phase: 5
priority: "P2"
order: 469
editorial_status: "reviewed"
---

# LEAD-14

## Original interview question

You inherit a legacy app with low test coverage and frequent bugs. What is your first 90-day plan?

## What the interviewer evaluates

- First 90 days as discovery, risk reduction and incremental delivery.
- Coverage quality and team trust rather than big rewrite.

## Explanation in Arabic

أول 90 يوم في legacy app: أول شهر أفهم product وincidents، build/release، hotspots، crash/ANR، security، وأعمل baseline. الشهر التاني أضيف safety nets لأكثر flow بيتكسر، أصلح blocker صغير، وأعمل seams للtests. الشهر التالت أحسن جزء واحد end-to-end وأقيس defect rate/lead time. ما أعلنش rewrite ضخم قبل فهم constraints ولا أركز على coverage percentage بلا معنى.

## Why it matters and how it works

A legacy system has hidden contracts in code, production behavior and people. Prioritize incidents, frequently changed paths and irreversible risks. Stabilizing CI and observability improves later refactors. Incremental seams allow tests around behavior before changing structure.

## Worked example

Days 1–30: reproduce release build and top crashes, map checkout state/data ownership. Days 31–60: add lost-response and Room migration tests, fix a frequent crash and document API contract. Days 61–90: extract one repository boundary, stage rollout and compare metrics.

## Trade-offs and decision criteria

A broad rewrite may simplify architecture eventually but risks regression and halts delivery. Small repairs can accumulate without a target design; use an ADR and metrics to keep direction.

## Failure modes

Raising nominal coverage from 20% to 80% with mocked implementation tests does not catch payment duplicates. Choose behavior and boundary tests based on production incidents. Avoid blaming prior team without understanding constraints.

## Production perspective

Present baseline, high-risk plan and measurable wins to product/team. Keep release cadence, mentor owners and revisit roadmap after evidence from first changes.

## Interview answer — short

“I spend the first month learning incidents and release risks, the second adding safety nets to hotspots, and the third delivering a measured incremental improvement—not a blind rewrite.”

## Interview answer — structured

“I first make the app build and release reproducibly, review incident and crash data, and map the flows that change often or carry financial/security risk. Then I add targeted tests for those contracts, improve CI and observability, and fix one small high-impact defect. By day 90 I migrate one bounded area behind a clearer seam and compare defects, lead time and performance against baseline. I involve the team so the plan reflects hidden constraints and does not stall feature delivery. The mechanics matter. A legacy system has hidden contracts in code, production behavior and people. Prioritize incidents, frequently changed paths and irreversible risks. Stabilizing CI and observability improves later refactors. Incremental seams allow tests around behavior before changing structure.”

## Interview answer — deep senior

“My first 30 days are discovery and trust building: pair with maintainers, run the production-like build, study crashes/ANRs, support tickets, payment unknowns, CI flakiness and security findings. I map ownership and collect baseline metrics. Days 31–60 focus on safety nets where failure is costly, such as an old-data Room migration fixture or lost-response idempotency test, plus a visible small fix. Days 61–90 deliver an incremental architectural seam—perhaps repository ownership of checkout state—with staged rollout and before/after evidence. I avoid a full rewrite until I know the cost and can prove why incremental change is insufficient. I share trade-offs and train other owners so improvements survive me. Consider a concrete case. Days 1–30: reproduce release build and top crashes, map checkout state/data ownership. Days 31–60: add lost-response and Room migration tests, fix a frequent crash and document API contract. Days 61–90: extract one repository boundary, stage rollout and compare metrics. A failure case illustrates the risk. Raising nominal coverage from 20% to 80% with mocked implementation tests does not catch payment duplicates. Choose behavior and boundary tests based on production incidents. Avoid blaming prior team without understanding constraints.”

## Deep-dive talking points

Prompt for discovery evidence, safety net, bounded seam, baseline metrics and team ownership.

## Follow-up questions

- [LEAD-03](../lead-03/): Which debt first? **Answer:** high-impact, frequently changed and risky paths.
- [LEAD-08](../lead-08/): How know improvement worked? **Answer:** compare incident, lead-time and performance baselines.

## Self-check rubric

Can you state the context, decision evidence, alternatives, affected people, measurable result and both follow-up answers?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — separation principles.
- [Android testing overview](https://developer.android.com/training/testing) — safety net design.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
