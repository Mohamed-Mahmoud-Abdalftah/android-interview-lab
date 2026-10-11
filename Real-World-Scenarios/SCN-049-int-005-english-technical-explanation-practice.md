---
id: SCN-049
lesson_id: INT-005
status: reviewed
code_verification: not_run
---
# SCN-049 — English technical explanation practice production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">إجابة خمس دقايق تبدأ تاريخ الموضوع ومتوصلش للقرار، أو ادعاء أرقام وخبرة مش حقيقية. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">الإجابة القوية لها structure: direct answer، mechanism، example، trade-off، evidence. English البسيطة الدقيقة أحسن من vocabulary كبيرة مبهمة. لو مش عارف، حدّد known/unknown وخطة تحقق. الإصلاح المختار: استخدم 20/90/180 ثانية، سجل نفسك، شيل filler، وراجع هل جاوبت السؤال وقلت assumptions.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
