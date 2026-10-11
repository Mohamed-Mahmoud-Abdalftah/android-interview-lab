---
id: SCN-029
lesson_id: ARC-004
status: reviewed
code_verification: tested
---
# SCN-029 — Hilt scopes, qualifiers and DI tests production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">Singleton ماسكة session/user object فتسرّب بيانات حساب قديم بعد logout، أو binding غلط توصل production endpoint في test. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">DI بتفصل إنشاء dependencies عن استخدامها، والscope عقد lifetime مش performance annotation. object أقصر عمرًا مينفعش يتخزن جوه owner أطول. qualifier بيفرق bindings من نفس type، والاختبار لازم يقدر يستبدل boundary من غير service locator خفي. الإصلاح المختار: ارسم ownership graph، اختار أضيق scope تحقق المشاركة المطلوبة، استخدم qualifiers بأسماء معنى، واختبر replacement والlogout/recreation.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
