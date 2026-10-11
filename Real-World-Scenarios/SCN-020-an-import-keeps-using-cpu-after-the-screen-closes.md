---
id: SCN-020
lesson_id: COR-003
status: reviewed
code_verification: tested
---
# SCN-020 — An import keeps using CPU after the screen closes

## Reproduction and competing causes

<p dir="rtl" lang="ar">تطبيق استيراد يقرأ 80 ألف row في loop حسابية على Default. المستخدم يقفل الشاشة لكن CPU يفضل عالي والنتيجة القديمة تظهر لما يفتح حساب تاني. تتبع owner والـJob ومواضع suspension. أصلحها بفحص cancellation عند batch boundary، generation للنتيجة، وfinally يقفل parser. اختبر حد أقصى لعدد rows بعد الإلغاء بدل الاعتماد على sleep.</p>

1. Capture an ordered trace with request or job identity.
2. Reproduce success, failure, cancellation, and late completion separately.
3. Change one boundary at a time and keep sensitive values out of logs.

## Correction and verification

<p dir="rtl" lang="ar">الإصلاح لازم يطابق contract الدرس، ويكون له regression test يثبت behavior مش الوقت. اعمل rollout تدريجي، وراقب cancellation، stale drops، failures المصنفة، والموارد المعلقة.</p>

## Senior follow-ups

1. **What evidence separates scheduling from business-state bugs?** A trace with owner, generation, cancellation, and publish timestamps.
2. **What is the rollback signal?** A predefined correctness or health regression, not a vague feeling after release.
3. **What remains unproved?** The JVM model does not prove Android lifecycle or production transport behavior.
