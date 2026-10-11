---
id: SCN-038
lesson_id: PRO-004
status: reviewed
code_verification: not_run
---
# SCN-038 — Gradle, AGP 9, D8/R8 and signing production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">release crash بسبب class اتشالت بالshrink، والفريق يضيف keep all فيلغي قيمة R8، أو secret متخزنة في BuildConfig. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Gradle يحسب task graph، AGP يبني Android variants، Kotlin compiler تنتج bytecode/IR outputs، D8 يحول لـDEX، وR8 يعمل shrinking/optimization/obfuscation حسب pipeline. signing تثبت publisher key مش أمان business logic. الإصلاح المختار: ثبت compatibility من docs، ابن release في CI، اختبر mapping/retrace/startup، واستخدم أضيق keep rules. signing keys خارج repo بصلاحيات محدودة.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
