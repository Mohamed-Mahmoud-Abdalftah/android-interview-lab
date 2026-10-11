---
id: SCN-031
lesson_id: ARC-006
status: reviewed
code_verification: not_run
---
# SCN-031 — Revision: architecture code review and DSA production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">Reviewer يطلب pattern أكبر من غير failure حقيقي، أو يوافق على repository بتكتب network result فوق local edits من غير conflict policy. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">مراجعة architecture تبدأ من invariants وdata ownership وfailure path، مش أسماء layers. في DSA نفس المهارة: عرّف contract وinvariant وبعدين اختار structure. الـreview الجيدة تفرّق blocker correctness عن preference. الإصلاح المختار: اكتب observation وتأثير واقتراح واختبار، واطلب evidence للtrade-off. في live coding اشرح invariant وcomplexity وحدود input.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
