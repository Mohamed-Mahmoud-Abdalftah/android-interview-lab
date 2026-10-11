---
id: SCN-048
lesson_id: INT-003
status: reviewed
code_verification: not_run
---
# SCN-048 — Performance and security review production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">الفريق يسرّع startup بإزالة auth check، أو يشفر token بمفتاح ثابت داخل APK. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Senior review ترتب المخاطر من evidence وتأثير واحتمال. performance optimization من baseline، security من assets/trust boundaries/abuse. ما تخلطش secret obfuscation بتفويض server. الإصلاح المختار: اعمل threat/performance budgets، اختبر release-like، أصلح أعلى risk، وحط regression gate وrollout monitoring.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
