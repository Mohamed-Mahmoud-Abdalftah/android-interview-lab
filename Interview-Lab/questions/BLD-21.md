---
id: "BLD-21"
question: "How would you safely roll out and then roll back a bad Android release?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "C"
phase: 4
priority: "P1"
order: 395
editorial_status: "reviewed"
---

# BLD-21

## Original interview question

How would you safely roll out and then roll back a bad Android release?

## What the interviewer evaluates

- Set staged exposure and objective gates before promotion.
- Distinguish halting distribution from downgrading installed users.
- Choose remote mitigation or higher-version fix with provenance.

## Explanation in Arabic

ابدأ internal/closed test للـAAB الفعلية، ثم staged rollout بنسبة صغيرة مع gates محددة مسبقًا: crash-free/ANR، startup، login/payment success، backend errors، حسب حجم العينة. زوّد النسبة تدريجيًا بعد وقت كافٍ، مع owner يملك قرار الإيقاف. لو ظهر bug، أوقف rollout/حلّل scope، واستخدم kill switch/remote config آمنة للميزة إن وجدت. Play قد يتيح halt لإصدار staged أو كامل وفق القناة، لكن هذا لا يزيل النسخة من الأجهزة التي ثبتتها بالفعل. “Rollback” الحقيقي لهؤلاء يحتاج غالبًا forward fix بـversionCode أعلى أو mitigation server-side؛ downgrade عادي ليس خطة موثوقة. راجع migration/data compatibility قبل النشر حتى يمكن التعافي.

## Why it matters and how it works

Staged rollout limits initial exposure and provides telemetry before wider distribution. Halting stops additional delivery under Play controls but does not reverse an already installed binary. Android update ordering by versionCode prevents a lower-code APK from normally replacing a higher one. Server-side flags may disable a risky path rapidly, while critical binary bugs need a signed higher-code release.

## Worked example

Release 431 reaches 5% and increases checkout unknown outcomes. The release owner halts staged rollout, turns off a new optional checkout UI behind a pretested flag, and reconciles pending orders server-side. Engineers retrace crashes with 431 mapping, prepare 432 from pinned toolchain with a regression test, validate internal track, then stage 432 while monitoring payment success and duplicates. Users already on 431 receive an update rather than an attempted downgrade.

## Trade-offs and decision criteria

Slow rollout reduces blast radius but delays delivery; thresholds need sample size and segment checks. A kill switch is fast but only works for behavior designed to be remotely disabled and must not bypass security. A hotfix is slower yet necessary for crashes or migrations. A fully rolled-out halt can change what Play offers to eligible users, but installed users still need a safe path forward.

## Failure modes

Team uses only aggregate crash rate and misses one ABI or country. Rollout expands before enough sessions accrue. A feature flag disables UI but leaves backend writes unsafe. Database migration is irreversible and previous binary cannot read new schema. The team assumes stopping Play rollout uninstalls a bad version.

## Production perspective

Define release gates, on-call owner and halt playbook before launch. Track metrics by version/device/ABI/region, retain mapping and artifact hash, rehearse remote mitigations, and design schema changes for forward compatibility and recovery.

## Interview answer — short

“I stage the exact tested artifact with telemetry gates, halt distribution on a bad signal, mitigate remotely where safe, and ship a higher-version fix for users already installed.”

## Interview answer — structured

“I start with internal/closed testing and a small staged percentage, using predeclared crash, ANR and critical-flow success thresholds segmented by device and ABI. If a gate fails, I halt promotion, identify affected cohorts and use a tested kill switch if it can safely disable the feature. Halting prevents more distribution but does not downgrade users already on the bad build. I prepare a corrected signed artifact with higher versionCode, regression test it, and stage it while watching recovery. Data migration compatibility is part of the plan.”

## Interview answer — deep senior

“A safe rollout begins before the Play percentage slider. I preserve the exact signed AAB tested in an internal track, its mapping file, source/toolchain provenance and a release owner. I define measurable gates for crash-free sessions, ANRs, startup and business flows such as payment success or unknown-outcome rate, with enough sample time and segmentation by app version, ABI and region. I increase staged exposure only when those gates hold. If checkout failures rise at 5%, I halt distribution and preserve incident evidence; a pretested remote flag can disable an optional UI path, while backend reconciliation protects pending writes. I do not claim that halting the rollout removes version 431 from users who installed it. Android normally rejects a lower versionCode as an update, so those users need a higher-code forward fix or safe server-side mitigation. I retrace with 431's map, add a regression test, validate 432 on an internal track and stage it with recovery metrics. Before any release I review database and API migrations for forward/backward compatibility, because an irreversible schema change can make a nominal rollback unsafe. The playbook defines who may halt, communicate and resume.”

## Deep-dive talking points

Discuss gates and sample size, staged halt, installed-user reality, kill switch limits, higher-code fix and migration safety.

## Follow-up questions

- Does halting rollout remove a bad build from installed devices? **Answer:** no; installed users need mitigation or an update.
- Can you simply publish the old lower versionCode? **Answer:** ordinary update ordering blocks that; use a higher-code corrected release.
- What business metric belongs beside crash rate? **Answer:** critical-flow success, such as payment completion and unknown-outcome rate.

## Self-check rubric

Set rollout gates, respond to a failed cohort, distinguish halt from installed-user recovery, and protect data migrations.

## References and reviewed-on date

- [Staged rollouts in Play Console](https://support.google.com/googleplay/android-developer/answer/6346149) — staged halt controls.
- [Halting a fully rolled-out release](https://support.google.com/googleplay/android-developer/answer/16285429) — current Play behavior.
- [Version your app](https://developer.android.com/studio/publish/versioning) — update ordering.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Play controls and rollout policy should be checked against the actual account.
