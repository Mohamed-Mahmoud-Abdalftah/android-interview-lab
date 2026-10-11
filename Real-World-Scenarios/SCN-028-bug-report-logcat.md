---
id: SCN-028
lesson_id: AND-006
status: reviewed
code_verification: not_run
---
# SCN-028 — Bug report فيه آلاف السطور، والمرشح بيقرأ logcat عشوائيًا. المطلوب hypothesis واضحة، time

## Symptom and competing hypotheses

<p dir="rtl" lang="ar">Bug report فيه آلاف السطور، والمرشح بيقرأ logcat عشوائيًا. المطلوب hypothesis واضحة، time window، process/build identity، وأداة تناسب السؤال؛ وبعدها DSA solution invariant مش كود محفوظ. الفرضيات المنافسة تشمل ownership غلط، state stale، input غير موثوقة، وplatform restriction. ممنوع نختار السبب من قرب log زمني فقط.</p>

## Investigation and correction

<p dir="rtl" lang="ar">ابدأ reproduction matrix صغيرة: fresh/restore، foreground/background، online/offline. خذ marker زمني وrequest ID، ثم اجمع أقل evidence تفصل hypotheses. redact قبل المشاركة. في live coding كرر نفس المنهج: examples، invariant، boundaries، tests. الإصلاح: استخدم logcat للأحداث المرتبة، dumpsys للحالة الحالية، bugreport للسياق النظامي، Perfetto للزمن والthreads. ما تجمعش بيانات مستخدم أكتر من اللازم، ومتعتبرش absence في log دليل إن الحدث ماحصلش.</p>

## Tests and rollout

1. Reproduce with one changed dimension at a time.
2. Assert the ordered state transition and the negative path.
3. Stage rollout with a correctness metric and rollback threshold.
4. Redact identifiers and never log tokens, intents, or payloads wholesale.

## Senior follow-ups

1. **What observation would falsify your leading hypothesis?** Choose a trace or state snapshot that the alternative predicts differently.
2. **What is the smallest reversible mitigation?** Disable or route around the proven boundary while preserving evidence.
3. **What remains unverified?** Device and framework behavior until an Android test or production trace runs.
