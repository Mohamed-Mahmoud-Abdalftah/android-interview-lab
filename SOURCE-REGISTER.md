# Source register

Checked on **2026-10-10** via the publicly accessible official pages below. “Documented” means the linked page directly supports the stated concept. “Observed” refers to the local build in [BUILD-VERIFICATION](BUILD-VERIFICATION.md). No external video, transcript, or audio resource was verified for this batch.

The [manifest](CONTENT-MANIFEST.json) now marks all unauthored lesson references `pending_verification` with no lesson-specific `source_urls`. A checked general reading page below does not prove a future topic's claims. Each newly authored lesson must research and record sources that directly support that topic before promotion to `reviewed`.

| Page | Exact URL | Version / applicability | Evidence and uncertainty |
|---|---|---|---|
| Amazon interview loop | https://amazon.jobs/content/en/how-we-hire/interview-loop | INT-004, employer-specific | Official STAR preparation guidance; checked 2026-10-10. This is not a universal hiring rubric. |
| Amazon interview guide | https://www.aboutamazon.com/news/workplace/amazon-interview-guide | INT-004, employer-specific | Official explanation of truthful STAR story structure and outcomes; checked 2026-10-10. |
| Google SRE postmortem culture | https://sre.google/workbook/postmortem-culture/ | INT-004 leadership scenario | Primary guidance on blameless analysis and action items; checked 2026-10-10. |
| Kotlin null safety | https://kotlinlang.org/docs/null-safety.html | Kotlin language; Day 1 | Documented nullable/non-null types and NPE escape hatches; checked 2026-10-10. |
| Kotlin basic syntax | https://kotlinlang.org/docs/basic-syntax.html | Week 1 reading | Official free written guide; checked 2026-10-10. |
| Kotlin equality | https://kotlinlang.org/docs/equality.html | KOT-002 research | Documents `==`, `===`, `equals()`/`hashCode()` relationship and array caveat; checked 2026-10-10. |
| Kotlin arrays | https://kotlinlang.org/docs/arrays.html | SYS-001, JVM lab | Documents Array/primitive arrays and indexed operations; checked 2026-10-10. |
| Java SE 17 HashMap | https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html | SYS-001 | Documents conditional constant-time basic operations under suitable hash distribution; checked 2026-10-10. |
| Kotlin collections overview | https://kotlinlang.org/docs/collections-overview.html | KOT-002 research | Documents read-only versus mutable interfaces and that a `val` mutable collection can still change; checked 2026-10-10. |
| Kotlin properties | https://kotlinlang.org/docs/properties.html | KOT-002 research | Documents `val`/`var` properties and accessors; checked 2026-10-10. |
| Kotlin functions | https://kotlinlang.org/docs/functions.html | KOT-004 | Documents functions, parameters and local functions; checked 2026-10-10. |
| Kotlin lambdas | https://kotlinlang.org/docs/lambdas.html | KOT-004 | Documents higher-order functions, lambda syntax and closure capture; checked 2026-10-10. |
| Kotlin inline functions | https://kotlinlang.org/docs/inline-functions.html | KOT-004 | Documents inline, non-local returns, noinline and crossinline; checked 2026-10-10. |
| Kotlin classes | https://kotlinlang.org/docs/classes.html | KOT-003, Kotlin 2.4.20 example | Documents primary/secondary constructors, property/init source order, delegation and validation; checked 2026-10-10. |
| Kotlin inheritance | https://kotlinlang.org/docs/inheritance.html | KOT-003 | Documents base-before-derived initialization and the danger of open-member calls from constructors; checked 2026-10-10. |
| Kotlin visibility modifiers | https://kotlinlang.org/docs/visibility-modifiers.html | KOT-003 | Documents private constructor syntax and internal module scope; checked 2026-10-10. |
| Java SE 17 Map contract | https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html | KOT-002 research, JVM lab | Warns map behavior is unspecified when a key changes in a way that affects equality; checked 2026-10-10. |
| Kotlin Java interop | https://kotlinlang.org/docs/java-interop.html | Kotlin/JVM; Day 1 | Documented platform types and relaxed checks; exact vendor SDK behavior must be tested. |
| Kotlin type checks and casts | https://kotlinlang.org/docs/typecasts.html | Kotlin language; Day 1 | Documented smart-cast stability rules. |
| Kotlin data classes | https://kotlinlang.org/docs/data-classes.html | Kotlin language; KOT-Q005 | Documented generated `copy`; local 2.4.20 compiler warning supplies exact visibility evidence. |
| ConsistentCopyVisibility API | https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-consistent-copy-visibility/ | Kotlin 2.x; KOT-Q005 | Documents prior public `copy` visibility; future behavior may differ. |
| Kotlin Gradle configuration | https://kotlinlang.org/docs/gradle-configure-project.html | KGP 2.4.20 with Gradle 9.6.1 | Official compatibility matrix lists KGP 2.4.20 with Gradle 7.6.3–9.7.0; the selected pair also built locally. |
| Gradle Java compatibility | https://docs.gradle.org/current/userguide/compatibility.html | Gradle 9.6.1 on JDK 17 | Official matrix includes Java 17 runtime support. |
| JUnit Jupiter Gradle build support | https://docs.junit.org/5.14.4/running-tests/build-support.html | JUnit 5.14.4, JVM lab | Official BOM, Jupiter, launcher, and Gradle setup; dependencies resolved and eight tests ran locally on 2026-10-10. |
| Kotlin functional interfaces | https://kotlinlang.org/docs/fun-interfaces.html | ARC-001 | Documents one-method functional interfaces and SAM creation; checked 2026-10-10. |
| Android domain layer | https://developer.android.com/topic/architecture/domain-layer | ARC-001 guidance | Recommends use cases when business logic is reused or complex; checked 2026-10-10. |
| Android architecture recommendations | https://developer.android.com/topic/architecture/recommendations | ARC-001 guidance, no Android SDK | Recommends UI/data boundaries and contextual domain use cases; no Android app was built. |
| Android activity lifecycle | https://developer.android.com/guide/components/activities/activity-lifecycle | AND-001 guidance, no Android SDK | Documents callbacks, visibility/foreground distinctions and configuration recreation; checked 2026-10-10. |
| Android RecyclerView guide | https://developer.android.com/develop/ui/views/layout/recyclerview | UI-001 guidance, no SDK build | Documents LayoutManager, Adapter and ViewHolder roles; checked 2026-10-10. |
| AndroidX ListAdapter API | https://developer.android.com/reference/kotlin/androidx/recyclerview/widget/ListAdapter | UI-001 guidance | Documents submitList/currentList and skipped earlier commit callbacks; checked 2026-10-10. |
| AndroidX DiffUtil.ItemCallback | https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil.ItemCallback | UI-001 guidance | Documents identity versus content callbacks; checked 2026-10-10. |
| Android view binding | https://developer.android.com/topic/libraries/view-binding | UI-001 guidance | Documents Fragment binding cleanup at onDestroyView; checked 2026-10-10. |
| Android Fragment lifecycle | https://developer.android.com/guide/fragments/lifecycle | AND-001 guidance, no Android SDK | Documents separate view lifecycle and onDestroyView cleanup; checked 2026-10-10. |
| Android process lifecycle | https://developer.android.com/guide/components/activities/process-lifecycle | AND-001 guidance | States onDestroy is not guaranteed for system process kill; checked 2026-10-10. |
| Android saved UI state | https://developer.android.com/topic/libraries/architecture/saving-states | AND-001 guidance | Distinguishes saved UI restoration from durable data storage; checked 2026-10-10. |
| Kotlin coroutine basics | https://kotlinlang.org/docs/coroutines-basics.html | COR-001, kotlinx-coroutines 1.11.0 | Documents suspend, scope, structured child lifetimes, async and runBlocking; checked 2026-10-10. |
| kotlinx coroutineScope API | https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/coroutine-scope.html | COR-001 | Documents in-place scope, child completion and cancellation; checked 2026-10-10. |
| Android coroutine best practices | https://developer.android.com/kotlin/coroutines/coroutines-best-practices | COR-001 guidance, no Android build | Documents main-safe data APIs, dispatcher injection and ViewModel ownership; checked 2026-10-10. |
| Android coroutines guide | https://developer.android.com/kotlin/coroutines | COR-001 guidance, no Android build | Documents dispatchers and viewModelScope; checked 2026-10-10. |
| Kotlin coroutines overview | https://kotlinlang.org/docs/coroutines-overview.html | Future Week 2 reading | Page was accessed; future coroutine library versions must be pinned separately. |
| Android coroutine testing | https://developer.android.com/kotlin/coroutines/test | Future Week 2/8 reading | Page was accessed; notes `runTest` and controlled test schedulers. |
| Android data layer | https://developer.android.com/topic/architecture/data-layer | Future Week 4/6/7 reading | Page was accessed; architecture recommendations require adaptation to requirements. |
| Compose state | https://developer.android.com/develop/ui/compose/state | Future Week 5 reading | Page was accessed; no Compose version selected yet. |
| OWASP mobile security | https://mas.owasp.org/ | Future Week 6/extended reading | Official free MASVS/MASTG entry point accessed; no certification claim. |
| AGP built-in Kotlin migration | https://developer.android.com/build/migrate-to-built-in-kotlin | AGP 9.0+ | Official page says built-in Kotlin enabled by default; a future Android toolchain must be chosen as a compatible set before build files are written. |

**Not yet reverified for a pinned build:** Android SDK/AGP/Kotlin/Gradle/KSP/Compose/AndroidX compatibility as a full set; Android 16/17 target-specific behavior; Navigation 2 versus 3 maturity; Android SDK presence; specific free listening videos. The schedule's future references are study directions, not verified version claims. Source dates must be refreshed for each authored batch.
