# Day 1 optional speaking (10 minutes)

Read [KOT-001](../01-Kotlin-JVM-ART/KOT-001-nullability-java-boundary.md) first. This is guided practice, not an assessment. No audio or pronunciation feedback is claimed.

**Listen to your own pacing:** Say each slash as a pause: “An unannotated Java value / may be null / even when Kotlin lets me call it directly.” Stress **may**, **boundary**, and **validate**. Repeat slowly twice, then at normal pace.

**20 seconds:** “I treat an unannotated Java result as uncertain. I receive it as nullable, validate it at the boundary, and return a safe domain value or an explicit error.”

**About 90 seconds:** Use the lesson's longer answer. Replace “vendor SDK” with one real API you have used only if you can describe its contract accurately. Do not invent a production incident.

**Useful phrases:** “The contract allows…”, “The failure occurs when…”, “I would verify that with…”, “That fallback is appropriate only if…”. Prefer “the call may return null” to the literal translation “the call has null.”

**Self-check:** Can a listener hear the cause, boundary decision, and test? If not, pause after each clause and try once more. Official free reading (not an audio promise): [Kotlin Java interoperability](https://kotlinlang.org/docs/java-interop.html), accessed 2026-10-10. No specific free video or caption source has been verified for this batch.
