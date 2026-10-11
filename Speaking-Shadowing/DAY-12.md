# Day 12 — Revision: deterministic coroutine tests and DSA

## 20-second answer

“A deterministic coroutine test owns the dispatcher, scheduler, and completion gates. I assert intermediate state before advancing virtual time, then advance only the work needed. I avoid sleeps and make every launched coroutine visible to runTest. For DSA I state the invariant before code and test boundaries, not just the happy path.”

## Pressure prompts

- What does runTest give you that runBlocking plus delay does not?
- Why should test dispatchers in one test usually share a TestCoroutineScheduler?
- How do you test a StateFlow that never completes without hanging the test?
- For two-sum on an unsorted array, state the one-pass hash-map invariant before coding.
- A coroutine test passes alone and fails in the suite. Give an evidence-first debugging plan.
