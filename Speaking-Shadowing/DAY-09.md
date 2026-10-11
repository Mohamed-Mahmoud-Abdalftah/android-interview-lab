# Day 9 — Cooperative cancellation and cleanup

## 20-second answer

“Cancellation is cooperative. Suspending APIs usually check it, but CPU loops need explicit checkpoints such as ensureActive or yield. I keep cleanup in finally, rethrow CancellationException, and restrict NonCancellable to a small bounded cleanup operation.”

## Pressure prompts

- A CPU-heavy loop is inside a suspend function but ignores cancellation. Explain why and choose checkpoints without destroying throughput.
- Review a repository that catches Exception and returns Result.failure. What cancellation bug can it create?
- A team wraps a network upload in withContext(NonCancellable) so cleanup finishes. Review the decision.
- Where should withTimeout live when UI, repository, and HTTP client all have deadlines?
- Design a deterministic test for cancellation and cleanup without Thread.sleep.
