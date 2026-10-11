# Day 19 optional speaking — useful architecture boundaries

Read [ARC-001](../04-Architecture-DI/arc-001-solid-and-useful-patterns.md). Ten minutes of guided speaking; no audio or pronunciation feedback is claimed.

**Pacing:** “The UI owns presentation / the use case owns the product rule / and the adapter owns persistence.” Stress **owns**. Repeat twice, then explain without notes.

**About 20 seconds:** “I separate a note-save rule from storage. A narrow writer port lets me validate and test the rule with a fake, while a real adapter must still prove its persistence contract.”

**About 90 seconds:** “I use SOLID as change-boundary guidance rather than a mandate for many classes. The SaveNote use case trims and validates input, then delegates once through a writer-only port. Invalid input never reaches storage, and writer failure propagates. A recording fake proves those rules without Android. It does not prove that Room commits atomically, survives process death, or handles expected user validation gracefully. I would choose a domain use case when logic is reused or complex, and keep a simpler repository call for a small feature. A real adapter needs contract and integration tests.”

**Useful phrases:** “behavioral contract”, “reason to change”, “narrow port”, “fake versus real adapter”. Avoid “more layers always mean better architecture”.

**Self-check:** Explain one reason to add this interface and one reason to remove it. Retry with [revision cards](../Flashcards-Revision/ARC-001.md). Free written reference: [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations), checked 2026-10-10.
