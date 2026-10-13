---
id: "BLD-09"
question: "How do you decide R8 keep rules for reflection, serialization, JNI, and SDKs?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "B"
phase: 4
priority: "P1"
order: 383
editorial_status: "reviewed"
---

# BLD-09

## Original interview question

How do you decide R8 keep rules for reflection, serialization, JNI, and SDKs?

## What the interviewer evaluates

- Identify the exact dynamic entry point and which property must survive.
- Use library consumer rules where the library owns the contract.
- Avoid blanket keeps and validate a minified consumer/release.

## Explanation in Arabic

لا تبدأ بــ`-keep class ** { *; }`. افحص كيف runtime يصل للكود: `Class.forName` يحتاج اسم class وربما constructor، JSON serializer قد يحتاج field names أو generic Signature، JNI قد يربط أسماء methods/classes، وSDK قد تشحن consumer rules جاهزة. حدّد هل المطلوب منع shrinking أو renaming أو الاحتفاظ بعضو/attribute فقط، واكتب أضيق rule. لو المكتبة تملك reflection داخلي، هي مسؤولة عن `consumerProguardFiles`؛ app تضيف قواعد لسلوك خاص بها. اختبر minified release ومسار التحميل الفعلي، وافحص أثر rule على الحجم.

## Practical walkthrough

Keep rules للreflection/JNI/serializer تبنى على contract: أي class/member يُبحث عنه بالاسم runtime؟ راجع vendor rules وR8 usage output، واكتب أصغر rule تسمح بالسلوك. لكل rule test يعمل في minified consumer app، خصوصًا native callbacks وserialized names. rule واسعة تقلل shrinking وتخفي unsupported SDK behavior؛ لا تعتمد على `@Keep` بلا فهم propagation.

## Why it matters and how it works

R8's static reachability cannot infer all runtime string-based lookups. Keep rule options can retain classes, members, names or attributes with different optimization impact. Some serializers use generated adapters and need few rules; reflective serializers may rely on fields and generic signatures. Library authors can package rules so consumers do not need undocumented manual configuration.

## Worked example

A plugin loader reads `com.acme.payment.BankHandler` from configuration and calls a no-arg constructor. Release removes or renames it. Preserve the specific class name and constructor needed by that lookup, then run a minified test that loads it from the same string. Do not keep the entire payment package. For a serializer, inspect its version's documented consumer rules before duplicating them.

## Trade-offs and decision criteria

Broad rules are easy but cost size and optimization. Replacing reflection with generated/explicit registration can improve reliability but requires SDK or architecture change. Narrow rules need tests because a missing constructor or attribute can still fail at runtime. Prefer upstream SDK rules when available and current.

## Failure modes

A class is kept but its required name changes. Fields survive but generic `Signature` is removed. JNI method lookup fails on one ABI. An SDK ships an overbroad rule that retains the whole app graph. A debug-only test misses all of these.

## Production perspective

Inventory dynamic entry points, rule owner and supporting tests. Build the actual minified variant, inspect R8 configuration/usage reports, and review rule size impact during SDK upgrades.

## Interview answer — short

“I derive each keep rule from a concrete dynamic lookup, preserve only required classes/names/members/attributes, and prove it with a minified runtime test.”

## Interview answer — structured

“I ask exactly what R8 cannot see. A string-based class load may need a name and constructor; reflective JSON may need fields and signatures; JNI needs its lookup contract. Then I add the narrowest rule that protects those requirements. SDK-internal reflection belongs in its consumer rules, while app-owned dynamic behavior belongs in the app. I run the minified release path and inspect retained code; a broad blanket keep is not a quality fix.”

## Interview answer — deep senior

“A keep rule should document a runtime dependency invisible to static analysis. I reproduce the minified failure and identify the lookup mechanism: `Class.forName` by string, serializer field name or generic metadata, native method registration, or an SDK callback factory. Each needs a different retention property. Keeping a class object does not necessarily preserve the name or every constructor; keeping names indiscriminately can block useful optimization. I consult the installed library version's consumer rules first, because SDK authors should ship rules for their own internals. If the app owns the reflection, I write a targeted app rule and add a release variant test that exercises that exact lookup with R8 enabled. For a serializer I prefer generated adapters when practical and inspect whether attributes or field names are required. I use R8 usage/configuration reports and APK size to check the rule is not needlessly broad. The rule is reviewed when SDK versions change, because dynamic contracts and R8 behavior can evolve.”

## How to answer in the interview

- **Why:** static optimizer cannot infer every dynamic lookup.
- **How:** identify reflective entry and protect needed names.
- **Trade-off:** targeted safety versus app size.
- **Failure case:** renamed JNI method crashes one device.
- **Production solution:** test minified integration path.

## Deep-dive talking points

Discuss name/member/attribute retention, library ownership, generated alternatives, precise tests and optimization cost.

## Follow-up questions

- Is keeping a class equivalent to preserving every member name? **Answer:** no; rule options and member specifications determine the exact guarantee.
- Who owns SDK-internal rules? **Answer:** preferably the SDK author through consumer configuration.
- Why test with minification? **Answer:** debug may not run the reachability and renaming transformations causing the failure.

## Self-check rubric

Trace one dynamic lookup, specify what must survive, and verify a narrow rule in release.

## References and reviewed-on date

- [R8 keep rule overview](https://developer.android.com/topic/performance/app-optimization/keep-rules-overview) — rule semantics.
- [Keep rule examples](https://developer.android.com/topic/performance/app-optimization/keep-rule-examples) — reflection cases.
- [Optimization for libraries](https://developer.android.com/topic/performance/app-optimization/library-optimization) — consumer rules.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Exact rule syntax depends on the runtime lookup.
