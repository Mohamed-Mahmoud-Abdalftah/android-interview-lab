# Day 3 optional speaking — construction and invariants

Read [KOT-003](../01-Kotlin-JVM-ART/kot-003-classes-constructors-initialization-order.md). This is ten minutes of guided output, not a scored assessment. No audio or pronunciation feedback is claimed.

**Pacing:** “Initialization follows source order / the secondary constructor delegates first / and an open call from a base constructor can reach an unready subclass.” Stress **source order**, **delegates**, and **unready**. Repeat slowly twice, then paraphrase.

**About 20 seconds:** “Kotlin interleaves property initializers and init blocks in source order. A secondary constructor delegates before its own body. I validate invariants during construction and use a factory for expected bad external input.”

**About 90 seconds:** “I trace object creation rather than assuming every property is ready at once. In the lab, normalization happens, the init block validates, and then the label is derived; a blank input stops later steps. A private constructor narrows ordinary creation paths, while a parsing factory reports expected invalid input without turning it into a crash. In a class hierarchy, base initialization precedes derived initialization, so I never call an overridable member from a base constructor if it could read derived state. I would test the exact order and negative branches on the pinned JVM setup, then separately verify any Android integration.”

**Useful phrases:** “The failure occurs before…”, “This is an invariant, not a network guarantee”, “I would move that hook after construction”, “The trace shows which initializer ran.” Avoid literal translation such as “the constructor entered on the child”; say “the base call dispatched to the derived override.”

**Self-check:** Can you explain order, failure path and redesign without reading? If not, use the [revision cards](../Flashcards-Revision/KOT-003.md) and retry once. Free official written reference: [Kotlin classes](https://kotlinlang.org/docs/classes.html), checked 2026-10-10. No listening resource has been verified for this batch.
