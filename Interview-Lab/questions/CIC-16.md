---
id: "CIC-16"
question: "How do you handle multiple environments and flavors?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 435
editorial_status: "reviewed"
---

# CIC-16

## Original interview question

How do you handle multiple environments and flavors?

## What the interviewer evaluates

- Flavor/build-type matrix and environment isolation.
- Preventing production credential/endpoint crossovers.

## Explanation in Arabic

Product flavors بتحدد variants زي dev/staging/prod، وbuild types زي debug/release بتحدد debuggability/minification/signing. مش كل combination لازم ينشر. نخلي `applicationId`، backend URL، Play app وsigning policy صريحة ومتحققة في CI؛ لا نحط private secrets في `BuildConfig` لأن APK قابل للفحص.

## Why it matters and how it works

Gradle combines flavor dimensions and build types into variants. Source sets and manifest placeholders can alter permissions, providers and endpoints. CI should inspect the final merged manifest and artifact metadata, not infer from variant name alone.

## Worked example

`prodRelease` targets production host and uses release signing; `stagingRelease` has distinct applicationId and test backend. Before upload, a script reads the built artifact metadata and rejects mismatch between track, package and endpoint.

## Trade-offs and decision criteria

Flavors improve isolation but multiply build/test combinations. Share common code and define a supported variant matrix; run broad tests on production-like minified variant. Backend flags may be simpler than a new flavor for small behavior switches.

## Failure modes

Staging app accidentally uses production payment API with a public test key, or prod app points to sandbox. Validate host and credentials at backend as well as CI; provider account separation limits impact.

## Production perspective

Release checklist records variant, applicationId, signing identity, backend host and Play track. Smoke installs delivered split APK on representative devices.

## Interview answer — short

“I use flavors for environment identity and build types for build behavior, then assert the built applicationId, host, signing and target track before publishing. BuildConfig is not a secret store.”

## Interview answer — structured

“Gradle variants combine flavors and build types, so I define a supported matrix instead of testing every theoretical combination. Staging and production use distinct application IDs and backend/provider accounts. CI checks the merged manifest and actual artifact metadata before upload, and release smoke tests use a minified variant. Private credentials stay server-side; a flavor constant in the APK is public. The mechanics matter. Gradle combines flavor dimensions and build types into variants. Source sets and manifest placeholders can alter permissions, providers and endpoints. CI should inspect the final merged manifest and artifact metadata, not infer from variant name alone. The choice has a trade-off. Flavors improve isolation but multiply build/test combinations. Share common code and define a supported variant matrix; run broad tests on production-like minified variant. Backend flags may be simpler than a new flavor for small behavior switches.”

## Interview answer — deep senior

“I design environment separation as a defense against wrong-target releases. The pipeline validates package name, host, signing certificate and Play app/track as one tuple, then promotes only the intended artifact. Backend also rejects test credentials or tenants in production. I keep feature toggles separate from environment identity so a flag does not create an uncontrolled flavor explosion. Tests run common logic once, variant-specific configuration on each shipped variant, and production-like R8/ABI checks before rollout. Consider a concrete case. `prodRelease` targets production host and uses release signing; `stagingRelease` has distinct applicationId and test backend. Before upload, a script reads the built artifact metadata and rejects mismatch between track, package and endpoint. A failure case illustrates the risk. Staging app accidentally uses production payment API with a public test key, or prod app points to sandbox. Validate host and credentials at backend as well as CI; provider account separation limits impact. In production, the response is concrete. Release checklist records variant, applicationId, signing identity, backend host and Play track. Smoke installs delivered split APK on representative devices. The decision has a trade-off. Flavors improve isolation but multiply build/test combinations. Share common code and define a supported variant matrix; run broad tests on production-like minified variant. Backend flags may be simpler than a new flavor for small behavior switches.”

## Deep-dive talking points

Prompt for variant tuple, merged manifest, test/prod account separation and flavor explosion.

## Follow-up questions

- [CIC-19](../cic-19/): How catch wrong flavor? **Answer:** assert artifact metadata against target track.
- [SEC-31](../sec-31/): Is BuildConfig secret? **Answer:** no, compiled values ship in APK.

## Self-check rubric

Can you explain the mechanism, apply the example, justify a trade-off, identify a failure mode, and answer both follow-ups?

## References and reviewed-on date

- [Android build variants](https://developer.android.com/build/build-variants) — flavors and build types.
- [Android app signing](https://developer.android.com/studio/publish/app-signing) — signing identity.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
