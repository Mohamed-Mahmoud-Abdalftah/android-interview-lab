---
id: "MOD-06"
question: "What are Dynamic Feature Modules / Play Feature Delivery?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "A"
phase: 4
priority: "P1"
order: 359
editorial_status: "reviewed"
---

# MOD-06

## Original interview question

What are Dynamic Feature Modules / Play Feature Delivery?

## What the interviewer evaluates

- Explain install-time versus on-demand feature delivery through App Bundles.
- Address download failure, offline need and runtime entry points.
- Distinguish dynamic delivery from ordinary modularization.

## Explanation in Arabic

Dynamic Feature Module جزء من Android App Bundle يمكن لـGoogle Play يوصله عند التثبيت أو عند الطلب حسب إعداد delivery. الهدف تقليل initial install أو توصيل قدرة قليلة الاستخدام لاحقًا، لكن runtime الآن يجب يتحمل download/progress/failure/cancel/offline. ليست مجرد Gradle module جديدة: اتجاه dependencies مختلف والـbase app لا يرى كود feature أثناء compilation بنفس الطريقة، وDI/navigation تحتاج bridge. لو ميزة حرجة يجب تعمل offline فورًا، on-demand غالبًا قرار سيئ؛ install-time أو base قد يناسب أكثر. اختبر على مسار توزيع حقيقي وليس IDE فقط.

## Why it matters and how it works

An App Bundle lets Play generate device-targeted APKs and deliver configured feature splits. On-demand installation requires an asynchronous request before code/resources are available. The feature depends on the base app, which affects graph visibility and Hilt integration. Delivery rules and Play environment shape actual availability, so local sideload behavior is insufficient proof.

## Worked example

A rarely used document-scanning feature is on demand. The app shows the scan entry point, requests installation on tap, presents progress and retry, and opens the scan route only after success. If the user is offline and has not installed it, the app offers a fallback explanation; essential receipt viewing stays installed locally.

## Trade-offs and decision criteria

Initial download size may shrink, but entry latency and failure states increase. Install-time delivery retains availability yet may not lower initial bytes. Dynamic features complicate testing, DI, navigation, localization/resource management and analytics. Use them when measured size/usage benefit outweighs operational cost.

## Failure modes

Navigation references a class before installation. An offline user cannot reach a required workflow. A feature relies on app Hilt aggregation unsupported by its compile direction. QA tests only debug builds where the module is always present. Installation cancellation leaves a spinner forever.

## Production perspective

Measure feature usage, package size and install success/latency. Test Play delivery modes, offline/cancel/retry, process recreation during install, and correct routing after updates. Include feature-install telemetry without logging sensitive data.

## Interview answer — short

“Dynamic features are App Bundle modules Play can deliver at install time or on demand. They trade initial size for runtime install states and integration complexity.”

## Interview answer — structured

“I use Play Feature Delivery for a capability whose usage and size justify separate delivery. For on-demand mode the app must request the split, show progress, handle failure/offline and navigate only after installation. Dynamic features also have a different compile dependency direction, so DI and navigation contracts need planning. I keep an essential offline workflow installed and test through real distribution paths.”

## Interview answer — deep senior

“A dynamic feature is a packaging and delivery decision, not merely a code-organization technique. The feature is part of an App Bundle and may be installed with the app or downloaded on demand according to configured Play delivery. An on-demand choice can reduce initial bytes for an infrequent, large capability, but it introduces a new runtime state machine: not installed, requesting, downloading, installed, failed or canceled. The app cannot navigate into unloaded code and must offer an offline/error path. It also changes integration: the feature's dependency direction relative to the base affects Hilt aggregation and requires a documented entry-point or explicit factory boundary. I would keep login, payment recovery or other must-work-offline paths in base or install-time delivery unless product constraints say otherwise. To decide, I measure feature usage, size, install latency and failure rate, then test with bundle delivery, process recreation and updates, not only a debug installation where all modules happen to be present. I also make sure analytics distinguishes a user declining the feature from an installation failure.”

## Deep-dive talking points

Discuss bundle splits, delivery modes, install state machine, offline requirements, DI bridge and telemetry.

## Follow-up questions

- Is a dynamic feature the same as a regular library module? **Answer:** no; it changes packaging, delivery and dependency direction.
- When can on-demand be harmful? **Answer:** when a required workflow must work immediately offline.
- What must happen before navigation? **Answer:** confirm that installation succeeded and code/resources are available.

## Self-check rubric

Choose a candidate feature, justify delivery, model install failure, and name integration tests.

## References and reviewed-on date

- [Play Feature Delivery overview](https://developer.android.com/guide/playcore/feature-delivery) — delivery modes.
- [Hilt in multi-module apps](https://developer.android.com/training/dependency-injection/hilt-multi-module) — dynamic feature caveat.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Play delivery behavior must be tested in the chosen channel.
