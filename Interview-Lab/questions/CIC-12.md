---
id: "CIC-12"
question: "How do you reduce Gradle cold-build and CI execution times?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 431
editorial_status: "reviewed"
---

# CIC-12

## Original interview question

How do you reduce Gradle cold-build and CI execution times?

## What the interviewer evaluates

- Cold-build diagnosis versus configuration and execution improvements.
- Caching correctness and dependency graph.

## Explanation in Arabic

Cold build مفيش cache دافئة، فقياسه مختلف عن incremental build. نعمل Gradle build scan/profile ونقسم الوقت: dependency download، configuration، Kotlin/Java compilation، KSP/KAPT، Android resources، tests. بعد القياس: configuration cache لو compatible، build cache، parallel modules، تقليل annotation processors، وdependencies محلية/locked. مش نفعّل flags عشوائي.

## Why it matters and how it works

Gradle’s configuration cache reuses configuration state when plugins/tasks are compatible; build cache reuses task outputs when inputs are identical. Remote cache helps CI clean agents but must be trusted and correctly keyed. A module graph with unnecessary `api` edges increases recompilation.

## Worked example

A 12-minute cold CI build spends five minutes resolving artifacts and four in KAPT. Add dependency mirror/cache with verification, migrate a supported processor to KSP after measuring, then compare clean-build scans. Keep a no-cache control run to detect false wins.

## Trade-offs and decision criteria

Caches speed repeat builds but cold baseline may stay unchanged. Parallel workers can saturate memory and slow compilation. Modularization may improve selective builds but adds configuration overhead; measure total critical path.

## Failure modes

An invalid remote cache serves stale output or includes secret-bearing artifacts. Use Gradle’s input tracking and trusted cache permissions; never cache signing keystores. A “warm local” benchmark is not a cold CI result.

## Production perspective

Track cold and warm p50/p95, cache hit rate, configuration time and affected-module rebuilds. Roll changes back if correctness or memory use worsens.

## Interview answer — short

“I profile a true cold build, identify the critical task/dependency path, then apply compatible configuration/build caches, dependency and processor improvements with measured before/after results.”

## Interview answer — structured

“I start with build scans on clean CI agents to distinguish download, configuration, compilation, resource processing and test time. Configuration cache and build cache address different phases; remote cache only helps with correct inputs and trusted access. I inspect KAPT/KSP, unnecessary `api` dependencies and module parallelism. I compare p50/p95 cold and incremental builds after each change, not assume a flag improved performance. The mechanics matter. Gradle’s configuration cache reuses configuration state when plugins/tasks are compatible; build cache reuses task outputs when inputs are identical. Remote cache helps CI clean agents but must be trusted and correctly keyed. A module graph with unnecessary `api` edges increases recompilation. The choice has a trade-off. Caches speed repeat builds but cold baseline may stay unchanged. Parallel workers can saturate memory and slow compilation. Modularization may improve selective builds but adds configuration overhead; measure total critical path.”

## Interview answer — deep senior

“A 40-minute build may spend most time queued, downloading dependencies, configuring projects or running devices; Gradle optimization only helps the measured portion. I profile the critical path, then target high-cost tasks and invalidation sources. I validate cache correctness with clean no-cache runs, dependency verification and artifact hashes, and ensure signing material is excluded. Module boundaries and `implementation` exposure can reduce recompilation, but too many modules may increase configuration overhead. I report actual wall-clock improvement and regression risk. Consider a concrete case. A 12-minute cold CI build spends five minutes resolving artifacts and four in KAPT. Add dependency mirror/cache with verification, migrate a supported processor to KSP after measuring, then compare clean-build scans. Keep a no-cache control run to detect false wins. A failure case illustrates the risk. An invalid remote cache serves stale output or includes secret-bearing artifacts. Use Gradle’s input tracking and trusted cache permissions; never cache signing keystores. A “warm local” benchmark is not a cold CI result. In production, the response is concrete. Track cold and warm p50/p95, cache hit rate, configuration time and affected-module rebuilds. Roll changes back if correctness or memory use worsens. The decision has a trade-off. Caches speed repeat builds but cold baseline may stay unchanged. Parallel workers can saturate memory and slow compilation. Modularization may improve selective builds but adds configuration overhead; measure total critical path.”

## Deep-dive talking points

Prompt for cold/warm distinction, configuration versus task cache, processor cost, critical path.

## Follow-up questions

- [CIC-20](../cic-20/): What if tests dominate? **Answer:** optimize/shard tests, not Gradle compilation flags.
- [CIC-02](../cic-02/): Why profile pipeline graph? **Answer:** parallel stages change wall-clock critical path.

## Self-check rubric

Can you explain the mechanism, apply the example, justify a trade-off, identify a failure mode, and answer both follow-ups?

## References and reviewed-on date

- [Gradle performance guide](https://docs.gradle.org/current/userguide/performance.html) — profiling and optimization.
- [Gradle configuration cache](https://docs.gradle.org/current/userguide/configuration_cache.html) — compatibility and reuse.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
