---
id: LAB-001
lesson_id: KOT-001
status: reviewed
code_verification: tested
---
# LAB-001 — Validate a Java profile name

**Requirements:** Given a nullable SDK name, trim surrounding whitespace; reject null and empty-after-trim values; expose a safe `ProfileName` factory; use `Guest` for an optional display label. Do not treat this fallback as valid for required identity fields.

**Constraints:** Kotlin/JVM, JDK 17, no Android SDK or external service. Starter: [Java SDK fake](../projects/kotlin-jvm-labs/src/main/java/academy/LegacyProfileApi.java) and [JUnit behavior tests](../projects/kotlin-jvm-labs/src/test/kotlin/academy/LabChecksTest.kt). Read those first, then implement without looking at the [reference solution](../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileName.kt).

**Approach:** A brute-force collection of scattered UI null checks has O(n) code sites to audit as the app grows. A single boundary factory performs O(m) trimming for input length m and O(m) storage for the normalized string in this implementation; later consumers use a validated type. This is an architecture benefit, not a measured performance claim. Invariant: every `ProfileName` returned by `parse` has a nonempty `value`.

**Checks:** Run `./gradlew clean test check run --no-daemon` from `projects/kotlin-jvm-labs/`. JUnit Jupiter discovers eight tests: seven safe-behavior cases and one expected unsafe Java null dereference. A useful extension is testing a product-specific maximum length. A Java API changing its null contract is a production caveat, not something Kotlin's type declaration can guarantee.

**Review rubric (10):** 3 correct null and blank handling, 2 validated invariant, 2 boundary placement, 2 behavior checks, 1 clear optional-field semantics. Optional self-check only; no timer or score is applied in Learning Mode.
