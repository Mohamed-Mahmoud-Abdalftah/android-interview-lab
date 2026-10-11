# Day 11 — Latest operators, buffering and stale writes

## 20-second answer

“Latest operators cancel obsolete coroutine work, but cancellation is not transaction rollback. I use them for superseded UI work, then add request generations or idempotency at boundaries where an old side effect can still complete. Buffer and conflate are semantic choices, not automatic performance fixes.”

## Pressure prompts

- What exactly does collectLatest cancel when a new value arrives, and what can still escape?
- A progress stream emits 1 through 100 faster than rendering. Compare buffer and conflate.
- Design type-ahead search with debounce, distinctUntilChanged, and flatMapLatest. Name the remaining risks.
- Why use a request generation if flatMapLatest already cancels old requests?
- A telemetry pipeline drops values under load. How do you decide whether this is a bug?
