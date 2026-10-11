---
id: SCN-027
lesson_id: AND-005
status: reviewed
code_verification: tested
---
# SCN-027 — Upload بدأ من screen scope فاتقطع بعد الخروج. الفريق نقله foreground service لكل الحالات،

## Symptom and competing hypotheses

<p dir="rtl" lang="ar">Upload بدأ من screen scope فاتقطع بعد الخروج. الفريق نقله foreground service لكل الحالات، فظهر notification مزعج وبدأ يصطدم بقيود البدء من الخلفية. المطلوب اختيار mechanism من durability وurgency وuser visibility. الفرضيات المنافسة تشمل ownership غلط، state stale، input غير موثوقة، وplatform restriction. ممنوع نختار السبب من قرب log زمني فقط.</p>

## Investigation and correction

<p dir="rtl" lang="ar">اكتب contract: هل لازم ينجو من process death؟ هل المستخدم شايفه الآن؟ هل له deadline؟ هل retry آمنة؟ بعدها اختار mechanism، خزّن input صغير وstable، واجعل worker idempotent لأن التنفيذ ممكن يتكرر. الإصلاح: متخزنش bytes كبيرة في WorkRequest input؛ خزّن URI/ID آمنة والصلاحية المطلوبة. صنّف retry، حط unique work policy عن قصد، واظهر progress من source of truth.</p>

## Tests and rollout

1. Reproduce with one changed dimension at a time.
2. Assert the ordered state transition and the negative path.
3. Stage rollout with a correctness metric and rollback threshold.
4. Redact identifiers and never log tokens, intents, or payloads wholesale.

## Senior follow-ups

1. **What observation would falsify your leading hypothesis?** Choose a trace or state snapshot that the alternative predicts differently.
2. **What is the smallest reversible mitigation?** Disable or route around the proven boundary while preserving evidence.
3. **What remains unverified?** Device and framework behavior until an Android test or production trace runs.
