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

## Concept and technical explanation

Model segregation across architectural boundaries enforces the Single Responsibility Principle and insulates core business logic from external payload variations. DTOs (Data Transfer Objects) belong strictly to the network module within the Data layer, directly modeling remote JSON/Protobuf schemas with serialization annotations. Room entities reside within the database module of the Data layer, carrying persistence annotations that map directly to SQLite tables, primary keys, and foreign indices. Domain models reside at the core in the Domain layer as pure, unannotated Kotlin data classes representing business truth, constraints, and enterprise invariants. UI models belong to the Presentation layer, structured specifically for rendering ergonomics in Jetpack Compose—flattening nested structures, converting raw timestamps into formatted localized strings, and providing UI flags.

## Practical walkthrough (English)

Differentiating and mapping the four model tiers in a financial ledger app:
```kotlin
// 1. DATA LAYER (Network): DTO mirrors backend JSON schema
@Serializable
data class AccountTransactionDto(
    @SerialName("tx_id") val txId: String,
    @SerialName("amount_cents") val amountCents: Long,
    @SerialName("timestamp_epoch") val timestampEpoch: Long
)

// 2. DATA LAYER (Database): Entity models local SQLite table
@Entity(tableName = "transactions")
data class TransactionEntity(
    @PrimaryKey val id: String,
    val amountCents: Long,
    val timestamp: Long
)

// 3. DOMAIN LAYER: Pure business entity with domain invariants
data class Transaction(
    val id: String,
    val amount: BigDecimal,
    val instant: Instant
)

// 4. PRESENTATION LAYER: UI model optimized for Compose rendering
data class TransactionUiModel(
    val id: String,
    val formattedAmount: String, // e.g. "$12.50"
    val displayDate: String,     // e.g. "Today, 3:45 PM"
    val isDebit: Boolean
)
```

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

DTOs live in the network module and Room entities live in the database module within the Data layer. Domain models reside in the pure Kotlin Domain layer representing core business concepts. UI models live in the Presentation layer optimized for Composable rendering.

## Interview answer — structured

Separating data representations across layers prevents external framework changes from polluting internal business models.

DTOs belong strictly to the network layer, mirroring remote JSON schemas with serialization annotations. Room entities belong to the local database layer, annotated with table and column definitions that reflect SQLite schemas.

In production, Domain models reside at the architectural core inside the domain layer. They are pure, unannotated Kotlin classes that represent business truth and invariants, completely free from database or network serialization dependencies.
As for UI models, they live in the presentation layer. These models are structured specifically for display ergonomics, containing formatted currency strings, localized date text, and layout visibility flags, allowing Jetpack Compose to render widgets passively without computing formatting logic during recomposition.


## Interview answer — deep senior

Under the hood, model segregation enforces the Single Responsibility Principle and eliminates subtle coupling across boundaries. A frequent shortcut in rushed codebases is annotating a single entity with both Moshi @Json annotations and Room @Entity annotations, then passing it straight into the UI. While this saves initial lines of code, it binds your database schema, backend API contracts, and UI display logic into a single rigid structure. If the backend renames a JSON property, your local database schema breaks, requiring Room migrations and risking database crashes in production.
By maintaining four distinct model types—DTOs for transport, Entities for persistent storage, Domain models for business logic, and UI models for presentation—each model is free to evolve independently. DTOs accommodate backend breaking changes and nullability quirks; Entities optimize for SQLite indexing, foreign keys, and relational normalization; Domain models enforce business rules and invariants; and UI models are tailored for Compose stability, memoization, and accessibility requirements.
Staff engineers enforce explicit mapping at the boundaries using pure extension functions like toDomain, toEntity, and toUiModel. While this requires mapper boilerplate, it isolates defects: a network contract modification only touches the network mapper, leaving database persistence, business validation, and UI rendering entirely untouched. This structural isolation is the hallmark of resilient enterprise architecture.

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
