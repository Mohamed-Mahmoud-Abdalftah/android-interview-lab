---
id: SCN-041
lesson_id: SYS-002
status: reviewed
code_verification: tested
---
# SCN-041 — Trees, graphs, heaps and basic DP production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Tree traversal تختار DFS/BFS من المطلوب، graph تحتاج visited وdirection/weights، heap تدعم أفضل عنصر مش sorted iteration، وDP تخزن overlapping subproblems بعد تعريف state/transition/base. الإصلاح المختار: اكتب graph contract، invariant، complexity، وoverflow. اختبر disconnected/cycle/duplicate edges وlarge weights.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
