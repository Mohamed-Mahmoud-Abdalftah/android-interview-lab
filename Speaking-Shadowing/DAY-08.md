# Day 8 — Job hierarchy and supervision

## 20-second answer

“A regular coroutine scope is fail-fast: one child failure fails the parent and cancels siblings. I use supervision only when sibling results are independently useful, handle each failure explicitly, and preserve parent cancellation.”

## 90-second answer

“I choose the Job topology from the product contract. If child operations create one atomic result, I use coroutineScope so a failure cancels the group. If the UI can honestly display independent cards, I use supervisorScope and represent success or failure per child. Supervision does not make exceptions disappear and it does not stop parent cancellation. I do not use CoroutineExceptionHandler as business recovery; it observes uncaught failures at a root boundary. I also avoid broad runCatching around suspending work unless cancellation is rethrown. My tests force one child failure to verify sibling behavior, then cancel the parent to prove no stale result is published.”

## Pressure follow-ups

- Why can an un-awaited Deferred be a design smell?
- What changes when the parent, rather than a child, fails?
- When is partial success actively dangerous?
- How would you prevent a result from a previous account appearing after a switch?
