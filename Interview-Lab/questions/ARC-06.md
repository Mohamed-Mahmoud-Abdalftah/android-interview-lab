---
id: "ARC-06"
question: "Where should DTOs, Room entities, domain models, and UI models live?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 151
editorial_status: "reviewed"
---

# ARC-06

## Original interview question

Where should DTOs, Room entities, domain models, and UI models live?

## What the interviewer evaluates

Assign transport, persistence, domain and rendering models to boundaries and explain mapping.

## Explanation in Arabic

DTO شكل network contract وبيعيش جنب Retrofit/service في data. Room entity شكل الجدول وعلاقاته وبيعيش في persistence/data. Domain model يمثّل business meaning من غير HTTP أو SQL annotations، وUI model يمثّل اللي الشاشة محتاجاه بالضبط، زي formatted amount وenabled button. ساعات model واحدة تكفي في app صغير، لكن ما تستخدمش DTO كـUI model لمجرد تقليل mapping؛ تغيّر اسم field في API ممكن يكسر Compose ويكشف nullable transport noise. Mapper يعمل validation ومعالجة version/schema بوضوح.

### Practical walkthrough in Egyptian Arabic

DTO تمثل wire schema وقد تحتوي fields nullable، Room entity تمثل storage schema، domain model يمثل invariant، وUiModel يمثل العرض. مثال price cents: لا تسمح DTO string غير صالحة تصبح domain amount بلا validation. تغيير API name أو DB column لا يجب أن يغير Compose screen. إذا موديل واحد يكفي لتطبيق صغير ومستقر، لا تنسخ classes بلا حاجة.

## Why it matters and how it works

Each model has a different reason to change: server schema, database migration, business rule, or screen design. Separate models at unstable boundaries, but avoid duplicating identical types without benefit. The data layer maps external representations into app data.

## Worked example

Conceptual mapping: `BalanceDto(amountMinor: Long, currencyCode: String)` from Retrofit becomes `Balance(Money(amountMinor, CurrencyCode(...)))` after validation; `BalanceEntity` stores stable columns in Room; `BalanceUiState(displayAmount: String)` uses locale formatting in UI. Never persist display text as authoritative amount.

## Trade-offs and decision criteria

Model separation adds conversion code and tests. For a tiny stable feature, DTO and domain can coincide temporarily if no important policy depends on them; document the coupling. For money, authentication, and offline sync, explicit models usually pay off.

## Failure modes

A server changes `amount` from integer cents to decimal string while Compose directly renders DTO; UI silently misformats. Another risk is storing transient `isLoading` in Room entity as though it were business data. Validate units and separate screen ephemera.

## Production perspective

An offline wallet maps validated response DTOs into domain Money values, persists minor units in Room, and exposes locale-specific UI text. Schema migrations and server-version tests protect both boundaries; server balance remains authoritative.

## Interview answer — short

DTOs belong to transport, Room entities to persistence, domain models to business meaning, and UI models to rendering. I map at boundaries so schema changes do not ripple through the app, especially for units and nullability.

## Interview answer — structured

These models answer different questions. A DTO matches a server payload, an entity matches local storage, a domain model expresses product rules, and a UI model has exactly what a screen needs to display. In a small app some types may be shared intentionally, but sharing should be a choice, not an accident. I validate and map at boundaries, especially for money units, optional fields, and error values. This keeps Compose from depending on Retrofit or Room details. This becomes critical when external and internal units differ. I would reject an absent required currency or convert minor units explicitly, then format at the UI boundary. One model used everywhere can be acceptable for a tiny stable feature, but it should be an explicit decision with tests.

## Interview answer — deep senior

I evaluate model separation by volatility and correctness risk. Server payloads can change independently of database schema; domain invariants such as positive amount or currency units should not depend on JSON annotations; UI formatting depends on locale and design. Mapping provides a controlled place to reject malformed data, choose defaults only where valid, and track migration. Excessive one-to-one models with no distinct contract add boilerplate, so I consolidate where boundaries truly align. In an offline-first app, Room entity design also reflects query and migration needs, while repository emits domain data from the local source of truth. I never let a formatted UI string become the canonical money value or let transport nullability leak into every composable. The four-model picture is not a requirement to copy every field four times. I look for independent reasons to change: server version, database migration, business invariant, and locale/design. When those are real, mapping localizes them. A Room entity might include indexing and foreign keys that the domain should never see. A UI model might include formatted text and button enablement that should never be persisted. I validate at each ingress and keep authoritative numeric values separate from display strings.

## How to answer in the interview

- **Why:** different boundaries have different contracts.
- **How:** map and validate at crossings.
- **Trade-off:** isolation versus conversion cost.
- **Failure case:** nullable DTO becomes trusted domain object.
- **Production solution:** test mapping and migration edges.

## Deep-dive talking points

Trace a balance through DTO, entity, domain Money, and localized UI text. Discuss units, nullability, schema migration, and where an identical model can be shared.

## Follow-up questions

- [ARC-07](../arc-07/): Why map models? **Answer:** to validate and isolate independent schema changes.
- [ARC-22](../arc-22/): What if Compose gets a DTO? **Answer:** it couples rendering to server schema and transport nullability.

## Self-check rubric

Name each model location, identify two schema-driven changes, and reject a UI-formatted money string as canonical data.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — data sources and repositories.
- [Android UI state](https://developer.android.com/topic/architecture/ui-layer/stateholders) — screen UI state.

Technically reviewed against the linked official Android architecture guidance on 2026-10-11. Conceptual flows and snippets are not device-tested.
