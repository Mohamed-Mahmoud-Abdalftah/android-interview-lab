---
id: SCN-021
lesson_id: COR-004
status: reviewed
code_verification: tested
---
# SCN-021 — One screen makes duplicate requests and another loses an event

## Reproduction and competing causes

<p dir="rtl" lang="ar">كل recomposition أو collector جديد بيجمع cold flow فتتكرر request، وفي نفس الوقت navigation معمولة StateFlow فتتعاد بعد rotation. افصل state عن effect، شارك upstream في scope مناسبة بسياسة WhileSubscribed، واربط collection بعمر الـview. اختبر عدد subscriptions وإعادة الإنشاء وغياب subscriber.</p>

1. Capture an ordered trace with request or job identity.
2. Reproduce success, failure, cancellation, and late completion separately.
3. Change one boundary at a time and keep sensitive values out of logs.

## Correction and verification

<p dir="rtl" lang="ar">الإصلاح لازم يطابق contract الدرس، ويكون له regression test يثبت behavior مش الوقت. اعمل rollout تدريجي، وراقب cancellation، stale drops، failures المصنفة، والموارد المعلقة.</p>

## Senior follow-ups

1. **What evidence separates scheduling from business-state bugs?** A trace with owner, generation, cancellation, and publish timestamps.
2. **What is the rollback signal?** A predefined correctness or health regression, not a vague feeling after release.
3. **What remains unproved?** The JVM model does not prove Android lifecycle or production transport behavior.
