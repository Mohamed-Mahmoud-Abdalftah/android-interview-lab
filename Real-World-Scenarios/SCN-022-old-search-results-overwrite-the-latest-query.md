---
id: SCN-022
lesson_id: COR-005
status: reviewed
code_verification: tested
---
# SCN-022 — Old search results overwrite the latest query

## Reproduction and competing causes

<p dir="rtl" lang="ar">request لكلمة قصيرة بطيئة ترجع بعد request لكلمة أطول، فتستبدل state الجديدة. استخدم controlled responses لإثبات الترتيب، ثم flatMapLatest للشغل القابل للإلغاء وrequest generation عند publish boundary. راقب cancelled، stale-dropped، latency، وما تعتبرش cancellation rollback للسيرفر.</p>

1. Capture an ordered trace with request or job identity.
2. Reproduce success, failure, cancellation, and late completion separately.
3. Change one boundary at a time and keep sensitive values out of logs.

## Correction and verification

<p dir="rtl" lang="ar">الإصلاح لازم يطابق contract الدرس، ويكون له regression test يثبت behavior مش الوقت. اعمل rollout تدريجي، وراقب cancellation، stale drops، failures المصنفة، والموارد المعلقة.</p>

## Senior follow-ups

1. **What evidence separates scheduling from business-state bugs?** A trace with owner, generation, cancellation, and publish timestamps.
2. **What is the rollback signal?** A predefined correctness or health regression, not a vague feeling after release.
3. **What remains unproved?** The JVM model does not prove Android lifecycle or production transport behavior.
