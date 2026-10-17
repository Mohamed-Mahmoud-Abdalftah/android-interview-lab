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

## Concept and technical explanation

Allowing a Repository to return an API Data Transfer Object (DTO) directly to Jetpack Compose violates architectural boundaries and introduces severe coupling risks. DTOs are volatile wire-format models tailored specifically for network transport and JSON deserialization, frequently carrying nullable fields, serialization annotations, and backend-driven structures. Directly exposing DTOs couples UI composables to remote schema changes, degrading Compose recomposition efficiency because DTO classes lack stability guarantees. Furthermore, this practice forces UI components to execute costly date parsing and currency formatting calculations during composition passes, while crippling offline caching by bypassing the local database as the Single Source of Truth.

## Practical walkthrough (English)

Contrasting direct DTO exposure with clean domain and UI model separation:
```kotlin
// ❌ ANTI-PATTERN: Composable coupled directly to network DTO
@Composable
fun OrderRowBad(orderDto: OrderNetworkDto) { // Leaks Retrofit DTO into UI
    // In-composition formatting causes CPU overhead and dropped frames on 120Hz displays
    val formattedDate = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date(orderDto.epochTimestamp ?: 0L))
    Text("Order #${orderDto.order_id}: $${orderDto.total_cents?.div(100.0) ?: 0.0} on $formattedDate")
}

// ✅ CLEAN ARCHITECTURE: Clean separation with immutable UI models
@Immutable
data class OrderRowUiModel(
    val orderNumber: String,
    val formattedPrice: String,
    val formattedDate: String
)

@Composable
fun OrderRowGood(uiModel: OrderRowUiModel) {
    // Pure rendering: Composable is skippable, stable, and completely decoupled from network contracts
    Text("Order #${uiModel.orderNumber}: ${uiModel.formattedPrice} on ${uiModel.formattedDate}")
}
```

## Explanation in Arabic

عندما يقوم الـ Repository بإرجاع كائن API DTO مباشرة إلى Jetpack Compose: ما هي مخاطر الارتباط (Coupling Risks) المترتبة على ذلك؟

1. تسريب تفاصيل الشبكة والسيرفر إلى طبقة العرض (Infrastructure Leaks):
   - الـ DTO مصمم ليطابق بنية JSON القادمة من السيرفر.
   - إذا اعتمد الـ Composable على `UserDto` مباشرة:
     * أي تغيير بسيط في الـ API من قبل فريق الـ Backend (مثل تغيير اسم حقل، تحويل حقل إلى Array، أو حذفه) سيكسر ملفات الـ UI والـ Compose Layouts فوراً!

2. تدهور أداء وسلاسة Jetpack Compose (Performance & Stability Degradation):
   - كائنات الـ DTO غالباً ما تحوي حقولاً غير مستقرة، أو حقول Nullable متعددة تتطلب فحوصات `if (dto.data != null)` متكررة داخل الـ Composable.
   - كما تضطر دالة الـ Composable لحساب وتنسيق النصوص والتواريخ في كل فريم (Jank Risk) بدلاً من استقبال نصوص جاهزة محسوبة مسبقاً.

3. استحالة عمل Offline Caching ومصادر بيانات متعددة:
   - الـ DTO يمثل استجابة HTTP فقط. إذا أردت جلب البيانات من Room أو Bluetooth، فلن تتوافق الكائنات، مما يدمر فكرة الـ Single Source of Truth.

## Practical walkthrough

تصحيح تسريب الـ DTO وفصل النماذج عبر طبقة وسيطة:
```kotlin
// ❌ كارثة ارتباط: Composable يعتمد مباشرة على Retrofit DTO:
@Composable
fun BadUserBadge(userDto: UserNetworkDto) { // تسريب كائن الشبكة للـ UI!
    // فحص nulls مستمر وتنسيق تواريخ مكلف داخل الـ Composable:
    val formattedDate = SimpleDateFormat("yyyy-MM-dd").format(Date(userDto.timestamp ?: 0L))
    Text("${userDto.first_name} ${userDto.last_name} - $formattedDate")
}

// ✅ كود سليم: فصل تام بنماذج UI نقية ومستقرة:
@Immutable
data class UserBadgeUiModel(
    val fullName: String,
    val formattedJoinedDate: String
)

@Composable
fun GoodUserBadge(user: UserBadgeUiModel) {
    // عرض نقي وفوري بدون أي null checks أو حسابات ثقيلة:
    Text("${user.fullName} - ${user.formattedJoinedDate}")
}
```

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

Returning API DTOs directly to Compose tightly couples the UI to backend schema changes, degrades recomposition performance due to unstable and unskippable models, forces expensive formatting calculations inside the composition pass, and destroys offline caching by bypassing the local database as a Single Source of Truth.

## Interview answer — structured

Exposing API DTOs across the repository boundary into Jetpack Compose introduces significant architectural coupling and UI performance bottlenecks.
First, it creates vulnerability to backend schema volatility. DTOs mirror wire payloads shaped by server engineers. If an endpoint renames a JSON attribute, changes a type, or converts a field into an array, that network modification immediately breaks Composable functions, UI tests, and previews across the application.
Second, it compromises Jetpack Compose stability and smart recomposition. DTOs generated by serialization libraries rarely satisfy Compose compiler stability requirements. They often contain mutable properties, standard collections, or nullable fields, causing composables that accept them to become unskippable and re-render unnecessarily on parent invalidations.
Third, it introduces formatting overhead within the composition phase. When composables consume raw DTOs, they are forced to parse ISO timestamps, format monetary values, and concatenate localized strings during every frame, resulting in memory allocation churn and frame drops during fast scrolling.
Finally, direct DTO propagation prevents robust offline-first architecture, as wire payloads cannot be reconciled with Room database entities or persistent caching mechanisms.

## Interview answer — deep senior

Under the hood, DTOs and Compose UI models serve fundamentally opposing architectural purposes. DTOs are optimized for deserialization ergonomics, relying on serialization annotations, nullable fallback defaults, and wire efficiency. In contrast, Compose UI models prioritize rendering efficiency, immutable data structures, and stability annotations like Immutable or Stable to maximize smart skipping during recomposition passes.
When a Composable accepts a raw DTO containing an unannotated List or nullable timestamps, the Compose compiler marks the parameter as unstable. Consequently, whenever the parent composable recomposes, the runtime cannot verify whether the parameter has changed, forcing full recomposition of the child composable.
Furthermore, executing string formatting, date parsing, or currency formatting inside Composable functions creates continuous memory allocation on the UI thread. During 120Hz scrolling across lazy lists, repeated object allocations trigger garbage collection pauses, causing visible frame drops and user interface jank.
The architectural contract mandates a two-stage transformation pipeline: the Data layer maps incoming network DTOs into clean Domain entities, validating data integrity and enforcing domain constraints. Subsequently, the Presentation layer (ViewModel) transforms Domain entities into tailored, pre-formatted, immutable UI models.
Staff engineers enforce this boundary through automated architectural linters and code reviews, ensuring that transport types from Retrofit or Ktor never cross past the Repository boundary.

## How to answer in the interview

- **Why:** wire contracts change independently from UI.
- **How:** map and validate before rendering.
- **Trade-off:** boundary code versus direct simplicity.
- **Failure case:** new backend enum crashes/silently succeeds.
- **Production solution:** contract test and explicit unknown handling.

## Deep-dive talking points

Analyze DTO field rename, nullability, units, unknown enum, UI formatting and repository contract tests.

## Follow-up questions

- **Interviewer:** "What happens to Compose skipping when a DTO class is modified?"
  **Answer:** "DTO classes from network libraries typically lack Compose stability annotations, making composables that accept them unskippable and forcing full recompositions on parent invalidations."

- **Interviewer:** "Where should the transformation from DTO to UI model take place?"
  **Answer:** "DTO to Domain model occurs in the Data layer (Repository). Domain model to UI model occurs in the Presentation layer (ViewModel or Presentation Mapper)."

## Self-check rubric

List three coupling risks and sketch the DTO-to-domain-to-UI mapping for a nullable price.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository abstraction.
- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — UI state production.

Technically reviewed against primary documentation on 2026-10-13.
