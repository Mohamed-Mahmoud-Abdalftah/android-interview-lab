# Day 2 optional speaking — equality and mutability (10 minutes)

Read [KOT-002](../01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md) and the [mutable-key case](../Real-World-Scenarios/SCN-002-mutable-cache-key.md) first. This is guided English practice, not an assessment. No audio, listening source, or pronunciation feedback is claimed.

**Pacing:** Say each slash as a short pause: “`val` fixes the binding / not the object / and a read-only list can still have a mutable owner.” Repeat twice slowly, then once at a natural pace. Stress **binding**, **object**, and **owner**.

**About 20 seconds:** “I separate reference mutability from object mutability. `val` prevents reassignment, while a mutable collection can still change. For comparisons, `==` asks for value equality and `===` asks whether references identify the same object. I keep hash-map keys stable.”

**About 90 seconds:** “In Kotlin, type inference chooses a static type from the initializer, and an explicit type at an API boundary can narrow what callers may do. A `List` view does not promise a snapshot if someone else still owns a mutable alias. For a data class, generated equality and hash code normally use primary-constructor properties. If one of those fields changes while the object is a map key, the Java `Map` contract does not specify the result; I would not claim that every lookup fails. I would use an immutable key, invalidate the old tenant's entry before changing identity, and test tenant isolation. At a Java collection boundary, I would copy elements if the contract requires a stable snapshot and coordinate any concurrent SDK updates.”

**Useful phrases:** “The binding stays fixed, but the object can change.” “These are equal values, not the same instance.” “The lookup result is not portable after the key changes.” “I would verify the cache instance and tenant scope first.”

**Self-check:** Can a listener hear the trace, the contract limit, and the correction? If not, pause after each cause-and-effect clause. Official free reading: [Kotlin equality](https://kotlinlang.org/docs/equality.html) and [collections overview](https://kotlinlang.org/docs/collections-overview.html), checked 2026-10-10.
