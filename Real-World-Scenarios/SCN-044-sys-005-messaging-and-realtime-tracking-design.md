---
id: SCN-044
lesson_id: SYS-005
status: reviewed
code_verification: not_run
---
# SCN-044 — Messaging and realtime tracking design production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">push تصل قبل data أو مرتين، location updates تستهلك battery، أو reconnect يكرر رسائل. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">Realtime mobile design تجمع push كwake hint، socket/stream أثناء foreground، REST catch-up، local ordered store، وserver sequence. delivery قد تتكرر وتتأخر وتتقطع؛ exactly-once end-to-end ادعاء محتاج تضييق شديد. الإصلاح المختار: استخدم event IDs/sequence، dedupe، gap detection، bounded reconnect، presence/freshness، وprivacy/retention للlocation.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
