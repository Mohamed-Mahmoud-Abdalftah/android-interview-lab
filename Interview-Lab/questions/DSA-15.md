---
id: "DSA-15"
question: "Build a rate limiter or deduplication map for requests. What data structure fits?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "C"
phase: 5
priority: "P2"
order: 454
editorial_status: "reviewed"
---

# DSA-15

## Original interview question

Build a rate limiter or deduplication map for requests. What data structure fits?

## What the interviewer evaluates

- Rate limiter versus dedup map semantics and expiry.
- Local map is not payment-wide exactly-once authority.

## Explanation in Arabic

Rate limiter ممكن يستخدم `HashMap<key, bucket>` يخزن tokens/time window لكل user، مع priority queue أو timer لتنظيف expiries. Dedup map يخزن operation ID→result/status مدة محددة، ولازم atomic check-and-set على server لو أكثر من process. Local Android map يمنع double tap في UI فقط؛ ما يضمنش عدم duplicate charge بعد restart أو جهاز تاني.

## Why it matters and how it works

Token bucket stores tokens, capacity and last-refill time per key; each request refills by elapsed monotonic time and consumes atomically. Dedup state maps stable identity to immutable parameters and prior result, with TTL and concurrency control. Eviction must not precede provider retention/reconciliation needs.

## Worked example

For search typing, an in-memory map keyed by query can coalesce requests and expire entries. For payment POST, backend durable store has unique operation ID and compares amount/order; Android persists same ID and queries status after timeout. Do not use a client LRU as financial ledger.

## Trade-offs and decision criteria

Hash maps give expected O(1) lookup but need memory bounds and cleanup. A sliding-window limiter can be more precise but store more timestamps. Distributed rate limiting needs shared atomic state; local per-device limits are bypassable.

## Failure modes

Wall clock moves backward, making refill wrong; use monotonic time for in-process limiter and server time/transaction semantics for distributed policy. Concurrent check-then-put without lock permits duplicates.

## Production perspective

Production limits by authenticated identity and endpoint, monitors denial rates, and distinguishes abuse throttling from financial idempotency. Test eviction, concurrency and process death.

## Interview answer — short

“A map works for per-key limiter or dedup state, but expiry and atomicity matter. Client-local dedup is only UX; payment idempotency must be enforced server-side with stable operation identity.”

## Interview answer — structured

“For a token bucket I store capacity, tokens and last refill time per key, updating atomically. For request dedup I map a stable operation ID to parameters/status for a defined retention window. A HashMap gives expected fast lookup, but memory and expiry need policy. On Android, local dedup prevents rapid taps; a backend unique record and provider contract protect against duplicate financial effects across devices and restarts. The mechanics matter. Token bucket stores tokens, capacity and last-refill time per key; each request refills by elapsed monotonic time and consumes atomically. Dedup state maps stable identity to immutable parameters and prior result, with TTL and concurrency control. Eviction must not precede provider retention/reconciliation needs. The choice has a trade-off. Hash maps give expected O(1) lookup but need memory bounds and cleanup. A sliding-window limiter can be more precise but store more timestamps. Distributed rate limiting needs shared atomic state; local per-device limits are bypassable.”

## Interview answer — deep senior

“I separate throttling from idempotency. A limiter answers ‘may this actor send now?’ using token/window state and monotonic elapsed time; a dedup store answers ‘is this the same intended operation?’ using immutable parameters and a stable ID. Both need atomic updates under concurrency and bounded retention. A distributed backend may use a transaction/unique constraint, while an in-memory Android map is disposable and bypassable. I test concurrent requests, time jumps, expiry, process death and a lost payment response. I never claim exactly-once network execution from a map. Consider a concrete case. For search typing, an in-memory map keyed by query can coalesce requests and expire entries. For payment POST, backend durable store has unique operation ID and compares amount/order; Android persists same ID and queries status after timeout. Do not use a client LRU as financial ledger. A failure case illustrates the risk. Wall clock moves backward, making refill wrong; use monotonic time for in-process limiter and server time/transaction semantics for distributed policy. Concurrent check-then-put without lock permits duplicates. In production, the response is concrete. Production limits by authenticated identity and endpoint, monitors denial rates, and distinguishes abuse throttling from financial idempotency. Test eviction, concurrency and process death.”

## Deep-dive talking points

Prompt for token bucket state, atomic check-and-set, monotonic time, TTL and payment authority.

## Follow-up questions

- [PAY-02](../pay-02/): What is idempotency? **Answer:** one intended business effect under server/provider contract.
- [DSA-10](../dsa-10/): Could LRU hold dedup forever? **Answer:** no, eviction can erase needed identity.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a trade-off/failure, and answer both follow-ups?

## References and reviewed-on date

- [Kotlin Map API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-map/) — map operations.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — financial retry semantics.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
