---
id: SCN-026
lesson_id: AND-004
status: reviewed
code_verification: not_run
---
# SCN-026 — التطبيق بيظهر ANR في release بس، والفريق شايف network logs في نفس الدقيقة فافترض إن الشبكة

## Symptom and competing hypotheses

<p dir="rtl" lang="ar">التطبيق بيظهر ANR في release بس، والفريق شايف network logs في نفس الدقيقة فافترض إن الشبكة السبب. المطلوب تربط trace بالـmain thread والـbinder waits والـlock owner بدل correlation سطحي. الفرضيات المنافسة تشمل ownership غلط، state stale، input غير موثوقة، وplatform restriction. ممنوع نختار السبب من قرب log زمني فقط.</p>

## Investigation and correction

<p dir="rtl" lang="ar">عند ANR ثبت timestamp وprocess وcomponent. اقرأ main-thread stack: CPU loop، monitor contention، binder call، I/O، ولا انتظار future. اتبع lock أو binder للthread المالكة. قارن traces متعددة؛ top frame واحدة ممكن تكون مكان انتظار مش السبب الأصلي. الإصلاح: خلي blocking boundary main-safe، قلّل critical sections، ومتستخدمش async عشوائي يخفي ordering. اجمع evidence من ANR trace وPerfetto وStrictMode في debug، وحدد rollout metric قبل الإصلاح.</p>

## Tests and rollout

1. Reproduce with one changed dimension at a time.
2. Assert the ordered state transition and the negative path.
3. Stage rollout with a correctness metric and rollback threshold.
4. Redact identifiers and never log tokens, intents, or payloads wholesale.

## Senior follow-ups

1. **What observation would falsify your leading hypothesis?** Choose a trace or state snapshot that the alternative predicts differently.
2. **What is the smallest reversible mitigation?** Disable or route around the proven boundary while preserving evidence.
3. **What remains unverified?** Device and framework behavior until an Android test or production trace runs.
