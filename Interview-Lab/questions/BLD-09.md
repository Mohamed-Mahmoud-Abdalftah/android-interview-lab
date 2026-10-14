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

Formulate R8 keep rules precisely: use -keepclassmembers for serialization DTO fields to retain names without locking the whole class, -keepclasseswithmembernames for JNI native methods, and targeted @Keep annotations for reflection targets, strictly avoiding broad wildcards that defeat shrinking.

## Interview answer — structured

Crafting surgical R8 keep rules preserves runtime functionality while maximizing dead-code elimination and obfuscation.

First, **Serialization Models (DTOs)**. Next, avoid broad `-keep class com.my.model.** { *; }`. Instead, preserve only the field names required by reflection serializers: `-keepclassmembers class com.example.dto.** { <fields>; }`.
Better yet, adopt Kotlinx Serialization or Moshi Codegen with KSP, which generate explicit adapters at compile time and require zero reflection keep rules. **JNI Native Invocations**.
Native C/C++ libraries resolve Java methods using explicit class and descriptor signatures. Preserve all native methods and their parameter types: `-keepclasseswithmembernames,includedescriptorclasses class * { native <methods>; }`. **Reflection Targets**.
Rather than maintaining fragile string patterns in `proguard-rules.pro`, decorate reflection-instantiated classes with `@Keep` (from AndroidX annotations). AGP bundles default rules preserving any class or member annotated with `@Keep`. **Third-Party SDKs**.
Finally, rely on the SDK's bundled `consumerProguardFiles`. Only author manual keep rules for legacy libraries that fail to publish their own consumer rules.


## Interview answer — deep senior

From an architectural code-shrinkage perspective, broad keep rules constitute silent technical debt.

First, with The allowshrinking and allowobfuscation Modifiers, proGuard rules support granular modifier flags. For example, `-keepnames` is equivalent to `-keep,allowshrinking`. It permits R8 to delete the class if unused, but prevents renaming if the class survives. This is ideal for analytics DTOs. Next, with Auditing Rule Impact with -whyareyoukeeping, when investigating why an unused class was unexpectedly retained in the final DEX, inject `-whyareyoukeeping class com.example.UnusedClass` into `proguard-rules.pro`. During build execution, R8 prints the exact chain of reachability references and keep rules that forced its preservation.
Finally, with Automated CI Size Regression Testing, enforce a maximum binary size ceiling in CI. Overly broad keep rules introduced in PRs immediately trigger size alert regressions, enforcing strict scrutiny during code reviews.


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
