# KOT-001 technical review — 2026-10-10

This is an editorial claim audit, separate from structural validation and test execution. The checked code is the Day 1 Kotlin/JVM lab on JDK 17 with Kotlin Gradle plugin 2.4.20. It does not establish Android ART or production vendor SDK behavior.

| Claim | Evidence | Review decision |
|---|---|---|
| `String` versus `String?` | [Kotlin null safety](https://kotlinlang.org/docs/null-safety.html) | Lesson distinguishes compile-time nullable checking from documented NPE escape hatches. |
| Unannotated Java result is a platform type; direct `.length` may throw | [Kotlin Java interop](https://kotlinlang.org/docs/java-interop.html); JUnit unsafe-boundary regression in `LabChecksTest` | Correct for the fake Java method. The test expects `NullPointerException`; it does not claim all Java APIs return null. |
| Smart cast needs a stable checked value | [Kotlin type checks and casts](https://kotlinlang.org/docs/typecasts.html) | Local snapshot advice is sound; the lesson explicitly avoids claiming it synchronizes concurrent owner updates. |
| Null and blank are distinct validation cases | [KOT-001 code](projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileName.kt) and JUnit tests | The factory checks both; `Guest` is stated as an optional UI-label decision, not a required identity policy. |
| Private-constructor data-class `copy()` can bypass a factory under the pinned setup | [Kotlin data classes](https://kotlinlang.org/docs/data-classes.html), [ConsistentCopyVisibility](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-consistent-copy-visibility/), and historical local compiler warning in [build evidence](BUILD-VERIFICATION.md) | The current implementation uses an ordinary class. Exact generated visibility is version/configuration-sensitive and is labeled as such. |
| Trace and follow-up answers match the code | [Lesson](01-Kotlin-JVM-ART/KOT-001-nullability-java-boundary.md), [Q1–Q5 index](Interview-Question-Bank/BY-TOPIC.md), [JUnit tests](projects/kotlin-jvm-labs/src/test/kotlin/academy/LabChecksTest.kt) | The null, blank, ordinary, and unsafe paths are each represented. The snippet containing `return ProfileName(normalized)` must be read inside `ProfileName.parse`, where the private constructor is accessible. |

**Open learning boundaries:** Java nullability annotations vary by vendor/compiler configuration; Unicode whitespace policy is product-specific; real SDK and Android behavior are untested. These are documented limits, not passed tests.
