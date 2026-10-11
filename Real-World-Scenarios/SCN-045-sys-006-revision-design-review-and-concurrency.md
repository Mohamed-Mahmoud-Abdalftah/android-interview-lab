---
id: SCN-045
lesson_id: SYS-006
status: reviewed
code_verification: not_run
---
# SCN-045 — Revision: design review and concurrency production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">مرشح يرسم boxes من غير offline/auth/failure، أو يضيف lock حول network call فيعمل convoy. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">System design interview تبدأ requirements وscale/failure/privacy، ثم state owners وAPIs/data flow، وبعدها alternatives. concurrency review تحدد shared state وatomic boundary وordering بدل قول thread-safe عامة. الإصلاح المختار: قدّم design أساسي وبديل، اذكر bottleneck/rollout/observability، واستخدم serialization أو atomic DB transaction عند boundary الصحيحة.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
