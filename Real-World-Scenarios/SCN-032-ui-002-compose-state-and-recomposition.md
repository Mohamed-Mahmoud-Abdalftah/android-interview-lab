---
id: SCN-032
lesson_id: UI-002
status: reviewed
code_verification: tested
---
# SCN-032 — Compose state and recomposition production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">List mutable اتغيرت in-place فالواجهة ما اتحدثتش، أو composable تعمل network call كل recomposition. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Composition تصف UI من state؛ recomposition تعيد تنفيذ composables اللي قرأت state اتغيرت، ومش معناها إعادة رسم كل الشاشة. state hoisting يفصل value وevents، والاستقرار يؤثر على إمكانية skip لكنه مش هدف يتزور بـannotations. الإصلاح المختار: استخدم immutable observable state، ارفعها لأقرب owner مشترك، خلي composition بلا side effects، وقِس recomposition قبل optimization.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
