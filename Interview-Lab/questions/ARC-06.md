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

أين تعيش كائنات DTOs و Room Entities و Domain Models و UI Models في المعمارية؟ وما دور كل منها؟

1. كائنات الـ DTOs (Data Transfer Objects):
   - **مكانها**: طبقة الـ Data (داخل مجلد `network` / `remote`).
   - **مهمتها**: مطابقة الـ JSON Schema أو الـ Protobuf القادم من الـ Backend بدقة.
   - **خصائصها**: تحوي وسوم Serialization مثل `@SerialName` أو `@SerializedName`، وغالباً ما تكون جميع حقولها قابلة للعدم (Nullable) لأن السيرفر قد يغير العقد في أي وقت.

2. كائنات الـ Room Entities:
   - **مكانها**: طبقة الـ Data (داخل مجلد `local` / `db`).
   - **مهمتها**: تمثيل الجداول والصفوف داخل قاعدة بيانات SQLite المحلية.
   - **خصائصها**: تحوي وسوم Room مثل `@Entity`, `@PrimaryKey`, `@ColumnInfo`.

3. كائنات الـ Domain Models:
   - **مكانها**: طبقة الـ Domain (داخل مجلد `model`).
   - **مهمتها**: تمثيل المفاهيم الأساسية للأعمال في التطبيق كـ Pure Kotlin Data Classes.
   - **خصائصها**: نظيفة تماماً من أي وسوم أو مكتبات خارجية، تضمن ثبات البيانات وسلامتها (Business Invariants).

4. كائنات الـ UI Models:
   - **مكانها**: طبقة الـ Presentation (داخل مجلد `ui` أو `feature`).
   - **مهمتها**: مطابقة ما يعرضه الـ Composable أو الـ View على الشاشة مباشرة.
   - **خصائصها**: نصوص منسقة جاهزة للعرض (Formatted strings)، ألوان، وأيقونات (`@StringRes`, `Color`).

## Practical walkthrough

تتبع نموذج منتج عبر الطبقات الأربع مع الـ Mappers:
```kotlin
// 1. DATA LAYER (Network DTO): يطابق JSON السيرفر بدقة:
@Serializable
data class ProductDto(
    @SerialName("prod_id") val id: String,
    @SerialName("cost_in_cents") val cost: Long,
    @SerialName("is_active") val active: Boolean?
)

// 2. DATA LAYER (Local Database Entity): يطابق جدول SQLite:
@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey val id: String,
    val costCents: Long,
    val lastUpdatedTimestamp: Long
)

// 3. DOMAIN LAYER (Pure Domain Model): نموذج البيزنس النقي المستقر:
data class Product(
    val id: String,
    val price: Long,
    val isAvailable: Boolean
)

// 4. PRESENTATION LAYER (UI Model): نصوص منسقة جاهزة للرسم في Compose:
@Immutable
data class ProductUiModel(
    val id: String,
    val formattedPrice: String, // جاهز مثل "$19.99"
    val statusColor: Color,
    val isBuyButtonEnabled: Boolean
)
```

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

DTOs live in Data/remote matching API schemas. Room entities live in Data/local matching SQLite tables. Domain models live in Domain representing pure business entities without framework annotations. UI models live in Presentation holding formatted, display-ready data.

## Interview answer — structured

Separating models across architectural layers guarantees isolation and prevents external schema changes from cascading across the application.

First, with DTOs (Data Transfer Objects), reside in the **Data Layer** (`remote/dto`). They represent network serialization schemas, annotated with `@Serializable` or `@SerializedName`. They are designed around API payloads and should never leak past the repository boundary. Next, with Room Entities, reside in the **Data Layer** (`local/entity`). They represent SQLite table schemas, annotated with `@Entity`, `@PrimaryKey`, and foreign keys. They reflect persistence requirements (indexes, table relations), not UI or business needs.
Additionally, with Domain Models, reside in the **Domain Layer** (`domain/model`). Pure Kotlin data classes representing business truth. They contain zero serialization or database annotations, enforcing invariant validity across the app. Finally, with UI Models, reside in the **Presentation Layer** (`presentation/model`). They contain pre-formatted strings, localized labels, and visual state properties tailored for instant, allocation-free rendering in Compose.


## Interview answer — deep senior

Why not use a single model class annotated with `@Serializable`, `@Entity`, and consumed directly in Compose? This shortcut—common in junior tutorials—creates catastrophic tight coupling: changing an API property name alters the local SQLite column, forces a Room database migration, and breaks the UI layout simultaneously!

Furthermore, UI models optimize rendering performance in Jetpack Compose. Instead of letting a Composable format dates or currency on every recomposition pass (`format(product.priceCents)`), the ViewModel maps the domain model into a `ProductUiModel` where `formattedPrice = "$19.99"` is computed once. This keeps the Composable function pure, lightweight, and skippable.


## How to answer in the interview

- **Why:** different boundaries have different contracts.
- **How:** map and validate at crossings.
- **Trade-off:** isolation versus conversion cost.
- **Failure case:** nullable DTO becomes trusted domain object.
- **Production solution:** test mapping and migration edges.

## Deep-dive talking points

Trace a balance through DTO, entity, domain Money, and localized UI text. Discuss units, nullability, schema migration, and where an identical model can be shared.

## Follow-up questions

- **Interviewer:** "What is the consequence of passing a Room Entity directly to a Composable?"
  **Answer:** "It leaks SQLite schema details into the UI, forces Compose to re-render when non-visual database metadata updates, and prevents running pure JVM UI tests without Room dependencies."

- **Interviewer:** "Can a Domain Model and a UI Model be identical in simple apps?"
  **Answer:** "Yes, if the domain model has no formatting requirements and is already `@Immutable`, the ViewModel can expose it directly to the UI to avoid redundant mapping boilerplate."

## Self-check rubric

Name each model location, identify two schema-driven changes, and reject a UI-formatted money string as canonical data.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — data sources and repositories.
- [Android UI state](https://developer.android.com/topic/architecture/ui-layer/stateholders) — screen UI state.

Technically reviewed against primary documentation on 2026-10-13.
