# Day 7 optional speaking — structured coroutines

Read [COR-001](../02-Coroutines-Flow/cor-001-suspend-dispatchers-and-structured-scopes.md). Ten minutes of guided speaking; no audio or pronunciation feedback is claimed.

**Pacing:** “Suspend permits pausing / a dispatcher decides where work runs / and the parent scope owns its children.” Stress **permits**, **decides**, **owns**. Repeat twice and paraphrase.

**About 20 seconds:** “Suspend is not a background-thread switch. I put blocking work on an appropriate dispatcher and keep concurrent children in a caller-owned scope so the caller can await them and cancel them.”

**About 90 seconds:** “In the profile card example, two independent suspending sources run as async children. A structured scope waits for both, propagates child failure, and cancels waiting children when the parent is cancelled. The injected dispatcher lets a test scheduler control execution without sleeping. The test proves this JVM behavior, not Android navigation. In Android I would choose a lifecycle-appropriate scope and make the data-layer operation main-safe; I would separately verify the underlying transport responds to cancellation and that late results cannot overwrite newer selection.”

**Useful phrases:** “child of the caller”, “cooperative cancellation”, “main-safe data operation”, “out-of-order response”. Avoid “suspend starts a new thread”.

**Self-check:** Explain the parent/child trace and one limitation from memory. Retry with [revision cards](../Flashcards-Revision/COR-001.md). Free written source: [Kotlin coroutine basics](https://kotlinlang.org/docs/coroutines-basics.html), checked 2026-10-10.
