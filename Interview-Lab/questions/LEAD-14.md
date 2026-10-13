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

### Practical walkthrough in Egyptian Arabic

أول 90 يوم في legacy app: أول أسبوعين افهم release pipeline وأهم crashes وslow builds وpayment/data incidents، واتفق على baseline. بعدها اختار vertical slice واحد متكرر العطل، أضف characterization tests عند boundary حقيقي واصلح السبب. في الشهر الثاني اعمل ownership أوضح وCI gate صغيرة موثوقة؛ الشهر الثالث وسع النمط للمنطقة التالية بعد قياس defect/lead time. تجنب big rewrite أو هدف coverage 80% من غير معرفة risk. احفظ migration/rollback لكل خطوة.

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

“I first make the app build and release reproducibly, review incident and crash data, and map the flows that change often or carry financial/security risk. Then I add targeted tests for those contracts, improve CI and observability, and fix one small high-impact defect. By day 90 I migrate one bounded area behind a clearer seam and compare defects, lead time and performance against baseline. I involve the team so the plan reflects hidden constraints and does not stall feature delivery.”

## Interview answer — deep senior

“I start by learning where the app hurts users and developers. In the first weeks I map the release path, variants, critical user journeys, crash and ANR clusters, flaky tests, data migrations and ownership. I take a baseline for change lead time, escaped defects and a few high-risk flows, then choose a vertical slice rather than a whole-app rewrite. In the next month I add characterization tests around that slice, repair a recurring failure and make its state and dependency boundaries explicit. In the third month I turn the successful pattern into a small team convention and CI gate, then select the next slice based on evidence. I involve support and QA so I do not optimize only code aesthetics. I protect release cadence with backward-compatible migrations and rollback plans. A raw coverage target is not a strategy: high coverage of trivial getters can coexist with untested payment retries. The trade-off is incremental visible improvement versus the appeal of a clean-slate rewrite; I choose a path that can ship safely every few weeks.”

## How to answer in the interview

- **Why:** legacy risk must be located before rewriting.
- **How:** baseline, fix one vertical slice, expand.
- **Trade-off:** incremental safety versus rewrite appeal.
- **Failure case:** coverage target misses critical path.
- **Production solution:** measure defects and ship reversible slices.

## Deep-dive talking points

Prompt for discovery evidence, safety net, bounded seam, baseline metrics and team ownership.

## Follow-up questions

- [LEAD-03](../lead-03/): Which debt first? **Answer:** high-impact, frequently changed and risky paths.
- [LEAD-08](../lead-08/): How know improvement worked? **Answer:** compare incident, lead-time and performance baselines.

## Self-check rubric

Prioritize a 90-day baseline, high-risk bug containment, seams and targeted tests, then incremental refactors. Define metrics and avoid promising a full rewrite before understanding production.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — separation principles.
- [Android testing overview](https://developer.android.com/training/testing) — safety net design.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
