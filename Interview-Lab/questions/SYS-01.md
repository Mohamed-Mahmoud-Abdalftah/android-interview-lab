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

في system-design interview ما نبدأش برسم modules فورًا. نسأل عن المستخدمين، أهم flows، offline requirement، data sensitivity، scale، latency, device/API support وteam constraints. نحدد success/failure semantics: مثلًا هل Home تقبل partial cards؟ هل payment timeout يظهر Pending؟ بعدها نرسم data flow وsource of truth، ثم نناقش alternatives والمراقبة والاختبارات.

## Practical walkthrough

لو المحاور قال صمّم marketplace، اسأله بسرعة: التصفح offline ولا checkout؟ هل inventory تتغير كل ثانية؟ إيه اللي يحصل لو authorization نجحت والرد ضاع؟ بعدها قول assumptions بصوت واضح وارسم رحلة واحدة من tap لحد backend والـRoom. حدد رقمين مهمين فقط، مثل أقصى عمر cache أو زمن بدء الشاشة، ثم اربط كل قرار باختبار أو metric بدل ذكر أسماء مكتبات وخلاص.

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

“I start by clarifying the top user flows, scale and constraints, especially offline, latency, security and failure semantics. Then I identify sources of truth and data flow, propose a simple architecture, and test tradeoffs against those requirements.”

## Interview answer — structured

“I usually ask which flows are critical, what must work offline, what latency matters and which data is sensitive. I state assumptions and choose a source of truth for each data type. Then I sketch UI state, repository boundaries, persistence, network and background recovery. I call out failure semantics—for example partial Home success versus all-or-nothing checkout—and explain why a chosen tradeoff fits. I end with observability and a few tests that would falsify the design, rather than listing libraries.”

## Interview answer — deep senior

“A strong system-design answer is a sequence of decisions. I first bound the problem: users, main journeys, device range, offline and process-death behavior, expected traffic, security and team ownership. I ask for measurable targets such as startup time or maximum stale age only where they affect choices. Next I define local and server authority, state transitions, concurrency and retry/idempotency contracts. I draw the simplest data flow that meets those constraints, then consider scaling and modularity. I explicitly identify dangerous failures—lost response after a payment commit, stale inventory, token refresh races—and explain recovery. Finally I name metrics, tests and rollout strategy. That gives the interviewer a design they can challenge rather than a technology catalog. For the marketplace example, I would distinguish offline browsing from online checkout and ask how stale inventory may be. That single answer changes whether Room is merely a cache or part of an offline workflow. I would walk one failure from tap to server commit and back, identify who owns each state, and end with a measurable check such as cache age, payment reconciliation delay, or startup latency. I would keep the diagram small enough to revise when the interviewer changes a constraint.”

## How to answer in the interview

- **Why:** requirements decide data ownership and failure semantics.
- **How:** clarify critical journey, offline need, scale, latency, and authority before choosing layers.
- **Trade-off:** questions consume time, so prioritize those that change the architecture.
- **Failure case:** treating a payment timeout as a failure or assuming always-online.
- **Production solution:** state assumptions, draw one end-to-end flow, and name measurable verification.

## Deep-dive talking points

Practice clarifying questions, one data flow and one failure walkthrough under time pressure.

## Follow-up questions

- [SYS-02](../sys-02/): What comes after requirements? **Answer:** clear boundaries, data ownership and incremental architecture.
- [SYS-11](../sys-11/): Which failure contracts matter? **Answer:** cancellation, timeout, retry and idempotency by operation.

## Self-check rubric

Can I state assumptions, identify source of truth, defend tradeoffs and name verification evidence?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — layers, SSOT and constraints.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
