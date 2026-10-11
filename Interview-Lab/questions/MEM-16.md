---
id: "MEM-16"
question: "What are StrictMode, Perfetto/System Trace, and Android vitals useful for?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "B"
phase: 1
priority: "P1"
order: 71
editorial_status: "reviewed"
---

# MEM-16

## Original interview question

What are StrictMode, Perfetto/System Trace, and Android vitals useful for?

## What the interviewer evaluates

- Match development-time violation detection, detailed device tracing, and field metrics to different questions.
- Explain what each tool can and cannot prove.
- Connect a field regression to a reproducible trace and verified fix.

## Explanation in Arabic

`StrictMode` ينبهك في التطوير لو حصل disk أو network access على Main أو بعض أنماط استخدام resources؛ يفيد لاكتشاف مخالفة مبكرة، لكنه لا يشرح كل أسباب jank. `Perfetto/System Trace` يسجل timeline للـthreads والـscheduler والـframes وBinder/I/O عشان تعرف أين ضاع الوقت في سيناريو محدد على جهاز. `Android vitals` يعطي إشارات من مستخدمين حقيقيين مثل ANR/crash وstartup أو rendering حسب التوفر، فيحدد حجم المشكلة والأجهزة المتأثرة، لكنه عادة لا يغني عن trace محلي يفسر السبب. استخدمهم كحلقة: field signal، إعادة إنتاج، trace، إصلاح، ثم قياس field بعد الإطلاق.

## Why it matters and how it works

StrictMode policies flag selected operations on a thread or VM, especially accidental main-thread disk/network work; they are guardrails, not comprehensive performance profilers. Perfetto records time-correlated system and app events on a device, exposing scheduling and cross-thread interactions. Android vitals aggregates production quality signals for Play-distributed apps, helping prioritize by user impact and cohort. A trace is detailed but narrow; a population metric is broad but may not pinpoint root cause.

## Worked example

Android vitals shows ANRs concentrated on low-end devices after a release. Reproduce opening the order list on a matching device. StrictMode reports a synchronous database read on Main; a Perfetto trace shows Main waiting during that query while frames are missed. Move the query behind a main-safe repository and check lock contention, then compare local trace and later ANR cohort. This is an investigative scenario; no real vitals or trace was collected here.

## Trade-offs and decision criteria

StrictMode is cheap to enable in debug builds but can produce expected or third-party violations that require triage. Perfetto offers rich causality at the cost of capture setup and trace interpretation. Android vitals reflects real users but is aggregated, delayed, and limited by distribution/reporting context. Use Android Studio CPU profiler when function-level CPU stacks are needed; system tracing alone may not identify each method.

## Failure modes

Shipping a harsh StrictMode penalty without understanding app behavior can harm users. Capturing a trace on a fast emulator misses the affected device conditions. Treating an ANR rate improvement from a tiny cohort as proven causality can mislead. A Perfetto trace without app markers or reproduction context is hard to interpret. Record build, scenario, API/device, and input size with each trace.

## Production perspective

Define an alert threshold and affected cohort from Android vitals; use privacy-safe identifiers to correlate release version. Reproduce on representative devices, annotate app spans, gather system trace, and fix the specific blocking path. Verify locally with the same scenario and in staged rollout metrics. Keep raw traces controlled because they may expose sensitive timing or identifiers.

## Interview answer — short

“StrictMode catches selected bad operations such as main-thread I/O in development. Perfetto explains a particular device's timing across threads and the system. Android vitals shows how often issues affect real users.”

## Interview answer — structured

“I use these tools at different levels. StrictMode gives quick development feedback for selected thread and VM violations, especially disk or network work on Main. Perfetto or System Trace records scheduling, frames, and cross-thread events during a repeatable device flow. Android vitals aggregates field ANR, crash, and performance signals to tell me priority and affected cohorts. A vitals spike alone does not identify the offending line, and a local trace alone does not establish user impact. I link them through a hypothesis, reproduction, fix, and rollout measurement.”

## Interview answer — deep senior

“My workflow starts with scale and then drills into causality. Android vitals may show a user-perceived ANR regression tied to a release and device class. I reproduce on a comparable device and enable StrictMode in debug to catch obvious synchronous I/O or leaked resource patterns. I then capture a Perfetto trace of the exact interaction, inspect Main thread slices, scheduler state, binder waits, disk operations, and frame deadlines, and add app trace markers if the operation is opaque. StrictMode does not catch every source of latency, and system traces may not resolve every method-level CPU hotspot, so I use a CPU profiler where needed. I fix the specific cause, rerun the same trace and UI metric, and use staged rollout vitals to confirm the field regression actually improves. The evidence and limitations are recorded separately.”

## Deep-dive talking points

Discuss population versus single-device evidence, StrictMode policy scope, Perfetto scheduling, app trace markers, and rollout verification.

## Follow-up questions

- Does a clean StrictMode run prove no ANR risk? **Answer:** no; it detects selected violations, while lock contention or expensive computation can still block Main.
- Can one Perfetto trace establish production prevalence? **Answer:** no; it explains a reproduced path, while field metrics establish affected population.
- Why might a trace need CPU profiling too? **Answer:** system traces show scheduling and slices, but method-level CPU attribution can need stack sampling or instrumentation.

## Self-check rubric

Pick each tool for a concrete question, state its limit, connect a field regression to a trace, and describe before/after verification.

## References and reviewed-on date

- [StrictMode API](https://developer.android.com/reference/android/os/StrictMode) — thread and VM policy checks.
- [System tracing overview](https://developer.android.com/topic/performance/tracing) — Perfetto timeline scope.
- [Android vitals ANRs](https://developer.android.com/topic/performance/vitals/anr) — field signal.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The ANR case is illustrative; no production telemetry is claimed.
