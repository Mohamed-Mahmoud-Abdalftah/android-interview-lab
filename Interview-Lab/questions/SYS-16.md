---
id: "SYS-16"
question: "Compare simple MVVM and Clean Architecture for different app sizes."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 345
editorial_status: "reviewed"
---

# SYS-16

## Original interview question

Compare simple MVVM and Clean Architecture for different app sizes.

## What the interviewer evaluates

Choose simple MVVM or additional Clean Architecture boundaries by complexity and reuse.

## Explanation in Arabic

لتطبيق صغير، ViewModel + repository + data sources مع unidirectional state غالبًا كفاية؛ use case لكل getter يزود boilerplate بلا قيمة. لما business rules تتكرر في شاشات أو تحتاج independence/testability قوية، domain layer/use cases أو interfaces مستقلة تستحق الكلفة. المهم single source of truth، lifecycle، error/cancellation contract، مش اسم pattern.

## Why it matters and how it works

Android architecture recommends UI and data layers, optional domain layer. MVVM is a UI state-holder pattern; Clean Architecture describes dependency and business-rule boundaries, so they are not mutually exclusive. Add abstractions when they isolate volatility or shared complex policy.

## Worked example

Conceptual small-app graph versus scaled business rule; code is illustrative.

```kotlin
// Small app: Screen -> ViewModel -> NotesRepository -> Room/HTTP.
// Shared checkout rule: CheckoutViewModel -> QuoteUseCase
// -> PricingRepository + InventoryRepository.
// Keep UI types out of the shared domain rule.
```

## Trade-offs and decision criteria

Simple MVVM minimizes indirection and speeds iteration; additional domain boundaries ease reuse and independent tests but impose mapping/DI burden. Avoid UI directly calling Retrofit/DAO for complex state, and avoid ceremonial interfaces for classes with one stable caller.

## Failure modes

A ViewModel that owns SQL and token refresh becomes hard to test and leaks lifecycle concerns into data. Conversely, six pass-through layers hide where a bug lives. A use case that references Activity context is not truly domain-independent.

## Production perspective

A small notes app uses ViewModel+Repository. A checkout app extracts pricing/discount eligibility into shared use cases because multiple screens and worker paths need identical rules. Both use Room/server authority for persistent data.

## Interview answer — short

“I use the simplest layered MVVM that meets the problem: UI state in ViewModel and data ownership in repository. I add domain/use-case boundaries when business logic is complex or reused, not as mandatory ceremony.”

## Interview answer — structured

“MVVM and Clean Architecture answer different questions. MVVM helps organize screen state and events; a clean dependency boundary can keep business rules independent of UI and data implementation. Android’s guidance starts with UI and data layers and treats domain as optional. For a small app, a ViewModel calling a repository is clear. If pricing or eligibility rules are reused across screens and workers, I extract a testable use case and perhaps an interface. I judge the extra mapping and DI cost against real coupling.”

## Interview answer — deep senior

“I begin with explicit responsibilities rather than a pattern diagram. UI renders immutable state; ViewModel coordinates screen lifetime; repository owns data sources and conflict policy. That may be enough for one team and a simple feature. When the same business rule spans several ViewModels, background work or alternative data implementations, I introduce a domain boundary with stable inputs/outputs and tests. I avoid both a god ViewModel that contains SQL/network logic and a maze of pass-through use cases that add no invariant. Process death, cancellation, offline source of truth and server authority remain the same regardless of pattern label. I measure change impact and test friction before expanding layers. A small notes app uses ViewModel+Repository.”

## Deep-dive talking points

Identify a rule that justifies extraction and one that does not.

## Follow-up questions

- [SYS-02](../sys-02/): What layers are baseline? **Answer:** UI and data, with domain optional.
- [MOD-13](../mod-13/): When interface? **Answer:** when it protects a real ownership/volatility boundary.

## Self-check rubric

Can I choose by complexity, keep business rules out of UI and avoid ceremonial layers?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — optional domain layer.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository responsibilities.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
