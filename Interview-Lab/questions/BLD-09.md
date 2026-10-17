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

## Concept and technical explanation

Authoring production R8 keep rules balances runtime safety against aggressive code and resource reduction:
- Core Guiding Principle: Keep rules must be surgical. Sweeping wildcards (e.g., -keep class com.mycompany.** { *; }) defeat tree-shaking, re-introduce dead code, and bloat the final DEX.
- Reflection & Serialization:
  * Prefer Compile-Time Code Generation: Modern pipelines replace reflection serializers with Kotlinx Serialization (@Serializable) or Moshi with code generation (@JsonClass(generateAdapter = true)), completely eliminating reflection keep rules.
  * Surgical Rules for Reflection: When using Gson or reflective parsers, preserve only fields via -keepclassmembers class com.example.models.** { <fields>; }, allowing R8 to obfuscate and optimize class names and unused constructors.
- JNI Native Integration:
  * Preserve native method declarations via -keepclasseswithmembernames class * { native <methods>; }.
  * Protect Java/Kotlin classes and callback methods invoked from C++ via explicit @Keep annotations.
- Third-Party SDKs & Dependencies:
  * Rely on bundled consumerProguardFiles packaged within official AARs.
  * Avoid manual SDK keep rules unless an unmaintained library lacks consumer declarations.

## Practical walkthrough (English)

Surgical keep rules and compile-time annotations:
```kotlin
// 1. Preferred modern approach: Compile-time serialization (Zero ProGuard rules needed!)
@Serializable
data class UserDto(val id: String, val username: String)

// 2. Direct code annotation via @Keep
@Keep
class NativeBridgeCallback {
    fun onNativePayloadReceived(data: ByteArray) { /* Invoked from C++ */ }
}

// 3. Surgical proguard-rules.pro:
// Preserve native method signatures globally
-keepclasseswithmembernames class * {
    native <methods>;
}

// Preserve only JSON fields for legacy reflective models (allow class renaming)
-keepclassmembers class com.example.legacy.models.** {
    <fields>;
}

// Preserve enum values() and valueOf() methods
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```

## Explanation in Arabic

كيف تحدد وتكتب قواعد R8 Keep Rules الدقيقة لنماذج الـ Reflection، والـ Serialization، والـ JNI، ومكتبات الـ SDKs دون إفساد تقليص حجم التطبيق؟

1. أنواع أوامر الـ Keep في ProGuard/R8:
   - **`-keep`**: يحافظ على الكلاس وجميع أعضائه بالاسم الأصلي ويمنع حذفه وتشويشه كلياً (يستخدم بحذر شديد).
   - **`-keepclassmembers`**: يحافظ على أعضاء الكلاس (Fields/Methods) فقط إذا كان الكلاس نفسه مستخدماً في الكود، مما يسمح بحذف الكلاس إذا كان غير مستخدم.
   - **`-keepnames`**: يسمح بتقليص وحذف الكلاس إذا لم يكن مستخدماً، لكن إذا تم استخدامه يُمنع تغيير اسمه الأصلي.

2. القواعد الدقيقة لكل مجال:
   - **الـ Serialization (DTOs)**: نحتاج فقط للحفاظ على أسماء الحقول (Fields) وليس كل الكلاس: `-keepclassmembers class com.example.dto.** { <fields>; }`.
   - **الـ JNI (Native Methods)**: نحافظ على الدوال الموسومة بـ `native` والكلاسات التي تحتويها: `-keepclasseswithmembernames class * { native <methods>; }`.
   - **الـ Reflection**: استخدام `@Keep` من مكتبة `androidx.annotation.Keep` مباشرة على الكلاس أو الدالة بدلاً من كتابة قواعد عريضة في ملف ProGuard.

3. الخطيئة الكبرى (Wildcard Poisoning):
   - كتابة `-keep class com.example.** { *; }` تلغي فائدة R8 بالكامل وتعطل الـ Shrinking والـ Optimization للمشروع.

## Practical walkthrough

أمثلة عملية لقواعد ProGuard الاحترافية والدقيقة للمجالات الحساسة:
```text
# 1. حماية كلاسات ودوال الـ Native المربوطة بـ C/C++ عبر JNI:
-keepclasseswithmembernames,includedescriptorclasses class * {
    native <methods>;
}

# 2. حماية حقول نماذج السيريالايزيشن الخاصة بالـ Network DTOs فقط لمنع تشويش الأسماء:
-keepclassmembers,allowobfuscation class * implements java.io.Serializable {
    static final long serialVersionUID;
    private static final java.io.ObjectStreamField[] serialPersistentFields;
}

# 3. حماية الـ Enums من حذف دالتي values() و valueOf() المستخدمتين بالـ Reflection:
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# 4. استخدام @Keep البرمجي كبديل أنظف وأسهل في صيانة الكود:
-keep @androidx.annotation.Keep class * { *; }
-keepclasseswithmembers class * {
    @androidx.annotation.Keep <methods>;
}
```

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

Deciding R8 keep rules requires precision to avoid disabling tree-shaking. Engineers prefer compile-time serialization like Kotlinx Serialization or Moshi codegen to eliminate reflection rules, use targeted keepclassmembers for JSON fields, protect native JNI signatures, and rely on consumerProguardFiles while strictly avoiding broad package-level wildcards.

## Interview answer — structured

Authoring R8 keep rules requires surgically protecting runtime dynamic symbols while preserving maximal dead-code elimination.
First, eliminate reflection where possible. Modern architectures replace reflection-heavy serializers with compile-time code generation such as Kotlinx Serialization or Moshi with generateAdapter, making manual keep rules unnecessary.
Second, for legacy reflection or Gson, use targeted member rules: apply -keepclassmembers to preserve only serializable fields rather than preserving entire classes and methods.
Third, protect native JNI bridges using -keepclasseswithmembernames to preserve methods declared external alongside their associated parameter types and C-callback classes.
Fourth, for third-party SDKs, rely on bundled consumerProguardFiles rather than authoring external rules.
Fifth, enforce strict code review rejecting broad wildcards like -keep class com.**, which disables tree-shaking across thousands of classes.

## Interview answer — deep senior

In enterprise Android codebases, poorly authored ProGuard and R8 rules represent one of the fastest paths to binary bloat and technical debt.
A common anti-pattern when encountering a release crash is adding a sweeping wildcard like -keep class com.company.** { *; }.
This brute-force approach immediately disables tree shaking, dead code elimination, and obfuscation across the entire package, defeating the core benefits of R8 and bloating DEX size.
Senior engineers adhere to a principled hierarchy.
Our first strategy is replacing runtime reflection with compile-time code generation.
By migrating from Gson to Kotlinx Serialization or Moshi with KSP code generation, serializers generate explicit adapter classes during compilation, completely removing the need for reflection keep rules.
When reflection is unavoidable—such as interacting with legacy backend DTOs—we write surgical rules: -keepclassmembers class com.example.dto.** { <fields>; }.
This preserves the field names required for JSON key mapping while allowing R8 to obfuscate and optimize class names, constructors, and unused helper methods.
For native C++ integration, we configure -keepclasseswithmembernames class * { native <methods>; } and annotate Java callback classes invoked from C++ with @Keep.
Finally, for third-party libraries, we verify that dependencies supply clean consumerProguardFiles, and use R8's configuration artifact to audit that imported rules do not pollute global compilation.

## How to answer in the interview

- **Why:** static optimizer cannot infer every dynamic lookup.
- **How:** identify reflective entry and protect needed names.
- **Trade-off:** targeted safety versus app size.
- **Failure case:** renamed JNI method crashes one device.
- **Production solution:** test minified integration path.

## Deep-dive talking points

Discuss name/member/attribute retention, library ownership, generated alternatives, precise tests and optimization cost.

## Follow-up questions

- **Interviewer:** "What does -whyareyoukeeping do in R8?"
  **Answer:** "It instructs R8 to print the exact dependency path and root keep rule explaining why a specific class was not stripped during shrinking."

- **Interviewer:** "What is the difference between -keep and -keepnames?"
  **Answer:** "-keep prevents both shrinking and obfuscation; -keepnames allows shrinking if unused, but prevents obfuscation if kept."

## Self-check rubric

Trace one dynamic lookup, specify what must survive, and verify a narrow rule in release.

## References and reviewed-on date

- [R8 keep rule overview](https://developer.android.com/topic/performance/app-optimization/keep-rules-overview) — rule semantics.
- [Keep rule examples](https://developer.android.com/topic/performance/app-optimization/keep-rule-examples) — reflection cases.
- [Optimization for libraries](https://developer.android.com/topic/performance/app-optimization/library-optimization) — consumer rules.

Technically reviewed against primary documentation on 2026-10-13.
