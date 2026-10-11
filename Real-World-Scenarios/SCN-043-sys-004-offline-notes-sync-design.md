---
id: SCN-043
lesson_id: SYS-004
status: reviewed
code_verification: not_run
---
# SCN-043 — Offline notes sync design production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Local database source of truth تخلي UI تقرأ فورًا. writes تتسجل mutation identity/outbox وتتزامن لاحقًا. conflict policy لازم تعتمد على domain: last-write، field merge، version reject، أو user resolution. tombstones مهمة للحذف. الإصلاح المختار: transaction تجمع local write وoutbox، operation IDs idempotent، versions واضحة، reconcile يحافظ على draft والدليل.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
