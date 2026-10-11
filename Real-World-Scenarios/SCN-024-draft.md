---
id: SCN-024
lesson_id: AND-002
status: reviewed
code_verification: tested
---
# SCN-024 — المستخدم كتب draft، لف الشاشة ففضل موجود، لكن بعد ما النظام قتل process رجع لقى الشاشة فاض

## Symptom and competing hypotheses

<p dir="rtl" lang="ar">المستخدم كتب draft، لف الشاشة ففضل موجود، لكن بعد ما النظام قتل process رجع لقى الشاشة فاضية. نجاح rotation test خلّى الفريق يفتكر إن state آمنة، مع إن ViewModel كانت بس مخبية المشكلة. الفرضيات المنافسة تشمل ownership غلط، state stale، input غير موثوقة، وplatform restriction. ممنوع نختار السبب من قرب log زمني فقط.</p>

## Investigation and correction

<p dir="rtl" lang="ar">قبل recreation خزّن أقل keys لازمة لإعادة البناء. عند الرجوع اقرأ saved arguments وSavedStateHandle، وبعدها حمّل البيانات الكبيرة من repository. متحطش object graph أو bitmap في Bundle؛ الحجم محدود والنسخة ممكن تبقى stale. الإصلاح: خزّن navigation identity وinput صغير في saved state، وخزّن business data في database. أعد اشتقاق القيم المحسوبة بدل تكرارها. اختبر recreation وprocess recreation كمسارين مختلفين.</p>

## Tests and rollout

1. Reproduce with one changed dimension at a time.
2. Assert the ordered state transition and the negative path.
3. Stage rollout with a correctness metric and rollback threshold.
4. Redact identifiers and never log tokens, intents, or payloads wholesale.

## Senior follow-ups

1. **What observation would falsify your leading hypothesis?** Choose a trace or state snapshot that the alternative predicts differently.
2. **What is the smallest reversible mitigation?** Disable or route around the proven boundary while preserving evidence.
3. **What remains unverified?** Device and framework behavior until an Android test or production trace runs.
