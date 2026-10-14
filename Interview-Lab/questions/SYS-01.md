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

## Explanation in Arabic

كيف تبدأ مقابلة Mobile System Design (المتطلبات، المقاييس، القيود، والمفاضلات) باحترافية كمهندس Senior/Staff؟

1. الهيكل الزمني والتكتيكي لمقابلة الـ Mobile System Design (45 دقيقة):
   - **أول 5-7 دقائق (Clarify Scope & Functional Requirements)**: لا تبدأ برسم مربعات أو كتابة كود! اطرح أسئلة توضيحية لتحديد نطاق المشكلة بدقة. ما هي الميزات الأساسية (Core Use Cases) وما الذي يقع خارج النطاق (Out of Scope)؟
   - **الدقائق 7-12 (Non-Functional Requirements & Constraints)**: حدد قيود الموبايل الفريدة: هل التطبيق Offline-First؟ ما هو حجم استهلاك البطارية والشبكة المسموح به؟ ما هو الـ Latency المستهدف؟ ما هي طبيعة الأجهزة المستهدفة (Low-end vs Flagship)؟
   - **الدقائق 12-25 (High-Level Architecture & End-to-End Flow)**: ارسم المعمارية الكلية (Data Flow): UI (Compose) -> ViewModel -> Domain (UseCases) -> Repository -> Data Sources (Local DB + Remote API) -> Backend Gateway.
   - **الدقائق 25-40 (Deep Dive into Complex Subsystems)**: التعمق في التحدي الأكبر (Sync Engine, Concurrency, Cache Eviction, Conflict Resolution).
   - **آخر 5 دقائق (Failure Modes & Trade-offs)**: استعراض سيناريوهات الفشل ونقاط الضعف والقرارات البديلة.

2. الفروق الجوهرية بين Mobile System Design و Backend System Design:
   - في الـ Backend: التركيز على QPS, Sharding, Load Balancers, Distributed Consensus.
   - في الـ Mobile: التركيز على **Resource Scarcity** (محدودية الرام والبطارية)، **Network Flakiness** (انقطاع الاتصال وتبديل الشبكات)، **Process Death**، **State Restoration**، و**Local Source of Truth**.

## Practical walkthrough

هيكلة إطار عمل مقابلة الـ System Design في كود معماري يوضح فصل المسؤوليات والـ High-Level Contracts:
```kotlin
// 1. تحديد الـ Domain Models والـ Contracts الصريحة قبل الخوض في التفاصيل:
interface FeedRepository {
    // Local Source of Truth يعيد Flow للـ UI وتحديثات فورية من قاعدة البيانات
    fun getFeedStream(): Flow<PagingData<FeedItem>>
    
    // المزامنة تتم في الخلفية بشكل منفصل
    suspend fun syncFeed(fetchStrategy: SyncStrategy): Result<Unit>
}

sealed interface SyncStrategy {
    object CacheFirst : SyncStrategy
    object NetworkFirst : SyncStrategy
    data class DeltaSync(val lastSyncTimestamp: Long) : SyncStrategy
}

// 2. نمذجة حالات الواجهة الصريحة (Unidirectional Data Flow) لمعالجة الأخطاء الجزئية:
data class FeedUiState(
    val isLoading: Boolean = false,
    val isOfflineMode: Boolean = false,
    val pendingUploadsCount: Int = 0,
    val bannerMessage: String? = null
)
```

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

Begin a mobile system design interview by clarifying functional and non-functional requirements in the first 5 minutes. Establish mobile constraints like offline tolerance, battery consumption, network flakiness, and low-end hardware profiles before proposing high-level data flow, domain contracts, and architectural trade-offs.

## Interview answer — structured

A disciplined mobile system design interview follows a structured, collaborative engineering framework.

First, with Scope Clarification & Functional Requirements, clarify the core user journeys and deliberately define out-of-scope items. For example, in an Instagram-like feed, clarify whether we are designing feed ingestion, media uploading, real-time comments, or strictly offline consumption. Next, with Mobile Constraints & Non-Functional Requirements, establish concrete operational targets.
Additionally, with Network Profile, offline-first vs. Connected-only, cellular data thrift, latency ceilings (e.g. Sub-200ms feed render from local cache). With Hardware Envelope, memory footprints for budget devices (2GB RAM), battery constraints (deferring syncs to Wi-Fi/charging via WorkManager).
With Data Volume, cache size ceilings (e.g., maximum 200MB LRU disk cache). With High-Level Architecture, establish the layered system boundary: presentation state machines, domain business logic, repository local-source-of-truth abstractions, and network/local persistence layers.
With Deep Dive & Bottlenecks, drill down into complex bottlenecks (e.g., two-way sync conflict resolution, binary chunk upload resumption, image pipeline memory management). Finally, with Trade-offs & Failure Modes, explicitly address edge cases (process death, partial backend outages, version skew).


## Interview answer — deep senior

From a staff-level perspective, the primary failure mode in mobile system design interviews is treating mobile like a stripped-down backend.

First, with The Client As An Untrusted, Volatile Runtime, backends operate in predictable server clusters; mobile clients operate on hostile, battery-constrained, physically moving devices where the OS can terminate the process at any second. Highlighting Android-specific lifecycle realities (Activity destruction, configuration changes, background execution limits) immediately differentiates senior candidates. Next, with Driving the Conversation Proactively, do not wait for the interviewer to prompt for constraints. Drive the whiteboard by outlining the API schema contract (REST vs. GraphQL vs. GRPC), storage strategy (Room SQLite vs. Proto DataStore), and telemetry footprint upfront.
Finally, with Explicit Trade-off Articulation, every architectural choice has a cost. If you choose an offline-first Room database with delta synchronization, immediately articulate the complexity trade-off: distributed conflict resolution (Client-Wins vs. Server-Wins), schema migrations, and sync queuing overhead.


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

Technically reviewed against primary documentation on 2026-10-13.
