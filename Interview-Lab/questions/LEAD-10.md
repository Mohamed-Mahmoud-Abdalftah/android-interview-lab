---
id: "LEAD-10"
question: "How do you decide build versus buy for third-party libraries/SDKs?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "B"
phase: 5
priority: "P2"
order: 465
editorial_status: "reviewed"
---

# LEAD-10

## Original interview question

How do you decide build versus buy for third-party libraries/SDKs?

## What the interviewer evaluates

- Build-versus-buy evaluation beyond feature list.
- Security, maintenance, SDK lifecycle and exit plan.

## Explanation in Arabic

قرار build vs buy يعتمد على قيمة الميزة، وقت الوصول، security/compliance، جودة SDK، التحديثات، lock-in، cost وteam capability. SDK مدفوعات أو biometric لازم نفهم certifications والدعم وABI/OS matrix؛ بناء بديل داخلي ممكن يبقى غير واقعي أو غير مسموح. بنعمل proof صغير، threat review، وexit plan لو vendor فشل.

## Why it matters and how it works

A third-party library becomes part of the app supply chain and release behavior. Evaluate license, maintenance cadence, API compatibility, size/performance, data collection, transitive dependencies and security advisories. A wrapper/port can contain vendor-specific APIs but not erase certification constraints.

## Worked example

Choose image loader: compare mature maintained library versus custom pipeline on caching, formats, memory and accessibility of fixes. Choose EMV SDK: certification/provider mandate may force buy, so isolate adapter, test device matrix and negotiate recovery contract.

## Trade-offs and decision criteria

Buying accelerates delivery but adds dependency and privacy risk. Building gives control but creates permanent maintenance and specialist staffing cost. A thin adapter reduces switching cost but too generic can hide unique capabilities.

## Failure modes

Team selects unmaintained SDK because demo works, then a new Android API or ABI release breaks production. Check release history and support SLA; canary updates and retain rollback compatibility.

## Production perspective

Document decision matrix with weighted criteria, owner, security review, total cost and exit trigger. Track vendor incidents, SDK crash rates and update lag after adoption.

## Interview answer — short

“I compare total lifecycle cost and risk, not just implementation time. For an SDK I check security, maintenance, device support, data handling and exit strategy before buying.”

## Interview answer — structured

“I start with requirements and constraints: is the capability commodity, regulated or differentiating? I compare in-house build effort and ongoing maintenance with a vendor’s reliability, license, privacy, security and Android compatibility. I run a proof on target devices and isolate vendor APIs behind a narrow adapter where useful. For EMV, certification may make a vendor SDK mandatory; I still test callbacks, ABI support and reversal behavior. The decision includes an exit trigger and migration cost. ”

## Interview answer — deep senior

“I model the full lifecycle. A library’s initial integration speed can be outweighed by transitive vulnerabilities, abandoned maintenance, size, startup cost, data collection or a poor incident SLA. Building internally requires specialist ownership, test infrastructure and update capacity; for regulated payment hardware it may not be feasible. I inspect source/release cadence and licensing, run a security and performance proof on release builds, and negotiate support/rollback. A domain port limits dependency spread but keeps provider-specific capabilities explicit. After adoption I monitor crash rate, update lag and vendor incidents, and I keep a documented exit plan rather than assuming switching is free. ”

## Deep-dive talking points

Prompt for lifecycle cost, supply-chain review, regulated constraints, adapter boundary and exit trigger.

## Follow-up questions

- [PAY-09](../pay-09/): Why wrap EMV SDK? **Answer:** isolate callbacks/quirks while preserving capability contracts.
- [CIC-18](../cic-18/): What if dependency build code is malicious? **Answer:** verify supply chain and isolate secrets.

## Self-check rubric

Can you state the context, decision evidence, alternatives, affected people, measurable result and both follow-up answers?

## References and reviewed-on date

- [Android app dependencies](https://developer.android.com/build/dependencies) — dependency management.
- [Gradle dependency verification](https://docs.gradle.org/current/userguide/dependency_verification.html) — supply-chain checks.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
