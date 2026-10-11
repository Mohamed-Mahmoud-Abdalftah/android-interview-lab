---
id: "MOD-18"
question: "A shared model change forces recompilation of many modules. How would you shrink the impact?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "C"
phase: 4
priority: "P1"
order: 371
editorial_status: "reviewed"
---

# MOD-18

## Original interview question

A shared model change forces recompilation of many modules. How would you shrink the impact?

## What the interviewer evaluates

- Diagnose high fan-out and public ABI rather than assume Gradle bug.
- Propose stable contracts or smaller ownership boundaries.
- Measure task graph and preserve semantic correctness.

## Explanation in Arabic

افحص build scan/task graph: هل shared model public ABI لعدد كبير؟ هل `api` dependency تصدّر types أوسع من اللازم؟ هل Kotlin inline/generated code يزيد أثر التغيير؟ بدلاً من `CommonUserModel` ضخمة تستخدمها 15 feature، قد تحتاج عقود صغيرة مستقرة (`UserId`, `DisplayName`) وfeature UI models محلية؛ data mapping تحوّل بينها. لا تنسخ domain invariant بين modules لمجرد تسريع compile. قِس قبل وبعد incremental build، وتأكد أن تغيير schema أو serialization ما زال ينتقل للمستهلكين الصحيحين.

## Why it matters and how it works

Changing a type in a high-fan-out API can invalidate downstream compile inputs. `api` edges and public signatures propagate visibility. Breaking one giant shared model into stable domain primitives and local presentation models can localize feature changes, but only if the contracts truly differ. Gradle configuration, annotation processing and resources may still drive work beyond ABI effects.

## Worked example

A `User` model includes account ID, profile image, loyalty tier, payment eligibility and admin flags. Changing a profile field rebuilds checkout and admin modules. Keep account identity and authorization rules in stable owned contracts; let profile and checkout map only needed data into their feature models. Move a library used solely by profile from `api` to `implementation` after public ABI is cleaned.

## Trade-offs and decision criteria

More models and mapping add code but reduce shared API churn and feature coupling. Excessive fragmentation can obscure one authoritative rule. The decision needs both build task evidence and correctness tests; a copied payment eligibility calculation is worse than a slow build.

## Failure modes

`implementation` is used despite public type exposure and consumers fail. Multiple feature copies of authorization policy drift. The model is split by field rather than ownership, creating many unstable micro-APIs. A build-speed conclusion comes from one noisy clean build.

## Production perspective

Track ABI and public API churn of high-fan-out modules, compare representative incremental builds, and test mappings and shared invariants. Use dependency reports and compiler/build scans to locate the actual invalidation path.

## Interview answer — short

“I trace the changed public ABI and exported `api` edges, shrink shared contracts to stable essentials, keep feature models local, and verify incremental build impact.”

## Interview answer — structured

“I use a build scan to see which compile tasks rerun and inspect whether a giant shared model sits in many public signatures. If profile-only fields force checkout to recompile, I separate stable account contracts from feature UI models and map data at boundaries. I check `api` versus `implementation` declarations and codegen/inline effects. I preserve central business invariants and measure controlled incremental builds after the change.”

## Interview answer — deep senior

“I would first prove the cause. A shared model change can alter public ABI, but annotation processing, resources or broad `api` classpaths may also expand work. I compare task graphs from a controlled one-line model change and inspect who imports the type through public signatures. If a `User` object combines profile presentation, payment eligibility and admin flags, every consumer sees changes it does not need. I separate stable identity and policy contracts from feature-specific presentation models, mapping at owned boundaries. I narrow `api` exports to types that genuinely appear in ABI and keep private SDK dependencies as `implementation`. I do not duplicate critical eligibility logic just to improve compilation; one authoritative domain owner still decides it. I test mappings, serialization and behavior in affected features, then rerun warm incremental builds and record compile fan-out and wall time. A smaller API should also make independent feature changes easier, not simply move complexity into dozens of trivial micro-modules. If build scans show code generation rather than the model as the bottleneck, I address that mechanism instead.”

## Deep-dive talking points

Discuss ABI fan-out, `api` leakage, domain versus UI models, mapping cost, build scans and invariant ownership.

## Follow-up questions

- Should payment eligibility be copied into each feature? **Answer:** no; keep one authoritative policy owner.
- What first proves the cause? **Answer:** controlled incremental task graph and public ABI inspection.
- Can changing `api` to `implementation` always fix it? **Answer:** no; public signatures and other build tasks may still require work.

## Self-check rubric

Trace one rebuild chain, redesign a shared model boundary, and verify build and behavior.

## References and reviewed-on date

- [Gradle Java Library Plugin](https://docs.gradle.org/current/userguide/java_library_plugin.html) — compile classpath boundaries.
- [Android modularization guide](https://developer.android.com/topic/modularization) — API and graph design.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Build effect must be measured in the actual repo.
A shared model change forces recompilation of many modules. How would you shrink the impact?
