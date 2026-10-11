---
id: SCN-033
lesson_id: UI-003
status: reviewed
code_verification: not_run
---
# SCN-033 — Compose effects and lifecycle collection production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">LaunchedEffect(Unit) تقرأ userId قديمة، أو key متغيرة كل frame تعيد network request، أو collector تستمر بعد view STOPPED. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Effect API تربط side effect بعمر composition ومفاتيحها. LaunchedEffect تلغي وتعيد التشغيل لما key تتغير. DisposableEffect تعمل cleanup. rememberUpdatedState يسمح effect طويلة تشوف callback حديثة من غير restart. lifecycle collection توقف استهلاك UI حسب owner. الإصلاح المختار: اختار key تمثل identity الحقيقية، افصل producer عن collector، واختبر restart/cleanup مع تغيير key وlifecycle.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
