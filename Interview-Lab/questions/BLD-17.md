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

تطبيق يُثبت ويعمل بشكل مثالي في بيئة الـ Debug، ولكنه ينهار فور الفتح (Crash on Launch) في بيئة الـ Release بسبب أسماء كلاسات تم تشويشها. كيف تثبت السبب الجذري برهانياً وتصلحه؟

1. إثبات السبب الجذري برهانياً (Step-by-Step Proof):
   - **الخطوة 1: استخراج الـ Crash Stack Trace الأصلي**: تشغيل الـ Release APK عبر ADB وقراءة الخطأ المشوش في Logcat:
     `java.lang.ClassNotFoundException: a.b.c`.
   - **الخطوة 2: فك التشفير عبر `retrace`**: تمرير الـ Stack Trace لـ `retrace mapping.txt` لاكتشاف اسم الكلاس الأصلي (مثلاً `com.example.ui.MainActivity` أو كلاس Fragment).
   - **الخطوة 3: البرهان في `usage.txt`**: فتح ملف `usage.txt`؛ إذا كان اسم الكلاس موجوداً فيه، فهذا إثبات قطعي بأن R8 اعتبره كوداً ميتاً وحذفه.
   - **الخطوة 4: فحص ملف الـ AndroidManifest المدمج**: فتح الـ APK في APK Analyzer وفحص `AndroidManifest.xml`. إذا كان الـ Manifest يشير إلى `com.example.ui.MainActivity` بينما R8 شوش اسم الكلاس إلى `a.b.c`، فهذا يثبت سبب الانهيار فور الفتح.

2. الحل الجذري:
   - إضافة قاعدة Keep Rule صريحة أو استخدام تعليق `@Keep` على الكلاس المستهدف.

## Practical walkthrough

خطوات التحقيق العملي في انهيار تشويش الكلاسات وحله بقاعدة Keep Rule دقيقة:
```bash
# 1. التقاط الـ Crash المشوش من الهاتف:
adb logcat -d *:E | grep -E "FATAL EXCEPTION|ClassNotFoundException"
# المخرجات: Caused by: java.lang.ClassNotFoundException: Didn't find class "com.example.auth.AuthRouter"

# 2. التحقق من ملف usage.txt لإثبات أن R8 حذفه أو شوش اسمه:
grep "com.example.auth.AuthRouter" app/build/outputs/mapping/release/usage.txt
```

```kotlin
// 3. الحل في كود Kotlin بإضافة تعليق @Keep الصريح:
@Keep // يمنع R8 من حذف الكلاس أو تغيير اسمه نهائياً
class AuthRouterImpl : AuthRouter {
    // Implementation
}
```

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

Prove the cause by retrieving the crash from Logcat, retracing it with mapping.txt to identify the original class, confirming its deletion in usage.txt, and inspecting the merged manifest or reflection call site in APK Analyzer. Remediate by applying a targeted @Keep annotation or surgical ProGuard rule.

## Interview answer — structured

Proving and remediating an immediate startup crash caused by obfuscated or stripped classes follows a forensic debugging pipeline.

First, **Capture & Retrace the Exception**. Next, extract the startup crash log via `adb logcat -d *:E`. Run the trace through `retrace mapping.txt`. The deobfuscated trace pinpoints the exact class (e.g. `ClassNotFoundException: Didn't find class com.example.analytics.AppInitializer`).
**Definitive Proof via R8 Diagnostic Reports**. Search for the class inside `app/build/outputs/mapping/release/usage.txt`. If present, R8 explicitly determined it was unreferenced dead code and pruned it from `classes.dex`.
If the class exists in `classes.dex` under an obfuscated name (`a.b.c`), but dynamic instantiation points (e.g., `Class.forName("com.example.analytics.AppInitializer")` or an unmerged manifest entry) look for the original string name, the failure is proven. **Surgical Remediation**.
Decorate the class with `@androidx.annotation.Keep` or add a surgical rule in `proguard-rules.pro`: `-keep class com.example.analytics.AppInitializer { <init>(); }`. Finally, rebuild and verify that the class now appears in `seeds.txt` and the app boots cleanly.


## Interview answer — deep senior

From an architectural systems perspective, startup obfuscation crashes frequently result from Manifest Merging and DI service loading.

First, with ServiceLoader & Provider Reflection, libraries using Java `ServiceLoader` (e.g. Kotlin Coroutines `AndroidDispatcherFactory`, OkHttp platform engines) rely on metadata files inside `META-INF/services/`. If R8 obfuscates the implementing class without rewriting the service provider configuration file, `ServiceLoader` throws runtime initialization exceptions on startup. Configure R8 with `-keepnames` for service provider classes. Next, with Manifest Class Reference Obfuscation, aGP automatically preserves any Activity or Service declared in the application's merged manifest. However, if an activity is declared in an external library manifest that was modified dynamically via manifest placeholders or instantiated via custom classloaders, AGP may miss the reference. Always verify the merged manifest inside `intermediates/merged_manifests/release/`.
Finally, with Automated Release Smoke Testing in CI, before deploying, CI release pipelines must execute an automated monkey test or startup smoke test (`adb shell monkey -p <pkg> 500`) against the signed release APK on an emulator to assert that startup initialization succeeds.


## How to answer in the interview

- **Why:** dynamic lookup can break under R8.
- **How:** reproduce, retrace and isolate exact rule.
- **Trade-off:** quick workaround versus targeted fix.
- **Failure case:** broad keep masks cause.
- **Production solution:** release regression test with narrow rule.

## Deep-dive talking points

Discuss controlled comparison, mapping, usage reports, manifest string, constructor retention and release test.

## Follow-up questions

- **Interviewer:** "Why does AGP automatically keep Activities declared in AndroidManifest.xml?"
  **Answer:** "AGP automatically generates ProGuard keep rules for all component classes referenced in the merged AndroidManifest.xml as compilation entry points."

- **Interviewer:** "What is the difference between ClassNotFoundException and NoClassDefFoundError?"
  **Answer:** "ClassNotFoundException occurs when dynamic loading (Class.forName) fails to find the class; NoClassDefFoundError occurs when a class was present at compile time but missing from the runtime classpath."

## Self-check rubric

State hypothesis, collect exact-artifact evidence, change one rule and verify minified startup.

## References and reviewed-on date

- [R8 keep rule examples](https://developer.android.com/topic/performance/app-optimization/keep-rule-examples) — reflection and naming.
- [Recover stack traces](https://developer.android.com/tools/retrace) — mapping evidence.

Technically reviewed against primary documentation on 2026-10-13.
