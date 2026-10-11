---
id: "PAT-02"
question: "Compare creational, structural, and behavioral patterns."
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 193
editorial_status: "reviewed"
---

# PAT-02

## Original interview question

Compare creational, structural, and behavioral patterns.

## What the interviewer evaluates

Classify patterns by intent and give discriminating examples, not just memorized lists.

## Explanation in Arabic

GoF بتقسم patterns: Creational تعالج إنشاء objects (`Factory Method`, `Abstract Factory`, `Builder`, `Singleton`)، Structural تعالج تركيب أو تغليف objects (`Adapter`, `Facade`, `Decorator`, `Proxy`)، Behavioral تعالج تفاعل ومسؤوليات (`Observer`, `Strategy`, `State`, `Command`). التقسيم حسب المشكلة الأساسية، مش implementation syntax؛ `object` في Kotlin ممكن ينفّذ Singleton لكن وجود object وحده مش مبرر global state. وفي Android شوف SDK adapter، Flow observer، payment strategy. بعض الأنماط تتداخل في تطبيق واقعي، وممكن class واحدة تلعب أكثر من دور.

## Why it matters and how it works

The taxonomy helps choose a starting family: construction, composition/interface shaping, or changing behavior and communication. The same feature may use several categories at distinct boundaries. Intent and consequence matter more than a pattern name.

## Worked example

Scenario: SDK needs complex configuration, so Builder creates a client (creational). A wrapper converts its callback to a domain result (Adapter, structural). Checkout chooses card or wallet route (Strategy, behavioral). UI observes repository state (Observer-like behavior).

## Trade-offs and decision criteria

Categorization is a navigation aid, not an implementation rule. A factory can hide an SDK while a strategy selects behavior; do not confuse them because both may appear in provider routing. Patterns add indirection if simple language constructs suffice.

## Failure modes

A class named `PaymentFactory` contains SDK calls, retry policy and UI navigation; the name “creational” cannot excuse mixed concerns. Separate construction/selection from provider behavior and UI state.

## Production perspective

A multi-provider app uses Hilt for construction, adapters for vendor APIs, strategies for provider behavior and observable state for UI. Contract tests verify semantics across each boundary.

## Interview answer — short

Creational patterns organize object creation, structural patterns organize composition or interface adaptation, and behavioral patterns organize algorithms and communication. I classify by intent, then choose the smallest useful implementation.

## Interview answer — structured

For a concrete Android feature, I might use Builder to configure a client, Adapter to translate a vendor callback, and Strategy to choose payment handling. Those are creational, structural and behavioral concerns respectively. The categories help me identify which problem I am solving, but the same app can combine them. I would not add a Factory just because construction occurs; ordinary constructors or DI may already be clear. The pattern must make change and testing easier.

## Interview answer — deep senior

The GoF categories are a map of design forces. Creational patterns hide or coordinate construction; structural patterns compose objects and reconcile interfaces; behavioral patterns describe how responsibilities and state-driven actions collaborate. I ask what is varying: object family, vendor API surface, or runtime algorithm. Confusing these leads to god-objects that both construct and execute providers while also controlling UI. Kotlin syntax can implement the intent compactly, and Android lifecycle may add constraints the original pattern catalog does not address. In production I define the contract, error semantics, ownership and tests. A category is useful for explanation, but it does not prove performance, substitutability or process-death correctness.

## Deep-dive talking points

Classify Builder, Adapter, Strategy and Observer in one checkout flow; note overlapping roles.

## Follow-up questions

- [PAT-03](../pat-03/): Which patterns manage construction? **Answer:** Singleton, Factory, Abstract Factory and Builder differ in what they create.
- [PAT-05](../pat-05/): Which manage behavior? **Answer:** Observer, Strategy, State, Command and Chain of Responsibility.

## Self-check rubric

Classify four named patterns by problem, then reject one unnecessary factory in a simple case.

## References and reviewed-on date

- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — language-level Singleton example.
- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — original taxonomy and catalog.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
