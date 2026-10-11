# Day 4 optional speaking — callbacks and closure timing

Read [KOT-004](../01-Kotlin-JVM-ART/kot-004-functions-lambdas-and-closures.md). Ten minutes of guided speaking; no audio or pronunciation feedback is claimed.

**Pacing:** “A closure can capture a binding / the callback executes when invoked / and the product contract decides whether to use a snapshot or current state.” Stress **when invoked** and **contract**. Repeat slowly twice, then paraphrase.

**About 20 seconds:** “I choose callback capture based on timing. A reload-current action reads state when invoked, while an event tied to an original item can intentionally capture a snapshot. I test the transition between setup and invocation.”

**About 90 seconds:** “A higher-order function accepts or returns a function value. In our JVM example, the button callback should reload the currently selected profile, so capturing an ID at setup can send a stale value. The corrected callback reads one ID per invocation, validates it, and delegates to a request function. That only proves the callback was called; it does not prove network success or make the state thread-safe. If the action is about an original event, I would capture that event ID intentionally. For Android APIs, I would inspect callback ownership, lifetime and thread, then separately test cancellation and late responses.”

**Useful phrases:** “at setup time”, “at invocation time”, “the caller owns the callback”, “the response arrived out of order”. Avoid saying “the lambda is asynchronous” without identifying the API that schedules it.

**Self-check:** Explain both contracts without notes. If unclear, retry with the [revision cards](../Flashcards-Revision/KOT-004.md). Free written reference: [Kotlin lambdas](https://kotlinlang.org/docs/lambdas.html), checked 2026-10-10.
