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

لماذا نستخدم محولات النماذج (Mappers) بين الطبقات المختلفة؟ وما الفوائد الحقيقية منها؟

1. مبدأ العزل والحماية (Decoupling and Insulation):
   - الـ Mapper هو المسؤول عن تحويل البيانات عند حدود الطبقات (Architectural Boundaries).
   - يمنع انتشار التغييرات الخارجية (Schema Ripple Effect): إذا قام فريق الـ Backend بتغيير اسم حقل من `user_name` إلى `handle`، يقتصر التعديل على دالة الـ Mapper في طبقة الـ Data فقط، بينما تظل آلاف الأسطر في الـ Domain والـ UI كما هي دون أي تغيير!

2. تنظيف البيانات والتحقق من صحتها (Data Sanitization & Null-Safety):
   - استجابات الـ JSON غالباً ما تحتوي على حقول مجهولة، أرقام سالبة غير متوقعة، أو حقول Nullable.
   - تقوم الـ Mappers بتحويل البيانات غير الموثوقة القادمة من السيرفر إلى نماذج بيزنس صارمة ومضمونة السلامة (Strict Domain Invariants) مع توفير قيم افتراضية آمنة.

3. تجهيز البيانات للواجهة (UI Formatting Optimization):
   - تحويل التواريخ من Unix Timestamp (`Long`) إلى نصوص منسقة محلياً (`String`) في مرحلة الـ Mapping، مما يريح الـ Composable من استهلاك المعالج في دوال التنسيق أثناء السكرول.

## Practical walkthrough

تنفيذ مابرات نظيفة باستخدام Extension Functions تضمن سلامة البيانات:
```kotlin
// 1. Data Layer Mapper: تحويل DTO السيرفر إلى Domain Entity مع تطهير البيانات:
fun UserDto.toDomain(): User {
    return User(
        id = this.id ?: throw InvalidUserDataException("User ID cannot be null"),
        displayName = this.fullName ?: "Anonymous Guest", // حماية من null
        isVerified = this.verificationStatus == "VERIFIED",
        joinedDate = Instant.ofEpochMilli(this.registeredAt ?: 0L)
    )
}

// 2. Presentation Layer Mapper: تحويل Domain Entity إلى UI Model جاهز للعرض:
fun User.toUiModel(dateTimeFormatter: DateTimeFormatter): UserUiModel {
    return UserUiModel(
        id = this.id,
        name = this.displayName,
        badgeVisible = this.isVerified,
        formattedJoinDate = dateTimeFormatter.format(this.joinedDate) // محسوبة مسبقاً للـ UI
    )
}
```

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

Mappers isolate architectural boundaries so external API or database changes don't break business logic or UI. They sanitize untrusted nullable payloads into validated domain models and transform domain data into pre-formatted, display-ready UI models.

## Interview answer — structured

Mappers are the gatekeepers of architectural boundaries, ensuring that each layer operates exclusively on data structures tailored to its purpose.

1. **Decoupling from External Volatility**: APIs and database schemas evolve constantly. Without mappers, renaming a JSON property cascades through the entire codebase, breaking domain logic and UI layouts. Mappers act as shock absorbers, confining external changes strictly to the data layer.

2. **Data Sanitization and Invariant Enforcement**: Network payloads are untrusted. Mappers sanitize raw inputs: mapping nullable DTO properties to non-nullable domain types with safe fallbacks, parsing raw string codes into type-safe enums or sealed classes, and rejecting corrupt records before they reach core business rules.

3. **Presentation Pre-computation**: Presentation mappers convert raw domain metrics (e.g. timestamps, currency in cents) into localized, human-readable strings (`$12.50`) once, keeping composable functions pure and avoiding expensive formatting passes during 120fps scrolling.

## Interview answer — deep senior

Under the hood, implementing mappers efficiently requires avoiding excessive object allocation churn. In Kotlin, mappers are best written as top-level or internal extension functions (`fun ProductDto.toDomain()`), avoiding unnecessary mapper class instantiations.

When dealing with large lists (e.g. 10,000 items), mapping must be executed off the main thread. Repositories execute DTO-to-Domain mapping within `withContext(Dispatchers.Default)` or `Dispatchers.IO` so that heavy JSON parsing and transformation passes never stutter the Android main looper.

In unit testing, testing mappers is straightforward: developers write pure JVM unit tests passing edge-case DTOs (null fields, malformed strings, boundary values) to verify that the domain model is always constructed in a valid, robust state.

## How to answer in the interview

- **Why:** schema drift must not leak into UI.
- **How:** validate and convert at boundary.
- **Trade-off:** extra code versus safer evolution.
- **Failure case:** unknown enum silently maps to success.
- **Production solution:** boundary tests for malformed payload.

## Deep-dive talking points

Inspect mapper behavior for missing required IDs, unknown enum cases, money conversion, error preservation and large-object copying.

## Follow-up questions

- **Interviewer:** "Should Mappers be classes or top-level extension functions?"
  **Answer:** "Top-level extension functions are preferred for stateless mappings because they avoid object allocation. A mapper class is only necessary when it requires injected dependencies like formatters or locale providers."

- **Interviewer:** "Can mapping become a performance bottleneck?"
  **Answer:** "Yes, if mapping large collections of thousands of items on the main thread. We optimize this by paginating data with Paging 3 and offloading mapping to `Dispatchers.Default`."

## Self-check rubric

Give a validation mapper, state its failure contract, explain one dangerous default, and name a boundary where mapping cost is justified.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — data-source boundary.
- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — state production.

Technically reviewed against primary documentation on 2026-10-13.
