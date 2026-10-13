---
id: "BLD-02"
question: "What are build types, product flavors, variants, and source sets?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "A"
phase: 4
priority: "P1"
order: 376
editorial_status: "reviewed"
---

# BLD-02

## Original interview question

What are build types, product flavors, variants, and source sets?

## What the interviewer evaluates

- Explain dimensions and cross-product composition.
- Describe source-set merge priority and variant-specific tests.
- Avoid confusing debug/release with customer or environment flavor.

## Explanation in Arabic

Build type مثل `debug`/`release` يحدد خصائص البناء كـdebuggable وminification/signing. Product flavor يمثل إصدار منتج/بيئة مثل `demo`/`full` أو `staging`/`prod` ضمن flavor dimensions. Variant هي تركيب build type مع flavor من كل dimension: `demoRelease`. Source sets مثل `src/main`, `src/demo`, `src/release`, `src/demoRelease` توفر code/resources/manifest للتركيب، مع merge priority موثقة. لا تضع secrets حقيقية في flavor source؛ APK قابل للفحص. اختبر release variant التي ستُنشر، وليس debug فقط.

### Practical walkthrough in Egyptian Arabic

Build type مثل debug/release يحدد debuggable/minify/signing، flavor مثل demo/prod يحدد منتج أو بيئة، والvariant حاصل تركيبهما. Source sets لها precedence؛ `src/debug` قد يحوي provider غير موجود في release. في CI اختبر productionRelease نفسه وافحص merged manifest وendpoint. لا تضع secret backend داخل `BuildConfig` وتعتبره آمنًا.

## Why it matters and how it works

AGP creates a variant for each valid combination of build type and flavor dimensions and merges relevant source sets. More dimensions multiply variants and build/CI cost. Variant-specific resources and manifests can override common values according to priority, which affects authorities, endpoints and app labels. Signing and optimization may differ from debug and expose release-only faults.

## Worked example

An app has `demo`/`full` flavor and `debug`/`release` type, yielding four variants. `src/main` has shared UI, `src/demo` supplies demo branding, and `src/fullRelease` supplies a publication-only provider authority. CI checks `fullRelease` merged manifest and minified startup, because `demoDebug` cannot prove the publication artifact.

## Trade-offs and decision criteria

Flavors support meaningful product/environment differences but can cause a variant explosion. Separate runtime configuration from compile-time flavor only when security and operational behavior allow. Repeated source-set overrides make logic hard to trace; keep differences explicit and small.

## Failure modes

A production endpoint is assumed because debug uses it, while release flavor overrides it. A provider authority differs after manifest merge. One dimension multiplies test matrix unexpectedly. A secret is embedded in `src/prod` and extracted from the app. A release-only minification bug is never exercised.

## Production perspective

List supported variants and source-set priorities, test the published combination, inspect merged manifest/resources, and track variant matrix size. Use server-side secrets and protected CI signing, not source-set secrecy.

## Interview answer — short

“Build type controls how an app is built; flavor selects product variation; a variant combines them; source sets supply variant-specific code and resources.”

## Interview answer — structured

“With demo/full flavors and debug/release build types, AGP creates four variants. `src/main` contributes common code, while flavor, build-type and variant source sets override or add specific resources and manifests by priority. I test the exact release variant shipped to users because signing, shrinker and merged manifest can differ from debug. I keep flavor dimensions limited and never treat a prod source set as a secret store.”

## Interview answer — deep senior

“I distinguish two axes. A build type describes build behavior—debuggability, minification, signing and similar settings—while a product flavor describes a product or environment choice within a dimension. AGP combines one choice from each flavor dimension with a build type to produce a variant. Its source sets contribute code, resources and manifests, with more specific variant/build-type/flavor sources overriding common `main` according to documented merge priority. That mechanism is powerful but creates a test matrix: two flavors by two types already makes four artifacts, and another dimension multiplies them. I keep differences as narrow as possible and identify the one actually distributed. A demoDebug test cannot establish that fullRelease has the right provider authority, endpoint, signing or R8 behavior. CI builds and inspects that final variant's merged manifest and launches a minified artifact. I also avoid putting credentials in a prod flavor, because compiled apps can be inspected. The trade-off is product flexibility versus combinatorial build and QA cost.”

## How to answer in the interview

- **Why:** variant combinations change shipped behavior.
- **How:** state build type, flavor and source precedence.
- **Trade-off:** matrix coverage versus build cost.
- **Failure case:** debug-only config hides release gap.
- **Production solution:** assert critical release variant.

## Deep-dive talking points

Discuss cross-product, source-set priority, manifest override, variant explosion, secrets and release tests.

## Follow-up questions

- Is `demoRelease` a build type? **Answer:** no; it is a variant combining demo flavor with release build type.
- Can `src/prod` hide a secret? **Answer:** no; data packaged in a client app can be extracted.
- Which variant should CI smoke-test? **Answer:** the exact one being published, including its merge/shrink settings.

## Self-check rubric

Derive a four-variant matrix, trace one override, and name a release-only failure.

## References and reviewed-on date

- [Configure build variants](https://developer.android.com/build/build-variants) — dimensions and source-set priority.
- [Android build structure](https://developer.android.com/build/android-build-structure) — project layout.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Example variant names are illustrative.
