---
id: "MOD-12"
question: "How do version catalogs and convention plugins reduce config duplication?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 365
editorial_status: "reviewed"
---

# MOD-12

## Original interview question

How do version catalogs and convention plugins reduce config duplication?

## What the interviewer evaluates

- Distinguish centralized dependency coordinates from reusable build logic.
- Explain one-source configuration with override/variant limits.
- Verify changes on actual modules and avoid hiding complexity.

## Explanation in Arabic

Gradle version catalog (`libs.versions.toml`) تجمع aliases للنسخ والإحداثيات، فتقلل تكرار strings وتسهّل رؤية اختلاف versions. لكنها لا تعني أن كل dependency تُضاف لكل module تلقائيًا. Convention plugin يطبق إعدادات متكررة مثل Android/Kotlin plugin، Java target، test setup، lint، Compose configuration على مجموعة modules، بدل copy-paste في كل `build.gradle.kts`. كلاهما يحتاج ownership وtests: تحديث plugin قد يؤثر في كل feature، وcatalog لا تحل version compatibility آليًا. تجنب plugin ضخمة فيها behavior خفي لكل الحالات.

## Why it matters and how it works

Catalog aliases centralize dependency and plugin coordinates for a multi-project build. Convention plugins package Gradle configuration logic as reusable, typed build logic and make module scripts smaller. A change to a shared convention or catalog can fan out across the graph, so its compatibility and performance impact should be checked with representative modules and variants.

## Worked example

`:feature:orders` applies `company.android.feature` and declares `implementation(libs.androidx.lifecycle.runtimeCompose)`. The convention sets Android/Kotlin toolchain, common test tasks and Compose options once; the catalog pins coordinates. A payment SDK remains a direct dependency of checkout rather than being added by the generic convention to all features.

## Trade-offs and decision criteria

Centralization reduces drift but can create a high-impact change point. Separate narrow conventions for library, feature and app modules rather than one plugin with many conditionals. Catalogs improve discoverability, yet version conflicts still require dependency insight and compatibility tests.

## Failure modes

Every module applies a giant convention that brings unnecessary plugins and slows configuration. A catalog alias is updated without checking AGP/Kotlin compatibility. A feature adds a needed direct dependency only to the catalog, so compile still fails. Build logic silently overrides a module's release settings.

## Production perspective

Version build logic, review catalog updates, run a representative module and full app variant in CI, and profile configuration time. Document supported override points and keep module scripts declarative.

## Interview answer — short

“Version catalogs centralize dependency coordinates; convention plugins centralize repeated Gradle behavior. Together they reduce drift, provided shared changes are tested across modules.”

## Interview answer — structured

“A catalog gives one alias and version source for libraries/plugins, while a convention plugin applies reusable configuration such as Android/Kotlin targets, Compose and test defaults. Modules still declare which libraries they need. I make conventions narrow enough that a payment SDK does not leak into every feature, and I test app variants after updating shared build logic because one change can affect the whole graph.”

## Interview answer — deep senior

“I separate data from behavior in the build. `libs.versions.toml` names versions and dependency coordinates, making it easier to audit or upgrade them consistently. It does not decide that every module depends on a library, nor does it solve binary incompatibility by itself. Convention plugins encode repeated build behavior—Android library settings, Kotlin target, Compose compiler setup, test configuration and lint policy—so feature scripts can state their intent instead of copying dozens of lines. I prefer several focused plugins, such as android-feature and android-library, over a single plugin with hidden feature flags. A shared convention is also a high-fan-out code path: an accidental signing or minification change can affect every release module. I maintain tests or sample-project checks for build logic, assemble relevant variants in CI and measure configuration time after refactors. Specific SDK dependencies remain declared where used, and override points are documented. This reduces drift while keeping the actual module graph visible.”

## Deep-dive talking points

Compare catalog aliases, convention behavior, direct dependencies, build logic tests and configuration cost.

## Follow-up questions

- Does adding an alias install a dependency everywhere? **Answer:** no; a module must declare use or a convention deliberately adds it.
- What belongs in a convention plugin? **Answer:** stable repeated build configuration for a coherent class of modules.
- What risk comes with centralization? **Answer:** one bad shared change can affect many modules and variants.

## Self-check rubric

Show one catalog alias and one convention, name a direct module dependency, and define CI evidence.

## References and reviewed-on date

- [Gradle version catalogs](https://docs.gradle.org/current/userguide/version_catalogs.html) — aliases and versions.
- [Gradle convention plugins](https://docs.gradle.org/current/userguide/sharing_build_logic_between_subprojects.html) — reusable build logic.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Plugin API compatibility depends on the project's Gradle and AGP versions.
