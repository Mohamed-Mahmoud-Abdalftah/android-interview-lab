---
id: SCN-030
lesson_id: ARC-005
status: reviewed
code_verification: not_run
---
# SCN-030 — Modules, contracts and ADRs production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">feature modules متشابكة bidirectional، وكل تعديل يبني التطبيق كله، والـADR تقول استخدمنا Clean Architecture من غير context أو بدائل. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">الموديول boundary للownership والاعتماد والبناء، مش folder تجميلي. contract ضيقة تقلل معرفة المستهلك بالتنفيذ. ADR تسجل context والخيارات والقرار والنتائج عشان الفريق يراجع reasoning بدل ما يحفظ النتيجة. الإصلاح المختار: اقسم حسب change ownership وpublic API، امنع cycles، قِس build graph، واكتب ADR بقرار قابل للنقض وconsequences واضحة.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
