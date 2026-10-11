---
id: SCN-034
lesson_id: UI-004
status: reviewed
code_verification: tested
---
# SCN-034 — Navigation ownership and back stack production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">نفس detail route تتضاف مرتين مع نفس ID، أو object كبيرة في arguments تبقى stale بعد process death. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Navigation state لها owner وback stack entries بهويات وsaved state. مرّر IDs صغيرة بدل objects، وحمّل البيانات من source of truth. singleTop/popUpTo يغيروا stack semantics؛ deep links entry points لازم تتختبر زي launcher. الإصلاح المختار: استخدم typed route contract، validate external routes، قرر singleTop/popUpTo من UX، واختبر Back عبر launch/deep link/notification.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
