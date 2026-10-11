---
id: SCN-040
lesson_id: PRO-006
status: reviewed
code_verification: not_run
---
# SCN-040 — Revision: release health and DSA production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">tests خضراء لكن migration path ناقصة أو security blocker مفتوحة، والفريق يكمل عشان deadline. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Release decision تجمع correctness/security/migration/crash/performance signals. gate لازم تكون قبل النشر ولها owner وthreshold وrollback. binary search في DSA تحتاج monotonic predicate وحدود تمنع overflow. الإصلاح المختار: حوّل criteria لsignals صريحة، staged rollout، halt/rollback rule، وpost-release observation. متخليش average واحدة تلغي blocker.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
