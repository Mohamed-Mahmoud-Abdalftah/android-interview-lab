---
id: "MOD-21"
question: "When are dynamic feature modules inappropriate because of offline/runtime constraints?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "C"
phase: 4
priority: "P1"
order: 374
editorial_status: "reviewed"
---

# MOD-21

## Original interview question

When are dynamic feature modules inappropriate because of offline/runtime constraints?

## What the interviewer evaluates

- Assess critical-path availability, latency and offline contract.
- Explain install failure and Play distribution constraints.
- Offer install-time/base alternatives with evidence.

## Explanation in Arabic

On-demand dynamic feature غير مناسبة إذا user يحتاجها فورًا بدون شبكة: عرض تذكرة سفر مخزنة، استعادة payment/status، أو إجراء safety/identity لازم في لحظة. حتى مع اتصال، download قد يفشل/يتأخر أو يُلغى، والfeature غير موجودة قبل install. لو requirements تقول must work offline، ضعها في base أو install-time delivery وتأكد أنها متاحة في القناة المدعومة. لو feature كبيرة ونادرة ولها fallback مقبول، on-demand قد تستحق. قرر من contract المنتج وقياس size/usage/failure، لا من الرغبة في مزيد modules.

## Why it matters and how it works

On-demand delivery separates feature availability from app installation. Before a successful split install, code and resources cannot be assumed present. Play Feature Delivery relies on supported distribution and installation mechanisms; test environments may package modules differently. An install-time module remains part of initial delivery, so it trades initial bytes for immediate availability.

## Worked example

A transit app shows an already purchased ticket offline at a station. Making ticket display on demand could strand the rider after a fresh install or device restore without network; include the secure ticket viewer and required assets in the initial install. An optional 3D station tour can be on demand with a download prompt, retry and graceful offline fallback.

## Trade-offs and decision criteria

Base/install-time size increases, but reliability of a critical path improves. On-demand reduces initial footprint but adds install UX, telemetry, QA matrix and possible policy/channel limits. A feature can be preinstalled conditionally depending on supported delivery modes, but do not assume it is available for every user until verified.

## Failure modes

The app navigates to a class before the split installs. An offline user cannot view a paid ticket. A test sideloads all splits and falsely concludes on-demand works offline. Install cancellation is not modeled, leaving a broken back stack. A library used by base is moved into a removable feature.

## Production perspective

Write availability requirements per journey, test fresh install/offline/poor network/cancellation and process recreation, and monitor install latency and failure rate. Keep emergency and recovery paths in reliably delivered code.

## Interview answer — short

“Avoid on-demand delivery for a must-work-immediately or offline critical path; keep required code installed and reserve dynamic delivery for optional features with a fallback.”

## Interview answer — structured

“I decide from availability requirements. A purchased-ticket viewer or payment recovery flow must work even when a split cannot download, so I put it in base or install-time delivery. An optional 3D tour can tolerate an on-demand prompt, progress and failure path. I test actual Play delivery, not a debug build with all modules installed, and measure size benefit against install latency and failure.”

## Interview answer — deep senior

“The relevant question is whether the feature can be unavailable at the moment the user needs it. On-demand delivery creates a runtime prerequisite: code and resources are present only after a successful install request, which can be delayed, denied, canceled or impossible offline. For a transit ticket already purchased and needed at a station, that is an unacceptable product risk; I keep the viewer and its required assets in base or install-time delivery and test fresh install plus offline use. A large optional 3D tour has a different contract: the app can show a download choice, progress, retry and graceful fallback. I also account for channel compatibility and updates, because local debug installs often include modules in a way that hides delivery failures. I measure initial bytes saved, usage frequency, install success and time, and support cost before choosing the mode. Navigation and DI must not assume the split exists, and any critical recovery path must remain available if installation fails. Dynamic delivery is valuable when its availability trade-off is acceptable, not simply because modularization is fashionable.”

## Deep-dive talking points

Discuss offline contract, split availability, base/install-time alternative, real delivery tests and telemetry.

## Follow-up questions

- Does on-demand code exist before installation succeeds? **Answer:** no; navigation must wait for availability.
- Is a debug build sufficient to test offline split behavior? **Answer:** no; exercise the actual delivery configuration.
- What metric justifies the trade-off? **Answer:** size/usage benefit against install latency, failure and support impact.

## Self-check rubric

Classify one critical and one optional feature, model install failure, and define real distribution tests.

## References and reviewed-on date

- [Play Feature Delivery overview](https://developer.android.com/guide/playcore/feature-delivery) — delivery modes and installation.
- [Android modularization guide](https://developer.android.com/topic/modularization) — module trade-offs.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Availability policy depends on the product journey.
When are dynamic feature modules inappropriate because of offline/runtime constraints?
