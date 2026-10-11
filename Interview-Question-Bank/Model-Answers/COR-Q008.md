---
id: COR-Q008-ANSWER
question_id: COR-Q008
status: reviewed
---
# COR-Q008 — Complete model answer

**Spoken answer:** “Every Deferred is a value-or-failure handle and needs an owner that consumes it. Awaiting only one can hide the second result, delay failure observation, or leave ambiguous partial work. I would await both in the same structured operation, usually with `awaitAll`, or remove async if the work is sequential.”

<p dir="rtl" lang="ar">ابدأ بالسؤال: ليه شغلت العملية الثانية أصلًا؟ لو النتيجتين مطلوبين، اجمعهم في نفس contract واستنى الاثنين. لو الثانية side effect، ما تخبيهاش في async؛ اعمل API توضح acknowledgement والفشل. ولو العملية الثانية optional، مثّل نتيجتها كـtyped partial result تحت supervision.</p>

**Mechanics:** Starting an `async` child begins work according to its start mode. Its exception is stored in the Deferred for observation by `await`, while parent-child propagation still depends on the surrounding Job topology. Structured code keeps Deferred handles local and consumes all required results.

**Common wrong answer:** “Un-awaited async is fire-and-forget.” It still has lifetime, failure, and resource costs; use a clearly owned `launch` only when no value is part of the contract.

**Follow-up 1:** Does the order of two `await` calls determine start order? No. Both eager `async` builders normally start when created; await order only controls where the caller first suspends for a result.

**Follow-up 2:** When is sequential code better? When the second request depends on the first, concurrency adds no latency benefit and makes failure reasoning harder.

**Rubric for self-review:** Discuss ownership, result consumption, exception visibility, and whether concurrency is actually valid.
