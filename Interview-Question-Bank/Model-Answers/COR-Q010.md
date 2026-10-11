---
id: COR-Q010-ANSWER
question_id: COR-Q010
status: reviewed
---
# COR-Q010 — Complete model answer

**Spoken answer:** “For an atomic dashboard snapshot I use coroutineScope and fail the whole load if one required source fails. For independent cards I use supervisorScope and a typed per-card result. In both designs parent cancellation cancels all work, retries require idempotent contracts, and tests cover one-child failure, simultaneous failure, cancellation, and stale completion.”

<p dir="rtl" lang="ar">في التصميم الأول state يا كاملة يا error؛ ده يحافظ على invariant لو offers تعتمد على profile version. في التصميم الثاني state فيها field لكل card: loading/success/error/stale، والـUI ما تدّعيش إن البيانات كاملة. supervision هنا قرار domain وUX، مش مجرد طريقة تمنع crash.</p>

**Mechanics:** Keep all children under the caller-owned scope. For partial results, catch expected failures inside each supervised child and return a typed result; preserve cancellation. Add request IDs if a newer refresh can supersede an older one. Record latency and failure by dependency without sensitive payloads.

**Common wrong answer:** “Use supervisorScope everywhere because it is more resilient.” Isolation without an explicit partial-state contract hides inconsistent data.

**Follow-up 1:** How do retries change the design? Retry each dependency only for classified transient failures, with backoff, attempt limits, and idempotency where side effects exist.

**Follow-up 2:** What if profile authentication fails? Treat it as a policy boundary: cancel dependent cards and move the session to reauthentication instead of rendering unrelated stale data as current.

**Rubric for self-review:** Present both valid designs, connect topology to product semantics, and include cancellation, stale results, retries, and observability.
