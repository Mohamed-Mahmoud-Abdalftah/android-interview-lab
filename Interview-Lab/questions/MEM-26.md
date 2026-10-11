---
id: "MEM-26"
question: "How would you create measurable performance budgets and regression tests?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "C"
phase: 1
priority: "P1"
order: 81
editorial_status: "reviewed"
---

# MEM-26

## Original interview question

How would you create measurable performance budgets and regression tests?

## What the interviewer evaluates

- Define user-journey metrics, device cohorts, conditions, and tail thresholds.
- Combine deterministic benchmarks with field monitoring and explicit correctness gates.
- Avoid flaky absolute thresholds on shared CI hardware or gaming the first-frame metric.

## Explanation in Arabic

Performance budget يعني اتفاق قابل للقياس: مثل cold-start `TTID` و`TTFD`، نسبة slow frames في scroll، peak memory بعد 10 دورات، وANR/OOM rate في production. حدد الجهاز أو فئة RAM، build قريب من release، حجم البيانات، حالة cache/network، وعدد runs؛ وإلا الرقم مش قابل للمقارنة. استعمل Macrobenchmark للرحلات الكبيرة وMicrobenchmark لدالة محددة، واحتفظ بالـtraces عند regression. في CI تجنب حد جامد شديد الحساسية على hardware مش ثابت؛ استخدم أجهزة مخصصة أو حد/اتجاه إحصائي مع إعادة تأكيد. لازم تحافظ على صحة النتيجة: تقليل وقت أول frame مع إخفاء المحتوى أو تأخير auth لا يعتبر نجاحًا.

## Why it matters and how it works

A budget turns “fast enough” into a repeatable product contract. Startup, rendering, memory, energy, and stability have different units and populations. Macrobenchmark runs app-level journeys and emits metrics/traces; unit or Microbenchmark tests isolate small algorithms. Field signals reveal devices and behavior the lab may miss. Compare distributions and tail values, not only a best run, and treat a regression as a hypothesis for investigation rather than automatically suppressing a failing threshold.

## Worked example

For a catalog app, set a documented budget for cold TTID and meaningful product-grid readiness on a mid-range physical device; set slow-frame percentile for a scripted 100-row scroll and a post-navigation retained-memory ceiling. Run controlled Macrobenchmark repetitions on a release-like build with fixed offline fixture data, archive traces, and compare against a baseline. An illustrative budget might alert on a material p95 regression rather than a 1 ms difference; actual thresholds must come from measured product baselines, not this example.

## Trade-offs and decision criteria

Strict fixed thresholds are easy to gate but can be flaky across thermals or CI machines; statistical comparison and dedicated devices reduce noise. A broad field percentile reflects users but changes with device mix, so segment cohorts. More metrics improve coverage but increase maintenance; prioritize critical journeys and explicit ownership. A test that warms caches may be valid for warm use but cannot substitute for cold-start coverage.

## Failure modes

An emulator test on a shared runner fails randomly due to host load. A team optimizes TTID by drawing a blank shell while TTFD regresses. A memory test compares snapshots before GC in one build and after GC in another. A budget omits low-RAM devices where OOMs occur. Tests should specify setup, cleanup, process state, compilation, dataset, and acceptable variance.

## Production perspective

Establish baseline distributions from controlled devices and Android vitals cohorts. Version the benchmark journeys with feature changes and archive trace artifacts for failures. Gate clear regressions, investigate ambiguous ones, and verify a fix in staged rollout by release and device tier. Pair performance budgets with correctness assertions for rendered data, auth, and navigation.

## Interview answer — short

“I define budgets per user journey and device cohort, measure repeatably with release-like benchmarks, and monitor field tail metrics. The tests also assert the screen remains correct and usable.”

## Interview answer — structured

“I choose a few critical journeys—cold launch, product scroll, checkout—and define metrics such as TTID, fully drawn readiness, slow frames, and peak/retained memory. Each budget specifies device, build, dataset, process/cache state, repetitions, and percentile, so comparisons mean something. Macrobenchmark provides end-to-end measurements and traces; smaller benchmarks isolate algorithms. I use stable physical-device CI where possible and account for run variance rather than failing on tiny noise. I validate user-visible correctness and watch Android vitals after rollout because lab results cannot represent every device.”

## Interview answer — deep senior

“A useful budget is a contract for a real interaction, not a single global millisecond number. I select critical user journeys and define both initial and meaningful readiness for startup, frame-tail metrics for interaction, and memory footprint or retention after repeated navigation. I specify device tier, refresh rate, build variant, compilation state, cache and network setup, dataset, repetitions, and statistical comparison. Macrobenchmark and traces catch whole-app regressions; Microbenchmark helps isolate a hot function, while correctness UI tests ensure an optimization did not skip content, auth, or state restoration. Dedicated physical devices reduce CI noise; ambiguous threshold crossings trigger investigation rather than arbitrary threshold inflation. I segment production vitals by release and device class, then compare staged rollout outcomes to the controlled benchmark. The budget evolves with product flows but every change has an explicit reason and evidence.”

## Deep-dive talking points

Discuss journey selection, TTID/TTFD, frame tails, reproducibility, CI noise, correctness assertions, and field cohort comparison.

## Follow-up questions

- Why measure p95 rather than only average? **Answer:** tail regressions can affect many real users while the mean hides slow outliers.
- Why can a strict emulator threshold be flaky? **Answer:** shared host load and thermal or scheduling variability change measurements independently of code.
- Can TTID alone be the startup budget? **Answer:** no; first frame can be blank while meaningful content or interaction is still delayed.

## Self-check rubric

Specify a journey and metric, control the environment, handle variance, retain correctness gates, and verify field impact.

## References and reviewed-on date

- [Macrobenchmark overview](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — full-journey tests and traces.
- [Measure app performance](https://developer.android.com/topic/performance/measuring-performance) — metric selection and tracing.
- [Android vitals](https://developer.android.com/games/optimize/vitals) — field quality signals.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Thresholds in the example are illustrative and not project measurements.
