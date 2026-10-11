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

Screenshot tests تقارن pixels عشان visual regressions؛ Baseline Profiles تحدد hot code paths عشان Android Runtime يجهزها للتنفيذ أسرع؛ Macrobenchmark يقيس startup/scrolling/frames على device مع setup ثابت. دي أدوات مختلفة: screenshot مش accessibility test، وprofile مش benchmark، وbenchmark debug build مش دليل على release performance.

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

“I define the performance hypothesis first. If product-list scrolling freezes, I benchmark frame timing and trace CPU/allocation behavior on low-end hardware, then optimize and rerun. A Baseline Profile may help cold startup or first-use compilation costs but will not fix an O(n²) filter or heavy image decode. I keep screenshot goldens for visual regression across relevant themes/locales and semantics tests for accessibility. CI/performance labs pin device and build conditions and compare distributions, with controlled review for noisy changes. Run Macrobenchmark before/after. ”

## Deep-dive talking points

Prompt for three tool purposes, release-like benchmark, representative profile path and measurement uncertainty.

## Follow-up questions

- [TST-14](../tst-14/): What does screenshot miss? **Answer:** semantic accessibility and business behavior.
- [DSA-14](../dsa-14/): Could a profile fix O(n²)? **Answer:** no; identify algorithmic work separately.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/overview) — profile purpose.
- [Android Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — measurement guidance.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
