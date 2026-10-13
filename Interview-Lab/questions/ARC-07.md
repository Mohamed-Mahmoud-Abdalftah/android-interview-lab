---
id: "ARC-07"
question: "Why do we use mappers between models?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 152
editorial_status: "reviewed"
---

# ARC-07

## Original interview question

Why do we use mappers between models?

## What the interviewer evaluates

Explain mapping as boundary validation and change isolation, with costs and avoidance of silent defaults.

## Explanation in Arabic

Mapper مش بس `dto.name -> model.name`؛ دي فرصة تتأكد من units، required fields، enum unknown values، وتفصل schema خارجي عن domain. `UserDto(id: String?)` ممكن يبقى `UserId` validated أو error واضح بدل `id ?: ""` اللي يعمل object باطل. Mapper بين domain وUI يضيف localized text أو presentation flags من غير ما يلوث domain. بس لو كل layer بتعمل copy متطابق من غير اختلاف حقيقي، ده boilerplate؛ اختار boundaries لها سبب تغيير مستقل.

## Practical walkthrough

Mapper يترجم ويطبّع بين schemas، وليس copy لكل field فقط. مثال backend يرسل amount minor units وstatus string؛ mapper يرفض unknown status أو يحافظ عليه كUnknown بدل افتراض Approved. ضع conversion عند data boundary واختبر null/overflow/new enum. كثرة mapper بلا اختلاف semantics تضيف boilerplate؛ حدد لماذا كل تحويل موجود.

## Why it matters and how it works

Mappings decouple schemas and make invalid external states explicit. They let persistence, network, business and UI evolve independently. The mapper should state failure behavior rather than silently manufacture valid-looking values.

## Worked example

Illustrative Kotlin/JVM mapping with an explicit failure for missing ID:
```kotlin
data class UserDto(val id: String?, val name: String?)
data class User(val id: String, val name: String)
fun UserDto.toDomain(): User? {
    val validId = id?.takeIf(String::isNotBlank) ?: return null
    return User(validId, name.orEmpty())
}
```
Here `null` intentionally means invalid payload; a production API should carry a diagnostic error category if callers need it.

## Trade-offs and decision criteria

Mapper code adds maintenance and allocation. Keep mapping at boundaries, not every function. For data with identical semantics and stable ownership, sharing a model can be reasonable. For high-risk units or changing schemas, explicit mapping is worth the cost.

## Failure modes

A mapper turns unknown server payment status into `SUCCESS` by default, hiding new protocol states. Use explicit unknown/error handling and telemetry. Another risk is losing server error codes by mapping every failure to a generic string.

## Production perspective

A marketplace app accepts versioned product DTOs, maps prices in minor units to a domain Money type, persists entities with migration tests, then formats UI labels by locale. Contract tests cover missing fields and new enum values.

## Interview answer — short

Mappers validate and translate across boundaries so transport, database, domain, and UI can change independently. I keep failure behavior explicit and avoid silent defaults that make bad data look valid.

## Interview answer — structured

I use a mapper where two models have different contracts. A network DTO may have nullable or versioned fields; a domain model may require a valid ID and money unit; a UI model may need localized text. The mapper is where I enforce those transitions. That improves tests and limits change propagation, but it is not free. If two types are truly identical and stable, I would not copy them solely to satisfy a layer diagram. I would test mappings with missing required IDs, unexpected enum values, and a price-unit change. A mapper that silently converts invalid data into a valid-looking empty or zero value can be more dangerous than having no mapper.

## Interview answer — deep senior

The most valuable mapper is a validation boundary. It can reject malformed IDs, convert units, handle unknown enum values, and preserve safe error context. I do not let `orEmpty()` or zero defaults conceal a failed transfer amount, because that can create plausible but false state. I test representative server payloads, schema migrations, and UI formatting separately. I also watch allocation and maintenance cost: deep copying a huge object graph on every frame is not justified by theoretical purity. Mapping belongs near the source or target boundary, with clear ownership and one place to update when contracts evolve. The goal is to keep business invariants stable while transport and presentation details change. Mapping also defines an error contract. If validation fails, I decide whether to reject the record, keep previous cached data, or surface a typed failure; I do not bury the cause in a default. For large datasets I consider where mapping runs and measure allocation, but correctness comes first for business-critical fields. I keep locale formatting out of the network mapper and server DTOs out of Compose. That separation lets transport evolve without changing every screen.

## How to answer in the interview

- **Why:** schema drift must not leak into UI.
- **How:** validate and convert at boundary.
- **Trade-off:** extra code versus safer evolution.
- **Failure case:** unknown enum silently maps to success.
- **Production solution:** boundary tests for malformed payload.

## Deep-dive talking points

Inspect mapper behavior for missing required IDs, unknown enum cases, money conversion, error preservation and large-object copying.

## Follow-up questions

- [ARC-06](../arc-06/): Which models need mapping? **Answer:** models with different transport, storage, business or UI contracts.
- [ARC-12](../arc-12/): How should mapping errors appear? **Answer:** as typed failures the UI can act on, not silent defaults.

## Self-check rubric

Give a validation mapper, state its failure contract, explain one dangerous default, and name a boundary where mapping cost is justified.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — data-source boundary.
- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — state production.

Technically reviewed against the linked official Android architecture guidance on 2026-10-11. Conceptual flows and snippets are not device-tested.
