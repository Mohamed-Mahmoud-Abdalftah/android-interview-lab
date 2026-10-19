---
id: "CIC-01"
question: "What are CI, Continuous Delivery, and Continuous Deployment?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "A"
phase: 4
priority: "P2"
order: 420
editorial_status: "reviewed"
---

# CIC-01

## Original interview question

What are CI, Continuous Delivery, and Continuous Deployment?

## What the interviewer evaluates

- Define integration, releasability, and automatic production promotion without conflating them.
- Apply the distinction to an Android release with store review and gradual rollout.
- Explain what a green pipeline, signed artifact, test track, feature flag, and rollout halt actually prove.

## Concept and technical explanation

Continuous Integration (CI) means integrating changes frequently into a shared codebase and verifying them automatically so conflicts and regressions surface early. A PR build, static checks, and tests are common implementation choices, not the definition or a guarantee of zero defects.

Continuous Delivery keeps a change in a releasable state through an automated build and verification pipeline. Promoting a candidate to users remains an intentional decision. A team may upload an artifact to an internal track as part of this process, but that exact track, signing method, and human gate are workflow choices rather than universal requirements.

Continuous Deployment automates promotion of passing changes into a production rollout without a per-release human approval. It does not require instantly reaching every user. On Android, store review, staged rollout configuration, and device update adoption mean the pipeline can request or start a rollout without guaranteeing immediate installation on all devices. An automatic rollout needs monitoring, a plan to halt further distribution, and a hotfix path for users who already installed a bad binary. Feature flags can reduce exposure for flag-controlled behavior, but cannot repair a crash before flag evaluation or every binary defect.

## Practical walkthrough (English)

A pull request runs a build and tests: CI. After merging, the pipeline builds a traceable release candidate, tests the release variant, and uploads it to an internal track; a release owner later approves public promotion: continuous delivery. If policy and automated checks instead promote the candidate to a monitored production rollout without a per-release approval, that is continuous deployment, even if the rollout begins with a small cohort. The store still controls review and distribution timing. Record source commit, artifact identity, track, rollout state, and the decision that triggered promotion.

## Explanation in Arabic

`CI` معناها ندمج تغييرات صغيرة باستمرار ونشغّل Build واختبارات آلية عشان Integration Problems تظهر بدري. PR Pipeline طريقة شائعة، لكن Green Build تثبت بس الـ Checks اللي شغّلتها؛ ما تقولش إنها ضمنت خلو التطبيق من Bugs.

`Continuous Delivery` معناها إن عندك Release Candidate قابلة للطرح بعد Pipeline بناء واختبار واضحة، لكن قرار طرحها للناس لسه مقصود ومتحكم فيه. ممكن تبني AAB وترفعها Internal Track ثم Release Owner يوافق على Production، لكن الـ Track وطريقة الموافقة تفاصيل Workflow مش تعريف المفهوم.

`Continuous Deployment` تضيف Automatic Production Promotion بعد Gates محددة من غير موافقة بشرية لكل Release. ده ما يعنيش 100% من المستخدمين في نفس اللحظة: Play Review وStaged Rollout ووصول التحديث للأجهزة لهم توقيتهم. أراقب Rollout وأعرف أوقف توزيع جديد وأجهز Hotfix للي ثبتوا Binary فيها مشكلة. Feature Flag تساعد لو العطل في سلوك تتحكم فيه، لكنها مش زر يصلح أي Crash في Binary.

## Practical walkthrough

PR تشغّل Build وTests: ده CI. بعد Merge تطلع Release Artifact معروفة من Commit محددة، تختبر Release Variant وترفعها Internal Testing، وبعدين صاحب القرار يوافق على Production: ده Continuous Delivery. لو Pipeline بعد Gates تروّج تلقائيًا لـ Monitored Production Rollout من غير Approval لكل إصدار، ده Continuous Deployment حتى لو البداية بنسبة صغيرة. أسجل Artifact Hash وTrack وRollout State وسبب الترقية. Play نفسها ممكن تراجع الإصدار وتوزعه بتوقيت مختلف عن وقت طلبنا.

## Why it matters and how it works

The terms identify who or what decides to promote a verified candidate. CI gives early integration feedback. Delivery keeps a candidate ready for a deliberate release decision. Deployment automates that decision under policy. A signed bundle or internal-track upload alone does not mean production users received it, and a green pipeline only establishes the checks that actually ran.

## Worked example

A release ledger records commit, toolchain, tests, signed AAB hash, internal-track upload, production approval or automatic promotion event, rollout percentage, and incident response. The same build and internal upload can serve either delivery or deployment; the difference is whether the production promotion decision is automated. This is an operational sketch, not a runnable GitHub Actions workflow.

## Trade-offs and decision criteria

Automatic promotion can shorten lead time but needs trustworthy gates, monitored rollout, and response ownership. Manual approval can be appropriate for higher-risk changes but can also delay safe releases. Android distribution is asynchronous, so a halted rollout can limit new exposure but does not remove an already installed bad binary. A server-controlled flag can help for a flaggable feature, not for every startup or migration failure.

## Failure modes

Calling an upload to internal testing a public production deployment. Assuming every green commit is releasable when release-only shrink or signing was never tested. Embedding long-lived store credentials in a workflow or logs. Believing a halted staged rollout rolls back installed apps. Believing a feature flag can fix a crash before the app fetches or reads it.

## Production perspective

Keep an auditable link from source commit to signed artifact and track promotion. Protect signing keys and store credentials, verify the actual release variant, and monitor crashes and key journeys by version during rollout. Define who can halt further distribution, how affected installed clients receive a hotfix, and which server flags can safely reduce exposure. Store review and user update timing remain external to the CI pipeline.

## Interview answer — short

CI integrates changes often and runs automated checks for fast feedback. Continuous Delivery keeps a tested release candidate ready, while promotion to users is an intentional decision. Continuous Deployment automates that production promotion after its gates. In Android, automatic promotion can still use a staged rollout, and Play review and user updates are asynchronous. A green build or internal upload alone does not mean users have the release.

## Interview answer — structured

I separate the release decision. CI catches integration problems early by building and testing frequent changes. Continuous Delivery extends that to a candidate we can release deliberately after the pipeline. Continuous Deployment lets policy and checks make the production promotion automatically, without a human approval for each version.

For an Android app, a PR can run checks, then a merge can produce a traceable release AAB and upload it to internal testing. If a release owner decides when to move that candidate to a public rollout, that is delivery. If passing checks automatically start a monitored production rollout, that is deployment, even if it begins with a small percentage.

Neither approach makes a release instantaneous on user devices. Play review and update adoption have their own timing. If a bad binary reaches users, halting rollout limits further distribution but cannot erase installs. I monitor crashes, preserve a hotfix path, and use a feature flag only for behavior it can actually control. A green pipeline proves its configured checks, not absence of defects.

## Interview answer — deep senior

The key boundary is production promotion. CI is a practice of frequent integration with automated feedback; it does not require one particular CI service or exact PR schedule. Continuous Delivery maintains a verifiable release candidate while a person or business process decides promotion. Continuous Deployment automates that decision after defined gates. The artifact can be built once and promoted through tracks, preserving its identity; rebuilding with different inputs at each stage weakens provenance.

On Android I distinguish pipeline success, store acceptance, rollout start, and installation on devices. They happen at different times. An AAB uploaded to internal testing is not a public release. A staged production rollout can be automated and still count as deployment; no rule says deployment must target 100% immediately. Store review may delay distribution, and users already holding a defective binary need an update or another compatible mitigation. Halting rollout mainly prevents new exposure. A remote feature flag helps only if the failing path is behind a flag that the installed client can read before the failure.

I would validate the release variant, protect signing and store credentials, record commit and signed artifact identity, and monitor crash and business signals by version. Gates should reflect real risks, including release-only shrinking or migrations, rather than only a debug unit-test pass. If policy calls for a manual approval, I call the process delivery. If it calls for automatic production promotion, I call it deployment and still require ownership for rollout monitoring and incident response. The vocabulary makes accountability clear; it is not a maturity ranking.

## How to answer in the interview

Define the production promotion boundary, walk one Android candidate through PR checks, internal testing, and production, then explain store timing, staged rollout, and bad-binary recovery.

## Deep-dive talking points

Release candidate identity; human versus automated promotion; internal versus production track; staged rollout; store review; signed artifact provenance; feature-flag limits; hotfix and monitoring.

## Follow-up questions

- **Interviewer:** "Does deployment mean 100% of users immediately?" **Answer:** "No. Automatic production promotion can begin with a staged rollout; review and device adoption still take time."
- **Interviewer:** "Can halting Play rollout remove a bad version already installed?" **Answer:** "No. It limits new distribution; existing installs need a hotfix or another compatible mitigation."
- **Interviewer:** "Will a remote feature flag fix any release bug?" **Answer:** "Only behavior the installed app can safely gate. A startup crash before flag evaluation needs another recovery path."

## Self-check rubric

Can I identify who decides production promotion, distinguish internal upload from public distribution, and state what a rollout halt and feature flag cannot undo?

## References and reviewed-on date

- [Android publishing overview](https://developer.android.com/studio/publish) — release preparation and distribution.
- [Play Console release and rollout guidance](https://support.google.com/googleplay/android-developer/answer/9859348) — rollout controls.
- [GitHub Actions CI](https://docs.github.com/en/actions/get-started/continuous-integration) — automated verification example.
- [GitHub Actions deployment](https://docs.github.com/en/actions/get-started/continuous-deployment) — deployment workflow and approvals.

Technically reviewed against current primary documentation on 2026-10-19; agent editorial review, not human verification.
