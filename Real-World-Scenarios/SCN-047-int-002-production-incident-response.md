---
id: SCN-047
lesson_id: INT-002
status: reviewed
code_verification: not_run
---
# SCN-047 — Production incident response production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">الفريق يقضي ساعات في root cause بينما crash rate بتزيد وعنده rollback آمن. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Incident response هدفها تقلل ضرر وتتعلم: detect، scope، mitigate، diagnose، recover، follow-up. severity من user impact مش صوت أعلى شخص. افصل timeline facts عن hypotheses، وخلي owner للقرار والتواصل. الإصلاح المختار: حدد incident commander، rollback/flag حسب threshold، حافظ على evidence، واكتب action items بowner وdeadline وverification.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
