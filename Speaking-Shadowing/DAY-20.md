# Day 20 optional speaking — MVVM and stale responses

Read [ARC-002](../04-Architecture-DI/arc-002-mvvm-udf-state-and-events.md). Ten minutes of self-directed practice; no audio or pronunciation assessment is claimed.

**Pacing:** “The UI sends an action / the state holder updates state / and the UI renders it.” Repeat twice, then explain without notes.

**About 20 seconds:** “Each save gets an identity. Only the current pending save can report success, so an old callback cannot claim that a newer draft was saved.”

**About 90 seconds:** “I use MVVM to separate rendering from state decisions. The screen sends a save action; a state holder emits pending state and coordinates repository work. It tags the result with the request identity and accepts only the current pending result. This guards the displayed state from a stale response. It does not cancel a write already in progress, so I also test the repository contract and define conflict policy. The JVM reducer tests cover state transitions; Android lifecycle and Flow collection need integration tests.”

**Self-check:** Explain the difference between stale UI feedback and stale persisted data. Retry with [revision cards](../Flashcards-Revision/ARC-002.md). Written reference: [Android UI layer](https://developer.android.com/topic/architecture/ui-layer), checked 2026-10-10.
