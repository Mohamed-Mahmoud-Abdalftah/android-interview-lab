---
id: SCN-037
lesson_id: PRO-002
status: reviewed
code_verification: tested
---
# SCN-037 — HTTP, timeouts, retries and token refresh production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين. اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">HTTP failure لازم يتصنف: DNS/connect/read timeout، status، parse، cancellation، أو unknown side-effect outcome. retry مش default؛ تحتاج safe/idempotent operation وbackoff/jitter وحد أقصى. token refresh لازم single-flight وتتجنب loops. الإصلاح المختار: اعمل authenticator/refresh coordinator واحد، idempotency key للside effects، صنّف statuses، واحفظ unknown outcome للمصالحة.</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
