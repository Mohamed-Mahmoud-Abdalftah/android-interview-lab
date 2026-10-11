---
id: SCN-042
lesson_id: SYS-003
status: reviewed
code_verification: not_run
---
# SCN-042 — Mobile auth and session state design production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">الموبايل يحتفظ session state لكن server هو authority. access token قصيرة، refresh boundary، logout/revocation، account switch، offline UX، وsecure storage كلها state machine. ممنوع client تعتبر claims إذن نهائي لعملية حساسة. الإصلاح المختار: اعمل generation/account namespace، single-flight refresh، clear/partition caches، وserver reauthorization لكل resource.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
