---
id: "BLD-17"
question: "An app installs in debug but crashes on launch in release due to renamed classes. How do you prove the cause?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "C"
phase: 4
priority: "P1"
order: 391
editorial_status: "reviewed"
---

# BLD-17

## Original interview question

An app installs in debug but crashes on launch in release due to renamed classes. How do you prove the cause?

## What the interviewer evaluates

- Form a falsifiable R8 hypothesis and reproduce exact release artifact.
- Use mapping, R8 reports and controlled build comparison.
- Fix a precise dynamic contract, not blanket disable optimization.

## Explanation in Arabic

ابدأ بالـcrash stack وartifact/version/variant، ثم retrace بالماب المطابقة. لو `ClassNotFoundException` أو reflection/JNI load في launch، افحص class name المتوقع وهل R8 أزال/غيّر الاسم؛ راجع `mapping.txt`, `usage.txt` وmerged rules. تجربة release مؤقتة بدون minify قد تدعم الفرضية، لكنها ليست إثباتًا وحدها لأن builds اختلفت أيضًا. أثبت بإعادة إنتاج crash في minified artifact، إضافة keep rule دقيقة أو إصلاح SDK، ثم تشغيل نفس launch path بنجاح مع R8. احتفظ بتغطية release startup في CI.

## Why it matters and how it works

Debug builds often omit R8 transformations, while release may rename or remove classes reached by string lookup. Mapping identifies renamed symbols and usage reports help show removed code. A controlled change to the exact dynamic entry point, with other inputs held constant, establishes causality more strongly than a broad switch that changes many build properties.

## Worked example

An SDK reads `com.example.app.StartupPlugin` from manifest metadata and calls `Class.forName`. Debug launches; release throws a class-not-found exception. Retrace and R8 reports show the plugin renamed to `a.b.C`. A narrow rule preserving the configured name and required constructor makes the minified release launch; a test asserts the manifest metadata and runtime lookup together.

## Trade-offs and decision criteria

Disabling R8 speeds diagnosis but increases artifact size and may not be acceptable for release. Broad `-keep` rules are a temporary experiment, not a refined fix. An SDK upgrade or explicit registration can eliminate fragile string lookup, but requires compatibility testing.

## Failure modes

Wrong mapping file points to unrelated class. Team fixes only the class name while constructor is still removed. A debug startup test is claimed to cover release. A global `-dontobfuscate` masks the problem but forfeits optimization. Manifest points to a different class in release source set.

## Production perspective

Archive maps and reports per artifact, include minified release startup test on relevant devices, and review dynamic entry points during SDK upgrades. Monitor staged rollout startup crash rate.

## Interview answer — short

“I reproduce the exact minified release, retrace its crash, inspect R8 mapping/usage and the string lookup, then fix the narrow required name or member and rerun launch.”

## Interview answer — structured

“I do not infer R8 from debug versus release alone. I capture the exact release stack and retrace with its map, inspect the configured reflective class name and R8 output, and compare a controlled minification-off experiment. Then I add a targeted rule or replace the fragile lookup and show the same release launch path passes with minification enabled. CI keeps a startup regression test.”

## Interview answer — deep senior

“To prove causality I control the artifact and the hypothesis. I identify the crashing release variant, version, mapping file and startup exception; an unrelated debug APK is only a comparison. Suppose manifest metadata names a plugin loaded through `Class.forName`. I retrace the release stack and inspect mapping and usage reports to determine whether R8 renamed or removed that configured class or its constructor. I check the merged release manifest too, because an incorrect string there can mimic an R8 issue. I may run a temporary release with minification disabled to narrow the search, but that changes a large set of transformations and is not a final proof. The convincing experiment keeps R8 on and changes only the required dynamic contract—perhaps a targeted rule preserving the class name and constructor, or SDK code that references the class explicitly. If the crash disappears and a minified startup test exercises that lookup, the causal claim is much stronger. I then review rule scope and artifact size, archive mapping with the release, and monitor startup crashes in staged rollout.”

## Deep-dive talking points

Discuss controlled comparison, mapping, usage reports, manifest string, constructor retention and release test.

## Follow-up questions

- Does debug success alone prove R8 caused the crash? **Answer:** no; other variant settings may differ.
- Why keep R8 enabled in the final proof? **Answer:** it tests the actual shipping transformation with a narrow fix.
- Could a kept class still fail? **Answer:** yes; required name or constructor/member may still be changed or missing.

## Self-check rubric

State hypothesis, collect exact-artifact evidence, change one rule and verify minified startup.

## References and reviewed-on date

- [R8 keep rule examples](https://developer.android.com/topic/performance/app-optimization/keep-rule-examples) — reflection and naming.
- [Recover stack traces](https://developer.android.com/tools/retrace) — mapping evidence.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Plugin scenario is illustrative.
