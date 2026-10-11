---
id: SCN-025
lesson_id: AND-003
status: reviewed
code_verification: tested
---
# SCN-025 — Deep link خارجية بتفتح شاشة payment result مباشرة، وPendingIntent mutable بتسمح لجهة تانية

## Symptom and competing hypotheses

<p dir="rtl" lang="ar">Deep link خارجية بتفتح شاشة payment result مباشرة، وPendingIntent mutable بتسمح لجهة تانية تغير extras. المشكلة هنا مش navigation بس؛ دي trust boundary بتدخل process بتاعتك. الفرضيات المنافسة تشمل ownership غلط، state stale، input غير موثوقة، وplatform restriction. ممنوع نختار السبب من قرب log زمني فقط.</p>

## Investigation and correction

<p dir="rtl" lang="ar">Android يحل intent مقابل filters ثم ينشئ أو يعيد route حسب task flags. عند boundary افحص action وscheme وhost وpath والـpayload، وبعدها حوّلها command داخلية typed. ما تعتمدش على UI السابقة إنها عملت validation. الإصلاح: خلّي components غير exported افتراضيًا، واستخدم explicit intents داخل التطبيق. لو boundary لازم exported، وثّق caller/authentication وvalidate كل input. اختبر back stack كـuser journey مش flags منفصلة.</p>

## Tests and rollout

1. Reproduce with one changed dimension at a time.
2. Assert the ordered state transition and the negative path.
3. Stage rollout with a correctness metric and rollback threshold.
4. Redact identifiers and never log tokens, intents, or payloads wholesale.

## Senior follow-ups

1. **What observation would falsify your leading hypothesis?** Choose a trace or state snapshot that the alternative predicts differently.
2. **What is the smallest reversible mitigation?** Disable or route around the proven boundary while preserving evidence.
3. **What remains unverified?** Device and framework behavior until an Android test or production trace runs.
