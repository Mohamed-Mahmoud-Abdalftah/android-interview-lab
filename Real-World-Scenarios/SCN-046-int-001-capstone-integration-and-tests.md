---
id: SCN-046
lesson_id: INT-001
status: reviewed
code_verification: not_run
---
# SCN-046 — Capstone integration and tests production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">save تظهر success قبل durable transaction، worker تشتغل بحساب قديم، أو tests تستخدم fake تخفي migration/cancellation. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Capstone تجمع offline notes: UI state holder، repository/local source، outbox worker، auth session، sync conflict، وobservability. integration معناها contracts تتوصل وتفشل بوضوح، مش كل classes في module واحدة. الإصلاح المختار: عرّف end-to-end acceptance paths، اختبر pure + database + worker contracts، وسجل Android SDK blocker بوضوح.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
