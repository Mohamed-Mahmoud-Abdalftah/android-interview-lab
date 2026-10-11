---
id: SCN-019
lesson_id: COR-002
status: reviewed
code_verification: tested
---
# SCN-019 — A failed dashboard card cancels healthy siblings

**Incident prompt:** After a release, a flaky notifications endpoint makes the entire dashboard blank. A quick patch wraps the three requests in `supervisorScope`, but some sessions now show an offer for the previous account.

## Investigation

<p dir="rtl" lang="ar">ابدأ من contract والـJob tree، مش من إضافة catch. حدّد هل profile وoffers وnotifications مستقلة فعلًا. سجّل request ID وaccount ID hashed ومرحلة كل child. أعد إنتاج حالتين: notifications تفشل أثناء نجاح الباقي، والمستخدم يبدل الحساب قبل رجوع offers القديمة. الـblank dashboard سببه fail-fast policy غير مناسبة لو cards مستقلة؛ الـoffer القديمة سببها غياب stale-result guard، وsupervision وحدها لا تعالجه.</p>

## Repair and rollout

1. Model each independent card as loading, content, or classified error.
2. Keep the three children in a caller-owned `supervisorScope`.
3. Rethrow cancellation and map only expected endpoint failures.
4. Attach account/request generation to every result and reject stale generations.
5. Redact payloads; monitor per-card failure and full-dashboard availability.
6. Roll out behind a flag and compare blank-screen rate, stale-drop count, and cancellation latency.

## Tests and failure cases

- One child fails: siblings complete and error is visible on exactly one card.
- Parent is cancelled: all children cancel and no card publishes afterward.
- Old account result arrives late: generation mismatch drops it.
- Authentication failure: dependent content is cleared and reauthentication begins.
- Two children fail: both errors remain attributable; no reliance on race order.

## Senior follow-ups

1. **Why did supervision expose a privacy bug?** It allowed healthy siblings to continue, revealing that result ownership was not tied to the current account generation.
2. **Would `CoroutineExceptionHandler` fix the blank screen?** No. It can observe an uncaught failure, but the state and sibling policy still need an explicit contract.
3. **What proves the fix?** Controlled scheduler tests for failure/cancellation/order plus a staged production comparison with privacy-safe counters.

[LAB-018](../Coding-Challenges/LAB-018-supervised-batch.md) exercises the failure boundary.
