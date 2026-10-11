---
id: SCN-035
lesson_id: UI-005
status: reviewed
code_verification: not_run
---
# SCN-035 — Adaptive UI, RTL, a11y and performance production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">layout ثابتة تنهار عند 200% font، icon اتجاهها غلط في RTL، أو تحسين يخفي semantics عشان يقلل nodes. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Adaptive UI تتصرف حسب available space/posture مش اسم الجهاز. RTL تحتاج logical start/end وعزل code LTR. accessibility contract تشمل semantics وfocus وtouch target وfont scale. الأداء يقاس frames ومراحل العمل، مش إحساس المطور. الإصلاح المختار: اختبر window sizes وRTL/font scale/TalkBack، استخدم semantics meaningful، وقِس jank قبل وبعد على build ممثلة.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
