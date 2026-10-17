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

## Concept and technical explanation

Proving startup crashes caused by R8 class renaming requires an evidence-based forensic investigation:
- Root Cause Analysis:
  1. Reflection & Dynamic Class Loading: Code calling Class.forName("com.example.FeatureRouter") or ServiceLoader.load() with hardcoded string identifiers fails because R8 obfuscated the class to an arbitrary short name (e.g. a.b.c).
  2. Manifest Declarations: Dynamically added or placeholder components whose names diverged between manifest merger and DEX shrinking.
  3. Dependency Injection Service Bridges: Reflection-based factories or serialization adapters missing constructor keep rules.
- Step-by-Step Forensic Proof:
  - Step 1: Capture the crash trace via adb logcat -d *:E. Identify the obfuscated token triggering ClassNotFoundException or NoClassDefFoundError.
  - Step 2: De-obfuscate the stack trace using retrace and the build's exact mapping.txt to retrieve the original fully-qualified class name.
  - Step 3: Inspect usage.txt: If the class is listed, R8 treated it as dead code and removed it entirely. If absent from usage.txt but missing at runtime, R8 renamed it without rewriting the dynamic reflection call site.
  - Step 4: Inspect classes.dex with APK Analyzer or dexdump: Verify the presence, package location, and method signatures of the compiled class.
- Remediation: Apply targeted @Keep annotations or surgical keep rules in proguard-rules.pro.

## Practical walkthrough (English)

Forensic CLI commands and targeted keep annotations:
```bash
# 1. Capture the crash stack trace from device:
adb logcat -d *:E | grep -E "FATAL EXCEPTION|ClassNotFoundException"

# 2. De-obfuscate the crash trace using mapping.txt and Retrace:
retrace.sh -verbose app/build/outputs/mapping/release/mapping.txt crash_log.txt

# 3. Prove whether R8 stripped the class by checking usage.txt:
grep "com.example.router.AuthRouter" app/build/outputs/mapping/release/usage.txt
```

```kotlin
// 4. Surgical fix in Kotlin code:
@Keep // Instructs R8 to preserve class name, members, and constructors
class AuthRouterImpl : AuthRouter {
    // Implementation details
}
```

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

We prove the cause by capturing the startup crash in Logcat, de-obfuscating the trace using mapping.txt and Retrace to identify the target class, and inspecting usage.txt to confirm if R8 pruned it. We inspect DEX contents with APK Analyzer to verify reflection call sites, then apply targeted @Keep annotations to resolve it.

## Interview answer — structured

When an application crashes on launch exclusively in release builds due to renamed classes, senior engineers follow an evidence-based forensic methodology rather than guessing ProGuard rules.
We capture the raw fatal exception from device Logcat. The stack trace typically displays a ClassNotFoundException referencing an obfuscated symbol like a.b.c. We de-obfuscate this trace using Google's Retrace tool paired with the exact mapping.txt generated during that release build, revealing the original fully qualified class name.
Next, we definitively prove the failure mechanism by auditing R8 diagnostic outputs. Searching for the class name in usage.txt confirms whether R8 flagged it as dead code and completely stripped it from the binary. If the class is absent from usage.txt, we inspect the compiled classes.dex using APK Analyzer to verify that the bytecode exists but was renamed, proving that a reflection call site such as Class.forName or a ServiceLoader configuration file failed to resolve the new symbol.
We resolve the defect surgically by applying an explicit @Keep annotation or authoring a targeted ProGuard rule preserving the class and its default constructor, then verify that the class appears in seeds.txt.

## Interview answer — deep senior

From a platform runtime and bytecode architecture perspective, startup obfuscation crashes occur when dynamic reflection boundaries intersect with static compiler optimization.
During compilation, R8 constructs an execution call graph starting from defined entry points, such as Activities declared in the merged AndroidManifest. When classes are instantiated dynamically—through Java reflection, ServiceLoader mechanisms, or custom dependency injection factories—R8 cannot trace the invocation statically. Consequently, R8 either renames the class during obfuscation or prunes it entirely during tree shaking, leading to immediate ClassNotFoundException crashes on application cold start.
To prove this conclusively, our forensic process relies on three diagnostic artifacts. First, mapping.txt maps obfuscated bytecode coordinates back to original source lines. Second, usage.txt provides undeniable proof of dead code stripping; if a class or its default constructor appears there, R8 actively removed it. Third, seeds.txt lists all symbols explicitly protected by keep rules; if the failing class is absent, our configuration failed to protect it.
Additionally, we inspect META-INF services directories inside the APK. Libraries relying on java.util.ServiceLoader require provider configuration files containing the fully qualified class name. If R8 renames the implementing class without rewriting the service provider file, initialization fails silently or crashes on launch.
Surgical remediation requires avoiding broad package wildcards that bloat DEX size. We decorate the specific implementation with AndroidX Keep or add targeted keepclassmembers rules. To prevent these regressions from ever reaching release stages, our continuous integration pipeline executes an automated sanity launch test against the signed release build on emulators before promoting artifacts to store tracks.

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
