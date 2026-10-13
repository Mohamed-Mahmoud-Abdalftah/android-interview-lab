---
id: "TST-17"
question: "What are screenshot tests, Baseline Profiles, and Macrobenchmark tests?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 412
editorial_status: "reviewed"
---

# TST-17

## Original interview question

What are screenshot tests, Baseline Profiles, and Macrobenchmark tests?

## What the interviewer evaluates

- Purpose and limitations of screenshots, Baseline Profiles and Macrobenchmark.
- Correct production-like performance setup.

## Explanation in Arabic

Screenshot test تقارن شكل UI بصورة baseline وتكشف layout أو RTL regression، لكنها لا تثبت إن الزر يعمل أو إن accessibility semantics صحيحة. `Baseline Profiles` تحدد hot paths علشان ART يهيئ compilation لمسارات مهمة؛ لازم نتحقق من الـprofile في build المناسب. `Macrobenchmark` تقيس startup أو frame timing على جهاز/إعدادات متكررة وبناء release-like، مش داخل unit test.

## Practical walkthrough

اختَر metric قبل التحسين: startup من tap لframe جاهز، أو jank في scroll حقيقي. قارن نفس device/OS/thermal state وعدة runs، وابحث عن allocation traces قبل تغيير الكود. لو image loading هو المشكلة، تحسين algorithm في ViewModel قد لا يصلح الرسم. لا تعتبر screenshot “performance test” ولا رقم benchmark واحدًا ضمانًا لكل الأجهزة.

## Why it matters and how it works

Baseline Profiles are generated from representative interactions and shipped with the app/library for ahead-of-time optimization. Macrobenchmark runs outside the target app process and requires appropriate benchmarkable build configuration. Screenshot goldens depend on device/font/theme and need controlled environment.

## Worked example

For a product list, capture screenshot goldens at light/dark and RTL; generate profile for cold launch plus first scroll; benchmark startup and frame timing on a representative low-end device across repeated iterations. Compare with a baseline and inspect allocation traces before optimizing.

## Trade-offs and decision criteria

Profiles can improve startup at install/runtime but add maintenance when navigation changes. Macrobenchmarks are slower and noisy; use stable hardware and repeated measurements. Screenshot tests catch appearance but not semantics or functional correctness.

## Failure modes

A team updates a Baseline Profile and claims success without measuring startup. Run Macrobenchmark before/after. A screenshot test fails because font rendering changed on CI; pin the rendering environment and review intentional changes.

## Production perspective

Use release-like benchmark variants, controlled thermal/battery state and representative devices. Gate large regressions with statistical tolerance, not a single noisy measurement.

## Interview answer — short

“Screenshot tests catch visual changes; Baseline Profiles guide runtime optimization; Macrobenchmark measures user-visible performance on devices. I use them together and validate with release-like builds.”

## Interview answer — structured

“Screenshots provide pixel-level regression signals, while semantics tests verify interaction and accessibility. A Baseline Profile describes code paths to precompile and may reduce startup/jank. Macrobenchmark measures startup or scrolling under controlled device conditions. I generate profiles from representative journeys, then benchmark to verify the impact rather than assume it. Debug builds and one-off measurements are unreliable.”

## Interview answer — deep senior

“These tools answer different questions. A screenshot golden catches a visual regression in light, dark, RTL or font-scaled layouts, but cannot prove a button’s behavior or screen-reader semantics. A Baseline Profile identifies important code paths for ahead-of-time optimization in the installed app; I verify the generated profile is packaged and represents real startup or scroll flows. Macrobenchmark measures user-visible startup and frame performance in a release-like build on a controlled device, across repeated runs. I define the metric and baseline before changing code, keep device and thermal conditions comparable, and inspect traces when a number moves. For a product list that janks, I would measure scroll frames and allocations, then separate image decode, composition/layout and data transformation costs. I would not claim a JVM microbenchmark or one fast emulator run proves production improvement on low-end phones. After optimizing, I rerun correctness and accessibility checks as well: a faster list that drops content descriptions or changes item identity is not a successful release.”

## How to answer in the interview

- **Why:** visual, compilation and runtime performance regressions need different evidence.
- **How:** map screenshot, Baseline Profile and Macrobenchmark to one scrolling screen.
- **Trade-off:** richer performance measurement costs devices and repeated runs.
- **Failure case:** one emulator timing number is treated as universal.
- **Production solution:** controlled release-like benchmark plus correctness checks.

## Deep-dive talking points

Prompt for three tool purposes, release-like benchmark, representative profile path and measurement uncertainty.

## Follow-up questions

- [TST-14](../tst-14/): What does screenshot miss? **Answer:** semantic accessibility and business behavior.
- [DSA-14](../dsa-14/): Could a profile fix O(n²)? **Answer:** no; identify algorithmic work separately.

## Self-check rubric

Choose a screenshot golden for layout, a Baseline Profile for hot-path compilation, and Macrobenchmark for startup/frame measurement. Define device, build variant, metric and baseline before claiming an improvement.

## References and reviewed-on date

- [Android Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/overview) — profile purpose.
- [Android Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — measurement guidance.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
