---
id: "SYS-01"
question: "How do you begin a mobile system-design interview (requirements, scale, constraints, trade-offs)?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 330
editorial_status: "reviewed"
---

# SYS-01

## Original interview question

How do you begin a mobile system-design interview (requirements, scale, constraints, trade-offs)?

## What the interviewer evaluates

Begin system-design answer with scope, nonfunctional requirements, constraints and measurable tradeoffs.

## Concept and technical explanation

A mobile system design interview differs fundamentally from backend system design. While backends prioritize queries per second, distributed database sharding, and consensus algorithms, mobile design centers on client resource scarcity, network volatility, operating system lifecycle constraints, and offline data consistency. Beginning an interview effectively requires a structured, collaborative engineering framework. In the first five to seven minutes, the engineer must clarify functional scope, defining core user journeys while explicitly bounding what is out of scope to avoid low-impact rabbit holes. Next, non-functional requirements must be established with concrete mobile metrics: offline-first versus online-only durability, cold startup latency thresholds (such as under 400 milliseconds), disk cache size ceilings (such as 150 megabytes), battery and cellular data constraints, and target hardware tiers (such as low-end Android devices with two gigabytes of RAM). Before selecting any libraries or third-party frameworks, the high-level architecture must be established around unidirectional data flow: UI state holders observing reactive database streams, domain use cases orchestrating business rules, and repositories mediating between local persistence and remote network APIs. Only after aligning on data flow and state ownership should the discussion drill down into complex subsystems, failure modes, and architectural trade-offs.

## Practical walkthrough (English)

Structuring the mobile system design scaffold with clear boundaries and domain contracts:
```kotlin
// 1. Domain contracts establishing repository boundaries before technical implementations
interface FeedRepository {
    // Local single source of truth streaming reactive UI state from disk
    fun getFeedStream(): Flow<PagingData<FeedItem>>

    // Explicit background synchronization contract with configurable strategy
    suspend fun syncFeed(strategy: SyncStrategy): Result<SyncSummary>
}

sealed interface SyncStrategy {
    data object CacheFirst : SyncStrategy
    data object NetworkFirst : SyncStrategy
    data class DeltaSync(val lastSyncTimestampMs: Long) : SyncStrategy
}

// 2. Unidirectional UI State modeling to handle partial failures and offline modes
data class FeedUiState(
    val isLoading: Boolean = false,
    val isOfflineMode: Boolean = false,
    val pendingUploadsCount: Int = 0,
    val bannerMessage: String? = null
)

// 3. User intent actions dispatched to the state machine
sealed interface FeedUserAction {
    data object RefreshTriggered : FeedUserAction
    data class ItemLiked(val itemId: String) : FeedUserAction
    data class RetrySyncRequested(val failedBatchId: String) : FeedUserAction
}
```

## Explanation in Arabic

في مقابلة `Mobile System Design`، البداية الصح بتبدأ بتوضيح الـ Scope في أول 5 دقائق والاتفاق على الـ Core Features وما هو خارج النطاق. بعدها بتحدد الـ Non-Functional Requirements الخاصة بالموبايل: قيود الـ Client من ناحية الرام والبطارية (Resource Scarcity)، تذبذب الشبكة (Network Flakiness)، ودعم الـ Offline Mode. بعد كده بترسم المعمارية الكلية بتدفق أحادي (Unidirectional Data Flow) ومصدر حقيقة محلي في الـ Database قبل الدخول في تفاصيل الـ Libraries.

## Practical walkthrough

في تصميم Feed لتطبيق صور، بنحدد في الأول إن الـ Scope هو التصفح والعرض دون إنترنت. الـ Non-Functional Requirements: تشغيل التطبيق في أقل من ثانية، كاش لا يتجاوز 150MB على القرص، والعمل على أجهزة بـ 2GB RAM. بعدها بنرسم الـ High-Level Architecture: الـ UI (Compose) بيراقب StateFlow من Room عبر الـ Repository، بينما WorkManager في الخلفية بينفذ مزامنة البيانات من الشبكة بسياسة محددة.

## Why it matters and how it works

Use a few explicit assumptions when interviewer leaves gaps; prioritize top user journey and most dangerous failure. Quantify rough load (active users, cache size, request rate) only if relevant. Build from boundaries: UI state holder, domain/use cases if justified, repositories, local/remote sources, backend contracts and background recovery.

## Worked example

Interview whiteboard artifact, not executable app code; write a decision record with constraints and measurable outcomes.

```kotlin
data class DesignBrief(
    val mustWorkOffline: Boolean,
    val maxColdStartMs: Long,
    val dataSensitivity: String,
    val acceptablePartialFailure: Boolean,
)
// Use the brief to evaluate architecture options and tests.
```

## Trade-offs and decision criteria

Asking too many questions can consume interview time; focus on constraints that change the design. Starting with a simple architecture helps, then expand only for scale or risk. Avoid naming technologies before agreeing on consistency and durability requirements.

## Failure modes

A design that assumes always-online may fail the core user scenario. Calling a payment timeout Failure can trigger duplicates. A giant generic architecture diagram can hide who owns data and how process death is recovered.

## Production perspective

For a marketplace app, clarify browsing offline versus checkout online, account scale, acceptable stale inventory and team ownership. Propose Room-backed feed, server-authoritative checkout, explicit Pending payment and measurable startup/ANR/Sync SLAs.

## Interview answer — short

We begin a mobile system design interview by clarifying functional boundaries and mobile-specific constraints before sketching architecture or picking libraries. We define core user journeys, latency budgets, offline expectations, battery limits, and budget device targets. Then we sketch unidirectional data flow from presentation to persistence, proactively addressing process death, network volatility, and local data consistency.

## Interview answer — structured

A disciplined mobile system design interview begins with collaborative problem scoping rather than immediate architecture diagrams.
In the first five minutes, I clarify primary user journeys and establish what is deliberately out of scope to prevent unproductive diversions.
Next, I establish mobile-specific non-functional requirements that directly dictate architectural decisions: whether the application must be offline-first, the acceptable latency threshold for screen rendering, cache size limits, and the minimum hardware envelope like budget Android devices with two gigabytes of RAM.
Once requirements and scale are bounded, I establish high-level boundaries showing unidirectional data flow: UI state holders observing reactive database streams, domain interactors executing business policies, and repositories coordinating remote APIs with local persistence.
Only after aligning on data flow and state ownership do we dive deep into complex bottlenecks like background synchronization conflict resolution, payload compaction, and process death recovery, concluding with explicit failure modes and architectural trade-offs.

## Interview answer — deep senior

What distinguishes a staff-level mobile engineer in system design is recognizing that mobile clients run inside an untrusted, resource-constrained, and hostile operating environment.
Unlike backend nodes that run in controlled server clusters, Android applications face spontaneous process termination by the Low Memory Killer, battery preservation restrictions imposed by Doze mode, and hostile network handoffs between cellular towers and Wi-Fi.
When opening the interview, I proactively articulate these runtime realities before the interviewer prompts me.
I frame the client database as the local single source of truth and the remote network as an asynchronous synchronization mechanism.
This immediately sets up a discussion around data durability, write queues, and idempotent mutations.
Furthermore, I establish operational trade-offs upfront.
Choosing an offline-first Room architecture with delta synchronization delivers instant UI rendering and zero offline perceived latency, but introduces substantial complexity around distributed conflict resolution, database schema migrations, and sync queuing overhead.
Conversely, an online-only cache-aside strategy simplifies state management and cuts client storage footprint, but degrades user experience during poor connectivity and increases backend request volume.
To complete the system envelope, I establish operational monitoring metrics including ANR rate thresholds under zero point four percent, cold startup latency targets under four hundred milliseconds, and automated contract testing with backend teams to validate schema evolution before shipping client releases.
Framing every decision around concrete trade-offs, operational failure modes, and client resource budgets demonstrates production maturity.

## How to answer in the interview

- **Why:** requirements decide data ownership and failure semantics.
- **How:** clarify critical journey, offline need, scale, latency, and authority before choosing layers.
- **Trade-off:** questions consume time, so prioritize those that change the architecture.
- **Failure case:** treating a payment timeout as a failure or assuming always-online.
- **Production solution:** state assumptions, draw one end-to-end flow, and name measurable verification.

## Deep-dive talking points

Practice clarifying questions, one data flow and one failure walkthrough under time pressure.

## Follow-up questions

- **Interviewer:** "What is the single most common mistake candidates make in mobile system design?"
  **Answer:** "Jumping straight into UI components or database schemas without clarifying requirements, scale constraints, and network failure modes."

- **Interviewer:** "How do you handle ambiguous requirements intentionally given by an interviewer?"
  **Answer:** "Make explicit engineering assumptions out loud, validate them with the interviewer, and document them on the whiteboard before continuing."

## Self-check rubric

Can I state assumptions, identify source of truth, defend tradeoffs and name verification evidence?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — layers, SSOT and constraints.

Technically reviewed against the cited primary documentation on 2026-10-19; agent editorial review, not human verification.
