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

## Practical walkthrough

لو محتاج crash reporting أو payment SDK، اعمل build-vs-buy على capability المطلوبة: time-to-market، maintenance، security، privacy، Android/ABI support، vendor SLA، exit cost. لا تدخل SDK لمجرد أن demo نجح؛ جرّبه في minified release على الأجهزة المستهدفة، راجع permissions وdata flow وoffline/timeout. ولو تبني بنفسك، احسب بروتوكولات وعمليات support طويلة الأجل. حدد adapter وحدود ownership عشان تقدر تستبدل vendor لاحقًا.

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

“I compare building and buying against the actual capability and risk. For a payment SDK, buying may provide certified device integration and shorter time to market, but it introduces vendor release cadence, ABI support, callback semantics, data handling and outage dependency. Building in-house offers control yet can require expertise and ongoing compliance or certification work that the team does not have. I prototype the riskiest path in a minified release build on target devices, inspect permissions and data flows, and test timeout, disconnect and process death before selecting a vendor. I score total cost of ownership, security review, support terms, update frequency and exit cost rather than license price alone. I wrap the SDK behind a small domain interface so the app’s UI does not depend on raw callbacks, but I do not claim an adapter removes vendor constraints. The decision document states which evidence would make us switch and how in-flight operations remain safe during migration.”

## How to answer in the interview

- **Why:** external dependency changes risk and control.
- **How:** compare capability, ownership, support and proof.
- **Trade-off:** market speed versus vendor lock-in.
- **Failure case:** demo succeeds but release ABI fails.
- **Production solution:** adapter plus device and contract evidence.

## Deep-dive talking points

Prompt for lifecycle cost, supply-chain review, regulated constraints, adapter boundary and exit trigger.

## Follow-up questions

- [PAY-09](../pay-09/): Why wrap EMV SDK? **Answer:** isolate callbacks/quirks while preserving capability contracts.
- [CIC-18](../cic-18/): What if dependency build code is malicious? **Answer:** verify supply chain and isolate secrets.

## Self-check rubric

Compare build and buy on capability, maintenance, security, privacy, cost and exit path; name the experiment that would change your recommendation.

## References and reviewed-on date

- [Android app dependencies](https://developer.android.com/build/dependencies) — dependency management.
- [Gradle dependency verification](https://docs.gradle.org/current/userguide/dependency_verification.html) — supply-chain checks.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
