---
id: "BLD-08"
question: "How do you debug crashes that occur only in release builds?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "B"
phase: 4
priority: "P1"
order: 382
editorial_status: "reviewed"
---

# BLD-08

## Original interview question

How do you debug crashes that occur only in release builds?

## What the interviewer evaluates

- Reproduce exact variant/artifact and recover original stack trace.
- Isolate R8, manifest, signing, resources and runtime config systematically.
- Fix root cause with a targeted change and release regression test.

## Explanation in Arabic

كيف تستكشف وتصلح الانهيارات (Crashes) التي تحدث فقط في نسخة الـ Release بينما يعمل التطبيق بشكل مثالي في بيئة الـ Debug؟

1. الأسباب الجذرية لانهيارات الـ Release-Only:
   - **تقليص أو حذف كود مستخدم بالـ Reflection (R8 Stripping)**: استدعاء كلاس أو دالة ديناميكياً؛ R8 لا يرى أي استدعاء مباشر فيعتقد أنها Dead Code ويحذفها، فتحدث `ClassNotFoundException` أو `NoSuchMethodException`.
   - **تشويش أسماء حقول الـ Serialization**: مكتبات مثل GSON أو Moshi تبحث عن أسماء الحقول في الـ JSON (مثل `user_id`). بعد التشويش، يتغير اسم الحقل في الـ DEX إلى `a`، فتفشل السيريالايزيشن أو تصبح كل الحقول `null` مما يسبب `NullPointerException`.
   - **حذف كود الـ JNI / Native Code**: دوال الـ Native التي تستدعي كود Java بالاسم الصريح تفشل بعد التشويش.
   - **تقليص الموارد (Resource Shrinking)**: استخدام `resources.getIdentifier("icon_" + name, "drawable", packageName)`؛ R8 يعتقد أن الصورة غير مستخدمة ويستبدلها بملف تالف.

2. كيفية إعادة إنتاج المشكلة محلياً (Reproducing Locally):
   - **إنشاء Build Type مخصص للتشخيص (`releaseTest` أو `benchmark`)**: يحتوي على `isMinifyEnabled = true` ولكن مع `isDebuggable = true` و `signingConfig = debug` لتشغيل الـ Debugger وفحص الـ Stack Trace مباشرة.

3. أدوات التحقيق في مخرجات R8:
   - فحص ملف `usage.txt` (الموجود في `build/outputs/mapping/release/`): يسرد كل الكلاسات والدوال التي حذفها R8 لمعرفة ما إذا كان الكلاس المنهار قد تم حذفه بالخطأ.

## Practical walkthrough

إنشاء Build Type هجين محلياً لاكتشاف مشاكل R8 واستخدام ملفات seeds.txt و usage.txt:
```kotlin
// في build.gradle.kts: إنشاء نوع بناء مخصص يماثل الـ Release تماماً ولكن يقبل الـ Debugger:
android {
    buildTypes {
        create("debugMinified") {
            initWith(getByName("release"))
            // تمكين الـ Debugging مع الحفاظ على نفس قواعد R8 والـ Obfuscation:
            isDebuggable = true
            signingConfig = signingConfigs.getByName("debug")
            matchingFallbacks += listOf("release")
        }
    }
}
```

```bash
# أوامر تشخيص مخرجات R8 عبر الـ CLI:
# 1. معرفة الكلاسات التي حذفها R8 وظن أنها غير مستخدمة:
grep "com.example.model.UserProfile" app/build/outputs/mapping/release/usage.txt

# 2. معرفة الكلاسات التي حافظ عليها R8 بناءً على الـ Keep Rules:
grep "com.example.model.UserProfile" app/build/outputs/mapping/release/seeds.txt
```

## Why it matters and how it works

Release builds combine different build type settings, often including shrinking, obfuscation, signing and variant resources. The mapping file translates obfuscated frames for one exact build. A crash can originate from dynamic code reachability, missing configuration, manifest merge or native packaging, so an R8 assumption alone is insufficient.

## Worked example

`ClassNotFoundException: com.acme.checkout.ProviderCheckoutActivity` appears only on release checkout launch: an SDK asks `Class.forName` for that configured name. Retrace the obfuscated *stack frames* with the matching map to find the failing caller; then inspect the mapping and R8 usage report to see whether the target was renamed or removed. A narrow rule preserving the required class name and constructor, or a corrected SDK rule, restores the lookup. A minified checkout smoke test prevents recurrence.

## Trade-offs and decision criteria

Disabling R8 can confirm a hypothesis quickly but sacrifices release size/performance and may hide other issues. Broad keep rules speed triage but obscure the true contract. Reproducing via Play internal track costs more time yet covers distribution and signing paths unavailable in a local universal APK.

## Failure modes

A wrong mapping file yields misleading frames. Debug-only credentials or provider authorities hide a release manifest issue. Crash reproduction uses unminified `release` variant and misses R8. A native library is missing only for x86 but testers use arm64. Team ships a blanket keep rule without a regression test.

## Production perspective

Archive mapping and artifact hashes, reproduce from the exact distribution path, document the causal failing boundary, and add a release variant test. Monitor crash-free users by version/ABI during staged rollout.

## Interview answer — short

Debug release-only crashes by creating a debuggable minified build type (isDebuggable = true with isMinifyEnabled = true), deobfuscating the stack trace with retrace and mapping.txt, and checking usage.txt to verify if R8 stripped reflection, serialization, or JNI entry points.

## Interview answer — structured

Release-only crashes almost universally stem from bytecode optimizations, identifier obfuscation, or tree shaking executed by R8.

First, **Common Failure Vectors**. Next, with Reflection Stripping, classes instantiated via `Class.forName()` or dynamic reflection appear unreachable in static call graphs, causing R8 to strip them (`ClassNotFoundException`).
Additionally, with Serialization Mismatches, reflection-based serializers (GSON) expect exact field names. Obfuscation renames fields to `a`, leaving deserialized objects populated with `null` values. With JNI Breakage, native C/C++ code referencing Java methods via JNI signatures fails when R8 renames or inlines the Java method.
With Dynamic Resource Lookups, using `Resources.getIdentifier()` fails when `shrinkResources = true` strips drawables flagged as unreferenced. **Local Reproduction Strategy**.
Add a hybrid build type (`debugMinified`) that mirrors `release` (`isMinifyEnabled = true`, identical ProGuard rules), but sets `isDebuggable = true` and debug signing. This allows developers to attach Android Studio's debugger and reproduce the exact crash locally. **Investigating R8 Diagnostic Reports**.
Inspect `build/outputs/mapping/release/usage.txt` to confirm if R8 pruned the missing class. Finally, inspect `seeds.txt` to verify whether keep rules successfully preserved intended entry points.


## Interview answer — deep senior

From an advanced compiler engineering perspective, release-only crashes also involve timing and aggressive method inlining.

First, with Aggressive Method Inlining & Class Merging, with `proguard-android-optimize.txt`, R8 merges single-implementation interfaces directly into concrete classes and inlines short methods. If an SDK inspects the runtime class hierarchy or checks `instanceof` on merged interfaces, type casting exceptions (`ClassCastException`) arise exclusively in release builds. Next, with Concurrency & Timing Discrepancies, release builds run significantly faster than debug builds because debug assertions are eliminated and bytecode is optimized. Race conditions or thread safety defects in asynchronous Coroutines that were masked by debug overhead can surface as timing bugs in optimized release binaries.
Finally, with Deobfuscating Production Traces, when diagnosing in the field, run Google's `retrace` CLI locally with the matching `mapping.txt`: `retrace mapping.txt obfuscated_trace.txt`. Ensure CI archives `mapping.txt` as a required build artifact for every released version code.


## How to answer in the interview

- **Why:** debug and release differ materially.
- **How:** reproduce exact variant and symbolicate.
- **Trade-off:** containment speed versus diagnosis.
- **Failure case:** wrong mapping leads false stack.
- **Production solution:** halt rollout and add release gate.

## Deep-dive talking points

Cover matching mapping, artifact provenance, split reproduction, differential diagnosis, R8 reports and rollout telemetry.

## Follow-up questions

- **Interviewer:** "What is the difference between seeds.txt and usage.txt?"
  **Answer:** "seeds.txt lists all classes and members preserved by keep rules; usage.txt lists all code stripped by R8 as dead code."

- **Interviewer:** "Why does GSON fail more often in release builds than Moshi with codegen?"
  **Answer:** "GSON uses runtime reflection requiring broad keep rules; Moshi with KSP generates explicit adapter classes at compile time, eliminating reflection lookups."

## Self-check rubric

Identify artifact, retrace, test release differences and close with a regression check.

## References and reviewed-on date

- [Recover obfuscated stack traces](https://developer.android.com/tools/retrace) — mapping and retrace.
- [Build and test an App Bundle](https://developer.android.com/guide/app-bundle/test) — release split testing.

Technically reviewed against primary documentation on 2026-10-13.
