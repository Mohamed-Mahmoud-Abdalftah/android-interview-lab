---
id: "MEM-25"
question: "How do you find a rare ANR associated with database lock contention?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "C"
phase: 1
priority: "P1"
order: 80
editorial_status: "reviewed"
---

# MEM-25

## Original interview question

How do you find a rare ANR associated with database lock contention?

## What the interviewer evaluates

- Inspect ANR clusters and all relevant thread stacks, not just the top Main frame.
- Identify the waiter, lock holder, long transaction, and why Main needs the resource.
- Reproduce under load and fix transaction scope or synchronous UI dependency with correctness intact.

## Explanation in Arabic

الـANR النادر قد يظهر Main thread واقفة في query أو `synchronized`، لكن السبب الحقيقي worker ماسك database lock أثناء transaction طويلة أو network call داخل transaction. ابدأ من ANR report: زمن ومكان الـMain، thread اللي ماسكة lock، وكل transaction شغالة. استخدم Perfetto/trace مع markers للاستعلامات، وحاول تعيد المشكلة بقراءات وكتابات متزامنة على جهاز بطيء. الحل غالبًا تقصير transaction، منع network داخلها، وتحويل UI لقراءة asynchronous/state بدل انتظار lock على Main. لا تخفِ المشكلة بزيادة timeout أو نقل نفس deadlock لthread أخرى. اختبر ordering والاتساق بعد التعديل.

## Practical walkthrough

لو ANR نادر في checkout وMain stack واقفة على Room query، متفترضش إن query بطيئة بذاتها. بص على كل threads: worker ماسك transaction أثناء network request؟ استخدم trace markers للمعاملة والـquery وحاول concurrent read/write على جهاز بطيء. اقفل transaction بسرعة بعد تسجيل pending operation، اعمل network خارجها، وبعد الرد حدّث الحالة في transaction قصيرة. احتفظ بـoperation ID عشان retries ما تكررش الدفع.

## Why it matters and how it works

Android reports ANR when a required app thread cannot respond in time; for input dispatch this is commonly Main, but the blocking cause may be elsewhere. Database transactions serialize some writes and can hold locks. A synchronous read on Main or a synchronous wait for a repository result makes UI hostage to another thread's transaction. Room discourages main-thread database access and supports suspend/Flow DAO patterns, but async alone does not remove a long transaction or deadlock.

## Worked example

A checkout repository opens a transaction, updates an order, then makes a network request before committing. During a slow connection, a screen waits synchronously for an order read and ANRs. The ANR stack shows Main waiting; a worker stack and trace show transaction ownership. Change the flow to persist a pending state in a short transaction, perform network work outside it with an idempotency key, and reconcile in another short transaction. This is a hypothetical root cause and proposed fix, not a reproduced device incident.

## Trade-offs and decision criteria

Short transactions improve availability but multi-step work must still preserve consistency through explicit states and idempotency. Moving the UI read off Main protects responsiveness but may leave a queue delay; show loading and investigate the lock holder. WAL or indexes may help some contention patterns but are not universal fixes. Avoid broad global mutexes that serialize unrelated operations.

## Failure modes

Looking only at `nativePollOnce` or the Main top frame misses the holder thread. Increasing an ANR threshold is not a solution. A database transaction waits on a network call and blocks all writers. A retry duplicates a payment after the first transaction outcome is unknown. Reproduce with concurrent load, latency injection, and crash recovery; assert state transitions and one external side effect.

## Production perspective

Segment ANR clusters by release, device, and operation. Add privacy-safe timing around transaction start/end, query latency, and lock waits. Capture a trace on a representative slow device with concurrent sync and UI access. Fix the longest critical section, then compare p95/p99 query time, ANR rate, and data correctness in staged rollout. Keep an operational rollback path if a migration changes transaction semantics.

## Interview answer — short

“I inspect the ANR's Main stack and the lock-holder thread, then trace the transaction and UI wait. I shorten the critical section, keep network work outside transactions, and make UI reads asynchronous with a safe loading state.”

## Interview answer — structured

“A rare lock ANR needs multi-thread evidence. I start with the ANR cluster, identify whether Main is doing a synchronous query or waiting on a result, and find the worker holding the database lock. I correlate that with transaction timing in a Perfetto trace and reproduce with concurrent reads/writes and injected latency. I move UI access to suspend/Flow DAO patterns and show loading, but I also shorten the transaction itself—especially removing network calls from it. For multi-step operations I use durable pending states and idempotency so the shorter transactions do not create duplicate side effects.”

## Interview answer — deep senior

“I treat the Main thread as the victim until evidence shows otherwise. The ANR report may show it blocked on a Room query, a `Future.get`, or a monitor; I inspect the full thread dump to find the lock holder and any dependency chain. A Perfetto trace with transaction markers and a concurrent-load reproduction tells me whether a long write, database initialization, nested transaction, or network call inside a transaction owns the delay. Moving a query off Main prevents direct UI blocking but does not fix database throughput or a deadlock. I reduce transaction scope, separate external I/O from local atomic updates, and model pending/reconciliation state where correctness spans a server call. For a payment path I reuse an idempotency key and resolve unknown outcomes rather than blindly retrying. I test slow network, concurrent sync, cancellation, process death, and database consistency, then compare tail lock/query latency and production ANR cohorts. A checkout transaction must never hold a database lock through a network request. I persist a pending operation quickly, call the server outside the transaction with a stable idempotency key, then reconcile in another short transaction. The intermediate state must survive process death; I measure lock-hold tail and test duplicate callback or retry behavior.”

## How to answer in the interview

- **Why:** Follow Main's lock chain to the actual holder.
- **How:** Trace transaction span with concurrent read/write reproduction.
- **Trade-off:** Short transactions require explicit pending-state recovery.
- **Failure case:** Moving only the Main query may leave contention intact.
- **Production solution:** Keep network outside transactions and verify idempotent recovery.

## Deep-dive talking points

Discuss waiter versus holder, transaction timing, Room async boundary, network outside transaction, durable pending state, and tail latency.

## Follow-up questions

- Does moving a query to `Dispatchers.IO` fix lock contention? **Answer:** it protects Main from direct blocking but the long lock and data latency remain to be resolved.
- Why avoid network inside a database transaction? **Answer:** unpredictable network delay holds locks and increases contention; separate steps with durable state and idempotency.
- Which trace evidence is most valuable? **Answer:** Main waiter stack, lock-holder thread, transaction duration, and concurrent operations around the ANR.

## Self-check rubric

Find waiter and holder, reproduce with latency, shorten the transaction, preserve cross-system correctness, and compare ANR/tail metrics.

## References and reviewed-on date

- [Diagnose and fix ANRs](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs) — waiters, lock contention, and traces.
- [Room asynchronous queries](https://developer.android.com/training/data-storage/room/async-queries) — nonblocking DAO use.
- [RoomDatabase.Builder](https://developer.android.com/reference/androidx/room/RoomDatabase.Builder) — transaction executor behavior.

Technically reviewed against these primary sources on 2026-10-13 by automated editorial review. The checkout case was not device-reproduced.
