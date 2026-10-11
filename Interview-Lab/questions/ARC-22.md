---
id: "ARC-22"
question: "A Repository returns an API DTO directly to Compose. What coupling risks follow?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "C"
phase: 2
priority: "P1"
order: 167
editorial_status: "reviewed"
---

# ARC-22

## Original interview question

A Repository returns an API DTO directly to Compose. What coupling risks follow?

## What the interviewer evaluates

Identify transport-schema coupling, null/error leakage and UI churn from direct DTO exposure.

## Explanation in Arabic

Repository بترجع `UserDto` لـCompose يعني UI بقت مرتبطة بأسماء JSON fields، nullable transport fields، وAPI version. أي server rename أو تغيير units ينتقل للشاشة، وممكن `null` يتعرض كقيمة أو يعمل crash. كمان DTO غالبًا لا تمثل cache freshness ولا domain validation. الأحسن repository تعمل mapping لـdomain model أو app data contract، وViewModel يطلع UI model للعرض. لكن ما تعملش models متطابقة بلا سبب؛ اعزل boundaries اللي احتمال تغييرها أو فيها invariants حقيقية.

## Why it matters and how it works

A repository should hide data sources and expose stable app data. A DTO is optimized for transport, not rendering. Mapping prevents server schema changes from rippling into UI and gives one place for validation and error classification.

## Worked example

Scenario: `ProductDto(priceCents: Long?, title: String?)` is rendered directly. A server rollout changes price unit or omits title; Compose now decides fallback and may display `0`. Instead data maps to `Product(id, Money(minor, currency), title)` or typed invalid-payload error; ViewModel formats locale text.

## Trade-offs and decision criteria

Mapping costs code and allocations. If an internal API is truly stable and the DTO already matches domain semantics, sharing may be acceptable temporarily; document the coupling and test contract changes. High-risk money and auth data deserve explicit models.

## Failure modes

A nullable DTO price gets `?: 0`, turning malformed data into a free product display. Another failure is Compose importing Retrofit annotation types, making a network client replacement require UI edits.

## Production perspective

An ecommerce app maps versioned price payloads and validates currency in data. Compose sees stable `ProductUiState`; API contract tests catch new fields and units before release.

## Interview answer — short

Returning an API DTO from a repository couples Compose to server schema, transport nullability and units. I map to validated app/domain data, then UI state, so contract changes are handled at one boundary.

## Interview answer — structured

A DTO represents what the server sent, not necessarily what the screen should trust or display. If it reaches Compose, network field names, nullable values and error conventions become UI dependencies. A server rollout can force UI changes or create silent defaults. I would map in the data layer to a stable model with validated ID and units, and let the ViewModel format it for the screen. I add only mappings that protect real differences, not redundant copies for every layer. A simple demonstration is a price field changing from integer cents to a decimal string. If Compose depends on the DTO, each screen must interpret the new unit and may disagree. A single data mapper can validate the conversion before UI sees it.

## Interview answer — deep senior

The coupling risk is broader than a compile error. A DTO might allow missing required fields, represent cents as a nullable number, or use server enum strings that can gain unknown values. If UI chooses defaults independently, two screens may disagree or display false business facts. Repository mapping centralizes validation and preserves a stable app contract, while UI mapping handles locale and visual state. I would test payload changes and malformed cases at the adapter boundary, and avoid exposing Retrofit `Response` or exception types through the repository. There is a maintenance cost to extra models, so I choose them where transport and domain have independent reasons to change. For price, payment or account data, that protection is usually worth it. I would check whether the DTO also leaks server enum values, optional IDs or raw exception text. Those are transport concerns with different evolution and trust rules than UI. The repository should expose a model that represents validated app meaning, and the ViewModel should project it for locale and screen design. Mapping is not free, but tests at the boundary catch drift early. For business-critical values such as money, I prefer an explicit unit type and reject malformed payloads rather than substituting zero.

## Deep-dive talking points

Analyze DTO field rename, nullability, units, unknown enum, UI formatting and repository contract tests.

## Follow-up questions

- [ARC-06](../arc-06/): Where should the DTO live? **Answer:** in Data next to transport, not in Compose.
- [ARC-07](../arc-07/): What should a mapper validate? **Answer:** required fields, units and unknown values without false defaults.

## Self-check rubric

List three coupling risks and sketch the DTO-to-domain-to-UI mapping for a nullable price.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository abstraction.
- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — UI state production.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
