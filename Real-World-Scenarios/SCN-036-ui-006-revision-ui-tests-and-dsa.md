---
id: SCN-036
lesson_id: UI-006
status: reviewed
code_verification: not_run
---
# SCN-036 — Revision: UI tests and DSA production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">اختبار يعتمد على text متغيرة وترتيب زمني وsleep، أو screenshot تعتبر accessibility proof. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">UI test تختبر behavior من semantics/user surface، unit test تختبر reducer، screenshot تختبر pixels ضمن حدود. اختار أقل طبقة تثبت الخطر. DSA sliding window تحتاج invariant عن محتوى النافذة، مش nested loops مخفية. الإصلاح المختار: استخدم stable semantics بحذر، controlled state، idling/scheduler مناسب، واختبر reducer سريعًا ثم journey حرجة على Android.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
